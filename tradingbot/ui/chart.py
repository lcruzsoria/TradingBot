"""Gráfico de velas rápido (pyqtgraph) con eje X por índice (hora de Nueva York) y ejes redimensionables."""
from __future__ import annotations

import math
from datetime import datetime, timezone

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsRectItem

from ..clock import NY_CLOSE_SERVER_AHEAD_HOURS
from ..skills.bias.rules import fmt_price
from . import theme
from .fmt import fecha_hora

MAX_CANDLES_DRAWN = 2500   # por encima de esto se dibuja una línea de cierres
LEVEL_LABELS = {"tdo": "TDO", "midnight": "Midnight", "pdh": "PDH", "pdl": "PDL"}
LEVEL_GROUP = {"tdo": "tdo", "midnight": "midnight", "pdh": "pdhl", "pdl": "pdhl"}   # botón que muestra cada nivel
LEVEL_STYLE = {"tdo": Qt.PenStyle.DashLine, "midnight": Qt.PenStyle.DotLine,
               "pdh": Qt.PenStyle.DashLine, "pdl": Qt.PenStyle.DashLine}


class DaySeparators(pg.GraphicsObject):
    """Líneas verticales punteadas al empezar cada día y su nombre abajo, centrado entre su separador y el siguiente.

    Solo pinta lo visible, así sirve para todo el histórico.
    """

    def __init__(self) -> None:
        super().__init__()
        self._x = np.empty(0)                           # separadores (inicio de cada día salvo el primero cargado)
        self._centers = np.empty(0)                     # centro de cada día, donde va su nombre
        self._labels: list[str] = []
        self._color = QColor("#787B86")

    def set_data(self, days: list, color: str) -> None:
        """days: tradingbot.skills.levels.daylevels.Day (bordes x0 / x1 y nombre)."""
        self._x = np.array([d.x0 for d in days[1:]], dtype=float)
        self._centers = np.array([d.center for d in days], dtype=float)
        self._labels = [d.label for d in days]
        self._color = QColor(color)
        self.update()

    def boundingRect(self) -> QRectF:
        vb = self.getViewBox()
        return vb.viewRect() if vb is not None else QRectF()

    def paint(self, p, *args) -> None:
        vb = self.getViewBox()
        if vb is None or not len(self._centers):
            return
        (x0, x1), (y0, y1) = vb.viewRange()
        i0, i1 = np.searchsorted(self._x, [x0, x1])
        c0, c1 = np.searchsorted(self._centers, [x0, x1])
        if c1 - c0 > 400:                               # muy alejado: los separadores no aportan nada
            return
        pen = QPen(self._color)
        pen.setCosmetic(True)
        pen.setStyle(Qt.PenStyle.DotLine)
        p.setPen(pen)
        for x in self._x[i0:i1]:
            p.drawLine(QPointF(x, y0), QPointF(x, y1))
        transform = p.transform()                       # el texto, en píxeles (sin estirarse con el zoom)
        p.resetTransform()
        metrics = p.fontMetrics()
        for cx, label in zip(self._centers[c0:c1], self._labels[c0:c1]):
            pt = transform.map(QPointF(cx, y0))
            p.drawText(QPointF(pt.x() - metrics.horizontalAdvance(label) / 2, pt.y() - 6), label)


class ScaleAxis(pg.AxisItem):
    """Eje que se redimensiona al arrastrarlo, como en TradingView. Doble clic: vuelve a la escala automática.

    - Eje de precio: arrastrar hacia abajo comprime el precio, hacia arriba lo estira.
    - Eje de tiempo: arrastrar a la izquierda muestra más velas, a la derecha menos (anclado a la derecha).
    """

    SENSITIVITY = 0.01      # factor de escala por píxel arrastrado

    def __init__(self, orientation: str, **kw):
        super().__init__(orientation=orientation, **kw)
        self.chart: "ChartView | None" = None
        vertical = orientation in ("left", "right")
        self.setCursor(Qt.CursorShape.SizeVerCursor if vertical else Qt.CursorShape.SizeHorCursor)
        self.setToolTip("Arrastra para redimensionar el eje. Doble clic: escala automática.")

    @property
    def vertical(self) -> bool:
        return self.orientation in ("left", "right")

    def mouseDragEvent(self, event):
        vb = self.linkedView()
        if self.chart is None or vb is None or event.button() != Qt.MouseButton.LeftButton:
            return super().mouseDragEvent(event)
        if vb.sceneBoundingRect().contains(event.buttonDownScenePos()):
            event.ignore()                              # el arrastre empezó dentro del gráfico, no en el eje
            return
        event.accept()
        delta = event.pos() - event.lastPos()
        if self.vertical:
            self.chart.scale_price(math.exp(delta.y() * self.SENSITIVITY))
        else:
            self.chart.scale_time(math.exp(-delta.x() * self.SENSITIVITY))

    def mouseClickEvent(self, event):
        if self.chart is not None and event.double() and event.button() == Qt.MouseButton.LeftButton:
            event.accept()
            if self.vertical:
                self.chart.reset_price_scale()
            else:
                self.chart.reset_time_scale()
            return
        return super().mouseClickEvent(event)


class TimeAxis(ScaleAxis):
    """Eje X por índice de vela: muestra la hora de Nueva York.

    Las velas llegan en hora del servidor del broker; `ny_shift` es cuánto va el servidor por delante de Nueva York
    (en Vantage, 7 h). Hasta que Quotes mide el desfase real se usa ese valor estimado.
    """

    def __init__(self, **kw):
        super().__init__("bottom", **kw)
        self._ts: np.ndarray = np.empty(0, dtype=np.int64)
        self.ny_shift = NY_CLOSE_SERVER_AHEAD_HOURS * 3600

    def set_times(self, ts: np.ndarray) -> None:
        self._ts = ts

    def set_ny_shift(self, seconds: int) -> None:
        if seconds != self.ny_shift:
            self.ny_shift = seconds
            self.picture = None                         # fuerza a redibujar las etiquetas
            self.update()

    def tickStrings(self, values, scale, spacing):
        out = []
        n = len(self._ts)
        for v in values:
            i = int(round(v))
            if 0 <= i < n:
                dt = datetime.fromtimestamp(int(self._ts[i]) - self.ny_shift, tz=timezone.utc)
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
    VIEW_BARS = 220          # velas visibles al cargar (y al hacer doble clic en el eje de tiempo)
    MIN_BARS = 10            # zoom máximo del eje de tiempo

    def __init__(self) -> None:
        self.time_axis = TimeAxis()
        self.price_axis = ScaleAxis("right")
        super().__init__(axisItems={"bottom": self.time_axis, "right": self.price_axis}, background=theme.CHART_BG)
        self.time_axis.chart = self.price_axis.chart = self
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
        self._tbr_items: list = []
        self._tbr_sessions: list = []
        self._tbr_opacity = 0.25
        self._tbr_visible = False
        self._day_items: list = []
        self._day_lines: list = []
        self._day_colors: dict[str, str] = {}
        self._level_groups: set[str] = set()
        self.separators = DaySeparators()
        self.separators.setZValue(-20)
        pi.addItem(self.separators, ignoreBounds=True)
        vb.sigRangeChanged.connect(lambda *_: (self.separators.prepareGeometryChange(), self.separators.update()))

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

    def set_candles(self, df, view_bars: int | None = None) -> None:
        o, h = df["open"].to_numpy(), df["high"].to_numpy()
        l, c = df["low"].to_numpy(), df["close"].to_numpy()
        self._n = len(df)
        self.time_axis.set_times(df["ts"].to_numpy())
        self.item.set_data(o, h, l, c)
        self.clear_levels()
        self._levels = {}
        self.set_tbr([])                    # las zonas van por índice de vela: se recalculan con las velas nuevas
        self.set_day_levels([], [], self._day_colors)
        self.set_last_price(float(c[-1]))
        vb = self.getPlotItem().getViewBox()
        vb.setLimits(xMin=-5, xMax=self._n + 60)
        vb.setXRange(max(0, self._n - (view_bars or self.VIEW_BARS)), self._n + 8, padding=0)
        self.reset_price_scale()

    # -- escala de los ejes (arrastrando sobre ellos) -------------------------------------------------
    @property
    def price_auto(self) -> bool:
        """True mientras el eje de precio se ajusta solo a las velas visibles."""
        return bool(self.getPlotItem().getViewBox().autoRangeEnabled()[1])

    def set_ny_shift(self, seconds: int) -> None:
        """Cuánto va el servidor del broker por delante de Nueva York (para las etiquetas del eje de tiempo)."""
        self.time_axis.set_ny_shift(seconds)

    def scale_price(self, factor: float) -> None:
        """Estira (factor < 1) o comprime (factor > 1) el precio alrededor del centro; pasa a escala manual."""
        vb = self.getPlotItem().getViewBox()
        y0, y1 = vb.viewRange()[1]
        center, half = (y0 + y1) / 2, (y1 - y0) / 2 * factor
        vb.disableAutoRange(axis=vb.YAxis)
        vb.setMouseEnabled(x=True, y=True)              # con escala manual, también se puede mover en vertical
        vb.setYRange(center - half, center + half, padding=0)

    def reset_price_scale(self) -> None:
        vb = self.getPlotItem().getViewBox()
        vb.setMouseEnabled(x=True, y=False)
        vb.setAutoVisible(y=True)
        vb.enableAutoRange(axis="y")

    def scale_time(self, factor: float) -> None:
        """Más velas (factor > 1) o menos (factor < 1), manteniendo fijo el borde derecho."""
        vb = self.getPlotItem().getViewBox()
        x0, x1 = vb.viewRange()[0]
        width = min(max((x1 - x0) * factor, self.MIN_BARS), self._n + 65)
        vb.setXRange(x1 - width, x1, padding=0)

    def reset_time_scale(self) -> None:
        vb = self.getPlotItem().getViewBox()
        vb.setXRange(max(0, self._n - self.VIEW_BARS), self._n + 8, padding=0)
        self.reset_price_scale()

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

    # -- TBR: zonas horarias y sus niveles ---------------------------------------------------------
    def set_tbr(self, sessions: list, opacity: float | None = None) -> None:
        """Zonas TBR calculadas (tradingbot.skills.tbr.zones.Session); solo se ven con show_tbr(True)."""
        self._tbr_sessions = list(sessions)
        if opacity is not None:
            self._tbr_opacity = opacity
        self._draw_tbr()

    def show_tbr(self, visible: bool) -> None:
        self._tbr_visible = visible
        self._draw_tbr()

    def _draw_tbr(self) -> None:
        pi = self.getPlotItem()
        for item in self._tbr_items:
            pi.removeItem(item)
        self._tbr_items.clear()
        if not self._tbr_visible or not self._tbr_sessions:
            return
        lines: dict[tuple[str, str], tuple[list, list]] = {}
        for s in self._tbr_sessions:
            fill = QColor(s.zone.color)
            fill.setAlphaF(self._tbr_opacity)
            # caja de la zona: de su inicio a su final y de su Low a su High
            box = QGraphicsRectItem(QRectF(s.x0, s.low, s.x1 - s.x0, max(s.high - s.low, 1e-9)))
            box.setBrush(fill)
            box.setPen(QPen(Qt.PenStyle.NoPen))
            box.setZValue(-10)                          # detrás de las velas
            pi.addItem(box, ignoreBounds=True)
            self._tbr_items.append(box)
            for level in s.levels:
                xs, ys = lines.setdefault((s.zone.color, level.kind), ([], []))
                xs += [level.x0, level.x1]
                ys += [level.price, level.price]
        for (color, kind), (xs, ys) in lines.items():
            pen_color = QColor(color)
            pen_color.setAlphaF(0.85)
            style = Qt.PenStyle.DotLine if kind == "mid" else Qt.PenStyle.SolidLine   # 50 %: punteada
            curve = pg.PlotCurveItem(x=np.array(xs), y=np.array(ys), connect="pairs",
                                     pen=pg.mkPen(pen_color, width=1, style=style))
            curve.setZValue(-5)
            pi.addItem(curve, ignoreBounds=True)        # no cambian la escala del precio
            self._tbr_items.append(curve)

    @property
    def tbr_item_count(self) -> int:
        return len(self._tbr_items)

    # -- niveles del día (TDO, Midnight, PDH / PDL) y separadores de día ------------------------------
    def set_day_levels(self, lines: list, days: list, colors: dict[str, str]) -> None:
        self._day_lines, self._day_colors = list(lines), dict(colors)
        self.separators.set_data(days, colors.get("separator", "#787B86"))
        self._draw_day_levels()

    def show_level(self, group: str, visible: bool) -> None:
        """group: "tdo", "midnight" o "pdhl" (un botón cada uno)."""
        if visible:
            self._level_groups.add(group)
        else:
            self._level_groups.discard(group)
        self._draw_day_levels()

    def _draw_day_levels(self) -> None:
        pi = self.getPlotItem()
        for item in self._day_items:
            pi.removeItem(item)
        self._day_items.clear()
        segments: dict[str, tuple[list, list]] = {}
        for line in self._day_lines:
            if LEVEL_GROUP[line.kind] not in self._level_groups:
                continue
            xs, ys = segments.setdefault(line.kind, ([], []))
            xs += [line.x0, line.x1]
            ys += [line.price, line.price]
            color = self._day_colors.get(LEVEL_GROUP[line.kind], theme.MUTED)
            label = pg.TextItem(LEVEL_LABELS[line.kind], color=color, anchor=(0, 0.5))
            label.setPos(line.x1, line.price)
            pi.addItem(label, ignoreBounds=True)
            self._day_items.append(label)
        for kind, (xs, ys) in segments.items():
            color = self._day_colors.get(LEVEL_GROUP[kind], theme.MUTED)
            curve = pg.PlotCurveItem(x=np.array(xs), y=np.array(ys), connect="pairs",
                                     pen=pg.mkPen(color, width=1, style=LEVEL_STYLE[kind]))
            curve.setZValue(-4)
            pi.addItem(curve, ignoreBounds=True)
            self._day_items.append(curve)

    @property
    def day_item_count(self) -> int:
        return len(self._day_items)
