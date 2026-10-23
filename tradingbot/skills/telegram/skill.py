"""Skill Telegram: avisos al móvil de lo que hace el bot (aperturas y cierres de Setup y, si se quiere, GO / NO GO de Cortex)."""
from __future__ import annotations

from ...core import Event, Skill, register_skill
from ..setup import store
from . import client, messages

NOTIFY_ALL = ("abre", "cierra", "go", "nogo")
DEFAULT_NOTIFY = ("abre", "cierra")


def _key(order) -> tuple:
    return order.symbol, order.direction, order.pattern_key, order.entry_ts


@register_skill("telegram")
class TelegramSkill(Skill):
    title = "Telegram"
    description = ("Avisos al móvil por Telegram: cuando Setup abre una operación y cuando cierra (TP, SL, BE o tiempo, con su R) "
                   "y, si se activa, cada GO / NO GO de Cortex. Solo avisa de lo que pasa en directo: lo que el bot repasa al "
                   "arrancar no se manda. El token y el chat van en el fichero de cuentas, fuera del repositorio.")
    subscribes = ("candles.loaded", "cortex.decision", "setup.executed", "setup.closed")
    publishes = ()
    slot = "aux4"

    def on_start(self) -> None:
        self.error = ""
        self.enabled = self.settings.get_bool("ENABLED", False)   # tradingbot.env, bloque TELEGRAM
        if not self.enabled:
            self.set_caption("apagado")
            return
        notify = [n.lower().replace(" ", "") for n in self.settings.get_list("NOTIFY", list(DEFAULT_NOTIFY))]
        unknown = [n for n in notify if n not in NOTIFY_ALL]
        if unknown:
            self.error = f"TELEGRAM_NOTIFY: {', '.join(unknown)} no existe (usa {', '.join(NOTIFY_ALL)})"
            raise ValueError(self.error)
        self.notify = set(notify)
        app = self.services.app_cfg.get("app") or {}
        self.profile = app.get("profile_name")
        self.token, self.chat = client.credentials(app.get("env_file"))
        if not self.token or not self.chat:
            self.error = ("Faltan TELEGRAM_TOKEN y TELEGRAM_CHAT_ID en el fichero de cuentas (fuera del repo) "
                          "o en variables de entorno")
            raise ValueError(self.error)
        self._start: dict[str, int] = {}                     # mercado -> última vela al arrancar: lo anterior no se avisa
        self._known = {_key(o) for o in store.load(store.file_for(self.services.app_cfg))}   # abiertas de antes: su cierre sí
        self.sent = 0
        if self.settings.get_bool("NOTIFY_START", True):
            self._send(messages.started(self.profile))
        self.set_caption("conectado")

    def handle(self, event: Event) -> None:
        if not self.enabled:
            return
        if self.error:
            raise ValueError(self.error)
        p = event.payload
        if event.topic == "candles.loaded":
            df = p.get("df")
            if df is not None and len(df):
                self._start.setdefault(str(p["symbol"]).lower(), int(df["ts"].iloc[-1]))
        elif event.topic == "setup.executed":
            order = p["order"]
            if self._live(order.symbol, order.entry_ts):
                self._known.add(_key(order))
                if "abre" in self.notify:
                    self._send(messages.opened(order, self.profile))
        elif event.topic == "setup.closed":
            order = p["order"]
            if (_key(order) in self._known or self._live(order.symbol, order.entry_ts)) and "cierra" in self.notify:
                self._send(messages.closed(order, p["closed"], self.profile))
            self._known.discard(_key(order))
        elif event.topic == "cortex.decision":
            wanted = "go" if p["decision"].allowed else "nogo"
            if wanted in self.notify and self._live(p["symbol"], getattr(p["hit"], "ts", None)):
                self._send(messages.decision(p, self.profile))

    def _live(self, symbol: str, ts) -> bool:
        """Si la vela es del arranque en adelante (como el forwardtest): lo que Pattern y Cortex repasan al arrancar
        ya pasó y no se avisa. Sin velas de ese mercado aún no se sabe: tampoco se avisa, para no mandar el repaso."""
        start = self._start.get((symbol or "").lower())
        return start is not None and ts is not None and int(ts) >= start

    def _send(self, text: str) -> None:
        client.send_message(self.token, self.chat, text)
        self.sent += 1
        self.set_caption(f"{self.sent} aviso(s)")
