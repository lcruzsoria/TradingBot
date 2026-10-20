"""Skill Cortex: coordinador. Reúne activo, temporalidad, sesgo, TBR y patrón, decide GO / NO GO y le da la orden a Setup."""
from __future__ import annotations

import time

from ..bias import Direction, TradeFilter
from ...core import Event, Skill, register_skill
from ...envconfig import EnvConfig
from .order import build_calendar_order, build_order
from ..setup import store
from ..setup.positions import resolve, trackable
from ..feed.skill import sweep_settings
from .validation import DEFAULT_ALLOW_NO_BIAS, Decision, validate

MAX_PENDING = 500
ROUND_WAIT_SECONDS = 60          # tras terminar de cargar un barrido, lo que se espera como mucho a Pattern y Bias
ROUND_MAX_SECONDS = 900          # y lo que puede durar como mucho una vuelta entera del barrido


@register_skill("cortex")
class CortexSkill(Skill):
    title = "Cortex"
    description = ("Coordinador del bot. Guarda el activo, la temporalidad y el Bias vigente; cuando Pattern identifica un "
                   "patrón de entrada en la TBR activa lo contrasta con el sesgo (a favor: GO; en contra, sin sesgo o "
                   "lateral: NO GO) y, si es GO, le pasa toda la información a Setup, que es quien opera. También "
                   "responde a las peticiones de operar (Bullish solo Long, Bearish solo Short). Mientras dura una vuelta "
                   "del barrido de la watchlist retiene los patrones y los decide al final, todos los mercados juntos y en "
                   "orden de hora (así se respeta una sola posición en toda la cuenta).")
    subscribes = ("bias.updated", "candles.loaded", "trade.request", "pattern.detected", "calendar.signal", "setup.closed",
                  "feed.sweep", "pattern.swept")
    publishes = ("trade.verdict", "cortex.decision", "setup.order", "setup.candles")
    slot = "center"
    interval = 5.0                   # para no esperar para siempre a una vuelta del barrido que no se completa

    def on_start(self) -> None:
        self.filter = TradeFilter()
        self.symbol = ""
        self.timeframe = ""
        self._bias: dict | None = None                  # último sesgo del gráfico
        self._biases: dict[str, dict] = {}              # mercado -> su último sesgo (gráfico o barrido)
        self._pending: list[dict] = []                 # patrones (y señales de calendario) que esperan a su sesgo o al barrido
        self._round: dict | None = None                 # vuelta del barrido de la watchlist en curso
        env = self.services.env
        app = (self.services.app_cfg or {}).get("app", {})
        every = sweep_settings(env.section("feed") if env is not None else EnvConfig(), app)[0]
        self._sweeping = every > 0 and bool(app.get("watchlist"))     # con barrido, solo se decide al cerrar cada vuelta
        self.allow_no_bias = self.settings.get_bool("ALLOW_NO_BIAS", DEFAULT_ALLOW_NO_BIAS)   # tradingbot.env, bloque CORTEX
        self.calendar_use_bias = self.settings.get_bool("CALENDAR_USE_BIAS", False)
        self._open: dict[str, object] = {}              # mercado -> orden abierta: hasta que cierre (stop, objetivo o tiempo) no se da otra
        self._candles: dict[str, object] = {}           # últimas velas de cada mercado, para que Setup resuelva enseguida lo ya ocurrido
        self._used: set = set()                         # sesiones (mercado, TBR, día) que ya dieron un trade: no pueden dar otro
        self.scope = (self.settings.get("POSITION_SCOPE", "global") or "global").lower()   # global: una en toda la cuenta; mercado: una por mercado
        if self.scope not in ("global", "mercado"):
            self.error = f"CORTEX_POSITION_SCOPE={self.scope}: usa global o mercado"
            raise ValueError(self.error)
        for order in store.load(store.file_for(self.services.app_cfg)):                      # las posiciones que Setup dejó abiertas antes de reiniciar
            if trackable(order):
                self._open[order.symbol] = order
                if order.tbr_zone:
                    self._used.add((order.symbol, order.tbr_zone, order.tbr_day))

    def handle(self, event: Event) -> None:
        p = event.payload
        if event.topic == "candles.loaded":
            symbol, tf = p["symbol"], p["timeframe"]
            if not p.get("background"):
                self.symbol, self.timeframe = symbol, tf
                self.set_caption(self.symbol)
            if p.get("df") is not None:                # también las del barrido: Setup sigue las posiciones de todos los mercados
                self._candles[symbol] = p["df"]
                self.publish("setup.candles", {"symbol": symbol, "timeframe": tf, "df": p["df"]})
        elif event.topic == "bias.updated":
            self._biases[p["symbol"]] = p
            if p.get("background"):
                self._round_seen("biased", p)
            else:
                self._bias = p
                self.filter.update(p["result"])
                self.set_caption(f"{self.symbol} {p['result'].bias.value}")
            self._decide()
        elif event.topic == "pattern.detected":
            self._pending = (self._pending + [p])[-MAX_PENDING:]
            self._decide()
        elif event.topic == "feed.sweep":
            self._sweep(p)
        elif event.topic == "pattern.swept":
            self._round_seen("swept", p)
        elif event.topic == "setup.closed":
            self._open.pop(event.payload["order"].symbol, None)
            self.set_caption(f"{event.payload['order'].symbol}: posición cerrada")
        elif event.topic == "calendar.signal":
            self._pending = (self._pending + [{**p, "calendar": True}])[-MAX_PENDING:]
            self._decide()
        elif event.topic == "trade.request":
            direction = event.payload["direction"]
            if not isinstance(direction, Direction):
                direction = Direction(direction)
            allowed, reason = self.filter.check(direction)
            self.publish("trade.verdict", {"request_id": event.payload.get("request_id"),
                                           "direction": direction, "allowed": allowed, "reason": reason})

    # -- barrido de la watchlist -------------------------------------------------------------------------------
    def _sweep(self, p: dict) -> None:
        """Una vuelta del barrido: desde que empieza hasta que Pattern y Bias han repasado cada mercado cargado, los patrones
        se retienen; al final se deciden todos juntos en orden de hora. Si no, con CORTEX_POSITION_SCOPE=global, un patrón de
        las 10:00 de un mercado que llega antes podría quitarle el sitio a uno de las 09:00 de otro que llega después."""
        if p["stage"] == "start":
            self._round = {"id": p["id"], "loaded": None, "swept": set(), "biased": set(), "since": time.monotonic(),
                           "ended": None}
            self.set_caption(f"barrido de {len(p.get('symbols', []))} mercados")
        elif self._round is not None and self._round["id"] == p["id"]:
            self._round["loaded"] = set(p.get("loaded", []))
            self._round["ended"] = time.monotonic()
            self._check_round()

    def _round_seen(self, kind: str, p: dict) -> None:
        if self._round is not None and self._round["id"] == p.get("sweep"):
            self._round[kind].add(p["symbol"])
            self._check_round()

    def _check_round(self) -> None:
        """Cierra la vuelta en curso si ya está todo (o si se ha esperado bastante) y decide lo retenido."""
        r = self._round
        if r is None:
            return
        now = time.monotonic()
        complete = r["loaded"] is not None and r["loaded"] <= (r["swept"] & r["biased"])
        late = (r["ended"] is not None and now - r["ended"] > ROUND_WAIT_SECONDS) or now - r["since"] > ROUND_MAX_SECONDS
        if complete or late:
            self._round = None
            self._decide(closing=True)

    def tick(self) -> None:
        self._check_round()

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
        filter_ = self.filter
        if payload["symbol"] in self._biases:          # el sesgo de ese mercado, si se conoce; si no, el del gráfico
            filter_ = TradeFilter()
            filter_.update(self._biases[payload["symbol"]]["result"])
        result = filter_.result
        busy = self._busy(payload["symbol"], payload.get("entry_ts"))
        if busy is not None:
            allowed, reason = False, self._busy_reason(busy)
        elif self.calendar_use_bias:
            allowed, reason = filter_.check(Direction(direction.capitalize()))
        else:
            allowed, reason = True, "estrategia de calendario: no depende del sesgo (CORTEX_CALENDAR_USE_BIAS=false)"
        if allowed:
            self._send(build_calendar_order(payload, result, reason))
        self.set_caption(f"{'GO' if allowed else 'NO GO'} {direction.capitalize()} calendario")

    def _decide(self, closing: bool = False) -> None:
        """Valida cada patrón pendiente con el sesgo de su mercado; si es GO, le pasa la orden a Setup.

        Mientras una vuelta del barrido está en curso no se decide nada: al terminar se deciden todos los mercados juntos.
        Con el barrido activo tampoco se decide fuera de una vuelta (p. ej. la señal del gráfico tras refrescarlo): el barrido
        repasa ese mismo mercado, y decidirlo antes que los demás le quitaría la posición a señales anteriores de otros mercados."""
        if self._round is not None or (self._sweeping and not closing):
            return
        waiting = []
        for p in sorted(self._pending, key=_when):                # en orden de hora: así se decidiría en directo
            if p.get("calendar"):
                self._calendar(p)
                continue
            bias = self._biases.get(p["symbol"])
            if bias is None:                                    # aún sin el sesgo de su mercado
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


def _when(p: dict) -> int:
    """Hora (servidor) de un patrón o de una señal de calendario pendiente."""
    if p.get("calendar"):
        return int(p.get("entry_ts") or 0)
    return int(p["hit"].ts or 0)
