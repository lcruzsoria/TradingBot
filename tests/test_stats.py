"""Ventana de estadísticas: cifras de las operaciones simuladas y el botón que la abre y la cierra."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from dataclasses import replace
from datetime import date, datetime

import pytest

from tradingbot.envconfig import EnvConfig
from tradingbot.skills.cortex.order import Order
from tradingbot.skills.setup.positions import Closed
from tradingbot.ui.stats_dialog import TradeStats, alignment_of, session_of

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
    assert s.flat == 0 and s.avg_win == 1.5 and s.avg_loss == -1.0 and s.best_trade.order is c
    pats = s.groups(lambda t: t.order.pattern)
    assert [(g.name, g.n, g.wins, g.losses, g.open, g.r) for g in pats] == [("Reversión", 1, 1, 0, 0, 2.0),
                                                                         ("Continuación", 2, 1, 1, 1, 0.0)]
    sides = s.groups(lambda t: t.order.direction, ("long", "short"))
    assert [(g.name, g.n) for g in sides] == [("long", 3), ("short", 0)] and sides[1].win_rate is None
    assert s.only(lambda t: t.order.symbol == "NAS100").total_r == -1.0
    s.reset()
    assert s.trades == [] and s.go == 0 and s.win_rate is None and s.profit_factor is None


def test_sesion_y_sesgo():
    assert [session_of(datetime(2026, 10, 6, h)) for h in (20, 2, 3, 9, 16, 17, 18)] ==         ["Asia", "Asia", "Londres", "Nueva York", "Nueva York", "Rollover", "Asia"]
    assert alignment_of(order()) == "A favor" and alignment_of(order(direction="short")) == "En contra"
    assert alignment_of(order(bias="No Bias")) == "Sin sesgo" and alignment_of(order(bias="Bearish", direction="short")) == "A favor"


def test_el_boton_abre_y_cierra_la_ventana(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": ["EURUSD"]}}
    bus = EventBus()
    win = MainWindow(bus, SkillManager(bus, Services(None, None, cfg, EnvConfig()), [{"type": "stats"}]), cfg, "t")
    assert win.stats_btn.isVisibleTo(win) and win.backtest_btn.isVisibleTo(win)
    o = order()
    s = TradeStats()                                                    # lo que publica la skill Stats
    s.executed(o)
    s.closed(o, Closed("objetivo", 115.0, 1_010_000, 1.0, 9.5))
    win._on_stats_session({"stats": s.snapshot()})

    win.stats_btn.click()                                               # abre
    dlg = win.stats_dialog
    assert dlg.isVisible() and win.stats_btn.isChecked() and win.stats_btn.text() == "Forwardtest"
    assert dlg.window_days == 30                                        # por defecto, los últimos 30 días
    dlg.set_window(None)                                                # la operación de prueba es de 1970
    assert dlg.blocks["trades"].value.text() == "1" and dlg.blocks["win"].value.text() == "100 %"
    assert dlg.history.rowCount() == 1 and dlg.history.item(0, 7).text() == "+1.00 R"
    assert dlg.by_symbol.rows[0][0].text() == "EURUSD" and dlg.by_symbol.rows[0][4].text() == "+1.00 R"
    assert [r[0].text() for r in dlg.by_session.rows] == ["Asia", "Londres", "Nueva York", "Rollover"]
    assert dlg.by_pattern.highlights[0][0].text() == "Continuación"
    dlg.set_window(0)                                                   # «Hoy»: la operación de prueba es de 1970
    assert dlg.blocks["trades"].value.text() == "0" and dlg.history.rowCount() == 0
    dlg.set_window(None)
    win.stats_btn.click()                                               # cierra
    assert not dlg.isVisible() and not win.stats_btn.isChecked()
    win.stats_btn.click()
    dlg.reject()                                                        # cerrar con Esc / la X desmarca el botón
    assert not dlg.isVisible() and not win.stats_btn.isChecked()


def _window(tmp_path, monkeypatch, skills, bus=None):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": ["EURUSD"]}}
    bus = bus or EventBus()
    return MainWindow(bus, SkillManager(bus, Services(None, None, cfg, EnvConfig()), skills), cfg, "t")


def test_reiniciar_avisa_a_la_skill(tmp_path, monkeypatch):
    from tradingbot.core import EventBus
    bus = EventBus()
    seen = []
    bus.subscribe("test", "stats.reset", seen.append)
    win = _window(tmp_path, monkeypatch, [{"type": "stats"}], bus)
    win.stats_btn.click()
    win.stats_dialog.reset_btn.click()
    assert [e.topic for e in seen] == ["stats.reset"]


def test_sin_skill_stats_no_hay_botones(tmp_path, monkeypatch):
    win = _window(tmp_path, monkeypatch, [])
    assert not win.stats_btn.isVisibleTo(win) and not win.backtest_btn.isVisibleTo(win)


def test_el_boton_backtest_abre_y_cierra_la_ventana(tmp_path, monkeypatch):
    from tradingbot.skills.stats.backtest import Backtest, Group
    win = _window(tmp_path, monkeypatch, [{"type": "stats"}])
    win._on_stats_backtest({"backtest": Backtest([Group("oro", "Oro", {"resumen": []})], {}), "error": ""})
    win.backtest_btn.click()
    dlg = win.backtest_dialog
    assert dlg.isVisible() and win.backtest_btn.isChecked() and dlg.group_key == "oro"
    win.backtest_btn.click()
    assert not dlg.isVisible() and not win.backtest_btn.isChecked()
