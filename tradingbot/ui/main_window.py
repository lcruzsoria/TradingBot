"""Ventana principal de TradingBot.

La ventana no ejecuta tareas: publica peticiones en el bus (feed.load, bias.recalc,
trade.request) y pinta lo que las skills publican (candles.loaded, bias.updated, quotes.updated...).
"""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (QApplication, QButtonGroup, QFrame, QGridLayout, QHBoxLayout, QLabel, QMainWindow,
                               QProgressBar, QPushButton, QVBoxLayout, QWidget)

from ..skills.bias import BiasResult
from ..skills.bias.models import Bias, RuleVote
from ..skills.bias.rules import fmt_price
from ..clock import format_offset, ny_from_server, server_minus_ny
from ..core import Event, EventBus, SkillManager
from ..skills.feed.datasource import AccountSnapshot
from ..timeframes import DEFAULT_TIMEFRAME, TIMEFRAMES, display_label
from . import theme
from .icons import gear_icon
from .bias_hist import PRICE_AXIS_WIDTH, BiasHistogram
from .sma_dialog import SmaDialog
from .bridge import UiBridge
from .chart import ChartView
from .errors import explain_error
from .fmt import fecha_corta, fecha_hora, miles
from .logview import LogView
from .ring import FREE_SLOT_TEXT, RingView, describe_skill
from .rules_dialog import RulesDialog
from .stats_dialog import StatsDialog, TradeStats
from .theme_dialog import ThemeDialog
from .watchlist_dialog import WatchlistDialog
from .. import envconfig, settings
from .widgets import STALE_AFTER_SECONDS, BiasCard, MarketsGrid, Panel, RulesList, StatBlock, repolish


class MainWindow(QMainWindow):
    first_loaded = Signal()

    def __init__(self, bus: EventBus, manager: SkillManager, app_cfg: dict, subtitle: str, demo: bool = False,
                 theme_name: str = theme.DEFAULT_PRESET):
        super().__init__()
        self.bus = bus
        self.manager = manager
        self.bridge = UiBridge(bus)
        self.watchlist: list[str] = [s.strip() for s in app_cfg["app"].get("watchlist", [])]
        self.candles = None
        self.connected = False
        self._busy = False
        self._first_done = False
        self._probe_id = 0
        self.theme_name = theme_name
        self.all_symbols: list[str] = []
        self.charted_symbol = ""
        self.ny_shift, self.ny_estimated = server_minus_ny(None)   # servidor - Nueva York (estimado hasta medirlo)
        self.current_symbol = self._match_symbol(app_cfg["app"]["symbol"]) or (self.watchlist[0] if self.watchlist else "")

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

        self.tf_group.buttonClicked.connect(lambda _b: self.load_candles())
        self.tbr_btn.toggled.connect(self.chart.show_tbr)
        self.recalc_btn.clicked.connect(lambda: self.bus.publish("bias.recalc", {}, source="ui"))
        self.colors_btn.clicked.connect(self.open_theme_editor)
        self.stats = TradeStats()
        self.stats_dialog: StatsDialog | None = None              # se crea la primera vez que se abre
        self.stats_btn.toggled.connect(self.toggle_stats)
        self.edit_markets_btn.clicked.connect(self.edit_watchlist)
        self.markets.symbol_selected.connect(self._on_market_clicked)
        self.bias_card.probe.connect(self._probe_trade)
        self.ring.skill_clicked.connect(self._show_skill)
        self.ring.free_slot_clicked.connect(self._show_free_slot)
        self.bridge.event.connect(self._on_event)
        self.bridge.flow.connect(self.ring.flash)

        self.ring.set_skills(manager.infos())
        self.engine = getattr(getattr(manager, "services", None), "engine", None)
        self._sync_rules()
        self._handlers = {
            "feed.connected": self._on_connected, "feed.progress": self._on_progress,
            "feed.failed": self._on_failed, "candles.loaded": self._on_candles,
            "quotes.updated": self._on_quotes, "bias.updated": self._on_bias, "tbr.updated": self._on_tbr,
            "levels.updated": self._on_day_levels, "market.closed": self._on_market_closed, "market.day": self._on_market_day, "cortex.decision": self._on_cortex_decision, "setup.executed": self._on_setup_executed, "setup.closed": self._on_setup_closed, "pattern.updated": self._on_pattern_updated,
            "pattern.detected": self._on_pattern_detected, "pattern.discarded": self._on_pattern_discarded,
            "pattern.session": self._on_pattern_session,
            "bias.schedule": self._on_bias_schedule, "bias.history": self._on_bias_history,
            "feed.refresh": self._on_refresh_request, "clock.offset": self._on_clock_offset,
            "trade.verdict": self._on_verdict, "skill.state": self._on_skill_state,
            "skill.error": self._on_skill_error,
        }
        self._set_status("Sin conectar", "busy")
        self.recalc_btn.setEnabled(False)
        self.markets.set_selected(self.current_symbol)
        self._sync_top_heights()
        first = "cortex" if "cortex" in manager.skills else next(iter(manager.skills), None)
        if first:
            self.ring.selected = first
            self._show_skill(first)
        self.log("TradingBot listo.")
        self._refresh_rules_view()
        wanted = app_cfg["app"]["symbol"]
        if self.watchlist and self._match_symbol(wanted) is None:
            self.log(f"'{wanted}' no está en el panel Quotes: se usa {self.current_symbol}.")

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
        left.addLayout(title_row)
        left.addLayout(chips)
        h.addLayout(left)

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

        # Las cifras van justo después de la cuenta; los botones Estadísticas y Skins, en la esquina derecha.
        h.addStretch(1)
        self.stats_btn = QPushButton("Estadísticas")
        self.stats_btn.setCheckable(True)
        self.stats_btn.setToolTip("Abrir o cerrar la ventana de estadísticas de las operaciones simuladas de la sesión")
        h.addWidget(self.stats_btn, 0, Qt.AlignRight | Qt.AlignVCenter)
        self.colors_btn = QPushButton("Skins")
        self.colors_btn.setToolTip("Cambiar la paleta (skin) y personalizar los colores de la interfaz")
        h.addWidget(self.colors_btn, 0, Qt.AlignRight | Qt.AlignVCenter)
        return bar

    def _build_left(self, app_cfg: dict) -> QVBoxLayout:
        left = QVBoxLayout()
        left.setSpacing(10)

        self.markets_panel = Panel("Quotes", "Pulsa una tarjeta para ver su gráfico")   # como su skill en el hexágono
        self.edit_markets_btn = QPushButton("Editar")
        self.edit_markets_btn.setToolTip("Elegir qué mercados se muestran")
        self.markets_panel.add_header_widget(self.edit_markets_btn)
        self.markets = MarketsGrid(self.watchlist)
        self.markets_panel.body.addWidget(self.markets)
        left.addWidget(self.markets_panel)

        chart_panel = Panel("Gráfico")
        self.chart_panel = chart_panel
        chart_panel.title.setToolTip("Precio bid. El eje de tiempo va en hora de Nueva York.\n"
                                     "Arrastra un eje para redimensionarlo; doble clic en él: escala automática.")
        # TBR: zonas horarias de NY y sus niveles (skill tbr; horarios y colores en tradingbot.env, bloque TBR)
        self.tbr_btn = QPushButton("TBR")
        self.tbr_btn.setProperty("chip", "true")
        self.tbr_btn.setCheckable(True)
        self.tbr_btn.setToolTip("Mostrar las zonas horarias (hora de NY) y sus niveles High, Low y 50 %")
        tbr_skill = self.manager.skills.get("tbr")
        self.tbr_btn.setVisible(tbr_skill is not None)
        self.tbr_btn.setChecked(tbr_skill is not None and tbr_skill.settings.get_bool("SHOW", False))
        # Niveles del día (skill levels; colores en tradingbot.env, bloque LEVELS): un botón por grupo
        levels_skill = self.manager.skills.get("levels")
        self.level_btns: dict[str, QPushButton] = {}
        for group, text, tip, key in (
                ("tdo", "TDO", "Apertura del mercado: precio de apertura de la primera vela del día", "SHOW_TDO"),
                ("midnight", "Midnight", "Precio de apertura a las 00:00 de Nueva York", "SHOW_MIDNIGHT"),
                ("pdhl", "PDH/PDL", "Máximo y mínimo del día anterior (Previous Day High / Low)", "SHOW_PDHL")):
            btn = QPushButton(text)
            btn.setProperty("chip", "true")
            btn.setCheckable(True)
            btn.setToolTip(tip)
            btn.setProperty("tip", tip)
            btn.setVisible(levels_skill is not None)
            btn.setChecked(levels_skill is not None and levels_skill.settings.get_bool(key, False))
            self.level_btns[group] = btn
        # SMA: media móvil de los cierres del timeframe visible; clic derecho para configurarla
        self.sma_btn = QPushButton("SMA")
        self.sma_btn.setProperty("chip", "true")
        self.sma_btn.setCheckable(True)
        self.sma_btn.setVisible(levels_skill is not None)
        self.sma_btn.setChecked(levels_skill is not None and levels_skill.settings.get_bool("SHOW_SMA", False))
        self.sma_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sma_btn.customContextMenuRequested.connect(lambda _pos: self.open_sma_config())
        self.sma_cfg_btn = QPushButton()                    # rueda: abre la ventana de la SMA (periodos, color y trazo)
        self.sma_cfg_btn.setIcon(gear_icon(theme.TEXT))
        self.sma_cfg_btn.setIconSize(QSize(16, 16))
        self.sma_cfg_btn.setProperty("chip", "true")
        self.sma_cfg_btn.setFixedWidth(30)
        self.sma_cfg_btn.setToolTip("Configurar la SMA: periodos, color de la línea y trazo")
        self.sma_cfg_btn.setVisible(levels_skill is not None)
        self.sma_cfg_btn.clicked.connect(self.open_sma_config)
        self._sma_cfg = (30, "#00ACC1", "normal")
        # Fibonacci de los patrones (0, 0,5 y 1 del tramo): lo dibuja la skill Pattern
        pattern_skill = self.manager.skills.get("pattern")
        self.fibo_btn = QPushButton("Fibo")
        self.fibo_btn.setProperty("chip", "true")
        self.fibo_btn.setCheckable(True)
        self.fibo_btn.setToolTip("Dibuja el fibonacci (niveles 0, 0,5 y 1) del tramo que da la rotura con cuerpo de las TBR "
                                 "recientes, con el patrón Continuación. La entrada es la reversión al 0,5.")
        self.fibo_btn.setVisible(pattern_skill is not None)
        self.fibo_btn.setChecked(pattern_skill is None or pattern_skill.settings.get_bool("SHOW_FIBO", True))
        self.pos_btn = QPushButton("Entradas")
        self.pos_btn.setProperty("chip", "true")
        self.pos_btn.setCheckable(True)
        self.pos_btn.setToolTip("Dibuja las entradas de los patrones como la herramienta de posición de TradingView: zona verde hasta el "
                                "objetivo, zona roja hasta el stop, con el R:R.")
        self.pos_btn.setVisible(pattern_skill is not None)
        self.pos_btn.setChecked(pattern_skill is None or pattern_skill.settings.get_bool("SHOW_POSITIONS", True))
        self._fibs: list = []                                   # fibonacci vigentes del activo del gráfico (Figure)
        self._positions: list = []                              # posiciones (entrada, stop y objetivo) de los patrones (Figure)
        # Histograma del sesgo: puntuación del Bias en cada vela, bajo el gráfico de precio
        self.hist_btn = QPushButton("Sesgo")
        self.hist_btn.setProperty("chip", "true")
        self.hist_btn.setCheckable(True)
        self.hist_btn.setToolTip("Histograma de la puntuación del sesgo en cada vela del timeframe visible, bajo el gráfico.\n"
                                 "Verde: sesgo alcista; rojo: bajista; gris: sin sesgo. Las líneas discontinuas marcan el umbral.")
        tools = QHBoxLayout()
        tools.setSpacing(6)
        self.tf_group = QButtonGroup(self)
        self.tf_group.setExclusive(True)
        wanted = app_cfg["app"].get("timeframe", DEFAULT_TIMEFRAME)
        for label in TIMEFRAMES:
            btn = QPushButton(display_label(label))
            btn.setProperty("chip", "true")
            btn.setProperty("tf", label)
            btn.setCheckable(True)
            btn.setChecked(label == wanted)
            self.tf_group.addButton(btn)
            tools.addWidget(btn)
        tools.addStretch(1)
        self.progress_label = QLabel("")
        self.progress_label.setObjectName("Muted")
        tools.addWidget(self.progress_label)

        # Cabecera del gráfico: título y timeframes | botones de niveles en 2x2 | sesgo de la sesión (compacto)
        chart_panel.layout().removeItem(chart_panel.head)      # el título pasa a la columna de la izquierda
        top = QHBoxLayout()
        top.setSpacing(12)
        left_col = QVBoxLayout()
        left_col.setSpacing(6)
        left_col.addWidget(chart_panel.title)
        left_col.addLayout(tools)
        top.addLayout(left_col, 1)
        grid = QGridLayout()
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(6)
        for i, btn in enumerate((self.level_btns["tdo"], self.level_btns["midnight"],
                                 self.level_btns["pdhl"], self.tbr_btn)):
            grid.addWidget(btn, i // 2, i % 2 + 1)
        grid.addWidget(self.hist_btn, 1, 0)                  # bajo SMA
        grid.addWidget(self.fibo_btn, 0, 3)
        grid.addWidget(self.pos_btn, 1, 3)
        sma_cell = QWidget()
        sma_row = QHBoxLayout(sma_cell)
        sma_row.setContentsMargins(0, 0, 0, 0)
        sma_row.setSpacing(4)
        sma_row.addWidget(self.sma_btn, 1)
        sma_row.addWidget(self.sma_cfg_btn)
        grid.addWidget(sma_cell, 0, 0)                   # a la izquierda de TDO (así el panel no crece en altura)
        top.addLayout(grid)
        self.bias_card = BiasCard()
        top.addWidget(self.bias_card)
        chart_panel.body.addLayout(top)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 1)
        chart_panel.body.addWidget(self.progress)
        self.error_banner = QLabel("")
        self.error_banner.setObjectName("ErrorBanner")
        self.error_banner.setWordWrap(True)
        self.error_banner.setTextFormat(Qt.TextFormat.RichText)
        self.error_banner.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.error_banner.hide()
        chart_panel.body.addWidget(self.error_banner)
        self.chart = ChartView()
        self.chart.show_tbr(self.tbr_btn.isChecked())
        for group, btn in self.level_btns.items():
            self.chart.show_level(group, btn.isChecked())
            btn.toggled.connect(lambda on, g=group: self.chart.show_level(g, on))
        self.chart.show_positions(self.pos_btn.isChecked())
        self.pos_btn.toggled.connect(self.chart.show_positions)
        self.chart.show_fibs(self.fibo_btn.isChecked())
        self.fibo_btn.toggled.connect(self.chart.show_fibs)
        self.chart.show_sma(self.sma_btn.isChecked())
        self.sma_btn.toggled.connect(self.chart.show_sma)
        self._refresh_sma_tip()
        chart_panel.body.addWidget(self.chart, 1)
        self.chart.getPlotItem().getAxis("right").setWidth(PRICE_AXIS_WIDTH)
        self.bias_hist = BiasHistogram()
        self.bias_hist.link_to(self.chart)
        self.bias_hist.setVisible(False)
        self.hist_btn.toggled.connect(self.bias_hist.setVisible)
        self.hist_btn.toggled.connect(lambda on: self._select_bar(None) if not on else None)
        self.bias_hist.bar_selected.connect(self._select_bar)
        chart_panel.body.addWidget(self.bias_hist)
        self.chart_stats = QLabel("Sin velas cargadas")
        self.chart_stats.setObjectName("Tiny")
        chart_panel.body.addWidget(self.chart_stats)
        left.addWidget(chart_panel, 1)

        log = Panel("Registro")
        log.note.setText("Eventos de las skills  -  «+ detalle» amplía la información")
        self.log_view = LogView()
        self.log_view.setFixedHeight(110)
        self._logged: dict[str, object] = {}       # última traza de cada tipo: no se repite si no cambia
        log.body.addWidget(self.log_view)
        left.addWidget(log)
        return left

    def _build_right(self) -> QWidget:
        side = QWidget()
        col = QVBoxLayout(side)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(10)

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

        rules = Panel("Reglas del sesgo")
        self.rules_panel = rules
        self.rules_when = QLabel("")                                 # vela a la que corresponden las reglas que se ven
        self.rules_when.setObjectName("CardNote")
        rules.head.insertWidget(1, self.rules_when)
        self._hist_data: dict | None = None                          # último bias.history (votos de cada regla en cada vela)
        self._live_result: BiasResult | None = None                  # sesgo de la vela actual (el que calcula el bot)
        rules.note.setTextFormat(Qt.TextFormat.RichText)             # «Voto de cada regla» es un enlace al editor
        rules.note.setCursor(Qt.CursorShape.PointingHandCursor)
        rules.note.setToolTip("Elige qué reglas aplican al sesgo y su peso")
        rules.note.linkActivated.connect(lambda _link: self.open_rules_editor())
        self._refresh_rules_link()
        self.rules_list = RulesList()
        rules.body.addWidget(self.rules_list)
        self.recalc_btn = QPushButton("Recalcular sesgo")
        rules.body.addWidget(self.recalc_btn)
        col.addWidget(rules)
        return side

    # -- reglas del sesgo: lista y editor --------------------------------------------------------------
    def _refresh_rules_link(self) -> None:
        self.rules_panel.note.setText(f"<a href='reglas' style='color: {theme.ACCENT};'>Voto de cada regla</a>")

    def _engine_rules(self) -> list[tuple[str, float]]:
        engine = self.engine
        return [(r.title or r.key, r.weight) for r in getattr(engine, "rules", [])] if engine is not None else []

    def _sync_rules(self) -> None:
        self.rules_list.set_rules(self._engine_rules())

    def open_rules_editor(self) -> None:
        engine = self.engine
        if engine is None:
            return
        dialog = RulesDialog(self, [(r.key, r.weight) for r in engine.rules], engine.min_score,
                             getattr(engine, "lateral_min", 0.0))
        if dialog.exec():
            self._apply_rules(dialog.selection(), dialog.min_score(), dialog.lateral_min())

    def _apply_rules(self, selection: list[tuple[str, float]], min_score: float, lateral_min: float | None = None) -> None:
        """Aplica al momento las reglas elegidas, las guarda en tradingbot.env y recalcula el sesgo."""
        self.engine.configure(selection, min_score, lateral_min)
        keys = [key for key, _w in selection]
        try:
            envconfig.set_value(envconfig.ENV_FILE, "BIAS_RULES", ", ".join(keys) or "ninguna")
            for key, weight in selection:
                envconfig.set_value(envconfig.ENV_FILE, f"BIAS_{key.upper()}_WEIGHT", f"{weight:g}")
            envconfig.set_value(envconfig.ENV_FILE, "BIAS_MIN_SCORE", f"{min_score:g}")
            if lateral_min is not None:
                envconfig.set_value(envconfig.ENV_FILE, "BIAS_LATERAL_MIN_EFFICIENCY", f"{lateral_min:g}")
            saved = f"guardadas en {envconfig.ENV_FILE.name}"
        except OSError as exc:
            saved = f"no se pudieron guardar ({exc})"
        self._sync_rules()
        listing = ", ".join(f"{key} +{weight:g}" for key, weight in selection) or "ninguna"
        self.log(f"bias: reglas actualizadas - {listing}; umbral ±{min_score:g} ({saved})", tone="info")
        if self.candles is not None:
            self.bus.publish("bias.recalc", {}, source="ui")

    def _refresh_sma_tip(self) -> None:
        period, color, style = self._sma_cfg
        self.sma_btn.setToolTip(f"Media móvil simple de {period} periodos ({style}, {color}) sobre las velas del timeframe visible.\n"
                                "Pulsa la rueda (o clic derecho en el botón) para cambiar los periodos, el color y el trazo.")

    def open_sma_config(self) -> None:
        """Ventana de la SMA: periodos, color y trazo; se aplica al momento y se guarda en tradingbot.env."""
        dialog = SmaDialog(self, *self._sma_cfg)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        self._apply_sma(*dialog.values())

    def _apply_sma(self, period: int, color: str, style: str) -> None:
        self._sma_cfg = (period, color, style)
        try:
            for key, value in (("SMA_PERIOD", str(period)), ("SMA_COLOR", color), ("SMA_STYLE", style)):
                envconfig.set_value(envconfig.ENV_FILE, f"LEVELS_{key}", value)
            saved = f"guardada en {envconfig.ENV_FILE.name}"
        except OSError as exc:
            saved = f"no se pudo guardar ({exc})"
        self._refresh_sma_tip()
        self.log(f"levels: SMA de {period} periodos, {style}, {color} ({saved})", tone="info")
        self.bus.publish("levels.sma", {"period": period, "color": color, "style": style}, source="ui")

    # -- utilidades -----------------------------------------------------------------------------
    def _sync_top_heights(self) -> None:
        """Quotes, con la altura justa para sus tarjetas: el resto va al gráfico."""
        self.markets_panel.setFixedHeight(self.markets_panel.sizeHint().height())

    def log(self, message: str, detail: str | None = None, tone: str | None = None) -> None:
        self.log_view.add(message, detail, tone)

    def log_once(self, kind: str, key, message: str, detail: str | None = None, tone: str | None = None) -> None:
        """Anota el evento solo si cambia respecto al último de su tipo (las skills recalculan a menudo)."""
        if self._logged.get(kind) == key:
            return
        self._logged[kind] = key
        self.log(message, detail, tone)

    def _bar_time(self, x) -> str:
        """Hora de Nueva York de la vela `x` del gráfico actual."""
        df = self.candles
        if x is None or df is None or not 0 <= int(x) < len(df):
            return "-"
        return f"{self._ny(df['ts'].iloc[int(x)]):%d/%m %H:%M} NY"

    def current_tf(self) -> str:
        btn = self.tf_group.checkedButton()
        return btn.property("tf") if btn else DEFAULT_TIMEFRAME

    def _set_status(self, text: str, state: str) -> None:
        self.status.setText(text)
        self.status.setProperty("state", state)
        repolish(self.status)

    def _set_busy(self, busy: bool, message: str = "") -> None:
        self._busy = busy
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

    def _match_symbol(self, name: str) -> str | None:
        """Nombre exacto del mercado en el panel (sin distinguir mayúsculas), o None si no está."""
        wanted = name.strip().lower()
        return next((s for s in self.watchlist if s.lower() == wanted), None)

    def _on_market_clicked(self, symbol: str) -> None:
        """Pinchar un mercado del panel carga su gráfico."""
        if self._busy:
            return
        self.current_symbol = self._match_symbol(symbol) or symbol
        self.load_candles()

    def load_candles(self) -> None:
        if self._busy:
            return
        symbol = self.current_symbol
        if not symbol:
            self.log("No hay mercados en el panel Quotes: añade alguno con el botón Editar.")
            return
        tf = self.current_tf()
        self._set_busy(True, "Conectando…" if not self.connected else f"Cargando {symbol} {display_label(tf)}…")
        if not self.connected:
            self._set_status("Conectando…", "busy")
        self.markets.set_selected(symbol)
        self.error_banner.hide()
        self.status.setToolTip("")
        self.log(f"ui -> feed: cargar {symbol} {display_label(tf)}")
        self.bus.publish("feed.load", {"symbol": symbol, "timeframe": tf}, source="ui")

    def _probe_trade(self, direction) -> None:
        self._probe_id += 1
        self.bus.publish("trade.request", {"request_id": f"ui-{self._probe_id}", "direction": direction}, source="ui")

    def closeEvent(self, event) -> None:
        self.manager.stop()
        super().closeEvent(event)

    # -- lista de mercados ------------------------------------------------------------------------
    def edit_watchlist(self) -> None:
        dialog = WatchlistDialog(self, self.all_symbols, self.watchlist)
        if dialog.exec():
            self.set_watchlist(dialog.symbols)

    def set_watchlist(self, symbols: list[str]) -> None:
        """Cambia los mercados mostrados, avisa a la skill Quotes y guarda la elección."""
        symbols = settings.clean_symbols(symbols)
        self.watchlist = symbols
        self.markets.set_symbols(symbols)
        self._sync_top_heights()
        kept = self._match_symbol(self.current_symbol)
        self.current_symbol = kept or (symbols[0] if symbols else "")
        self.markets.set_selected(self.current_symbol)
        self.stat_open.set_value("-", "")
        self.markets_panel.note.setText("Pulsa una tarjeta para ver su gráfico")
        try:
            settings.save_watchlist(symbols)
        except OSError as exc:
            self.log(f"No se pudo guardar la lista de mercados: {exc}")
        self.log(f"mercados: {', '.join(symbols) or 'ninguno'}")
        self.bus.publish("watchlist.changed", {"symbols": symbols}, source="ui")
        if kept is None and symbols and self.connected:
            self.log(f"El gráfico mostraba {self.charted_symbol or 'otro mercado'}, que ya no está en la lista: "
                     f"se carga {self.current_symbol}.")
            self.load_candles()

    # -- estadísticas -----------------------------------------------------------------------------
    def toggle_stats(self, show: bool) -> None:
        """El botón Estadísticas abre la ventana flotante y, pulsado otra vez, la cierra."""
        if not show:
            if self.stats_dialog is not None:
                self.stats_dialog.hide()
            return
        if self.stats_dialog is None:
            self.stats_dialog = StatsDialog(self, self.stats, lambda ts: self._ny(ts))
            self.stats_dialog.hidden.connect(lambda: self.stats_btn.setChecked(False))
        self.stats_dialog.popup_at(self.stats_btn)

    def _refresh_stats(self) -> None:
        if self.stats_dialog is not None and self.stats_dialog.isVisible():
            self.stats_dialog.refresh()

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
        self.bias_hist.style()
        self.sma_cfg_btn.setIcon(gear_icon(theme.TEXT))
        self._refresh_rules_link()
        self.rules_list.refresh()
        self.ring.update()
        if self.ring.selected in self.manager.skills:
            self._show_skill(self.ring.selected)
        self._refresh_stats()

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
        self.all_symbols = p.get("all_symbols", [])

    def _on_progress(self, p: dict) -> None:
        self.progress_label.setText(f"{miles(p['count'])} velas cargadas…")

    def _on_failed(self, p: dict) -> None:
        self.log(f"feed: error - {p['error']}")
        self._set_status("Error de conexión" if p["stage"] == "connect" else "Error al cargar", "error")
        self.status.setToolTip(p["error"])
        what = (f"No se pudieron cargar las velas de {p['symbol']}." if p.get("symbol")
                else "No se pudo conectar con MT5.")
        self.error_banner.setText(f"<b>{what}</b><br>{p['error']}<br>"
                                  f"<span style='color:{theme.MUTED}'>{explain_error(p['error'])}</span>")
        self.error_banner.show()
        self._set_busy(False)

    def _on_candles(self, p: dict) -> None:
        df, symbol, tf = p["df"], p["symbol"], p["timeframe"]
        self.charted_symbol = symbol
        if not p.get("refresh"):
            self.bias_hist.select(None)                              # otro activo o timeframe: se pierde la vela marcada
            self.chart.set_marker(None)
            self._hist_data = None
        self.error_banner.hide()
        if self.connected:
            self._set_status("Conectado", "ok")
        refresh = bool(p.get("refresh")) and self.candles is not None
        self.candles = df
        self.chart.set_candles(df, keep_view=refresh)
        if symbol != getattr(self, "_fib_symbol", symbol):
            self._fibs, self._positions = [], []                 # otro activo: se olvidan los dibujos anteriores
        self._fib_symbol = symbol
        self._apply_fibs()
        self.chart.set_ny_shift(self.ny_shift)
        self.chart_panel.title.setText(f"{symbol}  {display_label(tf)}")
        self._update_chart_stats()
        first, last = self._ny(df["ts"].iloc[0]), self._ny(df["ts"].iloc[-1])
        if refresh:
            self.log(f"feed: velas de {symbol} {display_label(tf)} actualizadas (última {last:%d/%m %H:%M} NY) "
                     f"en {p['seconds']:.1f}s")
        else:
            self.log(f"feed: {miles(len(df))} velas de {symbol} {display_label(tf)} "
                     f"({first:%Y-%m-%d} a {last:%Y-%m-%d %H:%M} NY) en {p['seconds']:.1f}s")
        self._set_busy(False)
        if not self._first_done:
            self._first_done = True
            self.first_loaded.emit()

    def _ny(self, server_ts) -> datetime:
        """Hora de Nueva York de una marca de tiempo del servidor (sin zona, para mostrar)."""
        return datetime.fromtimestamp(int(server_ts) - self.ny_shift, tz=timezone.utc).replace(tzinfo=None)

    def _update_chart_stats(self) -> None:
        df = self.candles
        if df is None or not len(df):
            return
        first, last = self._ny(df["ts"].iloc[0]), self._ny(df["ts"].iloc[-1])
        zone = "hora de Nueva York (estimada)" if self.ny_estimated else "hora de Nueva York"
        self.chart_stats.setText(f"{miles(len(df))} velas  -  desde {fecha_corta(first)}  -  "
                                 f"última {fecha_hora(last)}  -  {zone}")

    def _on_quotes(self, p: dict) -> None:
        quotes, account = p["quotes"], p["account"]
        shift, estimated = server_minus_ny(p.get("server_offset"))
        if (shift, estimated) != (self.ny_shift, self.ny_estimated):
            self.ny_shift, self.ny_estimated = shift, estimated     # desfase medido: el eje pasa a hora exacta
            self.chart.set_ny_shift(shift)
            self._update_chart_stats()
        self.markets.set_quotes(quotes)
        live = [q for q in quotes.values() if q]
        if live:
            freshest = max(q.ts for q in live)
            self._show_last_tick(freshest, p.get("server_offset"), p.get("offset_source"))
            open_n = sum(1 for q in live if freshest - q.ts <= STALE_AFTER_SECONDS)
            self.stat_open.set_value(f"{open_n} de {len(self.watchlist)}", "con precio en vivo")
            self.markets_panel.note.setText(f"{open_n} abiertos. Pulsa una tarjeta para ver su gráfico")
        self._apply_account(account)

    def _show_last_tick(self, server_ts: int, offset: int | None, source: str | None) -> None:
        """Hora del último tick en Nueva York (la de los mercados americanos)."""
        ny, estimated = ny_from_server(server_ts, offset)
        server_clock = datetime.fromtimestamp(server_ts, tz=timezone.utc).strftime("%H:%M:%S")
        if estimated:
            sub, how = "Nueva York (estimada)", "Desfase del servidor aún sin medir: se asume servidor = Nueva York + 7 h."
        else:
            sub, how = f"Nueva York ({ny.tzname()})", f"Desfase del servidor {format_offset(offset)} ({source})."
        self.stat_tick.set_value(ny.strftime("%H:%M:%S"), sub)
        self.stat_tick.setToolTip(f"Último tick en hora de Nueva York.\nHora del servidor del broker: {server_clock}.\n{how}")

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
        self._live_result = result
        self._refresh_rules_view()
        # Los niveles del día (apertura, máximo y mínimo previos) los pinta ahora la skill levels con sus botones.
        tone = "go" if result.bias.value == "Bullish" else "nogo" if result.bias.value == "Bearish" else None
        reason = p.get("reason") or "carga de velas"
        lines = [f"Sesgo: {result.bias.value}   ({p.get('symbol', '')}, día {result.day})",
                 f"Motivo del cálculo: {reason}",
                 f"Puntuación: {result.score:+g}  (Bullish con +{result.min_score:g} o más, "
                 f"Bearish con -{result.min_score:g} o menos)", "", "Reglas (voto, peso y puntos):"]
        marks = {1: "▲ alcista", -1: "▼ bajista", 0: "– sin voto"}
        for v in result.votes:
            lines.append(f"  {marks[v.vote]:<11} peso {v.weight * v.vote if v.vote else v.weight:+g}: {v.points:+g}   {v.rule}: {v.detail}")
        if result.levels:
            lines += ["", "Niveles: " + ", ".join(f"{k} {fmt_price(val)}" for k, val in result.levels.items())]
        self.log(f"bias: {result.bias.value} ({p.get('symbol', '')}, puntuación {result.score:+g}) - {reason}",
                 "\n".join(lines), tone)

    def _on_tbr(self, p: dict) -> None:
        if p["symbol"] != self.charted_symbol or p["timeframe"] != self.current_tf():
            return                                      # llega tarde: ya se está viendo otro gráfico
        self.chart.set_tbr(p["sessions"], p["opacity"], p.get("line_opacity"))
        zones = ", ".join(f"{z.name} {z.hours}" for z in p["zones"])
        if p["available"]:
            tip = (f"Zonas TBR en hora de Nueva York: {zones}.\n"
                   "Cajas del Low al High; sus niveles High, Low y 50 % (punteado) siguen hasta que una vela los toma.")
            if p["estimated"]:
                tip += "\nDesfase del servidor aún sin medir: se asume servidor = Nueva York + 7 h."
        else:
            top = max((t for t in TIMEFRAMES if TIMEFRAMES[t] <= p["max_tf"]), key=TIMEFRAMES.get, default=None)
            tip = (f"Las zonas TBR solo se dibujan hasta {display_label(top) if top else '—'} "
                   f"(TBR_MAX_TF_MINUTES): con velas más grandes no caben.")
        self.tbr_btn.setEnabled(p["available"])
        self.tbr_btn.setToolTip(tip)
        self._log_tbr(p)

    def _log_tbr(self, p: dict) -> None:
        sessions = [s for s in p["sessions"] if s.complete]
        intact = [(s, lv) for s in sessions for lv in s.levels if lv.kind in ("high", "low") and not lv.taken]
        key = (p["symbol"], p["timeframe"], p["available"], len(p["sessions"]), len(intact))
        if not p["available"]:
            self.log_once("tbr", key, f"tbr: sin zonas en {display_label(p['timeframe'])} (solo hasta "
                                      f"TBR_MAX_TF_MINUTES={p['max_tf']} min)")
            return
        lines = [f"Zonas TBR de {p['symbol']} {display_label(p['timeframe'])} (hora de NY):", ""]
        for s in p["sessions"][-10:]:
            state = "en curso" if not s.complete else ", ".join(
                f"{lv.kind.upper()} {fmt_price(lv.price)} {'tomado ' + self._bar_time(lv.x1) if lv.taken else 'intacto'}"
                for lv in s.levels if lv.kind in ("high", "low"))
            lines.append(f"  {s.day:%d/%m} {s.zone.name:<7} {s.zone.hours}  H {fmt_price(s.high)}  "
                         f"L {fmt_price(s.low)}  -  {state}")
        lines += ["", "Liquidez aún sin tomar (posibles objetivos o zonas de setup):"]
        lines += [f"  {lv.kind.upper()} de {s.zone.name} {s.day:%d/%m}: {fmt_price(lv.price)}" for s, lv in intact[-12:]]
        self.log_once("tbr", key, f"tbr: {len(p['sessions'])} zonas en {p['symbol']} "
                                  f"{display_label(p['timeframe'])}, {len(intact)} niveles High/Low aún sin tomar",
                      "\n".join(lines))

    def _on_day_levels(self, p: dict) -> None:
        if p["symbol"] != self.charted_symbol or p["timeframe"] != self.current_tf():
            return
        self.chart.set_day_levels(p["lines"], p["days"], p["colors"])
        self._sma_cfg = (p["sma_period"], p["colors"]["sma"], p["sma_style"])
        self.chart.set_sma(p["sma"], p["colors"]["sma"], p["sma_style"])
        self._refresh_sma_tip()
        for btn in self.level_btns.values():
            btn.setEnabled(p["available"])
            btn.setToolTip(btn.property("tip") if p["available"] else
                           "Los niveles del día no se dibujan con velas diarias o semanales (LEVELS_MAX_TF_MINUTES).")
        if not p["available"]:
            return
        today: dict[str, float] = {}
        for line in sorted(p["lines"], key=lambda ln: ln.x0):       # el último de cada tipo es el del día en curso
            today[line.kind] = line.price
        start = p["day_start"]
        kind = "índice USA" if p.get("us_index") else "resto de mercados"
        names = {"tdo": "TDO", "midnight": "Midnight", "pdh": "PDH", "pdl": "PDL"}
        levels = ", ".join(f"{names[k]} {fmt_price(v)}" for k, v in today.items() if k in names)
        self.log_once("levels", (p["symbol"], p["timeframe"], start, tuple(sorted(today.items()))),
                      f"levels: día de trading desde las {start // 60:02d}:{start % 60:02d} NY ({kind}) - "
                      f"{levels or 'sin niveles'}")

    # -- reglas de la vela marcada en el histograma ------------------------------------------------------------------
    def _select_bar(self, index) -> None:
        self.bias_hist.select(index)
        self.chart.set_marker(index)
        self._refresh_rules_view()

    def _historic_result(self, index: int) -> BiasResult | None:
        """El sesgo de la vela `index` reconstruido con los votos congelados de cada regla (sin precios: solo voto y peso)."""
        p = self._hist_data
        if p is None or not 0 <= index < len(p["scores"]):
            return None
        votes = tuple(RuleVote(title, int(p["votes"][index][k]), "Voto del bloque de esa vela (reconstruido del histórico)", weight)
                      for k, (title, weight) in enumerate(p["rules"]))
        score, minimum = float(p["scores"][index]), float(p["min_score"])
        lateral = bool(p.get("lateral") is not None and p["lateral"][index])
        bias = Bias.NO_BIAS if lateral else Bias.BULLISH if score >= minimum else Bias.BEARISH if score <= -minimum else Bias.NO_BIAS
        return BiasResult(bias, None, votes, {}, f"Vela del {self._bar_time(index)}", score, minimum, lateral)

    def _refresh_rules_view(self) -> None:
        """Panel de reglas: las de la vela marcada en el histograma o, si no hay ninguna, las de la vela actual."""
        index = self.bias_hist.selected if self.bias_hist.isVisibleTo(self) else None
        shown = self._historic_result(index) if index is not None else None
        tf = f"TF={display_label(self.current_tf())}"
        if shown is not None:
            self.rules_when.setText(f"  ·  {tf}  ·  {self._bar_time(index)}")
            self.rules_list.set_result(shown)
        else:
            self.rules_when.setText(f"  ·  {tf}  ·  Vela actual")
            self.rules_list.set_result(self._live_result)

    def _on_bias_history(self, p: dict) -> None:
        if p["symbol"] != self.charted_symbol or p["timeframe"] != self.current_tf():
            return
        self._hist_data = p
        self.bias_hist.set_scores(p["scores"], p["min_score"], p.get("lateral"))
        self._apply_fibs()                                              # el GO / NO GO de cada entrada depende de este sesgo
        self._refresh_rules_view()

    def _on_market_closed(self, p: dict) -> None:
        hour = p["when"].strftime("%H:%M")
        hhmm = lambda m: f"{m // 60:02d}:{m % 60:02d}"          # noqa: E731
        if p["weekly"]:
            self.log(f"mercados: cierre semanal a las {hour} NY - Forex y futuros de índices USA",
                     f"Cierre semanal (viernes {hour} NY): cierran Forex y los futuros de los índices americanos.\n"
                     f"Reabren el domingo: Forex a las {hhmm(p['reopen'])} NY y los índices a las {hhmm(p['index_reopen'])} NY.",
                     tone="warn")
        else:
            self.log(f"mercados: cierre de los futuros de índices USA a las {hour} NY",
                     f"Cierre diario de los futuros de los índices americanos ({hour} NY): reabren a las "
                     f"{hhmm(p['index_reopen'])} NY con un nuevo día de trading.\nForex sigue abierto: su día de trading "
                     f"empieza a las {hhmm(p['reopen'])} NY.", tone="warn")

    def _on_market_day(self, p: dict) -> None:
        """Cambio de día de trading: a las 18:00 NY en los índices americanos y a las 17:00 en el resto de activos."""
        from ..skills.levels.daylevels import is_us_index
        symbols = [s for s in self.watchlist if is_us_index(s, p["us_indices"]) == p["index"]]
        hour = p["when"].strftime("%H:%M")
        group = "índices USA" if p["index"] else "Forex, metales y resto"
        names = ", ".join(symbols) or "ninguno de tu lista de Quotes"
        self.log(f"mercados: nuevo día de trading ({p['day']}) a las {hour} NY - {group}",
                 f"Empieza el día de trading del {p['day']} para {group} ({hour} NY).\nActivos de tu lista: {names}.\n"
                 "Los niveles TDO, PDH/PDL y los separadores del gráfico se renuevan con este día.", tone="info")

    def _apply_fibs(self) -> None:
        """Pinta los fibonacci del activo del gráfico, buscando sus horas en las velas actuales (valen para cualquier timeframe)."""
        df = self.candles
        if df is None or not len(df):
            self.chart.set_fibs([])
            self.chart.set_positions([])
            return
        ts = df["ts"].to_numpy()
        n = len(ts)
        positions = []
        for f in sorted(self._positions, key=lambda f: f.x0_ts):
            x0 = int(np.searchsorted(ts, f.x0_ts, "left"))
            decision, reason = self._entry_decision(x0, f.direction)
            positions.append({"x0": x0, "x1": min(int(np.searchsorted(ts, f.x1_ts, "left")), n + 4),
                              "entry": f.levels["entrada"], "stop": f.levels["stop"], "target": f.levels["objetivo"],
                              "direction": f.direction, "state": f.state, "label": f.label, "decision": decision,
                              "reason": reason, "session": (f.zone, f.day)})
        busy_until = -1                                         # una sola posición abierta: las que llegan antes de que cierre no entran
        used = set()                                            # y una misma sesión no puede dar dos trades
        for pos in positions:
            if not pos["decision"]:
                continue
            if pos["x0"] < busy_until:
                pos["decision"], pos["reason"] = "NO GO", "posición abierta"
            elif pos["session"] in used:
                pos["decision"], pos["reason"] = "NO GO", "sesión ya operada"
            elif pos["decision"] == "GO":
                busy_until = pos["x1"]
                used.add(pos["session"])
        fibs = []
        for f in self._fibs:
            fib = {"x0": int(np.searchsorted(ts, f.x0_ts, "left")), "x1": min(int(np.searchsorted(ts, f.x1_ts, "left")), n + 4),
                   "levels": f.levels, "label": f.label, "state": f.state, "direction": f.direction}
            if f.state == "entrada":                            # el fibo lleva el GO / NO GO de su entrada: así se ve cuál se opera
                pos = next((p for p in positions if p["label"] == f.label and p["direction"] == f.direction
                            and fib["x0"] <= p["x0"] <= fib["x1"]), None)
                if pos is not None and pos["decision"]:
                    fib["decision"], fib["reason"] = pos["decision"], pos["reason"]
            fibs.append(fib)
        self.chart.set_fibs(fibs)
        self.chart.set_positions(positions)

    def _entry_decision(self, index: int, direction: str) -> tuple[str, str]:
        """GO / NO GO que habría dado Cortex a una entrada en la vela `index`, con el sesgo que tenía el bot en esa vela."""
        from types import SimpleNamespace
        from ..skills.bias.models import Bias
        from ..skills.cortex.validation import validate
        data = self._hist_data
        if not data or index >= len(data["scores"]) or len(data["scores"]) != len(self.candles):
            return "", ""
        score, min_score = float(data["scores"][index]), float(data["min_score"])
        lateral = data.get("lateral")
        side = bool(lateral[index]) if lateral is not None and len(lateral) == len(data["scores"]) else False
        bias = Bias.NO_BIAS if side else Bias.BULLISH if score >= min_score else Bias.BEARISH if score <= -min_score else Bias.NO_BIAS
        cortex = self.manager.skills.get("cortex")
        decision = validate(direction, SimpleNamespace(bias=bias, score=score, lateral=side, summary=f"puntuación {score:+g}"),
                            bool(getattr(cortex, "allow_no_bias", False)))
        return decision.verdict, f"{'lateral' if side else bias.value} {score:+g}"       # motivo corto para la etiqueta

    def _on_pattern_updated(self, p: dict) -> None:
        if p["symbol"] == self.charted_symbol:
            self._fibs = [f for f in p.get("figures", []) if f.kind == "fib"]
            self._positions = [f for f in p.get("figures", []) if f.kind == "pos"]
            self._apply_fibs()
        for error in p.get("errors", []):
            self.log_once("pattern_error", (p["symbol"], error), f"pattern: error en un patrón - {error}", tone="warn")
        for text in p.get("unavailable", []):
            self.log_once("pattern_tf", (p["symbol"], p["timeframe"], text), f"pattern: {text}", tone="warn")
        tbr = p["tbr"]
        if tbr is None:
            return
        tf = display_label(p["timeframe"])
        self.log_once("pattern_tbr", (p["symbol"], p["timeframe"], tbr.key, tbr.day, tbr.high, tbr.low),
                      f"pattern: TBR activa {tbr.zone} ({tbr.day:%d/%m}) en {p['symbol']} {tf} - High {fmt_price(tbr.high)}, "
                      f"Low {fmt_price(tbr.low)}, 50 % {fmt_price(tbr.mid)}",
                      f"La TBR activa es la última que cerró: {tbr.zone} del {tbr.day:%d/%m/%Y}.\n"
                      f"High {fmt_price(tbr.high)}   Low {fmt_price(tbr.low)}   50 % {fmt_price(tbr.mid)}   "
                      f"rango {fmt_price(tbr.range)}\nAhí se buscan los patrones definidos, hasta que empiece la TBR siguiente.", "info")

    def _pattern_lines(self, p: dict) -> tuple[str, str, list[str]]:
        """(lado, vela, líneas del detalle) de un resultado de patrón."""
        hit, tbr = p["hit"], p["tbr"]
        side = {"long": "Long", "short": "Short"}.get(hit.direction, "")
        if hit.ts:
            when = f"{self._ny(hit.ts):%d/%m %H:%M} NY"
        elif p["symbol"] == self.charted_symbol and p["timeframe"] == self.current_tf():
            when = self._bar_time(hit.x)
        else:
            when = "-"
        lines = [f"Patrón:   {hit.title}" + (f" ({side})" if side else ""),
                 f"TBR:      {tbr.zone} del {tbr.day:%d/%m/%Y} (High {fmt_price(tbr.high)}, Low {fmt_price(tbr.low)}, "
                 f"50 % {fmt_price(tbr.mid)})", f"Mercado:  {p['symbol']} {display_label(p['timeframe'])}", f"Vela:     {when}",
                 f"Precio:   {fmt_price(hit.price)}"]
        names = {"stop": "Stop", "target": "Objetivo"}
        lines += [f"{names.get(name, name.capitalize())}: {fmt_price(price)}" for name, price in hit.levels.items()]
        if hit.detail:
            lines += ["", hit.detail]
        return side, when, lines

    def _on_pattern_detected(self, p: dict) -> None:
        side, when, lines = self._pattern_lines(p)
        hit, tbr = p["hit"], p["tbr"]
        lines += ["", "La skill Setup lo valida ahora con el sesgo (GO / NO GO)."]
        self.log(f"pattern: {hit.title} {side} identificado en {tbr.zone} ({p['symbol']} {display_label(p['timeframe'])}, {when})",
                 "\n".join(lines), "info")

    def _on_pattern_discarded(self, p: dict) -> None:
        """Patrón invalidado, anulado o vencido: se anota por qué."""
        side, when, lines = self._pattern_lines(p)
        hit, tbr = p["hit"], p["tbr"]
        state = {"invalidated": "invalidado", "annulled": "anulado", "expired": "vencido"}.get(hit.status, hit.status)
        self.log(f"pattern: {hit.title}{' ' + side if side else ''} {state} en {tbr.zone} ({p['symbol']} "
                 f"{display_label(p['timeframe'])}, {when}) - {hit.detail}", "\n".join(lines), "warn")

    def _on_pattern_session(self, p: dict) -> None:
        tbr = p["tbr"]
        self.log_once("pattern_session", (p["symbol"], tbr.key, tbr.day),
                      f"pattern: fin de la jornada de setups en {p['symbol']} ({p['session_end']} NY): no se "
                      f"evalúan más hasta que cierre la próxima TBR", None, "warn")

    def _on_cortex_decision(self, p: dict) -> None:
        side, when, lines = self._pattern_lines(p)
        hit, tbr, decision = p["hit"], p["tbr"], p["decision"]
        self.stats.decision(decision.allowed)
        self._refresh_stats()
        lines += ["", f"Sesgo:    {p['bias'].value if p['bias'] else 'sin calcular'}", f"Decisión: {decision.verdict} - {decision.reason}"]
        lines += ["", "Con GO, Cortex le pasa la orden a Setup." if decision.allowed else "Con NO GO, Setup no recibe ninguna orden."]
        self.log(f"cortex: {decision.verdict} {side} ({hit.title}, {tbr.zone}, {p['symbol']} {display_label(p['timeframe'])}, {when}) - "
                 f"{decision.reason}", "\n".join(lines), "go" if decision.allowed else "nogo")

    def _on_setup_executed(self, p: dict) -> None:
        o = p["order"]
        self.stats.executed(o)
        self._refresh_stats()
        self.ring.celebrate(o.direction, o.symbol)
        lines = [f"Orden:    {o.label}", f"Activo:   {o.symbol}   Temporalidad: {display_label(o.timeframe)}",
                 f"Sesgo:    {o.bias} (puntuación {o.score:+g})"]
        if o.tbr_zone:
            lines.append(f"TBR:      {o.tbr_zone} del {o.tbr_day:%d/%m/%Y} (High {fmt_price(o.tbr_high)}, Low {fmt_price(o.tbr_low)}, "
                         f"50 % {fmt_price(o.tbr_mid)})")
        lines.append(f"Patrón:   {o.pattern}   Precio: {fmt_price(o.price)}")
        if o.stop is not None:
            lines.append(f"Stop:     {fmt_price(o.stop)}")
        if o.target is not None:
            lines.append(f"Objetivo: {fmt_price(o.target)}")
        if o.close_at:
            lines.append(f"Cierre:   a las {o.close_at} si no se ha tocado el stop ni el objetivo")
        lines += ["", f"Motivo:   {o.reason}", p["note"]]
        self.log(f"setup: orden {'enviada' if p['sent'] else 'preparada (simulación)'} - {o.label}", "\n".join(lines),
                 "info")

    def _on_setup_closed(self, p: dict) -> None:
        o, c = p["order"], p["closed"]
        self.stats.closed(o, c)
        self._refresh_stats()
        if c.r > 0:
            self.ring.win(c.r, o.symbol)
        why = {"objetivo": "objetivo alcanzado", "stop": "stop alcanzado", "tiempo": f"cierre por tiempo ({o.close_at})"}[c.result]
        opened = f"{self._ny(o.entry_ts):%d/%m %H:%M}" if o.entry_ts else "-"
        closed = f"{self._ny(c.exit_ts):%d/%m %H:%M}"
        lines = [f"Orden:    {o.label}", f"Entrada:  {fmt_price(o.price)} ({opened} NY)   Salida: {fmt_price(c.exit_price)} ({closed} NY)",
                 f"Motivo:   {why}", f"Resultado: {c.r:+.2f} R ({c.pct:+.2f} % del precio, sin spread)",
                 "Modo simulación: no hubo posición real en MT5."]
        verdict = {"objetivo": "GANADA (objetivo)", "stop": "PERDIDA (stop)", "tiempo": "cerrada por tiempo"}[c.result]
        self.log(f"setup: posición simulada {verdict} - {o.label}: {c.r:+.2f} R, {c.pct:+.2f} % ({opened} -> {closed} NY)",
                 chr(10).join(lines), "go" if c.r > 0 else "nogo")

    def _on_bias_schedule(self, p: dict) -> None:
        start = p["day_start"]
        kind = "índice USA" if p["us_index"] else "resto de mercados"
        if p["next"] is None:
            self.log_once("schedule", (p["symbol"], None), f"bias: recálculo programado desactivado para {p['symbol']}")
            return
        self.log_once("schedule", (p["symbol"], p["next"]),
                      f"bias: próximo recálculo de {p['symbol']} a las {p['next']:%H:%M} NY (cada {p['hours']:g} h, "
                      f"{kind}; día desde las {start // 60:02d}:{start % 60:02d})")

    def _on_refresh_request(self, p: dict) -> None:
        if p.get("reason") == "bias":
            self.log(f"bias: hora del recálculo programado - recargando velas de {p['symbol']}", tone="info")

    def _on_clock_offset(self, p: dict) -> None:
        offset = p.get("server_offset")
        if offset is None:
            return
        self.log_once("offset", offset, f"quotes: desfase del servidor {format_offset(offset)} "
                                        f"({p.get('offset_source', 'detectado')}); la hora de NY ya no es estimada")

    def _on_verdict(self, p: dict) -> None:
        if str(p.get("request_id", "")).startswith("ui-"):
            self.log(f"cortex: {p['reason']}")

    def _on_skill_state(self, p: dict) -> None:
        self.ring.update_state(p)
        if p["key"] == self.ring.selected:
            self._show_skill(p["key"])

    def _on_skill_error(self, p: dict) -> None:
        self.log(f"skill {p['key']}: error - {p['error']}", tone="warn")

    # -- detalle de la skill seleccionada ---------------------------------------------------------
    def _show_skill(self, key: str) -> None:
        info = self.manager.skills[key].info
        self.skill_detail.setText(describe_skill(info, self.ring.views[key], self.ring.last_in.get(key),
                                                 self.ring.last_out.get(key)))

    def _show_free_slot(self, slot) -> None:
        self.ring.selected = None
        self.skill_detail.setText(FREE_SLOT_TEXT % (theme.MUTED, slot))
        self.ring.update()
