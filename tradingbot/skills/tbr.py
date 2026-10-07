"""Skill TBR: zonas horarias (Time-Based Ranges) en hora de Nueva York y sus niveles High, Low y 50 %."""
from __future__ import annotations

from ..core import Event, Skill, register_skill
from ..tbr import (DEFAULT_DAYS, DEFAULT_MAX_TF_MINUTES, DEFAULT_OPACITY, compute, server_minus_ny,
                   zones_from_settings)
from ..timeframes import display_label, minutes


@register_skill("tbr")
class TbrSkill(Skill):
    title = "TBR"
    description = ("Marca las zonas horarias del día en hora de Nueva York (Asia, London, Pre-NY, NY-AM, NY-PM) y sus "
                   "niveles High, Low y 50 %, que se prolongan hasta que una vela los toma.")
    subscribes = ("candles.loaded", "clock.offset")
    publishes = ("tbr.updated",)
    slot = 2

    def on_start(self) -> None:
        self.error = "Configuración TBR no válida"   # con la configuración mal, el hexágono queda en rojo con el motivo
        self.offset: int | None = None
        self._last: dict | None = None
        try:
            self._load_settings()
        except ValueError as exc:
            self.error = str(exc)
            raise
        self.error = ""
        self.set_caption(f"{len(self.zones)} zonas")

    def _load_settings(self) -> None:
        # tradingbot.env, bloque TBR
        self.zones = zones_from_settings(self.settings)
        self.days = self.settings.get_int("DAYS", DEFAULT_DAYS)
        self.max_tf = self.settings.get_int("MAX_TF_MINUTES", DEFAULT_MAX_TF_MINUTES)
        opacity = self.settings.get_float("OPACITY", DEFAULT_OPACITY)
        if not 0 <= opacity <= 100:
            raise ValueError(f"TBR_OPACITY={opacity:g} debe estar entre 0 y 100 (%).")
        if self.days < 1:
            raise ValueError(f"TBR_DAYS={self.days} debe ser 1 o más.")
        self.opacity = opacity / 100

    def handle(self, event: Event) -> None:
        if self.error:
            raise ValueError(self.error)
        if event.topic == "clock.offset":
            if event.payload.get("server_offset") == self.offset:
                return
            self.offset = event.payload.get("server_offset")
        else:
            self._last = event.payload
        if self._last is not None:
            self.update()

    def update(self) -> None:
        p = self._last
        tf = p["timeframe"]
        available = minutes(tf) <= self.max_tf
        ahead, estimated = server_minus_ny(self.offset)
        sessions = []
        if available:
            df = p["df"]
            sessions = compute(df["ts"].to_numpy(), df["high"].to_numpy(), df["low"].to_numpy(), self.zones, ahead,
                               minutes(tf), self.days)
        self.set_caption(f"{len(sessions)} zonas" if available else f"no en {display_label(tf)}")
        self.publish("tbr.updated", {"symbol": p["symbol"], "timeframe": tf, "sessions": sessions,
                                     "available": available, "estimated": estimated, "opacity": self.opacity,
                                     "zones": self.zones, "max_tf": self.max_tf})
