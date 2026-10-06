"""Editor de colores: cambia la paleta al instante y, si quieres, la guarda."""
from __future__ import annotations

from dataclasses import replace
from typing import Callable

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QColorDialog, QComboBox, QDialog, QGridLayout, QHBoxLayout, QLabel, QPushButton,
                               QVBoxLayout)

from . import theme
from .theme import LABELS, PRESETS, Palette

PRESET_NAMES = {"negro": "Negro (texto azul, verde y rojo)", "pizarra": "Azul pizarra"}


def contrast_text(hex_color: str) -> str:
    """Negro o blanco, el que se lea mejor sobre ese color."""
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#000000" if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else "#ffffff"


class ThemeDialog(QDialog):
    def __init__(self, parent, preset: str, palette: Palette,
                 on_change: Callable[[str, Palette], None]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Colores")
        self.setMinimumWidth(380)
        self.preset, self.palette, self._on_change = preset, palette, on_change
        self.swatches: dict[str, QPushButton] = {}

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)

        top = QHBoxLayout()
        top.addWidget(QLabel("Paleta base"))
        self.preset_box = QComboBox()
        for key in PRESETS:
            self.preset_box.addItem(PRESET_NAMES.get(key, key), key)
        self.preset_box.setCurrentIndex(self.preset_box.findData(preset))
        self.preset_box.activated.connect(lambda _i: self._choose_preset(self.preset_box.currentData()))
        top.addWidget(self.preset_box, 1)
        lay.addLayout(top)

        grid = QGridLayout()
        grid.setVerticalSpacing(6)
        for row, (key, label) in enumerate(LABELS.items()):
            grid.addWidget(QLabel(label), row, 0)
            btn = QPushButton()
            btn.setMinimumWidth(120)
            btn.clicked.connect(lambda _c=False, k=key: self._pick(k))
            grid.addWidget(btn, row, 1)
            self.swatches[key] = btn
        lay.addLayout(grid)

        self.hint = QLabel("Los cambios se ven al instante. «Guardar» los conserva para la próxima vez "
                           "(theme.local.json, no se sube a git).")
        self.hint.setObjectName("Muted")
        self.hint.setWordWrap(True)
        lay.addWidget(self.hint)

        buttons = QHBoxLayout()
        self.reset_btn = QPushButton("Restablecer paleta")
        self.save_btn = QPushButton("Guardar")
        self.save_btn.setObjectName("Primary")
        close_btn = QPushButton("Cerrar")
        self.reset_btn.clicked.connect(lambda: self._choose_preset(self.preset))
        self.save_btn.clicked.connect(self.save)
        close_btn.clicked.connect(self.accept)
        buttons.addWidget(self.reset_btn)
        buttons.addStretch(1)
        buttons.addWidget(self.save_btn)
        buttons.addWidget(close_btn)
        lay.addLayout(buttons)
        self._refresh_swatches()

    # -- cambios -------------------------------------------------------------------------------
    def _refresh_swatches(self) -> None:
        for key, btn in self.swatches.items():
            value = getattr(self.palette, key)
            btn.setText(value.upper())
            btn.setStyleSheet(f"background: {value}; color: {contrast_text(value)}; "
                              f"border: 1px solid {theme.BORDER}; font-weight: 600;")

    def _emit(self) -> None:
        self._refresh_swatches()
        self._on_change(self.preset, self.palette)

    def set_color(self, key: str, value: str) -> None:
        self.palette = replace(self.palette, **theme.validate({key: value}))
        self.hint.setText("Cambios sin guardar. Pulsa «Guardar» para conservarlos.")
        self._emit()

    def _pick(self, key: str) -> None:
        color = QColorDialog.getColor(QColor(getattr(self.palette, key)), self, LABELS[key])
        if color.isValid():
            self.set_color(key, color.name())

    def _choose_preset(self, name: str) -> None:
        self.preset, self.palette = name, PRESETS[name]
        self.preset_box.setCurrentIndex(self.preset_box.findData(name))
        self.hint.setText("Paleta restablecida. Pulsa «Guardar» para conservarla.")
        self._emit()

    def save(self) -> None:
        try:
            theme.save_local(self.preset, self.palette)
        except OSError as exc:
            self.hint.setText(f"No se pudo guardar: {exc}")
            return
        self.hint.setText(f"Guardado en {theme.LOCAL_THEME_FILE.name}.")
