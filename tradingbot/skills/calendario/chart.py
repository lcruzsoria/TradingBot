"""Las entradas del backtest de Calendario, como posiciones del gráfico (perfil Calendario).

El backtest guarda de cada operación su mercado, la hora de entrada y de cierre (hora de Nueva York) y cómo acabó. El precio,
el stop y el objetivo se rehacen con las velas cargadas: entrada en la apertura de la vela, stop y objetivo a los % del
backtest. Solo salen las entradas cuya vela está entre las cargadas (FEED_MAX_BARS por mercado y timeframe).
"""
from __future__ import annotations

import numpy as np

from ..feed.mt5_client import ALIASES

STATES = {"objetivo": "objetivo", "stop": "stop", "tiempo": "tiempo"}


def market_key(name: str) -> str:
    """El mercado sin sufijo del broker y con un solo nombre (NAS100.r, NAS100.s y USTEC son el mismo)."""
    base = name.split(".")[0].lower()
    for group in ALIASES:
        if any(base.startswith(a.lower()) for a in group):
            return group[0].lower()
    return base


def backtest_positions(group, symbol: str, ts, opens, highs, lows, ahead: int) -> list[dict]:
    """Posiciones (formato de ChartView.set_positions) de las entradas largas del backtest en `symbol`.

    `ts`: horas de las velas (servidor); `ahead`: segundos que el servidor va por delante de Nueva York.
    """
    ops, raw = group.ops, group.raw
    if not len(ops) or not len(ts):
        return []
    mask = ((np.array([market_key(m) for m in ops.names("m")]) == market_key(symbol)) & (ops["d"] == 0)
            & np.isin(ops.weekday, raw["dias"]) & (ops.hour == raw["hora"]) & (ops["e"] % 60 == 0))
    chosen = ops.take(mask)
    ts = np.asarray(ts)
    n = len(ts)
    stop_pct, rr = float(raw["stop"]) / 100, float(raw["rr"])
    out = []
    for entry_min, exit_min, result in zip(chosen["e"], chosen["x"], chosen.names("o")):
        start, end = int(entry_min) * 60 + ahead, int(exit_min) * 60 + ahead
        x0 = int(np.searchsorted(ts, start, "left"))
        if x0 >= n or int(ts[x0]) != start:                  # la vela de entrada no está cargada (o el timeframe no la tiene)
            continue
        entry = float(opens[x0])
        stop, target = entry * (1 - stop_pct), entry * (1 + rr * stop_pct)
        last = min(int(np.searchsorted(ts, end, "left")), n)
        x1, hit = last, False
        for j in range(x0, last):                            # donde tocó stop u objetivo (el stop primero si caben los dos)
            if lows[j] <= stop or highs[j] >= target:
                x1, hit = j, True
                break
        state = STATES.get(str(result), "tiempo")
        if not hit and last >= n:
            state = "abierta"
        out.append({"x0": x0, "x1": min(x1, n + 4), "entry": entry, "stop": stop, "target": target, "direction": "long",
                    "state": state, "label": "Calendario", "decision": "", "reason": "", "session": ("calendario", start)})
    return out
