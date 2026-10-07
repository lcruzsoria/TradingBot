"""Fuente de datos real: terminal MetaTrader 5 (solo Windows).

Solo LECTURA: no hay ninguna llamada para enviar o modificar órdenes.
"""
from __future__ import annotations

import re
import threading
import time

import pandas as pd

from .config import Mt5Profile
from .datasource import AccountSnapshot, ProgressFn, Quote, aggregate_candles, normalize_candles
from .timeframes import DERIVED, base_timeframe, minutes, mt5_constant

CHUNK = 50_000


class Mt5Error(Exception):
    """Error de conexión o lectura con MT5."""


class Mt5Source:
    def __init__(self, profile: Mt5Profile, max_bars: int = 2_000_000):
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
            if p.password and mt5.login(p.login, password=p.password, server=p.server):
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
            info = self._require().account_info()
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
                exact = self._broker_names(mt5).get(name.strip().lower())
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

    def _load_candles(self, symbol: str, timeframe: str, progress: ProgressFn | None = None) -> pd.DataFrame:
        """Carga todas las velas que el terminal pueda entregar, de la más reciente hacia atrás."""
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
        while total < self.max_bars:
            count = min(CHUNK, self.max_bars - total)
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
            df = aggregate_candles(df, minutes(timeframe) * 60)
        return df

    # -- nombres de símbolo -----------------------------------------------
    def _broker_names(self, mt5) -> dict[str, str]:
        if self._names is None:
            self._names = {}
            for sym in mt5.symbols_get() or []:
                self._names.setdefault(sym.name.lower(), sym.name)
        return self._names

    def resolve_symbol(self, name: str) -> str | None:
        """Nombre exacto del símbolo en este broker. MT5 distingue mayúsculas: 'NAS100FT.R' no es 'NAS100FT.r'."""
        with self._lock:
            return self._broker_names(self._require()).get(name.strip().lower())

    def similar_symbols(self, name: str, limit: int = 8) -> list[str]:
        """Símbolos del broker que contienen la parte principal del nombre (antes del primer . - _ #)."""
        with self._lock:
            names = self._broker_names(self._require())
        base = re.split(r"[.\-_#]", name.strip())[0].lower()
        if not base:
            return []
        return sorted(actual for low, actual in names.items() if base in low)[:limit]

    # -- internos ---------------------------------------------------------
    def _require(self):
        if self._mt5 is None:
            raise Mt5Error("No hay conexión con MT5.")
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
