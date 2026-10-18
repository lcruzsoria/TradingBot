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
                   "que Setup abre y cierra, y lo guarda en un diario mensual (data/forwardtest) que no se pierde al reiniciar; "
                   "lo publica para la ventana Forwardtest (acierto, R, drawdown, rachas, libros...). Backtest: carga el "
                   "histórico de los patrones (2018-2026, índices, forex, oro y cripto) y de la estrategia Calendario para la "
                   "ventana Backtest. No opera ni decide nada.")
    subscribes = ("cortex.decision", "setup.executed", "setup.closed", "stats.reset", "stats.reload")
    publishes = ("stats.session", "stats.backtest")
    slot = "aux3"

    def on_start(self) -> None:
        folder = self.settings.get("FORWARD_DIR", "") or None                      # tradingbot.env, bloque STATS
        if folder is None and _is_demo(self.services.source):
            folder = journal.DEFAULT_DIR.parent / "forwardtest-demo"      # datos sintéticos (--demo, capturas): aparte
        self.journal = Journal(folder)
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
        if event.topic == "cortex.decision":
            decision = p["decision"]
            signal = _signal(p)
            if self.stats.decision(decision.allowed, signal):
                self._save(self.journal.signal, signal)
        elif event.topic == "setup.executed":
            if self.stats.executed(p["order"]):
                self._save(self.journal.opened, p["order"])
        elif event.topic == "setup.closed":
            if self.stats.closed(p["order"], p["closed"]):
                self._save(self.journal.closed, p["order"], p["closed"])
        elif event.topic == "stats.reset":            # «Nueva etapa»: el diario se conserva entero
            since = self._save(self.journal.stage)
            self.stats.reset(since)
        elif event.topic == "stats.reload":
            self._load_backtest()
            return
        self._publish_session()

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
            bot = sum((g.row("Ambos", BOT_FILTER) or {}).get("n") or 0 for g in self.backtest.groups)
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
