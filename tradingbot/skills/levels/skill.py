"""Skill Levels: niveles del día (TDO, Midnight, PDH / PDL) y separadores de día."""
from __future__ import annotations

import re

from ...core import Event, Skill, register_skill
from .daylevels import DEFAULT_COLORS, DEFAULT_DAYS, DEFAULT_MAX_TF_MINUTES, compute, separators
from ...clock import server_minus_ny
from ...timeframes import display_label, minutes

COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


@register_skill("levels")
class LevelsSkill(Skill):
    title = "Levels"
    description = ("Calcula los niveles de cada día de trading: TDO (apertura del mercado), Midnight (00:00 de Nueva "
                   "York) y PDH / PDL (máximo y mínimo del día anterior), y dónde empieza cada día.")
    subscribes = ("candles.loaded", "clock.offset")
    publishes = ("levels.updated",)
    slot = 3

    def on_start(self) -> None:
        self.error = "Configuración LEVELS no válida"
        self.offset: int | None = None
        self._last: dict | None = None
        try:
            self._load_settings()
        except ValueError as exc:
            self.error = str(exc)
            raise
        self.error = ""

    def _load_settings(self) -> None:
        # tradingbot.env, bloque LEVELS
        self.days = self.settings.get_int("DAYS", DEFAULT_DAYS)
        if self.days < 1:
            raise ValueError(f"LEVELS_DAYS={self.days} debe ser 1 o más.")
        self.max_tf = self.settings.get_int("MAX_TF_MINUTES", DEFAULT_MAX_TF_MINUTES)
        self.separators = self.settings.get_bool("SEPARATORS", True)
        self.colors = {}
        for key, default in DEFAULT_COLORS.items():
            color = self.settings.get(f"{key}_COLOR", default)
            if not COLOR.match(color):
                raise ValueError(f"LEVELS_{key}_COLOR={color!r}: usa un color #RRGGBB.")
            self.colors[key.lower()] = color.upper()

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
        tf, df = p["timeframe"], p["df"]
        available = minutes(tf) <= self.max_tf
        ahead, estimated = server_minus_ny(self.offset)
        lines, seps = [], []
        if available:
            lines = compute(df["ts"].to_numpy(), df["open"].to_numpy(), df["high"].to_numpy(), df["low"].to_numpy(),
                            ahead, self.days)
            seps = separators(df["ts"].to_numpy()) if self.separators else []
        self.set_caption(f"{len(lines)} niveles" if available else f"no en {display_label(tf)}")
        self.publish("levels.updated", {"symbol": p["symbol"], "timeframe": tf, "lines": lines, "separators": seps,
                                        "available": available, "estimated": estimated, "colors": self.colors,
                                        "max_tf": self.max_tf})
