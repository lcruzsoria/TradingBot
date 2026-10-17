"""Patrón «Continuación»: rotura con cuerpo de un lado de la TBR, fibonacci del tramo y entrada en la reversión al 0,5.

Ejemplo alcista (el bajista es el espejo exacto, con el Low):

1. Rotura: una vela de M15 CIERRA por encima del High de la TBR (rotura con cuerpo; una mecha sola no activa la TBR). La primera
   vela de ese tipo tras el cierre de la TBR, dentro de su plazo, la activa.
2. Swing previo: el último mínimo relevante (pivote: más bajo que las `PATTERN_CONTINUACION_SWING_BARS` velas de cada lado, 1 al
   inicio: el patrón de tres velas, con el extremo en la del medio) anterior
   a la rotura, desde el inicio de la TBR. A la derecha solo se miran las velas hasta la propia rotura, que confirma el pivote: así
   el pico inmediatamente anterior a la vela de rotura también es swing. Si no hay ninguno, el mínimo más bajo desde el inicio de la
   TBR hasta la rotura.
3. Fibonacci de ese tramo, con tres niveles: el 1 es el swing (origen del tramo), el 0 es el último pivote confirmado tras la rotura (el
   mismo patrón de tres velas: el máximo más alto en la vela del medio; un pivote más alto lo alarga) y el 0,5 es el punto medio. Hasta que
   hay un pivote confirmado, el 0 provisional es el extremo que lleva el precio.
4. Entrada: la primera vela que revierte hasta el 0,5 (su mínimo lo toca). Se identifica en ese momento y el 0 queda fijo; el precio de
   referencia es el 0,5. Si termina el plazo de la TBR sin que el precio revierta al 0,5, el patrón vence.
5. Stop en el swing (el nivel 1) y objetivo en el nivel -0,5 (media vuelta del tramo más allá del 0): con entrada en el 0,5, son 2R.

Solo trata el fibonacci en curso de las TBR recientes que se han activado.
Trabaja siempre con velas de `PATTERN_CONTINUACION_TF` (M15 al inicio), sea cual sea el timeframe del gráfico.
"""
from __future__ import annotations

import numpy as np

from ...timeframes import parse_timeframe
from .fibo import run_fibo
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


def _swing(L: np.ndarray, start: int, brk: int, k: int) -> int:
    """Índice del último pivote bajo (más bajo que `k` velas a cada lado) entre `start` y la rotura; si no hay, el mínimo más bajo."""
    for i in range(brk - 1, max(start, 0) - 1, -1):
        if i - k < 0:
            continue
        right = L[i + 1:min(i + k, brk) + 1]                    # a la derecha, hasta la propia vela de rotura (que confirma el pivote)
        if L[i] < L[i - k:i].min() and L[i] < right.min():
            return i
    window = L[max(start, 0):brk]
    return max(start, 0) + int(len(window) - 1 - np.argmin(window[::-1]))          # último mínimo (el más reciente si hay empate)


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
    sign = 1 if up else -1
    # espejo: el bajista se calcula con los precios cambiados de signo, así la lógica es una sola
    H, L = (h, l) if up else (-l, -h)
    side = "High" if up else "Low"
    direction = "long" if up else "short"
    # 2) swing previo a la rotura
    s = _swing(L, ctx.start_bar, j, swing_bars)
    swing = float(L[s])
    # 3) fibonacci del tramo (el 0 es el último pivote confirmado, ver fibo.py) y 4) reversión al 0,5
    state = run_fibo(H, L, j, end, swing, swing_bars, j, float(H[j]))
    zero, zero_idx, entry = state.zero, state.zero_idx, state.entry
    extreme = state.extreme
    half = (extreme + swing) / 2
    target = extreme + (extreme - swing) / 2                  # nivel -0,5: media vuelta del tramo más allá del 0
    levels = {"-0,5": sign * target, "0": sign * extreme, "0,5": sign * half, "1": sign * swing}
    if state.breach is not None:
        return [hit(INVALIDATED, direction, state.breach, sign * swing,
                    f"rotura con cuerpo del {side} en {_when(ctx, j)}; el retroceso perdió el swing ({sign * swing:.5g}) antes de llegar "
                    f"al 0,5: patrón invalidado")], []
    arrow = "▲" if up else "▼"
    label = f"{tbr.zone} {arrow}"
    x_end = int(ts[min(end, len(ts) - 1)]) + tf_sec
    if entry is not None:
        t, half = entry
        detail = (f"rotura con cuerpo del {side} en {_when(ctx, j)}, swing previo en {_when(ctx, s)}, 0 en {_when(ctx, zero_idx)}; reversión al 0,5 "
                  f"({sign * half:.5g}) en {_when(ctx, t)}. Entrada en el 0,5, stop en el swing y objetivo en el -0,5 (2R)")
        found = hit(DETECTED, direction, t, sign * half, detail,
                    {"stop": sign * swing, "target": sign * target, "fibo 0": sign * extreme, "fibo 0,5": sign * half})
        pos = position_figure(ctx, KEY, tbr.zone, direction, t, sign * half, sign * swing, sign * target, label)
        return [found], [Figure("fib", KEY, tbr.zone, direction, int(ts[s]), x_end, levels, "entrada", label), pos]
    if ctx.window_closed:
        x = min(max(end, 0), len(ts) - 1)
        return [hit(EXPIRED, direction, x, sign * half, f"rotura con cuerpo del {side} en {_when(ctx, j)} pero sin reversión al 0,5 "
                                                        f"antes de que empezara {ctx.next_zone} ({ctx.next_hours} NY)")], []
    return [], [Figure("fib", KEY, tbr.zone, direction, int(ts[s]), x_end, levels, "en curso", label)]


def _when(ctx: PatternContext, i: int) -> str:
    """Hora de Nueva York (HH:MM) de la vela `i`."""
    from datetime import datetime, timezone
    return datetime.fromtimestamp(int(ctx.ts[i]) - ctx.ahead, tz=timezone.utc).strftime("%H:%M NY")
