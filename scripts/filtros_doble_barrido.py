"""Busca filtros que mejoren el patrón «Doble barrido TBR», validándolos fuera de muestra.

Genera las operaciones del backtest (scripts/backtest_doble_barrido.py) con la configuración del bot y prueba filtros con datos que
se conocen ANTES de entrar: hora y día, tamaño del stop y del recorrido al objetivo, rangos de Asia y London, orden de los niveles,
dirección, mercado y sesgo del bot. Cada filtro se mide en el 60 % más antiguo de las operaciones (entrenamiento) y se confirma en el
40 % más reciente (validación): solo vale el que mejora en las dos partes.

Aviso: cuantos más filtros se prueban, más fácil es que alguno salga bien por azar; el informe cuenta cuántos se han probado.

Uso (desde la raíz del proyecto):
    uv run --with pyarrow python scripts/filtros_doble_barrido.py --carpeta analisis/m5
"""
from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import backtest_doble_barrido as bt                                                    # noqa: E402
from tradingbot.envconfig import EnvConfig                                           # noqa: E402
from tradingbot.skills.tbr.zones import zones_from_settings                           # noqa: E402

NUMERIC = ["riesgo %", "recorrido objetivo (R)", "hora entrada (NY)", "rango Asia %", "rango London %", "distancia entre niveles (R)"]
CATEGORICAL = ["dirección", "mercado", "dentro de NY Open", "Asia es el nivel más extremo", "sesgo vs operación", "lateral", "día semana"]
QUANTILES = (0.2, 0.33, 0.5, 0.67, 0.8)
MIN_N = 40                                    # operaciones mínimas por parte para fiarse del filtro
TRAIN = 0.6


def build_trades(folder: Path, symbols, be_r, entry_mode: str, stop_fib: float) -> pd.DataFrame:
    env = EnvConfig().section("TBR")
    order, zones = zones_from_settings(env, bt.ZONE_ORDER), zones_from_settings(env)
    rows = []
    for sym in symbols:
        path = folder / f"{sym}.parquet"
        if path.exists():
            rows += bt.run_symbol(bt.load(path), sym, order, zones, stop_fib, be_r, entry_mode)[0]
    t = pd.DataFrame(rows).sort_values("entrada (NY)").reset_index(drop=True)
    t["día semana"] = t["entrada (NY)"].dt.dayofweek.map(dict(enumerate(bt.DAYS)))
    return t


def candidates(t: pd.DataFrame) -> list[tuple[str, pd.Series]]:
    """Filtros simples: (nombre, máscara). Los umbrales numéricos salen de los cuantiles del entrenamiento."""
    train = t.iloc[:int(len(t) * TRAIN)]
    out = []
    for col in NUMERIC:
        for q in QUANTILES:
            thr = float(train[col].quantile(q))
            out.append((f"{col} >= {thr:.3g}", t[col] >= thr))
            out.append((f"{col} <= {thr:.3g}", t[col] <= thr))
    for col in CATEGORICAL:
        for val in sorted(t[col].unique(), key=str):
            out.append((f"{col} = {val}", t[col] == val))
            out.append((f"{col} != {val}", t[col] != val))
    return out


def measure(r: pd.Series) -> tuple[int, float]:
    return len(r), float(r.mean()) if len(r) else float("nan")


def evaluate(t: pd.DataFrame, mask: pd.Series, cut: int) -> dict:
    r = t["R"]
    n_tr, r_tr = measure(r.iloc[:cut][mask.iloc[:cut]])
    n_te, r_te = measure(r.iloc[cut:][mask.iloc[cut:]])
    return {"n entren.": n_tr, "R entren.": r_tr, "n valid.": n_te, "R valid.": r_te}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--simbolos", nargs="+", default=list(bt.SYMBOLS))
    ap.add_argument("--carpeta", default="analisis/m5")
    ap.add_argument("--entrada", default="asia", choices=bt.ENTRIES)
    ap.add_argument("--stop", type=float, default=bt.DEFAULT_STOP_FIB)
    ap.add_argument("--be-r", type=float, default=1.0)
    ap.add_argument("--salida", default="analisis/filtros_doble_barrido.xlsx")
    args = ap.parse_args()
    be_r = args.be_r if args.be_r > 0 else None
    t = build_trades(Path(args.carpeta), args.simbolos, be_r, args.entrada, args.stop)
    cut = int(len(t) * TRAIN)
    pd.set_option("display.width", 220)
    pd.set_option("display.max_colwidth", 70)
    print(f"{len(t)} operaciones sin filtro: R medio {t['R'].mean():+.3f} (entrenamiento {t['R'].iloc[:cut].mean():+.3f}, "
          f"validación {t['R'].iloc[cut:].mean():+.3f}); corte en {t['entrada (NY)'].iloc[cut]:%Y-%m-%d}")
    cands = candidates(t)
    rows = []
    for name, mask in cands:
        rows.append({"filtro": name, **evaluate(t, mask, cut)})
    simple = pd.DataFrame(rows)
    ok = simple[(simple["n entren."] >= MIN_N) & (simple["n valid."] >= MIN_N)].copy()
    ok["peor R"] = ok[["R entren.", "R valid."]].min(axis=1)
    good = ok[(ok["R entren."] > 0) & (ok["R valid."] > 0)].sort_values("peor R", ascending=False)
    print(f"\nFiltros simples probados: {len(cands)} (con >= {MIN_N} operaciones por parte: {len(ok)}); positivos en las dos partes: {len(good)}")
    print(good.head(15).round(3).to_string(index=False))
    # combinaciones de dos filtros entre los mejores simples (por R entrenamiento, sin mirar la validación)
    pool = ok[ok["R entren."] > ok["R entren."].quantile(0.7)].sort_values("R entren.", ascending=False).head(40)["filtro"].tolist()
    masks = dict(cands)
    combo_rows = []
    for a, b in itertools.combinations(pool, 2):
        m = masks[a] & masks[b]
        combo_rows.append({"filtro": f"{a}  Y  {b}", **evaluate(t, m, cut)})
    combos = pd.DataFrame(combo_rows)
    cok = combos[(combos["n entren."] >= MIN_N) & (combos["n valid."] >= MIN_N)].copy()
    cok["peor R"] = cok[["R entren.", "R valid."]].min(axis=1)
    cgood = cok[(cok["R entren."] > 0) & (cok["R valid."] > 0)].sort_values("R entren.", ascending=False)
    print(f"\nCombinaciones de dos (entre los 40 mejores simples del entrenamiento): {len(combos)} probadas, "
          f"{len(cgood)} positivas en las dos partes")
    print(cgood.head(12).round(3).to_string(index=False))
    try:
        out = Path(args.salida)
        out.parent.mkdir(parents=True, exist_ok=True)
        with pd.ExcelWriter(out) as xw:
            simple.to_excel(xw, sheet_name="Filtros simples", index=False)
            combos.to_excel(xw, sheet_name="Combinaciones", index=False)
            t.to_excel(xw, sheet_name="Operaciones", index=False)
        print(f"\nExcel: {out}")
    except ImportError:
        pass


if __name__ == "__main__":
    main()
