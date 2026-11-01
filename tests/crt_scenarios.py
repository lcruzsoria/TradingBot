"""Escenario sintético de CRT para los tests: un corto completo en M5 (hora de servidor = NY + 7 h), construido a mano.

Cronología (hora de Nueva York):
  día 1 12:00-12:45  caída que deja un FVG bajista en M15 con la zona 107.5-110 (sin mitigar después)
  día 2 03:00-06:00  C1 (H3): rango 100-105
  día 2 06:00-09:00  C2: sube barriendo el máximo de C1 (105), llega a 108.5 (dentro del FVG), invierte el FVG de M5 y cierra por
                     debajo de la apertura de la secuencia alcista (CISD) a las 06:50; entrada en la apertura de las 06:55

Variantes del FVG de MTF (`scenario(fvg=...)`):
  True      el FVG bajista de M15 es de antes de C1 y queda por encima de su máximo (105): cumple la regla
  False     sin hueco: no hay ningún FVG que tocar
  "en_c1"   el FVG se forma al empezar C1: su vela 3 es la primera de C1 y su máximo (107.5) es el máximo de C1, así que el borde
            inferior de la zona coincide con ese máximo y no queda por encima (caso del 05/10/2026 en NAS100)
"""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

AHEAD = 7 * 3600
STEP = 300


def _server_ts(ny: str) -> int:
    return int(datetime.fromisoformat(ny).replace(tzinfo=timezone.utc).timestamp()) + AHEAD


def _fill(start: str, end: str, a: float, b: float, noise: float = 0.15) -> list[tuple]:
    """Velas M5 que van de `a` a `b` entre dos horas NY (sin incluir `end`)."""
    t0, t1 = _server_ts(start), _server_ts(end)
    n = (t1 - t0) // STEP
    rows, prev = [], a
    for i in range(n):
        close = a + (b - a) * (i + 1) / n
        rows.append((t0 + i * STEP, prev, max(prev, close) + noise, min(prev, close) - noise, close))
        prev = close
    return rows


def _bars(start: str, bars: list[tuple]) -> list[tuple]:
    t = _server_ts(start)
    return [(t + i * STEP, *bar) for i, bar in enumerate(bars)]


def _c1_previo(con_hueco: bool = True) -> list[tuple]:
    """Día 1 con el FVG de M15 antes de C1 (o la misma caída continua, sin hueco), y C1 (03:00-06:00 del día 2) con rango 100-105."""
    rows = _fill("2026-10-12 08:00", "2026-10-12 12:00", 101, 111, 0.1)               # sube hasta el FVG del día 1
    if con_hueco:
        # velas M15 de 12:00, 12:15 y 12:30: vela 1 con mínimo 110, caída fuerte, vela 3 con máximo 107.5 -> FVG bajista 107.5-110
        rows += _bars("2026-10-12 12:00", [(111, 112, 110.2, 111.5), (111.5, 112, 110.1, 110.5), (110.5, 111.0, 110.0, 110.3),
                                           (110.3, 110.4, 108.0, 108.2), (108.2, 108.4, 106.5, 107.0), (107.0, 107.2, 106.0, 106.2),
                                           (106.2, 107.5, 105.8, 107.0), (107.0, 107.4, 105.6, 106.0), (106.0, 106.8, 105.5, 106.3)])
    else:
        rows += _fill("2026-10-12 12:00", "2026-10-12 12:45", 111, 106.3, 0.8)       # la misma caída pero continua, sin hueco
    rows += _fill("2026-10-12 12:45", "2026-10-12 15:00", 106.3, 101.0, 0.1)
    rows += _fill("2026-10-12 15:00", "2026-10-13 03:00", 101.0, 102.0, 0.1)
    rows += _bars("2026-10-13 03:00", [(102, 103, 101.5, 102.5)] * 6 + [(102.5, 105.0, 102.0, 104.0)] * 6 + [(104.0, 104.2, 100.0, 100.5)] * 6 +
                  [(100.5, 101.5, 100.1, 101.0)] * 6 + [(101.0, 104.5, 100.8, 103.3)] * 6 + [(103.3, 103.6, 102.9, 103.3)] * 6)
    return rows


def _c1_en_c1() -> list[tuple]:
    """El FVG de M15 se forma al empezar C1 (vela 3 = 03:00-03:15) y su máximo, 107.5, es el máximo de C1 (rango 100.5-107.5)."""
    rows = _fill("2026-10-12 08:00", "2026-10-13 02:30", 101, 111, 0.1)
    rows += _bars("2026-10-13 02:30", [(111, 112, 110.4, 111.5), (111.5, 112, 110.3, 110.6), (110.6, 111.0, 110.2, 110.4),   # vela 1 (02:30-02:45)
                                       (110.4, 110.5, 108.5, 108.8), (108.8, 109.0, 107.0, 107.4), (107.4, 107.6, 106.2, 106.4),   # vela 2 (02:45-03:00)
                                       (106.4, 107.5, 106.0, 107.0), (107.0, 107.4, 105.9, 106.1), (106.1, 106.9, 105.8, 106.0)])  # vela 3 (03:00-03:15)
    rows += _fill("2026-10-13 03:15", "2026-10-13 04:30", 106.0, 100.5, 0.1)
    rows += _fill("2026-10-13 04:30", "2026-10-13 06:00", 100.5, 103.3, 0.1)
    return rows


def _c2() -> list[tuple]:
    c2 = [(103.3, 103.4, 102.8, 103.0)] * 3                                          # 06:00-06:10 laterales y bajistas
    c2 += [(103.2, 104.1, 103.1, 104.0),                                             # 06:15 r1: apertura de la secuencia alcista
           (104.0, 105.1, 103.9, 105.0),                                             # 06:20 r2: supera el máximo de C1 (105)
           (105.0, 106.1, 104.9, 106.0),                                             # 06:25 r3
           (106.1, 107.4, 106.0, 107.4),                                             # 06:30 r4: FVG alcista de M5 (105.1-106.0)
           (107.4, 108.5, 107.3, 108.2),                                             # 06:35 r5: extremo del sweep (108.5, dentro del FVG)
           (108.2, 108.3, 106.5, 107.0),                                             # 06:40 d1
           (107.0, 107.1, 105.0, 105.5),                                             # 06:45 d2: cierra bajo el FVG: iFVG
           (105.5, 105.6, 103.0, 103.1)]                                             # 06:50 d3: cierra bajo 103.2: CISD
    c2 += [(103.1, 103.2, 100.0, 100.5), (100.5, 100.6, 98.0, 98.5), (98.5, 98.6, 95.0, 95.5), (95.5, 95.6, 92.0, 92.1)]
    c2 += [(92.1, 92.5, 91.5, 92.0)] * (36 - len(c2))
    return _bars("2026-10-13 06:00", c2)


def scenario(fvg: bool | str = True) -> pd.DataFrame:
    """`fvg=True`: el FVG bajista de M15 es de antes de C1 y queda por encima de su máximo. `fvg=False`: caída continua el día 1, sin
    hueco (no hay FVG de MTF que tocar). `fvg="en_c1"`: el borde inferior del FVG coincide con el máximo de C1."""
    rows = _c1_en_c1() if fvg == "en_c1" else _c1_previo(bool(fvg))
    rows += _c2()
    df = pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close"])
    df["spread"] = 0.1
    df["tick_volume"] = 0
    return df


def mirror(df: pd.DataFrame, k: float = 200.0) -> pd.DataFrame:
    """El mismo mercado puesto del revés (precio -> k - precio): los cortos pasan a largos y al revés."""
    out = df.copy()
    out["open"], out["close"] = k - df["open"], k - df["close"]
    out["high"], out["low"] = k - df["low"], k - df["high"]
    return out
