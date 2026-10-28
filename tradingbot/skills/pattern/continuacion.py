"""Patrón «Continuación»: rotura con cuerpo de un lado de la TBR, fibonacci del último tramo de estructura y entrada en el 0,5.

Ejemplo alcista (el bajista es el espejo exacto, con el Low):

1. Rotura: una vela de M15 CIERRA por encima del High de la TBR (rotura con cuerpo; una mecha sola no activa la TBR). La primera
   vela de ese tipo tras el cierre de la TBR, dentro de su plazo, la activa. Si antes de esa rotura una vela ya tomó con la mecha
   (y cerró dentro) cualquiera de los dos lados de la TBR, la TBR es de Reversión y la Continuación se bloquea: manda lo primero que pasa.
2. Swing high (el 0): el primer pivote alto (de `PATTERN_CONTINUACION_SWING_BARS` velas a cada lado, 1 al inicio: el patrón de tres velas,
   con el extremo en la del medio) a partir de la rotura. Un swing high más alto, antes de la entrada, sustituye al 0.
3. Swing low previo (el 1, el stop): un pivote bajo que ya existe, a la IZQUIERDA del 0. Dos casos:
   A. Ideal: el último swing low formado desde que cerró la TBR cuyo precio está dentro del rango de la TBR.
   B. Flexible: si no hay ninguno, el primer swing low tras la rotura (fuera del rango, por encima del High).
   Los dos pueden disparar a Cortex y el forwardtest anota de cuál se trata.
   El fibonacci va del 1 al 0, con el 0,5 como punto medio, y queda fijo. Como el 1 ya está formado, el stop existe cuando se forma el 0.
4. Entrada: la primera vela posterior a la que confirma el swing high del 0 que retrocede hasta el 0,5 (su mínimo lo toca) viniendo de
   arriba (abre por encima del 0,5). Si pierde el 1 antes de eso, el patrón se invalida; si termina el plazo de la TBR sin entrada,
   vence.
5. Stop en el swing low (el nivel 1) y objetivo en el nivel configurado (`PATTERN_TARGET_LEVEL`).

Solo trata el fibonacci en curso de las TBR recientes que se han activado.
Trabaja siempre con velas de `PATTERN_CONTINUACION_TF` (M15 al inicio), sea cual sea el timeframe del gráfico.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ...timeframes import parse_timeframe
from .fibo import at_level, fibo_levels, level_name, level_settings, rr_of
from .trade import position_figure
from .patterns import DETECTED, EXPIRED, INVALIDATED, Figure, Pattern, PatternContext, PatternHit, register_pattern

DEFAULT_TF = "15m"
DEFAULT_SWING_BARS = 1
KEY = "continuacion"
TITLE = "Continuación"
CASE_IDEAL = "A. Ideal"            # el swing que marca el stop está dentro del rango de la TBR (el precio vuelve al rango)
CASE_FLEXIBLE = "B. Flexible"      # el primer swing tras la rotura queda fuera del rango: también dispara, pero se anota aparte


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
        self.sl, self.tp = level_settings(get)                  # PATTERN_STOP_LEVEL / PATTERN_TARGET_LEVEL

    def timeframe(self) -> str:
        return self.tf

    def detect(self, ctx: PatternContext) -> list[PatternHit]:
        return analyze(ctx, self.swing_bars, self.sl, self.tp)[0]

    def figures(self, ctx: PatternContext) -> list[Figure]:
        return analyze(ctx, self.swing_bars, self.sl, self.tp)[1]


@dataclass(frozen=True)
class Leg:
    zero: float | None        # swing high tras la rotura (el 0)
    zero_idx: int
    origin: float | None      # swing low previo (el 1); None si todavía no hay
    origin_idx: int
    active: bool              # el fibo ya está formado (hay 0 y 1)
    entry: tuple[int, float] | None   # (vela de la entrada, nivel 0,5)
    breach: int | None        # vela en la que el precio perdió el 1 antes de la entrada


def run_leg(H: np.ndarray, L: np.ndarray, brk: int, end: int, k: int, O: np.ndarray | None = None,
            span: tuple[float, float] | None = None, first: int = 0) -> Leg:
    """Recorre las velas `brk + 1 .. end` buscando el swing high (0) tras la rotura, el swing low previo (1) y la entrada en el 0,5.

    El 1 ya está formado cuando se confirma el 0: el último swing low desde `first` (primera vela tras la TBR) con el precio dentro del
    rango `span` (caso A) o, si no hay, el primer swing low tras la rotura (caso B). La entrada solo puede ser una vela posterior a la
    que confirma el 0 y, si se dan las aperturas `O`, que abra por encima del 0,5 (viene del lado del 0)."""
    def pivot_low(q: int) -> bool:
        return q >= k and L[q] < L[q - k:q].min() and L[q] < L[q + 1:q + k + 1].min()

    def stop_swing(zero_idx: int) -> int | None:
        for q in range(zero_idx - 1, max(first, k) - 1, -1):          # A: el más reciente dentro del rango de la TBR
            if span is not None and span[0] <= L[q] <= span[1] and pivot_low(q) and L[q + 1:zero_idx + 1].min() >= L[q]:
                return q
        for q in range(max(brk, k), zero_idx):                          # B: el primero tras la rotura (fuera del rango)
            if span is not None and L[q] > span[1] and pivot_low(q) and L[q + 1:zero_idx + 1].min() >= L[q]:
                return q
        return None

    zero, zero_idx, origin, origin_idx = None, -1, None, -1
    for t in range(brk + 1, end + 1):
        if origin is not None:
            if L[t] < origin:                                               # perdió el 1 (el stop) antes de la entrada
                return Leg(zero, zero_idx, origin, origin_idx, True, None, t)
            half = (zero + origin) / 2
            if t > zero_idx + k and L[t] <= half and (O is None or O[t] > half):
                return Leg(zero, zero_idx, origin, origin_idx, True, (t, half), None)
        p = t - k
        if p >= max(brk, k) and H[p] > H[p - k:p].max() and H[p] > H[p + 1:p + k + 1].max() and (zero is None or H[p] > zero):
            zero, zero_idx = float(H[p]), p                                 # un swing high más alto sustituye al 0
            q = stop_swing(p)
            origin, origin_idx = (float(L[q]), q) if q is not None else (None, -1)
            if origin is not None and L[t] < origin:                        # la propia vela que confirma el 0 ya pierde el 1
                return Leg(zero, zero_idx, origin, origin_idx, True, None, t)
    return Leg(zero, zero_idx, origin, origin_idx, origin is not None, None, None)


def analyze(ctx: PatternContext, swing_bars: int, sl: float = 1.0, tp: float = -0.5) -> tuple[list[PatternHit], list[Figure]]:
    tbr = ctx.tbr
    start, end = ctx.first_bar, ctx.last_bar
    o, h, l, c, ts = ctx.open, ctx.high, ctx.low, ctx.close, ctx.ts
    tf_sec = ctx.tf_minutes * 60

    def hit(status, direction, x, price, detail, levels=None, variant=""):
        return PatternHit(KEY, TITLE, direction, int(x), float(price), detail, levels or {}, int(ts[x]) if 0 <= x < len(ts) else 0, status,
                          variant)

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
    sw0, sw1 = ("swing high", "swing low") if up else ("swing low", "swing high")      # el 0 y el 1 (el stop) de este lado
    # 2) swing high (0) tras la rotura y swing low previo (1); 3) entrada en el 0,5 (el 1 ya existe cuando se forma el 0)
    span = (tbr.low, tbr.high) if up else (-tbr.high, -tbr.low)
    leg = run_leg(H, L, j, end, swing_bars, o if up else -o, span, start)
    if leg.origin is None:
        if ctx.window_closed:
            x = min(max(end, 0), len(ts) - 1)
            return [hit(EXPIRED, direction, x, tbr.mid, f"rotura con cuerpo del {side} en {_when(ctx, j)} pero sin {sw0} tras la rotura con un {sw1} previo "
                                                        f"que marque el stop antes de que {ctx.limit_verb} {ctx.next_zone} ({ctx.next_hours} NY)")], []
        return [], []
    zero, swing, entry = leg.zero, leg.origin, leg.entry
    half = (zero + swing) / 2
    target = at_level(zero, swing, tp)                        # objetivo y stop en los niveles configurados
    stop = at_level(zero, swing, sl)
    levels = fibo_levels(zero, swing, sl, tp, sign)
    case = CASE_IDEAL if tbr.low <= sign * swing <= tbr.high else CASE_FLEXIBLE      # dónde cae el swing que marca el stop
    arrow = "▲" if up else "▼"
    label = f"{tbr.zone} {arrow}"
    x_end = int(ts[min(end, len(ts) - 1)]) + tf_sec
    if leg.breach is not None:                                # el fibo ya estaba formado: se anota (NO GO «I») y se dibuja hasta ahí
        marks = {"stop": sign * stop, "target": sign * target, "fibo 0": sign * zero, "fibo 0,5": sign * half}
        return [hit(INVALIDATED, direction, leg.breach, sign * swing,
                    f"rotura con cuerpo del {side} en {_when(ctx, j)}; el retroceso perdió el {sw1} ({sign * swing:.5g}) antes de llegar "
                    f"al 0,5: patrón invalidado", marks, case)], \
            [Figure("fib", KEY, tbr.zone, direction, int(ts[min(leg.origin_idx, leg.zero_idx)]), int(ts[leg.breach]) + tf_sec, levels, "invalidada", label,
                    tbr.day.isoformat(), target=level_name(tp))]
    if entry is not None:
        t, half = entry
        detail = (f"rotura con cuerpo del {side} en {_when(ctx, j)}, {sw1} previo (1) en {_when(ctx, leg.origin_idx)} y {sw0} (0) en "
                  f"{_when(ctx, leg.zero_idx)}; reversión al 0,5 ({sign * half:.5g}) en {_when(ctx, t)}. Entrada en el 0,5, stop en el "
                  f"{level_name(sl)} y objetivo en el {level_name(tp)} (RR {rr_of(sl, tp):.2g}). Caso {case}: "
                  f"{'el swing del stop está dentro del rango de la TBR' if case == CASE_IDEAL else 'el swing del stop queda fuera del rango de la TBR'}")
        found = hit(DETECTED, direction, t, sign * half, detail,
                    {"stop": sign * stop, "target": sign * target, "fibo 0": sign * zero, "fibo 0,5": sign * half}, case)
        pos = position_figure(ctx, KEY, tbr.zone, direction, t, sign * half, sign * stop, sign * target, label)
        return [found], [Figure("fib", KEY, tbr.zone, direction, int(ts[min(leg.origin_idx, leg.zero_idx)]), x_end, levels, "entrada", label, tbr.day.isoformat(), target=level_name(tp)), pos]
    if ctx.window_closed:                                     # setup formado cuyo plazo se corta por tiempo: Cortex lo anota NO GO «T»
        x = min(max(end, 0), len(ts) - 1)
        return [hit(EXPIRED, direction, x, sign * half, f"rotura con cuerpo del {side} en {_when(ctx, j)} pero sin reversión al 0,5 "
                                                        f"antes de que {ctx.limit_verb} {ctx.next_zone} ({ctx.next_hours} NY)",
                    {"stop": sign * stop, "target": sign * target, "fibo 0": sign * zero, "fibo 0,5": sign * half}, case)], \
            [Figure("fib", KEY, tbr.zone, direction, int(ts[min(leg.origin_idx, leg.zero_idx)]), x_end, levels, "vencida", label, tbr.day.isoformat(), target=level_name(tp))]
    return [], [Figure("fib", KEY, tbr.zone, direction, int(ts[min(leg.origin_idx, leg.zero_idx)]), x_end, levels, "en curso", label, tbr.day.isoformat(), target=level_name(tp))]


def _when(ctx: PatternContext, i: int) -> str:
    """Hora de Nueva York (HH:MM) de la vela `i`."""
    from datetime import datetime, timezone
    return datetime.fromtimestamp(int(ctx.ts[i]) - ctx.ahead, tz=timezone.utc).strftime("%H:%M NY")
