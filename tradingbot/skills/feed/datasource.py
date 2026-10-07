"""Contrato común de las fuentes de datos (MT5 real o datos sintéticos)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

import numpy as np
import pandas as pd

ProgressFn = Callable[[int], None]

CANDLE_COLUMNS = ["ts", "time", "open", "high", "low", "close", "tick_volume"]


@dataclass(frozen=True)
class Quote:
    """Último tick de un símbolo. ts = epoch en hora del servidor del broker."""
    symbol: str
    bid: float
    ask: float
    ts: int


@dataclass(frozen=True)
class AccountSnapshot:
    balance: float
    equity: float
    profit: float      # P&L flotante de las posiciones abiertas
    currency: str


class DataSource(Protocol):
    description: str

    def connect(self) -> str:
        """Conecta y devuelve un texto descriptivo de la cuenta/fuente."""

    def symbols(self) -> list[str]: ...

    def all_symbols(self) -> list[str]:
        """Todos los símbolos que ofrece el broker (para elegir la watchlist)."""

    def load_candles(self, symbol: str, timeframe: str, progress: ProgressFn | None = None) -> pd.DataFrame: ...

    def quotes(self, symbols: list[str]) -> dict[str, Quote | None]:
        """Último tick de cada símbolo (None si no está disponible en el broker)."""

    def account(self) -> AccountSnapshot | None:
        """Saldo, equity y P&L flotante de la cuenta conectada."""

    def close(self) -> None: ...


def aggregate_candles(df: pd.DataFrame, seconds: int, anchor: int = 0) -> pd.DataFrame:
    """Agrupa velas en velas más largas de `seconds` segundos.

    - Menos de un día: las velas se alinean con la medianoche (hora del servidor) de cada día, así que
      la última vela del día puede ser más corta (por ejemplo, con 7 h: 00-07, 07-14, 14-21 y 21-24).
    - Un día o más: ventanas consecutivas desde `anchor` (epoch en segundos).
    """
    ts = df["ts"].to_numpy(dtype=np.int64)
    if seconds < 86400:
        start = ts - ts % 86400 + (ts % 86400) // seconds * seconds
    else:
        start = (ts - anchor) // seconds * seconds + anchor
    grouped = df.assign(ts=start).groupby("ts", sort=True)
    out = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                      close=("close", "last"), tick_volume=("tick_volume", "sum")).reset_index()
    return normalize_candles(out)


def normalize_candles(df: pd.DataFrame) -> pd.DataFrame:
    """Ordena, elimina duplicados y fija el esquema estándar de velas.

    - ts:   epoch en segundos (hora del servidor del broker, tratada como UTC)
    - time: datetime naive equivalente a ts
    """
    df = df.drop_duplicates(subset="ts").sort_values("ts").reset_index(drop=True)
    df["ts"] = df["ts"].astype(np.int64)
    df["time"] = pd.to_datetime(df["ts"], unit="s")
    if "tick_volume" not in df:
        df["tick_volume"] = 0
    return df[CANDLE_COLUMNS]
