"""Reglas de Bias.

Cada regla es una clase que hereda de BiasRule, se registra con @register_rule("clave")
y devuelve un RuleVote (+1 alcista, -1 bajista, 0 sin opinión).

Para añadir un criterio nuevo:
  1. Crea aquí una clase nueva (copia una de las de ejemplo).
  2. Actívala en tradingbot.env añadiendo su clave a BIAS_RULES (sus parámetros: BIAS_<REGLA>_<PARÁMETRO>).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from .context import BiasContext
from .models import RuleVote

RULE_REGISTRY: dict[str, type["BiasRule"]] = {}


def register_rule(key: str):
    def decorator(cls: type["BiasRule"]) -> type["BiasRule"]:
        cls.key = key
        RULE_REGISTRY[key] = cls
        return cls
    return decorator


def fmt_price(value: float) -> str:
    if value >= 1000:
        return f"{value:,.2f}"
    return f"{value:.3f}" if value >= 10 else f"{value:.5f}"


class BiasRule(ABC):
    key: ClassVar[str] = ""
    title: ClassVar[str] = ""
    weight: float = 1.0            # peso por defecto en la puntuación del sesgo (BIAS_<REGLA>_WEIGHT lo cambia)

    def __init__(self, weight: float | None = None, **params):
        if weight is not None:
            self.weight = float(weight)
        self.params = params

    @abstractmethod
    def evaluate(self, ctx: BiasContext) -> RuleVote:
        ...

    def vote(self, vote: int, detail: str) -> RuleVote:
        return RuleVote(self.title or self.key, vote, detail, self.weight)


@register_rule("prev_day_break")
class PrevDayBreak(BiasRule):
    """EJEMPLO: el precio está fuera del rango del día anterior.

    Por encima del máximo previo -> alcista; por debajo del mínimo previo -> bajista.
    """
    title = "Ruptura del día anterior"
    weight = 2.0      # estructura: cerrar fuera del rango previo pesa más que el contexto intradía

    def evaluate(self, ctx: BiasContext) -> RuleVote:
        price, high, low = ctx.last_price, ctx.prev_high, ctx.prev_low
        if price is None or high is None or low is None:
            return self.vote(0, "Sin datos del día anterior")
        if price > high:
            return self.vote(1, f"Precio {fmt_price(price)} sobre el máximo previo {fmt_price(high)}")
        if price < low:
            return self.vote(-1, f"Precio {fmt_price(price)} bajo el mínimo previo {fmt_price(low)}")
        return self.vote(0, f"Precio {fmt_price(price)} dentro del rango previo")


@register_rule("above_below_open")
class AboveBelowOpen(BiasRule):
    """EJEMPLO: el precio está por encima o por debajo de la apertura del día.

    Parámetro opcional: tolerance_pct (zona neutra alrededor de la apertura, en %).
    """
    title = "Precio vs apertura del día"

    def evaluate(self, ctx: BiasContext) -> RuleVote:
        price, day_open = ctx.last_price, ctx.day_open
        if price is None or day_open is None:
            return self.vote(0, "Sin velas del día")
        tol = day_open * float(self.params.get("tolerance_pct", 0.0)) / 100.0
        if price > day_open + tol:
            return self.vote(1, f"Precio {fmt_price(price)} sobre la apertura {fmt_price(day_open)}")
        if price < day_open - tol:
            return self.vote(-1, f"Precio {fmt_price(price)} bajo la apertura {fmt_price(day_open)}")
        return self.vote(0, f"Precio {fmt_price(price)} en la apertura {fmt_price(day_open)}")
