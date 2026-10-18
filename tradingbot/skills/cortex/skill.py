"""Skill Cortex: coordinador. Reúne activo, temporalidad, sesgo, TBR y patrón, decide GO / NO GO y le da la orden a Setup."""
from __future__ import annotations

from ..bias import Direction, TradeFilter
from ...core import Event, Skill, register_skill
from .order import build_calendar_order, build_order
from ..setup.positions import resolve, trackable
from .validation import DEFAULT_ALLOW_NO_BIAS, Decision, validate

MAX_PENDING = 50


@register_skill("cortex")
class CortexSkill(Skill):
    title = "Cortex"
    description = ("Coordinador del bot. Guarda el activo, la temporalidad y el Bias vigente; cuando Pattern identifica un "
                   "patrón de entrada en la TBR activa lo contrasta con el sesgo (a favor: GO; en contra, sin sesgo o "
                   "lateral: NO GO) y, si es GO, le pasa toda la información a Setup, que es quien opera. También "
                   "responde a las peticiones de operar (Bullish solo Long, Bearish solo Short).")
    subscribes = ("bias.updated", "candles.loaded", "trade.request", "pattern.detected", "calendar.signal", "setup.closed")
    publishes = ("trade.verdict", "cortex.decision", "setup.order", "setup.candles")
    slot = "center"

    def on_start(self) -> None:
        self.filter = TradeFilter()
        self.symbol = ""
        self.timeframe = ""
        self._bias: dict | None = None
        self._pending: list[dict] = []                 # patrones que esperan a que llegue el sesgo de su mercado
        self.allow_no_bias = self.settings.get_bool("ALLOW_NO_BIAS", DEFAULT_ALLOW_NO_BIAS)   # tradingbot.env, bloque CORTEX
        self.calendar_use_bias = self.settings.get_bool("CALENDAR_USE_BIAS", False)
        self._open: dict[str, object] = {}              # mercado -> orden abierta: hasta que cierre (stop, objetivo o tiempo) no se da otra
        self._candles: dict[str, object] = {}           # últimas velas de cada mercado, para que Setup resuelva enseguida lo ya ocurrido
        self._used: set = set()                         # sesiones (mercado, TBR, día) que ya dieron un trade: no pueden dar otro
        self.scope = (self.settings.get("POSITION_SCOPE", "global") or "global").lower()   # global: una en toda la cuenta; mercado: una por mercado
        if self.scope not in ("global", "mercado"):
            self.error = f"CORTEX_POSITION_SCOPE={self.scope}: usa global o mercado"
            raise ValueError(self.error)

    def handle(self, event: Event) -> None:
        if event.topic == "candles.loaded":
            self.symbol, self.timeframe = event.payload["symbol"], event.payload["timeframe"]
            if event.payload.get("df") is not None:
                self._candles[self.symbol] = event.payload["df"]
                self.publish("setup.candles", {"symbol": self.symbol, "timeframe": self.timeframe, "df": event.payload["df"]})
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
        elif event.topic == "setup.closed":
            self._open.pop(event.payload["order"].symbol, None)
            self.set_caption(f"{event.payload['order'].symbol}: posición cerrada")
        elif event.topic == "calendar.signal":
            self._calendar(event.payload)
        elif event.topic == "trade.request":
            direction = event.payload["direction"]
            if not isinstance(direction, Direction):
                direction = Direction(direction)
            allowed, reason = self.filter.check(direction)
            self.publish("trade.verdict", {"request_id": event.payload.get("request_id"),
                                           "direction": direction, "allowed": allowed, "reason": reason})

    def _busy(self, symbol: str, entry_ts: int | None = None):
        """La orden abierta que impide abrir otra en `symbol` (en toda la cuenta o solo en ese mercado), o None.

        Una orden que con las velas actuales ya cerró antes de `entry_ts` (la hora de la nueva entrada) no bloquea: así los patrones
        pasados que se anuncian de golpe al arrancar el bot se juzgan en su orden, como habría pasado en directo.
        """
        for order in list(self._open.values()):
            if self.scope == "mercado" and order.symbol != symbol:
                continue
            df = self._candles.get(order.symbol)
            if df is not None and entry_ts:
                closed = resolve(order, df["ts"].to_numpy(), df["high"].to_numpy(), df["low"].to_numpy(), df["close"].to_numpy())
                if closed is not None and entry_ts > closed.exit_ts:
                    continue
            return order
        return None

    def _session_reason(self, p: dict) -> str | None:
        """Motivo de NO GO si la sesión (TBR) del patrón ya dio un trade, o None."""
        tbr = p["tbr"]
        if (p["symbol"], tbr.zone, tbr.day) in self._used:
            return f"la sesión {tbr.zone} del {tbr.day:%d/%m} en {p['symbol']} ya dio un trade: una misma sesión no puede dar dos"
        return None

    def _busy_reason(self, order) -> str:
        return (f"ya hay una posición abierta en {order.symbol} ({order.pattern}): hasta que no cierre (stop, objetivo o tiempo) "
                f"no se abre otra")

    def _send(self, order) -> None:
        """Le pasa la orden a Setup y, si se puede seguir, marca el mercado como ocupado hasta que cierre."""
        if trackable(order):
            self._open[order.symbol] = order
        self.publish("setup.order", {"order": order})
        df = self._candles.get(order.symbol)
        if df is not None:                              # si la operación ya terminó con las velas actuales, el resultado sale al momento
            self.publish("setup.candles", {"symbol": order.symbol, "timeframe": order.timeframe, "df": df})

    def _calendar(self, payload: dict) -> None:
        """Señal de calendario: GO sin consultar el sesgo (el backtest no lo usa), salvo CORTEX_CALENDAR_USE_BIAS=true."""
        direction = payload["direction"]
        result = self.filter.result
        busy = self._busy(payload["symbol"], payload.get("entry_ts"))
        if busy is not None:
            allowed, reason = False, self._busy_reason(busy)
        elif self.calendar_use_bias:
            allowed, reason = self.filter.check(Direction(direction.capitalize()))
        else:
            allowed, reason = True, "estrategia de calendario: no depende del sesgo (CORTEX_CALENDAR_USE_BIAS=false)"
        if allowed:
            self._send(build_calendar_order(payload, result, reason))
        self.set_caption(f"{'GO' if allowed else 'NO GO'} {direction.capitalize()} calendario")

    def _decide(self) -> None:
        """Valida cada patrón pendiente con el sesgo de su mercado; si es GO, le pasa la orden a Setup."""
        bias = self._bias
        if bias is None:
            return
        waiting = []
        for p in sorted(self._pending, key=lambda p: p["hit"].ts or 0):       # en orden de hora: así se decidiría en directo
            if p["symbol"] != bias["symbol"]:
                waiting.append(p)
                continue
            result = bias["result"]
            busy = self._busy(p["symbol"], p["hit"].ts)
            if busy is not None:                         # una sola posición abierta a la vez
                decision = Decision(False, self._busy_reason(busy))
            elif self._session_reason(p):                # y una misma sesión no puede dar dos trades
                decision = Decision(False, self._session_reason(p))
            else:
                decision = validate(p["hit"].direction, result, self.allow_no_bias)
            self.publish("cortex.decision", {"symbol": p["symbol"], "timeframe": p["timeframe"], "tbr": p["tbr"],
                                             "hit": p["hit"], "decision": decision, "bias": result.bias,
                                             "bias_result": result})
            if decision.allowed:
                self._used.add((p["symbol"], p["tbr"].zone, p["tbr"].day))
                self._send(build_order(p, decision, result))
            self.set_caption(f"{decision.verdict} {p['hit'].direction.capitalize()} {p['tbr'].zone}")
        self._pending = waiting
