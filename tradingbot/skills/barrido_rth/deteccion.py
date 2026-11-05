"""Detección del setup «Barrido del RTH» (estrategia del perfil `barrido_nyam`, modelo Greenbird): funciones puras, sin depender de otra skill.

Es una HIPÓTESIS SIN VALIDAR: solo simula, como todo el bot con SETUP_SEND_ORDERS=false.

Reglas (velas de `BARRIDO_RTH_TF`, M5 al inicio):

1. El RTH (TBR 09:00-10:00 NY) tiene que haber terminado: solo se busca desde su cierre.
2. Rotura: la primera vela, desde `BARRIDO_RTH_START` (10:00 NY), que CIERRA fuera del rango (una mecha sola no cuenta). Debe abrir antes de
   `BARRIDO_RTH_END` (11:00 NY): una primera rotura posterior no vale. Solo cuenta la primera del día.
3. Swing: el extremo (máximo en un corto, mínimo en un largo) de todo el tramo fuera del rango, desde la rotura hasta la vela de entrada.
   Stop: fijo, a `BARRIDO_RTH_STOP_POINTS` (30) puntos de la entrada si con eso queda cubierto el swing; si no, el swing más
   `BARRIDO_RTH_STOP_BUFFER` (5) puntos (por encima en un corto, por debajo en un largo).
   Breakeven (`BARRIDO_RTH_BE`): cuando el precio toca el Low del TBR NY Open (10:00 en adelante) que había hasta la entrada (el High en un
   largo), el stop pasa a la entrada. Sin él, la posición cierra solo en el objetivo 1 o en el stop.
4. Entrada: la primera vela POSTERIOR a la rotura que CIERRA de nuevo dentro del rango, a mercado a su cierre. Debe abrir antes de
   `BARRIDO_RTH_ENTRY_END` (12:00 NY, fin de NY Open). Si antes de volver el precio rompe también el otro lado, no hay setup.
5. Romper por arriba da un corto y romper por abajo, un largo.

Solo índices USA (NAS100, SP500, DJ30...), no Forex. Objetivo 1: el lado contrario del RTH (el Low en un corto, el High en un largo).
Objetivo 2: el nivel más cercano más allá del 1 entre el Low de Asia/London (el menos exigente) y el 50 % del NDOG/NWOG. El simulador de
Setup opera con el objetivo 1; el 2 se marca en el gráfico.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from types import SimpleNamespace

import numpy as np

from ...timeframes import parse_timeframe
from .._comun.contratos import DETECTED, INVALIDATED, ActiveTbr, Figure, PatternHit
from .._comun.gaps import opening_gaps
from ..setup.positions import resolve         # la misma regla con la que Setup cierra la posición simulada

KEY = "barrido_rth"
TITLE = "Barrido del RTH"
DEFAULT_TF = "5m"
DEFAULT_START = "10:00"          # hora de NY desde la que cuenta una rotura
DEFAULT_END = "11:00"            # hora de NY antes de la que debe abrir la vela que rompe el RTH
DEFAULT_ENTRY_END = "12:00"      # hora de NY antes de la que debe abrir la vela de entrada (fin de NY Open)
DEFAULT_STOP_POINTS = 30.0       # stop fijo, en puntos del precio, si cubre el swing
DEFAULT_STOP_BUFFER = 5.0        # si el swing queda más lejos, el stop es el swing más estos puntos
INDICES_USA = ("NAS100", "SP500", "DJ30", "US30", "US100", "US500", "USTEC", "US2000", "SPX500", "NDX100")
MAX_HOLD_SECONDS = 24 * 3600     # como tope, una posición dura 24 h (igual que el resto de órdenes)


def minutos(text: str, name: str) -> int:
    try:
        h, m = (int(x) for x in str(text).strip().split(":"))
        assert 0 <= h < 24 and 0 <= m < 60
    except (ValueError, AssertionError):
        raise ValueError(f"BARRIDO_RTH_{name}={text!r}: usa el formato HH:MM.") from None
    return h * 60 + m


@dataclass(frozen=True)
class Ajustes:
    """Ajustes de la skill (bloque BARRIDO_RTH de tradingbot.env, ya sin prefijo)."""
    tf: str = DEFAULT_TF
    start: int = minutos(DEFAULT_START, "START")
    end: int = minutos(DEFAULT_END, "END")
    entry_end: int = minutos(DEFAULT_ENTRY_END, "ENTRY_END")
    stop_points: float = DEFAULT_STOP_POINTS
    stop_buffer: float = DEFAULT_STOP_BUFFER
    be: bool = True              # breakeven al tomar el Low (High) del TBR NY Open

    @classmethod
    def desde(cls, settings) -> "Ajustes":
        get = (lambda key, default: default) if settings is None else settings.get
        tf = str(get("TF", DEFAULT_TF))
        parse_timeframe(tf)                                                   # valida el timeframe
        try:
            points, buffer = float(get("STOP_POINTS", DEFAULT_STOP_POINTS)), float(get("STOP_BUFFER", DEFAULT_STOP_BUFFER))
        except ValueError:
            raise ValueError("BARRIDO_RTH_STOP_POINTS y BARRIDO_RTH_STOP_BUFFER deben ser números.") from None
        if points <= 0 or buffer < 0:
            raise ValueError("BARRIDO_RTH_STOP_POINTS debe ser mayor que 0 y BARRIDO_RTH_STOP_BUFFER no puede ser negativo.")
        be = str(get("BE", "true")).strip().lower() in ("1", "true", "yes", "si", "sí", "on")
        a = cls(tf, minutos(get("START", DEFAULT_START), "START"), minutos(get("END", DEFAULT_END), "END"),
                minutos(get("ENTRY_END", DEFAULT_ENTRY_END), "ENTRY_END"), points, buffer, be)
        if a.end <= a.start:
            raise ValueError(f"BARRIDO_RTH_END={a.end // 60:02d}:{a.end % 60:02d} debe ser posterior a START.")
        if a.entry_end < a.end:
            raise ValueError(f"BARRIDO_RTH_ENTRY_END={a.entry_end // 60:02d}:{a.entry_end % 60:02d} no puede ser anterior a END.")
        return a


@dataclass(frozen=True)
class Zona:
    """Una TBR cerrada (RTH, Asia o London) con su cierre en hora del servidor."""
    key: str
    nombre: str
    day: date
    high: float
    low: float
    close_ts: int


@dataclass(frozen=True)
class Contexto:
    """Todo lo que necesita el análisis de un día: velas, RTH, Asia/London previas y la TBR (RTH) con la que se publica."""
    symbol: str
    tf_minutes: int
    ts: np.ndarray
    open: np.ndarray
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray
    ahead: int                   # segundos que el servidor va por delante de Nueva York
    tbr: ActiveTbr               # el RTH del día, tal como lo ven Cortex y la ventana
    rth: Zona
    previas: tuple[Zona, ...] = ()
    last_bar: int = 0            # última vela cerrada
    day_end: int = 0             # fin del día de trading del mercado (minutos desde medianoche de NY): ahí cierran los trades
    be_r: float | None = None    # R a favor para pasar el stop a la entrada (como Setup)


def es_indice_usa(symbol: str) -> bool:
    name = symbol.strip().lower()
    return any(name.startswith(p.lower()) for p in INDICES_USA)


def hora_ny(ctx: Contexto, i: int) -> str:
    return datetime.fromtimestamp(int(ctx.ts[i]) - ctx.ahead, tz=timezone.utc).strftime("%H:%M NY")


def cierre_del_dia(ts: int, ahead: int, end_minutes: int) -> int:
    """Hora (servidor) del fin del día de trading (`end_minutes` desde medianoche de NY) siguiente a la hora `ts` (servidor)."""
    ny = int(ts) - ahead
    end = (ny // 86400) * 86400 + end_minutes * 60
    while end <= ny:
        end += 86400
    return end + ahead


def _figura_posicion(ctx: Contexto, direction: str, t: int, entry: float, stop: float, target: float, label: str,
                     be_price: float | None = None) -> Figure:
    """Posición para el gráfico: de la vela de la entrada a la del cierre (o a la última vela si sigue abierta)."""
    close = int(ctx.ts[t]) + MAX_HOLD_SECONDS
    if ctx.day_end:
        close = min(close, cierre_del_dia(int(ctx.ts[t]), ctx.ahead, ctx.day_end))
    limit = int(np.searchsorted(ctx.ts, close, "left")) - 1
    tf_sec = ctx.tf_minutes * 60
    kind, idx = None, min(limit, len(ctx.ts) - 1)
    if limit >= t:
        order = SimpleNamespace(direction=direction, pattern_key=KEY, price=entry, stop=stop, target=target, entry_ts=int(ctx.ts[t]), close_ts=close, be_price=be_price)
        end = limit + 1
        done = resolve(order, ctx.ts[:end], ctx.high[:end], ctx.low[:end], ctx.close[:end], ctx.be_r, tf_sec)
        if done is not None:
            kind, idx = done.result, int(np.searchsorted(ctx.ts, done.exit_ts, "left"))
    state = {"objetivo": "objetivo", "stop": "stop", "breakeven": "be", "tiempo": "tiempo"}.get(
        kind, "abierta" if limit >= len(ctx.ts) - 1 else "tiempo")
    return Figure("pos", KEY, ctx.tbr.zone, direction, int(ctx.ts[t]), int(ctx.ts[idx]) + tf_sec,
                  {"entrada": float(entry), "stop": float(stop), "objetivo": float(target)}, state, label, ctx.tbr.day.isoformat())


def _objetivo2(ctx: Contexto, up: bool, first_target: float, session_ts: int) -> tuple[float, str] | None:
    """Objetivo 2: el nivel más cercano, más allá del objetivo 1, entre los Low de Asia y London (los High en un largo) y el 50 % del
    NDOG y del NWOG. Es «lo que esté antes» y, entre Asia y London, el menos exigente. Devuelve (precio, nombre) o None."""
    found = [(z.low if up else z.high, f"{'Low' if up else 'High'} de {z.nombre}") for z in ctx.previas]
    for kind, gap in opening_gaps(ctx.ts, ctx.open, ctx.close, session_ts, ctx.ahead).items():
        if gap is not None:
            found.append((gap.mid, f"50 % del {kind}"))
    beyond = [f for f in found if (f[0] < first_target if up else f[0] > first_target)]
    if not beyond:
        return None
    return max(beyond) if up else min(beyond)                                 # corto: el más alto de los que están por debajo; largo: el más bajo


def analizar(ctx: Contexto, a: Ajustes = Ajustes()) -> tuple[list[PatternHit], list[Figure]]:
    """Resultados del día del RTH de `ctx` (cero o uno) y su dibujo."""
    if len(ctx.ts) == 0 or not es_indice_usa(ctx.symbol):
        return [], []                                                         # de momento solo índices USA, no Forex
    rth = ctx.rth
    midnight = (rth.day.toordinal() - date(1970, 1, 1).toordinal()) * 86400 + ctx.ahead    # medianoche de NY, en hora del servidor
    from_ts = max(midnight + a.start * 60, rth.close_ts)                      # el RTH debe haber terminado
    first = int(np.searchsorted(ctx.ts, from_ts, "left"))
    last_break = int(np.searchsorted(ctx.ts, midnight + a.end * 60, "left")) - 1       # última vela que puede iniciar la rotura
    last_entry = min(ctx.last_bar, int(np.searchsorted(ctx.ts, midnight + a.entry_end * 60, "left")) - 1)    # y la de la entrada
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
    ts_hit = int(ctx.ts[t]) + ctx.tf_minutes * 60                             # la posición vive desde la vela siguiente
    extreme = float(np.max(ctx.high[sweep:t + 1]) if up else np.min(ctx.low[sweep:t + 1]))    # el swing: extremo de todo el tramo fuera del RTH
    other = bool(ctx.low[sweep:t + 1].min() < rth.low) if up else bool(ctx.high[sweep:t + 1].max() > rth.high)
    close = float(ctx.close[t])
    if other:                                                                 # barrió también el lado contrario antes de volver
        return [PatternHit(KEY, TITLE, direction, int(t), close, "el precio rompe también el otro lado del RTH antes de volver dentro: "
                           "sin setup hoy", {}, ts_hit, INVALIDATED)], []
    sign = 1.0 if up else -1.0                                                # corto: el stop va por encima de la entrada; largo: por debajo
    covers = sign * (extreme - close) <= a.stop_points                        # ¿el stop fijo cubre el swing?
    stop = close + sign * a.stop_points if covers else extreme + sign * a.stop_buffer
    goal = rth.low if up else rth.high
    detail = (f"primera rotura del {side} del RTH ({rth.high if up else rth.low:.5g}) en {hora_ny(ctx, sweep)}, con swing en {extreme:.5g}; la primera "
              f"vela que cierra de nuevo dentro del rango es la de {hora_ny(ctx, t)} ({close:.5g}). Entrada a mercado a ese cierre, stop en "
              f"{stop:.5g} ({'fijo a ' + format(a.stop_points, 'g') + ' puntos, cubre el swing' if covers else 'swing + ' + format(a.stop_buffer, 'g')}) y objetivo 1 en el {'Low' if up else 'High'} del RTH ({goal:.5g})")
    levels = {"stop": stop, "target": goal}
    if a.be:                                                                  # breakeven al tomar el Low (High) del TBR NY Open que había hasta la entrada
        ny_open = int(np.searchsorted(ctx.ts, midnight + a.start * 60, "left"))
        levels["be"] = float(np.min(ctx.low[ny_open:t + 1]) if up else np.max(ctx.high[ny_open:t + 1]))
    second = _objetivo2(ctx, up, goal, midnight + a.start * 60)
    if second is not None:
        levels["target2"] = second[0]
        detail += f"; objetivo 2 en {second[1]} ({second[0]:.5g})"
    figures = []
    if t + 1 < len(ctx.ts):
        fig = _figura_posicion(ctx, direction, t + 1, close, stop, goal, f"RTH {'▼' if up else '▲'} barrido", levels.get("be"))
        extra = {"entrada_ts": float(ctx.ts[t])}                              # la vela cuyo cierre es la entrada: el gráfico la marca ahí
        if second is not None:
            extra["objetivo2"] = second[0]
        figures = [replace(fig, levels={**fig.levels, **extra})]
    return [PatternHit(KEY, TITLE, direction, int(t), close, detail, levels, ts_hit, DETECTED)], figures
