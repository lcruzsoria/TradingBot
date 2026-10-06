"""Ejecución de tareas en segundo plano para no bloquear la interfaz."""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QThread, Signal


class Worker(QThread):
    """Ejecuta fn(progress_callback) en un hilo y emite el resultado o el error."""

    done = Signal(object)
    failed = Signal(str)
    progress = Signal(int)

    def __init__(self, fn: Callable[[Callable[[int], None]], object], parent=None):
        super().__init__(parent)
        self._fn = fn

    def run(self) -> None:
        try:
            self.done.emit(self._fn(self.progress.emit))
        except Exception as exc:  # noqa: BLE001 - se muestra al usuario
            self.failed.emit(f"{type(exc).__name__}: {exc}")
