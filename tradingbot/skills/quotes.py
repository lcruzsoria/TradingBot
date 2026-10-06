"""Skill Quotes: cotizaciones de la watchlist y cifras de la cuenta."""
from __future__ import annotations

from ..core import Event, Skill, register_skill


@register_skill("quotes")
class QuotesSkill(Skill):
    title = "Quotes"
    description = "Lee cada segundo las cotizaciones de la watchlist y el saldo, equity y P&L de la cuenta."
    subscribes = ("feed.connected",)
    publishes = ("quotes.updated",)
    slot = 5
    interval = 1.0

    def on_start(self) -> None:
        self.active = False
        self.watchlist = [s.upper() for s in self.services.app_cfg["app"].get("watchlist", [])]

    def handle(self, event: Event) -> None:
        self.active = True          # la conexión ya está abierta: empezar a leer
        self.tick()

    def tick(self) -> None:
        if not self.active:
            return
        source = self.services.source
        quotes = source.quotes(self.watchlist) if self.watchlist else {}
        self.publish("quotes.updated", {"quotes": quotes, "account": source.account()})
        live = sum(1 for q in quotes.values() if q)
        self.set_caption(f"{live}/{len(self.watchlist)} símbolos")
