"""Backtest de los patrones Continuación y Reversión (con sus fibonacci) en M15 sobre los índices americanos de MT5.

Solo LEE velas de MT5 (el bot no envía órdenes). Para cada índice, cada día y cada TBR (Asia, London, NY Open) aplica los patrones
del bot (tradingbot.skills.pattern) con las mismas reglas que en vivo, y simula la operación de cada entrada:

- Entrada: orden límite en el 0,5 del fibonacci (se llena en la vela en que el precio lo toca), stop en el nivel 1 (el swing en
  Continuación, la mecha pivote en Reversión) y objetivo en el -0,5 (2R).
- Si en una misma vela caben el stop y el objetivo, cuenta el stop. La vela de la entrada ya cuenta para el stop y el objetivo.
- Costes: el spread real que registra MT5 en la vela de la entrada, una vez por operación (R neto = R bruto - spread / riesgo).
- Si en 24 h no se alcanza ni el stop ni el objetivo, se cierra al cierre de esa vela (sensibilidad en otra hoja).
- Sesgo: el del bot (ruptura x2, TDO x2, Midnight x1, continuación x2; umbral 3; filtro de lateralidad de 6 h), calculado con las velas M15
  al abrirse cada bloque de 3 h, sin mirar al futuro. «A favor del sesgo» es lo que dejaría pasar Cortex.

Uso (desde la raíz del proyecto):
    uv run --with openpyxl python scripts/backtest_patrones.py
    uv run --with openpyxl python scripts/backtest_patrones.py --simbolos NAS100.r SP500.r

Salida: analisis/backtest_patrones.xlsx (carpeta ignorada por git).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tradingbot.config import load_profiles, select_profile                          # noqa: E402
from tradingbot.envconfig import EnvConfig                                           # noqa: E402
from tradingbot.skills.bias.history import block_ids, lateral_flags, score_history    # noqa: E402
from tradingbot.skills.feed.mt5_client import Mt5Source                              # noqa: E402
from tradingbot.skills.pattern import continuacion, reversion                        # noqa: E402
from tradingbot.skills.pattern.patterns import (ActiveTbr, DETECTED, EXPIRED, PatternContext, window_for)   # noqa: E402
from tradingbot.skills.tbr.zones import compute, zones_from_settings                 # noqa: E402

AHEAD = 7 * 3600                              # servidor del broker = NY + 7 h (Vantage)
TF_MIN = 15
SYMBOLS = ("NAS100.r", "SP500.r", "DJ30.r", "US2000.r")
PATTERNS = {"Continuación": continuacion, "Reversión": reversion}
ZONE_ORDER = ["ASIA", "LONDON", "NY_AM", "NY_PM"]
MAIN_FILTERS = ["sin filtro de sesgo", "a favor del sesgo (Cortex)", "una posición a la vez (todas)", "una posición a la vez (GO de Cortex)"]
NEW_UNTIL = {"LONDON": "NY_AM:FIN", "NY_AM": "@18:00"}      # plazos del bot: Asia hasta London (el normal), London hasta el final de
OLD_UNTIL = {"NY_AM": "@16:30"}                              # NY Open y NY Open hasta las 18:00
# BT_PLAZOS: "anterior" (NY Open hasta NY PM, lo demás normal) o, por defecto, los plazos del bot.
UNTIL = dict(OLD_UNTIL) if os.environ.get("BT_PLAZOS") == "anterior" else dict(NEW_UNTIL)
# BT_ALCANCE: "global" (por defecto, una sola posición abierta en toda la cuenta, como CORTEX_POSITION_SCOPE) o "mercado".
GLOBAL_SCOPE = os.environ.get("BT_ALCANCE", "global") != "mercado"
EXTEND = ()
BIAS_RULES = [("prev_day_break", 2.0), ("tdo", 2.0), ("midnight", 1.0), ("htf_break", 2.0)]
BIAS_MIN = 3.0
MAX_HOLD = 96                                 # velas M15 (24 h)
TP_MULTS = (1.0, 1.5, 2.0, 2.5, 3.0)
HOLDS = (48, 96, 192)
DAYS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def simulate(h, l, c, t, direction, entry, stop, target, max_hold):
    """(resultado, velas, R bruto, MAE en R, MFE en R) de una posición llena en la vela t."""
    risk = abs(entry - stop)
    end = min(len(h) - 1, t + max_hold)
    mae = mfe = 0.0
    for i in range(t, end + 1):
        if direction == "long":
            hit_stop, hit_tp = l[i] <= stop, h[i] >= target
            mae, mfe = max(mae, entry - l[i]), max(mfe, h[i] - entry)
        else:
            hit_stop, hit_tp = h[i] >= stop, l[i] <= target
            mae, mfe = max(mae, h[i] - entry), max(mfe, entry - l[i])
        if hit_stop:
            return "stop", i - t, -1.0, min(mae, risk) / risk, mfe / risk
        if hit_tp:
            return "objetivo", i - t, abs(target - entry) / risk, mae / risk, mfe / risk
    last = c[end]
    r = (last - entry) / risk if direction == "long" else (entry - last) / risk
    return "tiempo", end - t, r, mae / risk, mfe / risk


def stats(r: pd.Series, exit_time: pd.Series | None = None) -> dict:
    """Métricas de una serie de R por operación (ordenada por la hora de cierre si se da)."""
    r = r.astype(float)
    if exit_time is not None:
        r = r.loc[exit_time.sort_values().index]
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
            "mejor (R)": r.max(), "peor (R)": r.min(), "máx. drawdown (R)": -dd, "racha perdedora máx.": longest,
            "desv. típica (R)": sd, "estadístico t": r.mean() / (sd / np.sqrt(n)) if sd > 0 else 0.0}


def intraday_start(ts: np.ndarray, window: int = 200) -> int:
    """Primera vela desde la que el histórico es realmente M15: antes, MT5 solo tiene velas diarias o de varias horas (el paso
    mediano entre velas es de 15 minutos o menos)."""
    step = np.diff(ts)
    for i in range(0, max(len(step) - window, 1), 50):
        if np.median(step[i:i + window]) <= 900:
            return i
    return 0


def run_symbol(source, sym: str, order, zones):
    from analisis_setups import spread_prices
    df = source.load_candles(sym, "15m").reset_index(drop=True)
    df = df.iloc[intraday_start(df["ts"].to_numpy()):].reset_index(drop=True)      # antes de ese punto el broker solo tiene velas diarias
    spread = spread_prices(source, sym, df)
    df = df.iloc[:-1]                                    # la última vela sigue formándose
    spread = spread[:len(df)]
    ts = df["ts"].to_numpy().astype(np.int64)
    o, h, l, c = (df[k].to_numpy().astype(float) for k in ("open", "high", "low", "close"))
    n = len(ts)
    # sesgo del bot en cada vela (congelado al abrirse cada bloque de 3 h)
    score = score_history(ts, o, h, l, c, BIAS_RULES, AHEAD, 18 * 60, 3, 3, 30)
    ids = block_ids(ts - AHEAD, 18 * 3600, 3)
    lateral = lateral_flags(ts, c, 6.0, 0.15, ids)
    bias = np.where(lateral, 0, np.where(score >= BIAS_MIN, 1, np.where(score <= -BIAS_MIN, -1, 0)))
    sessions = compute(ts, h, l, zones, AHEAD, TF_MIN, days=int((ts[-1] - ts[0]) // 86400) + 3)
    trades, funnel = [], []
    for s in sessions:
        if not (s.complete and s.high > s.low):
            continue
        tbr = ActiveTbr(s.zone.key, s.zone.name, s.day, s.high, s.low, s.x0, s.x1)
        window = window_for(tbr, order, AHEAD, EXTEND, UNTIL)
        if window is None or window.end_ts is None or window.end_ts > ts[-1] + TF_MIN * 60:
            continue                                      # plazo todavía abierto (o fuera del ciclo): no se evalúa
        first = int(np.searchsorted(ts, window.close_ts, "left"))
        start = int(np.searchsorted(ts, window.start_ts, "left"))
        end = min(n - 1, int(np.searchsorted(ts, window.end_ts, "left")) - 1)
        if first > end or first >= n:
            continue
        ctx = PatternContext(sym, "15m", TF_MIN, ts, o, h, l, c, tbr, first, end, True, window.next_zone, window.next_hours, AHEAD, start, window.limit_verb)
        for name, mod in PATTERNS.items():
            hits, _figs = mod.analyze(ctx, 1)
            hit = hits[0] if hits else None
            status = "ignorada (otro patrón)" if hit is None else hit.status
            detail = "" if hit is None else hit.detail
            activated = hit is not None and not (hit.status == EXPIRED and detail.startswith("no hubo"))
            funnel.append({"mercado": sym, "patrón": name, "zona": tbr.zone, "día": tbr.day, "estado": status,
                           "activada": activated, "motivo": detail})
            if hit is None or hit.status != DETECTED:
                continue
            t, direction = hit.x, hit.direction
            entry, stop, target = hit.price, hit.levels["stop"], hit.levels["target"]
            risk = abs(entry - stop)
            if risk <= 0:
                continue
            res, bars, r_gross, mae, mfe = simulate(h, l, c, t, direction, entry, stop, target, MAX_HOLD)
            cost = float(spread[t]) / risk
            row = {"mercado": sym, "patrón": name, "zona": tbr.zone, "dirección": direction, "entrada (NY)": pd.Timestamp(int(ts[t]) - AHEAD, unit="s"),
                   "día": tbr.day, "entrada": entry, "stop": stop, "objetivo": target, "riesgo (precio)": risk, "riesgo %": 100 * risk / entry,
                   "spread (precio)": float(spread[t]), "resultado": res, "velas": bars, "R bruto": r_gross, "coste (R)": cost,
                   "R neto": r_gross - cost, "MAE (R)": mae, "MFE (R)": mfe, "puntuación sesgo": float(score[t]),
                   "sesgo": {1: "Bullish", -1: "Bearish", 0: "Sin sesgo"}[int(bias[t])], "lateral": bool(lateral[t]),
                   "cierre (NY)": pd.Timestamp(int(ts[min(t + bars, n - 1)]) - AHEAD, unit="s")}
            want = 1 if direction == "long" else -1
            row["sesgo vs operación"] = "a favor" if bias[t] == want else "en contra" if bias[t] == -want else "sin sesgo"
            for m in TP_MULTS:                           # sensibilidad al objetivo (en R)
                tgt = entry + m * risk if direction == "long" else entry - m * risk
                _, _, rg, _, _ = simulate(h, l, c, t, direction, entry, stop, tgt, MAX_HOLD)
                row[f"R neto TP {m:g}R"] = rg - cost
            for hold in HOLDS:                           # sensibilidad al tiempo máximo (objetivo 2R)
                _, _, rg, _, _ = simulate(h, l, c, t, direction, entry, stop, target, hold)
                row[f"R neto {hold // 4} h"] = rg - cost
            trades.append(row)
    info = {"mercado": sym, "velas M15": n, "desde (NY)": pd.Timestamp(int(ts[0]) - AHEAD, unit="s"),
            "hasta (NY)": pd.Timestamp(int(ts[-1]) - AHEAD, unit="s"), "spread medio (precio)": float(np.mean(spread)),
            "TBR evaluadas": len({(f["zona"], f["día"]) for f in funnel})}
    return trades, funnel, info


def table(trades: pd.DataFrame, by: list[str], col: str = "R neto") -> pd.DataFrame:
    rows = []
    for key, g in trades.groupby(by, observed=True):
        key = key if isinstance(key, tuple) else (key,)
        rows.append({**dict(zip(by, key)), **stats(g[col], g["cierre (NY)"])})
    return pd.DataFrame(rows)


def with_all(trades: pd.DataFrame) -> pd.DataFrame:
    both = trades.copy()
    both["patrón"] = "Ambos"
    return pd.concat([trades, both], ignore_index=True)


def overlap_flags(trades: pd.DataFrame, take: pd.Series | None = None) -> pd.Series:
    """True en las operaciones que no se habrían abierto porque ya había otra abierta (en toda la cuenta o en el mismo mercado, según GLOBAL_SCOPE; hasta su stop, objetivo
    o cierre por tiempo). Solo cuentan como abiertas las de `take` (las que el bot sí abre); la entrada debe ser posterior a la
    vela de cierre de la anterior."""
    flags = pd.Series(False, index=trades.index)
    pool = trades if take is None else trades[take]
    groups = [pool.sort_values("entrada (NY)")] if GLOBAL_SCOPE else [g.sort_values("entrada (NY)") for _s, g in pool.groupby("mercado")]
    used = set()                                                         # sesiones (mercado, TBR, día) que ya dieron un trade
    for g in groups:
        free_at = pd.Timestamp.min
        for i, row in g.iterrows():
            session = (row["mercado"], row["zona"], row["día"])
            if row["entrada (NY)"] <= free_at or session in used:
                flags[i] = True
            else:
                free_at = row["cierre (NY)"]
                used.add(session)
    return flags


def build_sheets(trades: pd.DataFrame, funnel: pd.DataFrame, infos: pd.DataFrame) -> dict[str, pd.DataFrame]:
    trades = trades.copy()
    trades["solapada (todas)"] = overlap_flags(trades)
    go = trades["sesgo vs operación"] != "en contra"                      # con CORTEX_ALLOW_NO_BIAS=true, GO = no ir contra el sesgo (las de "sin sesgo" también)
    trades["solapada (GO de Cortex)"] = overlap_flags(trades, go)
    t = with_all(trades)
    t["filtro"] = "sin filtro de sesgo"
    aligned = t[t["sesgo vs operación"] == "a favor"].assign(filtro="a favor del sesgo (Cortex)")
    against = t[t["sesgo vs operación"] == "en contra"].assign(filtro="en contra del sesgo")
    none = t[t["sesgo vs operación"] == "sin sesgo"].assign(filtro="sin sesgo / lateral")
    one_all = t[~t["solapada (todas)"]].assign(filtro="una posición a la vez (todas)")
    one_go = t[(t["sesgo vs operación"] != "en contra") & ~t["solapada (GO de Cortex)"]].assign(
        filtro="una posición a la vez (GO de Cortex)")
    f = pd.concat([t, aligned, against, none, one_all, one_go], ignore_index=True)
    f["año"] = f["entrada (NY)"].dt.year
    f["hora (NY)"] = f["entrada (NY)"].dt.hour
    f["día semana"] = f["entrada (NY)"].dt.dayofweek.map(dict(enumerate(DAYS)))
    sheets: dict[str, pd.DataFrame] = {}
    sheets["Resumen"] = table(f, ["patrón", "filtro"])
    sheets["Por mercado"] = table(f, ["mercado", "patrón", "filtro"])
    sheets["Por zona"] = table(f[f["patrón"] != "Ambos"], ["patrón", "zona", "filtro"])
    sheets["Por dirección"] = table(f[f["patrón"] != "Ambos"], ["patrón", "dirección", "filtro"])
    sheets["Por año"] = table(f[f["filtro"].isin(MAIN_FILTERS)], ["patrón", "filtro", "año"])
    base = f[(f["patrón"] != "Ambos") & (f["filtro"] == "sin filtro de sesgo")]
    sheets["Por hora"] = table(base, ["patrón", "hora (NY)"])
    sheets["Por día semana"] = table(base, ["patrón", "día semana"])
    half = trades["entrada (NY)"].median()
    halves = pd.concat([f[f["entrada (NY)"] <= half].assign(mitad="1ª mitad"), f[f["entrada (NY)"] > half].assign(mitad="2ª mitad")])
    sheets["Mitades (robustez)"] = table(halves[halves["filtro"].isin(MAIN_FILTERS)],
                                         ["patrón", "filtro", "mitad"])
    sens = []
    for (pat, flt), g in f[f["filtro"].isin(MAIN_FILTERS)].groupby(["patrón", "filtro"]):
        for m in TP_MULTS:
            s = stats(g[f"R neto TP {m:g}R"], g["cierre (NY)"])
            sens.append({"patrón": pat, "filtro": flt, "variante": f"objetivo {m:g}R", **s})
        for hold in HOLDS:
            s = stats(g[f"R neto {hold // 4} h"], g["cierre (NY)"])
            sens.append({"patrón": pat, "filtro": flt, "variante": f"objetivo 2R, máx. {hold // 4} h", **s})
        s = stats(g["R bruto"], g["cierre (NY)"])
        sens.append({"patrón": pat, "filtro": flt, "variante": "2R sin costes (R bruto)", **s})
    sheets["Sensibilidad"] = pd.DataFrame(sens)
    out = trades.groupby(["patrón", "resultado"]).size().unstack(fill_value=0)
    out["operaciones"] = out.sum(axis=1)
    out["MAE medio (R)"] = trades.groupby("patrón")["MAE (R)"].mean()
    out["MFE medio (R)"] = trades.groupby("patrón")["MFE (R)"].mean()
    out["velas medias en la operación"] = trades.groupby("patrón")["velas"].mean()
    out["riesgo medio %"] = trades.groupby("patrón")["riesgo %"].mean()
    out["coste medio (R)"] = trades.groupby("patrón")["coste (R)"].mean()
    sheets["Resultados y MAE-MFE"] = out.reset_index()
    fun = funnel.groupby(["mercado", "patrón", "estado"]).size().unstack(fill_value=0)
    fun["TBR evaluadas"] = fun.sum(axis=1)
    act = funnel[funnel["activada"]].groupby(["mercado", "patrón"]).size().rename("activadas")
    fun = fun.join(act).fillna(0)
    fun["% entradas sobre TBR"] = 100 * fun.get("detected", 0) / fun["TBR evaluadas"]
    fun["% entradas sobre activadas"] = 100 * fun.get("detected", 0) / fun["activadas"].replace(0, np.nan)
    sheets["Embudo"] = fun.reset_index().rename(columns={"detected": "entrada", "invalidated": "invalidada", "annulled": "anulada",
                                                          "expired": "vencida"})
    sheets["Datos"] = infos
    sheets["Operaciones"] = trades.sort_values("entrada (NY)")
    equity = []
    for pat, g in with_all(trades).groupby("patrón"):
        for flt, gg in (("sin filtro de sesgo", g), ("a favor del sesgo (Cortex)", g[g["sesgo vs operación"] == "a favor"]),
                        ("una posición a la vez (todas)", g[~g["solapada (todas)"]]),
                        ("una posición a la vez (GO de Cortex)", g[(g["sesgo vs operación"] != "en contra") & ~g["solapada (GO de Cortex)"]])):
            gg = gg.sort_values("cierre (NY)")
            equity.append(pd.DataFrame({"patrón": pat, "filtro": flt, "cierre (NY)": gg["cierre (NY)"].to_numpy(),
                                        "R neto": gg["R neto"].to_numpy(), "R acumulado": gg["R neto"].cumsum().to_numpy()}))
    sheets["Curva de capital (R)"] = pd.concat(equity, ignore_index=True)
    return sheets


NOTES = [
    ("Qué es", "Backtest de los patrones Continuación y Reversión del bot (con sus fibonacci) en M15 sobre los índices americanos."),
    ("Datos", "Velas M15 de MT5 (bid) con todo el histórico intradía que tiene el broker (antes de 2018 solo hay velas diarias, que se descartan; "
              "US2000 empieza en 2020). Ver la hoja Datos."),
    ("Operación", "Entrada límite en el 0,5; stop en el nivel 1; objetivo en el -0,5 (2R). Stop primero si caben los dos en una vela."),
    ("Costes", "Spread real de MT5 en la vela de la entrada, una vez por operación. No incluye comisiones ni deslizamiento."),
    ("Una posición a la vez", "Filtros «una posición a la vez»: una misma sesión (TBR) no da dos trades y no se abre otra operación (en toda la cuenta con BT_ALCANCE=global, el valor por defecto, o por mercado) hasta que la anterior haya cerrado (stop, objetivo o 24 h). «(todas)» recorre todas las entradas en orden; «(GO de Cortex)» solo las que Cortex dejaría pasar (no van contra el sesgo, con CORTEX_ALLOW_NO_BIAS=true), que es lo que hace el bot."),
    ("Plazos", "Cada TBR se busca hasta: Asia 02:00 (inicio de London), London 12:00 (final de NY Open) y NY Open 18:00 (variante anterior con BT_PLAZOS=anterior)."),
    ("Cierre por tiempo", "Si en 24 h no se alcanza stop ni objetivo, se cierra al cierre de esa vela. Hoja Sensibilidad: 12, 24 y 48 h."),
    ("Sesgo", "Reglas del bot (ruptura x2, TDO x2, Midnight x1, continuación x2; umbral 3; lateralidad 6 h / 0,15) con velas M15, congelado "
              "al abrir cada bloque de 3 h. «A favor» = lo que dejaría pasar Cortex; «sin sesgo» incluye el mercado lateral."),
    ("Una señal por patrón y TBR", "Cada patrón da como mucho una entrada por TBR y día. Los dos patrones pueden coincidir en la misma TBR."),
    ("Sin gestión de riesgo", "Cada operación vale 1R y se cuenta por separado: no hay límite de operaciones simultáneas, tamaño ni apalancamiento."),
    ("R", "R = distancia entre la entrada y el stop. R bruto = resultado sin costes; R neto = R bruto - spread / riesgo."),
    ("Estadístico t", "R medio / (desviación típica / raíz de n): por debajo de 2 la ventaja no es estadísticamente distinguible de cero."),
    ("Drawdown", "Máxima caída de la curva de R acumulado, con las operaciones ordenadas por su hora de cierre."),
    ("Mitades", "Se parte el histórico por la mediana de las fechas: si una mitad gana y la otra pierde, el resultado es poco fiable."),
    ("Límites", "Datos de un solo broker y ~4 años; con muchas variantes probadas parte de lo que gana puede ser azar."),
]


def write_excel(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    from openpyxl.chart import LineChart, Reference
    from openpyxl.chart.series import SeriesLabel
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    notes = pd.DataFrame(NOTES, columns=["tema", "explicación"])
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        notes.to_excel(xw, sheet_name="Metodología", index=False)
        for name, df in sheets.items():
            df.to_excel(xw, sheet_name=name[:31], index=False)
        head = PatternFill("solid", fgColor="1F3864")
        for ws in xw.book.worksheets:
            ws.freeze_panes = "A2"
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = head
                cell.alignment = Alignment(wrap_text=True, vertical="center")
            for i, col in enumerate(ws.columns, start=1):
                width = max(len(str(c.value)) if c.value is not None else 0 for c in list(col)[:200])
                ws.column_dimensions[get_column_letter(i)].width = min(max(10, width + 2), 60 if ws.title == "Metodología" else 28)
                for cell in list(col)[1:]:
                    if isinstance(cell.value, float):
                        cell.number_format = "0.000"
            if ws.title == "Metodología":
                ws.column_dimensions["B"].width = 120
        ws = xw.book["Curva de capital (R)"]
        eq = sheets["Curva de capital (R)"]
        chart = LineChart()
        chart.title = "R acumulado por patrón, sin filtro de sesgo (a favor del sesgo en las otras series)"
        chart.height, chart.width = 10, 26
        row = 2
        for (pat, flt), g in eq.groupby(["patrón", "filtro"], sort=False):
            if pat != "Ambos":
                chart.add_data(Reference(ws, min_col=5, min_row=row, max_row=row + len(g) - 1), titles_from_data=False)
                chart.series[-1].tx = SeriesLabel(v=f"{pat} - {flt}")
            row += len(g)
        ws.add_chart(chart, "H2")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--simbolos", nargs="+", default=list(SYMBOLS))
    ap.add_argument("--salida", default="analisis/backtest_patrones.xlsx")
    args = ap.parse_args()
    profiles, default = load_profiles()
    source = Mt5Source(select_profile(profiles, default, None), 2_000_000)
    print("conectado:", source.connect())
    env = EnvConfig().section("TBR")
    order = zones_from_settings(env, ZONE_ORDER)
    zones = zones_from_settings(env)
    all_trades, all_funnel, infos = [], [], []
    for want in args.simbolos:
        sym = source.resolve_symbol(want)
        if not sym:
            print("  sin símbolo:", want)
            continue
        trades, funnel, info = run_symbol(source, sym, order, zones)
        print(f"  {sym}: {info['velas M15']} velas M15 ({info['desde (NY)']:%Y-%m-%d} a {info['hasta (NY)']:%Y-%m-%d}), "
              f"{info['TBR evaluadas']} TBR, {len(trades)} entradas")
        all_trades += trades
        all_funnel += funnel
        infos.append(info)
    source.close()
    trades, funnel, infos = pd.DataFrame(all_trades), pd.DataFrame(all_funnel), pd.DataFrame(infos)
    sheets = build_sheets(trades, funnel, infos)
    out = Path(args.salida)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_excel(out, sheets)
    print(f"Excel: {out} ({len(trades)} operaciones)")
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 30)
    print(sheets["Resumen"].round(3).to_string())


if __name__ == "__main__":
    main()
