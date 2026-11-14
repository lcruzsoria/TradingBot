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
