"""Patrón «Barrido del RTH»: NY Open barre un lado del rango RTH (09:00-10:00) y cierra de vuelta dentro de él.

Es la estrategia del perfil `barrido_nyam` (MT5_<PERFIL>_STRATEGY=barrido_nyam). Es una HIPÓTESIS SIN VALIDAR: `default_on = False`
(solo la busca la skill barrido_rth del perfil) y solo simula, como todo el bot con SETUP_SEND_ORDERS=false.

Reglas (velas de `BARRIDO_RTH_TF`, M5 al inicio):

1. El RTH tiene que haber terminado: solo se busca desde el cierre de la TBR RTH.
2. Rotura: la primera vela, desde `BARRIDO_RTH_START` (10:00 NY), que CIERRA fuera del rango (una mecha sola no cuenta). Debe abrir antes de
   `BARRIDO_RTH_END` (11:00 NY): una primera rotura posterior no vale. Solo cuenta la primera del día.
3. Swing: el extremo (máximo en un corto, mínimo en un largo) de todo el tramo fuera del rango, desde la rotura hasta la vela de entrada.
4. Entrada: la primera vela POSTERIOR a la rotura que CIERRA de nuevo dentro del rango, a mercado a su cierre. Debe abrir antes de
   `BARRIDO_RTH_ENTRY_END` (12:00 NY, fin de NY Open). Si antes de volver el precio rompe también el otro lado, no hay setup.
5. Romper por arriba da un corto y romper por abajo, un largo. Stop en el swing.

Solo índices USA (NAS100, SP500, DJ30...), no Forex. Asia y London se pintan en el perfil. Objetivo 1: el lado contrario del RTH (el Low en un corto, el High en un largo);
Objetivo 2: el nivel más cercano más allá del 1 entre el Low
de Asia/London (el menos exigente) y el 50 % del NDOG/NWOG. El simulador de Setup opera con el objetivo 1;
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
DEFAULT_END = "11:00"            # hora de NY antes de la que debe abrir la vela que rompe el RTH
DEFAULT_ENTRY_END = "12:00"      # hora de NY antes de la que debe abrir la vela de entrada (fin de NY Open)
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
class BarridoRth(Pattern):
    title = TITLE
    default_on = False                     # hipótesis por validar: solo el perfil barrido_nyam (o PATTERN_TYPES=barrido_rth) la busca

    def __init__(self, settings=None) -> None:
        super().__init__(settings)
        get = (lambda key, default: default) if settings is None else settings.get
        self.tf = parse_timeframe(str(get("TF", DEFAULT_TF)))                 # bloque BARRIDO_RTH de tradingbot.env (sin prefijo)
        self.start = _minutes(get("START", DEFAULT_START), "START")
        self.end = _minutes(get("END", DEFAULT_END), "END")
        self.entry_end = _minutes(get("ENTRY_END", DEFAULT_ENTRY_END), "ENTRY_END")
        if self.end <= self.start:
            raise ValueError(f"BARRIDO_RTH_END={self.end // 60:02d}:{self.end % 60:02d} debe ser posterior a START.")
        if self.entry_end < self.end:
            raise ValueError(f"BARRIDO_RTH_ENTRY_END={self.entry_end // 60:02d}:{self.entry_end % 60:02d} no puede ser anterior a END.")

    def timeframe(self) -> str:
        return self.tf

    def detect(self, ctx: PatternContext) -> list[PatternHit]:
        return analyze(ctx, self.start, self.end, self.entry_end)[0]

    def figures(self, ctx: PatternContext) -> list[Figure]:
        return analyze(ctx, self.start, self.end, self.entry_end)[1]


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


def analyze(ctx: PatternContext, start_min: int = _minutes(DEFAULT_START, "START"), end_min: int = _minutes(DEFAULT_END, "END"),
            entry_end_min: int = _minutes(DEFAULT_ENTRY_END, "ENTRY_END")) -> tuple[list[PatternHit], list[Figure]]:
    if ctx.tbr.key != NY_KEY or not ctx.peers or len(ctx.ts) == 0 or not is_us_index(ctx.symbol, DEFAULT_US_INDICES):
        return [], []                                                         # de momento solo índices USA, no Forex
    rth = _rth(ctx)
    if rth is None:
        return [], []
    midnight = (ctx.tbr.day.toordinal() - date(1970, 1, 1).toordinal()) * 86400 + ctx.ahead    # medianoche de NY, en hora del servidor
    from_ts = max(midnight + start_min * 60, rth.close_ts)                    # el RTH debe haber terminado
    first = int(np.searchsorted(ctx.ts, from_ts, "left"))
    last_break = int(np.searchsorted(ctx.ts, midnight + end_min * 60, "left")) - 1       # última vela que puede iniciar la rotura
    last_entry = min(ctx.last_bar, int(np.searchsorted(ctx.ts, midnight + entry_end_min * 60, "left")) - 1)   # y la de la entrada
    if first >= len(ctx.ts) or first > ctx.last_bar:
        return [], []
    # la rotura: la primera vela desde las 10:00 que CIERRA fuera del rango (una mecha sola no cuenta); si llega tras la ventana, no vale
    outside = np.flatnonzero((ctx.close[first:ctx.last_bar + 1] > rth.high) | (ctx.close[first:ctx.last_bar + 1] < rth.low))
    if not outside.size:
        return [], []
    sweep = first + int(outside[0])
    if sweep > last_break:
        return [], []                                                         # la primera rotura llegó fuera de la ventana: no hay setup
    up = bool(ctx.close[sweep] > rth.high)
    side, direction = ("High", "short") if up else ("Low", "long")
    # la entrada: la primera vela POSTERIOR a la rotura que cierra de nuevo dentro del rango, una vez creado el swing
    closes = ctx.close[sweep + 1:last_entry + 1]
    back = np.flatnonzero(closes < rth.high) if up else np.flatnonzero(closes > rth.low)
    if not back.size:
        return [], []                                                         # aún no ha vuelto (o no volvió antes de la hora límite)
    t = sweep + 1 + int(back[0])
    extreme = float(np.max(ctx.high[sweep:t + 1]) if up else np.min(ctx.low[sweep:t + 1]))    # el swing: extremo de todo el tramo fuera del RTH, hasta la entrada
    other = bool(ctx.low[sweep:t + 1].min() < rth.low) if up else bool(ctx.high[sweep:t + 1].max() > rth.high)
    if other:                                                                 # barrió también el lado contrario antes de volver
        return [PatternHit(KEY, TITLE, direction, int(t), float(ctx.close[t]), f"el precio barre también el otro lado del RTH antes de "
                           f"volver dentro: sin setup hoy", {}, int(ctx.ts[t]) + ctx.tf_minutes * 60, INVALIDATED)], []
    close = float(ctx.close[t])
    stop = extreme
    goal = rth.low if up else rth.high
    detail = (f"primera rotura del {side} del RTH ({rth.high if up else rth.low:.5g}) en {_when(ctx, sweep)}, con swing en {stop:.5g}; la primera "
              f"vela que cierra de nuevo dentro del rango es la de {_when(ctx, t)} ({close:.5g}). Entrada a mercado a ese cierre, stop en el swing "
              f"({stop:.5g}) y objetivo 1 en el {'Low' if up else 'High'} del RTH ({goal:.5g})")
    levels = {"stop": stop, "target": goal}
    second = _target2(ctx, up, goal, midnight + start_min * 60)
    if second is not None:
        levels["target2"] = second[0]
        detail += f"; objetivo 2 en {second[1]} ({second[0]:.5g})"
    figures = []
    if t + 1 < len(ctx.ts):                                                   # la posición vive desde la vela siguiente
        fig = position_figure(ctx, KEY, ctx.tbr.zone, direction, t + 1, close, stop, goal, f"RTH {'▼' if up else '▲'} barrido")
        extra = {"entrada_ts": float(ctx.ts[t])}                              # la vela cuyo cierre es la entrada: el gráfico la marca ahí
        if second is not None:
            extra["objetivo2"] = second[0]
        figures = [replace(fig, levels={**fig.levels, **extra})]
    return [PatternHit(KEY, TITLE, direction, int(t), close, detail, levels, int(ctx.ts[t]) + ctx.tf_minutes * 60, DETECTED)], figures
