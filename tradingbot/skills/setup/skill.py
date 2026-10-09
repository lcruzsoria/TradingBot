"""Skill Setup: la estrategia de trading, continuación sobre las TBR (toma de liquidez, retest del 50 %, 2ª ruptura)."""
from __future__ import annotations

from ...core import Event, Skill, register_skill
from ...timeframes import minutes
from .setups import (DEFAULT_KINDS, DEFAULT_TP_RANGES, DEFAULT_WINDOW_HOURS, KINDS, LIVE, STATUS_NAMES, detect)


@register_skill("setup")
class SetupSkill(Skill):
    title = "Setup"
    description = ("La estrategia de trading. En cada TBR: el precio toma la liquidez de un lado, vuelve a tocar el "
                   "50 % y rompe otra vez por el mismo lado; entrada con orden límite en el nivel roto, stop bajo "
                   "el mínimo del retest y objetivo en el nivel -1. Solo informa: no envía órdenes.")
    subscribes = ("candles.loaded", "tbr.updated")
    publishes = ("setup.updated",)
    slot = 4

    def on_start(self) -> None:
        self.error = "Configuración SETUP no válida"   # con la configuración mal, el hexágono queda en rojo con el motivo
        self._candles: dict | None = None
        self._tbr: dict | None = None
        try:
            self._load_settings()
        except ValueError as exc:
            self.error = str(exc)
            raise
        self.error = ""
        self.set_caption("esperando TBR")

    def _load_settings(self) -> None:
        # tradingbot.env, bloque SETUP
        self.window_hours = self.settings.get_float("WINDOW_HOURS", DEFAULT_WINDOW_HOURS)
        if self.window_hours <= 0:
            raise ValueError(f"SETUP_WINDOW_HOURS={self.window_hours:g} debe ser mayor que 0.")
        self.tp_ranges = self.settings.get_float("TP_RANGES", DEFAULT_TP_RANGES)
        if self.tp_ranges <= 0:
            raise ValueError(f"SETUP_TP_RANGES={self.tp_ranges:g} debe ser mayor que 0.")
        self.zones = [z.upper() for z in self.settings.get_list("ZONES", [])] or None   # vacío: todas las TBR
        self.kinds = tuple(k.lower() for k in self.settings.get_list("TYPES", list(DEFAULT_KINDS)))
        unknown = [k for k in self.kinds if k not in KINDS]
        if unknown or not self.kinds:
            raise ValueError(f"SETUP_TYPES={', '.join(self.kinds) or 'vacío'}: de momento solo existe continuation.")

    def handle(self, event: Event) -> None:
        if self.error:
            raise ValueError(self.error)
        if event.topic == "candles.loaded":
            self._candles = event.payload
        else:
            self._tbr = event.payload
        c, t = self._candles, self._tbr
        if c is None or t is None or (c["symbol"], c["timeframe"]) != (t["symbol"], t["timeframe"]):
            return                                      # aún no han llegado las zonas de estas velas
        self.update()

    def update(self) -> None:
        c, t = self._candles, self._tbr
        setups = []
        window = max(1, int(self.window_hours * 60 / minutes(c["timeframe"])))
        if t["available"]:
            df = c["df"]
            setups = detect(t["sessions"], df["high"].to_numpy(), df["low"].to_numpy(), window, self.zones,
                            self.tp_ranges, self.kinds)
        live = [s for s in setups if s.status in LIVE]
        # el más relevante: el vivo más reciente; si no hay, el último que terminó
        last = (live or setups or [None])[-1]
        if not t["available"]:
            self.set_caption("sin TBR")
        elif last is None:
            self.set_caption("sin setups")
        else:
            self.set_caption(f"{last.direction.capitalize()} {last.zone}: {STATUS_NAMES[last.status].split(',')[0]}")
        self.publish("setup.updated", {"symbol": c["symbol"], "timeframe": c["timeframe"], "setups": setups,
                                       "last": last, "window_bars": window, "bars": len(c["df"])})
