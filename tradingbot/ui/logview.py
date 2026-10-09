"""Registro de la ventana principal: una línea por evento relevante de las skills.

Cuando el evento tiene más información de la que cabe en una línea (votos de las reglas, controles del Bias Execution,
datos de un setup...), la línea lleva un enlace «+ detalle» que la abre en una ventana aparte.
"""
from __future__ import annotations

import html
from datetime import datetime

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QTextBrowser, QVBoxLayout, QWidget

from . import theme

MAX_LINES = 500


class LogView(QTextBrowser):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("LogView")
        self.setOpenLinks(False)                 # los enlaces abren el detalle, no un navegador
        self.setReadOnly(True)
        self.document().setMaximumBlockCount(MAX_LINES)
        self._details: dict[int, tuple[str, str]] = {}
        self._next_id = 0
        self.anchorClicked.connect(self._open)

    def add(self, message: str, detail: str | None = None, tone: str | None = None) -> None:
        """tone: "go" (verde), "nogo" (rojo), "warn" o "info" (color de acento); None, el gris normal."""
        stamp = f"[{datetime.now():%H:%M:%S}]"
        colors = {"go": theme.BULL, "nogo": theme.BEAR, "warn": theme.WARN, "info": theme.ACCENT}
        text = html.escape(message)
        if tone in colors:
            text = f"<span style='color:{colors[tone]}'>{text}</span>"
        if detail:
            self._next_id += 1
            self._details[self._next_id] = (message, detail)
            if len(self._details) > MAX_LINES:
                self._details.pop(min(self._details))
            text += f" <a href='detalle:{self._next_id}' style='color:{theme.ACCENT}'>+ detalle</a>"
        self.append(f"{stamp} {text}")
        bar = self.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _open(self, url: QUrl) -> None:
        try:
            title, detail = self._details[int(url.toString().split(":", 1)[1])]
        except (KeyError, ValueError, IndexError):
            return
        DetailDialog(title, detail, self.window()).show()


class DetailDialog(QDialog):
    """Detalle de una línea del Registro (no bloquea la ventana principal)."""

    def __init__(self, title: str, detail: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Registro: detalle")
        self.setMinimumWidth(560)
        lay = QVBoxLayout(self)
        head = QLabel(title)
        head.setObjectName("CardTitle")
        head.setWordWrap(True)
        lay.addWidget(head)
        body = QTextBrowser()
        body.setObjectName("LogView")
        body.setPlainText(detail)
        body.setMinimumHeight(220)
        lay.addWidget(body, 1)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.close)
        lay.addWidget(buttons)
