"""Backtest del «modelo Green Bird» (barrido de Asia / London / PDH-PDL / hora previa a NY + reclaim, en NY AM) sobre NQ (velas M5).

Traduce los tuits y los gráficos de @greenbirdtrader (sep-oct de 2026) a reglas medibles; la lógica de la señal está en
`tradingbot.skills.pattern.green_bird` (explicada allí). Solo LEE velas (parquet de `descargar_m5.py`): el bot no envía órdenes.

Lo que muestran sus gráficos (ver docs/backtest_green_bird/RESULTADOS.md) y cómo se traduce:
  - El barrido se produce en la hora de 09:00-10:00 (sobre todo a la apertura de las 09:30) y toma varios niveles a la vez (Asia, London, PDL...),
    aunque el precio ya los hubiera cruzado antes: ventana de barrido 09:30-11:00, sin exigir nivel intacto, pero con cruce nuevo desde dentro.
  - Entra DESPUÉS del reclaim, con una vela de desplazamiento a favor (cuerpo >= 1,0 veces el medio) que sigue dentro del nivel, hasta 6 velas M5 después.
  - Stop en el extremo del barrido (unos 25-30 puntos en NQ). Gestión: parciales (1/3 a 1 R, 1/3 a 2 R), stop a la entrada tras el primer parcial y el
    resto con trailing (mínimo / máximo de las últimas 3 velas M5), como mucho hasta las 16:00 NY.
  - «One and done»: como mucho una operación por día de trading (la primera señal entre todos los niveles).

Limitaciones que no se pueden quitar con M5: él entra con velas de 1-3 minutos, así que su entrada y su stop son más finos que los de aquí.
Costes: spread fijo en puntos (`--spread`, 1,5 por defecto) una vez por operación; R neto = R bruto - spread / riesgo. Si en una vela caben el stop y el
objetivo cuenta el stop; el stop al breakeven y el trailing actúan desde la vela siguiente a la que los activa.

CRITERIOS, FIJADOS ANTES DE VER RESULTADOS (variante «principal»). Solo se da por buena si cumple TODOS:
  1. Al menos 150 operaciones.
  2. R neto medio > +0,05 con t > 2 en el histórico completo, y R neto medio > 0 en cada mitad (partido por la fecha de entrada).
  3. Mejora al control aleatorio: la misma ventana, el mismo riesgo y la misma gestión, con hora y dirección al azar (10 repeticiones).
Las demás variantes son sensibilidad: no se eligen por sus resultados (con tantas pruebas, alguna saldría bien por azar).

Uso (desde la raíz del proyecto; el parquet pide pyarrow):
    uv run --with pyarrow python scripts/backtest_green_bird.py --datos analisis/m5/metaquotes/USTEC.parquet analisis/m5/NAS100.r.parquet

Salida: docs/backtest_green_bird/RESULTADOS.md (resumen) y analisis/backtest_green_bird.csv (todas las operaciones, ignorada).
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backtest_patrones import stats                                                               # noqa: E402
from tradingbot.skills.pattern.green_bird import KINDS, Params, find_signals                      # noqa: E402

MAX_HOLD = 288                                    # velas M5 (24 h)
CASH_CLOSE = 16 * 60                              # minutos de NY: hora límite de la operación (sin gestión nocturna)
MIN_TRADES, MIN_MEAN, MIN_T = 150, 0.05, 2.0
DEFAULTS = ("analisis/m5/metaquotes/USTEC.parquet", "analisis/m5/NAS100.r.parquet")


@dataclass(frozen=True)
class Manage:
    """Gestión de la posición. `parciales`: (R, fracción). Tras `arm_r` R a favor, el stop pasa a la entrada y, con `trail_bars`, sigue al
    mínimo (largo) / máximo (corto) de las últimas velas. `until_close`: cierra a las 16:00 NY (False: hasta 24 h)."""
    parciales: tuple[tuple[float, float], ...] = ((1.0, 1 / 3), (2.0, 1 / 3))
    arm_r: float = 1.0
    trail_bars: int = 3
    until_close: bool = True


@dataclass(frozen=True)
class Variant:
    name: str
    params: Params
    manage: Manage = Manage()
    kinds: tuple[str, ...] = KINDS
    min_levels: int = 1


V2 = Params(reclaim_bars=3, intact=False, fresh_cross=True, window_end=11 * 60, displacement=1.0, entry_wait=6)
PRIMARY = "principal (desplazamiento, parciales 1 R / 2 R y trailing)"
CONTROL = "control aleatorio (misma ventana, riesgo y gestión)"
V1 = Params(reclaim_bars=3, intact=True, window_end=12 * 60, target_r=2.0)
FIXED_2R = Manage(parciales=((2.0, 1.0),), arm_r=float("inf"), trail_bars=0, until_close=False)

VARIANTS = (
    Variant(PRIMARY, V2),
    Variant("sin desplazamiento (entrada al cierre del reclaim)", Params(**{**V2.__dict__, "displacement": None})),
    Variant("desplazamiento exigente (cuerpo >= 1,5 veces)", Params(**{**V2.__dict__, "displacement": 1.5})),
    Variant("al menos 2 niveles barridos a la vez", V2, min_levels=2),
    Variant("sin parciales: stop a la entrada tras 1 R y trailing", V2, Manage(parciales=())),
    Variant("solo parciales (1 R, 2 R) sin trailing ni breakeven", V2, Manage(trail_bars=0, arm_r=float("inf"))),
    Variant("objetivo fijo 2 R", V2, FIXED_2R),
    Variant("objetivo fijo 1 R", V2, Manage(parciales=((1.0, 1.0),), arm_r=float("inf"), trail_bars=0, until_close=False)),
    Variant("la operación puede pasar del cierre (24 h)", V2, Manage(until_close=False)),
    Variant("ventana de barrido hasta las 10:00", Params(**{**V2.__dict__, "window_end": 10 * 60})),
    Variant("nivel intacto (como en la primera versión)", Params(**{**V2.__dict__, "intact": True})),
    Variant("solo Asia / London / PDH-PDL (sin la hora previa a NY)", V2, kinds=("ASIA", "LONDON", "PDHL")),
    Variant("primera versión (reclaim M5, objetivo 2 R)", V1, FIXED_2R),
)


def detect_ahead(ts: np.ndarray) -> int:
    """Desfase del servidor respecto a NY: la hora del servidor sin velas es la del mantenimiento (17:00-18:00 NY)."""
    hours = np.bincount((ts % 86400) // 3600, minlength=24)
    return ((int(np.argmin(hours)) - 17) % 24) * 3600


def load(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path).sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    return df.iloc[:-1]                           # la última vela puede seguir formándose


def simulate_managed(h, l, c, t: int, direction: str, entry: float, stop: float, end: int, m: Manage):
    """(resultado, velas, R bruto, MAE en R, MFE en R) de una posición que vive desde la vela `t` hasta `end` como máximo, con la gestión `m`."""
    risk = abs(entry - stop)
    sign = 1 if direction == "long" else -1
    targets = [(entry + sign * r * risk, f) for r, f in m.parciales]
    left, total, cur = 1.0, 0.0, stop
    armed, mae, mfe, reason = False, 0.0, 0.0, "tiempo"
    i = t
    for i in range(t, end + 1):
        worst = (entry - l[i]) if sign == 1 else (h[i] - entry)
        best = (h[i] - entry) if sign == 1 else (entry - l[i])
        mae, mfe = max(mae, worst / risk), max(mfe, best / risk)
        if (l[i] <= cur) if sign == 1 else (h[i] >= cur):                                   # el stop manda si caben stop y objetivo
            total += left * sign * (cur - entry) / risk
            left, reason = 0.0, ("stop" if cur == stop else "breakeven / trailing")
            break
        while targets and ((h[i] >= targets[0][0]) if sign == 1 else (l[i] <= targets[0][0])):
            price, frac = targets.pop(0)
            take = min(frac, left)
            total += take * sign * (price - entry) / risk
            left -= take
        if left <= 1e-9:
            left, reason = 0.0, "objetivo"
            break
        if not armed and best / risk >= m.arm_r:
            armed = True
        if armed:
            cur = max(cur, entry) if sign == 1 else min(cur, entry)
            if m.trail_bars and i >= m.trail_bars:
                trail = l[i - m.trail_bars + 1:i + 1].min() if sign == 1 else h[i - m.trail_bars + 1:i + 1].max()
                cur = max(cur, trail) if sign == 1 else min(cur, trail)
    if left > 0:
        total += left * sign * (c[i] - entry) / risk
    return reason, i - t, total, mae, mfe


def trade_end(mins, ts_len: int, t: int, m: Manage, max_hold: int) -> int:
    end = min(ts_len - 1, t + max_hold)
    if m.until_close:
        after = np.flatnonzero(mins[t:end + 1] >= CASH_CLOSE)
        if len(after) and mins[t] < CASH_CLOSE:
            end = t + int(after[0]) - 1
    return max(end, t)


def run_market(name: str, df: pd.DataFrame, spread: float, max_hold: int, rng: np.random.Generator):
    ts = df["ts"].to_numpy().astype(np.int64)
    o, h, l, c = (df[k].to_numpy().astype(float) for k in ("open", "high", "low", "close"))
    ahead = detect_ahead(ts)
    n = len(ts)
    mins = ((ts - ahead) % 86400) // 60
    trades = []
    for var in VARIANTS:
        taken: set[int] = set()
        for d, sig in find_signals(ts, ahead, o, h, l, c, var.params):
            if sig.kind not in var.kinds or sig.levels_swept < var.min_levels or d in taken:
                continue
            taken.add(d)                                       # «one and done»: la primera señal del día
            t, risk = sig.entry_bar, abs(sig.entry - sig.stop)
            end = trade_end(mins, n, t, var.manage, max_hold)
            res, bars, r_gross, mae, mfe = simulate_managed(h, l, c, t, sig.direction, sig.entry, sig.stop, end, var.manage)
            trades.append(row(var.name, name, sig.kind, sig.side, sig.levels_swept, d, sig.direction, ts, ahead, n, t, sig.entry, sig.stop,
                              risk, res, bars, r_gross, mae, mfe, spread))
            if var.name == PRIMARY:
                trades += control_rows(name, sig, ts, ahead, mins, h, l, c, n, risk, spread, d, max_hold, var, rng)
    info = {"mercado": name, "velas M5": n, "desde (NY)": pd.Timestamp(int(ts[0]) - ahead, unit="s"),
            "hasta (NY)": pd.Timestamp(int(ts[-1]) - ahead, unit="s"), "desfase servidor": f"NY + {ahead // 3600} h"}
    return trades, info


def row(variant, market, kind, side, swept, day, direction, ts, ahead, n, t, entry, stop, risk, res, bars, r_gross, mae, mfe, spread) -> dict:
    return {"variante": variant, "mercado": market, "nivel": kind, "lado barrido": side, "niveles barridos": swept, "día": day,
            "dirección": direction, "entrada (NY)": pd.Timestamp(int(ts[t]) - ahead, unit="s"), "entrada": entry, "stop": stop,
            "riesgo (puntos)": risk, "resultado": res, "velas": bars, "R bruto": r_gross, "coste (R)": spread / risk,
            "R neto": r_gross - spread / risk, "MAE (R)": mae, "MFE (R)": mfe,
            "cierre (NY)": pd.Timestamp(int(ts[min(t + bars, n - 1)]) - ahead, unit="s")}


def control_rows(market, sig, ts, ahead, mins, h, l, c, n, risk, spread, day, max_hold, var, rng, reps: int = 10) -> list[dict]:
    """Control: mismo día, mismo riesgo y misma gestión, pero con entrada en una vela al azar de la ventana de barrido y dirección al azar."""
    out = []
    lo, hi = 9 * 60 + 30, var.params.window_end
    window = np.flatnonzero((np.abs(np.arange(n) - sig.bar) <= 40) & (mins >= lo) & (mins < hi))
    window = window[window + 1 < n]
    if len(window) == 0:
        return out
    for _ in range(reps):
        i = int(rng.choice(window))
        direction = "long" if rng.random() < 0.5 else "short"
        entry = float(c[i])
        stop = entry - risk if direction == "long" else entry + risk
        end = trade_end(mins, n, i + 1, var.manage, max_hold)
        res, bars, r_gross, mae, mfe = simulate_managed(h, l, c, i + 1, direction, entry, stop, end, var.manage)
        out.append(row(CONTROL, market, sig.kind, sig.side, sig.levels_swept, day, direction, ts, ahead, n, i + 1, entry, stop, risk, res, bars,
                       r_gross, mae, mfe, spread))
    return out


def summary_row(r: pd.DataFrame) -> dict:
    if r.empty:
        return {"operaciones": 0}
    s = stats(r["R neto"], r["cierre (NY)"])
    return {"operaciones": s["operaciones"], "win rate %": s["win rate %"], "R bruto medio": r["R bruto"].mean(),
            "coste medio (R)": r["coste (R)"].mean(), "R neto medio": s["R medio"], "t": s["estadístico t"], "profit factor": s["profit factor"],
            "mejor (R)": s["mejor (R)"], "máx. drawdown (R)": s["máx. drawdown (R)"]}


def split_halves(r: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if r.empty:
        return r, r
    cut = r["entrada (NY)"].sort_values().iloc[len(r) // 2]
    return r[r["entrada (NY)"] < cut], r[r["entrada (NY)"] >= cut]


def half_means(r: pd.DataFrame) -> tuple[float, float]:
    a, b = split_halves(r)
    return (a["R neto"].mean() if len(a) else float("nan"), b["R neto"].mean() if len(b) else float("nan"))


def evaluate(primary: pd.DataFrame, control: pd.DataFrame) -> list[tuple[str, bool, str]]:
    n = len(primary)
    out = [(f"Al menos {MIN_TRADES} operaciones", n >= MIN_TRADES, f"{n} operaciones")]
    s = summary_row(primary)
    mean, t = s.get("R neto medio", float("nan")), s.get("t", float("nan"))
    m1, m2 = half_means(primary)
    out.append((f"R neto medio > {MIN_MEAN:+.2f} con t > {MIN_T:g} y positivo en cada mitad", bool(mean > MIN_MEAN and t > MIN_T and m1 > 0 and m2 > 0),
                f"completo {mean:+.3f} R (t {t:.1f}); 1.ª mitad {m1:+.3f}, 2.ª mitad {m2:+.3f}"))
    mc = control["R neto"].mean() if len(control) else float("nan")
    out.append(("Mejora al control aleatorio", bool(mean > mc), f"modelo {mean:+.3f} R frente a control {mc:+.3f} R"))
    return out


def md_table(df: pd.DataFrame, floats: int = 3) -> str:
    def fmt(x):
        if isinstance(x, (float, np.floating)):
            return "" if np.isnan(x) else f"{x:.{floats}f}"
        return str(x)
    head = "| " + " | ".join(str(c) for c in df.columns) + " |"
    sep = "|" + "|".join("---:" if i else "---" for i in range(len(df.columns))) + "|"
    rows = ["| " + " | ".join(fmt(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join([head, sep, *rows])


def build_report(trades: pd.DataFrame, infos: pd.DataFrame, args) -> str:
    lines = ["# Backtest: modelo Green Bird (barrido + reclaim con desplazamiento, parciales y trailing) sobre NQ", "",
             f"Script: `scripts/backtest_green_bird.py`. Lógica: `tradingbot/skills/pattern/green_bird.py`. Generado el {date.today():%d/%m/%Y}. "
             f"Spread supuesto: {args.spread:g} puntos por operación.", ""]
    lines += ["## Qué muestran sus gráficos", "",
              "Observado en 7 capturas de @greenbirdtrader (13, 15, 19, 20, 23 y 27 de octubre de 2026; MNQ en 1-15 min, con su indicador «Green Bird NY»):", "",
              "- Cajas de Asia (20:00-00:00) y London (02:00-05:00) con sus mínimos y máximos marcados, y la caja verde de 09:00-10:00 NY.",
              "- El barrido de Asia / London / PDL / PWL lo hace el precio dentro de la hora de 09:00-10:00 (sobre todo a la apertura de las 09:30), a veces tomando "
              "varios niveles a la vez y aunque el precio ya los hubiera cruzado antes.",
              "- Entra tras el reclaim, con una vela de desplazamiento, no en el primer cierre dentro; también opera antes de las 10:00 (27 oct, 9:42).",
              "- Stop pequeño en el extremo del barrido (24-31 puntos), objetivo lejano (R:R dibujado 8 y 11, el extremo contrario de la caja o Asia / London) y escalera de parciales.", "",
              "Solo se ve lo que publica (días ganadores) y su entrada con velas de 1-3 minutos; aquí solo hay M5.", ""]
    lines += ["## Datos", "", md_table(infos.assign(**{"desde (NY)": infos["desde (NY)"].dt.strftime("%Y-%m-%d"),
                                                      "hasta (NY)": infos["hasta (NY)"].dt.strftime("%Y-%m-%d")})), ""]
    primary, control = trades[trades["variante"] == PRIMARY], trades[trades["variante"] == CONTROL]
    results = evaluate(primary, control)
    ok = all(good for _, good, _ in results)
    lines += ["## Veredicto (criterios fijados antes de ver los resultados)", "",
              "**La hipótesis cumple todos los criterios.**" if ok else "**La hipótesis NO cumple los criterios: no hay ventaja demostrada.**", ""]
    lines += [f"- {'CUMPLE' if good else 'NO CUMPLE'} - {name}: {detail}" for name, good, detail in results]
    lines += ["", "## Variantes", "", "La primera es la hipótesis; las demás son sensibilidad, no se eligen por sus resultados. "
              "Los dos mercados cubren casi las mismas fechas: no son muestras independientes y las cifras agrupadas cuentan dos veces los mismos días.", ""]
    names = [v.name for v in VARIANTS] + [CONTROL]
    rows = [{"variante": nm, **summary_row(trades[trades["variante"] == nm]), "R neto 1.ª mitad": half_means(trades[trades["variante"] == nm])[0],
             "R neto 2.ª mitad": half_means(trades[trades["variante"] == nm])[1]} for nm in names]
    lines += [md_table(pd.DataFrame(rows)), ""]
    if len(primary):
        for title, key in (("Por mercado", "mercado"), ("Por nivel", "nivel"), ("Por dirección", "dirección"), ("Por niveles barridos a la vez", "niveles barridos"),
                           ("Por resultado", "resultado")):
            lines += [f"## Variante principal: {title.lower()}", "",
                      md_table(pd.DataFrame([{key: k, **summary_row(g)} for k, g in primary.groupby(key)])), ""]
        by_year = primary.assign(año=primary["entrada (NY)"].dt.year)
        lines += ["## Variante principal: por año", "", md_table(pd.DataFrame([{"año": k, **summary_row(g)} for k, g in by_year.groupby("año")])), ""]
    lines += ["## Cómo leerlo", "",
              "- `R bruto medio` cerca de 0 con `R neto medio` negativo significa que el movimiento no tiene memoria y el spread se come lo que quede.",
              "- Un `t` por debajo de 2 no se distingue de cero. Con 13 variantes mirando los mismos datos, alguna sale bien por azar.",
              "- Lo que NO mide: sus entradas con velas de 1-3 minutos, el tamaño variable, decidir no operar un día ni la selección de los días que publica "
              "en X (solo ganadores). Es la versión mecánica de lo que se ve en sus gráficos, con velas M5.",
              "- CFD de un solo broker, spread fijo, sin ver el recorrido interno de cada vela M5.", ""]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--datos", nargs="+", default=list(DEFAULTS), help="parquet de velas M5 (descargar_m5.py)")
    ap.add_argument("--spread", type=float, default=1.5, help="spread supuesto, en puntos del índice, por operación")
    ap.add_argument("--salida", default="docs/backtest_green_bird/RESULTADOS.md")
    ap.add_argument("--csv", default="analisis/backtest_green_bird.csv")
    ap.add_argument("--max-velas", type=int, default=MAX_HOLD, help="velas M5 como máximo con la operación abierta (288 = 24 h)")
    args = ap.parse_args()
    rng = np.random.default_rng(7)
    all_trades, infos = [], []
    for path in args.datos:
        p = Path(path)
        if not p.exists():
            print("  no existe:", p)
            continue
        trades, info = run_market(p.stem, load(p), args.spread, args.max_velas, rng)
        print(f"  {p.stem}: {info['velas M5']} velas M5 ({info['desde (NY)']:%Y-%m-%d} a {info['hasta (NY)']:%Y-%m-%d}), {info['desfase servidor']}, "
              f"{sum(1 for t in trades if t['variante'] == PRIMARY)} operaciones de la variante principal")
        all_trades += trades
        infos.append(info)
    trades, infos = pd.DataFrame(all_trades), pd.DataFrame(infos)
    if trades.empty:
        print("Sin operaciones: nada que informar.")
        return
    csv = Path(args.csv)
    csv.parent.mkdir(parents=True, exist_ok=True)
    trades.to_csv(csv, index=False)
    out = Path(args.salida)
    out.parent.mkdir(parents=True, exist_ok=True)
    report = build_report(trades, infos, args)
    out.write_text(report, encoding="utf-8")
    print(f"\nInforme: {out}\nOperaciones: {csv} ({len(trades)})\n")
    print(report.split("## Variantes")[0].split("## Veredicto")[1])


if __name__ == "__main__":
    main()
