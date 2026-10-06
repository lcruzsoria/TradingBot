"""Skill Bias: sesgo (Bullish / Bearish / No Bias) de la sesión del día en curso."""
from __future__ import annotations

from ..core import Event, Skill, register_skill


@register_skill("bias")
class BiasSkill(Skill):
    title = "Bias"
    description = "Evalúa las reglas del sesgo con las últimas velas y decide Bullish, Bearish o No Bias."
    subscribes = ("candles.loaded", "bias.recalc")
    publishes = ("bias.updated",)
    slot = 1

    def on_start(self) -> None:
        self._last: dict | None = None

    def handle(self, event: Event) -> None:
        if event.topic == "candles.loaded":
            self._last = event.payload
        if self._last is None:
            return
        result = self.services.engine.evaluate(self._last["df"])
        self.set_caption(result.bias.value)
        self.publish("bias.updated", {"result": result, "symbol": self._last["symbol"],
                                      "timeframe": self._last["timeframe"]})
