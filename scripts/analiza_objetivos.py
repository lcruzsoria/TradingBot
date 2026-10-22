"""Objetivo 1R / 1,5R / 2R con los filtros de coste, calidad de la rotura y noticias (B4-B6 de la propuesta de optimización).

Lee analisis/backtest_patrones.pkl. Umbrales (percentiles) fijados con el 60 % más antiguo y medidos en el 40 % final; los
resultados «una posición» aplican las reglas del bot (GO de Cortex, una posición abierta, una sesión un trade) sobre todo el
histórico y luego parten por fecha. Win rate = % de operaciones con R bruto > 0 (stop original, objetivo a RR veces el riesgo).

    uv run python scripts/analiza_objetivos.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest_patrones as bt                                                       # noqa: E402

RRS = (1.0, 1.5, 2.0)


def main() -> None:
    t = pd.read_pickle("analisis/backtest_patrones.pkl").sort_values("entrada (NY)").reset_index(drop=True)
    t = t.dropna(subset=["riesgo/ATR", "coste (R)"]).reset_index(drop=True)
    cut = int(len(t) * 0.6)
    tr = t.iloc[:cut]
    q = lambda f, p, d=tr: np.nanpercentile(d[f], p)                                 # noqa: E731
    cont, rev = t["patrón"] == "Continuación", t["patrón"] == "Reversión"
    pc = q("cuerpo rotura/ATR", 50, tr[tr["patrón"] == "Continuación"])
    pr = q("mecha toma/ATR", 50, tr[tr["patrón"] == "Reversión"])
    cost_ok = t["coste (R)"] <= q("coste (R)", 60)
    risk_ok = t["riesgo/ATR"] >= q("riesgo/ATR", 40)
    quality = (cont & (t["cuerpo rotura/ATR"] >= pc)) | (rev & (t["mecha toma/ATR"] >= pr))
    rules = {
        "0 sin filtro": pd.Series(True, index=t.index),
        "A coste<=p40": t["coste (R)"] <= q("coste (R)", 40),
        "C coste<=p60 & riesgo/ATR>=p40": cost_ok & risk_ok,
        "Q C + rotura/toma de calidad (>= mediana)": cost_ok & risk_ok & quality,
        "N C sin franja de noticias": cost_ok & risk_ok & ~t["franja noticias"],
        "QN C + calidad + sin noticias": cost_ok & risk_ok & quality & ~t["franja noticias"],
    }
    print(f"Umbrales (entrenamiento): coste<=p40 {q('coste (R)', 40):.3f}, coste<=p60 {q('coste (R)', 60):.3f}, riesgo/ATR>=p40 {q('riesgo/ATR', 40):.2f}, "
          f"cuerpo rotura/ATR>= {pc:.2f}, mecha toma/ATR>= {pr:.2f}\n")
    # calidad de la rotura por quintiles (sin otros filtros)
    for col, mask in (("cuerpo rotura/ATR", cont), ("mecha toma/ATR", rev)):
        g = t[mask].copy()
        g["quintil"] = pd.qcut(g[col], 5, duplicates="drop")
        print(f"{col} por quintiles (todo el histórico, 2R):")
        print(g.groupby("quintil", observed=True).agg(n=("R neto", "size"), win=("R bruto", lambda s: 100 * (s > 0).mean()), R=("R neto", "mean")).round(3).to_string(), "\n")
    rows = []
    go = t["sesgo vs operación"] != "en contra"
    for name, mask in rules.items():
        for rr in RRS:
            tag = f"k1 RR{rr:g}"
            net, gross = t[f"R neto {tag}"], t[f"R bruto {tag}"]
            for lab, sel in (("todas", mask), ("una posición (GO)", mask & go)):
                pool = sel
                if lab != "todas":
                    flags = bt.overlap_flags(t, pool, f"cierre {tag}")
                    pool = sel & ~flags
                for per, part in (("entren.", pool & (t.index < cut)), ("valid.", pool & (t.index >= cut))):
                    n = int(part.sum())
                    rows.append({"filtro": name, "RR": rr, "modo": lab, "periodo": per, "n": n,
                                 "win %": 100 * (gross[part] > 0).mean() if n else np.nan,
                                 "R neto": net[part].mean() if n else np.nan,
                                 "R neto/año": net[part].sum() / ((t.loc[part, "entrada (NY)"].max() - t.loc[part, "entrada (NY)"].min()).days / 365.25) if n > 1 else np.nan})
    out = pd.DataFrame(rows)
    pd.set_option("display.width", 250)
    for modo in ("todas", "una posición (GO)"):
        print(f"=== {modo} ===")
        piv = out[out["modo"] == modo].pivot_table(index=["filtro", "RR"], columns="periodo", values=["n", "win %", "R neto", "R neto/año"])
        print(piv.round(3).to_string(), "\n")
    out.to_csv("analisis/objetivos_filtros.csv", index=False)


if __name__ == "__main__":
    main()
