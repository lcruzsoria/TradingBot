"""Configuración del botón SMA del gráfico: qué dibuja (SMA, VWAP o los dos) y periodos, color y trazo de cada línea."""
from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QColorDialog, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLabel, QPushButton,
                               QSpinBox, QVBoxLayout)

from ..skills.levels.daylevels import DEFAULT_COLORS, DEFAULT_SMA_SHOW, SMA_SHOWS, SMA_STYLES
from . import theme

STYLE_NAMES = {"normal": "Normal", "discontinuo": "Discontinuo", "punteado": "Punteado"}
SHOW_NAMES = {"sma": "SMA", "vwap": "VWAP", "ambos": "SMA y VWAP"}


def contrast_text(color: str) -> str:
    c = QColor(color)
    return "#000000" if (299 * c.red() + 587 * c.green() + 114 * c.blue()) / 1000 > 140 else "#FFFFFF"


class SmaDialog(QDialog):
    """Elige qué dibuja el botón (SMA, VWAP o ambos) y, de cada línea, el color y el trazo; de la SMA, también los periodos."""

    def __init__(self, parent, period: int, color: str, style: str, show: str = DEFAULT_SMA_SHOW,
                 vwap_color: str = DEFAULT_COLORS["VWAP"], vwap_style: str = SMA_STYLES[0]) -> None:
        super().__init__(parent)
        self.setWindowTitle("SMA / VWAP")
        self.setMinimumWidth(360)
        self._color, self._vwap_color = color, vwap_color
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)
        intro = QLabel("SMA: media móvil simple de los cierres, con las velas del timeframe que estás viendo.\n"
                       "VWAP: precio medio ponderado por volumen (precio típico y tick volume), que se reinicia al empezar "
                       "cada día de trading.")
        intro.setWordWrap(True)
        intro.setObjectName("Muted")
        root.addWidget(intro)

        form = QFormLayout()
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(8)
        self.show_box = QComboBox()
        for key in SMA_SHOWS:
            self.show_box.addItem(SHOW_NAMES[key], key)
        self.show_box.setCurrentIndex(SMA_SHOWS.index(show) if show in SMA_SHOWS else 0)
        form.addRow("Mostrar", self.show_box)
        self.period_spin = QSpinBox()
        self.period_spin.setRange(1, 1000)
        self.period_spin.setValue(period)
        self.period_spin.setSuffix(" periodos")
        form.addRow("Periodos de la SMA", self.period_spin)
        self.color_btn = QPushButton()
        self.color_btn.clicked.connect(lambda: self._pick("sma"))
        form.addRow("Color de la SMA", self.color_btn)
        self.style_box = self._style_box(style)
        form.addRow("Trazo de la SMA", self.style_box)
        self.vwap_color_btn = QPushButton()
        self.vwap_color_btn.clicked.connect(lambda: self._pick("vwap"))
        form.addRow("Color del VWAP", self.vwap_color_btn)
        self.vwap_style_box = self._style_box(vwap_style)
        form.addRow("Trazo del VWAP", self.vwap_style_box)
        root.addLayout(form)

        buttons = QDialogButtonBox()
        buttons.addButton("Guardar y aplicar", QDialogButtonBox.ButtonRole.AcceptRole)
        buttons.addButton("Cancelar", QDialogButtonBox.ButtonRole.RejectRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)
        self.show_box.currentIndexChanged.connect(self._sync_rows)
        self._paint()
        self._sync_rows()

    @staticmethod
    def _style_box(style: str) -> QComboBox:
        box = QComboBox()
        for key in SMA_STYLES:
            box.addItem(STYLE_NAMES[key], key)
        box.setCurrentIndex(SMA_STYLES.index(style) if style in SMA_STYLES else 0)
        return box

    def _sync_rows(self) -> None:
        """Los ajustes de la línea que no se va a dibujar quedan desactivados."""
        mode = self.show_box.currentData()
        for widget in (self.period_spin, self.color_btn, self.style_box):
            widget.setEnabled(mode in ("sma", "ambos"))
        for widget in (self.vwap_color_btn, self.vwap_style_box):
            widget.setEnabled(mode in ("vwap", "ambos"))

    def _paint(self) -> None:
        for button, color in ((self.color_btn, self._color), (self.vwap_color_btn, self._vwap_color)):
            button.setText(color.upper())
            button.setStyleSheet(f"background: {color}; color: {contrast_text(color)}; "
                                 f"border: 1px solid {theme.BORDER}; font-weight: 600;")

    def _pick(self, which: str) -> None:
        current = self._color if which == "sma" else self._vwap_color
        color = QColorDialog.getColor(QColor(current), self, "Color de la SMA" if which == "sma" else "Color del VWAP")
        if not color.isValid():
            return
        if which == "sma":
            self._color = color.name().upper()
        else:
            self._vwap_color = color.name().upper()
        self._paint()

    def values(self) -> tuple[int, str, str, str, str, str]:
        """(periodos de la SMA, color de la SMA #RRGGBB, trazo de la SMA, qué mostrar, color del VWAP, trazo del VWAP)."""
        return (self.period_spin.value(), self._color, self.style_box.currentData(), self.show_box.currentData(),
                self._vwap_color, self.vwap_style_box.currentData())
