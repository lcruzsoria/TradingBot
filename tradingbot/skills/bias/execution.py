"""Bias Execution: decide si un setup detectado se puede ejecutar (GO) o no (NO GO), y por qué.

Cada setup pasa por una lista de controles; basta que falle uno para que sea NO GO:

1. Confirmado     el setup ya tiene dirección (han cerrado sus velas de confirmación).
2. Vigente        se confirmó hace como mucho BIAS_EXEC_MAX_AGE_BARS velas: más tarde, la entrada ya no es la del
                  setup (el precio se ha ido y el riesgo / beneficio cambia).
3. Sesgo          la dirección va a favor del sesgo del día: Bullish solo Long, Bearish solo Short. Con No Bias, solo
                  si BIAS_EXEC_ALLOW_NO_BIAS=true (por defecto no: sin sesgo claro no se opera).
4. Premium / Discount (solo reversiones, BIAS_EXEC_PREMIUM_DISCOUNT): se compra por debajo de la apertura del día
                  (descuento) y se vende por encima (premium). Una reversión Long por encima de la apertura compra caro.

El bot NO envía órdenes: el resultado solo se publica (bias.execution) e informa.
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import Bias, BiasResult
from .rules import fmt_price

DEFAULT_MAX_AGE_BARS = 2
DEFAULT_ALLOW_NO_BIAS = False
DEFAULT_PREMIUM_DISCOUNT = True


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class ExecutionDecision:
    allowed: bool
    reason: str                 # motivo principal: el primer control que falla, o el resumen del GO
    checks: tuple[Check, ...]

    @property
    def verdict(self) -> str:
        return "GO" if self.allowed else "NO GO"


class ExecutionGate:
    def __init__(self, max_age_bars: int = DEFAULT_MAX_AGE_BARS, allow_no_bias: bool = DEFAULT_ALLOW_NO_BIAS,
                 premium_discount: bool = DEFAULT_PREMIUM_DISCOUNT):
        self.max_age_bars = max_age_bars
        self.allow_no_bias = allow_no_bias
        self.premium_discount = premium_discount

    def evaluate(self, setup, bars: int, result: BiasResult | None) -> ExecutionDecision:
        """`setup`: tradingbot.skills.setup.setups.Setup; `bars`: velas cargadas (para saber su antigüedad)."""
        checks: list[Check] = []
        confirmed = setup.direction is not None
        checks.append(Check("Confirmado", confirmed,
                            "velas de confirmación cerradas" if confirmed else "esperando el cierre de confirmación"))
        if confirmed:
            age = bars - 1 - setup.confirm_x
            checks.append(Check("Vigente", age <= self.max_age_bars,
                                "confirmado en la última vela" if age == 0 else
                                f"confirmado hace {age} vela(s) (máximo {self.max_age_bars})"))
            checks.append(self._bias_check(setup.direction, result))
            if self.premium_discount and setup.kind == "reversal":
                checks.append(self._premium_discount(setup, result))
        failed = [c for c in checks if not c.passed]
        if failed:
            return ExecutionDecision(False, f"{failed[0].name}: {failed[0].detail}", tuple(checks))
        return ExecutionDecision(True, "todas las condiciones se cumplen", tuple(checks))

    def _bias_check(self, direction: str, result: BiasResult | None) -> Check:
        if result is None:
            return Check("Sesgo", False, "el sesgo del día aún no está calculado")
        side = direction.capitalize()
        if result.bias is Bias.NO_BIAS:
            if self.allow_no_bias:
                return Check("Sesgo", True, f"{side} con No Bias (permitido por BIAS_EXEC_ALLOW_NO_BIAS)")
            return Check("Sesgo", False, f"{side} sin sesgo del día (No Bias): no se opera")
        wanted = "long" if result.bias is Bias.BULLISH else "short"
        if direction == wanted:
            return Check("Sesgo", True, f"{side} a favor del sesgo {result.bias.value}")
        return Check("Sesgo", False, f"{side} contra el sesgo {result.bias.value}")

    @staticmethod
    def _premium_discount(setup, result: BiasResult | None) -> Check:
        day_open = result.levels.get("Apertura") if result is not None else None
        if day_open is None or setup.entry is None:
            return Check("Premium / Discount", False, "sin apertura del día para comparar")
        entry, ref = fmt_price(setup.entry), fmt_price(day_open)
        if setup.direction == "long":
            ok = setup.entry < day_open
            return Check("Premium / Discount", ok, f"compra a {entry} {'bajo' if ok else 'sobre'} la apertura {ref}"
                         + ("" if ok else " (premium)"))
        ok = setup.entry > day_open
        return Check("Premium / Discount", ok, f"venta a {entry} {'sobre' if ok else 'bajo'} la apertura {ref}"
                     + ("" if ok else " (descuento)"))
