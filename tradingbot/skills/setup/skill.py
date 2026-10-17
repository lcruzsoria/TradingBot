"""Skill Setup: valida el trade. Cuando Pattern detecta un patrón de entrada, lo contrasta con el sesgo (GO / NO GO)."""
from __future__ import annotations

from ...core import Event, Skill, register_skill
from .validation import DEFAULT_ALLOW_NO_BIAS, validate

MAX_PENDING = 50


@register_skill("setup")
class SetupSkill(Skill):
    title = "Setup"
    description = ("Valida el trade. Cuando Pattern identifica el patrón de entrada en la TBR activa, comprueba que va "
                   "alineado con las reglas del Bias: a favor del sesgo es GO; en contra, sin sesgo o con el mercado lateral, "
                   "NO GO. Solo informa: no envía órdenes.")
    subscribes = ("pattern.detected", "bias.updated")
    publishes = ("setup.decision",)
    slot = 4

    def on_start(self) -> None:
        self._bias: dict | None = None
        self._pending: list[dict] = []                 # patrones que esperan a que llegue el sesgo
        self.allow_no_bias = self.settings.get_bool("ALLOW_NO_BIAS", DEFAULT_ALLOW_NO_BIAS)   # tradingbot.env, bloque SETUP
        self.set_caption("esperando patrón")

    def handle(self, event: Event) -> None:
        if event.topic == "pattern.detected":
            self._pending = (self._pending + [event.payload])[-MAX_PENDING:]
        else:
            self._bias = event.payload
        self._decide()

    def _decide(self) -> None:
        """Valida los patrones pendientes con el sesgo del mismo mercado (el último que llegó)."""
        bias = self._bias
        if bias is None:
            return
        waiting = []
        for p in self._pending:
            if p["symbol"] != bias["symbol"]:
                waiting.append(p)
                continue
            hit, result = p["hit"], bias["result"]
            decision = validate(hit.direction, result, self.allow_no_bias)
            side = hit.direction.capitalize()
            self.set_caption(f"{decision.verdict} {side} {p['tbr'].zone}")
            self.publish("setup.decision", {"symbol": p["symbol"], "timeframe": p["timeframe"], "tbr": p["tbr"], "hit": hit,
                                            "decision": decision, "bias": result.bias if result else None,
                                            "bias_result": result})
        self._pending = waiting
