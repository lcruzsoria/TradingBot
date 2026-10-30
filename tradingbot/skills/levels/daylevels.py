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
from datetime import date, datetime

import numpy as np

DAY = 86_400
EXTEND_BARS = 2          # los niveles del día en curso pasan un poco de la última vela (su rótulo no tapa el precio)
WEEKDAYS = ("LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO")

# Valores por defecto (tradingbot.env, bloque LEVELS)
DEFAULT_DAYS = 10
DEFAULT_MAX_TF_MINUTES = 720          # hasta H12: con velas diarias "el día" es una sola vela
DEFAULT_COLORS = {"TDO": "#787B86", "MIDNIGHT": "#FF9800", "PDHL": "#2962FF", "SEPARATOR": "#787B86", "SMA": "#00ACC1",
                  "VWAP": "#E040FB"}
DEFAULT_SMA_PERIOD = 30                # velas del timeframe que se está viendo
SMA_STYLES = ("normal", "discontinuo", "punteado")
SMA_SHOWS = ("sma", "vwap", "ambos")   # qué dibuja el botón SMA: la media, el VWAP o los dos
DEFAULT_SMA_SHOW = "sma"
DEFAULT_MARKET_CLOSE = "17:00"        # cierre de los futuros de índices (diario) y de Forex (semanal), hora de NY
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


def vwap(ts, high, low, close, volume, server_ahead: int, start_minutes: int) -> tuple[np.ndarray, list[int]]:
    """VWAP de cada vela, con reinicio en cada día de trading (el mismo día que usan TDO, PDH / PDL y los separadores).

    Precio típico (máximo + mínimo + cierre) / 3 ponderado por el volumen (tick volume del broker), acumulado desde la
    primera vela del día. Sin volumen acumulado (todo 0 o sin datos) no hay VWAP: NaN. Devuelve (valores, índices de
    las velas donde empieza un día nuevo, salvo la primera): el gráfico corta ahí la línea, como TradingView.
    """
    n = len(ts)
    out = np.full(n, np.nan)
    if n == 0:
        return out, []
    typical = (np.asarray(high, dtype=float) + np.asarray(low, dtype=float) + np.asarray(close, dtype=float)) / 3
    vol = np.nan_to_num(np.asarray(volume, dtype=float), nan=0.0)
    day_of = trading_day(ts, server_ahead, start_minutes)
    starts = np.r_[0, np.flatnonzero(np.diff(day_of)) + 1]
    ends = np.r_[starts[1:], n]
    for i0, i1 in zip(starts, ends):
        cum_vol = np.cumsum(vol[i0:i1])
        cum_pv = np.cumsum((typical * vol)[i0:i1])
        out[i0:i1] = np.divide(cum_pv, cum_vol, out=np.full(i1 - i0, np.nan), where=cum_vol > 0)
    return out, [int(i) for i in starts[1:]]


def _date(day: int) -> date:
    return date.fromordinal(date(1970, 1, 1).toordinal() + day)


def market_close(prev: datetime, now: datetime, close_minutes: int) -> dict | None:
    """Cierre de mercado ocurrido entre `prev` y `now` (hora de NY), o None.

    Los futuros de los índices americanos cierran cada día laborable a la hora de cierre (17:00 NY) y reabren una hora
    después. Forex, metales y cripto cierran solo el viernes (cierre semanal, a la misma hora) y reabren el domingo.
    Sábados y domingos no hay cierres.
    """
    if prev >= now or now.weekday() > 4:
        return None
    closing = now.replace(hour=close_minutes // 60, minute=close_minutes % 60, second=0, microsecond=0)
    if not prev < closing <= now:
        return None
    weekly = now.weekday() == 4
    return {"when": closing, "weekly": weekly,
            "markets": ("Futuros de índices USA", "Forex") if weekly else ("Futuros de índices USA",)}


def new_trading_day(prev: datetime, now: datetime, start_minutes: int) -> dict | None:
    """Cambio de día de trading ocurrido entre `prev` y `now` (hora de NY) para un activo cuyo día empieza a `start_minutes`.

    El día lleva el nombre del día en que termina (el que empieza el domingo por la tarde es el LUNES). Los mercados
    abren de domingo a jueves por la tarde: el viernes y el sábado no empieza ningún día de trading.
    """
    if prev >= now or now.weekday() not in (6, 0, 1, 2, 3):
        return None
    start = now.replace(hour=start_minutes // 60, minute=start_minutes % 60, second=0, microsecond=0)
    if not prev < start <= now:
        return None
    return {"when": start, "day": WEEKDAYS[(now.weekday() + 1) % 7]}
