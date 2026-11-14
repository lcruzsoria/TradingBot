"""Cuartos de cada ciclo de la Quarterly Theory (hora de Nueva York; el día de trading empieza a las 18:00 NY).

- `dia`:    cuatro cuartos de 6 h: Asia 18:00-00:00 (Q1), Londres 00:00-06:00 (Q2), NY AM 06:00-12:00 (Q3), NY PM 12:00-18:00 (Q4).
- `90m`:    cuartos de 90 minutos desde las 18:00 (en NY AM: 06:00, 07:30, 09:00 y 10:30). Cada cuatro forman una sesión de 6 h.
- `semana`: un cuarto por día de trading: lunes Q1 ... jueves Q4. El viernes y el fin de semana no son cuartos.

El True Open de un ciclo es la apertura de su Q2 (en `dia`, las 00:00 NY; en `90m`, la segunda mitad de hora y media de la sesión: 07:30 en NY AM;
en `semana`, el martes).
"""
from __future__ import annotations

DAY = 86400
START = 18 * 3600                     # el día de trading empieza a las 18:00 NY
CICLOS = {"dia": 6 * 3600, "90m": 90 * 60, "semana": DAY}       # duración de un cuarto, en segundos
ETIQUETAS = {"dia": "día (6 h)", "90m": "90 minutos", "semana": "semana (días)"}


def cuarto(ny: int, ciclo: str) -> int | None:
    """Número de cuarto (creciente en el tiempo) al que pertenece el instante `ny` (segundos de NY desde 1970), o None si no es cuarto
    (viernes y fin de semana en `semana`)."""
    q = (ny - START) // CICLOS[ciclo]
    if ciclo == "semana" and _dia_semana(q) > 3:
        return None
    return int(q)


def _dia_semana(q: int) -> int:
    """Día de la semana (0 lunes) del día de trading número `q` (el que empieza a las 18:00 del día anterior)."""
    return (q + 1 + 3) % 7


def inicio(q: int, ciclo: str) -> int:
    """Instante (segundos de NY) en que empieza el cuarto `q`."""
    return START + q * CICLOS[ciclo]


def numero(q: int, ciclo: str) -> int:
    """Posición del cuarto dentro de su ciclo: 1 a 4."""
    return _dia_semana(q) + 1 if ciclo == "semana" else q % 4 + 1


def cuarto_true_open(q: int, ciclo: str) -> int:
    """Cuarto cuya apertura es el True Open del ciclo que contiene a `q` (su Q2)."""
    return q - _dia_semana(q) + 1 if ciclo == "semana" else (q // 4) * 4 + 1
