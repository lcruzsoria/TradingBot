"""Skill Levels: niveles del día (TDO, Midnight, PDH / PDL) y separadores de día."""
from __future__ import annotations

import re
from datetime import datetime

from ...clock import NY, server_minus_ny
from ...core import Event, Skill, register_skill
from ...timeframes import display_label, minutes
from .daylevels import (DEFAULT_COLORS, DEFAULT_DAY_START, DEFAULT_DAYS, DEFAULT_INDEX_DAY_START,
                        DEFAULT_MARKET_CLOSE, DEFAULT_MAX_TF_MINUTES, DEFAULT_SMA_PERIOD, DEFAULT_US_INDICES, SMA_STYLES, compute, days, is_us_index,
                        market_close, new_trading_day, parse_time)

COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


@register_skill("levels")
class LevelsSkill(Skill):
    title = "Levels"
    description = ("Calcula los niveles de cada día de trading: TDO (True Day Open), Midnight (00:00 de Nueva York) y "
                   "PDH / PDL (máximo y mínimo del día anterior), y dónde empieza cada día: a las 18:00 de NY en los "
                   "índices americanos y a las 17:00 en el resto.")
    subscribes = ("candles.loaded", "clock.offset", "levels.sma")
    publishes = ("levels.updated", "market.closed", "market.day")
    slot = 3
    interval = 20.0                       # cada cuánto se comprueba si ha cerrado un mercado

    def on_start(self) -> None:
        self.error = "Configuración LEVELS no válida"
        self.offset: int | None = None
        self._last: dict | None = None
        self._checked = datetime.now(NY)      # los cierres anteriores al arranque no se anotan
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
        self.market_close = parse_time(self.settings.get("MARKET_CLOSE", DEFAULT_MARKET_CLOSE), "LEVELS_MARKET_CLOSE")
        self.sma_period = self.settings.get_int("SMA_PERIOD", DEFAULT_SMA_PERIOD)
        if self.sma_period < 1:
            raise ValueError(f"LEVELS_SMA_PERIOD={self.sma_period} debe ser 1 o más.")
        self.sma_style = self.settings.get("SMA_STYLE", SMA_STYLES[0]).strip().lower()
        if self.sma_style not in SMA_STYLES:
            raise ValueError(f"LEVELS_SMA_STYLE={self.sma_style!r}: usa {', '.join(SMA_STYLES)}.")

    def start_for(self, symbol: str) -> int:
        """Minutos (hora de NY) a los que empieza el día de trading de este activo."""
        return self.index_day_start if is_us_index(symbol, self.us_indices) else self.day_start

    def handle(self, event: Event) -> None:
        if self.error:
            raise ValueError(self.error)
        if event.topic == "levels.sma":                      # la media se reconfigura desde su botón
            p = event.payload
            self.sma_period, self.sma_style, self.colors["sma"] = int(p["period"]), p["style"], p["color"].upper()
            if self._last is None:
                return
        elif event.topic == "clock.offset":
            if event.payload.get("server_offset") == self.offset:
                return
            self.offset = event.payload.get("server_offset")
        else:
            self._last = event.payload
        if self._last is not None:
            self.update()

    def tick(self) -> None:
        """Avisa cuando cierra un mercado (market.closed) y cuando empieza el día de trading de los índices o del resto (market.day)."""
        now, prev = datetime.now(NY), self._checked
        self._checked = now
        if self.error:
            return
        closed = market_close(prev, now, self.market_close)
        if closed:
            self.publish("market.closed", {**closed, "index_reopen": self.index_day_start, "reopen": self.day_start})
        for index, start in ((True, self.index_day_start), (False, self.day_start)):     # cada activo cambia de día a su hora
            new_day = new_trading_day(prev, now, start)
            if new_day:
                self.publish("market.day", {**new_day, "index": index, "start": start, "us_indices": self.us_indices})

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
        sma = df["close"].rolling(self.sma_period).mean().to_numpy()
        self.set_caption(f"día {start // 60:02d}:{start % 60:02d}" if available else f"no en {display_label(tf)}")
        self.publish("levels.updated", {"symbol": symbol, "timeframe": tf, "lines": lines, "days": day_list,
                                        "day_start": start, "us_index": is_us_index(symbol, self.us_indices),
                                        "available": available, "estimated": estimated,
                                        "colors": self.colors, "max_tf": self.max_tf, "sma": sma,
                                        "sma_period": self.sma_period, "sma_style": self.sma_style})
