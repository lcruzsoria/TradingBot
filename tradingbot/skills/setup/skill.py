"""Skill Setup: el ejecutor. Solo actúa cuando Cortex le da la orden de operar en la cuenta del broker."""
from __future__ import annotations

from ...core import Event, Skill, register_skill
from .positions import resolve, trackable


@register_skill("setup")
class SetupSkill(Skill):
    title = "Setup"
    description = ("El ejecutor: mete la operación en la cuenta del broker (MT5). Solo recibe órdenes de Cortex, que es "
                   "quien reúne el activo, la temporalidad, el sesgo, la TBR y el patrón válido; Setup no decide nada. "
                   "Por ahora funciona en modo simulación: prepara la orden y la anota, pero no la envía a MT5. Sigue las "
                   "posiciones simuladas (stop, objetivo y cierre por tiempo) con las velas que le reenvía Cortex.")
    subscribes = ("setup.order", "setup.candles")
    publishes = ("setup.executed", "setup.closed")
    slot = "aux1"

    def on_start(self) -> None:
        self.error = "Configuración SETUP no válida"
        self.send_orders = self.settings.get_bool("SEND_ORDERS", False)      # tradingbot.env, bloque SETUP
        if self.send_orders:
            self.error = ("SETUP_SEND_ORDERS=true: el envío real de órdenes a MT5 aún no está implementado "
                          "(la skill funciona en modo simulación)")
            raise ValueError(self.error)
        self.error = ""
        self.executed = 0
        self.positions: list = []                       # órdenes simuladas abiertas (se pierden al reiniciar el bot)
        self.set_caption("esperando a Cortex")

    def handle(self, event: Event) -> None:
        if self.error:
            raise ValueError(self.error)
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
        self.set_caption(f"simulada: {order.direction.capitalize()} {order.symbol}")
        note = "Modo simulación: la orden está lista pero no se ha enviado a MT5."
        if trackable(order):
            note += " El resultado se anotará en el Registro cuando la posición cierre (stop, objetivo o 24 h)."
        self.publish("setup.executed", {"order": order, "sent": False, "note": note})

    def _follow(self, payload: dict) -> None:
        """Comprueba stop, objetivo y cierre por tiempo de las posiciones abiertas del mercado cuyas velas llegan."""
        df = payload["df"]
        ts, high, low, close = (df[k].to_numpy() for k in ("ts", "high", "low", "close"))
        still = []
        for order in self.positions:
            closed = resolve(order, ts, high, low, close) if order.symbol == payload["symbol"] else None
            if closed is None:
                still.append(order)
                continue
            self.publish("setup.closed", {"order": order, "closed": closed, "sent": False})
            self.set_caption(f"cerrada: {closed.result} {closed.r:+.2f} R")
        self.positions = still
        if still:
            self.set_caption(f"{len(still)} posición(es) abierta(s)")
