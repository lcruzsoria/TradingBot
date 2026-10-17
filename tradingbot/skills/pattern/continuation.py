"""Patrón 1: continuación clásica de la tendencia tras tomar un extremo de la TBR activa.

Ejemplo bajista (el alcista es el espejo exacto, con el High):

1. Toma del Low: una vela (con la mecha o con el cuerpo) pierde el Low de la TBR. La TBR queda activa. Si una misma vela
   toma el High y el Low, no hay patrón.
2. Retroceso: después de la toma, la primera vela alcista (cierre sobre su apertura) es la «reversión» y cuenta como la vela 1.
   Basta una vela. La profundidad del retroceso se mide con la mecha (el máximo de las velas posteriores a la toma): si llega al
   50 % de la TBR (o al High) el patrón se INVALIDA. No importa que el cuerpo cierre por debajo.
3. Vela de disparo: la primera vela bajista (cierre bajo su apertura) tras la reversión cuya mecha superior no supere
   `PATTERN_CONTINUATION_MAX_WICK_PCT` % del tamaño total de la vela (0 = sin mecha, máximo 5). Puede formarse fuera de la TBR
   (por debajo del Low si el precio sigue cayendo). Se identifica al cierre de esa vela.
4. Plazo: la vela de disparo debe ser, como mucho, la número `PATTERN_CONTINUATION_MAX_CANDLES` (10) contando la de reversión;
   si no, el patrón se ANULA. Además, todo debe ocurrir antes de que empiece la TBR siguiente (si no, VENCE).

Trabaja siempre con velas de `PATTERN_CONTINUATION_TF` (M5 al inicio), sea cual sea el timeframe del gráfico. Un intento por TBR.
"""
from __future__ import annotations

from ...timeframes import parse_timeframe
from .patterns import ANNULLED, DETECTED, EXPIRED, INVALIDATED, Pattern, PatternContext, PatternHit, register_pattern

DEFAULT_TF = "5m"
DEFAULT_MAX_WICK_PCT = 0.0
MAX_WICK_PCT_LIMIT = 5.0
DEFAULT_MAX_CANDLES = 10
TITLE = "Continuación clásica"


@register_pattern("continuacion_clasica")
class ClassicContinuation(Pattern):
    title = TITLE

    def __init__(self, settings=None) -> None:
        super().__init__(settings)
        get = (lambda key, default: default) if settings is None else settings.get
        self.tf = parse_timeframe(str(get("CONTINUATION_TF", DEFAULT_TF)))
        self.max_wick_pct = float(str(get("CONTINUATION_MAX_WICK_PCT", DEFAULT_MAX_WICK_PCT)).replace(",", "."))
        self.max_candles = int(get("CONTINUATION_MAX_CANDLES", DEFAULT_MAX_CANDLES))
        if not 0 <= self.max_wick_pct <= MAX_WICK_PCT_LIMIT:
            raise ValueError(f"PATTERN_CONTINUATION_MAX_WICK_PCT={self.max_wick_pct:g} debe estar entre 0 y {MAX_WICK_PCT_LIMIT:g}.")
        if self.max_candles < 1:
            raise ValueError(f"PATTERN_CONTINUATION_MAX_CANDLES={self.max_candles} debe ser 1 o más.")

    def timeframe(self) -> str:
        return self.tf

    def detect(self, ctx: PatternContext) -> list[PatternHit]:
        return scan(ctx, self.max_wick_pct, self.max_candles)


def scan(ctx: PatternContext, max_wick_pct: float, max_candles: int) -> list[PatternHit]:
    tbr = ctx.tbr
    start, end = ctx.first_bar, ctx.last_bar
    o, h, l, c, ts = ctx.open, ctx.high, ctx.low, ctx.close, ctx.ts

    def hit(status, direction, x, price, detail, levels=None):
        return [PatternHit("continuacion_clasica", TITLE, direction, int(x), float(price), detail, levels or {},
                           int(ts[x]) if 0 <= x < len(ts) else 0, status)]

    def expired(direction, detail):
        x = min(max(end, 0), len(ts) - 1)
        return hit(EXPIRED, direction, x, tbr.mid, f"{detail} antes de que empezara {ctx.next_zone} ({ctx.next_hours} NY)")

    # 1) toma de un extremo de la TBR: define el lado
    sweep = None
    for i in range(start, end + 1):
        took_low, took_high = l[i] < tbr.low, h[i] > tbr.high
        if took_low and took_high:
            return hit(INVALIDATED, "", i, tbr.mid, "una misma vela tomó el High y el Low de la TBR: sin patrón")
        if took_low or took_high:
            sweep = (i, took_low)
            break
    if sweep is None:
        return expired("", "no hubo toma del High ni del Low de la TBR") if ctx.window_closed else []
    s, short = sweep
    direction = "short" if short else "long"
    side = "Low" if short else "High"
    # espejo: el largo se calcula con los precios cambiados de signo, así la lógica es una sola
    if short:
        O, H, L, C, mid = o, h, l, c, tbr.mid
        top = tbr.high
    else:
        O, H, L, C, mid = -o, -l, -h, -c, -tbr.mid
        top = -tbr.low
    sign = 1 if short else -1

    # 2) y 3) retroceso, invalidación, plazo de velas y vela de disparo
    r1 = None
    retrace = None                                     # máximo del retroceso (con la mecha), en el espejo
    for j in range(s + 1, end + 1):
        if H[j] >= mid:
            why = "tomó el lado contrario" if H[j] >= top else "llegó al 50 % de la TBR"
            return hit(INVALIDATED, direction, j, sign * mid,
                       f"toma del {side} en {_when(ctx, s)}; el retroceso {why} (mecha hasta {sign * H[j]:.5g}): patrón invalidado")
        retrace = H[j] if retrace is None else max(retrace, H[j])
        if r1 is None:
            if C[j] > O[j]:
                r1 = j                                 # la reversión es la vela 1
            continue
        n = j - r1 + 1
        if n > max_candles:
            break
        rng = H[j] - L[j]
        if C[j] < O[j] and rng > 0 and (H[j] - O[j]) <= max_wick_pct / 100 * rng + 1e-12 * abs(rng):
            wick = (H[j] - O[j]) / rng * 100
            return hit(DETECTED, direction, j, c[j],
                       f"toma del {side} en {_when(ctx, s)}, reversión en {_when(ctx, r1)}, vela de disparo nº {n} de {max_candles} "
                       f"(mecha {wick:.1f} %, máx. {max_wick_pct:g} %)",
                       {"toma": float(sign * (L[s])), "retroceso máx.": float(sign * retrace)})
    if r1 is not None and end >= r1 + max_candles - 1:
        x = r1 + max_candles - 1
        return hit(ANNULLED, direction, x, tbr.mid, f"pasaron {max_candles} velas desde la reversión ({_when(ctx, r1)}) "
                                                     f"sin vela sin mecha superior: patrón anulado")
    if ctx.window_closed:
        if r1 is None:
            return expired(direction, f"toma del {side} en {_when(ctx, s)} pero sin retroceso (ninguna vela de rebote)")
        return expired(direction, f"toma del {side} en {_when(ctx, s)} y reversión en {_when(ctx, r1)} pero sin vela de disparo")
    return []


def _when(ctx: PatternContext, i: int) -> str:
    """Hora de Nueva York (HH:MM) de la vela `i`."""
    from datetime import datetime, timezone
    return datetime.fromtimestamp(int(ctx.ts[i]) - ctx.ahead, tz=timezone.utc).strftime("%H:%M NY")
