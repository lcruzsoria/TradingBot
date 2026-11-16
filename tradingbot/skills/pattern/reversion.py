"""Patrón «Reversión»: toma de un lado de la TBR solo con la mecha, fibonacci de la primera pierna de reversión y entrada en el 0,5.

Ejemplo bajista (el alcista es el espejo exacto, con el Low):

1. Toma con mecha: una vela de M15 supera el High de la TBR con su mecha pero CIERRA dentro del rango (si cerrara fuera, sería una
   rotura con cuerpo y la TBR sería del patrón Continuación). Es la primera toma de un lado tras el cierre de la TBR.
2. Mecha pivote: el pivote de tres velas (su máximo es el más alto de las tres) que forma esa mecha. Si antes de confirmarse alguna
   vela cierra por encima del High, el patrón se invalida (pasa a ser continuación).
3. Fibonacci (modo «swing», el de siempre): como en Continuación, de la primera pierna tras la toma. El 0 es el primer swing low posterior
   a la mecha pivote (en el corto) y el 1 el swing high que viene después, que solo vale si queda por encima del máximo de la vela del 0.
   Mientras el precio no revierta al 0,5, un swing low posterior más bajo sustituye al 0 y el 1 se busca de nuevo. El 0,5 es el punto
   medio. La mecha de la toma ya no es el 1: solo invalida si el precio la pierde antes de que haya fibo. (Modo «mecha», el anterior:
   el 1 es la mecha pivote y el 0 el último pivote bajo; queda para comparar en el backtest.)
4. Entrada: la primera vela posterior a la que confirma el swing del 1 que revierte hasta el 0,5 (su máximo lo toca y abre por debajo).
   Stop en el 1 y objetivo en el -0,5 (media vuelta del tramo más allá del 0): con entrada en el 0,5, son 2R. Si el precio pierde el 1
   antes de la entrada, se invalida; si termina el plazo de la TBR sin reversión al 0,5, vence.
5. Rotura con cuerpo: si, ya confirmada la mecha pivote, una vela CIERRA por encima del High tomado antes de la entrada, la reversión se
   anula (el mercado ha roto ese lado: ahora es continuación). Una rotura en la misma vela de la entrada o después no la anula.

Trabaja siempre con velas de `PATTERN_REVERSION_TF` (M15 al inicio), sea cual sea el timeframe del gráfico.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np

from ...timeframes import parse_timeframe
from .continuacion import _when, make_sub, run_leg
from . import confirm as confirmation
from .fibo import at_level, fibo_levels, level_name, level_settings, rr_of, run_fibo
from .trade import position_figure
from .patterns import DETECTED, EXPIRED, INVALIDATED, Figure, Pattern, PatternContext, PatternHit, register_pattern

DEFAULT_TF = "15m"
DEFAULT_SWING_BARS = 1
DEFAULT_FIBO = "swing"      # «swing»: el fibo del swing high (0) al swing low posterior (1); «mecha»: el 1 es la mecha de la toma (modo anterior)
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
        self.sl, self.tp = level_settings(get)                  # PATTERN_STOP_LEVEL / PATTERN_TARGET_LEVEL

    def timeframe(self) -> str:
        return self.tf

    def detect(self, ctx: PatternContext) -> list[PatternHit]:
        return analyze(ctx, self.swing_bars, self.sl, self.tp)[0]

    def figures(self, ctx: PatternContext) -> list[Figure]:
        return analyze(ctx, self.swing_bars, self.sl, self.tp)[1]


def analyze(ctx: PatternContext, k: int, sl: float = 1.0, tp: float = -0.5, confirm: str = "none",
            ltf: dict | None = None, mode: str = DEFAULT_FIBO, entry_ltf: dict | None = None) -> tuple[list[PatternHit], list[Figure]]:
    """`confirm`: "none" (entrada en el 0,5 sin más), "cisd" (antes de la entrada, una vela de M15 cierra bajo el CISD) o "bpr" (antes de la
    entrada, BPR + retest + cierre bajo el CISD en las velas `ltf` = {"ts", "open", "high", "low", "close", "tf_min"} de M5 o M3).

    `entry_ltf` ({"ts", "open", "high", "low", "close"}, solo con mode "swing"): velas de un timeframe menor en las que buscar la entrada una vez
    definido el fibo; la hora del resultado (`ts`) es la de esa vela."""
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
    cidx = None
    not_before = -1
    if confirm != "none":
        not_before = end + 1                                  # sin confirmación no hay entrada
        W = (h, l, o, c) if up else (-l, -h, -o, -c)          # espacio del corto
        if confirm == "cisd":
            cidx = confirmation.cisd_confirmation(*W, origin, max(ctx.start_bar, 0), end)
            if cidx is not None:
                not_before = cidx
        elif confirm == "bpr" and ltf is not None:
            lts, lsec = ltf["ts"], ltf["tf_min"] * 60
            a, b = int(np.searchsorted(lts, ts[origin], "left")), int(np.searchsorted(lts, ts[origin] + tf_sec, "left"))
            lend = int(np.searchsorted(lts, ts[min(end, len(ts) - 1)] + tf_sec, "left")) - 1
            if b > a and lend >= a:
                LW = ((ltf["open"], ltf["high"], ltf["low"], ltf["close"]) if up else (-ltf["open"], -ltf["low"], -ltf["high"], -ltf["close"]))
                Lo, Lh, Ll, Lc = LW
                anchor = a + int(np.argmax(Lh[a:b]))
                floor = int(np.searchsorted(lts, ts[max(ctx.start_bar, 0)], "left"))
                li = confirmation.bpr_confirmation(Lh, Ll, Lo, Lc, anchor, floor, lend)
                if li is not None:
                    cidx = li
                    done_at = int(lts[li]) + lsec           # la confirmación cierra ahí: la entrada, en una vela de M15 que abra después
                    not_before = int(np.searchsorted(ts, done_at, "left")) - 1
    wick_price = origin_price
    if mode == "swing":
        # el fibo es de la primera pierna de reversión: 0 = swing high posterior a la mecha, 1 = swing low siguiente (por debajo del mínimo
        # de la vela del 0); la mecha de la toma solo invalida si el precio la pierde antes de tener el fibo
        leg = run_leg(H, L, confirmed, end, k, -o if up else o, wick_price, not_before,
                      None if entry_ltf is None else make_sub(ctx, entry_ltf, not up))
        if leg.origin is None:
            if leg.breach is not None:
                return [hit(INVALIDATED, direction, leg.breach, sign * wick_price,
                            f"toma con mecha del {side} en {_when(ctx, j)}; el precio perdió la mecha pivote ({sign * wick_price:.5g}) en "
                            f"{_when(ctx, leg.breach)} antes de definir el fibo (swing high y swing low): patrón invalidado")], []
            if ctx.window_closed:
                return expired(direction, f"toma con mecha del {side} en {_when(ctx, j)} pero sin swing high y swing low posteriores")
            return [], []
        zero, zero_idx, extreme, origin_price = leg.zero, leg.zero_idx, leg.zero, leg.origin
        entry, breach, x0 = leg.entry, leg.breach, leg.zero_idx
        z, one = ("swing low", "swing high") if up else ("swing high", "swing low")           # en el corto el 0 es un mínimo y el 1 un máximo
        legtxt = f"{z} (0) en {_when(ctx, zero_idx)} y {one} (1) en {_when(ctx, leg.origin_idx)}"
    else:
        state = run_fibo(H, L, confirmed, end, origin_price, k, origin + 1, float(H[origin:confirmed + 1].max()),
                         -o if up else o, not_before)
        zero, zero_idx, extreme, entry, breach, x0 = state.zero, state.zero_idx, state.extreme, state.entry, state.breach, origin
        legtxt = f"0 en {_when(ctx, zero_idx)}"
    half = (extreme + origin_price) / 2
    target = at_level(extreme, origin_price, tp)              # objetivo y stop en los niveles configurados
    stop = at_level(extreme, origin_price, sl)
    levels = fibo_levels(extreme, origin_price, sl, tp, sign)
    label = f"{tbr.zone} {'▼' if up else '▲'} Rev"
    x_end = int(ts[min(end, len(ts) - 1)]) + tf_sec

    def invalid(t, price, detail):
        """Invalidación. Si el 0 ya estaba fijado (hay fibo), lleva sus niveles y se dibuja el fibo hasta la vela que lo invalida:
        Cortex lo anota NO GO «I»."""
        if zero is None:
            return [hit(INVALIDATED, direction, t, price, detail)], []
        marks = {"stop": sign * stop, "target": sign * target, "fibo 0": sign * extreme, "fibo 0,5": sign * half}
        return [hit(INVALIDATED, direction, t, price, detail, marks)], \
            [Figure("fib", KEY, tbr.zone, direction, int(ts[x0]), int(ts[t]) + tf_sec, levels, "invalidada", label, tbr.day.isoformat(), target=level_name(tp))]

    broke = next((t for t in range(confirmed + 1, end + 1) if (c[t] > tbr.high if up else c[t] < tbr.low)), None)
    if broke is not None and (entry is None or broke < entry[0]) and (breach is None or broke < breach):
        return invalid(broke, tbr.mid,
                       f"toma con mecha del {side} en {_when(ctx, j)}, mecha pivote en {_when(ctx, origin)}; una vela cerró fuera del "
                       f"{side} en {_when(ctx, broke)} antes del retroceso al 0,5: rotura con cuerpo, ya no es reversión")
    if breach is not None:
        lost = "el 1 del fibo" if mode == "swing" else "la mecha pivote"
        return invalid(breach, sign * origin_price,
                       f"toma con mecha del {side} en {_when(ctx, j)}; el precio {'perdió' if mode == 'swing' else 'superó'} {lost} ({sign * origin_price:.5g}) antes de "
                       f"llegar al 0,5: patrón invalidado")
    if entry is not None:
        t, half = entry
        detail = (f"toma con mecha del {side} en {_when(ctx, j)}, mecha pivote en {_when(ctx, origin)}, {legtxt}; "
                  f"retroceso al 0,5 ({sign * half:.5g}) en {_when(ctx, t)}. Entrada en el 0,5, stop en el {level_name(sl)} y objetivo "
                  f"en el {level_name(tp)} (RR {rr_of(sl, tp):.2g})")
        found = hit(DETECTED, direction, t, sign * half, detail,
                    {"stop": sign * stop, "target": sign * target, "fibo 0": sign * extreme, "fibo 0,5": sign * half})
        if mode == "swing" and leg.entry_sub is not None:
            found = replace(found, ts=int(entry_ltf["ts"][leg.entry_sub]))
        pos = position_figure(ctx, KEY, tbr.zone, direction, t, sign * half, sign * stop, sign * target, label)
        return [found], [Figure("fib", KEY, tbr.zone, direction, int(ts[x0]), x_end, levels, "entrada", label, tbr.day.isoformat(), target=level_name(tp)), pos]
    if ctx.window_closed:                                     # setup formado cuyo plazo se corta por tiempo: Cortex lo anota NO GO «T»
        why = "sin retroceso al 0,5" if confirm == "none" or cidx is not None else f"sin confirmación ({confirm.upper()})"
        found, _ = expired(direction, f"toma con mecha del {side} en {_when(ctx, j)} pero {why}")
        x = found[0].x
        return [hit(EXPIRED, direction, x, sign * half, found[0].detail,
                    {"stop": sign * stop, "target": sign * target, "fibo 0": sign * extreme, "fibo 0,5": sign * half})], \
            [Figure("fib", KEY, tbr.zone, direction, int(ts[x0]), x_end, levels, "vencida", label, tbr.day.isoformat(), target=level_name(tp))]
    return [], [Figure("fib", KEY, tbr.zone, direction, int(ts[x0]), x_end, levels, "en curso", label, tbr.day.isoformat(), target=level_name(tp))]
