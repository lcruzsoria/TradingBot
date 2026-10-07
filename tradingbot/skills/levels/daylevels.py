"""Niveles del día: TDO, Midnight, PDH / PDL y separadores de día.

El "día de trading" empieza a una hora fija de Nueva York que depende del activo (tradingbot.env, bloque LEVELS):
las 18:00 para los índices americanos (NAS100, SP500, DJ30...) y las 17:00 para el resto. Lleva el nombre del día en
que termina: el que empieza el martes a las 17:00 es el MIÉRCOLES.

- TDO (True Day Open): apertura de la primera vela del día de trading.
- Midnight: apertura de la primera vela desde las 00:00 de Nueva York de ese día.
- PDH / PDL: máximo y mínimo del día de trading anterior.
Cada nivel se dibuja desde su vela hasta el final de su día; los del día en curso, un poco más allá de la última vela.
Un separador vertical marca el inicio de cada día, y el nombre del día va centrado entre su separador y el siguiente.
"""
from __future__ import annotations

import re
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
DEFAULT_DAY_START = "17:00"           # inicio del día (y TDO) en hora de NY: forex, metales, cripto...
DEFAULT_INDEX_DAY_START = "18:00"     # ...y en los índices americanos
DEFAULT_US_INDICES = ("NAS100", "SP500", "DJ30", "US30", "US100", "US500", "USTEC", "US2000", "SPX500", "NDX100")

TIME = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*$")


@dataclass(frozen=True)
class Line:
    kind: str            # "tdo", "midnight", "pdh" o "pdl"
    price: float
    x0: float            # índice de vela donde empieza...
    x1: float            # ...y donde acaba (final del día, o borde derecho en el día en curso)


@dataclass(frozen=True)
class Day:
    """Un día de trading en el eje del gráfico (índices de vela +- 0,5)."""
    x0: float            # borde izquierdo: aquí va su separador (salvo en el primer día cargado)
    x1: float            # borde derecho: el separador del día siguiente, o la última vela
    label: str           # nombre del día (LUNES, MARTES...)

    @property
    def center(self) -> float:
        return (self.x0 + self.x1) / 2


def parse_time(text: str, key: str) -> int:
    """'17:00' -> minutos desde medianoche."""
    match = TIME.match(text or "")
    if not match or int(match.group(1)) > 23 or int(match.group(2)) > 59:
        raise ValueError(f"{key}={text!r}: usa el formato HH:MM (por ejemplo 17:00).")
    return int(match.group(1)) * 60 + int(match.group(2))


def is_us_index(symbol: str, prefixes) -> bool:
    """NAS100.r, nas100ft.r, SP500... (sin distinguir mayúsculas y con cualquier sufijo del broker)."""
    name = symbol.strip().lower()
    return any(name.startswith(p.strip().lower()) for p in prefixes if p.strip())


def trading_day(ts, server_ahead: int, start_minutes: int) -> np.ndarray:
    """Día de trading de cada vela (días desde 1970, con la fecha del día en que termina)."""
    ny = np.asarray(ts, dtype=np.int64) - int(server_ahead)
    return (ny - start_minutes * 60) // DAY + 1


def days(ts, server_ahead: int, start_minutes: int) -> list[Day]:
    """Los días de trading del histórico, con sus bordes en el eje y su nombre."""
    n = len(ts)
    if n == 0:
        return []
    day_of = trading_day(ts, server_ahead, start_minutes)
    starts = np.r_[0, np.flatnonzero(np.diff(day_of)) + 1]
    ends = np.r_[starts[1:], n]
    return [Day(float(i0) - 0.5, float(i1) - 0.5, WEEKDAYS[_date(int(day_of[i0])).weekday()])
            for i0, i1 in zip(starts, ends)]


def compute(ts, open_, high, low, server_ahead: int, start_minutes: int,
            days_back: int = DEFAULT_DAYS) -> list[Line]:
    """Líneas de los últimos `days_back` días de trading con velas."""
    n = len(ts)
    if n == 0 or days_back <= 0:
        return []
    ts = np.asarray(ts, dtype=np.int64)
    open_, high, low = (np.asarray(a, dtype=float) for a in (open_, high, low))
    day_of = trading_day(ts, server_ahead, start_minutes)
    starts = np.r_[0, np.flatnonzero(np.diff(day_of)) + 1]
    ends = np.r_[starts[1:], n]
    out: list[Line] = []
    for k in range(max(0, len(starts) - days_back), len(starts)):
        i0, i1 = int(starts[k]), int(ends[k])
        x0 = i0 - 0.5
        x1 = float(n - 1 + EXTEND_BARS) if k == len(starts) - 1 else i1 - 0.5
        out.append(Line("tdo", float(open_[i0]), x0, x1))
        # 00:00 de Nueva York del día en que termina este día de trading, en hora del servidor
        midnight = int(day_of[i0]) * DAY + int(server_ahead)
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
