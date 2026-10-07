"""Skill Levels: niveles del día (TDO, Midnight, PDH / PDL) y separadores de día."""
from __future__ import annotations

import re

from ...clock import server_minus_ny
from ...core import Event, Skill, register_skill
from ...timeframes import display_label, minutes
from .daylevels import (DEFAULT_COLORS, DEFAULT_DAY_START, DEFAULT_DAYS, DEFAULT_INDEX_DAY_START,
                        DEFAULT_MAX_TF_MINUTES, DEFAULT_US_INDICES, compute, days, is_us_index, parse_time)

COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


@register_skill("levels")
class LevelsSkill(Skill):
    title = "Levels"
    description = ("Calcula los niveles de cada día de trading: TDO (True Day Open), Midnight (00:00 de Nueva York) y "
                   "PDH / PDL (máximo y mínimo del día anterior), y dónde empieza cada día: a las 18:00 de NY en los "
                   "índices americanos y a las 17:00 en el resto.")
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
        self.day_start = parse_time(self.settings.get("DAY_START", DEFAULT_DAY_START), "LEVELS_DAY_START")
        self.index_day_start = parse_time(self.settings.get("INDEX_DAY_START", DEFAULT_INDEX_DAY_START),
                                          "LEVELS_INDEX_DAY_START")
        self.us_indices = self.settings.get_list("US_INDICES", list(DEFAULT_US_INDICES))
        self.colors = {}
        for key, default in DEFAULT_COLORS.items():
            color = self.settings.get(f"{key}_COLOR", default)
            if not COLOR.match(color):
                raise ValueError(f"LEVELS_{key}_COLOR={color!r}: usa un color #RRGGBB.")
            self.colors[key.lower()] = color.upper()

    def start_for(self, symbol: str) -> int:
        """Minutos (hora de NY) a los que empieza el día de trading de este activo."""
        return self.index_day_start if is_us_index(symbol, self.us_indices) else self.day_start

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
        tf, df, symbol = p["timeframe"], p["df"], p["symbol"]
        available = minutes(tf) <= self.max_tf
        ahead, estimated = server_minus_ny(self.offset)
        start = self.start_for(symbol)
        lines, day_list = [], []
        if available:
            ts = df["ts"].to_numpy()
            lines = compute(ts, df["open"].to_numpy(), df["high"].to_numpy(), df["low"].to_numpy(), ahead, start,
                            self.days)
            day_list = days(ts, ahead, start) if self.separators else []
        self.set_caption(f"día {start // 60:02d}:{start % 60:02d}" if available else f"no en {display_label(tf)}")
        self.publish("levels.updated", {"symbol": symbol, "timeframe": tf, "lines": lines, "days": day_list,
                                        "day_start": start, "available": available, "estimated": estimated,
                                        "colors": self.colors, "max_tf": self.max_tf})
