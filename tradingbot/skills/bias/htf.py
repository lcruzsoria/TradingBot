"""Reglas de la vela anterior (H3 en índices, H4 en el resto): sesgo de la vela actual a partir de las dos anteriores.

La vela actual es la 0; la ya cerrada es la n-1 y la anterior a ella, la n-2. El sesgo de la vela 0 sale de si la n-1
barrió el High o el Low de la n-2 y cerró de vuelta dentro de su rango:

- n-1 barre el High de la n-2 (su máximo lo supera) y cierra dentro del rango de la n-2   -> bajista
- n-1 barre el Low de la n-2 (su mínimo lo pierde) y cierra dentro del rango de la n-2     -> alcista
- barre los dos lados, barre y cierra fuera (ruptura) o no barre ninguno                  -> sin sesgo (no vota)

Continuación (la regla complementaria): si la n-1 cierra POR ENCIMA del High de la n-2 -> continuación alcista; si cierra
POR DEBAJO del Low de la n-2 -> continuación bajista; si cierra dentro de su rango, no vota. Como cerrar fuera y cerrar
dentro son excluyentes, esta regla y la de barrido nunca puntúan a la vez con el mismo par de velas.

Sin sesgo en las dos reglas: la n-1 interna a la n-2 (no la supera por ningún lado) y la n-1 que barre con mecha el High y el
Low de la n-2 a la vez (envolvente), cierre donde cierre.

Las velas se forman agrupando las del gráfico (M15, H1...) en bloques del tamaño elegido, alineados con el inicio del día de
trading del activo en hora de Nueva York: 18:00 en los índices americanos (H3: 18, 21, 00, 03, 06, 09, 12, 15) y 17:00 en el
resto (H4: 17, 21, 01, 05, 09, 13). Solo se usan velas ya cerradas: la vela 0 (en curso) no interviene.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

DEFAULT_INDEX_HOURS = 3     # BIAS_HTF_SWEEP_INDEX_HOURS
DEFAULT_HOURS = 4           # BIAS_HTF_SWEEP_HOURS
NEEDED_BLOCKS = 3           # la vela 0 más la n-1 y la n-2


@dataclass(frozen=True)
class HtfSweep:
    vote: int               # +1 alcista, -1 bajista, 0 sin sesgo
    detail: str
    hours: int


def _fmt(value: float) -> str:
    return f"{value:,.2f}" if value >= 1000 else f"{value:.3f}" if value >= 10 else f"{value:.5f}"


def htf_blocks(ts, high, low, close, ahead: int, anchor_minutes: int, hours: int):
    """Velas de `hours` horas a partir de las del gráfico: (inicio NY, high, low, close) de cada una, de la más antigua a la actual."""
    ts = np.asarray(ts, dtype=np.int64)
    bucket = ((ts - int(ahead)) - anchor_minutes * 60) // (hours * 3600)
    first = np.r_[True, bucket[1:] != bucket[:-1]]
    starts = np.flatnonzero(first)
    ends = np.r_[starts[1:] - 1, len(ts) - 1]
    hi = np.maximum.reduceat(np.asarray(high, dtype=float), starts)
    lo = np.minimum.reduceat(np.asarray(low, dtype=float), starts)
    cl = np.asarray(close, dtype=float)[ends]
    t0 = bucket[starts] * hours * 3600 + anchor_minutes * 60          # inicio de cada bloque, en hora de NY (epoch ingenuo)
    return t0, hi, lo, cl


def sweep_vote(hi2: float, lo2: float, hi1: float, lo1: float, close1: float) -> tuple[int, str]:
    """(voto, motivo) de la vela n-1 frente a la n-2. Cerrar «dentro» incluye los extremos de la n-2."""
    swept_high, swept_low = hi1 > hi2, lo1 < lo2
    inside = lo2 <= close1 <= hi2
    if swept_high and swept_low:
        return 0, "barrió el High y el Low de la anterior: sin sesgo"
    if swept_high:
        return (-1, "barrió el High de la anterior y cerró dentro: bajista") if inside else \
            (0, "barrió el High pero cerró fuera (ruptura): sin sesgo")
    if swept_low:
        return (1, "barrió el Low de la anterior y cerró dentro: alcista") if inside else \
            (0, "barrió el Low pero cerró fuera (ruptura): sin sesgo")
    return 0, "no barrió el High ni el Low de la anterior: sin sesgo"


def break_vote(hi2: float, lo2: float, hi1: float, lo1: float, close1: float) -> tuple[int, str]:
    """(voto, motivo) de la continuación: la vela n-1 cierra fuera del rango de la n-2.

    Si la n-1 barre con su mecha los dos lados de la n-2 (vela envolvente) no hay sesgo, aunque cierre fuera.
    """
    if hi1 > hi2 and lo1 < lo2:
        return 0, "barrió el High y el Low de la anterior: sin sesgo"
    if close1 > hi2:
        return 1, "cerró por encima del High de la anterior: continuación alcista"
    if close1 < lo2:
        return -1, "cerró por debajo del Low de la anterior: continuación bajista"
    return 0, "cerró dentro del rango de la anterior: sin sesgo"


def _last_blocks(df: pd.DataFrame, ahead: int, anchor_minutes: int, hours: int, tf_minutes: int):
    """Las últimas velas de `hours` horas con sus datos, o un HtfSweep sin voto si no se pueden formar."""
    name = f"H{hours}"
    if tf_minutes > hours * 60:
        return HtfSweep(0, f"El gráfico es de un timeframe mayor que {name}: no se pueden formar sus velas", hours)
    tail = df.tail(int(NEEDED_BLOCKS * hours * 60 / max(tf_minutes, 1)) * 3 + 50)     # basta el final del histórico
    blocks = htf_blocks(tail["ts"].to_numpy(), tail["high"].to_numpy(), tail["low"].to_numpy(),
                        tail["close"].to_numpy(), ahead, anchor_minutes, hours)
    if len(blocks[0]) < NEEDED_BLOCKS:
        return HtfSweep(0, f"Faltan velas {name} para evaluar la vela anterior", hours)
    return blocks


def _when(t) -> str:
    return (datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=int(t))).strftime("%H:%M")


def htf_sweep(df: pd.DataFrame, ahead: int, anchor_minutes: int, hours: int, tf_minutes: int) -> HtfSweep:
    """Sesgo de la vela actual de `hours` horas a partir del barrido de las dos anteriores, con las velas `df` del gráfico."""
    blocks = _last_blocks(df, ahead, anchor_minutes, hours, tf_minutes)
    if isinstance(blocks, HtfSweep):
        return blocks
    t0, hi, lo, cl = blocks
    vote, why = sweep_vote(hi[-3], lo[-3], hi[-2], lo[-2], cl[-2])
    return HtfSweep(vote, f"H{hours}: la vela de las {_when(t0[-2])} NY {why} (High {_fmt(hi[-2])} / Low {_fmt(lo[-2])} frente a "
                          f"{_fmt(hi[-3])} / {_fmt(lo[-3])} de la de las {_when(t0[-3])})", hours)


def htf_break(df: pd.DataFrame, ahead: int, anchor_minutes: int, hours: int, tf_minutes: int) -> HtfSweep:
    """Sesgo de la vela actual por continuación: la n-1 cierra fuera del rango de la n-2 (encima: alcista; debajo: bajista)."""
    blocks = _last_blocks(df, ahead, anchor_minutes, hours, tf_minutes)
    if isinstance(blocks, HtfSweep):
        return blocks
    t0, hi, lo, cl = blocks
    vote, why = break_vote(hi[-3], lo[-3], hi[-2], lo[-2], cl[-2])
    return HtfSweep(vote, f"H{hours}: la vela de las {_when(t0[-2])} NY {why} (cierre {_fmt(cl[-2])} frente a High {_fmt(hi[-3])} / "
                          f"Low {_fmt(lo[-3])} de la de las {_when(t0[-3])})", hours)
