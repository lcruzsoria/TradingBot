"""Backtest de la hipótesis «retest del VWAP dentro de la TBR, con objetivo en el extremo de su rango» (M15, índices americanos).

Solo LEE velas de MT5 (el bot no envía órdenes). La lógica de la señal está en `tradingbot.skills.pattern.vwap_retest` (explicada
allí): con la TBR ya cerrada y su rango intacto, el precio vuelve a tocar el VWAP del día de trading desde arriba (largo) o desde abajo
(corto), cierra otra vez a su favor, y se entra a mercado en la apertura de la vela siguiente, con stop bajo el VWAP y objetivo en el
extremo de la TBR. Como mucho una operación por TBR.

Método (el mismo que `backtest_patrones.py`): velas M15 de MT5, mismas TBR (Asia, London, NY Open) y mismos plazos que el bot; spread
real de MT5 en la vela de la entrada, una vez por operación (R neto = R bruto - spread / riesgo); si en una vela caben el stop y el
objetivo, cuenta el stop; 24 h como máximo. Sin breakeven (se mide la geometría pura; `--be-r` lo activa).

CRITERIOS, FIJADOS ANTES DE VER RESULTADOS (variante «principal»). Solo se da por buena si cumple TODOS:
  1. Al menos 500 operaciones.
  2. R neto medio > +0,05 y estadístico t > 2 en cada una de las dos mitades del histórico (partido por la fecha de entrada).
  3. R neto medio positivo en al menos 3 de los 4 mercados.
  4. Mejora a la línea base «sin VWAP» (la misma señal con el 50 % de la TBR en lugar del VWAP): si el VWAP no aporta nada sobre
     el 50 %, la idea no es del VWAP.
Las demás variantes son sensibilidad (no se eligen por sus resultados: con tantas pruebas, alguna saldría bien por azar).

Uso (desde la raíz del proyecto):
    uv run python scripts/backtest_vwap_tbr.py
    uv run python scripts/backtest_vwap_tbr.py --simbolos NAS100.r SP500.r --perfil puprime

Salida: docs/backtest_vwap_tbr/RESULTADOS.md (resumen, se sube a git) y analisis/backtest_vwap_tbr.csv (todas las operaciones, ignorada).
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

from backtest_patrones import (AHEAD, EXTEND, MAX_HOLD, SYMBOLS, TF_MIN, UNTIL, ZONE_ORDER, intraday_start, simulate,   # noqa: E402
                               stats)
from tradingbot.config import load_profiles, select_profile                                      # noqa: E402
from tradingbot.envconfig import EnvConfig                                                       # noqa: E402
from tradingbot.skills.feed.mt5_client import Mt5Source                                          # noqa: E402
from tradingbot.skills.levels.daylevels import DEFAULT_US_INDICES, is_us_index, vwap            # noqa: E402
from tradingbot.skills.pattern.patterns import ActiveTbr, window_for                             # noqa: E402
from tradingbot.skills.pattern.vwap_retest import Params, find_signal                            # noqa: E402
from tradingbot.skills.tbr.zones import compute, zones_from_settings                             # noqa: E402

PAD = 16                                         # velas anteriores a la ventana que se pasan a la señal (VWAP, pendiente)
MIN_TRADES, MIN_MEAN, MIN_T, MIN_MARKETS = 500, 0.05, 2.0, 3
PRIMARY, CONTROL = "principal (VWAP)", "línea base: 50 % de la TBR en lugar del VWAP"


@dataclass(frozen=True)
class Variant:
    name: str
    params: Params = Params()
    anchor: str = "vwap"                          # "vwap" o "mid" (50 % de la TBR, para la línea base)
    min_rel_range: float | None = None            # rango de la TBR >= esta fracción de la mediana de las 20 sesiones anteriores


VARIANTS = (
    Variant(PRIMARY),
    Variant(CONTROL, anchor="mid"),
    Variant("pendiente del VWAP a favor (8 velas)", Params(slope_bars=8)),
    Variant("confluencia VWAP - 50 % (10 % del rango)", Params(confluence=0.10)),
    Variant("rango de la TBR >= 80 % de la mediana", min_rel_range=0.8),
    Variant("stop a 0,15 rangos del VWAP", Params(stop_frac=0.15)),
    Variant("stop a 0,5 rangos del VWAP", Params(stop_frac=0.5)),
    Variant("objetivo: extremo + 0,5 rangos", Params(target=0.5)),
)


def run_symbol(source, sym: str, order, zones, be_r, max_hold):
    from analisis_setups import spread_prices
    source.connect()
    df = source.load_candles(sym, "15m").reset_index(drop=True)
    df = df.iloc[intraday_start(df["ts"].to_numpy()):].reset_index(drop=True)
    source.connect()
    spread = spread_prices(source, sym, df)
    df = df.iloc[:-1]                                    # la última vela sigue formándose
    spread = spread[:len(df)]
    ts = df["ts"].to_numpy().astype(np.int64)
    o, h, l, c = (df[k].to_numpy().astype(float) for k in ("open", "high", "low", "close"))
    volume = df["tick_volume"].to_numpy().astype(float)
    n = len(ts)
    day_start = (18 if is_us_index(sym, DEFAULT_US_INDICES) else 17) * 60
    vw, _ = vwap(ts, h, l, c, volume, AHEAD, day_start)
    sessions = compute(ts, h, l, zones, AHEAD, TF_MIN, days=int((ts[-1] - ts[0]) // 86400) + 3)
    history: dict[str, list[float]] = {}
    trades, funnel = [], 0
    for s in sessions:
        if not (s.complete and s.high > s.low):
            continue
        rng = s.high - s.low
        past = history.setdefault(s.zone.key, [])
        rel = rng / float(np.median(past[-20:])) if len(past) >= 10 else float("nan")
        past.append(rng)
        tbr = ActiveTbr(s.zone.key, s.zone.name, s.day, s.high, s.low, s.x0, s.x1)
        window = window_for(tbr, order, AHEAD, EXTEND, UNTIL)
        if window is None or window.end_ts is None or window.end_ts > ts[-1] + TF_MIN * 60:
            continue
        first = int(np.searchsorted(ts, window.close_ts, "left"))
        end = min(n - 1, int(np.searchsorted(ts, window.end_ts, "left")) - 1)
        if first > end or first >= n:
            continue
        funnel += 1
        lo = max(0, first - PAD)
        sl = slice(lo, end + 2)
        for var in VARIANTS:
            if var.min_rel_range is not None and not rel >= var.min_rel_range:
                continue                                  # NaN (poco historial) también se descarta
            anchor = vw[sl] if var.anchor == "vwap" else np.full(len(vw[sl]), (s.high + s.low) / 2)
            sig = find_signal(o[sl], h[sl], l[sl], c[sl], anchor, s.high, s.low, first - lo, end - lo, var.params)
            if sig is None:
                continue
            t = lo + sig.entry_bar
            risk = abs(sig.entry - sig.stop)
            res, bars, r_gross, mae, mfe = simulate(h, l, c, t, sig.direction, sig.entry, sig.stop, sig.target, max_hold, be_r)
            cost = float(spread[t]) / risk
            trades.append({"variante": var.name, "mercado": sym, "zona": tbr.zone, "día": tbr.day, "dirección": sig.direction,
                           "entrada (NY)": pd.Timestamp(int(ts[t]) - AHEAD, unit="s"), "entrada": sig.entry, "stop": sig.stop,
                           "objetivo": sig.target, "vwap": sig.vwap, "riesgo (precio)": risk, "riesgo / rango": risk / rng,
                           "R potencial": abs(sig.target - sig.entry) / risk, "resultado": res, "velas": bars,
                           "R bruto": r_gross, "coste (R)": cost, "R neto": r_gross - cost, "MAE (R)": mae, "MFE (R)": mfe,
                           "cierre (NY)": pd.Timestamp(int(ts[min(t + bars, n - 1)]) - AHEAD, unit="s")})
    info = {"mercado": sym, "velas M15": n, "desde (NY)": pd.Timestamp(int(ts[0]) - AHEAD, unit="s"),
            "hasta (NY)": pd.Timestamp(int(ts[-1]) - AHEAD, unit="s"), "TBR evaluadas": funnel}
    return trades, info


def summary_row(r: pd.DataFrame) -> dict:
    """Cifras de un grupo de operaciones (ordenadas por la hora de cierre)."""
    if r.empty:
        return {"operaciones": 0}
    s = stats(r["R neto"], r["cierre (NY)"])
    be = (1 + r["coste (R)"].mean()) / (1 + r["R potencial"].mean())          # win rate de equilibrio con la geometría de estas operaciones
    return {"operaciones": s["operaciones"], "win rate %": s["win rate %"], "equilibrio %": 100 * be, "R potencial medio": r["R potencial"].mean(),
            "R bruto medio": r["R bruto"].mean(), "coste medio (R)": r["coste (R)"].mean(), "R neto medio": s["R medio"],
            "t": s["estadístico t"], "profit factor": s["profit factor"], "máx. drawdown (R)": s["máx. drawdown (R)"]}


def split_halves(r: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if r.empty:
        return r, r
    cut = r["entrada (NY)"].sort_values().iloc[len(r) // 2]
    return r[r["entrada (NY)"] < cut], r[r["entrada (NY)"] >= cut]


def evaluate(primary: pd.DataFrame, control: pd.DataFrame) -> list[tuple[str, bool, str]]:
    """Los criterios fijados de antemano: (criterio, cumple, detalle)."""
    out = []
    n = len(primary)
    out.append((f"Al menos {MIN_TRADES} operaciones", n >= MIN_TRADES, f"{n} operaciones"))
    halves = split_halves(primary)
    cells = []
    ok = True
    for label, half in zip(("1.ª mitad", "2.ª mitad"), halves):
        row = summary_row(half)
        mean, t = row.get("R neto medio", float("nan")), row.get("t", float("nan"))
        good = bool(len(half) > 2 and mean > MIN_MEAN and t > MIN_T)
        ok &= good
        cells.append(f"{label}: {mean:+.3f} R (t {t:.1f}, {len(half)} op.)" if len(half) else f"{label}: sin operaciones")
    out.append((f"R neto medio > {MIN_MEAN:+.2f} y t > {MIN_T:g} en las dos mitades", ok, "; ".join(cells)))
    per_market = primary.groupby("mercado")["R neto"].mean() if n else pd.Series(dtype=float)
    positive = int((per_market > 0).sum())
    out.append((f"R neto medio positivo en al menos {MIN_MARKETS} mercados", positive >= MIN_MARKETS,
                ", ".join(f"{m} {v:+.3f}" for m, v in per_market.items()) or "sin datos"))
    mean_p = primary["R neto"].mean() if n else float("nan")
    mean_c = control["R neto"].mean() if len(control) else float("nan")
    out.append(("Mejora a la línea base sin VWAP", bool(mean_p > mean_c), f"VWAP {mean_p:+.3f} R frente a 50 % de la TBR {mean_c:+.3f} R"))
    return out


def md_table(df: pd.DataFrame, floats: int = 3) -> str:
    def fmt(x):
        if isinstance(x, (float, np.floating)):
            return "" if np.isnan(x) else f"{x:.{floats}f}"
        return str(x)
    head = "| " + " | ".join(str(c) for c in df.columns) + " |"
    sep = "|" + "|".join("---:" if i else "---" for i in range(len(df.columns))) + "|"
    rows = ["| " + " | ".join(fmt(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join([head, sep, *rows])


def build_report(trades: pd.DataFrame, infos: pd.DataFrame, args) -> str:
    lines = ["# Backtest: retest del VWAP dentro de la TBR (objetivo en el extremo del rango)", "",
             f"Script: `scripts/backtest_vwap_tbr.py`. Lógica: `tradingbot/skills/pattern/vwap_retest.py`. Generado el {date.today():%d/%m/%Y}.", ""]
    lines += ["## Datos", "", md_table(infos.assign(**{"desde (NY)": infos["desde (NY)"].dt.strftime("%Y-%m-%d"),
                                                      "hasta (NY)": infos["hasta (NY)"].dt.strftime("%Y-%m-%d")})), ""]
    primary, control = trades[trades["variante"] == PRIMARY], trades[trades["variante"] == CONTROL]
    results = evaluate(primary, control)
    verdict = all(ok for _, ok, _ in results)
    lines += ["## Veredicto (criterios fijados antes de ver los resultados)", "",
              "**La hipótesis cumple todos los criterios.**" if verdict else
              "**La hipótesis NO cumple los criterios: no hay ventaja demostrada.**", ""]
    lines += [f"- {'CUMPLE' if ok else 'NO CUMPLE'} - {name}: {detail}" for name, ok, detail in results]
    lines += ["", "## Variantes", "", "La primera es la hipótesis; las demás son sensibilidad, no se eligen por sus resultados.", ""]
    rows = [{"variante": name, **summary_row(g)} for name, g in ((v.name, trades[trades["variante"] == v.name]) for v in VARIANTS)]
    lines += [md_table(pd.DataFrame(rows)), ""]
    if len(primary):
        for title, key in (("Por mercado", "mercado"), ("Por zona", "zona"), ("Por dirección", "dirección")):
            lines += [f"## Variante principal: {title.lower()}", "",
                      md_table(pd.DataFrame([{key: k, **summary_row(g)} for k, g in primary.groupby(key)])), ""]
        by_year = primary.assign(año=primary["entrada (NY)"].dt.year)
        lines += ["## Variante principal: por año", "", md_table(pd.DataFrame([{"año": k, **summary_row(g)} for k, g in by_year.groupby("año")])), ""]
    lines += ["## Cómo leerlo", "",
              "- `equilibrio %` es el win rate que hace falta para empatar con la geometría real de las operaciones y sus costes; "
              "si el `win rate %` no lo supera, no hay ventaja aunque el R bruto parezca bueno.",
              "- `R bruto medio` cerca de 0 con `R neto medio` negativo significa que el movimiento no tiene memoria y el spread se come "
              "lo que quede: es el resultado que dieron los patrones Continuación y Reversión (ver `docs/backtest_patrones`).",
              "- Un `t` por debajo de 2 no se distingue de cero. Con 8 variantes mirando los mismos datos, alguna sale bien por azar.",
              "- VWAP con tick volume del broker (CFD): es un indicador del precio con el volumen de ticks, no el volumen del mercado "
              "regulado. Un solo broker, velas M15 sin ver el recorrido interno.", ""]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--simbolos", nargs="+", default=list(SYMBOLS))
    ap.add_argument("--perfil", default=None, help="perfil de MT5 (puprime, metaquotes...); por defecto el del .env")
    ap.add_argument("--salida", default="docs/backtest_vwap_tbr/RESULTADOS.md")
    ap.add_argument("--csv", default="analisis/backtest_vwap_tbr.csv")
    ap.add_argument("--max-velas", type=int, default=MAX_HOLD, help="velas M15 como máximo con la operación abierta (96 = 24 h)")
    ap.add_argument("--be-r", type=float, default=None, help="breakeven en R (por defecto, sin breakeven)")
    args = ap.parse_args()
    profiles, default = load_profiles()
    source = Mt5Source(select_profile(profiles, default, args.perfil), 2_000_000)
    print("conectado:", source.connect())
    env = EnvConfig().section("TBR")
    order, zones = zones_from_settings(env, ZONE_ORDER), zones_from_settings(env)
    all_trades, infos = [], []
    for want in args.simbolos:
        sym = source.resolve_symbol(want)
        if not sym:
            print("  sin símbolo:", want)
            continue
        trades, info = run_symbol(source, sym, order, zones, args.be_r, args.max_velas)
        main_count = sum(1 for t in trades if t["variante"] == PRIMARY)
        print(f"  {sym}: {info['velas M15']} velas M15 ({info['desde (NY)']:%Y-%m-%d} a {info['hasta (NY)']:%Y-%m-%d}), "
              f"{info['TBR evaluadas']} TBR, {main_count} entradas de la variante principal")
        all_trades += trades
        infos.append(info)
    source.close()
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
