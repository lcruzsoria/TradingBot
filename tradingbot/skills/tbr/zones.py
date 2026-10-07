"""TBR (Time-Based Ranges): zonas horarias del día en hora de Nueva York y sus niveles.

Cada zona (Asia, London, Pre-NY, NY-AM, NY-PM...) es una franja horaria fija en hora de Nueva York. Para cada día y
zona se calcula el máximo (High), el mínimo (Low) y el punto medio (50 %) de las velas de esa franja: la zona se dibuja
como una caja del Low al High. Cuando la franja termina, cada nivel sale del borde derecho de la caja y se extiende
hasta que una vela posterior lo "toma" (lo toca o lo atraviesa); si ninguna lo ha tomado aún, llega al borde derecho.

Las velas llegan con la hora del servidor del broker. `server_minus_ny` es cuánto va el servidor por delante de Nueva
York (en los brokers con cierre en Nueva York, como Vantage, siempre 7 h, también al cambiar de horario).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

import numpy as np


DAY = 86_400
EXTEND_BARS = 8          # un nivel aún no tomado se prolonga hasta este margen a la derecha de la última vela

# Valores por defecto (se cambian en tradingbot.env, bloque TBR)
DEFAULT_SHOW = False
DEFAULT_DAYS = 10
DEFAULT_OPACITY = 12     # % de opacidad del relleno de las zonas (traslúcido)
DEFAULT_LINE_OPACITY = 60   # % de opacidad de las líneas High, Low y 50 %
DEFAULT_MAX_TF_MINUTES = 60
DEFAULT_ZONES = (        # clave, nombre, horario NY, color
    ("ASIA", "Asia", "20:00-00:00", "#FFD60A"),
    ("LONDON", "London", "02:00-05:00", "#FF3B30"),
    ("PRE_NY", "Pre-NY", "09:00-10:00", "#9E9E9E"),
    ("NY_AM", "NY-AM", "10:00-12:00", "#00C853"),
    ("NY_PM", "NY-PM", "13:30-16:30", "#A64DFF"),
)

HOURS = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*$")
COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


@dataclass(frozen=True)
class Zone:
    key: str
    name: str
    start: int           # minutos desde medianoche (hora de NY)
    end: int
    color: str           # #RRGGBB

    @property
    def minutes(self) -> int:
        """Duración; si termina a la misma hora o antes que empieza, acaba al día siguiente (20:00-00:00 = 4 h)."""
        return (self.end - self.start) % 1440 or 1440

    @property
    def hours(self) -> str:
        return f"{self.start // 60:02d}:{self.start % 60:02d}-{self.end // 60:02d}:{self.end % 60:02d}"


@dataclass(frozen=True)
class Level:
    kind: str            # "high", "low" o "mid" (50 %)
    price: float
    x0: float            # desde el final de la zona (índice de vela)...
    x1: float            # ...hasta la vela que lo toma, o el borde derecho si sigue intacto
    taken: bool


@dataclass(frozen=True)
class Session:
    zone: Zone
    day: date            # día (hora de NY) en que empieza la zona
    x0: float            # bordes de la zona en el eje del gráfico (índice de vela +- 0,5)
    x1: float
    complete: bool       # False mientras la franja sigue en curso (aún sin niveles)
    high: float          # caja de la zona: del Low al High de sus velas (en curso: lo que va de franja)
    low: float
    levels: tuple[Level, ...] = ()


def parse_hours(text: str, key: str = "HOURS") -> tuple[int, int]:
    match = HOURS.match(text or "")
    if not match:
        raise ValueError(f"TBR_{key}={text!r}: usa el formato HH:MM-HH:MM (por ejemplo 20:00-00:00).")
    h0, m0, h1, m1 = (int(g) for g in match.groups())
    if h0 > 23 or h1 > 24 or m0 > 59 or m1 > 59 or (h1 == 24 and m1):
        raise ValueError(f"TBR_{key}={text!r}: hora no válida.")
    return h0 * 60 + m0, (h1 * 60 + m1) % 1440


def zones_from_settings(settings) -> list[Zone]:
    """Zonas del bloque TBR de tradingbot.env (`settings` ya sin el prefijo TBR_)."""
    defaults = {key: (name, hours, color) for key, name, hours, color in DEFAULT_ZONES}
    keys = [k.upper() for k in settings.get_list("ZONES", list(defaults))]
    zones = []
    for key in keys:
        name, hours, color = defaults.get(key, (key.replace("_", " ").title(), None, None))
        hours = settings.get(f"{key}_HOURS", hours)
        color = settings.get(f"{key}_COLOR", color)
        if hours is None or color is None:
            raise ValueError(f"La zona TBR {key} necesita TBR_{key}_HOURS y TBR_{key}_COLOR en tradingbot.env.")
        if not COLOR.match(color):
            raise ValueError(f"TBR_{key}_COLOR={color!r}: usa un color #RRGGBB.")
        start, end = parse_hours(hours, f"{key}_HOURS")
        zones.append(Zone(key, settings.get(f"{key}_NAME", name), start, end, color.upper()))
    return zones


def compute(ts, high, low, zones: list[Zone], server_ahead: int, tf_minutes: int,
            days: int = DEFAULT_DAYS) -> list[Session]:
    """Zonas y niveles de los últimos `days` días (naturales, en hora de NY).

    `ts` son las horas de apertura de las velas (servidor, segundos), ordenadas. Una vela pertenece a la zona si se
    solapa con ella (así H1 también recoge la franja 13:30-16:30).
    """
    n = len(ts)
    if n == 0 or not zones or days <= 0:
        return []
    ny = np.asarray(ts, dtype=np.int64) - int(server_ahead)
    high, low = np.asarray(high, dtype=float), np.asarray(low, dtype=float)
    tf = int(tf_minutes) * 60
    last_day = int(ny[-1] // DAY)
    out: list[Session] = []
    for day in range(last_day - days + 1, last_day + 1):
        for zone in zones:
            start = day * DAY + zone.start * 60
            end = start + zone.minutes * 60
            i0 = int(np.searchsorted(ny, start - tf, "right"))      # primera vela que termina después del inicio
            i1 = int(np.searchsorted(ny, end, "left"))              # velas que empiezan antes del final
            if i1 <= i0:
                continue                                            # sin velas (fin de semana, festivo...)
            complete = i1 < n or int(ny[-1]) + tf >= end
            x0, x1 = i0 - 0.5, i1 - 0.5
            hi, lo = float(high[i0:i1].max()), float(low[i0:i1].min())
            levels: tuple[Level, ...] = ()
            if complete:
                mid = (hi + lo) / 2
                after_h, after_l = high[i1:], low[i1:]
                levels = tuple(_level(kind, price, hit, x1, i1, n) for kind, price, hit in (
                    ("high", hi, after_h >= hi),
                    ("low", lo, after_l <= lo),
                    ("mid", mid, (after_l <= mid) & (after_h >= mid)),
                ))
            out.append(Session(zone, date.fromordinal(date(1970, 1, 1).toordinal() + day), x0, x1, complete, hi, lo,
                               levels))
    return out


def _level(kind: str, price: float, hit: np.ndarray, x0: float, i1: int, n: int) -> Level:
    idx = np.flatnonzero(hit)
    if idx.size:
        return Level(kind, price, x0, float(i1 + idx[0]), True)
    return Level(kind, price, x0, float(n - 1 + EXTEND_BARS), False)
