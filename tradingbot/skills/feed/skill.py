"""Skill Feed: conecta con MT5 y carga las velas (las del gráfico y, en segundo plano, las de toda la watchlist)."""
from __future__ import annotations

import math
import time

from ...core import Event, Skill, register_skill
from ...timeframes import DEFAULT_TIMEFRAME, display_label, minutes, parse_timeframe

LIVE_CHECK_SECONDS = 30
DEFAULT_SWEEP_MINUTES = 5.0             # FEED_SWEEP_MINUTES: cada cuánto se repasan todos los mercados (0 = nunca)
DEFAULT_SWEEP_DAYS = 10                 # FEED_SWEEP_DAYS: días de velas que se cargan de cada mercado en el barrido


def sweep_settings(feed, app: dict) -> tuple[float, str, int]:
    """(minutos entre barridos, timeframe, días de velas) del bloque FEED de tradingbot.env, validados."""
    every = feed.get_float("SWEEP_MINUTES", DEFAULT_SWEEP_MINUTES)
    if every < 0:
        raise ValueError(f"FEED_SWEEP_MINUTES={every:g} debe ser 0 (sin barrido) o más.")
    raw = feed.get("SWEEP_TIMEFRAME", "") or app.get("timeframe") or DEFAULT_TIMEFRAME
    try:
        tf = parse_timeframe(raw)
    except ValueError as exc:
        raise ValueError(f"FEED_SWEEP_TIMEFRAME: {exc}") from None
    days = feed.get_int("SWEEP_DAYS", DEFAULT_SWEEP_DAYS)
    if days < 1:
        raise ValueError(f"FEED_SWEEP_DAYS={days} debe ser 1 o más.")
    return every, tf, days


@register_skill("feed")
class FeedSkill(Skill):
    title = "Feed"
    description = ("Conecta con MT5 y carga todas las velas disponibles del símbolo y timeframe pedidos. "
                   "Cada 30 s mira si el terminal tiene velas nuevas del mercado que se muestra y, si las hay, las recarga "
                   "(así el gráfico, los patrones y Cortex siguen el mercado en directo). También las recarga cuando otra "
                   "skill lo pide (feed.refresh), p. ej. el recálculo del Bias. Además barre en segundo plano todos los "
                   "mercados de la watchlist (FEED_SWEEP_MINUTES), para que Pattern, Cortex y Setup los evalúen aunque no "
                   "estén en pantalla; esas velas no mueven el gráfico.")
    subscribes = ("feed.load", "feed.refresh", "watchlist.changed")
    publishes = ("feed.connected", "feed.progress", "candles.loaded", "feed.failed", "feed.sweep")
    slot = 0
    interval = LIVE_CHECK_SECONDS

    def on_start(self) -> None:
        self.connected = False
        self._live: tuple[str, str, int] | None = None   # (mercado, temporalidad, última vela base) de la última carga
        app = self.services.app_cfg.get("app", {})
        self.watchlist = [s.strip() for s in app.get("watchlist", []) if s.strip()]
        self.sweep_every, self.sweep_tf, self.sweep_days = sweep_settings(self.settings, app)   # tradingbot.env, bloque FEED
        self._sweep_id = 0
        self._next_sweep: float | None = None            # None: el primero se hace en cuanto haya conexión

    def tick(self) -> None:
        """Velas en directo: si el terminal ya tiene una vela más reciente que la de la última carga, se recarga.

        MT5 entrega primero las velas que tiene guardadas (que pueden ir horas por detrás) y las sincroniza después; sin
        esta comprobación el gráfico se quedaba en esa primera carga hasta el siguiente recálculo del sesgo.
        Después, si toca, el barrido de la watchlist."""
        last_bar = getattr(self.services.source, "last_bar_ts", None)
        if self.connected and self._live is not None and last_bar is not None:
            symbol, tf, seen = self._live
            latest = last_bar(symbol, tf)
            if latest is not None and latest > seen:
                self.handle(Event("feed.refresh", {"symbol": symbol, "timeframe": tf, "reason": "live"}, self.key))
        if self._sweep_due():
            self.sweep()

    def handle(self, event: Event) -> None:
        if event.topic == "watchlist.changed":
            self.watchlist = [s.strip() for s in event.payload["symbols"] if s.strip()]
            return
        symbol = str(event.payload["symbol"]).strip()
        tf = event.payload["timeframe"]
        source = self.services.source
        started = time.perf_counter()
        first, round_ = not self.connected, None
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
            if first and self._sweep_due():
                # El primer barrido se anuncia antes que las velas del gráfico: así Cortex retiene también los patrones
                # de este mercado y decide los de todos los mercados juntos, en orden de hora.
                round_ = self._open_round()
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
            if round_ is not None:
                self._run_round(round_)                     # el gráfico ha fallado, pero los demás mercados se siguen
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
        if round_ is not None:
            self._run_round(round_)

    # -- barrido de la watchlist en segundo plano ----------------------------------------------------------------
    def _sweep_due(self) -> bool:
        if not self.connected or self.sweep_every <= 0 or not self.watchlist:
            return False
        return self._next_sweep is None or time.monotonic() >= self._next_sweep

    def sweep(self) -> None:
        """Carga las velas recientes de cada mercado de la watchlist y las publica como `background`: las skills las evalúan
        igual que las del gráfico (Pattern, Cortex, Setup...), pero la ventana no las pinta."""
        self._run_round(self._open_round())

    def _open_round(self) -> dict:
        self._sweep_id += 1
        round_ = {"id": self._sweep_id, "symbols": list(self.watchlist), "timeframe": self.sweep_tf}
        self._next_sweep = time.monotonic() + self.sweep_every * 60       # también si falla: no se insiste sin parar
        self.publish("feed.sweep", {"stage": "start", **round_})
        return round_

    def _run_round(self, round_: dict) -> None:
        source, tf = self.services.source, round_["timeframe"]
        bars = math.ceil(self.sweep_days * 1440 / minutes(tf))
        recent = getattr(source, "load_recent", None)
        started, loaded, failed = time.perf_counter(), [], {}
        caption = self.caption
        for i, symbol in enumerate(round_["symbols"], 1):
            self.set_caption(f"barrido {i}/{len(round_['symbols'])}")
            t0 = time.perf_counter()
            try:
                df = recent(symbol, tf, bars) if recent else source.load_candles(symbol, tf).tail(bars).reset_index(drop=True)
            except Exception as exc:  # noqa: BLE001 - un mercado que no carga no para el barrido
                failed[symbol] = f"{type(exc).__name__}: {exc}"
                continue
            if not len(df):
                failed[symbol] = "sin velas"
                continue
            loaded.append(symbol)
            self.publish("candles.loaded", {"symbol": symbol, "timeframe": tf, "df": df, "seconds": time.perf_counter() - t0,
                                            "refresh": False, "reason": "barrido", "background": True,
                                            "sweep": round_["id"]})
        self.set_caption(caption)
        self.publish("feed.sweep", {"stage": "end", "id": round_["id"], "timeframe": tf, "loaded": loaded,
                                    "failed": failed, "seconds": time.perf_counter() - started})

    def on_stop(self) -> None:
        try:
            self.services.source.close()
        except Exception:  # noqa: BLE001
            pass
