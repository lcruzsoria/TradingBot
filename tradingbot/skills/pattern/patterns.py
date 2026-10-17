"""Patrones a identificar dentro de la TBR activa.

La **TBR activa** es la última TBR (Asia, London o NY Open) que ya cerró: nos deja definidos su High, su Low y su 50 %. Cada
patrón es una clase que se registra con `@register_pattern("clave")` y mira las velas posteriores al cierre de esa TBR, hasta
que empieza la TBR siguiente (ver `window_for`): Asia hasta London, London hasta NY Open y NY Open hasta NY PM.

Para definir un patrón nuevo (un módulo en esta carpeta, importado al final de este módulo para que se registre; ver
`continuacion.py`):

    @register_pattern("mi_patron")
    class MiPatron(Pattern):
        title = "Mi patrón"

        def detect(self, ctx: PatternContext) -> list[PatternHit]:
            # ctx.tbr (High, Low, 50 %), ctx.high / ctx.low / ctx.close ..., y las velas a mirar: de ctx.first_bar
            # (primera vela tras el cierre de la TBR) a ctx.last_bar (última cerrada dentro del plazo)
            ...
            return [PatternHit(self.key, self.title, "long", x=i, price=ctx.tbr.mid, detail="qué se vio")]

Cada vez que llegan velas, la skill llama a `detect` y un patrón devuelve lo que ve AHORA (la skill no repite avisos). Un
resultado tiene un estado: `detected` (patrón identificado: pasa a Cortex, que lo valida con el sesgo), `invalidated` (se
rompió una condición), `annulled` (se agotó el plazo propio del patrón) o `expired` (terminó el plazo de la TBR sin
completarse). Los tres últimos solo se anotan en el Registro. `settings` (bloque PATTERN de tradingbot.env, sin prefijo)
sirve para leer los ajustes propios del patrón, y `timeframe()` para pedir un timeframe distinto al del gráfico.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import ClassVar

import numpy as np

PATTERN_REGISTRY: dict[str, type["Pattern"]] = {}
DAY = 86400

DETECTED, INVALIDATED, ANNULLED, EXPIRED = "detected", "invalidated", "annulled", "expired"


def register_pattern(key: str):
    def decorator(cls: type["Pattern"]) -> type["Pattern"]:
        cls.key = key
        PATTERN_REGISTRY[key] = cls
        return cls
    return decorator


@dataclass(frozen=True)
class ActiveTbr:
    """La última TBR cerrada: su caja y sus tres niveles."""
    key: str                 # clave de la zona (ASIA, LONDON, NY_AM...)
    zone: str                # nombre (Asia, London, NY Open...)
    day: date
    high: float
    low: float
    x0: float                # bordes de la caja en el eje del gráfico (índice de vela +- 0,5)
    x1: float

    @property
    def mid(self) -> float:
        return (self.high + self.low) / 2

    @property
    def range(self) -> float:
        return self.high - self.low

    @property
    def first_bar(self) -> int:
        """Índice (en las velas del gráfico) de la primera vela posterior al cierre de la TBR."""
        return int(round(self.x1 + 0.5))


@dataclass(frozen=True)
class TbrWindow:
    """Plazo en el que se buscan patrones en una TBR: desde su cierre hasta el inicio de la siguiente."""
    close_ts: int            # cierre de la TBR (hora del servidor, segundos)
    end_ts: int | None       # inicio de la TBR siguiente (None: sin límite)
    next_zone: str           # nombre de la TBR siguiente
    next_hours: str          # su hora de inicio en NY, HH:MM
    session_end_ts: int | None   # fin de la última zona del ciclo (NY PM): a partir de ahí no se evalúa más
    session_end_hours: str
    start_ts: int = 0        # inicio de la propia TBR (hora del servidor, segundos)
    limit_verb: str = "empezara"   # "empezara" (inicio de la TBR siguiente) o "terminara" (plazo ampliado hasta el fin de la última)


@dataclass(frozen=True)
class PatternContext:
    symbol: str
    timeframe: str           # timeframe de estas velas
    tf_minutes: int
    ts: np.ndarray
    open: np.ndarray
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray
    tbr: ActiveTbr
    first_bar: int           # primera vela posterior al cierre de la TBR
    last_bar: int            # última vela cerrada dentro del plazo
    window_closed: bool      # el plazo ya terminó (empezó la TBR siguiente)
    next_zone: str = ""
    next_hours: str = ""
    ahead: int = 0           # segundos que el servidor va por delante de Nueva York (para mostrar horas de NY)
    start_bar: int = 0       # primera vela de la propia TBR
    limit_verb: str = "empezara"   # cómo se nombra el límite: "antes de que empezara X" o "antes de que terminara X"


@dataclass(frozen=True)
class PatternHit:
    """Un resultado de un patrón en la TBR activa."""
    key: str
    title: str
    direction: str           # "long" o "short"
    x: int                   # vela en la que se identifica (o en la que se invalida, anula o vence)
    price: float             # precio de referencia (entrada, nivel roto...)
    detail: str = ""
    levels: dict[str, float] = field(default_factory=dict)   # otros precios del patrón (stop, objetivo...) para mostrarlos
    ts: int = 0              # hora (servidor) de esa vela, para mostrarla aunque el gráfico tenga otro timeframe
    status: str = DETECTED   # detected / invalidated / annulled / expired


@dataclass(frozen=True)
class Figure:
    """Algo que el patrón quiere dibujar en el gráfico: de momento, un fibonacci con los niveles 0, 0,5 y 1."""
    kind: str                # "fib"
    key: str                 # patrón
    zone: str                # TBR a la que pertenece
    direction: str           # "long" o "short"
    x0_ts: int               # desde esta vela (hora del servidor)...
    x1_ts: int               # ...hasta esta
    levels: dict[str, float]    # {"0": precio, "0,5": precio, "1": precio}
    state: str = ""          # "en curso", "entrada"
    label: str = ""


class Pattern(ABC):
    key: ClassVar[str] = ""
    title: ClassVar[str] = ""

    def __init__(self, settings=None) -> None:
        self.settings = settings         # bloque PATTERN de tradingbot.env (ya sin prefijo), o None

    def timeframe(self) -> str | None:
        """Timeframe con el que trabaja el patrón (None: el del gráfico)."""
        return None

    @abstractmethod
    def detect(self, ctx: PatternContext) -> list[PatternHit]:
        ...

    def figures(self, ctx: PatternContext) -> list[Figure]:
        """Dibujos del patrón para el gráfico (por defecto, ninguno)."""
        return []


def active_tbr(sessions, zones: list[str] | None = None) -> ActiveTbr | None:
    """La última TBR ya cerrada (opcionalmente solo de las zonas `zones`, por clave), o None."""
    wanted = {z.upper() for z in zones} if zones else None
    closed = [s for s in sessions if s.complete and s.high > s.low and (wanted is None or s.zone.key in wanted)]
    if not closed:
        return None
    s = max(closed, key=lambda s: s.x1)
    return ActiveTbr(s.zone.key, s.zone.name, s.day, s.high, s.low, s.x0, s.x1)


def recent_tbrs(sessions, zones: list[str] | None = None) -> list[ActiveTbr]:
    """La última TBR cerrada de cada zona (opcionalmente solo de las zonas `zones`), de la más antigua a la más reciente."""
    wanted = {z.upper() for z in zones} if zones else None
    latest: dict[str, object] = {}
    for s in sessions:
        if not (s.complete and s.high > s.low) or (wanted is not None and s.zone.key not in wanted):
            continue
        if s.zone.key not in latest or s.x1 > latest[s.zone.key].x1:
            latest[s.zone.key] = s
    ordered = sorted(latest.values(), key=lambda s: s.x1)
    return [ActiveTbr(s.zone.key, s.zone.name, s.day, s.high, s.low, s.x0, s.x1) for s in ordered]


def history_tbrs(sessions, zones: list[str] | None, skip: set, days: int) -> list[ActiveTbr]:
    """Las TBR cerradas de los últimos `days` días que no están en `skip` ((clave, día)), de la más antigua a la más reciente.

    Son las TBR pasadas, solo para dibujar sus fibos y entradas; las que cuentan para operar son las de `recent_tbrs`.
    """
    wanted = {z.upper() for z in zones} if zones else None
    done = [s for s in sessions if s.complete and s.high > s.low and (wanted is None or s.zone.key in wanted)]
    if not done:
        return []
    cutoff = max(s.day for s in done).toordinal() - days + 1
    old = [s for s in done if s.day.toordinal() >= cutoff and (s.zone.key, s.day) not in skip]
    old.sort(key=lambda s: s.x1)
    return [ActiveTbr(s.zone.key, s.zone.name, s.day, s.high, s.low, s.x0, s.x1) for s in old]


def _hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def window_for(tbr: ActiveTbr, order, ahead: int, extend=(), until=None) -> TbrWindow | None:
    """Plazo de la TBR activa. `order`: las zonas del ciclo en orden (Asia, London, NY Open, NY PM) como `Zone`.

    Termina cuando empieza la TBR siguiente del ciclo: Asia -> London, London -> NY Open y NY Open -> NY PM. Tras la última
    zona del ciclo (NY PM) no se evalúan más setups. Si la zona de la TBR no está en el ciclo, devuelve None (sin límite).
    `extend`: claves de zona cuyo plazo se amplía hasta el final de la última zona del ciclo (p. ej. NY_AM hasta el fin de
    NY PM, en vez de hasta el inicio de NY PM). `until`: {clave de zona: clave de otra zona, o 'CLAVE:FIN'} para que el plazo llegue hasta el inicio
    (o el final, con ':FIN') de esa otra zona, o 'ZONA@HH:MM' para que llegue hasta esa hora de NY (p. ej. ASIA -> NY_AM: Asia hasta el inicio de NY Open, en vez de hasta London). `ahead`: segundos que el servidor va por delante de Nueva York.
    """
    zone = next((z for z in order if z.key == tbr.key), None)
    if zone is None:
        return None
    day = tbr.day.toordinal() - date(1970, 1, 1).toordinal()
    close_ny = day * DAY + zone.start * 60 + zone.minutes * 60
    best = None
    for other in order:
        if other.key == tbr.key:
            continue
        for k in range(0, 3):
            start = (day + k) * DAY + other.start * 60
            if start >= close_ny and (best is None or start < best[0]):
                best = (start, other)
    last = order[-1]
    session_end = None
    if best is not None and best[1].key == last.key:
        session_end = best[0] + last.minutes * 60 + ahead          # la siguiente zona es la última: su final cierra la jornada
    start_ts = close_ny - zone.minutes * 60 + ahead
    last_hours = _hhmm((last.start + last.minutes) % 1440)
    spec = (until or {}).get(tbr.key, "")
    if "@" in spec:                                                       # "NY_AM@18:00": hasta una hora fija de NY
        h, m = (int(x) for x in spec.split("@", 1)[1].split(":"))
        wall = h * 60 + m
        end = min(s for s in ((day + k) * DAY + wall * 60 for k in range(0, 3)) if s >= close_ny) + ahead
        return TbrWindow(close_ny + ahead, end, "el plazo", _hhmm(wall), end, _hhmm(wall), start_ts, "terminara")
    to_end = spec.upper().endswith(":FIN")                               # "NY_AM:FIN": hasta el final de esa zona
    target = next((z for z in order if z.key == spec.upper().removesuffix(":FIN")), None)
    if target is not None and target.key != tbr.key:
        begin = min(s for s in ((day + k) * DAY + target.start * 60 for k in range(0, 3)) if s >= close_ny)
        if to_end:
            end = begin + target.minutes * 60 + ahead
            return TbrWindow(close_ny + ahead, end, target.name, _hhmm((target.start + target.minutes) % 1440),
                             end if target.key == last.key else None, last_hours, start_ts, "terminara")
        ends_session = begin + target.minutes * 60 + ahead if target.key == last.key else None
        return TbrWindow(close_ny + ahead, begin + ahead, target.name, _hhmm(target.start), ends_session, last_hours, start_ts)
    if tbr.key in {k.upper() for k in extend} and last.key != tbr.key:
        first_last = min((day + k) * DAY + last.start * 60 for k in range(0, 3) if (day + k) * DAY + last.start * 60 >= close_ny)
        end = first_last + last.minutes * 60 + ahead              # el plazo llega hasta el final de la última zona del ciclo
        return TbrWindow(close_ny + ahead, end, last.name, last_hours, end, last_hours, start_ts, "terminara")
    return TbrWindow(close_ny + ahead, None if best is None else best[0] + ahead,
                     "" if best is None else best[1].name, "" if best is None else _hhmm(best[1].start),
                     session_end, last_hours, start_ts)


from . import continuacion, reversion  # noqa: E402,F401  (registran los patrones definidos)
