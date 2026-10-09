"""Skill Bias: sesgo (Bullish / Bearish / No Bias) de la sesión del día en curso y Bias Execution de los setups."""
from __future__ import annotations

from datetime import datetime

from ...clock import NY
from ...core import Event, Skill, register_skill
from ...timeframes import minutes
from ..levels.daylevels import DEFAULT_DAY_START, DEFAULT_INDEX_DAY_START, DEFAULT_US_INDICES, is_us_index, parse_time
from .execution import DEFAULT_ALLOW_NO_BIAS, DEFAULT_MAX_AGE_BARS, DEFAULT_PREMIUM_DISCOUNT, ExecutionGate
from .schedule import CHECK_SECONDS, DEFAULT_HOURS, DEFAULT_INDEX_HOURS, next_recalc


@register_skill("bias")
class BiasSkill(Skill):
    title = "Bias"
    description = ("Evalúa las reglas del sesgo (voto x peso) y decide Bullish, Bearish o No Bias. Lo recalcula cada "
                   "3 h en los índices americanos y cada 4 h en el resto, y decide si cada setup detectado se puede "
                   "ejecutar (GO / NO GO) y por qué.")
    subscribes = ("candles.loaded", "bias.recalc", "levels.updated", "setup.updated")
    publishes = ("bias.updated", "bias.schedule", "bias.execution", "feed.refresh")
    slot = 1
    interval = CHECK_SECONDS

    def on_start(self) -> None:
        self._last: dict | None = None
        self.result = None
        self.result_symbol = ""
        self._setup: dict | None = None
        self._next: datetime | None = None
        self._plan: tuple | None = None          # (símbolo, timeframe, inicio del día, horas, índice USA)
        self._reason = "carga de velas"
        # tradingbot.env, bloque BIAS
        self.index_hours = self.settings.get_float("RECALC_INDEX_HOURS", DEFAULT_INDEX_HOURS)
        self.hours = self.settings.get_float("RECALC_HOURS", DEFAULT_HOURS)
        for key, value in (("RECALC_INDEX_HOURS", self.index_hours), ("RECALC_HOURS", self.hours)):
            if value < 0:
                raise ValueError(f"BIAS_{key}={value:g} debe ser 0 (sin recálculo) o más.")
        max_age = self.settings.get_int("EXEC_MAX_AGE_BARS", DEFAULT_MAX_AGE_BARS)
        if max_age < 0:
            raise ValueError(f"BIAS_EXEC_MAX_AGE_BARS={max_age} debe ser 0 o más.")
        self.gate = ExecutionGate(max_age, self.settings.get_bool("EXEC_ALLOW_NO_BIAS", DEFAULT_ALLOW_NO_BIAS),
                                  self.settings.get_bool("EXEC_PREMIUM_DISCOUNT", DEFAULT_PREMIUM_DISCOUNT))

    # -- mensajes -----------------------------------------------------------------------------------
    def handle(self, event: Event) -> None:
        topic, p = event.topic, event.payload
        if topic == "levels.updated":
            self._schedule(p["symbol"], p["timeframe"], p["day_start"], p.get("us_index", False))
            return
        if topic == "setup.updated":
            self._setup = p
            self._execution()
            return
        if topic == "candles.loaded":
            if minutes(p["timeframe"]) > 1440:
                # Con velas semanales "el día" no existe: se conserva el último sesgo calculado.
                self.set_caption("sin velas semanales")
                return
            self._last = p
            if p.get("reason") == "bias":
                self._reason = "recálculo programado"
            elif p.get("reason"):
                self._reason = str(p["reason"])
            if self._plan is None or self._plan[0] != p["symbol"]:   # sin la skill levels: horario por el símbolo
                index = is_us_index(p["symbol"], DEFAULT_US_INDICES)
                start = parse_time(DEFAULT_INDEX_DAY_START if index else DEFAULT_DAY_START, "inicio del día")
                self._schedule(p["symbol"], p["timeframe"], start, index)
        elif topic == "bias.recalc":
            self._reason = "a petición (botón Recalcular)"
        if self._last is None:
            return
        self.result = self.services.engine.evaluate(self._last["df"])
        self.result_symbol = self._last["symbol"]
        self.set_caption(self.result.bias.value)
        self.publish("bias.updated", {"result": self.result, "symbol": self._last["symbol"],
                                      "timeframe": self._last["timeframe"], "reason": self._reason})
        self._reason = "carga de velas"
        self._execution()

    def tick(self) -> None:
        """Si ha llegado la hora del recálculo, pide velas nuevas al feed (el sesgo se recalcula al llegar)."""
        if self._next is None or self._last is None or datetime.now(NY) < self._next:
            return
        symbol, tf = self._last["symbol"], self._last["timeframe"]
        self.publish("feed.refresh", {"symbol": symbol, "timeframe": tf, "reason": "bias"})
        self._advance()

    # -- recálculo programado -----------------------------------------------------------------------------
    def _schedule(self, symbol: str, tf: str, day_start: int, us_index: bool) -> None:
        hours = self.index_hours if us_index else self.hours
        plan = (symbol, tf, day_start, hours, us_index)
        if plan == self._plan:
            return
        self._plan = plan
        self._advance()

    def _advance(self) -> None:
        symbol, tf, day_start, hours, us_index = self._plan
        self._next = next_recalc(datetime.now(NY), day_start, hours) if hours > 0 else None
        self.publish("bias.schedule", {"symbol": symbol, "next": self._next, "hours": hours, "us_index": us_index,
                                       "day_start": day_start})

    # -- Bias Execution -----------------------------------------------------------------------------------
    def _execution(self) -> None:
        p = self._setup
        if p is None or not p["setups"]:
            return
        setup = p["setups"][-1]                       # el más reciente (también si aún está pendiente)
        result = self.result if self.result_symbol == p["symbol"] else None
        decision = self.gate.evaluate(setup, p["bars"], result)
        self.publish("bias.execution", {"symbol": p["symbol"], "timeframe": p["timeframe"], "setup": setup,
                                        "decision": decision, "bias": result.bias if result else None})
