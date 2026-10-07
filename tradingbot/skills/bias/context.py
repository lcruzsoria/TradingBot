"""Contexto que reciben las reglas: velas del día en curso y del día anterior."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd


@dataclass
class BiasContext:
    candles: pd.DataFrame          # histórico completo (columnas estándar)
    day: date                      # día de trading evaluado (hora del servidor del broker)
    today: pd.DataFrame            # velas de ese día
    prev: pd.DataFrame | None      # velas del día de trading anterior (si existe)

    @property
    def last_price(self) -> float | None:
        return float(self.today["close"].iloc[-1]) if len(self.today) else None

    @property
    def day_open(self) -> float | None:
        return float(self.today["open"].iloc[0]) if len(self.today) else None

    @property
    def prev_high(self) -> float | None:
        return float(self.prev["high"].max()) if self.prev is not None and len(self.prev) else None

    @property
    def prev_low(self) -> float | None:
        return float(self.prev["low"].min()) if self.prev is not None and len(self.prev) else None

    @property
    def prev_close(self) -> float | None:
        return float(self.prev["close"].iloc[-1]) if self.prev is not None and len(self.prev) else None


def build_context(candles: pd.DataFrame, day: date | None = None) -> BiasContext | None:
    """Construye el contexto del día indicado (por defecto, el de la última vela)."""
    if candles is None or len(candles) == 0:
        return None
    if day is None:
        day = candles["time"].iloc[-1].date()
    start = pd.Timestamp(day) - pd.Timedelta(days=10)
    window = candles[(candles["time"] >= start) & (candles["time"] < pd.Timestamp(day) + pd.Timedelta(days=1))]
    dates = window["time"].dt.date
    today = window[dates == day]
    earlier = sorted(d for d in dates.unique() if d < day)
    prev = window[dates == earlier[-1]] if earlier else None
    return BiasContext(candles=candles, day=day, today=today, prev=prev)
