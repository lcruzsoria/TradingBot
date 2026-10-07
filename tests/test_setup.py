"""Skill Setup: continuaciones y reversiones tras tomar la liquidez del High / Low de las zonas TBR."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import time

import numpy as np
import pandas as pd

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.setup.setups import classify, detect
from tradingbot.skills.tbr.zones import Zone, compute

from tests.test_tbr import AHEAD, candles

# Zona 10:00-11:00 (velas 0-3): High 105, Low 95. Después, la vela 4 toma el High (106).
HIGHS = [101, 105, 102, 101, 106, 104, 103, 102]
LOWS = [99, 98, 95, 99, 101, 100, 99, 98]


def sessions():
    ts, high, low = candles(10, 8, highs=HIGHS, lows=LOWS)
    return compute(ts, high, low, [Zone("NY_AM", "NY-AM", 600, 660, "#00C853")], AHEAD, 15, days=1)


def test_clasificacion_segun_el_cierre_de_confirmacion():
    assert classify("high", 105, 106) == ("continuation", "long")
    assert classify("high", 105, 104) == ("reversal", "short")
    assert classify("low", 95, 94) == ("continuation", "short")
    assert classify("low", 95, 96) == ("reversal", "long")


def test_reversion_tras_barrer_el_high():
    close = [100, 104, 100, 100, 105.5, 103, 102, 101]     # toma en la 4; la 6 (3.ª vela) cierra dentro
    [s] = detect(sessions(), close, confirm_bars=3)
    assert (s.side, s.level, s.sweep_x, s.confirm_x) == ("high", 105, 4, 6)
    assert (s.kind, s.direction) == ("reversal", "short")
    assert s.label == "Reversión Short en el High de NY-AM"


def test_continuacion_y_pendiente():
    close = [100, 104, 100, 100, 105.5, 105.8, 106, 101]
    [s] = detect(sessions(), close, confirm_bars=2)         # la 5 cierra por encima de 105
    assert (s.kind, s.direction, s.confirm_x) == ("continuation", "long", 5)
    [p] = detect(sessions(), close, confirm_bars=5)         # aún no han cerrado 5 velas desde la toma
    assert (p.kind, p.direction) == ("pending", None) and "pendiente" in p.label


def test_filtros_de_zonas_y_tipos():
    close = [100, 104, 100, 100, 105.5, 103, 102, 101]
    assert detect(sessions(), close, 3, zones=["LONDON"]) == []
    assert detect(sessions(), close, 3, zones=["ny_am"]) != []
    assert detect(sessions(), close, 3, kinds=("continuation",)) == []


def run_skill(env_text):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus, events = EventBus(), []
    bus.subscribe("t", "setup.updated", events.append)
    manager = SkillManager(bus, Services(None, None, {"app": {}}, EnvConfig(parse(env_text))),
                           [{"type": "tbr"}, {"type": "setup"}])
    manager.start()
    ts, high, low = candles(10, 8, highs=HIGHS, lows=LOWS)
    df = pd.DataFrame({"ts": ts, "high": high, "low": low,
                       "close": np.array([100, 104, 100, 100, 105.5, 103, 102, 101], dtype=float)})
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "15m", "df": df}, source="feed")
    deadline = time.time() + 3
    while not events and time.time() < deadline:
        time.sleep(0.02)
    manager.stop()
    return manager.skills["setup"], events


def test_la_skill_publica_los_setups_de_las_zonas_tbr():
    skill, events = run_skill("TBR_ZONES=ny_am\nTBR_NY_AM_HOURS=10:00-11:00\nTBR_DAYS=1\n")
    p = events[-1].payload
    assert p["symbol"] == "EURUSD" and p["confirm_bars"] == 3
    assert p["last"].label == "Reversión Short en el High de NY-AM"


def test_la_skill_rechaza_valores_no_validos():
    skill, events = run_skill("SETUP_CONFIRM_BARS=0\n")
    assert skill.state.value == "error" and "SETUP_CONFIRM_BARS" in skill.note and not events
    skill, events = run_skill("SETUP_TYPES=breakout\n")
    assert skill.state.value == "error" and "SETUP_TYPES" in skill.note
