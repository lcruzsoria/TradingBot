"""Skill Móvil: el bot en el móvil. Avisos por Telegram (aperturas y cierres de Setup y, si se quiere, GO / NO GO de Cortex) y
un panel web de solo lectura (abiertas, cierres, sesgo y decisiones) que se abre en el navegador del móvil."""
from __future__ import annotations

import ipaddress
import re
import time

from ...core import Event, Skill, register_skill
from ...envconfig import EnvConfig
from ..setup import store
from . import card, messages, telegram
from .panel import PanelServer, PanelState
from .secrets import secret

NOTIFY_ALL = ("abre", "cierra", "go", "nogo")
DEFAULT_NOTIFY = ("abre", "cierra")
DEFAULT_PORT = 8765
CAPTURE_TIMEOUT = 15.0                                       # segundos que se espera a la ventana


COMMAND_NAME = re.compile(r"^[a-z0-9_]{1,32}$")                  # lo que Telegram admite como nombre de comando


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
    subscribes = ("candles.loaded", "quotes.updated", "bias.updated", "cortex.decision", "setup.executed", "setup.closed",
                  "movil.capture")
    publishes = ("movil.capture.request",)
    slot = "aux4"
    interval = 3.0                                          # cada cuánto se miran los comandos que llegan por Telegram

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
        self.commands = settings.get_bool("COMMANDS", True)
        self.accounts = self._accounts()                     # un comando por cuenta: /puprime, /metaquotes...
        self._offset: int | None = None                      # siguiente mensaje de Telegram por leer
        self._capture_asked: float | None = None             # cuándo se pidió a la ventana una captura (/captura)
        self.token, self.chat = telegram.credentials(self.env_file)
        if not self.token or not self.chat:
            self.error = ("Faltan TELEGRAM_TOKEN y TELEGRAM_CHAT_ID en el fichero de cuentas (fuera del repo) "
                          "o en variables de entorno")
            raise ValueError(self.error)
        self._known = {_key(o) for o in store.load(store.file_for(self.services.app_cfg))}   # abiertas de antes: su cierre sí
        if self.commands:
            self._skip_backlog()
        if settings.get_bool("NOTIFY_START", True):
            self._send(messages.started(self.profile))

    def _accounts(self) -> dict[str, str]:
        """Los perfiles del selector (cuentas) con nombre válido de comando de Telegram: {nombre: texto del menú}."""
        taken = {c for c, _ in messages.COMMANDS} | {"start", "help"}
        found = {}
        for name, display in (self.services.app_cfg.get("app") or {}).get("profiles") or []:
            name = str(name).lower()
            if COMMAND_NAME.match(name) and name not in taken:
                found[name] = f"Forwardtest de {display}"
        return found

    def _command_menu(self) -> list[tuple[str, str]]:
        return [*messages.COMMANDS, *self.accounts.items()]

    def _send(self, text: str) -> None:
        telegram.send_message(self.token, self.chat, text)
        self.sent += 1
        self._caption()

    # -- comandos por Telegram: /estado, /abiertas... (solo desde tu chat, solo lectura) ----------------
    def _skip_backlog(self) -> None:
        """Lo que se escribió con el bot parado no se contesta: se sigue desde el último mensaje."""
        try:
            old = telegram.get_updates(self.token, -1)
            self._offset = old[-1]["update_id"] + 1 if old else 0
            telegram.set_commands(self.token, self._command_menu())
        except telegram.TelegramError:
            self._offset = None                              # sin red al arrancar: se reintenta en el primer tick

    def tick(self) -> None:
        if not self.telegram or not self.commands or self.error:
            return
        if self._capture_asked is not None and time.monotonic() - self._capture_asked > CAPTURE_TIMEOUT:
            self._capture_asked = None
            self._send("La ventana del bot no ha contestado: ¿está abierta la interfaz?")
        try:
            if self._offset is None:
                self._skip_backlog()
                return
            for update in telegram.get_updates(self.token, self._offset):
                self._offset = update["update_id"] + 1
                self._command(update.get("message") or {})
        except telegram.TelegramError:
            return                                           # un fallo de red no es un error de la skill: se reintenta

    def _command(self, message: dict) -> None:
        if str((message.get("chat") or {}).get("id")) != str(self.chat):
            return                                           # solo contesta a tu chat
        text = (message.get("text") or "").strip()
        if not text.startswith("/"):
            return
        command = text[1:].split()[0].split("@")[0].lower() if len(text) > 1 else ""
        if command == "panel":
            self._photo(card.render(self.board.snapshot()))
            return
        if command in self.accounts:                         # el forwardtest de esa cuenta: solo sus operaciones
            snap = self.board.snapshot(command)
            self._photo(card.render_operations(snap), f"<b>Forwardtest · {command}</b> <i>{snap['updated']}</i>")
            return
        if command == "captura":                             # la ventana la dibuja la interfaz (hilo de Qt): se le pide
            self._capture_asked = time.monotonic()
            self.publish("movil.capture.request", {"request_id": "tg"})
            return
        reply = None if command in ("ayuda", "start", "help") else messages.answer(command, self.board.snapshot())
        self._send(reply if reply is not None else messages.help_text(tuple(self.accounts.items())))

    def _photo(self, png: bytes, caption: str | None = None) -> None:
        if caption is None:
            stamp = self.board.snapshot()["updated"]
            caption = f"<i>{stamp}{' · ' + self.profile if self.profile else ''}</i>"
        telegram.send_photo(self.token, self.chat, png, caption)
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
        if topic == "movil.capture":                         # la captura que pidió /captura, ya dibujada por la interfaz
            if self.telegram and self._capture_asked is not None:
                self._capture_asked = None
                if p.get("png"):
                    self._photo(p["png"])
                else:
                    self._send("No se pudo capturar la ventana.")
            return
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
