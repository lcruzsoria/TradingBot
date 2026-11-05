"""Huecos de apertura NDOG y NWOG, calculados con velas (M5 o M15: el cierre y la apertura que forman el hueco son los mismos).

NDOG (hueco diario): entre el cierre de la última vela antes de las 17:00 NY y la apertura de la primera vela desde esa hora (el
cierre de las 17:00 frente a la reapertura). NWOG (hueco semanal): entre el cierre del viernes y la apertura del domingo, es decir, el
cierre de la última vela antes de una pausa larga (fin de semana) y la apertura de la primera tras ella.

Cada hueco es un `Gap` con sus dos precios; `low` y `high` dan sus bordes y `mid` su 50 %, que es el nivel que se usa. Se devuelve el último de cada tipo anterior a `before_ts`.
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
    def mid(self) -> float:
        """El 50 % del hueco: el nivel que se usa como objetivo (evita confusiones con cuál de los dos bordes)."""
        return (self.close + self.open) / 2

    @property
    def low(self) -> float:
        return min(self.close, self.open)

    @property
    def high(self) -> float:
        return max(self.close, self.open)


def gap_list(ts, open_, close, ahead: int, hour: int = DEFAULT_HOUR) -> list[Gap]:
    """Todos los NDOG y NWOG del histórico, del más antiguo al más reciente (`ahead`: servidor - NY, en segundos)."""
    ts = np.asarray(ts)
    n = len(ts)
    if n < 2:
        return []
    ny = ts - ahead
    tod = (ny % DAY) // 60                                    # minuto del día en NY de cada vela
    pause = np.diff(ts)                                       # segundos entre el inicio de dos velas consecutivas
    out = []
    for i in range(1, n):
        weekend = pause[i - 1] >= WEEKEND_MIN
        daily = (not weekend and pause[i - 1] <= BREAK_MAX and tod[i] >= hour and (tod[i - 1] < hour or ny[i] // DAY != ny[i - 1] // DAY))
        if weekend or daily:
            out.append(Gap("NWOG" if weekend else "NDOG", float(close[i - 1]), float(open_[i]), int(ts[i - 1]), int(ts[i])))
    return out


def opening_gaps(ts, open_, close, before_ts: int, ahead: int, hour: int = DEFAULT_HOUR) -> dict[str, Gap | None]:
    """El último NDOG y el último NWOG cuyo hueco termina antes de `before_ts` (hora del servidor)."""
    ts = np.asarray(ts)
    n = int(np.searchsorted(ts, before_ts, "left"))          # solo velas anteriores a before_ts
    out: dict[str, Gap | None] = {"NDOG": None, "NWOG": None}
    for gap in gap_list(ts[:n], open_[:n], close[:n], ahead, hour):
        out[gap.kind] = gap
    return out


def gap_lines(ts, open_, close, ahead: int, line_cls, hour: int = DEFAULT_HOUR, extend: float = 8.0) -> list:
    """Líneas del gráfico de cada hueco: sus dos bordes (`ndog` / `nwog`) y su 50 % (`ndog50` / `nwog50`).

    Cada hueco se dibuja desde su apertura hasta el siguiente de su tipo (el último, hasta el borde derecho). `line_cls`: la clase `Line` del gráfico.
    """
    ts = np.asarray(ts)
    gaps = gap_list(ts, np.asarray(open_), np.asarray(close), ahead, hour)
    last_x = float(len(ts) - 1 + extend)
    out = []
    for kind in ("NDOG", "NWOG"):
        own = [g for g in gaps if g.kind == kind]
        for k, gap in enumerate(own):
            x0 = float(np.searchsorted(ts, gap.open_ts, "left")) - 0.5
            x1 = float(np.searchsorted(ts, own[k + 1].open_ts, "left")) - 0.5 if k + 1 < len(own) else last_x
            tag = kind.lower()
            out += [line_cls(tag, gap.high, x0, x1), line_cls(tag, gap.low, x0, x1), line_cls(tag + "50", gap.mid, x0, x1)]
    return out
