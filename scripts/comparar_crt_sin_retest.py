"""Compara las operaciones simuladas del CRT con la regla vigente (analisis/crt_operaciones.pkl) y sin retest del BPR
(analisis/crt_operaciones_sin_retest.pkl, de `simular_crt_sin_retest.py`): por grupo y TF del iFVG, por objetivo y por mercado.

Uso (desde la raíz del proyecto):
    uv run --with pyarrow python scripts/comparar_crt_sin_retest.py
    uv run --with pyarrow python scripts/comparar_crt_sin_retest.py --solo-tbr     # solo entradas dentro de Asia, London y NY Open
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
A = pd.read_pickle(ROOT / "analisis" / "crt_operaciones.pkl")["operaciones"]
B = pd.read_pickle(ROOT / "analisis" / "crt_operaciones_sin_retest.pkl")["operaciones"]
ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument("--solo-tbr", action="store_true", help="solo las entradas que caen en el horario de una TBR (Asia, London, NY Open)")
if ap.parse_args().solo_tbr:
    A, B = (T[T["zona"] != "Fuera de TBR"] for T in (A, B))
    print("Solo entradas dentro de Asia, London y NY Open")


def stats(t: pd.DataFrame) -> dict:
    """Operaciones, % de acierto, de stop y de breakeven, R medio y total, factor de beneficio y drawdown en R."""
    r = t["R neto"].astype(float)
    if not len(r):
        return dict(n=0)
    win, loss = r[r > 0].sum(), -r[r < 0].sum()
    t = t.sort_values("entrada (NY)")
    eq = t["R neto"].astype(float).cumsum()
    return dict(n=len(r), acierto=round(100 * (r > 0).mean(), 1), stop=round(100 * (t["cómo"] == "stop").mean(), 1),
                be=round(100 * (t["cómo"] == "BE").mean(), 1), R_medio=round(r.mean(), 3), R_total=round(r.sum(), 1),
                PF=round(win / loss, 2) if loss else np.inf, dd_R=round((eq.cummax() - eq).max(), 1),
                dias=t["entrada (NY)"].astype(str).str[:10].nunique())


for code, name in ((2, "objetivo 2R (el del bot)"), (1, "objetivo 1R"), (3, "objetivo 3R")):
    print(f"\n=== {name}, BE a +1R ===")
    rows = []
    for grp in ("indices", "forex", None):
        for ltf in (15, 5):
            for label, T in (("vigente", A), ("sin retest", B)):
                t = T[(T["objetivo_cod"] == code) & (T["ltf"] == ltf)]
                if grp:
                    t = t[t["grupo"] == grp]
                rows.append({"grupo": grp or "todo", "ltf": f"M{ltf}", "regla": label, **stats(t)})
    print(pd.DataFrame(rows).to_string(index=False))

print("\n=== 2R, por mercado, M15 y M5 ===")
rows = []
for mk in sorted(A["mercado"].unique()):
    for ltf in (15, 5):
        for label, T in (("vigente", A), ("sin retest", B)):
            t = T[(T["objetivo_cod"] == 2) & (T["ltf"] == ltf) & (T["mercado"] == mk)]
            rows.append({"mercado": mk, "ltf": f"M{ltf}", "regla": label, **{k: v for k, v in stats(t).items() if k in ("n", "acierto", "R_medio", "R_total", "PF")}})
print(pd.DataFrame(rows).to_string(index=False))

print("\nPeriodo:", A["entrada (NY)"].astype(str).min()[:10], "->", A["entrada (NY)"].astype(str).max()[:10])

print("\n=== 2R, por TBR (M15 y M5) ===")
rows = []
for zona in ("Asia", "London", "NY Open", "Fuera de TBR"):
    for ltf in (15, 5):
        for label, T in (("vigente", A), ("sin retest", B)):
            t = T[(T["objetivo_cod"] == 2) & (T["ltf"] == ltf) & (T["zona"] == zona)]
            rows.append({"TBR": zona, "ltf": f"M{ltf}", "regla": label, **{k: v for k, v in stats(t).items() if k in ("n", "acierto", "R_medio", "R_total", "PF")}})
print(pd.DataFrame(rows).to_string(index=False))
