"""Validación del trade: el patrón de entrada que detecta Pattern debe ir alineado con el sesgo (reglas de Bias).

Bullish solo permite Long y Bearish solo Short. Con No Bias (también cuando el filtro de lateralidad lo deja sin sesgo) no se
opera, salvo que CORTEX_ALLOW_NO_BIAS=true. El bot NO envía órdenes sin que Cortex lo ordene: el resultado informa.
"""

from dataclasses import dataclass

from ..bias.models import Bias

DEFAULT_ALLOW_NO_BIAS = False
DEFAULT_MAX_SPREAD_R = 0.07      # spread máximo, en R (spread / riesgo de la entrada): 0 lo desactiva. Es el p60 del backtest
SPREAD_REASON = "spread alto"    # el motivo de un NO GO por spread empieza así: el gráfico lo marca con una S roja


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str              # motivo del GO / NO GO

    @property
    def verdict(self) -> str:
        return "GO" if self.allowed else "NO GO"

    @property
    def spread_abort(self) -> bool:
        return not self.allowed and self.reason.startswith(SPREAD_REASON)


def check_spread(spread: float | None, entry: float | None, stop: float | None, max_r: float) -> Decision | None:
    """NO GO por spread si cuesta más de `max_r` veces el riesgo de la entrada; None si pasa (o si no se puede saber)."""
    if not max_r or not spread or spread <= 0 or entry is None or stop is None:
        return None
    risk = abs(float(entry) - float(stop))
    if risk <= 0:
        return None
    cost = float(spread) / risk
    if cost <= max_r:
        return None
    return Decision(False, f"{SPREAD_REASON}: {cost:.2f} R del riesgo (spread {spread:.5g}, máximo {max_r:g} R)")


def validate(direction: str, bias_result, allow_no_bias: bool = DEFAULT_ALLOW_NO_BIAS) -> Decision:
    """GO / NO GO para un trade en `direction` ("long" o "short") según el sesgo vigente (un BiasResult o None)."""
    if bias_result is None:
        return Decision(False, "el sesgo del día aún no está calculado")
    side = direction.capitalize()
    bias = bias_result.bias
    if bias is Bias.NO_BIAS:
        if allow_no_bias:
            return Decision(True, f"{side} sin sesgo ({bias_result.summary}); permitido por CORTEX_ALLOW_NO_BIAS")
        why = "mercado lateral" if getattr(bias_result, "lateral", False) else "sin sesgo claro"
        return Decision(False, f"{why}: {bias_result.summary}")
    if (bias is Bias.BULLISH) == (direction == "long"):
        return Decision(True, f"{side} a favor del sesgo {bias.value} (puntuación {bias_result.score:+g})")
    return Decision(False, f"{side} contra el sesgo {bias.value} (puntuación {bias_result.score:+g})")
