"""Patrón «Doble barrido TBR»: NY Open cierra por encima de los High de Asia y London (o por debajo de sus Low), vuelve por debajo de los dos y
se entra en el retesteo del más alto.

Ejemplo bajista (el alcista es el espejo exacto, con los Low):

1. Toma con cuerpo: una vela de M5 CIERRA por encima de los High de la TBR de Asia y de la de London (cruzándolos: la vela anterior
   no había cerrado ya por encima), desde el cierre de la última de las dos hasta el cierre de la TBR de NY Open. Puede ser antes de
   que empiece NY Open. El orden da igual: basta que una vela cierre sobre el más alto de los
   dos (así ya ha cerrado sobre el otro).
2. Swing high: el máximo absoluto del barrido, desde esa vela hasta el paso 3. Se va actualizando con cada máximo nuevo hasta que el
   precio vuelve por debajo de los dos High; entonces queda fijo. Es el 1 de un fibonacci cuyo 0 es el más alto de los dos High.
3. Confirmación: una vela posterior pasa por DEBAJO de los dos High (basta la mecha).
4. Entrada: tras la confirmación, el precio retestea el High de Asia (basta la mecha: el rango de la vela lo atraviesa): venta en ese
   nivel (`PATTERN_DOBLE_BARRIDO_ENTRY`: asia, o el más extremo / menos extremo de los dos). Solo vale desde el inicio de la TBR de NY
   Open: un retesteo anterior no es entrada. Si antes de entrar el precio supera el swing, el barrido sigue en marcha y se reinicia desde
   ahí; pasado el cierre de la TBR de NY Open, el setup se invalida. Stop en el 0,618 de ese fibonacci
   (`PATTERN_DOBLE_BARRIDO_STOP_FIB`; 1 = el propio swing high). Objetivo: el Low más bajo entre Asia y London. Con la posición a +BE_R el stop pasa
   a la entrada en cuanto el precio toca ese nivel (ver `setup/positions.py`).

Un solo trade al día: si los dos lados dan entrada, cuenta la primera. Se busca hasta el cierre del día de trading. Trabaja siempre con velas de `PATTERN_DOBLE_BARRIDO_TF` (M5 al inicio).
"""
from __future__ import annotations

import numpy as np

from ...timeframes import parse_timeframe
from .continuacion import _when
from .patterns import DETECTED, EXPIRED, INVALIDATED, Figure, Pattern, PatternContext, PatternHit, register_pattern
from .trade import day_close, position_figure

DEFAULT_TF = "5m"
KEY = "doble_barrido"
TITLE = "Doble barrido TBR"
DEFAULT_STOP_FIB = 0.618
ENTRIES = ("asia", "extremo", "primero")   # nivel que se retestea: el de Asia, el más extremo de los dos o el menos extremo
DEFAULT_ENTRY = "asia"
NY_KEY = "NY_AM"                       # la TBR que barre
EARLIER = ("ASIA", "LONDON")           # las TBR cuyos niveles barre
MAX_GAP = 36 * 3600                    # una Asia o London más antigua que esto no es la del día


@register_pattern(KEY)
class DobleBarrido(Pattern):
    title = TITLE
    default_on = False                     # en backtest hasta validarlo: con PATTERN_TYPES vacío el bot no lo busca ni Cortex lo ve

    def __init__(self, settings=None) -> None:
        super().__init__(settings)
        get = (lambda key, default: default) if settings is None else settings.get
        self.tf = parse_timeframe(str(get("DOBLE_BARRIDO_TF", DEFAULT_TF)))
        self.entry = str(get("DOBLE_BARRIDO_ENTRY", DEFAULT_ENTRY)).strip().lower()
        if self.entry not in ENTRIES:
            raise ValueError(f"PATTERN_DOBLE_BARRIDO_ENTRY={self.entry!r} debe ser {', '.join(ENTRIES)}.")
        self.stop_fib = float(get("DOBLE_BARRIDO_STOP_FIB", DEFAULT_STOP_FIB))
        if not 0 < self.stop_fib <= 1:
            raise ValueError(f"PATTERN_DOBLE_BARRIDO_STOP_FIB={self.stop_fib:g} debe estar entre 0 (sin incluir) y 1.")

    def timeframe(self) -> str:
        return self.tf

    def detect(self, ctx: PatternContext) -> list[PatternHit]:
        return analyze(ctx, self.stop_fib, self.entry)[0]

    def figures(self, ctx: PatternContext) -> list[Figure]:
        return analyze(ctx, self.stop_fib, self.entry)[1]


def _earlier(ctx: PatternContext):
    """Las TBR de Asia y London que preceden a esta NY Open (las últimas cerradas antes de que empezara), o None si falta alguna."""
    own = next((p for p in ctx.peers if p.key == ctx.tbr.key and p.day == ctx.tbr.day), None)
    start = own.start_ts if own is not None else (int(ctx.ts[ctx.start_bar]) if 0 <= ctx.start_bar < len(ctx.ts) else None)
    if start is None:
        return None, None
    found = []
    for key in EARLIER:
        options = [p for p in ctx.peers if p.key == key and p.close_ts <= start and start - p.close_ts <= MAX_GAP]
        if not options:
            return None, None
        found.append(max(options, key=lambda p: p.close_ts))
    return found, start


def analyze(ctx: PatternContext, stop_fib: float = DEFAULT_STOP_FIB, entry: str = DEFAULT_ENTRY) -> tuple[list[PatternHit], list[Figure]]:
    if ctx.tbr.key != NY_KEY or not ctx.peers or len(ctx.ts) == 0:
        return [], []
    earlier, start_ts = _earlier(ctx)
    if earlier is None:
        return [], []
    end, closed = ctx.last_bar, ctx.window_closed
    if ctx.day_end:                                                       # se busca hasta el cierre del día de trading
        limit = day_close(start_ts, ctx.ahead, ctx.day_end)
        end = min(end, int(np.searchsorted(ctx.ts, limit, "left")) - 1)
        closed = closed or int(ctx.ts[-1]) + ctx.tf_minutes * 60 >= limit
    begin = min(int(np.searchsorted(ctx.ts, max(p.close_ts for p in earlier), "left")), ctx.start_bar)   # las tomas pueden ser antes de NY
    if end <= ctx.start_bar:
        return [], []
    hits, figures, trades = [], [], []
    for up in (True, False):
        found, figs = _side(ctx, earlier, up, begin, end, closed, stop_fib, entry)
        if found and found[0].status == DETECTED:
            trades.append((found, figs))
        else:
            hits += found
            figures += figs
    if trades:                                                            # un solo trade al día: el de la primera entrada
        found, figs = min(trades, key=lambda t: t[0][0].x)
        hits += found
        figures += figs
    return hits, figures


def _side(ctx: PatternContext, earlier, up: bool, begin: int, end: int, closed: bool, stop_fib: float, entry_mode: str) -> tuple[list[PatternHit], list[Figure]]:
    ts, tf_sec = ctx.ts, ctx.tf_minutes * 60
    sign = 1 if up else -1
    # espejo: el alcista se calcula con los precios cambiados de signo, así la lógica es una sola
    H, L, C = (ctx.high, ctx.low, ctx.close) if up else (-ctx.low, -ctx.high, -ctx.close)
    highs = [p.high if up else -p.low for p in earlier]                   # los dos niveles barridos
    lows = [p.low if up else -p.high for p in earlier]
    top, lower = max(highs), min(highs)                                   # el más extremo y el menos extremo de los dos niveles
    level = {"extremo": top, "asia": highs[0], "primero": lower}[entry_mode]   # el que se retestea (0 del fibonacci del stop)
    target = min(lows)                                                    # el Low más bajo entre Asia y London
    side = "High" if up else "Low"
    direction = "short" if up else "long"
    beyond = "sobre" if up else "bajo"
    which = {"asia": "de Asia", "extremo": f"más {'alto' if up else 'bajo'}", "primero": "menos extremo"}[entry_mode]
    start = ctx.start_bar                                                 # inicio de NY Open: la entrada no puede ser antes

    def hit(status, x, price, detail, levels=None):
        return PatternHit(KEY, TITLE, direction, int(x), float(price), detail, levels or {}, int(ts[x]) if 0 <= x < len(ts) else 0, status)

    # 1) cierre con cuerpo sobre el más alto de los dos niveles (con él ya ha cerrado sobre el otro). Debe ser un cruce: si la vela
    #    anterior ya había cerrado al otro lado, el precio no barre los niveles, ya estaba más allá
    take_end = min(end, ctx.first_bar - 1)                                # la toma es de NY Open: hasta que cierra su TBR
    crossed = [t for t in (begin + int(i) for i in np.flatnonzero(C[begin:take_end + 1] > top)) if t > 0 and C[t - 1] <= top]
    if not crossed:
        return [], []
    both = crossed[0]
    # 3) vuelve por debajo de los dos niveles (basta la mecha); 2) swing: el máximo absoluto del barrido hasta ese momento; 4) retesteo
    #    del nivel (basta la mecha: el rango de la vela lo atraviesa), desde NY Open. Si antes de entrar el precio supera ese swing, el
    #    barrido sigue en marcha y se reinicia desde ahí (pasado el cierre de la TBR de NY Open, el setup se invalida)
    while True:
        dips = np.flatnonzero(L[both + 1:end + 1] < lower)
        if not dips.size:
            return [], []
        dip = both + 1 + int(dips[0])
        swing = both + int(np.argmax(H[both:dip + 1]))
        swing_price = sign * float(H[swing])
        stop = sign * (level + stop_fib * (float(H[swing]) - level))    # el 0,618 entre el nivel (0) y el swing (1)
        entry = restart = None
        for t in range(dip + 1, end + 1):
            if t >= start and L[t] <= level <= H[t]:
                entry = t
                break
            if H[t] > H[swing]:
                restart = t
                break
        if entry is not None or restart is None:
            break
        if restart > take_end:
            return [hit(INVALIDATED, restart, swing_price,
                        f"cierre con cuerpo {beyond} el {side} de Asia y London en {_when(ctx, both)}; el precio superó el swing "
                        f"({swing_price:.5g}) en {_when(ctx, restart)} sin haber entrado y ya pasó NY Open: patrón invalidado")], []
        both = restart
    price, goal = sign * level, sign * target
    levels = {"stop": stop, "target": goal}
    label = f"{ctx.tbr.zone} {'▼' if up else '▲'} DB"
    if entry is not None:
        detail = (f"cierre con cuerpo {beyond} el {side} de Asia y London en {_when(ctx, both)}, swing en {_when(ctx, swing)} ({swing_price:.5g}), "
                  f"precio por debajo de los dos niveles en {_when(ctx, dip)}; retesteo del {side} {which} "
                  f"({price:.5g}) en {_when(ctx, entry)}. Entrada en el nivel, stop en el {stop_fib:g} del fibonacci hasta el swing ({stop:.5g}) y objetivo en el "
                  f"{'Low más bajo' if up else 'High más alto'} de Asia y London ({goal:.5g})")
        return [hit(DETECTED, entry, price, detail, levels)], \
            [position_figure(ctx, KEY, ctx.tbr.zone, direction, entry, price, stop, goal, label)]
    if closed:                                                            # setup formado cuyo plazo se corta por tiempo: Cortex lo anota NO GO «T»
        x = min(max(end, 0), len(ts) - 1)
        return [hit(EXPIRED, x, price, f"cierre con cuerpo {beyond} el {side} de Asia y London en {_when(ctx, both)} y precio por debajo de los "
                                       f"dos niveles en {_when(ctx, dip)}, pero sin retesteo antes del cierre del día", levels)], []
    return [], []
