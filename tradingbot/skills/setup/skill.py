"""Skill Setup: la estrategia de trading sobre las tomas de liquidez de las zonas TBR."""
from __future__ import annotations

from ...core import Event, Skill, register_skill
from .setups import DEFAULT_CONFIRM_BARS, DEFAULT_KINDS, KINDS, detect


@register_skill("setup")
class SetupSkill(Skill):
    title = "Setup"
    description = ("La estrategia de trading: cuando el precio toma la liquidez del High o del Low de una zona TBR, "
                   "decide si es una continuación (cierra más allá del nivel) o una reversión (cierra de vuelta "
                   "dentro). Solo informa: no envía órdenes.")
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
        self.confirm_bars = self.settings.get_int("CONFIRM_BARS", DEFAULT_CONFIRM_BARS)
        if self.confirm_bars < 1:
            raise ValueError(f"SETUP_CONFIRM_BARS={self.confirm_bars} debe ser 1 o más.")
        self.zones = [z.upper() for z in self.settings.get_list("ZONES", [])] or None   # vacío: todas las zonas TBR
        self.kinds = tuple(k.lower() for k in self.settings.get_list("TYPES", list(DEFAULT_KINDS)))
        unknown = [k for k in self.kinds if k not in KINDS]
        if unknown or not self.kinds:
            raise ValueError(f"SETUP_TYPES={', '.join(self.kinds) or 'vacío'}: usa reversal, continuation o ambos.")

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
        if t["available"]:
            setups = detect(t["sessions"], c["df"]["close"].to_numpy(), self.confirm_bars, self.zones, self.kinds)
        confirmed = [s for s in setups if s.direction is not None]
        last = confirmed[-1] if confirmed else None
        if not t["available"]:
            self.set_caption("sin TBR")
        elif last is None:
            self.set_caption("sin setups")
        else:
            self.set_caption(f"{last.kind[:3].title()}. {last.direction.capitalize()} {last.zone}")
        self.publish("setup.updated", {"symbol": c["symbol"], "timeframe": c["timeframe"], "setups": setups,
                                       "last": last, "confirm_bars": self.confirm_bars})
