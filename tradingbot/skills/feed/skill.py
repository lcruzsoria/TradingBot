"""Skill Feed: conecta con MT5 y carga las velas."""
from __future__ import annotations

import time

from ...core import Event, Skill, register_skill
from ...timeframes import display_label


@register_skill("feed")
class FeedSkill(Skill):
    title = "Feed"
    description = ("Conecta con MT5 y carga todas las velas disponibles del símbolo y timeframe pedidos. "
                   "También las recarga cuando otra skill lo pide (feed.refresh), p. ej. el recálculo del Bias.")
    subscribes = ("feed.load", "feed.refresh")
    publishes = ("feed.connected", "feed.progress", "candles.loaded", "feed.failed")
    slot = 0

    def on_start(self) -> None:
        self.connected = False

    def handle(self, event: Event) -> None:
        symbol = str(event.payload["symbol"]).strip()
        tf = event.payload["timeframe"]
        source = self.services.source
        started = time.perf_counter()
        try:
            if not self.connected:
                self.set_caption("conectando")
                info = source.connect()
                symbols = source.symbols()
                self.connected = True
                self.publish("feed.connected", {"info": info, "symbols": symbols, "all_symbols": source.all_symbols()})
            self.set_caption(f"{symbol} {display_label(tf)}")
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
                                         "symbol": symbol, "timeframe": tf,
                                         "error": f"{type(exc).__name__}: {exc}"})
            raise
        self.publish("candles.loaded", {"symbol": symbol, "timeframe": tf, "df": df,
                                        "seconds": time.perf_counter() - started,
                                        "refresh": event.topic == "feed.refresh",   # recarga: la vista no se mueve
                                        "reason": event.payload.get("reason")})

    def on_stop(self) -> None:
        try:
            self.services.source.close()
        except Exception:  # noqa: BLE001
            pass
