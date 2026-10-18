"""Forwardtest: diario mensual de la skill Stats (no se pierde al reiniciar), meses guardados y el área Stats de la ventana."""
import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from dataclasses import replace
from datetime import date, datetime
from types import SimpleNamespace

from tradingbot.core import Event, EventBus, Services, SkillManager
from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.cortex.order import Order
from tradingbot.skills.setup.positions import Closed
from tradingbot.skills.stats.journal import Journal, month_label, next_month, previous_month
from tradingbot.skills.stats.session import Signal, TradeStats, reason_of
import tradingbot.skills  # noqa: F401

ORDER = Order("NAS100", "15m", "long", "Continuación", "continuacion", "London", date(2026, 10, 6), 105.0, 95.0, 100.0, 105.0,
              95.0, 115.0, "Bullish", 3.0, "GO", entry_ts=1_000_000, close_ts=1_086_400)
WIN = Closed("objetivo", 115.0, 1_010_000, 2.0, 9.5)


def clock(*when):
    return lambda: datetime(*when)


def skill_in(folder):
    bus = EventBus()
    env = EnvConfig(parse(f"STATS_FORWARD_DIR={folder}\nSTATS_BACKTEST_FILE={folder / 'no.json'}"))
    skill = SkillManager(bus, Services(None, None, {"app": {}}, env), [{"type": "stats"}]).skills["stats"]
    skill.on_start()
    return skill


def decision(allowed, ts=900_000, reason="Long a favor del sesgo Bullish (puntuación +3)"):
    hit = SimpleNamespace(title="Continuación", direction="long", ts=ts)
    tbr = SimpleNamespace(zone=SimpleNamespace(name="London"), day=date(2026, 10, 6))
    return Event("cortex.decision", {"symbol": "NAS100", "timeframe": "15m", "hit": hit, "tbr": tbr,
                                     "decision": SimpleNamespace(allowed=allowed, reason=reason)}, "cortex")


def lines(folder):
    return [json.loads(line) for p in sorted(folder.glob("*.jsonl")) for line in p.read_text(encoding="utf-8").splitlines()]


def test_meses():
    assert previous_month("2026-01") == "2025-12" and next_month("2026-12") == "2027-01"
    assert month_label("2026-10") == "Octubre 2026"
    assert reason_of("ya hay una posición abierta en NAS100 (Reversión): hasta...") == "Posición abierta en el mercado"
    assert reason_of("mercado lateral: puntuación 0") == "Mercado lateral" and reason_of("algo nuevo: detalle") == "Algo nuevo"


def test_el_diario_sobrevive_al_reinicio_sin_duplicar(tmp_path):
    skill = skill_in(tmp_path)
    skill.handle(decision(True))
    skill.handle(Event("setup.executed", {"order": ORDER}, "setup"))
    skill.handle(Event("setup.closed", {"order": ORDER, "closed": WIN}, "setup"))
    other = replace(ORDER, symbol="GER40", entry_ts=1_020_000)
    skill.handle(Event("setup.executed", {"order": other}, "setup"))
    assert [r["t"] for r in lines(tmp_path)] == ["signal", "open", "close", "open"]
    assert lines(tmp_path)[1]["order"]["tbr_day"] == "2026-10-06"

    again = skill_in(tmp_path)                                  # reinicio: vuelve todo
    s = again.stats
    assert (s.go, len(s.done), s.total_r, len(s.open), len(s.stale)) == (1, 1, 2.0, 0, 1)
    assert s.done[0].order == ORDER and s.signals[0].zone == "London 06/10"
    # Cortex vuelve a anunciar los patrones recientes: nada se duplica y la abierta vuelve a estar seguida
    again.handle(decision(True))
    again.handle(Event("setup.executed", {"order": ORDER}, "setup"))
    again.handle(Event("setup.closed", {"order": ORDER, "closed": WIN}, "setup"))
    again.handle(Event("setup.executed", {"order": other}, "setup"))
    assert len(lines(tmp_path)) == 4 and (again.stats.go, len(again.stats.open), len(again.stats.stale)) == (1, 1, 0)


def test_nueva_etapa_no_borra_el_diario(tmp_path):
    skill = skill_in(tmp_path)
    skill.handle(Event("setup.closed", {"order": ORDER, "closed": WIN}, "setup"))
    skill.handle(Event("stats.reset", {}, "ui"))
    assert skill.stats.trades == [] and skill.stats.since
    assert skill_in(tmp_path).stats.trades == []                # en vivo, desde la etapa
    month = Journal(tmp_path).months()[0]
    assert Journal(tmp_path).load_month(month).total_r == 2.0   # el mes guardado, completo


def test_una_operacion_cuenta_en_el_mes_en_que_abre(tmp_path):
    sept = Journal(tmp_path, clock(2026, 9, 30, 23, 0))
    sept.signal(Signal(False, "NAS100", "15m", "Reversión", "short", "Short contra el sesgo Bullish", 990_000))
    sept.opened(ORDER)
    oct_ = Journal(tmp_path, clock(2026, 10, 1, 9, 0))
    oct_.closed(ORDER, WIN)
    assert oct_.months() == ["2026-10", "2026-09"]
    s = oct_.load_month("2026-09")
    assert (len(s.done), s.total_r, s.nogo) == (1, 2.0, 1)
    assert oct_.load_month("2026-10").trades == []
    recent = oct_.load_recent()                                 # en vivo: mes actual y anterior
    assert (len(recent.done), recent.nogo) == (1, 1)
    assert Journal(tmp_path, clock(2026, 12, 1)).load_recent().trades == []      # septiembre ya no entra en vivo


def test_lineas_rotas_se_saltan(tmp_path):
    j = Journal(tmp_path, clock(2026, 10, 18))
    j.opened(ORDER)
    with j.path("2026-10").open("a", encoding="utf-8") as f:
        f.write('{"t": "close", "order": {"symbol": "X"}\n{no es json\n')
    assert len(j.load_recent().trades) == 1


def test_area_stats_y_meses_guardados(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.ui.main_window import RIGHT_WIDTH, MainWindow
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    folder = tmp_path / "ft"
    Journal(folder, clock(2026, 9, 10)).closed(ORDER, WIN)
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": ["EURUSD"]}}
    bus = EventBus()
    env = EnvConfig(parse(f"STATS_FORWARD_DIR={folder}"))
    win = MainWindow(bus, SkillManager(bus, Services(None, None, cfg, env), [{"type": "stats"}]), cfg, "t")
    assert win.stats_area.title.text() == "Stats" and win.stats_area.width() == RIGHT_WIDTH
    assert (win.stats_btn.text(), win.backtest_btn.text()) == ("Forwardtest", "Backtest")
    win._on_stats_session({"stats": TradeStats(), "folder": str(folder)})
    win.stats_btn.click()
    dlg = win.stats_dialog
    assert [dlg.month_box.itemText(i) for i in range(dlg.month_box.count())] == ["En vivo", "Septiembre 2026"]
    assert dlg.blocks["trades"].value.text() == "0"
    dlg.set_month("2026-09")
    assert dlg.blocks["trades"].value.text() == "1" and not dlg.reset_btn.isEnabled()
    assert dlg.history.item(0, 7).text() == "+2.00 R" and "Septiembre 2026" in dlg.summary.text()
    dlg.set_month(None)
    assert dlg.month == "" and dlg.reset_btn.isEnabled()


def test_en_modo_demo_el_diario_va_aparte(tmp_path):
    from tradingbot.skills.feed.demo_data import DemoSource
    from tradingbot.skills.stats import journal
    bus = EventBus()
    skill = SkillManager(bus, Services(DemoSource(), None, {"app": {}}, EnvConfig()), [{"type": "stats"}]).skills["stats"]
    skill.on_start()
    assert skill.journal.folder == journal.DEFAULT_DIR.parent / "forwardtest-demo"
