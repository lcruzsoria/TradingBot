"""Largos de lunes a hora fija, sin patrones: ¿la ventaja de los largos de lunes está en el calendario o en el patrón? Solo lee MT5.

Entrada a mercado en la apertura de una vela M15 a una hora fija de Nueva York (00:00, 02:00, 05:00 u 08:00), stop a un % fijo del
precio, objetivo a RR veces el stop y cierre por tiempo a las 10:00 NY si no se ha tocado ninguno (la ventana Asia + London). El
stop va antes que el objetivo si caben los dos en una vela. Coste: el spread de la vela de entrada, una vez por operación.
Compara con los demás días de la semana y con los cortos, que son el control: si solo el lunes largo sale, es calendario.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import backtest_patrones as bp                                       # noqa: E402
from analisis_setups import spread_prices                            # noqa: E402
from tradingbot.config import load_profiles, select_profile          # noqa: E402
from tradingbot.skills.feed.mt5_client import Mt5Source              # noqa: E402

ENTRY_HOURS = (0, 2, 5, 8)
EXIT_HOUR = 10
STOPS = (0.15, 0.25, 0.35, 0.50, 0.75)         # % del precio
RRS = (1.0, 1.5, 2.0)
CACHE = Path("analisis/lunes_hora_fija.pkl")


def bracket(h, l, c, i0, i1, direction, entry, risk, rr):
    """R bruto de una posición abierta en la vela i0 y cerrada como tarde al cierre de la vela i1."""
    stop = entry - risk if direction == "long" else entry + risk
    tgt = entry + rr * risk if direction == "long" else entry - rr * risk
    for i in range(i0, i1 + 1):
        if direction == "long":
            if l[i] <= stop:
                return -1.0
            if h[i] >= tgt:
                return rr
        else:
            if h[i] >= stop:
                return -1.0
            if l[i] <= tgt:
                return rr
    r = c[i1] - entry if direction == "long" else entry - c[i1]
    return r / risk


def collect() -> pd.DataFrame:
    profiles, default = load_profiles()
    source = Mt5Source(select_profile(profiles, default, None), 2_000_000)
    source.connect()
    rows = []
    for want in bp.SYMBOLS:
        sym = source.resolve_symbol(want)
        df = source.load_candles(sym, "15m").reset_index(drop=True)
        df = df.iloc[bp.intraday_start(df["ts"].to_numpy()):].reset_index(drop=True)
        spread = spread_prices(source, sym, df)
        df = df.iloc[:-1]
        spread = spread[:len(df)]
        ts = df["ts"].to_numpy().astype(np.int64)
        o, h, l, c = (df[k].to_numpy().astype(float) for k in ("open", "high", "low", "close"))
        ny = pd.to_datetime(ts - bp.AHEAD, unit="s")
        day = ny.normalize()
        hour, minute = ny.hour.to_numpy(), ny.minute.to_numpy()
        for d in sorted(set(day)):
            idx = np.where(day == d)[0]
            if len(idx) == 0 or d.weekday() > 4:
                continue
            hh, mm, ii = hour[idx], minute[idx], idx
            end = ii[(hh == EXIT_HOUR - 1) & (mm == 45)]
            if len(end) == 0:
                continue
            for eh in ENTRY_HOURS:
                st = ii[(hh == eh) & (mm == 0)]
                if len(st) == 0 or st[0] >= end[0]:
                    continue
                i0, i1 = int(st[0]), int(end[0])
                if ts[i1] - ts[i0] > (EXIT_HOUR - eh) * 3600 + 900:       # hueco de datos (festivo o cierre)
                    continue
                entry = o[i0]
                for direction in ("long", "short"):
                    ret = (c[i1] - entry) if direction == "long" else (entry - c[i1])
                    rows.append({"mercado": sym, "día": d, "dow": d.weekday(), "año": d.year, "hora": eh, "dir": direction,
                                 "stop %": 0.0, "RR": 0.0, "R bruto": 100 * ret / entry, "coste": 100 * spread[i0] / entry})
                    for sp in STOPS:
                        risk = entry * sp / 100
                        for rr in RRS:
                            rg = bracket(h, l, c, i0, i1, direction, entry, risk, rr)
                            rows.append({"mercado": sym, "día": d, "dow": d.weekday(), "año": d.year, "hora": eh, "dir": direction,
                                         "stop %": sp, "RR": rr, "R bruto": rg, "coste": spread[i0] / risk})
        print(sym, "ok")
    source.close()
    out = pd.DataFrame(rows)
    out.to_pickle(CACHE)
    return out


def summ(g: pd.DataFrame, pct: bool = False) -> pd.Series:
    net = g["R bruto"] - g["coste"]
    n = len(g)
    t = net.mean() / (net.std() / np.sqrt(n)) if n > 2 and net.std() > 0 else 0.0
    return pd.Series({"operaciones": n, "win %": 100 * (net > 0).mean(), "bruto": g["R bruto"].mean(), "neto": net.mean(), "t": t})


def main() -> None:
    df = pd.read_pickle(CACHE) if "--cache" in sys.argv and CACHE.exists() else collect()
    pd.set_option("display.width", 200)
    pd.set_option("display.max_rows", 200)
    drift = df[df["stop %"] == 0]
    br = df[df["stop %"] > 0]
    two = ["NAS100.r", "DJ30.r"]
    print("\nDERIVA PURA (sin stop; rentabilidad en %, entrada -> 10:00 NY) — largos por día de la semana, entrada 00:00")
    print(drift[(drift["dir"] == "long") & (drift["hora"] == 0)].groupby("dow").apply(summ).round(4))
    print("\nDERIVA PURA, lunes por hora de entrada y dirección (NAS100+DJ30 / los 4)")
    for name, mk in (("NAS100+DJ30", two), ("4 mercados", list(bp.SYMBOLS))):
        d = drift[(drift["dow"] == 0) & drift["mercado"].isin(mk)]
        print(name, "\n", d.groupby(["dir", "hora"]).apply(summ).round(4))
    print("\nLUNES LARGO CON STOP Y OBJETIVO, entrada 02:00 NY, NAS100+DJ30 (neto en R)")
    b = br[(br["dow"] == 0) & (br["dir"] == "long") & br["mercado"].isin(two)]
    print(b[b["hora"] == 2].groupby(["stop %", "RR"]).apply(summ).round(3))
    print("\nLUNES LARGO, stop 0,35 %, RR 1,5, por hora de entrada y mercado")
    sel = br[(br["dow"] == 0) & (br["dir"] == "long") & (br["stop %"] == 0.35) & (br["RR"] == 1.5)]
    print(sel.groupby(["mercado", "hora"]).apply(summ).round(3))
    print("\nCONTROL (stop 0,35 %, RR 1,5, entrada 02:00, NAS100+DJ30): día de la semana y dirección")
    ctl = br[(br["stop %"] == 0.35) & (br["RR"] == 1.5) & (br["hora"] == 2) & br["mercado"].isin(two)]
    print(ctl.groupby(["dir", "dow"]).apply(summ).round(3))
    g = b[(b["hora"] == 2) & (b["stop %"] == 0.35) & (b["RR"] == 1.5)].sort_values("día")
    half = len(g) // 2
    print("\nLUNES LARGO 02:00, stop 0,35 %, RR 1,5, NAS100+DJ30: mitades y años")
    print(pd.DataFrame({"antigua": summ(g.iloc[:half]), "reciente": summ(g.iloc[half:])}).round(3))
    print(g.groupby("año").apply(summ).round(3))


if __name__ == "__main__":
    main()
