"""Bus de eventos: así se comunican las skills entre sí y con la interfaz.

- publish(topic, payload, source) entrega el evento a todos los suscriptores cuyo patrón encaje.
- Patrones: "bias.updated" (exacto), "bias.*" (prefijo) y "*" (todo).
- La entrega es inmediata y no bloquea: los suscriptores solo encolan o emiten una señal.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class Event:
    topic: str
    payload: dict[str, Any] = field(default_factory=dict)
    source: str = ""
    ts: float = field(default_factory=time.time)


Callback = Callable[[Event], None]
Tap = Callable[[Event, list[str]], None]


def matches(pattern: str, topic: str) -> bool:
    if pattern == "*" or pattern == topic:
        return True
    return pattern.endswith(".*") and topic.startswith(pattern[:-1])


class EventBus:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._subs: list[tuple[str, str, Callback]] = []   # (nombre, patrón, callback)
        self._taps: list[Tap] = []

    def subscribe(self, name: str, pattern: str, callback: Callback) -> None:
        with self._lock:
            self._subs.append((name, pattern, callback))

    def unsubscribe(self, name: str) -> None:
        with self._lock:
            self._subs = [s for s in self._subs if s[0] != name]

    def add_tap(self, tap: Tap) -> None:
        """Observador global: recibe cada evento junto con los nombres de quienes lo recibieron."""
        with self._lock:
            self._taps.append(tap)

    def publish(self, topic: str, payload: dict[str, Any] | None = None, source: str = "") -> Event:
        event = Event(topic, payload or {}, source)
        with self._lock:
            targets = [s for s in self._subs if matches(s[1], topic)]
            taps = list(self._taps)
        names: list[str] = []
        for name, _pattern, callback in targets:
            if name == source:          # nadie recibe sus propios mensajes
                continue
            names.append(name)
            try:
                callback(event)
            except Exception:           # un suscriptor roto no debe afectar a los demás
                pass
        for tap in taps:
            try:
                tap(event, names)
            except Exception:
                pass
        return event
