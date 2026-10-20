"""Seguimiento de las posiciones simuladas: stop, objetivo, stop a breakeven y cierre por tiempo, con las velas del mercado."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

BE_CHECK_SECONDS = 15 * 60           # el paso del stop a breakeven se mira al cierre de cada vela de 15 min


@dataclass(frozen=True)
class Closed:
    result: str              # "objetivo", "stop", "breakeven" (stop ya movido a la entrada) o "tiempo"
    exit_price: float
    exit_ts: int             # hora de servidor de la vela en que se cierra
    r: float                 # resultado en R (sin spread)
    pct: float               # resultado en % del precio de entrada
    be_ts: int | None = None  # hora de servidor de la vela de 15 min a cuyo cierre el stop pasó a la entrada (None: no pasó)


def trackable(order) -> bool:
    """Solo se siguen las órdenes que traen hora de entrada, stop, objetivo y hora de cierre."""
    return None not in (order.entry_ts, order.close_ts, order.stop, order.target)


def closes_m15(ts: int, bar_seconds: int | None) -> bool:
    """Si la vela que empieza en `ts` cierra a la vez que una vela de 15 min (con velas de 15 min o más, todas)."""
    if not bar_seconds or bar_seconds >= BE_CHECK_SECONDS:
        return True
    return (int(ts) + bar_seconds) % BE_CHECK_SECONDS == 0


def resolve(order, ts, high, low, close, be_r: float | None = None, bar_seconds: int | None = None) -> Closed | None:
    """Cierre de la posición `order` (larga o corta) con las velas dadas, o None si sigue abierta.

    Misma regla que el backtest: desde la vela de la entrada, si caben stop y objetivo en una vela cuenta el stop; el cierre por
    tiempo es al cierre de la última vela anterior a `close_ts` y solo se da cuando ya existe una vela posterior (así no se
    cierra con una vela que aún se está formando).

    Breakeven (`be_r`, en R; None = sin breakeven): si una vela de 15 min cierra con la posición `be_r` R o más a favor, el stop
    pasa al precio de entrada desde la vela siguiente; si después lo toca, la operación cierra a 0 R («breakeven»).
    `bar_seconds` es la duración de las velas, para saber cuáles cierran con una de 15 min.
    """
    ts = np.asarray(ts, dtype=np.int64)
    long = order.direction == "long"
    entry, stop, target = order.price, order.stop, order.target
    risk = abs(entry - stop)
    if risk <= 0:
        return None
    sign = 1.0 if long else -1.0
    be_ts = None

    def done(result: str, price: float, i: int) -> Closed:
        move = sign * (price - entry)
        return Closed(result, price, int(ts[i]), move / risk, 100 * move / entry, be_ts)

    start = int(np.searchsorted(ts, order.entry_ts, "left"))
    last = None
    for i in range(start, len(ts)):
        if ts[i] >= order.close_ts:
            return done("tiempo", float(close[last]), last) if last is not None else None
        current = entry if be_ts is not None else stop
        hit_stop = low[i] <= current if long else high[i] >= current
        hit_target = high[i] >= target if long else low[i] <= target
        if hit_stop:
            return done("breakeven" if be_ts is not None else "stop", current, i)
        if hit_target:
            return done("objetivo", target, i)
        if (be_r is not None and be_ts is None and i < len(ts) - 1 and closes_m15(ts[i], bar_seconds)
                and sign * (close[i] - entry) / risk >= be_r):
            be_ts = int(ts[i])          # vela cerrada (ya hay otra después): el stop pasa a la entrada
        last = i
    return None
