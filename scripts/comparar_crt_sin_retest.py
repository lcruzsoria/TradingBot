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
ap.add_argument("--extremo-hora", type=int, metavar="MIN", help="solo los setups cuyo extremo del sweep (el mínimo en un largo, el máximo en un corto) cae a MIN minutos o menos "
                "de una hora en punto, o sea de la apertura de una vela H1 (la vela de M5/M15 que lo marca empieza a ±MIN)")
ap.add_argument("--ny-open", metavar="HH:MM-HH:MM", help="otro horario (NY) para la TBR NY Open en lugar del de tradingbot.env (10:00-12:00); la zona de cada operación se recalcula "
                "con la hora de su entrada, sin volver a simular")
args = ap.parse_args()
if args.ny_open:
    (h0, m0), (h1, m1) = (tuple(int(x) for x in part.split(":")) for part in args.ny_open.split("-"))

    def rezone(T: pd.DataFrame) -> pd.DataFrame:
        minute = pd.to_datetime(T["entrada (NY)"]).dt.hour * 60 + pd.to_datetime(T["entrada (NY)"]).dt.minute
        zona = T["zona"].where(T["zona"] != "NY Open", "Fuera de TBR")
        return T.assign(zona=zona.where(~((minute >= h0 * 60 + m0) & (minute < h1 * 60 + m1)), "NY Open"))
    A, B = rezone(A), rezone(B)
    print(f"TBR NY Open de {args.ny_open} (NY)")
if args.solo_tbr:
    A, B = (T[T["zona"] != "Fuera de TBR"] for T in (A, B))
    print("Solo entradas dentro de Asia, London y NY Open")
if args.extremo_hora is not None:
    def near_open(T: pd.DataFrame) -> pd.DataFrame:
        minute = ((T["t extremo"].astype("int64") - 7 * 3600) // 60) % 60                 # hora de servidor = NY + 7 h: los minutos coinciden
        return T[np.minimum(minute, 60 - minute) <= args.extremo_hora]
    A, B = near_open(A), near_open(B)
    print(f"Solo setups con el extremo del sweep a ±{args.extremo_hora} min de una hora en punto")


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
