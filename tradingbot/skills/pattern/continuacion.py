"""Patrón «Continuación»: rotura con cuerpo de un lado de la TBR, fibonacci del último tramo de estructura y entrada en el 0,5.

Ejemplo alcista (el bajista es el espejo exacto, con el Low):

1. Rotura: una vela de M15 CIERRA por encima del High de la TBR (rotura con cuerpo; una mecha sola no activa la TBR). La primera
   vela de ese tipo tras el cierre de la TBR, dentro de su plazo, la activa. Si antes de esa rotura una vela ya tomó con la mecha
   (y cerró dentro) cualquiera de los dos lados de la TBR, la TBR es de Reversión y la Continuación se bloquea: manda lo primero que pasa.
2. Swing points tras la rotura (pivotes de `PATTERN_CONTINUACION_SWING_BARS` velas a cada lado, 1 al inicio: el patrón de tres velas,
   con el extremo en la del medio): el 0 es un swing high y el 1 es el swing low que viene después de él. Mientras no hay swing low, un
   swing high más alto sustituye al 0; si el precio pierde el 1 antes de superar el 0, el 1 se busca de nuevo (un swing low más bajo).
3. Fibonacci de ese tramo (del swing high al swing low), con el 0,5 como punto medio. Queda fijo.
4. Activación: el precio supera el 0 (rompe la estructura). Hasta entonces el fibo solo se dibuja, sin entrada.
5. Entrada: la primera vela, ya activado, que retrocede hasta el 0,5 (su mínimo lo toca). Si pierde el 1 antes de eso, el patrón se
   invalida; si termina el plazo de la TBR sin entrada, vence.
6. Stop en el swing low (el nivel 1) y objetivo en el nivel -0,5 (media vuelta del tramo más allá del 0): con entrada en el 0,5, 2R.

Solo trata el fibonacci en curso de las TBR recientes que se han activado.
Trabaja siempre con velas de `PATTERN_CONTINUACION_TF` (M15 al inicio), sea cual sea el timeframe del gráfico.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ...timeframes import parse_timeframe
from .trade import position_figure
from .patterns import DETECTED, EXPIRED, INVALIDATED, Figure, Pattern, PatternContext, PatternHit, register_pattern

DEFAULT_TF = "15m"
DEFAULT_SWING_BARS = 1
KEY = "continuacion"
TITLE = "Continuación"


@register_pattern(KEY)
class Continuacion(Pattern):
    title = TITLE

    def __init__(self, settings=None) -> None:
        super().__init__(settings)
        get = (lambda key, default: default) if settings is None else settings.get
        self.tf = parse_timeframe(str(get("CONTINUACION_TF", DEFAULT_TF)))
        self.swing_bars = int(get("CONTINUACION_SWING_BARS", DEFAULT_SWING_BARS))
        if self.swing_bars < 1:
            raise ValueError(f"PATTERN_CONTINUACION_SWING_BARS={self.swing_bars} debe ser 1 o más.")

    def timeframe(self) -> str:
        return self.tf

    def detect(self, ctx: PatternContext) -> list[PatternHit]:
        return analyze(ctx, self.swing_bars)[0]

    def figures(self, ctx: PatternContext) -> list[Figure]:
        return analyze(ctx, self.swing_bars)[1]


@dataclass(frozen=True)
class Leg:
    zero: float | None        # swing high (el 0)
    zero_idx: int
    origin: float | None      # swing low posterior (el 1); None si todavía no hay
    origin_idx: int
    active: bool              # el precio ya superó el 0
    entry: tuple[int, float] | None   # (vela de la entrada, nivel 0,5)
    breach: int | None        # vela en la que el precio perdió el 1 con el tramo activado


def run_leg(H: np.ndarray, L: np.ndarray, brk: int, end: int, k: int) -> Leg:
    """Recorre las velas `brk + 1 .. end` buscando el swing high (0), el swing low posterior (1), la activación y la entrada."""
    zero, zero_idx, origin, origin_idx, act = None, -1, None, -1, None
    for t in range(brk + 1, end + 1):
        if act is not None:
            if L[t] < origin:
                return Leg(zero, zero_idx, origin, origin_idx, True, None, t)
            half = (zero + origin) / 2
            if t > act and L[t] <= half:
                return Leg(zero, zero_idx, origin, origin_idx, True, (t, half), None)
            continue
        if origin is not None and L[t] < origin:
            origin = None                                                   # perdió el 1 sin superar el 0: se busca otro swing low
        p = t - k
        if p >= max(brk, k):
            if origin is None and H[p] > H[p - k:p].max() and H[p] > H[p + 1:p + k + 1].max():
                if zero is None or H[p] > zero:
                    zero, zero_idx = float(H[p]), p                         # un swing high más alto sustituye al 0
            if zero is not None and p > zero_idx and L[p] < L[p - k:p].min() and L[p] < L[p + 1:p + k + 1].min():
                if origin is None or L[p] < origin:
                    origin, origin_idx = float(L[p]), p
        if origin is not None and H[t] > zero:
            act = t                                                         # superó el 0: el tramo queda fijo
    return Leg(zero, zero_idx, origin, origin_idx, act is not None, None, None)


def analyze(ctx: PatternContext, swing_bars: int) -> tuple[list[PatternHit], list[Figure]]:
    tbr = ctx.tbr
    start, end = ctx.first_bar, ctx.last_bar
    o, h, l, c, ts = ctx.open, ctx.high, ctx.low, ctx.close, ctx.ts
    tf_sec = ctx.tf_minutes * 60

    def hit(status, direction, x, price, detail, levels=None):
        return PatternHit(KEY, TITLE, direction, int(x), float(price), detail, levels or {}, int(ts[x]) if 0 <= x < len(ts) else 0, status)

    # 1) rotura con cuerpo (cierre más allá del High o del Low)
    brk = None
    for j in range(start, end + 1):
        if c[j] > tbr.high:
            brk = (j, True)
            break
        if c[j] < tbr.low:
            brk = (j, False)
            break
    if brk is None:
        if ctx.window_closed:
            x = min(max(end, 0), len(ts) - 1)
            return [hit(EXPIRED, "", x, tbr.mid, f"no hubo rotura con cuerpo del High ni del Low de la TBR antes de que empezara "
                                                  f"{ctx.next_zone} ({ctx.next_hours} NY)")], []
        return [], []
    j, up = brk
    if (h[start:j] > tbr.high).any() or (l[start:j] < tbr.low).any():
        return [], []                                         # una mecha tomó antes un lado de la TBR: es de Reversión, no de Continuación
    sign = 1 if up else -1
    # espejo: el bajista se calcula con los precios cambiados de signo, así la lógica es una sola
    H, L = (h, l) if up else (-l, -h)
    side = "High" if up else "Low"
    direction = "long" if up else "short"
    # 2) swing high (0) y swing low posterior (1) tras la rotura; 3) activación al superar el 0 y 4) reversión al 0,5
    leg = run_leg(H, L, j, end, swing_bars)
    if leg.origin is None:
        if ctx.window_closed:
            x = min(max(end, 0), len(ts) - 1)
            return [hit(EXPIRED, direction, x, tbr.mid, f"rotura con cuerpo del {side} en {_when(ctx, j)} pero sin swing high y swing low "
                                                        f"posteriores antes de que {ctx.limit_verb} {ctx.next_zone} ({ctx.next_hours} NY)")], []
        return [], []
    zero, swing, entry = leg.zero, leg.origin, leg.entry
    half = (zero + swing) / 2
    target = zero + (zero - swing) / 2                        # nivel -0,5: media vuelta del tramo más allá del 0
    levels = {"-0,5": sign * target, "0": sign * zero, "0,5": sign * half, "1": sign * swing}
    arrow = "▲" if up else "▼"
    label = f"{tbr.zone} {arrow}"
    x_end = int(ts[min(end, len(ts) - 1)]) + tf_sec
    if leg.breach is not None:                                # el fibo ya estaba formado: se anota (NO GO «I») y se dibuja hasta ahí
        marks = {"stop": sign * swing, "target": sign * target, "fibo 0": sign * zero, "fibo 0,5": sign * half}
        return [hit(INVALIDATED, direction, leg.breach, sign * swing,
                    f"rotura con cuerpo del {side} en {_when(ctx, j)}; el retroceso perdió el swing low ({sign * swing:.5g}) antes de llegar "
                    f"al 0,5: patrón invalidado", marks)], \
            [Figure("fib", KEY, tbr.zone, direction, int(ts[leg.zero_idx]), int(ts[leg.breach]) + tf_sec, levels, "invalidada", label,
                    tbr.day.isoformat())]
    if entry is not None:
        t, half = entry
        detail = (f"rotura con cuerpo del {side} en {_when(ctx, j)}, swing high (0) en {_when(ctx, leg.zero_idx)} y swing low (1) en "
                  f"{_when(ctx, leg.origin_idx)}; reversión al 0,5 ({sign * half:.5g}) en {_when(ctx, t)}. Entrada en el 0,5, stop en el "
                  f"swing low y objetivo en el -0,5 (2R)")
        found = hit(DETECTED, direction, t, sign * half, detail,
                    {"stop": sign * swing, "target": sign * target, "fibo 0": sign * zero, "fibo 0,5": sign * half})
        pos = position_figure(ctx, KEY, tbr.zone, direction, t, sign * half, sign * swing, sign * target, label)
        return [found], [Figure("fib", KEY, tbr.zone, direction, int(ts[leg.zero_idx]), x_end, levels, "entrada", label, tbr.day.isoformat()), pos]
    if ctx.window_closed:                                     # setup formado cuyo plazo se corta por tiempo: Cortex lo anota NO GO «T»
        x = min(max(end, 0), len(ts) - 1)
        return [hit(EXPIRED, direction, x, sign * half, f"rotura con cuerpo del {side} en {_when(ctx, j)} pero sin reversión al 0,5 "
                                                        f"antes de que {ctx.limit_verb} {ctx.next_zone} ({ctx.next_hours} NY)",
                    {"stop": sign * swing, "target": sign * target, "fibo 0": sign * zero, "fibo 0,5": sign * half})], \
            [Figure("fib", KEY, tbr.zone, direction, int(ts[leg.zero_idx]), x_end, levels, "vencida", label, tbr.day.isoformat())]
    return [], [Figure("fib", KEY, tbr.zone, direction, int(ts[leg.zero_idx]), x_end, levels, "en curso", label, tbr.day.isoformat())]


def _when(ctx: PatternContext, i: int) -> str:
    """Hora de Nueva York (HH:MM) de la vela `i`."""
    from datetime import datetime, timezone
    return datetime.fromtimestamp(int(ctx.ts[i]) - ctx.ahead, tz=timezone.utc).strftime("%H:%M NY")
