"""Widgets propios: panel, tarjetas de mercado, tarjeta del Bias y reglas."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..bias import Bias, BiasResult, Direction
from ..bias.rules import fmt_price
from ..datasource import Quote
from . import theme
from .fmt import fecha_larga, hace

STALE_AFTER_SECONDS = 300  # un tick más de 5 min por detrás del más reciente = mercado cerrado


def repolish(widget: QWidget) -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class StatBlock(QWidget):
    """Cifra destacada de la cabecera: etiqueta, valor y nota."""

    def __init__(self, label: str, value: str = "-", sub: str = "") -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.label = QLabel(label)
        self.label.setObjectName("StatLabel")
        self.value = QLabel(value)
        self.value.setObjectName("StatValue")
        self.sub = QLabel(sub)
        self.sub.setObjectName("StatSub")
        for w in (self.label, self.value, self.sub):
            lay.addWidget(w)

    def set_value(self, value: str, sub: str = "", color: str | None = None) -> None:
        self.value.setText(value)
        self.value.setStyleSheet(f"color: {color};" if color else "")
        self.sub.setText(sub)


class Panel(QFrame):
    """Panel con título a la izquierda y nota a la derecha."""

    def __init__(self, title: str, note: str = "") -> None:
        super().__init__()
        self.setObjectName("Card")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 11, 14, 12)
        outer.setSpacing(8)
        head = QHBoxLayout()
        self.head = head
        self.title = QLabel(title)
        self.title.setObjectName("CardTitle")
        self.note = QLabel(note)
        self.note.setObjectName("CardNote")
        head.addWidget(self.title)
        head.addStretch(1)
        head.addWidget(self.note)
        outer.addLayout(head)
        self.body = QVBoxLayout()
        self.body.setSpacing(8)
        outer.addLayout(self.body, 1)

    def add_header_widget(self, widget: QWidget) -> None:
        """Coloca un control (p. ej. un botón) en la cabecera, a la derecha de la nota."""
        self.head.addWidget(widget)


class MarketCard(QFrame):
    clicked = Signal(str)

    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.symbol = symbol
        self._last_bid: float | None = None
        self.setObjectName("MarketCard")
        self.setProperty("selected", "false")
        self.setProperty("stale", "false")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(11, 8, 11, 8)
        lay.setSpacing(1)

        top = QHBoxLayout()
        self.name = QLabel(symbol)
        self.name.setObjectName("MkSymbol")
        self.badge = QLabel("Mercado cerrado")
        self.badge.setObjectName("MkBadge")
        self.badge.hide()
        top.addWidget(self.name)
        top.addStretch(1)
        top.addWidget(self.badge)
        self.price = QLabel("-")
        self.price.setObjectName("MkPrice")
        bottom = QHBoxLayout()
        self.spread = QLabel("")
        self.spread.setObjectName("MkSub")
        self.age = QLabel("")
        self.age.setObjectName("MkSub")
        bottom.addWidget(self.spread)
        bottom.addStretch(1)
        bottom.addWidget(self.age)
        lay.addLayout(top)
        lay.addWidget(self.price)
        lay.addLayout(bottom)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.symbol)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", "true" if selected else "false")
        repolish(self)

    def set_quote(self, quote: Quote | None, age: int = 0) -> None:
        if quote is None:
            self._last_bid = None
            self.price.setStyleSheet("")
            self.price.setText("-")
            self.spread.setText("No disponible en este broker")
            self.age.setText("")
            self._set_stale(True, badge=False)
            return
        stale = age > STALE_AFTER_SECONDS
        # El precio se tiñe de verde si el último tick sube y de rojo si baja; si no cambia, mantiene el color.
        if stale:
            self.price.setStyleSheet("")
        elif self._last_bid is not None and quote.bid != self._last_bid:
            self.price.setStyleSheet(f"color: {theme.BULL if quote.bid > self._last_bid else theme.BEAR};")
        self._last_bid = quote.bid
        self.price.setText(fmt_price(quote.bid))
        self.spread.setText(f"{fmt_price(quote.bid)} / {fmt_price(quote.ask)}")
        self.age.setText(hace(age))
        self._set_stale(stale, badge=stale)

    def _set_stale(self, stale: bool, badge: bool) -> None:
        self.badge.setVisible(badge)
        self.setProperty("stale", "true" if stale else "false")
        repolish(self)
        for child in (self.name, self.price):
            repolish(child)


class MarketsGrid(QWidget):
    """Cuadrícula de cotizaciones de solo lectura; al pulsar una tarjeta se elige el símbolo."""

    symbol_selected = Signal(str)

    def __init__(self, symbols: list[str], columns: int = 4) -> None:
        super().__init__()
        self.cards: dict[str, MarketCard] = {}
        self._columns = columns
        self._selected = ""
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(8)
        for c in range(columns):
            self._grid.setColumnStretch(c, 1)
        self.set_symbols(symbols)

    def set_symbols(self, symbols: list[str]) -> None:
        """Reconstruye las tarjetas con una lista nueva (conserva la selección si sigue en la lista)."""
        for card in self.cards.values():
            self._grid.removeWidget(card)
            card.deleteLater()
        self.cards = {}
        for i, sym in enumerate(symbols):
            card = MarketCard(sym)
            card.clicked.connect(self.symbol_selected)
            self.cards[sym] = card
            self._grid.addWidget(card, i // self._columns, i % self._columns)
        self.set_selected(self._selected)

    def set_selected(self, symbol: str) -> None:
        self._selected = symbol
        for sym, card in self.cards.items():
            card.set_selected(sym.lower() == symbol.strip().lower())

    def set_quotes(self, quotes: dict[str, Quote | None]) -> None:
        # Edad relativa al tick más reciente de la lista: no depende de la zona horaria del servidor.
        freshest = max((q.ts for q in quotes.values() if q), default=0)
        for sym, card in self.cards.items():
            q = quotes.get(sym)
            card.set_quote(q, freshest - q.ts if q else 0)


class BiasCard(QFrame):
    """Recuadro principal: sesgo de la sesión del día en curso.

    Pulsar Long o Short envía una petición de prueba a Cortex (`probe`).
    """

    probe = Signal(object)   # Direction

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("BiasCard")
        self.setProperty("state", "idle")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 16)
        lay.setSpacing(2)

        self.caption = QLabel("Sesgo de la sesión")
        self.caption.setObjectName("BiasCaption")
        self.value = QLabel("Sin calcular")
        self.value.setObjectName("BiasValue")
        self.detail = QLabel("Carga velas para calcular el sesgo")
        self.detail.setObjectName("BiasDetail")
        self.detail.setWordWrap(True)

        chips = QVBoxLayout()
        chips.setSpacing(5)
        self.long_chip = ClickableLabel("Long")
        self.short_chip = ClickableLabel("Short")
        for chip, direction in ((self.long_chip, Direction.LONG), (self.short_chip, Direction.SHORT)):
            chip.setObjectName("Chip")
            chip.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            chip.setCursor(Qt.CursorShape.PointingHandCursor)
            chip.setToolTip("Pregunta a Cortex si esta dirección está permitida ahora")
            chip.clicked.connect(lambda d=direction: self.probe.emit(d))
            chips.addWidget(chip)

        lay.addWidget(self.caption)
        lay.addWidget(self.value)
        lay.addWidget(self.detail)
        lay.addSpacing(8)
        lay.addLayout(chips)

    def set_loading(self) -> None:
        self.detail.setText("Calculando…")

    def set_result(self, result: BiasResult | None) -> None:
        if result is None:
            self.setProperty("state", "idle")
            self.value.setText("Sin calcular")
            self.detail.setText("Carga velas para calcular el sesgo")
            for chip, name in ((self.long_chip, "Long"), (self.short_chip, "Short")):
                chip.setProperty("allowed", "")
                chip.setText(name)
                repolish(chip)
        else:
            state = {Bias.BULLISH: "bull", Bias.BEARISH: "bear", Bias.NO_BIAS: "none"}[result.bias]
            self.setProperty("state", state)
            self.value.setText(result.bias.value)
            day = f"{fecha_larga(result.day)}. " if result.day else ""
            self.detail.setText(f"{day}{result.summary}")
            for chip, direction, arrow in ((self.long_chip, Direction.LONG, "▲"), (self.short_chip, Direction.SHORT, "▼")):
                ok = result.allows(direction)
                chip.setProperty("allowed", "true" if ok else "false")
                chip.setText(f"{arrow} {direction.value} {'permitido' if ok else 'bloqueado'}")
                repolish(chip)
        repolish(self)
        repolish(self.value)


class RulesList(QWidget):
    """Desglose: qué votó cada regla del Bias."""

    def __init__(self) -> None:
        super().__init__()
        self._rows = QVBoxLayout(self)
        self._rows.setContentsMargins(0, 0, 0, 0)
        self._rows.setSpacing(8)
        self._result: BiasResult | None = None
        self.set_result(None)

    def refresh(self) -> None:
        self.set_result(self._result)

    def _clear(self) -> None:
        while self._rows.count():
            item = self._rows.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def set_result(self, result: BiasResult | None) -> None:
        self._result = result
        self._clear()
        if result is None or not result.votes:
            empty = QLabel("Aún no hay reglas evaluadas.")
            empty.setObjectName("Muted")
            self._rows.addWidget(empty)
            self._rows.addStretch(1)
            return
        colors = {1: theme.BULL, -1: theme.BEAR, 0: theme.NEUTRAL}
        marks = {1: "▲", -1: "▼", 0: "–"}
        for vote in result.votes:
            row = QWidget()
            h = QHBoxLayout(row)
            h.setContentsMargins(0, 0, 0, 0)
            h.setSpacing(8)
            mark = QLabel(marks[vote.vote])
            mark.setFixedWidth(14)
            mark.setStyleSheet(f"color: {colors[vote.vote]}; font-weight: 700;")
            text = QVBoxLayout()
            text.setSpacing(0)
            name = QLabel(vote.rule)
            name.setStyleSheet("font-weight: 600;")
            detail = QLabel(vote.detail)
            detail.setObjectName("Muted")
            detail.setWordWrap(True)
            text.addWidget(name)
            text.addWidget(detail)
            h.addWidget(mark, 0, Qt.AlignmentFlag.AlignTop)
            h.addLayout(text, 1)
            self._rows.addWidget(row)
        self._rows.addStretch(1)
