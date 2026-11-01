"""Backtest del CRT (variante B) en NAS100 (HTF H3) o forex (HTF H4, --mercado forex): sweep en el HTF, FVG tocado en MTF, iFVG en M5/M3, CISD y tres entradas.

REGLAS (las del usuario, ver docs/estrategia_crt/GUIA.md) Y CRITERIOS, FIJADOS ANTES DE VER LOS RESULTADOS:
- HTF = H3 con las velas alineadas a las 18:00 NY (18, 21, 0, 3 ... 15). Sweep: una vela H3 (C2) supera el máximo (o mínimo) de la
  anterior (C1). Máximo barrido -> corto; mínimo barrido -> largo. El largo se calcula como el corto con los precios cambiados
  de signo, así que las dos direcciones usan exactamente el mismo código.
- "Cierra dentro del rango": en vivo no se conoce hasta que C2 termina, así que el CISD exige que el precio ya esté de vuelta
  dentro del rango de C1 (cierre LTF por debajo del máximo de C1, en cortos). Variante informativa, CON look-ahead: exigir además
  que C2 cierre dentro del rango de C1.
- Si C2 supera los dos extremos de C1 a la vez, ese setup se descarta.
- MTF = M15, M30 y H1 (se agregan de M5). Criterio 2: el máximo del sweep (el más alto de C2 hasta el momento) está dentro de un
  FVG bajista de MTF (largos: el mínimo dentro de un FVG alcista). Definiciones operativas:
    * FVG: tres velas con hueco entre el mínimo de la 1.ª y el máximo de la 3.ª (bajista) o al revés (alcista).
    * Ya formado: la 3.ª vela está cerrada antes de la primera vela LTF que supera el máximo de C1.
    * Sin mitigar: desde que se forma hasta que empieza el sweep, ningún precio ha entrado en la zona.
    * Antigüedad máxima: 10 días (sensibilidad: 3 y 30).
    * Toca: el extremo del sweep cae dentro de la zona del FVG (sin tolerancia; sensibilidad con tolerancia).
- LTF = M5 y M3 (dos backtests separados; el TF donde aparece el iFVG es el TF de entrada).
    * iFVG (cortos): FVG alcista del tramo alcista que lleva al extremo del sweep (3.ª vela entre 120 min antes y la vela del extremo,
      sin cerrar por debajo de su base antes del extremo). Se invierte cuando una vela cierra por debajo de su base.
    * CISD: tras la inversión, cierre por debajo de la apertura de la secuencia de velas alcistas consecutivas que terminó en el
      extremo del sweep. Tiene que ocurrir dentro de C2.
- Entradas (cada una es un backtest):
    1. A la apertura de la vela siguiente a la del CISD.
    2. Retesteo del iFVG: el precio continúa (nuevo mínimo bajo el de la vela del CISD) y vuelve a la base del iFVG; orden límite en
       esa base. Se cancela si toca el stop o si llega al objetivo sin retestear.
    3. Primera vela sin mecha tras el CISD (sin mecha en el lado del extremo: bajista con máximo = apertura, en cortos). Entrada a la
       apertura de la vela siguiente.
- Stop en el extremo del sweep (sin colchón; el spread se descuenta como coste). Objetivo 2R. A 1R el stop pasa a la entrada (BE).
  Stop y objetivo en la misma vela: cuenta el stop. A las 18:00 NY no se abren entradas y lo abierto se cierra al cierre de la última
  vela anterior. Una operación a la vez (se descartan setups que llegan con otra operación abierta).
- Costes: spread real de MT5 en la vela de entrada (R neto = R bruto - spread / riesgo).
- Se da por buena (cada una de las 6 combinaciones LTF x entrada) si cumple TODOS:
    1. NAS100 de PUPrime, todo el histórico: >= 100 operaciones y R neto medio > +0,05 con t > 2.
    2. R neto medio positivo en 2018-2022 y en 2023 en adelante (con al menos una operación en cada periodo).
    3. R neto medio > 0 en el control: NAS100 (USTEC) de MetaQuotes.

Uso (desde la raíz del proyecto):
    uv run python scripts/backtest_crt.py --descargar     # velas M5 y M3 de MT5 (solo lectura)
    uv run python scripts/backtest_crt.py

Salida: docs/estrategia_crt/RESULTADOS.md y analisis/backtest_crt_<mercado>_m<tf>_e<entrada>.csv (operaciones).
"""
from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from backtest_orb_nasdaq import row, summary, table                                   # noqa: E402
from backtest_patrones import AHEAD                                                   # noqa: E402
from estudio_ema_vwap import TRAIN_END                                                # noqa: E402

DOC = ROOT / "docs" / "estrategia_crt" / "RESULTADOS.md"
H3_MIN = 180
H3_ORIGIN = 18 * 3600                                    # las velas H3 empiezan a las 18:00 NY
SESSION_END = 18 * 3600                                  # cierre de sesión de los índices
MTF = (15, 30, 60)
LTFS = (5, 3)
VARIANTS = {1: "vela siguiente al CISD", 2: "retesteo del iFVG", 3: "primera vela sin mecha"}
MIN_OPS, MIN_MEAN, MIN_T = 100, 0.05, 2.0
DATASETS = (("puprime", "NAS100"), ("metaquotes", "NAS100"))                          # el control, al final
MARKETS = {
    "indices": dict(htf="H3", htf_min=180, origin=18 * 3600, session_end=18 * 3600, suffix="", unit=1.0, unit_name="pts",
                    datasets=(("puprime", "NAS100"), ("metaquotes", "NAS100")), title="NAS100",
                    primary="NAS100 de PUPrime", control="NAS100 (USTEC) de MetaQuotes"),
    # Forex: velas H4 alineadas a las 17:00 NY (las H4 nativas de MT5, servidor = NY + 7 h) y cierre de sesión a las 17:00 NY, el
    # corte del día FX. Referencia EURUSD, control GBPUSD (los dos de PUPrime).
    "forex": dict(htf="H4", htf_min=240, origin=17 * 3600, session_end=17 * 3600, suffix="_forex", unit=0.0001, unit_name="pips",
                  datasets=(("puprime", "EURUSD"), ("puprime", "GBPUSD")), title="EURUSD y GBPUSD",
                  primary="EURUSD de PUPrime", control="GBPUSD de PUPrime"),
}


def configure(name: str) -> dict:
    """Aplica el mercado elegido a las constantes que usan el resto de funciones."""
    global H3_MIN, H3_ORIGIN, SESSION_END, DATASETS
    m = MARKETS[name]
    H3_MIN, H3_ORIGIN, SESSION_END, DATASETS = m["htf_min"], m["origin"], m["session_end"], m["datasets"]
    return m


@dataclass(frozen=True)
class Rule:
    lookback_days: int = 10                              # antigüedad máxima del FVG de MTF
    touch_tol: float = 0.0                               # tolerancia al tocar el FVG, en fracción del precio
    leg_min: int = 120                                   # minutos hacia atrás para buscar el FVG LTF del tramo del sweep
    close_inside: bool = False                           # informativo, con look-ahead: C2 cierra dentro del rango de C1
    wait_c2: bool = False                                # sin look-ahead: espera al cierre de C2 y busca el CISD hasta el final de C3
    rr: float = 2.0
    be_at: float = 1.0                                   # el stop pasa a la entrada al llegar a este R (0 = sin BE)


# -- datos ---------------------------------------------------------------------------------------------------------------

def cache_path(profile: str, want: str, tf: int) -> Path:
    return ROOT / "analisis" / f"crt_{profile}_{want.lower()}_m{tf}.pkl"


def download(profile: str, want: str, tf: int) -> None:
    """Velas M<tf> con spread (en precio) y tick volume. Todos los perfiles comparten el terminal: cambia su cuenta."""
    from tradingbot.config import load_profiles, select_profile
    from tradingbot.skills.feed.mt5_client import CHUNK, Mt5Source
    profiles, default = load_profiles()
    source = Mt5Source(select_profile(profiles, default, profile), 2_000_000)
    print("conectado:", source.connect(), flush=True)
    sym = source.resolve_symbol(want)
    mt5 = source._mt5
    mt5.symbol_select(sym, True)
    point = mt5.symbol_info(sym).point
    frames, pos = [], 0
    while True:
        rates = None
        for _ in range(6):                               # la primera petición puede llegar antes de que MT5 sincronice
            rates = mt5.copy_rates_from_pos(sym, getattr(mt5, f"TIMEFRAME_M{tf}"), pos, CHUNK)
            if rates is not None and len(rates):
                break
            time.sleep(2)
        if rates is None or len(rates) == 0:
            break
        frames.append(pd.DataFrame(rates))
        pos += len(rates)
        if len(rates) < CHUNK:
            break
    source.close()
    df = pd.concat(frames).drop_duplicates("time").sort_values("time").reset_index(drop=True)
    df = df.rename(columns={"time": "ts"})[["ts", "open", "high", "low", "close", "tick_volume", "spread"]]
    df["spread"] = df["spread"].astype(float) * point
    ts = df["ts"].to_numpy()
    step, start = np.diff(ts), 0
    for i in range(0, max(len(step) - 200, 1), 50):      # antes, MT5 solo tiene velas de varias horas o diarias
        if np.median(step[i:i + 200]) <= tf * 60:
            start = i
            break
    df = df.iloc[start:-1].reset_index(drop=True)        # sin la última vela, que puede estar abierta
    cache_path(profile, want, tf).parent.mkdir(exist_ok=True)
    pd.to_pickle((sym, df), cache_path(profile, want, tf))
    print(f"  {sym} M{tf}: {len(df)} velas ({pd.Timestamp(int(ts[start]) - AHEAD, unit='s')} -> "
          f"{pd.Timestamp(int(ts[-2]) - AHEAD, unit='s')} NY)", flush=True)


def aggregate(df: pd.DataFrame, minutes: int, origin: int = 0) -> pd.DataFrame:
    """Velas de `minutes` minutos alineadas a `origin` segundos de la hora de NY, a partir de las M5."""
    ny = df["ts"].to_numpy() - AHEAD
    key = (ny - origin) // (minutes * 60)
    g = df.groupby(key, sort=True)
    out = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(), "close": g["close"].last(),
                        "spread": g["spread"].last()})
    out["ts"] = out.index.to_numpy() * minutes * 60 + origin + AHEAD
    return out.reset_index(drop=True)


def view(df: pd.DataFrame, sign: int) -> dict:
    """Arrays de precios. sign = -1 cambia el signo (y por tanto máximos y mínimos): un largo se ve como un corto."""
    ts = df["ts"].to_numpy().astype(np.int64)
    o, h, l, c, sp = (df[k].to_numpy().astype(float) for k in ("open", "high", "low", "close", "spread"))
    if sign < 0:
        o, c, h, l = -o, -c, -l, -h
    return {"ts": ts, "open": o, "high": h, "low": l, "close": c, "spread": sp}


def bearish_fvgs(v: dict, minutes: int) -> dict:
    """FVG bajistas: mínimo de la vela 1 por encima del máximo de la vela 3. `formed` = cierre de la vela 3."""
    ts, h, l = v["ts"], v["high"], v["low"]
    i = np.arange(2, len(ts))
    ok = (l[i - 2] > h[i]) & (ts[i] - ts[i - 2] <= 2 * minutes * 60 + 3600)
    i = i[ok]
    return {"formed": ts[i] + minutes * 60, "bottom": h[i], "top": l[i - 2]}


def session_end(ts: int) -> int:
    ny = ts - AHEAD
    return ((ny - SESSION_END) // 86400 + 1) * 86400 + SESSION_END + AHEAD


# -- setups --------------------------------------------------------------------------------------------------------------

def find_setups(base: pd.DataFrame, ltf: pd.DataFrame, ltf_min: int, rule: Rule) -> tuple[list, dict]:
    """Todos los setups (sweep + FVG de MTF + iFVG + CISD) del histórico, sin entrada todavía."""
    h3 = aggregate(base, H3_MIN, H3_ORIGIN)
    mtf = {m: aggregate(base, m) for m in MTF}
    funnel = {"velas HTF con sweep": 0, "con FVG de MTF sin mitigar al alcance": 0, "con el extremo tocando el FVG": 0,
              "con iFVG": 0, "con CISD": 0}
    leg_bars = max(rule.leg_min // ltf_min, 3)
    setups = []
    for sign, name in ((1, "short"), (-1, "long")):
        B, L, H = view(base, sign), view(ltf, sign), view(h3, sign)
        fv = {m: bearish_fvgs(view(mtf[m], sign), m) for m in MTF}
        lts, lo_, hi_, cl_, op_ = L["ts"], L["low"], L["high"], L["close"], L["open"]
        for i in range(1, len(H["ts"])):
            s2 = int(H["ts"][i])
            if s2 - int(H["ts"][i - 1]) > H3_MIN * 60 or H["high"][i] <= H["high"][i - 1]:
                continue
            c1h, c1l = H["high"][i - 1], H["low"][i - 1]
            a, b = int(np.searchsorted(lts, s2)), int(np.searchsorted(lts, s2 + H3_MIN * 60))
            if b - a < 4:
                continue
            rel = np.flatnonzero(hi_[a:b] > c1h)
            if not len(rel):
                continue
            s0 = a + int(rel[0])
            if rule.wait_c2 and not (c1l <= H["close"][i] < c1h):             # C2 tiene que cerrar dentro del rango de C1
                continue
            b_end = int(np.searchsorted(lts, s2 + 2 * H3_MIN * 60)) if rule.wait_c2 else b
            funnel["velas HTF con sweep"] += 1
            hall, t0 = hi_[a:b].max(), int(lts[s0])
            tol_all = rule.touch_tol * abs(hall)
            zones = []
            for m in MTF:
                f = fv[m]
                lo = int(np.searchsorted(f["formed"], t0 - rule.lookback_days * 86400, "left"))
                hi = int(np.searchsorted(f["formed"], t0, "right"))
                if hi <= lo:
                    continue
                sel = np.flatnonzero((f["top"][lo:hi] + tol_all > c1h) & (f["bottom"][lo:hi] - tol_all <= hall)) + lo
                for q in sel:
                    x0 = int(np.searchsorted(B["ts"], f["formed"][q], "left"))
                    x1 = int(np.searchsorted(B["ts"], t0, "left"))
                    if x1 <= x0 or B["high"][x0:x1].max() < f["bottom"][q]:     # sin mitigar
                        zones.append((m, float(f["bottom"][q]), float(f["top"][q])))
            if not zones:
                continue
            funnel["con FVG de MTF sin mitigar al alcance"] += 1
            hx, ih = hi_[s0], s0
            hit_ever = inv_ever = False
            trig = None
            for j in range(s0, b_end):
                if j < b and lo_[j] < c1l:                                    # barre los dos extremos de C1
                    break
                if hi_[j] > hx:
                    if j >= b:                                                # C3 sigue más allá del extremo: el setup se anula
                        break
                    hx, ih = hi_[j], j
                tol = rule.touch_tol * abs(hx)
                hit = [z for z in zones if z[1] - tol <= hx <= z[2] + tol]
                if not hit:
                    continue
                hit_ever = True
                if j == ih:
                    continue
                ks = np.arange(max(2, ih - leg_bars), ih + 1)
                ks = ks[lo_[ks] > hi_[ks - 2]]                                # FVG alcistas del tramo (en el espacio del corto)
                elig = [int(k) for k in ks if k == ih or cl_[k + 1:ih + 1].min() >= hi_[k - 2]]
                if not elig:
                    continue
                bots = hi_[np.array(elig) - 2]
                below = np.flatnonzero(cl_[ih + 1:j + 1] < bots.max())
                if not len(below):
                    continue
                m_inv = ih + 1 + int(below[0])
                kf = max(k for k in elig if hi_[k - 2] > cl_[m_inv])
                inv_ever = True
                e = ih
                while e > ih - 5 and cl_[e] <= op_[e]:                        # última vela alcista a/antes del extremo
                    e -= 1
                if cl_[e] <= op_[e]:
                    continue
                st = e
                while st - 1 >= 0 and cl_[st - 1] > op_[st - 1]:
                    st -= 1
                level = op_[st]
                if cl_[j] < level and cl_[j] < c1h and (not rule.wait_c2 or j >= b):
                    trig = {"sign": sign, "dirección": name, "C2": s2, "jc": j, "ih": ih, "stop": float(hx), "level": float(level),
                            "z_bottom": float(hi_[kf - 2]), "z_top": float(lo_[kf]), "mtf": "/".join(sorted({f"M{z[0]}" for z in hit}, key=lambda x: int(x[1:]))),
                            "inside": bool(c1l <= H["close"][i] <= c1h)}
                    break
            funnel["con el extremo tocando el FVG"] += hit_ever
            funnel["con iFVG"] += inv_ever
            if trig:
                funnel["con CISD"] += 1
                setups.append(trig)
    setups.sort(key=lambda s: s["jc"] * 10 + (0 if s["sign"] > 0 else 1))
    return setups, funnel


# -- entradas y gestión --------------------------------------------------------------------------------------------------

def execute(L: dict, st: dict, variant: int, ltf_min: int, rule: Rule) -> dict | None:
    """Entrada y gestión de un setup (espacio del corto: stop por encima, objetivo por debajo)."""
    ts, o, h, l, c, sp = L["ts"], L["open"], L["high"], L["low"], L["close"], L["spread"]
    n, jc, hx, step = len(ts), st["jc"], st["stop"], ltf_min * 60
    end = session_end(int(ts[jc]))
    fill = None
    if variant == 1:
        e = jc + 1
        if e >= n or ts[e] - ts[jc] > 2 * step or ts[e] >= end:
            return None
        entry, start = o[e], e
    elif variant == 2:
        zb = st["z_bottom"]
        risk0 = hx - zb
        if risk0 <= 0:
            return None
        target0, cont, k, start = zb - rule.rr * risk0, False, jc + 1, None
        while k < n and ts[k] < end and ts[k] - ts[k - 1] <= 2 * step:
            if cont and h[k] >= zb:
                entry, start, fill = max(zb, o[k]), k, k
                break
            if h[k] >= hx:                                # el setup se invalida antes de retestear
                break
            if l[k] < l[jc]:
                cont = True
            if cont and l[k] <= target0:                  # llegó al objetivo sin retestear
                break
            k += 1
        if start is None:
            return None
    else:
        k, start = jc + 1, None
        while k < n and ts[k] < end and ts[k] - ts[k - 1] <= 2 * step:
            if h[k] >= hx:
                break
            if c[k] < o[k] and h[k] <= o[k] + 1e-9:       # bajista sin mecha en el lado del extremo
                e = k + 1
                if e < n and ts[e] - ts[k] <= 2 * step and ts[e] < end:
                    entry, start = o[e], e
                break
            k += 1
        if start is None:
            return None
    risk = hx - entry
    if risk <= 0:
        return None
    target = entry - rule.rr * risk
    cur_stop, how, exit_price, j = hx, None, None, start
    while j < n:
        if ts[j] >= end:
            exit_price, how, j = c[j - 1], "sesión", j - 1
            break
        adverse = h[j] >= cur_stop
        favour = l[j] <= target and j != fill
        if adverse:
            exit_price, how = cur_stop, ("BE" if cur_stop == entry else "stop")
            break
        if favour:
            exit_price, how = target, "objetivo"
            break
        if rule.be_at and j != fill and (entry - l[j]) >= rule.be_at * risk:
            cur_stop = entry
        j += 1
    if exit_price is None:
        j, how = n - 1, "fin de datos"
        exit_price = c[j]
    sgn = st["sign"]
    gross = (entry - exit_price) / risk
    cost = sp[start] / risk
    return {"entrada (NY)": pd.Timestamp(int(ts[start]) - AHEAD, unit="s"), "cierre (NY)": pd.Timestamp(int(ts[j]) - AHEAD, unit="s"),
            "dirección": st["dirección"], "FVG MTF": st["mtf"], "C2 cierra dentro": st["inside"], "entrada": sgn * entry,
            "stop": sgn * hx, "objetivo": sgn * target, "salida": sgn * exit_price, "riesgo": risk, "riesgo %": 100 * risk / abs(entry),
            "cómo": how, "R bruto": gross, "coste (R)": cost, "R neto": gross - cost, "_ts_exit": int(ts[j])}


def run_variant(ltf: pd.DataFrame, setups: list, variant: int, ltf_min: int, rule: Rule) -> pd.DataFrame:
    views = {1: view(ltf, 1), -1: view(ltf, -1)}
    rows, last_exit = [], 0
    for st in setups:
        L = views[st["sign"]]
        if int(L["ts"][st["jc"]]) < last_exit:             # sigue abierta la operación anterior
            continue
        r = execute(L, st, variant, ltf_min, rule)
        if r is None:
            continue
        if rule.close_inside and not r["C2 cierra dentro"]:
            continue
        last_exit = r.pop("_ts_exit")
        rows.append(r)
    return pd.DataFrame(rows)


def by_period(t: pd.DataFrame, cut: pd.Timestamp = TRAIN_END) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not len(t):
        return t, t
    return t[t["entrada (NY)"] < cut], t[t["entrada (NY)"] >= cut]


def val(x: dict) -> str:
    return f"{x['R medio']:+.3f} R, t {x['estadístico t']:+.2f}" if x.get("operaciones") else "sin operaciones"


# -- informe -------------------------------------------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--descargar", action="store_true", help="descarga las velas M5 y M3 de MT5 y termina")
    ap.add_argument("--mercado", choices=sorted(MARKETS), default="indices",
                    help="indices (NAS100, HTF H3) o forex (EURUSD/GBPUSD, HTF H4)")
    ap.add_argument("--ltf", type=int, nargs="+", choices=(1, 3, 5), default=list(LTFS),
                    help="timeframes de entrada (iFVG, CISD y entrada). Con M1 el histórico de MT5 solo llega a 2024: el criterio (2) "
                         "usa dos mitades por fecha")
    ap.add_argument("--esperar-c2", action="store_true", help="espera al cierre de C2 dentro del rango de C1 (sin look-ahead) y "
                                                                "busca el CISD hasta el final de C3")
    args = ap.parse_args()
    mk = configure(args.mercado)
    ltfs = tuple(args.ltf)
    htf, unit, unit_name = mk["htf"], mk["unit"], mk["unit_name"]
    if args.descargar:
        for profile, want in DATASETS:
            for tf in ltfs:
                try:
                    download(profile, want, tf)
                except Exception as err:                       # noqa: BLE001
                    print(f"  fallo {profile} {want} M{tf}: {err}", flush=True)
        return
    base_rule = Rule(wait_c2=args.esperar_c2)
    suffix = mk["suffix"] + ("_m1" if ltfs == (1,) else "") + ("_esperar_c2" if args.esperar_c2 else "")
    doc = DOC.with_name(f"RESULTADOS{suffix}.md")

    def key(profile: str, want: str) -> str:
        return f"{profile}/{want}"

    raw = {}
    for profile, want in DATASETS:
        for tf in sorted({5, *ltfs}):
            sym, df = pd.read_pickle(cache_path(profile, want, tf))
            raw[(key(profile, want), tf)] = (f"{sym} ({profile})", df)
    P, C = key(*DATASETS[0]), key(*DATASETS[1])
    first = pd.Timestamp(int(raw[(P, min(ltfs))][1]["ts"].iloc[0]) - AHEAD, unit="s")
    last = pd.Timestamp(int(raw[(P, min(ltfs))][1]["ts"].iloc[-1]) - AHEAD, unit="s")
    if first < TRAIN_END - pd.Timedelta(days=730):
        cut, lab1, lab2 = TRAIN_END, "hasta 2022", "2023 en adelante"
    else:                                                   # histórico corto (M1): dos mitades por fecha
        cut = first + (last - first) / 2
        lab1, lab2 = f"1.ª mitad (hasta {cut:%Y-%m})", f"2.ª mitad (desde {cut:%Y-%m})"

    results, funnels, setups_by = {}, {}, {}
    for profile, want in DATASETS:
        k = key(profile, want)
        base = raw[(k, 5)][1]
        for tf in ltfs:
            st, fn = find_setups(base, raw[(k, tf)][1], tf, base_rule)
            setups_by[(k, tf)], funnels[(k, tf)] = st, fn
            for v in VARIANTS:
                t = run_variant(raw[(k, tf)][1], st, v, tf, base_rule)
                results[(k, tf, v)] = t
                if len(t):
                    t.to_csv(ROOT / "analisis" / f"backtest_crt_{profile}_{want.lower()}_m{tf}_e{v}{suffix}.csv", index=False)
            print(f"{k} M{tf}: {len(st)} setups", flush=True)

    verdict, summ = [], {}
    for tf in ltfs:
        for v, vname in VARIANTS.items():
            t, ctrl = results[(P, tf, v)], results[(C, tf, v)]
            s, c = summary(t), summary(ctrl)
            p1, p2 = by_period(t, cut)
            s1, s2 = summary(p1), summary(p2)
            ok1 = s.get("operaciones", 0) >= MIN_OPS and s["R medio"] > MIN_MEAN and s["estadístico t"] > MIN_T
            ok2 = bool(s1.get("operaciones")) and bool(s2.get("operaciones")) and s1["R medio"] > 0 and s2["R medio"] > 0
            ok3 = bool(c.get("operaciones")) and c["R medio"] > 0
            summ[(tf, v)] = (ok1, ok2, ok3)
            verdict.append([f"M{tf} · {v}. {vname}", f"{s.get('operaciones', 0)} ops, {val(s)}", "sí" if ok1 else "**no**",
                            f"{val(s1)} / {val(s2)}", "sí" if ok2 else "**no**", val(c), "sí" if ok3 else "**no**",
                            "**Pasa**" if ok1 and ok2 and ok3 else "No pasa"])
    n_pass = sum(all(x) for x in summ.values())

    out = [f"# Backtest: CRT (variante B) en {mk['title']}, {htf} → M15/M30/H1 → {'/'.join(f'M{x}' for x in ltfs)}" + (
               " · esperando al cierre de C2" if args.esperar_c2 else ""), "",
           *(["**Variante sin look-ahead:** C2 tiene que haber cerrado dentro del rango de C1 (cierre real del HTF) y el CISD y la "
              "entrada se buscan desde el cierre de C2 hasta el final de C3. Si el precio supera el extremo del sweep en C3, el setup "
              "se anula.", ""] if args.esperar_c2 else []),
           *(["**Forex:** velas H4 alineadas a las 17:00 NY, sin entradas a las 17:00 NY y lo abierto se cierra (el corte del día FX; "
              "las 18:00 eran el cierre de los índices). Mismas reglas que en NAS100 para FVG, iFVG, CISD, entradas y gestión.", ""]
             if args.mercado == "forex" else []),
           "Script: `scripts/backtest_crt.py`. Solo lee velas M1, M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están "
           "en la cabecera del script y en `GUIA.md`; se fijaron antes de ver los resultados.", "",
           f"- **Se da por buena (cada combinación LTF × entrada) si:** (1) {mk['primary']}, todo el histórico: ≥ {MIN_OPS} "
           f"operaciones y R neto > +{MIN_MEAN} con t > {MIN_T}; (2) R neto positivo en los dos periodos ({lab1}; {lab2}); (3) R neto "
           f"> 0 en el control ({mk['control']}).",
           f"- Son {3 * len(ltfs)} combinaciones, así que algún t alto por azar es esperable: se mira la consistencia, no un solo número.", "",
           "## Veredicto", "",
           table(verdict, ["Combinación", mk["primary"], "(1)", f"{lab1} / {lab2}", "(2)", f"Control: {mk['control']}", "(3)",
                           "Resultado"]),
           "", f"**{n_pass} de {3 * len(ltfs)} combinaciones pasan.**", "",
           "## Datos", ""]
    for (k, tf), (name, df) in raw.items():
        a, z = pd.Timestamp(int(df["ts"].iloc[0]) - AHEAD, unit="s"), pd.Timestamp(int(df["ts"].iloc[-1]) - AHEAD, unit="s")
        out.append(f"- {name} M{tf}: {len(df)} velas, {a:%Y-%m-%d} → {z:%Y-%m-%d} (NY).")
    out += ["", "## Embudo (cuántos pasos pasan)", ""]
    frows = []
    for (k, tf), fn in funnels.items():
        frows.append([f"{raw[(k, tf)][0]} M{tf}"] + [fn[x] for x in fn] + [len(setups_by[(k, tf)])])
    out += [table(frows, ["Mercado", *list(next(iter(funnels.values())).keys()), "setups finales"]), ""]
    out += [f"## Resultados en {mk['primary']} (R neto, con spread)", ""]
    for tf in ltfs:
        rows = []
        for v, vname in VARIANTS.items():
            t = results[(P, tf, v)]
            p1, p2 = by_period(t, cut)
            rows += [row(f"M{tf} · {v}. {vname}", t), row(f"  {lab1}", p1), row(f"  {lab2}", p2),
                     row("  sin costes (R bruto)", t, "R bruto")]
            if len(t):
                rows += [row("  largos", t[t["dirección"] == "long"]), row("  cortos", t[t["dirección"] == "short"])]
        out += [table(rows), ""]
    out += [f"## Control: {mk['control']}", ""]
    rows = []
    for tf in ltfs:
        for v, vname in VARIANTS.items():
            t = results[(C, tf, v)]
            p1, p2 = by_period(t, cut)
            rows += [row(f"M{tf} · {v}. {vname}", t), row(f"  {lab1}", p1), row(f"  {lab2}", p2)]
    out += [table(rows), "", f"## Cómo terminan y riesgo ({mk['primary']})", ""]
    rows = []
    for tf in ltfs:
        for v, vname in VARIANTS.items():
            t = results[(P, tf, v)]
            if not len(t):
                continue
            ends = ", ".join(f"{x} {n}" for x, n in t["cómo"].value_counts().items())
            rows.append([f"M{tf} · {v}", ends, f"{t['riesgo'].median() / unit:.1f}", f"{t['riesgo'].quantile(.1) / unit:.1f}",
                         f"{t['riesgo'].quantile(.9) / unit:.1f}", f"{t['coste (R)'].mean():.3f}",
                         f"{(t['coste (R)'] > 0.2).mean() * 100:.0f} %"])
    out += [table(rows, ["Combinación", "Cierres", f"Riesgo mediano ({unit_name})", "p10", "p90", "Coste medio (R)",
                         "Coste > 0,2 R"]), "", f"## Por año ({mk['primary']})", ""]
    for tf in ltfs:
        for v, vname in VARIANTS.items():
            t = results[(P, tf, v)]
            if len(t):
                out += [f"**M{tf} · {v}. {vname}**", "",
                        table([row(str(y), g) for y, g in t.groupby(t["entrada (NY)"].dt.year)]), ""]
    out += ["## Sensibilidad (no cuenta para el veredicto)", "",
            "Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).",
            ""]
    sens = []
    for label, rule in (("antigüedad del FVG 3 días", replace(base_rule, lookback_days=3)),
                        ("antigüedad del FVG 30 días", replace(base_rule, lookback_days=30)),
                        ("tolerancia al tocar el FVG 0,05 % del precio", replace(base_rule, touch_tol=0.0005)),
                        ("exigir que C2 cierre dentro de C1 (look-ahead)", replace(base_rule, close_inside=True)),
                        ("sin BE", replace(base_rule, be_at=0.0)), ("objetivo 3R", replace(base_rule, rr=3.0))):
        for tf in ltfs:
            if rule.lookback_days != base_rule.lookback_days or rule.touch_tol != base_rule.touch_tol:
                st, _ = find_setups(raw[(P, 5)][1], raw[(P, tf)][1], tf, rule)
            else:
                st = setups_by[(P, tf)]
            for v in VARIANTS:
                sens.append(row(f"{label}: M{tf} · {v}", run_variant(raw[(P, tf)][1], st, v, tf, rule)))
    out += [table(sens)]
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
