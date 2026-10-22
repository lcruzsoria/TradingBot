"""Operación de un patrón: cómo termina (stop u objetivo) y el dibujo de la posición, como la herramienta de posición de TradingView."""
from __future__ import annotations

from types import SimpleNamespace

import numpy as np

from ..setup.positions import resolve
from .patterns import Figure

MAX_HOLD_SECONDS = 24 * 3600          # igual que en cortex/order.py


def day_close(ts: int, ahead: int, end_minutes: int) -> int:
    """Hora (servidor) del fin del día de trading (`end_minutes` desde medianoche de NY) siguiente a la hora `ts` (servidor)."""
    ny = int(ts) - ahead
    end = (ny // 86400) * 86400 + end_minutes * 60
    while end <= ny:
        end += 86400
    return end + ahead


def outcome(h: np.ndarray, l: np.ndarray, start: int, direction: str, stop: float, target: float,
            last: int | None = None) -> tuple[str | None, int]:
    """Cómo termina una posición llena en la vela `start`: ("target" | "stop", vela) o (None, última vela mirada) si sigue abierta.

    Se mira desde la propia vela de la entrada. Si en una misma vela caben el stop y el objetivo, cuenta el stop (el caso malo).
    """
    end = len(h) - 1 if last is None else min(last, len(h) - 1)
    for i in range(start, end + 1):
        if direction == "long":
            hit_stop, hit_target = l[i] <= stop, h[i] >= target
        else:
            hit_stop, hit_target = h[i] >= stop, l[i] <= target
        if hit_stop:
            return "stop", i
        if hit_target:
            return "target", i
    return None, end


def position_figure(ctx, key: str, zone: str, direction: str, t: int, entry: float, stop: float, target: float,
                    label: str) -> Figure:
    """Posición para el gráfico: de la vela de la entrada a la del cierre (o a la última vela si sigue abierta)."""
    close = int(ctx.ts[t]) + MAX_HOLD_SECONDS                                  # como tope, 24 h tras la entrada
    if ctx.day_end:
        close = min(close, day_close(int(ctx.ts[t]), ctx.ahead, ctx.day_end))      # y, antes, el fin del día de trading
    limit = int(np.searchsorted(ctx.ts, close, "left")) - 1
    tf_sec = ctx.tf_minutes * 60
    kind, idx = None, min(limit, len(ctx.ts) - 1)
    if limit >= t:      # la misma regla que la posición simulada de Setup, con su breakeven (stop a la entrada al cierre de una vela de 15 min)
        order = SimpleNamespace(direction=direction, price=entry, stop=stop, target=target, entry_ts=int(ctx.ts[t]), close_ts=close)
        end = limit + 1
        done = resolve(order, ctx.ts[:end], ctx.high[:end], ctx.low[:end], ctx.close[:end], ctx.be_r, tf_sec)
        if done is not None:
            kind, idx = done.result, int(np.searchsorted(ctx.ts, done.exit_ts, "left"))
    state = {"objetivo": "objetivo", "stop": "stop", "breakeven": "be", "tiempo": "tiempo"}.get(
        kind, "abierta" if limit >= len(ctx.ts) - 1 else "tiempo")
    return Figure("pos", key, zone, direction, int(ctx.ts[t]), int(ctx.ts[idx]) + tf_sec,
                  {"entrada": float(entry), "stop": float(stop), "objetivo": float(target)}, state, label, ctx.tbr.day.isoformat())
