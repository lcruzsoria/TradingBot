"""Patrones a identificar dentro de la TBR activa.

La **TBR activa** es la última TBR (Asia, London o NY Open) que ya cerró: nos deja definidos su High, su Low y su 50 %. Cada
patrón es una clase que se registra con `@register_pattern("clave")` y mira las velas posteriores al cierre de esa TBR, hasta
que empieza la TBR siguiente (ver `window_for`): Asia hasta London, London hasta NY Open y NY Open hasta NY PM.

Para definir un patrón nuevo (los patrones viven en esta carpeta y se importan al final de este módulo):

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


def active_tbr(sessions, zones: list[str] | None = None) -> ActiveTbr | None:
    """La última TBR ya cerrada (opcionalmente solo de las zonas `zones`, por clave), o None."""
    wanted = {z.upper() for z in zones} if zones else None
    closed = [s for s in sessions if s.complete and s.high > s.low and (wanted is None or s.zone.key in wanted)]
    if not closed:
        return None
    s = max(closed, key=lambda s: s.x1)
    return ActiveTbr(s.zone.key, s.zone.name, s.day, s.high, s.low, s.x0, s.x1)


def _hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def window_for(tbr: ActiveTbr, order, ahead: int) -> TbrWindow | None:
    """Plazo de la TBR activa. `order`: las zonas del ciclo en orden (Asia, London, NY Open, NY PM) como `Zone`.

    Termina cuando empieza la TBR siguiente del ciclo: Asia -> London, London -> NY Open y NY Open -> NY PM. Tras la última
    zona del ciclo (NY PM) no se evalúan más setups. Si la zona de la TBR no está en el ciclo, devuelve None (sin límite).
    `ahead`: segundos que el servidor va por delante de Nueva York.
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
    return TbrWindow(close_ny + ahead, None if best is None else best[0] + ahead,
                     "" if best is None else best[1].name, "" if best is None else _hhmm(best[1].start),
                     session_end, _hhmm((last.start + last.minutes) % 1440))


from . import continuation  # noqa: E402,F401  (registra los patrones definidos)
