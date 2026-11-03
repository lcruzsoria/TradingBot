"""Backtest del CRT por zona común (FVG de M15 ∩ iFVG de M5, toque y cierre con cuerpo más allá del CISD) con velas M5.

Solo LEE velas ya descargadas (analisis/m5/<carpeta>/<símbolo>.parquet, ver scripts/descargar_m5.py): no necesita MT5 ni envía órdenes.
Usa el mismo motor que la skill CRT en directo (`tradingbot.skills.crt.engine`: `find_zone_setups`, `entry_point` variante 1 y `manage`):
stop en el extremo del sweep, objetivo a `rr` veces el riesgo, breakeven al tocar +`be` R y cierre al acabar la sesión. El resultado es
BRUTO y neto de un spread supuesto (puntos básicos del precio: índices 1,5; forex 0,7; oro 2), porque los parquet no traen el spread.

Uso (desde la raíz del proyecto):
    uv run --with pyarrow python scripts/backtest_crt_zona.py
    uv run --with pyarrow --with openpyxl python scripts/backtest_crt_zona.py --carpeta metaquotes --simbolos USTEC US30 US500 EURUSD GBPUSD
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tradingbot.skills.crt import engine                                              # noqa: E402
from tradingbot.skills.levels.daylevels import DEFAULT_US_INDICES, is_us_index           # noqa: E402

AHEAD = 7 * 3600                                    # servidor del broker = NY + 7 h
SYMBOLS = {"puprime": ("NAS100.s", "SP500.s", "DJ30.s", "EURUSD", "GBPUSD"), "metaquotes": ("USTEC", "US500", "US30", "EURUSD", "GBPUSD")}
INDICES = DEFAULT_US_INDICES + ("USTEC", "US500", "US30")
SPREAD_BP = {"indices": 1.5, "forex": 0.7}


def run_symbol(df: pd.DataFrame, symbol: str, rr: float, be: float, entry: int = 1) -> pd.DataFrame:
    kind = "indices" if is_us_index(symbol, INDICES) else "forex"
    base = engine.INDICES if kind == "indices" else engine.FOREX
    cfg = engine.Cfg(base.htf_min, base.origin, base.session_end, AHEAD)
    rule = engine.Rule(rr=rr, be_at=be)
    setups, funnel = engine.find_zone_setups(df, df, 5, cfg)
    views = {1: engine.view(df, 1), -1: engine.view(df, -1)}
    rows, busy_until = [], -1
    for st in setups:
        L = views[st["sign"]]
        ep = engine.entry_point(L, st, entry, 5, rule, cfg)
        if ep is None:
            continue
        res = engine.manage(L, st, ep, rule)
        if res is None:
            continue
        ts_in = int(L["ts"][ep["start"]])
        if ts_in < busy_until:                       # una operación a la vez por mercado, como el bot (un setup nuevo no entra con otro abierto)
            continue
        busy_until = int(L["ts"][res["exit_index"]])
        price = abs(ep["entry"])
        cost = price * SPREAD_BP[kind] / 1e4 / ep["risk"]
        rows.append({"símbolo": symbol, "lado": st["dirección"], "entrada": pd.Timestamp(ts_in - AHEAD, unit="s"), "hora_ny": (ts_in - AHEAD) % 86400 // 3600,
                     "riesgo_pct": 100 * ep["risk"] / price, "cómo": res["cómo"], "bruto": res["gross"], "neto": res["gross"] - cost,
                     "duración_h": (busy_until - ts_in) / 3600})
    out = pd.DataFrame(rows)
    out.attrs["funnel"] = funnel
    return out


def summarize(t: pd.DataFrame, name: str) -> dict:
    n = len(t)
    if not n:
        return {"grupo": name, "n": 0}
    g, net = t["bruto"].to_numpy(), t["neto"].to_numpy()
    se = net.std(ddof=1) / np.sqrt(n) if n > 1 else float("nan")
    return {"grupo": name, "n": n, "acierto %": round(100 * (g > 0.5).mean(), 1), "R bruto": round(g.mean(), 3), "R neto": round(net.mean(), 3),
            "IC95 neto": f"{net.mean() - 1.96 * se:+.2f}..{net.mean() + 1.96 * se:+.2f}", "R neto total": round(net.sum(), 1)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--carpeta", default="puprime")
    ap.add_argument("--simbolos", nargs="*")
    ap.add_argument("--datos", default=str(ROOT / "analisis" / "m5"), help="carpeta con las velas M5 (en un worktree, la del proyecto principal)")
    ap.add_argument("--rr", type=float, default=2.0)
    ap.add_argument("--be", type=float, default=1.0, help="R al que el stop pasa a la entrada (0 = sin breakeven)")
    ap.add_argument("--salida", default="analisis/backtest_crt_zona.xlsx")
    args = ap.parse_args()
    frames = []
    for sym in args.simbolos or SYMBOLS[args.carpeta]:
        path = Path(args.datos) / args.carpeta / f"{sym}.parquet"
        df = pd.read_parquet(path)[["ts", "open", "high", "low", "close"]].sort_values("ts").reset_index(drop=True)
        t = run_symbol(df, sym, args.rr, args.be)
        print(f"{sym}: {len(df)} velas, embudo {t.attrs['funnel']}", flush=True)
        frames.append(t)
    t = pd.concat(frames, ignore_index=True)
    if t.empty:
        print("sin operaciones")
        return
    cut = t["entrada"].quantile(0.6)
    rows = [summarize(t, "TODO")] + [summarize(t[t["símbolo"] == s], s) for s in t["símbolo"].unique()]
    rows += [summarize(t[t["entrada"] <= cut], f"hasta {cut:%Y-%m-%d} (60 %)"), summarize(t[t["entrada"] > cut], "después (40 %)")]
    rows += [summarize(t[t["lado"] == s], f"lado {s}") for s in ("long", "short")]
    rows += [summarize(t[t["cómo"] == c], f"salida {c}") for c in t["cómo"].unique()]
    table = pd.DataFrame(rows)
    print(f"\nrr {args.rr} · BE a {args.be} R · {args.carpeta}\n" + table.to_string(index=False))
    try:
        out = ROOT / args.salida
        out.parent.mkdir(exist_ok=True)
        with pd.ExcelWriter(out) as xl:
            table.to_excel(xl, sheet_name="resumen", index=False)
            t.to_excel(xl, sheet_name="operaciones", index=False)
        print("->", out)
    except ImportError:
        pass


if __name__ == "__main__":
    main()
