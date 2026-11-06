"""Detección del setup «Barrido de Asia» (modelo Greenbird, perfil `asia_sweep`): funciones puras, sin depender de otra skill.

Es una HIPÓTESIS SIN VALIDAR: solo simula, como todo el bot con SETUP_SEND_ORDERS=false.

Reglas (velas de `BARRIDO_ASIA_TF`, M5 al inicio):

1. El rango de Asia (TBR 20:00-00:00 NY) tiene que haber terminado: solo se busca desde su cierre.
2. Rotura: la primera vela, desde `BARRIDO_ASIA_START` (00:00 NY), que CIERRA fuera del rango (una mecha sola no cuenta). Debe abrir antes de
   `BARRIDO_ASIA_END` (01:00 NY): una primera rotura posterior no vale. Solo cuenta la primera del día.
3. Swing: el extremo (máximo en un corto, mínimo en un largo) de todo el tramo fuera del rango, desde la rotura hasta la vela de entrada.
   Stop: fijo, a `BARRIDO_ASIA_STOP_POINTS` (30) puntos de la entrada si con eso queda cubierto el swing; si no, el swing más
   `BARRIDO_ASIA_STOP_BUFFER` (5) puntos (por encima en un corto, por debajo en un largo).
4. Entrada: la primera vela POSTERIOR a la rotura que CIERRA de nuevo dentro del rango de Asia, a mercado a su cierre. Debe abrir antes de
   `BARRIDO_ASIA_ENTRY_END` (01:00 NY): la vela de entrada de 5 min tiene que cerrar dentro de Asia a la 01:00 como tarde. Si antes de volver el precio rompe también el otro lado, no hay setup.
5. Romper por arriba da un corto y romper por abajo, un largo. Objetivo: el lado contrario del rango de Asia (el Low en un corto, el High
   en un largo). Sin breakeven: la posición cierra en el objetivo, en el stop o a final del día de trading.

Solo índices USA (NAS100, SP500, DJ30...), no Forex.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from types import SimpleNamespace

import numpy as np

from ...timeframes import parse_timeframe
from .._comun.contratos import DETECTED, INVALIDATED, ActiveTbr, Figure, PatternHit
from . import stops
from ..setup.positions import resolve         # la misma regla con la que Setup cierra la posición simulada

KEY = "barrido_asia"
TITLE = "Barrido de Asia"
ZONA = "ASIA"                    # la TBR cuyo rango se rompe
DEFAULT_TF = "5m"
DEFAULT_START = "00:00"          # hora de NY desde la que cuenta una rotura (cierre de Asia)
DEFAULT_END = "01:00"            # hora de NY antes de la que debe abrir la vela que rompe el rango
DEFAULT_ENTRY_END = "01:00"      # hora de NY antes de la que debe abrir la vela de entrada: su cierre es a la 01:00 como tarde
DEFAULT_STOP_POINTS = 30.0       # stop fijo, en puntos del precio, si cubre el swing
DEFAULT_STOP_BUFFER = 5.0        # si el swing queda más lejos, el stop es el swing más estos puntos
INDICES_USA = ("NAS100", "SP500", "DJ30", "US30", "US100", "US500", "USTEC", "US2000", "SPX500", "NDX100")
MAX_HOLD_SECONDS = 24 * 3600     # como tope, una posición dura 24 h (igual que el resto de órdenes)


def minutos(text: str, name: str) -> int:
    try:
        h, m = (int(x) for x in str(text).strip().split(":"))
        assert 0 <= h < 24 and 0 <= m < 60
    except (ValueError, AssertionError):
        raise ValueError(f"BARRIDO_ASIA_{name}={text!r}: usa el formato HH:MM.") from None
    return h * 60 + m


@dataclass(frozen=True)
class Ajustes:
    """Ajustes de la skill (bloque BARRIDO_ASIA de tradingbot.env, ya sin prefijo)."""
    tf: str = DEFAULT_TF
    start: int = minutos(DEFAULT_START, "START")
    end: int = minutos(DEFAULT_END, "END")
    entry_end: int = minutos(DEFAULT_ENTRY_END, "ENTRY_END")
    stop_points: float = DEFAULT_STOP_POINTS
    stop_buffer: float = DEFAULT_STOP_BUFFER
    stop_mercado: tuple = ()     # stop propio de algunos mercados: ((MERCADO, puntos, buffer), ...)

    @classmethod
    def desde(cls, settings) -> "Ajustes":
        get = (lambda key, default: default) if settings is None else settings.get
        tf = str(get("TF", DEFAULT_TF))
        parse_timeframe(tf)                                                   # valida el timeframe
        try:
            points, buffer = float(get("STOP_POINTS", DEFAULT_STOP_POINTS)), float(get("STOP_BUFFER", DEFAULT_STOP_BUFFER))
        except ValueError:
            raise ValueError("BARRIDO_ASIA_STOP_POINTS y BARRIDO_ASIA_STOP_BUFFER deben ser números.") from None
        if points <= 0 or buffer < 0:
            raise ValueError("BARRIDO_ASIA_STOP_POINTS debe ser mayor que 0 y BARRIDO_ASIA_STOP_BUFFER no puede ser negativo.")
        a = cls(tf, minutos(get("START", DEFAULT_START), "START"), minutos(get("END", DEFAULT_END), "END"),
                minutos(get("ENTRY_END", DEFAULT_ENTRY_END), "ENTRY_END"), points, buffer,
                stops.leer(settings, "BARRIDO_ASIA", points, buffer))
        if a.end <= a.start:
            raise ValueError(f"BARRIDO_ASIA_END={a.end // 60:02d}:{a.end % 60:02d} debe ser posterior a START.")
        if a.entry_end < a.end:
            raise ValueError(f"BARRIDO_ASIA_ENTRY_END={a.entry_end // 60:02d}:{a.entry_end % 60:02d} no puede ser anterior a END.")
        return a

    def stop_de(self, symbol: str) -> tuple[float, float]:
        """(puntos, buffer) del stop fijo de un mercado: el suyo si el bloque lo define (STOP_POINTS_<MERCADO>), si no el general."""
        return stops.de(self.stop_mercado, symbol, self.stop_points, self.stop_buffer)


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
    """Todo lo que necesita el análisis de una noche: velas, rango de Asia y la TBR con la que se publica."""
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
    last_bar: int = 0            # última vela cerrada
    day_end: int = 0             # fin del día de trading del mercado (minutos desde medianoche de NY): ahí cierran los trades

    @property
    def cierre_rango(self) -> int:
        """Cierre del rango que se rompe (hora del servidor): la skill lo usa para saber si la noche es reciente."""
        return self.asia.close_ts


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


def _figura_posicion(ctx: Contexto, direction: str, t: int, entry: float, stop: float, target: float, label: str) -> Figure:
    """Posición para el gráfico: de la vela de la entrada a la del cierre (o a la última vela si sigue abierta)."""
    close = int(ctx.ts[t]) + MAX_HOLD_SECONDS
    if ctx.day_end:
        close = min(close, cierre_del_dia(int(ctx.ts[t]), ctx.ahead, ctx.day_end))
    limit = int(np.searchsorted(ctx.ts, close, "left")) - 1
    tf_sec = ctx.tf_minutes * 60
    kind, idx = None, min(limit, len(ctx.ts) - 1)
    if limit >= t:
        order = SimpleNamespace(direction=direction, pattern_key=KEY, price=entry, stop=stop, target=target, entry_ts=int(ctx.ts[t]), close_ts=close)
        end = limit + 1
        done = resolve(order, ctx.ts[:end], ctx.high[:end], ctx.low[:end], ctx.close[:end], None, tf_sec)
        if done is not None:
            kind, idx = done.result, int(np.searchsorted(ctx.ts, done.exit_ts, "left"))
    state = {"objetivo": "objetivo", "stop": "stop", "breakeven": "be", "tiempo": "tiempo"}.get(
        kind, "abierta" if limit >= len(ctx.ts) - 1 else "tiempo")
    return Figure("pos", KEY, ctx.tbr.zone, direction, int(ctx.ts[t]), int(ctx.ts[idx]) + tf_sec,
                  {"entrada": float(entry), "stop": float(stop), "objetivo": float(target)}, state, label, ctx.tbr.day.isoformat())


def analizar(ctx: Contexto, a: Ajustes = Ajustes()) -> tuple[list[PatternHit], list[Figure]]:
    """Resultados de la noche de Asia de `ctx` (cero o uno) y su dibujo."""
    if len(ctx.ts) == 0 or not es_indice_usa(ctx.symbol):
        return [], []                                                         # de momento solo índices USA, no Forex
    asia = ctx.asia
    midnight = (asia.day.toordinal() + 1 - date(1970, 1, 1).toordinal()) * 86400 + ctx.ahead    # medianoche de NY en que cierra Asia, en hora del servidor
    from_ts = max(midnight + a.start * 60, asia.close_ts)                     # Asia debe haber terminado
    first = int(np.searchsorted(ctx.ts, from_ts, "left"))
    last_break = int(np.searchsorted(ctx.ts, midnight + a.end * 60, "left")) - 1       # última vela que puede iniciar la rotura
    last_entry = min(ctx.last_bar, int(np.searchsorted(ctx.ts, midnight + a.entry_end * 60, "left")) - 1)    # y la de la entrada
    if first >= len(ctx.ts) or first > ctx.last_bar:
        return [], []
    # la rotura: la primera vela desde las 00:00 que CIERRA fuera del rango (una mecha sola no cuenta); si llega tras la ventana, no vale
    outside = np.flatnonzero((ctx.close[first:ctx.last_bar + 1] > asia.high) | (ctx.close[first:ctx.last_bar + 1] < asia.low))
    if not outside.size:
        return [], []
    sweep = first + int(outside[0])
    if sweep > last_break:
        return [], []                                                         # la primera rotura llegó fuera de la ventana: no hay setup
    up = bool(ctx.close[sweep] > asia.high)
    side, direction = ("High", "short") if up else ("Low", "long")
    # la entrada: la primera vela POSTERIOR a la rotura que cierra de nuevo dentro del rango, una vez creado el swing
    closes = ctx.close[sweep + 1:last_entry + 1]
    back = np.flatnonzero(closes < asia.high) if up else np.flatnonzero(closes > asia.low)
    if not back.size:
        return [], []                                                         # aún no ha vuelto (o no volvió antes de la hora límite)
    t = sweep + 1 + int(back[0])
    ts_hit = int(ctx.ts[t]) + ctx.tf_minutes * 60                             # la posición vive desde la vela siguiente
    extreme = float(np.max(ctx.high[sweep:t + 1]) if up else np.min(ctx.low[sweep:t + 1]))    # el swing: extremo de todo el tramo fuera del rango
    other = bool(ctx.low[sweep:t + 1].min() < asia.low) if up else bool(ctx.high[sweep:t + 1].max() > asia.high)
    close = float(ctx.close[t])
    if other:                                                                 # rompió también el lado contrario antes de volver
        return [PatternHit(KEY, TITLE, direction, int(t), close, "el precio rompe también el otro lado de Asia antes de volver dentro: "
                           "sin setup hoy", {}, ts_hit, INVALIDATED)], []
    sign = 1.0 if up else -1.0                                                # corto: el stop va por encima de la entrada; largo: por debajo
    puntos, buffer = a.stop_de(ctx.symbol)                                    # el stop fijo del mercado
    covers = sign * (extreme - close) <= puntos                        # ¿el stop fijo cubre el swing?
    stop = close + sign * puntos if covers else extreme + sign * buffer
    goal = asia.low if up else asia.high
    detail = (f"primera rotura del {side} de Asia ({asia.high if up else asia.low:.5g}) en {hora_ny(ctx, sweep)}, con swing en {extreme:.5g}; la "
              f"primera vela que cierra de nuevo dentro del rango es la de {hora_ny(ctx, t)} ({close:.5g}). Entrada a mercado a ese cierre, stop en "
              f"{stop:.5g} ({'fijo a ' + format(puntos, 'g') + ' puntos, cubre el swing' if covers else 'swing + ' + format(buffer, 'g')}) "
              f"y objetivo en el {'Low' if up else 'High'} de Asia ({goal:.5g})")
    figures = []
    if t + 1 < len(ctx.ts):
        fig = _figura_posicion(ctx, direction, t + 1, close, stop, goal, f"Asia {'▼' if up else '▲'} barrido")
        figures = [Figure(fig.kind, fig.key, fig.zone, fig.direction, fig.x0_ts, fig.x1_ts, {**fig.levels, "entrada_ts": float(ctx.ts[t])},
                          fig.state, fig.label, fig.day)]               # la vela cuyo cierre es la entrada: el gráfico la marca ahí
    return [PatternHit(KEY, TITLE, direction, int(t), close, detail, {"stop": stop, "target": goal}, ts_hit, DETECTED)], figures


def contextos(symbol: str, tf_minutes: int, ts, o, h, l, c, sessions, ahead: int, day_end: int = 0, be_r: float | None = None) -> list[Contexto]:
    """Un contexto por cada noche con Asia cerrada, de la más antigua a la más reciente: lo que analiza la skill y también el backtest.

    `sessions`: las sesiones de la skill TBR (con Asia). Las velas `ts, o, h, l, c` son las ya cerradas. `be_r` no se usa (sin breakeven)."""
    out = []
    for s in sorted((s for s in sessions if s.zone.key == ZONA and s.complete and s.high > s.low), key=lambda s: s.day):
        day0 = (s.day.toordinal() - date(1970, 1, 1).toordinal()) * 86400
        close_ts = day0 + s.zone.start * 60 + s.zone.minutes * 60 + ahead
        tbr = ActiveTbr(ZONA, s.zone.name, s.day, s.high, s.low, s.x0, s.x1)
        out.append(Contexto(symbol, tf_minutes, ts, o, h, l, c, ahead, tbr, Zona(s.zone.name, s.day, s.high, s.low, close_ts), len(ts) - 1, day_end))
    return out
