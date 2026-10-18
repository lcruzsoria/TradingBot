"""Skill Feed en directo: recarga las velas cuando el terminal tiene una vela nueva del mercado que se muestra."""
import pandas as pd

from tradingbot.core import Event, EventBus, Services, SkillManager
from tradingbot.envconfig import EnvConfig
import tradingbot.skills  # noqa: F401


class FakeSource:
    def __init__(self):
        self.bars = [1_000, 1_900]           # horas de las velas que tiene el terminal
        self.loads = 0

    def connect(self):
        return "ok"

    def symbols(self):
        return ["ETHUSD.bc"]

    def all_symbols(self):
        return ["ETHUSD.bc"]

    def load_candles(self, symbol, tf, progress=None):
        self.loads += 1
        return pd.DataFrame({"ts": self.bars, "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0})

    def last_bar_ts(self, symbol, tf):
        return self.bars[-1]


def feed(source):
    bus = EventBus()
    out = []
    bus.subscribe("test", "candles.loaded", out.append)
    skill = SkillManager(bus, Services(source, None, {"app": {}}, EnvConfig()), [{"type": "feed"}]).skills["feed"]
    skill.on_start()
    return skill, out


def test_recarga_solo_cuando_hay_una_vela_nueva():
    src = FakeSource()
    skill, out = feed(src)
    skill.tick()                                                        # sin nada cargado: no hace nada
    skill.handle(Event("feed.load", {"symbol": "ETHUSD.bc", "timeframe": "15m"}, "ui"))
    skill.tick()
    assert src.loads == 1 and len(out) == 1 and not out[0].payload["refresh"]
    src.bars.append(2_800)                                              # el terminal ya tiene otra vela
    skill.tick()
    assert src.loads == 2 and out[-1].payload["refresh"] and out[-1].payload["reason"] == "live"
    assert int(out[-1].payload["df"]["ts"].iloc[-1]) == 2_800
    skill.tick()
    assert src.loads == 2


def test_sin_last_bar_ts_no_hay_directo():
    class Plain(FakeSource):
        last_bar_ts = None
    src = Plain()
    skill, out = feed(src)
    skill.handle(Event("feed.load", {"symbol": "ETHUSD.bc", "timeframe": "15m"}, "ui"))
    src.bars.append(2_800)
    skill.tick()
    assert src.loads == 1
