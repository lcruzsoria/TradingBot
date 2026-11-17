"""Fuente de datos real: terminal MetaTrader 5 (solo Windows).

Lee velas, cotizaciones y la cuenta. Solo envía órdenes (abrir, mover el stop, cerrar) en los perfiles con
MT5_<PERFIL>_SEND_ORDERS=true, y solo si la cuenta conectada es demo: en una cuenta real las rechaza.
"""
from __future__ import annotations

import math
import re
import threading
import time

import pandas as pd

from ...config import Mt5Profile
from .datasource import AccountSnapshot, Fill, ProgressFn, Quote, aggregate_candles, normalize_candles
from ...timeframes import DERIVED, SESSION_ANCHORED, base_timeframe, minutes, mt5_constant

CHUNK = 50_000
MAGIC = 3_690_369          # número mágico de las órdenes del bot: así se distinguen de las que se abren a mano
DEVIATION = 20             # desvío máximo del precio al enviar una orden a mercado, en puntos

# El mismo mercado con otro nombre según el broker (USOIL en MetaQuotes es CL-OIL.s en PUPrime). Solo nombres que no son
# también acciones: DOW, CL o SPX son empresas en algunos brokers.
ALIASES: tuple[tuple[str, ...], ...] = (
    ("NAS100", "USTEC", "US100", "NDX100"),
    ("SP500", "US500", "SPX500"),
    ("DJ30", "US30", "WS30"),
    ("GER40", "DE40", "GER30", "DAX40"),
    ("USOIL", "WTI", "XTIUSD", "USOUSD", "CL-OIL"),
    ("UKOIL", "BRENT", "XBRUSD"),
    ("XAUUSD", "GOLD"),
    ("XAGUSD", "SILVER"),
)
SUFFIX = r"(?:[.\-_#][a-z0-9]*)?"                    # .s, .r, -cs, #...: lo que el broker añade al nombre


def equivalent(name: str, names: dict[str, str], explicit: dict[str, str] | None = None) -> str | None:
    """Nombre exacto en el broker del mercado `name` del bot. Por orden: la equivalencia propia del perfil
    (MT5_<PERFIL>_SYMBOLS), el mismo nombre, el mismo nombre con sufijo (NAS100 -> NAS100.s) y sus otros nombres
    (USOIL -> CL-OIL.s). Con varios candidatos, el más corto. `names`: nombre en minúsculas -> nombre exacto."""
    key = name.strip().lower()
    if explicit and key in explicit:
        return names.get(explicit[key].strip().lower())
    group = next((g for g in ALIASES if key in {a.lower() for a in g}), ())
    for alt in [key] + [a.lower() for a in group if a.lower() != key]:
        if alt in names:
            return names[alt]
        pattern = re.compile(re.escape(alt) + SUFFIX)
        found = sorted((actual for low, actual in names.items() if pattern.fullmatch(low)), key=lambda n: (len(n), n))
        if found:
            return found[0]
    return None


class Mt5Error(Exception):
    """Error de conexión o lectura con MT5."""


class TradeError(Mt5Error):
    """MT5 no ha aceptado una orden (o el bot no la envía: cuenta real, lote mínimo, precio ya pasado...)."""


class Mt5Source:
    def __init__(self, profile: Mt5Profile, max_bars: int = 20_000):
        self.profile = profile
        self.max_bars = max_bars
        self.description = profile.label
        self._mt5 = None
        # La API de MT5 no es reentrante: se serializan las llamadas entre hilos.
        self._lock = threading.RLock()
        self._missing: set[str] = set()
        self._names: dict[str, str] | None = None   # nombre en minúsculas -> nombre exacto del broker

    # -- conexión ---------------------------------------------------------
    def connect(self) -> str:
        with self._lock:
            return self._connect()

    def _connect(self) -> str:
        try:
            import MetaTrader5 as mt5
        except ImportError as exc:  # pragma: no cover - solo Windows
            raise Mt5Error("No se pudo importar MetaTrader5 (solo disponible en Windows). Usa --demo para probar sin MT5.") from exc

        p = self.profile
        kwargs: dict = {}
        if p.terminal_path:
            kwargs["path"] = p.terminal_path
        if p.password:
            kwargs.update(login=p.login, password=p.password, server=p.server)
        if not mt5.initialize(**kwargs):
            raise Mt5Error(f"No se pudo conectar con el terminal MT5 (¿está abierto?): {mt5.last_error()}")
        self._mt5 = mt5

        info = mt5.account_info()
        if info is not None and info.login != p.login:
            # Sin contraseña en el perfil, MT5 usa la que el terminal tenga guardada para esa cuenta: así un mismo
            # terminal sirve para varios perfiles y al cambiar de perfil cambia de cuenta.
            logged = (mt5.login(p.login, password=p.password, server=p.server) if p.password
                      else mt5.login(p.login, server=p.server))
            if logged:
                info = mt5.account_info()
            else:
                actual = info.login
                self.close()
                raise Mt5Error(f"El terminal está en la cuenta {actual}, pero el perfil '{p.name}' es la {p.login}. "
                               "Abre esa cuenta en MT5 o añade la contraseña al perfil.")
        if info is None:
            self.close()
            raise Mt5Error(f"MT5 no devuelve datos de la cuenta: {mt5.last_error()}")

        is_demo = info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO
        if p.is_demo and not is_demo:
            self.close()
            raise Mt5Error(f"El perfil '{p.name}' se llama demo, pero la cuenta {info.login} NO es demo. Conexión cancelada.")
        kind = "DEMO" if is_demo else "REAL"
        return f"MT5 {kind} {info.login}  {info.currency} {info.balance:,.2f}"

    def close(self) -> None:
        with self._lock:
            if self._mt5 is not None:
                self._mt5.shutdown()
                self._mt5 = None
            self._names = None

    # -- datos ------------------------------------------------------------
    def symbols(self) -> list[str]:
        with self._lock:
            return self._symbols()

    def all_symbols(self) -> list[str]:
        with self._lock:
            return sorted(self._broker_names(self._require()).values(), key=str.lower)

    def _symbols(self) -> list[str]:
        mt5 = self._require()
        found = mt5.symbols_get() or []
        visibles = sorted(s.name for s in found if s.visible)
        return visibles or sorted(s.name for s in found)[:200]

    def account(self) -> AccountSnapshot | None:
        with self._lock:
            try:
                mt5 = self._require()
            except TradeError:                          # en otra cuenta y sin poder volver: no hay lectura de la suya
                return None
            info = self._own_account(mt5) if self.profile.send_orders else mt5.account_info()
            if info is None:
                return None
            return AccountSnapshot(float(info.balance), float(info.equity), float(info.profit), str(info.currency))

    def quotes(self, symbols: list[str]) -> dict[str, Quote | None]:
        with self._lock:
            mt5 = self._require()
            out: dict[str, Quote | None] = {}
            for name in symbols:
                if name in self._missing:
                    out[name] = None
                    continue
                exact = self._resolve(mt5, name)
                if exact is None:
                    self._missing.add(name)  # no existe en este broker: no reintentar cada segundo
                    out[name] = None
                    continue
                tick = mt5.symbol_info_tick(exact)
                if tick is None and mt5.symbol_select(exact, True):
                    tick = mt5.symbol_info_tick(exact)
                if tick is None or (tick.bid == 0 and tick.ask == 0):
                    out[name] = None
                else:
                    out[name] = Quote(name, float(tick.bid), float(tick.ask), int(tick.time))
            return out

    def load_candles(self, symbol: str, timeframe: str, progress: ProgressFn | None = None) -> pd.DataFrame:
        with self._lock:
            return self._load_candles(symbol, timeframe, progress)

    def load_recent(self, symbol: str, timeframe: str, bars: int) -> pd.DataFrame:
        """Solo las últimas `bars` velas (base): lo que usa el barrido de mercados en segundo plano."""
        with self._lock:
            return self._load_candles(symbol, timeframe, None, max(1, min(bars, self.max_bars)))

    def _load_candles(self, symbol: str, timeframe: str, progress: ProgressFn | None = None,
                      limit: int | None = None) -> pd.DataFrame:
        """Carga todas las velas que el terminal pueda entregar (o las `limit` últimas), de la más reciente hacia atrás."""
        mt5 = self._require()
        base = base_timeframe(timeframe)
        tf = mt5_constant(mt5, base)
        exact = self.resolve_symbol(symbol)
        if exact is None:
            hints = self.similar_symbols(symbol)
            raise Mt5Error(f"El símbolo '{symbol}' no existe en este broker."
                           + (f" Nombres parecidos: {', '.join(hints)}." if hints else ""))
        symbol = exact
        if not mt5.symbol_select(symbol, True):
            raise Mt5Error(f"No se pudo activar el símbolo '{symbol}' en MT5: {mt5.last_error()}")

        frames: list[pd.DataFrame] = []
        total = 0
        limit = self.max_bars if limit is None else limit
        while total < limit:
            count = min(CHUNK, limit - total)
            rates = self._copy_rates(mt5, symbol, tf, total, count, first=(total == 0))
            if rates is None or len(rates) == 0:
                break
            frames.append(pd.DataFrame(rates))
            total += len(rates)
            if progress:
                progress(total)
            if len(rates) < count:
                break
        if not frames:
            raise Mt5Error(f"Sin velas para {symbol} {timeframe}: {mt5.last_error()}")

        df = normalize_candles(pd.concat(frames[::-1], ignore_index=True).rename(columns={"time": "ts"}))
        if timeframe in DERIVED:          # p. ej. 7h: MT5 no lo tiene, se agrupa desde 1h
            df = aggregate_candles(df, minutes(timeframe) * 60, day_offset=SESSION_ANCHORED.get(timeframe))
        return df

    def last_bar_ts(self, symbol: str, timeframe: str) -> int | None:
        """Hora (servidor) de la vela más reciente que tiene el terminal, en la temporalidad base: para saber si hay velas
        nuevas sin recargarlo todo. None si no hay datos."""
        with self._lock:
            mt5 = self._require()
            exact = self.resolve_symbol(symbol)
            if exact is None:
                return None
            rates = mt5.copy_rates_from_pos(exact, mt5_constant(mt5, base_timeframe(timeframe)), 0, 1)
            return int(rates[-1]["time"]) if rates is not None and len(rates) else None

    # -- nombres de símbolo -----------------------------------------------
    def _broker_names(self, mt5) -> dict[str, str]:
        if self._names is None:
            self._names = {}
            for sym in mt5.symbols_get() or []:
                self._names.setdefault(sym.name.lower(), sym.name)
        return self._names

    def _resolve(self, mt5, name: str) -> str | None:
        return equivalent(name, self._broker_names(mt5), self.profile.symbol_map)

    def resolve_symbol(self, name: str) -> str | None:
        """Nombre exacto del símbolo en este broker, o el de su equivalente (NAS100 -> NAS100.s). MT5 distingue
        mayúsculas: 'NAS100FT.R' no es 'NAS100FT.r'."""
        with self._lock:
            return self._resolve(self._require(), name)

    def equivalents(self, names: list[str]) -> dict[str, str | None]:
        """Los nombres del bot que este broker llama de otra forma (o que no tiene: None)."""
        with self._lock:
            mt5 = self._require()
            out = {n: self._resolve(mt5, n) for n in names}
        return {n: exact for n, exact in out.items() if exact != n}

    def similar_symbols(self, name: str, limit: int = 8) -> list[str]:
        """Símbolos del broker que contienen la parte principal del nombre (antes del primer . - _ #)."""
        with self._lock:
            names = self._broker_names(self._require())
        base = re.split(r"[.\-_#]", name.strip())[0].lower()
        if not base:
            return []
        return sorted(actual for low, actual in names.items() if base in low)[:limit]

    # -- operativa (solo MT5_<PERFIL>_SEND_ORDERS=true y cuenta demo) --------------
    def open_market(self, symbol: str, direction: str, risk_money: float, stop: float, target: float,
                    comment: str = "TradingBot") -> Fill:
        """Abre a mercado `direction` ("long"/"short") en `symbol` con su stop y su objetivo, con los lotes que hacen que tocar
        el stop cueste `risk_money` (redondeados hacia abajo al paso de lote del broker). TradeError si no se puede."""
        with self._lock:
            mt5 = self._trading()
            exact = self._resolve(mt5, symbol)
            if exact is None or not mt5.symbol_select(exact, True):
                raise TradeError(f"el símbolo '{symbol}' no existe en este broker")
            info, tick = mt5.symbol_info(exact), mt5.symbol_info_tick(exact)
            if info is None or tick is None or not tick.bid or not tick.ask:
                raise TradeError(f"{exact} sin cotización (¿mercado cerrado?)")
            if int(getattr(info, "trade_mode", 4)) == 0:          # SYMBOL_TRADE_MODE_DISABLED: se ve pero no se opera
                raise TradeError(f"{exact} no se puede operar en este broker (fija otro con MT5_<PERFIL>_SYMBOLS, p. ej. "
                                 f"{symbol}={exact}.s)")
            long = direction == "long"
            kind = mt5.ORDER_TYPE_BUY if long else mt5.ORDER_TYPE_SELL
            price = float(tick.ask if long else tick.bid)
            digits = int(info.digits)
            stop, target = round(float(stop), digits), round(float(target), digits)
            if (long and not stop < price < target) or (not long and not target < price < stop):
                raise TradeError(f"el precio ({price:.{digits}f}) ya está fuera del stop ({stop:.{digits}f}) o del objetivo "
                                 f"({target:.{digits}f})")
            volume, per_lot = self._volume(mt5, info, kind, price, stop, risk_money)
            if volume <= 0:
                raise TradeError(f"con {risk_money:,.2f} de riesgo no llega al lote mínimo de {exact} ({info.volume_min:g} lotes "
                                 f"arriesgan {per_lot * info.volume_min:,.2f})")
            result = mt5.order_send({"action": mt5.TRADE_ACTION_DEAL, "symbol": exact, "volume": volume, "type": kind,
                                     "price": price, "sl": stop, "tp": target, "deviation": DEVIATION, "magic": MAGIC,
                                     "comment": comment[:31], "type_time": mt5.ORDER_TIME_GTC,
                                     "type_filling": self._filling(mt5, info)})
            self._check(mt5, result, f"abrir {direction} {exact}")
            ticket = self._position_ticket(mt5, result, exact)
            filled = float(result.price or price)
            return Fill(ticket, exact, float(result.volume or volume), filled, round(per_lot * volume, 2))

    def position_open(self, ticket: int) -> bool:
        with self._lock:
            return bool(self._require().positions_get(ticket=int(ticket)))

    def set_stop(self, ticket: int, stop: float) -> bool:
        """Mueve el stop de la posición (conserva el objetivo). False si la posición ya no existe."""
        with self._lock:
            mt5 = self._trading()
            found = mt5.positions_get(ticket=int(ticket))
            if not found:
                return False
            pos = found[0]
            info = mt5.symbol_info(pos.symbol)
            stop = round(float(stop), int(info.digits)) if info is not None else float(stop)
            result = mt5.order_send({"action": mt5.TRADE_ACTION_SLTP, "position": int(ticket), "symbol": pos.symbol,
                                     "sl": stop, "tp": float(pos.tp), "magic": MAGIC})
            self._check(mt5, result, f"mover el stop de {pos.symbol} a {stop}")
            return True

    def close_position(self, ticket: int, comment: str = "TradingBot cierre") -> bool:
        """Cierra la posición a mercado. False si ya estaba cerrada (stop u objetivo en MT5)."""
        with self._lock:
            mt5 = self._trading()
            found = mt5.positions_get(ticket=int(ticket))
            if not found:
                return False
            pos = found[0]
            info, tick = mt5.symbol_info(pos.symbol), mt5.symbol_info_tick(pos.symbol)
            if info is None or tick is None:
                raise TradeError(f"{pos.symbol} sin cotización para cerrar la posición {ticket}")
            buy = pos.type == mt5.POSITION_TYPE_BUY
            result = mt5.order_send({"action": mt5.TRADE_ACTION_DEAL, "position": int(ticket), "symbol": pos.symbol,
                                     "volume": float(pos.volume), "type": mt5.ORDER_TYPE_SELL if buy else mt5.ORDER_TYPE_BUY,
                                     "price": float(tick.bid if buy else tick.ask), "deviation": DEVIATION, "magic": MAGIC,
                                     "comment": comment[:31], "type_time": mt5.ORDER_TIME_GTC,
                                     "type_filling": self._filling(mt5, info)})
            self._check(mt5, result, f"cerrar la posición {ticket} de {pos.symbol}")
            return True

    DEAL_REASONS = {4: "sl", 5: "tp", 6: "stopout", 3: "bot"}     # DEAL_REASON_SL, _TP, _SO, _EXPERT; el resto: a mano

    def closing(self, ticket: int) -> dict | None:
        """Cierre de la posición según MT5: precio medio y hora (servidor) de las operaciones de salida, resultado total en
        dinero (beneficio + comisión + swap) y motivo ("sl", "tp", "bot", "stopout" o "manual"). None si sigue abierta o
        aún no consta."""
        with self._lock:
            mt5 = self._require()
            if mt5.positions_get(ticket=int(ticket)):
                return None
            deals = mt5.history_deals_get(position=int(ticket)) or ()
            outs = [d for d in deals if int(d.entry) in (1, 3)]          # DEAL_ENTRY_OUT, DEAL_ENTRY_OUT_BY
            if not outs:
                return None
            volume = sum(float(d.volume) for d in outs) or 1.0
            last = max(outs, key=lambda d: int(d.time_msc or d.time * 1000))
            return {"price": sum(float(d.price) * float(d.volume) for d in outs) / volume, "ts": int(last.time),
                    "profit": round(sum(float(d.profit) + float(d.commission) + float(d.swap) + float(getattr(d, "fee", 0.0))
                                        for d in deals), 2),
                    "reason": self.DEAL_REASONS.get(int(last.reason), "manual")}

    def realized(self, ticket: int) -> float | None:
        """Resultado de la posición ya cerrada, en la moneda de la cuenta (beneficio + comisión + swap). None si no consta."""
        with self._lock:
            mt5 = self._require()
            deals = mt5.history_deals_get(position=int(ticket))
            if not deals:
                return None
            return round(sum(float(d.profit) + float(d.commission) + float(d.swap) + float(getattr(d, "fee", 0.0))
                             for d in deals), 2)

    def _trading(self):
        """La conexión, si en ella se puede operar: solo en cuentas demo (es lo que permite MT5_<PERFIL>_SEND_ORDERS)."""
        mt5 = self._require()
        info = mt5.account_info()
        if info is None:
            raise TradeError(f"MT5 no devuelve datos de la cuenta: {mt5.last_error()}")
        if info.login != self.profile.login:
            other = info.login
            info = self._own_account(mt5)
            if info is None:
                raise TradeError(f"el terminal está en la cuenta {other}, no en la {self.profile.login} del perfil, y no se pudo volver a ella")
        if info.trade_mode != mt5.ACCOUNT_TRADE_MODE_DEMO:
            raise TradeError(f"la cuenta {info.login} NO es demo: el bot solo envía órdenes a cuentas demo")
        return mt5

    @staticmethod
    def _volume(mt5, info, kind, price: float, stop: float, risk_money: float) -> tuple[float, float]:
        """(lotes, pérdida por lote si toca el stop). Los lotes, hacia abajo al paso del broker y como mucho el máximo;
        0 si no llega al mínimo."""
        loss = mt5.order_calc_profit(kind, info.name, 1.0, price, stop)
        if loss is None or loss >= 0:                       # sin cálculo del terminal: con el valor del tick
            loss = -abs(price - stop) / float(info.trade_tick_size) * float(info.trade_tick_value)
        per_lot = abs(float(loss))
        if per_lot <= 0 or risk_money <= 0:
            return 0.0, per_lot
        step = float(info.volume_step) or 0.01
        lots = min(math.floor(risk_money / per_lot / step + 1e-9) * step, float(info.volume_max))
        decimals = max(0, -int(math.floor(math.log10(step)))) if step < 1 else 0
        lots = round(lots, decimals)
        return (lots if lots >= float(info.volume_min) else 0.0), per_lot

    @staticmethod
    def _filling(mt5, info) -> int:
        """Tipo de ejecución que admite el símbolo: FOK, IOC o, si no, RETURN."""
        mode = int(getattr(info, "filling_mode", 0) or 0)
        if mode & 1:
            return mt5.ORDER_FILLING_FOK
        if mode & 2:
            return mt5.ORDER_FILLING_IOC
        return mt5.ORDER_FILLING_RETURN

    @staticmethod
    def _check(mt5, result, what: str) -> None:
        if result is None:
            raise TradeError(f"MT5 no responde al {what}: {mt5.last_error()}")
        if result.retcode not in (mt5.TRADE_RETCODE_DONE, mt5.TRADE_RETCODE_DONE_PARTIAL, mt5.TRADE_RETCODE_PLACED):
            raise TradeError(f"MT5 rechaza {what}: {result.retcode} {result.comment}")

    @staticmethod
    def _position_ticket(mt5, result, symbol: str) -> int:
        """Ticket de la posición recién abierta: el de la orden (cuentas con cobertura) o, si no, la última del bot en el
        símbolo (cuentas netting)."""
        if result.order and mt5.positions_get(ticket=int(result.order)):
            return int(result.order)
        mine = [p for p in mt5.positions_get(symbol=symbol) or () if p.magic == MAGIC]
        return int(max(mine, key=lambda p: p.time_msc).ticket) if mine else int(result.order)

    # -- internos ---------------------------------------------------------
    def _own_account(self, mt5):
        """Los datos de la cuenta del perfil. Si otro proceso ha cambiado el terminal de cuenta (otro perfil en el mismo MT5), vuelve a ella;
        None si no lo consigue o si MT5 da una lectura a medias (equity 0 con saldo: el terminal está cambiando de cuenta)."""
        p = self.profile
        info = mt5.account_info()
        if info is not None and info.login != p.login:
            logged = (mt5.login(p.login, password=p.password, server=p.server) if p.password else mt5.login(p.login, server=p.server))
            info = mt5.account_info() if logged else None
        if info is None or info.login != p.login or (info.balance > 0 and info.equity <= 0):
            return None
        return info

    def _require(self):
        if self._mt5 is None:
            raise Mt5Error("No hay conexión con MT5.")
        if self.profile.send_orders:                    # perfil que opera de verdad: velas, precios y cuenta, solo de la suya
            mt5, p = self._mt5, self.profile
            info = mt5.account_info()
            if info is not None and info.login != p.login:
                logged = (mt5.login(p.login, password=p.password, server=p.server) if p.password
                          else mt5.login(p.login, server=p.server))
                if not logged or getattr(mt5.account_info(), "login", None) != p.login:
                    raise TradeError(f"El terminal está en la cuenta {info.login} y no se pudo volver a la {p.login} del perfil "
                                   f"'{p.name}': sin datos hasta que vuelva (no se leen velas de otro broker).")
        return self._mt5

    @staticmethod
    def _copy_rates(mt5, symbol, tf, start_pos, count, first: bool):
        # El historial puede tardar en sincronizarse la primera vez.
        attempts = 5 if first else 1
        for attempt in range(attempts):
            rates = mt5.copy_rates_from_pos(symbol, tf, start_pos, count)
            if rates is not None and len(rates) > 0:
                return rates
            if attempt < attempts - 1:
                time.sleep(1.0)
        return rates
