"""Hipótesis en estudio: el «modelo Green Bird» (barrido de liquidez + reclaim en NY AM), traducido de los tuits de @greenbirdtrader.

NO es todavía un patrón del bot (no se registra ni dispara a Cortex): es la lógica pura, sin MT5, que usa
`scripts/backtest_green_bird.py` para medir si la idea tiene ventaja. Si la tiene, se convierte en patrón.

Lo que cuenta en sus tuits (septiembre-octubre de 2026), reducido a reglas medibles. Ejemplo corto (el largo es el espejo exacto):

1. Niveles de liquidez del día de trading, todos de arriba: máximo de Asia (20:00-00:00 NY), de London (02:00-05:00), PDH (máximo del día
   de trading anterior) y máximo de la hora previa a NY (09:00-10:00). Son los mismos rangos de la TBR y los PDH / PDL de `daylevels`.
2. Ventana de NY AM: de 09:30 a 12:00 (para el rango de 09:00-10:00, a partir de las 10:00, cuando ya está cerrado).
3. Barrido: una vela de la ventana supera el nivel con su máximo. Con `intact`, el nivel no se había tocado desde que se formó: la liquidez
   sigue ahí y es el barrido de la ventana el que la toma.
4. Reclaim: en esa misma vela o en las `reclaim_bars` siguientes, una vela CIERRA otra vez por debajo del nivel. Si no, el precio ha
   aceptado la ruptura y el nivel no da operación.
5. Entrada a mercado al cierre de la vela del reclaim (el bot solo ve velas cerradas). Stop justo por encima del máximo del barrido. Objetivo:
   `target_r` veces el riesgo, o el extremo contrario del mismo rango (`target_r=None`).
6. Se descartan las señales con riesgo menor de `min_risk_pct` o mayor de `max_risk_pct` del precio (ruido y barridos que se fueron lejos).

Su «one and done»: como mucho una operación al día (la primera señal de la ventana); esa regla se aplica fuera, en el script.
Lo que los tuits no dicen (timeframe de entrada exacto, definición de reclaim, stop) se fija aquí de antemano y se mide como sensibilidad.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from ..levels.daylevels import trading_day

KINDS = ("PDHL", "ASIA", "LONDON", "PRE_NY")        # PDH / PDL, y los rangos de Asia, London y 09:00-10:00 NY
RANGES = {"ASIA": (20 * 60, 24 * 60), "LONDON": (2 * 60, 5 * 60), "PRE_NY": (9 * 60, 10 * 60)}     # minutos de NY (inicio, fin)
DAY_START = 18 * 60                                  # los índices americanos empiezan el día de trading a las 18:00 NY
WINDOW_OPEN = 9 * 60 + 30                            # NY AM: de la apertura del cash...
PRE_NY_OPEN = 10 * 60                                # ...(el rango de 09:00-10:00 solo se opera cuando ya ha cerrado)


@dataclass(frozen=True)
class Params:
    reclaim_bars: int = 3              # velas (tras la del barrido) en las que debe llegar el cierre de vuelta dentro
    intact: bool = True                # el nivel no se había tocado entre su formación y el inicio de la ventana
    window_end: int = 12 * 60          # minutos de NY: no se entra más tarde
    target_r: float | None = 2.0       # objetivo a x veces el riesgo; None = el extremo contrario del mismo rango
    min_risk_pct: float = 0.03         # riesgo mínimo y máximo, en % del precio
    max_risk_pct: float = 0.40
    fresh_cross: bool = False          # el barrido debe ser un cruce nuevo: la vela anterior cerró del lado de dentro del nivel (evita contar como
                                       # barrido un precio que ya estaba al otro lado cuando empieza la ventana)
    displacement: float | None = None  # None: se entra al cierre de la vela del reclaim. x: se entra al cierre de la primera vela, desde el reclaim
                                       # y hasta `entry_wait` velas después, que cierra dentro del nivel con un cuerpo a favor de x veces el medio de las 20 anteriores
    entry_wait: int = 6


@dataclass(frozen=True)
class Signal:
    kind: str                          # uno de KINDS
    side: str                          # "high" (barrido de máximos: corto) o "low" (barrido de mínimos: largo)
    direction: str
    sweep_bar: int                     # primera vela que supera el nivel
    bar: int                           # vela del reclaim (la señal se confirma en su cierre)
    entry_bar: int                     # primera vela con la posición viva (la siguiente)
    entry: float
    stop: float
    target: float
    level: float
    opposite: float                    # extremo contrario del mismo rango (referencia)
    levels_swept: int = 1              # cuántos niveles del mismo lado (Asia, London, PDH / PDL, hora previa a NY) ha tomado el extremo del barrido


def day_levels(ts, ahead: int, high, low) -> dict[int, dict[str, tuple[float, float, int]]]:
    """Por día de trading: {tipo: (máximo, mínimo, primera vela con el nivel ya formado)}.

    Los rangos de sesión se miden dentro del propio día de trading (Asia 20:00-00:00 y London 02:00-05:00 pertenecen al día que termina
    esa tarde); PDH / PDL es el día de trading anterior completo. El índice de vela es el de la primera vela POSTERIOR al fin del rango."""
    ts = np.asarray(ts, dtype=np.int64)
    ny = ts - ahead
    day_of = trading_day(ts, ahead, DAY_START)
    mins = ((ny % 86400) // 60).astype(np.int64)
    starts = np.r_[0, np.flatnonzero(np.diff(day_of)) + 1]
    ends = np.r_[starts[1:], len(ts)]
    out: dict[int, dict[str, tuple[float, float, int]]] = {}
    prev: tuple[float, float] | None = None
    for i0, i1 in zip(starts, ends):
        d = int(day_of[i0])
        found: dict[str, tuple[float, float, int]] = {}
        if prev is not None:
            found["PDHL"] = (*prev, int(i0))               # ya conocido desde que empieza el día
        m = mins[i0:i1]
        for kind, (a, b) in RANGES.items():
            sel = np.flatnonzero((m >= a) & (m < b))
            if len(sel) < 3:
                continue
            idx = i0 + sel
            found[kind] = (float(high[idx].max()), float(low[idx].min()), int(idx[-1]) + 1)
        out[d] = found
        prev = (float(high[i0:i1].max()), float(low[i0:i1].min()))
    return out


def find_signals(ts, ahead: int, o, h, l, c, params: Params = Params()) -> list[tuple[int, Signal]]:
    """Señales de cada día de trading (todas las de cada nivel, la primera por nivel y lado): lista de (día, señal), ordenada por vela de entrada."""
    ts = np.asarray(ts, dtype=np.int64)
    n = len(ts)
    ny = ts - ahead
    mins = ((ny % 86400) // 60).astype(np.int64)
    day_of = trading_day(ts, ahead, DAY_START)
    levels = day_levels(ts, ahead, h, l)
    starts = np.r_[0, np.flatnonzero(np.diff(day_of)) + 1]
    ends = np.r_[starts[1:], n]
    out: list[tuple[int, Signal]] = []
    for i0, i1 in zip(starts, ends):
        d = int(day_of[i0])
        for kind, (hi, lo, formed) in levels.get(d, {}).items():
            open_min = PRE_NY_OPEN if kind == "PRE_NY" else WINDOW_OPEN
            win = np.flatnonzero((mins[i0:i1] >= open_min) & (mins[i0:i1] < params.window_end) & (mins[i0:i1] < 17 * 60)) + i0
            if len(win) == 0 or win[0] < formed:
                continue
            first = int(win[0])
            for side, level, opposite in (("high", hi, lo), ("low", lo, hi)):
                if params.intact and formed < first:
                    seen_h, seen_l = h[formed:first], l[formed:first]
                    if len(seen_h) and ((side == "high" and seen_h.max() > level) or (side == "low" and seen_l.min() < level)):
                        continue
                sig = _scan(o, h, l, c, win, kind, side, level, opposite, params, n)
                if sig is not None:
                    swept = sum(1 for lh, ll, _ in levels[d].values() if (sig.stop > lh if side == "high" else sig.stop < ll))
                    out.append((d, replace(sig, levels_swept=max(1, swept))))
    out.sort(key=lambda x: (x[1].entry_bar, KINDS.index(x[1].kind)))
    return out


def _scan(o, h, l, c, win, kind: str, side: str, level: float, opposite: float, p: Params, n: int) -> Signal | None:
    sweep = None
    for i in win:
        i = int(i)
        beyond = h[i] > level if side == "high" else l[i] < level
        if sweep is None:
            if not beyond:
                continue
            if p.fresh_cross and i > 0 and ((c[i - 1] > level) if side == "high" else (c[i - 1] < level)):
                continue                                  # ya estaba al otro lado del nivel: no es un barrido nuevo
            sweep = i                                     # primera vela que toma la liquidez
        elif i - sweep > p.reclaim_bars:
            return None                                   # el precio aceptó la ruptura: sin operación en este nivel
        back = c[i] < level if side == "high" else c[i] > level
        if not back:
            continue
        if p.displacement is not None:                       # entrada con desplazamiento: vela a favor con cuerpo grande que sigue dentro del nivel
            j = _displacement_bar(o, c, i, min(i + p.entry_wait, int(win[-1])), side, level, p.displacement)
            if j is None:
                return None
            i = j
        if i + 1 >= n:
            return None
        extreme = float(h[sweep:i + 1].max()) if side == "high" else float(l[sweep:i + 1].min())
        entry = float(c[i])
        risk = abs(extreme - entry)
        if not (entry * p.min_risk_pct / 100 <= risk <= entry * p.max_risk_pct / 100):
            return None
        direction = "short" if side == "high" else "long"
        sign = -1 if direction == "short" else 1
        target = entry + sign * (p.target_r * risk if p.target_r is not None else abs(opposite - entry))
        if (target - entry) * sign < risk * 0.5:          # el extremo contrario queda demasiado cerca: no hay recorrido
            return None
        return Signal(kind, side, direction, sweep, i, i + 1, entry, extreme, float(target), level, opposite)
    return None


def _displacement_bar(o, c, start: int, last: int, side: str, level: float, k: float) -> int | None:
    """Primera vela entre `start` y `last` que cierra dentro del nivel, a favor del reclaim (a la baja tras barrer máximos) y con un
    cuerpo de al menos `k` veces el cuerpo medio de las 20 velas anteriores."""
    for j in range(start, last + 1):
        body = c[j] - o[j]
        inside = c[j] < level if side == "high" else c[j] > level
        favour = body < 0 if side == "high" else body > 0
        mean = float(np.abs(c[max(0, j - 20):j] - o[max(0, j - 20):j]).mean()) if j > 0 else 0.0
        if inside and favour and mean > 0 and abs(body) >= k * mean:
            return j
    return None
