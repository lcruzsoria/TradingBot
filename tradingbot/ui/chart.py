"""Gráfico de velas rápido (pyqtgraph) con eje X por índice y niveles de referencia."""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPen, QPolygonF

from ..bias.rules import fmt_price
from . import theme
from .fmt import fecha_hora

MAX_CANDLES_DRAWN = 2500   # por encima de esto se dibuja una línea de cierres


class TimeAxis(pg.AxisItem):
    """Eje X por índice de vela: muestra la hora del servidor del broker."""

    def __init__(self, **kw):
        super().__init__(orientation="bottom", **kw)
        self._ts: np.ndarray = np.empty(0, dtype=np.int64)

    def set_times(self, ts: np.ndarray) -> None:
        self._ts = ts

    def tickStrings(self, values, scale, spacing):
        out = []
        n = len(self._ts)
        for v in values:
            i = int(round(v))
            if 0 <= i < n:
                dt = datetime.fromtimestamp(int(self._ts[i]), tz=timezone.utc)
                out.append(fecha_hora(dt))
            else:
                out.append("")
        return out


class CandlestickItem(pg.GraphicsObject):
    def __init__(self) -> None:
        super().__init__()
        empty = np.empty(0)
        self._o = self._h = self._l = self._c = empty
        self._rect = QRectF()
        self.set_colors()

    def set_colors(self) -> None:
        self._up_fill, self._up_line = QColor(theme.CANDLE_UP_FILL), QColor(theme.CANDLE_UP_LINE)
        self._down_fill, self._down_line = QColor(theme.CANDLE_DOWN_FILL), QColor(theme.CANDLE_DOWN_LINE)
        self.update()

    def set_data(self, o, h, l, c) -> None:
        self.prepareGeometryChange()
        self._o, self._h, self._l, self._c = o, h, l, c
        if len(o):
            lo, hi = float(l.min()), float(h.max())
            self._rect = QRectF(-1, lo, len(o) + 2, max(hi - lo, 1e-9))
        else:
            self._rect = QRectF()
        self.informViewBoundsChanged()
        self.update()

    def boundingRect(self) -> QRectF:
        return self._rect

    def dataBounds(self, ax, frac=1.0, orthoRange=None):
        n = len(self._o)
        if n == 0:
            return (None, None)
        if ax == 0:
            return (0, n)
        if orthoRange is not None:
            i0 = max(0, int(orthoRange[0]) - 1)
            i1 = min(n, int(orthoRange[1]) + 2)
            if i1 <= i0:
                return (None, None)
            return (float(self._l[i0:i1].min()), float(self._h[i0:i1].max()))
        return (float(self._l.min()), float(self._h.max()))

    def paint(self, p, *args) -> None:
        vb = self.getViewBox()
        n = len(self._o)
        if vb is None or n == 0:
            return
        (x0, x1), _ = vb.viewRange()
        i0, i1 = max(0, int(x0) - 1), min(n, int(x1) + 2)
        count = i1 - i0
        if count <= 0:
            return

        if count > MAX_CANDLES_DRAWN:
            step = count // MAX_CANDLES_DRAWN + 1
            idx = np.arange(i0, i1, step)
            poly = QPolygonF([QPointF(float(i), float(self._c[i])) for i in idx])
            pen = QPen(QColor(theme.ACCENT)); pen.setCosmetic(True); pen.setWidthF(1.2)
            p.setPen(pen)
            p.drawPolyline(poly)
            return

        up_pen = QPen(self._up_line); up_pen.setCosmetic(True); up_pen.setWidthF(1.2)
        down_pen = QPen(self._down_line); down_pen.setCosmetic(True); down_pen.setWidthF(1.2)
        body_w = 0.34
        for i in range(i0, i1):
            o, h, l, c = self._o[i], self._h[i], self._l[i], self._c[i]
            up = c >= o
            p.setPen(up_pen if up else down_pen)
            p.setBrush(self._up_fill if up else self._down_fill)
            p.drawLine(QPointF(i, l), QPointF(i, h))
            top, bottom = (c, o) if up else (o, c)
            if top - bottom <= 0:
                p.drawLine(QPointF(i - body_w, o), QPointF(i + body_w, o))
            else:
                p.drawRect(QRectF(i - body_w, bottom, 2 * body_w, top - bottom))


class ChartView(pg.PlotWidget):
    def __init__(self) -> None:
        self.time_axis = TimeAxis()
        super().__init__(axisItems={"bottom": self.time_axis}, background=theme.CHART_BG)
        pi = self.getPlotItem()
        pi.hideAxis("left")
        pi.showAxis("right")
        self._style_axes()
        pi.setMenuEnabled(False)
        vb = pi.getViewBox()
        vb.setMouseEnabled(x=True, y=False)
        vb.enableAutoRange(axis="y")
        vb.setAutoVisible(y=True)
        self.item = CandlestickItem()
        pi.addItem(self.item)
        self._lines: list[pg.InfiniteLine] = []
        self._last_line: pg.InfiniteLine | None = None
        self._last_value: float | None = None
        self._levels: dict[str, float] = {}
        self._n = 0

    def _style_axes(self) -> None:
        pi = self.getPlotItem()
        explicit = bool(theme.CHART_GRID)
        for name in ("right", "bottom"):
            ax = pi.getAxis(name)
            ax.setPen(pg.mkPen(theme.CHART_GRID if explicit else theme.BORDER))
            ax.setTextPen(pg.mkPen(theme.CHART_TEXT))
        # Con color de rejilla propio: se pinta tal cual (intensidad completa) y también en vertical.
        pi.showGrid(x=explicit, y=True, alpha=1.0 if explicit else 0.07)

    def apply_theme(self) -> None:
        """Repinta con la paleta activa (fondo, ejes, velas, niveles y último precio)."""
        self.setBackground(theme.CHART_BG)
        self._style_axes()
        self.item.set_colors()
        if self._last_value is not None:
            self.set_last_price(self._last_value)
        if self._levels:
            self.set_levels(dict(self._levels))
        self.update()

    def set_candles(self, df, view_bars: int = 220) -> None:
        o, h = df["open"].to_numpy(), df["high"].to_numpy()
        l, c = df["low"].to_numpy(), df["close"].to_numpy()
        self._n = len(df)
        self.time_axis.set_times(df["ts"].to_numpy())
        self.item.set_data(o, h, l, c)
        self.clear_levels()
        self._levels = {}
        self.set_last_price(float(c[-1]))
        vb = self.getPlotItem().getViewBox()
        vb.setLimits(xMin=-5, xMax=self._n + 60)
        vb.setXRange(max(0, self._n - view_bars), self._n + 8, padding=0)
        vb.enableAutoRange(axis="y")

    def set_last_price(self, value: float) -> None:
        """Línea punteada y etiqueta con el último precio, como en los gráficos de MT5."""
        self._last_value = value
        if self._last_line is not None:
            self.getPlotItem().removeItem(self._last_line)
        self._last_line = pg.InfiniteLine(
            pos=value, angle=0, movable=False,
            pen=pg.mkPen(theme.MUTED, width=1, style=Qt.PenStyle.DotLine),
            label=fmt_price(value),
            labelOpts={"position": 1.0, "color": theme.BG, "fill": theme.TEXT, "movable": False,
                       "anchors": [(1, 0.5), (1, 0.5)]})
        self.getPlotItem().addItem(self._last_line, ignoreBounds=True)

    def set_levels(self, levels: dict[str, float]) -> None:
        self.clear_levels()
        self._levels = dict(levels)
        palette = {"Máx. previo": theme.LEVEL_HIGH, "Mín. previo": theme.LEVEL_LOW, "Apertura": theme.LEVEL_OPEN}
        for i, (name, value) in enumerate(levels.items()):
            color = palette.get(name, theme.NEUTRAL)
            pen = pg.mkPen(color, width=1, style=Qt.PenStyle.DashLine)
            line = pg.InfiniteLine(pos=value, angle=0, pen=pen, movable=False,
                                   label=f"{name} {fmt_price(value)}",
                                   labelOpts={"position": 0.01 + 0.19 * i, "color": theme.LEVEL_LABEL or color, "movable": False,   # escalonadas para no pisarse
                                           "anchors": [(0, 1), (0, 1)]})
            self.getPlotItem().addItem(line, ignoreBounds=True)
            self._lines.append(line)

    def clear_levels(self) -> None:
        for line in self._lines:
            self.getPlotItem().removeItem(line)
        self._lines.clear()
