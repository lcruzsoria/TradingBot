"""Busca si hay algún subconjunto de las operaciones de los patrones con ventaja real, controlando el azar de probar muchas combinaciones.

Parte de analisis/backtest_patrones.xlsx (scripts/backtest_patrones.py). Método:

1. Cada operación tiene características que se conocen ANTES de entrar: mercado, patrón, zona, dirección, franja horaria, día de la
   semana, año, sesgo (a favor / en contra / sin sesgo), lateral, puntuación del sesgo, tamaño del riesgo y coste (spread / riesgo).
2. Se generan todos los subconjuntos de 1, 2 y 3 características con suficientes operaciones.
3. Se ELIGE con el primer 60 % del tiempo (entrenamiento) y se VALIDA con el 40 % final, que no se ha usado para elegir.
4. Prueba de permutación: se repite todo el proceso barajando los resultados entre las operaciones (sin ventaja posible). Dice cuánto
   aparecería de bueno solo por probar tantas combinaciones: el mejor subconjunto real solo cuenta si supera a lo que da el azar.

Uso (desde la raíz del proyecto):
    uv run --with openpyxl python scripts/buscar_subconjuntos.py
"""
from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import numpy as np
import pandas as pd

TRAIN = 0.6
MIN_TRAIN = 80
MIN_TEST = 40
PERMUTATIONS = 300
BANDS = [(0, 5, "00-05 NY"), (6, 9, "06-09 NY"), (10, 13, "10-13 NY"), (14, 17, "14-17 NY"), (18, 23, "18-23 NY")]
DAYS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def features(t: pd.DataFrame) -> pd.DataFrame:
    f = pd.DataFrame(index=t.index)
    f["mercado"] = t["mercado"]
    f["patrón"] = t["patrón"]
    f["zona"] = t["zona"]
    f["dirección"] = t["dirección"]
    hour = t["entrada (NY)"].dt.hour
    f["franja"] = hour.map(lambda h: next(name for lo, hi, name in BANDS if lo <= h <= hi))
    f["día"] = t["entrada (NY)"].dt.dayofweek.map(dict(enumerate(DAYS)))
    f["año"] = t["entrada (NY)"].dt.year.astype(str)
    f["sesgo"] = t["sesgo vs operación"]
    f["lateral"] = np.where(t["lateral"], "lateral", "no lateral")
    f["puntuación"] = pd.cut(t["puntuación sesgo"], [-99, -4.5, -2.5, 2.5, 4.5, 99],
                             labels=["<= -5", "-4 a -3", "-2 a 2", "3 a 4", ">= 5"]).astype(str)
    f["riesgo"] = pd.qcut(t["riesgo %"], 5, labels=["riesgo muy bajo", "riesgo bajo", "riesgo medio", "riesgo alto", "riesgo muy alto"]).astype(str)
    f["coste"] = pd.cut(t["coste (R)"], [-1, 0.05, 0.1, 0.2, 99], labels=["coste < 0,05 R", "coste 0,05-0,1 R", "coste 0,1-0,2 R",
                                                                           "coste > 0,2 R"]).astype(str)
    return f


def build_masks(f: pd.DataFrame, max_dims: int = 3, min_n: int = 120):
    """Matriz booleana (operaciones x subconjuntos) y su descripción."""
    cols = list(f.columns)
    atoms = {(c, v): (f[c] == v).to_numpy() for c in cols for v in f[c].unique()}
    descs, masks = [], []
    for k in range(1, max_dims + 1):
        for dims in itertools.combinations(cols, k):
            values = [sorted(f[d].unique()) for d in dims]
            for combo in itertools.product(*values):
                m = np.logical_and.reduce([atoms[(d, v)] for d, v in zip(dims, combo)])
                if m.sum() >= min_n:
                    descs.append(" + ".join(f"{d}={v}" for d, v in zip(dims, combo)))
                    masks.append(m)
    return np.column_stack(masks), descs


def tstats(M: np.ndarray, r: np.ndarray, sel: np.ndarray):
    """(n, media, t) de cada subconjunto con las operaciones `sel`. `r` puede ser un vector o una matriz (operaciones x barajados)."""
    Ms = M[sel].astype(np.float32)
    rr = r[sel].astype(np.float32)
    n = Ms.sum(axis=0)
    s1 = Ms.T @ rr
    s2 = Ms.T @ (rr * rr)
    nn = n.reshape(-1, 1) if rr.ndim == 2 else n
    mean = np.divide(s1, nn, out=np.zeros_like(s1), where=nn > 0)
    var = np.divide(s2, nn, out=np.zeros_like(s2), where=nn > 1) - mean ** 2
    se = np.sqrt(np.maximum(var, 1e-12) / np.maximum(nn, 1))
    return n, mean, np.where(nn > 1, mean / se, 0.0)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--entrada", default="analisis/backtest_patrones.xlsx")
    ap.add_argument("--salida", default="analisis/subconjuntos_patrones.xlsx")
    ap.add_argument("--columna", default="R neto", help="resultado a analizar (R neto, R bruto, R neto TP 3R...)")
    args = ap.parse_args()
    t = pd.read_excel(args.entrada, sheet_name="Operaciones").sort_values("entrada (NY)").reset_index(drop=True)
    r = t[args.columna].to_numpy(dtype=np.float32)
    f = features(t)
    cut = t["entrada (NY)"].quantile(TRAIN)
    train = (t["entrada (NY)"] <= cut).to_numpy()
    test = ~train
    M, descs = build_masks(f)
    print(f"{len(t)} operaciones, {M.shape[1]} subconjuntos; entrenamiento hasta {cut:%Y-%m-%d} ({train.sum()} op.), validación {test.sum()} op.")
    n_tr, m_tr, t_tr = tstats(M, r, train)
    n_te, m_te, t_te = tstats(M, r, test)
    ok = (n_tr >= MIN_TRAIN) & (n_te >= MIN_TEST)
    table = pd.DataFrame({"subconjunto": descs, "n entren.": n_tr, "R medio entren.": m_tr, "t entren.": t_tr,
                          "n valid.": n_te, "R medio valid.": m_te, "t valid.": t_te})[ok].copy()
    table["R medio total"] = [r[M[:, i]].mean() for i in np.flatnonzero(ok)]
    table["n total"] = [int(M[:, i].sum()) for i in np.flatnonzero(ok)]
    table["t total"] = [r[M[:, i]].mean() / (r[M[:, i]].std(ddof=1) / np.sqrt(M[:, i].sum())) for i in np.flatnonzero(ok)]
    table["positivo en las dos mitades"] = (table["R medio entren."] > 0) & (table["R medio valid."] > 0)
    # prueba de permutación: ¿cuánto sale de bueno por azar al probar tantas combinaciones?
    rng = np.random.default_rng(7)
    perm = np.column_stack([rng.permutation(r) for _ in range(PERMUTATIONS)])
    _, pm_tr, pt_tr = tstats(M, perm, train)
    _, pm_te, pt_te = tstats(M, perm, test)
    pt_tr = np.where(ok[:, None], pt_tr, -np.inf)
    best_idx = pt_tr.argmax(axis=0)                                   # el mejor subconjunto de entrenamiento de cada barajado
    perm_best_t = pt_tr.max(axis=0)
    perm_best_valid = pm_te[best_idx, np.arange(PERMUTATIONS)]        # y cómo le va en validación
    everyone = np.ones(len(t), dtype=bool)
    _, _, pt_all = tstats(M, perm, everyone)                          # t sobre todo el histórico de cada subconjunto, en cada barajado
    perm_max_total = np.where(ok[:, None], pt_all, -np.inf).max(axis=0)
    obs_total_best = float(table["t total"].max())
    top = table.sort_values("t entren.", ascending=False).head(25)
    best = table.sort_values("t entren.", ascending=False).iloc[0]
    p_train = float((perm_best_t >= best["t entren."]).mean())
    p_valid = float((perm_best_valid >= best["R medio valid."]).mean())
    both = table[table["positivo en las dos mitades"]].sort_values("t total", ascending=False)
    summary = pd.DataFrame([
        {"concepto": "Resultado analizado", "valor": args.columna},
        {"concepto": "Operaciones", "valor": len(t)},
        {"concepto": "Subconjuntos probados (con suficientes operaciones)", "valor": int(ok.sum())},
        {"concepto": "R medio de todas las operaciones", "valor": float(r.mean())},
        {"concepto": "Mejor subconjunto por t en entrenamiento", "valor": best["subconjunto"]},
        {"concepto": "  su R medio en entrenamiento / validación", "valor": f"{best['R medio entren.']:+.3f} / {best['R medio valid.']:+.3f}"},
        {"concepto": "  su t en entrenamiento / validación", "valor": f"{best['t entren.']:+.2f} / {best['t valid.']:+.2f}"},
        {"concepto": "t del mejor subconjunto que se esperaría solo por azar (mediana de los barajados)", "valor": float(np.median(perm_best_t))},
        {"concepto": "  percentil 95 del azar", "valor": float(np.percentile(perm_best_t, 95))},
        {"concepto": "p del t de entrenamiento (cuántas veces el azar iguala o supera al mejor)", "valor": p_train},
        {"concepto": "R medio en validación del mejor subconjunto de entrenamiento en el azar (mediana)", "valor": float(np.median(perm_best_valid))},
        {"concepto": "p de la validación (el azar iguala o supera su R medio en validación)", "valor": p_valid},
        {"concepto": "Mejor t sobre todo el histórico (sin separar mitades)", "valor": obs_total_best},
        {"concepto": "  máximo de t que da solo el azar: mediana / percentil 95",
         "valor": f"{np.median(perm_max_total):.2f} / {np.percentile(perm_max_total, 95):.2f}"},
        {"concepto": "  p (el azar iguala o supera ese t)", "valor": float((perm_max_total >= obs_total_best).mean())},
        {"concepto": "Subconjuntos con R medio > 0 en las dos mitades", "valor": int(len(both))},
        {"concepto": "  de ellos, con t total > 3", "valor": int((both["t total"] > 3).sum())},
        {"concepto": "  los que se esperarían por azar con R > 0 en las dos mitades (media de los barajados)",
         "valor": float(((pm_tr > 0) & (pm_te > 0) & ok[:, None]).sum(axis=0).mean())},
    ])
    by = {c: pd.DataFrame([{c: v, "operaciones": int(m.sum()), "R medio": float(r[m].mean()),
                            "win rate %": 100 * float((r[m] > 0).mean()),
                            "t": float(r[m].mean() / (r[m].std(ddof=1) / np.sqrt(m.sum()))) if m.sum() > 2 else 0.0}
                           for v in sorted(f[c].unique()) for m in [(f[c] == v).to_numpy()]]).rename(columns={c: "valor"}) for c in f.columns}
    robust = []
    names = {d: i for i, d in enumerate(descs)}
    for desc in both.head(8)["subconjunto"]:
        m = M[:, names[desc]]
        for dim in ("mercado", "año", "patrón"):
            for v in sorted(f[dim].unique()):
                mm = m & (f[dim] == v).to_numpy()
                if mm.sum() >= 5:
                    robust.append({"subconjunto": desc, "desglose": dim, "valor": v, "operaciones": int(mm.sum()),
                                   "R medio": float(r[mm].mean()), "win rate %": 100 * float((r[mm] > 0).mean())})
    singles = pd.concat([d.assign(característica=c)[["característica", "valor", "operaciones", "R medio", "win rate %", "t"]]
                         for c, d in by.items()], ignore_index=True)
    out = Path(args.salida)
    out.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out, engine="openpyxl") as xw:
        summary.to_excel(xw, sheet_name="Conclusión", index=False)
        singles.to_excel(xw, sheet_name="Una característica", index=False)
        top.to_excel(xw, sheet_name="Mejores en entrenamiento", index=False)
        both.head(200).to_excel(xw, sheet_name="Positivos en las dos mitades", index=False)
        pd.DataFrame(robust).to_excel(xw, sheet_name="Desglose de los mejores", index=False)
        table.sort_values("t total", ascending=False).head(300).to_excel(xw, sheet_name="Mejores por t total", index=False)
        for ws in xw.book.worksheets:
            ws.freeze_panes = "A2"
            for i, col in enumerate(ws.columns, start=1):
                width = max(len(str(c.value)) if c.value is not None else 0 for c in list(col)[:100])
                ws.column_dimensions[ws.cell(1, i).column_letter].width = min(max(12, width + 2), 70)
                for cell in list(col)[1:]:
                    if isinstance(cell.value, float):
                        cell.number_format = "0.000"
    pd.set_option("display.width", 230)
    pd.set_option("display.max_colwidth", 90)
    print(summary.to_string(index=False))
    print("\nMejores en entrenamiento:")
    print(top[["subconjunto", "n entren.", "R medio entren.", "t entren.", "n valid.", "R medio valid.", "t valid."]].round(3).head(12).to_string(index=False))
    print("\nPositivos en las dos mitades (por t total):")
    print(both[["subconjunto", "n total", "R medio total", "t total", "R medio entren.", "R medio valid."]].round(3).head(12).to_string(index=False))
    print("\nDesglose de los mejores:")
    print(pd.DataFrame(robust).round(3).to_string(index=False))
    print("\nUna característica:")
    print(singles.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
