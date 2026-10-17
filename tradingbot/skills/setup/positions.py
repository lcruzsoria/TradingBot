"""Seguimiento de las posiciones simuladas: stop, objetivo y cierre por tiempo, con las velas del mercado."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Closed:
    result: str              # "objetivo", "stop" o "tiempo"
    exit_price: float
    exit_ts: int             # hora de servidor de la vela en que se cierra
    r: float                 # resultado en R (sin spread)
    pct: float               # resultado en % del precio de entrada


def trackable(order) -> bool:
    """Solo se siguen las órdenes que traen hora de entrada, stop, objetivo y hora de cierre."""
    return None not in (order.entry_ts, order.close_ts, order.stop, order.target)


def resolve(order, ts, high, low, close) -> Closed | None:
    """Cierre de la posición `order` (larga o corta) con las velas dadas, o None si sigue abierta.

    Misma regla que el backtest: desde la vela de la entrada, si caben stop y objetivo en una vela cuenta el stop; el cierre por
    tiempo es al cierre de la última vela anterior a `close_ts` y solo se da cuando ya existe una vela posterior (así no se
    cierra con una vela que aún se está formando).
    """
    ts = np.asarray(ts, dtype=np.int64)
    long = order.direction == "long"
    entry, stop, target = order.price, order.stop, order.target
    risk = abs(entry - stop)
    if risk <= 0:
        return None
    sign = 1.0 if long else -1.0

    def done(result: str, price: float, i: int) -> Closed:
        move = sign * (price - entry)
        return Closed(result, price, int(ts[i]), move / risk, 100 * move / entry)

    start = int(np.searchsorted(ts, order.entry_ts, "left"))
    last = None
    for i in range(start, len(ts)):
        if ts[i] >= order.close_ts:
            return done("tiempo", float(close[last]), last) if last is not None else None
        hit_stop = low[i] <= stop if long else high[i] >= stop
        hit_target = high[i] >= target if long else low[i] <= target
        if hit_stop:
            return done("stop", stop, i)
        if hit_target:
            return done("objetivo", target, i)
        last = i
    return None
