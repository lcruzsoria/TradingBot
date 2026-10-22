"""Filtros de coste y volatilidad sobre las operaciones del backtest de patrones (B1-B4 de la propuesta de optimización).

Lee analisis/backtest_patrones.pkl (lo escribe scripts/backtest_patrones.py). Para cada característica conocida al entrar (coste en R,
spread relativo a su hora, spread/ATR, riesgo/ATR, ATR14/ATR100, caja TBR/ATR, velas hasta la entrada) prueba quedarse con las
operaciones por debajo o por encima de un percentil. Los umbrales se fijan con el 60 % más antiguo (entrenamiento) y se miden en el 40 % final (validación). Como
control, se quita el mismo número de operaciones al azar (2000 veces) y se cuenta con qué frecuencia el azar iguala el R neto
del filtro en validación.

    uv run python scripts/analiza_filtros.py [--pkl analisis/backtest_patrones.pkl] [--patron Ambos]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

FEATURES = ["coste (R)", "spread relativo", "spread/ATR", "riesgo/ATR", "ATR14/ATR100", "caja TBR/ATR", "velas hasta entrada"]
PCTS = (20, 40, 60, 80)
TARGETS = {"2R": ("R bruto", "R neto"), "1R": (None, "R neto TP 1R"), "1,5R": (None, "R neto TP 1.5R")}


def wr(df: pd.DataFrame, col_net: str) -> float:
    return 100 * (df[col_net] > 0).mean() if len(df) else float("nan")


def summarize(df: pd.DataFrame) -> dict:
    return {"n": len(df), "win 2R %": wr(df, "R neto"), "win 1R %": wr(df, "R neto TP 1R"), "R neto 2R": df["R neto"].mean(),
            "R neto 1R": df["R neto TP 1R"].mean()}


def random_p(test: pd.DataFrame, kept: pd.Series, rng, draws: int = 2000) -> float:
    """Frecuencia con la que quedarse al azar con las mismas operaciones iguala el R neto (2R) del filtro."""
    r = test["R neto"].to_numpy()
    k = int(kept.sum())
    if k < 10:
        return float("nan")
    target = r[kept.to_numpy()].mean()
    means = np.array([r[rng.choice(len(r), k, replace=False)].mean() for _ in range(draws)])
    return float((means >= target).mean())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkl", default="analisis/backtest_patrones.pkl")
    ap.add_argument("--patron", default="Ambos", choices=["Ambos", "Continuación", "Reversión"])
    args = ap.parse_args()
    t = pd.read_pickle(args.pkl).sort_values("entrada (NY)").reset_index(drop=True)
    t = t.dropna(subset=FEATURES)
    if args.patron != "Ambos":
        t = t[t["patrón"] == args.patron].reset_index(drop=True)
    cut = int(len(t) * 0.6)
    train, test = t.iloc[:cut], t.iloc[cut:]
    print(f"{len(t)} operaciones ({args.patron}); entrenamiento {len(train)} hasta {train['entrada (NY)'].iloc[-1]:%Y-%m-%d}, validación {len(test)}")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    print("\nBase:")
    print(pd.DataFrame({"entrenamiento": summarize(train), "validación": summarize(test)}).round(3).T.to_string())
    rng = np.random.default_rng(1)
    rows = []
    for f in FEATURES:
        for p in PCTS:
            thr = np.percentile(train[f], p)
            for side, keep in (("<=", lambda d: d[f] <= thr), (">=", lambda d: d[f] >= thr)):
                tr, te = train[keep(train)], test[keep(test)]
                if len(tr) < 150 or len(te) < 100:
                    continue
                s_tr, s_te = summarize(tr), summarize(te)
                rows.append({"filtro": f"{f} {side} p{p} ({thr:.3g})", "% quedan": 100 * len(te) / len(test), "n val": s_te["n"],
                             "win 2R tr": s_tr["win 2R %"], "win 2R val": s_te["win 2R %"], "win 1R val": s_te["win 1R %"],
                             "R2 tr": s_tr["R neto 2R"], "R2 val": s_te["R neto 2R"], "R1 val": s_te["R neto 1R"],
                             "p azar": random_p(test, keep(test), rng)})
    out = pd.DataFrame(rows).sort_values("R2 val", ascending=False)
    print("\nFiltros individuales (ordenados por R neto 2R en validación; 'p azar' = frecuencia con la que el azar iguala ese R):")
    print(out.round(3).to_string(index=False))
    Path("analisis").mkdir(exist_ok=True)
    out.to_csv("analisis/filtros_individuales.csv", index=False)


if __name__ == "__main__":
    main()
