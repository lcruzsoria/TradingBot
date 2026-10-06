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

    def load_candles(self, symbol: str, timeframe: str, progress: ProgressFn | None = None) -> pd.DataFrame: ...

    def quotes(self, symbols: list[str]) -> dict[str, Quote | None]:
        """Último tick de cada símbolo (None si no está disponible en el broker)."""

    def account(self) -> AccountSnapshot | None:
        """Saldo, equity y P&L flotante de la cuenta conectada."""

    def close(self) -> None: ...


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
