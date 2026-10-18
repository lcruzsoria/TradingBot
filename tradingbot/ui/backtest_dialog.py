"""Backtest de los patrones en una ventana flotante, con el mismo estilo que Forwardtest.

Arriba se eligen el grupo de mercados, el patrón y el filtro (lo que opera el bot, a favor del sesgo o sin filtro); debajo, el
veredicto, las cifras clave, la curva de R acumulado, las barras por año y por hora, y los «libros»: comparativa entre mercados,
por mercado, zona, lado, filtro, día, mitades, sensibilidad, mejoras, embudo y la metodología. Los datos los carga la skill Stats.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pyqtgraph as pg
from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtWidgets import (QButtonGroup, QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout,
                               QWidget)

from ..skills.stats.backtest import BOT_FILTER, MAIN_FILTERS, PATTERNS, Backtest, Group, verdict
from . import theme
from .fmt import miles
from .stats_dialog import Book, Tile

DAY_ORDER = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
SIDE_NAMES = {"long": "▲ LARGO", "short": "▼ CORTO"}
METRIC_HEADERS = ("Ops", "Acierto", "R medio", "R total", "PF", "Máx. DD", "t")
BREAKEVEN_2R = 100 / 3                     # con objetivo 2R se empata ganando 1 de cada 3


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


# -- piezas de la ventana --------------------------------------------------------------------------
class BarCard(Book):
    """Tarjeta con un gráfico de barras: verde si el valor es positivo, rojo si es negativo."""

    def __init__(self, title: str, note: str) -> None:
        super().__init__(title, note, ())
        self.plot = pg.PlotWidget()
        self.plot.setFixedHeight(120)
        pi = self.plot.getPlotItem()
        pi.setMenuEnabled(False)
        pi.hideButtons()
        pi.getViewBox().setMouseEnabled(x=False, y=False)
        self.zero = pg.InfiniteLine(0, angle=0, movable=False)
        pi.addItem(self.zero, ignoreBounds=True)
        self.bars: pg.BarGraphItem | None = None
        self.layout().addWidget(self.plot)
        self.values: list[float] = []
        self.base_note = note

    def set_bars(self, labels: list[str], values: list[float | None]) -> None:
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
        self.values = [v or 0.0 for v in values]
        self.note.setText(self.base_note if self.values else "sin datos para este patrón y filtro")
        if not self.values:
            return
        brushes = [pg.mkBrush(theme.BULL if v > 0 else theme.BEAR if v < 0 else theme.MUTED) for v in self.values]
        self.bars = pg.BarGraphItem(x=list(range(len(self.values))), height=self.values, width=0.7, brushes=brushes,
                                    pen=pg.mkPen(None))
        pi.addItem(self.bars)
        step = max(1, len(labels) // 14)
        pi.getAxis("bottom").setTicks([[(i, lab) for i, lab in enumerate(labels) if i % step == 0]])
        if self.values:
            pi.setXRange(-0.6, len(self.values) - 0.4, padding=0)


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
        self.pattern = PATTERNS[0]
        self.filter = MAIN_FILTERS[0]

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

        # Selectores: mercados, patrón y filtro
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

        self.by_year = BarCard("Por año", "R total de cada año")
        self.by_hour = BarCard("Por hora de entrada", "R medio por operación, hora de Nueva York (sin filtro)")
        self.compare = Book("Comparativa entre mercados", "", ("Mercado", "Desde", "Ops", "Acierto", "R bruto",
                                                               "R neto", "R total", "PF", "t"),
                            highlights=("Mejor mercado", "Peor mercado", "Coste medio del grupo"))
        self.by_market = Book("Por mercado", "", ("Mercado",) + METRIC_HEADERS,
                              highlights=("Mejor mercado", "Peor mercado", "Más operaciones"))
        self.by_zone = Book("Por zona (TBR)", "la TBR donde se dio la entrada", ("Zona",) + METRIC_HEADERS)
        self.by_side = Book("Por lado", "largos contra cortos", ("Lado",) + METRIC_HEADERS)
        self.by_filter = Book("Por filtro", "el mismo patrón con cada filtro del backtest", ("Filtro",) + METRIC_HEADERS)
        self.by_day = Book("Por día de la semana", "día de la entrada (sin filtro)", ("Día",) + METRIC_HEADERS)
        self.halves = Book("Robustez", "el histórico partido en dos por la mediana de las fechas", ("Mitad",) + METRIC_HEADERS)
        self.sensitivity = Book("Sensibilidad", "otros objetivos y tiempos máximos con las mismas entradas",
                                ("Variante",) + METRIC_HEADERS)
        self.improvements = Book("Mejoras (stop y RR)", "siempre con las reglas del bot; stop k veces el original",
                                 ("Mejora", "Stop", "RR", "Ops", "Acierto", "R bruto", "R neto", "t", "1ª mitad", "2ª mitad"))
        self.funnel = Book("Embudo", "de las TBR evaluadas a las entradas", ("Mercado · patrón", "TBR", "Activadas", "Entradas",
                                                                             "Vencidas", "Invalidadas", "% TBR", "% activadas"))
        self.outcomes = Book("Cómo terminan", "operaciones sin filtro", ("Patrón", "Objetivo", "Stop", "Tiempo", "MAE",
                                                                         "MFE", "Velas", "Riesgo %", "Coste"))
        self.data_book = Book("Datos", "velas M15 de MT5 usadas", ("Mercado", "Velas", "Desde", "Hasta", "TBR"))
        for book in (self.by_year, self.by_hour, self.compare, self.by_market, self.by_zone, self.by_side, self.by_filter,
                     self.by_day, self.halves, self.sensitivity, self.improvements, self.funnel, self.outcomes, self.data_book):
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
        self.reload_btn.setToolTip("Vuelve a leer el resumen del backtest (tras regenerarlo con scripts/exportar_backtest.py)")
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

    def _build_group_chips(self) -> None:
        while self.group_row.count():
            w = self.group_row.takeAt(0).widget()
            if w is not None:
                w.deleteLater()
        self.group_btns.clear()
        self.group_btn_group = QButtonGroup(self)
        for g in self.backtest.groups if self.backtest else []:
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
        self._build_group_chips()
        self._chips_for = ""
        if backtest and backtest.groups:
            self.set_group(self.group_key if backtest.group(self.group_key) else backtest.groups[0].key)
        else:
            self.refresh()

    def set_group(self, key: str) -> None:
        self.group_key = key
        g = self.group
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
            self.empty.setText(self.error or "No hay resultados de backtest cargados.\nGenera el resumen con "
                                             "scripts/exportar_backtest.py y pulsa Recargar.")
            self.generated.setText("")
            return
        for key, btn in self.group_btns.items():
            btn.setChecked(key == self.group_key)
        if self._chips_for != g.key:
            self._chips_for = g.key
            self.pattern_btns = self._chips(self.pattern_row, g.patterns, self.set_pattern, self.pattern)
            self.filter_btns = self._chips(self.filter_row, g.filters, self.set_filter, self.filter, g.filters)
            if BOT_FILTER in self.filter_btns:
                self.filter_btns[BOT_FILTER].setToolTip("No va contra el sesgo (GO de Cortex), una sola posición abierta a "
                                                        "la vez y una TBR, un trade: lo que haría el bot")
        self.subtitle.setText(g.description)
        own = "patrones" in g.raw
        self.by_hour.base_note = "R medio por operación, hora de Nueva York" + ("" if own else " (sin filtro)")
        self.by_day.note.setText("día de la entrada, misma hora, stop y RR" if own else "día de la entrada (sin filtro)")
        self.outcomes.note.setText("con la configuración del bot" if own else "operaciones sin filtro")
        for key, btn in self.pattern_btns.items():
            btn.setChecked(key == self.pattern)
        for key, btn in self.filter_btns.items():
            btn.setChecked(key == self.filter)
        self.generated.setText(f"{g.period} · actualizado {g.updated}" if g.updated else g.period)
        row = g.row(self.pattern, self.filter)
        self._paint_head(g, row)
        self._paint_curve(g.curve(self.pattern, self.filter))
        years = sorted(g.rows("por_anio", self.pattern, self.filter), key=lambda r: r.get("año") or 0)
        self.by_year.set_bars([str(r.get("año")) for r in years], [r.get("total") for r in years])
        hours = sorted(g.breakdown("por_hora", "hora (NY)", self.pattern, self.filter), key=lambda r: r.get("hora (NY)") or 0)
        self.by_hour.set_bars([f"{r.get('hora (NY)'):02d}" for r in hours], [r.get("mean") for r in hours])
        self._fill_compare(g)
        self._fill_markets(g)
        self._fill(self.by_zone, g.breakdown("por_zona", "zona", self.pattern, self.filter), "zona")
        self._fill(self.by_side, g.breakdown("por_direccion", "dirección", self.pattern, self.filter), "dirección",
                   lambda n: _colored(SIDE_NAMES.get(n, n), theme.BULL if n == "long" else theme.BEAR))
        self._fill_filters(g)
        days = sorted(g.breakdown("por_dia", "día semana", self.pattern, self.filter),
                      key=lambda r: DAY_ORDER.index(r["día semana"]) if r.get("día semana") in DAY_ORDER else 9)
        self._fill(self.by_day, days, "día semana", lambda n: n.capitalize())
        self._fill(self.halves, g.rows("mitades", self.pattern, self.filter), "mitad")
        self._fill(self.sensitivity, g.rows("sensibilidad", self.pattern, self.filter), "variante")
        self._fill_improvements(g)
        self._fill_funnel(g)
        self._fill_outcomes(g)
        self._fill_data(g)
        self.method_text.setText("<br>".join(f"<b>{t}</b>: {e}" for t, e in g.table("metodologia")))

    def _paint_head(self, g: Group, r: dict | None) -> None:
        b = self.blocks
        if not r or not r.get("n"):
            for tile in b.values():
                tile.set_value("-", "")
            self.verdict.setText("Sin operaciones con este patrón y filtro")
            self.summary.setText("")
            return
        text, sign = verdict(r.get("t"), r.get("mean"))
        color = theme.BULL if sign > 0 else theme.BEAR if sign < 0 else theme.WARN
        self.verdict.setStyleSheet(f"QLabel#Verdict {{ border: 1px solid {color}; border-left: 4px solid {color}; "
                                   f"border-radius: 4px; padding: 7px 10px; background: {theme.mix(theme.PANEL, color, 0.10)}; }}")
        mean = r.get("mean") or 0
        per_100 = f"{mean * 100:+.1f} R cada 100 operaciones"
        self.verdict.setText(f"<b style='color:{color}'>{text}</b>  ·  {self.pattern}, {g.all_filters.get(self.filter, self.filter).lower()}, "
                             f"{g.name.lower()}: {per_100} (t {_num(r.get('t'), 2, sign=True)})")
        wr = r.get("wr")
        b["n"].set_value(miles(int(r["n"])), f"{len(g.markets)} mercado{'s' if len(g.markets) != 1 else ''} · {g.period}")
        own = "patrones" in g.raw                       # Calendario: cierres por tiempo, no hay un equilibrio fijo
        b["wr"].set_value("-" if wr is None else f"{wr:.1f} %",
                          "con R neto positivo" if own else f"equilibrio {BREAKEVEN_2R:.1f} % con 2R",
                          theme.BULL if wr and wr > BREAKEVEN_2R + 1 else None)
        b["mean"].set_value(_r(r.get("mean")), f"t {_num(r.get('t'), 2, sign=True)}", _tone(r.get("mean")))
        b["total"].set_value(f"{r['total']:+.0f} R", "suma de todas", _tone(r.get("total")))
        b["pf"].set_value(_num(r.get("pf")), "ganado / perdido", _pf_tone(r.get("pf")))
        b["dd"].set_value(f"{r['dd']:.0f} R" if r.get("dd") else "0 R", f"racha perdedora {r.get('streak') or '-'}",
                          theme.BEAR if r.get("dd") else None)
        gross = next((v for v in g.rows("sensibilidad", self.pattern, self.filter) if "sin costes" in v.get("variante", "")),
                     None)
        outcomes = [o for o in g.table("resultados") if self.pattern in ("Ambos", o.get("patrón"))]
        cost = (sum((o.get("coste medio (R)") or 0) * (o.get("n") or 0) for o in outcomes) /
                max(1, sum(o.get("n") or 0 for o in outcomes))) if outcomes else None
        parts = [f"ganada media {_colored(_r(r.get('avg_win')), theme.BULL)}",
                 f"perdida media {_colored(_r(r.get('avg_loss')), theme.BEAR)}"]
        if gross:
            parts.append(f"sin costes {_colored(_r(gross.get('mean')), _tone(gross.get('mean')))}")
        if cost is not None:
            parts.append(f"coste medio {_colored(f'{cost:.3f} R', theme.BEAR)} por operación")
        best = max(g.rows("por_mercado", self.pattern, self.filter), key=lambda x: x.get("mean") or -9, default=None)
        if best:
            parts.append(f"mejor mercado {_short_market(best['mercado'])} {_colored(_r(best.get('mean')), _tone(best.get('mean')))}")
        self.summary.setText("  ·  ".join(parts))

    def _paint_curve(self, pts: list[tuple[str, float]]) -> None:
        self.curve_plot.setBackground(theme.CHART_BG)
        for side in ("left", "bottom"):
            axis = self.curve_plot.getPlotItem().getAxis(side)
            axis.setPen(pg.mkPen(theme.CHART_GRID or theme.BORDER))
            axis.setTextPen(pg.mkPen(theme.CHART_TEXT))
        self.zero.setPen(pg.mkPen(theme.MUTED, style=Qt.PenStyle.DashLine))
        if not pts:
            self.curve.setData([], [])
            self.curve_card.note.setText("sin curva para este filtro")
            return
        xs = [datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() for d, _ in pts]
        ys = [v for _, v in pts]
        color = theme.BULL if ys[-1] > 0 else theme.BEAR if ys[-1] < 0 else theme.MUTED
        fill = pg.mkBrush(theme.mix(theme.CHART_BG, color, 0.25))
        self.curve.setData(xs, ys, pen=pg.mkPen(color, width=2), fillLevel=0, brush=fill)
        self.curve_card.note.setText(f"R neto acumulado: {ys[-1]:+.0f} R al final")

    def _fill(self, book: Book, rows: list[dict], key: str, name=lambda n: str(n)) -> None:
        book.empty_text = "Sin datos para este patrón y filtro"
        book.set_rows([[(name(r.get(key)), None)] + metric_cells(r) for r in rows])

    def _fill_markets(self, g: Group) -> None:
        rows = sorted(g.rows("por_mercado", self.pattern, self.filter), key=lambda r: -(r.get("mean") or -9))
        self._fill(self.by_market, rows, "mercado", _short_market)
        self.by_market.note.setText(f"{len(rows)} mercado{'s' if len(rows) != 1 else ''} de {g.name.lower()}")
        played = [r for r in rows if r.get("n")]
        best = max(played, key=lambda r: r.get("mean") or -9, default=None)
        worst = min(played, key=lambda r: r.get("mean") or 9, default=None)
        most = max(played, key=lambda r: r.get("n") or 0, default=None)
        for i, (pick, color, sub) in enumerate(((best, theme.BULL, lambda r: f"{_r(r.get('mean'))} · t {_num(r.get('t'), 1, sign=True)}"),
                                                (worst, theme.BEAR, lambda r: f"{_r(r.get('mean'))} · t {_num(r.get('t'), 1, sign=True)}"),
                                                (most, theme.WARN, lambda r: f"{miles(int(r['n']))} ops"))):
            if pick is None:
                self.by_market.set_highlight(i, "-", "", color)
            else:
                self.by_market.set_highlight(i, _short_market(pick["mercado"]), sub(pick), color)

    def _fill_compare(self, g: Group) -> None:
        comp = self.backtest.comparison if self.backtest else {}
        bot = self.filter != "sin filtro de sesgo"           # la comparativa solo tiene «lo que opera el bot» y «sin filtro»
        rows = comp.get("bot" if bot else "sin_filtro") or []
        self.compare.note.setText(("lo que opera el bot" if bot else "sin filtro") + f", ambos patrones · en negrita, {g.name.lower()}")
        out = []
        for r in sorted(rows, key=lambda r: -(r.get("R neto medio") or -9)):
            mine = r.get("grupo") == g.name
            name = _short_market(r.get("mercado", ""))
            if r.get("nota"):
                name += f'  <span style="color:{theme.WARN}">*</span>'
            out.append([(f"<b>{name}</b>" if mine else name, None if mine else theme.MUTED),
                        (str(r.get("desde", ""))[:4], theme.MUTED),
                        (miles(int(r.get("n") or 0)), None),
                        ("-" if r.get("wr") is None else f"{r['wr']:.1f} %", None),
                        (_r(r.get("R bruto medio")), _tone(r.get("R bruto medio"))),
                        (_r(r.get("R neto medio")), _tone(r.get("R neto medio"))),
                        ("-" if r.get("R neto total") is None else f"{r['R neto total']:+.0f} R", _tone(r.get("R neto total"))),
                        (_num(r.get("pf")), _pf_tone(r.get("pf"))),
                        (_num(r.get("t"), 1, sign=True), _t_tone(r.get("t")))])
        self.compare.empty_text = "Sin comparativa (ejecuta scripts/comparativa_mercados.py y exporta de nuevo)"
        self.compare.set_rows(out)
        played = [r for r in rows if r.get("n")]
        best = max(played, key=lambda r: r.get("R neto medio") or -9, default=None)
        worst = min(played, key=lambda r: r.get("R neto medio") or 9, default=None)
        for i, (pick, color) in enumerate(((best, theme.BULL), (worst, theme.BEAR))):
            if pick is None:
                self.compare.set_highlight(i, "-", "", color)
            else:
                self.compare.set_highlight(i, _short_market(pick["mercado"]), f"{_r(pick.get('R neto medio'))} · {pick['grupo']}",
                                           color)
        mine = next((r for r in comp.get("por_grupo") or [] if r.get("grupo") == g.name and "bot" in r.get("caso", "")), None)
        if mine:
            self.compare.set_highlight(2, f"{mine.get('coste medio (R)'):.3f} R", f"{g.name} · sin costes "
                                       f"{_r(mine.get('R bruto medio'))}", theme.WARN)
        else:
            self.compare.set_highlight(2, "-", "", theme.WARN)

    def _fill_filters(self, g: Group) -> None:
        rows = []
        for filt, name in g.all_filters.items():
            r = g.row(self.pattern, filt)
            label = f"<b>{name}</b>" if filt == self.filter else name
            rows.append([(label, None if r and r.get("n") else theme.MUTED)] + metric_cells(r))
        self.by_filter.set_rows(rows)

    def _fill_improvements(self, g: Group) -> None:
        rows = []
        for r in g.table("mejoras"):
            rows.append([(r.get("mejora", ""), None), (f"x{r.get('stop (x original)'):g}", None), (f"{r.get('RR'):g}", None),
                         (miles(int(r.get("n") or 0)), None), ("-" if r.get("wr") is None else f"{r['wr']:.1f} %", None),
                         (_r(r.get("R bruto medio")), _tone(r.get("R bruto medio"))),
                         (_r(r.get("R neto medio")), _tone(r.get("R neto medio"))),
                         (_num(r.get("t"), 1, sign=True), _t_tone(r.get("t"))),
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
                         (miles(int(r.get("TBR evaluadas") or 0)), theme.MUTED), (miles(int(r.get("activadas") or 0)), None),
                         (miles(int(r.get("entrada") or 0)), theme.ACCENT), (miles(int(r.get("vencida") or 0)), None),
                         (miles(int(r.get("invalidada") or 0)), None),
                         ("-" if pct is None else f"{pct:.0f} %", None), ("-" if act is None else f"{act:.0f} %", None)])
        self.funnel.set_rows(rows)

    def _fill_outcomes(self, g: Group) -> None:
        rows = []
        for r in g.table("resultados"):
            if self.pattern not in ("Ambos", r.get("patrón")):
                continue
            n = r.get("n") or 0

            def share(k):
                return f"{miles(int(r.get(k) or 0))} ({100 * (r.get(k) or 0) / n:.0f} %)" if n else "-"

            rows.append([(r.get("patrón", ""), None), (share("objetivo"), theme.BULL), (share("stop"), theme.BEAR),
                         (share("tiempo"), theme.WARN), (_unit(r.get("MAE medio (R)"), 2, " R"), None),
                         (_unit(r.get("MFE medio (R)"), 2, " R"), None),
                         (_unit(r.get("velas medias en la operación"), 0), None),
                         (_unit(r.get("riesgo medio %"), 2, " %"), None),
                         (_unit(r.get("coste medio (R)"), 3, " R"), theme.BEAR)])
        self.outcomes.set_rows(rows)

    def _fill_data(self, g: Group) -> None:
        self.data_book.set_rows([[(_short_market(m.get("mercado", "")), None), (_count(m.get("velas M15")), None),
                                  (str(m.get("desde (NY)") or "-"), theme.MUTED), (str(m.get("hasta (NY)") or "-"), theme.MUTED),
                                  (_count(m.get("TBR evaluadas")), None)] for m in g.markets])
        # Libros sin datos en este grupo (p. ej. zonas o embudo en Calendario): fuera
        for book, sheet in ((self.by_zone, "por_zona"), (self.funnel, "embudo"), (self.improvements, "mejoras"),
                            (self.by_hour, "por_hora"), (self.by_day, "por_dia"), (self.outcomes, "resultados")):
            book.setVisible(bool(g.table(sheet)))
        comp = self.backtest.comparison if self.backtest else {}
        self.compare.setVisible(any(r.get("grupo") == g.name for r in comp.get("bot") or []))
