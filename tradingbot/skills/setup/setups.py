"""Setups de la estrategia: tomas de liquidez en el High o el Low de las zonas TBR.

Cuando termina una zona TBR (Asia, London, NY-AM...), su High y su Low quedan como liquidez: encima del High hay stops
de cortos y debajo del Low, stops de largos. La primera vela que supera uno de esos niveles lo "toma" (la skill TBR ya
marca cuál es). A partir de esa vela se esperan `confirm_bars` velas (contando la de la toma) y se mira dónde cierra la
última de ellas:

- Toma del High y cierre POR ENCIMA del High   -> continuación alcista (Long): el precio acepta por encima.
- Toma del High y cierre DE VUELTA por debajo  -> reversión bajista (Short): barrido de liquidez y rechazo.
- Toma del Low  y cierre POR DEBAJO del Low    -> continuación bajista (Short).
- Toma del Low  y cierre DE VUELTA por encima  -> reversión alcista (Long).

Mientras no hayan cerrado las velas de confirmación, el setup está "pendiente" (sin dirección).
Es la primera versión de la estrategia: aquí se irán añadiendo los filtros (sesgo, TDO, horario...).
El bot NO envía órdenes: los setups solo se publican e informan.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np


# Valores por defecto (se cambian en tradingbot.env, bloque SETUP)
DEFAULT_CONFIRM_BARS = 3
KINDS = ("reversal", "continuation")
DEFAULT_KINDS = KINDS
KIND_NAMES = {"reversal": "Reversión", "continuation": "Continuación", "pending": "Pendiente"}


@dataclass(frozen=True)
class Setup:
    zone: str            # nombre de la zona TBR (p. ej. "NY-AM")
    zone_key: str        # clave de la zona (p. ej. "NY_AM")
    day: date            # día (hora de NY) en que empezó la zona
    side: str            # liquidez tomada: "high" o "low"
    level: float         # precio del nivel tomado
    sweep_x: int         # vela (índice) que toma el nivel
    kind: str            # "reversal", "continuation" o "pending"
    direction: str | None   # "long", "short" o None mientras está pendiente
    confirm_x: int | None   # vela que confirma (cierre de la última vela de confirmación)

    @property
    def label(self) -> str:
        """Texto corto, p. ej. "Reversión Short en el High de NY-AM"."""
        where = f"el {'High' if self.side == 'high' else 'Low'} de {self.zone}"
        if self.direction is None:
            return f"Toma de liquidez en {where} (pendiente)"
        return f"{KIND_NAMES[self.kind]} {self.direction.capitalize()} en {where}"


def classify(side: str, level: float, close: float) -> tuple[str, str]:
    """(tipo, dirección) según dónde cierra la vela de confirmación respecto al nivel tomado."""
    if side == "high":
        return ("continuation", "long") if close > level else ("reversal", "short")
    return ("continuation", "short") if close < level else ("reversal", "long")


def detect(sessions, close, confirm_bars: int = DEFAULT_CONFIRM_BARS, zones: list[str] | None = None,
           kinds=DEFAULT_KINDS) -> list[Setup]:
    """Setups de las zonas TBR ya calculadas (tradingbot.skills.tbr.zones.Session), ordenados por vela de la toma.

    `close` son los cierres de las mismas velas con las que se calcularon las zonas. `zones`: claves de zona a vigilar
    (None = todas). `kinds`: tipos que interesan; los pendientes siempre se incluyen.
    """
    close = np.asarray(close, dtype=float)
    n = len(close)
    wanted = {z.upper() for z in zones} if zones else None
    out: list[Setup] = []
    for s in sessions:
        if not s.complete or (wanted is not None and s.zone.key not in wanted):
            continue
        for level in s.levels:
            if level.kind not in ("high", "low") or not level.taken:
                continue
            i = int(round(level.x1))
            if not 0 <= i < n:
                continue
            j = i + confirm_bars - 1
            if j >= n:
                kind, direction, confirm_x = "pending", None, None
            else:
                kind, direction = classify(level.kind, level.price, float(close[j]))
                confirm_x = j
                if kind not in kinds:
                    continue
            out.append(Setup(s.zone.name, s.zone.key, s.day, level.kind, level.price, i, kind, direction, confirm_x))
    out.sort(key=lambda st: (st.sweep_x, st.side))
    return out
