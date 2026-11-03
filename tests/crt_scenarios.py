"""Escenario sintético de CRT para los tests: un corto completo en M5 (hora de servidor = NY + 7 h), construido a mano.

Cronología (hora de Nueva York):
  día 1 08:00-día 2 03:00  mercado de relleno (sube y baja sin dejar huecos de MTF)
  día 2 03:00-06:00        C1 (H3): rango 100-105
  día 2 06:00-09:00        C2: sube barriendo el máximo de C1 (105) hasta el extremo 108.5 (06:35); el desplazamiento a la baja deja un FVG
                           bajista de M15 con la zona 103.2-107.3 (formado a las 07:15, DESPUÉS del extremo); el precio vuelve a él
                           (07:15, toca 103.2); en M5 la vuelta deja un FVG alcista 103.4-104.9 y a las 07:30 una vela cierra bajo su base
                           (103.4): iFVG invertido = CISD; entrada en la apertura de las 07:35 (103.1); el precio cae al objetivo (92.3)
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


def _c1() -> list[tuple]:
    """Relleno del día 1 y C1 (03:00-06:00 del día 2) con rango 100-105."""
    rows = _fill("2026-10-12 08:00", "2026-10-12 12:00", 101, 111, 0.1)
    rows += _fill("2026-10-12 12:00", "2026-10-12 15:00", 111, 101.0, 0.1)
    rows += _fill("2026-10-12 15:00", "2026-10-13 03:00", 101.0, 102.0, 0.1)
    rows += _bars("2026-10-13 03:00", [(102, 103, 101.5, 102.5)] * 6 + [(102.5, 105.0, 102.0, 104.0)] * 6 + [(104.0, 104.2, 100.0, 100.5)] * 6 +
                  [(100.5, 101.5, 100.1, 101.0)] * 6 + [(101.0, 104.5, 100.8, 103.3)] * 6 + [(103.3, 103.6, 102.9, 103.3)] * 6)
    return rows


def _c2() -> list[tuple]:
    c2 = [(103.3, 103.4, 102.8, 103.0)] * 3                                          # 06:00-06:10 laterales
    c2 += [(103.2, 104.1, 103.1, 104.0),                                             # 06:15
           (104.0, 105.1, 103.9, 105.0),                                             # 06:20 supera el máximo de C1 (105): empieza el sweep
           (105.0, 107.5, 104.9, 107.4),                                             # 06:25
           (107.4, 108.0, 107.3, 107.9),                                             # 06:30 vela 1 del FVG de M15 (mínimo 107.3 de 06:30-06:45)
           (107.9, 108.5, 107.8, 108.2),                                             # 06:35 extremo del sweep (108.5)
           (108.2, 108.3, 107.6, 107.7),                                             # 06:40
           (107.7, 107.8, 105.5, 105.6),                                             # 06:45 vela 2 del FVG de M15: desplazamiento a la baja
           (105.6, 105.9, 103.5, 103.6),                                             # 06:50
           (103.6, 104.0, 102.0, 102.2),                                             # 06:55
           (102.2, 103.0, 101.0, 101.5),                                             # 07:00 vela 3 del FVG de M15 (máximo 103.2 de 07:00-07:15)
           (101.5, 102.4, 100.8, 102.0),                                             # 07:05
           (102.0, 103.2, 101.5, 102.8),                                             # 07:10 -> FVG bajista de M15 103.2-107.3, formado a las 07:15
           (102.8, 103.4, 102.6, 103.3),                                             # 07:15 el precio vuelve al FVG (máximo 103.4 >= 103.2)
           (103.3, 105.2, 103.2, 105.1),                                             # 07:20
           (105.1, 106.0, 104.9, 105.9),                                             # 07:25 FVG alcista de M5 (103.4-104.9)
           (105.9, 106.0, 103.0, 103.1)]                                             # 07:30 cierra bajo 103.4: iFVG invertido = CISD
    c2 += [(103.1, 103.2, 100.0, 100.5), (100.5, 100.6, 98.0, 98.5), (98.5, 98.6, 95.0, 95.5), (95.5, 95.6, 92.0, 92.1)]       # 07:35-07:50
    c2 += [(92.1, 92.5, 91.5, 92.0)] * (36 - len(c2))
    return _bars("2026-10-13 06:00", c2)


def scenario() -> pd.DataFrame:
    df = pd.DataFrame(_c1() + _c2(), columns=["ts", "open", "high", "low", "close"])
    df["spread"] = 0.1
    df["tick_volume"] = 0
    return df


def mirror(df: pd.DataFrame, k: float = 200.0) -> pd.DataFrame:
    """El mismo mercado puesto del revés (precio -> k - precio): los cortos pasan a largos y al revés."""
    out = df.copy()
    out["open"], out["close"] = k - df["open"], k - df["close"]
    out["high"], out["low"] = k - df["low"], k - df["high"]
    return out


def eurusd(pad: int = 150) -> pd.DataFrame:
    """EURUSD M5 real del 02/11/2026 de las 17:00 a las 23:55 NY (tests/crt_eurusd_20261102.py), con `pad` velas planas delante para llegar al mínimo de
    la skill. Largo por zona común: C2 de las 21:00 (H4) barre el mínimo de C1 (1.11808); el FVG de M15 1.11814-1.11833 y el iFVG de M5 1.11815-1.11834
    comparten la zona 1.11815-1.11833; el iFVG se invierte a las 21:55; pullback a la zona a las 22:10 (de arriba abajo); la vela de las 22:25 cierra
    con cuerpo sobre el CISD (1.11841); entrada a las 22:30 en 1.11843 con stop en 1.1177."""
    from crt_eurusd_20261102 import BARS
    first = _server_ts(f"2026-11-02 {BARS[0][0]}")
    rows = [(first - (pad - i) * STEP, BARS[0][1], BARS[0][1], BARS[0][1], BARS[0][1]) for i in range(pad)]
    rows += [(_server_ts(f"2026-11-02 {hhmm}"), o, h, l, c) for hhmm, o, h, l, c in BARS]
    return pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close"])
