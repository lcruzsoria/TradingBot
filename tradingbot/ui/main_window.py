"""Ventana principal de TradingBot.

La ventana no ejecuta tareas: publica peticiones en el bus (feed.load, bias.recalc,
trade.request) y pinta lo que las skills publican (candles.loaded, bias.updated, quotes.updated...).
"""
from __future__ import annotations

from datetime import datetime, timezone

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QApplication, QButtonGroup, QComboBox, QFrame, QHBoxLayout, QLabel, QMainWindow, QPlainTextEdit,
                               QProgressBar, QPushButton, QVBoxLayout, QWidget)

from ..bias import BiasResult
from ..core import Event, EventBus, SkillManager
from ..datasource import AccountSnapshot
from ..timeframes import DEFAULT_TIMEFRAME, TIMEFRAMES, minutes
from . import theme
from .bridge import UiBridge
from .chart import ChartView
from .fmt import fecha_corta, fecha_hora, miles
from .ring import FREE_SLOT_TEXT, RingView, describe_skill
from .theme_dialog import ThemeDialog
from .widgets import STALE_AFTER_SECONDS, BiasCard, MarketsGrid, Panel, RulesList, StatBlock, repolish


class MainWindow(QMainWindow):
    first_loaded = Signal()

    def __init__(self, bus: EventBus, manager: SkillManager, app_cfg: dict, subtitle: str, demo: bool = False,
                 theme_name: str = theme.DEFAULT_PRESET):
        super().__init__()
        self.bus = bus
        self.manager = manager
        self.bridge = UiBridge(bus)
        self.watchlist: list[str] = [s.upper() for s in app_cfg["app"].get("watchlist", [])]
        self.candles = None
        self.connected = False
        self._busy = False
        self._first_done = False
        self._probe_id = 0
        self.theme_name = theme_name

        self.setWindowTitle("TradingBot")
        self.resize(1540, 960)
        self.setMinimumSize(1240, 800)

        root = QWidget()
        root.setObjectName("Root")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(12, 10, 12, 12)
        outer.setSpacing(10)
        outer.addWidget(self._build_header(subtitle, demo))

        body = QHBoxLayout()
        body.setSpacing(10)
        body.addLayout(self._build_left(app_cfg), 1)
        right = self._build_right()
        right.setFixedWidth(392)
        body.addWidget(right)
        outer.addLayout(body, 1)

        self.load_btn.clicked.connect(self.load_candles)
        self.tf_group.buttonClicked.connect(lambda _b: self.load_candles())
        self.symbol.activated.connect(lambda _i: self.load_candles())
        self.symbol.lineEdit().returnPressed.connect(self.load_candles)
        self.recalc_btn.clicked.connect(lambda: self.bus.publish("bias.recalc", {}, source="ui"))
        self.colors_btn.clicked.connect(self.open_theme_editor)
        self.markets.symbol_selected.connect(self._on_market_clicked)
        self.bias_card.probe.connect(self._probe_trade)
        self.ring.skill_clicked.connect(self._show_skill)
        self.ring.free_slot_clicked.connect(self._show_free_slot)
        self.bridge.event.connect(self._on_event)
        self.bridge.flow.connect(self.ring.flash)

        self.ring.set_skills(manager.infos())
        self._handlers = {
            "feed.connected": self._on_connected, "feed.progress": self._on_progress,
            "feed.failed": self._on_failed, "candles.loaded": self._on_candles,
            "quotes.updated": self._on_quotes, "bias.updated": self._on_bias,
            "trade.verdict": self._on_verdict, "skill.state": self._on_skill_state,
            "skill.error": self._on_skill_error,
        }
        self._set_status("Sin conectar", "busy")
        self.recalc_btn.setEnabled(False)
        self.markets.set_selected(self.symbol.currentText())
        first = "cortex" if "cortex" in manager.skills else next(iter(manager.skills), None)
        if first:
            self.ring.selected = first
            self._show_skill(first)
        self.log("TradingBot listo.")

    # -- construcción de la interfaz ---------------------------------------------------------
    def _build_header(self, subtitle: str, demo: bool) -> QFrame:
        bar = QFrame()
        bar.setObjectName("Toolbar")
        h = QHBoxLayout(bar)
        h.setContentsMargins(16, 10, 16, 10)
        h.setSpacing(16)

        left = QVBoxLayout()
        left.setSpacing(5)
        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        brand = QLabel("TradingBot")
        brand.setObjectName("Brand")
        sub = QLabel(subtitle)
        sub.setObjectName("Muted")
        title_row.addWidget(brand)
        title_row.addWidget(sub)
        if demo:
            badge = QLabel("Datos sintéticos")
            badge.setObjectName("DemoBadge")
            title_row.addWidget(badge)
        title_row.addStretch(1)
        chips = QHBoxLayout()
        chips.setSpacing(6)
        self.status = QLabel("Sin conectar")
        self.status.setObjectName("StatusChip")
        self.account = QLabel("")
        self.account.setObjectName("AccountChip")
        self.account.hide()
        chips.addWidget(self.status)
        chips.addWidget(self.account)
        chips.addStretch(1)
        self.colors_btn = QPushButton("Colores")
        self.colors_btn.setToolTip("Personalizar los colores de la interfaz")
        chips.addWidget(self.colors_btn)
        left.addLayout(title_row)
        left.addLayout(chips)
        h.addLayout(left, 1)

        self.stat_balance = StatBlock("Saldo")
        self.stat_pnl = StatBlock("P&L abierto")
        self.stat_open = StatBlock("Mercados abiertos")
        self.stat_tick = StatBlock("Último tick")
        for i, block in enumerate((self.stat_balance, self.stat_pnl, self.stat_open, self.stat_tick)):
            if i:
                divider = QFrame()
                divider.setObjectName("StatDivider")
                h.addWidget(divider)
            h.addWidget(block)
        return bar

    def _build_left(self, app_cfg: dict) -> QVBoxLayout:
        left = QVBoxLayout()
        left.setSpacing(10)

        self.markets_panel = Panel("Mercados", "Pulsa una tarjeta para ver su gráfico")
        self.markets = MarketsGrid(self.watchlist)
        self.markets_panel.body.addWidget(self.markets)
        if self.watchlist:
            left.addWidget(self.markets_panel)

        chart_panel = Panel("Gráfico", "Precio bid - hora del servidor del broker")
        self.chart_panel = chart_panel
        tools = QHBoxLayout()
        tools.setSpacing(6)
        self.tf_group = QButtonGroup(self)
        self.tf_group.setExclusive(True)
        wanted = app_cfg["app"].get("timeframe", DEFAULT_TIMEFRAME)
        for label in TIMEFRAMES:
            btn = QPushButton(f"M{minutes(label)}")
            btn.setProperty("chip", "true")
            btn.setProperty("tf", label)
            btn.setCheckable(True)
            btn.setChecked(label == wanted)
            self.tf_group.addButton(btn)
            tools.addWidget(btn)
        tools.addSpacing(10)
        self.symbol = QComboBox()
        self.symbol.setEditable(True)
        self.symbol.addItem(app_cfg["app"]["symbol"])
        self.symbol.setToolTip("Símbolo: escribe uno o elige de la lista")
        tools.addWidget(self.symbol)
        self.load_btn = QPushButton("Cargar velas")
        self.load_btn.setObjectName("Primary")
        tools.addWidget(self.load_btn)
        tools.addStretch(1)
        self.progress_label = QLabel("")
        self.progress_label.setObjectName("Muted")
        tools.addWidget(self.progress_label)
        chart_panel.body.addLayout(tools)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 1)
        chart_panel.body.addWidget(self.progress)
        self.chart = ChartView()
        chart_panel.body.addWidget(self.chart, 1)
        self.chart_stats = QLabel("Sin velas cargadas")
        self.chart_stats.setObjectName("Tiny")
        chart_panel.body.addWidget(self.chart_stats)
        left.addWidget(chart_panel, 1)

        log = Panel("Registro")
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(500)
        self.log_view.setFixedHeight(96)
        log.body.addWidget(self.log_view)
        left.addWidget(log)
        return left

    def _build_right(self) -> QWidget:
        side = QWidget()
        col = QVBoxLayout(side)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(10)

        self.bias_card = BiasCard()
        col.addWidget(self.bias_card)

        skills = Panel("Skills", "Cada hexágono es una skill")
        self.ring = RingView()
        skills.body.addWidget(self.ring, 1)
        self.skill_detail = QLabel("")
        self.skill_detail.setObjectName("SkillDetail")
        self.skill_detail.setWordWrap(True)
        self.skill_detail.setTextFormat(Qt.TextFormat.RichText)
        self.skill_detail.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.skill_detail.setMinimumHeight(98)
        skills.body.addWidget(self.skill_detail)
        col.addWidget(skills, 1)

        rules = Panel("Reglas del sesgo", "Voto de cada regla")
        self.rules_list = RulesList()
        rules.body.addWidget(self.rules_list)
        self.recalc_btn = QPushButton("Recalcular sesgo")
        rules.body.addWidget(self.recalc_btn)
        col.addWidget(rules)
        return side

    # -- utilidades -----------------------------------------------------------------------------
    def log(self, message: str) -> None:
        self.log_view.appendPlainText(f"[{datetime.now():%H:%M:%S}] {message}")

    def current_tf(self) -> str:
        btn = self.tf_group.checkedButton()
        return btn.property("tf") if btn else DEFAULT_TIMEFRAME

    def _set_status(self, text: str, state: str) -> None:
        self.status.setText(text)
        self.status.setProperty("state", state)
        repolish(self.status)

    def _set_busy(self, busy: bool, message: str = "") -> None:
        self._busy = busy
        for w in (self.load_btn, self.symbol):
            w.setEnabled(not busy)
        for b in self.tf_group.buttons():
            b.setEnabled(not busy)
        self.recalc_btn.setEnabled(not busy and self.candles is not None)
        if busy:
            self.progress.setRange(0, 0)
        else:
            self.progress.setRange(0, 1)
            self.progress.setValue(0)
        self.progress_label.setText(message)

    # -- acciones del usuario: publican en el bus --------------------------------------------
    def start(self) -> None:
        self.manager.start()
        self.load_candles()

    def _on_market_clicked(self, symbol: str) -> None:
        if self._busy:
            return
        self.symbol.setCurrentText(symbol)
        self.load_candles()

    def load_candles(self) -> None:
        if self._busy:
            return
        symbol = self.symbol.currentText().strip().upper()
        if not symbol:
            self.log("Indica un símbolo.")
            return
        tf = self.current_tf()
        self._set_busy(True, "Conectando…" if not self.connected else f"Cargando {symbol} M{minutes(tf)}…")
        if not self.connected:
            self._set_status("Conectando…", "busy")
        self.markets.set_selected(symbol)
        self.log(f"ui -> feed: cargar {symbol} M{minutes(tf)}")
        self.bus.publish("feed.load", {"symbol": symbol, "timeframe": tf}, source="ui")

    def _probe_trade(self, direction) -> None:
        self._probe_id += 1
        self.bus.publish("trade.request", {"request_id": f"ui-{self._probe_id}", "direction": direction}, source="ui")

    def closeEvent(self, event) -> None:
        self.manager.stop()
        super().closeEvent(event)

    # -- tema -------------------------------------------------------------------------------------
    def open_theme_editor(self) -> None:
        dialog = ThemeDialog(self, self.theme_name, theme.current(), self.apply_theme)
        dialog.exec()

    def apply_theme(self, name: str, palette) -> None:
        """Aplica una paleta a toda la interfaz sin reiniciar."""
        self.theme_name = name
        theme.apply(palette)
        QApplication.instance().setStyleSheet(theme.stylesheet())
        self.chart.apply_theme()
        self.rules_list.refresh()
        self.ring.update()
        if self.ring.selected in self.manager.skills:
            self._show_skill(self.ring.selected)

    # -- eventos que llegan de las skills (hilo de la interfaz) -----------------------------------
    def _on_event(self, event: Event) -> None:
        handler = self._handlers.get(event.topic)
        if handler:
            handler(event.payload)

    def _on_connected(self, p: dict) -> None:
        self.connected = True
        self._set_status("Conectado", "ok")
        self.account.setText(p["info"])
        self.account.show()
        self.log(f"feed: conectado - {p['info']}")
        if p["symbols"]:
            current = self.symbol.currentText()
            self.symbol.blockSignals(True)
            self.symbol.clear()
            self.symbol.addItems(p["symbols"])
            self.symbol.setCurrentText(current)
            self.symbol.blockSignals(False)

    def _on_progress(self, p: dict) -> None:
        self.progress_label.setText(f"{miles(p['count'])} velas cargadas…")

    def _on_failed(self, p: dict) -> None:
        self.log(f"feed: error - {p['error']}")
        self._set_status("Error de conexión" if p["stage"] == "connect" else "Error al cargar", "error")
        self._set_busy(False)

    def _on_candles(self, p: dict) -> None:
        df, symbol, tf = p["df"], p["symbol"], p["timeframe"]
        self.candles = df
        self.chart.set_candles(df)
        first, last = df["time"].iloc[0], df["time"].iloc[-1]
        self.chart_panel.title.setText(f"{symbol}  M{minutes(tf)}")
        self.chart_stats.setText(f"{miles(len(df))} velas  -  desde {fecha_corta(first)}  -  última {fecha_hora(last)}")
        self.log(f"feed: {miles(len(df))} velas de {symbol} M{minutes(tf)} "
                 f"({first:%Y-%m-%d} a {last:%Y-%m-%d %H:%M}) en {p['seconds']:.1f}s")
        self._set_busy(False)
        if not self._first_done:
            self._first_done = True
            self.first_loaded.emit()

    def _on_quotes(self, p: dict) -> None:
        quotes, account = p["quotes"], p["account"]
        self.markets.set_quotes(quotes)
        live = [q for q in quotes.values() if q]
        if live:
            freshest = max(q.ts for q in live)
            self.stat_tick.set_value(datetime.fromtimestamp(freshest, tz=timezone.utc).strftime("%H:%M:%S"),
                                     "hora del servidor")
            open_n = sum(1 for q in live if freshest - q.ts <= STALE_AFTER_SECONDS)
            self.stat_open.set_value(f"{open_n} de {len(self.watchlist)}", "con precio en vivo")
            self.markets_panel.note.setText(f"{open_n} abiertos. Pulsa una tarjeta para ver su gráfico")
        self._apply_account(account)

    def _apply_account(self, account: AccountSnapshot | None) -> None:
        if account is None:
            return
        self.stat_balance.set_value(f"{account.balance:,.2f}", f"{account.currency}  -  equity {account.equity:,.2f}")
        pct = account.profit / account.balance * 100 if account.balance else 0.0
        color = theme.BULL if account.profit > 0 else theme.BEAR if account.profit < 0 else None
        self.stat_pnl.set_value(f"{account.profit:+,.2f}", f"{pct:+.2f}% del saldo", color)

    def _on_bias(self, p: dict) -> None:
        result: BiasResult = p["result"]
        self.bias_card.set_result(result)
        self.rules_list.set_result(result)
        self.chart.set_levels(result.levels)
        self.log(f"bias: {result.bias.value} - {result.summary}")

    def _on_verdict(self, p: dict) -> None:
        if str(p.get("request_id", "")).startswith("ui-"):
            self.log(f"cortex: {p['reason']}")

    def _on_skill_state(self, p: dict) -> None:
        self.ring.update_state(p)
        if p["key"] == self.ring.selected:
            self._show_skill(p["key"])

    def _on_skill_error(self, p: dict) -> None:
        self.log(f"skill {p['key']}: {p['error']}")

    # -- detalle de la skill seleccionada ---------------------------------------------------------
    def _show_skill(self, key: str) -> None:
        info = self.manager.skills[key].info
        self.skill_detail.setText(describe_skill(info, self.ring.views[key], self.ring.last_in.get(key),
                                                 self.ring.last_out.get(key)))

    def _show_free_slot(self, slot) -> None:
        self.ring.selected = None
        self.skill_detail.setText(FREE_SLOT_TEXT % (theme.MUTED, slot))
        self.ring.update()
