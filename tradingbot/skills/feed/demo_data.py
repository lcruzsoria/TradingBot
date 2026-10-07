"""Fuente de datos sintética para desarrollar la interfaz sin MT5 (opción --demo)."""
from __future__ import annotations

import time

import numpy as np
import pandas as pd

from .datasource import AccountSnapshot, ProgressFn, Quote, aggregate_candles, normalize_candles
from ...timeframes import DERIVED, minutes

SERVER_OFFSET = 3 * 3600   # el servidor simulado va 3 h por delante de UTC (como muchos brokers en verano)
DAYS = 150          # historial de velas de minutos
HOUR_DAYS = 1500    # historial de velas de 1 hora (para H1 en adelante)
SUNDAY_ANCHOR = 3 * 86400   # el 4-ene-1970 fue domingo: las velas semanales empiezan en domingo

# Precio aproximado de cada símbolo de demostración (la base sintética ronda 1.085)
PRICE = {"EURUSD": 1.0850, "GBPUSD": 1.27, "USDJPY": 158.0, "XAUUSD": 4140.0, "NAS100": 31095.0,
         "US500": 7784.0, "SP500": 7784.0, "DJ30": 52164.0, "GER40": 25265.0, "UK100": 9800.0, "USOIL": 90.6, "BTCUSD": 85600.0, "ETHUSD": 2708.0}
STALE = {"GER40"}   # simula un mercado cerrado


class DemoSource:
    description = "Datos sintéticos (sin MT5)"

    def __init__(self) -> None:
        self._base: pd.DataFrame | None = None
        self._hours: pd.DataFrame | None = None
        self._px: dict[str, float] = {}
        self._rng = np.random.default_rng()

    def connect(self) -> str:
        return "datos sintéticos"

    def symbols(self) -> list[str]:
        return list(PRICE)

    def all_symbols(self) -> list[str]:
        return sorted(PRICE)

    def close(self) -> None:
        pass

    def _minute_bars(self) -> pd.DataFrame:
        if self._base is None:
            rng = np.random.default_rng(7)
            end = pd.Timestamp(time.time() + SERVER_OFFSET, unit="s").floor("min")
            idx = pd.date_range(end - pd.Timedelta(days=DAYS), end, freq="1min")
            idx = idx[idx.dayofweek < 5]
            days = idx.normalize()
            # tendencia distinta cada día + ruido por minuto
            drift_by_day = dict(zip(np.unique(days), rng.normal(0, 1.4e-6, len(np.unique(days)))))
            drift = np.array([drift_by_day[d] for d in days])
            steps = drift + rng.normal(0, 3.2e-5, len(idx))
            close = 1.0850 + np.cumsum(steps)
            open_ = np.concatenate(([close[0]], close[:-1]))
            wick = np.abs(rng.normal(0, 1.8e-5, len(idx)))
            self._base = pd.DataFrame({
                "open": open_,
                "high": np.maximum(open_, close) + wick,
                "low": np.minimum(open_, close) - wick,
                "close": close,
                "tick_volume": rng.integers(20, 400, len(idx)),
            }, index=idx)
        return self._base

    def account(self) -> AccountSnapshot | None:
        profit = round(float(self._rng.normal(0, 40)), 2)
        return AccountSnapshot(100000.0, 100000.0 + profit, profit, "USD")

    def quotes(self, symbols: list[str]) -> dict[str, Quote | None]:
        now = int(time.time()) + SERVER_OFFSET
        out: dict[str, Quote | None] = {}
        for name in symbols:
            key = name.upper()
            if key not in PRICE:
                out[name] = None
                continue
            if key not in self._px:
                self._px[key] = float(self._minute_bars()["close"].iloc[-1]) * PRICE[key] / 1.0850
            self._px[key] *= 1 + self._rng.normal(0, 4e-5)
            mid = self._px[key]
            half = mid * 1.2e-5
            ts = now - (3 * 3600 + 19 * 60 if key in STALE else 0)
            out[name] = Quote(name, mid - half, mid + half, ts)
        return out

    def _hour_bars(self) -> pd.DataFrame:
        """Serie larga de velas de 1 hora que termina en el mismo precio que la de minutos."""
        if self._hours is None:
            rng = np.random.default_rng(11)
            end = pd.Timestamp(time.time() + SERVER_OFFSET, unit="s").floor("h")
            idx = pd.date_range(end - pd.Timedelta(days=HOUR_DAYS), end, freq="1h")
            idx = idx[idx.dayofweek < 5]
            days = idx.normalize()
            uniq = np.unique(days)
            drift_by_day = dict(zip(uniq, rng.normal(0, 8e-5, len(uniq))))
            steps = np.array([drift_by_day[d] for d in days]) + rng.normal(0, 2.4e-4, len(idx))
            close = np.cumsum(steps)
            close = close - close[-1] + float(self._minute_bars()["close"].iloc[-1])   # mismo precio final
            open_ = np.concatenate(([close[0]], close[:-1]))
            wick = np.abs(rng.normal(0, 1.2e-4, len(idx)))
            self._hours = pd.DataFrame({
                "open": open_, "high": np.maximum(open_, close) + wick, "low": np.minimum(open_, close) - wick,
                "close": close, "tick_volume": rng.integers(2000, 20000, len(idx)),
            }, index=idx)
        return self._hours

    def load_candles(self, symbol: str, timeframe: str, progress: ProgressFn | None = None) -> pd.DataFrame:
        m = minutes(timeframe)
        scale = PRICE.get(symbol.upper(), 1.0850) / 1.0850
        if m < 60:
            base = self._minute_bars()
            agg = base.copy() if m == 1 else base.resample(f"{m}min").agg(
                {"open": "first", "high": "max", "low": "min", "close": "last", "tick_volume": "sum"}).dropna()
            out = agg.copy()
            out["ts"] = out.index.astype("datetime64[s]").astype("int64")
            df = normalize_candles(out.reset_index(drop=True))
        else:
            hours = self._hour_bars().copy()
            hours["ts"] = hours.index.astype("datetime64[s]").astype("int64")
            hours = normalize_candles(hours.reset_index(drop=True))
            if m == 60:
                df = hours
            elif m == 10080:
                df = aggregate_candles(hours, 604800, anchor=SUNDAY_ANCHOR)
            else:
                df = aggregate_candles(hours, m * 60)
        df = df.copy()
        df[["open", "high", "low", "close"]] *= scale
        if progress:
            progress(len(df))
        return df
