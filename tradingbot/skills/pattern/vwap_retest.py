"""Hipótesis en estudio: retest del VWAP dentro de la TBR, con objetivo en el extremo de su rango.

NO es todavía un patrón del bot (no se registra ni dispara a Cortex): es la lógica pura, sin MT5, que usa
`scripts/backtest_vwap_tbr.py` para medir si la idea tiene ventaja. Si la tiene, se convierte en patrón.

Ejemplo largo (el corto es el espejo exacto). Trabaja con velas M15 y con el VWAP del día de trading (`daylevels.vwap`):

1. La TBR ya cerró y su rango sigue intacto: desde su cierre, ninguna vela ha tomado ni el High ni el Low. Si el precio ya
   llegó al extremo, la continuación «hasta el extremo» se ha consumido.
2. El VWAP está dentro del rango de la TBR (Low <= VWAP <= High).
3. Retest con rechazo: las `lookback` velas anteriores cerraron por encima del VWAP (el precio venía de arriba), y esta vela lo
   toca con su mínimo y cierra otra vez por encima.
4. Entrada a mercado al cierre de la vela del retest (el bot solo ve velas cerradas; una orden límite en el VWAP sufre
   selección adversa: ver docs/analisis_setups/CAMBIOS.md, v1 frente a v2). La posición vive desde la vela siguiente.
5. Stop: el más lejano entre el mínimo de la vela del retest y `stop_frac` rangos por debajo del VWAP. Objetivo: el High de la
   TBR (más `target` rangos, si se pide). Solo se opera si el objetivo está al menos a `min_rr` veces el riesgo.
6. Filtros opcionales para el estudio: pendiente del VWAP a favor (`slope_bars`) y confluencia con el 50 % de la TBR
   (`confluence`: el VWAP a menos de esa fracción del rango del punto medio).

Se opera como mucho una vez por TBR (la primera señal).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Params:
    lookback: int = 2                  # velas anteriores que cerraron del lado del VWAP desde el que viene el precio
    stop_frac: float = 0.25            # stop: esta fracción del rango más allá del VWAP (o el extremo de la vela del retest, si está más lejos)
    target: float = 0.0                # objetivo: el extremo de la TBR más este múltiplo del rango (0 = justo el extremo)
    min_rr: float = 1.0                # el objetivo debe estar al menos a esta distancia en R
    slope_bars: int = 0                # 0 = sin filtro; n: el VWAP debe ir a favor de la operación respecto de hace n velas
    confluence: float | None = None    # None = sin filtro; x: |VWAP - 50 %| <= x * rango


@dataclass(frozen=True)
class Signal:
    direction: str                     # "long" o "short"
    bar: int                           # vela del retest (la señal se confirma en su cierre)
    entry_bar: int                     # primera vela con la posición viva (la siguiente al retest)
    entry: float                       # cierre de la vela del retest
    stop: float
    target: float
    vwap: float                        # VWAP en la vela del retest


def _scan_long(o, h, l, c, vwap, high, low, first, end, p: Params):
    """Primera señal larga en las velas `first..end` (se entra al cierre de la vela de la señal)."""
    rng = high - low
    mid = (high + low) / 2
    if rng <= 0:
        return None
    for t in range(max(first, p.lookback, p.slope_bars), end + 1):
        if h[first:t + 1].max() >= high or l[first:t + 1].min() <= low:
            return None                                          # el rango dejó de estar intacto: se acabó la TBR
        v = vwap[t]
        if np.isnan(v) or not low <= v <= high:
            continue
        if not (l[t] <= v < c[t]):
            continue                                             # toca el VWAP con la mínima y cierra por encima
        if p.lookback and not all(c[t - k] > vwap[t - k] for k in range(1, p.lookback + 1)):
            continue                                             # venía de arriba (no cruza el VWAP de abajo arriba)
        if p.slope_bars and not v > vwap[t - p.slope_bars]:
            continue
        if p.confluence is not None and abs(v - mid) > p.confluence * rng:
            continue
        entry = float(c[t])
        stop = min(float(l[t]), v - p.stop_frac * rng)
        target = high + p.target * rng
        risk = entry - stop
        if risk <= 0 or (target - entry) < p.min_rr * risk:
            continue
        return t, entry, stop, target, float(v)
    return None


def find_signal(o, h, l, c, vwap, high: float, low: float, first: int, end: int, params: Params = Params()) -> Signal | None:
    """Primera señal (larga o corta) de la TBR `[low, high]` entre las velas `first` y `end`, o None.

    El corto se calcula con los precios cambiados de signo, así la lógica es una sola.
    """
    o, h, l, c, vwap = (np.asarray(a, dtype=float) for a in (o, h, l, c, vwap))
    end = min(end, len(c) - 1)
    if first > end:
        return None
    long_ = _scan_long(o, h, l, c, vwap, high, low, first, end, params)
    short = _scan_long(-o, -l, -h, -c, -vwap, -low, -high, first, end, params)
    if long_ is None and short is None:
        return None
    if short is None or (long_ is not None and long_[0] <= short[0]):
        t, entry, stop, target, v = long_
        return Signal("long", t, t + 1, entry, stop, target, v)
    t, entry, stop, target, v = short
    return Signal("short", t, t + 1, -entry, -stop, -target, -v)
