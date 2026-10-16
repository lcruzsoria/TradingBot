"""Editor de las reglas del Bias: qué reglas se aplican y con qué peso."""
from __future__ import annotations

import inspect

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QDoubleSpinBox, QGridLayout, QHBoxLayout, QLabel,
                               QVBoxLayout)

from ..skills.bias.rules import RULE_REGISTRY

OVERLAPS = (("tdo", "above_below_open"),)      # reglas que miden casi lo mismo: activadas a la vez contarían doble


def rule_choices() -> list[tuple[str, str, str, float]]:
    """Reglas disponibles: (clave, nombre, descripción, peso por defecto), en el orden en que se definieron."""
    return [(key, cls.title or key, inspect.getdoc(cls) or "", float(cls.weight)) for key, cls in RULE_REGISTRY.items()]


class RulesDialog(QDialog):
    """Marca las reglas que aplican y fija el peso de cada una; el sesgo es la suma de voto x peso."""

    def __init__(self, parent, active: list[tuple[str, float]], min_score: float) -> None:
        super().__init__(parent)
        self.setWindowTitle("Reglas del sesgo")
        self.setMinimumWidth(560)
        weights = dict(active)
        self.checks: dict[str, QCheckBox] = {}
        self.spins: dict[str, QDoubleSpinBox] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)
        intro = QLabel("Marca las reglas que aplican al sesgo y dales un peso. Cada regla vota +1, -1 o 0; el sesgo "
                       "sale de la suma de voto × peso.")
        intro.setWordWrap(True)
        intro.setObjectName("Muted")
        root.addWidget(intro)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(8)
        for col, text in enumerate(("Aplicar", "Regla", "Peso")):
            head = QLabel(text)
            head.setObjectName("Muted")
            grid.addWidget(head, 0, col)
        for row, (key, title, doc, default_weight) in enumerate(rule_choices(), start=1):
            check = QCheckBox()
            check.setChecked(key in weights)
            name = QLabel(title)
            name.setStyleSheet("font-weight: 600;")
            name.setToolTip(doc)
            check.setToolTip(doc)
            spin = QDoubleSpinBox()
            spin.setRange(0.0, 10.0)
            spin.setSingleStep(0.5)
            spin.setDecimals(1)
            spin.setValue(weights.get(key, default_weight))
            spin.setEnabled(check.isChecked())
            spin.setFixedWidth(84)
            check.toggled.connect(spin.setEnabled)
            check.toggled.connect(self._refresh_notes)
            first_line = doc.splitlines()[0] if doc else ""
            detail = QLabel(first_line)
            detail.setObjectName("Muted")
            detail.setWordWrap(True)
            grid.addWidget(check, row * 2 - 1, 0, 2, 1, Qt.AlignmentFlag.AlignTop)
            grid.addWidget(name, row * 2 - 1, 1)
            grid.addWidget(spin, row * 2 - 1, 2, 2, 1, Qt.AlignmentFlag.AlignTop)
            grid.addWidget(detail, row * 2, 1)
            self.checks[key], self.spins[key] = check, spin
        grid.setColumnStretch(1, 1)
        root.addLayout(grid)

        minimum = QHBoxLayout()
        minimum.addWidget(QLabel("Puntuación mínima para tener sesgo"))
        self.min_spin = QDoubleSpinBox()
        self.min_spin.setRange(0.5, 20.0)
        self.min_spin.setSingleStep(0.5)
        self.min_spin.setDecimals(1)
        self.min_spin.setValue(min_score)
        self.min_spin.setFixedWidth(84)
        self.min_spin.setToolTip("Bullish con esta puntuación o más; Bearish con menos de su opuesto; si no, No Bias.")
        minimum.addStretch(1)
        minimum.addWidget(self.min_spin)
        root.addLayout(minimum)

        self.note = QLabel("")
        self.note.setWordWrap(True)
        self.note.setObjectName("Muted")
        root.addWidget(self.note)
        buttons = QDialogButtonBox()
        self.save_btn = buttons.addButton("Guardar y aplicar", QDialogButtonBox.ButtonRole.AcceptRole)
        buttons.addButton("Cancelar", QDialogButtonBox.ButtonRole.RejectRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)
        self._refresh_notes()

    def _refresh_notes(self) -> None:
        titles = {key: title for key, title, _doc, _w in rule_choices()}
        warnings = [f"«{titles[a]}» y «{titles[b]}» miden casi lo mismo: activadas a la vez contarían doble."
                    for a, b in OVERLAPS if self.checks[a].isChecked() and self.checks[b].isChecked()]
        if not any(c.isChecked() for c in self.checks.values()):
            warnings.append("Sin ninguna regla el sesgo es siempre No Bias.")
        self.note.setText("  ".join(warnings) or "Se guarda en tradingbot.env (BIAS_RULES y BIAS_<REGLA>_WEIGHT) y se aplica al momento.")

    def selection(self) -> list[tuple[str, float]]:
        """Reglas marcadas con su peso, en el orden de la lista."""
        return [(key, round(self.spins[key].value(), 3)) for key in self.checks if self.checks[key].isChecked()]

    def min_score(self) -> float:
        return round(self.min_spin.value(), 3)
