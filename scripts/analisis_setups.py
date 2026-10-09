"""Análisis estadístico histórico de los setups sobre las TBR: genera un Excel para refinar la estrategia.

Solo LEE velas de MT5 (el bot no envía órdenes). Para cada mercado y cada TBR cerrada busca:

- Continuación: el setup real de la skill Setup (tradingbot.skills.setup.setups.detect).
- Reversión C (propuesta, aún sin implementar en la skill): tras la toma de liquidez y el retest del 50 %, el precio
  cierra bajo el mínimo del retest sin haber vuelto a romper el High: orden límite en ese mínimo, stop en el High
  tomado y objetivo en el nivel -1 por el lado contrario.

Uso (desde la raíz del proyecto):
    uv run --with openpyxl python scripts/analisis_setups.py
    uv run --with openpyxl python scripts/analisis_setups.py --simbolos NAS100.r EURUSD --salida analisis/prueba.xlsx

Supuestos: sin spread ni comisiones; si en una vela caben stop y objetivo, cuenta el stop; el sesgo se reconstruye con las
dos reglas y pesos por defecto del bot (ruptura del día previo x2, precio vs apertura x1; sesgo con |puntuación| >= 2).
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tradingbot.config import load_profiles, select_profile                      # noqa: E402
from tradingbot.envconfig import EnvConfig                                       # noqa: E402
from tradingbot.skills.feed.mt5_client import Mt5Source                          # noqa: E402
from tradingbot.skills.levels.daylevels import DEFAULT_US_INDICES, is_us_index   # noqa: E402
from tradingbot.skills.setup.setups import detect                                # noqa: E402
from tradingbot.skills.tbr.zones import compute, zones_from_settings             # noqa: E402

AHEAD = 7 * 3600                      # servidor del broker = NY + 7 h (Vantage)
WINDOW = 96                           # velas M15 (24 h) de validez, como SETUP_WINDOW_HOURS=24
SYMBOLS = ("NAS100.r", "SP500.r", "DJ30.r", "EURUSD", "GBPUSD", "XAUUSD")
DAYS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


# -- sesgo reconstruido -------------------------------------------------------------------------------
def bias_score(ts, o, h, l, c, start_hours: int) -> np.ndarray:
    """Puntuación del Bias del bot en cada vela: ruptura del día previo (x2) + precio vs apertura del día (x1)."""
    day = ((ts - AHEAD) - start_hours * 3600) // 86400
    first = np.r_[True, day[1:] != day[:-1]]
    ids = np.cumsum(first) - 1
    d_open = o[first][ids]
    day_h = np.maximum.reduceat(h, np.flatnonzero(first))
    day_l = np.minimum.reduceat(l, np.flatnonzero(first))
    prev_h, prev_l = np.r_[np.nan, day_h][ids], np.r_[np.nan, day_l][ids]
    score = np.where(c > prev_h, 2, 0) - np.where(c < prev_l, 2, 0)
    return score + np.where(c > d_open, 1, 0) - np.where(c < d_open, 1, 0), d_open


def alignment(score: float, direction: int) -> str:
    bias = 1 if score >= 2 else -1 if score <= -2 else 0
    return "sin sesgo" if bias == 0 else "a favor del sesgo" if bias == direction else "contra el sesgo"


# -- simulación de órdenes --------------------------------------------------------------------------------
def first_hit(mask: np.ndarray) -> int | None:
    idx = np.flatnonzero(mask)
    return int(idx[0]) if idx.size else None


def sim_from_fill(h, l, c, m, entry, stop, tp, d, horizon):
    """Resultado de una operación llenada en la vela m: ('target'|'stop'|'abierta', fin, R, MAE, MFE).

    MAE / MFE: máxima excursión en contra / a favor (en precio). Si caben stop y objetivo en la misma vela, cuenta el stop.
    """
    end = min(len(h), m + horizon)
    hs, ls = h[m:end], l[m:end]
    risk = (entry - stop) * d
    if d > 0:
        s_hit, t_hit = first_hit(ls <= stop), first_hit(hs >= tp)
    else:
        s_hit, t_hit = first_hit(hs >= stop), first_hit(ls <= tp)
    if s_hit is not None and (t_hit is None or s_hit <= t_hit):
        status, last, r = "stop", s_hit, -1.0
    elif t_hit is not None:
        status, last, r = "target", t_hit, abs(tp - entry) / risk
    else:
        status, last = "abierta", len(hs) - 1
        r = (c[end - 1] - entry) * d / risk
    seg_h, seg_l = hs[:last + 1], ls[:last + 1]
    mae = max(0.0, (entry - seg_l.min()) if d > 0 else (seg_h.max() - entry))
    mfe = max(0.0, (seg_h.max() - entry) if d > 0 else (entry - seg_l.min()))
    return status, m + last, r, mae, mfe


def market_entry_r(h, l, c, st, d, rng):
    """R de entrar a mercado en el cierre de la vela de la 2ª ruptura (mismo stop y objetivo en rangos); NaN si no se resuelve."""
    k, entry = st.rebreak_x, c[st.rebreak_x]
    if (entry - st.stop) * d <= 0:
        return np.nan
    status, _, r, _, _ = sim_from_fill(h, l, c, k, entry, st.stop, entry + d * rng, d, 2 * WINDOW)
    return round(r, 2) if status != "abierta" else np.nan


# -- reversión C (propuesta) ------------------------------------------------------------------------------
def reversal_c(s, h, l, c, window):
    """Eventos de la TBR `s` tras el retest del 50 % y, si procede, la reversión C. Devuelve lista de dicts."""
    out, n = [], len(h)
    start = int(s.x1 + 0.5)
    for flip in (1, -1):
        hh, ll, cc, top, bot = (h, l, c, s.high, s.low) if flip == 1 else (-l, -h, -c, -s.low, -s.high)
        mid, rng = (top + bot) / 2, top - bot
        end = min(n, start + window)
        i = next((q for q in range(start, end) if hh[q] > top or ll[q] < bot), None)
        if i is None or ll[i] < bot:
            continue
        j = next((q for q in range(i + 1, end) if ll[q] <= mid), None)
        ev = dict(flip=flip, i=i, j=j, siguiente="sin retest del 50 %", f=None)
        if j is not None and ll[j] <= bot:
            ev["siguiente"] = "invalidada (tomó el lado contrario)"
        elif j is not None:
            ev["siguiente"] = "sin resolver"
            low2 = float(ll[i + 1:j + 1].min())
            for q in range(j + 1, end):
                if ll[q] <= bot and hh[q] <= top:
                    ev["siguiente"] = "invalidada (tomó el lado contrario)"
                    break
                if hh[q] > top:
                    ev["siguiente"] = "continuación (2ª ruptura)"
                    break
                if cc[q] < low2:
                    ev["siguiente"], ev["f"], ev["low2"] = "reversión (cierre bajo el retest)", q, low2
                    break
                low2 = min(low2, float(ll[q]))
        if ev["f"] is not None:
            f, entry, stop, tp = ev["f"], ev["low2"], top, bot - rng
            risk = stop - entry
            # orden límite (venta en el espejo): se llena al retestar el nivel; caduca si antes llega al objetivo
            last = min(n, f + 1 + window)
            m = None
            for q in range(f + 1, last):
                if hh[q] >= entry:
                    m = q
                    break
                if ll[q] <= tp:
                    break
            if risk > 0 and m is not None:
                status, end_x, r, mae, mfe = sim_from_fill(hh, ll, cc, m, entry, stop, tp, -1, 2 * window)
                r_low = sim_from_fill(hh, ll, cc, m, entry, stop, bot, -1, 2 * window)[2]
                ev.update(m=m, status=status, end_x=end_x, r=r, mae=mae, mfe=mfe, r_low=r_low, entry=flip * entry,
                          stop=flip * stop, target=flip * tp, risk=risk, rng=rng)
        out.append(ev)
    return out


# -- estadísticas -------------------------------------------------------------------------------------
def stats(r: pd.Series) -> dict:
    r = r.dropna()
    n = len(r)
    if n == 0:
        return {}
    wins, losses = r[r > 0], r[r < 0]
    equity = r.cumsum()
    streak = best = 0
    for v in r:
        streak = streak + 1 if v < 0 else 0
        best = max(best, streak)
    sd = r.std(ddof=1) if n > 1 else float("nan")
    return {"operaciones": n, "ganadoras": len(wins), "perdedoras": len(losses),
            "win rate %": round(100 * len(wins) / n, 1), "R medio": round(r.mean(), 3), "R total": round(r.sum(), 1),
            "profit factor": round(wins.sum() / -losses.sum(), 2) if len(losses) and losses.sum() else float("nan"),
            "R medio ganadora": round(wins.mean(), 2) if len(wins) else 0, "R medio perdedora": round(losses.mean(), 2) if len(losses) else 0,
            "mejor R": round(r.max(), 2), "peor R": round(r.min(), 2),
            "max drawdown (R)": round((equity - equity.cummax()).min(), 1), "racha perdedora máx.": best,
            "estadístico t": round(r.mean() / (sd / np.sqrt(n)), 2) if sd and sd == sd else float("nan")}


def group_stats(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    rows = []
    for key, g in df.sort_values("fecha_entrada").groupby(by):
        key = key if isinstance(key, tuple) else (key,)
        rows.append({**dict(zip(by, key)), **stats(g["R"])})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--simbolos", nargs="+", default=list(SYMBOLS))
    ap.add_argument("--velas", type=int, default=100_000, help="velas M15 a pedir por mercado (el broker limita)")
    ap.add_argument("--salida", default="analisis/analisis_setups.xlsx")
    args = ap.parse_args()

    profiles, default = load_profiles()
    source = Mt5Source(select_profile(profiles, default, None), 2_000_000)
    print("conectado:", source.connect())
    zones = zones_from_settings(EnvConfig().section("TBR"))
    trades, missed, events, meta = [], [], [], []
    for want in args.simbolos:
        sym = source.resolve_symbol(want)
        if not sym:
            print("  sin símbolo:", want)
            continue
        df = source.load_candles(sym, "15m").tail(args.velas).reset_index(drop=True)
        ts = df["ts"].to_numpy().astype(np.int64)
        o, h, l, c = (df[k].to_numpy().astype(float) for k in ("open", "high", "low", "close"))
        index = is_us_index(sym, DEFAULT_US_INDICES)
        score, d_open = bias_score(ts, o, h, l, c, 18 if index else 17)
        sessions = compute(ts, h, l, zones, AHEAD, 15, days=1_000_000)
        ny = lambda x: pd.Timestamp(int(ts[int(x)]) - AHEAD, unit="s")           # noqa: E731
        meta.append({"mercado": sym, "velas M15": len(df), "desde (NY)": ny(0), "hasta (NY)": ny(len(df) - 1),
                     "TBR cerradas": sum(s.complete for s in sessions), "día de trading desde (NY)": "18:00" if index else "17:00"})
        print(f"  {sym}: {len(df)} velas, {len(sessions)} TBR")

        # ---- continuación: el setup real de la skill ----
        by_session = {(s.zone.key, s.day): s for s in sessions}
        for st in detect(sessions, h, l, WINDOW):
            s = by_session[(st.zone_key, st.day)]
            d = 1 if st.direction == "long" else -1
            rng = st.high - st.low
            base = {"mercado": sym, "tipo": "Continuación", "TBR": st.zone, "día TBR": pd.Timestamp(st.day),
                    "dirección": st.direction, "estado": st.status, "motivo": st.note,
                    "High": st.high, "50 %": st.mid, "Low": st.low, "rango": rng, "rango % precio": 100 * rng / st.high,
                    "hora toma (NY)": ny(st.sweep_x), "hora retest (NY)": ny(st.retest_x) if st.retest_x is not None else None,
                    "hora 2ª ruptura (NY)": ny(st.rebreak_x) if st.rebreak_x is not None else None}
            if st.status not in ("target", "stop", "filled"):
                row = dict(base)
                if st.rebreak_x is not None and st.status in ("armed", "expired"):   # alternativa: entrar a mercado
                    row["R si entrada a mercado"] = market_entry_r(h, l, c, st, d, rng)
                missed.append(row)
                continue
            risk = abs(st.entry - st.stop)
            status, end_x, r, mae, mfe = sim_from_fill(h, l, c, st.fill_x, st.entry, st.stop, st.target, d, 2 * WINDOW)
            row = {**base, "fecha_entrada": ny(st.fill_x), "hora entrada (NY)": ny(st.fill_x).hour,
                   "día semana": DAYS[ny(st.fill_x).weekday()], "hora salida (NY)": ny(end_x),
                   "entrada": st.entry, "stop": st.stop, "objetivo": st.target, "riesgo": risk,
                   "riesgo / rango": risk / rng, "R potencial": abs(st.target - st.entry) / risk,
                   "velas hasta llenar": st.fill_x - st.rebreak_x, "velas en operación": end_x - st.fill_x,
                   "resultado": status, "R": r if status != "abierta" else np.nan,
                   "R abierta (a mercado)": r if status == "abierta" else np.nan,
                   "MAE (R)": mae / risk, "MFE (R)": mfe / risk, "MAE (rangos)": mae / rng, "MFE (rangos)": mfe / rng,
                   "puntuación sesgo": int(score[st.rebreak_x]), "sesgo": alignment(score[st.rebreak_x], d),
                   "entrada vs apertura": "premium" if st.entry > d_open[st.fill_x] else "descuento"}
            row["R si entrada a mercado"] = market_entry_r(h, l, c, st, d, rng)
            for name, stop2 in (("stop en 50 %", st.mid), ("stop en el Low de la TBR", st.low if d > 0 else st.high)):
                if (st.entry - stop2) * d > 0:
                    row[f"R con {name}"] = round(sim_from_fill(h, l, c, st.fill_x, st.entry, stop2, st.entry + d * rng,
                                                              d, 2 * WINDOW)[2], 2)
            for mult in (0.5, 1.5, 2.0):
                row[f"R con objetivo {str(mult).replace('.', ',').removesuffix(',0')} rangos"] = round(sim_from_fill(h, l, c, st.fill_x, st.entry, st.stop,
                                                                          st.entry + d * mult * rng, d, 2 * WINDOW)[2], 2)
            trades.append(row)

        # ---- eventos tras el retest y reversión C ----
        for s in sessions:
            if not s.complete or s.high <= s.low:
                continue
            for ev in reversal_c(s, h, l, c, WINDOW):
                direction = ev["flip"]                                 # lado de la toma de liquidez (1 = High)
                events.append({"mercado": sym, "TBR": s.zone.name, "lado de la toma": "High" if direction == 1 else "Low",
                               "retest del 50 %": ev["j"] is not None, "siguiente": ev["siguiente"]})
                if "r" not in ev:
                    continue
                d = -direction
                trades.append({
                    "mercado": sym, "tipo": "Reversión C", "TBR": s.zone.name, "día TBR": pd.Timestamp(s.day),
                    "dirección": "long" if d > 0 else "short", "estado": ev["status"] if ev["status"] != "abierta" else "filled",
                    "High": s.high, "50 %": (s.high + s.low) / 2, "Low": s.low, "rango": ev["rng"],
                    "rango % precio": 100 * ev["rng"] / s.high, "hora toma (NY)": ny(ev["i"]), "hora retest (NY)": ny(ev["j"]),
                    "hora 2ª ruptura (NY)": ny(ev["f"]), "fecha_entrada": ny(ev["m"]), "hora entrada (NY)": ny(ev["m"]).hour,
                    "día semana": DAYS[ny(ev["m"]).weekday()], "hora salida (NY)": ny(ev["end_x"]),
                    "entrada": ev["entry"], "stop": ev["stop"], "objetivo": ev["target"], "riesgo": ev["risk"],
                    "riesgo / rango": ev["risk"] / ev["rng"], "R potencial": abs(ev["target"] - ev["entry"]) / ev["risk"],
                    "velas hasta llenar": ev["m"] - ev["f"], "velas en operación": ev["end_x"] - ev["m"],
                    "resultado": ev["status"], "R": ev["r"] if ev["status"] != "abierta" else np.nan,
                    "R abierta (a mercado)": ev["r"] if ev["status"] == "abierta" else np.nan,
                    "MAE (R)": ev["mae"] / ev["risk"], "MFE (R)": ev["mfe"] / ev["risk"],
                    "MAE (rangos)": ev["mae"] / ev["rng"], "MFE (rangos)": ev["mfe"] / ev["rng"],
                    "puntuación sesgo": int(score[ev["f"]]), "sesgo": alignment(score[ev["f"]], d),
                    "R con objetivo en el Low/High opuesto": round(ev["r_low"], 2)})
    source.close()

    T = pd.DataFrame(trades).sort_values("fecha_entrada").reset_index(drop=True)
    T.insert(0, "id", np.arange(1, len(T) + 1))
    M = pd.DataFrame(missed)
    E = pd.DataFrame(events)
    done = T[T["resultado"].isin(["target", "stop"])]
    write_excel(args.salida, T, done, M, E, pd.DataFrame(meta))
    print("Excel:", args.salida, f"({len(T)} operaciones, {len(M)} setups no entrados)")


# -- Excel --------------------------------------------------------------------------------------------
def write_excel(path, T, done, M, E, meta) -> None:
    from openpyxl.chart import LineChart, Reference
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    kinds = ["Continuación", "Reversión C"]
    summary = pd.DataFrame([{"tipo": k, **stats(done[done["tipo"] == k].sort_values("fecha_entrada")["R"])} for k in kinds])
    by_tbr = group_stats(done, ["tipo", "TBR"])
    by_sym = group_stats(done, ["tipo", "mercado"])
    by_dir = group_stats(done, ["tipo", "dirección"])
    by_bias = group_stats(done, ["tipo", "sesgo"])
    by_hour = group_stats(done, ["tipo", "hora entrada (NY)"])
    by_dow = group_stats(done, ["tipo", "día semana"])
    by_tbr_dir = group_stats(done, ["tipo", "TBR", "dirección"])
    by_tbr_bias = group_stats(done, ["tipo", "TBR", "sesgo"])
    by_pd = group_stats(done[done["tipo"] == "Continuación"], ["tipo", "entrada vs apertura"])
    done = done.copy()
    done["rango % precio (tramo)"] = pd.qcut(done["rango % precio"], 4, labels=["Q1 estrecho", "Q2", "Q3", "Q4 amplio"])
    by_range = group_stats(done, ["tipo", "rango % precio (tramo)"])
    done["riesgo / rango (tramo)"] = pd.cut(done["riesgo / rango"], [0, 0.5, 0.65, 0.8, 1.01, 99],
                                            labels=["<=0,5", "0,5-0,65", "0,65-0,8", "0,8-1", ">1"])
    by_risk = group_stats(done, ["tipo", "riesgo / rango (tramo)"])

    # embudo y probabilidades por TBR: tras la toma de liquidez y el retest, ¿qué viene primero?
    E = E.copy()
    sweeps = E.groupby(["TBR"]).size().rename("tomas de liquidez")
    touched = E[E["retest del 50 %"]].groupby("TBR").size().rename("con retest del 50 %")
    funnel = pd.concat([sweeps, touched], axis=1)
    for label, key in (("continuación", "continuación (2ª ruptura)"), ("reversión", "reversión (cierre bajo el retest)"),
                       ("invalidada", "invalidada (tomó el lado contrario)"), ("sin resolver", "sin resolver")):
        funnel[label] = E[E["siguiente"] == key].groupby("TBR").size()
    funnel = funnel.fillna(0).astype(int)
    funnel["% retest tras la toma"] = (100 * funnel["con retest del 50 %"] / funnel["tomas de liquidez"]).round(1)
    resolved = funnel["continuación"] + funnel["reversión"]
    funnel["% continuación (de las resueltas)"] = (100 * funnel["continuación"] / resolved).round(1)
    funnel["% reversión (de las resueltas)"] = (100 * funnel["reversión"] / resolved).round(1)
    funnel = funnel.reset_index()
    ev_dir = E[E["retest del 50 %"]].copy()
    ev_dir["resolución"] = ev_dir["siguiente"].str.split(" ").str[0]
    probs = ev_dir.pivot_table(index=["TBR", "lado de la toma"], columns="resolución", values="mercado", aggfunc="count",
                               fill_value=0).reset_index()
    probs.columns.name = None

    miss = pd.DataFrame()
    if len(M):
        miss = (M.groupby(["TBR", "estado", "motivo"]).size().rename("setups").reset_index()
                 .sort_values(["TBR", "setups"], ascending=[True, False]))

    # curva de equity
    curve = done.sort_values("fecha_entrada")[["fecha_entrada", "tipo", "R"]].copy()
    for k in kinds:
        curve[k] = curve["R"].where(curve["tipo"] == k, 0).cumsum()
    curve = curve[["fecha_entrada", *kinds]]

    # sensibilidad: R medio de la continuación según objetivo y stop
    cont = done[done["tipo"] == "Continuación"]
    sens = pd.DataFrame({
        "stop \\ objetivo": ["bajo el mínimo del retest (actual)", "en el 50 %", "en el Low de la TBR"],
        "0,5 rangos": [cont["R con objetivo 0,5 rangos"].mean(), np.nan, np.nan],
        "1 rango (actual)": [cont["R"].mean(), cont["R con stop en 50 %"].mean(), cont["R con stop en el Low de la TBR"].mean()],
        "1,5 rangos": [cont["R con objetivo 1,5 rangos"].mean(), np.nan, np.nan],
        "2 rangos": [cont["R con objetivo 2 rangos"].mean(), np.nan, np.nan]}).round(3)
    # entrar a mercado en la 2ª ruptura: sobre TODAS las que llegan a ese punto (llenadas o no), sin sesgo de selección
    mk = pd.concat([T.loc[T["tipo"] == "Continuación", ["R si entrada a mercado"]],
                    M[["R si entrada a mercado"]] if "R si entrada a mercado" in M else pd.DataFrame()])["R si entrada a mercado"].dropna()
    late = cont[cont["velas hasta llenar"] > 2]["R"]
    sens.loc[len(sens)] = ["entrada a mercado en la 2ª ruptura (todas, n=%d)" % len(mk), np.nan, round(mk.mean(), 3), np.nan, np.nan]
    sens.loc[len(sens)] = ["orden límite activada 3+ velas tras la 2ª ruptura (n=%d)" % len(late), np.nan,
                           round(late.mean(), 3) if len(late) else np.nan, np.nan, np.nan]
    sens_note = ("R medio por operación de la continuación. La fila 'bajo el mínimo del retest' varía el objetivo; las otras "
                 "dos filas varían el stop con el objetivo actual (1 rango). Filtra la hoja 'Operaciones' para cruzar más.")
    notes = [
        ["Qué es", "Análisis histórico de los setups sobre las TBR (continuación real de la skill Setup y reversión C propuesta)."],
        ["Datos", "Velas M15 de MT5 (Vantage demo) de los mercados de la hoja 'Mercados'. Hora de NY (servidor = NY + 7 h)."],
        ["Continuación", "Toma del High/Low de la TBR, retest del 50 %, 2ª ruptura; orden límite en el nivel roto, stop bajo el "
                         "mínimo del retest, objetivo en el nivel -1 (1 rango)."],
        ["Reversión C", "Tras la toma y el retest del 50 %, cierre bajo el mínimo del retest sin 2ª ruptura; orden límite en ese "
                        "mínimo, stop en el High tomado, objetivo en el nivel -1 por el lado contrario. Es una propuesta: aún no está en la skill."],
        ["Supuestos", "Sin spread ni comisiones. Si en una vela caben stop y objetivo, cuenta el stop (pesimista). Ventana de "
                      "24 h para completar el setup y 48 h para resolverlo. Las operaciones abiertas al final de los datos no cuentan en las estadísticas."],
        ["Sesgo reconstruido", "Con las dos reglas del bot (ruptura del día previo x2, precio vs apertura x1) y sesgo si |puntuación| >= 2. "
                               "Es una aproximación del Bias real, que incluirá más reglas."],
        ["Lectura", "R = múltiplo del riesgo inicial. 'estadístico t' > 2 indica que el R medio difiere de cero con cierta fiabilidad; "
                    "con muchas pruebas cruzadas (hoja por hoja) hay que ser prudente: pueden salir ventajas por azar."],
        ["Cuidado: sesgo de selección", "Los setups que caducan 'porque el precio llegó al objetivo sin llenar la orden' son ganadores por "
                                        "construcción: su R a mercado NO es una expectativa. Para comparar la entrada a mercado se usan todas las 2ª rupturas "
                                        "(hoja 'Sensibilidad')."],
        ["Reversión B (descartada)", "Otra reversión probada (barrido que cierra de vuelta dentro, venta/compra límite en el nivel) dio "
                                     "R medio de -0,24 con 15.086 operaciones: no se incluye."]]

    with pd.ExcelWriter(path, engine="openpyxl") as xl:
        sheets = [("Resumen", None), ("Por TBR", by_tbr), ("Por TBR y dirección", by_tbr_dir), ("Por TBR y sesgo", by_tbr_bias),
                  ("Por mercado", by_sym), ("Por dirección", by_dir), ("Por sesgo", by_bias), ("Por hora entrada NY", by_hour),
                  ("Por día de la semana", by_dow), ("Por rango", by_range), ("Por riesgo-rango", by_risk),
                  ("Premium-Discount", by_pd), ("Embudo por TBR", funnel), ("Continuación vs reversión", probs),
                  ("Sensibilidad", sens), ("Setups no entrados", miss), ("Curva R", curve),
                  ("Operaciones", T), ("Setups sin entrar (detalle)", M), ("Mercados", meta), ("Notas", pd.DataFrame(notes, columns=["tema", "detalle"]))]
        for name, frame in sheets:
            if name == "Resumen":
                summary.to_excel(xl, sheet_name=name, index=False)
            elif frame is not None and len(frame):
                frame.to_excel(xl, sheet_name=name, index=False)
        ws_s = xl.sheets["Sensibilidad"]
        ws_s.cell(row=len(sens) + 3, column=1, value=sens_note)
        # formato
        head_fill, head_font = PatternFill("solid", fgColor="1F3A5F"), Font(bold=True, color="FFFFFF")
        for ws in xl.book.worksheets:
            for cell in ws[1]:
                cell.fill, cell.font = head_fill, head_font
                cell.alignment = Alignment(wrap_text=True, vertical="center")
            ws.freeze_panes = "A2" if ws.title in ("Operaciones", "Setups sin entrar (detalle)", "Curva R") else None
            ws.auto_filter.ref = ws.dimensions if ws.max_row > 1 and ws.title != "Sensibilidad" else None
            for i, col in enumerate(ws.iter_cols(min_row=1, max_row=min(ws.max_row, 60)), 1):
                width = max((len(str(c.value)) for c in col if c.value is not None), default=8)
                ws.column_dimensions[get_column_letter(i)].width = min(max(10, width + 2), 48 if ws.title == "Notas" or i > 1 else 60)
            for row in ws.iter_rows(min_row=2):
                for cell in row:
                    if isinstance(cell.value, float):
                        cell.number_format = "0.000" if abs(cell.value) < 10 else "0.00"
                    elif hasattr(cell.value, "year"):
                        cell.number_format = "yyyy-mm-dd hh:mm" if getattr(cell.value, "hour", None) is not None else "yyyy-mm-dd"
        xl.sheets["Notas"].column_dimensions["B"].width = 140
        for ws in xl.book.worksheets:
            for name in ("R", "R medio", "R total", "max drawdown (R)"):
                col = next((c.column for c in ws[1] if c.value == name), None)
                if col and ws.title != "Operaciones":
                    from openpyxl.formatting.rule import CellIsRule
                    letter = get_column_letter(col)
                    rng = f"{letter}2:{letter}{ws.max_row}"
                    ws.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=["0"], font=Font(color="C0392B")))
                    ws.conditional_formatting.add(rng, CellIsRule(operator="greaterThan", formula=["0"], font=Font(color="1E8449")))
        ws = xl.sheets["Curva R"]
        chart = LineChart()
        chart.title, chart.height, chart.width = "R acumulado por tipo de setup (orden cronológico)", 10, 28
        chart.y_axis.title = "R"
        data = Reference(ws, min_col=2, min_row=1, max_col=3, max_row=ws.max_row)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(Reference(ws, min_col=1, min_row=2, max_row=ws.max_row))
        ws.add_chart(chart, "F2")


if __name__ == "__main__":
    main()
