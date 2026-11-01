"""Escenario sintético de CRT para los tests: un corto completo en M5 (hora de servidor = NY + 7 h), construido a mano.

Cronología (hora de Nueva York):
  día 1 12:00-12:45  caída que deja un FVG bajista en M15 con la zona 107.5-110 (sin mitigar después)
  día 2 03:00-06:00  C1 (H3): rango 100-105
  día 2 06:00-09:00  C2: sube barriendo el máximo de C1 (105), llega a 108.5 (dentro del FVG), invierte el FVG de M5 y cierra por
                     debajo de la apertura de la secuencia alcista (CISD) a las 06:35; entrada en la apertura de las 06:40
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


def scenario(fvg: bool = True) -> pd.DataFrame:
    """`fvg=False`: la misma historia con una caída continua el día 1, sin hueco (no hay FVG de MTF que tocar)."""
    rows: list[tuple] = []
    rows += _fill("2026-10-12 08:00", "2026-10-12 12:00", 101, 111, 0.1)          # sube hasta el FVG del día 1
    if fvg:
        # velas M15 de 12:00, 12:15 y 12:30: vela 1 con mínimo 110, caída fuerte, vela 3 con máximo 107.5 -> FVG bajista 107.5-110
        t = _server_ts("2026-10-12 12:00")
        for i, (o, h, l, c) in enumerate([(111, 112, 110.2, 111.5), (111.5, 112, 110.1, 110.5), (110.5, 111.0, 110.0, 110.3),
                                           (110.3, 110.4, 108.0, 108.2), (108.2, 108.4, 106.5, 107.0), (107.0, 107.2, 106.0, 106.2),
                                           (106.2, 107.5, 105.8, 107.0), (107.0, 107.4, 105.6, 106.0), (106.0, 106.8, 105.5, 106.3)]):
            rows.append((t + i * STEP, o, h, l, c))
    else:
        rows += _fill("2026-10-12 12:00", "2026-10-12 12:45", 111, 106.3, 0.8)
    rows += _fill("2026-10-12 12:45", "2026-10-12 15:00", 106.3, 101.0, 0.1)
    rows += _fill("2026-10-12 15:00", "2026-10-13 03:00", 101.0, 102.0, 0.1)
    # C1: de 03:00 a 06:00 NY, rango 100-105
    t = _server_ts("2026-10-13 03:00")
    c1 = [(102, 103, 101.5, 102.5)] * 6 + [(102.5, 105.0, 102.0, 104.0)] * 6 + [(104.0, 104.2, 100.0, 100.5)] * 6 + \
         [(100.5, 101.5, 100.1, 101.0)] * 6 + [(101.0, 104.5, 100.8, 103.3)] * 6 + [(103.3, 103.6, 102.9, 103.3)] * 6
    rows += [(t + i * STEP, *bar) for i, bar in enumerate(c1)]
    # C2: de 06:00 a 09:00 NY
    t = _server_ts("2026-10-13 06:00")
    c2 = [(103.3, 103.4, 102.8, 103.0)] * 3                                          # 06:00-06:10 laterales y bajistas
    c2 += [(103.2, 104.1, 103.1, 104.0),                                             # 06:15 r1: apertura de la secuencia alcista
           (104.0, 105.1, 103.9, 105.0),                                             # 06:20 r2: supera el máximo de C1 (105)
           (105.0, 106.1, 104.9, 106.0),                                             # 06:25 r3
           (106.1, 107.5, 106.0, 107.4),                                             # 06:30 r4: FVG alcista de M5 (105.1-106.0)
           (107.4, 108.5, 107.3, 108.2),                                             # 06:35 r5: extremo del sweep (108.5, dentro del FVG)
           (108.2, 108.3, 106.5, 107.0),                                             # 06:40 d1
           (107.0, 107.1, 105.0, 105.5),                                             # 06:45 d2: cierra bajo el FVG: iFVG
           (105.5, 105.6, 103.0, 103.1)]                                             # 06:50 d3: cierra bajo 103.2: CISD
    c2 += [(103.1, 103.2, 100.0, 100.5), (100.5, 100.6, 98.0, 98.5), (98.5, 98.6, 95.0, 95.5), (95.5, 95.6, 92.0, 92.1)]
    c2 += [(92.1, 92.5, 91.5, 92.0)] * (36 - len(c2))
    rows += [(t + i * STEP, *bar) for i, bar in enumerate(c2)]
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
