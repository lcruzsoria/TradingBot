"""Skill Setup: el ejecutor. Solo actúa cuando Cortex le da la orden de operar en la cuenta del broker."""
from __future__ import annotations

from ...core import Event, Skill, register_skill


@register_skill("setup")
class SetupSkill(Skill):
    title = "Setup"
    description = ("El ejecutor: mete la operación en la cuenta del broker (MT5). Solo recibe órdenes de Cortex, que es "
                   "quien reúne el activo, la temporalidad, el sesgo, la TBR y el patrón válido; Setup no decide nada. "
                   "Por ahora funciona en modo simulación: prepara la orden y la anota, pero no la envía a MT5.")
    subscribes = ("setup.order",)
    publishes = ("setup.executed",)
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
        self.set_caption("esperando a Cortex")

    def handle(self, event: Event) -> None:
        if self.error:
            raise ValueError(self.error)
        if event.source != "cortex":                    # solo Cortex puede dar la orden de operar
            self.set_caption("orden rechazada")
            return
        order = event.payload["order"]
        self.executed += 1
        self.set_caption(f"simulada: {order.direction.capitalize()} {order.symbol}")
        self.publish("setup.executed", {"order": order, "sent": False,
                                        "note": "Modo simulación: la orden está lista pero no se ha enviado a MT5."})
