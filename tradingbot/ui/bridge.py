"""Puente bus -> interfaz: pasa los eventos de los hilos de las skills al hilo de Qt."""
from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from ..core import Event, EventBus


class UiBridge(QObject):
    event = Signal(object)            # Event (se entrega en el hilo de la interfaz)
    flow = Signal(str, list, str)     # origen, destinatarios, tema: para animar los hexágonos

    def __init__(self, bus: EventBus) -> None:
        super().__init__()
        self.bus = bus
        bus.subscribe("ui", "*", self.event.emit)
        bus.add_tap(self._tap)

    def _tap(self, event: Event, targets: list[str]) -> None:
        if event.topic.startswith("skill."):          # estado y errores no son tráfico entre skills
            return
        skills = [t for t in targets if t != "ui"]
        if skills:
            self.flow.emit(event.source, skills, event.topic)

    def publish(self, topic: str, payload: dict | None = None) -> None:
        self.bus.publish(topic, payload, source="ui")
