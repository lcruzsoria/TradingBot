"""Skill Cortex: coordinador. Aplica el filtro de operativa según el Bias del día."""
from __future__ import annotations

from ..bias import Direction, TradeFilter
from ...core import Event, Skill, register_skill


@register_skill("cortex")
class CortexSkill(Skill):
    title = "Cortex"
    description = ("Coordinador del bot. Guarda el Bias vigente y responde a las peticiones de operar: "
                   "con Bullish solo permite Long, con Bearish solo Short y con No Bias ambas.")
    subscribes = ("bias.updated", "candles.loaded", "trade.request")
    publishes = ("trade.verdict",)
    slot = "center"

    def on_start(self) -> None:
        self.filter = TradeFilter()
        self.symbol = ""

    def handle(self, event: Event) -> None:
        if event.topic == "candles.loaded":
            self.symbol = event.payload["symbol"]
            self.set_caption(self.symbol)
        elif event.topic == "bias.updated":
            result = event.payload["result"]
            self.filter.update(result)
            self.set_caption(f"{self.symbol} {result.bias.value}")
        elif event.topic == "trade.request":
            direction = event.payload["direction"]
            if not isinstance(direction, Direction):
                direction = Direction(direction)
            allowed, reason = self.filter.check(direction)
            self.publish("trade.verdict", {"request_id": event.payload.get("request_id"),
                                           "direction": direction, "allowed": allowed, "reason": reason})
