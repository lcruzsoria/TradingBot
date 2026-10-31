"""Backtest del TBR de 18:00 a 20:00 NY con filtro de ancho y EMA 20, en velas M15. Solo LEE velas ya descargadas.

ESTRATEGIA (la del usuario) Y CRITERIOS, FIJADOS ANTES DE VER LOS RESULTADOS:
- TBR: máximo y mínimo de las velas M15 de 18:00 a 20:00 NY (el inicio del día de trading). Solo vale si su ancho está entre 100 y
  300 puntos del NAS100. Fuera de ese ancho no se opera ese día.
- Rotura con cuerpo: la primera vela M15 que cierra por encima del máximo (largo) o por debajo del mínimo (corto) del TBR y del
  mismo lado de la EMA 20 de los cierres M15. Las roturas contra la EMA se ignoran y se sigue esperando. La rotura tiene que cerrar
  como tarde a las 00:00 NY; si no, se cancela el día. Una operación por día.
- Entrada a la apertura de la vela siguiente. Stop en el extremo contrario del TBR; objetivo 2R. Al llegar a 1R el stop pasa a la
  entrada (BE). Si en una misma vela se tocan el stop y el objetivo, cuenta el stop. Dentro del trade se sigue hasta el stop o el
  objetivo, aunque pase de día.
- Costes: spread real de MT5 en la vela de entrada (R neto = R bruto - spread / riesgo).
- Otros mercados: el ancho se pasa a puntos del NAS100 con la relación de precios de ese día (ancho × NAS100 / mercado al cierre
  de las 20:00), para pedir el mismo tamaño relativo de rango.
- Se da por buena si cumple TODOS:
    1. NAS100 de PUPrime, todo el histórico: al menos 100 operaciones y R neto medio > +0,05 con t > 2.
    2. R neto medio positivo en 2018-2022 y en 2023 en adelante.
    3. R neto medio > 0 con t > 1,65 en al menos 2 de 3: SP500 y DJ30 de PUPrime y NAS100 de MetaQuotes.
- Variantes (sensibilidad, no cuentan para el veredicto): sin filtro EMA; anular el día si la primera rotura va contra la EMA;
  sin BE; objetivo 1R; sin filtro de ancho.

Uso (desde la raíz del proyecto, con las velas M15 de scripts/estudio_ema_vwap.py --descargar):
    uv run python scripts/backtest_tbr.py

Salida: docs/backtest_tbr/RESULTADOS.md y analisis/backtest_tbr_<mercado>.csv (operaciones).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from backtest_orb_nasdaq import halves, row, summary, table                           # noqa: E402
from estudio_ema_vwap import AHEAD, DAY_START, TRAIN_END, cache_path                  # noqa: E402

DOC = ROOT / "docs" / "backtest_tbr" / "RESULTADOS.md"
TBR_END = 20 * 60                                       # el TBR va de 18:00 (inicio del día de trading) a 20:00 NY
SETUP_END = 24 * 60                                     # la rotura tiene que cerrar como tarde a las 00:00 NY
MIN_OPS, MIN_MEAN, MIN_T, MIN_T_OTHER, MIN_OTHER = 100, 0.05, 2.0, 1.65, 2


@dataclass(frozen=True)
class Rule:
    min_width: float = 100.0                            # ancho del TBR en puntos del NAS100
    max_width: float = 300.0                            # 0 = sin filtro de ancho
    unit: str = "puntos"                                # "puntos" del NAS100 o "pct" del precio (cierre de las 20:00)
    ema: int = 20                                       # 0 = sin filtro EMA
    against: str = "esperar"                            # rotura contra la EMA: "esperar" a otra o "anular" el día
    rr: float = 2.0
    be_at: float = 1.0                                  # el stop pasa a la entrada al llegar a este R (0 = sin BE)


def prepare(df: pd.DataFrame, rule: Rule) -> pd.DataFrame:
    d = df.copy()
    ny = d["ts"].to_numpy() - AHEAD
    d["ny"] = pd.to_datetime(ny, unit="s")
    minute = (ny // 60) % 1440
    d["desde"] = (minute - DAY_START) % 1440            # minutos desde las 18:00 NY
    d["día"] = (ny // 60 - DAY_START + 1440) // 1440
    d["ema"] = d["close"].ewm(span=rule.ema, adjust=False).mean() if rule.ema else np.nan
    return d


def ranges(d: pd.DataFrame) -> pd.DataFrame:
    """TBR de cada día de trading: máximo, mínimo, cierre de las 20:00 y número de velas."""
    tbr = d[d["desde"] < TBR_END - DAY_START]
    g = tbr.groupby("día").agg(hi=("high", "max"), lo=("low", "min"), cierre=("close", "last"), velas=("high", "size"),
                                  fecha=("ny", "first"))
    return g[g["velas"] >= 7]


def trades(d: pd.DataFrame, rule: Rule, scale: pd.Series | None = None) -> tuple[pd.DataFrame, dict]:
    """Una operación como mucho por día de trading. `scale` pasa el ancho a puntos del NAS100 (1 en el propio NAS100)."""
    o, h, l, c, ema, spread = (d[k].to_numpy() for k in ("open", "high", "low", "close", "ema", "spread"))
    since, day, ny = d["desde"].to_numpy(), d["día"].to_numpy(), d["ny"].to_numpy()
    starts = np.flatnonzero(np.r_[True, day[1:] != day[:-1]])
    first = dict(zip(day[starts], starts))
    rng = ranges(d)
    funnel = {"días con TBR": len(rng), "ancho válido": 0, "con rotura": 0, "roturas contra la EMA ignoradas": 0, "operaciones": 0}
    rows, n = [], len(d)
    for dy, r in rng.iterrows():
        width = r["hi"] - r["lo"]
        if rule.unit == "pct":
            eq = 100 * width / r["cierre"]
        else:
            eq = width * (scale.get(dy, np.nan) if scale is not None else 1.0)
        if rule.max_width and not (rule.min_width <= eq <= rule.max_width):
            continue
        funnel["ancho válido"] += 1
        i, hit = first[dy], None
        while i < n and day[i] == dy and since[i] + 15 <= SETUP_END - DAY_START:
            if since[i] >= TBR_END - DAY_START and (c[i] > r["hi"] or c[i] < r["lo"]):
                long = c[i] > r["hi"]
                if rule.ema and ((c[i] <= ema[i]) if long else (c[i] >= ema[i])):
                    funnel["roturas contra la EMA ignoradas"] += 1
                    if rule.against == "anular":
                        break
                else:
                    hit = i
                    break
            i += 1
        if hit is None:
            continue
        funnel["con rotura"] += 1
        e = hit + 1
        if e >= n or day[e] != dy:
            continue
        long = c[hit] > r["hi"]
        entry = o[e]
        stop = r["lo"] if long else r["hi"]
        risk = (entry - stop) if long else (stop - entry)
        if risk <= 0:                                   # abre ya al otro lado del TBR
            continue
        sgn = 1 if long else -1
        target = entry + sgn * rule.rr * risk
        cur_stop, how, exit_price, j = stop, "fin de datos", None, e
        while j < n:                                    # dentro del trade se sigue hasta el stop o el objetivo, sin límite de hora
            adverse = l[j] <= cur_stop if long else h[j] >= cur_stop
            favour = h[j] >= target if long else l[j] <= target
            if adverse:
                exit_price, how = cur_stop, ("BE" if cur_stop == entry else "stop")
                break
            if favour:
                exit_price, how = target, "objetivo"
                break
            if rule.be_at and ((h[j] - entry) if long else (entry - l[j])) >= rule.be_at * risk:
                cur_stop = entry
            j += 1
        if exit_price is None:
            j -= 1
            exit_price = c[j]
        gross = sgn * (exit_price - entry) / risk
        cost = spread[e] / risk
        funnel["operaciones"] += 1
        rows.append({"entrada (NY)": ny[e], "cierre (NY)": ny[j], "dirección": "long" if long else "short", "ancho TBR": width,
                     "ancho NAS100": eq, "entrada": entry, "stop": stop, "objetivo": target, "salida": exit_price, "cómo": how,
                     "R bruto": gross, "coste (R)": cost, "R neto": gross - cost})
    return pd.DataFrame(rows), funnel


def nas_scale(nas: pd.DataFrame, other: pd.DataFrame) -> pd.Series:
    """Relación de precios NAS100 / mercado al cierre del TBR de cada día de trading."""
    return ranges(nas)["cierre"] / ranges(other)["cierre"]


def by_period(t: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    return t[t["entrada (NY)"] < TRAIN_END], t[t["entrada (NY)"] >= TRAIN_END]


def main() -> None:
    base = Rule()
    raw = {}
    for profile, want in (("puprime", "NAS100"), ("puprime", "SP500"), ("puprime", "DJ30"), ("metaquotes", "NAS100")):
        sym, df = pd.read_pickle(cache_path(profile, want))
        raw[(profile, want)] = (f"{sym} ({profile})", df)

    def run(key, rule):
        name, df = raw[key]
        d = prepare(df, rule)
        scale = None
        if key != ("puprime", "NAS100"):
            scale = nas_scale(prepare(raw[("puprime", "NAS100")][1], rule), d)
        return trades(d, rule, scale)

    nas_key = ("puprime", "NAS100")
    name_nas = raw[nas_key][0]
    main_t, funnel = run(nas_key, base)
    main_t.to_csv(ROOT / "analisis" / "backtest_tbr_puprime_nas100.csv", index=False)
    s = summary(main_t)
    p1, p2 = by_period(main_t)
    s1, s2 = summary(p1), summary(p2)
    others = []
    for key in (("puprime", "SP500"), ("puprime", "DJ30"), ("metaquotes", "NAS100")):
        t, f = run(key, base)
        t.to_csv(ROOT / "analisis" / f"backtest_tbr_{key[0]}_{key[1].lower()}.csv", index=False)
        others.append((raw[key][0], key, t, f, summary(t)))

    ok1 = s.get("operaciones", 0) >= MIN_OPS and s["R medio"] > MIN_MEAN and s["estadístico t"] > MIN_T
    ok2 = bool(s1.get("operaciones")) and bool(s2.get("operaciones")) and s1["R medio"] > 0 and s2["R medio"] > 0
    n_other = sum(bool(so.get("operaciones")) and so["R medio"] > 0 and so["estadístico t"] > MIN_T_OTHER
                  for _, _, _, _, so in others)
    ok3 = n_other >= MIN_OTHER
    passed = ok1 and ok2 and ok3

    def val(x: dict) -> str:
        return f"{x['R medio']:+.3f} R, t {x['estadístico t']:+.2f}" if x.get("operaciones") else "sin operaciones"

    widths = ranges(prepare(raw[nas_key][1], base))
    w = widths["hi"] - widths["lo"]
    out = ["# Backtest: TBR de 18:00 a 20:00 NY con EMA 20 (M15)", "",
           "Script: `scripts/backtest_tbr.py`. Solo lee velas M15 ya descargadas.", "",
           "## Estrategia y criterios (fijados antes de ver los resultados)", "",
           "- **TBR:** máximo y mínimo de las velas M15 de 18:00 a 20:00 NY. Solo se opera si mide entre 100 y 300 puntos del "
           "NAS100.",
           "- **Rotura con cuerpo:** la primera vela M15 que cierra fuera del TBR y del mismo lado de la EMA 20 (las roturas contra "
           "la EMA se ignoran y se sigue esperando). Tiene que cerrar como tarde a las 00:00 NY; si no, se cancela el día. Una "
           "operación por día.",
           "- **Entrada** a la apertura de la vela siguiente; **stop** en el extremo contrario del TBR; **objetivo** 2R; a 1R el "
           "stop pasa a la entrada (BE). Stop y objetivo en la misma vela: cuenta el stop. Dentro del trade se sigue hasta el stop o "
           "el objetivo, aunque pase de día.",
           "- **Costes:** spread real de MT5 en la vela de entrada.",
           "- **Otros mercados:** el ancho se pasa a puntos del NAS100 con la relación de precios del día.",
           f"- **Se da por buena si:** (1) NAS100 de PUPrime, todo el histórico: ≥ {MIN_OPS} operaciones y R neto > +{MIN_MEAN} con "
           f"t > {MIN_T}; (2) R neto positivo en 2018-2022 y en 2023 en adelante; (3) R neto > 0 con t > {MIN_T_OTHER} en al menos "
           f"{MIN_OTHER} de 3: SP500 y DJ30 de PUPrime, NAS100 de MetaQuotes.", "",
           "## Veredicto", "",
           table([[f"{name_nas}: ≥ {MIN_OPS} ops, R neto > +{MIN_MEAN}, t > {MIN_T}",
                   f"{s.get('operaciones', 0)} ops, {val(s)}", "sí" if ok1 else "**no**"],
                  ["Positivo en 2018-2022 y en 2023-2026", f"{val(s1)} / {val(s2)}", "sí" if ok2 else "**no**"],
                  [f"Otros mercados con R neto > 0 y t > {MIN_T_OTHER}", f"{n_other} de 3", "sí" if ok3 else "**no**"]],
                 ["Criterio", "Valor", "Cumple"]), "",
           f"**{'Pasa' if passed else 'No pasa'}.**", "",
           "## Ancho del TBR en el NAS100 de PUPrime", "",
           f"{len(w)} días. Mediana {w.median():.1f} puntos; percentil 10 {w.quantile(.1):.1f}, percentil 90 {w.quantile(.9):.1f}. "
           f"Entre {base.min_width:.0f} y {base.max_width:.0f} puntos: "
           f"{100 * ((w >= base.min_width) & (w <= base.max_width)).mean():.1f} % de los días. Mediana por año: "
           + ", ".join(f"{y} {v:.0f}" for y, v in w.groupby(widths["fecha"].dt.year).median().items()) + ".", "",
           "Embudo: " + ", ".join(f"{k} {v}" for k, v in funnel.items()) + ".", "",
           "## Resultados (R neto, con spread)", "",
           table([row(f"{name_nas}, todo", main_t), row("  2018-2022", p1), row("  2023-2026", p2),
                  row("  sin costes (R bruto)", main_t, "R bruto"),
                  row("  largos", main_t[main_t["dirección"] == "long"]) if len(main_t) else ["  largos", 0] + ["-"] * 6,
                  row("  cortos", main_t[main_t["dirección"] == "short"]) if len(main_t) else ["  cortos", 0] + ["-"] * 6]
                 + [row(name, t) for name, _, t, _, _ in others]
                 + [row(f"{name} sin costes", t, "R bruto") for name, _, t, _, _ in others]), "",
           "Cómo terminan (NAS100 de PUPrime): " + (", ".join(f"{k} {v}" for k, v in main_t["cómo"].value_counts().items())
                                                    if len(main_t) else "-")
           + (f". Coste medio {main_t['coste (R)'].mean():.3f} R." if len(main_t) else "."), "",
           "Embudo de los otros mercados: " + "; ".join(
               f"{name}: " + ", ".join(f"{k} {v}" for k, v in f.items()) for name, _, _, f, _ in others) + ".", "",
           "## Por año (NAS100 de PUPrime)", ""]
    year_rows = [row(str(y), g) for y, g in main_t.groupby(pd.to_datetime(main_t["entrada (NY)"]).dt.year)] if len(main_t) else []
    out += [table(year_rows), "", "## Sensibilidad (no cuenta para el veredicto)", ""]
    sens = []
    for label, rule in (("sin filtro EMA", replace(base, ema=0)), ("anular el día si la rotura va contra la EMA",
                                                                    replace(base, against="anular")),
                        ("sin BE", replace(base, be_at=0.0)), ("objetivo 1R (BE desactivado)", replace(base, rr=1.0, be_at=0.0)),
                        ("sin filtro de ancho", replace(base, max_width=0.0))):
        sens.append(row(f"{label}: {name_nas}", run(nas_key, rule)[0]))
        for name, key, _, _, _ in others:
            sens.append(row(f"{label}: {name}", run(key, rule)[0]))
    out += [table(sens)]
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
