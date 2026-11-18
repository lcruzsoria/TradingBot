"""Skill SMT: SMT secuencial entre NAS100, SP500 y DJ30 (Quarterly Theory). Solo informa: publica `smt.updated` y `smt.detected`; no opera."""
from __future__ import annotations

import numpy as np

from ...clock import server_minus_ny
from ...core import Event, Skill, register_skill
from ...timeframes import minutes, parse_timeframe
from . import ciclos
from .smt import detectar

DEFAULT_TF = "5m"
DEFAULT_TRIAD = ("NAS100", "SP500", "DJ30")
DEFAULT_CICLOS = ("dia", "90m", "semana")
KEEP_EVENTS = 12                       # SSMT recientes que se publican por ciclo


@register_skill("smt")
class SmtSkill(Skill):
    title = "SMT"
    description = ("SMT secuencial (Quarterly Theory): compara NAS100, SP500 y DJ30 y avisa cuando, en cuartos consecutivos de un ciclo (semana, día, 90 minutos), "
                   "uno rompe el máximo o mínimo del cuarto anterior y otro no. Solo informa, no envía órdenes.")
    subscribes = ("candles.loaded", "clock.offset")
    publishes = ("smt.updated", "smt.detected")
    slot = "aux2"

    def on_start(self) -> None:
        self.error = "Configuración SMT no válida"
        self._offset: int | None = None
        self._velas: dict[str, tuple] = {}              # activo de la tríada -> (ts, open, high, low, close)
        self._seen: set = set()
        try:
            self._load_settings()
        except ValueError as exc:
            self.error = str(exc)
            raise
        self.error = ""
        self.set_caption("esperando los tres índices")

    def _load_settings(self) -> None:
        # tradingbot.env, bloque SMT: SMT_TF, SMT_TRIAD, SMT_CICLOS, SMT_DAYS
        self.tf = str(self.settings.get("TF", DEFAULT_TF))
        parse_timeframe(self.tf)
        self.triad = tuple(n.upper() for n in self.settings.get_list("TRIAD", list(DEFAULT_TRIAD)))
        if len(self.triad) < 2:
            raise ValueError("SMT_TRIAD necesita al menos dos activos.")
        self.ciclos = tuple(n.lower() for n in self.settings.get_list("CICLOS", list(DEFAULT_CICLOS)))
        bad = [n for n in self.ciclos if n not in ciclos.CICLOS]
        if bad or not self.ciclos:
            raise ValueError(f"SMT_CICLOS={', '.join(self.ciclos)}: ciclo desconocido {', '.join(bad)}. Disponibles: {', '.join(ciclos.CICLOS)}.")
        self.days = self.settings.get_int("DAYS", 10)
        if self.days < 2:
            raise ValueError(f"SMT_DAYS={self.days} debe ser 2 o más.")

    def _activo(self, symbol: str) -> str | None:
        name = symbol.strip().upper()
        return next((t for t in self.triad if name.startswith(t)), None)

    def handle(self, event: Event) -> None:
        if self.error:
            raise ValueError(self.error)
        if event.topic == "clock.offset":
            if event.payload.get("server_offset") == self._offset:
                return
            self._offset = event.payload.get("server_offset")
        else:
            p = event.payload
            activo = self._activo(p["symbol"])
            if activo is None or p["timeframe"] != self.tf:
                return
            df = p["df"].iloc[:-1]                      # la última vela sigue formándose
            if len(df) < 10:
                return
            self._velas[activo] = (df["ts"].to_numpy(np.int64), *(df[k].to_numpy(float) for k in ("open", "high", "low", "close")))
        if len(self._velas) == len(self.triad):
            self.update()

    def update(self) -> None:
        ahead, _ = server_minus_ny(self._offset)
        last = min(int(v[0][-1]) for v in self._velas.values())
        first = last - self.days * 86400
        series = {}
        for sym, (ts, *rest) in self._velas.items():
            i = int(np.searchsorted(ts, first))
            series[sym] = (ts[i:], *(r[i:] for r in rest))
        tf_min = minutes(self.tf)
        by_cycle = {ciclo: detectar(series, ciclo, ahead, tf_min, last)[-KEEP_EVENTS:] for ciclo in self.ciclos}
        events = sorted((e for lst in by_cycle.values() for e in lst), key=lambda e: e.ts)
        self.publish("smt.updated", {"triad": self.triad, "timeframe": self.tf, "ciclos": by_cycle, "events": events})
        if events:
            e = events[-1]
            self.set_caption(f"{e.ciclo} {e.etiqueta} {'▼' if e.direccion == 'bajista' else '▲'} {e.rompen[0]}")
        else:
            self.set_caption("sin SSMT reciente")
        for e in events:
            key = (e.ciclo, e.cuarto, e.direccion, e.ts)
            if key not in self._seen:
                self._seen.add(key)
                self.publish("smt.detected", {"smt": e, "triad": self.triad, "timeframe": self.tf})
