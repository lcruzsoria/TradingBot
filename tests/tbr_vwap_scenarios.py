"""Escenarios de confluencia y retest de «TBR con VWAP» (TBR 100-110, 50 % = 105; la TBR cierra tras la vela 7).

Los usan los tests (tests/test_tbr_vwap_pattern.py) y el dibujo de los escenarios, para que lo dibujado sea lo probado.
Cada escenario: (clave, título, filas (open, high, low, close), operación esperada: "long" / "short" / None, motivo, confluencia).
"""
import numpy as np

HIGH, LOW, FIRST = 110.0, 100.0, 8


def mirror(rows):
    return [(210 - o, 210 - l, 210 - h, 210 - c) for o, h, l, c in rows]


BASE = [(104.0, 104.5, 103.5, 104.0)] * 8                                   # la propia TBR, con el VWAP en ~104 (cerca del 50 %)
LOW_BASE = [(102.0, 102.5, 101.5, 102.0)] * 8                               # una TBR que se formó abajo: VWAP en ~102 (lejos del 50 %)
RETEST_UP = [(107.0, 108.0, 106.5, 107.5), (107.5, 108.0, 106.0, 107.0),    # venía de arriba del VWAP...
             (107.0, 107.2, 103.5, 105.0),                                   # ...retest: toca el VWAP con la mínima y cierra arriba
             (105.2, 106.0, 104.8, 105.5), (105.5, 106.5, 105.0, 106.0)]

SCENARIOS = [
    ("A", "A · Válido: TBR cerrada, VWAP en confluencia con el 50 %, retest", BASE + RETEST_UP, "long",
     "retest tras el cierre de la TBR con el VWAP junto al 50 %"),
    ("B", "B · Corto: el espejo exacto", mirror(BASE + RETEST_UP), "short", "mismo setup con el precio venido de abajo"),
    ("C", "C · Retest con la TBR aún abierta", [(104.0, 104.5, 103.5, 104.0)] * 3 + [(106.0, 107.0, 105.5, 106.5), (106.5, 107.0, 105.5, 106.8),
        (106.8, 107.0, 103.5, 105.0), (105.0, 106.0, 104.8, 105.5), (105.0, 106.0, 104.8, 105.5)]
        + [(105.5, 106.5, 105.2, 106.0), (106.0, 107.0, 105.5, 106.5), (106.5, 107.2, 105.8, 106.9)], None,
     "el toque del VWAP ocurre antes del cierre de la TBR: el 50 % aún no es fiable"),
    ("D", "D · VWAP lejos del 50 %: sin confluencia", LOW_BASE + [(107.0, 108.0, 106.5, 107.5), (107.5, 108.0, 106.0, 107.0),
        (107.0, 107.2, 101.8, 104.0), (104.2, 105.0, 103.8, 104.8)], None, "el VWAP (~102) está a 3 puntos del 50 % (máx. 1)"),
    ("E", "E · Toca el VWAP y cierra por debajo", BASE + RETEST_UP[:2] + [(107.0, 107.2, 103.0, 103.8), (103.8, 104.5, 103.0, 104.2)],
     None, "no hay rechazo: la vela cierra bajo el VWAP"),
    ("F", "F · Rango consumido antes del retest", BASE + [(107.0, 110.5, 106.5, 109.0)] + RETEST_UP[1:], None,
     "una vela ya tomó el High: la continuación al extremo se agotó"),
]


def arrays(rows):
    return tuple(np.array(x, dtype=float) for x in zip(*rows))
