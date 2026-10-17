"""Fibonacci de un tramo con pivotes de tres velas: lo comparten los patrones Continuación y Reversión.

Todo se calcula «en largo» (el origen es un mínimo y el tramo sube); el corto es el espejo con los precios cambiados de signo.

- Nivel 1: el origen del tramo (el swing en Continuación, la mecha pivote en Reversión).
- Nivel 0: el último pivote confirmado (el máximo más alto en la vela del medio de `k` velas a cada lado) tras el origen. Un pivote
  posterior más alto alarga el tramo. Mientras no hay pivote confirmado, el 0 provisional es el extremo que lleva el precio.
- Entrada: la primera vela que revierte hasta el 0,5 (su mínimo lo toca), con el 0 vigente en ese momento.
- Si el precio pierde el origen antes de la entrada (mínimo por debajo del nivel 1), el tramo se anula.
- Stop en el nivel 1 y objetivo en el nivel -0,5 (media vuelta del tramo más allá del 0): con entrada en el 0,5 son 2R.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FiboState:
    zero: float | None        # último pivote confirmado (None si todavía no hay ninguno)
    zero_idx: int
    running: float            # extremo que lleva el precio desde el origen (el 0 provisional)
    entry: tuple[int, float] | None   # (vela de la entrada, nivel 0,5)
    breach: int | None        # vela en la que el precio perdió el origen antes de la entrada

    @property
    def extreme(self) -> float:
        """El 0 que se dibuja: el pivote ya fijado al entrar; mientras no, el más alto entre el pivote y el extremo del precio."""
        if self.entry is not None:
            return self.zero
        return self.running if self.zero is None else max(self.zero, self.running)


def run_fibo(H: np.ndarray, L: np.ndarray, last_done: int, end: int, origin: float, k: int, first_pivot: int,
             running: float) -> FiboState:
    """Recorre las velas `last_done + 1 .. end`. `first_pivot`: primera vela que puede ser el pivote del 0; `running`: extremo ya visto."""
    zero, zero_idx = None, -1
    for t in range(last_done + 1, end + 1):
        if L[t] < origin:
            return FiboState(zero, zero_idx, running, None, t)              # perdió el origen antes de la entrada
        p = t - k                                                           # la vela t confirma el pivote de k velas atrás
        if p >= max(first_pivot, k) and H[p] > H[p - k:p].max() and H[p] > H[p + 1:p + k + 1].max():
            if zero is None or H[p] > zero:
                zero, zero_idx = float(H[p]), p                             # un pivote más alto alarga el tramo
        running = max(running, float(H[t]))
        if zero is not None and t > zero_idx and L[t] <= (zero + origin) / 2:
            return FiboState(zero, zero_idx, running, (t, (zero + origin) / 2), None)
    return FiboState(zero, zero_idx, running, None, None)
