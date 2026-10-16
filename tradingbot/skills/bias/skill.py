"""Skill Bias: sesgo (Bullish / Bearish / No Bias) de la sesión del día en curso y Bias Execution de los setups."""
from __future__ import annotations

from datetime import datetime

from ...clock import NY, server_minus_ny
from ...core import Event, Skill, register_skill
from ...timeframes import minutes
from ..levels.daylevels import DEFAULT_DAY_START, DEFAULT_INDEX_DAY_START, DEFAULT_US_INDICES, is_us_index, parse_time
from .htf import DEFAULT_HOURS as DEFAULT_SWEEP_HOURS, DEFAULT_INDEX_HOURS as DEFAULT_SWEEP_INDEX_HOURS, htf_sweep
from .execution import DEFAULT_ALLOW_NO_BIAS, DEFAULT_PREMIUM_DISCOUNT, ExecutionGate
from .schedule import CHECK_SECONDS, DEFAULT_HOURS, DEFAULT_INDEX_HOURS, next_recalc


@register_skill("bias")
class BiasSkill(Skill):
    title = "Bias"
    description = ("Evalúa las reglas del sesgo (voto x peso) y decide Bullish, Bearish o No Bias. Lo recalcula cada "
                   "3 h en los índices americanos y cada 4 h en el resto, y decide si cada setup detectado se puede "
                   "ejecutar (GO / NO GO) y por qué.")
    subscribes = ("candles.loaded", "bias.recalc", "levels.updated", "setup.updated", "clock.offset")
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
        self._levels: dict | None = None         # último levels.updated (TDO y Midnight para las reglas)
        self._eval_levels: dict = {}             # niveles con los que se calculó el sesgo vigente
        self._offset: int | None = None          # desfase del servidor (clock.offset), para formar las velas H3 / H4
        self._reason = "carga de velas"
        # tradingbot.env, bloque BIAS
        self.index_hours = self.settings.get_float("RECALC_INDEX_HOURS", DEFAULT_INDEX_HOURS)
        self.hours = self.settings.get_float("RECALC_HOURS", DEFAULT_HOURS)
        for key, value in (("RECALC_INDEX_HOURS", self.index_hours), ("RECALC_HOURS", self.hours)):
            if value < 0:
                raise ValueError(f"BIAS_{key}={value:g} debe ser 0 (sin recálculo) o más.")
        self.sweep_index_hours = self.settings.get_int("HTF_SWEEP_INDEX_HOURS", DEFAULT_SWEEP_INDEX_HOURS)
        self.sweep_hours = self.settings.get_int("HTF_SWEEP_HOURS", DEFAULT_SWEEP_HOURS)
        for key, value in (("HTF_SWEEP_INDEX_HOURS", self.sweep_index_hours), ("HTF_SWEEP_HOURS", self.sweep_hours)):
            if value < 1:
                raise ValueError(f"BIAS_{key}={value} debe ser 1 o más.")
        self.gate = ExecutionGate(self.settings.get_bool("EXEC_ALLOW_NO_BIAS", DEFAULT_ALLOW_NO_BIAS),
                                  self.settings.get_bool("EXEC_PREMIUM_DISCOUNT", DEFAULT_PREMIUM_DISCOUNT))

    # -- mensajes -----------------------------------------------------------------------------------
    def handle(self, event: Event) -> None:
        topic, p = event.topic, event.payload
        if topic == "levels.updated":
            self._schedule(p["symbol"], p["timeframe"], p["day_start"], p.get("us_index", False))
            self._levels = p
            if self._last is None or self._day_levels() == self._eval_levels:
                return
            self._reason = "niveles del día (TDO / Midnight)"     # han cambiado: hay que recalcular con ellos
        if topic == "clock.offset":
            if p.get("server_offset") == self._offset:
                return
            self._offset = p.get("server_offset")
            if self._last is None:
                return
            self._reason = "desfase del servidor"                # las velas H3 / H4 dependen de la hora de NY
        elif topic == "setup.updated":
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
        self._eval_levels = self._day_levels()
        self.result = self.services.engine.evaluate(self._last["df"], levels=self._eval_levels, htf=self._htf())
        self.result_symbol = self._last["symbol"]
        self.set_caption(self.result.bias.value)
        self.publish("bias.updated", {"result": self.result, "symbol": self._last["symbol"],
                                      "timeframe": self._last["timeframe"], "reason": self._reason})
        self._reason = "carga de velas"
        self._execution()

    def _htf(self):
        """Barrido de la vela anterior (H3 en índices, H4 en el resto) con las velas del gráfico; None si la regla no está activa."""
        if not any(getattr(r, "key", "") == "htf_sweep" for r in getattr(self.services.engine, "rules", [])):
            return None
        c = self._last
        index = self._plan[4] if self._plan else is_us_index(c["symbol"], DEFAULT_US_INDICES)
        start = self._plan[2] if self._plan else parse_time(DEFAULT_INDEX_DAY_START if index else DEFAULT_DAY_START, "inicio del día")
        ahead, _ = server_minus_ny(self._offset)
        return htf_sweep(c["df"], ahead, start, self.sweep_index_hours if index else self.sweep_hours, minutes(c["timeframe"]))

    def _day_levels(self) -> dict:
        """TDO y Midnight del día en curso, de la skill Levels, si corresponden a las velas con las que se evalúa."""
        p, c = self._levels, self._last
        if p is None or c is None or not p.get("available") or (p["symbol"], p["timeframe"]) != (c["symbol"], c["timeframe"]):
            return {}
        today: dict[str, float] = {}
        tdo = max((ln for ln in p["lines"] if ln.kind == "tdo"), key=lambda ln: ln.x0, default=None)
        if tdo is not None:
            today["tdo"] = tdo.price
            # el Midnight del día en curso: el que empieza después del TDO de hoy (antes de las 00:00 NY aún no existe)
            mid = max((ln for ln in p["lines"] if ln.kind == "midnight" and ln.x0 > tdo.x0), key=lambda ln: ln.x0, default=None)
            if mid is not None:
                today["midnight"] = mid.price
        return today

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
        if p is None or p["last"] is None:
            return
        setup = p["last"]                             # el vivo más reciente, o el último que terminó
        result = self.result if self.result_symbol == p["symbol"] else None
        decision = self.gate.evaluate(setup, result)
        self.publish("bias.execution", {"symbol": p["symbol"], "timeframe": p["timeframe"], "setup": setup,
                                        "decision": decision, "bias": result.bias if result else None})
