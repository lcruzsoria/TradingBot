"""Patrón «Reversión»: toma de un lado de la TBR solo con la mecha, fibonacci de la mecha pivote al pivote siguiente y entrada en el 0,5.

Ejemplo bajista (el alcista es el espejo exacto, con el Low):

1. Toma con mecha: una vela de M15 supera el High de la TBR con su mecha pero CIERRA dentro del rango (si cerrara fuera, sería una
   rotura con cuerpo y la TBR sería del patrón Continuación). Es la primera toma de un lado tras el cierre de la TBR.
2. Mecha pivote: el pivote de tres velas (su máximo es el más alto de las tres) que forma esa mecha. Si antes de confirmarse alguna
   vela cierra por encima del High, el patrón se invalida (pasa a ser continuación).
3. Fibonacci: el 1 es la mecha pivote y el 0 es el primer pivote bajo confirmado que genera a continuación (queda fijo: uno
   posterior más bajo no lo sustituye). El 0,5 es el punto medio.
4. Entrada: la primera vela que revierte hasta el 0,5 (su máximo lo toca). Stop en el 1 (la mecha pivote) y objetivo en el -0,5
   (media vuelta del tramo más allá del 0): con entrada en el 0,5, son 2R. Si el precio supera la mecha pivote antes de la entrada, se
   invalida; si termina el plazo de la TBR sin reversión al 0,5, vence.
5. Rotura con cuerpo: si, ya confirmada la mecha pivote, una vela CIERRA por encima del High tomado antes de la entrada, la reversión se
   anula (el mercado ha roto ese lado: ahora es continuación). Una rotura en la misma vela de la entrada o después no la anula.

Trabaja siempre con velas de `PATTERN_REVERSION_TF` (M15 al inicio), sea cual sea el timeframe del gráfico.
"""
from __future__ import annotations

import numpy as np

from ...timeframes import parse_timeframe
from .continuacion import _when
from .fibo import run_fibo
from .trade import position_figure
from .patterns import DETECTED, EXPIRED, INVALIDATED, Figure, Pattern, PatternContext, PatternHit, register_pattern

DEFAULT_TF = "15m"
DEFAULT_SWING_BARS = 1
KEY = "reversion"
TITLE = "Reversión"


@register_pattern(KEY)
class Reversion(Pattern):
    title = TITLE

    def __init__(self, settings=None) -> None:
        super().__init__(settings)
        get = (lambda key, default: default) if settings is None else settings.get
        self.tf = parse_timeframe(str(get("REVERSION_TF", DEFAULT_TF)))
        self.swing_bars = int(get("REVERSION_SWING_BARS", DEFAULT_SWING_BARS))
        if self.swing_bars < 1:
            raise ValueError(f"PATTERN_REVERSION_SWING_BARS={self.swing_bars} debe ser 1 o más.")

    def timeframe(self) -> str:
        return self.tf

    def detect(self, ctx: PatternContext) -> list[PatternHit]:
        return analyze(ctx, self.swing_bars)[0]

    def figures(self, ctx: PatternContext) -> list[Figure]:
        return analyze(ctx, self.swing_bars)[1]


def analyze(ctx: PatternContext, k: int) -> tuple[list[PatternHit], list[Figure]]:
    tbr = ctx.tbr
    start, end = ctx.first_bar, ctx.last_bar
    o, h, l, c, ts = ctx.open, ctx.high, ctx.low, ctx.close, ctx.ts
    tf_sec = ctx.tf_minutes * 60

    def hit(status, direction, x, price, detail, levels=None):
        return PatternHit(KEY, TITLE, direction, int(x), float(price), detail, levels or {}, int(ts[x]) if 0 <= x < len(ts) else 0, status)

    def expired(direction, detail):
        x = min(max(end, 0), len(ts) - 1)
        return [hit(EXPIRED, direction, x, tbr.mid, f"{detail} antes de que {ctx.limit_verb} {ctx.next_zone} ({ctx.next_hours} NY)")], []

    # 1) primera toma de un lado: con mecha (cierra dentro) es reversión; con cuerpo es continuación y aquí no hay nada
    take = None
    for j in range(start, end + 1):
        if c[j] > tbr.high or c[j] < tbr.low:
            return [], []
        wick_up, wick_down = h[j] > tbr.high, l[j] < tbr.low
        if wick_up and wick_down:
            return [hit(INVALIDATED, "", j, tbr.mid, "una misma vela tomó con mecha el High y el Low de la TBR: sin patrón")], []
        if wick_up or wick_down:
            take = (j, wick_up)
            break
    if take is None:
        return expired("", "no hubo toma con mecha del High ni del Low de la TBR") if ctx.window_closed else ([], [])
    j, up = take
    sign = -1 if up else 1                                   # tomar el High es reversión bajista (espejo); tomar el Low, alcista
    H, L = (-l, -h) if up else (h, l)
    side = "High" if up else "Low"
    direction = "short" if up else "long"
    # 2) mecha pivote: pivote de k velas a cada lado (el máximo más alto en la del medio, en el corto) que forma esa mecha
    origin = confirmed = None
    for t in range(j, end + 1):
        if t > j and (c[t] > tbr.high or c[t] < tbr.low):
            return [hit(INVALIDATED, direction, t, tbr.mid,
                        f"toma con mecha del {side} en {_when(ctx, j)}, pero una vela cerró fuera de la TBR antes de confirmarse la mecha "
                        f"pivote: ya no es reversión")], []
        p = t - k
        if p >= j and p - k >= 0 and L[p] < L[p - k:p].min() and L[p] < L[p + 1:p + k + 1].min():
            beyond = h[p] > tbr.high if up else l[p] < tbr.low                          # el pivote debe ser la propia mecha
            if beyond:
                origin, confirmed = p, t
                break
    if origin is None:
        if ctx.window_closed:
            return expired(direction, f"toma con mecha del {side} en {_when(ctx, j)} pero sin mecha pivote confirmada")
        return [], []
    origin_price = float(L[origin])
    # 3) fibonacci de la mecha pivote al pivote siguiente y 4) reversión al 0,5
    state = run_fibo(H, L, confirmed, end, origin_price, k, origin + 1, float(H[origin:confirmed + 1].max()),
                     -o if up else o)
    zero_idx, entry = state.zero_idx, state.entry
    extreme = state.extreme
    half = (extreme + origin_price) / 2
    target = extreme + (extreme - origin_price) / 2
    levels = {"-0,5": sign * target, "0": sign * extreme, "0,5": sign * half, "1": sign * origin_price}
    broke = next((t for t in range(confirmed + 1, end + 1) if (c[t] > tbr.high if up else c[t] < tbr.low)), None)
    if broke is not None and (entry is None or broke < entry[0]) and (state.breach is None or broke < state.breach):
        return [hit(INVALIDATED, direction, broke, tbr.mid,
                    f"toma con mecha del {side} en {_when(ctx, j)}, mecha pivote en {_when(ctx, origin)}; una vela cerró fuera del "
                    f"{side} en {_when(ctx, broke)} antes del retroceso al 0,5: rotura con cuerpo, ya no es reversión")], []
    if state.breach is not None:
        return [hit(INVALIDATED, direction, state.breach, sign * origin_price,
                    f"toma con mecha del {side} en {_when(ctx, j)}; el precio superó la mecha pivote ({sign * origin_price:.5g}) antes de "
                    f"llegar al 0,5: patrón invalidado")], []
    label = f"{tbr.zone} {'▼' if up else '▲'} Rev"
    x_end = int(ts[min(end, len(ts) - 1)]) + tf_sec
    if entry is not None:
        t, half = entry
        detail = (f"toma con mecha del {side} en {_when(ctx, j)}, mecha pivote en {_when(ctx, origin)}, 0 en {_when(ctx, zero_idx)}; "
                  f"retroceso al 0,5 ({sign * half:.5g}) en {_when(ctx, t)}. Entrada en el 0,5, stop en la mecha pivote y objetivo en "
                  f"el -0,5 (2R)")
        found = hit(DETECTED, direction, t, sign * half, detail,
                    {"stop": sign * origin_price, "target": sign * target, "fibo 0": sign * extreme, "fibo 0,5": sign * half})
        pos = position_figure(ctx, KEY, tbr.zone, direction, t, sign * half, sign * origin_price, sign * target, label)
        return [found], [Figure("fib", KEY, tbr.zone, direction, int(ts[origin]), x_end, levels, "entrada", label, tbr.day.isoformat()), pos]
    if ctx.window_closed:
        return expired(direction, f"toma con mecha del {side} en {_when(ctx, j)} pero sin retroceso al 0,5")
    return [], [Figure("fib", KEY, tbr.zone, direction, int(ts[origin]), x_end, levels, "en curso", label, tbr.day.isoformat())]
