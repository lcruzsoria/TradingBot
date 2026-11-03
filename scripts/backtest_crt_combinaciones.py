"""Backtest del CRT por zona común con todas las combinaciones de timeframes: FVG normal y iFVG de 15 o 5 min con TF del FVG >= TF del iFVG.

Lee velas ya descargadas (`scripts/descargar_velas.py`: analisis/5m y analisis/15m, carpeta `puprime`) y usa el mismo motor que la skill
(`engine.find_multi_setups`): cada combinación se mira con las velas del TF de su iFVG; la inversión, el CISD, el cierre sobre el CISD y la entrada (a la
apertura de la vela siguiente de ese TF) son de ese TF. Cada combinación se simula por separado (una operación a la vez por mercado y combinación) y, aparte,
«todas»: lo que haría el bot con todas a la vez (el primer cierre sobre el CISD de cada C2 y lado, una posición por mercado). Stop en el extremo del sweep,
objetivo `rr` R y breakeven al tocar +`be` R, con el gestor del motor sobre las velas del TF de la combinación. Neto = bruto - spread supuesto (índices 1,5 pb,
forex 0,7 pb). Se usa el tramo común a los dos TF de cada mercado (el de 5 min es el más corto).

Uso (desde la raíz del proyecto):
    uv run --with pyarrow --with openpyxl python scripts/backtest_crt_combinaciones.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tradingbot.skills.crt import bias, engine                                          # noqa: E402
from tradingbot.skills.levels.daylevels import DEFAULT_US_INDICES, is_us_index           # noqa: E402

AHEAD = 7 * 3600
SYMBOLS = ("NAS100.s", "SP500.s", "DJ30.s", "EURUSD", "GBPUSD")
SPREAD_BP = {"indices": 1.5, "forex": 0.7}
BIAS_CFG = bias.CrtBiasCfg(True, False, 10.0, 1.0, ("1h", "4h", "1d"), 1, 50.0)


def load(data: Path, tf: str, carpeta: str, sym: str) -> pd.DataFrame:
    df = pd.read_parquet(data / tf / carpeta / f"{sym}.parquet")[["ts", "open", "high", "low", "close"]]
    return df.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)


def run_symbol(series: dict, sym: str, rr: float, be: float, entry: int = 1) -> pd.DataFrame:
    kind = "indices" if is_us_index(sym, DEFAULT_US_INDICES) else "forex"
    base = engine.INDICES if kind == "indices" else engine.FOREX
    cfg = engine.Cfg(base.htf_min, base.origin, base.session_end, AHEAD)
    rule = engine.Rule(rr=rr, be_at=be)
    setups, funnel = engine.find_multi_setups(series, cfg)
    views = {m: {1: engine.view(d, 1), -1: engine.view(d, -1)} for m, d in series.items()}
    zones = bias.zone_cache(series[5], cfg, BIAS_CFG)
    rows, busy = [], {}
    first_c2: dict[tuple, bool] = {}
    for st in setups:                                                  # en orden de hora de su cierre sobre el CISD
        m = st["ltf"]
        L = views[m][st["sign"]]
        ep = engine.entry_point(L, st, entry, m, rule, cfg)
        if ep is None:
            continue
        res = engine.manage(L, st, ep, rule)
        if res is None:
            continue
        ts = L["ts"]
        t_in, t_out = int(ts[ep["start"]]), int(ts[res["exit_index"]])
        sgn = st["sign"]
        pts = bias.evaluate(series[5], st["dirección"], int(st["C2"]), (sgn * st["z_bottom"], sgn * st["z_top"]), cfg, BIAS_CFG, AHEAD, zones)
        price = abs(ep["entry"])
        cost = price * SPREAD_BP[kind] / 1e4 / ep["risk"]
        combo = f"FVG M{st['mtf'][1:]} + iFVG M{m}"
        row = {"símbolo": sym, "combinación": combo, "entrada": pd.Timestamp(t_in - AHEAD, unit="s"), "lado": st["dirección"], "cómo": res["cómo"],
               "bruto": res["gross"], "neto": res["gross"] - cost, "puntos": int(pts.score), "C2": int(st["C2"]), "t_in": t_in, "t_out": t_out}
        for key in (combo, "todas"):
            if key == "todas":
                c2 = (int(st["C2"]), st["sign"])
                if first_c2.get(c2) or t_in < busy.get(("todas", sym), -1):
                    continue                                           # el bot: una posición por mercado y el primer setup de cada C2 y lado
                first_c2[c2] = True
            elif t_in < busy.get((key, sym), -1):
                continue
            busy[(key, sym)] = t_out
            rows.append({**row, "grupo": key})
    out = pd.DataFrame(rows)
    out.attrs["funnel"] = funnel
    return out


def summarize(t: pd.DataFrame, name: str) -> dict:
    n = len(t)
    if not n:
        return {"grupo": name, "n": 0}
    g, net = t["bruto"].to_numpy(), t["neto"].to_numpy()
    se = net.std(ddof=1) / np.sqrt(n) if n > 1 else float("nan")
    return {"grupo": name, "n": n, "R bruto": round(g.mean(), 3), "R neto": round(net.mean(), 3), "IC95 neto": f"{net.mean() - 1.96 * se:+.2f}..{net.mean() + 1.96 * se:+.2f}",
            "R neto total": round(net.sum(), 1)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--datos", default=str(ROOT / "analisis"))
    ap.add_argument("--carpeta", default="puprime")
    ap.add_argument("--simbolos", nargs="*", default=list(SYMBOLS))
    ap.add_argument("--rr", type=float, default=2.0)
    ap.add_argument("--be", type=float, default=1.0)
    ap.add_argument("--salida", default="analisis/backtest_crt_combinaciones.xlsx")
    args = ap.parse_args()
    data = Path(args.datos)
    frames = []
    for sym in args.simbolos:
        series = {m: load(data, f"{m}m", args.carpeta, sym) for m in (5, 15)}
        start = max(int(d["ts"].iloc[0]) for d in series.values())            # el tramo común a los dos TF
        series = {m: d[d["ts"] >= start].reset_index(drop=True) for m, d in series.items()}
        t = run_symbol(series, sym, args.rr, args.be)
        print(f"{sym}: desde {pd.Timestamp(start - AHEAD, unit='s'):%Y-%m-%d} NY, {len(series[5])} velas M5, embudo {t.attrs['funnel']}", flush=True)
        frames.append(t)
    t = pd.concat(frames, ignore_index=True)
    order = ["todas"] + sorted(g for g in t["grupo"].unique() if g != "todas")
    rows = [summarize(t[t["grupo"] == g], g) for g in order]
    table = pd.DataFrame(rows)
    print(f"\nrr {args.rr} · BE a {args.be} R · {args.carpeta}\n" + table.to_string(index=False))
    for g in ("todas",):
        s = t[t["grupo"] == g]
        print(f"\n{g}: por mercado")
        print(pd.DataFrame([summarize(s[s["símbolo"] == x], x) for x in s["símbolo"].unique()]).to_string(index=False))
        print(f"\n{g}: por puntos del sesgo")
        print(pd.DataFrame([summarize(s[s["puntos"] == k], f"{k} puntos") for k in range(4)]).to_string(index=False))
        print(f"\n{g}: combinación que dio la entrada")
        print(pd.DataFrame([summarize(s[s["combinación"] == c], c) for c in sorted(s["combinación"].unique())]).to_string(index=False))
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
