"""Skill Quotes: cotizaciones de la watchlist y cifras de la cuenta."""
from __future__ import annotations

import time

from ..clock import OffsetDetector
from ..core import Event, Skill, register_skill


@register_skill("quotes")
class QuotesSkill(Skill):
    title = "Quotes"
    description = "Lee cada segundo las cotizaciones de la watchlist y el saldo, equity y P&L de la cuenta."
    subscribes = ("feed.connected", "watchlist.changed")
    publishes = ("quotes.updated",)
    slot = 5
    interval = 1.0

    def on_start(self) -> None:
        self.active = False
        # tradingbot.env: QUOTES_INTERVAL (segundos) y QUOTES_SERVER_UTC_OFFSET (horas; vacío = detectarlo)
        interval = self.settings.get_float("INTERVAL", float(self.params.get("interval", 1.0)))
        if interval <= 0:
            raise ValueError(f"QUOTES_INTERVAL={interval} debe ser mayor que 0.")
        self.interval = interval
        offset_hours = self.settings.get_float("SERVER_UTC_OFFSET")
        self.fixed_offset = None if offset_hours is None else int(round(offset_hours * 3600))
        self.detector = OffsetDetector()
        self.watchlist = [s.strip() for s in self.services.app_cfg["app"].get("watchlist", [])]

    def handle(self, event: Event) -> None:
        if event.topic == "watchlist.changed":
            self.watchlist = [s.strip() for s in event.payload["symbols"]]
        else:
            self.active = True      # la conexión ya está abierta: empezar a leer
        self.tick()

    def tick(self) -> None:
        if not self.active:
            return
        source, watchlist = self.services.source, self.watchlist
        quotes = source.quotes(watchlist) if watchlist else {}
        live = [qt.ts for qt in quotes.values() if qt]
        if live and self.fixed_offset is None:
            self.detector.observe(max(live), time.time())
        offset, origin = ((self.fixed_offset, "configurado") if self.fixed_offset is not None
                          else (self.detector.offset, "detectado" if self.detector.offset is not None else None))
        self.publish("quotes.updated", {"quotes": quotes, "account": source.account(),
                                        "server_offset": offset, "offset_source": origin})
        live = sum(1 for q in quotes.values() if q)
        self.set_caption(f"{live}/{len(watchlist)} símbolos")
