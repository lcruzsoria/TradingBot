"""Timeframes disponibles en la interfaz."""
from __future__ import annotations

# etiqueta -> minutos
TIMEFRAMES: dict[str, int] = {"1m": 1, "3m": 3, "5m": 5, "15m": 15}
DEFAULT_TIMEFRAME = "15m"


def minutes(label: str) -> int:
    try:
        return TIMEFRAMES[label]
    except KeyError:
        raise ValueError(f"Timeframe no soportado: {label!r}. Opciones: {', '.join(TIMEFRAMES)}") from None


def mt5_constant(mt5_module, label: str) -> int:
    """Devuelve la constante TIMEFRAME_Mx del módulo MetaTrader5."""
    return getattr(mt5_module, f"TIMEFRAME_M{minutes(label)}")
