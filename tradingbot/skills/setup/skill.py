"""Skill Setup: el ejecutor. Solo actúa cuando Cortex le da la orden de operar en la cuenta del broker."""
from __future__ import annotations

from ...core import Event, Skill, register_skill
from ...timeframes import TIMEFRAMES
from . import account, store
from .positions import resolve, trackable

DEFAULT_RISK_PCT = 1.0            # SETUP_RISK_PCT: riesgo de cada operación, % del saldo virtual
DEFAULT_BE_TRIGGER_PCT = 1.0      # SETUP_BE_TRIGGER_PCT: ganancia flotante (% del saldo) que pasa el stop a la entrada


@register_skill("setup")
class SetupSkill(Skill):
    title = "Setup"
    description = ("El ejecutor: mete la operación en la cuenta del broker (MT5). Solo recibe órdenes de Cortex, que es "
                   "quien reúne el activo, la temporalidad, el sesgo, la TBR y el patrón válido; Setup no decide nada. "
                   "Por ahora funciona en modo simulación: prepara la orden y la anota, pero no la envía a MT5. Sigue las "
                   "posiciones simuladas (stop, objetivo, stop a breakeven y cierre por tiempo) con las velas que le reenvía "
                   "Cortex, y lleva la cuenta virtual del perfil: el saldo de la cuenta al empezar más lo ganado o perdido en "
                   "cada operación (R x riesgo). Las abiertas y la cuenta se guardan en data/perfiles/<perfil>/: se pueden "
                   "consultar y siguen ahí al reiniciar el bot.")
    subscribes = ("setup.order", "setup.candles", "feed.connected")
    publishes = ("setup.executed", "setup.closed", "setup.account")
    slot = "aux1"

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
        self.error = ""
        self.executed = 0
        self.file = store.file_for(self.services.app_cfg)
        self.positions: list = [o for o in store.load(self.file) if trackable(o)]   # órdenes simuladas abiertas (en disco)
        self.account = account.VirtualAccount(account.file_for(self.services.app_cfg))
        self.set_caption(f"{len(self.positions)} posición(es) abierta(s)" if self.positions else "esperando a Cortex")
        self._publish_account()

    def handle(self, event: Event) -> None:
        if self.error:
            raise ValueError(self.error)
        if event.topic == "feed.connected":
            self._start_account()
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
            note += (" El resultado se anotará en el Registro y en el saldo virtual del perfil cuando la posición cierre "
                     "(stop, objetivo, breakeven o tiempo).")
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
            self._publish_account()

    def _publish_account(self) -> None:
        self.publish("setup.account", self.account.summary(self.risk_pct, self.positions))

    def _follow(self, payload: dict) -> None:
        """Comprueba stop, objetivo, breakeven y cierre por tiempo de las posiciones abiertas del mercado cuyas velas llegan."""
        df = payload["df"]
        ts, high, low, close = (df[k].to_numpy() for k in ("ts", "high", "low", "close"))
        minutes = TIMEFRAMES.get(payload.get("timeframe") or "")
        still = []
        for order in self.positions:
            closed = (resolve(order, ts, high, low, close, self.be_r, minutes * 60 if minutes else None)
                      if order.symbol == payload["symbol"] else None)
            if closed is None:
                still.append(order)
                continue
            amount = self.account.book(order, closed, self.risk_pct)
            self.publish("setup.closed", {"order": order, "closed": closed, "sent": False, "amount": amount,
                                          "balance": self.account.balance if amount is not None else None,
                                          "currency": self.account.currency})
            self.set_caption(f"cerrada: {closed.result} {closed.r:+.2f} R")
        if len(still) != len(self.positions):
            store.save(still, self.file)
            self.positions = still
            self._publish_account()
        if still:
            self.set_caption(f"{len(still)} posición(es) abierta(s)")
