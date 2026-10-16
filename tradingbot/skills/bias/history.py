"""Histórico del sesgo: la puntuación que habría tenido el Bias en cada vela del gráfico (histograma bajo el precio).

Reconstruye, sin mirar al futuro, el mismo cálculo que hace el bot en vivo: el sesgo se calcula al abrirse cada vela HTF
(cada 3 h en índices, cada 4 h en el resto) con el precio de apertura de su primera vela, y se mantiene hasta la siguiente.
Reglas soportadas: ruptura del día anterior, TDO (y la apertura del día, que aquí se trata igual), Midnight, barrido y
continuación de la vela anterior y SMA. Las demás reglas no puntúan en el histórico.
"""
from __future__ import annotations

import numpy as np

from .htf import break_vote, sweep_vote

DAY = 86400


def _first(keys: np.ndarray) -> np.ndarray:
    return np.r_[True, keys[1:] != keys[:-1]]


def _htf_votes(t, h, l, c, anchor: int, hours: int, kind: str) -> np.ndarray:
    """Voto de la vela anterior (barrido o continuación) para cada vela: el de su bloque de `hours` horas, con las dos anteriores."""
    first = _first((t - anchor) // (hours * 3600))
    starts = np.flatnonzero(first)
    ids = np.cumsum(first) - 1
    ends = np.r_[starts[1:] - 1, len(t) - 1]
    hi, lo, cl = np.maximum.reduceat(h, starts), np.minimum.reduceat(l, starts), c[ends]
    vote = sweep_vote if kind == "sweep" else break_vote
    votes = np.zeros(len(starts))
    for b in range(2, len(starts)):
        votes[b] = vote(hi[b - 2], lo[b - 2], hi[b - 1], lo[b - 1], cl[b - 1])[0]
    return votes[ids]


def score_history(ts, o, h, l, c, rules: list[tuple[str, float]], ahead: int, anchor_minutes: int, recalc_hours: float,
                  htf_hours: int, sma_period: int) -> np.ndarray:
    """Puntuación (suma de voto x peso) de cada vela. `rules`: (clave, peso) de las reglas activas."""
    ts = np.asarray(ts, dtype=np.int64)
    o, h, l, c = (np.asarray(a, dtype=float) for a in (o, h, l, c))
    n = len(ts)
    if n == 0:
        return np.zeros(0)
    t, anchor = ts - int(ahead), anchor_minutes * 60
    day = (t - anchor) // DAY
    first = _first(day)
    starts = np.flatnonzero(first)
    ids = np.cumsum(first) - 1
    px = o                                           # el sesgo se calcula al abrir la vela: con su precio de apertura
    votes: dict[str, np.ndarray] = {}
    day_open = o[first][ids]
    prev_h = np.r_[np.nan, np.maximum.reduceat(h, starts)][ids]
    prev_l = np.r_[np.nan, np.minimum.reduceat(l, starts)][ids]
    votes["prev_day_break"] = (px > prev_h).astype(float) - (px < prev_l).astype(float)
    votes["tdo"] = votes["above_below_open"] = np.sign(px - day_open)
    idx = np.arange(n)
    after_mid = np.where(t >= (day + 1) * DAY, idx, n)                 # 00:00 NY del día en que termina el día de trading
    mid_idx = np.minimum.reduceat(after_mid, starts)[ids]
    valid = (mid_idx < n) & (idx >= mid_idx)
    votes["midnight"] = np.where(valid, np.sign(px - o[np.minimum(mid_idx, n - 1)]), 0.0)
    wanted = {key for key, _w in rules}
    if "htf_sweep" in wanted:
        votes["htf_sweep"] = _htf_votes(t, h, l, c, anchor, htf_hours, "sweep")
    if "htf_break" in wanted:
        votes["htf_break"] = _htf_votes(t, h, l, c, anchor, htf_hours, "break")
    if "sma" in wanted:
        csum = np.r_[0.0, np.cumsum(c)]
        sma = np.full(n, np.nan)
        if n > sma_period:
            sma[sma_period:] = (csum[sma_period:n] - csum[:n - sma_period]) / sma_period      # cierres de las velas anteriores
        votes["sma"] = np.where(np.isnan(sma), 0.0, np.sign(px - sma))
    total = np.zeros(n)
    for key, weight in rules:
        if key in votes:
            total += np.nan_to_num(votes[key]) * float(weight)
    if recalc_hours and recalc_hours > 0:                              # congelado: solo cambia al crearse la vela 0
        block = _first((t - anchor) // int(recalc_hours * 3600))
        total = total[np.flatnonzero(block)[np.cumsum(block) - 1]]
    return total
