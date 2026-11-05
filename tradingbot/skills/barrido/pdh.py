"""Detección del setup «Barrido del PDH/PDL en Asia» (modelo Greenbird, perfil `barrido_nyam`): funciones puras, sin depender de otra skill.

Es una HIPÓTESIS SIN VALIDAR: solo simula, como todo el bot con SETUP_SEND_ORDERS=false.

Reglas (velas de `BARRIDO_PDH_TF`, M5 al inicio):

1. PDH / PDL: máximo y mínimo del día de trading anterior (en los índices USA el día va de las 18:00 a las 18:00 de NY, LEVELS_INDEX_DAY_START).
2. Nivel fresco: desde las 18:00, que empieza el día nuevo, hasta las 20:00 el precio no ha tocado el nivel. Si ya lo tocó, no hay setup.
3. Barrido: entre `BARRIDO_PDH_START` (20:00 NY) y `BARRIDO_PDH_END` (21:00 NY) una vela supera el nivel: es el alto (bajo) del rango de Asia
   que se está formando. Con ello el nivel queda mitigado: no se vuelve a usar.
4. Entrada: la primera vela, desde la del barrido (inclusive), que CIERRA por debajo del PDH (por encima del PDL), a mercado a su cierre. La
   vela de 5 min debe cerrar a las 21:00 como tarde. Si no cierra de vuelta dentro de la ventana, no hay setup.
5. Stop: fijo, a `BARRIDO_PDH_STOP_POINTS` (30) puntos de la entrada si con eso queda cubierto el swing (el extremo desde el barrido hasta la
   entrada); si no, el swing más `BARRIDO_PDH_STOP_BUFFER` (5) puntos.
6. Objetivo: el Low (High) del rango de Asia. Como ese rango no está formado a la hora de la entrada, la señal se da cuando Asia cierra
   (00:00 NY) con la entrada ya fijada en la vela del barrido; la posición se simula desde esa vela. Sin breakeven.
7. Una sola operación por noche: la del primer lado (PDH o PDL) cuya vela de entrada cierra antes.

Solo índices USA (NAS100, SP500, DJ30...), no Forex.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from types import SimpleNamespace

import numpy as np

from ...timeframes import parse_timeframe
from .._comun.contratos import DETECTED, ActiveTbr, Figure, PatternHit
from ..setup.positions import resolve         # la misma regla con la que Setup cierra la posición simulada

KEY = "barrido_pdh"
TITLE = "Barrido PDH/PDL"
ZONA = "ASIA"                    # la TBR cuyo rango da el objetivo
DEFAULT_TF = "5m"
DEFAULT_START = "20:00"          # hora de NY desde la que cuenta el barrido (apertura de Asia)
DEFAULT_END = "21:00"            # hora de NY antes de la que debe abrir la vela de entrada (cierra a las 21:00 como tarde)
DEFAULT_STOP_POINTS = 30.0
DEFAULT_STOP_BUFFER = 5.0
INDICES_USA = ("NAS100", "SP500", "DJ30", "US30", "US100", "US500", "USTEC", "US2000", "SPX500", "NDX100")
MAX_HOLD_SECONDS = 24 * 3600
DAY = 86400


def minutos(text: str, name: str, prefix: str = "BARRIDO_PDH") -> int:
    try:
        h, m = (int(x) for x in str(text).strip().split(":"))
        assert 0 <= h < 24 and 0 <= m < 60
    except (ValueError, AssertionError):
        raise ValueError(f"{prefix}_{name}={text!r}: usa el formato HH:MM.") from None
    return h * 60 + m


@dataclass(frozen=True)
class Ajustes:
    """Ajustes de la skill (bloque BARRIDO_PDH de tradingbot.env, ya sin prefijo)."""
    tf: str = DEFAULT_TF
    start: int = minutos(DEFAULT_START, "START")
    end: int = minutos(DEFAULT_END, "END")
    stop_points: float = DEFAULT_STOP_POINTS
    stop_buffer: float = DEFAULT_STOP_BUFFER

    @classmethod
    def desde(cls, settings, start: str = DEFAULT_START, end: str = DEFAULT_END, prefix: str = "BARRIDO_PDH") -> "Ajustes":
        """`start` y `end`: horas por defecto de la ventana; `prefix`: el del bloque de tradingbot.env (para los mensajes de error)."""
        get = (lambda key, default: default) if settings is None else settings.get
        tf = str(get("TF", DEFAULT_TF))
        parse_timeframe(tf)                                                   # valida el timeframe
        try:
            points, buffer = float(get("STOP_POINTS", DEFAULT_STOP_POINTS)), float(get("STOP_BUFFER", DEFAULT_STOP_BUFFER))
        except ValueError:
            raise ValueError(f"{prefix}_STOP_POINTS y {prefix}_STOP_BUFFER deben ser números.") from None
        if points <= 0 or buffer < 0:
            raise ValueError(f"{prefix}_STOP_POINTS debe ser mayor que 0 y {prefix}_STOP_BUFFER no puede ser negativo.")
        a = cls(tf, minutos(get("START", start), "START", prefix), minutos(get("END", end), "END", prefix), points, buffer)
        if a.end <= a.start:
            raise ValueError(f"{prefix}_END={a.end // 60:02d}:{a.end % 60:02d} debe ser posterior a START.")
        return a


@dataclass(frozen=True)
class Zona:
    """La TBR de Asia cerrada, con su cierre en hora del servidor."""
    nombre: str
    day: date                    # día en que empieza (las 20:00 de NY); cierra a medianoche
    high: float
    low: float
    close_ts: int


@dataclass(frozen=True)
class Contexto:
    """Todo lo que necesita el análisis de una noche: velas, rango de Asia y niveles del día anterior."""
    symbol: str
    tf_minutes: int
    ts: np.ndarray
    open: np.ndarray
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray
    ahead: int                   # segundos que el servidor va por delante de Nueva York
    tbr: ActiveTbr               # Asia, tal como la ven Cortex y la ventana
    asia: Zona
    pdh: float | None = None     # máximo y mínimo del día de trading anterior (None si no hay velas de ese día)
    pdl: float | None = None
    dia_ini: int = 0             # primera vela del día de trading en que cae la noche (las 18:00 de NY)
    last_bar: int = 0            # última vela cerrada
    day_end: int = 0             # fin del día de trading del mercado (minutos desde medianoche de NY): ahí cierran los trades
    salir_al_cierre: bool = False   # True: la posición cierra al cierre del rango (Londres, 05:00) y no al final del día de trading

    @property
    def salida(self) -> int:
        """Hora (servidor) en que cierra la posición: el cierre del rango si `salir_al_cierre`, o el fin del día de trading (0 = sin ella)."""
        return self.asia.close_ts if self.salir_al_cierre else 0

    @property
    def cierre_rango(self) -> int:
        """Cierre del rango de Asia (hora del servidor): la skill lo usa para saber si la noche es reciente."""
        return self.asia.close_ts


def es_indice_usa(symbol: str) -> bool:
    name = symbol.strip().lower()
    return any(name.startswith(p.lower()) for p in INDICES_USA)


def hora_ny(ctx: Contexto, i: int) -> str:
    return datetime.fromtimestamp(int(ctx.ts[i]) - ctx.ahead, tz=timezone.utc).strftime("%H:%M NY")


def cierre_del_dia(ts: int, ahead: int, end_minutes: int) -> int:
    """Hora (servidor) del fin del día de trading (`end_minutes` desde medianoche de NY) siguiente a la hora `ts` (servidor)."""
    ny = int(ts) - ahead
    end = (ny // DAY) * DAY + end_minutes * 60
    while end <= ny:
        end += DAY
    return end + ahead


def _figura_posicion(ctx: Contexto, direction: str, t: int, entry: float, stop: float, target: float, label: str, key: str = KEY) -> Figure:
    """Posición para el gráfico: de la vela de la entrada a la del cierre (o a la última vela si sigue abierta)."""
    close = int(ctx.ts[t]) + MAX_HOLD_SECONDS
    if ctx.day_end:
        close = min(close, cierre_del_dia(int(ctx.ts[t]), ctx.ahead, ctx.day_end))
    if ctx.salida:
        close = min(close, ctx.salida)
    limit = int(np.searchsorted(ctx.ts, close, "left")) - 1
    tf_sec = ctx.tf_minutes * 60
    kind, idx = None, min(limit, len(ctx.ts) - 1)
    if limit >= t:
        order = SimpleNamespace(direction=direction, pattern_key=key, price=entry, stop=stop, target=target, entry_ts=int(ctx.ts[t]), close_ts=close)
        end = limit + 1
        done = resolve(order, ctx.ts[:end], ctx.high[:end], ctx.low[:end], ctx.close[:end], None, tf_sec)
        if done is not None:
            kind, idx = done.result, int(np.searchsorted(ctx.ts, done.exit_ts, "left"))
    state = {"objetivo": "objetivo", "stop": "stop", "breakeven": "be", "tiempo": "tiempo"}.get(
        kind, "abierta" if limit >= len(ctx.ts) - 1 else "tiempo")
    return Figure("pos", key, ctx.tbr.zone, direction, int(ctx.ts[t]), int(ctx.ts[idx]) + tf_sec,
                  {"entrada": float(entry), "stop": float(stop), "objetivo": float(target)}, state, label, ctx.tbr.day.isoformat())


def _lado(ctx: Contexto, a: Ajustes, first: int, last: int, up: bool) -> tuple[int, int] | None:
    """(vela del barrido, vela de entrada) del PDH (up) o del PDL, o None: nivel ya tocado antes de las 20:00, sin barrido o sin cierre de vuelta."""
    level = ctx.pdh if up else ctx.pdl
    if level is None:
        return None
    before_high, before_low = ctx.high[ctx.dia_ini:first], ctx.low[ctx.dia_ini:first]
    if (before_high.size and float(before_high.max()) >= level) if up else (before_low.size and float(before_low.min()) <= level):
        return None                                                           # el nivel no está fresco: ya lo tocó el precio entre las 18:00 y las 20:00
    window = slice(first, last + 1)
    touched = np.flatnonzero(ctx.high[window] > level) if up else np.flatnonzero(ctx.low[window] < level)
    if not touched.size:
        return None                                                           # no lo barre dentro de la ventana
    sweep = first + int(touched[0])
    closes = ctx.close[sweep:last + 1]
    back = np.flatnonzero(closes < level) if up else np.flatnonzero(closes > level)
    return None if not back.size else (sweep, sweep + int(back[0]))


def analizar(ctx: Contexto, a: Ajustes = Ajustes(), key: str = KEY, title: str = TITLE, rango: str = "Asia") -> tuple[list[PatternHit], list[Figure]]:
    """Resultados de la noche de `ctx` (cero o uno) y su dibujo. `key`, `title` y `rango` (nombre de la TBR que da el objetivo) cambian en el setup de Londres."""
    if len(ctx.ts) == 0 or not es_indice_usa(ctx.symbol):
        return [], []                                                         # de momento solo índices USA, no Forex
    asia = ctx.asia
    day0 = (asia.day.toordinal() - date(1970, 1, 1).toordinal()) * DAY + ctx.ahead       # medianoche de NY de la noche, en hora del servidor
    first = int(np.searchsorted(ctx.ts, day0 + a.start * 60, "left"))
    last = min(ctx.last_bar, int(np.searchsorted(ctx.ts, day0 + a.end * 60, "left")) - 1)    # última vela que puede ser la de entrada
    if first > last or ctx.ts[first] >= day0 + a.end * 60:
        return [], []
    found = [(r[1], r[0], up) for up in (True, False) if (r := _lado(ctx, a, first, last, up)) is not None]
    if not found:
        return [], []
    t, sweep, up = min(found)                                                 # el lado cuya entrada cierra antes
    direction = "short" if up else "long"
    level = ctx.pdh if up else ctx.pdl
    name = "PDH" if up else "PDL"
    ts_hit = int(ctx.ts[t]) + ctx.tf_minutes * 60                             # la posición vive desde la vela siguiente
    extreme = float(np.max(ctx.high[sweep:t + 1]) if up else np.min(ctx.low[sweep:t + 1]))    # el swing del barrido
    close = float(ctx.close[t])
    sign = 1.0 if up else -1.0                                                # corto: el stop va por encima de la entrada; largo: por debajo
    covers = sign * (extreme - close) <= a.stop_points
    stop = close + sign * a.stop_points if covers else extreme + sign * a.stop_buffer
    goal = asia.low if up else asia.high
    detail = (f"el {name} ({level:.5g}), sin tocar desde las 18:00, es barrido a las {hora_ny(ctx, sweep)} con swing en {extreme:.5g} y pasa a ser el "
              f"{'High' if up else 'Low'} de {rango} (nivel mitigado); la primera vela que cierra de nuevo {'por debajo' if up else 'por encima'} es la de "
              f"{hora_ny(ctx, t)} ({close:.5g}). Entrada a mercado a ese cierre, stop en {stop:.5g} "
              f"({'fijo a ' + format(a.stop_points, 'g') + ' puntos, cubre el swing' if covers else 'swing + ' + format(a.stop_buffer, 'g')}) "
              f"y objetivo en el {'Low' if up else 'High'} de {rango} ({goal:.5g})"
              + (" o, si no llega, salida al cierre del rango" if ctx.salir_al_cierre else ""))
    figures = []
    if t + 1 < len(ctx.ts):
        fig = _figura_posicion(ctx, direction, t + 1, close, stop, goal, f"{name} {'▼' if up else '▲'} barrido", key)
        figures = [Figure(fig.kind, fig.key, fig.zone, fig.direction, fig.x0_ts, fig.x1_ts, {**fig.levels, "entrada_ts": float(ctx.ts[t])},
                          fig.state, fig.label, fig.day)]
    levels = {"stop": stop, "target": goal, **({"cierre": float(ctx.salida)} if ctx.salida else {})}       # "cierre": hora (servidor) de la salida forzosa
    return [PatternHit(key, title, direction, int(t), close, detail, levels, ts_hit, DETECTED)], figures


def contextos(symbol: str, tf_minutes: int, ts, o, h, l, c, sessions, ahead: int, day_end: int = 0, be_r: float | None = None,
              zona: str = ZONA, salir_al_cierre: bool = False) -> list[Contexto]:
    """Un contexto por cada noche con Asia cerrada, de la más antigua a la más reciente: lo que analiza la skill y también el backtest.

    `sessions`: las sesiones de la skill TBR (con Asia). Las velas `ts, o, h, l, c` son las ya cerradas. `day_end`: hora de NY en que
    cambia el día de trading (18:00 en los índices USA), de la que salen el PDH y el PDL. `be_r` no se usa (sin breakeven). `zona`: la TBR que da el objetivo (Asia, o Londres con `salir_al_cierre`)."""
    ts = np.asarray(ts, dtype=np.int64)
    day_of = (ts - ahead - day_end * 60) // DAY + 1                           # día de trading de cada vela (el mismo cálculo que la skill Levels)
    out = []
    for s in sorted((s for s in sessions if s.zone.key == zona and s.complete and s.high > s.low), key=lambda s: s.day):
        day0 = (s.day.toordinal() - date(1970, 1, 1).toordinal()) * DAY
        close_ts = day0 + s.zone.start * 60 + s.zone.minutes * 60 + ahead
        first = int(np.searchsorted(ts, day0 + s.zone.start * 60 + ahead, "left"))
        pdh = pdl = None
        dia_ini = first
        if first < len(ts):
            dia = int(day_of[first])
            dia_ini = int(np.searchsorted(day_of, dia, "left"))
            if dia_ini > 0:                                                   # el día de trading anterior: el que acaba de cerrar a las 18:00
                prev0 = int(np.searchsorted(day_of, int(day_of[dia_ini - 1]), "left"))
                pdh, pdl = float(np.max(h[prev0:dia_ini])), float(np.min(l[prev0:dia_ini]))
        tbr = ActiveTbr(zona, s.zone.name, s.day, s.high, s.low, s.x0, s.x1)
        out.append(Contexto(symbol, tf_minutes, ts, o, h, l, c, ahead, tbr, Zona(s.zone.name, s.day, s.high, s.low, close_ts), pdh, pdl,
                            dia_ini, len(ts) - 1, day_end, salir_al_cierre))
    return out
