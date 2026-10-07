"""El mercado se elige pinchando su tarjeta; el timeframe, con los chips. No hay selector ni botón de cargar."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from tradingbot import settings
from tradingbot.core import EventBus, Services, SkillManager
from tradingbot.ui.main_window import MainWindow
from tradingbot.ui.watchlist_dialog import WatchlistDialog


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


@pytest.fixture
def make_window(qapp, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "settings.local.json")

    def _make(watchlist, symbol="EURUSD", timeframe="15m"):
        cfg = {"app": {"symbol": symbol, "timeframe": timeframe, "watchlist": watchlist}}
        bus = EventBus()
        loads = []
        bus.subscribe("t", "feed.load", loads.append)
        win = MainWindow(bus, SkillManager(bus, Services(None, None, cfg), []), cfg, "t")
        return win, loads
    return _make


def chips(win):
    return [b.text() for b in win.tf_group.buttons()]


def test_ya_no_hay_selector_ni_boton_cargar(make_window):
    win, _ = make_window(["EURUSD"])
    assert not hasattr(win, "symbol") and not hasattr(win, "load_btn")


def test_chips_de_timeframe(make_window):
    win, _ = make_window(["EURUSD"])
    assert chips(win) == ["M1", "M3", "M5", "M15", "H1", "H3", "H4", "H7", "H12", "1D", "1W"]
    assert win.current_tf() == "15m"


def test_el_mercado_inicial_es_el_de_config_si_esta_en_el_panel(make_window):
    win, _ = make_window(["NAS100FT.r", "EURUSD"], symbol="eurusd")
    assert win.current_symbol == "EURUSD"


def test_mercado_inicial_fuera_del_panel_se_sustituye_por_el_primero(make_window):
    win, _ = make_window(["DJ30", "EURUSD"], symbol="GER40")
    assert win.current_symbol == "DJ30"
    assert "GER40" in win.log_view.toPlainText() and "no está en el panel Quotes" in win.log_view.toPlainText()


def test_pinchar_una_tarjeta_carga_ese_mercado_con_el_timeframe_elegido(make_window):
    win, loads = make_window(["NAS100FT.r", "DJ30"])
    win.tf_group.buttons()[6].setChecked(True)             # H4
    win._on_market_clicked("dj30")
    assert win.current_symbol == "DJ30"
    assert loads[-1].payload == {"symbol": "DJ30", "timeframe": "4h"}   # nombre exacto de la lista


def test_cambiar_de_timeframe_recarga_el_mercado_actual(make_window):
    win, loads = make_window(["DJ30"], symbol="DJ30")
    btn = next(b for b in win.tf_group.buttons() if b.text() == "1W")
    btn.click()
    assert loads[-1].payload == {"symbol": "DJ30", "timeframe": "1w"}


def test_si_se_quita_el_mercado_actual_se_carga_otro(make_window):
    win, loads = make_window(["GER40", "EURUSD"], symbol="GER40")
    win.connected = True
    win.set_watchlist(["EURUSD", "DJ30"])                 # GER40 fuera
    assert win.current_symbol == "EURUSD" and loads[-1].payload["symbol"] == "EURUSD"


def test_si_el_mercado_actual_sigue_no_se_recarga(make_window):
    win, loads = make_window(["GER40", "EURUSD"], symbol="EURUSD")
    win.connected = True
    win.set_watchlist(["EURUSD", "DJ30"])
    assert loads == [] and win.current_symbol == "EURUSD"
    assert settings.load_watchlist([]) == ["EURUSD", "DJ30"]


def test_sin_mercados_no_hace_nada(make_window):
    win, loads = make_window(["EURUSD"])
    win.set_watchlist([])
    win.load_candles()
    assert loads == [] and win.current_symbol == ""


def test_el_dialogo_no_deja_guardar_una_lista_vacia(qapp):
    dlg = WatchlistDialog(None, ["EURUSD"], ["EURUSD"])
    dlg.chosen.selectAll()
    dlg.remove_selected()
    dlg._save()
    assert dlg.result() == 0 and "al menos un mercado" in dlg.hint.text()
    dlg.add_symbol("EURUSD")
    dlg._save()
    assert dlg.result() == 1


def test_lista_vacia_en_ajustes_cae_a_la_de_config(tmp_path):
    f = tmp_path / "s.json"
    settings.save_settings({"watchlist": []}, f)
    assert settings.load_watchlist(["DJ30"], f) == ["DJ30"]
    assert settings.load_watchlist([], f) == list(settings.DEFAULT_WATCHLIST)
