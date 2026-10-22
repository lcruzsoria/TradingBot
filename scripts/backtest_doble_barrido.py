"""Backtest del patrón «Doble barrido TBR» (NY Open barre los niveles de Asia y London) con velas M5.

Solo LEE velas ya descargadas (analisis/m5/<símbolo>.parquet, ver scripts/descargar_m5.py): no necesita MT5 ni envía órdenes. Cada día
aplica `tradingbot.skills.pattern.doble_barrido` con las mismas reglas que en vivo (TBR de Asia, London y NY Open, cierre con cuerpo
sobre los dos niveles, retesteo desde NY Open, un solo trade al día) y simula la operación con `tradingbot.skills.setup.positions.resolve`,
la misma que sigue las posiciones del bot: stop, objetivo, breakeven en cuanto el precio toca +1 R y cierre al final del día de trading
(o a las 24 h). El resultado es BRUTO: los parquet no traen el spread.

Barrido de variantes del stop (`--stops`): el 0,618 del fibonacci nivel -> swing es el propuesto; 1 es el propio swing.

Uso (desde la raíz del proyecto):
    uv run --with pyarrow python scripts/backtest_doble_barrido.py
    uv run --with pyarrow --with openpyxl python scripts/backtest_doble_barrido.py --simbolos NAS100.r DJ30.r --stops 0.5 0.618 1

Salida: tabla por consola y analisis/backtest_doble_barrido.xlsx si openpyxl está instalado (carpeta ignorada por git).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tradingbot.envconfig import EnvConfig                                           # noqa: E402
from tradingbot.skills.levels.daylevels import DEFAULT_US_INDICES, is_us_index          # noqa: E402
from tradingbot.skills.bias.history import block_ids, lateral_flags, score_history      # noqa: E402
from tradingbot.skills.pattern.doble_barrido import DEFAULT_STOP_FIB, ENTRIES, _earlier, analyze          # noqa: E402
from tradingbot.skills.pattern.patterns import (DETECTED, ActiveTbr, PatternContext, PeerTbr,   # noqa: E402
                                                history_tbrs, window_for)
from tradingbot.skills.pattern.trade import MAX_HOLD_SECONDS, day_close              # noqa: E402
from tradingbot.skills.setup.positions import resolve                                 # noqa: E402
from tradingbot.skills.tbr.zones import compute, zones_from_settings                 # noqa: E402

AHEAD = 7 * 3600                                  # servidor del broker = NY + 7 h (Vantage, como el resto de scripts)
TF_MIN = 5
SYMBOLS = ("NAS100.r", "SP500.r", "DJ30.r")
ZONE_ORDER = ["ASIA", "LONDON", "NY_AM", "NY_PM"]
UNTIL = {"LONDON": "NY_AM:FIN", "NY_AM": "@18:00"}      # plazos del bot (los de skills/pattern/skill.py)
BIAS_RULES = [("prev_day_break", 2.0), ("tdo", 2.0), ("midnight", 1.0), ("htf_break", 2.0)]     # el sesgo del bot (como backtest_patrones.py)
BIAS_MIN = 3.0
DAYS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def stats(r: pd.Series) -> dict:
    """Métricas de una serie de R por operación (en orden de entrada)."""
    r = r.astype(float)
    n = len(r)
    if n == 0:
        return {"operaciones": 0}
    wins, losses = r[r > 0], r[r < 0]
    equity = r.cumsum()
    dd = (equity.cummax().clip(lower=0) - equity).max()
    streak = longest = 0
    for x in r:
        streak = streak + 1 if x < 0 else 0
        longest = max(longest, streak)
    sd = r.std(ddof=1) if n > 2 else 0.0
    return {"operaciones": n, "win rate %": 100 * (r > 0).mean(), "R medio": r.mean(), "R total": r.sum(),
            "profit factor": (wins.sum() / -losses.sum()) if len(losses) and losses.sum() < 0 else np.nan,
            "ganancia media (R)": wins.mean() if len(wins) else np.nan, "pérdida media (R)": losses.mean() if len(losses) else np.nan,
            "máx. drawdown (R)": -dd, "racha perdedora máx.": longest,
            "estadístico t": r.mean() / (sd / np.sqrt(n)) if sd > 0 else 0.0}


def load(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path).sort_values("ts").drop_duplicates("ts").reset_index(drop=True)
    return df.iloc[:-1]                                # la última vela puede seguir formándose


def bias_m15(ts, o, h, l, c, us_index: bool):
    """(horas M15, sesgo -1/0/1, lateral) del bot, calculado con las velas M15 agrupadas desde las M5, sin mirar al futuro."""
    g = pd.DataFrame({"ts": ts // 900 * 900, "o": o, "h": h, "l": l, "c": c}).groupby("ts").agg(o=("o", "first"), h=("h", "max"), l=("l", "min"), c=("c", "last"))
    t15 = g.index.to_numpy().astype(np.int64)
    o15, h15, l15, c15 = (g[k].to_numpy() for k in ("o", "h", "l", "c"))
    day_start, recalc = (18 * 60, 3) if us_index else (17 * 60, 4)
    score = score_history(t15, o15, h15, l15, c15, BIAS_RULES, AHEAD, day_start, recalc, recalc, 30)
    ids = block_ids(t15 - AHEAD, day_start * 60, recalc)
    lateral = lateral_flags(t15, c15, 6.0, 0.15, ids)
    bias = np.where(lateral, 0, np.where(score >= BIAS_MIN, 1, np.where(score <= -BIAS_MIN, -1, 0)))
    return t15, bias, lateral


def run_symbol(df: pd.DataFrame, sym: str, order, zones, stop_fib: float, be_r: float | None, entry_mode: str = ENTRIES[0],
               target_r: float | None = None):
    """(operaciones, embudo) de un mercado con una variante de stop."""
    ts = df["ts"].to_numpy().astype(np.int64)
    o, h, l, c = (df[k].to_numpy().astype(float) for k in ("open", "high", "low", "close"))
    n = len(ts)
    us_index = is_us_index(sym, DEFAULT_US_INDICES)
    day_end = (18 if us_index else 17) * 60                                    # el día de trading acaba a las 18:00 NY en índices USA
    t15, bias15, lateral15 = bias_m15(ts, o, h, l, c, us_index)
    sessions = compute(ts, h, l, zones, AHEAD, TF_MIN, days=int((ts[-1] - ts[0]) // 86400) + 3)
    peers = []
    for item in history_tbrs(sessions, None, set(), 100_000):
        w = window_for(item, order, AHEAD, (), UNTIL)
        if w is not None:
            peers.append(PeerTbr(item.key, item.zone, item.day, item.high, item.low, w.start_ts, w.close_ts))
    peers = tuple(peers)
    trades, funnel = [], []
    for s in sessions:
        if s.zone.key != "NY_AM" or not (s.complete and s.high > s.low):
            continue
        tbr = ActiveTbr(s.zone.key, s.zone.name, s.day, s.high, s.low, s.x0, s.x1)
        window = window_for(tbr, order, AHEAD, (), UNTIL)
        if window is None or window.end_ts is None or window.end_ts > ts[-1] + TF_MIN * 60:
            continue                                              # plazo todavía abierto: no se evalúa
        first = int(np.searchsorted(ts, window.close_ts, "left"))
        start = int(np.searchsorted(ts, window.start_ts, "left"))
        end = min(n - 1, int(np.searchsorted(ts, window.end_ts, "left")) - 1)
        if first > end or first >= n:
            continue
        ctx = PatternContext(sym, "5m", TF_MIN, ts, o, h, l, c, tbr, first, end, True, window.next_zone, window.next_hours, AHEAD,
                             start, window.limit_verb, day_end, be_r, peers)
        hits, _figs = analyze(ctx, stop_fib, entry_mode)
        for hit in hits:
            funnel.append({"mercado": sym, "día": tbr.day, "dirección": hit.direction, "estado": hit.status, "motivo": hit.detail})
            if hit.status != DETECTED:
                continue
            t = hit.x
            entry, stop, target = hit.price, hit.levels["stop"], hit.levels["target"]
            risk = abs(entry - stop)
            if risk <= 0:
                continue
            if target_r is not None:                                  # variante: objetivo fijo en R en vez del extremo de Asia/London
                target = entry - target_r * risk if hit.direction == "short" else entry + target_r * risk
            close_ts = min(int(ts[t]) + MAX_HOLD_SECONDS, day_close(int(ts[t]), AHEAD, day_end))
            (asia, london), _ = _earlier(ctx)
            up = hit.direction == "short"
            a_lvl, l_lvl = (asia.high, london.high) if up else (asia.low, london.low)
            k15 = int(np.searchsorted(t15, int(ts[t]), "right")) - 1
            want = -1 if up else 1
            order_ = SimpleNamespace(direction=hit.direction, pattern_key="doble_barrido", price=entry, stop=stop, target=target,
                                     entry_ts=int(ts[t]), close_ts=close_ts)
            done = resolve(order_, ts, h, l, c, be_r, TF_MIN * 60)
            if done is None:
                continue                                          # sigue abierta al final de los datos
            trades.append({"mercado": sym, "día": tbr.day, "dirección": hit.direction,
                           "entrada (NY)": pd.Timestamp(int(ts[t]) - AHEAD, unit="s"), "entrada": entry, "stop": stop,
                           "objetivo": target, "riesgo (precio)": risk, "riesgo %": 100 * risk / entry,
                           "recorrido objetivo (R)": abs(target - entry) / risk, "resultado": done.result, "R": done.r,
                           "hora entrada (NY)": (int(ts[t]) - AHEAD) % 86400 / 3600, "dentro de NY Open": bool(t < first),
                           "Asia es el nivel más extremo": bool((a_lvl >= l_lvl) if up else (a_lvl <= l_lvl)),
                           "rango Asia %": 100 * (asia.high - asia.low) / entry, "rango London %": 100 * (london.high - london.low) / entry,
                           "distancia entre niveles (R)": abs(a_lvl - l_lvl) / risk,
                           "sesgo vs operación": "a favor" if bias15[k15] == want else "en contra" if bias15[k15] == -want else "sin sesgo",
                           "lateral": bool(lateral15[k15]),
                           "salida (NY)": pd.Timestamp(done.exit_ts - AHEAD, unit="s")})
    return trades, funnel


def summary(trades: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    rows = []
    for key, g in trades.groupby(by, observed=True):
        key = key if isinstance(key, tuple) else (key,)
        rows.append({**dict(zip(by, key)), **stats(g.sort_values("entrada (NY)")["R"])})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--simbolos", nargs="+", default=list(SYMBOLS))
    ap.add_argument("--carpeta", default="analisis/m5", help="carpeta con los parquet M5 (<símbolo>.parquet)")
    ap.add_argument("--stops", nargs="+", type=float, default=[DEFAULT_STOP_FIB, 0.5, 0.786, 1.0],
                    help="niveles del fibonacci (0 = nivel de entrada, 1 = swing) donde probar el stop")
    ap.add_argument("--entradas", nargs="+", default=[ENTRIES[0]], choices=ENTRIES,
                    help="nivel que se retestea: extremo (el más alto/bajo de los dos), asia o primero (el que el precio toca antes)")
    ap.add_argument("--be-r", type=float, default=None,
                    help="breakeven en R (por defecto SETUP_BE_TRIGGER_PCT / SETUP_RISK_PCT del bot; 0 = sin breakeven)")
    ap.add_argument("--salida", default="analisis/backtest_doble_barrido.xlsx")
    args = ap.parse_args()
    setup = EnvConfig().section("SETUP")
    be_pct, risk_pct = setup.get_float("BE_TRIGGER_PCT", 1.0), setup.get_float("RISK_PCT", 1.0)
    be_r = args.be_r if args.be_r is not None else (be_pct / risk_pct if be_pct > 0 and risk_pct > 0 else None)
    be_r = None if be_r is not None and be_r <= 0 else be_r
    print("breakeven:", "sin breakeven" if be_r is None else f"stop a la entrada en cuanto el precio toca +{be_r:g} R")
    env = EnvConfig().section("TBR")
    order, zones = zones_from_settings(env, ZONE_ORDER), zones_from_settings(env)
    frames = {}
    for sym in args.simbolos:
        path = Path(args.carpeta) / f"{sym}.parquet"
        if not path.exists():
            print("  sin datos:", path)
            continue
        frames[sym] = load(path)
        d = frames[sym]
        print(f"  {sym}: {len(d)} velas M5 ({pd.Timestamp(int(d['ts'].iloc[0]) - AHEAD, unit='s'):%Y-%m-%d} a "
              f"{pd.Timestamp(int(d['ts'].iloc[-1]) - AHEAD, unit='s'):%Y-%m-%d})")
    all_trades, funnel = [], []
    for entry_mode in args.entradas:
        for stop_fib in args.stops:
            for sym, df in frames.items():
                trades, fun = run_symbol(df, sym, order, zones, stop_fib, be_r, entry_mode)
                all_trades += [{"entrada en": entry_mode, "stop (fibo)": stop_fib, **t} for t in trades]
                if stop_fib == args.stops[0]:
                    funnel += [{"entrada en": entry_mode, **f} for f in fun]
    trades = pd.DataFrame(all_trades)
    if trades.empty:
        print("sin operaciones")
        return
    trades["año"] = trades["entrada (NY)"].dt.year
    trades["día semana"] = trades["entrada (NY)"].dt.dayofweek.map(dict(enumerate(DAYS)))
    funnel = pd.DataFrame(funnel)
    sheets = {"Resumen": summary(trades, ["entrada en", "stop (fibo)"]),
              "Por mercado": summary(trades, ["entrada en", "stop (fibo)", "mercado"]),
              "Por dirección": summary(trades, ["entrada en", "stop (fibo)", "dirección"]),
              "Por año": summary(trades, ["entrada en", "stop (fibo)", "año"]),
              "Por día semana": summary(trades, ["entrada en", "stop (fibo)", "día semana"]),
              "Resultados": trades.groupby(["entrada en", "stop (fibo)", "resultado"]).size().rename("operaciones").reset_index(),
              "Embudo": funnel.groupby(["entrada en", "mercado", "dirección", "estado"]).size().rename("días").reset_index(),
              "Operaciones": trades}
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 30)
    print("\nResumen por stop (R bruto, sin spread):")
    print(sheets["Resumen"].round(3).to_string(index=False))
    print("\nEmbudo (días de NY Open por resultado del patrón):")
    print(sheets["Embudo"].to_string(index=False))
    try:
        out = Path(args.salida)
        out.parent.mkdir(parents=True, exist_ok=True)
        with pd.ExcelWriter(out) as xw:
            for name, frame in sheets.items():
                frame.to_excel(xw, sheet_name=name, index=False)
        print(f"\nExcel: {out} ({len(trades)} operaciones)")
    except ImportError:
        print("\n(instala openpyxl con `--with openpyxl` para guardar el Excel)")


if __name__ == "__main__":
    main()
