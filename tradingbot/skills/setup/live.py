"""Operativa real (perfiles con MT5_<PERFIL>_SEND_ORDERS=true): el Forwardtest del perfil es la imagen de la cuenta demo.

- Empieza el día que el perfil arranca por primera vez (`operativa_real.json` en su carpeta): lo de antes no cuenta, aunque
  Pattern y Cortex lo repasen al arrancar.
- Solo se abren señales frescas (de después de ese arranque y de hace como mucho FRESH_SECONDS o dos velas): una señal vieja no
  se abre tarde.
- La entrada es la de MT5 (precio de ejecución) y el cierre también: precio, hora y resultado de las operaciones de cierre de la
  posición. El resultado en R es el dinero ganado o perdido (con comisión y swap) entre el riesgo en dinero al abrir.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

from ...clock import NY, server_minus_ny
from .positions import Closed

START_FILE = "operativa_real.json"
FRESH_SECONDS = 30 * 60          # una señal de hace más de esto (o de dos velas de su temporalidad) ya no se abre

RESULTS = {"tp": "objetivo", "bot": "tiempo", "manual": "manual", "stopout": "stop out"}   # "sl": stop o breakeven


def server_now(offset: int | None) -> int:
    """Hora del servidor (como si fuera UTC): con el desfase medido por Quotes o, sin él, el de los brokers con cierre en
    Nueva York (servidor = NY + 7 h)."""
    if offset is not None:
        return int(time.time()) + int(offset)
    shift, _ = server_minus_ny(None)
    ny = datetime.now(NY).utcoffset() if NY is not None else timedelta(hours=-5)
    return int(time.time() + ny.total_seconds()) + shift


def since(app_cfg: dict | None, now=time.time) -> float | None:
    """Hora (UTC, epoch) en que el perfil empezó a operar de verdad; la primera vez se fija ahora. None sin carpeta."""
    folder = ((app_cfg or {}).get("app") or {}).get("data_dir")
    if not folder:
        return None
    path = Path(folder) / START_FILE
    try:
        return float(json.loads(path.read_text(encoding="utf-8"))["desde_utc"])
    except (OSError, ValueError, KeyError, TypeError):
        pass
    start = float(now())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"desde_utc": start, "desde": datetime.fromtimestamp(start).isoformat(timespec="seconds")},
                               indent=2), encoding="utf-8")
    return start


def to_server(utc: float, offset: int | None) -> int:
    """Una hora UTC en hora del servidor."""
    return int(utc + server_now(offset) - time.time())


def fresh(order, now_server: int, since_server: int | None, bar_seconds: int | None) -> bool:
    """Si la señal es de después del arranque del perfil y todavía reciente."""
    ts = order.entry_ts
    if ts is None or (since_server is not None and ts < since_server - (bar_seconds or 0)):
        return False
    return now_server - ts <= max(FRESH_SECONDS, 2 * (bar_seconds or 0) + 300)


def closed_from_broker(order, deal: dict, ts=None, high=None, low=None) -> Closed:
    """El cierre de la posición tal como consta en MT5 (`deal`: price, ts, profit, reason)."""
    entry, stop, long = float(order.price), float(order.stop), order.direction == "long"
    exit_price, exit_ts, profit = float(deal["price"]), int(deal["ts"]), float(deal["profit"] or 0.0)
    reason = deal.get("reason") or "manual"
    result = ("breakeven" if order.be_sent else "stop") if reason == "sl" else RESULTS.get(reason, reason)
    sign = 1.0 if long else -1.0
    dist = abs(entry - stop)
    money = float(order.risk_money or 0.0)
    r = profit / money if money > 0 else (sign * (exit_price - entry) / dist if dist > 0 else 0.0)
    max_r = min_r = None
    if ts is not None and len(ts) and dist > 0:
        ts = np.asarray(ts, dtype=np.int64)
        a, b = int(np.searchsorted(ts, order.entry_ts, "left")), int(np.searchsorted(ts, exit_ts, "right"))
        if b > a:
            best = (np.max(high[a:b]) - entry) if long else (entry - np.min(low[a:b]))
            worst = (entry - np.min(low[a:b])) if long else (np.max(high[a:b]) - entry)
            max_r, min_r = round(max(float(best), 0.0) / dist, 4), round(-min(max(float(worst), 0.0) / dist, 1.0), 4)
    return Closed(result, exit_price, exit_ts, round(r, 4), 100 * sign * (exit_price - entry) / entry, order.be_at,
                  max_r, min_r)
