"""Niveles del día (TDO, Midnight, PDH / PDL) y separadores de día."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.levels import daylevels as levels
from tradingbot.skills.levels.daylevels import compute, days, is_us_index, parse_time

AHEAD = 7 * 3600                                       # servidor = NY + 7 h
DAY0 = int(datetime(2026, 10, 6, tzinfo=timezone.utc).timestamp())   # martes 6 oct, 00:00 del servidor
FOREX, INDEX = 17 * 60, 18 * 60                        # inicio del día en NY: 17:00 / 18:00


def hourly(n_days: int = 3):
    """Velas H1 de 00:00 a 23:00 del servidor (00:00 servidor = 17:00 NY; 01:00 servidor = 18:00 NY)."""
    ts = [DAY0 + d * 86400 + h * 3600 for d in range(n_days) for h in range(24)]
    base = np.arange(len(ts), dtype=float)
    return np.array(ts, dtype=np.int64), base + 0.5, base + 1.0, base


def by_kind(lines, kind):
    return [line for line in lines if line.kind == kind]


def test_inicio_del_dia_segun_el_activo():
    assert parse_time("17:00", "K") == 1020 and parse_time("9:30", "K") == 570
    with pytest.raises(ValueError, match="HH:MM"):
        parse_time("25:00", "LEVELS_DAY_START")
    indices = levels.DEFAULT_US_INDICES
    assert is_us_index("NAS100.r", indices) and is_us_index("nas100ft.r", indices) and is_us_index("SP500", indices)
    assert not is_us_index("EURUSD", indices) and not is_us_index("XAUUSD", indices)
    ts, *_ = hourly(3)
    # forex: el día empieza a las 17:00 NY = vela 00:00 del servidor
    assert [d.x0 for d in days(ts, AHEAD, FOREX)] == [-0.5, 23.5, 47.5]
    # índices: a las 18:00 NY = vela 01:00 del servidor (la de las 00:00 es aún del día anterior)
    assert [d.x0 for d in days(ts, AHEAD, INDEX)] == [-0.5, 0.5, 24.5, 48.5]


def test_nombre_del_dia_centrado_entre_separadores():
    ts, *_ = hourly(3)
    d = days(ts, AHEAD, FOREX)
    # el día que empieza el lunes 5 a las 17:00 NY (servidor martes 00:00) es el MARTES
    assert [x.label for x in d] == ["MARTES", "MIÉRCOLES", "JUEVES"]
    assert d[1].center == (23.5 + 47.5) / 2                    # entre su separador y el siguiente
    assert d[-1].x1 == len(ts) - 0.5                           # el de hoy, hasta la última vela


def test_tdo_midnight_pdh_y_pdl_de_cada_dia():
    ts, o, h, l = hourly(3)
    lines = compute(ts, o, h, l, AHEAD, FOREX, days_back=10)
    tdo = by_kind(lines, "tdo")
    assert [t.price for t in tdo] == [0.5, 24.5, 48.5]                   # open de la vela de las 17:00 NY
    assert (tdo[0].x0, tdo[0].x1) == (-0.5, 23.5)
    assert tdo[-1].x1 == len(ts) - 1 + levels.EXTEND_BARS
    midnight = by_kind(lines, "midnight")                                # 00:00 NY = 07:00 del servidor
    assert [m.price for m in midnight] == [7.5, 31.5, 55.5] and midnight[0].x0 == 6.5
    pdh, pdl = by_kind(lines, "pdh"), by_kind(lines, "pdl")
    assert [p.price for p in pdh] == [24.0, 48.0] and [p.price for p in pdl] == [0.0, 24.0]
    assert (pdh[0].x0, pdh[0].x1) == (23.5, 47.5)
    # índices: el TDO es la vela de las 18:00 NY
    assert [t.price for t in by_kind(compute(ts, o, h, l, AHEAD, INDEX), "tdo")][1:] == [1.5, 25.5, 49.5]


def test_solo_los_ultimos_dias_y_sin_velas():
    ts, o, h, l = hourly(5)
    assert len(by_kind(compute(ts, o, h, l, AHEAD, FOREX, days_back=2), "tdo")) == 2
    assert compute(np.array([], dtype=np.int64), [], [], [], AHEAD, FOREX) == []
    assert days(np.array([], dtype=np.int64), AHEAD, FOREX) == []


def run_skill(env_text, timeframe="1h", symbol="EURUSD"):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus, events = EventBus(), []
    bus.subscribe("t", "levels.updated", events.append)
    manager = SkillManager(bus, Services(None, None, {"app": {}}, EnvConfig(parse(env_text))), [{"type": "levels"}])
    manager.start()
    ts, o, h, l = hourly(3)
    df = pd.DataFrame({"ts": ts, "open": o, "high": h, "low": l})
    bus.publish("candles.loaded", {"symbol": symbol, "timeframe": timeframe, "df": df}, source="feed")
    deadline = time.time() + 3
    while not events and time.time() < deadline:
        time.sleep(0.02)
    manager.stop()
    return manager.skills["levels"], events


def test_la_skill_usa_la_hora_de_inicio_de_cada_activo():
    _, events = run_skill("LEVELS_PDHL_COLOR=#00ff00\n")
    p = events[-1].payload
    assert p["available"] and p["day_start"] == FOREX and len(p["days"]) == 3 and p["colors"]["pdhl"] == "#00FF00"
    assert {line.kind for line in p["lines"]} == {"tdo", "midnight", "pdh", "pdl"}
    _, events = run_skill("", symbol="NAS100.r")
    assert events[-1].payload["day_start"] == INDEX and len(events[-1].payload["days"]) == 4
    _, events = run_skill("LEVELS_US_INDICES=GER40\nLEVELS_INDEX_DAY_START=19:30\n", symbol="ger40.r")
    assert events[-1].payload["day_start"] == 19 * 60 + 30
    _, events = run_skill("LEVELS_SEPARATORS=false\n", timeframe="1d")
    assert events[-1].payload["available"] is False and events[-1].payload["lines"] == []
    skill, events = run_skill("LEVELS_DAY_START=5pm\n")
    assert skill.state.value == "error" and "LEVELS_DAY_START" in skill.note and not events


def test_los_botones_muestran_cada_nivel(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "1h", "watchlist": ["EURUSD"]}}
    bus = EventBus()
    env = EnvConfig(parse("LEVELS_SHOW_PDHL=true\n"))
    win = MainWindow(bus, SkillManager(bus, Services(None, None, cfg, env), [{"type": "levels"}]), cfg, "t")
    assert [b.text() for b in win.level_btns.values()] == ["TDO", "Midnight", "PDH/PDL"]
    assert win.level_btns["pdhl"].isChecked() and not win.level_btns["tdo"].isChecked()   # LEVELS_SHOW_PDHL
    ts, o, h, l = hourly(3)
    df = pd.DataFrame({"ts": ts, "open": o, "high": h, "low": l, "close": o, "time": pd.to_datetime(ts, unit="s")})
    win._on_candles({"df": df, "symbol": "EURUSD", "timeframe": "1h", "seconds": 0.1})
    win._on_day_levels({"symbol": "EURUSD", "timeframe": "1h", "lines": compute(ts, o, h, l, AHEAD, FOREX),
                        "days": days(ts, AHEAD, FOREX), "day_start": FOREX, "available": True, "estimated": False,
                        "max_tf": 720,
                        "colors": {"tdo": "#787B86", "midnight": "#FF9800", "pdhl": "#2962FF", "separator": "#787B86"}})
    only_pdhl = win.chart.day_item_count                    # 2 curvas + 4 rótulos (PDH y PDL de 2 días)
    assert only_pdhl == 6
    win.level_btns["tdo"].setChecked(True)
    assert win.chart.day_item_count == only_pdhl + 1 + 3   # + curva TDO y sus 3 rótulos
    win.level_btns["tdo"].setChecked(False)
    win.level_btns["pdhl"].setChecked(False)
    assert win.chart.day_item_count == 0
    seps = win.chart.separators                             # no dependen de los botones
    assert list(seps._x) == [23.5, 47.5] and seps._labels == ["MARTES", "MIÉRCOLES", "JUEVES"]
    assert list(seps._centers) == [11.5, 35.5, 59.5]
