"""Histograma del sesgo bajo el gráfico de precio (como el volumen de TradingView): una barra por vela con su puntuación."""
from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from . import theme

MAX_BARS = 4000          # solo se dibujan las últimas velas
PRICE_AXIS_WIDTH = 74    # igual que el eje de precio, para que las velas queden alineadas con las barras


class BiasHistogram(pg.PlotWidget):
    """Puntuación del Bias en cada vela: verde con sesgo alcista, rojo con sesgo bajista y gris sin sesgo."""

    def __init__(self) -> None:
        super().__init__(background=theme.CHART_BG)
        pi = self.getPlotItem()
        pi.hideAxis("left")
        pi.hideAxis("bottom")
        pi.showAxis("right")
        pi.getAxis("right").setWidth(PRICE_AXIS_WIDTH)
        pi.setMenuEnabled(False)
        pi.getViewBox().setMouseEnabled(x=False, y=False)
        self.setFixedHeight(110)
        self._scores = np.zeros(0)
        self._min = 1.0
        self._items: list = []
        self.style()

    def style(self) -> None:
        self.setBackground(theme.CHART_BG)
        ax = self.getPlotItem().getAxis("right")
        ax.setPen(pg.mkPen(theme.CHART_GRID or theme.BORDER))
        ax.setTextPen(pg.mkPen(theme.CHART_TEXT))
        self._draw()

    def link_to(self, chart) -> None:
        """El eje de tiempo sigue al del gráfico de precio."""
        self.getPlotItem().setXLink(chart.getPlotItem())

    def set_scores(self, scores, min_score: float) -> None:
        self._scores, self._min = np.asarray(scores, dtype=float), float(min_score)
        self._draw()

    def _draw(self) -> None:
        pi = self.getPlotItem()
        for item in self._items:
            pi.removeItem(item)
        self._items.clear()
        scores = self._scores
        if not len(scores):
            return
        first = max(0, len(scores) - MAX_BARS)
        x = np.arange(first, len(scores), dtype=float)
        y = scores[first:]
        bull, bear, flat = QColor(theme.BULL), QColor(theme.BEAR), QColor(theme.MUTED)
        for color in (bull, bear, flat):
            color.setAlphaF(0.85)
        brushes = [bull if v >= self._min else bear if v <= -self._min else flat for v in y]
        bars = pg.BarGraphItem(x=x, height=y, width=0.8, brushes=brushes, pens=[pg.mkPen(None)] * len(y))
        pi.addItem(bars)
        self._items.append(bars)
        for level, style in ((0.0, Qt.PenStyle.SolidLine), (self._min, Qt.PenStyle.DashLine), (-self._min, Qt.PenStyle.DashLine)):
            line = pg.InfiniteLine(pos=level, angle=0, pen=pg.mkPen(theme.MUTED, width=1, style=style))
            line.setZValue(-5)
            pi.addItem(line, ignoreBounds=True)
            self._items.append(line)
        top = max(float(np.max(np.abs(y))), self._min) * 1.15
        pi.getViewBox().setYRange(-top, top, padding=0)

    @property
    def bar_count(self) -> int:
        return min(len(self._scores), MAX_BARS)
