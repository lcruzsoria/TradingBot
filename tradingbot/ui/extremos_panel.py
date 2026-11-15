"""Panel de la ventana Backtest para el grupo Enigma369 (tipo «extremos»): en qué zona se hacen el máximo y el mínimo de cada día.

No hay operaciones ni R: cada cifra es un % de extremos frente al % de tiempo de esa zona y frente a lo esperado por el horario. Los
histogramas de día, mes y año se pulsan como los del resto de la ventana (la selección la guarda BacktestDialog).
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ..skills.stats.backtest import DAYS, MONTHS
from ..skills.stats.extremos import CONDITIONS, SESSIONS, Extremes, Selection, Share, cell_name
from . import theme
from .fmt import miles
from .stats_dialog import Book, Tile

MEASURES = {"Combinación de color hasta el cuarto": "Combinación cuarto", "Combinación de color hasta el micro": "Combinación micro",
            "Alineación 3-6-9 hasta el cuarto": "Alineación cuarto", "Alineación 3-6-9 hasta el micro": "Alineación micro",
            "Cuarto 3-6-9": "Cuarto 3-6-9", "Micro 3-6-9": "Micro 3-6-9"}
SHARE_HEADERS = ("Extremos", "% extremos", "% tiempo", "Ratio", "z")


def _pct(v) -> str:
    return "-" if v is None else f"{v:.1f} %"


def _pp(v) -> str:
    return "-" if v is None else f"{v:+.1f} pp"


def _z(v) -> tuple[str, str | None]:
    if v is None:
        return "-", theme.MUTED
    return f"{v:+.1f}", theme.MUTED if abs(v) < 2 else theme.BULL if v > 0 else theme.BEAR


def _share_cells(sh: Share) -> list[tuple[str, str | None]]:
    tone = None if sh.excess is None or abs(sh.z or 0) < 2 else theme.BULL if sh.excess > 0 else theme.BEAR
    return [(miles(sh.hits), None), (_pct(sh.pct), tone), (_pct(100 * sh.base), theme.MUTED),
            ("-" if sh.ratio is None else f"{sh.ratio:.2f}", tone), _z(sh.z)]


class ExtremosPanel(QWidget):
    """Cifras, histogramas y tablas del grupo de extremos de Enigma369."""

    year_toggled = Signal(object)
    month_toggled = Signal(object)
    day_toggled = Signal(object)
    years_cleared = Signal()
    months_cleared = Signal()
    days_cleared = Signal()

    def __init__(self, bar_card) -> None:
        super().__init__()
        self.measure = next(iter(MEASURES))
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)
        row = QHBoxLayout()
        row.setSpacing(6)
        label = QLabel("Medida")
        label.setObjectName("Tiny")
        label.setFixedWidth(56)
        row.addWidget(label)
        self.measure_btns: dict[str, QPushButton] = {}
        group = QButtonGroup(self)
        for key, name in MEASURES.items():
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setProperty("chip", "true")
            btn.setChecked(key == self.measure)
            btn.setToolTip(f"Histogramas de día, mes, año y mercado: extremos en «{key}» frente a lo esperado por el horario")
            btn.clicked.connect(lambda _=False, k=key: self.set_measure(k))
            group.addButton(btn)
            row.addWidget(btn)
            self.measure_btns[key] = btn
        row.addStretch(1)
        lay.addLayout(row)
        self.verdict = QLabel()
        self.verdict.setObjectName("Verdict")
        self.verdict.setWordWrap(True)
        self.verdict.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(self.verdict)
        tiles = QHBoxLayout()
        tiles.setSpacing(8)
        self.tiles: dict[str, Tile] = {}
        for key, name in (("days", "Días"), ("open", "En la apertura"), ("crit", "En cuarto 3-6-9"), ("combo", "Combinación cuarto"),
                          ("micro", "Combinación micro"), ("cell", "Sesión-cuarto top")):
            tile = Tile(name)
            self.tiles[key] = tile
            tiles.addWidget(tile, 1)
        lay.addLayout(tiles)
        self.by_cell = bar_card("Por sesión y cuarto", "% de extremos menos % de tiempo (pp) · NY")
        self.by_session = bar_card("Por sesión", "% de extremos menos % de tiempo (pp)")
        self.by_number = bar_card("Por número del cuarto", "% de extremos menos % de tiempo (pp) · días que cuentan")
        self.by_micro = bar_card("Por micro (22,5 min)", "% de extremos menos % de tiempo (pp) · velas M3")
        self.by_day = bar_card("Por día de la semana", "")
        self.by_month = bar_card("Por mes", "")
        self.by_year = bar_card("Por año", "")
        self.by_day.toggled.connect(self.day_toggled.emit)
        self.by_month.toggled.connect(self.month_toggled.emit)
        self.by_year.toggled.connect(self.year_toggled.emit)
        self.by_day.cleared.connect(self.days_cleared.emit)
        self.by_month.cleared.connect(self.months_cleared.emit)
        self.by_year.cleared.connect(self.years_cleared.emit)
        self.conditions = Book("Condiciones", "frente al tiempo y frente al horario de cada extremo",
                               ("Condición",) + SHARE_HEADERS + ("Por horario", "z horario"))
        self.cells = Book("Sesión-cuarto", "dónde caen los extremos (hora de NY)", ("Zona",) + SHARE_HEADERS + ("Máx.", "Mín."))
        self.markets = Book("Por mercado", "", ("Mercado", "Días", "% extremos", "Por horario", "Diferencia", "z horario"))
        for w in (self.by_cell, self.by_session, self.by_number, self.by_micro, self.by_day, self.by_month, self.by_year, self.conditions,
                  self.cells, self.markets):
            lay.addWidget(w)

    def set_measure(self, key: str) -> None:
        self.measure = key
        if getattr(self, "_last", None):
            self.show_group(*self._last)

    # -- pintar --------------------------------------------------------------------------------
    def show_group(self, ext: Extremes, pattern: str, filt: str, years: set, months: set, days: set) -> None:
        self._last = (ext, pattern, filt, years, months, days)
        for k, btn in self.measure_btns.items():
            btn.setChecked(k == self.measure)
        sel = ext.select(pattern, filt, years, months, days)
        self._paint_head(sel)
        self._paint_shares(sel)
        name = MEASURES[self.measure].lower()
        note = f"% de extremos en {name} menos su % de tiempo (pp) · pulsa para filtrar"
        for card in (self.by_day, self.by_month, self.by_year):
            card.base_note = note
        self._paint_split(self.by_day, ext.split("wd", range(5), pattern, filt, years, months, days), days, lambda d: DAYS[d][:3], lambda d: DAYS[d])
        self._paint_split(self.by_month, ext.split("month", range(1, 13), pattern, filt, years, months, days), months,
                          lambda m: MONTHS[m - 1], lambda m: MONTHS[m - 1])
        self._paint_split(self.by_year, ext.split("year", ext.years, pattern, filt, years, months, days), years, str, str)
        rows = []
        for m, market in enumerate(ext.cats):
            s = ext.select(pattern, filt, years, months, days, market=m).condition(self.measure)
            rows.append([(market.split(".")[0], None), (miles(ext.select(pattern, filt, years, months, days, market=m).n_days), theme.MUTED),
                         (_pct(s.pct), None), (_pct(None if s.ctrl is None else 100 * s.ctrl), theme.MUTED),
                         (_pp(s.ctrl_excess), _tone(s.ctrl_excess, s.z_ctrl)), _z(s.z_ctrl)])
        self.markets.note.setText(f"{name} · frente al horario")
        self.markets.set_rows(rows)

    def _paint_head(self, sel: Selection) -> None:
        t = self.tiles
        if not sel.n:
            for tile in t.values():
                tile.set_value("-", "")
            self.verdict.setText("Sin extremos con este filtro y selección")
            return
        t["days"].set_value(miles(sel.n_days), f"{miles(sel.n)} extremos")
        t["open"].set_value(_pct(100 * sel.opening() / sel.n), "vela de las 18:00 (hueco)")
        for key, cond in (("crit", "Cuarto 3-6-9"), ("combo", "Combinación de color hasta el cuarto"), ("micro", "Combinación de color hasta el micro")):
            s = sel.condition(cond)
            t[key].set_value(_pct(s.pct), f"horario {_pct(None if s.ctrl is None else 100 * s.ctrl)} · z {s.z_ctrl or 0:+.1f}",
                             _tone(s.ctrl_excess, s.z_ctrl))
        best = max(sel.cells(), key=lambda x: x[1].excess or -99)
        t["cell"].set_value(cell_name(*best[0]), f"{_pct(best[1].pct)} · tiempo {_pct(100 * best[1].base)}", theme.BULL)
        s = sel.condition(self.measure)
        sign = 0 if s.z_ctrl is None or abs(s.z_ctrl) < 2 else 1 if s.z_ctrl > 0 else -1
        color = theme.BULL if sign > 0 else theme.BEAR if sign < 0 else theme.WARN
        text = {1: "Más extremos de lo que da el horario", -1: "Menos extremos de lo que da el horario", 0: "Lo que da el horario"}[sign]
        self.verdict.setStyleSheet(f"QLabel#Verdict {{ border: 1px solid {color}; border-left: 4px solid {color}; border-radius: 4px; "
                                   f"padding: 7px 10px; background: {theme.mix(theme.PANEL, color, 0.10)}; }}")
        self.verdict.setText(f"<b style='color:{color}'>{text}</b>  ·  {MEASURES[self.measure]}: {_pct(s.pct)} de los extremos, "
                             f"{_pct(None if s.ctrl is None else 100 * s.ctrl)} por horario, {_pct(100 * s.base)} del tiempo "
                             f"(z horario {s.z_ctrl or 0:+.1f}, n {miles(s.n)})")

    def _paint_shares(self, sel: Selection) -> None:
        cells = sel.cells() if sel.n else []
        self.by_cell.set_bars([c for c, _ in cells], [f"{SESSIONS[s - 1][:2]}{q}" for (s, q), _ in cells], [sh.excess for _, sh in cells],
                              [f"{cell_name(*c)}: {_pct(sh.pct)} de los extremos · {_pct(100 * sh.base)} del tiempo · z {sh.z or 0:+.1f}" for c, sh in cells])
        ses = sel.sessions() if sel.n else []
        self.by_session.set_bars([s for s, _ in ses], [SESSIONS[s - 1] for s, _ in ses], [sh.excess for _, sh in ses],
                                 [f"{SESSIONS[s - 1]}: {_pct(sh.pct)} de los extremos · {_pct(100 * sh.base)} del tiempo" for s, sh in ses])
        nums = sel.numbers() if sel.n else []
        self.by_number.set_bars([k for k, _ in nums], [str(k) for k, _ in nums], [sh.excess for _, sh in nums],
                                [f"cuarto {k}: {_pct(sh.pct)} de los extremos · {_pct(100 * sh.base)} del tiempo · z {sh.z or 0:+.1f}" for k, sh in nums])
        mic = [(k, sh) for k, sh in sel.micros() if sh.n] if sel.n else []
        self.by_micro.set_bars([k for k, _ in mic], [f"M{k}" for k, _ in mic], [sh.excess for _, sh in mic],
                               [f"M{k}: {_pct(sh.pct)} de los extremos · {_pct(100 * sh.base)} del tiempo · z {sh.z or 0:+.1f}" for k, sh in mic])
        self.conditions.set_rows([[(name, None)] + _share_cells(sh) + [(_pct(None if sh.ctrl is None else 100 * sh.ctrl), theme.MUTED), _z(sh.z_ctrl)]
                                  for name, sh in ((c, sel.condition(c)) for c in CONDITIONS)] if sel.n else [])
        highs = sel.ext["d"] == 0
        code = (sel.ext["s"] - 1) * 4 + sel.ext["q"] - 1
        rows = []
        for c, sh in sorted(cells, key=lambda x: -(x[1].excess or -99)):
            idx = (c[0] - 1) * 4 + c[1] - 1
            rows.append([(cell_name(*c), None)] + _share_cells(sh) +
                        [(miles(int(((code == idx) & highs).sum())), theme.MUTED), (miles(int(((code == idx) & ~highs).sum())), theme.MUTED)])
        self.cells.set_rows(rows)

    def _paint_split(self, card, parts: list[tuple[int, Selection]], chosen: set, short, long) -> None:
        shares = [(k, s.condition(self.measure)) for k, s in parts]
        card.set_bars([k for k, _ in shares], [short(k) for k, _ in shares], [sh.excess for _, sh in shares],
                      [f"{long(k)}: {_pct(sh.pct)} en {MEASURES[self.measure].lower()} · tiempo {_pct(100 * sh.base)} (z {sh.z or 0:+.1f}) · "
                       f"por horario {_pct(None if sh.ctrl is None else 100 * sh.ctrl)} (z {sh.z_ctrl or 0:+.1f}) · {miles(sh.n)} extremos"
                       for k, sh in shares], chosen)


def _tone(excess, z) -> str | None:
    if excess is None or z is None or abs(z) < 2:
        return None
    return theme.BULL if excess > 0 else theme.BEAR
