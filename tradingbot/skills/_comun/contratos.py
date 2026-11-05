"""Tipos que se intercambian las skills de patrones y Cortex, Setup y la ventana (no pertenecen a ninguna skill concreta).

Los define este módulo neutro para que una skill pueda publicar `pattern.detected`, `pattern.updated`... sin depender del código de otra
(Pattern, Barrido RTH...). Pattern los vuelve a exportar con los mismos nombres.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

DETECTED, INVALIDATED, ANNULLED, EXPIRED = "detected", "invalidated", "annulled", "expired"


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
    variant: str = ""        # caso del patrón (Continuación: «A. Ideal» o «B. Flexible»); vacío si el patrón no distingue casos


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
    day: str = ""            # día de la TBR (AAAA-MM-DD): con la zona identifica la sesión
    target: str = ""         # nombre del nivel objetivo («-0,2»): el gráfico lo pinta en rojo


