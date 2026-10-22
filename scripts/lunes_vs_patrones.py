"""Largos de lunes (Asia y London) con los patrones frente a la entrada a hora fija.

Lee analisis/backtest_patrones.pkl (scripts/backtest_patrones.py) y analisis/lunes_hora_fija.pkl (scripts/lunes_hora_fija.py).
Patrones: largos de lunes en Asia y London, sin filtro y con el filtro de coste y riesgo (coste<=p60 y riesgo/ATR>=p40, umbrales
del 60 % antiguo), con stop original y objetivo a 1, 1,5 y 2R. Hora fija: entrada 02:00 NY, stop 0,35 %, mismo RR, con y sin coste<=p60.
Ambos se parten por fecha: 60 % antiguo (entrenamiento) y 40 % final (validación).

    uv run python scripts/lunes_vs_patrones.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

RRS = (1.0, 1.5, 2.0)


def row(name: str, rr: float, net: pd.Series, gross: pd.Series, days: pd.Series) -> dict:
    n = len(net)
    years = max((days.max() - days.min()).days / 365.25, 1e-9) if n > 1 else np.nan
    t = net.mean() / (net.std() / np.sqrt(n)) if n > 2 and net.std() > 0 else 0.0
    return {"método": name, "RR": rr, "n": n, "win %": 100 * (gross > 0).mean() if n else np.nan, "R neto": net.mean() if n else np.nan,
            "R neto/año": net.sum() / years if n > 1 else np.nan, "t": t}


def main() -> None:
    p = pd.read_pickle("analisis/backtest_patrones.pkl").sort_values("entrada (NY)").reset_index(drop=True)
    p = p.dropna(subset=["riesgo/ATR", "coste (R)"]).reset_index(drop=True)
    cut_ts = p["entrada (NY)"].iloc[int(len(p) * 0.6)]                       # fecha de corte del backtest de patrones
    tr = p[p["entrada (NY)"] < cut_ts]
    ok = (p["coste (R)"] <= np.percentile(tr["coste (R)"], 60)) & (p["riesgo/ATR"] >= np.percentile(tr["riesgo/ATR"], 40))
    mon = (p["entrada (NY)"].dt.dayofweek == 0) & (p["dirección"] == "long") & p["zona"].isin(["Asia", "London"])
    fixed = pd.read_pickle("analisis/lunes_hora_fija.pkl")
    f = fixed[(fixed["dow"] == 0) & (fixed["dir"] == "long") & (fixed["hora"] == 2) & (fixed["stop %"] == 0.35)].copy()
    f["día"] = pd.to_datetime(f["día"])
    f_cut = f[f["RR"] == 1.5].sort_values("día")["día"].iloc[int(len(f[f["RR"] == 1.5]) * 0.6)]
    rows = []
    for rr in RRS:
        tag = f"k1 RR{rr:g}"
        for lab, sel in (("patrones, largos de lunes Asia+London", mon), ("patrones + filtro coste/riesgo", mon & ok),
                         ("patrones, resto de operaciones + filtro", ~mon & ok)):
            for per, part in (("entren.", p["entrada (NY)"] < cut_ts), ("valid.", p["entrada (NY)"] >= cut_ts)):
                g = p[sel & part]
                rows.append({"periodo": per, **row(lab, rr, g[f"R neto {tag}"], g[f"R bruto {tag}"], g["entrada (NY)"])})
        g0 = f[f["RR"] == rr]
        thr = np.percentile((g0[g0["día"] < f_cut])["coste"], 60)
        for lab, sel in (("hora fija 02:00, stop 0,35 %", g0), ("hora fija + coste<=p60", g0[g0["coste"] <= thr])):
            for per, part in (("entren.", sel[sel["día"] < f_cut]), ("valid.", sel[sel["día"] >= f_cut])):
                rows.append({"periodo": per, **row(lab, rr, part["R bruto"] - part["coste"], part["R bruto"] - part["coste"] + part["coste"], part["día"])})
    out = pd.DataFrame(rows)
    pd.set_option("display.width", 220)
    piv = out.pivot_table(index=["método", "RR"], columns="periodo", values=["n", "win %", "R neto", "R neto/año", "t"], sort=False)
    print(f"corte patrones {cut_ts:%Y-%m-%d}, hora fija {f_cut:%Y-%m-%d}\n")
    print(piv.round(3).to_string())
    # los lunes por año con el filtro (patrones, RR 1,5)
    g = p[mon & ok].assign(año=lambda d: d["entrada (NY)"].dt.year)
    print("\nPatrones + filtro, largos de lunes, RR 1,5, por año:")
    print(g.groupby("año")["R neto k1 RR1.5"].agg(["size", "mean"]).round(3).T.to_string())
    print("\nPor mercado:")
    print(g.groupby("mercado")["R neto k1 RR1.5"].agg(["size", "mean"]).round(3).to_string())


if __name__ == "__main__":
    main()
