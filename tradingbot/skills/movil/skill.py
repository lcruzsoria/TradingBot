"""Skill Móvil: el bot en el móvil. Avisos por Telegram (aperturas y cierres de Setup y, si se quiere, GO / NO GO de Cortex) y
un panel web de solo lectura (abiertas, cierres, sesgo y decisiones) que se abre en el navegador del móvil."""
from __future__ import annotations

import ipaddress

from ...core import Event, Skill, register_skill
from ...envconfig import EnvConfig
from ..setup import store
from . import messages, telegram
from .panel import PanelServer, PanelState
from .secrets import secret

NOTIFY_ALL = ("abre", "cierra", "go", "nogo")
DEFAULT_NOTIFY = ("abre", "cierra")
DEFAULT_PORT = 8765


def _key(order) -> tuple:
    return order.symbol, order.direction, order.pattern_key, order.entry_ts


def _loopback(host: str) -> bool:
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


@register_skill("movil")
class MovilSkill(Skill):
    title = "Móvil"
    description = ("El bot en el móvil. Telegram: avisa cuando Setup abre una operación y cuando cierra (TP, SL, BE o tiempo, "
                   "con su R) y, si se activa, de cada GO / NO GO de Cortex; solo lo que pasa en directo, no el repaso al "
                   "arrancar. Panel: una página web de solo lectura con las abiertas, los cierres, el sesgo y las decisiones, "
                   "que se abre en el navegador del móvil. Los secretos (token, chat, clave) van fuera del repositorio.")
    subscribes = ("candles.loaded", "quotes.updated", "bias.updated", "cortex.decision", "setup.executed", "setup.closed")
    publishes = ()
    slot = "aux4"

    def on_start(self) -> None:
        self.error = ""
        env = self.services.env if self.services.env is not None else EnvConfig()
        app = self.services.app_cfg.get("app") or {}
        self.profile = app.get("profile_name")
        self.env_file = app.get("env_file")
        self._start: dict[str, int] = {}                     # mercado -> última vela al arrancar: lo anterior no se avisa
        self.sent = 0
        self.server: PanelServer | None = None
        self.board = PanelState(self.services.app_cfg, env.section("STATS").get("FORWARD_DIR"))
        self.telegram = False
        self._start_panel(env.section("PANEL"))                     # primero el panel: un fallo de Telegram no lo apaga
        self._start_telegram(env.section("TELEGRAM"))
        self._caption()

    def on_stop(self) -> None:
        if self.server is not None:
            self.server.stop()
            self.server = None

    # -- Telegram -----------------------------------------------------------------------------------
    def _start_telegram(self, settings: EnvConfig) -> None:
        self.telegram = settings.get_bool("ENABLED", False)          # tradingbot.env, bloque TELEGRAM
        if not self.telegram:
            return
        notify = [n.lower().replace(" ", "") for n in settings.get_list("NOTIFY", list(DEFAULT_NOTIFY))]
        unknown = [n for n in notify if n not in NOTIFY_ALL]
        if unknown:
            self.error = f"TELEGRAM_NOTIFY: {', '.join(unknown)} no existe (usa {', '.join(NOTIFY_ALL)})"
            raise ValueError(self.error)
        self.notify = set(notify)
        self.token, self.chat = telegram.credentials(self.env_file)
        if not self.token or not self.chat:
            self.error = ("Faltan TELEGRAM_TOKEN y TELEGRAM_CHAT_ID en el fichero de cuentas (fuera del repo) "
                          "o en variables de entorno")
            raise ValueError(self.error)
        self._known = {_key(o) for o in store.load(store.file_for(self.services.app_cfg))}   # abiertas de antes: su cierre sí
        if settings.get_bool("NOTIFY_START", True):
            self._send(messages.started(self.profile))

    def _send(self, text: str) -> None:
        telegram.send_message(self.token, self.chat, text)
        self.sent += 1
        self._caption()

    # -- panel ------------------------------------------------------------------------------------
    def _start_panel(self, settings: EnvConfig) -> None:
        if not settings.get_bool("ENABLED", False):                  # tradingbot.env, bloque PANEL
            return
        host = settings.get("HOST", "127.0.0.1") or "127.0.0.1"
        port = settings.get_int("PORT", DEFAULT_PORT)
        token = secret("PANEL_TOKEN", self.env_file)
        if not _loopback(host) and not token:
            self.error = (f"PANEL_HOST={host} abre el panel a otros equipos: pon antes una clave PANEL_TOKEN en el fichero "
                          "de cuentas (fuera del repo)")
            raise ValueError(self.error)
        try:
            self.server = PanelServer(self.board, host, port, token)
        except OSError as exc:
            self.error = f"el panel no puede usar {host}:{port} ({exc.strerror or exc})"
            raise ValueError(self.error) from None
        self.server.start()

    def _caption(self) -> None:
        parts = []
        if self.telegram:
            parts.append(f"{self.sent} aviso(s)")
        if self.server is not None:
            parts.append(f"panel :{self.server.port}")
        self.set_caption(" · ".join(parts) if parts else "apagado")

    # -- mensajes del bot -------------------------------------------------------------------------
    def handle(self, event: Event) -> None:
        if self.error:
            raise ValueError(self.error)
        p = event.payload
        topic = event.topic
        if topic == "quotes.updated":
            self.board.quotes(p)
        elif topic == "bias.updated":
            self.board.bias_updated(p)
        elif topic == "candles.loaded":
            df = p.get("df")
            if df is not None and len(df):
                self._start.setdefault(str(p["symbol"]).lower(), int(df["ts"].iloc[-1]))
        elif topic == "cortex.decision":
            if not self._live(p["symbol"], getattr(p["hit"], "ts", None)):
                return
            self.board.decision(p)
            wanted = "go" if p["decision"].allowed else "nogo"
            if self.telegram and wanted in self.notify:
                self._send(messages.decision(p, self.profile))
        elif topic == "setup.executed" and self.telegram:
            order = p["order"]
            if self._live(order.symbol, order.entry_ts):
                self._known.add(_key(order))
                if "abre" in self.notify:
                    self._send(messages.opened(order, self.profile))
        elif topic == "setup.closed" and self.telegram:
            order = p["order"]
            if (_key(order) in self._known or self._live(order.symbol, order.entry_ts)) and "cierra" in self.notify:
                self._send(messages.closed(order, p["closed"], self.profile))
            self._known.discard(_key(order))

    def _live(self, symbol: str, ts) -> bool:
        """Si la vela es del arranque en adelante (como el forwardtest): lo que Pattern y Cortex repasan al arrancar
        ya pasó y no se avisa. Sin velas de ese mercado aún no se sabe: tampoco se avisa, para no mandar el repaso."""
        start = self._start.get((symbol or "").lower())
        return start is not None and ts is not None and int(ts) >= start
