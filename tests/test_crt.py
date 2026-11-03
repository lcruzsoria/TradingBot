"""CRT (Candle Range Theory): motor, skill y perfil de estrategia, con el escenario sintético de tests/crt_scenarios.py."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
import time
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crt_scenarios import AHEAD, eurusd, mirror, nas100, scenario                                # noqa: E402
from tradingbot.envconfig import EnvConfig, parse                                # noqa: E402
from tradingbot.skills.crt import engine                                         # noqa: E402

CFG = engine.Cfg(180, 18 * 3600, 18 * 3600, AHEAD)
RULE = engine.Rule()


def ny(ts: int) -> str:
    return f"{pd.Timestamp(int(ts) - AHEAD, unit='s'):%Y-%m-%d %H:%M}"


def at(hhmm: str) -> int:
    return pd.Timestamp(f"2026-10-13 {hhmm}").value // 10**9 + AHEAD


def test_el_escenario_da_un_unico_corto_con_todos_los_pasos():
    df = scenario()
    setups, funnel = engine.find_setups(df, df, 5, RULE, CFG)
    assert len(setups) == 1
    assert funnel["velas HTF con sweep"] >= 1                                         # (el relleno del día 1 también tiene sweeps sin FVG)
    assert [funnel[k] for k in list(funnel)[1:5]] == [1, 1, 1, 1]
    st = setups[0]
    assert st["dirección"] == "short" and st["stop"] == 108.5 and st["mtf"] == "M15"
    assert ny(df["ts"][st["ih"]]) == "2026-10-13 06:35"                               # el extremo del sweep
    assert ny(df["ts"][st["jt"]]) == "2026-10-13 07:15"                               # la vuelta al FVG de M15 103.2-107.3 (formado a las 07:15)
    assert [z[:3] for z in st["zones"]] == [(15, 103.2, 107.3)]
    assert st["kf"] > st["jt"]                                                        # el iFVG de LTF se forma después del toque
    assert ny(df["ts"][st["jc"]]) == "2026-10-13 07:30"                               # el cierre bajo la base del iFVG es el CISD
    assert (st["z_bottom"], st["z_top"], st["level"]) == (103.4, 104.9, 103.4)
    assert st["inside"] is False                                                      # C2 acaba fuera de C1 y el setup vale igual


def test_entrada_1_a_la_apertura_de_la_vela_siguiente_al_cisd_y_gana_2r():
    df = scenario()
    st = engine.find_setups(df, df, 5, RULE, CFG)[0][0]
    L = engine.view(df, 1)
    ep = engine.entry_point(L, st, 1, 5, RULE, CFG)
    assert ny(L["ts"][st["jc"]]) == "2026-10-13 07:30" and ny(L["ts"][ep["start"]]) == "2026-10-13 07:35"
    assert ep["entry"] == pytest.approx(103.1) and ep["risk"] == pytest.approx(5.4)
    res = engine.manage(L, st, ep, RULE)
    assert res["cómo"] == "objetivo" and res["gross"] == pytest.approx(2.0)
    assert res["target"] == pytest.approx(103.1 - 2 * 5.4)


def test_entrada_4_al_cierre_de_la_vela_del_cisd_y_gana_2r():
    df = scenario()
    st = engine.find_setups(df, df, 5, RULE, CFG)[0][0]
    L = engine.view(df, 1)
    ep = engine.entry_point(L, st, 4, 5, RULE, CFG)
    assert ny(L["ts"][st["jc"]]) == "2026-10-13 07:30" and ny(L["ts"][ep["start"]]) == "2026-10-13 07:35"        # la hora de la entrada es el fin de esa vela
    assert ep["entry"] == pytest.approx(L["close"][st["jc"]]) == pytest.approx(103.1)      # el cierre de la vela del CISD
    assert ep["risk"] == pytest.approx(108.5 - 103.1)
    L2 = engine.view(df.assign(open=df["open"].where(df.index != st["jc"] + 1, 102.0)), 1)      # si la siguiente abre más lejos del extremo
    assert engine.entry_point(L2, st, 4, 5, RULE, CFG)["risk"] == pytest.approx(5.4)           # la entrada 4 no cambia...
    assert engine.entry_point(L2, st, 1, 5, RULE, CFG)["risk"] == pytest.approx(108.5 - 102.0)   # ...y la 1 sí
    res = engine.manage(L, st, ep, RULE)
    assert res["cómo"] == "objetivo" and res["gross"] == pytest.approx(2.0)


def test_la_entrada_tiene_que_abrirse_antes_de_que_cierre_c2():
    df = scenario()
    st = engine.find_setups(df, df, 5, RULE, CFG)[0][0]
    L = engine.view(df, 1)
    assert st["c2_end"] == at("09:00")
    tarde = dict(st, c2_end=int(L["ts"][st["jc"]]) + 300)                              # C2 acaba justo con la vela del CISD
    for variant in (1, 2, 3, 4):
        assert engine.entry_point(L, tarde, variant, 5, RULE, CFG) is None
    assert engine.entry_point(L, dict(st, c2_end=at("07:40")), 1, 5, RULE, CFG)["start"] == st["jc"] + 1


def test_regla_1_se_descarta_si_el_extremo_de_c1_da_menos_de_2r_y_se_anota_el_r_maximo():
    df = scenario()
    st = engine.find_setups(df, df, 5, RULE, CFG)[0][0]
    L = engine.view(df, 1)
    ep = engine.entry_point(L, st, 1, 5, RULE, CFG)
    assert st["c1"][0] == pytest.approx(100.0)                                       # el mínimo de C1 (espacio del corto)
    assert engine.planned_rr(st, ep) == pytest.approx((103.1 - 100.0) / 5.4)         # 0.57 R: queda cerca, se descartaría con min_rr=2
    reach = engine.max_r(L, st, ep)                                                  # lo que habría llegado a dar antes del stop
    assert reach == pytest.approx((103.1 - L["low"][ep["start"]:].min()) / 5.4) and reach > 2.0   # el escenario baja a 92.3: 2 R, no 0.57


def test_si_ya_hay_una_operacion_abierta_no_se_abre_otra_ni_en_sentido_contrario():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import backtest_crt as bt
    bt.configure("indices")
    df = scenario()
    st = engine.find_setups(df, df, 5, RULE, CFG)[0][0]
    L = engine.view(df, 1)
    ep = engine.entry_point(L, st, 1, 5, RULE, CFG)
    segundo = dict(st, jc=ep["start"] + 1, sign=-1, dirección="long")             # otro setup, de sentido contrario, con la primera operación abierta
    both = bt.run_variant(df, [st, segundo], 1, 5, RULE)
    assert len(bt.run_variant(df, [segundo], 1, 5, RULE)) == 1                    # solo, sí daría operación
    assert len(both) == 1 and both["dirección"].iloc[0] == "short"                 # no se abre; la primera sigue su curso


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


def test_sin_hueco_de_mtf_tras_el_extremo_no_hay_setup():
    df = scenario()
    t = (df["ts"] >= at("06:45")) & (df["ts"] <= at("07:15"))
    df.loc[t, "high"] = df.loc[t, "high"].clip(lower=108.0)                       # el desplazamiento no deja hueco en M15
    assert engine.find_setups(df, df, 5, RULE, CFG)[0] == []


def test_si_el_precio_no_vuelve_al_fvg_no_hay_setup():
    df = scenario()
    c2 = df["ts"] >= at("07:10")
    cols = ["open", "high", "low", "close"]
    df.loc[c2, cols] = df.loc[c2, cols].clip(upper=102.9)                          # tras formarse los FVG (el más bajo, 103.0-103.5) ya no los toca
    setups, funnel = engine.find_setups(df, df, 5, RULE, CFG)
    assert setups == [] and funnel["con FVG de MTF formado tras el extremo"] == 1 and funnel["con vuelta al FVG"] == 0


def test_un_extremo_nuevo_reinicia_el_setup():
    df = scenario()
    i = int(df.index[df["ts"] == at("07:20")][0])
    df.loc[i, "high"] = 109.0                                                    # antes del CISD el precio hace un máximo nuevo
    setups, _ = engine.find_setups(df, df, 5, RULE, CFG)
    assert setups == []                                                          # el FVG y la vuelta eran del extremo anterior


def c2_invalid(setups) -> list:
    """Los invalidados de la C2 del escenario (06:00 NY); el relleno del día 1 también tiene sweeps."""
    return [x for x in setups.invalid if x["C2"] == at("06:00")]


def test_si_el_precio_llega_al_extremo_opuesto_de_c1_sin_completar_el_setup_queda_invalidado():
    df = scenario()
    i = int(df.index[df["ts"] == at("06:55")][0])
    df.loc[i, "low"] = 99.0                                                      # C2 pasa el mínimo de C1 (100) antes de que haya FVG de MTF
    setups, funnel = engine.find_setups(df, df, 5, RULE, CFG)
    assert setups == []
    [inv] = c2_invalid(setups)
    assert (inv["dirección"], inv["motivo"], inv["stop"]) == ("short", "sin FVG de MTF", 108.5)
    df2 = scenario()
    j = int(df2.index[df2["ts"] == at("07:20")][0])
    df2.loc[j, "low"] = 99.0                                                     # ahora lo alcanza con el FVG ya formado pero sin iFVG invertido
    st2 = engine.find_setups(df2, df2, 5, RULE, CFG)[0]
    assert st2 == [] and [x["motivo"] for x in c2_invalid(st2)] == ["sin iFVG invertido"]


def test_si_c2_tomo_antes_el_otro_extremo_el_sweep_es_el_del_otro_lado():
    df = scenario()
    i = int(df.index[df["ts"] == at("06:05")][0])
    df.loc[i, "low"] = 99.0                                                      # C2 toma antes el mínimo de C1: no es un corto
    setups, _ = engine.find_setups(df, df, 5, RULE, CFG)
    assert setups == [] and [x["dirección"] for x in c2_invalid(setups)] == ["long"]  # y el largo se invalida al llegar después al máximo de C1


def test_el_cisd_es_la_inversion_del_ifvg_sin_mirar_la_secuencia_ni_el_rango_de_c1():
    """El CISD es el cierre bajo la base del FVG alcista de M5 (103.4), no un nivel de secuencia ni de C1."""
    df = scenario()
    st = engine.find_setups(df, df, 5, RULE, CFG)[0][0]
    assert df["close"][st["jc"]] < st["z_bottom"] <= df["close"][st["jc"] - 1]            # la vela anterior aún cierra por encima
    c1 = (df["ts"] >= at("03:00")) & (df["ts"] < at("06:00"))
    df.loc[c1, ["high", "low", "open", "close"]] = df.loc[c1, ["high", "low", "open", "close"]].clip(upper=102.5)
    assert len(engine.find_setups(df, df, 5, RULE, CFG)[0]) == 1                          # cambiar el rango de C1 no cambia el CISD


def test_h4_en_forex_y_cfg_del_mercado():
    assert engine.INDICES.htf_min == 180 and engine.INDICES.session_end == 18 * 3600
    assert engine.FOREX.htf_min == 240 and engine.FOREX.session_end == 17 * 3600
    ts = pd.Timestamp("2026-10-13 06:50").value // 10**9 + AHEAD
    assert ny(engine.session_end(ts, CFG)) == "2026-10-13 18:00"
    assert ny(engine.session_end(ts, engine.Cfg(240, 17 * 3600, 17 * 3600, AHEAD))) == "2026-10-13 17:00"


# -- skill, Cortex y Setup -----------------------------------------------------------------------------------------------

def run(strategy="crt", env_text="", skills=("crt", "cortex", "setup"), source=None):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus = EventBus()
    out = {"signal": [], "order": [], "executed": []}
    bus.subscribe("t", "crt.signal", out["signal"].append)
    bus.subscribe("t", "setup.order", out["order"].append)
    bus.subscribe("t", "setup.executed", out["executed"].append)
    app = {"strategy": strategy} if strategy else {}
    manager = SkillManager(bus, Services(source, None, {"app": app}, EnvConfig(parse(env_text))), [{"type": s} for s in skills])
    manager.start()
    bus.publish("clock.offset", {"server_offset": None, "offset_source": "test"}, source="quotes")   # None = +7 h estimado
    return manager, bus, out


def loaded(bus, df, symbol="NAS100.s", tf="5m"):
    bus.publish("candles.loaded", {"symbol": symbol, "timeframe": tf, "df": df}, source="feed")
    time.sleep(0.6)


def until_entry(df: pd.DataFrame, extra: int = 1) -> pd.DataFrame:
    """Las velas hasta la de la entrada del EURUSD (22:30 NY del 02/11, la última puede estar formándose)."""
    return df[df["ts"] <= pd.Timestamp("2026-11-02 22:30").value // 10**9 + AHEAD + (extra - 1) * 300].reset_index(drop=True)


def test_la_zona_comun_da_el_largo_del_eurusd_del_02_11():
    df = eurusd()
    cfg = engine.Cfg(240, 17 * 3600, 17 * 3600, AHEAD)
    setups, funnel = engine.find_zone_setups(df, df, 5, cfg)
    st = [x for x in setups if ny(x["C2"]) == "2026-11-02 21:00"][0]
    assert st["dirección"] == "long" and st["mtf"] == "M15"
    assert ny(df["ts"][st["inv"]]) == "2026-11-02 21:55"                                # el iFVG se invierte: la vela cierra sobre su techo (1.11834)
    assert ny(df["ts"][st["jt"]]) == "2026-11-02 22:10"                                 # el pullback a la zona común, de arriba abajo
    assert ny(df["ts"][st["jc"]]) == "2026-11-02 22:25"                                 # la primera vela que cierra con cuerpo sobre el CISD tras el toque
    assert (-st["level"], -st["stop"]) == (pytest.approx(1.11841), pytest.approx(1.1177))
    assert sorted((-st["z_bottom"], -st["z_top"])) == pytest.approx([1.11815, 1.11833])     # zona común: FVG de M15 1.11814-1.11833 y iFVG de M5 1.11815-1.11834
    ep = engine.entry_point(engine.view(df, -1), st, 1, 5, RULE, cfg)
    assert ny(df["ts"][ep["start"]]) == "2026-11-02 22:30" and -ep["entry"] == pytest.approx(1.11843)


def test_el_ifvg_es_de_un_tf_igual_o_menor_que_el_fvg_y_manda_el_de_mayor_tf(monkeypatch):
    df = eurusd()
    cfg = engine.Cfg(240, 17 * 3600, 17 * 3600, AHEAD)
    st = [x for x in engine.find_zone_setups(df, df, 5, cfg)[0] if ny(x["C2"]) == "2026-11-02 21:00"][0]
    assert st["mtf"] == "M15"                                                           # con un FVG de M15 y otro de M5 posibles, el de mayor TF
    assert [x for x in engine.find_zone_setups(df, df, 30, cfg)[0] if ny(x["C2"]) == "2026-11-02 21:00"] == []     # un iFVG de 30 min no cabe en un FVG de M15 ni de M5
    monkeypatch.setattr(engine, "ZONE_TFS", (5,))
    for x in engine.find_zone_setups(df, df, 5, cfg)[0]:                                # FVG de M5 con iFVG de M5: dos huecos distintos
        assert x["mtf"] == "M5" and (x["ifvg"][0], x["ifvg"][1]) != (x["zones"][0][1], x["zones"][0][2])


def test_un_fvg_que_una_mecha_ya_mitigo_antes_de_nacer_el_ifvg_no_vale():
    df = nas100()
    cfg = engine.Cfg(180, 18 * 3600, 18 * 3600, AHEAD)
    setups, _ = engine.find_zone_setups(df, df, 5, cfg)
    # el FVG de M5 27966.4-27969.9 (01:10-01:20 NY) lo mitiga la mecha de las 01:25 NY, antes de nacer el iFVG de 27951.7-27981.9 (02:00-02:10 NY): sin pareja ni setup
    assert [x for x in setups if ny(x["C2"]) == "2026-11-03 00:00"] == []


def test_las_combinaciones_de_tf_se_miran_con_las_velas_del_tf_del_ifvg():
    from tradingbot.skills.crt.chart import complete_series
    df = eurusd()
    cfg = engine.Cfg(240, 17 * 3600, 17 * 3600, AHEAD)
    series = complete_series({5: df}, cfg)
    assert sorted(series) == [5, 15]                                                   # el de 15 min sale del de 5; el de 3 no se puede sacar
    setups, _ = engine.find_multi_setups(series, cfg)
    assert {st["ltf"] for st in setups} <= {5, 15}
    five = [st for st in setups if st["ltf"] == 5 and ny(st["C2"]) == "2026-11-02 21:00"]
    assert five and ny(df["ts"][five[0]["jc"]]) == "2026-11-02 22:25"                  # la combinación de siempre (FVG M15 + iFVG M5) sigue dando la misma entrada
    ordered = [st["t_cisd"] for st in setups]
    assert ordered == sorted(ordered)                                                  # salen en orden de la hora del cierre sobre el CISD
    for st in setups:                                                                  # TF del FVG >= TF del iFVG
        assert int(st["mtf"][1:]) >= st["ltf"]


def test_cada_pareja_ifvg_fvg_lleva_su_propio_estado():
    """El iFVG de las 00:25-00:35 forma pareja con varios FVG: tocar la zona de una (00:50) no activa la de otra que aún no existe (la de las 01:35-01:45)."""
    df = nas100()
    cfg = engine.Cfg(180, 18 * 3600, 18 * 3600, AHEAD)
    setups, _ = engine.find_zone_setups(df, df, 5, cfg)
    assert all(not (ny(x["C2"]) == "2026-11-03 00:00" and ny(df["ts"][x["jc"]]) == "2026-11-03 01:35") for x in setups)


def test_sin_pullback_a_la_zona_no_hay_entrada_aunque_cierre_sobre_el_cisd():
    df = eurusd()
    cfg = engine.Cfg(240, 17 * 3600, 17 * 3600, AHEAD)
    cut = df[df["ts"] < pd.Timestamp("2026-11-02 22:10").value // 10**9 + AHEAD].reset_index(drop=True)      # sin las velas del pullback
    assert [x for x in engine.find_zone_setups(cut, cut, 5, cfg)[0] if ny(x["C2"]) == "2026-11-02 21:00"] == []


def test_la_skill_da_la_senal_y_llega_simulada_a_setup():
    manager, bus, out = run()
    loaded(bus, until_entry(eurusd()), "EURUSD")
    loaded(bus, until_entry(eurusd()), "EURUSD")                                 # no se repite para el mismo sweep
    manager.stop()
    assert len(out["signal"]) == 1
    s = out["signal"][0].payload
    assert (s["symbol"], s["direction"], s["strategy"]) == ("EURUSD", "long", "crt")
    assert s["price"] == pytest.approx(1.11843) and s["stop"] == pytest.approx(1.1177) and s["target"] == pytest.approx(1.11843 + 2 * 0.00073)
    assert s["close_at"].startswith("17:00 NY")
    o = out["executed"][0].payload["order"]
    assert o.pattern_key == "crt" and o.tbr_zone == "" and o.direction == "long" and "CRT" in o.pattern
    assert out["executed"][0].payload["sent"] is False                           # simulación: no se envía a MT5


def test_la_skill_guarda_los_setups_de_los_ultimos_dias_para_el_grafico():
    manager, bus, out = run()
    loaded(bus, until_entry(eurusd(), extra=40), "EURUSD")
    marks = manager.skills["crt"].marks["EURUSD"]
    manager.stop()
    assert marks["ltf"] == 5 and len(marks["ts"]) > 0
    assert [m["when"] for m in marks["marks"] if m["when"] == "02/11 21:00" and m["state"] != "sin_entrada"] == ["02/11 21:00"]


def test_fuera_del_perfil_crt_la_skill_no_opera():
    manager, bus, out = run(strategy="")
    loaded(bus, until_entry(eurusd()), "EURUSD")
    manager.stop()
    assert out["signal"] == [] and manager.skills["crt"].caption == "solo en el perfil CRT"


def test_ignora_otros_mercados_y_timeframes_distintos():
    manager, bus, out = run()
    loaded(bus, until_entry(eurusd()), symbol="XAUUSD")
    loaded(bus, until_entry(eurusd()), symbol="EURUSD", tf="15m")
    manager.stop()
    assert out["signal"] == []


def test_no_da_senal_si_la_entrada_es_antigua():
    manager, bus, out = run()
    df = eurusd()
    loaded(bus, df[df["ts"] <= pd.Timestamp("2026-11-02 23:00").value // 10**9 + AHEAD].reset_index(drop=True), "EURUSD")   # ya pasó hace una hora
    manager.stop()
    assert out["signal"] == []


def test_ajustes_no_validos_ponen_la_skill_en_error():
    manager, _, _ = run(env_text="CRT_ENTRY=2")
    state = manager.skills["crt"].state.value
    manager.stop()
    assert state == "error"
    manager, _, _ = run(env_text="CRT_ENTRY=4")
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


def test_la_skill_no_pide_velas_a_mt5_con_el_perfil_en_5_min():
    class Source:
        def __init__(self):
            self.calls = []

        def load_recent(self, symbol, timeframe, bars):
            self.calls.append((symbol, timeframe))
            return eurusd().tail(bars).reset_index(drop=True)

    source = Source()
    manager, bus, out = run(source=source)
    loaded(bus, until_entry(eurusd()), "EURUSD")
    manager.stop()
    assert source.calls == []                                                            # las de 15 min salen de las de 5 y no hay combinaciones con 3 min
    assert len(out["signal"]) == 1 and out["signal"][0].payload["timeframe"] == "5m"

def test_los_niveles_que_c2_puede_barrer_son_el_pdh_los_swings_de_h4_y_las_velas_de_h12_intactos():
    import numpy as np
    day, h4, h12, ahead = 86400, 14400, 43200, 7 * 3600
    t0 = pd.Timestamp("2026-10-27 18:00").value // 10**9 + ahead              # inicio de un día de sesión (NY)

    def candles(step, highs):
        n = len(highs)
        return {"ts": np.array([t0 + i * step for i in range(n)]), "high": np.array(highs, dtype=float)}

    dv = candles(day, [100, 105, 103, 101])                                    # 4 días cerrados: el último (PDH) llega a 101
    sv = candles(h4, [100, 110, 100, 99, 98, 97, 120, 96, 95, 94] + [93] * 14)     # pivotes en 1 (110) y 6 (120)
    tv = candles(h12, [100, 108, 104, 99, 99, 99, 99, 99])
    s2 = t0 + 4 * day                                                           # C2 empieza justo al cerrar el día 4
    hv = candles(3 * 3600, [90] * (4 * 8))                                      # ninguna vela HTF supera nada hasta C2
    hv["high"][8] = 112                                                         # salvo una que supera el swing de 110 (día 2)
    got = dict((n.split(" ")[0] + " " + n.split(" ")[1], p) for p, n in engine.sweep_levels(s2, hv, dv, tv, sv, ahead, ("PDH", "máx")))
    assert got["PDH día"] == 101 and got["swing H4"] == 120                      # el swing de 110 ya lo barrió una vela HTF: no está intacto
    assert any(n.startswith("máx H12") for _, n in engine.sweep_levels(s2, hv, dv, tv, sv, ahead, ("PDH", "máx")))
