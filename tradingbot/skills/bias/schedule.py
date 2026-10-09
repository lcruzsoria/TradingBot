"""Recálculo programado del sesgo: cada N horas, alineado con el inicio del día de trading (hora de Nueva York).

Índices americanos: el día empieza a las 18:00 NY y se recalcula cada 3 h (18, 21, 00, 03, 06, 09, 12, 15), al cierre
de cada vela H3. Resto de activos: el día empieza a las 17:00 NY y se recalcula cada 4 h (17, 21, 01, 05, 09, 13), al
cierre de cada vela H4. Así el sesgo se revisa con cada bloque de sesión cerrado, no a mitad de vela.
"""
from __future__ import annotations

from datetime import datetime, timedelta

DEFAULT_INDEX_HOURS = 3     # BIAS_RECALC_INDEX_HOURS
DEFAULT_HOURS = 4           # BIAS_RECALC_HOURS
CHECK_SECONDS = 30          # cada cuánto mira la skill si toca recalcular


def next_recalc(now_ny: datetime, anchor_minutes: int, hours: float) -> datetime:
    """Primera hora de recálculo estrictamente posterior a `now_ny` (con zona de NY), alineada con `anchor_minutes`."""
    step = timedelta(hours=hours)
    anchor = now_ny.replace(hour=anchor_minutes // 60, minute=anchor_minutes % 60, second=0, microsecond=0)
    if anchor > now_ny:
        anchor -= timedelta(days=1)
    blocks = int((now_ny - anchor) / step) + 1
    return anchor + blocks * step
