"""Sesgo propio del perfil CRT: zonas de reversión en HTF (FVG, rejection block y order block), un punto cada una, ventana de 10 días."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
import time
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crt_scenarios import AHEAD, eurusd                                           # noqa: E402
from tradingbot.envconfig import EnvConfig, parse                                 # noqa: E402
from tradingbot.skills.bias.models import Bias                                    # noqa: E402
from tradingbot.skills.crt import bias, engine                                    # noqa: E402

CFG = engine.Cfg(240, 17 * 3600, 17 * 3600, AHEAD)
START = pd.Timestamp("2026-10-20 00:00")


def hourly(bars: list[tuple], start: pd.Timestamp = START) -> pd.DataFrame:
    """Velas de 1 h (apertura, máximo, mínimo, cierre) desde `start` (hora NY), en hora de servidor."""
    t0 = start.value // 10**9 + AHEAD
    return pd.DataFrame([(t0 + i * 3600, *b) for i, b in enumerate(bars)], columns=["ts", "open", "high", "low", "close"])


def c2_at(hours: int) -> int:
    return START.value // 10**9 + AHEAD + hours * 3600


# 1. FVG alcista: el máximo de la vela 1 (102) queda bajo el mínimo de la 3 (104)
FVG = [(100, 102, 99, 101.5), (101.5, 108, 101.2, 107.5), (107.5, 110, 104, 109.5)]
# 2. Rejection block alcista: swing low con una mecha inferior de 6.2 sobre un rango de 7.0 (89 %)
RB = [(108, 109, 106.5, 107), (105.2, 106, 99, 105.2), (105.5, 108.5, 104.8, 108)]
# 3. Order block alcista: vela bajista (104 -> 102, máximo 104.5), vela alcista de impulso y un FVG: el mínimo de la tercera (105) queda sobre el máximo de la bajista
OB = [(104, 104.5, 101.5, 102), (102, 108, 101.8, 107.5), (107.5, 110, 105, 109)]
FLAT = [(110, 110.5, 109.5, 110)] * 3                                             # relleno que no deja zonas


def zone_rules(df, direction="long", tfs=("1h",), **kw):
    return sorted({z["rule"] for z in bias.zones(df, direction, CFG, tfs, **kw)})


def test_fvg_alcista_es_un_soporte_y_el_bajista_una_resistencia():
    df = hourly(FLAT + FVG + FLAT)
    spans = lambda d, side: [(x["bottom"], x["top"]) for x in bias.zones(d, side, CFG, ("1h",)) if x["rule"] == "fvg"]      # noqa: E731
    assert (102, 104) in spans(df, "long")
    assert (102, 104) not in spans(df, "short")                                                  # para un corto no es una resistencia
    mirror = hourly([(200 - o, 200 - l, 200 - h, 200 - c) for o, h, l, c in FLAT + FVG + FLAT])
    assert (96, 98) in spans(mirror, "short") and (96, 98) not in spans(mirror, "long")


def test_rejection_block_swing_de_una_vela_y_mecha_de_mas_del_50_por_ciento():
    df = hourly(FLAT + RB + FLAT)
    spans = lambda d, **kw: [(x["bottom"], x["top"]) for x in bias.zones(d, "long", CFG, ("1h",), **kw) if x["rule"] == "rejection"]      # noqa: E731
    assert (99, 105.2) in spans(df)                                                              # del mínimo al borde inferior del cuerpo
    assert (99, 105.2) not in spans(df, min_wick=0.95)                                           # la mecha es el 89 %: con >95 % ya no vale
    chata = hourly(FLAT + [RB[0], (105.2, 106, 104.6, 105.2), RB[2]] + FLAT)                       # mecha del 29 %
    assert spans(chata) == []
    assert (99, 105.2) not in spans(hourly(FLAT + [(108, 109, 107, 107.5), (105.2, 106, 99, 105.2), (104.7, 104.9, 98.5, 104.5)] + FLAT))   # el mínimo de su entorno es otro
    ancho = hourly(FLAT + [(108, 109, 107, 107.5), (107, 108, 105, 107.2), (105.2, 106, 99, 105.2), (104.7, 104.9, 101, 104.5), (104.5, 106, 102, 105)] + FLAT)
    assert (99, 105.2) in spans(ancho)                                                           # con 1 vela a cada lado basta (2 velas más arriba a la izquierda y a la derecha)


def test_order_block_es_la_ultima_vela_contraria_antes_del_impulso():
    df = hourly(FLAT + OB + FLAT)
    z = [z for z in bias.zones(df, "long", CFG, ("1h",)) if z["rule"] == "ob"]
    assert (101.5, 104.5) in [(x["bottom"], x["top"]) for x in z]                                  # el rango completo de la vela bajista
    sin_fvg = hourly(FLAT + [OB[0], OB[1], (107.5, 110, 104.2, 109)] + FLAT)                       # el impulso no deja FVG (mínimo 104.2 < 104.5): no es OB
    assert (101.5, 104.5) not in [(x["bottom"], x["top"]) for x in bias.zones(sin_fvg, "long", CFG, ("1h",)) if x["rule"] == "ob"]
    assert (101.5, 104.5) not in [(x["bottom"], x["top"]) for x in bias.zones(hourly(FLAT + [OB[0], (102.5, 103, 101.8, 102), OB[2]] + FLAT), "long", CFG, ("1h",))
                                  if x["rule"] == "ob"]                                            # la vela siguiente no es un impulso alcista
    assert (101.5, 104.5) not in [(x["bottom"], x["top"]) for x in bias.zones(df, "short", CFG, ("1h",)) if x["rule"] == "ob"]


def test_cada_zona_cuenta_un_punto_y_la_zona_comun_tiene_que_solaparse():
    on = bias.CrtBiasCfg(True, True, 10, 1, ("1h",))
    for bars, rule in ((FLAT + FVG + FLAT, "fvg"), (FLAT + RB + FLAT, "rejection"), (FLAT + OB + FLAT, "ob")):      # cada zona, sin que otra la mitigue
        solo = bias.evaluate(hourly(bars), "long", c2_at(len(bars) + 1), (101.8, 103.0), CFG, on, AHEAD)             # solapa con la zona
        assert solo.score == 1 and solo.counts()[rule] == 1 and solo.go and solo.result().bias is Bias.BULLISH
    df = hourly(FLAT + FVG + FLAT + RB + FLAT + OB + FLAT)
    c2 = c2_at(len(df) + 1)
    lejos = bias.evaluate(df, "long", c2, (130, 131), CFG, on, AHEAD)                             # el CRT no se forma dentro de ninguna
    assert lejos.score == 0 and not lejos.go and lejos.result().bias is Bias.NO_BIAS
    corto = bias.evaluate(df, "short", c2, (101.8, 103.0), CFG, on, AHEAD)                        # son soportes: para un corto no cuentan
    assert corto.counts()["rejection"] == 0 and corto.counts()["ob"] == 0                           # el rejection block y el OB de este caso son soportes


def test_una_zona_mitigada_antes_de_la_c2_ya_no_cuenta():
    on = bias.CrtBiasCfg(True, True, 10, 1, ("1h",))
    limpio = hourly(FLAT + FVG + FLAT)
    assert bias.evaluate(limpio, "long", c2_at(len(limpio) + 1), (102, 104), CFG, on, AHEAD).score == 1
    tocada = hourly(FLAT + FVG + FLAT + [(108, 109, 103.5, 107)] + FLAT)                          # una vela vuelve a entrar en el FVG (mínimo 103.5 < techo 104)
    assert all(z["dead"] is not None for z in bias.zones(tocada, "long", CFG, ("1h",)) if z["rule"] == "fvg")
    assert bias.evaluate(tocada, "long", c2_at(len(tocada) + 1), (102, 104), CFG, on, AHEAD).counts()["fvg"] == 0
    # la mitigación de la propia C2 (su mecha entra en la zona) no la anula
    assert bias.evaluate(tocada, "long", c2_at(len(FLAT + FVG + FLAT)), (102, 104), CFG, on, AHEAD).counts()["fvg"] == 1


def test_las_zonas_de_mas_de_10_dias_no_valen_y_el_limite_se_configura():
    df = hourly(FVG + FLAT * 4)
    on = bias.CrtBiasCfg(True, True, 10, 1, ("1h",))
    zone_created = START.value // 10**9 + AHEAD + 3 * 3600
    assert bias.evaluate(df, "long", zone_created + 9 * 86400, (102, 104), CFG, on, AHEAD).score >= 1                # 9 días antes de la C2
    assert bias.evaluate(df, "long", zone_created + 11 * 86400, (102, 104), CFG, on, AHEAD).score == 0               # 11 días: caducada
    corto = bias.CrtBiasCfg(True, True, 3, 1, ("1h",))
    assert bias.evaluate(df, "long", zone_created + 4 * 86400, (102, 104), CFG, corto, AHEAD).score == 0
    nueva = hourly(FVG + FLAT * 4, START + pd.Timedelta(days=6))                                                   # zona posterior a la C2: queda a la derecha
    assert bias.evaluate(nueva, "long", START.value // 10**9 + AHEAD + 3600, (102, 104), CFG, on, AHEAD).score == 0


def test_deshabilitado_el_sesgo_es_cero_y_el_setup_siempre_go():
    df = hourly(FLAT + FVG + FLAT)
    off = bias.evaluate(df, "long", c2_at(40), (102, 104), CFG, bias.CrtBiasCfg(), AHEAD)
    assert not off.enabled and off.score == 0 and off.go and off.result().bias is Bias.NO_BIAS and "deshabilitado" in off.summary()


def test_la_configuracion_del_sesgo_crt_se_lee_del_env_y_se_valida():
    def load(text):
        return bias.load_cfg(EnvConfig(parse(text)).section("CRT"))
    d = load("")
    assert (d.enabled, d.enforce, d.lookback_days, d.min_score, d.tfs, d.swing_width, d.rb_min_wick_pct) == (False, False, 10.0, 1.0, ("1h", "4h", "1d"), 1, 50.0)
    c = load("CRT_BIAS_ENABLED=true\nCRT_BIAS_ENFORCE=true\nCRT_BIAS_LOOKBACK_DAYS=5\nCRT_BIAS_MIN_SCORE=2\nCRT_BIAS_TFS=4h, 1d\nCRT_BIAS_SWING_WIDTH=2\nCRT_BIAS_RB_MIN_WICK_PCT=60")
    assert (c.enabled, c.enforce, c.lookback_days, c.min_score, c.tfs, c.swing_width, c.rb_min_wick_pct) == (True, True, 5.0, 2.0, ("4h", "1d"), 2, 60.0)
    for bad in ("CRT_BIAS_TFS=15m", "CRT_BIAS_LOOKBACK_DAYS=0", "CRT_BIAS_RB_MIN_WICK_PCT=120", "CRT_BIAS_SWING_WIDTH=0"):
        with pytest.raises(ValueError):
            load(bad)


# -- skill y Cortex --------------------------------------------------------------------------------------------------------

@pytest.fixture
def fvg_sin_mitigar(monkeypatch):
    """El FVG de 1 h del escenario EURUSD (1.11832-1.11846) lo toca el precio a las 19:40, antes de la C2 de las 21:00, y no llega a la zona común (BPR 1.11815-1.11818):
    con las reglas de zonas sin mitigar y de solape ya no puntúa. Aquí se da por sin mitigar y sobre el BPR para probar los puntos del sesgo y el GO / NO GO."""
    real = bias.zones

    def zones(*a, **k):
        out = real(*a, **k)
        for z in out:
            if z["rule"] == "fvg":
                z["dead"], z["bottom"], z["top"] = None, 1.1181, 1.1183
        return out
    monkeypatch.setattr(bias, "zones", zones)


@pytest.fixture(autouse=True)
def solo_m5(monkeypatch):
    """Estos tests miran el sesgo, no la prioridad de M15: el escenario (EURUSD) tiene un BPR de M15 con retest que descartaría su setup de M5."""
    def only_m5(series, cfg, hist=None):
        setups, funnel = engine.find_zone_setups(series[5], series[5], 5, cfg, {5: series[5]}, hist)
        for st in setups:
            st["ltf"], st["t_cisd"] = 5, int(series[5]["ts"].iloc[st["jc"]])
        return setups, funnel
    monkeypatch.setattr(engine, "find_multi_setups", only_m5)


def run(env_text=""):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus = EventBus()
    out = {"signal": [], "executed": [], "bias": []}
    bus.subscribe("t", "crt.signal", out["signal"].append)
    bus.subscribe("t", "setup.executed", out["executed"].append)
    bus.subscribe("t", "bias.updated", out["bias"].append)
    manager = SkillManager(bus, Services(None, None, {"app": {"strategy": "crt"}}, EnvConfig(parse(env_text))), [{"type": s} for s in ("crt", "cortex", "setup")])
    manager.start()
    bus.publish("clock.offset", {"server_offset": None, "offset_source": "test"}, source="quotes")
    return manager, bus, out


def load_entry(bus, symbol="EURUSD"):
    df = eurusd()
    df = df[df["ts"] <= pd.Timestamp("2026-11-02 22:35").value // 10**9 + AHEAD].reset_index(drop=True)      # la vela de las 22:35 se está formando: la entrada es a su apertura
    bus.publish("candles.loaded", {"symbol": symbol, "timeframe": "5m", "df": df}, source="feed")
    time.sleep(0.6)


def test_con_el_sesgo_apagado_el_setup_es_go_y_la_tarjeta_dice_sesgo_cero():
    manager, bus, out = run()
    load_entry(bus)
    manager.stop()
    assert len(out["signal"]) == 1 and len(out["executed"]) == 1                          # GO aunque no haya zonas HTF
    s = out["signal"][0].payload
    assert s["bias_enabled"] is False and s["bias_points"].score == 0 and s["bias_result"].bias is Bias.NO_BIAS
    card = out["bias"][-1].payload["result"]
    assert [v.rule for v in card.votes] == [t for _, t in bias.RULES] and "deshabilitado" in card.summary
    assert out["executed"][0].payload["order"].bias == "No Bias" and out["executed"][0].payload["order"].score == 0


def test_con_el_sesgo_encendido_el_setup_es_go_con_los_puntos_que_pide_y_no_go_si_no_llega(fvg_sin_mitigar):
    manager, bus, out = run("CRT_BIAS_ENABLED=true\nCRT_BIAS_ENFORCE=true\nCRT_BIAS_MIN_SCORE=1")
    load_entry(bus)
    manager.stop()
    p = out["signal"][0].payload["bias_points"]
    assert p.enabled and p.score == 1 and [z["rule"] for z in p.zones] == ["fvg"] and p.zones[0]["tf"] == "1h"      # un FVG de 1h (1.1183-1.1185) solapa con la zona común
    assert len(out["executed"]) == 1                                                       # 1 punto >= 1: GO
    assert out["executed"][0].payload["order"].bias == "Bullish" and out["executed"][0].payload["order"].score == 1
    manager, bus, out = run("CRT_BIAS_ENABLED=true\nCRT_BIAS_ENFORCE=true\nCRT_BIAS_MIN_SCORE=2")
    load_entry(bus)
    manager.stop()
    assert len(out["signal"]) == 1 and out["executed"] == []                               # 1 punto < 2: NO GO, no se abre
    assert out["signal"][0].payload["bias_points"].go is False and manager.skills["cortex"].caption.startswith("NO GO")
    card = out["bias"][-1].payload["result"]
    assert card.score == 1 and card.bias is Bias.NO_BIAS and "FVG en HTF 1h" in card.summary


def test_el_perfil_crt_no_lleva_la_skill_bias_de_los_otros_perfiles():
    from tradingbot.config import strategy_skills
    kept = strategy_skills([{"type": t} for t in ("bias", "cortex", "pattern", "setup")], "crt")
    assert "bias" not in [s["type"] for s in kept] and [s["type"] for s in kept] == ["cortex", "setup", "crt"]
    assert "bias" in [s["type"] for s in strategy_skills([{"type": "bias"}], "calendario")]       # los demás perfiles siguen con la suya


def test_se_valida_por_regla_de_mayor_a_menor_tf_y_el_tf_mayor_da_el_punto(monkeypatch):
    llamadas = []
    zona = lambda rule, tf, created: {"rule": rule, "tf": tf, "bottom": 101.0, "top": 105.0, "created": created, "candle": created}      # noqa: E731
    c2 = c2_at(300)

    def falsas(df, direction, cfg, tfs=("1h", "4h", "1d"), swing_width=1, min_wick=0.5, horizon_days=10.0):
        llamadas.append(tfs[0])
        return {"1d": [zona("fvg", "1d", c2 - 5 * 86400)],
                "4h": [zona("fvg", "4h", c2 - 3 * 86400), zona("ob", "4h", c2 - 2 * 86400)],
                "1h": [zona("fvg", "1h", c2 - 3600), zona("ob", "1h", c2 - 7200), zona("rejection", "1h", c2 - 7200)]}[tfs[0]]

    monkeypatch.setattr(bias, "zones", falsas)
    got = bias.evaluate(hourly(FLAT * 4), "long", c2, (102, 103), CFG, bias.CrtBiasCfg(True, True, 10, 1, ("1h", "4h", "1d")), AHEAD)
    assert llamadas == ["1d", "4h", "1h"]                                                         # de mayor a menor
    assert [(z["rule"], z["tf"]) for z in got.zones] == [("fvg", "1d"), ("rejection", "1h"), ("ob", "4h")] or \
        sorted((z["rule"], z["tf"]) for z in got.zones) == [("fvg", "1d"), ("ob", "4h"), ("rejection", "1h")]
    assert got.score == 3                                                                         # un punto por regla, no uno por zona (el FVG de 4h y de 1h no suman)
    llamadas.clear()
    solo = bias.evaluate(hourly(FLAT * 4), "long", c2, (102, 103), CFG, bias.CrtBiasCfg(True, True, 10, 1, ("4h", "1d")), AHEAD)
    assert llamadas == ["1d", "4h"] and sorted((z["rule"], z["tf"]) for z in solo.zones) == [("fvg", "1d"), ("ob", "4h")]
    llamadas.clear()

    def todo_en_1d(df, direction, cfg, tfs=("1h", "4h", "1d"), swing_width=1, min_wick=0.5, horizon_days=10.0):
        llamadas.append(tfs[0])
        return [zona(r, "1d", c2 - 86400) for r in ("fvg", "rejection", "ob")] if tfs[0] == "1d" else []

    monkeypatch.setattr(bias, "zones", todo_en_1d)
    assert bias.evaluate(hourly(FLAT * 4), "long", c2, (102, 103), CFG, bias.CrtBiasCfg(True, True, 10, 1, ("1h", "4h", "1d")), AHEAD).score == 3
    assert llamadas == ["1d"]                                                                     # con las tres reglas validadas en 1d no se mira más


def test_con_el_sesgo_encendido_sin_enforce_se_calcula_pero_no_anula_el_trade(fvg_sin_mitigar):
    manager, bus, out = run("CRT_BIAS_ENABLED=true\nCRT_BIAS_MIN_SCORE=2")                # 1 punto < 2, pero CRT_BIAS_ENFORCE=false (por defecto)
    load_entry(bus)
    manager.stop()
    p = out["signal"][0].payload["bias_points"]
    assert p.enabled and not p.enforce and p.score == 1 and p.go                          # se calcula y el setup sigue siendo GO
    order = out["executed"][0].payload["order"]
    assert len(out["executed"]) == 1 and order.bias == "No Bias" and order.score == 1          # se abre igual; la orden lleva el sesgo real (1 punto, sin llegar al mínimo)
    assert "informativo" in out["bias"][-1].payload["result"].summary and "FVG en HTF 1h" in out["bias"][-1].payload["result"].summary
