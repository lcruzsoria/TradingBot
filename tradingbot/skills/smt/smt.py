"""Detección del SMT secuencial (SSMT) de la Quarterly Theory: funciones puras.

Un SSMT es una divergencia entre dos cuartos CONSECUTIVOS de un ciclo en activos muy correlacionados (para los índices, NAS100, SP500 y DJ30):
se marca el máximo (mínimo) absoluto del cuarto anterior en cada activo; en el cuarto actual, uno o más activos lo superan y otro o varios no.
Los extremos no tienen que haberse formado a la misma hora. Romper el máximo con uno y dejar al otro sin romperlo es un SSMT bajista (alcista si es el mínimo).
Según el curso, el SSMT suele ser la manipulación del cuarto; para darle valor debe formarse por encima del True Open del ciclo (bajista) o por debajo (alcista).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import ciclos

PARON = 3600                       # el parón diario de los índices (17:00-18:00 NY): un cuarto que acaba en él no tiene velas en su última hora


@dataclass(frozen=True)
class Smt:
    ciclo: str
    cuarto: int                  # número de cuarto (creciente) en que se forma
    etiqueta: str                # Q1..Q4 del ciclo
    direccion: str               # "bajista" (máximos) o "alcista" (mínimos)
    ts: int                      # hora (servidor) de la primera vela que rompe el extremo del cuarto anterior
    ts_fin: int                  # hora (servidor) en que termina el cuarto
    rompen: tuple                # activos que rompen el extremo anterior
    tiempos: tuple               # hora (servidor) en que rompe cada uno de `rompen`, en el mismo orden
    fallan: tuple                # activos que no lo rompen (al terminar el cuarto, o hasta ahora si sigue en curso)
    extremo: float               # extremo alcanzado por el primero que rompe, en su activo
    true_open_ok: bool | None    # el barrido está por encima (bajista) o por debajo (alcista) del True Open del ciclo; None si no hay True Open
    completo: bool               # el cuarto ya ha terminado


def _alinear(series: dict) -> tuple[np.ndarray, dict]:
    """Velas comunes a todos los activos: {símbolo: (ts, open, high, low, close)} -> (ts comunes, {símbolo: (open, high, low, close)})."""
    common = None
    for ts, *_ in series.values():
        common = ts if common is None else np.intersect1d(common, ts)
    out = {}
    for sym, (ts, *rest) in series.items():
        idx = np.searchsorted(ts, common)
        out[sym] = tuple(np.asarray(a)[idx] for a in rest)
    return common, out


def detectar(series: dict, ciclo: str, ahead: int, tf_minutes: int, ultimo_ts: int | None = None, divergencia: bool = True) -> list[Smt]:
    """Todos los SSMT del `ciclo` en las velas de `series` ({símbolo: (ts, open, high, low, close)}, ts en hora del servidor).

    `ahead`: segundos que el servidor va por delante de NY. Solo se usan cuartos anteriores completos (con su primera y su última vela).
    `ultimo_ts`: hora de la última vela cerrada (para saber qué cuarto sigue en curso); por defecto, la última de las series.
    `divergencia=False` devuelve lo contrario: los cuartos en que TODOS los activos rompen el extremo anterior (sin divergencia), para comparar."""
    if len(series) < 2:
        return []
    ts, a = _alinear(series)
    if len(ts) < 3:
        return []
    ny = ts - ahead
    bar = tf_minutes * 60
    q = np.array([-1 if (c := ciclos.cuarto(int(t), ciclo)) is None else c for t in ny])
    last = int(ts[-1]) if ultimo_ts is None else ultimo_ts
    bounds = {}                                        # cuarto -> (primera, última) posición
    for i, qi in enumerate(q):
        if qi != -1:
            lo, _ = bounds.get(int(qi), (i, i))
            bounds[int(qi)] = (lo, i)
    dur = ciclos.CICLOS[ciclo]
    syms = list(series)
    out = []
    for k in sorted(bounds):
        prev = k - 1
        if prev not in bounds or (ciclo == "semana" and ciclos.numero(k, ciclo) == 1):
            continue                                   # el cuarto anterior no existe (o la semana empieza: el lunes no sigue al jueves)
        p0, p1 = bounds[prev]
        if ny[p0] > ciclos.inicio(prev, ciclo) + bar or ny[p1] + 2 * bar + PARON < ciclos.inicio(prev, ciclo) + dur:
            continue                                   # al cuarto anterior le faltan velas al principio o al final: su extremo no es fiable
        k0, k1 = bounds[k]
        prev_hi = {s: float(a[s][1][p0:p1 + 1].max()) for s in syms}
        prev_lo = {s: float(a[s][2][p0:p1 + 1].min()) for s in syms}
        fin = ciclos.inicio(k, ciclo) + dur + ahead
        completo = last + bar >= fin
        tbr_q = ciclos.cuarto_true_open(k, ciclo)
        opens = {s: float(a[s][0][bounds[tbr_q][0]]) for s in syms} if tbr_q in bounds else {}
        for side, direccion in (("high", "bajista"), ("low", "alcista")):
            first = {}
            for s in syms:
                seg = a[s][1][k0:k1 + 1] > prev_hi[s] if side == "high" else a[s][2][k0:k1 + 1] < prev_lo[s]
                hit = np.flatnonzero(seg)
                if hit.size:
                    first[s] = k0 + int(hit[0])
            ran = list(first)
            fail = [s for s in syms if s not in first]
            if not ran or bool(fail) != divergencia:
                continue                               # sin divergencia (todos rompen) o, con `divergencia=False`, con ella
            lead = min(ran, key=lambda s: first[s])
            i = first[lead]
            seg = slice(k0, k1 + 1)
            extremo = float(a[lead][1][seg].max() if side == "high" else a[lead][2][seg].min())
            ok = None
            if lead in opens and opens[lead]:
                ok = extremo > opens[lead] if side == "high" else extremo < opens[lead]
            out.append(Smt(ciclo, int(k), f"Q{ciclos.numero(k, ciclo)}", direccion, int(ts[i]), int(fin), tuple(ran), tuple(int(ts[first[s]]) for s in ran), tuple(fail), extremo, ok, completo))
    return sorted(out, key=lambda e: e.ts)
