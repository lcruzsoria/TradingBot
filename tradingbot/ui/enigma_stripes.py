"""Franjas de la skill Enigma369 bajo el gráfico de precio: una fila por capa de cuartos, con su código y su número."""
from __future__ import annotations

import html

import pyqtgraph as pg
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QButtonGroup, QGraphicsRectItem, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from . import theme
from .bias_hist import PRICE_AXIS_WIDTH

ROW_HEIGHT = 24
MIN_LABEL_BARS = 3      # una franja más estrecha que esto no lleva texto


class StripeRows(pg.PlotWidget):
    """Una fila por capa, de la menor (arriba) a la mayor (abajo); el eje de tiempo sigue al del gráfico de precio."""

    def __init__(self) -> None:
        super().__init__(background=theme.CHART_BG)
        pi = self.getPlotItem()
        pi.hideAxis("left")
        pi.hideAxis("bottom")
        pi.showAxis("right")
        ax = pi.getAxis("right")
        ax.setWidth(PRICE_AXIS_WIDTH)
        pi.setMenuEnabled(False)
        pi.getViewBox().setMouseEnabled(x=False, y=False)
        self._items: list = []
        self._layers: tuple = ()
        self._labels: list[tuple] = []          # (texto, inicio y fin de su franja en velas, y)
        self.getPlotItem().getViewBox().sigRangeChanged.connect(lambda *_: self._fit_labels())
        self.style()

    def style(self) -> None:
        self.setBackground(theme.CHART_BG)
        ax = self.getPlotItem().getAxis("right")
        ax.setPen(pg.mkPen(theme.CHART_GRID or theme.BORDER))
        ax.setTextPen(pg.mkPen(theme.CHART_TEXT))

    def link_to(self, chart) -> None:
        self.getPlotItem().setXLink(chart.getPlotItem())

    def set_rows(self, layers: tuple, rows: list[list[dict]], names: dict[str, str], opacity: float = 1.0) -> None:
        pi = self.getPlotItem()
        for item in self._items:
            pi.removeItem(item)
        self._items.clear()
        self._labels.clear()
        self._layers = tuple(layers)
        count = len(layers)
        self.setFixedHeight(ROW_HEIGHT * count + 6)
        for i, segs in enumerate(rows):
            y = i                                    # la capa mayor abajo y la menor arriba
            for s in segs:
                color = QColor(s["color"])
                color.setAlphaF(opacity)
                box = QGraphicsRectItem(s["x0"], y + 0.06, s["x1"] - s["x0"], 0.88)
                box.setBrush(color)
                edge = QPen(QColor(theme.CHART_BG), 1)
                edge.setCosmetic(True)
                box.setPen(edge)
                pi.addItem(box, ignoreBounds=True)
                self._items.append(box)
                if s["x1"] - s["x0"] >= MIN_LABEL_BARS:
                    text = pg.TextItem(anchor=(0.5, 0.5))
                    text.setHtml(f'<span style="font-size:8pt; color:#2B2B2B; font-weight:600">{html.escape(s["text"])}</span>')
                    text.setPos((s["x0"] + s["x1"]) / 2, y + 0.5)
                    pi.addItem(text, ignoreBounds=True)
                    self._items.append(text)
                    self._labels.append((text, s["x0"], s["x1"], y + 0.5))
        tick_rows = [(i + 0.5, names.get(layer, layer)) for i, layer in enumerate(layers)]
        pi.getAxis("right").setTicks([tick_rows])
        pi.getViewBox().setYRange(0, count, padding=0)
        self._fit_labels()

    def _fit_labels(self) -> None:
        """Un texto solo se ve si cabe en su franja con el zoom actual (si no, se solapa con el de al lado)."""
        vb = self.getPlotItem().getViewBox()
        x0, x1 = vb.viewRange()[0]
        per_bar = vb.width() / max(x1 - x0, 1e-9)
        for text, left, right, y in self._labels:
            left, right = max(left, x0), min(right, x1)             # solo la parte visible de la franja
            text.setVisible(right > left and (right - left) * per_bar >= text.boundingRect().width() + 8)
            text.setPos((left + right) / 2, y)

    @property
    def segment_count(self) -> int:
        return sum(isinstance(i, QGraphicsRectItem) for i in self._items)


class EnigmaStripes(QWidget):
    """Selector de ciclos (Semana → Cuarto con velas de 5m, Día → Micro con velas de 1m) y las cuatro franjas."""

    mode_selected = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        head = QHBoxLayout()
        head.setSpacing(6)
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.buttons: dict[str, QPushButton] = {}
        for mode, text, tip in (("semana", "Semana → Cuarto", "Cuatro ciclos: semana del mes, día, sesión y cuarto de 90 min. Velas de 5m."),
                                ("dia", "Día → Micro", "Cuatro ciclos: día, sesión, cuarto de 90 min y micro de 22,5 min. Velas de 1m.")):
            btn = QPushButton(text)
            btn.setProperty("chip", "true")
            btn.setCheckable(True)
            btn.setToolTip(tip)
            self.group.addButton(btn)
            self.buttons[mode] = btn
            head.addWidget(btn)
            btn.clicked.connect(lambda _c=False, m=mode: self.mode_selected.emit(m))
        self.info = QLabel("")
        self.info.setObjectName("Tiny")
        self.info.setWordWrap(True)
        head.addWidget(self.info, 1)
        lay.addLayout(head)
        self.rows = StripeRows()
        lay.addWidget(self.rows)

    def link_to(self, chart) -> None:
        self.rows.link_to(chart)

    def style(self) -> None:
        self.rows.style()

    def set_mode(self, mode: str) -> None:
        if mode in self.buttons:
            self.buttons[mode].setChecked(True)

    def set_data(self, p: dict, names: dict[str, str]) -> None:
        self.set_mode(p.get("mode", "semana"))
        if not p.get("available"):
            self.rows.set_rows((), [], names)
            self.info.setText(p.get("reason", ""))
            return
        self.rows.set_rows(p["layers"], p["rows"], names, p.get("stripe_opacity", 1.0))
        now = " · ".join(f'{names.get(z["layer"], z["layer"])} {z["text"].replace(" · ", " (") + ")" if z["number"] else z["text"]}' for z in p["now"])
        runs = p["alignments_now"]
        self.info.setText(("Alineado: " + ", ".join(r["label"] for r in runs) + "   |   " if runs else "") + "Última vela: " + now)
