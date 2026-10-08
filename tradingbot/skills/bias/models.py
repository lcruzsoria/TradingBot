"""Tipos del módulo Bias."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class Bias(str, Enum):
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NO_BIAS = "No Bias"


class Direction(str, Enum):
    LONG = "Long"
    SHORT = "Short"


@dataclass(frozen=True)
class RuleVote:
    """Resultado de una regla: +1 alcista, -1 bajista, 0 sin opinión, con el peso de la regla."""
    rule: str
    vote: int
    detail: str
    weight: float = 1.0

    @property
    def points(self) -> float:
        """Aportación a la puntuación del sesgo: voto x peso."""
        return self.vote * self.weight


@dataclass(frozen=True)
class BiasResult:
    bias: Bias
    day: date | None
    votes: tuple[RuleVote, ...] = ()
    levels: dict[str, float] = field(default_factory=dict)
    summary: str = ""
    score: float = 0.0          # suma de voto x peso de todas las reglas
    min_score: float = 1.0      # puntuación mínima (en valor absoluto) para que haya sesgo

    def allows(self, direction: Direction) -> bool:
        """Filtro de operativa: Bullish solo Long, Bearish solo Short, No Bias ambas."""
        if self.bias is Bias.NO_BIAS:
            return True
        if self.bias is Bias.BULLISH:
            return direction is Direction.LONG
        return direction is Direction.SHORT
