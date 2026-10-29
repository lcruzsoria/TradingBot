"""Fibonacci de un tramo con pivotes de tres velas: lo usa el patrón Reversión.

Todo se calcula «en largo» (el origen es un mínimo y el tramo sube); el corto es el espejo con los precios cambiados de signo.

- Nivel 1: el origen del tramo (la mecha pivote en Reversión).
- Nivel 0: el primer pivote confirmado (el máximo más alto en la vela del medio de `k` velas a cada lado) tras el origen. Queda fijo:
  un pivote posterior más alto no lo alarga. Mientras no hay pivote confirmado, el 0 provisional es el extremo que lleva el precio.
- Entrada: la primera vela que revierte hasta el 0,5 (su mínimo lo toca) viniendo de arriba (abre por encima del 0,5), a partir de
  la vela que confirma el pivote del 0 (incluida): el pivote fija el 0, pero la entrada solo pide que el precio toque el 0,5.
- Si el precio pierde el origen antes de la entrada (mínimo por debajo del nivel 1), el tramo se anula.
- Stop y objetivo en los niveles de PATTERN_STOP_LEVEL (1 al inicio: la mecha pivote o el swing) y PATTERN_TARGET_LEVEL (-0,2 al
  inicio; el -0,5 sería media vuelta del tramo más allá del 0). Con entrada en el 0,5: RR = (0,5 - objetivo) / (stop - 0,5).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


DEFAULT_STOP_LEVEL = 1.0           # PATTERN_STOP_LEVEL: el stop en el nivel 1 (la mecha pivote o el swing)
DEFAULT_TARGET_LEVEL = -0.2        # PATTERN_TARGET_LEVEL: el objetivo (backtest 2018-2026: mejor que el -0,5 de antes)


def level_settings(get) -> tuple[float, float]:
    """(stop, objetivo) del bloque PATTERN (PATTERN_STOP_LEVEL, PATTERN_TARGET_LEVEL), como niveles del fibo."""
    try:
        sl = float(str(get("STOP_LEVEL", DEFAULT_STOP_LEVEL)).replace(",", "."))
        tp = float(str(get("TARGET_LEVEL", DEFAULT_TARGET_LEVEL)).replace(",", "."))
    except ValueError:
        raise ValueError("PATTERN_STOP_LEVEL y PATTERN_TARGET_LEVEL deben ser números (por ejemplo 1 y -0.2).") from None
    if not 0.5 < sl <= 2:
        raise ValueError(f"PATTERN_STOP_LEVEL={sl:g}: el stop debe estar más allá de la entrada (0,5) y no más lejos que el 2.")
    if not -2 <= tp < 0.5:
        raise ValueError(f"PATTERN_TARGET_LEVEL={tp:g}: el objetivo debe estar por debajo de la entrada (0,5) y no más allá del -2.")
    return sl, tp


def level_name(x: float) -> str:
    """Nombre del nivel como se dibuja en el gráfico: -0.2 -> «-0,2», 1.0 -> «1»."""
    return f"{x:g}".replace(".", ",")


def at_level(zero: float, origin: float, x: float) -> float:
    """Precio del nivel `x` de un fibo con el 0 en `zero` y el 1 en `origin` (0,5 = la entrada; negativos, más allá del 0)."""
    return zero + x * (origin - zero)


def fibo_levels(zero: float, origin: float, sl: float, tp: float, sign: float) -> dict[str, float]:
    """Los niveles que se dibujan: el objetivo y el stop configurados, el 0, el 0,5 (la entrada) y el 1 (la estructura)."""
    out = {level_name(tp): sign * at_level(zero, origin, tp), "0": sign * zero, "0,5": sign * (zero + origin) / 2, "1": sign * origin}
    if sl != 1.0:
        out[level_name(sl)] = sign * at_level(zero, origin, sl)
    return out


def rr_of(sl: float, tp: float) -> float:
    return (0.5 - tp) / (sl - 0.5)


@dataclass(frozen=True)
class FiboState:
    zero: float | None        # primer pivote confirmado (None si todavía no hay ninguno)
    zero_idx: int
    running: float            # extremo que lleva el precio desde el origen (el 0 provisional)
    entry: tuple[int, float] | None   # (vela de la entrada, nivel 0,5)
    breach: int | None        # vela en la que el precio perdió el origen antes de la entrada

    @property
    def extreme(self) -> float:
        """El 0 que se dibuja: el primer pivote; mientras no hay ninguno, el extremo que lleva el precio."""
        return self.running if self.zero is None else self.zero


def run_fibo(H: np.ndarray, L: np.ndarray, last_done: int, end: int, origin: float, k: int, first_pivot: int,
             running: float, O: np.ndarray | None = None) -> FiboState:
    """Recorre las velas `last_done + 1 .. end`. `first_pivot`: primera vela que puede ser el pivote del 0; `running`: extremo ya visto.
    `O`: aperturas (con el mismo signo que H y L): si se dan, la vela de la entrada debe abrir por encima del 0,5."""
    zero, zero_idx = None, -1
    for t in range(last_done + 1, end + 1):
        if L[t] < origin:
            return FiboState(zero, zero_idx, running, None, t)              # perdió el origen antes de la entrada
        p = t - k                                                           # la vela t confirma el pivote de k velas atrás
        if p >= max(first_pivot, k) and H[p] > H[p - k:p].max() and H[p] > H[p + 1:p + k + 1].max():
            if zero is None:
                zero, zero_idx = float(H[p]), p                             # el primer pivote fija el 0
        running = max(running, float(H[t]))
        if zero is not None and t >= zero_idx + k and L[t] <= (zero + origin) / 2 and (O is None or O[t] > (zero + origin) / 2):
            return FiboState(zero, zero_idx, running, (t, (zero + origin) / 2), None)
    return FiboState(zero, zero_idx, running, None, None)
