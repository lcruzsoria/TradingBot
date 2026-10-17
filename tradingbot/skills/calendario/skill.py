"""Skill Calendario: largos a hora fija en los días de la semana configurados (por defecto, lunes de madrugada)."""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np

from ...clock import server_minus_ny
from ...core import Event, Skill, register_skill
from ...timeframes import minutes

DAYS = {"lunes": 0, "martes": 1, "miercoles": 2, "miércoles": 2, "jueves": 3, "viernes": 4}
MAX_LATE_BARS = 2                                  # una señal se da si la vela de entrada es una de las últimas 2


def parse_hour(text: str, key: str) -> int:
    """Minutos desde las 00:00 de una hora 'HH:MM'."""
    try:
        h, m = (int(x) for x in text.strip().split(":"))
    except ValueError:
        raise ValueError(f"{key}={text}: usa el formato HH:MM (hora de Nueva York)") from None
    if not (0 <= h < 24 and 0 <= m < 60):
        raise ValueError(f"{key}={text}: hora fuera de rango")
    return h * 60 + m


def matches(symbol: str, wanted: list[str]) -> bool:
    """El símbolo del broker (con su sufijo y mayúsculas, que no se tocan) corresponde a alguno de los pedidos."""
    s = symbol.lower()
    return any(s.startswith(w.lower()) for w in wanted)


@register_skill("calendario")
class CalendarioSkill(Skill):
    title = "Calendario"
    description = ("Estrategia de calendario, sin patrones: entra largo a una hora fija de Nueva York (por defecto, lunes a "
                   "las 02:00 en NAS100 y DJ30), con stop a un % del precio y objetivo a RR veces el stop, y cierra por tiempo "
                   "a las 10:00. Aprovecha la deriva alcista nocturna de los índices (backtest 2018-2026, "
                   "scripts/lunes_hora_fija.py). Avisa a Cortex, que le da la orden a Setup; solo simulación.")
    subscribes = ("candles.loaded", "clock.offset")
    publishes = ("calendar.signal",)
    slot = "aux2"

    def on_start(self) -> None:
        self.error = "Configuración CALENDARIO no válida"
        self._offset: int | None = None
        self._seen: set = set()
        try:
            self._load_settings()
        except ValueError as exc:
            self.error = str(exc)
            raise
        self.error = ""
        self.set_caption("esperando velas")

    def _load_settings(self) -> None:
        s = self.settings                                                              # tradingbot.env, bloque CALENDARIO
        self.symbols = s.get_list("SYMBOLS", ["NAS100", "DJ30"])
        days = [d.lower() for d in s.get_list("DAYS", ["lunes"])]
        unknown = [d for d in days if d not in DAYS]
        if unknown:
            raise ValueError(f"CALENDARIO_DAYS={', '.join(days)}: día desconocido {', '.join(unknown)} "
                             f"(usa lunes, martes, miercoles, jueves o viernes)")
        self.days = sorted({DAYS[d] for d in days})
        self.entry = parse_hour(s.get("ENTRY_HOUR", "02:00"), "CALENDARIO_ENTRY_HOUR")
        self.exit = parse_hour(s.get("EXIT_HOUR", "10:00"), "CALENDARIO_EXIT_HOUR")
        if self.exit <= self.entry:
            raise ValueError("CALENDARIO_EXIT_HOUR debe ser posterior a CALENDARIO_ENTRY_HOUR")
        self.stop_pct = s.get_float("STOP_PCT", 0.5)
        self.rr = s.get_float("RR", 2.0)
        if self.stop_pct <= 0 or self.rr <= 0:
            raise ValueError("CALENDARIO_STOP_PCT y CALENDARIO_RR deben ser mayores que 0")
        direction = (s.get("DIRECTION", "long") or "long").lower()
        if direction != "long":
            raise ValueError("CALENDARIO_DIRECTION=long: los cortos de lunes pierden en el backtest, solo se admiten largos")
        self.direction = direction

    def handle(self, event: Event) -> None:
        if self.error:
            raise ValueError(self.error)
        if event.topic == "clock.offset":
            self._offset = event.payload.get("server_offset")
            return
        symbol, tf, df = event.payload["symbol"], event.payload["timeframe"], event.payload["df"]
        if not matches(symbol, self.symbols):
            self.set_caption(f"{symbol} no está en CALENDARIO_SYMBOLS")
            return
        if len(df) == 0 or minutes(tf) > 60 or (60 % minutes(tf)):
            self.set_caption("necesita velas de 60 min o menos")
            return
        ahead, _ = server_minus_ny(self._offset)
        ts = df["ts"].to_numpy().astype(np.int64)
        for i in range(max(len(ts) - MAX_LATE_BARS, 0), len(ts)):
            ny = datetime.fromtimestamp(int(ts[i]) - ahead, timezone.utc)                          # hora de Nueva York (ingenua)
            if ny.weekday() not in self.days or ny.hour * 60 + ny.minute != self.entry:
                continue
            key = (symbol, ny.date())
            if key in self._seen:
                continue
            self._seen.add(key)
            price = float(df["open"].to_numpy()[i])
            risk = price * self.stop_pct / 100
            self.publish("calendar.signal", {
                "symbol": symbol, "timeframe": tf, "direction": self.direction, "price": price, "stop": price - risk,
                "target": price + self.rr * risk, "day": ny.date(), "entry_ts": int(ts[i]),
                "close_ts": int(ts[i]) + (self.exit - self.entry) * 60,
                "close_at": f"{self.exit // 60:02d}:{self.exit % 60:02d} NY ({ny:%d/%m/%Y})"})
            self.set_caption(f"señal {symbol}")
            return
        self.set_caption(f"{symbol}: esperando {self.entry // 60:02d}:{self.entry % 60:02d} NY")
