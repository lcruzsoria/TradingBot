"""Análisis estadístico histórico de los setups sobre las TBR: genera un Excel para refinar la estrategia.

Solo LEE velas de MT5 (el bot no envía órdenes). Para cada mercado y cada TBR cerrada busca:

- Continuación: el setup real de la skill Setup (tradingbot.skills.setup.setups.detect).
- Reversión C (propuesta, aún sin implementar en la skill): tras la toma de liquidez y el retest del 50 %, el precio
  cierra bajo el mínimo del retest sin haber vuelto a romper el High: orden límite en ese mínimo, stop en el High
  tomado y objetivo en el nivel -1 por el lado contrario.

Cada iteración de la estrategia es una VERSIÓN (v1, v2...; ver VARIANTES): se calculan todas con los mismos datos y se
escribe un Excel por versión (analisis/analisis_setups_vN.xlsx) con su hoja 'Cambios' y una 'Comparativa' con las
anteriores. El detalle de cada cambio está en docs/analisis_setups/CAMBIOS.md.

Uso (desde la raíz del proyecto):
    uv run --with openpyxl python scripts/analisis_setups.py
    uv run --with openpyxl python scripts/analisis_setups.py --versiones v1 v2 --simbolos NAS100.r EURUSD

Supuestos: sin spread ni comisiones; si en una vela caben stop y objetivo, cuenta el stop; el sesgo se reconstruye con las
dos reglas y pesos por defecto del bot (ruptura del día previo x2, precio vs apertura x1; sesgo con |puntuación| >= 2).
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
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
STOPS = ("retest", "mitad", "extremo")        # stop: mínimo del retest / 50 % de la TBR / extremo opuesto de la TBR
TPS = (0.5, 1.0, 1.5, 2.0)                    # objetivos, en rangos de la TBR más allá del nivel roto (1 = nivel -1)


def tp_label(mult: float) -> str:
    return str(mult).replace(".", ",").removesuffix(",0")


@dataclass(frozen=True)
class Variante:
    clave: str            # "v1"
    nombre: str
    cambio: str           # qué se cambia respecto a la versión anterior
    hipotesis: str        # por qué se prueba
    entrada: str = "limite"      # "limite": orden límite en el nivel roto; "mercado": apertura de la vela siguiente a la 2ª ruptura
    stop: str = "retest"         # ver STOPS
    objetivo: float = 1.0        # rangos más allá del nivel roto
    min_rango: float = 0.0       # filtro: rango de la TBR >= esta fracción de la mediana de sus últimas 20 sesiones (0 = sin filtro)


VARIANTES = (
    Variante("v1", "Base: orden límite y stop bajo el mínimo del retest",
             "Ninguno: es la estrategia tal como está implementada en la skill Setup (commit 4d0d94e).",
             "Línea base para comparar.", "limite", "retest", 1.0),
    Variante("v2", "Entrada a mercado en la 2ª ruptura",
             "La entrada pasa de orden límite en el nivel roto a mercado, en la apertura de la vela siguiente a la 2ª ruptura. "
             "Stop y objetivo no cambian.",
             "La orden límite sufre selección adversa: se llena sobre todo en los trades que fallan (retestan enseguida) y "
             "no se llena en los que despegan.", "mercado", "retest", 1.0),
    Variante("v3", "Entrada a mercado y stop en el extremo opuesto de la TBR",
             "Sobre v2, el stop pasa de bajo el mínimo del retest al Low de la TBR (al High en cortos).",
             "El stop del retest es estrecho (0,5-0,65 del rango) y lo barre el ruido; con el stop más lejos debería "
             "sobrevivir más operaciones.", "mercado", "extremo", 1.0),
    Variante("v4", "Entrada a mercado, stop en el extremo y filtro de rango mínimo",
             "Sobre v3, solo se opera si el rango de la TBR es al menos el 80 % de la mediana de sus últimas 20 sesiones "
             "(la misma TBR del mismo mercado). Se calcula con datos anteriores: no mira al futuro.",
             "En v1-v3 el cuartil de rangos más estrechos es el peor; con rangos pequeños el spread y el ruido pesan más "
             "que el movimiento.", "mercado", "extremo", 1.0, 0.8),
    Variante("v5", "Entrada a mercado, stop en el 50 %, objetivo a 1,5 rangos y filtro de rango",
             "Sobre v4, el stop pasa del extremo opuesto de la TBR al 50 % de la TBR y el objetivo del nivel -1 (1 rango) a 1,5 rangos "
             "más allá del nivel roto. Elegidos con la 1ª mitad del histórico (hoja 'Sensibilidad 1ª vs 2ª mitad' de v4: mejor "
             "celda, +0,062R) y comprobados en la 2ª mitad (+0,092R).",
             "Si el precio vuelve al 50 % tras la 2ª ruptura, la continuación ha fallado: es el stop natural. Con él, el objetivo "
             "más lejano compensa los stops más frecuentes.", "mercado", "mitad", 1.5, 0.8),
)


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


def continuation_row(var, base, st, d, rng, o, h, l, c, ny, score, d_open, rel_range=float('nan')):
    """Operación de la continuación según la versión `var`, o None si no hay operación (no se llena, sin recorrido...)."""
    k = st.rebreak_x
    if var.min_rango and not rel_range >= var.min_rango:      # NaN (sin historial suficiente) también se descarta
        return None
    if var.entrada == "limite":
        if st.status not in ("target", "stop", "filled"):
            return None
        m, entry = st.fill_x, st.entry
    else:
        m = k + 1 if k is not None else None
        if m is None or m >= len(h):
            return None
        entry = o[m]
    level = st.high if d > 0 else st.low                       # nivel roto: la entrada límite y la base del objetivo
    stops = {"retest": st.stop, "mitad": st.mid, "extremo": st.low if d > 0 else st.high}
    stop = stops[var.stop]
    risk = (entry - stop) * d
    target = level + d * var.objetivo * rng
    if risk <= 0 or (target - entry) * d <= 0:
        return None
    status, end_x, r, mae, mfe = sim_from_fill(h, l, c, m, entry, stop, target, d, 2 * WINDOW)
    row = {**base, "fecha_entrada": ny(m), "hora entrada (NY)": ny(m).hour, "día semana": DAYS[ny(m).weekday()],
           "hora salida (NY)": ny(end_x), "entrada": entry, "stop": stop, "objetivo": target, "riesgo": risk,
           "riesgo / rango": risk / rng, "R potencial": abs(target - entry) / risk,
           "velas hasta llenar": m - k, "velas en operación": end_x - m,
           "resultado": status, "R": r if status != "abierta" else np.nan,
           "R abierta (a mercado)": r if status == "abierta" else np.nan,
           "MAE (R)": mae / risk, "MFE (R)": mfe / risk, "MAE (rangos)": mae / rng, "MFE (rangos)": mfe / rng,
           "puntuación sesgo": int(score[k]), "sesgo": alignment(score[k], d),
           "entrada vs apertura": "premium" if entry > d_open[m] else "descuento",
           "rango vs mediana 20 sesiones": rel_range}
    for stop_key in STOPS:                                      # rejilla de sensibilidad: R para cada stop y objetivo
        for mult in TPS:
            stop2, tgt2 = stops[stop_key], level + d * mult * rng
            ok = (entry - stop2) * d > 0 and (tgt2 - entry) * d > 0
            res = sim_from_fill(h, l, c, m, entry, stop2, tgt2, d, 2 * WINDOW) if ok else None
            row[f"R[{stop_key}|{tp_label(mult)}]"] = round(res[2], 2) if res and res[0] != "abierta" else np.nan
    return row


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
    ap.add_argument("--versiones", nargs="+", default=[v.clave for v in VARIANTES], help="versiones a calcular")
    ap.add_argument("--salida", default="analisis", help="carpeta de los Excel (analisis_setups_vN.xlsx)")
    args = ap.parse_args()
    versiones = [v for v in VARIANTES if v.clave in args.versiones]

    profiles, default = load_profiles()
    source = Mt5Source(select_profile(profiles, default, None), 2_000_000)
    print("conectado:", source.connect())
    zones = zones_from_settings(EnvConfig().section("TBR"))
    trades = {v.clave: [] for v in versiones}
    missed = {v.clave: [] for v in versiones}
    c_trades, events, meta = [], [], []
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

        # ---- continuación: el setup real de la skill, con cada versión de la estrategia ----
        past, rel = defaultdict(list), {}                    # rango de cada TBR frente a la mediana de sus 20 sesiones previas
        for s in sorted((s for s in sessions if s.complete and s.high > s.low), key=lambda s: s.x1):
            hist = past[s.zone.key][-20:]
            rel[(s.zone.key, s.day)] = (s.high - s.low) / float(np.median(hist)) if len(hist) >= 5 else float("nan")
            past[s.zone.key].append(s.high - s.low)
        for st in detect(sessions, h, l, WINDOW):
            d = 1 if st.direction == "long" else -1
            rng = st.high - st.low
            base = {"mercado": sym, "tipo": "Continuación", "TBR": st.zone, "día TBR": pd.Timestamp(st.day),
                    "dirección": st.direction, "estado setup": st.status, "motivo": st.note,
                    "High": st.high, "50 %": st.mid, "Low": st.low, "rango": rng, "rango % precio": 100 * rng / st.high,
                    "hora toma (NY)": ny(st.sweep_x), "hora retest (NY)": ny(st.retest_x) if st.retest_x is not None else None,
                    "hora 2ª ruptura (NY)": ny(st.rebreak_x) if st.rebreak_x is not None else None}
            for var in versiones:
                row = continuation_row(var, base, st, d, rng, o, h, l, c, ny, score, d_open, rel.get((st.zone_key, st.day), float('nan')))
                (trades if row is not None else missed)[var.clave].append(row if row is not None else dict(base))

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
                c_trades.append({
                    "mercado": sym, "tipo": "Reversión C", "TBR": s.zone.name, "día TBR": pd.Timestamp(s.day),
                    "dirección": "long" if d > 0 else "short", "estado setup": ev["status"] if ev["status"] != "abierta" else "filled",
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

    meta_df, E = pd.DataFrame(meta), pd.DataFrame(events)
    C = pd.DataFrame(c_trades)
    results = {}
    for var in versiones:
        T = pd.concat([pd.DataFrame(trades[var.clave]), C], ignore_index=True).sort_values("fecha_entrada").reset_index(drop=True)
        T.insert(0, "id", np.arange(1, len(T) + 1))
        results[var.clave] = (T, T[T["resultado"].isin(["target", "stop"])], pd.DataFrame(missed[var.clave]))

    # comparativa entre versiones (la reversión C no cambia entre versiones)
    comp_rows, comp_tbr, comp_bias = [], [], []
    for var in versiones:
        _, done, _ = results[var.clave]
        cont = done[done["tipo"] == "Continuación"].sort_values("fecha_entrada")
        comp_rows.append({"versión": var.clave, "estrategia": var.nombre, **stats(cont["R"])})
        for key, g in cont.groupby("TBR"):
            comp_tbr.append({"versión": var.clave, "TBR": key, **{k: v for k, v in stats(g["R"]).items()
                                                                  if k in ("operaciones", "win rate %", "R medio", "R total")}})
        for key, g in cont.groupby("sesgo"):
            comp_bias.append({"versión": var.clave, "sesgo": key, **{k: v for k, v in stats(g["R"]).items()
                                                                     if k in ("operaciones", "win rate %", "R medio", "R total")}})
    comp = pd.DataFrame(comp_rows)
    comp.insert(3, "dif. R medio vs anterior", comp["R medio"].diff().round(3))
    comp_tbr = pd.DataFrame(comp_tbr).pivot_table(index="TBR", columns="versión", values="R medio").round(3).reset_index()
    comp_bias = pd.DataFrame(comp_bias).pivot_table(index="sesgo", columns="versión", values="R medio").round(3).reset_index()
    cambios = pd.DataFrame([{"versión": v.clave, "estrategia": v.nombre, "qué cambia": v.cambio, "por qué": v.hipotesis,
                             "entrada": "orden límite en el nivel roto" if v.entrada == "limite" else "a mercado, apertura tras la 2ª ruptura",
                             "stop": {"retest": "bajo el mínimo del retest", "mitad": "en el 50 % de la TBR",
                                      "extremo": "en el extremo opuesto de la TBR"}[v.stop],
                             "objetivo": f"{tp_label(v.objetivo)} rango(s) más allá del nivel roto",
                             "filtro": f"rango >= {v.min_rango:g} x mediana de 20 sesiones" if v.min_rango else "ninguno"}
                            for v in versiones])
    out = Path(args.salida)
    for var in versiones:
        T, done, M = results[var.clave]
        path = out / f"analisis_setups_{var.clave}.xlsx"
        write_excel(path, T, done, M, E, meta_df, var, comp, comp_tbr, comp_bias, cambios)
        print("Excel:", path, f"({len(T)} operaciones, {len(M)} setups sin entrar)")
    print()
    print(comp.drop(columns=["ganadoras", "perdedoras", "R medio ganadora", "R medio perdedora", "mejor R", "peor R"]).to_string(index=False))


# -- Excel --------------------------------------------------------------------------------------------
def write_excel(path, T, done, M, E, meta, var, comp, comp_tbr, comp_bias, cambios) -> None:
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
        miss = (M.groupby(["TBR", "estado setup", "motivo"]).size().rename("setups").reset_index()
                 .sort_values(["TBR", "setups"], ascending=[True, False]))

    # curva de equity
    curve = done.sort_values("fecha_entrada")[["fecha_entrada", "tipo", "R"]].copy()
    for k in kinds:
        curve[k] = curve["R"].where(curve["tipo"] == k, 0).cumsum()
    curve = curve[["fecha_entrada", *kinds]]

    # sensibilidad: R medio de la continuación para cada stop y objetivo (con la entrada de esta versión)
    cont = done[done["tipo"] == "Continuación"]
    stop_names = {"retest": "bajo el mínimo del retest", "mitad": "en el 50 % de la TBR", "extremo": "en el extremo opuesto de la TBR"}
    sens = pd.DataFrame([{"stop \\ objetivo (rangos)": stop_names[k] + (" (actual)" if k == var.stop else ""),
                          **{tp_label(m) + (" (actual)" if m == var.objetivo else ""): cont[f"R[{k}|{tp_label(m)}]"].mean()
                             for m in TPS}} for k in STOPS]).round(3)
    sens_note = ("R medio por operación de la continuación en esta versión, para cada stop (filas) y objetivo (columnas, en rangos "
                 "de la TBR más allá del nivel roto; 1 = nivel -1). Cada celda es una estrategia distinta: filtra 'Operaciones' "
                 "(columnas R[stop|objetivo]) para cruzar con TBR, sesgo, hora...")
    # misma rejilla en la 1ª y la 2ª mitad del histórico: lo que solo funciona en una mitad es azar o sobreajuste
    cut = cont["fecha_entrada"].median()
    halves = []
    for label, part in ((f"1ª mitad (hasta {cut:%Y-%m-%d})", cont[cont["fecha_entrada"] <= cut]),
                        (f"2ª mitad (desde {cut:%Y-%m-%d})", cont[cont["fecha_entrada"] > cut])):
        for k in STOPS:
            halves.append({"periodo": label, "stop": stop_names[k], "operaciones": len(part),
                           **{tp_label(m): part[f"R[{k}|{tp_label(m)}]"].mean() for m in TPS}})
    halves = pd.DataFrame(halves).round(3)
    late = cont[cont["velas hasta llenar"] > 2]["R"] if var.entrada == "limite" else pd.Series(dtype=float)
    if len(late):
        sens_note += f" Con orden límite, las llenadas 3+ velas después de la 2ª ruptura: R medio {late.mean():.3f} (n={len(late)})."
    notes = [
        ["Qué es", "Análisis histórico de los setups sobre las TBR (continuación real de la skill Setup y reversión C propuesta)."],
        ["Datos", "Velas M15 de MT5 (Vantage demo) de los mercados de la hoja 'Mercados'. Hora de NY (servidor = NY + 7 h)."],
        ["Versión", f"{var.clave}: {var.nombre}. {var.cambio}"],
        ["Continuación", "Toma del High/Low de la TBR, retest del 50 %, 2ª ruptura. Entrada y stop según la versión (hoja 'Cambios'); "
                         "objetivo en el nivel -1 (1 rango más allá del nivel roto)."],
        ["Reversión C", "Tras la toma y el retest del 50 %, cierre bajo el mínimo del retest sin 2ª ruptura; orden límite en ese "
                        "mínimo, stop en el High tomado, objetivo en el nivel -1 por el lado contrario. Es una propuesta: aún no está en la skill."],
        ["Supuestos", "Sin spread ni comisiones. Si en una vela caben stop y objetivo, cuenta el stop (pesimista). Ventana de "
                      "24 h para completar el setup y 48 h para resolverlo. Las operaciones abiertas al final de los datos no cuentan en las estadísticas."],
        ["Sesgo reconstruido", "Con las dos reglas del bot (ruptura del día previo x2, precio vs apertura x1) y sesgo si |puntuación| >= 2. "
                               "Es una aproximación del Bias real, que incluirá más reglas."],
        ["Lectura", "R = múltiplo del riesgo inicial. 'estadístico t' > 2 indica que el R medio difiere de cero con cierta fiabilidad; "
                    "con muchas pruebas cruzadas (hoja por hoja) hay que ser prudente: pueden salir ventajas por azar."],
        ["Cuidado: sesgo de selección", "Los setups que caducan 'porque el precio llegó al objetivo sin llenar la orden' son ganadores por "
                                        "construcción: su R a mercado NO es una expectativa. Para comparar entradas se usan TODAS las 2ª rupturas "
                                        "(versiones v2 y v3: entrada a mercado en la apertura de la vela siguiente)."],
        ["Reversión B (descartada)", "Otra reversión probada (barrido que cierra de vuelta dentro, venta/compra límite en el nivel) dio "
                                     "R medio de -0,24 con 15.086 operaciones: no se incluye."]]

    with pd.ExcelWriter(path, engine="openpyxl") as xl:
        sheets = [("Cambios", cambios), ("Comparativa", comp), ("Comparativa por TBR", comp_tbr),
                  ("Comparativa por sesgo", comp_bias), ("Resumen", None), ("Por TBR", by_tbr), ("Por TBR y dirección", by_tbr_dir), ("Por TBR y sesgo", by_tbr_bias),
                  ("Por mercado", by_sym), ("Por dirección", by_dir), ("Por sesgo", by_bias), ("Por hora entrada NY", by_hour),
                  ("Por día de la semana", by_dow), ("Por rango", by_range), ("Por riesgo-rango", by_risk),
                  ("Premium-Discount", by_pd), ("Embudo por TBR", funnel), ("Continuación vs reversión", probs),
                  ("Sensibilidad", sens), ("Sensibilidad 1ª vs 2ª mitad", halves), ("Setups no entrados", miss), ("Curva R", curve),
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
