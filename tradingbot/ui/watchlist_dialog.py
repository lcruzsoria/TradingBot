"""Editor de la lista de mercados: busca entre los símbolos de tu broker y ordénalos."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QAbstractItemView, QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton,
                               QVBoxLayout)

from ..settings import clean_symbols

# Búsquedas por nombre común -> fragmentos que suelen llevar los símbolos de los brokers.
ALIASES: dict[str, list[str]] = {
    "dow": ["DJ30", "DJI", "US30", "WS30", "DOW"], "dow jones": ["DJ30", "DJI", "US30", "WS30", "DOW"],
    "wall street": ["US30", "WS30"],
    "nasdaq": ["NAS", "USTEC", "US100", "NDX"], "nasdaq 100": ["NAS", "USTEC", "US100", "NDX"],
    "s&p": ["SP500", "US500", "SPX"], "s&p 500": ["SP500", "US500", "SPX"], "sp500": ["SP500", "US500", "SPX"],
    "dax": ["GER", "DE40", "DE30", "DAX"], "ibex": ["ES35", "IBEX"], "nikkei": ["NIKKEI", "JP225", "JPN225"],
    "oro": ["XAU", "GOLD"], "gold": ["XAU", "GOLD"], "plata": ["XAG", "SILVER"], "silver": ["XAG", "SILVER"],
    "petroleo": ["OIL", "WTI", "XTI", "BRENT", "XBR"], "petróleo": ["OIL", "WTI", "XTI", "BRENT", "XBR"],
    "oil": ["OIL", "WTI", "XTI", "BRENT", "XBR"], "bitcoin": ["BTC"], "ethereum": ["ETH"],
}
MAX_SHOWN = 400


def filter_symbols(names: list[str], query: str) -> list[str]:
    """Símbolos que encajan con la búsqueda (sin distinguir mayúsculas; entiende 'dow', 'oro', 'nasdaq'...)."""
    q = query.strip().lower()
    if not q:
        return list(names)[:MAX_SHOWN]
    terms = [t.lower() for t in ALIASES.get(q, [])] + [q]
    return [n for n in names if any(t in n.lower() for t in terms)][:MAX_SHOWN]


class WatchlistDialog(QDialog):
    def __init__(self, parent, broker_symbols: list[str], current: list[str]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Mercados")
        self.setMinimumSize(640, 460)
        self.broker_symbols = list(broker_symbols)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)
        columns = QHBoxLayout()
        columns.setSpacing(14)

        # columna izquierda: buscar y añadir
        left = QVBoxLayout()
        left.addWidget(QLabel("Símbolos de tu broker"))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Busca: dow, nasdaq, dax, oro, petróleo, bitcoin, DJ30…")
        self.search.textChanged.connect(self._refresh_matches)
        self.search.returnPressed.connect(self.add_selected)
        self.matches = QListWidget()
        self.matches.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.matches.itemDoubleClicked.connect(lambda _i: self.add_selected())
        self.add_btn = QPushButton("Añadir")
        self.add_btn.clicked.connect(self.add_selected)
        left.addWidget(self.search)
        left.addWidget(self.matches, 1)
        left.addWidget(self.add_btn)
        columns.addLayout(left, 1)

        # columna derecha: lista actual
        right = QVBoxLayout()
        right.addWidget(QLabel("Mercados mostrados"))
        self.chosen = QListWidget()
        self.chosen.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.chosen.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.chosen.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.chosen.addItems(clean_symbols(current))
        buttons = QHBoxLayout()
        up, down, remove = QPushButton("Subir"), QPushButton("Bajar"), QPushButton("Quitar")
        up.clicked.connect(lambda: self.move(-1))
        down.clicked.connect(lambda: self.move(1))
        remove.clicked.connect(self.remove_selected)
        for b in (up, down, remove):
            buttons.addWidget(b)
        right.addWidget(self.chosen, 1)
        right.addLayout(buttons)
        columns.addLayout(right, 1)
        root.addLayout(columns, 1)

        self.hint = QLabel("")
        self.hint.setObjectName("Muted")
        self.hint.setWordWrap(True)
        root.addWidget(self.hint)
        bottom = QHBoxLayout()
        bottom.addStretch(1)
        save = QPushButton("Guardar")
        save.setObjectName("Primary")
        cancel = QPushButton("Cancelar")
        save.clicked.connect(self._save)
        cancel.clicked.connect(self.reject)
        bottom.addWidget(save)
        bottom.addWidget(cancel)
        root.addLayout(bottom)

        if not self.broker_symbols:
            self.hint.setText("No hay lista de símbolos del broker (¿sin conexión?). Puedes escribir un nombre "
                              "exacto y pulsar Enter para añadirlo.")
        self._refresh_matches()

    def _save(self) -> None:
        if not self.symbols:
            self.hint.setText("Añade al menos un mercado: el selector del gráfico solo ofrece los de esta lista.")
            return
        self.accept()

    # -- datos -----------------------------------------------------------------------------------
    @property
    def symbols(self) -> list[str]:
        return clean_symbols(self.chosen.item(i).text() for i in range(self.chosen.count()))

    def _refresh_matches(self) -> None:
        self.matches.clear()
        self.matches.addItems(filter_symbols(self.broker_symbols, self.search.text()))
        if self.matches.count() and self.search.text().strip():
            self.matches.setCurrentRow(0)

    # -- acciones ------------------------------------------------------------------------------------
    def add_symbol(self, name: str) -> None:
        if name.strip().lower() not in {s.lower() for s in self.symbols}:
            self.chosen.addItem(name.strip())

    def add_selected(self) -> None:
        picked = [i.text() for i in self.matches.selectedItems()]
        if picked:
            for name in picked:
                self.add_symbol(name)
        elif not self.broker_symbols and self.search.text().strip():
            self.add_symbol(self.search.text())   # sin lista del broker: se añade tal cual
            self.search.clear()

    def remove_selected(self) -> None:
        for item in self.chosen.selectedItems():
            self.chosen.takeItem(self.chosen.row(item))

    def move(self, delta: int) -> None:
        row = self.chosen.currentRow()
        new = row + delta
        if row < 0 or not 0 <= new < self.chosen.count():
            return
        item = self.chosen.takeItem(row)
        self.chosen.insertItem(new, item)
        self.chosen.setCurrentRow(new)
