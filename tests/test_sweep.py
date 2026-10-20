"""Barrido de la watchlist en segundo plano: todos los mercados se evalúan aunque no estén en pantalla."""
import time
from datetime import date

import numpy as np
import pandas as pd
import pytest

from tradingbot.core import Event, EventBus, Services, SkillManager
from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.bias.models import Bias, BiasResult
from tradingbot.skills.feed.skill import sweep_settings
from tradingbot.skills.pattern.patterns import ActiveTbr, PatternHit
import tradingbot.skills  # noqa: F401


class FakeSource:
    def __init__(self):
        self.recent = []

    def connect(self):
        return "ok"

    def symbols(self):
        return []

    def all_symbols(self):
        return []

    def load_candles(self, symbol, tf, progress=None):
        return candles()

    def load_recent(self, symbol, tf, bars):
        self.recent.append((symbol, tf, bars))
        if symbol == "MALO":
            raise RuntimeError("no existe")
        return candles()


def candles(n=200, start=1_790_000_000):
    ts = start + 900 * np.arange(n)
    close = 1.0 + 0.001 * np.sin(np.arange(n) / 5)
    return pd.DataFrame({"ts": ts, "time": pd.to_datetime(ts, unit="s"), "open": close, "high": close + 0.001,
                         "low": close - 0.001, "close": close, "tick_volume": 1})


def feed(env_text="", watchlist=("EURUSD", "XAUUSD", "MALO")):
    bus, out = EventBus(), []
    bus.subscribe("t", "*", out.append)
    cfg = {"app": {"timeframe": "15m", "watchlist": list(watchlist)}}
    src = FakeSource()
    skill = SkillManager(bus, Services(src, None, cfg, EnvConfig(parse(env_text))), [{"type": "feed"}]).skills["feed"]
    skill.on_start()
    return skill, src, out


def test_ajustes_del_barrido():
    assert sweep_settings(EnvConfig(), {"timeframe": "5m"}) == (5.0, "5m", 10)
    env = EnvConfig(parse("FEED_SWEEP_MINUTES=2\nFEED_SWEEP_TIMEFRAME=M15\nFEED_SWEEP_DAYS=3\n")).section("FEED")
    assert sweep_settings(env, {"timeframe": "5m"}) == (2.0, "15m", 3)
    for bad in ("FEED_SWEEP_MINUTES=-1", "FEED_SWEEP_DAYS=0", "FEED_SWEEP_TIMEFRAME=X9"):
        with pytest.raises(ValueError, match=bad.split("=")[0]):
            sweep_settings(EnvConfig(parse(bad)).section("FEED"), {})


def test_el_barrido_carga_toda_la_watchlist_sin_tocar_el_grafico():
    skill, src, out = feed()
    skill.handle(Event("feed.load", {"symbol": "EURUSD", "timeframe": "5m"}, "ui"))
    topics = [e.topic for e in out if e.topic in ("feed.sweep", "candles.loaded")]
    # el barrido se anuncia antes que las velas del gráfico (así Cortex retiene también sus patrones)
    assert topics == ["feed.sweep", "candles.loaded", "candles.loaded", "candles.loaded", "feed.sweep"]
    start, chart, *swept, end = [e.payload for e in out if e.topic in ("feed.sweep", "candles.loaded")]
    assert start["stage"] == "start" and start["symbols"] == ["EURUSD", "XAUUSD", "MALO"]
    assert not chart.get("background") and chart["timeframe"] == "5m"
    assert [p["symbol"] for p in swept] == ["EURUSD", "XAUUSD"]
    assert all(p["background"] and p["sweep"] == start["id"] and p["timeframe"] == "15m" for p in swept)
    assert end["stage"] == "end" and end["loaded"] == ["EURUSD", "XAUUSD"] and "MALO" in end["failed"]
    assert src.recent[0] == ("EURUSD", "15m", 960)                       # 10 días de velas de 15 min
    n = len(out)
    skill.tick()                                                        # la siguiente vuelta, dentro de 5 minutos
    assert not any(e.topic == "feed.sweep" for e in out[n:])


def test_el_barrido_sigue_la_watchlist_y_se_puede_apagar():
    skill, src, out = feed("FEED_SWEEP_MINUTES=0\n")
    skill.handle(Event("feed.load", {"symbol": "EURUSD", "timeframe": "5m"}, "ui"))
    assert not any(e.topic == "feed.sweep" for e in out)
    skill, src, out = feed()
    skill.handle(Event("watchlist.changed", {"symbols": ["BTCUSD"]}, "ui"))
    skill.handle(Event("feed.load", {"symbol": "EURUSD", "timeframe": "5m"}, "ui"))
    assert [p for p in (e.payload for e in out if e.topic == "feed.sweep")][0]["symbols"] == ["BTCUSD"]


def test_el_sesgo_del_barrido_no_cambia_el_del_grafico():
    from tradingbot.skills.bias import BiasEngine
    from tradingbot.skills.bias.rules import PrevDayBreak
    bus, out = EventBus(), []
    bus.subscribe("t", "bias.*", out.append)
    skill = SkillManager(bus, Services(None, BiasEngine([PrevDayBreak()]), {"app": {}}, EnvConfig()),
                         [{"type": "bias"}]).skills["bias"]
    skill.on_start()
    skill.handle(Event("candles.loaded", {"symbol": "XAUUSD", "timeframe": "15m", "df": candles(), "background": True,
                                          "sweep": 3}, "feed"))
    assert [e.topic for e in out] == ["bias.updated"]                   # sin histórico ni recálculo programado
    p = out[0].payload
    assert p["symbol"] == "XAUUSD" and p["background"] and p["sweep"] == 3
    assert skill.result is None and skill._last is None


def test_pattern_avisa_de_cada_mercado_repasado():
    bus, out = EventBus(), []
    bus.subscribe("t", "pattern.*", out.append)
    skill = SkillManager(bus, Services(None, None, {"app": {}}, EnvConfig()), [{"type": "pattern"}]).skills["pattern"]
    skill.on_start()
    mark = {"background": True, "sweep": 1}
    skill.handle(Event("candles.loaded", {"symbol": "XAUUSD", "timeframe": "15m", "df": candles(), **mark}, "feed"))
    assert out == []                                                    # aún faltan sus TBR
    skill.handle(Event("tbr.updated", {"symbol": "XAUUSD", "timeframe": "15m", "sessions": [], "available": False,
                                       **mark}, "tbr"))
    assert [e.topic for e in out] == ["pattern.updated", "pattern.swept"]
    assert all(e.payload["background"] and e.payload["symbol"] == "XAUUSD" for e in out)
    assert skill._candles is None                                       # el gráfico no cambia


TBR = ActiveTbr("NY_AM", "NY Open", date(2026, 10, 19), 105.0, 95.0, -0.5, 9.5)


def bias(kind=Bias.BULLISH):
    return BiasResult(kind, None, (), {}, "resumen", 3.0, 3.0, False)


def test_cortex_decide_la_vuelta_entera_en_orden_de_hora():
    bus, decisions = EventBus(), []
    bus.subscribe("t", "cortex.decision", decisions.append)
    manager = SkillManager(bus, Services(None, None, {"app": {}}, EnvConfig()), [{"type": "cortex"}])
    manager.start()
    mark = {"background": True, "sweep": 7}
    bus.publish("feed.sweep", {"stage": "start", "id": 7, "symbols": ["NAS100", "XAUUSD"]}, source="feed")
    for symbol, ts in (("NAS100", 2_000), ("XAUUSD", 1_000)):            # el de las 10:00 llega antes que el de las 09:00
        hit = PatternHit("p", "Patrón", "long", 13, 100.0, "", {"stop": 95.0, "target": 115.0}, ts)
        bus.publish("pattern.detected", {"symbol": symbol, "timeframe": "15m", "tbr": TBR, "hit": hit, **mark},
                    source="pattern")
        bus.publish("bias.updated", {"result": bias(), "symbol": symbol, "timeframe": "15m", **mark}, source="bias")
        bus.publish("pattern.swept", {"symbol": symbol, "timeframe": "15m", **mark}, source="pattern")
    time.sleep(0.3)
    assert decisions == []                                              # el barrido aún no ha terminado
    bus.publish("feed.sweep", {"stage": "end", "id": 7, "loaded": ["NAS100", "XAUUSD"], "failed": {}}, source="feed")
    deadline = time.time() + 3
    while len(decisions) < 2 and time.time() < deadline:
        time.sleep(0.02)
    manager.stop()
    first, second = (d.payload for d in decisions)
    assert first["symbol"] == "XAUUSD" and first["decision"].allowed       # el primero en el tiempo se queda la posición
    assert second["symbol"] == "NAS100" and not second["decision"].allowed  # una sola posición en toda la cuenta
    assert "ya hay una posición abierta en XAUUSD" in second["decision"].reason
