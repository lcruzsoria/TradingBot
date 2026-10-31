"""Rejilla del filtro de ancho del TBR 18-20 NY en % del precio (en lugar de puntos fijos). Solo LEE velas ya descargadas.

Con el ancho en puntos fijos (100-300 puntos del NAS100, scripts/backtest_tbr.py) la estrategia salía positiva en los 4 mercados pero
sin significación, y casi todos los días válidos eran de 2025-2026. Aquí el ancho se mide en % del precio (cierre de las 20:00 NY),
para que haya días válidos en todos los años. El resto de reglas son las de backtest_tbr.py (EMA 20, entrada en la vela siguiente
a la rotura con cuerpo, stop en el extremo contrario, objetivo 2R, BE a 1R, rotura hasta las 00:00, una operación por día).

PROTOCOLO Y CRITERIOS, FIJADOS ANTES DE VER LOS RESULTADOS:
- Rejilla de bandas [mínimo, máximo) en % del precio: mínimos 0,10 0,15 0,20 0,25 0,30 0,40 0,50 0,60 0,80; máximos 0,30 0,40
  0,50 0,60 0,80 1,00 1,50 y sin límite.
- Selección SOLO con el NAS100 de PUPrime de 2018-2022: la banda con mayor estadístico t entre las que tienen al menos 40 operaciones.
- Se da por buena si esa banda cumple TODOS:
    1. NAS100 de PUPrime de 2023 en adelante (no visto al elegir): R neto medio > 0 con t > 1,65.
    2. R neto medio > 0 con t > 1,65 en al menos 2 de 3: SP500 y DJ30 de PUPrime (todo el histórico) y NAS100 de MetaQuotes, con
       la misma banda en % de su propio precio.
- Como contexto, la rejilla entera en todo el histórico del NAS100 de PUPrime, marcando las bandas que superan la corrección de
  Bonferroni por el número de bandas (no cuenta para el veredicto).

Uso (desde la raíz del proyecto):
    uv run python scripts/backtest_tbr_rejilla.py

Salida: docs/backtest_tbr/REJILLA_PCT.md y analisis/backtest_tbr_rejilla_pct.csv.
"""
from __future__ import annotations

import sys
from statistics import NormalDist
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from backtest_orb_nasdaq import row, summary, table                                   # noqa: E402
from backtest_tbr import Rule, by_period, prepare, trades                             # noqa: E402
from estudio_ema_vwap import cache_path                                               # noqa: E402

DOC = ROOT / "docs" / "backtest_tbr" / "REJILLA_PCT.md"
MINS = (0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.80)
MAXS = (0.30, 0.40, 0.50, 0.60, 0.80, 1.00, 1.50, 99.0)
MIN_TRAIN_OPS, MIN_T, MIN_OTHER = 40, 1.65, 2
OTHERS = (("puprime", "SP500"), ("puprime", "DJ30"), ("metaquotes", "NAS100"))


def band(lo: float, hi: float) -> str:
    return f"{lo:.2f}–{hi:.2f} %" if hi < 99 else f"≥ {lo:.2f} %"


def stat(t: pd.DataFrame) -> tuple[int, float, float]:
    s = summary(t)
    if not s.get("operaciones"):
        return 0, float("nan"), float("nan")
    return s["operaciones"], s["R medio"], s["estadístico t"]


def main() -> None:
    data = {}
    for profile, want in (("puprime", "NAS100"),) + OTHERS:
        sym, df = pd.read_pickle(cache_path(profile, want))
        data[(profile, want)] = (f"{sym} ({profile})", prepare(df, Rule()))
    name_nas, nas = data[("puprime", "NAS100")]

    grid = []
    for lo in MINS:
        for hi in MAXS:
            if hi <= lo:
                continue
            rule = replace(Rule(), unit="pct", min_width=lo, max_width=hi)
            t, _ = trades(nas, rule)
            tr, te = by_period(t) if len(t) else (t, t)
            n, m, tt = stat(t)
            n1, m1, t1 = stat(tr)
            n2, m2, t2 = stat(te)
            grid.append({"banda": band(lo, hi), "mín": lo, "máx": hi, "rule": rule, "ops": n, "R neto": m, "t": tt,
                         "ops 2018-22": n1, "R 2018-22": m1, "t 2018-22": t1, "ops 2023-26": n2, "R 2023-26": m2, "t 2023-26": t2})
            print(f"  {band(lo, hi)}: {n} ops, R {m:+.3f}, t {tt:+.2f} | train {n1} {m1:+.3f} t {t1:+.2f}", flush=True)
    g = pd.DataFrame(grid)
    g.drop(columns="rule").to_csv(ROOT / "analisis" / "backtest_tbr_rejilla_pct.csv", index=False)
    bonf_t = NormalDist().inv_cdf(1 - 0.05 / len(g))                  # una cola, 5 % repartido entre las bandas

    eligible = g[g["ops 2018-22"] >= MIN_TRAIN_OPS]
    pick = eligible.loc[eligible["t 2018-22"].idxmax()]
    rule = pick["rule"]
    t_all, _ = trades(nas, rule)
    _, t_test = by_period(t_all)
    n2, m2, tt2 = stat(t_test)
    ok1 = n2 > 0 and m2 > 0 and tt2 > MIN_T
    other_rows, n_ok = [], 0
    for key in OTHERS:
        name, d = data[key]
        t, _ = trades(d, rule)
        n, m, tt = stat(t)
        n_ok += n > 0 and m > 0 and tt > MIN_T
        other_rows.append(row(name, t))
        other_rows.append(row(f"  {name} 2023-2026", by_period(t)[1]) if len(t) else [f"  {name} 2023-2026", 0] + ["-"] * 6)
    ok2 = n_ok >= MIN_OTHER
    passed = ok1 and ok2

    def f(x, fmt):
        return "-" if pd.isna(x) else format(x, fmt)

    grid_rows = [[r["banda"], r["ops"], f(r["R neto"], "+.3f"), f(r["t"], "+.2f"), r["ops 2018-22"], f(r["R 2018-22"], "+.3f"),
                  f(r["t 2018-22"], "+.2f"), r["ops 2023-26"], f(r["R 2023-26"], "+.3f"), f(r["t 2023-26"], "+.2f"),
                  "sí" if r["t"] > bonf_t and r["R neto"] > 0 else ""] for _, r in g.iterrows()]
    yrs = [row(str(y), x) for y, x in t_all.groupby(pd.to_datetime(t_all["entrada (NY)"]).dt.year)] if len(t_all) else []
    out = ["# Rejilla del ancho del TBR 18-20 NY en % del precio (M15, EMA 20)", "",
           "Script: `scripts/backtest_tbr_rejilla.py`. Reglas de la estrategia: [RESULTADOS.md](RESULTADOS.md) (con el ancho en "
           "puntos fijos).", "",
           "## Protocolo y criterios (fijados antes de ver los resultados)", "",
           f"- Rejilla de {len(g)} bandas de ancho en % del precio (cierre de las 20:00 NY).",
           f"- **Selección** solo con {name_nas} de 2018-2022: la banda con mayor t entre las que tienen ≥ {MIN_TRAIN_OPS} "
           "operaciones.",
           f"- **Se da por buena si** esa banda tiene (1) en {name_nas} de 2023 en adelante R neto > 0 con t > {MIN_T}, y (2) R neto "
           f"> 0 con t > {MIN_T} en al menos {MIN_OTHER} de 3: SP500 y DJ30 de PUPrime y NAS100 de MetaQuotes, con la misma banda.",
           "", "## Veredicto", "",
           f"Banda elegida en 2018-2022: **{pick['banda']}** ({pick['ops 2018-22']} ops, R neto {pick['R 2018-22']:+.3f}, "
           f"t {pick['t 2018-22']:+.2f}).", "",
           table([[f"{name_nas} 2023-2026: R neto > 0 y t > {MIN_T}", f"{n2} ops, {f(m2, '+.3f')} R, t {f(tt2, '+.2f')}",
                   "sí" if ok1 else "**no**"],
                  [f"Otros mercados con R neto > 0 y t > {MIN_T}", f"{n_ok} de 3", "sí" if ok2 else "**no**"]],
                 ["Criterio", "Valor", "Cumple"]), "",
           f"**{'Pasa' if passed else 'No pasa'}.**", "",
           f"## Banda elegida ({pick['banda']})", "",
           table([row(f"{name_nas}, todo", t_all), row("  2018-2022 (selección)", by_period(t_all)[0]),
                  row("  2023-2026 (prueba)", t_test), row("  sin costes", t_all, "R bruto"),
                  row("  largos", t_all[t_all["dirección"] == "long"]), row("  cortos", t_all[t_all["dirección"] == "short"])]
                 + other_rows), "",
           "Por año (NAS100 de PUPrime):", "", table(yrs), "",
           f"## Rejilla completa ({name_nas}, R neto con spread)", "",
           f"Bonferroni: t > {bonf_t:.2f} para {len(g)} bandas.", "",
           table(grid_rows, ["Banda", "Ops", "R neto", "t", "Ops 18-22", "R 18-22", "t 18-22", "Ops 23-26", "R 23-26", "t 23-26",
                             "Bonferroni"])]
    DOC.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
