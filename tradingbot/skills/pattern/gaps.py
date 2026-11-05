"""Huecos de apertura NDOG y NWOG, calculados con velas (M5 o M15: el cierre y la apertura que forman el hueco son los mismos).

NDOG (hueco diario): entre el cierre de la última vela antes de las 17:00 NY y la apertura de la primera vela desde esa hora (el
cierre de las 17:00 frente a la reapertura). NWOG (hueco semanal): entre el cierre del viernes y la apertura del domingo, es decir, el
cierre de la última vela antes de una pausa larga (fin de semana) y la apertura de la primera tras ella.

Cada hueco es un `Gap` con sus dos precios; `low` y `high` dan sus bordes. Se devuelve el último de cada tipo anterior a `before_ts`.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

DAY = 86400
DEFAULT_HOUR = 17 * 60             # minutos desde medianoche de NY: cierre diario
BREAK_MAX = 3 * 3600               # una pausa de más de esto entre dos velas no es la diaria: es el fin de semana (o un festivo)
WEEKEND_MIN = 24 * 3600


@dataclass(frozen=True)
class Gap:
    kind: str            # "NDOG" o "NWOG"
    close: float         # cierre de la última vela antes del hueco
    open: float          # apertura de la primera vela después
    close_ts: int        # inicio de esa última vela (hora del servidor)
    open_ts: int         # inicio de la primera vela posterior

    @property
    def low(self) -> float:
        return min(self.close, self.open)

    @property
    def high(self) -> float:
        return max(self.close, self.open)


def opening_gaps(ts, open_, close, before_ts: int, ahead: int, hour: int = DEFAULT_HOUR) -> dict[str, Gap | None]:
    """El último NDOG y el último NWOG cuyo hueco termina antes de `before_ts` (hora del servidor; `ahead`: servidor - NY, en segundos)."""
    ts = np.asarray(ts)
    n = int(np.searchsorted(ts, before_ts, "left"))          # solo velas anteriores a before_ts
    out: dict[str, Gap | None] = {"NDOG": None, "NWOG": None}
    if n < 2:
        return out
    ny = ts[:n] - ahead
    tod = (ny % DAY) // 60                                    # minuto del día en NY de cada vela
    pause = np.diff(ts[:n])                                   # segundos entre el inicio de dos velas consecutivas
    for i in range(n - 1, 0, -1):                             # de la más reciente a la más antigua
        weekend = pause[i - 1] >= WEEKEND_MIN
        daily = (not weekend and pause[i - 1] <= BREAK_MAX and tod[i] >= hour and (tod[i - 1] < hour or ny[i] // DAY != ny[i - 1] // DAY))
        kind = "NWOG" if weekend else "NDOG" if daily else None
        if kind and out[kind] is None:
            out[kind] = Gap(kind, float(close[i - 1]), float(open_[i]), int(ts[i - 1]), int(ts[i]))
        if all(out.values()):
            break
    return out
