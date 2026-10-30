"""Confirmación fuera de muestra de la pista de las rejillas de ORB: el ORB que termina a las 09:45 NY. Solo LEE velas de MT5.

En NAS100 de PUPrime (docs/backtest_orb_nasdaq/orbs_*m), los mejores ORB de cada duración acababan todos a las 09:45 (+0,02 a +0,04 R
netos por operación, t hasta 2,2), pero entre 362 pruebas eso puede ser azar. Aquí se prueba en datos que no se miraron al elegirla.

HIPÓTESIS Y CRITERIOS, FIJADOS ANTES DE VER ESTOS DATOS:
- Principal: ORB de 45 min de 09:00 a 09:45 NY, con las reglas de la rejilla (scripts/backtest_orb_nasdaq.py): entrada al cierre de
  la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto + 20 % del ancho;
  objetivo 1:1; a las 6 h se cierra. Una operación por día. Con el spread real de MT5.
- Datos nuevos: SP500 y DJ30 de PUPrime, y NAS100 de MetaQuotes.
- Se confirma si:
    1. R neto medio positivo con t > 1,65 (5 %, una cola) en al menos 2 de los 3 conjuntos, y
    2. juntando los 3, R neto medio positivo con t > 2.
- Los ORB de 15, 30 y 60 min que acaban a las 09:45 se muestran como contexto: no cuentan para el veredicto.

Los datos se descargan en este orden: primero los de PUPrime y al final los de MetaQuotes. Todos los perfiles comparten el
terminal de MT5, y así el terminal queda en la cuenta de MetaQuotes, la del bot por defecto.

Con --ema N se añade el filtro de tendencia (largos solo con el cierre de la rotura por encima de la EMA de N cierres en velas de
--ema-tf minutos, cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera) y se muestra también el NAS100
de PUPrime (dentro de muestra) como referencia. Es una hipótesis nueva: el veredicto sigue usando solo los 3 conjuntos nuevos.

Uso (desde la raíz del proyecto):
    uv run python scripts/confirmar_orb_0945.py
    uv run python scripts/confirmar_orb_0945.py --cache
    uv run python scripts/confirmar_orb_0945.py --cache --ema 10 --ema-tf 60

Salida: docs/backtest_orb_nasdaq/CONFIRMACION_0945.md (con la EMA, CONFIRMACION_0945_ema<N>_<tf>m.md).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from backtest_orb_nasdaq import AHEAD, GRID_WINDOW, Params, hhmm, load, row, summary, table, trades   # noqa: E402

END = 9 * 60 + 45                                   # el ORB acaba a las 09:45 NY
PRIMARY = 45                                        # minutos del ORB principal
CONTEXT = (15, 30, 60)
DATASETS = (("puprime", "SP500"), ("puprime", "DJ30"), ("metaquotes", "NAS100"))     # PUPrime primero, MetaQuotes al final
ONE_SIDED_T, POOLED_T, MIN_SETS = 1.65, 2.0, 2
DOC = ROOT / "docs" / "backtest_orb_nasdaq" / "CONFIRMACION_0945.md"


def params(minutes: int, ema: int = 0, ema_tf: int = 5) -> Params:
    start = END - minutes
    return Params(start=start, minutes=minutes, deadline=END + GRID_WINDOW, exit_min=END + GRID_WINDOW, ema=ema, ema_tf=ema_tf)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cache", action="store_true", help="reutiliza las velas ya descargadas (no se conecta a MT5)")
    ap.add_argument("--ema", type=int, default=0, help="filtro de tendencia: EMA de ese periodo (0 = sin filtro)")
    ap.add_argument("--ema-tf", type=int, default=5, help="marco de la EMA en minutos")
    args = ap.parse_args()
    ema, ema_tf = args.ema, args.ema_tf
    doc = DOC if not ema else DOC.with_name(f"CONFIRMACION_0945_ema{ema}_{ema_tf}m.md")
    reference = []

    results, pooled, context_rows, data_lines = [], [], [], []
    for profile, want in DATASETS:
        sym, df = load(profile, want, args.cache)
        ny = df["ts"].to_numpy() - AHEAD
        at17 = int(((ny % 86400) // 3600 == 17).sum())
        data_lines.append(f"- {sym} ({profile}): {len(df):,} velas M5 del {pd.Timestamp(int(ny[0]), unit='s'):%d/%m/%Y} al "
                          f"{pd.Timestamp(int(ny[-1]), unit='s'):%d/%m/%Y}; velas a las 17 h NY (pausa diaria): {at17}."
                          .replace(",", "."))
        t, funnel = trades(df, params(PRIMARY, ema, ema_tf))
        if ema:
            data_lines[-1] += f" Descartadas por la EMA: {funnel['descartadas por la EMA']} de {funnel['con rotura']} roturas."
        s = summary(t)
        ok = bool(s.get("operaciones")) and s["R medio"] > 0 and s["estadístico t"] > ONE_SIDED_T
        results.append((f"{sym} ({profile})", t, ok))
        pooled.append(t.assign(mercado=f"{sym} ({profile})"))
        for minutes in CONTEXT:
            tc, _ = trades(df, params(minutes, ema, ema_tf))
            context_rows.append(row(f"{sym}, {minutes} min ({hhmm(END - minutes)}–09:45)", tc))
        print(f"  {sym} ({profile}): {s.get('operaciones', 0)} ops, R neto {s.get('R medio', 0):+.3f}, t {s.get('estadístico t', 0):+.2f}",
              flush=True)

    if ema:                                          # referencia: el NAS100 de PUPrime, donde nació la pista (dentro de muestra)
        sym, df = load("puprime", "NAS100", True)
        tr, _ = trades(df, params(PRIMARY, ema, ema_tf))
        t0, _ = trades(df, params(PRIMARY))
        reference = [row(f"{sym} (puprime), sin EMA", t0), row(f"{sym} (puprime), con EMA", tr)]
    allt = pd.concat(pooled, ignore_index=True).sort_values("cierre (NY)")
    sp = summary(allt)
    n_ok = sum(ok for _, _, ok in results)
    c1 = n_ok >= MIN_SETS
    c2 = bool(sp.get("operaciones")) and sp["R medio"] > 0 and sp["estadístico t"] > POOLED_T
    confirmed = c1 and c2

    title = "# Confirmación del ORB que termina a las 09:45 (fuera de muestra)" + (
        f", con filtro EMA {ema} en velas de {ema_tf} min" if ema else "")
    out = [title, "",
           "Script: `scripts/confirmar_orb_0945.py`. Solo lee velas de MT5.", "",
           "## Hipótesis y criterios (fijados antes de ver estos datos)", "",
           f"- **Principal:** ORB de {PRIMARY} min de {hhmm(END - PRIMARY)} a 09:45 NY; entrada al cierre de la primera vela M5 que "
           f"cierra fuera del ORB, como tarde {GRID_WINDOW // 60} h después; stop en el extremo opuesto + 20 % del ancho; objetivo "
           "1:1; cierre a las 6 h. Con el spread real de MT5.",
           "- **Datos nuevos** (no se miraron al elegir la hipótesis): SP500 y DJ30 de PUPrime, NAS100 de MetaQuotes.",
           f"- **Se confirma si** (1) R neto medio positivo con t > {ONE_SIDED_T} en al menos {MIN_SETS} de los 3 conjuntos y "
           f"(2) los 3 juntos dan R neto medio positivo con t > {POOLED_T}.", "",
           *([f"- **Filtro EMA {ema} ({ema_tf} min):** largos solo con el cierre de la rotura por encima de la EMA y cortos solo "
               "por debajo; si la primera rotura del día va contra la EMA, ese día no se opera.", ""] if ema else []),
           "## Datos", "", *data_lines, "",
           "## Veredicto", "",
           table([[f"R neto > 0 y t > {ONE_SIDED_T} en al menos {MIN_SETS} de 3", f"{n_ok} de 3", "sí" if c1 else "**no**"],
                  [f"Los 3 juntos: R neto > 0 y t > {POOLED_T}",
                   f"{sp.get('R medio', 0):+.3f} R, t {sp.get('estadístico t', 0):+.2f}", "sí" if c2 else "**no**"]],
                 ["Criterio", "Valor", "Cumple"]), "",
           f"**{'Se confirma' if confirmed else 'No se confirma'}.**", "",
           f"## ORB principal ({PRIMARY} min, {hhmm(END - PRIMARY)}–09:45)", "",
           table([row(name, t) for name, t, _ in results] + [row("Los 3 juntos", allt)]), "",
           "Sin costes (R bruto):", "",
           table([row(name, t, "R bruto") for name, t, _ in results] + [row("Los 3 juntos", allt, "R bruto")]), "",
           "Por lado:", "",
           table([row(f"{name}, {side}", t[t["dirección"] == side]) for name, t, _ in results for side in ("long", "short")]), "",
           "Por mitades del histórico:", "",
           table([row(f"{name}, {half}", part) for name, t, _ in results
                  for half, part in zip(("1.ª mitad", "2.ª mitad"),
                                        (t[t["entrada (NY)"] <= t["entrada (NY)"].median()],
                                         t[t["entrada (NY)"] > t["entrada (NY)"].median()]))]), "",
           *(["## Referencia: NAS100 de PUPrime (dentro de muestra, no cuenta para el veredicto)", "", table(reference), ""]
             if reference else []),
           "## Contexto: las otras duraciones que acaban a las 09:45 (no cuentan para el veredicto)", "",
           table(context_rows)]
    doc.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))
    print(f"\nInforme: {doc}")


if __name__ == "__main__":
    main()
