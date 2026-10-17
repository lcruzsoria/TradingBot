"""Skill Cortex: coordinador. Reúne activo, temporalidad, sesgo, TBR y patrón, decide GO / NO GO y le da la orden a Setup."""
from __future__ import annotations

from ..bias import Direction, TradeFilter
from ...core import Event, Skill, register_skill
from .order import build_calendar_order, build_order
from .validation import DEFAULT_ALLOW_NO_BIAS, validate

MAX_PENDING = 50


@register_skill("cortex")
class CortexSkill(Skill):
    title = "Cortex"
    description = ("Coordinador del bot. Guarda el activo, la temporalidad y el Bias vigente; cuando Pattern identifica un "
                   "patrón de entrada en la TBR activa lo contrasta con el sesgo (a favor: GO; en contra, sin sesgo o "
                   "lateral: NO GO) y, si es GO, le pasa toda la información a Setup, que es quien opera. También "
                   "responde a las peticiones de operar (Bullish solo Long, Bearish solo Short).")
    subscribes = ("bias.updated", "candles.loaded", "trade.request", "pattern.detected", "calendar.signal")
    publishes = ("trade.verdict", "cortex.decision", "setup.order")
    slot = "center"

    def on_start(self) -> None:
        self.filter = TradeFilter()
        self.symbol = ""
        self.timeframe = ""
        self._bias: dict | None = None
        self._pending: list[dict] = []                 # patrones que esperan a que llegue el sesgo de su mercado
        self.allow_no_bias = self.settings.get_bool("ALLOW_NO_BIAS", DEFAULT_ALLOW_NO_BIAS)   # tradingbot.env, bloque CORTEX
        self.calendar_use_bias = self.settings.get_bool("CALENDAR_USE_BIAS", False)

    def handle(self, event: Event) -> None:
        if event.topic == "candles.loaded":
            self.symbol, self.timeframe = event.payload["symbol"], event.payload["timeframe"]
            self.set_caption(self.symbol)
        elif event.topic == "bias.updated":
            self._bias = event.payload
            result = event.payload["result"]
            self.filter.update(result)
            self.set_caption(f"{self.symbol} {result.bias.value}")
            self._decide()
        elif event.topic == "pattern.detected":
            self._pending = (self._pending + [event.payload])[-MAX_PENDING:]
            self._decide()
        elif event.topic == "calendar.signal":
            self._calendar(event.payload)
        elif event.topic == "trade.request":
            direction = event.payload["direction"]
            if not isinstance(direction, Direction):
                direction = Direction(direction)
            allowed, reason = self.filter.check(direction)
            self.publish("trade.verdict", {"request_id": event.payload.get("request_id"),
                                           "direction": direction, "allowed": allowed, "reason": reason})

    def _calendar(self, payload: dict) -> None:
        """Señal de calendario: GO sin consultar el sesgo (el backtest no lo usa), salvo CORTEX_CALENDAR_USE_BIAS=true."""
        direction = payload["direction"]
        result = self.filter.result
        if self.calendar_use_bias:
            allowed, reason = self.filter.check(Direction(direction.capitalize()))
        else:
            allowed, reason = True, "estrategia de calendario: no depende del sesgo (CORTEX_CALENDAR_USE_BIAS=false)"
        if allowed:
            self.publish("setup.order", {"order": build_calendar_order(payload, result, reason)})
        self.set_caption(f"{'GO' if allowed else 'NO GO'} {direction.capitalize()} calendario")

    def _decide(self) -> None:
        """Valida cada patrón pendiente con el sesgo de su mercado; si es GO, le pasa la orden a Setup."""
        bias = self._bias
        if bias is None:
            return
        waiting = []
        for p in self._pending:
            if p["symbol"] != bias["symbol"]:
                waiting.append(p)
                continue
            result = bias["result"]
            decision = validate(p["hit"].direction, result, self.allow_no_bias)
            self.publish("cortex.decision", {"symbol": p["symbol"], "timeframe": p["timeframe"], "tbr": p["tbr"],
                                             "hit": p["hit"], "decision": decision, "bias": result.bias,
                                             "bias_result": result})
            if decision.allowed:
                self.publish("setup.order", {"order": build_order(p, decision, result)})
            self.set_caption(f"{decision.verdict} {p['hit'].direction.capitalize()} {p['tbr'].zone}")
        self._pending = waiting
