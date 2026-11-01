"""CRT (Candle Range Theory): motor, skill y perfil de estrategia, con el escenario sintético de tests/crt_scenarios.py."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
import time
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crt_scenarios import AHEAD, mirror, scenario                                # noqa: E402
from tradingbot.envconfig import EnvConfig, parse                                # noqa: E402
from tradingbot.skills.crt import engine                                         # noqa: E402

CFG = engine.Cfg(180, 18 * 3600, 18 * 3600, AHEAD)
RULE = engine.Rule()


def ny(ts: int) -> str:
    return f"{pd.Timestamp(int(ts) - AHEAD, unit='s'):%Y-%m-%d %H:%M}"


def test_el_escenario_da_un_unico_corto_con_todos_los_pasos():
    df = scenario()
    setups, funnel = engine.find_setups(df, df, 5, RULE, CFG)
    assert len(setups) == 1 and funnel["con CISD"] == 1
    st = setups[0]
    assert st["dirección"] == "short" and st["stop"] == 108.5 and st["level"] == pytest.approx(103.2)
    assert "M15" in st["mtf"]                                                    # el extremo del sweep tocó el FVG de M15
    assert funnel["con el extremo tocando el FVG"] >= funnel["con iFVG"] >= funnel["con CISD"]


def test_entrada_1_a_la_apertura_de_la_vela_siguiente_al_cisd_y_gana_2r():
    df = scenario()
    st = engine.find_setups(df, df, 5, RULE, CFG)[0][0]
    L = engine.view(df, 1)
    ep = engine.entry_point(L, st, 1, 5, RULE, CFG)
    assert ny(L["ts"][st["jc"]]) == "2026-10-13 06:50" and ny(L["ts"][ep["start"]]) == "2026-10-13 06:55"
    assert ep["entry"] == pytest.approx(103.1) and ep["risk"] == pytest.approx(5.4)
    res = engine.manage(L, st, ep, RULE)
    assert res["cómo"] == "objetivo" and res["gross"] == pytest.approx(2.0)
    assert res["target"] == pytest.approx(103.1 - 2 * 5.4)


def test_con_be_a_1r_un_retroceso_cierra_a_cero():
    df = scenario()
    st = engine.find_setups(df, df, 5, RULE, CFG)[0][0]
    L = engine.view(df, 1)
    ep = engine.entry_point(L, st, 1, 5, RULE, CFG)
    i = ep["start"] + 1                                                          # tras la entrada: a 1R y rebote a la entrada
    df2 = df.copy()
    df2.loc[i, ["open", "high", "low", "close"]] = [103.1, 103.2, 97.0, 97.5]    # 1R = 5.4 -> mínimo 97.7 o menos
    df2.loc[i + 1, ["open", "high", "low", "close"]] = [97.5, 103.6, 97.4, 103.4]  # vuelve a la entrada
    L2 = engine.view(df2, 1)
    res = engine.manage(L2, st, ep, engine.Rule(be_at=1.0))
    assert res["cómo"] == "BE" and res["gross"] == pytest.approx(0.0)


def test_el_largo_es_el_espejo_del_corto():
    df = scenario()
    short = engine.find_setups(df, df, 5, RULE, CFG)[0]
    m = mirror(df)
    long_ = engine.find_setups(m, m, 5, RULE, CFG)[0]
    assert [(s["dirección"], s["jc"]) for s in short] == [("short", long_[0]["jc"])] and long_[0]["dirección"] == "long"
    ep_s = engine.entry_point(engine.view(df, 1), short[0], 1, 5, RULE, CFG)
    ep_l = engine.entry_point(engine.view(m, -1), long_[0], 1, 5, RULE, CFG)
    assert ep_s["start"] == ep_l["start"] and ep_s["risk"] == pytest.approx(ep_l["risk"])


def test_sin_fvg_de_mtf_no_hay_setup():
    df = scenario(fvg=False)
    assert engine.find_setups(df, df, 5, RULE, CFG)[0] == []


def test_si_el_sweep_no_llega_al_fvg_no_hay_setup():
    df = scenario()
    c2 = df["ts"] >= pd.Timestamp("2026-10-13 06:00").value // 10**9 + AHEAD
    cols = ["open", "high", "low", "close"]
    df.loc[c2, cols] = df.loc[c2, cols].clip(upper=107.0)                      # el sweep se queda corto: el FVG de M15 empieza en 107.5
    st = engine.find_setups(df, df, 5, RULE, CFG)[0]
    assert all("M15" not in x["mtf"] and "M30" not in x["mtf"] for x in st)     # (un FVG de H1 más ancho aún podría tocarse)


def test_el_fvg_tiene_que_quedar_por_encima_del_maximo_de_c1():
    df = scenario("en_c1")                                                       # borde inferior del FVG = máximo de C1 (107.5)
    assert engine.find_setups(df, df, 5, RULE, CFG)[0] == []
    assert len(engine.find_setups(df, df, 5, engine.Rule(fvg_above=False), CFG)[0]) == 1     # la regla anterior sí lo daba por bueno


def test_largo_el_fvg_alcista_tiene_que_quedar_por_debajo_del_minimo_de_c1():
    m = mirror(scenario("en_c1"))
    assert engine.find_setups(m, m, 5, RULE, CFG)[0] == []
    st = engine.find_setups(m, m, 5, engine.Rule(fvg_above=False), CFG)[0]
    assert len(st) == 1 and st[0]["dirección"] == "long"


def test_si_el_fvg_ya_fue_mitigado_no_cuenta():
    df = scenario()
    t = pd.Timestamp("2026-10-12 20:00").value // 10**9 + AHEAD                  # esa tarde el precio ya había entrado en el FVG
    i = int((df["ts"] - t).abs().idxmin())
    df.loc[i, "high"] = 108.0
    assert engine.find_setups(df, df, 5, RULE, CFG)[0] == []


def test_h4_en_forex_y_cfg_del_mercado():
    assert engine.INDICES.htf_min == 180 and engine.INDICES.session_end == 18 * 3600
    assert engine.FOREX.htf_min == 240 and engine.FOREX.session_end == 17 * 3600
    ts = pd.Timestamp("2026-10-13 06:50").value // 10**9 + AHEAD
    assert ny(engine.session_end(ts, CFG)) == "2026-10-13 18:00"
    assert ny(engine.session_end(ts, engine.Cfg(240, 17 * 3600, 17 * 3600, AHEAD))) == "2026-10-13 17:00"


# -- skill, Cortex y Setup -----------------------------------------------------------------------------------------------

def run(strategy="crt", env_text="", skills=("crt", "cortex", "setup")):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus = EventBus()
    out = {"signal": [], "order": [], "executed": []}
    bus.subscribe("t", "crt.signal", out["signal"].append)
    bus.subscribe("t", "setup.order", out["order"].append)
    bus.subscribe("t", "setup.executed", out["executed"].append)
    app = {"strategy": strategy} if strategy else {}
    manager = SkillManager(bus, Services(None, None, {"app": app}, EnvConfig(parse(env_text))), [{"type": s} for s in skills])
    manager.start()
    bus.publish("clock.offset", {"server_offset": None, "offset_source": "test"}, source="quotes")   # None = +7 h estimado
    return manager, bus, out


def loaded(bus, df, symbol="NAS100.r", tf="5m"):
    bus.publish("candles.loaded", {"symbol": symbol, "timeframe": tf, "df": df}, source="feed")
    time.sleep(0.6)


def until_entry(df: pd.DataFrame, extra: int = 1) -> pd.DataFrame:
    """Las velas hasta la de la entrada (06:55 NY, la última puede estar formándose)."""
    return df[df["ts"] <= pd.Timestamp("2026-10-13 06:55").value // 10**9 + AHEAD + extra * 300 - 300].reset_index(drop=True)


def test_la_skill_da_la_senal_y_llega_simulada_a_setup():
    manager, bus, out = run()
    loaded(bus, until_entry(scenario()))
    loaded(bus, until_entry(scenario()))                                         # no se repite para el mismo sweep
    manager.stop()
    assert len(out["signal"]) == 1
    s = out["signal"][0].payload
    assert (s["symbol"], s["direction"], s["strategy"]) == ("NAS100.r", "short", "crt")
    assert s["price"] == pytest.approx(103.1) and s["stop"] == pytest.approx(108.5) and s["target"] == pytest.approx(92.3)
    assert s["close_at"].startswith("18:00 NY")
    o = out["executed"][0].payload["order"]
    assert o.pattern_key == "crt" and o.tbr_zone == "" and o.direction == "short" and "CRT" in o.pattern
    assert out["executed"][0].payload["sent"] is False                           # simulación: no se envía a MT5


def test_el_largo_llega_como_largo():
    manager, bus, out = run()
    loaded(bus, until_entry(mirror(scenario())))
    manager.stop()
    assert [e.payload["direction"] for e in out["signal"]] == ["long"]
    s = out["signal"][0].payload
    assert s["price"] == pytest.approx(200 - 103.1) and s["stop"] == pytest.approx(200 - 108.5)


def test_fuera_del_perfil_crt_la_skill_no_opera():
    manager, bus, out = run(strategy="")
    loaded(bus, until_entry(scenario()))
    manager.stop()
    assert out["signal"] == [] and manager.skills["crt"].caption == "solo en el perfil CRT"


def test_ignora_otros_mercados_y_timeframes_distintos():
    manager, bus, out = run()
    loaded(bus, until_entry(scenario()), symbol="XAUUSD")
    loaded(bus, until_entry(scenario()), tf="15m")
    manager.stop()
    assert out["signal"] == []


def test_no_da_senal_si_la_entrada_es_antigua():
    manager, bus, out = run()
    df = scenario()
    loaded(bus, df[df["ts"] <= pd.Timestamp("2026-10-13 08:00").value // 10**9 + AHEAD].reset_index(drop=True))   # ya pasó hace una hora
    manager.stop()
    assert out["signal"] == []


def test_ajustes_no_validos_ponen_la_skill_en_error():
    manager, _, _ = run(env_text="CRT_ENTRY=7")
    state = manager.skills["crt"].state.value
    manager.stop()
    assert state == "error"
    manager, _, _ = run(env_text="CRT_ENTRY=2")
    ok = manager.skills["crt"].state.value
    manager.stop()
    assert ok != "error"


# -- perfil de estrategia -------------------------------------------------------------------------------------------------

def test_el_perfil_crt_trae_su_skill_y_quita_pattern_tbr_y_calendario(tmp_path):
    from tradingbot.config import load_profiles, strategy_skills
    env = tmp_path / ".env"
    env.write_text("MT5_PUPRIME_LOGIN=7\nMT5_PUPRIME_SERVER=PUPrime-Demo\nMT5_PUPRIME_PASSWORD=x\n"
                   "MT5_CRT_BASE=puprime\nMT5_CRT_NAME=CRT\nMT5_CRT_STRATEGY=crt\nMT5_CRT_CAPITAL=50000\nMT5_CRT_CURRENCY=USD\n",
                   encoding="utf-8")
    profiles, _ = load_profiles(env)
    crt, pup = profiles["crt"], profiles["puprime"]
    assert (crt.login, crt.server, crt.password) == (pup.login, pup.server, pup.password)
    assert (crt.strategy, crt.capital, crt.currency, crt.display) == ("crt", 50_000.0, "USD", "CRT")
    kept = strategy_skills([{"type": t} for t in ("cortex", "pattern", "tbr", "calendario", "setup")], "crt")
    assert [s["type"] for s in kept] == ["cortex", "setup", "crt"]
    assert kept[-1]["slot"] == "aux2"
    assert strategy_skills([{"type": "cortex"}], "calendario") == [{"type": "cortex"}]      # CRT no se cuela en otros perfiles
