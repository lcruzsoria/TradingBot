"""Niveles del día: TDO, Midnight, PDH / PDL y separadores de día.

El "día de trading" es el día del servidor del broker, el mismo que usa el Bias (en Vantage, servidor = NY + 7 h:
el día empieza a las 17:00 de NY y su primera vela, a las 18:00, es la apertura del mercado).

- TDO: apertura de la primera vela del día de trading (apertura del mercado).
- Midnight: apertura de la primera vela desde las 00:00 de Nueva York de ese día.
- PDH / PDL: máximo y mínimo del día de trading anterior.
Cada nivel se dibuja desde su vela hasta el final de su día; los del día en curso, un poco más allá de la última vela.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np

DAY = 86_400
EXTEND_BARS = 2          # los niveles del día en curso pasan un poco de la última vela (su rótulo no tapa el precio)
WEEKDAYS = ("LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO")

# Valores por defecto (tradingbot.env, bloque LEVELS)
DEFAULT_DAYS = 10
DEFAULT_MAX_TF_MINUTES = 720          # hasta H12: con velas diarias "el día" es una sola vela
DEFAULT_COLORS = {"TDO": "#787B86", "MIDNIGHT": "#FF9800", "PDHL": "#2962FF", "SEPARATOR": "#787B86"}


@dataclass(frozen=True)
class Line:
    kind: str            # "tdo", "midnight", "pdh" o "pdl"
    price: float
    x0: float            # índice de vela donde empieza...
    x1: float            # ...y donde acaba (final del día, o borde derecho en el día en curso)


@dataclass(frozen=True)
class Separator:
    x: float             # entre la última vela de un día y la primera del siguiente
    label: str           # día de la semana del día que empieza


def day_index(ts) -> np.ndarray:
    """Día de trading (día del servidor) de cada vela, como número de días desde 1970."""
    return np.asarray(ts, dtype=np.int64) // DAY


def separators(ts) -> list[Separator]:
    """Un separador al empezar cada día de trading (todo el histórico; se pintan solo los visibles)."""
    days = day_index(ts)
    if len(days) < 2:
        return []
    starts = np.flatnonzero(np.diff(days)) + 1
    return [Separator(float(i) - 0.5, WEEKDAYS[_date(int(days[i])).weekday()]) for i in starts]


def compute(ts, open_, high, low, server_ahead: int, days: int = DEFAULT_DAYS) -> list[Line]:
    """Líneas de los últimos `days` días de trading con velas."""
    n = len(ts)
    if n == 0 or days <= 0:
        return []
    ts = np.asarray(ts, dtype=np.int64)
    open_, high, low = (np.asarray(a, dtype=float) for a in (open_, high, low))
    day_of = ts // DAY
    starts = np.r_[0, np.flatnonzero(np.diff(day_of)) + 1]
    ends = np.r_[starts[1:], n]
    out: list[Line] = []
    first = max(0, len(starts) - days)
    for k in range(first, len(starts)):
        i0, i1 = int(starts[k]), int(ends[k])
        x0 = i0 - 0.5
        x1 = float(n - 1 + EXTEND_BARS) if k == len(starts) - 1 else i1 - 0.5
        out.append(Line("tdo", float(open_[i0]), x0, x1))
        # medianoche de Nueva York dentro de este día del servidor
        midnight = int(day_of[i0]) * DAY + server_ahead % DAY
        j = i0 + int(np.searchsorted(ts[i0:i1], midnight, "left"))
        if j < i1:
            out.append(Line("midnight", float(open_[j]), j - 0.5, x1))
        if k > 0:
            p0, p1 = int(starts[k - 1]), i0
            out.append(Line("pdh", float(high[p0:p1].max()), x0, x1))
            out.append(Line("pdl", float(low[p0:p1].min()), x0, x1))
    return out


def _date(day: int) -> date:
    return date.fromordinal(date(1970, 1, 1).toordinal() + day)
