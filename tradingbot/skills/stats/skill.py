"""Skill Stats: el forwardtest (lo que hace el bot desde que opera, guardado por meses) y los resultados del backtest."""
from __future__ import annotations

from ...core import Event, Skill, register_skill
from .backtest import BOT_FILTER, load
from . import journal
from .journal import Journal
from .session import Signal, TradeStats


@register_skill("stats")
class StatsSkill(Skill):
    title = "Stats"
    description = ("Las cifras del bot en un solo sitio. Forwardtest: anota cada GO / NO GO de Cortex y cada operación simulada "
                   "que Setup abre y cierra en directo (no los patrones pasados que se repiten al arrancar), y lo guarda en un diario mensual por perfil (data/perfiles/<perfil>/forwardtest) que no se pierde al reiniciar; "
                   "lo publica para la ventana Forwardtest (acierto, R, drawdown, rachas, libros...). Backtest: carga el "
                   "histórico de los patrones (2018-2026, índices, forex, oro y cripto) y de la estrategia Calendario para la "
                   "ventana Backtest. No opera ni decide nada.")
    subscribes = ("candles.loaded", "cortex.decision", "setup.executed", "setup.closed", "stats.reset", "stats.reload")
    publishes = ("stats.session", "stats.backtest")
    slot = "aux3"

    def on_start(self) -> None:
        # STATS_FORWARD_DIR o el diario del perfil (cada cuenta el suyo); datos sintéticos sin perfil: aparte
        self.journal = Journal(journal.folder_for(self.services.app_cfg, self.settings.get("FORWARD_DIR", "") or None,
                                                  _is_demo(self.services.source)))
        self._start: dict[str, int] = {}               # mercado -> última vela de su primera carga (el arranque, en hora del servidor)
        try:
            self.stats = self.journal.load_recent()
        except OSError as exc:
            self.stats = TradeStats()
            self.publish("skill.error", {"key": self.key, "error": f"no se pudo leer el diario del forwardtest: {exc}"})
        self.backtest = None
        self._load_backtest()
        self._publish_session()

    def handle(self, event: Event) -> None:
        p = event.payload
        if event.topic == "candles.loaded":
            df = p.get("df")
            if df is not None and len(df):
                self._start.setdefault(p["symbol"].lower(), int(df["ts"].iloc[-1]))
            return
        if event.topic == "cortex.decision":
            decision = p["decision"]
            signal = _signal(p)
            if self.live(signal.symbol, signal.ts) and self.stats.decision(decision.allowed, signal):
                self._save(self.journal.signal, signal)
        elif event.topic == "setup.executed":
            order = p["order"]
            if self.stats.find(order) is None and not self.live(order.symbol, order.entry_ts):
                return
            if self.stats.executed(order):
                self._save(self.journal.opened, order)
        elif event.topic == "setup.closed":
            if self.stats.find(p["order"]) is None and not self.live(p["order"].symbol, p["order"].entry_ts):
                return
            if self.stats.closed(p["order"], p["closed"]):
                self._save(self.journal.closed, p["order"], p["closed"])
        elif event.topic == "stats.reset":            # «Nueva etapa»: el diario se conserva entero
            since = self._save(self.journal.stage)
            self.stats.reset(since)
        elif event.topic == "stats.reload":
            self._load_backtest()
            return
        self._publish_session()

    def live(self, symbol: str, ts: int | None) -> bool:
        """Si la vela del patrón es del arranque en adelante. Al arrancar, Pattern y Cortex repasan los patrones recientes
        del histórico: eso es backtest, no forwardtest, y no se anota (las operaciones que ya estaban en el diario sí
        reciben su cierre). Sin velas de ese mercado aún, o sin hora, no se puede saber y se anota."""
        start = self._start.get((symbol or "").lower())
        return start is None or ts is None or int(ts) >= start

    def _save(self, write, *args):
        try:
            return write(*args)
        except OSError as exc:
            self.set_caption("diario sin guardar")
            self.publish("skill.error", {"key": self.key, "error": f"no se pudo guardar el diario del forwardtest: {exc}"})
            return None

    def _load_backtest(self) -> None:
        """Lee el resumen del backtest (STATS_BACKTEST_FILE o el de la skill) y lo publica, o publica el error."""
        try:
            self.backtest = load(self.settings.get("BACKTEST_FILE", "") or None)       # tradingbot.env, bloque STATS
        except (OSError, ValueError) as exc:
            self.backtest = None
            self.publish("stats.backtest", {"backtest": None, "error": str(exc)})
            return
        self.publish("stats.backtest", {"backtest": self.backtest, "error": ""})

    def _publish_session(self) -> None:
        s = self.stats
        self.publish("stats.session", {"stats": s.snapshot(), "folder": str(self.journal.folder)})
        if s.done:
            self.set_caption(f"{len(s.done)} ops · {s.total_r:+.2f} R")
        elif s.open:
            self.set_caption(f"{len(s.open)} abierta(s)")
        elif self.backtest is not None:
            bot = sum(int(g.filter_mask("Ambos", BOT_FILTER).sum()) for g in self.backtest.groups if not g.is_calendar)
            self.set_caption(f"backtest: {bot:,} ops".replace(",", "."))
        else:
            self.set_caption("sin backtest")


def _is_demo(source) -> bool:
    return type(source).__name__ == "DemoSource"


def _signal(p: dict) -> Signal:
    """La señal de un `cortex.decision` (los tests pueden mandar solo la decisión)."""
    hit, tbr = p.get("hit"), p.get("tbr")
    zone = getattr(getattr(tbr, "zone", None), "name", "") or ""
    day = getattr(tbr, "day", None)
    return Signal(p["decision"].allowed, p.get("symbol", ""), p.get("timeframe", ""), getattr(hit, "title", ""),
                  getattr(hit, "direction", ""), getattr(p["decision"], "reason", ""), getattr(hit, "ts", None) or None,
                  f"{zone} {day:%d/%m}" if zone and day else zone)
