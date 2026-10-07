"""Timeframes disponibles en la interfaz.

Claves internas: 1m 3m 5m 15m 1h 3h 4h 7h 12h 1d 1w. En pantalla se ven como M1 M3 M5 M15 H1 H3 H4 H7 H12 1D 1W.

MT5 no tiene H7 (solo H1, H2, H3, H4, H6, H8 y H12), así que 7h se construye agrupando velas de 1h
(ver DERIVED y datasource.aggregate_candles).
"""
from __future__ import annotations

# clave -> minutos que dura la vela
TIMEFRAMES: dict[str, int] = {
    "1m": 1, "3m": 3, "5m": 5, "15m": 15,
    "1h": 60, "3h": 180, "4h": 240, "7h": 420, "12h": 720,
    "1d": 1440, "1w": 10080,
}
DEFAULT_TIMEFRAME = "15m"

# clave -> constante del módulo MetaTrader5
NATIVE: dict[str, str] = {
    "1m": "TIMEFRAME_M1", "3m": "TIMEFRAME_M3", "5m": "TIMEFRAME_M5", "15m": "TIMEFRAME_M15",
    "1h": "TIMEFRAME_H1", "3h": "TIMEFRAME_H3", "4h": "TIMEFRAME_H4", "12h": "TIMEFRAME_H12",
    "1d": "TIMEFRAME_D1", "1w": "TIMEFRAME_W1",
}

# timeframes que MT5 no ofrece y se construyen a partir de otro: clave -> timeframe base
DERIVED: dict[str, str] = {"7h": "1h"}


def minutes(label: str) -> int:
    try:
        return TIMEFRAMES[label]
    except KeyError:
        raise ValueError(f"Timeframe no soportado: {label!r}. Opciones: {', '.join(TIMEFRAMES)}") from None


def display_label(label: str) -> str:
    """Nombre que se ve en pantalla: M15, H4, 1D, 1W."""
    m = minutes(label)
    if m < 60:
        return f"M{m}"
    if m < 1440:
        return f"H{m // 60}"
    return "1D" if m == 1440 else "1W"


def base_timeframe(label: str) -> str:
    """Timeframe que hay que pedir realmente a MT5 (el mismo, salvo en los derivados)."""
    minutes(label)
    return DERIVED.get(label, label)


def mt5_constant(mt5_module, label: str) -> int:
    """Devuelve la constante TIMEFRAME_* de MetaTrader5 (solo para timeframes nativos)."""
    try:
        return getattr(mt5_module, NATIVE[label])
    except KeyError:
        raise ValueError(f"'{label}' no es un timeframe nativo de MT5 (usa base_timeframe).") from None
