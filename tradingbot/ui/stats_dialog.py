"""Estadísticas de la sesión: decisiones de Cortex y resultado de las operaciones simuladas de Setup, en una ventana flotante.

Arriba, las cifras clave y una línea de resumen; debajo, la curva de R acumulado y los «libros»: el mismo resultado partido por
patrón, lado, sesión, mercado y sesgo, y el diario con cada operación.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable

import pyqtgraph as pg
from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (QButtonGroup, QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from ..clock import NY
from ..skills.stats.session import ALIGNMENTS, SESSIONS, Group, Trade, TradeStats, alignment_of, session_of  # noqa: F401
from ..timeframes import display_label
from . import theme
from .fmt import fecha_hora

RESULT_NAMES = {"objetivo": "Objetivo", "stop": "Stop", "tiempo": "Tiempo"}
WINDOWS = (("Hoy", 0), ("7 días", 7), ("Todo", None))       # días hacia atrás (en fecha de Nueva York) o None: todo


# -- formato ---------------------------------------------------------------------------------------
def _r(value: float | None, digits: int = 2) -> str:
    return "-" if value is None else f"{value:+.{digits}f} R"


def _pct(value: float | None) -> str:
    return "-" if value is None else f"{value:+.2f} %"


def _tone(value: float | None) -> str | None:
    if not value:
        return None
    return theme.BULL if value > 0 else theme.BEAR


def _span(seconds: float | None) -> str:
    if seconds is None:
        return "-"
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"{minutes} min"
    return f"{minutes // 60} h {minutes % 60:02d} min"


def _colored(text: str, color: str | None) -> str:
    return f'<span style="color:{color}">{text}</span>' if color else text


def _ny_today() -> datetime:
    if NY is not None:
        return datetime.now(NY).replace(tzinfo=None)
    return datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=5)


# -- piezas de la ventana --------------------------------------------------------------------------
class Tile(QFrame):
    """Cifra clave de la fila de arriba: etiqueta pequeña, valor grande y nota."""

    def __init__(self, label: str) -> None:
        super().__init__()
        self.setObjectName("StatTile")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 7, 10, 8)
        lay.setSpacing(1)
        self.label = QLabel(label)
        self.label.setObjectName("StatLabel")
        self.value = QLabel("-")
        self.value.setObjectName("TileValue")
        self.sub = QLabel("")
        self.sub.setObjectName("StatSub")
        for w in (self.label, self.value, self.sub):
            lay.addWidget(w)

    def set_value(self, value: str, sub: str = "", color: str | None = None) -> None:
        self.value.setText(value)
        self.value.setStyleSheet(f"color: {color};" if color else "")
        self.sub.setText(sub)


class Book(QFrame):
    """Tarjeta con título, nota a la derecha, unos destacados opcionales y una tabla de filas."""

    def __init__(self, title: str, note: str, headers: tuple[str, ...], highlights: bool | tuple[str, ...] = False) -> None:
        super().__init__()
        self.setObjectName("Card")
        self.headers = headers
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 11, 14, 10)
        lay.setSpacing(8)
        head = QHBoxLayout()
        t = QLabel(title.upper())
        t.setObjectName("BookTitle")
        n = QLabel(note)
        n.setObjectName("CardNote")
        head.addWidget(t)
        head.addStretch(1)
        head.addWidget(n)
        lay.addLayout(head)
        self.note = n
        self.highlights: list[tuple[QLabel, QLabel]] = []
        if highlights:
            row = QHBoxLayout()
            row.setSpacing(12)
            captions = highlights if isinstance(highlights, tuple) else ("Más ganadas", "Más perdidas", "Más operaciones")
            for caption in captions:
                box = QVBoxLayout()
                box.setSpacing(0)
                c = QLabel(caption.upper())
                c.setObjectName("BookHead")
                name, sub = QLabel("-"), QLabel("")
                name.setObjectName("BookStrong")
                sub.setObjectName("StatSub")
                for w in (c, name, sub):
                    box.addWidget(w)
                row.addLayout(box, 1)
                self.highlights.append((name, sub))
            lay.addLayout(row)
        self.grid = QGridLayout()
        self.grid.setHorizontalSpacing(14)
        self.grid.setVerticalSpacing(0)
        self.grid.setColumnStretch(0, 1)
        lay.addLayout(self.grid)
        self.rows: list[list[QLabel]] = []
        self.empty_text = "Sin operaciones en este periodo"

    def set_highlight(self, i: int, name: str, sub: str, color: str) -> None:
        label, note = self.highlights[i]
        label.setText(name)
        label.setStyleSheet(f"color: {color};" if name != "-" else "")
        note.setText(sub)

    def set_rows(self, rows: list[list[tuple[str, str | None]]]) -> None:
        """Cada fila: (texto, color) por columna. La primera columna va a la izquierda y el resto a la derecha."""
        while self.grid.count():
            w = self.grid.takeAt(0).widget()
            if w is not None:
                w.hide()                  # no esperar al deleteLater: al cambiar de filtro se verían las dos tablas
                w.deleteLater()
        self.rows = []
        for col, text in enumerate(self.headers):
            self._put(0, col, text, None, "BookHead")
        for i, row in enumerate(rows):
            line = QFrame()
            line.setObjectName("BookRule")
            line.setFixedHeight(1)
            self.grid.addWidget(line, 2 * i + 1, 0, 1, len(self.headers))
            self.rows.append([self._put(2 * i + 2, col, text, color, "BookName" if col == 0 else "BookCell")
                              for col, (text, color) in enumerate(row)])
        if not rows:
            self._put(1, 0, self.empty_text, None, "Muted")

    def _put(self, row: int, col: int, text: str, color: str | None, name: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName(name)
        label.setTextFormat(Qt.TextFormat.RichText if "<" in text else Qt.TextFormat.PlainText)
        if color:
            label.setStyleSheet(f"color: {color};")
        align = Qt.AlignmentFlag.AlignLeft if col == 0 else Qt.AlignmentFlag.AlignRight
        self.grid.addWidget(label, row, col, align | Qt.AlignmentFlag.AlignVCenter)
        return label


GROUP_HEADERS = ("G · P · N", "Ops", "Acierto", "R", "R medio", "% precio")


def group_cells(g: Group) -> list[tuple[str, str | None]]:
    """Columnas comunes de un libro para un grupo (sin el nombre)."""
    if not g.n:
        return [(f"{g.wins} {g.losses} {g.flat}", theme.MUTED), ("0", theme.MUTED)] + [("-", theme.MUTED)] * 4
    return [(f"{g.wins} {g.losses} {g.flat}", None), (str(g.n), None), (f"{g.win_rate:.0f} %", None),
            (_r(g.r), _tone(g.r)), (_r(g.mean), _tone(g.mean)), (_pct(g.pct), _tone(g.pct))]


# -- ventana ---------------------------------------------------------------------------------------
class StatsDialog(QDialog):
    """Ventana flotante (no modal) con las estadísticas; se abre y se cierra con el botón Estadísticas de la cabecera."""

    hidden = Signal()
    reset_requested = Signal()           # «Reiniciar»: las cifras las lleva la skill Stats, que es quien las borra

    def __init__(self, parent, stats: TradeStats, to_ny: Callable[[int], datetime],
                 symbols: Callable[[], list[str]] = lambda: [], today: Callable[[], datetime] = _ny_today) -> None:
        super().__init__(parent)
        self.setWindowTitle("Estadísticas")
        self.setWindowFlag(Qt.WindowType.Tool, True)      # flota sobre la ventana principal sin bloquearla
        self.setModal(False)
        self.resize(720, 880)
        self.stats, self._to_ny, self._symbols, self._today = stats, to_ny, symbols, today
        self.window_days: int | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 12, 14, 12)
        outer.setSpacing(10)

        # Cabecera: título y periodo
        head = QHBoxLayout()
        title = QLabel("Estadísticas · Simulación")
        title.setObjectName("Brand")
        sub = QLabel("operaciones de Setup tras el GO de Cortex")
        sub.setObjectName("Tiny")
        head.addWidget(title)
        head.addSpacing(8)
        head.addWidget(sub)
        head.addStretch(1)
        period = QLabel("Periodo")
        period.setObjectName("Tiny")
        head.addWidget(period)
        self.window_group = QButtonGroup(self)
        self.window_btns: dict[str, QPushButton] = {}
        for name, days in WINDOWS:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setProperty("chip", "true")
            btn.setToolTip("Operaciones con entrada " + ("hoy (fecha de Nueva York)" if days == 0 else
                                                          f"en los últimos {days} días" if days else "en toda la sesión del bot"))
            btn.setChecked(days is None)
            btn.clicked.connect(lambda _=False, d=days: self.set_window(d))
            self.window_group.addButton(btn)
            self.window_btns[name] = btn
            head.addWidget(btn)
        outer.addLayout(head)

        # Cifras clave
        tiles = QHBoxLayout()
        tiles.setSpacing(8)
        self.blocks: dict[str, Tile] = {}
        for key, label in (("trades", "Operaciones"), ("wlb", "G · P · N"), ("win", "Acierto"), ("total", "R total"),
                           ("pct", "% del precio"), ("dd", "Máx. drawdown")):
            tile = Tile(label)
            self.blocks[key] = tile
            tiles.addWidget(tile, 1)
        outer.addLayout(tiles)
        self.summary = QLabel()
        self.summary.setObjectName("Tiny")
        self.summary.setTextFormat(Qt.TextFormat.RichText)
        self.summary.setWordWrap(True)
        outer.addWidget(self.summary)

        # Contenido desplazable: curva, libros y diario
        body = QWidget()
        lay = QVBoxLayout(body)
        lay.setContentsMargins(0, 0, 4, 0)
        lay.setSpacing(10)

        curve_card = Book("Curva de R", "R acumulado tras cada cierre", ())
        self.curve_plot = pg.PlotWidget()
        self.curve_plot.setFixedHeight(130)
        pi = self.curve_plot.getPlotItem()
        pi.setMenuEnabled(False)
        pi.hideButtons()
        pi.getViewBox().setMouseEnabled(x=False, y=False)
        self.curve = pi.plot([0.0])
        self.zero = pg.InfiniteLine(0, angle=0, movable=False)
        pi.addItem(self.zero, ignoreBounds=True)
        curve_card.layout().addWidget(self.curve_plot)
        lay.addWidget(curve_card)

        self.by_pattern = Book("Por patrón", "el patrón que dio la entrada", ("Patrón",) + GROUP_HEADERS, highlights=True)
        self.by_side = Book("Por lado", "largos contra cortos", ("Lado",) + GROUP_HEADERS)
        self.by_session = Book("Por sesión", "la sesión a la hora de entrada (NY)", ("Sesión",) + GROUP_HEADERS)
        self.by_symbol = Book("Por mercado", "todos los mercados de la lista", ("Mercado",) + GROUP_HEADERS)
        self.by_bias = Book("Por sesgo", "el sesgo vigente al entrar", ("Sesgo",) + GROUP_HEADERS)
        for book in (self.by_pattern, self.by_side, self.by_session, self.by_symbol, self.by_bias):
            lay.addWidget(book)

        journal = Book("Diario", "las más recientes arriba", ())
        self.history = self._table(("Entrada (NY)", "Mercado", "Lado", "Patrón", "Sesión", "Salida", "Duración", "Resultado"))
        self.history.setMinimumHeight(220)
        journal.layout().addWidget(self.history)
        lay.addWidget(journal)
        lay.addStretch(1)

        scroll = QScrollArea()
        scroll.setObjectName("StatsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

        buttons = QHBoxLayout()
        note = QLabel("Resultados en R, sin spread. G · P · N: ganadas, perdidas y neutras (0 R). Se reinician al cerrar el bot.")
        note.setObjectName("Tiny")
        note.setWordWrap(True)
        self.reset_btn = QPushButton("Reiniciar")
        self.reset_btn.setToolTip("Borra las estadísticas de la sesión (las posiciones abiertas siguen su curso en Setup)")
        self.reset_btn.clicked.connect(self._reset)
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.hide)
        buttons.addWidget(note, 1)
        buttons.addWidget(self.reset_btn)
        buttons.addWidget(close_btn)
        outer.addLayout(buttons)
        self.refresh()

    @staticmethod
    def _table(headers: tuple[str, ...]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().hide()
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setShowGrid(False)
        table.horizontalHeader().setStretchLastSection(True)
        return table

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

    def reject(self) -> None:            # Esc o la X: se oculta y conserva su sitio
        self.hide()

    def _reset(self) -> None:
        self.stats.reset()                # se vacía ya la copia; la skill confirma con su próximo stats.session
        self.refresh()
        self.reset_requested.emit()

    def set_window(self, days: int | None) -> None:
        self.window_days = days
        for name, d in WINDOWS:
            self.window_btns[name].setChecked(d == days)
        self.refresh()

    # -- pintar ------------------------------------------------------------------------------
    def _ny_of(self, t: Trade) -> datetime | None:
        return self._to_ny(t.order.entry_ts) if t.order.entry_ts else None

    def _in_window(self, t: Trade) -> bool:
        if self.window_days is None:
            return True
        ny = self._ny_of(t)
        return ny is not None and (self._today().date() - ny.date()).days <= self.window_days

    def _session(self, t: Trade) -> str:
        ny = self._ny_of(t)
        return session_of(ny) if ny else "Sin hora"

    def refresh(self) -> None:
        s = self.stats.only(self._in_window)
        done, opened = s.done, s.open
        b = self.blocks
        b["trades"].set_value(str(len(done)), f"{len(opened)} abierta{'s' if len(opened) != 1 else ''}  ·  {s.by_time} por tiempo")
        b["wlb"].set_value(f"{s.wins} · {s.losses} · {s.flat}", "ganadas · perdidas · neutras")
        wr = s.win_rate
        b["win"].set_value("-" if wr is None else f"{wr:.0f} %", f"de {len(done)} cerradas" if done else "sin cerradas")
        b["total"].set_value(_r(s.total_r), f"media {_r(s.expectancy)}", _tone(s.total_r))
        b["pct"].set_value(_pct(s.total_pct if done else None), "suma por operación", _tone(s.total_pct))
        dd = s.max_drawdown
        b["dd"].set_value(f"{-dd:.2f} R" if dd else "0 R", "desde el máximo", theme.BEAR if dd else None)
        self.summary.setText(self._summary(s))

        self._paint_curve(s.equity)
        self._fill_patterns(s)
        self._fill(self.by_side, s.groups(lambda t: t.order.direction, ("long", "short")),
                   lambda n: _colored("▲ LARGO", theme.BULL) if n == "long" else _colored("▼ CORTO", theme.BEAR))
        self._fill(self.by_session, s.groups(self._session, SESSIONS))
        self._fill(self.by_symbol, s.groups(lambda t: t.order.symbol, self._symbols()))
        self._fill(self.by_bias, s.groups(lambda t: alignment_of(t.order), ALIGNMENTS))
        self._fill_history(s.trades)

    def _summary(self, s: TradeStats) -> str:
        if not s.done:
            parts = ["Aún no hay operaciones cerradas en este periodo"]
        else:
            pf = s.profit_factor
            pf_text = "∞" if pf == float("inf") else f"{pf:.2f}"
            best, worst = s.best_trade, s.worst_trade
            st = s.streak
            streak = _colored(f"{abs(st)}{'G' if st > 0 else 'P'}", _tone(st)) if st else "-"
            parts = [f"media {_colored(_r(s.expectancy), _tone(s.expectancy))}",
                     f"profit factor {_colored(pf_text, theme.BULL if pf > 1 else theme.BEAR if pf < 1 else None)}",
                     f"ganada media {_colored(_r(s.avg_win), theme.BULL) if s.avg_win else '-'}",
                     f"perdida media {_colored(_r(s.avg_loss), theme.BEAR) if s.avg_loss else '-'}",
                     f"mejor {_colored(_r(best.r), _tone(best.r))} {best.order.symbol}",
                     f"peor {_colored(_r(worst.r), _tone(worst.r))} {worst.order.symbol}",
                     f"racha {streak}",
                     f"duración media {_span(s.avg_duration)}"]
        evaluated = s.go + s.nogo
        cortex = (f"Cortex {_colored(f'{s.go} GO', theme.BULL)} / {_colored(f'{s.nogo} NO GO', theme.BEAR)}"
                  f" ({100 * s.go / evaluated:.0f} % aprobadas)" if evaluated else "Cortex: ninguna señal evaluada")
        return "  ·  ".join(parts + [cortex])

    def _fill(self, book: Book, groups: list[Group], name: Callable[[str], str] = lambda n: n) -> None:
        rows = []
        for g in groups:
            label = name(g.name)
            if g.open:
                label += f'  <span style="color:{theme.WARN}">· {g.open} abierta{"s" if g.open != 1 else ""}</span>'
            cells = group_cells(g)
            rows.append([(label, theme.MUTED if not g.n and not g.open else None)] + cells)
        book.set_rows(rows)

    def _fill_patterns(self, s: TradeStats) -> None:
        groups = s.groups(lambda t: t.order.pattern)
        self._fill(self.by_pattern, groups)
        played = [g for g in groups if g.n]
        for i, (pick, color, sub) in enumerate((
                (max(played, key=lambda g: (g.wins, g.r), default=None), theme.BULL, lambda g: f"{g.wins} G · {g.n} ops"),
                (max(played, key=lambda g: (g.losses, -g.r), default=None), theme.BEAR, lambda g: f"{g.losses} P · {g.n} ops"),
                (max(played, key=lambda g: (g.n, g.r), default=None), theme.WARN, lambda g: f"{g.n} ops · {_r(g.r)}"))):
            if pick is None or (i == 0 and not pick.wins) or (i == 1 and not pick.losses):
                self.by_pattern.set_highlight(i, "-", "", color)
            else:
                self.by_pattern.set_highlight(i, pick.name, sub(pick), color)

    def _paint_curve(self, equity: list[float]) -> None:
        self.curve_plot.setBackground(theme.CHART_BG)
        for side in ("left", "bottom"):
            axis = self.curve_plot.getPlotItem().getAxis(side)
            axis.setPen(pg.mkPen(theme.CHART_GRID or theme.BORDER))
            axis.setTextPen(pg.mkPen(theme.CHART_TEXT))
        last = equity[-1]
        color = theme.BULL if last > 0 else theme.BEAR if last < 0 else theme.MUTED
        self.curve.setData(list(range(len(equity))), equity, pen=pg.mkPen(color, width=2),
                           symbol="o", symbolSize=5, symbolBrush=color, symbolPen=None)
        self.zero.setPen(pg.mkPen(theme.MUTED, style=Qt.PenStyle.DashLine))

    def _cell(self, table: QTableWidget, row: int, col: int, text: str, color: str | None = None) -> None:
        item = QTableWidgetItem(text)
        if col:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if color:
            item.setForeground(QBrush(QColor(color)))
        table.setItem(row, col, item)

    def _fill_history(self, trades: list[Trade]) -> None:
        rows = sorted(trades, key=lambda t: t.order.entry_ts or 0, reverse=True)     # las más recientes arriba
        self.history.setRowCount(len(rows))
        for i, t in enumerate(rows):
            o = t.order
            when = fecha_hora(self._to_ny(o.entry_ts)) if o.entry_ts else "-"
            side_color = theme.BULL if o.direction == "long" else theme.BEAR
            self._cell(self.history, i, 0, when)
            self._cell(self.history, i, 1, f"{o.symbol} {display_label(o.timeframe)}")
            self._cell(self.history, i, 2, "Largo" if o.direction == "long" else "Corto", side_color)
            self._cell(self.history, i, 3, o.pattern)
            self._cell(self.history, i, 4, self._session(t))
            if t.closed:
                self._cell(self.history, i, 5, RESULT_NAMES.get(t.closed.result, t.closed.result))
                self._cell(self.history, i, 6, _span(t.duration))
                self._cell(self.history, i, 7, _r(t.r), _tone(t.r))
            else:
                self._cell(self.history, i, 5, "Abierta", theme.WARN)
                self._cell(self.history, i, 6, "-")
                self._cell(self.history, i, 7, "-")
        self.history.resizeColumnsToContents()
