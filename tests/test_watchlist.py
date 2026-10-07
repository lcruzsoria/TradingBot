import json
import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

import tradingbot.skills  # noqa: F401
from tradingbot import settings
from tradingbot.skills.bias import BiasEngine
from tradingbot.core import EventBus, Services, SkillManager
from tradingbot.skills.feed.demo_data import DemoSource
from tradingbot.ui.watchlist_dialog import WatchlistDialog, filter_symbols

BROKER = ["AUDUSD", "BTCUSD", "DJ30", "ETHUSD", "EURUSD", "GER40", "NAS100", "NAS100FT.r", "SP500", "UK100",
          "XAUUSD", "XTIUSD"]


def test_clean_symbols_conserva_orden_y_elimina_repetidos():
    assert settings.clean_symbols([" DJ30", "dj30", "", "NAS100FT.r", "EURUSD "]) == ["DJ30", "NAS100FT.r", "EURUSD"]


def test_guardar_y_cargar_watchlist(tmp_path):
    f = tmp_path / "settings.local.json"
    assert settings.load_watchlist(["A", "B"], f) == ["A", "B"]            # sin fichero: la de config.toml
    settings.save_settings({"otra": 1}, f)
    settings.save_watchlist(["DJ30", "NAS100FT.r", "dj30"], f)
    assert settings.load_watchlist(["A"], f) == ["DJ30", "NAS100FT.r"]
    assert json.loads(f.read_text())["otra"] == 1                          # no pisa otros ajustes


def test_fichero_de_ajustes_corrupto(tmp_path):
    f = tmp_path / "settings.local.json"
    f.write_text("{no es json")
    with pytest.raises(ValueError, match="settings.local.json"):
        settings.load_watchlist([], f)


def test_busqueda_con_alias():
    assert filter_symbols(BROKER, "dow") == ["DJ30"] == filter_symbols(BROKER + ["USDJPY"], "Dow Jones")  # USDJPY no cuela
    assert filter_symbols(BROKER, "nasdaq") == ["NAS100", "NAS100FT.r"]
    assert filter_symbols(BROKER, "oro") == ["XAUUSD"]
    assert filter_symbols(BROKER, "petróleo") == ["XTIUSD"]
    assert filter_symbols(BROKER, "nas100ft.R") == ["NAS100FT.r"]            # sin distinguir mayúsculas
    assert filter_symbols(BROKER, "") == BROKER and filter_symbols(BROKER, "zzz") == []


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def test_dialogo_quitar_germania_y_poner_dow(qapp):
    dlg = WatchlistDialog(None, BROKER, ["NAS100", "SP500", "GER40", "EURUSD"])
    dlg.chosen.setCurrentRow(2)
    dlg.remove_selected()                       # fuera GER40
    dlg.search.setText("dow")
    assert dlg.matches.count() == 1 and dlg.matches.currentItem().text() == "DJ30"
    dlg.add_selected()
    dlg.add_selected()                           # añadir dos veces no duplica
    assert dlg.symbols == ["NAS100", "SP500", "EURUSD", "DJ30"]
    dlg.chosen.setCurrentRow(3)
    dlg.move(-2)
    assert dlg.symbols == ["NAS100", "DJ30", "SP500", "EURUSD"]


def test_dialogo_sin_lista_del_broker_permite_escribir(qapp):
    dlg = WatchlistDialog(None, [], [])
    dlg.search.setText("DJ30")
    dlg.add_selected()
    assert dlg.symbols == ["DJ30"]


def test_grid_se_reconstruye_y_conserva_la_seleccion(qapp):
    from tradingbot.ui.widgets import MarketsGrid
    grid = MarketsGrid(["NAS100", "GER40"])
    grid.set_selected("nas100")
    grid.set_symbols(["NAS100", "DJ30"])
    assert list(grid.cards) == ["NAS100", "DJ30"] and grid.cards["NAS100"].property("selected") == "true"


def wait_for(cond, timeout=5.0):
    end = time.time() + timeout
    while time.time() < end:
        if cond():
            return True
        time.sleep(0.02)
    return False


def test_quotes_cambia_de_lista_sin_reiniciar():
    bus, events = EventBus(), []
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": ["EURUSD", "GER40"]}}
    manager = SkillManager(bus, Services(DemoSource(), BiasEngine([]), cfg), [{"type": "feed", "slot": 0}, {"type": "quotes", "slot": 5}])
    bus.subscribe("t", "*", events.append)
    manager.start()
    try:
        bus.publish("feed.load", {"symbol": "EURUSD", "timeframe": "15m"}, source="ui")
        assert wait_for(lambda: any(e.topic == "quotes.updated" for e in events))
        assert "all_symbols" in next(e for e in events if e.topic == "feed.connected").payload
        n = len(events)
        bus.publish("watchlist.changed", {"symbols": ["EURUSD", "DJ30"]}, source="ui")
        assert wait_for(lambda: any(e.topic == "quotes.updated" and "DJ30" in e.payload["quotes"] for e in events[n:]))
        last = [e for e in events if e.topic == "quotes.updated"][-1].payload["quotes"]
        assert set(last) == {"EURUSD", "DJ30"} and last["DJ30"] is not None
    finally:
        manager.stop()
