"""Skill Setup: el ejecutor. Solo actúa cuando Cortex le da la orden de operar en la cuenta del broker."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np

from ...core import Event, Skill, register_skill
from ...timeframes import TIMEFRAMES
from ..levels.daylevels import DEFAULT_US_INDICES
from ..stats.journal import Journal, folder_for
from . import account, challenge, live, store
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
                   "que arriesgan SETUP_RISK_PCT del saldo real de la cuenta, solo si la señal es nueva; mueven el stop a "
                   "breakeven, cierran por tiempo y su Forwardtest es la imagen de la cuenta: entrada, salida y resultado "
                   "los de MT5. Sigue las "
                   "posiciones simuladas (stop, objetivo, stop a breakeven y cierre por tiempo) con las velas que le reenvía "
                   "Cortex, y lleva la cuenta virtual del perfil: el saldo de la cuenta al empezar más lo ganado o perdido en "
                   "cada operación (R x riesgo). Las cerradas del forwardtest pasan a la cuenta al consolidar: al cierre de la "
                   "vela de 3 h (índices) o de 4 h (resto) en la que cerraron. Las abiertas y la cuenta se guardan en "
                   "data/perfiles/<perfil>/: se pueden consultar y siguen ahí al reiniciar el bot.")
    subscribes = ("setup.order", "setup.candles", "feed.connected", "clock.offset")
    publishes = ("setup.executed", "setup.closed", "setup.account", "setup.consolidated", "setup.skipped",
                 "setup.challenge", "setup.trading")
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
        strategy = (self.services.app_cfg["app"].get("strategy") or "") if self.services.app_cfg else ""
        if strategy and self.services.env is not None:                       # <ESTRATEGIA>_SETUP_BE_TRIGGER_PCT: el perfil de estrategia usa el suyo (0: sin breakeven)
            be_pct = self.services.env.section(f"{strategy}_SETUP").get_float("BE_TRIGGER_PCT", be_pct)
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
        self.since = live.since(self.services.app_cfg) if self.live else None   # desde cuándo opera de verdad (UTC)
        self._trade_block: str | None = None            # por qué MT5 rechazaría ahora las órdenes (None: las acepta)
        self._trade_checked = False
        self._candles: dict[str, tuple] = {}            # últimas velas de cada mercado con posición real (máximo y mínimo en R)
        self.challenge = None                           # challenge simulado sobre la cuenta real (SETUP_CHALLENGE_*)
        target = self.settings.get("CHALLENGE_TARGET_PCT", "") or ",".join(map(str, challenge.DEFAULT_TARGET_PCT))
        if self.live and target.strip() not in ("0", "0.0"):
            try:                                        # un valor por fase (8,8 y 6,5) o uno para todas
                self.challenge = challenge.Challenge(
                    Path(app["data_dir"]) / challenge.FILE if app.get("data_dir") else challenge.FILE, target,
                    self.settings.get("CHALLENGE_MAX_DD_PCT", "") or ",".join(map(str, challenge.DEFAULT_MAX_DD_PCT)),
                    self.settings.get_int("CHALLENGE_PHASES", challenge.DEFAULT_PHASES))
            except ValueError as exc:
                self.error = f"SETUP_CHALLENGE_*: {exc}"
                raise
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
                self._check_trading()
                self._check_challenge()
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
        if self.live:
            self._live_order(order)
            return
        if trackable(order):
            self.positions.append(order)
            store.save(self.positions, self.file)
            self._publish_account()
        self.set_caption(f"simulada: {order.direction.capitalize()} {order.symbol}")
        note = "Modo simulación: la orden está lista pero no se ha enviado a MT5."
        if trackable(order):
            note += (" El resultado se anotará en el Registro y en el Forwardtest cuando la posición cierre (stop, objetivo, "
                     "breakeven o tiempo), y pasará al saldo virtual del perfil al consolidar.")
        self.publish("setup.executed", {"order": order, "sent": False, "note": note,
                                        "risk_amount": self.account.risk_amount(self.risk_pct) if self.account.started else None})

    def _live_order(self, order) -> None:
        """Perfil que opera de verdad: solo abre en MT5 las señales nuevas; lo que no llega a la cuenta no cuenta (no entra
        en el Forwardtest: este es la imagen de la cuenta) y Cortex libera el mercado."""
        bar = TIMEFRAMES.get(order.timeframe)
        now = self.server_now()
        if self.challenge is not None and self.challenge.blocks_trading:
            reason = self.challenge.blocks_trading
        elif not trackable(order):
            reason = "la orden no trae stop, objetivo y horas de entrada y de cierre"
        elif not live.fresh(order, now, live.to_server(self.since, self.offset) if self.since else None,
                            bar * 60 if bar else None):
            reason = "la señal es de antes de que el perfil empezara a operar, o ya es vieja: no se abre tarde"
        else:
            order, sent, risk, note = self._send(order)
            if sent:
                self.positions.append(order)
                store.save(self.positions, self.file)
                self._publish_account()
                self.set_caption(f"enviada: {order.direction.capitalize()} {order.symbol}")
                self.publish("setup.executed", {"order": order, "sent": True, "note": note, "risk_amount": risk})
                return
            reason = note
        self.set_caption(f"no enviada: {order.direction.capitalize()} {order.symbol}")
        self.publish("setup.skipped", {"order": order, "note": reason})

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
            return order, False, None, "no hay datos de la cuenta de MT5"
        balance, currency = real
        risk = round(balance * self.risk_pct / 100, 2)
        try:
            fill = self.services.source.open_market(order.symbol, order.direction, risk, order.stop, order.target,
                                                    f"TB {order.pattern_key}"[:31])
        except Exception as exc:  # noqa: BLE001 - lo que diga MT5 va a la nota
            return order, False, risk, str(exc)
        order = replace(order, ticket=fill.ticket, volume=fill.volume, signal_price=order.price, price=fill.price,
                        risk_money=fill.risk)
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
            moved = self.services.source.set_stop(order.ticket, order.price)       # el precio real de entrada
        except Exception as exc:  # noqa: BLE001 - se reintenta con las próximas velas
            self.set_caption(f"{order.symbol}: no se pudo mover el stop ({exc})")
            return order
        return replace(order, be_sent=True, be_at=self.server_now()) if moved else order

    def _sync_real(self) -> None:
        """Las posiciones reales: cierra por tiempo las que llegan a su hora y apunta las que MT5 ya ha cerrado (stop,
        objetivo, breakeven, el bot o a mano), con su precio, su hora y su resultado de la cuenta."""
        if not self.positions:
            return
        src, now, still = self.services.source, self.server_now(), []
        for order in self.positions:
            try:
                if order.close_ts and now >= order.close_ts:
                    src.close_position(order.ticket)
                deal = src.closing(order.ticket)
            except Exception as exc:  # noqa: BLE001 - sin conexión: se mira en la próxima vuelta
                self.set_caption(f"{order.symbol}: sin datos de MT5 ({exc})")
                still.append(order)
                continue
            if deal is None:
                still.append(order)
                continue
            ts, high, low = self._candles.get(order.symbol, (None, None, None))
            closed = live.closed_from_broker(order, deal, ts, high, low)
            self.publish("setup.closed", {"order": order, "closed": closed, "sent": True,
                                          "real": {"ticket": order.ticket, "volume": order.volume, "profit": deal["profit"],
                                                   "closed_by_bot": deal.get("reason") == "bot"},
                                          "consolidate_at": self.schedule.due(order.symbol, closed.exit_ts),
                                          "consolidate_hours": self.schedule.hours(order.symbol)})
            self.set_caption(f"cerrada en MT5: {closed.result} {deal['profit']:+,.2f}")
        if len(still) != len(self.positions):
            store.save(still, self.file)
            self.positions = still
            self._publish_account()

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
        if self.live:                                   # cierres en MT5 y el saldo real, que cambia con cada uno
            self._check_trading()
            self._sync_real()
            self._check_challenge()
            self._publish_account()

    def _check_trading(self) -> None:
        """Si MT5 aceptaría ahora las órdenes del bot (Algo Trading activado...). Avisa (setup.trading: Registro y Telegram)
        al detectar que no, y otra vez cuando vuelve a aceptarlas; mientras tanto las señales se quedan sin enviar."""
        check = getattr(self.services.source, "trading_block", None)
        if check is None:
            return
        try:
            block = check()
        except Exception:  # noqa: BLE001 - sin conexión: en la próxima vuelta
            return
        if block == self._trade_block:
            return
        first, self._trade_block = self._trade_block is None and not self._trade_checked, block
        self._trade_checked = True
        if block is None and first:                     # al arrancar con todo bien no hace falta avisar
            return
        self.set_caption("MT5 no acepta órdenes" if block else "MT5 vuelve a aceptar órdenes")
        self.publish("setup.trading", {"blocked": block})

    def _check_challenge(self) -> None:
        """Challenge simulado: al llegar al objetivo cierra lo abierto y congela la cuenta hasta las 00:00 (entonces empieza la
        fase siguiente); si el equity toca el drawdown máximo, cierra lo abierto y deja de operar. Cada cambio sale en setup.challenge (Registro y Telegram)."""
        if self.challenge is None:
            return
        try:
            snap = self.services.source.account()
        except Exception:  # noqa: BLE001 - sin conexión: en la próxima vuelta
            return
        if snap is None:
            return
        for event in self.challenge.update(snap.balance, snap.equity, snap.currency):
            if event["kind"] in ("suspendido", "fase"):      # suspendido, o fase superada: cuenta congelada hasta mañana
                for order in self.positions:
                    try:
                        self.services.source.close_position(order.ticket)
                    except Exception as exc:  # noqa: BLE001 - se dice en el Registro
                        event.setdefault("errors", []).append(f"{order.symbol} ({order.ticket}): {exc}")
                self._sync_real()
            self.publish("setup.challenge", event)

    def server_now(self) -> int:
        """Hora del servidor (como si fuera UTC). Hasta que Quotes mida el desfase (con mercados abiertos), la estimada
        de los brokers con cierre en Nueva York: servidor = NY + 7 h, como la del gráfico."""
        return live.server_now(self.offset)

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
        if self.challenge is not None and self.challenge.started:
            summary["challenge"] = self.challenge.summary()
        if self.live and (real := self._real_balance()) is not None:     # la cabecera: el saldo real de la cuenta...
            balance, currency = real
            extra = self.challenge.adjustment if self.challenge is not None else 0.0
            # ...más las operaciones recuperadas del Forwardtest que no están en MT5 (equipo suspendido): saldo y resultado
            # son los del Forwardtest. El riesgo de cada orden sigue saliendo del saldo real.
            summary.update(balance=balance + extra, currency=currency, risk_amount=balance * self.risk_pct / 100, live=True,
                           real_balance=balance, recovered=extra)
        self.publish("setup.account", summary)

    def _follow(self, payload: dict) -> None:
        """Comprueba stop, objetivo, breakeven y cierre por tiempo de las posiciones abiertas del mercado cuyas velas llegan."""
        df = payload["df"]
        ts, high, low, close = (df[k].to_numpy() for k in ("ts", "high", "low", "close"))
        if self.live:                                   # la posición la cierra MT5 (o el bot por tiempo): aquí solo el breakeven
            self._candles[payload["symbol"]] = (ts, high, low)
            moved = [self._breakeven(o, ts, high, low) if o.symbol == payload["symbol"] else o for o in self.positions]
            if any(a is not b for a, b in zip(moved, self.positions)):
                self.positions = moved
                store.save(moved, self.file)
            self._sync_real()
            return
        minutes = TIMEFRAMES.get(payload.get("timeframe") or "")
        now = self.server_now()
        still = []
        for order in self.positions:
            closed = (resolve(order, ts, high, low, close, self.be_r, minutes * 60 if minutes else None, now)
                      if order.symbol == payload["symbol"] else None)
            if closed is None:
                still.append(order)
                continue
            self.publish("setup.closed", {"order": order, "closed": closed, "sent": False,
                                          "consolidate_at": self.schedule.due(order.symbol, closed.exit_ts),
                                          "consolidate_hours": self.schedule.hours(order.symbol)})
            self.set_caption(f"cerrada: {closed.result} {closed.r:+.2f} R")
        if len(still) != len(self.positions):
            store.save(still, self.file)
            self.positions = still
            self._publish_account()
        if still:
            self.set_caption(f"{len(still)} posición(es) abierta(s)")
