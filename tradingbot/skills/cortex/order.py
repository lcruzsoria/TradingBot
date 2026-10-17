"""Orden que Cortex le pasa a Setup: todo lo que hace falta para operar, ya decidido."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Order:
    symbol: str              # activo a operar
    timeframe: str           # temporalidad con la que se identificó el patrón
    direction: str           # "long" o "short"
    pattern: str             # patrón de entrada identificado (título)
    pattern_key: str
    tbr_zone: str            # TBR usada: nombre, día y niveles
    tbr_day: date
    tbr_high: float
    tbr_low: float
    tbr_mid: float
    price: float             # precio de referencia del patrón (entrada)
    stop: float | None       # los que defina el patrón (hit.levels["stop"], ["target"])
    target: float | None
    bias: str                # sesgo vigente (Bullish / Bearish / No Bias) y su puntuación
    score: float
    reason: str              # por qué Cortex da GO

    @property
    def label(self) -> str:
        return f"{self.direction.capitalize()} {self.symbol} {self.timeframe} ({self.pattern} en {self.tbr_zone})"


def build_order(payload: dict, decision, bias_result) -> Order:
    """Orden a partir de un `pattern.detected`, la decisión de Cortex y el sesgo vigente."""
    hit, tbr = payload["hit"], payload["tbr"]
    return Order(payload["symbol"], payload["timeframe"], hit.direction, hit.title, hit.key, tbr.zone, tbr.day,
                 tbr.high, tbr.low, tbr.mid, hit.price, hit.levels.get("stop"), hit.levels.get("target"),
                 bias_result.bias.value, float(bias_result.score), decision.reason)
