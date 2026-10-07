"""Horas: del servidor del broker a Nueva York.

MT5 entrega las marcas de tiempo en la hora del servidor del broker, tratada como si fuera UTC. Para mostrarlas
en hora de Nueva York hay que conocer el desfase real del servidor respecto a UTC (por ejemplo +3 h en verano para
muchos brokers). Se mide comparando los ticks en vivo con el reloj del PC (OffsetDetector).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
    NY = ZoneInfo("America/New_York")
except Exception:  # noqa: BLE001 - sin base de zonas horarias (en Windows hace falta el paquete tzdata)
    NY = None

# Servidores con cierre diario en Nueva York (los habituales en forex/CFD): hora del servidor = hora de NY + 7 h.
NY_CLOSE_SERVER_AHEAD_HOURS = 7


def ny_from_server(server_ts: int, utc_offset_seconds: int | None) -> tuple[datetime, bool]:
    """Devuelve (hora en Nueva York, estimada).

    Con el desfase conocido la conversión es exacta y respeta el cambio de horario de EE. UU. Sin él se asume un
    servidor con cierre en Nueva York (servidor = NY + 7 h) y la hora se marca como estimada.
    """
    if utc_offset_seconds is not None and NY is not None:
        utc = datetime.fromtimestamp(server_ts - utc_offset_seconds, tz=timezone.utc)
        return utc.astimezone(NY), False
    naive = datetime.fromtimestamp(server_ts, tz=timezone.utc).replace(tzinfo=None)
    return naive - timedelta(hours=NY_CLOSE_SERVER_AHEAD_HOURS), True


class OffsetDetector:
    """Mide el desfase del servidor respecto a UTC con ticks en vivo.

    Un tick sirve solo si es NUEVO y su hora avanza al ritmo del reloj del PC (descarta mercados cerrados y saltos
    desde datos viejos). El desfase se redondea a cuartos de hora y se acepta tras `needed` medidas iguales seguidas;
    así también se adapta si el servidor cambia de horario mientras el bot está abierto.
    """

    def __init__(self, needed: int = 3) -> None:
        self.needed = needed
        self.offset: int | None = None
        self._prev: tuple[int, float] | None = None
        self._history: list[int] = []

    def observe(self, tick_ts: int, wall_utc: float) -> int | None:
        prev, self._prev = self._prev, (tick_ts, wall_utc)
        if prev is None:
            return self.offset
        d_tick, d_wall = tick_ts - prev[0], wall_utc - prev[1]
        if d_tick <= 0 or d_tick > d_wall + 3:        # sin ticks nuevos, o salto desde datos antiguos
            return self.offset
        diff = tick_ts - wall_utc
        candidate = round(diff / 900) * 900
        if abs(diff - candidate) > 30 or not -12 * 3600 <= candidate <= 14 * 3600:
            self._history.clear()                     # el tick no está en hora con el reloj: no se fía
            return self.offset
        self._history = (self._history + [candidate])[-self.needed:]
        if len(self._history) == self.needed and len(set(self._history)) == 1:
            self.offset = candidate
        return self.offset


def format_offset(seconds: int) -> str:
    sign = "+" if seconds >= 0 else "-"
    minutes = abs(seconds) // 60
    return f"UTC{sign}{minutes // 60}" + (f":{minutes % 60:02d}" if minutes % 60 else "")
