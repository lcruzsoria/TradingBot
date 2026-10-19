"""Skill Feed: conecta con MT5 y carga las velas."""
from __future__ import annotations

import time

from ...core import Event, Skill, register_skill

LIVE_CHECK_SECONDS = 30
from ...timeframes import display_label


@register_skill("feed")
class FeedSkill(Skill):
    title = "Feed"
    description = ("Conecta con MT5 y carga todas las velas disponibles del símbolo y timeframe pedidos. "
                   "Cada 30 s mira si el terminal tiene velas nuevas del mercado que se muestra y, si las hay, las recarga "
                   "(así el gráfico, los patrones y Cortex siguen el mercado en directo). También las recarga cuando otra "
                   "skill lo pide (feed.refresh), p. ej. el recálculo del Bias.")
    subscribes = ("feed.load", "feed.refresh")
    publishes = ("feed.connected", "feed.progress", "candles.loaded", "feed.failed")
    slot = 0
    interval = LIVE_CHECK_SECONDS

    def on_start(self) -> None:
        self.connected = False
        self._live: tuple[str, str, int] | None = None   # (mercado, temporalidad, última vela base) de la última carga

    def tick(self) -> None:
        """Velas en directo: si el terminal ya tiene una vela más reciente que la de la última carga, se recarga.

        MT5 entrega primero las velas que tiene guardadas (que pueden ir horas por detrás) y las sincroniza después; sin
        esta comprobación el gráfico se quedaba en esa primera carga hasta el siguiente recálculo del sesgo."""
        last_bar = getattr(self.services.source, "last_bar_ts", None)
        if not self.connected or self._live is None or last_bar is None:
            return
        symbol, tf, seen = self._live
        latest = last_bar(symbol, tf)
        if latest is not None and latest > seen:
            self.handle(Event("feed.refresh", {"symbol": symbol, "timeframe": tf, "reason": "live"}, self.key))

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
                app = self.services.app_cfg["app"]
                wanted = list(dict.fromkeys([*app.get("watchlist", []), symbol]))
                lookup = getattr(source, "equivalents", None)    # nombres que este broker llama de otra forma
                self.publish("feed.connected", {"info": info, "symbols": symbols, "all_symbols": source.all_symbols(),
                                                "equivalents": lookup(wanted) if lookup else {}})
            self.set_caption(f"{symbol} {display_label(tf)}")
            last_report = 0.0

            def progress(count: int) -> None:
                nonlocal last_report
                if time.monotonic() - last_report > 0.1:
                    last_report = time.monotonic()
                    self.publish("feed.progress", {"count": count})

            df = source.load_candles(symbol, tf, progress)
        except Exception as exc:  # noqa: BLE001
            self._live = None                               # no se insiste en directo con un mercado que no carga
            self.set_caption("error")
            self.publish("feed.failed", {"stage": "load" if self.connected else "connect",
                                         "symbol": symbol, "timeframe": tf,
                                         "error": f"{type(exc).__name__}: {exc}"})
            raise
        last_bar = getattr(source, "last_bar_ts", None)
        try:
            base = last_bar(symbol, tf) if last_bar else None
        except Exception:  # noqa: BLE001 - solo sirve para el directo: si falla, se mira en el siguiente tick
            base = None
        self._live = (symbol, tf, base if base is not None else int(df["ts"].iloc[-1])) if len(df) else None
        self.publish("candles.loaded", {"symbol": symbol, "timeframe": tf, "df": df,
                                        "seconds": time.perf_counter() - started,
                                        "refresh": event.topic == "feed.refresh",   # recarga: la vista no se mueve
                                        "reason": event.payload.get("reason")})

    def on_stop(self) -> None:
        try:
            self.services.source.close()
        except Exception:  # noqa: BLE001
            pass
