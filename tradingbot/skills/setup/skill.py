"""Skill Setup: el ejecutor. Solo actúa cuando Cortex le da la orden de operar en la cuenta del broker."""
from __future__ import annotations

import time
from dataclasses import replace
from datetime import datetime, timedelta

import numpy as np

from ...clock import NY, server_minus_ny
from ...core import Event, Skill, register_skill
from ...timeframes import TIMEFRAMES
from ..levels.daylevels import DEFAULT_US_INDICES
from ..stats.journal import Journal, folder_for
from . import account, store
from .positions import resolve, trackable

DEFAULT_RISK_PCT = 1.0            # SETUP_RISK_PCT: riesgo de cada operación, % del saldo virtual
DEFAULT_BE_TRIGGER_PCT = 1.0      # SETUP_BE_TRIGGER_PCT: ganancia flotante (% del saldo) que pasa el stop a la entrada
CONSOLIDATE_CHECK_SECONDS = 30.0  # cada cuánto se mira si ha terminado una vela de consolidación


@register_skill("setup")
class SetupSkill(Skill):
    title = "Setup"
    description = ("El ejecutor: mete la operación en la cuenta del broker (MT5). Solo recibe órdenes de Cortex, que es "
                   "quien reúne el activo, la temporalidad, el sesgo, la TBR y el patrón válido; Setup no decide nada. "
                   "En casi todos los perfiles funciona en modo simulación: prepara la orden y la anota, pero no la envía a "
                   "MT5. Los perfiles con MT5_<PERFIL>_SEND_ORDERS=true (solo cuentas demo) la envían de verdad, con los lotes "
                   "que arriesgan SETUP_RISK_PCT del saldo real de la cuenta, y mueven el stop y cierran la posición de MT5 "
                   "cuando lo hace la simulada. Sigue las "
                   "posiciones simuladas (stop, objetivo, stop a breakeven y cierre por tiempo) con las velas que le reenvía "
                   "Cortex, y lleva la cuenta virtual del perfil: el saldo de la cuenta al empezar más lo ganado o perdido en "
                   "cada operación (R x riesgo). Las cerradas del forwardtest pasan a la cuenta al consolidar: al cierre de la "
                   "vela de 3 h (índices) o de 4 h (resto) en la que cerraron. Las abiertas y la cuenta se guardan en "
                   "data/perfiles/<perfil>/: se pueden consultar y siguen ahí al reiniciar el bot.")
    subscribes = ("setup.order", "setup.candles", "feed.connected", "clock.offset")
    publishes = ("setup.executed", "setup.closed", "setup.account", "setup.consolidated")
    slot = "aux4"
    interval = CONSOLIDATE_CHECK_SECONDS

    def on_start(self) -> None:
        self.error = "Configuración SETUP no válida"
        self.send_orders = self.settings.get_bool("SEND_ORDERS", False)      # tradingbot.env, bloque SETUP
        if self.send_orders:
            self.error = ("SETUP_SEND_ORDERS=true no se usa: para operar de verdad en una cuenta demo, pon "
                          "MT5_<PERFIL>_SEND_ORDERS=true en el perfil (C:\\Users\\claude\\mt5\\.env) y deja esta clave en false")
            raise ValueError(self.error)
        self.risk_pct = self.settings.get_float("RISK_PCT", DEFAULT_RISK_PCT)
        be_pct = self.settings.get_float("BE_TRIGGER_PCT", DEFAULT_BE_TRIGGER_PCT)
        if self.risk_pct <= 0 or be_pct < 0:
            self.error = (f"SETUP_RISK_PCT={self.risk_pct:g} debe ser mayor que 0 y SETUP_BE_TRIGGER_PCT={be_pct:g}, "
                          "0 (sin breakeven) o más")
            raise ValueError(self.error)
        self.be_r = be_pct / self.risk_pct if be_pct > 0 else None         # p. ej. 1 % de ganancia con 1 % de riesgo: +1 R
        env = self.services.env
        indices = env.get_list("LEVELS_US_INDICES", list(DEFAULT_US_INDICES)) if env is not None else DEFAULT_US_INDICES
        try:
            self.schedule = account.Schedule(self.settings.get_int("CONSOLIDATE_INDEX_HOURS", account.DEFAULT_INDEX_HOURS),
                                             self.settings.get_int("CONSOLIDATE_HOURS", account.DEFAULT_OTHER_HOURS), indices)
        except ValueError as exc:
            self.error = str(exc)
            raise
        # el diario del forwardtest del perfil (el mismo que escribe Stats): lo que se consolida en la cuenta
        self.journal = Journal(folder_for(self.services.app_cfg, env.get("STATS_FORWARD_DIR") if env is not None else None,
                                          type(self.services.source).__name__ == "DemoSource"))
        self.offset: int | None = None                  # desfase del servidor (clock.offset): para saber su hora
        self.error = ""
        self.executed = 0
        self.file = store.file_for(self.services.app_cfg)
        self.positions: list = [o for o in store.load(self.file) if trackable(o)]   # órdenes simuladas abiertas (en disco)
        self.account = account.VirtualAccount(account.file_for(self.services.app_cfg))
        app = (self.services.app_cfg or {}).get("app", {})
        self.live = bool(app.get("send_orders"))       # MT5_<PERFIL>_SEND_ORDERS: opera de verdad en la cuenta (demo)
        self._real: tuple[float, str] | None = None    # último saldo real de la cuenta (perfiles que operan de verdad)
        if app.get("capital"):                          # perfil con capital simulado propio (MT5_<PERFIL>_CAPITAL): no depende del saldo de MT5
            self.account.start(float(app["capital"]), app.get("currency") or "USD")
        self.set_caption(f"{len(self.positions)} posición(es) abierta(s)" if self.positions else "esperando a Cortex")
        self._consolidate()                             # lo que haya terminado mientras el bot estaba parado
        self._publish_account()

    def handle(self, event: Event) -> None:
        if self.error:
            raise ValueError(self.error)
        if event.topic == "feed.connected":
            self._start_account()
            if self.live:
                self._publish_account()
            return
        if event.topic == "clock.offset":
            self.offset = event.payload.get("server_offset")
            self._consolidate()
            return
        if event.source != "cortex":                    # solo Cortex puede dar la orden de operar
            self.set_caption("orden rechazada")
            return
        if event.topic == "setup.candles":
            self._follow(event.payload)
            return
        order = event.payload["order"]
        self.executed += 1
        sent, risk, note = False, (self.account.risk_amount(self.risk_pct) if self.account.started else None), ""
        if self.live and trackable(order):
            order, sent, risk, note = self._send(order)
        if trackable(order):
            self.positions.append(order)
            store.save(self.positions, self.file)
            self._publish_account()
        self.set_caption(f"{'enviada' if sent else 'simulada'}: {order.direction.capitalize()} {order.symbol}")
        if not self.live:
            note = "Modo simulación: la orden está lista pero no se ha enviado a MT5."
        if trackable(order):
            note += (" El resultado se anotará en el Registro y en el Forwardtest cuando la posición cierre (stop, objetivo, "
                     "breakeven o tiempo), y pasará al saldo virtual del perfil al consolidar.")
        self.publish("setup.executed", {"order": order, "sent": sent, "note": note, "risk_amount": risk})

    # -- operativa real (MT5_<PERFIL>_SEND_ORDERS=true) -----------------------------------------
    def _real_balance(self) -> tuple[float, str] | None:
        """Saldo y moneda de la cuenta de MT5 ahora (None sin conexión)."""
        try:
            snap = self.services.source.account()
        except Exception:  # noqa: BLE001 - sin conexión: se usa el último conocido
            return self._real
        if snap is not None and snap.balance > 0:
            self._real = (float(snap.balance), snap.currency)
        return self._real

    def _send(self, order):
        """Abre la posición en MT5 con los lotes que arriesgan SETUP_RISK_PCT del saldo real. Si MT5 no la acepta, la
        operación sigue como simulada (el Forwardtest no cambia) y la nota dice por qué."""
        real = self._real_balance()
        if real is None:
            return order, False, None, "No enviada a MT5: no hay datos de la cuenta. Se sigue como simulada."
        balance, currency = real
        risk = round(balance * self.risk_pct / 100, 2)
        try:
            fill = self.services.source.open_market(order.symbol, order.direction, risk, order.stop, order.target,
                                                    f"TB {order.pattern_key}"[:31])
        except Exception as exc:  # noqa: BLE001 - lo que diga MT5 va a la nota; la simulada sigue
            return order, False, risk, f"No enviada a MT5: {exc}. Se sigue como simulada."
        order = replace(order, ticket=fill.ticket, volume=fill.volume, fill_price=fill.price)
        note = (f"Enviada a MT5: posición {fill.ticket}, {fill.volume:g} lotes de {fill.symbol} a {fill.price:g}, stop "
                f"{order.stop:g} y objetivo {order.target:g}; arriesga {fill.risk:,.2f} {currency} ({self.risk_pct:g} % del saldo "
                f"real, {balance:,.2f}).")
        return order, True, fill.risk, note

    def _breakeven(self, order, ts, high, low):
        """Mueve a la entrada el stop de la posición real en cuanto el precio toca +be_r R (la misma regla que la simulada).
        Devuelve la orden (con be_sent=True si ya se movió)."""
        if self.be_r is None or order.be_sent or not order.ticket or order.stop is None:
            return order
        risk = abs(order.price - order.stop)
        first = int(np.searchsorted(ts, order.entry_ts, "left"))
        if risk <= 0 or first >= len(ts):
            return order
        best = (np.max(high[first:]) - order.price) if order.direction == "long" else (order.price - np.min(low[first:]))
        if best / risk < self.be_r:
            return order
        try:
            moved = self.services.source.set_stop(order.ticket, order.fill_price or order.price)
        except Exception as exc:  # noqa: BLE001 - se reintenta con las próximas velas
            self.set_caption(f"{order.symbol}: no se pudo mover el stop ({exc})")
            return order
        return replace(order, be_sent=True) if moved else order

    def _close_real(self, order) -> dict | None:
        """Cierra en MT5 la posición de una operación que la simulada da por cerrada (si MT5 no la cerró ya con su stop u
        objetivo) y devuelve lo que pasó en la cuenta."""
        if not order.ticket:
            return None
        src, out = self.services.source, {"ticket": order.ticket, "volume": order.volume}
        try:
            out["closed_by_bot"] = src.close_position(order.ticket)
        except Exception as exc:  # noqa: BLE001 - queda abierta en MT5: se dice en el Registro
            out["error"] = str(exc)
            return out
        try:
            out["profit"] = src.realized(order.ticket)
        except Exception:  # noqa: BLE001
            out["profit"] = None
        return out

    def _start_account(self) -> None:
        """La primera conexión del perfil fija su capital inicial: el saldo de la cuenta de MT5 en ese momento."""
        if self.account.started:
            return
        try:
            snap = self.services.source.account()
        except Exception:  # noqa: BLE001 - sin datos de la cuenta se prueba en la próxima conexión
            snap = None
        if snap is not None and self.account.start(snap.balance, snap.currency):
            self._consolidate()
            self._publish_account()

    def tick(self) -> None:
        self._consolidate()
        if self.live:                                   # el saldo real cambia con cada cierre en MT5
            self._publish_account()

    def server_now(self) -> int:
        """Hora del servidor (como si fuera UTC). Hasta que Quotes mida el desfase (con mercados abiertos), la estimada
        de los brokers con cierre en Nueva York: servidor = NY + 7 h, como la del gráfico."""
        if self.offset is not None:
            return int(time.time()) + int(self.offset)
        shift, _ = server_minus_ny(None)
        ny = datetime.now(NY).utcoffset() if NY is not None else timedelta(hours=-5)
        return int(time.time() + ny.total_seconds()) + shift

    def _consolidate(self) -> None:
        """Pasa a la cuenta las cerradas del forwardtest cuya vela de consolidación (3 h índices, 4 h resto) ya terminó."""
        if self.error:
            return
        now = self.server_now()
        before = (len(self.account.trades), list(self.account.pending))
        new = self.account.consolidate(self.journal.closes(), now, self.risk_pct, self.schedule)
        if new:
            self.publish("setup.consolidated", {"trades": new, "balance": self.account.balance,
                                                "currency": self.account.currency})
        if (len(self.account.trades), self.account.pending) != before:
            self._publish_account()

    def _publish_account(self) -> None:
        summary = self.account.summary(self.risk_pct, self.positions)
        if self.live and (real := self._real_balance()) is not None:     # la cabecera muestra el saldo real de la cuenta
            balance, currency = real
            summary.update(balance=balance, currency=currency, risk_amount=balance * self.risk_pct / 100, live=True)
        self.publish("setup.account", summary)

    def _follow(self, payload: dict) -> None:
        """Comprueba stop, objetivo, breakeven y cierre por tiempo de las posiciones abiertas del mercado cuyas velas llegan."""
        df = payload["df"]
        ts, high, low, close = (df[k].to_numpy() for k in ("ts", "high", "low", "close"))
        minutes = TIMEFRAMES.get(payload.get("timeframe") or "")
        now = self.server_now()
        still = []
        changed = False
        for order in self.positions:
            closed = (resolve(order, ts, high, low, close, self.be_r, minutes * 60 if minutes else None, now)
                      if order.symbol == payload["symbol"] else None)
            if closed is None:
                if order.ticket and order.symbol == payload["symbol"]:
                    moved = self._breakeven(order, ts, high, low)
                    changed |= moved is not order
                    order = moved
                still.append(order)
                continue
            real = self._close_real(order)
            self.publish("setup.closed", {"order": order, "closed": closed, "sent": real is not None, "real": real,
                                          "consolidate_at": self.schedule.due(order.symbol, closed.exit_ts),
                                          "consolidate_hours": self.schedule.hours(order.symbol)})
            self.set_caption(f"cerrada: {closed.result} {closed.r:+.2f} R")
        if len(still) != len(self.positions) or changed:
            store.save(still, self.file)
            self.positions = still
            self._publish_account()
        if still:
            self.set_caption(f"{len(still)} posición(es) abierta(s)")
