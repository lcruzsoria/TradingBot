"""Retest del VWAP dentro de la TBR con objetivo en su extremo (hipótesis en estudio): la lógica de la señal."""
import numpy as np
import pytest

from tradingbot.skills.pattern.vwap_retest import Params, find_signal

# TBR: Low 100, High 110 (50 % = 105). VWAP fijo en 104. Velas tras el cierre de la TBR:
#   0 y 1: por encima del VWAP sin tocarlo; 2: retest (mínima 103,5 <= 104) que cierra en 105; 3: entrada (abre en 105,2).
#          (open, high, low, close)
LONG = [(107.0, 108.0, 106.5, 107.5),
        (107.5, 108.0, 106.0, 107.0),
        (107.0, 107.2, 103.5, 105.0),
        (105.2, 106.0, 104.8, 105.5),
        (105.5, 106.0, 105.0, 105.8)]
HIGH, LOW, VWAP = 110.0, 100.0, 104.0


def arrays(rows):
    o, h, l, c = (np.array(x, dtype=float) for x in zip(*rows))
    return o, h, l, c


def signal(rows=LONG, vwap=VWAP, high=HIGH, low=LOW, params=Params(), first=0):
    o, h, l, c = arrays(rows)
    v = np.full(len(c), vwap, dtype=float) if np.isscalar(vwap) else np.asarray(vwap, dtype=float)
    return find_signal(o, h, l, c, v, high, low, first, len(c) - 1, params)


def test_largo_retest_del_vwap_con_objetivo_en_el_high():
    s = signal()
    assert (s.direction, s.bar, s.entry_bar) == ("long", 2, 3)
    assert s.entry == 105.2                         # apertura de la vela siguiente al retest
    assert s.stop == 101.5                          # el más lejano: 104 - 0,25 x 10 (el mínimo del retest, 103,5, queda más cerca)
    assert s.target == 110.0 and s.vwap == 104.0


def test_el_corto_es_el_espejo_exacto():
    mirror = [(210 - o, 210 - l, 210 - h, 210 - c) for o, h, l, c in LONG]      # p -> 210 - p: High 110 -> Low 100
    s = signal(mirror, vwap=210 - VWAP)
    assert (s.direction, s.bar, s.entry_bar) == ("short", 2, 3)
    assert s.entry == pytest.approx(210 - 105.2) and s.stop == pytest.approx(210 - 101.5) and s.target == pytest.approx(100.0)


def test_el_stop_es_el_minimo_del_retest_si_queda_mas_lejos():
    rows = [r for r in LONG]
    rows[2] = (107.0, 107.2, 100.8, 105.0)           # el retest baja hasta 100,8 (más lejos que 101,5)
    assert signal(rows).stop == 100.8


def test_sin_senal_si_el_rango_ya_no_esta_intacto():
    rows = list(LONG)
    rows[0] = (107.0, 110.5, 106.5, 107.5)           # una vela ya tomó el High: la continuación al extremo se consumió
    assert signal(rows) is None
    rows = list(LONG)
    rows[1] = (107.5, 108.0, 99.5, 107.0)            # o el Low
    assert signal(rows) is None


def test_sin_senal_si_el_vwap_queda_fuera_del_rango_o_no_hay_vwap():
    assert signal(vwap=111.0) is None and signal(vwap=99.0) is None
    assert signal(vwap=np.full(len(LONG), np.nan)) is None


def test_sin_senal_si_no_venia_de_arriba_o_no_cierra_por_encima():
    rows = list(LONG)
    rows[1] = (105.0, 105.5, 102.0, 103.0)           # la vela anterior cerró por debajo del VWAP (cruza de abajo arriba)
    assert signal(rows) is None
    rows = list(LONG)
    rows[2] = (107.0, 107.2, 103.0, 103.8)           # toca el VWAP pero cierra por debajo: no hay rechazo
    assert signal(rows) is None


def test_el_objetivo_debe_estar_al_menos_a_min_rr():
    rows = list(LONG)
    rows[3] = (109.5, 109.8, 109.0, 109.5)           # la entrada abre casi en el objetivo: 0,5 de recorrido para 8 de riesgo
    assert signal(rows) is None
    assert signal(params=Params(min_rr=1.5)) is None  # 4,8 de recorrido para 3,7 de riesgo = 1,3 R
    assert signal(params=Params(min_rr=1.2)) is not None


def test_objetivo_mas_alla_del_extremo():
    assert signal(params=Params(target=0.5)).target == 115.0


def test_filtros_de_pendiente_y_de_confluencia():
    rising = np.array([103.0, 103.5, 104.0, 104.2, 104.5])      # el VWAP sube
    assert signal(vwap=rising, params=Params(slope_bars=2)) is not None
    falling = rising[::-1].copy()                                # y baja (con el VWAP en 104 en la vela del retest)
    assert signal(vwap=falling, params=Params(slope_bars=2)) is None
    assert signal(params=Params(confluence=0.15)) is not None    # |104 - 105| = 1 <= 1,5
    assert signal(params=Params(confluence=0.05)) is None        # 1 > 0,5


def test_solo_busca_desde_el_cierre_de_la_tbr_y_dentro_del_plazo():
    assert signal(first=3) is None                               # la señal estaría en la vela 2, anterior al inicio
    o, h, l, c = arrays(LONG)
    v = np.full(len(c), VWAP)
    assert find_signal(o, h, l, c, v, HIGH, LOW, 0, 2) is None   # la vela de la entrada (3) queda fuera del plazo
    assert find_signal(o, h, l, c, v, HIGH, LOW, 0, 3) is not None
