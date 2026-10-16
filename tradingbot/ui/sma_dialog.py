"""Configuración de la media móvil simple (SMA) del gráfico: periodos, color y trazo de la línea."""
from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QColorDialog, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLabel, QPushButton,
                               QSpinBox, QVBoxLayout)

from ..skills.levels.daylevels import SMA_STYLES
from . import theme

STYLE_NAMES = {"normal": "Normal", "discontinuo": "Discontinuo", "punteado": "Punteado"}


def contrast_text(color: str) -> str:
    c = QColor(color)
    return "#000000" if (299 * c.red() + 587 * c.green() + 114 * c.blue()) / 1000 > 140 else "#FFFFFF"


class SmaDialog(QDialog):
    """Elige los periodos de la SMA (velas del timeframe que se está viendo), el color de su línea y el trazo."""

    def __init__(self, parent, period: int, color: str, style: str) -> None:
        super().__init__(parent)
        self.setWindowTitle("SMA")
        self.setMinimumWidth(340)
        self._color = color
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)
        intro = QLabel("Media móvil simple de los cierres, con las velas del timeframe que estás viendo.")
        intro.setWordWrap(True)
        intro.setObjectName("Muted")
        root.addWidget(intro)

        form = QFormLayout()
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(8)
        self.period_spin = QSpinBox()
        self.period_spin.setRange(1, 1000)
        self.period_spin.setValue(period)
        self.period_spin.setSuffix(" periodos")
        form.addRow("Periodos", self.period_spin)
        self.color_btn = QPushButton()
        self.color_btn.clicked.connect(self._pick)
        form.addRow("Color de la línea", self.color_btn)
        self.style_box = QComboBox()
        for key in SMA_STYLES:
            self.style_box.addItem(STYLE_NAMES[key], key)
        self.style_box.setCurrentIndex(SMA_STYLES.index(style) if style in SMA_STYLES else 0)
        form.addRow("Trazo", self.style_box)
        root.addLayout(form)

        buttons = QDialogButtonBox()
        buttons.addButton("Guardar y aplicar", QDialogButtonBox.ButtonRole.AcceptRole)
        buttons.addButton("Cancelar", QDialogButtonBox.ButtonRole.RejectRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)
        self._paint()

    def _paint(self) -> None:
        self.color_btn.setText(self._color.upper())
        self.color_btn.setStyleSheet(f"background: {self._color}; color: {contrast_text(self._color)}; "
                                     f"border: 1px solid {theme.BORDER}; font-weight: 600;")

    def _pick(self) -> None:
        color = QColorDialog.getColor(QColor(self._color), self, "Color de la SMA")
        if color.isValid():
            self._color = color.name().upper()
            self._paint()

    def values(self) -> tuple[int, str, str]:
        """(periodos, color #RRGGBB, trazo)."""
        return self.period_spin.value(), self._color, self.style_box.currentData()
