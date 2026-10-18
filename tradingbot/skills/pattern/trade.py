"""Operación de un patrón: cómo termina (stop u objetivo) y el dibujo de la posición, como la herramienta de posición de TradingView."""
from __future__ import annotations

import numpy as np

from .patterns import Figure

MAX_HOLD_SECONDS = 24 * 3600          # igual que en cortex/order.py


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
    limit = int(np.searchsorted(ctx.ts, int(ctx.ts[t]) + MAX_HOLD_SECONDS, "left")) - 1       # 24 h tras la entrada
    kind, idx = outcome(ctx.high, ctx.low, t, direction, stop, target, limit)
    tf_sec = ctx.tf_minutes * 60
    state = {"target": "objetivo", "stop": "stop"}.get(kind, "abierta" if limit >= len(ctx.ts) - 1 else "tiempo")
    return Figure("pos", key, zone, direction, int(ctx.ts[t]), int(ctx.ts[idx]) + tf_sec,
                  {"entrada": float(entry), "stop": float(stop), "objetivo": float(target)}, state, label)
