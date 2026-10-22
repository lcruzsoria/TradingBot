"""Validación del trade: el patrón de entrada que detecta Pattern debe ir alineado con el sesgo (reglas de Bias).

Bullish solo permite Long y Bearish solo Short. Con No Bias (también cuando el filtro de lateralidad lo deja sin sesgo) no se
opera, salvo que CORTEX_ALLOW_NO_BIAS=true. El bot NO envía órdenes sin que Cortex lo ordene: el resultado informa.

Regla de spread: un patrón que sería GO se aborta (NO GO) si el spread de la vela de entrada, frente al riesgo de la operación
(entrada - stop), supera CORTEX_MAX_SPREAD_R. Con un stop corto el spread se come una parte grande de 1R: en el backtest de 9 años
(14.919 operaciones de patrón en 4 índices) las de coste > 0,14 R perdían -0,56 R de media, y quedarse con las de coste <= 0,07 R
llevaba el R neto de -0,09 a ~+0,03 (validado con el 40 % final, umbral fijado en el 60 % antiguo). Ver scripts/analiza_filtros.py.
"""

from dataclasses import dataclass

from ..bias.models import Bias

DEFAULT_ALLOW_NO_BIAS = False
DEFAULT_MAX_SPREAD_R = 0.07      # spread / riesgo máximo; 0 = sin regla de spread


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str              # motivo del GO / NO GO
    code: str = ""           # tipo del NO GO cuando tiene un símbolo propio en el gráfico: "spread"
    short: str = ""          # motivo corto para la etiqueta del gráfico (si no, se saca del motivo)

    @property
    def verdict(self) -> str:
        return "GO" if self.allowed else "NO GO"


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


def check_spread(spread: float | None, entry: float, stop: float | None, max_r: float) -> Decision | None:
    """NO GO si el spread de la vela de entrada supera `max_r` veces el riesgo (entrada - stop); None si pasa, si la regla está
    desactivada (`max_r` <= 0) o si falta algún dato (sin spread de MT5 o sin stop no se puede juzgar)."""
    if max_r <= 0 or spread is None or stop is None or not spread == spread:
        return None
    risk = abs(entry - stop)
    if risk <= 0:
        return None
    cost = spread / risk
    if cost <= max_r:
        return None
    return Decision(False, f"spread alto en la vela de entrada: {spread:.5g} = {cost:.3f} R del riesgo ({risk:.5g}), por encima del "
                           f"umbral de {max_r:g} R (CORTEX_MAX_SPREAD_R)", "spread", f"spread {cost:.2f} R > {max_r:g} R")
