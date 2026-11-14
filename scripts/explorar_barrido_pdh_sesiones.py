"""Exploración: barrido del PDH/PDL del día de trading anterior en distintas ventanas del día (Londres, pre-NY, apertura, RTH, tarde), con las reglas del setup de Asia:
nivel fresco (no tocado desde las 18:00 hasta el inicio de la ventana), barrido dentro de la ventana, entrada al cierre de la primera vela que cierra de vuelta
dentro, stop fijo por mercado (o swing + buffer), una operación por día (el lado cuya entrada cierra antes). Salidas: tiempo, 1R, 2R, 3R. Sin costes.

    uv run --with pyarrow python scripts/explorar_barrido_pdh_sesiones.py [--sin-fresco]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tradingbot.skills.setup.positions import resolve  # noqa: E402

SYMBOLS = ("NAS100.s", "SP500.s", "DJ30.s")
STOPS = {"NAS100.s": (30.0, 5.0), "SP500.s": (5.0, 1.5), "DJ30.s": (20.0, 10.0)}
AHEAD = 7 * 3600
DAY = 86400
H = 3600
VELAS = Path("C:/Users/claude/DEV/TradingBot/analisis/5m/puprime")
TF = 5
VENTANAS = [("Asia (ref.)", "20:00", "21:00"),
            ("Londres", "02:00", "03:00"), ("Londres ampl.", "02:00", "04:00"), ("Londres", "02:00", "05:00"), ("Londres tarde", "03:00", "05:00"),
            ("Pre-NY", "05:00", "08:00"), ("Pre-NY", "06:00", "09:00"),
            ("Apertura", "08:30", "09:30"), ("Apertura NY", "09:30", "10:30"), ("Apertura NY", "09:30", "11:00"), ("RTH 9-10", "09:00", "10:00"),
            ("RTH", "10:00", "11:00"), ("RTH", "10:00", "12:00"),
            ("Mediodía", "11:00", "13:00"), ("Tarde", "12:00", "14:00"), ("Tarde", "13:30", "15:30"), ("Tarde", "14:00", "16:00")]
SALIDAS = (("tiempo", None), ("1R", 1.0), ("2R", 2.0), ("3R", 3.0))


def hm(t: str) -> int:
    h, m = t.split(":")
    return (int(h) * 60 + int(m)) * 60


def cargar(sym: str):
    df = pd.read_parquet(VELAS / f"{sym}.parquet").iloc[:-1]
    return tuple(df[k].to_numpy(np.int64 if k == "ts" else float) for k in ("ts", "open", "high", "low", "close"))


def operaciones(sym: str, datos, ini: str, fin: str, fresco: bool) -> dict:
    """Operaciones por salida: {nombre: [dict, ...]}, una por día de trading."""
    ts, o, h, l, c = datos
    ny = ts - AHEAD
    td = (ny - 18 * H) // DAY                                   # día de trading (empieza a las 18:00 NY)
    sd = (ny - 18 * H) % DAY                                    # segundos desde las 18:00
    ws, we = (hm(ini) - 18 * H) % DAY, (hm(fin) - 18 * H) % DAY
    we = we if we > ws else we + DAY
    puntos, buffer = STOPS[sym]
    cortes = np.flatnonzero(np.diff(td)) + 1
    ini_d = np.concatenate(([0], cortes))
    fin_d = np.concatenate((cortes, [len(ts)]))
    out = {n: [] for n, _ in SALIDAS}
    for k in range(1, len(ini_d)):
        a, b = ini_d[k], fin_d[k]
        pa, pb = ini_d[k - 1], fin_d[k - 1]
        if td[a] - td[pa] != 1 or (b - a) < 150 or (pb - pa) < 150:
            continue
        pdh, pdl = float(h[pa:pb].max()), float(l[pa:pb].min())
        idx = np.arange(a, b)
        win = idx[(sd[idx] >= ws) & (sd[idx] < we)]
        if len(win) < 3:
            continue
        first, last = int(win[0]), int(win[-1])
        cand = []
        for up in (True, False):
            nivel = pdh if up else pdl
            if fresco and first > a and ((h[a:first].max() >= nivel) if up else (l[a:first].min() <= nivel)):
                continue
            hit = np.flatnonzero(h[first:last + 1] > nivel) if up else np.flatnonzero(l[first:last + 1] < nivel)
            if not hit.size:
                continue
            sw = first + int(hit[0])
            back = np.flatnonzero(c[sw:last + 1] < nivel) if up else np.flatnonzero(c[sw:last + 1] > nivel)
            if not back.size:
                continue
            cand.append((sw + int(back[0]), sw, up))
        if not cand:
            continue
        e, sw, up = min(cand)
        close = float(c[e])
        sign = 1.0 if up else -1.0
        extremo = float(h[sw:e + 1].max() if up else l[sw:e + 1].min())
        stop = close + sign * puntos if sign * (extremo - close) <= puntos else extremo + sign * buffer
        riesgo = abs(stop - close)
        if riesgo <= 0:
            continue
        direccion = "short" if up else "long"
        entry_ts = int(ts[e]) + TF * 60
        fin_dia = int(ts[b - 1]) + TF * 60
        for nombre, rr in SALIDAS:
            if rr is None:
                target = close - sign * 1e7                      # nunca se toca: sale por tiempo (18:00 NY) o en el stop
            else:
                target = close - sign * rr * riesgo
            order = SimpleNamespace(direction=direccion, price=close, stop=stop, target=target, entry_ts=entry_ts, close_ts=fin_dia, be_price=None, solo_tiempo=rr is None)
            done = resolve(order, ts, h, l, c, None, TF * 60)
            if done is not None:
                out[nombre].append({"day": int(td[a]), "r": done.r, "dir": direccion})
    return out


def fila(rows: list[dict]) -> str:
    if not rows:
        return "   n=0"
    r = np.array([t["r"] for t in rows])
    t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 2 and r.std() > 0 else 0
    return f"n={len(r):4d} acierto {100 * (r > 0).mean():3.0f} % R={r.sum():+7.1f} ({r.mean():+.3f}/op, t={t:+.1f})"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sin-fresco", action="store_true", help="no exigir que el nivel esté sin tocar desde las 18:00")
    args = ap.parse_args()
    datos = {s: cargar(s) for s in SYMBOLS}
    print(f"Nivel {'sin exigir frescura' if args.sin_fresco else 'fresco (no tocado desde las 18:00)'}; stop fijo por mercado; una operación por día y mercado\n")
    for nombre, ini, fin in VENTANAS:
        ops = {n: [] for n, _ in SALIDAS}
        for s in SYMBOLS:
            for n, rows in operaciones(s, datos[s], ini, fin, not args.sin_fresco).items():
                ops[n] += rows
        print(f"{nombre:13s} {ini}-{fin}")
        for n, _ in SALIDAS:
            print(f"     salida {n:6s} {fila(ops[n])}")
        print()


if __name__ == "__main__":
    main()
