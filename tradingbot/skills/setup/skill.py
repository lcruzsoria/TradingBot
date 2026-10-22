"""Skill Setup: el ejecutor. Solo actúa cuando Cortex le da la orden de operar en la cuenta del broker."""
from __future__ import annotations

import time
from datetime import datetime, timedelta

from ...clock import NY, server_minus_ny
from ...core import Event, Skill, register_skill
from ...timeframes import TIMEFRAMES
from ..levels.daylevels import DEFAULT_US_INDICES
from ..stats.journal import Journal, folder_for
from . import account, store
from .positions import resolve, trackable

DEFAULT_RISK_PCT = 1.0            # SETUP_RISK_PCT: riesgo de cada operación, % del saldo virtual
DEFAULT_BE_TRIGGER_PCT = 1.0      # SETUP_BE_TRIGGER_PCT: ganancia flotante (% del saldo) que pasa el stop a la entrada
CONSOLIDATE_CHECK_SECONDS = 30.0  # cada cuánto se mira si ha terminado una vela de consolidación


@register_skill("setup")
class SetupSkill(Skill):
    title = "Setup"
    description = ("El ejecutor: mete la operación en la cuenta del broker (MT5). Solo recibe órdenes de Cortex, que es "
                   "quien reúne el activo, la temporalidad, el sesgo, la TBR y el patrón válido; Setup no decide nada. "
                   "Por ahora funciona en modo simulación: prepara la orden y la anota, pero no la envía a MT5. Sigue las "
                   "posiciones simuladas (stop, objetivo, stop a breakeven y cierre por tiempo) con las velas que le reenvía "
                   "Cortex, y lleva la cuenta virtual del perfil: el saldo de la cuenta al empezar más lo ganado o perdido en "
                   "cada operación (R x riesgo). Las cerradas del forwardtest pasan a la cuenta al consolidar: al cierre de la "
                   "vela de 3 h (índices) o de 4 h (resto) en la que cerraron. Las abiertas y la cuenta se guardan en "
                   "data/perfiles/<perfil>/: se pueden consultar y siguen ahí al reiniciar el bot.")
    subscribes = ("setup.order", "setup.candles", "feed.connected", "clock.offset")
    publishes = ("setup.executed", "setup.closed", "setup.account", "setup.consolidated")
    slot = "aux1"
    interval = CONSOLIDATE_CHECK_SECONDS

    def on_start(self) -> None:
        self.error = "Configuración SETUP no válida"
        self.send_orders = self.settings.get_bool("SEND_ORDERS", False)      # tradingbot.env, bloque SETUP
        if self.send_orders:
            self.error = ("SETUP_SEND_ORDERS=true: el envío real de órdenes a MT5 aún no está implementado "
                          "(la skill funciona en modo simulación)")
            raise ValueError(self.error)
        self.risk_pct = self.settings.get_float("RISK_PCT", DEFAULT_RISK_PCT)
        be_pct = self.settings.get_float("BE_TRIGGER_PCT", DEFAULT_BE_TRIGGER_PCT)
        if self.risk_pct <= 0 or be_pct < 0:
            self.error = (f"SETUP_RISK_PCT={self.risk_pct:g} debe ser mayor que 0 y SETUP_BE_TRIGGER_PCT={be_pct:g}, "
                          "0 (sin breakeven) o más")
            raise ValueError(self.error)
        self.be_r = be_pct / self.risk_pct if be_pct > 0 else None         # p. ej. 1 % de ganancia con 1 % de riesgo: +1 R
        env = self.services.env
        indices = env.get_list("LEVELS_US_INDICES", list(DEFAULT_US_INDICES)) if env is not None else DEFAULT_US_INDICES
        try:
            self.schedule = account.Schedule(self.settings.get_int("CONSOLIDATE_INDEX_HOURS", account.DEFAULT_INDEX_HOURS),
                                             self.settings.get_int("CONSOLIDATE_HOURS", account.DEFAULT_OTHER_HOURS), indices)
        except ValueError as exc:
            self.error = str(exc)
            raise
        # el diario del forwardtest del perfil (el mismo que escribe Stats): lo que se consolida en la cuenta
        self.journal = Journal(folder_for(self.services.app_cfg, env.get("STATS_FORWARD_DIR") if env is not None else None,
                                          type(self.services.source).__name__ == "DemoSource"))
        self.offset: int | None = None                  # desfase del servidor (clock.offset): para saber su hora
        self.error = ""
        self.executed = 0
        self.file = store.file_for(self.services.app_cfg)
        self.positions: list = [o for o in store.load(self.file) if trackable(o)]   # órdenes simuladas abiertas (en disco)
        self.account = account.VirtualAccount(account.file_for(self.services.app_cfg))
        app = (self.services.app_cfg or {}).get("app", {})
        if app.get("capital"):                          # perfil con capital simulado propio (MT5_<PERFIL>_CAPITAL): no depende del saldo de MT5
            self.account.start(float(app["capital"]), app.get("currency") or "USD")
        self.set_caption(f"{len(self.positions)} posición(es) abierta(s)" if self.positions else "esperando a Cortex")
        self._consolidate()                             # lo que haya terminado mientras el bot estaba parado
        self._publish_account()

    def handle(self, event: Event) -> None:
        if self.error:
            raise ValueError(self.error)
        if event.topic == "feed.connected":
            self._start_account()
            return
        if event.topic == "clock.offset":
            self.offset = event.payload.get("server_offset")
            self._consolidate()
            return
        if event.source != "cortex":                    # solo Cortex puede dar la orden de operar
            self.set_caption("orden rechazada")
            return
        if event.topic == "setup.candles":
            self._follow(event.payload)
            return
        order = event.payload["order"]
        self.executed += 1
        if trackable(order):
            self.positions.append(order)
            store.save(self.positions, self.file)
            self._publish_account()
        self.set_caption(f"simulada: {order.direction.capitalize()} {order.symbol}")
        note = "Modo simulación: la orden está lista pero no se ha enviado a MT5."
        if trackable(order):
            note += (" El resultado se anotará en el Registro y en el Forwardtest cuando la posición cierre (stop, objetivo, "
                     "breakeven o tiempo), y pasará al saldo virtual del perfil al consolidar.")
        self.publish("setup.executed", {"order": order, "sent": False, "note": note,
                                        "risk_amount": self.account.risk_amount(self.risk_pct) if self.account.started else None})

    def _start_account(self) -> None:
        """La primera conexión del perfil fija su capital inicial: el saldo de la cuenta de MT5 en ese momento."""
        if self.account.started:
            return
        try:
            snap = self.services.source.account()
        except Exception:  # noqa: BLE001 - sin datos de la cuenta se prueba en la próxima conexión
            snap = None
        if snap is not None and self.account.start(snap.balance, snap.currency):
            self._consolidate()
            self._publish_account()

    def tick(self) -> None:
        self._consolidate()

    def server_now(self) -> int:
        """Hora del servidor (como si fuera UTC). Hasta que Quotes mida el desfase (con mercados abiertos), la estimada
        de los brokers con cierre en Nueva York: servidor = NY + 7 h, como la del gráfico."""
        if self.offset is not None:
            return int(time.time()) + int(self.offset)
        shift, _ = server_minus_ny(None)
        ny = datetime.now(NY).utcoffset() if NY is not None else timedelta(hours=-5)
        return int(time.time() + ny.total_seconds()) + shift

    def _consolidate(self) -> None:
        """Pasa a la cuenta las cerradas del forwardtest cuya vela de consolidación (3 h índices, 4 h resto) ya terminó."""
        if self.error:
            return
        now = self.server_now()
        before = (len(self.account.trades), list(self.account.pending))
        new = self.account.consolidate(self.journal.closes(), now, self.risk_pct, self.schedule)
        if new:
            self.publish("setup.consolidated", {"trades": new, "balance": self.account.balance,
                                                "currency": self.account.currency})
        if (len(self.account.trades), self.account.pending) != before:
            self._publish_account()

    def _publish_account(self) -> None:
        self.publish("setup.account", self.account.summary(self.risk_pct, self.positions))

    def _follow(self, payload: dict) -> None:
        """Comprueba stop, objetivo, breakeven y cierre por tiempo de las posiciones abiertas del mercado cuyas velas llegan."""
        df = payload["df"]
        ts, high, low, close = (df[k].to_numpy() for k in ("ts", "high", "low", "close"))
        minutes = TIMEFRAMES.get(payload.get("timeframe") or "")
        now = self.server_now()
        still = []
        for order in self.positions:
            closed = (resolve(order, ts, high, low, close, self.be_r, minutes * 60 if minutes else None, now)
                      if order.symbol == payload["symbol"] else None)
            if closed is None:
                still.append(order)
                continue
            self.publish("setup.closed", {"order": order, "closed": closed, "sent": False,
                                          "consolidate_at": self.schedule.due(order.symbol, closed.exit_ts),
                                          "consolidate_hours": self.schedule.hours(order.symbol)})
            self.set_caption(f"cerrada: {closed.result} {closed.r:+.2f} R")
        if len(still) != len(self.positions):
            store.save(still, self.file)
            self.positions = still
            self._publish_account()
        if still:
            self.set_caption(f"{len(still)} posición(es) abierta(s)")
