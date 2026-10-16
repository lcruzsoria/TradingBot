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
from tradingbot.skills.bias.htf import sweep_vote                                # noqa: E402
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
    sesgo_reglas: str = "nuevo"     # reglas del sesgo del filtro: "nuevo" (ruptura, TDO, Midnight), "con_sweep" (+ barrido) o "solo_sweep"
    sesgo: str = "todos"          # filtro de Bias Execution: "todos", "a favor" o "no contra" (a favor o sin sesgo)
    spread: bool = False         # aplica el spread real de cada vela de entrada
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
             "que el movimiento.", "mercado", "extremo", 1.0, min_rango=0.8),
    Variante("v5", "Entrada a mercado, stop en el 50 %, objetivo a 1,5 rangos y filtro de rango",
             "Sobre v4, el stop pasa del extremo opuesto de la TBR al 50 % de la TBR y el objetivo del nivel -1 (1 rango) a 1,5 rangos "
             "más allá del nivel roto. Elegidos con la 1ª mitad del histórico (hoja 'Sensibilidad 1ª vs 2ª mitad' de v4: mejor "
             "celda, +0,062R) y comprobados en la 2ª mitad (+0,092R).",
             "Si el precio vuelve al 50 % tras la 2ª ruptura, la continuación ha fallado: es el stop natural. Con él, el objetivo "
             "más lejano compensa los stops más frecuentes.", "mercado", "mitad", 1.5, min_rango=0.8),
    Variante("v6", "v5 con el spread real de cada entrada",
             "Sobre v5, se aplica el spread real que MT5 registra en cada vela (Vantage demo). El largo compra al ask y sale al "
             "bid; el corto vende al bid y sale al ask. El riesgo (1R) incluye el spread. Misma entrada, stop, objetivo y filtro.",
             "Hasta v5 no había costes: con una ventaja de +0,06R hay que saber si el spread se la come.",
             "mercado", "mitad", 1.5, spread=True, min_rango=0.8),
    Variante("v7", "v6 con Bias Execution: solo operaciones a favor del sesgo",
             "Sobre v6, solo se opera si la dirección va a favor del sesgo del día reconstruido con las reglas actuales del bot "
             "(ruptura del día previo x2, TDO x1, Midnight x1; sesgo con |puntuación| >= 2). Es lo que haría Bias Execution con "
             "BIAS_EXEC_ALLOW_NO_BIAS=false.",
             "Medir si el Bias, con las reglas TDO y Midnight, mejora la estrategia como filtro.",
             "mercado", "mitad", 1.5, sesgo="a favor", spread=True, min_rango=0.8),
    Variante("v8", "v6 sin operar contra el sesgo",
             "Sobre v6, solo se descartan las operaciones contra el sesgo: se opera a favor o sin sesgo (equivale a "
             "BIAS_EXEC_ALLOW_NO_BIAS=true).",
             "Si pedir sesgo a favor deja muy pocas operaciones, ver si basta con evitar las contrarias.",
             "mercado", "mitad", 1.5, sesgo="no contra", spread=True, min_rango=0.8),
    Variante("v9", "v6 con Bias Execution usando solo el barrido de la vela anterior",
             "Sobre v6, solo se opera a favor del sesgo que da la regla de barrido de la vela anterior: H3 en índices y H4 en el "
             "resto; el sesgo de la vela actual sale de las dos velas anteriores cerradas (n-1 y n-2). Sin barrido válido no hay "
             "sesgo y no se opera.",
             "Probar el primer criterio nuevo de Bias, aislado: si el barrido con cierre dentro anticipa la dirección.",
             "mercado", "mitad", 1.5, sesgo_reglas="solo_sweep", sesgo="a favor", spread=True, min_rango=0.8),
    Variante("v10", "v6 con Bias Execution: reglas actuales más el barrido (peso 2)",
             "Sobre v7, el sesgo suma la regla de barrido de la vela anterior con peso 2 a las reglas actuales (ruptura x2, TDO, "
             "Midnight); solo a favor del sesgo.",
             "Ver si el barrido añade información a las reglas de dirección del día.",
             "mercado", "mitad", 1.5, sesgo_reglas="con_sweep", sesgo="a favor", spread=True, min_rango=0.8),
)


# -- sesgo reconstruido -------------------------------------------------------------------------------
def htf_sweep_array(ts, h, l, c, start_hours: int, hours: int) -> np.ndarray:
    """Voto del barrido de la vela anterior para cada vela M15: el de la vela H3 / H4 en la que está, calculado solo con las
    dos velas anteriores ya cerradas (n-1 y n-2): sin mirar la vela en curso."""
    bucket = ((ts - AHEAD) - start_hours * 3600) // (hours * 3600)
    first = np.r_[True, bucket[1:] != bucket[:-1]]
    starts = np.flatnonzero(first)
    ids = np.cumsum(first) - 1
    ends = np.r_[starts[1:] - 1, len(ts) - 1]
    hi, lo, cl = np.maximum.reduceat(h, starts), np.minimum.reduceat(l, starts), c[ends]
    votes = np.zeros(len(starts), dtype=int)
    for b in range(2, len(starts)):
        votes[b] = sweep_vote(hi[b - 2], lo[b - 2], hi[b - 1], lo[b - 1], cl[b - 1])[0]
    return votes[ids]


def sweep_events(sym, ts, o, h, l, c, start_hours: int, hours: int) -> list[dict]:
    """Cada vela H3 / H4 con el sesgo que le da el barrido de las dos anteriores y lo que hizo después (sin mirar al futuro al
    decidir el sesgo): sirve para medir si el sesgo anticipa la dirección de la vela 0."""
    bucket = ((ts - AHEAD) - start_hours * 3600) // (hours * 3600)
    first = np.r_[True, bucket[1:] != bucket[:-1]]
    starts = np.flatnonzero(first)
    ends = np.r_[starts[1:] - 1, len(ts) - 1]
    op, hi, lo, cl = o[starts], np.maximum.reduceat(h, starts), np.minimum.reduceat(l, starts), c[ends]
    t0 = bucket[starts] * hours * 3600 + start_hours * 3600
    out = []
    for b in range(2, len(starts)):
        vote = sweep_vote(hi[b - 2], lo[b - 2], hi[b - 1], lo[b - 1], cl[b - 1])[0]
        rng_prev = hi[b - 1] - lo[b - 1]
        if rng_prev <= 0:
            continue
        move = cl[b] - op[b]
        out.append({"mercado": sym, "velas": f"H{hours}", "voto": vote, "inicio (NY)": pd.Timestamp(int(t0[b]), unit="s"),
                    "movimiento de la vela (rangos de la n-1)": move / rng_prev,
                    "movimiento (% del precio)": 100 * move / op[b],
                    "cierra al alza": bool(move > 0),
                    "máximo desde la apertura (rangos)": (hi[b] - op[b]) / rng_prev,
                    "mínimo desde la apertura (rangos)": (lo[b] - op[b]) / rng_prev})
    return out


def sweep_prediction(ev: pd.DataFrame) -> pd.DataFrame:
    """Tabla: por mercado y sesgo del barrido, cuánto acierta la dirección de la vela 0 y cuánto se mueve a favor."""
    rows = []
    groups = [("TODOS", ev)] + [(k, g) for k, g in ev.groupby("mercado")]
    for name, g in groups:
        base_up = 100 * g["cierra al alza"].mean()
        for label, vote in (("bajista (barrió el High)", -1), ("alcista (barrió el Low)", 1), ("sin sesgo", 0)):
            sub = g[g["voto"] == vote]
            if not len(sub):
                continue
            sign = vote if vote else 1
            move = sign * sub["movimiento de la vela (rangos de la n-1)"]
            hit = 100 * (sub["cierra al alza"] == (vote >= 0)).mean() if vote else float("nan")
            sd = move.std(ddof=1)
            rows.append({"mercado": name, "sesgo del barrido": label, "velas": len(sub), "% de velas": round(100 * len(sub) / len(g), 1),
                         "acierta la dirección %": round(hit, 1) if vote else np.nan,
                         "% de velas alcistas en general": round(base_up, 1),
                         "movimiento medio a favor (rangos de la n-1)": round(move.mean(), 3) if vote else np.nan,
                         "estadístico t": round(move.mean() / (sd / np.sqrt(len(sub))), 2) if vote and sd and len(sub) > 1 else np.nan})
    return pd.DataFrame(rows)


def bias_arrays(ts, o, h, l, c, start_hours: int, sweep_hours: int = 4) -> dict:
    """Votos y puntuación del Bias del bot en cada vela, con los datos disponibles en ella (sin mirar al futuro).

    prev: ruptura del día de trading anterior (+1 sobre su máximo, -1 bajo su mínimo). tdo: precio vs la apertura del día de
    trading (True Day Open). mid: precio vs la apertura de las 00:00 NY (0 hasta que existe esa vela).
    nuevo = 2 prev + tdo + mid (reglas actuales del bot); viejo = 2 prev + tdo (reglas anteriores: prev + apertura del día).
    """
    t = ts - AHEAD
    day = (t - start_hours * 3600) // 86400
    first = np.r_[True, day[1:] != day[:-1]]
    starts = np.flatnonzero(first)
    ids = np.cumsum(first) - 1
    d_open = o[first][ids]
    day_h, day_l = np.maximum.reduceat(h, starts), np.minimum.reduceat(l, starts)
    prev_h, prev_l = np.r_[np.nan, day_h][ids], np.r_[np.nan, day_l][ids]
    prev = np.where(c > prev_h, 1, 0) - np.where(c < prev_l, 1, 0)
    tdo = np.sign(c - d_open).astype(int)
    idx = np.arange(len(ts))
    after_mid = np.where(t >= (day + 1) * 86400, idx, len(ts))            # 00:00 NY del día en que termina el día de trading
    mid_idx = np.minimum.reduceat(after_mid, starts)[ids]
    valid = (mid_idx < len(ts)) & (idx >= mid_idx)
    mid_open = o[np.minimum(mid_idx, len(ts) - 1)]
    mid = np.where(valid, np.sign(c - mid_open), 0).astype(int)
    sweep = htf_sweep_array(ts, h, l, c, start_hours, sweep_hours)
    nuevo = 2 * prev + tdo + mid
    return {"prev": prev, "tdo": tdo, "mid": mid, "sweep": sweep, "nuevo": nuevo, "viejo": 2 * prev + tdo,
            "con_sweep": nuevo + 2 * sweep, "solo_sweep": 2 * sweep, "d_open": d_open}


def vote_vs_trade(vote: int, direction: int) -> str:
    """El voto de una regla frente a la dirección de la operación."""
    return "neutro" if vote == 0 else "apoya" if vote * direction > 0 else "contra"


def bias_columns(bias: dict, k: int, d: int) -> dict:
    """Columnas de sesgo de una operación, con el sesgo en la vela k del disparo."""
    return {"puntuación sesgo": int(bias["nuevo"][k]), "sesgo": alignment(bias["nuevo"][k], d),
            "puntuación sesgo (reglas antiguas)": int(bias["viejo"][k]), "sesgo (reglas antiguas)": alignment(bias["viejo"][k], d),
            "voto ruptura previo": vote_vs_trade(int(bias["prev"][k]), d), "voto TDO": vote_vs_trade(int(bias["tdo"][k]), d),
            "voto Midnight": vote_vs_trade(int(bias["mid"][k]), d),
            "voto barrido vela anterior": vote_vs_trade(int(bias["sweep"][k]), d),
            "puntuación sesgo (con barrido)": int(bias["con_sweep"][k]), "sesgo (con barrido)": alignment(bias["con_sweep"][k], d),
            "sesgo (solo barrido)": alignment(bias["solo_sweep"][k], d)}


def alignment(score: float, direction: int) -> str:
    bias = 1 if score >= 2 else -1 if score <= -2 else 0
    return "sin sesgo" if bias == 0 else "a favor del sesgo" if bias == direction else "contra el sesgo"


# -- simulación de órdenes --------------------------------------------------------------------------------
def first_hit(mask: np.ndarray) -> int | None:
    idx = np.flatnonzero(mask)
    return int(idx[0]) if idx.size else None


def sim_from_fill(h, l, c, m, entry, stop, tp, d, horizon, cost=0.0):
    """Resultado de una operación llenada en la vela m: ('target'|'stop'|'abierta', fin, R, MAE, MFE).

    MAE / MFE: máxima excursión en contra / a favor (en precio). Si caben stop y objetivo en la misma vela, cuenta el stop.

    cost: spread (en precio) al entrar. Las velas son de precio bid: un largo compra al ask (entrada + spread) y sale al bid;
    un corto vende al bid y sale al ask, así que su stop y su objetivo saltan `cost` antes en las velas bid. El riesgo (1R)
    incluye el spread. Con cost = 0 no hay costes.
    """
    end = min(len(h), m + horizon)
    hs, ls = h[m:end], l[m:end]
    if d > 0:
        entry_eff = entry + cost
        risk = entry_eff - stop
        s_hit, t_hit = first_hit(ls <= stop), first_hit(hs >= tp)
        r_target = (tp - entry_eff) / risk
    else:
        entry_eff = entry
        risk = stop - entry
        s_hit, t_hit = first_hit(hs >= stop - cost), first_hit(ls <= tp - cost)
        r_target = (entry - tp) / risk
    if s_hit is not None and (t_hit is None or s_hit <= t_hit):
        status, last, r = "stop", s_hit, -1.0
    elif t_hit is not None:
        status, last, r = "target", t_hit, r_target
    else:
        status, last = "abierta", len(hs) - 1
        r = ((c[end - 1] - entry_eff) if d > 0 else (entry - (c[end - 1] + cost))) / risk
    seg_h, seg_l = hs[:last + 1], ls[:last + 1]
    if d > 0:
        mae, mfe = entry_eff - seg_l.min(), seg_h.max() - entry_eff
    else:
        mae, mfe = seg_h.max() + cost - entry, entry - (seg_l.min() + cost)
    return status, m + last, r, max(0.0, mae), max(0.0, mfe)


def spread_prices(source, sym, df) -> np.ndarray:
    """Spread (en precio) de cada vela de `df`, tal como lo registra MT5 (puntos x tamaño del punto del símbolo)."""
    from tradingbot.skills.feed.mt5_client import CHUNK
    mt5 = source._mt5
    point = mt5.symbol_info(sym).point
    frames, total, oldest = [], 0, None
    while oldest is None or oldest > int(df["ts"].iloc[0]):
        rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M15, total, CHUNK)
        if rates is None or len(rates) == 0:
            break
        frames.append(pd.DataFrame(rates)[["time", "spread"]])
        total += len(rates)
        oldest = int(rates["time"].min())
        if len(rates) < CHUNK:
            break
    sp = pd.concat(frames).drop_duplicates("time").rename(columns={"time": "ts"})
    merged = df[["ts"]].merge(sp, on="ts", how="left")["spread"]
    return (merged.fillna(merged.median()).to_numpy().astype(float)) * point


def continuation_row(var, base, st, d, rng, o, h, l, c, ny, bias, rel_range=float('nan'), spread=None):
    """Operación de la continuación según la versión `var`, o None si no hay operación (no se llena, sin recorrido...)."""
    k = st.rebreak_x
    if var.min_rango and not rel_range >= var.min_rango:      # NaN (sin historial suficiente) también se descarta
        return None
    if var.sesgo != "todos" and k is not None:
        mood = alignment(bias[var.sesgo_reglas][k], d)
        if mood == "contra el sesgo" or (var.sesgo == "a favor" and mood != "a favor del sesgo"):
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
    cost = float(spread[m]) if var.spread and spread is not None else 0.0
    risk = (entry + cost - stop) if d > 0 else (stop - entry)           # 1R, con el spread incluido en los largos
    target = level + d * var.objetivo * rng
    if risk <= 0 or (target - entry) * d <= 0:
        return None
    status, end_x, r, mae, mfe = sim_from_fill(h, l, c, m, entry, stop, target, d, 2 * WINDOW, cost)
    row = {**base, "fecha_entrada": ny(m), "hora entrada (NY)": ny(m).hour, "día semana": DAYS[ny(m).weekday()],
           "hora salida (NY)": ny(end_x), "entrada": entry, "stop": stop, "objetivo": target, "riesgo": risk,
           "riesgo / rango": risk / rng, "R potencial": abs(target - entry) / risk,
           "velas hasta llenar": m - k, "velas en operación": end_x - m,
           "resultado": status, "R": r if status != "abierta" else np.nan,
           "R abierta (a mercado)": r if status == "abierta" else np.nan,
           "MAE (R)": mae / risk, "MFE (R)": mfe / risk, "MAE (rangos)": mae / rng, "MFE (rangos)": mfe / rng,
           **bias_columns(bias, k, d),
           "entrada vs apertura": "premium" if entry > bias["d_open"][m] else "descuento",
           "rango vs mediana 20 sesiones": rel_range, "spread (precio)": cost, "spread en R": cost / risk}
    if var.spread:                                              # mismo trade sin costes, para medir cuánto cuesta el spread
        free = sim_from_fill(h, l, c, m, entry, stop, target, d, 2 * WINDOW)
        row["R sin spread"] = round(free[2], 2) if free[0] != "abierta" else np.nan
    for stop_key in STOPS:                                      # rejilla de sensibilidad: R para cada stop y objetivo
        for mult in TPS:
            stop2, tgt2 = stops[stop_key], level + d * mult * rng
            ok = (entry - stop2) * d > 0 and (tgt2 - entry) * d > 0
            res = sim_from_fill(h, l, c, m, entry, stop2, tgt2, d, 2 * WINDOW, cost) if ok else None
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
            # niveles en precios reales, para simular con spread (bid/ask) fuera del espejo
            ev.update(e_real=flip * entry, s_real=flip * stop, t_real=flip * tp, bot_real=flip * bot, rng=rng)
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


def real_c_trade(h, l, c, sp, ev, window):
    """Reversión C simulada en precios reales con el spread de cada vela, o None si no hay operación.

    Las velas son bid. Venta límite (corto): se llena cuando el bid llega a la entrada; compra límite (largo): cuando el ask
    (bid + spread) baja hasta ella. Stop y objetivo se activan por el lado que corresponde (ver sim_from_fill). El riesgo (1R)
    incluye el spread. La orden caduca si antes de llenarse llega al objetivo o pasa la ventana.
    """
    d = -ev["flip"]
    f, entry, stop, tp = ev["f"], ev["e_real"], ev["s_real"], ev["t_real"]
    if (entry - stop) * d <= 0:
        return None
    n = len(h)
    m = None
    for q in range(f + 1, min(n, f + 1 + window)):
        if d < 0:
            touched, hit_tp = h[q] >= entry, l[q] + sp[q] <= tp
        else:
            touched, hit_tp = l[q] + sp[q] <= entry, h[q] >= tp
        if touched:
            m = q
            break
        if hit_tp:
            return None
    if m is None:
        return None
    cost = float(sp[m])
    e_sim = entry if d < 0 else entry - cost                 # la compra límite se paga al ask: entrada efectiva = entry
    status, end_x, r, mae, mfe = sim_from_fill(h, l, c, m, e_sim, stop, tp, d, 2 * window, cost)
    free = sim_from_fill(h, l, c, m, entry, stop, tp, d, 2 * window)
    r_low = sim_from_fill(h, l, c, m, e_sim, stop, ev["bot_real"], d, 2 * window, cost)[2]
    risk = (e_sim + cost - stop) if d > 0 else (stop - e_sim)
    return dict(m=m, status=status, end_x=end_x, r=r, mae=mae, mfe=mfe, r_low=r_low, entry=entry, stop=stop, target=tp,
                risk=risk, rng=ev["rng"], cost=cost, r_free=free[2] if free[0] != "abierta" else np.nan)


def c_row(sym, s, ev, b, d, ny, bias):
    """Fila de la hoja Operaciones para la reversión C (b: resultado de la simulación; sin spread si no tiene 'cost')."""
    cost = b.get("cost", 0.0)
    row = {
        "mercado": sym, "tipo": "Reversión C", "TBR": s.zone.name, "día TBR": pd.Timestamp(s.day),
        "dirección": "long" if d > 0 else "short", "estado setup": b["status"] if b["status"] != "abierta" else "filled",
        "High": s.high, "50 %": (s.high + s.low) / 2, "Low": s.low, "rango": b["rng"],
        "rango % precio": 100 * b["rng"] / s.high, "hora toma (NY)": ny(ev["i"]), "hora retest (NY)": ny(ev["j"]),
        "hora 2ª ruptura (NY)": ny(ev["f"]), "fecha_entrada": ny(b["m"]), "hora entrada (NY)": ny(b["m"]).hour,
        "día semana": DAYS[ny(b["m"]).weekday()], "hora salida (NY)": ny(b["end_x"]),
        "entrada": b["entry"], "stop": b["stop"], "objetivo": b["target"], "riesgo": b["risk"],
        "riesgo / rango": b["risk"] / b["rng"], "R potencial": abs(b["target"] - b["entry"]) / b["risk"],
        "velas hasta llenar": b["m"] - ev["f"], "velas en operación": b["end_x"] - b["m"],
        "resultado": b["status"], "R": b["r"] if b["status"] != "abierta" else np.nan,
        "R abierta (a mercado)": b["r"] if b["status"] == "abierta" else np.nan,
        "MAE (R)": b["mae"] / b["risk"], "MFE (R)": b["mfe"] / b["risk"],
        "MAE (rangos)": b["mae"] / b["rng"], "MFE (rangos)": b["mfe"] / b["rng"],
        **bias_columns(bias, ev["f"], d),
        "spread (precio)": cost, "spread en R": cost / b["risk"],
        "R con objetivo en el Low/High opuesto": round(b["r_low"], 2)}
    if "cost" in b:
        row["R sin spread"] = round(b["r_free"], 2) if b["r_free"] == b["r_free"] else np.nan
    return row


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
    sweep_rows = []
    missed = {v.clave: [] for v in versiones}
    c_trades, c_trades_sp, events, meta = [], [], [], []
    for want in args.simbolos:
        sym = source.resolve_symbol(want)
        if not sym:
            print("  sin símbolo:", want)
            continue
        df = source.load_candles(sym, "15m").tail(args.velas).reset_index(drop=True)
        ts = df["ts"].to_numpy().astype(np.int64)
        o, h, l, c = (df[k].to_numpy().astype(float) for k in ("open", "high", "low", "close"))
        index = is_us_index(sym, DEFAULT_US_INDICES)
        bias = bias_arrays(ts, o, h, l, c, 18 if index else 17, 3 if index else 4)
        sweep_rows += sweep_events(sym, ts, o, h, l, c, 18 if index else 17, 3 if index else 4)
        spread = spread_prices(source, sym, df)
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
                row = continuation_row(var, base, st, d, rng, o, h, l, c, ny, bias, rel.get((st.zone_key, st.day), float('nan')), spread)
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
                    if ev["f"] is not None:
                        real = real_c_trade(h, l, c, spread, ev, WINDOW)
                        if real is not None:
                            c_trades_sp.append(c_row(sym, s, ev, real, -direction, ny, bias))
                    continue
                d = -direction
                c_trades.append(c_row(sym, s, ev, ev, d, ny, bias))                 # v1-v5: sin costes
                if ev["f"] is not None:
                    real = real_c_trade(h, l, c, spread, ev, WINDOW)                # v6 en adelante: spread real
                    if real is not None:
                        c_trades_sp.append(c_row(sym, s, ev, real, d, ny, bias))
    source.close()

    meta_df, E = pd.DataFrame(meta), pd.DataFrame(events)
    sweep_pred = sweep_prediction(pd.DataFrame(sweep_rows))
    C, C_sp = pd.DataFrame(c_trades), pd.DataFrame(c_trades_sp)
    results = {}
    for var in versiones:
        T = pd.concat([pd.DataFrame(trades[var.clave]), C_sp if var.spread else C], ignore_index=True).sort_values("fecha_entrada").reset_index(drop=True)
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
    comp_c = []
    for var in versiones:
        _, done_v, _ = results[var.clave]
        c_part = done_v[done_v["tipo"] == "Reversión C"].sort_values("fecha_entrada")
        for label, sub in (("sin filtro", c_part), ("solo a favor del sesgo", c_part[c_part["sesgo"] == "a favor del sesgo"]),
                           ("a favor o sin sesgo", c_part[c_part["sesgo"] != "contra el sesgo"])):
            if len(sub):
                comp_c.append({"versión": var.clave, "spread": "real" if var.spread else "sin costes", "filtro de sesgo": label,
                               **{k: v for k, v in stats(sub["R"]).items()
                                  if k in ("operaciones", "win rate %", "R medio", "R total", "profit factor", "max drawdown (R)",
                                           "estadístico t")}})
    comp_c = pd.DataFrame(comp_c)
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
        write_excel(path, T, done, M, E, meta_df, var, comp, comp_tbr, comp_bias, cambios, comp_c, sweep_pred)
        print("Excel:", path, f"({len(T)} operaciones, {len(M)} setups sin entrar)")
    print()
    print(comp.drop(columns=["ganadoras", "perdedoras", "R medio ganadora", "R medio perdedora", "mejor R", "peor R"]).to_string(index=False))


# -- Excel --------------------------------------------------------------------------------------------
def write_excel(path, T, done, M, E, meta, var, comp, comp_tbr, comp_bias, cambios, comp_c, sweep_pred) -> None:
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

    # aportación del Bias: ¿mejora la estrategia usarlo como filtro? (con las reglas nuevas y con las antiguas)
    regimes = (("sin filtro", None), ("solo a favor del sesgo", ["a favor del sesgo"]),
               ("a favor o sin sesgo (excluye contra)", ["a favor del sesgo", "sin sesgo"]),
               ("solo contra el sesgo", ["contra el sesgo"]), ("solo sin sesgo", ["sin sesgo"]))
    bias_rows = []
    for kind in kinds:
        part = done[done["tipo"] == kind].sort_values("fecha_entrada")
        for rules, col in (("nuevas (ruptura, TDO, Midnight)", "sesgo"), ("antiguas (ruptura, apertura)", "sesgo (reglas antiguas)"),
                           ("nuevas + barrido de la vela anterior (peso 2)", "sesgo (con barrido)"),
                           ("solo barrido de la vela anterior", "sesgo (solo barrido)")):
            for label, allowed in regimes:
                sub = part if allowed is None else part[part[col].isin(allowed)]
                if len(sub):
                    bias_rows.append({"tipo": kind, "reglas del sesgo": rules, "filtro": label, **stats(sub["R"])})
    bias_value = pd.DataFrame(bias_rows)
    rule_rows = []
    for kind in kinds:
        part = done[done["tipo"] == kind]
        for col, name in (("voto ruptura previo", "ruptura del día anterior"), ("voto TDO", "TDO"), ("voto Midnight", "Midnight"),
                          ("voto barrido vela anterior", "barrido de la vela anterior (H3/H4)")):
            for vote in ("apoya", "neutro", "contra"):
                sub = part[part[col] == vote].sort_values("fecha_entrada")
                if len(sub):
                    st_ = stats(sub["R"])
                    rule_rows.append({"tipo": kind, "regla": name, "su voto frente a la operación": vote,
                                      **{k: st_[k] for k in ("operaciones", "win rate %", "R medio", "R total", "profit factor", "estadístico t")}})
    by_rule = pd.DataFrame(rule_rows)
    dist = (done.groupby(["tipo", "sesgo"]).size().rename("operaciones nuevas").reset_index()
            .merge(done.groupby(["tipo", "sesgo (reglas antiguas)"]).size().rename("operaciones antiguas").reset_index()
                   .rename(columns={"sesgo (reglas antiguas)": "sesgo"}), on=["tipo", "sesgo"], how="outer").fillna(0))
    costs = pd.DataFrame()
    if var.spread:                    # cuánto cuesta el spread y cuánto spread aguanta la ventaja
        cc = done[done["tipo"] == "Continuación"].copy()
        cc["spread % precio"] = 100 * cc["spread (precio)"] / cc["entrada"]
        rows = []
        for key, g in [*cc.groupby("mercado"), ("TODOS", cc)]:
            free, paid = g["R sin spread"].mean(), g["R"].mean()
            rows.append({"mercado": key, "operaciones": len(g), "spread medio (precio)": g["spread (precio)"].mean(),
                         "spread % del precio": g["spread % precio"].mean(), "spread medio en R": g["spread en R"].mean(),
                         "R medio sin spread": free, "R medio con spread": paid, "coste del spread (R)": free - paid,
                         "veces el spread que aguanta la ventaja": free / (free - paid) if free - paid else np.nan})
        costs = pd.DataFrame(rows).round(4)
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
        ["Spread en la reversión C", "En v1-v5 la reversión C se simula sin costes (como la continuación). Desde v6 se simula en precios "
                                     "reales con el spread de cada vela: la venta límite se llena con el bid, la compra límite con el ask, y el stop "
                                     "y el objetivo se activan por el lado correspondiente. El riesgo (1R) incluye el spread."],
        ["Reversión C", "Tras la toma y el retest del 50 %, cierre bajo el mínimo del retest sin 2ª ruptura; orden límite en ese "
                        "mínimo, stop en el High tomado, objetivo en el nivel -1 por el lado contrario. Es una propuesta: aún no está en la skill."],
        ["Supuestos", "Sin spread ni comisiones. Si en una vela caben stop y objetivo, cuenta el stop (pesimista). Ventana de "
                      "24 h para completar el setup y 48 h para resolverlo. Las operaciones abiertas al final de los datos no cuentan en las estadísticas."],
        ["Sesgo reconstruido", "Con las reglas actuales del bot: ruptura del día de trading anterior x2, precio vs TDO x1 y precio vs "
                               "Midnight (00:00 NY) x1; sesgo si |puntuación| >= 2. Hasta v6 el análisis usaba ruptura x2 + apertura del día x1 "
                               "(las columnas '... (reglas antiguas)' las conservan). Se calcula en la vela del disparo, sin mirar al futuro."],
        ["Lectura", "R = múltiplo del riesgo inicial. 'estadístico t' > 2 indica que el R medio difiere de cero con cierta fiabilidad; "
                    "con muchas pruebas cruzadas (hoja por hoja) hay que ser prudente: pueden salir ventajas por azar."],
        ["Cuidado: sesgo de selección", "Los setups que caducan 'porque el precio llegó al objetivo sin llenar la orden' son ganadores por "
                                        "construcción: su R a mercado NO es una expectativa. Para comparar entradas se usan TODAS las 2ª rupturas "
                                        "(versiones v2 y v3: entrada a mercado en la apertura de la vela siguiente)."],
        ["Reversión B (descartada)", "Otra reversión probada (barrido que cierra de vuelta dentro, venta/compra límite en el nivel) dio "
                                     "R medio de -0,24 con 15.086 operaciones: no se incluye."]]

    with pd.ExcelWriter(path, engine="openpyxl") as xl:
        sheets = [("Cambios", cambios), ("Comparativa", comp), ("Comparativa por TBR", comp_tbr),
                  ("Comparativa por sesgo", comp_bias), ("Comparativa reversión C", comp_c), ("Costes del spread", costs), ("Aportación del Bias", bias_value),
                  ("Aportación por regla", by_rule), ("Barrido - predicción vela", sweep_pred), ("Distribución del sesgo", dist), ("Resumen", None), ("Por TBR", by_tbr), ("Por TBR y dirección", by_tbr_dir), ("Por TBR y sesgo", by_tbr_bias),
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
