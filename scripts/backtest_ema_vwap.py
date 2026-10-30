"""Backtest de la estrategia «Rechazo fallido del VWAP» en M15, salida de scripts/estudio_ema_vwap.py. Solo LEE velas ya descargadas.

La exploración (NAS100 de PUPrime 2018-2022) mostró que, en tendencia bajista, cuando el precio rebota hasta el VWAP y cierra otra
vez por debajo de la EMA 10 y del VWAP (el «rechazo» de manual para vender), lo que viene después es una subida. Aquí se prueba
como estrategia en datos que no se miraron al definirla.

ESTRATEGIA Y CRITERIOS, FIJADOS ANTES DE VER LOS DATOS DE PRUEBA:
- Señal (velas M15, VWAP del día de trading desde las 18:00 NY, EMA 10 de los cierres): las dos velas anteriores cerraron por
  debajo de la EMA 10 y del VWAP, y la vela actual toca el VWAP con su máximo pero vuelve a cerrar por debajo de los dos.
- Largo al cierre de esa vela. Salida al cierre de la vela 16 después (4 h) o de la última del día de trading si llega antes. Sin
  stop ni objetivo. Una posición a la vez. Resultado en ATR 14 de M15 de la vela de la señal, menos el spread de esa vela.
- Línea base: largo en cualquier vela (una cada 16), con la misma salida: lo que da la subida de fondo del mercado.
- Se da por buena si cumple TODOS:
    1. NAS100 de PUPrime de 2023 en adelante (no visto): R neto medio > 0 con t > 2.
    2. En ese periodo, el R neto medio supera al de la línea base.
    3. R neto medio > 0 con t > 1,65 en al menos 2 de 3: SP500 y DJ30 de PUPrime (todo su histórico) y NAS100 de MetaQuotes.
- Variantes (sensibilidad, no cuentan para el veredicto): tocar la EMA en lugar del VWAP; salida a las 8 velas; stop a 1,5 ATR.

Uso (desde la raíz del proyecto, con las velas descargadas por estudio_ema_vwap.py --descargar):
    uv run python scripts/backtest_ema_vwap.py

Salida: docs/estudio_ema_vwap/BACKTEST.md y analisis/backtest_ema_vwap_<mercado>.csv (operaciones).
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

from estudio_ema_vwap import TRAIN_END, cache_path, features, session_of, table          # noqa: E402

DOC = ROOT / "docs" / "estudio_ema_vwap" / "BACKTEST.md"
MIN_T_TEST, MIN_T_OTHER, MIN_OTHER = 2.0, 1.65, 2


@dataclass(frozen=True)
class Rule:
    touch: str = "vwap"                 # media que tiene que tocar la vela: "vwap" o "ema"
    hold: int = 16                      # velas hasta la salida
    stop_atr: float = 0.0               # stop a N ATR por debajo de la entrada (0 = sin stop)


def signals(d: pd.DataFrame, rule: Rule) -> np.ndarray:
    below = d["estado"].to_numpy() == "debajo"
    touch = d["high"].to_numpy() >= d[rule.touch].to_numpy()
    prev2 = np.r_[False, False, below[:-2]] & np.r_[False, below[:-1]]
    return np.flatnonzero(prev2 & below & touch)


def simulate(d: pd.DataFrame, entries: np.ndarray, rule: Rule) -> pd.DataFrame:
    """Largos en las velas `entries`, una posición a la vez."""
    c, l, atr, cost, day = (d[k].to_numpy() for k in ("close", "low", "atr", "coste", "día"))
    ny = d["ny"].to_numpy()
    rows, busy_until = [], -1
    n = len(d)
    for i in entries:
        if i <= busy_until or i + 1 >= n:
            continue
        last = i
        for j in range(i + 1, min(i + rule.hold, n - 1) + 1):          # hasta la vela `hold` o el final del día de trading
            if day[j] != day[i]:
                break
            last = j
        exit_price, how = c[last], "tiempo"
        if rule.stop_atr:
            stop = c[i] - rule.stop_atr * atr[i]
            hit = next((j for j in range(i + 1, last + 1) if l[j] <= stop), None)
            if hit is not None:
                exit_price, how, last = stop, "stop", hit
        if last == i:                                                  # señal en la última vela del día: no hay operación
            continue
        busy_until = last
        gross = (exit_price - c[i]) / atr[i]
        rows.append({"entrada (NY)": ny[i], "salida (NY)": ny[last], "entrada": c[i], "salida": exit_price, "ATR": atr[i],
                     "cómo": how, "velas": last - i, "R bruto (ATR)": gross, "coste (ATR)": cost[i], "R neto (ATR)": gross - cost[i]})
    return pd.DataFrame(rows)


def stat(t: pd.DataFrame, col: str = "R neto (ATR)") -> dict:
    x = t[col] if len(t) else pd.Series(dtype=float)
    n = len(x)
    if n < 2:
        return {"n": n, "mean": float("nan"), "t": float("nan"), "wr": float("nan"), "total": float("nan")}
    return {"n": n, "mean": float(x.mean()), "t": float(x.mean() / (x.std(ddof=1) / np.sqrt(n))), "wr": float(100 * (x > 0).mean()),
            "total": float(x.sum())}


def cells(s: dict) -> list:
    if not s["n"] or np.isnan(s["mean"]):
        return [s["n"], "-", "-", "-", "-"]
    return [s["n"], f"{s['wr']:.1f} %", f"{s['mean']:+.3f}", f"{s['t']:+.2f}", f"{s['total']:+.1f}"]


HEAD = ["", "Ops", "Acierto", "R neto medio (ATR)", "t", "R total (ATR)"]


def run(d: pd.DataFrame, rule: Rule) -> pd.DataFrame:
    return simulate(d, signals(d, rule), rule)


def baseline(d: pd.DataFrame, rule: Rule) -> pd.DataFrame:
    return simulate(d, np.arange(0, len(d), rule.hold), replace(rule, stop_atr=0.0))


def main() -> None:
    main_rule = Rule()
    sets = {}
    for profile, want in (("puprime", "NAS100"), ("puprime", "SP500"), ("puprime", "DJ30"), ("metaquotes", "NAS100")):
        sym, df = pd.read_pickle(cache_path(profile, want))
        sets[(profile, want)] = (f"{sym} ({profile})", features(df))

    name_nas, nas = sets[("puprime", "NAS100")]
    test = nas[nas["ny"] >= TRAIN_END]
    train = nas[nas["ny"] < TRAIN_END]
    t_test, b_test = run(test, main_rule), baseline(test, main_rule)
    s_test, sb_test = stat(t_test), stat(b_test)
    others = []
    for key in (("puprime", "SP500"), ("puprime", "DJ30"), ("metaquotes", "NAS100")):
        name, d = sets[key]
        tr = run(d, main_rule)
        tr.to_csv(ROOT / "analisis" / f"backtest_ema_vwap_{key[0]}_{key[1].lower()}.csv", index=False)
        others.append((name, d, tr, stat(tr), stat(baseline(d, main_rule))))
    t_test.to_csv(ROOT / "analisis" / "backtest_ema_vwap_puprime_nas100_prueba.csv", index=False)

    ok1 = s_test["n"] > 0 and s_test["mean"] > 0 and s_test["t"] > MIN_T_TEST
    ok2 = s_test["n"] > 0 and s_test["mean"] > sb_test["mean"]
    n_other = sum(s["n"] > 0 and s["mean"] > 0 and s["t"] > MIN_T_OTHER for _, _, _, s, _ in others)
    ok3 = n_other >= MIN_OTHER
    passed = ok1 and ok2 and ok3

    out = ["# Backtest: «Rechazo fallido del VWAP» (largos, M15)", "",
           "Script: `scripts/backtest_ema_vwap.py`. Exploración previa: [EXPLORACION.md](EXPLORACION.md).", "",
           "## Estrategia y criterios (fijados antes de ver los datos de prueba)", "",
           "- **Señal:** las dos velas M15 anteriores cerraron por debajo de la EMA 10 y del VWAP del día; la vela actual toca el VWAP "
           "con su máximo y vuelve a cerrar por debajo de los dos.",
           "- **Largo** al cierre de esa vela; **salida** a las 16 velas (4 h) o al final del día de trading. Sin stop. Una posición a "
           "la vez. Resultado en ATR 14 de M15, con el spread descontado.",
           "- **Línea base:** largo en cualquier vela (una cada 16) con la misma salida: la subida de fondo.",
           f"- **Se da por buena si:** (1) NAS100 de PUPrime de 2023 en adelante: R neto > 0 con t > {MIN_T_TEST}; (2) ahí supera a la "
           f"línea base; (3) R neto > 0 con t > {MIN_T_OTHER} en al menos {MIN_OTHER} de 3: SP500 y DJ30 de PUPrime, NAS100 de "
           "MetaQuotes.", "",
           "## Veredicto", "",
           table([[f"NAS100 PUPrime 2023-2026: R neto > 0 y t > {MIN_T_TEST}", f"{s_test['mean']:+.3f} ATR, t {s_test['t']:+.2f}",
                   "sí" if ok1 else "**no**"],
                  ["Supera a la línea base", f"{s_test['mean']:+.3f} frente a {sb_test['mean']:+.3f}", "sí" if ok2 else "**no**"],
                  [f"Otros mercados con R neto > 0 y t > {MIN_T_OTHER}", f"{n_other} de 3", "sí" if ok3 else "**no**"]],
                 ["Criterio", "Valor", "Cumple"]), "",
           f"**{'Pasa' if passed else 'No pasa'}.**", "",
           "## Resultados", "",
           table([[f"{name_nas} 2018-2022 (exploración)"] + cells(stat(run(train, main_rule))),
                  [f"{name_nas} 2023-2026 (prueba)"] + cells(s_test),
                  ["  línea base 2023-2026"] + cells(sb_test)]
                 + [r for name, _, _, s, sb in others for r in ([name] + cells(s), ["  línea base"] + cells(sb))], HEAD), "",
           "Sin costes (R bruto, en ATR):", "",
           table([[f"{name_nas} 2023-2026"] + cells(stat(t_test, "R bruto (ATR)"))]
                 + [[name] + cells(stat(tr, "R bruto (ATR)")) for name, _, tr, _, _ in others], HEAD), "",
           "## Por año (todos los conjuntos de prueba)", ""]
    year_rows = []
    for name, tr in [(f"{name_nas} prueba", t_test)] + [(name, tr) for name, _, tr, _, _ in others]:
        if not len(tr):
            continue
        for y, g in tr.groupby(pd.to_datetime(tr["entrada (NY)"]).dt.year):
            year_rows.append([f"{name} {y}"] + cells(stat(g)))
    out += [table(year_rows, HEAD), "", "## Por sesión de la señal", ""]
    sess_rows = []
    for name, tr in [(f"{name_nas} prueba", t_test)] + [(name, tr) for name, _, tr, _, _ in others]:
        if not len(tr):
            continue
        minute = pd.to_datetime(tr["entrada (NY)"]).dt.hour * 60 + pd.to_datetime(tr["entrada (NY)"]).dt.minute
        for sname, g in tr.groupby(session_of(minute)):
            sess_rows.append([f"{name}, {sname}"] + cells(stat(g)))
    out += [table(sess_rows, HEAD), "", "## Sensibilidad (no cuenta para el veredicto)", ""]
    sens_rows = []
    for label, rule in (("tocar la EMA en lugar del VWAP", Rule(touch="ema")), ("salida a las 8 velas", Rule(hold=8)),
                        ("stop a 1,5 ATR", Rule(stop_atr=1.5))):
        sens_rows.append([f"{label}: {name_nas} 2023-2026"] + cells(stat(run(test, rule))))
        for name, d, _, _, _ in others:
            sens_rows.append([f"{label}: {name}"] + cells(stat(run(d, rule))))
    out += [table(sens_rows, HEAD)]
    DOC.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
