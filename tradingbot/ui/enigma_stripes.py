"""Franjas de la skill Enigma369 bajo el gráfico de precio: una fila por capa de cuartos, con su código y su número."""
from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPen
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from . import theme
from .bias_hist import PRICE_AXIS_WIDTH

ROW_HEIGHT = 24


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
        self._layers: tuple = ()
        self._item = StripeItem()
        pi.addItem(self._item, ignoreBounds=True)
        pi.getViewBox().sigRangeChanged.connect(lambda *_: (self._item.prepareGeometryChange(), self._item.update()))
        self.style()

    def style(self) -> None:
        self.setBackground(theme.CHART_BG)
        ax = self.getPlotItem().getAxis("right")
        ax.setPen(pg.mkPen(theme.CHART_GRID or theme.BORDER))
        ax.setTextPen(pg.mkPen(theme.CHART_TEXT))

    def link_to(self, chart) -> None:
        """El rango de velas visible es el del gráfico de precio. Se copia a mano (sin XLink) en cada cambio de rango y de tamaño:
        el XLink de pyqtgraph deja el rango desplazado unas velas si el ancho de las franjas cambia después de enlazarlas."""
        self._chart_vb = chart.getPlotItem().getViewBox()
        self._chart_vb.sigRangeChanged.connect(lambda *_: self.sync_x())
        self._chart_vb.sigResized.connect(lambda *_: self.sync_x())
        self.sync_x()

    def sync_x(self) -> None:
        vb = getattr(self, "_chart_vb", None)
        if vb is not None:
            self.getPlotItem().getViewBox().setXRange(*vb.viewRange()[0], padding=0)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.sync_x()

    def set_rows(self, layers: tuple, rows: list[list[dict]], names: dict[str, str], opacity: float = 1.0) -> None:
        pi = self.getPlotItem()
        self._layers = tuple(layers)
        count = len(layers)
        self.setFixedHeight(ROW_HEIGHT * count + 6)
        self._item.set_data(rows, opacity)
        tick_rows = [(i + 0.5, names.get(layer, layer)) for i, layer in enumerate(layers)]
        pi.getAxis("right").setTicks([tick_rows])
        pi.getViewBox().setYRange(0, count, padding=0)
        self.sync_x()

    @property
    def segment_count(self) -> int:
        return self._item.segment_count


class StripeItem(pg.GraphicsObject):
    """Todas las franjas en un solo objeto: pinta solo las visibles (con miles de velas, un objeto por franja y texto es lento).

    Cada texto se elige al pintar: el completo, y si no cabe en su franja con el zoom actual, la referencia con número o solo el número."""

    def __init__(self) -> None:
        super().__init__()
        self._rows: list[list[dict]] = []
        self._opacity = 1.0

    def set_data(self, rows: list[list[dict]], opacity: float) -> None:
        self._rows = [list(r) for r in rows]
        self._opacity = opacity
        self.prepareGeometryChange()
        self.update()

    @property
    def segment_count(self) -> int:
        return sum(len(r) for r in self._rows)

    def boundingRect(self) -> QRectF:
        vb = self.getViewBox()
        return vb.viewRect() if vb is not None else QRectF()

    def paint(self, p, *args) -> None:
        vb = self.getViewBox()
        if vb is None or not self._rows:
            return
        (vx0, vx1), _ = vb.viewRange()
        transform = p.transform()
        edge = QPen(QColor(theme.CHART_BG), 1)
        edge.setCosmetic(True)
        texts = []
        for y, segs in enumerate(self._rows):
            for s in segs:
                if s["x1"] < vx0 or s["x0"] > vx1:
                    continue
                color = QColor(s["color"])
                color.setAlphaF(self._opacity)
                p.setPen(edge)
                p.setBrush(color)
                p.drawRect(QRectF(s["x0"], y + 0.06, s["x1"] - s["x0"], 0.88))
                texts.append((s, y))
        p.resetTransform()                                     # los textos, en píxeles
        font = p.font()
        font.setPointSize(8)
        font.setWeight(QFont.Weight.DemiBold)
        p.setFont(font)
        p.setPen(QColor("#2B2B2B"))
        metrics = p.fontMetrics()
        for s, y in texts:
            left, right = max(s["x0"], vx0), min(s["x1"], vx1)
            room = transform.map(QPointF(right, 0)).x() - transform.map(QPointF(left, 0)).x() - 8
            shown = next((t for t in dict.fromkeys(filter(None, (s["text"], s.get("ref", s["text"]), s.get("num", "")))) if metrics.horizontalAdvance(t) <= room), None)
            if shown is None:
                continue
            c = transform.map(QPointF((left + right) / 2, y + 0.5))
            p.drawText(QPointF(c.x() - metrics.horizontalAdvance(shown) / 2, c.y() + metrics.ascent() / 2 - 1), shown)


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
        self.rows = StripeRows()
        lay.addWidget(self.rows)
        lay.addLayout(head)                          # los selectores van debajo de las franjas

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
