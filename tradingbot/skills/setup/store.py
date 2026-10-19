"""Posiciones simuladas abiertas en disco: `data/setup/abiertas.json`, para no perderlas al reiniciar y poder consultarlas.

Lo escribe Setup cada vez que abre o cierra una; al arrancar, Setup las sigue y Cortex sabe qué mercados están ocupados.
Es un JSON legible: una lista con la orden completa de cada posición (mercado, lado, patrón, precio, stop, objetivo, TBR,
sesgo, motivo y horas de entrada y de cierre por tiempo).
"""
from __future__ import annotations

import json
from dataclasses import asdict, fields
from datetime import date
from pathlib import Path

from ...config import PROJECT_ROOT
from ..cortex.order import Order

DEFAULT_FILE = PROJECT_ROOT / "data" / "setup" / "abiertas.json"


def order_to_json(order: Order) -> dict:
    d = asdict(order)
    d["tbr_day"] = order.tbr_day.isoformat() if isinstance(order.tbr_day, date) else order.tbr_day
    return d


def order_from_json(data: dict) -> Order:
    names = {f.name for f in fields(Order)}
    d = {k: v for k, v in data.items() if k in names}
    if isinstance(d.get("tbr_day"), str):
        d["tbr_day"] = date.fromisoformat(d["tbr_day"])
    return Order(**d)


def load(path: Path | None = None) -> list[Order]:
    """Las posiciones guardadas; sin fichero, o si no se entiende, ninguna (las que no se entienden se saltan)."""
    path = Path(path or DEFAULT_FILE)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    orders = []
    for item in data if isinstance(data, list) else []:
        try:
            orders.append(order_from_json(item))
        except (TypeError, ValueError):
            continue
    return orders


def save(orders: list[Order], path: Path | None = None) -> None:
    """Escribe todas las posiciones abiertas (sustituye el fichero de una vez, así nunca queda a medias)."""
    path = Path(path or DEFAULT_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps([order_to_json(o) for o in orders], ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)
