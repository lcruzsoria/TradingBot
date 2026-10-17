"""Skill Pattern: TBR activa, registro de patrones y validación con el sesgo (GO / NO GO)."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import time
from datetime import date

import numpy as np
import pandas as pd
import pytest

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.bias.models import Bias, BiasResult
from tradingbot.skills.pattern.patterns import (PATTERN_REGISTRY, Pattern, PatternContext, PatternHit, active_tbr,
                                                register_pattern, validate)
from tradingbot.skills.tbr.zones import Session, Zone

ASIA = Zone("ASIA", "Asia", 1200, 0, "#FFD60A")
LONDON = Zone("LONDON", "London", 120, 300, "#FF3B30")
NY = Zone("NY_AM", "NY Open", 600, 720, "#00C853")


def session(zone, day, x1, high=105.0, low=95.0, complete=True):
    return Session(zone, day, x1 - 10, x1, complete, high, low)


def bias(kind, score=3.0):
    return BiasResult(kind, None, (), {}, "resumen", score, 3.0)


class RompeElHigh(Pattern):
    """Patrón de prueba: un cierre por encima del High de la TBR activa."""
    title = "Cierre sobre el High"

    def detect(self, ctx: PatternContext):
        out = []
        for i in range(ctx.first_bar, ctx.last_bar + 1):
            if ctx.close[i] > ctx.tbr.high:
                out.append(PatternHit(self.key, self.title, "long", i, ctx.tbr.high, "cierre sobre el High",
                                      {"stop": ctx.tbr.low}))
                break
        return out


@pytest.fixture
def registry(monkeypatch):
    monkeypatch.setitem(PATTERN_REGISTRY, "rompe_high", RompeElHigh)
    monkeypatch.setattr(RompeElHigh, "key", "rompe_high", raising=False)
    return PATTERN_REGISTRY


def test_el_decorador_registra_un_patron_con_su_clave():
    try:
        register_pattern("temporal")(RompeElHigh)
        assert PATTERN_REGISTRY["temporal"] is RompeElHigh and RompeElHigh.key == "temporal"
    finally:
        PATTERN_REGISTRY.pop("temporal", None)


def test_la_tbr_activa_es_la_ultima_cerrada():
    sessions = [session(ASIA, date(2026, 10, 5), 20.5), session(LONDON, date(2026, 10, 6), 50.5, 108, 92),
                session(NY, date(2026, 10, 6), 90.5, complete=False)]
    tbr = active_tbr(sessions)
    assert (tbr.zone, tbr.high, tbr.low, tbr.mid) == ("London", 108.0, 92.0, 100.0)     # la de NY aún no ha cerrado
    assert tbr.first_bar == 51 and tbr.range == 16.0
    assert active_tbr(sessions, ["asia"]).zone == "Asia"                                 # solo las zonas pedidas
    assert active_tbr([session(NY, date(2026, 10, 6), 90.5, complete=False)]) is None
    assert active_tbr([]) is None


def test_el_sesgo_valida_el_patron():
    long_hit = PatternHit("p", "P", "long", 10, 100.0)
    short_hit = PatternHit("p", "P", "short", 10, 100.0)
    assert validate(long_hit, bias(Bias.BULLISH)).allowed and not validate(short_hit, bias(Bias.BULLISH)).allowed
    assert validate(short_hit, bias(Bias.BEARISH, -3.0)).allowed and not validate(long_hit, bias(Bias.BEARISH, -3.0)).allowed
    sin = validate(long_hit, bias(Bias.NO_BIAS, 0.0))
    assert not sin.allowed and "sin sesgo" in sin.reason and sin.verdict == "NO GO"
    assert validate(long_hit, bias(Bias.NO_BIAS, 0.0), allow_no_bias=True).allowed
    lateral = BiasResult(Bias.NO_BIAS, None, (), {}, "Mercado lateral", 3.0, 3.0, True, 0.05)
    assert "lateral" in validate(long_hit, lateral).reason
    assert not validate(long_hit, None).allowed                                          # sesgo aún sin calcular


def run_skill(env_text="", bias_result=None, publish_bias=True):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus, found, updated = EventBus(), [], []
    bus.subscribe("t", "pattern.detected", found.append)
    bus.subscribe("t", "pattern.updated", updated.append)
    manager = SkillManager(bus, Services(None, None, {"app": {}}, EnvConfig(parse(env_text))), [{"type": "pattern"}])
    manager.start()
    n = 30
    close = np.array([100.0] * 12 + [101, 106, 107] + [100.0] * 15)                       # cierra sobre el High en la vela 13
    df = pd.DataFrame({"ts": np.arange(n) * 900, "open": close, "high": close + 1, "low": close - 1, "close": close})
    sessions = [session(NY, date(2026, 10, 6), 9.5)]
    if publish_bias and bias_result is not None:
        bus.publish("bias.updated", {"result": bias_result, "symbol": "EURUSD", "timeframe": "15m"}, source="bias")
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "15m", "df": df}, source="feed")
    bus.publish("tbr.updated", {"symbol": "EURUSD", "timeframe": "15m", "sessions": sessions, "available": True}, source="tbr")
    deadline = time.time() + 3
    while not updated and time.time() < deadline:
        time.sleep(0.02)
    time.sleep(0.2)
    return manager, bus, found, updated, df, sessions


def test_un_patron_a_favor_del_sesgo_es_go_y_en_contra_es_no_go(registry):
    manager, _bus, found, updated, *_ = run_skill("", bias(Bias.BULLISH))
    manager.stop()
    assert updated[-1].payload["tbr"].zone == "NY Open" and len(found) == 1
    p = found[0].payload
    assert p["hit"].key == "rompe_high" and p["hit"].direction == "long" and p["hit"].x == 13
    assert p["decision"].allowed and "a favor del sesgo Bullish" in p["decision"].reason
    manager, _bus, found, *_ = run_skill("", bias(Bias.BEARISH, -3.0))
    manager.stop()
    assert len(found) == 1 and not found[0].payload["decision"].allowed                   # se muestra igualmente, como NO GO
    assert "contra el sesgo Bearish" in found[0].payload["decision"].reason


def test_no_repite_avisos_y_espera_al_sesgo(registry):
    manager, bus, found, updated, df, sessions = run_skill("", bias(Bias.BULLISH))
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "15m", "df": df}, source="feed")   # recarga de las mismas velas
    bus.publish("tbr.updated", {"symbol": "EURUSD", "timeframe": "15m", "sessions": sessions, "available": True}, source="tbr")
    time.sleep(0.3)
    manager.stop()
    assert len(found) == 1                                                                 # el mismo patrón no se avisa dos veces
    manager, _bus, found, updated, *_ = run_skill("", None)                                # sin sesgo calculado: no se avisa aún
    manager.stop()
    assert found == [] and len(updated[-1].payload["hits"]) == 1                           # pero sí se ve en pattern.updated
    assert not updated[-1].payload["decisions"][0].allowed


def test_ajustes_de_pattern(registry):
    manager, *_ = run_skill("PATTERN_TYPES=\n", bias(Bias.BULLISH))
    manager.stop()
    for text, key in (("PATTERN_WINDOW_HOURS=0\n", "PATTERN_WINDOW_HOURS"), ("PATTERN_TYPES=no_existe\n", "no_existe")):
        manager, _bus, found, *_ = run_skill(text, bias(Bias.BULLISH))
        manager.stop()
        assert manager.skills["pattern"].state.value == "error" and key in manager.skills["pattern"].note and not found
    manager, _bus, found, *_ = run_skill("PATTERN_ZONES=ASIA\n", bias(Bias.BULLISH))     # la TBR activa es NY Open: no es de Asia
    manager.stop()
    assert found == []
    manager, _bus, found, *_ = run_skill("PATTERN_ALLOW_NO_BIAS=true\n", bias(Bias.NO_BIAS, 0.0))
    manager.stop()
    assert len(found) == 1 and found[0].payload["decision"].allowed


def test_sin_patrones_definidos_la_skill_lo_dice():
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    assert not PATTERN_REGISTRY                                                            # de momento no hay ninguno definido
    bus = EventBus()
    manager = SkillManager(bus, Services(None, None, {"app": {}}, EnvConfig()), [{"type": "pattern"}])
    manager.start()
    n = 12
    df = pd.DataFrame({"ts": np.arange(n) * 900, "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0})
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "15m", "df": df}, source="feed")
    bus.publish("tbr.updated", {"symbol": "EURUSD", "timeframe": "15m", "sessions": [session(NY, date(2026, 10, 6), 9.5)],
                                "available": True}, source="tbr")
    time.sleep(0.4)
    caption = manager.skills["pattern"].caption
    manager.stop()
    assert caption == "sin patrones definidos"


def test_el_registro_anota_la_tbr_activa_y_cada_patron(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": ["EURUSD"]}}
    win = MainWindow(EventBus(), SkillManager(EventBus(), Services(None, None, cfg, EnvConfig()), []), cfg, "t")
    tbr = active_tbr([session(NY, date(2026, 10, 6), 9.5)])
    win._on_pattern_updated({"symbol": "EURUSD", "timeframe": "15m", "tbr": tbr, "hits": [], "decisions": [], "errors": []})
    hit = PatternHit("rompe_high", "Cierre sobre el High", "long", 13, 105.0, "detalle", {"stop": 95.0})
    from tradingbot.skills.pattern.patterns import PatternDecision
    win._on_pattern_detected({"symbol": "EURUSD", "timeframe": "15m", "tbr": tbr, "hit": hit, "bias": Bias.BULLISH,
                              "decision": PatternDecision(True, "Long a favor del sesgo Bullish")})
    win._on_pattern_detected({"symbol": "EURUSD", "timeframe": "15m", "tbr": tbr, "hit": hit, "bias": Bias.BEARISH,
                              "decision": PatternDecision(False, "Long contra el sesgo Bearish")})
    text = win.log_view.toPlainText()
    assert "pattern: TBR activa NY Open" in text and "50 %" in text
    assert "Cierre sobre el High Long en NY Open" in text and "GO: Long a favor del sesgo Bullish" in text
    assert "NO GO: Long contra el sesgo Bearish" in text                                   # se muestra también el denegado
