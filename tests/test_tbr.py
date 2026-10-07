"""Zonas TBR (hora de Nueva York) y sus niveles High / Low / 50 %."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

from tradingbot.skills.tbr import zones as tbr
from tradingbot.envconfig import EnvConfig, parse
from tradingbot.clock import server_minus_ny
from tradingbot.skills.tbr.zones import Zone, compute, parse_hours, zones_from_settings

AHEAD = 7 * 3600                                      # servidor = NY + 7 h
NY_DAY = datetime(2026, 10, 6, tzinfo=timezone.utc)   # medianoche NY del día de prueba (como época "ingenua")


def server_ts(hour: float, day_shift: int = 0) -> int:
    """Hora del servidor de una vela que en Nueva York abre a `hour` del día de prueba."""
    return int(NY_DAY.timestamp() + day_shift * 86400 + hour * 3600 + AHEAD)


def candles(start_hour: float, count: int, tf_min: int = 15, highs=None, lows=None):
    ts = np.array([server_ts(start_hour + i * tf_min / 60) for i in range(count)], dtype=np.int64)
    high = np.array(highs if highs is not None else [100.0] * count, dtype=float)
    low = np.array(lows if lows is not None else [99.0] * count, dtype=float)
    return ts, high, low


def zone(start, end, key="Z"):
    s, e = parse_hours(f"{start}-{end}")
    return Zone(key, key, s, e, "#FF0000")


def test_horarios_y_zonas_por_defecto():
    assert parse_hours("20:00-00:00") == (1200, 0) and parse_hours("13:30-16:30") == (810, 990)
    assert zone("20:00", "00:00").minutes == 240 and zone("22:00", "02:00").minutes == 240
    with pytest.raises(ValueError, match="HH:MM"):
        parse_hours("20h-24h")
    zones = zones_from_settings(EnvConfig())
    assert [(z.name, z.hours) for z in zones] == [("Asia", "20:00-00:00"), ("London", "02:00-05:00"),
                                                   ("Pre-NY", "09:00-10:00"), ("NY-AM", "10:00-12:00"),
                                                   ("NY-PM", "13:30-16:30")]


def test_zonas_desde_tradingbot_env():
    env = EnvConfig(parse("TBR_ZONES=ny_am, kz\nTBR_NY_AM_COLOR=#123456\nTBR_KZ_NAME=Killzone\n"
                          "TBR_KZ_HOURS=07:00-09:00\nTBR_KZ_COLOR=#abcdef\n")).section("TBR")
    zones = zones_from_settings(env)
    assert [(z.key, z.name, z.hours, z.color) for z in zones] == [
        ("NY_AM", "NY-AM", "10:00-12:00", "#123456"), ("KZ", "Killzone", "07:00-09:00", "#ABCDEF")]
    with pytest.raises(ValueError, match="TBR_X_HOURS"):
        zones_from_settings(EnvConfig(parse("TBR_ZONES=X\n")).section("TBR"))
    with pytest.raises(ValueError, match="RRGGBB"):
        zones_from_settings(EnvConfig(parse("TBR_ASIA_COLOR=amarillo\n")).section("TBR"))


def test_niveles_high_low_y_50_se_prolongan_hasta_que_se_toman():
    # Zona 10:00-11:00 (4 velas de M15): máximo 105, mínimo 95, 50 % = 100.
    highs = [101, 105, 102, 101,   103, 104, 106, 104]
    lows = [99, 98, 95, 99,        101, 100.5, 101, 99]
    ts, high, low = candles(10, 8, highs=highs, lows=lows)
    [s] = compute(ts, high, low, [zone("10:00", "11:00")], AHEAD, 15, days=1)
    assert (s.x0, s.x1, s.complete, s.high, s.low) == (-0.5, 3.5, True, 105, 95)   # caja del Low al High
    lv = {level.kind: level for level in s.levels}
    assert (lv["high"].price, lv["low"].price, lv["mid"].price) == (105, 95, 100)
    assert lv["high"].taken and lv["high"].x1 == 6           # la vela 6 (máx. 106) toma el High
    assert lv["mid"].taken and lv["mid"].x1 == 7             # la 7 baja hasta 99: toca el 50 %
    assert not lv["low"].taken and lv["low"].x1 == 7 + tbr.EXTEND_BARS   # intacto: hasta el borde derecho
    assert all(level.x0 == s.x1 for level in s.levels)       # salen del borde derecho de la caja


def test_zona_que_cruza_medianoche_y_zona_en_curso_sin_niveles():
    ts, high, low = candles(19, 24)                         # 19:00 a 00:45 en M15
    [asia] = compute(ts, high, low, [zone("20:00", "00:00")], AHEAD, 15, days=2)
    assert (asia.x0, asia.x1, asia.complete) == (3.5, 19.5, True)   # velas de 20:00 a 23:45
    ts, high, low = candles(10, 4)                          # NY-AM aún abierta: 10:00 a 10:45
    [live] = compute(ts, high, low, [zone("10:00", "12:00")], AHEAD, 15, days=1)
    assert not live.complete and live.levels == () and (live.high, live.low) == (100, 99)   # la caja ya crece


def test_con_h1_la_zona_1330_recoge_las_velas_que_se_solapan():
    ts, high, low = candles(12, 6, tf_min=60)               # 12:00 ... 17:00
    [s] = compute(ts, high, low, [zone("13:30", "16:30")], AHEAD, 60, days=1)
    assert (s.x0, s.x1) == (0.5, 4.5)                       # velas de 13:00, 14:00, 15:00 y 16:00


def test_desfase_del_servidor():
    ts, high, low = candles(10, 8)
    # si el servidor fuera NY + 6 h, la misma vela de las 10:00 (servidor) serían las 11:00 en NY
    [s] = compute(ts, high, low, [zone("11:00", "12:00")], 6 * 3600, 15, days=1)
    assert s.x0 == -0.5
    assert server_minus_ny(None) == (7 * 3600, True)
    summer = datetime(2026, 7, 1, 12, tzinfo=timezone.utc)
    assert server_minus_ny(3 * 3600, summer) == (7 * 3600, False)  # servidor UTC+3, NY UTC-4
    assert server_minus_ny(2 * 3600, datetime(2026, 1, 15, 12, tzinfo=timezone.utc)) == (7 * 3600, False)


def test_solo_los_ultimos_dias_y_sin_velas_no_hay_zona():
    ts = np.array([server_ts(10, d) for d in range(5)], dtype=np.int64)
    sessions = compute(ts, np.ones(5), np.ones(5), [zone("10:00", "11:00")], AHEAD, 15, days=2)
    assert len(sessions) == 2
    assert compute(ts, np.ones(5), np.ones(5), [zone("03:00", "04:00")], AHEAD, 15, days=5) == []
    assert compute(np.array([], dtype=np.int64), [], [], [zone("10:00", "11:00")], AHEAD, 15) == []


def run_skill(env_text, timeframe="15m", offset=None):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus, events = EventBus(), []
    bus.subscribe("t", "tbr.updated", events.append)
    env = EnvConfig(parse(env_text))
    manager = SkillManager(bus, Services(None, None, {"app": {}}, env), [{"type": "tbr"}])
    manager.start()
    ts, high, low = candles(9, 16)
    df = pd.DataFrame({"ts": ts, "high": high, "low": low})
    if offset is not None:
        bus.publish("clock.offset", {"server_offset": offset, "offset_source": "detectado"}, source="quotes")
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": timeframe, "df": df}, source="feed")
    deadline = time.time() + 3
    while not events and time.time() < deadline:
        time.sleep(0.02)
    manager.stop()
    return manager.skills["tbr"], events


def test_la_skill_publica_las_zonas():
    skill, events = run_skill("TBR_OPACITY=20\nTBR_LINE_OPACITY=50\nTBR_DAYS=1\n", offset=None)
    p = events[-1].payload
    assert p["available"] and p["estimated"] and p["opacity"] == 0.2 and p["line_opacity"] == 0.5
    assert [s.zone.name for s in p["sessions"]] == ["Pre-NY", "NY-AM"]
    _, events = run_skill("", timeframe="4h")
    assert events[-1].payload["available"] is False and events[-1].payload["sessions"] == []


def test_la_skill_rechaza_valores_no_validos():
    skill, events = run_skill("TBR_OPACITY=150\n")
    assert skill.state.value == "error" and "TBR_OPACITY" in skill.note and not events
    skill, events = run_skill("TBR_LINE_OPACITY=-5\n")
    assert skill.state.value == "error" and "TBR_LINE_OPACITY" in skill.note and not events


def test_el_boton_tbr_muestra_y_oculta_las_zonas(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": ["EURUSD"]}}
    bus = EventBus()
    env = EnvConfig(parse("TBR_SHOW=false\n"))
    win = MainWindow(bus, SkillManager(bus, Services(None, None, cfg, env), [{"type": "tbr"}]), cfg, "t")
    assert win.tbr_btn.isVisible() or not win.isVisible()
    assert win.tbr_btn.text() == "TBR" and not win.tbr_btn.isChecked()
    assert win.chart_panel.note.text() == ""                  # ya no está el texto "Precio bid - hora del servidor"
    ts, high, low = candles(9, 16, highs=[100 + i % 3 for i in range(16)])
    df = pd.DataFrame({"ts": ts, "open": high, "high": high, "low": low, "close": low,
                       "time": pd.to_datetime(ts, unit="s")})
    win._on_candles({"df": df, "symbol": "EURUSD", "timeframe": "15m", "seconds": 0.1})
    sessions = compute(ts, high, low, zones_from_settings(EnvConfig()), AHEAD, 15, 1)
    win._on_tbr({"symbol": "EURUSD", "timeframe": "15m", "sessions": sessions, "available": True,
                 "estimated": False, "opacity": 0.15, "zones": zones_from_settings(EnvConfig()), "max_tf": 60})
    assert win.chart.tbr_item_count == 0                      # calculadas, pero ocultas
    win.tbr_btn.setChecked(True)
    assert win.chart.tbr_item_count > 0
    win.tbr_btn.setChecked(False)
    assert win.chart.tbr_item_count == 0
    win._on_tbr({"symbol": "EURUSD", "timeframe": "15m", "sessions": [], "available": False, "estimated": False,
                 "opacity": 0.15, "zones": [], "max_tf": 60})
    assert not win.tbr_btn.isEnabled() and "H1" in win.tbr_btn.toolTip()
