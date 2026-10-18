"""Ventana de estadísticas: cifras de las operaciones simuladas y el botón que la abre y la cierra."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from dataclasses import replace
from datetime import date

import pytest

from tradingbot.envconfig import EnvConfig
from tradingbot.skills.cortex.order import Order
from tradingbot.skills.setup.positions import Closed
from tradingbot.ui.stats_dialog import TradeStats

BASE = Order("EURUSD", "15m", "long", "Continuación", "p", "NY Open", date(2026, 10, 6), 105.0, 95.0, 100.0, 105.0, 95.0, 115.0,
             "Bullish", 3.0, "GO", entry_ts=1_000_000, close_ts=1_086_400)


def order(**kw):
    return replace(BASE, **kw)


def test_cifras_de_la_sesion():
    s = TradeStats()
    a, b, c, d = order(), order(symbol="NAS100", entry_ts=1_001_000), order(pattern="Reversión", entry_ts=1_002_000), order(entry_ts=1_003_000)
    for o in (a, b, c, d):
        s.executed(o)
    s.decision(True)
    s.decision(False)
    s.closed(a, Closed("objetivo", 115.0, 1_010_000, 1.0, 9.5))
    s.closed(b, Closed("stop", 95.0, 1_011_000, -1.0, -9.5))
    s.closed(c, Closed("objetivo", 115.0, 1_012_000, 2.0, 19.0))
    s.closed(d, None)                                                   # sin resultado: sigue abierta
    assert (len(s.done), len(s.open), s.wins, s.losses) == (3, 1, 2, 1)
    assert s.total_r == 2.0 and s.win_rate == pytest.approx(66.67, abs=0.01) and s.expectancy == pytest.approx(2 / 3)
    assert s.profit_factor == 3.0 and s.equity == [0.0, 1.0, 0.0, 2.0] and s.max_drawdown == 1.0
    assert s.streak == 1 and (s.best, s.worst) == (2.0, -1.0) and (s.go, s.nogo) == (1, 1)
    assert s.breakdown(lambda o: o.symbol) == [("EURUSD", 2, 2, 3.0), ("NAS100", 1, 0, -1.0)]
    s.reset()
    assert s.trades == [] and s.go == 0 and s.win_rate is None and s.profit_factor is None


def test_el_boton_abre_y_cierra_la_ventana(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": ["EURUSD"]}}
    win = MainWindow(EventBus(), SkillManager(EventBus(), Services(None, None, cfg, EnvConfig()), []), cfg, "t")
    o = order()
    win._on_setup_executed({"order": o, "sent": False, "note": "simulación"})
    win._on_setup_closed({"order": o, "closed": Closed("objetivo", 115.0, 1_010_000, 1.0, 9.5), "sent": False})

    win.stats_btn.click()                                               # abre
    dlg = win.stats_dialog
    assert dlg.isVisible() and win.stats_btn.isChecked()
    assert dlg.blocks["trades"].value.text() == "1" and dlg.blocks["win"].value.text() == "100 %"
    assert dlg.history.rowCount() == 1 and dlg.history.item(0, 5).text() == "+1.00 R"
    win.stats_btn.click()                                               # cierra
    assert not dlg.isVisible() and not win.stats_btn.isChecked()
    win.stats_btn.click()
    dlg.reject()                                                        # cerrar con Esc / la X desmarca el botón
    assert not dlg.isVisible() and not win.stats_btn.isChecked()
