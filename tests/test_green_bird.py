"""Modelo Green Bird (barrido + reclaim en NY AM): lógica pura de `pattern/green_bird.py`, con velas M5 sintéticas."""
import numpy as np

from tradingbot.skills.pattern.green_bird import Params, find_signals

AHEAD = 7 * 3600
DAY0 = 1_800_000_000 // 86400 * 86400            # un día cualquiera a las 00:00 UTC; las horas se cuentan en NY desde las 18:00 del día anterior


def ts_ny(day_offset: int, hhmm: int) -> int:
    """Hora del servidor de las `hhmm` (minutos desde medianoche) de NY, `day_offset` días después de DAY0."""
    return DAY0 + day_offset * 86400 + hhmm * 60 + AHEAD


def build(day_offset: int = 1):
    """Dos días de trading de velas M5 planas en 10.000 (rango de 5 puntos) en un día de trading hasta las 12:00 NY."""
    ts = []
    for d in (day_offset - 1, day_offset):
        start, end = (18 * 60, 24 * 60) if d == day_offset - 1 else (0, 12 * 60)
        # el día de trading que termina en `day_offset` empieza a las 18:00 del día anterior
        ts += [ts_ny(d, m) for m in range(start, end, 5)]
    ts = np.array(ts, dtype=np.int64)
    o = np.full(len(ts), 10_000.0)
    h, l, c = o + 5, o - 5, o.copy()
    return ts, o, h, l, c


def test_barrido_de_maximos_con_reclaim_da_un_corto():
    ts, o, h, l, c = build()
    pre = np.flatnonzero((((ts - AHEAD) % 86400) // 60 >= 9 * 60) & (((ts - AHEAD) % 86400) // 60 < 10 * 60))
    h[pre] = 10_010.0                                   # rango de 09:00-10:00: máximo 10.010
    i = int(np.flatnonzero((((ts - AHEAD) % 86400) // 60) == 10 * 60 + 15)[0])
    h[i] = 10_020.0                                     # barrido del máximo...
    c[i] = 10_004.0                                     # ...y cierre otra vez dentro
    sigs = [s for _, s in find_signals(ts, AHEAD, o, h, l, c, Params()) if s.kind == "PRE_NY"]
    assert len(sigs) == 1
    s = sigs[0]
    assert s.direction == "short" and s.bar == i and s.entry_bar == i + 1
    assert s.stop == 10_020.0 and s.entry == 10_004.0
    assert abs(s.target - (10_004.0 - 2 * (10_020.0 - 10_004.0))) < 1e-9


def test_si_el_cierre_no_vuelve_en_las_velas_permitidas_no_hay_operacion():
    ts, o, h, l, c = build()
    mins = ((ts - AHEAD) % 86400) // 60
    h[(mins >= 9 * 60) & (mins < 10 * 60)] = 10_010.0
    for k in range(5):                                # cinco velas cerrando por encima del nivel: ruptura aceptada
        i = int(np.flatnonzero(mins == 10 * 60 + 15 + 5 * k)[0])
        h[i], c[i] = 10_020.0, 10_018.0
    assert [s for _, s in find_signals(ts, AHEAD, o, h, l, c, Params(reclaim_bars=3)) if s.kind == "PRE_NY"] == []


def test_nivel_ya_tocado_no_cuenta_si_se_exige_intacto():
    ts, o, h, l, c = build()
    mins = ((ts - AHEAD) % 86400) // 60
    h[(mins >= 2 * 60) & (mins < 5 * 60)] = 10_010.0     # máximo de London: 10.010
    h[int(np.flatnonzero(mins == 6 * 60)[0])] = 10_020.0  # ya lo tomaron a las 06:00
    i = int(np.flatnonzero(mins == 10 * 60)[0])
    h[i], c[i] = 10_015.0, 10_004.0                         # barrido y reclaim en la ventana
    assert not [s for _, s in find_signals(ts, AHEAD, o, h, l, c, Params(intact=True)) if s.kind == "LONDON" and s.side == "high"]
    assert [s for _, s in find_signals(ts, AHEAD, o, h, l, c, Params(intact=False)) if s.kind == "LONDON" and s.side == "high"]


def test_entrada_con_desplazamiento_espera_a_la_vela_de_cuerpo_grande():
    ts, o, h, l, c = build()
    mins = ((ts - AHEAD) % 86400) // 60
    h[(mins >= 9 * 60) & (mins < 10 * 60)] = 10_010.0
    o[:], c[:] = 10_000.0, 10_001.0                       # cuerpos pequeños de 1 punto
    i = int(np.flatnonzero(mins == 10 * 60 + 15)[0])
    h[i], o[i], c[i] = 10_020.0, 10_001.0, 10_005.0       # barrido y reclaim (cuerpo pequeño)
    o[i + 2], c[i + 2] = 10_005.0, 9_990.0                # dos velas después: desplazamiento a la baja
    p = Params(displacement=1.0, entry_wait=6, fresh_cross=True, intact=False)
    sigs = [s for _, s in find_signals(ts, AHEAD, o, h, l, c, p) if s.kind == "PRE_NY"]
    assert len(sigs) == 1 and sigs[0].bar == i + 2 and sigs[0].entry == 9_990.0 and sigs[0].stop == 10_020.0
