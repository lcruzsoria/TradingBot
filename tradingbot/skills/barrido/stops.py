"""Stop fijo por mercado de los setups de barrido: el valor general (`STOP_POINTS`, `STOP_BUFFER`, pensado para el Nasdaq) y, si hace falta, uno por mercado.

Los índices no cotizan igual (NAS100 ~25.000, DJ30 ~51.000, SP500 ~6.900), así que los mismos puntos no valen para todos. En el bloque de cada setup
de tradingbot.env se añade el sufijo del mercado, que casa con el comienzo del símbolo (DJ30 vale para DJ30.s):

    BARRIDO_RTH_STOP_POINTS=30            # general (NAS100 y cualquier mercado sin valor propio)
    BARRIDO_RTH_STOP_POINTS_DJ30=75       # stop fijo del DJ30
    BARRIDO_RTH_STOP_BUFFER_DJ30=10       # swing + 10 puntos en el DJ30
"""
from __future__ import annotations

POINTS, BUFFER = "STOP_POINTS_", "STOP_BUFFER_"


def leer(settings, prefix: str, points: float, buffer: float) -> tuple[tuple[str, float, float], ...]:
    """Valores propios de cada mercado del bloque `settings` (ya sin prefijo): ((MERCADO, puntos, buffer), ...). Lo que falte usa el valor general."""
    values = {} if settings is None else getattr(settings, "values", {})
    markets = sorted({k.split("_", 2)[2] for k in values if k.startswith((POINTS, BUFFER)) and len(k.split("_", 2)) == 3})
    out = []
    for m in markets:
        try:
            p, b = float(values.get(POINTS + m, points)), float(values.get(BUFFER + m, buffer))
        except ValueError:
            raise ValueError(f"{prefix}_STOP_POINTS_{m} y {prefix}_STOP_BUFFER_{m} deben ser números.") from None
        if p <= 0 or b < 0:
            raise ValueError(f"{prefix}_STOP_POINTS_{m} debe ser mayor que 0 y {prefix}_STOP_BUFFER_{m} no puede ser negativo.")
        out.append((m, p, b))
    return tuple(out)


def de(por_mercado, symbol: str, points: float, buffer: float) -> tuple[float, float]:
    """(puntos, buffer) del mercado `symbol`: el de la clave más larga que abre su nombre, o el general."""
    name = symbol.strip().upper()
    best = max((m for m in por_mercado if name.startswith(m[0].upper())), key=lambda m: len(m[0]), default=None)
    return (best[1], best[2]) if best else (points, buffer)
