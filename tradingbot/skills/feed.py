"""Skill Feed: conecta con MT5 y carga las velas."""
from __future__ import annotations

import time

from ..core import Event, Skill, register_skill
from ..timeframes import minutes


@register_skill("feed")
class FeedSkill(Skill):
    title = "Feed"
    description = "Conecta con MT5 y carga todas las velas disponibles del símbolo y timeframe pedidos."
    subscribes = ("feed.load",)
    publishes = ("feed.connected", "feed.progress", "candles.loaded", "feed.failed")
    slot = 0

    def on_start(self) -> None:
        self.connected = False

    def handle(self, event: Event) -> None:
        symbol = str(event.payload["symbol"]).upper()
        tf = event.payload["timeframe"]
        source = self.services.source
        started = time.perf_counter()
        try:
            if not self.connected:
                self.set_caption("conectando")
                info = source.connect()
                symbols = source.symbols()
                self.connected = True
                self.publish("feed.connected", {"info": info, "symbols": symbols})
            self.set_caption(f"{symbol} M{minutes(tf)}")
            last_report = 0.0

            def progress(count: int) -> None:
                nonlocal last_report
                if time.monotonic() - last_report > 0.1:
                    last_report = time.monotonic()
                    self.publish("feed.progress", {"count": count})

            df = source.load_candles(symbol, tf, progress)
        except Exception as exc:  # noqa: BLE001
            self.set_caption("error")
            self.publish("feed.failed", {"stage": "load" if self.connected else "connect",
                                         "error": f"{type(exc).__name__}: {exc}"})
            raise
        self.publish("candles.loaded", {"symbol": symbol, "timeframe": tf, "df": df,
                                        "seconds": time.perf_counter() - started})

    def on_stop(self) -> None:
        try:
            self.services.source.close()
        except Exception:  # noqa: BLE001
            pass
