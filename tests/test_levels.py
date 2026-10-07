"""Niveles del día (TDO, Midnight, PDH / PDL) y separadores de día."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from tradingbot.skills.levels import daylevels as levels
from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.levels.daylevels import compute, separators

AHEAD = 7 * 3600                                       # servidor = NY + 7 h
DAY0 = int(datetime(2026, 10, 6, tzinfo=timezone.utc).timestamp())   # martes 6 oct (día del servidor)


def hourly(days: int = 3, first_hour: int = 1):
    """Velas H1 de varios días del servidor, de `first_hour` a 23 h (como Vantage: sin la vela de las 00:00)."""
    ts = [DAY0 + d * 86400 + h * 3600 for d in range(days) for h in range(first_hour, 24)]
    n = len(ts)
    base = np.arange(n, dtype=float)
    return np.array(ts, dtype=np.int64), base + 0.5, base + 1.0, base


def by_kind(lines, kind):
    return [line for line in lines if line.kind == kind]


def test_tdo_midnight_pdh_y_pdl_de_cada_dia():
    ts, o, h, l = hourly(3)                            # 23 velas por día (01:00 a 23:00 del servidor)
    lines = compute(ts, o, h, l, AHEAD, days=10)
    tdo = by_kind(lines, "tdo")
    assert [t.price for t in tdo] == [0.5, 23.5, 46.5]                   # open de la primera vela de cada día
    assert (tdo[0].x0, tdo[0].x1) == (-0.5, 22.5)                        # todo el día...
    assert tdo[-1].x1 == len(ts) - 1 + levels.EXTEND_BARS                # ...y el de hoy, algo más allá
    midnight = by_kind(lines, "midnight")                                # 00:00 NY = 07:00 del servidor
    assert [m.price for m in midnight] == [6.5, 29.5, 52.5] and midnight[0].x0 == 5.5
    pdh, pdl = by_kind(lines, "pdh"), by_kind(lines, "pdl")
    assert [p.price for p in pdh] == [23.0, 46.0] and [p.price for p in pdl] == [0.0, 23.0]   # del día anterior
    assert (pdh[0].x0, pdh[0].x1) == (22.5, 45.5)                        # se dibujan sobre el día siguiente


def test_solo_los_ultimos_dias_y_sin_velas():
    ts, o, h, l = hourly(5)
    assert len(by_kind(compute(ts, o, h, l, AHEAD, days=2), "tdo")) == 2
    assert compute(np.array([], dtype=np.int64), [], [], [], AHEAD) == []


def test_separadores_con_el_nombre_del_dia():
    ts, *_ = hourly(3)
    seps = separators(ts)
    assert [(s.x, s.label) for s in seps] == [(22.5, "MIÉRCOLES"), (45.5, "JUEVES")]
    assert separators(ts[:1]) == []


def run_skill(env_text, timeframe="1h"):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus, events = EventBus(), []
    bus.subscribe("t", "levels.updated", events.append)
    manager = SkillManager(bus, Services(None, None, {"app": {}}, EnvConfig(parse(env_text))), [{"type": "levels"}])
    manager.start()
    ts, o, h, l = hourly(3)
    df = pd.DataFrame({"ts": ts, "open": o, "high": h, "low": l})
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": timeframe, "df": df}, source="feed")
    deadline = time.time() + 3
    while not events and time.time() < deadline:
        time.sleep(0.02)
    manager.stop()
    return manager.skills["levels"], events


def test_la_skill_publica_niveles_y_separadores():
    _, events = run_skill("LEVELS_PDHL_COLOR=#00ff00\n")
    p = events[-1].payload
    assert p["available"] and len(p["separators"]) == 2 and p["colors"]["pdhl"] == "#00FF00"
    assert {line.kind for line in p["lines"]} == {"tdo", "midnight", "pdh", "pdl"}
    _, events = run_skill("LEVELS_SEPARATORS=false\n", timeframe="1d")
    assert events[-1].payload["available"] is False and events[-1].payload["lines"] == []
    skill, events = run_skill("LEVELS_TDO_COLOR=gris\n")
    assert skill.state.value == "error" and "LEVELS_TDO_COLOR" in skill.note and not events


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
    win._on_day_levels({"symbol": "EURUSD", "timeframe": "1h", "lines": compute(ts, o, h, l, AHEAD),
                        "separators": separators(ts), "available": True, "estimated": False, "max_tf": 720,
                        "colors": {"tdo": "#787B86", "midnight": "#FF9800", "pdhl": "#2962FF", "separator": "#787B86"}})
    only_pdhl = win.chart.day_item_count                    # 2 curvas + 4 rótulos (PDH y PDL de 2 días)
    assert only_pdhl == 6
    win.level_btns["tdo"].setChecked(True)
    assert win.chart.day_item_count == only_pdhl + 1 + 3   # + curva TDO y sus 3 rótulos
    win.level_btns["tdo"].setChecked(False)
    win.level_btns["pdhl"].setChecked(False)
    assert win.chart.day_item_count == 0
    assert len(win.chart.separators._labels) == 2          # los separadores no dependen de los botones
