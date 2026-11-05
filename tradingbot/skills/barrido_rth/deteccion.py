"""Patrón «Barrido del RTH»: NY Open barre un lado del rango RTH (09:00-10:00) y cierra de vuelta dentro de él.

Es la estrategia del perfil `barrido_nyam` (MT5_<PERFIL>_STRATEGY=barrido_nyam). Es una HIPÓTESIS SIN VALIDAR: `default_on = False`
(solo la busca la skill barrido_rth del perfil) y solo simula, como todo el bot con SETUP_SEND_ORDERS=false.

Reglas (velas de `BARRIDO_RTH_TF`, M5 al inicio):

1. El RTH tiene que haber terminado: solo se busca desde el cierre de la TBR RTH.
2. Solo vale el PRIMER barrido del día: la primera vela, desde `BARRIDO_RTH_START` (10:00 NY), que supera el High o el Low del
   RTH. Si esa vela barre los dos lados a la vez, no hay setup.
3. La entrada es la primera vela que CIERRA de nuevo dentro del rango (por debajo del High barrido, o por encima del Low barrido):
   la propia vela de barrido si ya cierra dentro, o la primera posterior que lo haga. Debe haber abierto antes de
   `BARRIDO_RTH_END` (10:30 NY); si no vuelve a tiempo, o barre también el otro lado antes de volver, no hay setup. Un
   primer barrido posterior a la ventana tampoco cuenta.
4. Barrer el High da un corto y barrer el Low, un largo. Entrada a mercado al cierre de esa vela.

Solo índices USA (NAS100, SP500, DJ30...), no Forex. Asia y London se pintan en el perfil. Objetivo 1: el lado contrario del RTH (el Low en un corto, el High en un largo);
Objetivo 2: el nivel más cercano más allá del 1 entre el Low
de Asia/London (el menos exigente) y el 50 % del NDOG/NWOG. Stop: el extremo del barrido. El simulador de Setup opera con el objetivo 1;
el 2 se marca en el gráfico.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import date

import numpy as np

from ...timeframes import parse_timeframe
from ..levels.daylevels import DEFAULT_US_INDICES, is_us_index
from ..levels.gaps import opening_gaps
from ..pattern.continuacion import _when
from ..pattern.patterns import DETECTED, INVALIDATED, Figure, Pattern, PatternContext, PatternHit, register_pattern
from ..pattern.trade import position_figure

KEY = "barrido_rth"
TITLE = "Barrido del RTH"
DEFAULT_TF = "5m"
DEFAULT_START = "10:00"          # hora de NY desde la que cuenta un barrido
DEFAULT_END = "10:30"            # hora de NY antes de la que debe abrir la vela de barrido
NY_KEY = "NY_AM"                 # TBR en cuya hora se busca
RTH_KEY = "PRE_NY"               # el rango que se barre


def _minutes(text: str, name: str) -> int:
    try:
        h, m = (int(x) for x in str(text).strip().split(":"))
        assert 0 <= h < 24 and 0 <= m < 60
    except (ValueError, AssertionError):
        raise ValueError(f"BARRIDO_RTH_{name}={text!r}: usa el formato HH:MM.") from None
    return h * 60 + m


@register_pattern(KEY)
class BarridoRht(Pattern):
    title = TITLE
    default_on = False                     # hipótesis por validar: solo el perfil barrido_nyam (o PATTERN_TYPES=barrido_rth) la busca

    def __init__(self, settings=None) -> None:
        super().__init__(settings)
        get = (lambda key, default: default) if settings is None else settings.get
        self.tf = parse_timeframe(str(get("TF", DEFAULT_TF)))                 # bloque BARRIDO_RTH de tradingbot.env (sin prefijo)
        self.start = _minutes(get("START", DEFAULT_START), "START")
        self.end = _minutes(get("END", DEFAULT_END), "END")
        if self.end <= self.start:
            raise ValueError(f"BARRIDO_RTH_END={self.end // 60:02d}:{self.end % 60:02d} debe ser posterior a START.")

    def timeframe(self) -> str:
        return self.tf

    def detect(self, ctx: PatternContext) -> list[PatternHit]:
        return analyze(ctx, self.start, self.end)[0]

    def figures(self, ctx: PatternContext) -> list[Figure]:
        return analyze(ctx, self.start, self.end)[1]


def _rth(ctx: PatternContext):
    """El RTH de este día, ya cerrado, o None."""
    own = next((p for p in ctx.peers if p.key == ctx.tbr.key and p.day == ctx.tbr.day), None)
    if own is None:
        return None
    options = [p for p in ctx.peers if p.key == RTH_KEY and p.day == ctx.tbr.day and p.close_ts <= own.start_ts]
    return max(options, key=lambda p: p.close_ts) if options else None


def _target2(ctx: PatternContext, up: bool, first_target: float, session_ts: int) -> tuple[float, str] | None:
    """Objetivo 2: el nivel más cercano, más allá del objetivo 1, entre los Low de Asia y London (los High en un largo) y el 50 % del
    NDOG y del NWOG. Es «lo que esté antes» y, entre Asia y London, el menos exigente. Devuelve (precio, nombre) o None."""
    found = []
    for key in ("ASIA", "LONDON"):                                            # las últimas cerradas antes de NY Open
        tbr = max((p for p in ctx.peers if p.key == key and p.close_ts <= session_ts), key=lambda p: p.close_ts, default=None)
        if tbr is not None:
            found.append((tbr.low if up else tbr.high, f"{'Low' if up else 'High'} de {tbr.zone}"))
    for kind, gap in opening_gaps(ctx.ts, ctx.open, ctx.close, session_ts, ctx.ahead).items():
        if gap is not None:
            found.append((gap.mid, f"50 % del {kind}"))
    beyond = [f for f in found if (f[0] < first_target if up else f[0] > first_target)]
    if not beyond:
        return None
    return max(beyond) if up else min(beyond)                                 # corto: el más alto de los que están por debajo; largo: el más bajo


def analyze(ctx: PatternContext, start_min: int = _minutes(DEFAULT_START, "START"),
            end_min: int = _minutes(DEFAULT_END, "END")) -> tuple[list[PatternHit], list[Figure]]:
    if ctx.tbr.key != NY_KEY or not ctx.peers or len(ctx.ts) == 0 or not is_us_index(ctx.symbol, DEFAULT_US_INDICES):
        return [], []                                                         # de momento solo índices USA, no Forex
    rth = _rth(ctx)
    if rth is None:
        return [], []
    midnight = (ctx.tbr.day.toordinal() - date(1970, 1, 1).toordinal()) * 86400 + ctx.ahead    # medianoche de NY, en hora del servidor
    from_ts = max(midnight + start_min * 60, rth.close_ts)                    # el RTH debe haber terminado
    to_ts = midnight + end_min * 60
    first = int(np.searchsorted(ctx.ts, from_ts, "left"))
    last = min(ctx.last_bar, int(np.searchsorted(ctx.ts, to_ts, "left")) - 1)    # última vela que puede ser la de la entrada
    if first >= len(ctx.ts) or first > ctx.last_bar:
        return [], []
    # el primer barrido del día: la primera vela desde las 10:00 que supera un lado del RTH (aunque sea tras la ventana, entonces no vale)
    swept = np.flatnonzero((ctx.high[first:ctx.last_bar + 1] > rth.high) | (ctx.low[first:ctx.last_bar + 1] < rth.low))
    if not swept.size:
        return [], []
    sweep = first + int(swept[0])
    if sweep > last:
        return [], []                                                         # el primer barrido llegó fuera de la ventana: no hay setup
    up = bool(ctx.high[sweep] > rth.high)
    if up and ctx.low[sweep] < rth.low:
        return [PatternHit(KEY, TITLE, "short", int(sweep), float(ctx.close[sweep]), f"la vela de {_when(ctx, sweep)} barre el High y el Low "
                           f"del RTH a la vez: sin setup hoy", {}, int(ctx.ts[sweep]) + ctx.tf_minutes * 60, INVALIDATED)], []
    side, direction = ("High", "short") if up else ("Low", "long")
    # la entrada: la primera vela (la del barrido o una posterior) que cierra de nuevo dentro del rango, la del barrido incluida
    closes = ctx.close[sweep:last + 1]
    back = np.flatnonzero(closes < rth.high) if up else np.flatnonzero(closes > rth.low)
    if not back.size:
        return [], []                                                         # aún no ha vuelto (o no volvió antes de las 10:30)
    t = sweep + int(back[0])
    extreme = float(np.max(ctx.high[sweep:t + 1]) if up else np.min(ctx.low[sweep:t + 1]))    # extremo del barrido hasta la entrada
    other = bool(ctx.low[sweep:t + 1].min() < rth.low) if up else bool(ctx.high[sweep:t + 1].max() > rth.high)
    if other:                                                                 # barrió también el lado contrario antes de volver
        return [PatternHit(KEY, TITLE, direction, int(t), float(ctx.close[t]), f"el precio barre también el otro lado del RTH antes de "
                           f"volver dentro: sin setup hoy", {}, int(ctx.ts[t]) + ctx.tf_minutes * 60, INVALIDATED)], []
    close = float(ctx.close[t])
    stop = extreme
    goal = rth.low if up else rth.high
    detail = (f"primer barrido del {side} del RTH ({rth.high if up else rth.low:.5g}) en {_when(ctx, sweep)}; la primera vela que cierra de nuevo "
              f"dentro del rango es la de {_when(ctx, t)} ({close:.5g}). Entrada a mercado a ese cierre, stop en el extremo del barrido "
              f"({stop:.5g}) y objetivo 1 en el {'Low' if up else 'High'} del RTH ({goal:.5g})")
    levels = {"stop": stop, "target": goal}
    second = _target2(ctx, up, goal, midnight + start_min * 60)
    if second is not None:
        levels["target2"] = second[0]
        detail += f"; objetivo 2 en {second[1]} ({second[0]:.5g})"
    figures = []
    if t + 1 < len(ctx.ts):                                                   # la posición vive desde la vela siguiente
        fig = position_figure(ctx, KEY, ctx.tbr.zone, direction, t + 1, close, stop, goal, f"RTH {'▼' if up else '▲'} barrido")
        figures = [replace(fig, levels={**fig.levels, "objetivo2": second[0]}) if second is not None else fig]
    return [PatternHit(KEY, TITLE, direction, int(t), close, detail, levels, int(ctx.ts[t]) + ctx.tf_minutes * 60, DETECTED)], figures
