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
    """Ruptura del día anterior: el precio está fuera del rango del día previo.

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
    """Apertura del día (por fecha del servidor): el precio está por encima o por debajo de ella.

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


def _level_vote(rule: BiasRule, ctx: BiasContext, level: float | None, name: str, missing: str) -> RuleVote:
    """Voto de una regla de nivel: +1 con el precio por encima del nivel, -1 por debajo, 0 sobre él (zona neutra opcional)."""
    price = ctx.last_price
    if price is None or level is None:
        return rule.vote(0, missing)
    tol = level * float(rule.params.get("tolerance_pct", 0.0)) / 100.0
    if price > level + tol:
        return rule.vote(1, f"Precio {fmt_price(price)} sobre {name} {fmt_price(level)}")
    if price < level - tol:
        return rule.vote(-1, f"Precio {fmt_price(price)} bajo {name} {fmt_price(level)}")
    return rule.vote(0, f"Precio {fmt_price(price)} en {name} {fmt_price(level)}")


@register_rule("tdo")
class AboveBelowTdo(BiasRule):
    """Relación del precio con el TDO (True Day Open): la apertura del día de trading de ese activo.

    El día empieza a las 18:00 de NY en los índices americanos y a las 17:00 en el resto (LEVELS_INDEX_DAY_START /
    LEVELS_DAY_START). Por encima del TDO -> alcista; por debajo -> bajista. Necesita la skill Levels.
    Parámetro opcional: tolerance_pct (zona neutra alrededor del nivel, en %).
    """
    title = "Precio vs TDO"

    def evaluate(self, ctx: BiasContext) -> RuleVote:
        return _level_vote(self, ctx, ctx.tdo, "el TDO", "Sin TDO del día (skill Levels apagada o timeframe grande)")


@register_rule("midnight")
class AboveBelowMidnight(BiasRule):
    """Relación del precio con el Midnight: la apertura de las 00:00 de Nueva York del día en curso.

    Por encima -> alcista; por debajo -> bajista. Antes de las 00:00 NY todavía no existe y no vota.
    Necesita la skill Levels. Parámetro opcional: tolerance_pct.
    """
    title = "Precio vs Midnight"

    def evaluate(self, ctx: BiasContext) -> RuleVote:
        return _level_vote(self, ctx, ctx.midnight, "el Midnight",
                           "Aún no hay Midnight (antes de las 00:00 NY) o la skill Levels está apagada")


@register_rule("htf_sweep")
class HtfSweepRule(BiasRule):
    """Barrido de la vela anterior: el sesgo de la vela actual (H3 en índices, H4 en el resto) sale de las dos anteriores.

    Si la vela n-1 barrió el High de la n-2 y cerró dentro de su rango -> bajista; si barrió el Low y cerró dentro -> alcista.
    Barrer los dos lados, cerrar fuera o no barrer no puntúa. La vela actual (0) no interviene. Ver bias/htf.py.
    Parámetros: BIAS_HTF_SWEEP_INDEX_HOURS (3) y BIAS_HTF_SWEEP_HOURS (4): tamaño de las velas en índices / resto.
    """
    title = "Barrido de la vela anterior"
    weight = 2.0

    def evaluate(self, ctx: BiasContext) -> RuleVote:
        htf = ctx.htf
        if htf is None:
            return self.vote(0, "Sin velas H3 / H4 para evaluar el barrido")
        return self.vote(htf.vote, htf.detail)


@register_rule("htf_break")
class HtfBreakRule(BiasRule):
    """Continuación de la vela anterior: el sesgo de la vela actual (H3 en índices, H4 en el resto) sale de las dos anteriores.

    Si la vela n-1 cierra POR ENCIMA del High de la n-2 -> continuación alcista; si cierra POR DEBAJO del Low de la n-2 ->
    continuación bajista; si cierra dentro de su rango no puntúa; si barre con mecha los dos lados de la n-2 tampoco puntúa.
    Es la regla complementaria del barrido: no puntúan a la vez. La vela actual (0) no interviene. Parámetros: BIAS_HTF_SWEEP_INDEX_HOURS (3) y BIAS_HTF_SWEEP_HOURS (4), compartidos.
    """
    title = "Continuación de la vela anterior"
    weight = 2.0

    def evaluate(self, ctx: BiasContext) -> RuleVote:
        brk = ctx.htf_break
        if brk is None:
            return self.vote(0, "Sin velas H3 / H4 para evaluar la continuación")
        return self.vote(brk.vote, brk.detail)
