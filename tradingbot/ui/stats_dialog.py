"""Estadísticas de la sesión: decisiones de Cortex y resultado de las operaciones simuladas de Setup, en una ventana flotante."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

import pyqtgraph as pg
from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (QDialog, QGridLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                               QTabWidget, QVBoxLayout, QWidget)

from ..timeframes import display_label
from . import theme
from .fmt import fecha_hora
from .widgets import StatBlock

RESULT_NAMES = {"objetivo": "Objetivo", "stop": "Stop", "tiempo": "Tiempo"}


@dataclass
class Trade:
    order: object                        # Order de Cortex
    closed: object | None = None         # Closed de Setup, o None mientras sigue abierta

    @property
    def r(self) -> float:
        return self.closed.r if self.closed else 0.0


@dataclass
class TradeStats:
    """Lo que ha pasado en la sesión: GO / NO GO de Cortex y las operaciones simuladas (se pierde al reiniciar el bot)."""
    go: int = 0
    nogo: int = 0
    trades: list[Trade] = field(default_factory=list)

    # -- registro ----------------------------------------------------------------------------
    def decision(self, allowed: bool) -> None:
        if allowed:
            self.go += 1
        else:
            self.nogo += 1

    def executed(self, order) -> None:
        self.trades.append(Trade(order))

    def closed(self, order, closed) -> None:
        if closed is None:
            return
        for t in self.trades:
            if t.order is order and t.closed is None:
                t.closed = closed
                return
        self.trades.append(Trade(order, closed))        # no la vimos entrar (p. ej. ventana creada después)

    def reset(self) -> None:
        self.go = self.nogo = 0
        self.trades.clear()

    # -- cifras ------------------------------------------------------------------------------
    @property
    def done(self) -> list[Trade]:
        """Cerradas, en orden de salida."""
        return sorted((t for t in self.trades if t.closed), key=lambda t: t.closed.exit_ts)

    @property
    def open(self) -> list[Trade]:
        return [t for t in self.trades if t.closed is None]

    @property
    def wins(self) -> int:
        return sum(1 for t in self.done if t.r > 0)

    @property
    def losses(self) -> int:
        return sum(1 for t in self.done if t.r < 0)

    @property
    def by_time(self) -> int:
        return sum(1 for t in self.done if t.closed.result == "tiempo")

    @property
    def win_rate(self) -> float | None:
        n = len(self.done)
        return 100 * self.wins / n if n else None

    @property
    def total_r(self) -> float:
        return sum(t.r for t in self.done)

    @property
    def total_pct(self) -> float:
        return sum(t.closed.pct for t in self.done)

    @property
    def expectancy(self) -> float | None:
        n = len(self.done)
        return self.total_r / n if n else None

    @property
    def profit_factor(self) -> float | None:
        gained = sum(t.r for t in self.done if t.r > 0)
        lost = -sum(t.r for t in self.done if t.r < 0)
        if lost:
            return gained / lost
        return float("inf") if gained else None

    @property
    def best(self) -> float | None:
        return max((t.r for t in self.done), default=None)

    @property
    def worst(self) -> float | None:
        return min((t.r for t in self.done), default=None)

    @property
    def equity(self) -> list[float]:
        """R acumulado tras cada cierre, empezando en 0."""
        out, acc = [0.0], 0.0
        for t in self.done:
            acc += t.r
            out.append(acc)
        return out

    @property
    def max_drawdown(self) -> float:
        """Mayor caída del R acumulado desde un máximo previo (en R, positiva)."""
        peak, dd = 0.0, 0.0
        for v in self.equity:
            peak = max(peak, v)
            dd = max(dd, peak - v)
        return dd

    @property
    def streak(self) -> int:
        """Racha actual: +n ganadas seguidas o -n perdidas seguidas (0 sin operaciones o si la última quedó en 0 R)."""
        n = 0
        for t in reversed(self.done):
            sign = (t.r > 0) - (t.r < 0)
            if sign == 0 or (n and (n > 0) != (sign > 0)):
                break
            n += sign
        return n

    def breakdown(self, key: Callable[[object], str]) -> list[tuple[str, int, int, float]]:
        """(nombre, cerradas, ganadas, R total) por grupo, de más a menos R."""
        rows: dict[str, list] = {}
        for t in self.done:
            row = rows.setdefault(key(t.order), [0, 0, 0.0])
            row[0] += 1
            row[1] += t.r > 0
            row[2] += t.r
        return sorted(((k, n, w, r) for k, (n, w, r) in rows.items()), key=lambda x: -x[3])


def _r(value: float | None, digits: int = 2) -> str:
    return "-" if value is None else f"{value:+.{digits}f} R"


def _tone(value: float | None) -> str | None:
    if not value:
        return None
    return theme.BULL if value > 0 else theme.BEAR


class StatsDialog(QDialog):
    """Ventana flotante (no modal) con las estadísticas; se abre y se cierra con el botón Estadísticas de la cabecera."""

    hidden = Signal()

    def __init__(self, parent, stats: TradeStats, to_ny: Callable[[int], datetime]) -> None:
        super().__init__(parent)
        self.setWindowTitle("Estadísticas")
        self.setWindowFlag(Qt.WindowType.Tool, True)      # flota sobre la ventana principal sin bloquearla
        self.setModal(False)
        self.resize(740, 720)
        self.stats, self._to_ny = stats, to_ny

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(12)
        intro = QLabel("Operaciones simuladas de esta sesión (Cortex da el GO y Setup las sigue hasta el stop, el objetivo "
                       "o el cierre por tiempo). Resultados en R, sin spread; se reinician al cerrar el bot.")
        intro.setObjectName("Muted")
        intro.setWordWrap(True)
        lay.addWidget(intro)

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(10)
        self.blocks: dict[str, StatBlock] = {}
        for i, (key, label) in enumerate((("trades", "Operaciones"), ("win", "Acierto"), ("total", "Resultado"),
                                          ("exp", "Expectativa"), ("pf", "Profit factor"), ("dd", "Máx. drawdown"),
                                          ("cortex", "Señales de Cortex"), ("best", "Mejor / peor"), ("streak", "Racha"))):
            block = StatBlock(label)
            self.blocks[key] = block
            grid.addWidget(block, i // 3, i % 3)
        lay.addLayout(grid)

        self.curve_plot = pg.PlotWidget()
        self.curve_plot.setFixedHeight(170)
        pi = self.curve_plot.getPlotItem()
        pi.setMenuEnabled(False)
        pi.hideButtons()
        pi.getViewBox().setMouseEnabled(x=False, y=False)
        pi.setLabel("left", "R acumulado")
        self.curve = pi.plot([0.0])
        self.zero = pg.InfiniteLine(0, angle=0, movable=False)
        pi.addItem(self.zero, ignoreBounds=True)
        lay.addWidget(self.curve_plot)

        self.tabs = QTabWidget()
        self.by_symbol = self._table(("Mercado", "Cerradas", "Ganadas", "Acierto", "Resultado"))
        self.by_pattern = self._table(("Patrón", "Cerradas", "Ganadas", "Acierto", "Resultado"))
        self.history = self._table(("Entrada (NY)", "Mercado", "Lado", "Patrón", "Salida", "Resultado"))
        self.tabs.addTab(self.history, "Operaciones")
        self.tabs.addTab(self.by_symbol, "Por mercado")
        self.tabs.addTab(self.by_pattern, "Por patrón")
        lay.addWidget(self.tabs, 1)

        buttons = QHBoxLayout()
        self.reset_btn = QPushButton("Reiniciar")
        self.reset_btn.setToolTip("Borra las estadísticas de la sesión (las posiciones abiertas siguen su curso en Setup)")
        self.reset_btn.clicked.connect(self._reset)
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.hide)
        buttons.addWidget(self.reset_btn)
        buttons.addStretch(1)
        buttons.addWidget(close_btn)
        lay.addLayout(buttons)
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
        self.stats.reset()
        self.refresh()

    # -- pintar ------------------------------------------------------------------------------
    def refresh(self) -> None:
        s = self.stats
        done, opened = s.done, s.open
        b = self.blocks
        b["trades"].set_value(str(len(done)), f"{len(opened)} abierta(s)  -  {s.by_time} por tiempo")
        wr = s.win_rate
        b["win"].set_value("-" if wr is None else f"{wr:.0f} %", f"{s.wins} ganadas  -  {s.losses} perdidas")
        b["total"].set_value(_r(s.total_r), f"{s.total_pct:+.2f} % del precio", _tone(s.total_r))
        b["exp"].set_value(_r(s.expectancy), "R medio por operación", _tone(s.expectancy))
        pf = s.profit_factor
        b["pf"].set_value("-" if pf is None else "∞" if pf == float("inf") else f"{pf:.2f}", "ganado / perdido",
                          None if pf is None else theme.BULL if pf > 1 else theme.BEAR if pf < 1 else None)
        dd = s.max_drawdown
        b["dd"].set_value(f"{-dd:.2f} R" if dd else "0 R", "desde el máximo", theme.BEAR if dd else None)
        evaluated = s.go + s.nogo
        b["cortex"].set_value(f"{s.go} GO  /  {s.nogo} NO GO",
                              f"{100 * s.go / evaluated:.0f} % aprobadas" if evaluated else "ninguna evaluada")
        b["best"].set_value(f"{_r(s.best, 1)}  /  {_r(s.worst, 1)}" if done else "-", "mejor y peor operación")
        st = s.streak
        b["streak"].set_value(f"{abs(st)} {'ganada' if st > 0 else 'perdida'}{'s' if abs(st) != 1 else ''}" if st else "-",
                              "seguidas", _tone(st))

        self._paint_curve(s.equity)
        self._fill_groups(self.by_symbol, s.breakdown(lambda o: o.symbol))
        self._fill_groups(self.by_pattern, s.breakdown(lambda o: o.pattern))
        self._fill_history(s.trades)

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

    def _fill_groups(self, table: QTableWidget, rows: list[tuple[str, int, int, float]]) -> None:
        table.setRowCount(len(rows))
        for i, (name, n, wins, r) in enumerate(rows):
            for col, text in enumerate((name, str(n), str(wins), f"{100 * wins / n:.0f} %")):
                self._cell(table, i, col, text)
            self._cell(table, i, 4, _r(r), _tone(r))
        table.resizeColumnsToContents()

    def _fill_history(self, trades: list[Trade]) -> None:
        rows = sorted(trades, key=lambda t: t.order.entry_ts or 0, reverse=True)     # las más recientes arriba
        self.history.setRowCount(len(rows))
        for i, t in enumerate(rows):
            o = t.order
            when = fecha_hora(self._to_ny(o.entry_ts)) if o.entry_ts else "-"
            side_color = theme.BULL if o.direction == "long" else theme.BEAR
            self._cell(self.history, i, 0, when)
            self._cell(self.history, i, 1, f"{o.symbol} {display_label(o.timeframe)}")
            self._cell(self.history, i, 2, o.direction.capitalize(), side_color)
            self._cell(self.history, i, 3, o.pattern)
            if t.closed:
                self._cell(self.history, i, 4, RESULT_NAMES.get(t.closed.result, t.closed.result))
                self._cell(self.history, i, 5, _r(t.r), _tone(t.r))
            else:
                self._cell(self.history, i, 4, "Abierta", theme.WARN)
                self._cell(self.history, i, 5, "-")
        self.history.resizeColumnsToContents()
