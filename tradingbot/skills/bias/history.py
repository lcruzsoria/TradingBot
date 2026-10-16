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


def efficiency(c, k: int) -> np.ndarray:
    """Eficiencia del movimiento de las k velas anteriores a cada vela: |cierre final - inicial| / suma de |cambios|.

    0 = el precio fue y volvió (lateral); 1 = fue en línea recta (tendencia).
    """
    c = np.asarray(c, dtype=float)
    n = len(c)
    csum = np.r_[0.0, np.cumsum(np.abs(np.diff(c, prepend=c[0])))]
    i = np.arange(n)
    lo = np.maximum(i - k, 0)
    path = csum[i] - csum[lo + 1]                                           # suma de |cambios| entre lo e i-1
    net = np.abs(c[np.maximum(i - 1, 0)] - c[lo])
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(path > 0, net / path, 0.0)
    out[:k] = 0.0
    return out


def recent_efficiency(ts, c, hours: float) -> float | None:
    """Eficiencia del precio en las últimas `hours` horas hasta la última vela, o None si no hay velas suficientes."""
    ts = np.asarray(ts, dtype=np.int64)
    c = np.asarray(c, dtype=float)
    if len(c) < 3:
        return None
    first = int(np.searchsorted(ts, ts[-1] - int(hours * 3600)))
    if first >= len(c) - 2 or ts[0] > ts[-1] - int(hours * 3600):
        return None                                                          # el histórico no llega a cubrir la ventana
    window = c[first:]
    path = float(np.abs(np.diff(window)).sum())
    return abs(float(window[-1] - window[0])) / path if path > 0 else 0.0


def lateral_flags(ts, c, hours: float, min_efficiency: float, ids) -> np.ndarray:
    """True en las velas cuyo bloque empezó con el mercado lateral (eficiencia de las últimas `hours` horas < mínimo)."""
    ts = np.asarray(ts, dtype=np.int64)
    if len(ts) < 3 or min_efficiency <= 0:
        return np.zeros(len(ts), dtype=bool)
    step = max(int(np.median(np.diff(ts))), 1)
    k = max(int(round(hours * 3600 / step)), 1)
    return (efficiency(c, k) < min_efficiency)[ids]


def sma_vote(px, c, period: int) -> np.ndarray:
    """+1 / -1 según el precio `px` de cada vela esté sobre o bajo la media de los `period` cierres anteriores (0 si faltan velas)."""
    n = len(c)
    csum = np.r_[0.0, np.cumsum(c)]
    sma = np.full(n, np.nan)
    if n > period:
        sma[period:] = (csum[period:n] - csum[:n - period]) / period
    return np.where(np.isnan(sma), 0.0, np.sign(px - sma))


def block_ids(t, anchor_seconds: int, hours: float) -> np.ndarray:
    """Primera vela de cada bloque de `hours` horas, repetida para todas las velas del bloque (el sesgo se congela ahí)."""
    block = _first((t - anchor_seconds) // int(hours * 3600))
    return np.flatnonzero(block)[np.cumsum(block) - 1]


def rule_votes(ts, o, h, l, c, keys, ahead: int, anchor_minutes: int, htf_hours: int, sma_period: int) -> dict[str, np.ndarray]:
    """Voto (+1 / -1 / 0) de cada regla en cada vela, con el precio de apertura de la vela (sin mirar al futuro)."""
    ts = np.asarray(ts, dtype=np.int64)
    o, h, l, c = (np.asarray(a, dtype=float) for a in (o, h, l, c))
    n = len(ts)
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
    wanted = set(keys)
    if "htf_sweep" in wanted:
        votes["htf_sweep"] = _htf_votes(t, h, l, c, anchor, htf_hours, "sweep")
    if "htf_break" in wanted:
        votes["htf_break"] = _htf_votes(t, h, l, c, anchor, htf_hours, "break")
    if "sma" in wanted:
        votes["sma"] = sma_vote(px, c, sma_period)
    return votes


def score_history(ts, o, h, l, c, rules: list[tuple[str, float]], ahead: int, anchor_minutes: int, recalc_hours: float,
                  htf_hours: int, sma_period: int) -> np.ndarray:
    """Puntuación (suma de voto x peso) de cada vela. `rules`: (clave, peso) de las reglas activas."""
    ts = np.asarray(ts, dtype=np.int64)
    if len(ts) == 0:
        return np.zeros(0)
    votes = rule_votes(ts, o, h, l, c, [key for key, _w in rules], ahead, anchor_minutes, htf_hours, sma_period)
    total = np.zeros(len(ts))
    for key, weight in rules:
        if key in votes:
            total += np.nan_to_num(votes[key]) * float(weight)
    if recalc_hours and recalc_hours > 0:                              # congelado: solo cambia al crearse la vela 0
        total = total[block_ids(ts - int(ahead), anchor_minutes * 60, recalc_hours)]
    return total
