"""Setup de continuación sobre una TBR: toma de liquidez, retest del 50 %, segunda ruptura y entrada límite.

La TBR (Asia, London, Pre-NY, NY-AM, NY-PM...) ya cerrada es el rango de trabajo. Se anotan sus tres niveles clave:
High, Low y 50 %. Largo (el corto es el espejo exacto, con el Low):

1. Toma de liquidez   una vela supera el High del rango.
2. Retest del 50 %    el precio vuelve al rango y TOCA el 50 % (con mecha o con cierre, da igual). Si no lo toca no
                      hay rango ni setup.
3. Segunda ruptura    el precio vuelve a superar el High, por el mismo lado que en el paso 1.

Entrada: orden LÍMITE en el High, el nivel que se rompió en los pasos 1 y 3 (sin esperar confirmación).
Stop: bajo el mínimo del paso 2 (el más bajo entre la toma y la segunda ruptura). Objetivo: el nivel -1 de Fibonacci,
un rango completo sobre el High (el doble del rango contado desde el Low).

Reglas de limpieza:
- Se invalida si, antes de la segunda ruptura, el precio toma el lado contrario (el Low en un largo).
- La orden límite caduca si el precio llega al objetivo sin haberla llenado, o pasada la ventana de validez.
- Un setup por TBR y por lado.
- Si en una misma vela caben el stop y el objetivo, se cuenta el stop (lo pesimista).

El bot NO envía órdenes: los setups solo se publican e informan.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np


# Valores por defecto (se cambian en tradingbot.env, bloque SETUP)
DEFAULT_WINDOW_HOURS = 24      # tiempo, desde que acaba la TBR, para completar los tres pasos y llenar la orden
DEFAULT_TP_RANGES = 1.0        # objetivo: rangos por encima del High (1 = nivel -1 de Fibonacci)
KINDS = ("continuation",)
DEFAULT_KINDS = KINDS

# Estados, de menos a más avanzado
WAITING = ("sweep", "retest")           # esperando el retest del 50 % / la segunda ruptura
LIVE = ("sweep", "retest", "armed", "filled")
STATUS_NAMES = {
    "sweep": "esperando el retest del 50 %", "retest": "esperando la segunda ruptura",
    "armed": "orden límite activa", "filled": "entrada ejecutada, en curso",
    "target": "objetivo alcanzado", "stop": "stop alcanzado",
    "expired": "caducado", "invalid": "invalidado",
}


@dataclass(frozen=True)
class Setup:
    zone: str                  # nombre de la TBR (p. ej. "NY-AM")
    zone_key: str
    day: date                  # día (hora de NY) en que empezó la TBR
    direction: str             # "long" (toma el High) o "short" (toma el Low)
    high: float                # los tres niveles clave de la TBR
    low: float
    mid: float
    sweep_x: int               # vela del paso 1
    status: str                # ver STATUS_NAMES
    note: str = ""             # por qué caducó o se invalidó
    retest_x: int | None = None    # vela del paso 2
    rebreak_x: int | None = None   # vela del paso 3
    fill_x: int | None = None      # vela en la que se llena la orden límite
    end_x: int | None = None       # vela en la que acaba (objetivo, stop, caducidad o invalidación)
    entry: float | None = None
    stop: float | None = None
    target: float | None = None
    kind: str = "continuation"

    @property
    def level(self) -> float:
        """Nivel cuya liquidez se toma y donde está la entrada: el High en un largo, el Low en un corto."""
        return self.high if self.direction == "long" else self.low

    @property
    def side(self) -> str:
        return "high" if self.direction == "long" else "low"

    @property
    def live(self) -> bool:
        return self.status in LIVE

    @property
    def rr(self) -> float | None:
        if None in (self.entry, self.stop, self.target) or self.entry == self.stop:
            return None
        return abs(self.target - self.entry) / abs(self.entry - self.stop)

    @property
    def label(self) -> str:
        """Texto corto, p. ej. "Continuación Long en NY-AM: orden límite activa"."""
        return f"Continuación {self.direction.capitalize()} en {self.zone}: {STATUS_NAMES[self.status]}"


def detect(sessions, high, low, window_bars: int, zones: list[str] | None = None,
           tp_ranges: float = DEFAULT_TP_RANGES, kinds=DEFAULT_KINDS) -> list[Setup]:
    """Setups de las TBR ya calculadas (tradingbot.skills.tbr.zones.Session), ordenados por vela de la toma.

    `high` y `low` son las de las mismas velas con las que se calcularon las TBR. `window_bars`: velas de validez desde
    que acaba la TBR. `zones`: claves a vigilar (None = todas).
    """
    if "continuation" not in kinds:
        return []
    h, l = np.asarray(high, dtype=float), np.asarray(low, dtype=float)
    n = len(h)
    wanted = {z.upper() for z in zones} if zones else None
    out: list[Setup] = []
    for s in sessions:
        if not s.complete or s.high <= s.low or (wanted is not None and s.zone.key not in wanted):
            continue
        start = int(s.x1 + 0.5)                        # primera vela tras la TBR
        if start >= n:
            continue
        for flip in (1, -1):                           # 1: toma el High (largo); -1: espejo, toma el Low (corto)
            setup = _scan(s, h, l, start, window_bars, tp_ranges, flip)
            if setup is not None:
                out.append(setup)
    out.sort(key=lambda st: (st.sweep_x, st.direction))
    return out


def _scan(s, h, l, start: int, window: int, tp_ranges: float, flip: int) -> Setup | None:
    n = len(h)
    if flip == 1:
        hh, ll, top, bot = h, l, s.high, s.low
    else:
        hh, ll, top, bot = -l, -h, -s.low, -s.high     # espejo: el corto es un largo sobre precios cambiados de signo
    mid, rng = (top + bot) / 2, top - bot
    end = min(n, start + window)
    expired_by_time = start + window <= n - 1          # ya pasó la ventana con datos de sobra

    def make(status, sweep_x, note="", **kw) -> Setup:
        def real(v):                                   # de vuelta a precios reales
            return None if v is None else flip * v
        return Setup(s.zone.name, s.zone.key, s.day, "long" if flip == 1 else "short", s.high, s.low,
                     (s.high + s.low) / 2, sweep_x, status, note, kw.get("retest_x"), kw.get("rebreak_x"),
                     kw.get("fill_x"), kw.get("end_x"), real(kw.get("entry")), real(kw.get("stop")),
                     real(kw.get("target")))

    # paso 1: toma de liquidez (si antes o a la vez se toma el lado contrario, no hay setup)
    i = next((q for q in range(start, end) if hh[q] > top or ll[q] < bot), None)
    if i is None or ll[i] < bot:
        return None
    # paso 2: el precio toca el 50 % sin tomar el lado contrario
    j = next((q for q in range(i + 1, end) if ll[q] <= mid), None)
    if j is None:
        return make("expired", i, "no volvió al 50 %", end_x=end - 1) if expired_by_time else make("sweep", i)
    if ll[j] <= bot:
        return make("invalid", i, "tomó el lado contrario antes de la segunda ruptura", retest_x=j, end_x=j)
    # paso 3: segunda ruptura por el mismo lado
    k = next((q for q in range(j + 1, end) if hh[q] > top or ll[q] <= bot), None)
    if k is None:
        return (make("expired", i, "sin segunda ruptura", retest_x=j, end_x=end - 1) if expired_by_time
                else make("retest", i, retest_x=j))
    if ll[k] <= bot:
        return make("invalid", i, "tomó el lado contrario antes de la segunda ruptura", retest_x=j, end_x=k)
    entry, stop = top, float(ll[i + 1:k].min())          # stop: mínimo del paso 2
    target = top + tp_ranges * rng
    common = dict(retest_x=j, rebreak_x=k, entry=entry, stop=stop, target=target)
    if stop >= entry:
        return make("invalid", i, "stop sin recorrido", end_x=k, **common)
    # orden límite en el nivel: se llena en la primera vela que lo toca; caduca si antes llega al objetivo
    last = min(n, k + 1 + window)
    m = None
    for q in range(k + 1, last):
        if ll[q] <= entry:
            m = q
            break
        if hh[q] >= target:
            return make("expired", i, "el precio llegó al objetivo sin llenar la orden", end_x=q, **common)
    if m is None:
        if k + 1 + window <= n - 1:
            return make("expired", i, "la orden no se llenó dentro de la ventana", end_x=last - 1, **common)
        return make("armed", i, **common)
    for q in range(m, min(n, m + 1 + 2 * window)):          # resultado, con el stop primero si caben los dos
        if ll[q] <= stop:
            return make("stop", i, fill_x=m, end_x=q, **common)
        if hh[q] >= target:
            return make("target", i, fill_x=m, end_x=q, **common)
    return make("filled", i, fill_x=m, **common)
