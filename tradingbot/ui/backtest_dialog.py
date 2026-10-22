"""Backtest de las estrategias en una ventana flotante, con el mismo estilo que Forwardtest.

Arriba se eligen el grupo (índices, forex, oro, cripto o Calendario), el patrón y el filtro (lo que opera el bot, a favor del
sesgo o sin filtro); debajo, el veredicto, las cifras clave, la curva de R acumulado, las barras por año y por hora, y los
«libros»: comparativa entre mercados, por mercado, zona, lado, filtro, día, mitades, sensibilidad, mejoras, embudo y metodología.

Las barras por año y por hora se pulsan: cada histograma marca un solo año (u hora); un clic en otra barra la sustituye y en la
misma la quita, y todo lo demás se recalcula solo con esas operaciones. Cada histograma aplica el filtro del otro, pero no el
suyo, para que se pueda cambiar de barra viéndolas todas. Los datos los carga la
skill Stats; las cifras se calculan en `skills/stats/backtest.py` a partir de cada operación.
"""
from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtWidgets import (QButtonGroup, QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout,
                               QWidget)

from ..skills.stats.backtest import BOT_FILTER, MAIN_FILTERS, PATTERNS, Backtest, Group, Ops, summarize, verdict
from . import theme
from .fmt import miles
from .stats_dialog import Book, Tile

SIDE_NAMES = {0: "▲ LARGO", 1: "▼ CORTO"}
METRIC_HEADERS = ("Ops", "Acierto", "R medio", "R total", "PF", "Máx. DD", "t")
BREAKEVEN_2R = 100 / 3                     # con objetivo 2R se empata ganando 1 de cada 3
MIN_OPS_BEST = 30                          # para «mejor / peor mercado» no cuentan los que tienen menos operaciones
STATIC_NOTE = " · no cambia con el filtro de años u horas"


# -- formato ---------------------------------------------------------------------------------------
def _num(v, digits: int = 2, sign: bool = False) -> str:
    if v is None:
        return "-"
    return f"{v:+.{digits}f}" if sign else f"{v:.{digits}f}"


def _r(v, digits: int = 3) -> str:
    return "-" if v is None else f"{v:+.{digits}f} R"


def _tone(v) -> str | None:
    if not v:
        return None
    return theme.BULL if v > 0 else theme.BEAR


def _t_tone(t) -> str | None:
    """El t solo se colorea si es significativo (|t| >= 2)."""
    if t is None or abs(t) < 2:
        return theme.MUTED
    return theme.BULL if t > 0 else theme.BEAR


def _pf_tone(pf) -> str | None:
    if pf is None:
        return None
    return theme.BULL if pf > 1 else theme.BEAR if pf < 1 else None


def _colored(text: str, color: str | None) -> str:
    return f'<span style="color:{color}">{text}</span>' if color else text


def metric_cells(r: dict | None) -> list[tuple[str, str | None]]:
    """Columnas comunes de un libro del backtest (sin el nombre): operaciones, acierto, R medio y total, PF, drawdown y t."""
    if not r or not r.get("n"):
        return [("0", theme.MUTED)] + [("-", theme.MUTED)] * 6
    wr = r.get("wr")
    return [(miles(int(r["n"])), None),
            ("-" if wr is None else f"{wr:.1f} %", None),          # sin color: el equilibrio depende del objetivo
            (_r(r.get("mean")), _tone(r.get("mean"))),
            ("-" if r.get("total") is None else f"{r['total']:+.1f} R", _tone(r.get("total"))),
            (_num(r.get("pf")), _pf_tone(r.get("pf"))),
            ("-" if r.get("dd") is None else f"{r['dd']:.0f} R", theme.BEAR if r.get("dd") else None),
            (_num(r.get("t"), 1, sign=True), _t_tone(r.get("t")))]


def _unit(v, digits: int, unit: str = "") -> str:
    return "-" if v is None else f"{v:.{digits}f}{unit}"


def _count(v) -> str:
    return "-" if v is None else miles(int(v))


def _short_market(name: str) -> str:
    """NAS100.r -> NAS100 (el sufijo del broker no aporta en la ventana)."""
    return name.split(".")[0] if name else name


def _mean(ops: Ops, col: str) -> float | None:
    """Media de una columna (sin los huecos), o None si no la hay."""
    if col not in ops.cols or not len(ops):
        return None
    v = ops[col][~np.isnan(ops[col])]
    return float(v.mean()) if len(v) else None


def _ranked(items: list, n_of) -> list:
    """Los que cuentan para «mejor / peor»: con MIN_OPS_BEST operaciones o más, salvo que con la selección no llegue ni la
    mitad (entonces todos los que tengan alguna)."""
    played = [x for x in items if n_of(x)]
    enough = [x for x in played if n_of(x) >= MIN_OPS_BEST]
    return enough if len(enough) * 2 >= len(played) else played


def _clean(net) -> np.ndarray:
    net = np.asarray(net, dtype=float)
    return net[~np.isnan(net)]


# -- piezas de la ventana --------------------------------------------------------------------------
class BarCard(Book):
    """Tarjeta con un gráfico de barras (verde si es positivo, rojo si es negativo) que se pulsa para filtrar.

    Cada clic en una barra emite `toggled` con su clave (el año o la hora). Con una elegida, las demás se atenúan.
    """

    toggled = Signal(object)
    cleared = Signal()

    def __init__(self, title: str, note: str) -> None:
        super().__init__(title, note, ())
        self.clear_btn = QPushButton("Quitar")
        self.clear_btn.setProperty("chip", "true")
        self.clear_btn.setToolTip("Quitar la selección de este gráfico")
        self.clear_btn.clicked.connect(self.cleared.emit)
        self.clear_btn.hide()
        self.layout().itemAt(0).layout().addWidget(self.clear_btn)
        self.plot = pg.PlotWidget()
        self.plot.setFixedHeight(120)
        self.plot.setCursor(Qt.CursorShape.PointingHandCursor)
        pi = self.plot.getPlotItem()
        pi.setMenuEnabled(False)
        pi.hideButtons()
        pi.getViewBox().setMouseEnabled(x=False, y=False)
        self.zero = pg.InfiniteLine(0, angle=0, movable=False)
        pi.addItem(self.zero, ignoreBounds=True)
        self.bars: pg.BarGraphItem | None = None
        self.layout().addWidget(self.plot)
        self.keys: list = []
        self.values: list[float] = []
        self.tips: list[str] = []
        self.base_note = note
        self.plot.scene().sigMouseClicked.connect(self._clicked)
        self.plot.scene().sigMouseMoved.connect(self._hover)

    def set_bars(self, keys: list, labels: list[str], values: list[float | None], tips: list[str],
                 selected: set = frozenset(), marked=None) -> None:
        """Pinta las barras. `selected`: claves elegidas (las demás, atenuadas); `marked`: la que usa el bot sin selección."""
        pi = self.plot.getPlotItem()
        self.plot.setBackground(theme.CHART_BG)
        for side in ("left", "bottom"):
            axis = pi.getAxis(side)
            axis.setPen(pg.mkPen(theme.CHART_GRID or theme.BORDER))
            axis.setTextPen(pg.mkPen(theme.CHART_TEXT))
        self.zero.setPen(pg.mkPen(theme.MUTED, style=Qt.PenStyle.DashLine))
        if self.bars is not None:
            pi.removeItem(self.bars)
            self.bars = None
        self.keys, self.tips = list(keys), list(tips)
        self.values = [v or 0.0 for v in values]
        self.clear_btn.setVisible(bool(selected))
        self.note.setText(self.base_note if self.values else "sin datos para este patrón y filtro")
        if not self.values:
            return
        brushes, pens = [], []
        for key, v in zip(self.keys, self.values):
            color = theme.BULL if v > 0 else theme.BEAR if v < 0 else theme.MUTED
            on = not selected or key in selected
            brushes.append(pg.mkBrush(color if on else theme.mix(theme.CHART_BG, color, 0.28)))
            outline = key in selected or (not selected and key == marked)
            pens.append(pg.mkPen(theme.TEXT, width=1.5) if outline else pg.mkPen(None))
        self.bars = pg.BarGraphItem(x=list(range(len(self.values))), height=self.values, width=0.7, brushes=brushes, pens=pens)
        pi.addItem(self.bars)
        step = max(1, len(labels) // 14)
        pi.getAxis("bottom").setTicks([[(i, lab) for i, lab in enumerate(labels) if i % step == 0]])
        pi.setXRange(-0.6, len(self.values) - 0.4, padding=0)

    def _index_at(self, scene_pos) -> int | None:
        vb = self.plot.getPlotItem().getViewBox()
        if not vb.sceneBoundingRect().contains(scene_pos):
            return None
        x = vb.mapSceneToView(scene_pos).x()
        i = int(round(x))
        return i if 0 <= i < len(self.keys) and abs(x - i) <= 0.45 else None

    def _clicked(self, event) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        i = self._index_at(event.scenePos())
        if i is not None:
            self.toggled.emit(self.keys[i])

    def _hover(self, pos) -> None:
        i = self._index_at(pos)
        self.plot.setToolTip(self.tips[i] + "\nClic: filtrar / quitar" if i is not None else "")

    def click(self, key) -> None:
        """Como pulsar la barra de `key` (para los tests)."""
        self.toggled.emit(key)


# -- ventana ---------------------------------------------------------------------------------------
class BacktestDialog(QDialog):
    """Ventana flotante (no modal) con el backtest; se abre y se cierra con el botón Backtest de la cabecera."""

    hidden = Signal()
    reload_requested = Signal()

    def __init__(self, parent, backtest: Backtest | None = None, error: str = "") -> None:
        super().__init__(parent)
        self.setWindowTitle("Backtest")
        self.setWindowFlag(Qt.WindowType.Tool, True)
        self.setModal(False)
        self.resize(820, 900)
        self.backtest, self.error = backtest, error
        self.group_key = ""
        self.profile_key = ""
        self.pattern = PATTERNS[0]
        self.filter = MAIN_FILTERS[0]
        self.years: set[int] = set()                 # años y horas elegidos en los histogramas (vacío: todos)
        self.hours: set[int] = set()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 12, 14, 12)
        outer.setSpacing(10)

        head = QHBoxLayout()
        title = QLabel("Backtest · Histórico")
        title.setObjectName("Brand")
        self.subtitle = QLabel("patrones Continuación y Reversión en M15 · objetivo 2R · spread real")
        self.subtitle.setObjectName("Tiny")
        head.addWidget(title)
        head.addSpacing(8)
        head.addWidget(self.subtitle)
        head.addStretch(1)
        self.generated = QLabel("")
        self.generated.setObjectName("Tiny")
        head.addWidget(self.generated)
        outer.addLayout(head)

        # Selectores: perfil, mercados, patrón y filtro
        self.profile_row = QHBoxLayout()
        self.profile_row.setSpacing(6)
        self.profile_btns: dict[str, QPushButton] = {}
        self.profile_btn_group = QButtonGroup(self)
        self.profile_label_row = self._labelled("Perfil", self.profile_row)
        outer.addLayout(self.profile_label_row)
        self.group_row = QHBoxLayout()
        self.group_row.setSpacing(6)
        self.group_btns: dict[str, QPushButton] = {}
        self.group_btn_group = QButtonGroup(self)
        outer.addLayout(self._labelled("Mercados", self.group_row))
        sel = QHBoxLayout()
        sel.setSpacing(6)
        self.pattern_row, self.filter_row = QHBoxLayout(), QHBoxLayout()      # sus chips dependen del grupo elegido
        self.pattern_row.setSpacing(6)
        self.filter_row.setSpacing(6)
        self.pattern_btns: dict[str, QPushButton] = {}
        self.filter_btns: dict[str, QPushButton] = {}
        self._chip_groups: dict[str, QButtonGroup] = {}
        sel.addLayout(self.pattern_row)
        sel.addSpacing(14)
        filt_label = QLabel("Filtro")
        filt_label.setObjectName("Tiny")
        sel.addWidget(filt_label)
        sel.addLayout(self.filter_row)
        sel.addStretch(1)
        outer.addLayout(self._labelled("Patrón", sel))
        self._chips_for = ""                                                    # grupo para el que están hechos los chips

        # Selección de los histogramas: qué años / horas se están mirando
        self.selection_bar = QFrame()
        self.selection_bar.setObjectName("Card")
        sel_row = QHBoxLayout(self.selection_bar)
        sel_row.setContentsMargins(10, 5, 6, 5)
        self.selection_label = QLabel()
        self.selection_label.setTextFormat(Qt.TextFormat.RichText)
        self.selection_label.setObjectName("Tiny")
        self.selection_label.setWordWrap(True)
        self.clear_selection_btn = QPushButton("Quitar filtro")
        self.clear_selection_btn.setProperty("chip", "true")
        self.clear_selection_btn.clicked.connect(self.clear_selection)
        sel_row.addWidget(self.selection_label, 1)
        sel_row.addWidget(self.clear_selection_btn)
        outer.addWidget(self.selection_bar)

        # Veredicto y cifras clave
        self.verdict = QLabel()
        self.verdict.setObjectName("Verdict")
        self.verdict.setTextFormat(Qt.TextFormat.RichText)
        self.verdict.setWordWrap(True)
        outer.addWidget(self.verdict)
        tiles = QHBoxLayout()
        tiles.setSpacing(8)
        self.blocks: dict[str, Tile] = {}
        for key, label in (("n", "Operaciones"), ("wr", "Acierto"), ("mean", "R medio (neto)"), ("total", "R total"),
                           ("pf", "Profit factor"), ("dd", "Máx. drawdown")):
            tile = Tile(label)
            self.blocks[key] = tile
            tiles.addWidget(tile, 1)
        outer.addLayout(tiles)
        self.summary = QLabel()
        self.summary.setObjectName("Tiny")
        self.summary.setTextFormat(Qt.TextFormat.RichText)
        self.summary.setWordWrap(True)
        outer.addWidget(self.summary)

        # Contenido desplazable
        body = QWidget()
        lay = QVBoxLayout(body)
        lay.setContentsMargins(0, 0, 4, 0)
        lay.setSpacing(10)
        curve_card = Book("Curva de R", "R neto acumulado, operaciones por fecha de cierre", ())
        self.curve_card = curve_card
        self.curve_plot = pg.PlotWidget(axisItems={"bottom": pg.DateAxisItem(orientation="bottom")})
        self.curve_plot.setFixedHeight(150)
        pi = self.curve_plot.getPlotItem()
        pi.setMenuEnabled(False)
        pi.hideButtons()
        pi.getViewBox().setMouseEnabled(x=False, y=False)
        self.curve = pi.plot([0.0])
        self.zero = pg.InfiniteLine(0, angle=0, movable=False)
        pi.addItem(self.zero, ignoreBounds=True)
        curve_card.layout().addWidget(self.curve_plot)
        lay.addWidget(curve_card)

        self.by_year = BarCard("Por año", "R total de cada año · pulsa para filtrar")
        self.by_hour = BarCard("Por hora de entrada", "R medio por operación, hora de Nueva York · pulsa para filtrar")
        self.by_year.toggled.connect(self.toggle_year)
        self.by_hour.toggled.connect(self.toggle_hour)
        self.by_year.cleared.connect(lambda: self._set_selection(set(), self.hours))
        self.by_hour.cleared.connect(lambda: self._set_selection(self.years, set()))
        self.compare = Book("Comparativa entre mercados", "", ("Mercado", "Desde", "Ops", "Acierto", "R bruto",
                                                               "R neto", "R total", "PF", "t"),
                            highlights=("Mejor mercado", "Peor mercado", "Coste medio del grupo"))
        self.by_market = Book("Por mercado", "", ("Mercado",) + METRIC_HEADERS,
                              highlights=("Mejor mercado", "Peor mercado", "Más operaciones"))
        self.by_zone = Book("Por zona (TBR)", "la TBR donde se dio la entrada", ("Zona",) + METRIC_HEADERS)
        self.by_side = Book("Por lado", "largos contra cortos", ("Lado",) + METRIC_HEADERS)
        self.by_filter = Book("Por filtro", "el mismo patrón con cada filtro del backtest", ("Filtro",) + METRIC_HEADERS)
        self.by_day = Book("Por día de la semana", "día de la entrada", ("Día",) + METRIC_HEADERS)
        self.halves = Book("Robustez", "el histórico partido en dos por la mediana de las fechas", ("Mitad",) + METRIC_HEADERS)
        self.sensitivity = Book("Sensibilidad", "otros objetivos y tiempos máximos con las mismas entradas",
                                ("Variante",) + METRIC_HEADERS)
        self.improvements = Book("Mejoras (stop y RR)", "siempre con las reglas del bot; stop k veces el original",
                                 ("Mejora", "Stop", "RR", "Ops", "Acierto", "R bruto", "R neto", "t", "1ª mitad", "2ª mitad"))
        self.funnel = Book("Embudo", "de las TBR evaluadas a las entradas", ("Mercado · patrón", "TBR", "Activadas", "Entradas",
                                                                             "Vencidas", "Invalidadas", "% TBR", "% activadas"))
        self.outcomes = Book("Cómo terminan", "", ("Patrón", "Objetivo", "Stop", "Breakeven", "Tiempo", "MAE", "MFE",
                                                   "Velas", "Riesgo %", "Coste"))
        self.data_book = Book("Datos", "velas M15 de MT5 usadas", ("Mercado", "Velas", "Desde", "Hasta", "TBR"))
        for book in (self.by_year, self.by_hour, self.compare, self.by_market, self.by_zone, self.by_side, self.by_filter,
                     self.by_day, self.halves, self.sensitivity, self.outcomes, self.improvements, self.funnel, self.data_book):
            lay.addWidget(book)
        self.method = Book("Metodología", "cómo se hizo", ())
        self.method_text = QLabel()
        self.method_text.setObjectName("Tiny")
        self.method_text.setWordWrap(True)
        self.method_text.setTextFormat(Qt.TextFormat.RichText)
        self.method.layout().addWidget(self.method_text)
        lay.addWidget(self.method)
        lay.addStretch(1)

        self.empty = QLabel()
        self.empty.setObjectName("Muted")
        self.empty.setWordWrap(True)
        self.empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(self.empty)
        self.scroll = QScrollArea()
        self.scroll.setObjectName("StatsScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidget(body)
        outer.addWidget(self.scroll, 1)

        buttons = QHBoxLayout()
        note = QLabel("R neto = con el spread real de MT5 (sin comisiones ni deslizamiento). t: por debajo de 2 en valor absoluto "
                      "no se distingue de cero. Con objetivo 2R se empata acertando el 33,3 %.")
        note.setObjectName("Tiny")
        note.setWordWrap(True)
        self.reload_btn = QPushButton("Recargar")
        self.reload_btn.setToolTip("Vuelve a leer el backtest (tras regenerarlo con scripts/exportar_backtest.py)")
        self.reload_btn.clicked.connect(self.reload_requested.emit)
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.hide)
        buttons.addWidget(note, 1)
        buttons.addWidget(self.reload_btn)
        buttons.addWidget(close_btn)
        outer.addLayout(buttons)
        self.set_backtest(backtest, error)

    # -- construcción ------------------------------------------------------------------------
    @staticmethod
    def _labelled(text: str, row: QHBoxLayout) -> QHBoxLayout:
        out = QHBoxLayout()
        out.setSpacing(8)
        label = QLabel(text)
        label.setObjectName("Tiny")
        label.setFixedWidth(56)
        out.addWidget(label)
        out.addLayout(row, 1)
        return out

    def _chips(self, row: QHBoxLayout, keys, slot, current, names: dict | None = None) -> dict[str, QPushButton]:
        """Rehace los chips de `row` (uno por clave, exclusivos)."""
        while row.count():
            w = row.takeAt(0).widget()
            if w is not None:
                w.hide()
                w.deleteLater()
        group = QButtonGroup(self)
        self._chip_groups[str(id(row))] = group
        btns = {}
        for key in keys:
            btn = QPushButton((names or {}).get(key, key))
            btn.setCheckable(True)
            btn.setProperty("chip", "true")
            btn.setChecked(key == current)
            btn.clicked.connect(lambda _=False, k=key: slot(k))
            group.addButton(btn)
            row.addWidget(btn)
            btns[key] = btn
        return btns

    def _build_profile_chips(self) -> None:
        while self.profile_row.count():
            w = self.profile_row.takeAt(0).widget()
            if w is not None:
                w.deleteLater()
        self.profile_btns.clear()
        self.profile_btn_group = QButtonGroup(self)
        profiles = self.backtest.profiles if self.backtest else []
        for key, name in profiles:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setProperty("chip", "true")
            btn.setToolTip("Perfil de MT5 con el que se hizo este backtest")
            btn.clicked.connect(lambda _=False, k=key: self.set_profile(k))
            self.profile_btn_group.addButton(btn)
            self.profile_row.addWidget(btn)
            self.profile_btns[key] = btn
        self.profile_row.addStretch(1)
        for i in range(self.profile_label_row.count()):          # con un solo perfil (ficheros antiguos) no hace falta elegir
            w = self.profile_label_row.itemAt(i).widget()
            if w is not None:
                w.setVisible(len(profiles) > 1)
        self.profile_row_visible = len(profiles) > 1

    def _build_group_chips(self) -> None:
        while self.group_row.count():
            w = self.group_row.takeAt(0).widget()
            if w is not None:
                w.deleteLater()
        self.group_btns.clear()
        self.group_btn_group = QButtonGroup(self)
        shown = self.backtest.groups_of(self.profile_key) if self.backtest else []
        for g in shown:
            btn = QPushButton(g.name)
            btn.setCheckable(True)
            btn.setProperty("chip", "true")
            btn.setToolTip(", ".join(_short_market(m.get("mercado", "")) for m in g.markets) + f" · {g.period}")
            btn.clicked.connect(lambda _=False, k=g.key: self.set_group(k))
            self.group_btn_group.addButton(btn)
            self.group_row.addWidget(btn)
            self.group_btns[g.key] = btn
        self.group_row.addStretch(1)

    # -- abrir / cerrar ----------------------------------------------------------------------
    def popup_at(self, anchor: QWidget) -> None:
        """Muestra la ventana bajo `anchor` (el botón), alineada por su borde derecho; luego recuerda dónde la dejes."""
        if not getattr(self, "_placed", False):
            screen = anchor.screen().availableGeometry() if anchor.screen() else None
            if screen is not None:
                self.resize(self.width(), min(self.height(), screen.height() - 80))
            corner = anchor.mapToGlobal(QPoint(anchor.width(), anchor.height() + 6))
            self.move(corner.x() - self.width(), corner.y())
            self._placed = True
        self.refresh()
        self.show()
        self.raise_()
        self.activateWindow()

    def hideEvent(self, event) -> None:  # noqa: N802
        super().hideEvent(event)
        self.hidden.emit()

    def reject(self) -> None:
        self.hide()

    # -- selección ---------------------------------------------------------------------------
    def set_backtest(self, backtest: Backtest | None, error: str = "") -> None:
        self.backtest, self.error = backtest, error
        self._chips_for = ""
        if backtest and backtest.groups:
            keep = backtest.group(self.group_key) or backtest.groups[0]
            self.profile_key = keep.profile
            self._build_profile_chips()
            self._build_group_chips()
            self.set_group(keep.key)
        else:
            self._build_profile_chips()
            self._build_group_chips()
            self.refresh()

    def set_profile(self, key: str) -> None:
        """Otro perfil: se queda el mismo grupo de mercados si el perfil lo tiene (índices con índices) y si no, el primero."""
        if not self.backtest or key == self.profile_key:
            return
        groups = self.backtest.groups_of(key)
        if not groups:
            return
        base = self.group_key.split(":", 1)[-1]
        chosen = next((g for g in groups if g.key.split(":", 1)[-1] == base), groups[0])
        self.profile_key = key
        self._build_group_chips()
        self.set_group(chosen.key)

    def set_group(self, key: str) -> None:
        if key != self.group_key:                       # otro grupo, otros años y horas: la selección no vale
            self.years, self.hours = set(), set()
        self.group_key = key
        g = self.group
        if g is not None and g.profile != self.profile_key:
            self.profile_key = g.profile
            self._build_group_chips()
        if g is not None:                                # cada grupo trae sus patrones y filtros: si no vale, el primero
            if self.pattern not in g.patterns:
                self.pattern = g.patterns[0]
            if self.filter not in g.filters:
                self.filter = next(iter(g.filters))
        self.refresh()

    def set_pattern(self, pattern: str) -> None:
        self.pattern = pattern
        self.refresh()

    def set_filter(self, filt: str) -> None:
        self.filter = filt
        self.refresh()

    def toggle_year(self, year: int) -> None:
        """Clic en una barra del año: queda solo ese año (sustituye al que hubiera) o, si ya estaba marcado, se quita."""
        self._set_selection(self._single(self.years, year), self.hours)

    def toggle_hour(self, hour: int) -> None:
        self._set_selection(self.years, self._single(self.hours, hour))

    @staticmethod
    def _single(current: set, key) -> set:
        """Un solo año (u hora) por histograma."""
        return set() if int(key) in current else {int(key)}

    def clear_selection(self) -> None:
        self._set_selection(set(), set())

    def _set_selection(self, years: set, hours: set) -> None:
        self.years, self.hours = set(years), set(hours)
        self.refresh()

    @property
    def group(self) -> Group | None:
        return self.backtest.group(self.group_key) if self.backtest else None

    # -- pintar ------------------------------------------------------------------------------
    def refresh(self) -> None:
        g = self.group
        self.empty.setVisible(g is None)
        self.scroll.setVisible(g is not None)
        for w in (self.verdict, self.summary, *self.blocks.values()):
            w.setVisible(g is not None)
        if g is None:
            self.selection_bar.hide()
            self.empty.setText(self.error or "No hay resultados de backtest cargados.\nGenéralos con "
                                             "scripts/exportar_backtest.py y pulsa Recargar.")
            self.generated.setText("")
            return
        for key, btn in self.profile_btns.items():
            btn.setChecked(key == self.profile_key)
        for key, btn in self.group_btns.items():
            btn.setChecked(key == self.group_key)
        if self._chips_for != g.key:
            self._chips_for = g.key
            self.pattern_btns = self._chips(self.pattern_row, g.patterns, self.set_pattern, self.pattern)
            self.filter_btns = self._chips(self.filter_row, g.filters, self.set_filter, self.filter, g.filters)
            if BOT_FILTER in self.filter_btns:
                self.filter_btns[BOT_FILTER].setToolTip("No va contra el sesgo (GO de Cortex), una sola posición abierta a "
                                                        "la vez y una TBR, un trade: lo que haría el bot")
        for key, btn in self.pattern_btns.items():
            btn.setChecked(key == self.pattern)
        for key, btn in self.filter_btns.items():
            btn.setChecked(key == self.filter)
        self.subtitle.setText(g.description)
        self.generated.setText(f"{g.period} · actualizado {g.updated}" if g.updated else g.period)

        view = g.view(self.pattern, self.filter, self.years, self.hours)
        self._paint_selection(g)
        self._paint_head(g, view.main)
        self._paint_curve(view.main)
        self._paint_bars(g, view)
        self._fill_compare(g)
        self._fill_markets(g, view.markets)
        self._fill_ops(self.by_zone, view.zones)
        self._fill_ops(self.by_side, view.sides, lambda k: _colored(SIDE_NAMES.get(k, str(k)), theme.BULL if k == 0 else theme.BEAR))
        self._fill_ops(self.by_filter, view.filters,
                       lambda k: f"<b>{g.all_filters.get(k, k)}</b>" if k == self.filter else g.all_filters.get(k, k))
        self._fill_ops(self.by_day, view.days, lambda k: k.capitalize())
        self._fill_ops(self.halves, view.halves)
        self._fill_rows(self.sensitivity, [(label, summarize(_clean(net))) for label, net in view.sensitivity])
        self._fill_outcomes(view.outcomes)
        self._fill_improvements(g)
        self._fill_funnel(g)
        self._fill_data(g)
        self.method_text.setText("<br>".join(f"<b>{t}</b>: {e}" for t, e in g.table("metodologia")))
        cal = g.is_calendar
        self.by_zone.setVisible(not cal)
        self.funnel.setVisible(bool(g.table("embudo")))
        self.improvements.setVisible(bool(g.table("mejoras")))
        self.compare.setVisible(not cal)
        self.by_day.note.setText("día de la entrada, misma hora, stop y RR (control)" if cal else "día de la entrada")
        self.by_side.note.setText("los cortos son el control" if cal else "largos contra cortos")
        static = STATIC_NOTE if self.years or self.hours else ""
        self.improvements.note.setText("siempre con las reglas del bot; stop k veces el original" + static)
        self.funnel.note.setText("de las TBR evaluadas a las entradas" + static)
        self.data_book.note.setText("velas M15 de MT5 usadas" + static)

    def _paint_selection(self, g: Group) -> None:
        parts = []
        if self.years:
            parts.append("años <b>" + ", ".join(str(y) for y in sorted(self.years)) + "</b>")
        if self.hours:
            parts.append("horas de entrada <b>" + ", ".join(f"{h:02d}:00" for h in sorted(self.hours)) + "</b> (NY)")
        self.selection_bar.setVisible(bool(parts))
        if parts:
            extra = " La hora sustituye a la de la configuración del bot." if g.is_calendar and self.hours else ""
            self.selection_label.setText(f"Filtrando por {' y '.join(parts)}: todas las cifras de abajo se recalculan solo con "
                                         f"esas operaciones.{extra}")

    def _paint_bars(self, g: Group, view) -> None:
        years = [(y, o.stats()) for y, o in view.years]
        self.by_year.set_bars([y for y, _ in years], [str(y) for y, _ in years], [s.get("total") for _, s in years],
                              [f"{y}: {s['n']} ops · {s['total']:+.1f} R · media {_r(s.get('mean'))}" for y, s in years],
                              self.years)
        hours = [(h, o.stats()) for h, o in view.hours]
        self.by_hour.set_bars([h for h, _ in hours], [f"{h:02d}" for h, _ in hours], [s.get("mean") for _, s in hours],
                              [f"{h:02d}:00 NY: {s['n']} ops · media {_r(s.get('mean'))} · {s['total']:+.1f} R" for h, s in hours],
                              self.hours, g.raw.get("hora") if g.is_calendar else None)

    def _paint_head(self, g: Group, main: Ops) -> None:
        b = self.blocks
        r = main.stats()
        if not r.get("n"):
            for tile in b.values():
                tile.set_value("-", "")
            self.verdict.setStyleSheet("")
            self.verdict.setText("Sin operaciones con este patrón, filtro y selección")
            self.summary.setText("")
            return
        text, sign = verdict(r.get("t"), r.get("mean"))
        color = theme.BULL if sign > 0 else theme.BEAR if sign < 0 else theme.WARN
        self.verdict.setStyleSheet(f"QLabel#Verdict {{ border: 1px solid {color}; border-left: 4px solid {color}; "
                                   f"border-radius: 4px; padding: 7px 10px; background: {theme.mix(theme.PANEL, color, 0.10)}; }}")
        per_100 = f"{(r.get('mean') or 0) * 100:+.1f} R cada 100 operaciones"
        filt = g.all_filters.get(self.filter, self.filter)
        where = f"{self.pattern}, {filt if g.is_calendar else filt.lower()}" + ("" if g.is_calendar else f", {g.name.lower()}")
        if self.years or self.hours:
            where += " (filtrado)"
        self.verdict.setText(f"<b style='color:{color}'>{text}</b>  ·  {where}: {per_100} (t {_num(r.get('t'), 2, sign=True)})")
        markets = len(set(main["m"].tolist()))
        b["n"].set_value(miles(int(r["n"])), f"{markets} mercado{'s' if markets != 1 else ''}" +
                         (" · selección" if self.years or self.hours else f" · {g.period}"))
        wr = r.get("wr")
        b["wr"].set_value("-" if wr is None else f"{wr:.1f} %",
                          "con R neto positivo" if g.is_calendar else f"equilibrio {BREAKEVEN_2R:.1f} % con 2R",
                          None if g.is_calendar else theme.BULL if wr and wr > BREAKEVEN_2R + 1 else None)
        b["mean"].set_value(_r(r.get("mean")), f"t {_num(r.get('t'), 2, sign=True)}", _tone(r.get("mean")))
        b["total"].set_value(f"{r['total']:+.0f} R", "suma de todas", _tone(r.get("total")))
        b["pf"].set_value(_num(r.get("pf")), "ganado / perdido", _pf_tone(r.get("pf")))
        b["dd"].set_value(f"{r['dd']:.0f} R" if r.get("dd") else "0 R", f"racha perdedora {r.get('streak') or '-'}",
                          theme.BEAR if r.get("dd") else None)
        gross = float((main["r"] + main["k"]).mean())
        cost = _mean(main, "k")
        parts = [f"ganada media {_colored(_r(r.get('avg_win')), theme.BULL)}",
                 f"perdida media {_colored(_r(r.get('avg_loss')), theme.BEAR)}",
                 f"sin costes {_colored(_r(gross), _tone(gross))}"]
        if cost is not None:
            parts.append(f"coste medio {_colored(f'{cost:.3f} R', theme.BEAR)} por operación")
        stats = [(name, o.stats()) for name, o in main.split(main.names("m"))]
        best = max(_ranked(stats, lambda x: x[1]["n"]), key=lambda x: x[1]["mean"], default=None)
        if best:
            parts.append(f"mejor mercado {_short_market(best[0])} {_colored(_r(best[1]['mean']), _tone(best[1]['mean']))}")
        self.summary.setText("  ·  ".join(parts))

    def _paint_curve(self, main: Ops) -> None:
        self.curve_plot.setBackground(theme.CHART_BG)
        for side in ("left", "bottom"):
            axis = self.curve_plot.getPlotItem().getAxis(side)
            axis.setPen(pg.mkPen(theme.CHART_GRID or theme.BORDER))
            axis.setTextPen(pg.mkPen(theme.CHART_TEXT))
        self.zero.setPen(pg.mkPen(theme.MUTED, style=Qt.PenStyle.DashLine))
        if not len(main):
            self.curve.setData([], [])
            self.curve_card.note.setText("sin operaciones")
            return
        xs, ys = main.curve()
        color = theme.BULL if ys[-1] > 0 else theme.BEAR if ys[-1] < 0 else theme.MUTED
        fill = pg.mkBrush(theme.mix(theme.CHART_BG, color, 0.25))
        self.curve.setData(xs, ys, pen=pg.mkPen(color, width=2), fillLevel=0, brush=fill)
        self.curve_card.note.setText(f"R neto acumulado: {ys[-1]:+.0f} R al final")

    def _fill_rows(self, book: Book, rows: list[tuple[str, dict]], name=lambda n: str(n)) -> None:
        book.empty_text = "Sin operaciones con este patrón, filtro y selección"
        book.set_rows([[(name(k), None if s.get("n") else theme.MUTED)] + metric_cells(s) for k, s in rows])

    def _fill_ops(self, book: Book, groups: list[tuple[object, Ops]], name=lambda n: str(n)) -> None:
        self._fill_rows(book, [(k, o.stats()) for k, o in groups], name)

    def _fill_markets(self, g: Group, markets: list[tuple[str, Ops]]) -> None:
        rows = sorted(((m, o.stats()) for m, o in markets), key=lambda x: -(x[1].get("mean") or -9))
        self._fill_rows(self.by_market, rows, _short_market)
        self.by_market.note.setText(f"{len(rows)} mercado{'s' if len(rows) != 1 else ''} de {g.name.lower()}")
        played = [x for x in rows if x[1].get("n")]
        enough = _ranked(rows, lambda x: x[1].get("n", 0))
        best = max(enough, key=lambda x: x[1]["mean"], default=None)
        worst = min(enough, key=lambda x: x[1]["mean"], default=None)
        most = max(played, key=lambda x: x[1]["n"], default=None)
        for i, (pick, color, sub) in enumerate((
                (best, theme.BULL, lambda s: f"{_r(s.get('mean'))} · t {_num(s.get('t'), 1, sign=True)}"),
                (worst, theme.BEAR, lambda s: f"{_r(s.get('mean'))} · t {_num(s.get('t'), 1, sign=True)}"),
                (most, theme.WARN, lambda s: f"{miles(int(s['n']))} ops"))):
            if pick is None:
                self.by_market.set_highlight(i, "-", "", color)
            else:
                self.by_market.set_highlight(i, _short_market(pick[0]), sub(pick[1]), color)

    def _fill_compare(self, g: Group) -> None:
        if not self.backtest or g.is_calendar:
            return
        since = {m.get("mercado"): str(m.get("desde (NY)") or "")[:4] for grp in self.backtest.groups_of(g.profile)
                 for m in grp.markets}
        rows = []
        for market, group_name, ops in self.backtest.compare(self.filter, self.years, self.hours, g.profile):
            s = ops.stats()
            gross = float((ops["r"] + ops["k"]).mean()) if len(ops) else None
            rows.append((market, group_name, s, gross))
        rows.sort(key=lambda x: -(x[2].get("mean") if x[2].get("n") else -9))
        self.compare.note.setText(f"{g.all_filters.get(self.filter, self.filter).lower()}, ambos patrones · en negrita, "
                                  f"{g.name.lower()}" + (" · filtrado" if self.years or self.hours else ""))
        out = []
        for market, group_name, s, gross in rows:
            mine = group_name == g.name
            name = _short_market(market)
            if self.backtest.note(market):
                name += f'  <span style="color:{theme.WARN}">*</span>'
            if not s.get("n"):
                out.append([(name, theme.MUTED), (since.get(market, ""), theme.MUTED)] + [("-", theme.MUTED)] * 7)
                continue
            out.append([(f"<b>{name}</b>" if mine else name, None if mine else theme.MUTED),
                        (since.get(market, ""), theme.MUTED), (miles(int(s["n"])), None), (f"{s['wr']:.1f} %", None),
                        (_r(gross), _tone(gross)), (_r(s["mean"]), _tone(s["mean"])),
                        (f"{s['total']:+.0f} R", _tone(s["total"])), (_num(s.get("pf")), _pf_tone(s.get("pf"))),
                        (_num(s.get("t"), 1, sign=True), _t_tone(s.get("t")))])
        self.compare.empty_text = "Sin operaciones con este filtro y selección"
        self.compare.set_rows(out)
        enough = _ranked(rows, lambda x: x[2].get("n", 0))
        best = max(enough, key=lambda x: x[2]["mean"], default=None)
        worst = min(enough, key=lambda x: x[2]["mean"], default=None)
        for i, (pick, color) in enumerate(((best, theme.BULL), (worst, theme.BEAR))):
            if pick is None:
                self.compare.set_highlight(i, "-", "", color)
            else:
                self.compare.set_highlight(i, _short_market(pick[0]), f"{_r(pick[2]['mean'])} · {pick[1]}", color)
        mine = [o for _m, grp, o in self.backtest.compare(self.filter, self.years, self.hours, g.profile) if grp == g.name and len(o)]
        if mine:
            k = np.concatenate([o["k"] for o in mine])
            gross = float(np.concatenate([o["r"] + o["k"] for o in mine]).mean())
            self.compare.set_highlight(2, f"{k.mean():.3f} R", f"{g.name} · sin costes {_r(gross)}", theme.WARN)
        else:
            self.compare.set_highlight(2, "-", "", theme.WARN)

    def _fill_outcomes(self, outcomes: list[tuple[str, Ops]]) -> None:
        self.outcomes.note.setText("las operaciones elegidas" + (" (filtradas)" if self.years or self.hours else ""))
        rows = []
        for pattern, ops in outcomes:
            n = len(ops)
            names = ops.names("o") if n else np.asarray([])

            def share(result):
                c = int((names == result).sum())
                return f"{miles(c)} ({100 * c / n:.0f} %)" if n else "-"

            rows.append([(pattern, None if n else theme.MUTED), (share("objetivo"), theme.BULL), (share("stop"), theme.BEAR),
                         (share("breakeven"), theme.MUTED), (share("tiempo"), theme.WARN), (_unit(_mean(ops, "mae"), 2, " R"), None),
                         (_unit(_mean(ops, "mfe"), 2, " R"), None), (_unit(_mean(ops, "v"), 0), None),
                         (_unit(_mean(ops, "rk"), 2, " %"), None), (_unit(_mean(ops, "k"), 3, " R"), theme.BEAR)])
        self.outcomes.set_rows(rows)

    def _fill_improvements(self, g: Group) -> None:
        rows = []
        for r in g.table("mejoras"):
            rows.append([(r.get("mejora", ""), None), (f"x{r.get('stop (x original)'):g}", None), (f"{r.get('RR'):g}", None),
                         (miles(int(r.get("n") or 0)), None), ("-" if r.get("wr") is None else f"{r['wr']:.1f} %", None),
                         (_r(r.get("R bruto medio")), _tone(r.get("R bruto medio"))),
                         (_r(r.get("R neto medio")), _tone(r.get("R neto medio"))),
                         (_num(r.get("estadístico t"), 1, sign=True), _t_tone(r.get("estadístico t"))),
                         (_r(r.get("R neto 1ª mitad")), _tone(r.get("R neto 1ª mitad"))),
                         (_r(r.get("R neto 2ª mitad")), _tone(r.get("R neto 2ª mitad")))])
        self.improvements.empty_text = "Sin hoja de mejoras en este backtest"
        self.improvements.set_rows(rows)

    def _fill_funnel(self, g: Group) -> None:
        rows = []
        for r in g.table("embudo"):
            if self.pattern not in ("Ambos", r.get("patrón")):
                continue
            pct = r.get("% entradas sobre TBR")
            act = r.get("% entradas sobre activadas")
            rows.append([(f"{_short_market(r.get('mercado', ''))} · {r.get('patrón', '')}", None),
                         (_count(r.get("TBR evaluadas")), theme.MUTED), (_count(r.get("activadas")), None),
                         (_count(r.get("entrada")), theme.ACCENT), (_count(r.get("vencida")), None),
                         (_count(r.get("invalidada")), None),
                         ("-" if pct is None else f"{pct:.0f} %", None), ("-" if act is None else f"{act:.0f} %", None)])
        self.funnel.set_rows(rows)

    def _fill_data(self, g: Group) -> None:
        self.data_book.set_rows([[(_short_market(m.get("mercado", "")), None), (_count(m.get("velas M15")), None),
                                  (str(m.get("desde (NY)") or "-"), theme.MUTED), (str(m.get("hasta (NY)") or "-"), theme.MUTED),
                                  (_count(m.get("TBR evaluadas")), None)] for m in g.markets])
