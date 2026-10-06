"""Fuente de datos sintética para desarrollar la interfaz sin MT5 (opción --demo)."""
from __future__ import annotations

import time

import numpy as np
import pandas as pd

from .datasource import AccountSnapshot, ProgressFn, Quote, normalize_candles
from .timeframes import minutes

DAYS = 150

# Precio aproximado de cada símbolo de demostración (la base sintética ronda 1.085)
PRICE = {"EURUSD": 1.0850, "GBPUSD": 1.27, "USDJPY": 158.0, "XAUUSD": 4140.0, "NAS100": 31095.0,
         "US500": 7784.0, "GER40": 25265.0, "USOIL": 90.6, "BTCUSD": 85600.0, "ETHUSD": 2708.0}
STALE = {"GER40"}   # simula un mercado cerrado


class DemoSource:
    description = "Datos sintéticos (sin MT5)"

    def __init__(self) -> None:
        self._base: pd.DataFrame | None = None
        self._px: dict[str, float] = {}
        self._rng = np.random.default_rng()

    def connect(self) -> str:
        return "datos sintéticos"

    def symbols(self) -> list[str]:
        return list(PRICE)

    def close(self) -> None:
        pass

    def _minute_bars(self) -> pd.DataFrame:
        if self._base is None:
            rng = np.random.default_rng(7)
            end = pd.Timestamp(time.time(), unit="s").floor("min")
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
        now = int(time.time())
        out: dict[str, Quote | None] = {}
        for name in symbols:
            if name not in PRICE:
                out[name] = None
                continue
            if name not in self._px:
                self._px[name] = float(self._minute_bars()["close"].iloc[-1]) * PRICE[name] / 1.0850
            self._px[name] *= 1 + self._rng.normal(0, 4e-5)
            mid = self._px[name]
            half = mid * 1.2e-5
            ts = now - (3 * 3600 + 19 * 60 if name in STALE else 0)
            out[name] = Quote(name, mid - half, mid + half, ts)
        return out

    def load_candles(self, symbol: str, timeframe: str, progress: ProgressFn | None = None) -> pd.DataFrame:
        m = minutes(timeframe)
        base = self._minute_bars()
        if m == 1:
            agg = base.copy()
        else:
            agg = base.resample(f"{m}min").agg({"open": "first", "high": "max", "low": "min",
                                                "close": "last", "tick_volume": "sum"}).dropna()
        scale = PRICE.get(symbol, 1.0850) / 1.0850
        out = agg.copy()
        out[["open", "high", "low", "close"]] *= scale
        out["ts"] = (out.index.astype("datetime64[s]").astype("int64"))
        df = out.reset_index(drop=True)
        if progress:
            progress(len(df))
        return normalize_candles(df)
