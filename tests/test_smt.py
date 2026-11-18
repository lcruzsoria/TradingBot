"""Skill SMT: cuartos de cada ciclo y SMT secuencial entre varios índices (Quarterly Theory)."""
import time

import numpy as np
import pandas as pd
import pytest

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.smt import ciclos
from tradingbot.skills.smt.smt import detectar

H = 3600
DAY = 86400
# 1970-01-05 es lunes. Su día de trading empieza el domingo 1970-01-04 a las 18:00 NY (servidor = NY en estos tests).
LUNES = 3 * DAY + 18 * H


def serie(inicio, valores, bar=300):
    """Velas de M5 desde `inicio`: `valores` = lista de (high, low); open y close en el medio."""
    ts = np.array([inicio + bar * i for i in range(len(valores))])
    h = np.array([v[0] for v in valores], dtype=float)
    l = np.array([v[1] for v in valores], dtype=float)
    m = (h + l) / 2
    return ts, m, h, l, m


def test_cuartos_del_dia_son_asia_londres_ny_am_y_ny_pm_y_los_de_90_minutos_empiezan_a_las_18_00():
    ny = lambda h, m=0: 5 * DAY + h * H + m * 60          # un día cualquiera a esa hora de NY
    q = lambda h, m=0, c="dia": ciclos.numero(ciclos.cuarto(ny(h, m), c), c)
    assert [q(19), q(1), q(7), q(13)] == [1, 2, 3, 4]      # Asia, Londres, NY AM, NY PM
    assert [q(6, 0, "90m"), q(7, 30, "90m"), q(9, 0, "90m"), q(10, 30, "90m")] == [1, 2, 3, 4]    # NY AM en cuartos de 90 minutos
    assert q(7, 30, "90m") == 2 and ciclos.inicio(ciclos.cuarto_true_open(ciclos.cuarto(ny(9), "90m"), "90m"), "90m") == ny(7, 30)   # True Open de NY AM: 07:30
    d = ciclos.cuarto(ny(1), "dia")
    assert ciclos.inicio(ciclos.cuarto_true_open(d, "dia"), "dia") == ny(0)         # True Open del día: las 00:00


def test_la_semana_son_lunes_a_jueves_y_el_viernes_no_es_cuarto():
    lunes = ciclos.cuarto(LUNES + 2 * H, "semana")
    assert ciclos.numero(lunes, "semana") == 1 and ciclos.inicio(lunes, "semana") == LUNES
    assert [ciclos.numero(ciclos.cuarto(LUNES + i * DAY + H, "semana"), "semana") for i in range(4)] == [1, 2, 3, 4]
    assert ciclos.cuarto(LUNES + 4 * DAY + H, "semana") is None and ciclos.cuarto(LUNES + 6 * DAY + H, "semana") is None   # viernes y domingo
    assert ciclos.cuarto_true_open(ciclos.cuarto(LUNES + 3 * DAY + H, "semana"), "semana") == ciclos.cuarto(LUNES + DAY + H, "semana")   # el martes


def _tres(q1, q2):
    """Tres activos con las velas de dos cuartos de 90 minutos seguidos (18 velas M5 cada uno): q1 y q2 son listas de 18 (high, low) por activo."""
    return {s: serie(5 * DAY + 6 * H, q1[s] + q2[s]) for s in q1}


def test_ssmt_bajista_uno_rompe_el_maximo_del_cuarto_anterior_y_otro_no():
    base = [(100.0, 98.0)] * 18
    q1 = {"NQ": base[:9] + [(110.0, 99.0)] + base[10:], "ES": base[:9] + [(108.0, 99.0)] + base[10:], "YM": base}
    q2 = {"NQ": [(100.0, 98.0)] * 4 + [(112.0, 100.0)] + [(100.0, 98.0)] * 13,       # rompe 110
          "ES": [(100.0, 98.0)] * 18,                                                  # no rompe 108
          "YM": [(100.0, 98.0)] * 18}
    found = detectar(_tres(q1, q2), "90m", 0, 5)
    bajistas = [e for e in found if e.direccion == "bajista"]
    assert len(bajistas) == 1
    e = bajistas[0]
    assert (e.etiqueta, e.rompen, set(e.fallan), e.extremo) == ("Q2", ("NQ",), {"ES", "YM"}, 112.0)
    assert e.ts == 5 * DAY + 6 * H + 90 * 60 + 4 * 300 and e.tiempos == (e.ts,)


def test_si_todos_rompen_el_extremo_no_hay_ssmt_y_se_puede_pedir_lo_contrario():
    base = [(100.0, 98.0)] * 18
    q1 = {s: base[:9] + [(110.0, 99.0)] + base[10:] for s in ("NQ", "ES", "YM")}
    q2 = {s: [(100.0, 98.0)] * 4 + [(112.0, 100.0)] + [(100.0, 98.0)] * 13 for s in ("NQ", "ES", "YM")}
    assert detectar(_tres(q1, q2), "90m", 0, 5) == []
    todos = detectar(_tres(q1, q2), "90m", 0, 5, divergencia=False)
    assert [(e.direccion, len(e.rompen), e.fallan) for e in todos] == [("bajista", 3, ())]


def test_ssmt_alcista_con_el_minimo_y_los_extremos_no_tienen_que_coincidir_en_el_tiempo():
    base = [(100.0, 98.0)] * 18
    q1 = {"NQ": base[:2] + [(100.0, 90.0)] + base[3:], "ES": base[:15] + [(100.0, 91.0)] + base[16:], "YM": base}      # mínimos a horas distintas
    q2 = {"NQ": [(100.0, 98.0)] * 3 + [(100.0, 88.0)] + [(100.0, 98.0)] * 14, "ES": [(100.0, 92.0)] * 18, "YM": [(100.0, 98.0)] * 18}
    alcistas = [e for e in detectar(_tres(q1, q2), "90m", 0, 5) if e.direccion == "alcista"]
    assert [(e.rompen, set(e.fallan)) for e in alcistas] == [(("NQ",), {"ES", "YM"})]


def test_el_barrido_debe_estar_sobre_el_true_open_en_un_ssmt_bajista():
    # cuartos de 90 minutos: el True Open es la apertura del Q2 (aquí, el cuarto 2 del ciclo de 6 h que empieza a las 06:00 NY, a las 07:30)
    base = [(100.0, 98.0)] * 18
    q1 = {"NQ": base, "ES": base, "YM": base}
    q2 = {"NQ": [(100.0, 98.0)] * 4 + [(104.0, 100.0)] + [(100.0, 98.0)] * 13, "ES": [(100.0, 98.0)] * 18, "YM": [(100.0, 98.0)] * 18}
    datos = {s: serie(5 * DAY + 9 * H, q1[s] + q2[s]) for s in q1}      # 09:00 y 10:30: Q3 y Q4 de NY AM; su True Open es el de las 07:30, que no está en los datos
    assert all(e.true_open_ok is None for e in detectar(datos, "90m", 0, 5))


def test_la_skill_publica_el_ssmt_cuando_llegan_los_tres_indices_y_valida_sus_ajustes():
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus, found, updated = EventBus(), [], []
    bus.subscribe("t", "smt.detected", found.append)
    bus.subscribe("t", "smt.updated", updated.append)
    manager = SkillManager(bus, Services(None, None, {"app": {"strategy": "barrido_nyam"}}, EnvConfig(parse("SMT_DAYS=3\n"))), [{"type": "smt", "slot": "aux2"}])
    manager.start()
    base = [(100.0, 98.0)] * 18
    q1 = {"NQ": base[:9] + [(110.0, 99.0)] + base[10:], "ES": base[:9] + [(108.0, 99.0)] + base[10:], "YM": base}
    q2 = {"NQ": [(100.0, 98.0)] * 4 + [(112.0, 100.0)] + [(100.0, 98.0)] * 13, "ES": [(100.0, 98.0)] * 18, "YM": [(100.0, 98.0)] * 18}
    ahead = 7 * H
    for sym, name in (("NQ", "NAS100.s"), ("ES", "SP500.s"), ("YM", "DJ30.s")):
        ts, o, h, l, c = serie(5 * DAY + 6 * H + ahead, q1[sym] + q2[sym] + [(100.0, 98.0)] * 4)
        df = pd.DataFrame({"ts": ts, "open": o, "high": h, "low": l, "close": c})
        bus.publish("candles.loaded", {"symbol": name, "timeframe": "5m", "df": df}, source="feed")
    deadline = time.time() + 3
    while not found and time.time() < deadline:
        time.sleep(0.02)
    time.sleep(0.1)
    manager.stop()
    assert found and found[0].payload["smt"].direccion == "bajista" and found[0].payload["smt"].rompen == ("NAS100",)
    assert updated[-1].payload["triad"] == ("NAS100", "SP500", "DJ30")

    def skill(text):
        s = SkillManager(EventBus(), Services(None, None, {"app": {"strategy": "barrido_nyam"}}, EnvConfig(parse(text))), [{"type": "smt"}]).skills["smt"]
        s.on_start()
        return s
    assert skill("").ciclos == ("dia", "90m", "semana")
    with pytest.raises(ValueError, match="SMT_CICLOS"):
        skill("SMT_CICLOS=dia, luna\n")


def _freedom(es_rompe=False):
    """Tres activos con velas de 5 min desde las 07:30 (servidor = NY): Q2 plano 7:30-9:00, y desde las 9:00 un SSMT alcista del NQ con su tCISD."""
    plano = (99.0, 100.0, 98.0, 99.0)
    quieta = (99.0, 100.0, 98.5, 99.5)
    nq = [plano] * 18 + [quieta] * 3 + [(99.0, 99.5, 96.0, 97.0), (97.0, 100.5, 96.5, 100.0), (100.0, 100.0, 98.5, 99.5)] + [(99.5, 112.0, 99.0, 111.0)]
    es = [plano] * 18 + [quieta] * 3 + [(99.0, 99.5, 96.0 if es_rompe else 98.5, 97.0)] + [quieta] * 4
    ts = np.array([5 * DAY + 7 * H + 1800 + 300 * i for i in range(len(nq))])
    mk = lambda v: (ts, *(np.array([x[k] for x in v]) for k in range(4)))
    return {"NQ": mk(nq), "ES": mk(es), "YM": mk(es)}


def test_modelo_freedom_tcisd_alcista_entra_al_cierre_de_la_vela_que_rechaza_el_retest():
    from tradingbot.skills.smt.freedom import modelo
    trades = modelo(_freedom(), "NQ", 0, 5, "90m", 3.0)
    assert len(trades) == 1
    t = trades[0]
    # la vela de las 9:15 rompe el mínimo de Q2 (98) solo en el NQ y cierra bajista: es la vela del tCISD (apertura 99); la siguiente cierra por encima (confirma);
    # la tercera toca 99 y cierra por encima: entrada al cierre, stop en el mínimo del SSMT (96), objetivo a 3R
    assert (t["direction"], t["entry"], t["stop"], round(t["target"], 6)) == ("long", 99.5, 96.0, 110.0)
    nivel = modelo(_freedom(), "NQ", 0, 5, "90m", 2.0, "nivel")[0]
    assert (nivel["entry"], nivel["stop"], nivel["target"]) == (99.0, 96.0, 105.0)                # orden en la apertura de la vela del tCISD
    assert modelo(_freedom(), "NQ", 0, 5, "90m", 2.0, "nivel", holgura=1.0) == []                 # el precio no atraviesa el nivel (mínimo 98,5 frente a 99 - 1)
    assert modelo(_freedom(es_rompe=True), "NQ", 0, 5, "90m", 3.0) == []                          # si todos rompen el extremo, el SSMT se invalida


def test_agregar_junta_velas_finas_en_velas_mas_gruesas():
    from tradingbot.skills.smt.freedom import agregar
    ts = np.array([0, 300, 600, 900, 1200, 1500])
    o, h, l, c = (np.array(x, dtype=float) for x in ([1, 2, 3, 4, 5, 6], [2, 5, 4, 5, 9, 7], [0, 1, 2, 3, 4, 5], [2, 3, 4, 5, 6, 7]))
    t, o2, h2, l2, c2 = agregar((ts, o, h, l, c), 0, 15)
    assert list(t) == [0, 900] and list(o2) == [1, 4] and list(h2) == [5, 9] and list(l2) == [0, 3] and list(c2) == [4, 7]
