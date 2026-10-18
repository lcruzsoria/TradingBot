"""Skill Stats: reúne las estadísticas de la sesión (Cortex y Setup) y los resultados del backtest de los patrones."""
from __future__ import annotations

from ...core import Event, Skill, register_skill
from .backtest import BOT_FILTER, load
from .session import TradeStats


@register_skill("stats")
class StatsSkill(Skill):
    title = "Stats"
    description = ("Las cifras del bot en un solo sitio. Sesión: anota cada GO / NO GO de Cortex y cada operación simulada que "
                   "Setup abre y cierra (acierto, R, drawdown, rachas...), y lo publica para la ventana Estadísticas. "
                   "Backtest: carga el histórico de los patrones (2018-2026, índices, forex, oro y cripto) para la ventana "
                   "Backtest. No opera ni decide nada.")
    subscribes = ("cortex.decision", "setup.executed", "setup.closed", "stats.reset", "stats.reload")
    publishes = ("stats.session", "stats.backtest")
    slot = "aux3"

    def on_start(self) -> None:
        self.stats = TradeStats()
        self.backtest = None
        self._load_backtest()
        self._publish_session()

    def handle(self, event: Event) -> None:
        p = event.payload
        if event.topic == "cortex.decision":
            self.stats.decision(p["decision"].allowed)
        elif event.topic == "setup.executed":
            self.stats.executed(p["order"])
        elif event.topic == "setup.closed":
            self.stats.closed(p["order"], p["closed"])
        elif event.topic == "stats.reset":
            self.stats.reset()
        elif event.topic == "stats.reload":
            self._load_backtest()
            return
        self._publish_session()

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
        self.publish("stats.session", {"stats": s.snapshot()})
        if s.done:
            self.set_caption(f"{len(s.done)} ops · {s.total_r:+.2f} R")
        elif s.open:
            self.set_caption(f"{len(s.open)} abierta(s)")
        elif self.backtest is not None:
            bot = sum((g.row("Ambos", BOT_FILTER) or {}).get("n") or 0 for g in self.backtest.groups)
            self.set_caption(f"backtest: {bot:,} ops".replace(",", "."))
        else:
            self.set_caption("sin backtest")
