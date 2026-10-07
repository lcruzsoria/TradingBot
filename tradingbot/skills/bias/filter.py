"""Filtro de operativa basado en el Bias del día.

La futura capa de ejecución debe preguntar aquí ANTES de abrir cualquier trade.
"""
from __future__ import annotations

from .models import Bias, BiasResult, Direction


class TradeFilter:
    def __init__(self) -> None:
        self._result: BiasResult | None = None

    def update(self, result: BiasResult) -> None:
        self._result = result

    @property
    def result(self) -> BiasResult | None:
        return self._result

    def check(self, direction: Direction) -> tuple[bool, str]:
        """Devuelve (permitido, motivo)."""
        if self._result is None:
            return False, "Bias aún no calculado: no se permite operar"
        if self._result.allows(direction):
            return True, f"{direction.value} permitido con {self._result.bias.value}"
        return False, f"{direction.value} bloqueado: el sesgo del día es {self._result.bias.value}"
