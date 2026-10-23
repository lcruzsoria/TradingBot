"""Gráfico de velas rápido (pyqtgraph) con eje X por índice (hora de Nueva York) y ejes redimensionables."""
from __future__ import annotations

import html
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
from .fmt import DIAS, fecha_hora

MAX_CANDLES_DRAWN = 2500   # por encima de esto se dibuja una línea de cierres
NO_GO_OPACITY = 0.5        # fibos y posiciones de las entradas que Cortex no opera (NO GO)
NO_GO_PILL_OPACITY = 0.7   # su etiqueta, algo menos difuminada para que se lea
LEVEL_LABELS = {"tdo": "TDO", "midnight": "Midnight", "pdh": "PDH", "pdl": "PDL"}
LEVEL_GROUP = {"tdo": "tdo", "midnight": "midnight", "pdh": "pdhl", "pdl": "pdhl"}   # botón que muestra cada nivel
LEVEL_STYLE = {"tdo": Qt.PenStyle.DashLine, "midnight": Qt.PenStyle.DotLine,
               "pdh": Qt.PenStyle.DashLine, "pdl": Qt.PenStyle.DashLine}


def _alpha(color: str, alpha: int) -> QColor:
    c = QColor(color)
    c.setAlpha(alpha)
    return c


def _verdict_color(pos: dict) -> str:
    """Punto de la píldora: verde si Cortex la opera (GO), rojo si no (NO GO), gris sin veredicto."""
    return {"GO": "#26A69A", "NO GO": "#EF5350"}.get(pos.get("decision"), theme.MUTED)


def _ratio(pos: dict) -> float:
    risk = abs(float(pos["entry"]) - float(pos["stop"]))
    return abs(float(pos["target"]) - float(pos["entry"])) / risk if risk > 0 else 0.0


BE_GRAY = "#9E9E9E"          # break even: gris neutro (en el texto, el borde de la píldora y el de la caja)

# Resultado de cada posición según su estado: siglas y color del borde de su píldora (None: borde normal).
RESULTS = {"objetivo": ("TP", "#26A69A"), "stop": ("SL", "#EF5350"), "be": ("BE", BE_GRAY),
           "tiempo": ("T", None), "abierta": ("…", None)}
RESULT_TEXT = {"TP": "#2ECC71"}    # letras del resultado con otro color que el borde: TP en un verde más vivo
BOX_BORDER = {"objetivo": "#26A69A", "be": BE_GRAY}     # borde de la caja de la posición: verde si fue TP, gris si fue BE


class PositionPill(pg.TextItem):
    """Etiqueta de una posición: barra y símbolo del veredicto de Cortex (✓ GO, ✕ NO GO), patrón y R, y al final el
    resultado (TP, SL, BE, T o … si sigue abierta). El borde va del color del resultado: verde TP, rojo SL, gris BE.

    Va en el stop (el nivel 1 del fibo), por fuera de la caja y algo separada: debajo en los largos, encima en los cortos."""

    def __init__(self, pos: dict) -> None:
        result, color = RESULTS.get(str(pos["state"]), (str(pos["state"]), None))
        outside = -PILL_GAP if pos["direction"] == "long" else 1 + PILL_GAP
        super().__init__(anchor=(0, outside), fill=pg.mkBrush(_alpha(theme.PANEL, 225)),
                         border=pg.mkPen(color, width=1.5) if color else pg.mkPen(theme.BORDER))
        decision = pos.get("decision")
        self._bar = QColor(_verdict_color(pos)) if decision else None
        symbol = {"GO": "✓", "NO GO": "✕"}.get(decision, "")
        self.result = result
        self.setHtml(f'<span style="font-size:9pt">&nbsp;&nbsp;<b style="color:{_verdict_color(pos)}">{symbol}</b>&nbsp;'
                     f'<span style="color:{theme.TEXT}">{html.escape(pos["label"])} {_ratio(pos):.1f}R</span>'
                     f'&nbsp;<span style="color:{theme.BORDER}">│</span>&nbsp;'
                     f'<b style="color:{RESULT_TEXT.get(result, color or theme.MUTED)}">{result}</b></span>')
        self.setZValue(8)

    def paint(self, p, *args) -> None:
        super().paint(p, *args)
        if self._bar is not None:                       # barra fina del veredicto en el borde izquierdo
            rect = self.textItem.mapRectToParent(self.textItem.boundingRect())
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(self._bar)
            p.drawRect(QRectF(rect.left(), rect.top(), 3, rect.height()))


PILL_GAP = 0.35            # separación de la píldora respecto al stop, en fracción de su alto


def _fib_color(name: str) -> str:
    """Color de cada nivel del fibo: el 0,5 (la entrada) en ámbar, el -0,5 (el objetivo) en rojo, el resto apagado."""
    return "#BA7517" if name == "0,5" else "#E24B4A" if name == "-0,5" else theme.MUTED


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

    def ny_time(self, i: int) -> datetime:
        return datetime.fromtimestamp(int(self._ts[i]) - self.ny_shift, tz=timezone.utc)

    def cursor_label(self, i: int) -> str:
        """Fecha y hora de Nueva York de la vela i con el día de la semana ("mar 06 oct 18:00"), para el cursor."""
        dt = self.ny_time(i)
        return f"{DIAS[dt.weekday()][:3]} {fecha_hora(dt)}"

    def tickStrings(self, values, scale, spacing):
        out = []
        n = len(self._ts)
        for v in values:
            i = int(round(v))
            out.append(fecha_hora(self.ny_time(i)) if 0 <= i < n else "")
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
        self._tbr_opacity = 0.12
        self._tbr_line_opacity = 0.6
        self._tbr_visible = False
        self._day_items: list = []
        self._day_lines: list = []
        self._day_colors: dict[str, str] = {}
        self._level_groups: set[str] = set()
        self._sma: tuple | None = None            # (valores, color, trazo) de la última SMA recibida
        self._sma_visible = False
        self._sma_item = None
        self._positions: list[dict] = []          # posiciones de los patrones: {x0, x1, entry, stop, target, label, state, direction}
        self._pos_visible = True
        self._pos_items: list = []
        self._pos_pills: list = []                # la píldora de cada posición, en el mismo orden que _positions
        self._fibs: list[dict] = []               # fibonacci de los patrones: {x0, x1, levels, label, state, direction}
        self._fib_visible = True
        self._fib_items: list = []
        self._hover: int | None = None            # posición bajo el ratón
        self._pinned: int | None = None           # posición con la ficha fijada por un clic
        self.separators = DaySeparators()
        self.separators.setZValue(-20)
        pi.addItem(self.separators, ignoreBounds=True)
        vb.sigRangeChanged.connect(lambda *_: (self.separators.prepareGeometryChange(), self.separators.update()))
        self._init_crosshair()
        self._card = pg.TextItem(anchor=(0, 0))         # ficha de detalle de una posición (al pasar o pulsar)
        self._card.setParentItem(vb)                    # en píxeles del gráfico, como la leyenda
        self._card.setZValue(31)
        self._card.hide()
        self.scene().sigMouseClicked.connect(self._chart_clicked)
        vb.sigRangeChanged.connect(lambda *_: (self._fit_pills(), self._update_card()))

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
        self._style_crosshair()
        if self._last_value is not None:
            self.set_last_price(self._last_value)
        if self._levels:
            self.set_levels(dict(self._levels))
        self._draw_positions()
        self.update()

    def set_candles(self, df, view_bars: int | None = None, keep_view: bool = False) -> None:
        """keep_view: recarga de las mismas velas; la vista se queda donde estaba (y sigue a las velas nuevas)."""
        vb = self.getPlotItem().getViewBox()
        old_n, (old_x0, old_x1) = self._n, vb.viewRange()[0]
        o, h = df["open"].to_numpy(), df["high"].to_numpy()
        l, c = df["low"].to_numpy(), df["close"].to_numpy()
        self._n = len(df)
        self.time_axis.set_times(df["ts"].to_numpy())
        self.item.set_data(o, h, l, c)
        self.clear_levels()
        self._levels = {}
        self.set_tbr([])                    # las zonas van por índice de vela: se recalculan con las velas nuevas
        self.set_day_levels([], [], self._day_colors)
        self.set_sma(None)
        self.set_last_price(float(c[-1]))
        vb.setLimits(xMin=-5, xMax=self._n + 60)
        self._update_crosshair()
        if keep_view and old_n:
            shift = self._n - old_n
            vb.setXRange(old_x0 + shift, old_x1 + shift, padding=0)
            return
        vb.setXRange(max(0, self._n - (view_bars or self.VIEW_BARS)), self._n + 8, padding=0)
        self.reset_price_scale()

    # -- cursor en cruz (como en TradingView) -------------------------------------------------------
    def _init_crosshair(self) -> None:
        """Líneas que siguen al ratón (la vertical, pegada a la vela), su fecha en el eje de tiempo, su precio en el de
        precio y, arriba a la izquierda, los datos de la vela marcada (sin ratón: la última)."""
        pi = self.getPlotItem()
        vb = pi.getViewBox()
        self._mouse: QPointF | None = None             # posición del ratón en la escena (None: fuera del gráfico)
        self.cursor_index: int | None = None           # vela bajo el cursor
        self._cross_v = pg.InfiniteLine(angle=90, movable=False)
        self._cross_h = pg.InfiniteLine(angle=0, movable=False)
        for line in (self._cross_v, self._cross_h):
            line.setZValue(20)
            line.hide()
            pi.addItem(line, ignoreBounds=True)
        self._cross_time = pg.TextItem(anchor=(0.5, 0))
        self._cross_time.setParentItem(self.time_axis)  # sobre el eje, en píxeles
        self._cross_price = pg.TextItem(anchor=(0, 0.5))
        self._cross_price.setParentItem(self.price_axis)
        for tag in (self._cross_time, self._cross_price):
            tag.setZValue(20)
            tag.hide()
        self.legend = pg.TextItem(anchor=(0, 0))
        self.legend.setParentItem(vb)                   # fija en la esquina, no se mueve con las velas
        self.legend.setPos(6, 4)
        self.legend.setZValue(30)
        self._style_crosshair()
        self.scene().sigMouseMoved.connect(self._mouse_moved)
        vb.sigRangeChanged.connect(lambda *_: self._update_crosshair())

    def _style_crosshair(self) -> None:
        pen = pg.mkPen(theme.MUTED, width=1, style=Qt.PenStyle.DashLine)
        self._cross_v.setPen(pen)
        self._cross_h.setPen(pen)
        for tag in (self._cross_time, self._cross_price):
            tag.setColor(theme.BG)
            tag.fill = pg.mkBrush(theme.TEXT)
            tag.update()
        self._update_crosshair()

    def _mouse_moved(self, pos) -> None:
        vb = self.getPlotItem().getViewBox()
        self._mouse = QPointF(pos) if vb.sceneBoundingRect().contains(pos) else None
        self._update_crosshair()
        hover = self._position_at(pos)
        if hover != self._hover:
            self._hover = hover
            self._update_card()

    def leaveEvent(self, event) -> None:
        self._mouse = None
        self._update_crosshair()
        if self._hover is not None:
            self._hover = None
            self._update_card()
        super().leaveEvent(event)

    def _update_crosshair(self) -> None:
        vb = self.getPlotItem().getViewBox()
        parts = (self._cross_v, self._cross_h, self._cross_time, self._cross_price)
        if self._mouse is None or not self._n:
            self.cursor_index = None
            for part in parts:
                part.hide()
            self._update_legend(self._n - 1)
            return
        pt = vb.mapSceneToView(self._mouse)
        i = min(max(int(round(pt.x())), 0), self._n - 1)
        price = pt.y()
        self.cursor_index = i
        self._cross_v.setPos(i)
        self._cross_h.setPos(price)
        scene = vb.mapViewToScene(QPointF(i, price))
        self._cross_time.setText(self.time_axis.cursor_label(i))
        self._cross_time.setPos(self.time_axis.mapFromScene(scene).x(), 0)
        self._cross_price.setText(fmt_price(price))
        self._cross_price.setPos(0, self.price_axis.mapFromScene(scene).y())
        for part in parts:
            part.show()
        self._update_legend(i)

    def _update_legend(self, i: int) -> None:
        if not 0 <= i < self._n:
            self.legend.setHtml("")
            return
        it = self.item
        o, h, l, c = (float(a[i]) for a in (it._o, it._h, it._l, it._c))
        prev = float(it._c[i - 1]) if i else o
        change = c - prev
        pct = change / prev * 100 if prev else 0.0
        decimals = len(fmt_price(c).partition(".")[2])
        color = theme.BULL if c >= o else theme.BEAR
        muted = theme.CHART_TEXT or theme.MUTED

        def value(name: str, v: float) -> str:
            return f'<span style="color:{muted}">{name}</span>&nbsp;<span style="color:{color}">{fmt_price(v)}</span>'

        self.legend.setHtml(
            f'<span style="color:{muted}">{self.time_axis.cursor_label(i)}</span>&nbsp;&nbsp; '
            + "&nbsp; ".join(value(n, v) for n, v in (("O", o), ("H", h), ("L", l), ("C", c)))
            + f'&nbsp;&nbsp; <span style="color:{color}">{change:+,.{decimals}f} ({pct:+.2f}%)</span>')

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
    def set_tbr(self, sessions: list, opacity: float | None = None, line_opacity: float | None = None) -> None:
        """Zonas TBR calculadas (tradingbot.skills.tbr.zones.Session); solo se ven con show_tbr(True)."""
        self._tbr_sessions = list(sessions)
        if opacity is not None:
            self._tbr_opacity = opacity
        if line_opacity is not None:
            self._tbr_line_opacity = line_opacity
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
            pen_color.setAlphaF(self._tbr_line_opacity)
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

    def set_marker(self, index: int | None) -> None:
        """Línea vertical sobre la vela marcada en el histograma del sesgo (None: sin marca)."""
        pi = self.getPlotItem()
        marker = getattr(self, "_marker", None)
        if index is None:
            if marker is not None:
                marker.hide()
            return
        if marker is None:
            marker = self._marker = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(theme.ACCENT, width=1, style=Qt.PenStyle.DashLine))
            marker.setZValue(5)
            pi.addItem(marker, ignoreBounds=True)
        marker.setPos(float(index))
        marker.show()

    # -- posiciones de los patrones (como la herramienta de posición de TradingView) ---------------------------------------
    def set_positions(self, positions: list[dict]) -> None:
        """positions: {x0, x1 (índices de vela), entry, stop, target (precios), direction, state, label}."""
        self._positions = list(positions)
        self._draw_positions()

    def show_positions(self, visible: bool) -> None:
        self._pos_visible = visible
        self._draw_positions()

    def _draw_positions(self) -> None:
        pi = self.getPlotItem()
        for item in self._pos_items:
            pi.removeItem(item)
        self._pos_items.clear()
        self._pos_pills.clear()
        if not self._pos_visible:
            self._update_card()
            return
        for pos in self._positions:
            first = len(self._pos_items)
            x0, x1 = float(pos["x0"]), float(pos["x1"])
            entry, stop, target = float(pos["entry"]), float(pos["stop"]), float(pos["target"])
            for lo, hi, color in ((min(entry, target), max(entry, target), QColor(38, 166, 154, 70)),
                                  (min(entry, stop), max(entry, stop), QColor(239, 83, 80, 70))):
                box = QGraphicsRectItem(QRectF(x0, lo, max(x1 - x0, 0.5), max(hi - lo, 1e-9)))
                box.setBrush(color)
                box.setPen(QPen(Qt.PenStyle.NoPen))
                box.setZValue(-6)
                pi.addItem(box, ignoreBounds=True)
                self._pos_items.append(box)
            border = BOX_BORDER.get(str(pos["state"]))
            if border:
                lo, hi = sorted((stop, target))
                frame = QGraphicsRectItem(QRectF(x0, lo, max(x1 - x0, 0.5), max(hi - lo, 1e-9)))
                pen = QPen(QColor(border), 1.5)
                pen.setCosmetic(True)                           # grosor en píxeles, no en precio
                frame.setPen(pen)
                frame.setBrush(Qt.BrushStyle.NoBrush)
                frame.setZValue(-4)
                pi.addItem(frame, ignoreBounds=True)
                self._pos_items.append(frame)
            line = pg.PlotCurveItem(x=np.array([x0, x1]), y=np.array([entry, entry]), pen=pg.mkPen(theme.MUTED, width=1.2))
            line.setZValue(-5)
            pi.addItem(line, ignoreBounds=True)
            self._pos_items.append(line)
            pill = PositionPill(pos)
            pill.setPos(x0, stop)
            pi.addItem(pill, ignoreBounds=True)
            self._pos_items.append(pill)
            if pos.get("decision") == "NO GO":                       # la que Cortex no opera se ve atenuada, como su fibo
                for item in self._pos_items[first:]:
                    item.setOpacity(NO_GO_PILL_OPACITY if item is pill else NO_GO_OPACITY)
            self._pos_pills.append(pill)
        self._fit_pills()
        self._update_card()

    def _fit_pills(self) -> None:
        """Las píldoras empiezan en la vela de entrada, pero si no caben hasta el eje de precio se corren a la izquierda
        para que se vea entera (el resultado va al final). Solo lo que haga falta."""
        vb = self.getPlotItem().getViewBox()
        right = vb.sceneBoundingRect().right() - 2
        for pos, pill in zip(self._positions, self._pos_pills):
            x0, stop = float(pos["x0"]), float(pos["stop"])
            width = pill.boundingRect().width()                 # en píxeles: la píldora no se escala con el gráfico
            start = vb.mapViewToScene(QPointF(x0, stop)).x()
            x = vb.mapSceneToView(QPointF(right - width, 0)).x() if start + width > right else x0
            pill.setPos(x, stop)

    @property
    def position_count(self) -> int:
        return 0 if not self._pos_visible else len(self._positions)

    def _position_at(self, scene_pos) -> int | None:
        """Posición bajo el ratón (su caja o su píldora); la última dibujada gana si se solapan."""
        vb = self.getPlotItem().getViewBox()
        if not vb.sceneBoundingRect().contains(scene_pos):
            return None
        pt = vb.mapSceneToView(scene_pos)
        for i in reversed(range(len(self._pos_pills))):
            pos = self._positions[i]
            x0, x1 = float(pos["x0"]), float(pos["x1"])
            lo, hi = sorted((float(pos["stop"]), float(pos["target"])))
            if (x0 <= pt.x() <= x0 + max(x1 - x0, 0.5) and lo <= pt.y() <= hi) \
                    or self._pos_pills[i].sceneBoundingRect().contains(scene_pos):
                return i
        return None

    def _chart_clicked(self, event) -> None:
        """Pulsar una posición deja su ficha fija; pulsarla otra vez (o fuera de las posiciones) la quita."""
        i = self._position_at(event.scenePos())
        self._pinned = None if i == self._pinned else i
        self._update_card()

    def _update_card(self) -> None:
        """Ficha con el detalle de la posición fijada (o, si no hay, la que está bajo el ratón), bajo su píldora."""
        n = len(self._pos_pills)
        if self._pinned is not None and self._pinned >= n:
            self._pinned = None                                 # ya no está dibujada
        i = self._pinned if self._pinned is not None else self._hover
        card = self._card
        vb = self.getPlotItem().getViewBox()
        if i is None or i >= n or not vb.sceneBoundingRect().intersects(self._pos_pills[i].sceneBoundingRect()):
            card.hide()                                         # sin posición, o con su píldora fuera de la vista
            return
        pos = self._positions[i]
        entry, stop, target = float(pos["entry"]), float(pos["stop"]), float(pos["target"])
        muted = theme.MUTED

        def row(name: str, value: str, color: str = muted) -> str:
            return (f'<tr><td style="color:{color}; padding-right:14px">{name}</td>'
                    f'<td align="right" style="color:{theme.TEXT}">{value}</td></tr>')

        rows = (row("Entrada", fmt_price(entry)) + row("Stop", fmt_price(stop), "#EF5350")
                + row("Objetivo", fmt_price(target), "#26A69A") + row("R:R", f"{_ratio(pos):.2f}"))
        verdict = ""
        if pos.get("decision"):
            verdict = (f'<div style="margin-top:3px"><span style="color:{_verdict_color(pos)}">Cortex {pos["decision"]}</span>'
                       f'<span style="color:{muted}">&nbsp; {html.escape(pos.get("reason", ""))}</span></div>')
        card.setHtml(f'<div style="font-size:8pt"><div style="color:{theme.TEXT}"><b>{html.escape(pos["label"])}</b>'
                     f' · {"Largo" if pos["direction"] == "long" else "Corto"} · {html.escape(str(pos["state"]))}</div>'
                     f'<table cellspacing="0" cellpadding="0">{rows}</table>{verdict}</div>')
        card.fill = pg.mkBrush(_alpha(theme.PANEL, 245))
        card.border = pg.mkPen(theme.BORDER)
        rect = self._pos_pills[i].sceneBoundingRect()
        below, above = vb.mapFromScene(rect.bottomLeft()), vb.mapFromScene(rect.topLeft())   # bordes de la píldora
        size = card.textItem.boundingRect()
        x = min(max(below.x(), 4.0), vb.width() - size.width() - 4)
        y = below.y() + 4 if below.y() + 4 + size.height() <= vb.height() else above.y() - 4 - size.height()
        card.setPos(x, y)
        card.show()
        card.update()

    # -- fibonacci de los patrones ---------------------------------------------------------------------------
    def set_fibs(self, fibs: list[dict]) -> None:
        """fibs: dibujos {x0, x1 (índices de vela), levels {"0", "0,5", "1": precio}, label, state, direction}."""
        self._fibs = list(fibs)
        self._draw_fibs()

    def show_fibs(self, visible: bool) -> None:
        self._fib_visible = visible
        self._draw_fibs()

    def _draw_fibs(self) -> None:
        """Solo los niveles con su nombre (sin precio ni título): el detalle de la entrada está en su posición."""
        pi = self.getPlotItem()
        for item in self._fib_items:
            pi.removeItem(item)
        self._fib_items.clear()
        if not self._fib_visible:
            return
        for fib in self._fibs:
            first = len(self._fib_items)
            x0, x1 = float(fib["x0"]), float(fib["x1"])
            for name, price in fib["levels"].items():
                half = name == "0,5"
                color = _fib_color(name)
                pen = pg.mkPen(color, width=2 if half else 1.2, style=Qt.PenStyle.DashLine if half else Qt.PenStyle.SolidLine)
                line = pg.PlotCurveItem(x=np.array([x0, x1]), y=np.array([price, price]), pen=pen)
                line.setZValue(-2)
                pi.addItem(line, ignoreBounds=True)
                text = pg.TextItem(anchor=(0, 0.5))
                text.setHtml(f'<span style="font-size:8pt; color:{color}">{name}</span>')
                text.setPos(x1, price)
                pi.addItem(text, ignoreBounds=True)
                self._fib_items += [line, text]
            if fib.get("tag") and "1" in fib["levels"]:               # «T» (tiempo) o «I» (invalidado): en el nivel 1, por fuera
                tag = pg.TextItem(anchor=(0.5, -0.1 if fib["direction"] == "long" else 1.1))
                tag.setHtml(f'<span style="font-size:9pt; font-weight:bold; color:{theme.MUTED}">{html.escape(str(fib["tag"]))} · {"invalidado" if fib["tag"] == "I" else "tiempo"}</span>')
                tag.setPos((x0 + x1) / 2, fib["levels"]["1"])
                pi.addItem(tag, ignoreBounds=True)
                self._fib_items.append(tag)
            if fib.get("decision") == "NO GO":                       # entrada detectada que Cortex no opera: atenuada
                for item in self._fib_items[first:]:
                    item.setOpacity(NO_GO_OPACITY)

    @property
    def fib_count(self) -> int:
        """Fibonacci dibujados (cada uno son tres niveles)."""
        return 0 if not self._fib_visible else len(self._fibs)

    # -- media móvil simple ----------------------------------------------------------------------------
    def set_sma(self, values, color: str = "#00ACC1", style: str = "normal") -> None:
        """values: la SMA de cada vela (NaN al principio) o None para quitarla."""
        self._sma = None if values is None else (np.asarray(values, dtype=float), color, style)
        self._draw_sma()

    def show_sma(self, visible: bool) -> None:
        self._sma_visible = visible
        self._draw_sma()

    def _draw_sma(self) -> None:
        pi = self.getPlotItem()
        if self._sma_item is not None:
            pi.removeItem(self._sma_item)
            self._sma_item = None
        if self._sma is None or not self._sma_visible:
            return
        values, color, style = self._sma
        pen_style = {"discontinuo": Qt.PenStyle.DashLine, "punteado": Qt.PenStyle.DotLine}.get(style, Qt.PenStyle.SolidLine)
        item = pg.PlotCurveItem(x=np.arange(len(values), dtype=float), y=values, connect="finite",
                                pen=pg.mkPen(color, width=1.5, style=pen_style))
        item.setZValue(-3)
        pi.addItem(item, ignoreBounds=True)
        self._sma_item = item

    @property
    def sma_drawn(self) -> bool:
        return self._sma_item is not None

    @property
    def day_item_count(self) -> int:
        return len(self._day_items)
