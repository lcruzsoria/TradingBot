"""Patrón 2: continuación 50 %. Como el patrón 1, pero la TBR se activa al tomar el 50 % sin haber tomado antes un extremo.

Ejemplo bajista (el alcista es el espejo exacto):

1. Activación: una vela toma el 50 % de abajo hacia arriba (con mecha o con cuerpo) sin que antes se haya tomado el High ni el
   Low. La dirección es bajista (de arriba hacia abajo sería alcista). Esa vela cuenta como la vela 1 y NUNCA es la de disparo.
   Si esa misma vela toma también el High (el extremo contrario), el patrón se INVALIDA.
2. Límite: el precio no puede tocar el High en ningún momento antes del disparo (si lo toca, INVALIDADO).
3. Vela de disparo: desde la vela siguiente a la de activación, la primera vela bajista sin mecha superior (o con una de hasta
   `PATTERN_CONTINUATION50_MAX_WICK_PCT` %, 0 al inicio) que esté POR DEBAJO del 50 % (su máximo bajo el 50 %). Se identifica al
   cierre. Puede formarse fuera de la TBR.
4. Plazo: como mucho la vela `PATTERN_CONTINUATION50_MAX_CANDLES` (10) contando la de activación; si no, se ANULA. Todo debe
   ocurrir antes de que empiece la TBR siguiente (si no, VENCE).

Entre los patrones 1 y 2 solo se activa uno por TBR: el que tenga el primer hecho (ver activation.py). El otro se descarta sin avisar.
"""
from __future__ import annotations

from .activation import first_event
from .continuation import _when, read_options
from .patterns import ANNULLED, DETECTED, EXPIRED, INVALIDATED, Pattern, PatternContext, PatternHit, register_pattern

TITLE = "Continuación 50 %"


@register_pattern("continuacion_50")
class HalfContinuation(Pattern):
    title = TITLE

    def __init__(self, settings=None) -> None:
        super().__init__(settings)
        self.tf, self.max_wick_pct, self.max_candles = read_options(settings, "CONTINUATION50")

    def timeframe(self) -> str:
        return self.tf

    def detect(self, ctx: PatternContext) -> list[PatternHit]:
        return scan(ctx, self.max_wick_pct, self.max_candles)


def scan(ctx: PatternContext, max_wick_pct: float, max_candles: int) -> list[PatternHit]:
    tbr = ctx.tbr
    end = ctx.last_bar
    o, h, l, c, ts = ctx.open, ctx.high, ctx.low, ctx.close, ctx.ts

    def hit(status, direction, x, price, detail, levels=None):
        return [PatternHit("continuacion_50", TITLE, direction, int(x), float(price), detail, levels or {},
                           int(ts[x]) if 0 <= x < len(ts) else 0, status)]

    event = first_event(ctx)
    if event is None or event.kind != "mid":
        return []                                       # sin activación, o la TBR la tiene el patrón 1: sin aviso
    a, short = event.index, event.side == "below"
    direction = "short" if short else "long"
    # espejo: el largo se calcula con los precios cambiados de signo, así la lógica es una sola
    if short:
        O, H, L, C, mid, top = o, h, l, c, tbr.mid, tbr.high
    else:
        O, H, L, C, mid, top = -o, -l, -h, -c, -tbr.mid, -tbr.low
    sign = 1 if short else -1
    contrary = "High" if short else "Low"
    origin = "abajo hacia arriba" if short else "arriba hacia abajo"
    if event.contrary_taken:
        return hit(INVALIDATED, direction, a, tbr.mid,
                   f"la vela que tomó el 50 % ({_when(ctx, a)}) tomó también el {contrary}: patrón invalidado")
    for j in range(a + 1, end + 1):
        if H[j] >= top:
            return hit(INVALIDATED, direction, j, sign * top,
                       f"toma del 50 % de {origin} en {_when(ctx, a)}; el precio tocó el {contrary} de la TBR: patrón invalidado")
        n = j - a + 1
        if n > max_candles:
            break
        rng = H[j] - L[j]
        if (C[j] < O[j] and rng > 0 and H[j] < mid and (H[j] - O[j]) <= max_wick_pct / 100 * rng + 1e-12 * abs(rng)):
            wick = (H[j] - O[j]) / rng * 100
            peak = max(H[a + 1:j + 1].max(), H[a])
            return hit(DETECTED, direction, j, c[j],
                       f"toma del 50 % de {origin} en {_when(ctx, a)}, vela de disparo nº {n} de {max_candles} bajo el 50 % "
                       f"(mecha {wick:.1f} %, máx. {max_wick_pct:g} %)",
                       {"toma 50 %": float(tbr.mid), "máx. antes del disparo": float(sign * peak)})
    if end >= a + max_candles - 1:
        x = a + max_candles - 1
        return hit(ANNULLED, direction, x, tbr.mid, f"pasaron {max_candles} velas desde la toma del 50 % ({_when(ctx, a)}) "
                                                     f"sin vela de disparo sin mecha bajo el 50 %: patrón anulado")
    if ctx.window_closed:
        return hit(EXPIRED, direction, min(max(end, 0), len(ts) - 1), tbr.mid,
                   f"toma del 50 % de {origin} en {_when(ctx, a)} pero sin vela de disparo bajo el 50 % antes de que "
                   f"empezara {ctx.next_zone} ({ctx.next_hours} NY)")
    return []
