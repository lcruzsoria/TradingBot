"""Patrones a identificar dentro de la TBR activa.

La **TBR activa** es la última TBR (Asia, London o NY Open) que ya cerró: nos deja definidos su High, su Low y su 50 %. Cada
patrón es una clase que se registra con `@register_pattern("clave")` y mira las velas posteriores al cierre de esa TBR.

Para definir un patrón nuevo (todos los patrones viven en este módulo o en otros de esta carpeta que se importen aquí):

    @register_pattern("mi_patron")
    class MiPatron(Pattern):
        title = "Mi patrón"

        def detect(self, ctx: PatternContext) -> list[PatternHit]:
            # ctx.tbr (High, Low, 50 %), ctx.high / ctx.low / ctx.close ..., ctx.first_bar (primera vela tras el cierre)
            ...
            return [PatternHit(self.key, self.title, "long", x=i, price=ctx.tbr.mid, detail="qué se vio")]

La skill llama a `detect` con cada carga de velas y de TBR; un patrón solo debe devolver lo que ve AHORA (la skill se
encarga de no repetir avisos). Cada patrón identificado pasa a la skill Setup, que lo valida con el sesgo (GO / NO GO).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import ClassVar

import numpy as np

PATTERN_REGISTRY: dict[str, type["Pattern"]] = {}


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
        """Índice de la primera vela posterior al cierre de la TBR."""
        return int(round(self.x1 + 0.5))


@dataclass(frozen=True)
class PatternContext:
    symbol: str
    timeframe: str
    tf_minutes: int
    ts: np.ndarray
    open: np.ndarray
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray
    tbr: ActiveTbr
    window_bars: int         # velas, desde el cierre de la TBR, durante las que se buscan patrones

    @property
    def first_bar(self) -> int:
        return self.tbr.first_bar

    @property
    def last_bar(self) -> int:
        """Última vela en la que se busca: el final del histórico o el fin de la ventana tras el cierre de la TBR."""
        return min(len(self.close) - 1, self.first_bar + self.window_bars - 1)


@dataclass(frozen=True)
class PatternHit:
    """Un patrón identificado en la TBR activa."""
    key: str
    title: str
    direction: str           # "long" o "short"
    x: int                   # vela en la que se identifica
    price: float             # precio de referencia (entrada, nivel roto...)
    detail: str = ""
    levels: dict[str, float] = field(default_factory=dict)   # otros precios del patrón (stop, objetivo...) para mostrarlos


class Pattern(ABC):
    key: ClassVar[str] = ""
    title: ClassVar[str] = ""

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
