"""Motor de la estrategia CRT (variante B): sweep en el HTF, FVG tocado en MTF, iFVG en LTF, CISD y tres entradas.

Lo usan la skill CRT (en directo) y scripts/backtest_crt.py (histórico): es el mismo código, así lo probado es lo que se opera.
Reglas completas en docs/estrategia_crt/GUIA.md. El largo se calcula como el corto con los precios cambiados de signo (`view`).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

MTF = (15, 30, 60)                                       # timeframes del FVG de confirmación (minutos)


@dataclass(frozen=True)
class Cfg:
    """Mercado: velas HTF, cierre de sesión y desfase del servidor respecto a Nueva York."""
    htf_min: int = 180                                   # índices H3 (180), forex H4 (240)
    origin: int = 18 * 3600                              # las velas HTF empiezan a esta hora NY (segundos desde las 00:00)
    session_end: int = 18 * 3600                         # a esta hora NY no se abren entradas y lo abierto se cierra
    ahead: int = 7 * 3600                                # servidor = NY + ahead


INDICES = Cfg(180, 18 * 3600, 18 * 3600)
FOREX = Cfg(240, 17 * 3600, 17 * 3600)


@dataclass(frozen=True)
class Rule:
    lookback_days: int = 10                              # antigüedad máxima del FVG de MTF
    touch_tol: float = 0.0                               # tolerancia al tocar el FVG, en fracción del precio
    leg_min: int = 120                                   # minutos hacia atrás para buscar el FVG LTF del tramo del sweep
    close_inside: bool = False                           # informativo, con look-ahead: C2 cierra dentro del rango de C1
    wait_c2: bool = False                                # sin look-ahead: espera al cierre de C2 y busca el CISD hasta el final de C3
    rr: float = 2.0
    be_at: float = 1.0                                   # el stop pasa a la entrada al llegar a este R (0 = sin BE)


def aggregate(df: pd.DataFrame, minutes: int, cfg: Cfg, origin: int = 0) -> pd.DataFrame:
    """Velas de `minutes` minutos alineadas a `origin` segundos de la hora de NY, a partir de velas más cortas."""
    ny = df["ts"].to_numpy() - cfg.ahead
    key = (ny - origin) // (minutes * 60)
    g = df.groupby(key, sort=True)
    out = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(), "close": g["close"].last(),
                        "spread": g["spread"].last() if "spread" in df else 0.0})
    out["ts"] = out.index.to_numpy() * minutes * 60 + origin + cfg.ahead
    return out.reset_index(drop=True)


def view(df: pd.DataFrame, sign: int) -> dict:
    """Arrays de precios. sign = -1 cambia el signo (y por tanto máximos y mínimos): un largo se ve como un corto."""
    ts = df["ts"].to_numpy().astype(np.int64)
    o, h, l, c = (df[k].to_numpy().astype(float) for k in ("open", "high", "low", "close"))
    sp = df["spread"].to_numpy().astype(float) if "spread" in df else np.zeros(len(df))
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


def session_end(ts: int, cfg: Cfg) -> int:
    """Próximo cierre de sesión (hora de servidor) posterior a `ts`."""
    ny = ts - cfg.ahead
    return ((ny - cfg.session_end) // 86400 + 1) * 86400 + cfg.session_end + cfg.ahead


# -- setups --------------------------------------------------------------------------------------------------------------

def find_setups(base: pd.DataFrame, ltf: pd.DataFrame, ltf_min: int, rule: Rule, cfg: Cfg) -> tuple[list, dict]:
    """Todos los setups (sweep + FVG de MTF + iFVG + CISD) de las velas dadas, sin entrada todavía.

    `base` son las velas de las que salen el HTF y el MTF (en el backtest, M5) y `ltf` las de la entrada (M5, M3 o M1).
    """
    htf = aggregate(base, cfg.htf_min, cfg, cfg.origin)
    mtf = {m: aggregate(base, m, cfg) for m in MTF}
    funnel = {"velas HTF con sweep": 0, "con FVG de MTF sin mitigar al alcance": 0, "con el extremo tocando el FVG": 0,
              "con iFVG": 0, "con CISD": 0}
    leg_bars = max(rule.leg_min // ltf_min, 3)
    setups = []
    for sign, name in ((1, "short"), (-1, "long")):
        B, L, H = view(base, sign), view(ltf, sign), view(htf, sign)
        fv = {m: bearish_fvgs(view(mtf[m], sign), m) for m in MTF}
        lts, lo_, hi_, cl_, op_ = L["ts"], L["low"], L["high"], L["close"], L["open"]
        for i in range(1, len(H["ts"])):
            s2 = int(H["ts"][i])
            if s2 - int(H["ts"][i - 1]) > cfg.htf_min * 60 or H["high"][i] <= H["high"][i - 1]:
                continue
            c1h, c1l = H["high"][i - 1], H["low"][i - 1]
            a, b = int(np.searchsorted(lts, s2)), int(np.searchsorted(lts, s2 + cfg.htf_min * 60))
            if b - a < 4:
                continue
            rel = np.flatnonzero(hi_[a:b] > c1h)
            if not len(rel):
                continue
            s0 = a + int(rel[0])
            if rule.wait_c2 and not (c1l <= H["close"][i] < c1h):             # C2 tiene que cerrar dentro del rango de C1
                continue
            b_end = int(np.searchsorted(lts, s2 + 2 * cfg.htf_min * 60)) if rule.wait_c2 else b
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
                        zones.append((m, float(f["bottom"][q]), float(f["top"][q]), int(f["formed"][q])))
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
                            "z_bottom": float(hi_[kf - 2]), "z_top": float(lo_[kf]),
                            "mtf": "/".join(sorted({f"M{z[0]}" for z in hit}, key=lambda x: int(x[1:]))),
                            "inside": bool(c1l <= H["close"][i] <= c1h),
                            # detalle para dibujar la operación (índices sobre las velas `ltf`; zonas en el espacio del corto)
                            "s0": s0, "kf": kf, "m_inv": m_inv, "seq": (st, e), "c1": (c1l, c1h), "zones": hit}
                    break
            funnel["con el extremo tocando el FVG"] += hit_ever
            funnel["con iFVG"] += inv_ever
            if trig:
                funnel["con CISD"] += 1
                setups.append(trig)
    setups.sort(key=lambda s: s["jc"] * 10 + (0 if s["sign"] > 0 else 1))
    return setups, funnel


# -- entradas y gestión --------------------------------------------------------------------------------------------------

def entry_point(L: dict, st: dict, variant: int, ltf_min: int, rule: Rule, cfg: Cfg, closed: int | None = None) -> dict | None:
    """Dónde y cuándo se entra en un setup (espacio del corto: stop por encima, objetivo por debajo), o None si no hay entrada.

    `closed` es el número de velas ya cerradas (por defecto todas): la vela de la entrada puede ser la que aún se forma, pero la
    condición de «sin mecha» (entrada 3) solo se mira en velas cerradas.
    """
    ts, o, h, l, c = L["ts"], L["open"], L["high"], L["low"], L["close"]
    n, jc, hx, step = len(ts), st["jc"], st["stop"], ltf_min * 60
    closed = n if closed is None else closed
    end = session_end(int(ts[jc]), cfg)
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
        while k < min(n, closed) and ts[k] < end and ts[k] - ts[k - 1] <= 2 * step:
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
    return {"entry": float(entry), "start": int(start), "fill": fill, "risk": float(risk), "end": int(end)}


def manage(L: dict, st: dict, ep: dict, rule: Rule) -> dict:
    """Gestión de una entrada con las velas dadas: stop, objetivo, BE y cierre de sesión. Devuelve la fila del backtest."""
    ts, h, l, c, sp = L["ts"], L["high"], L["low"], L["close"], L["spread"]
    n, hx, entry, risk, start, fill, end = len(ts), st["stop"], ep["entry"], ep["risk"], ep["start"], ep["fill"], ep["end"]
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
    return {"exit_index": j, "exit_price": float(exit_price), "cómo": how, "target": float(target), "gross": (entry - exit_price) / risk,
            "cost": sp[start] / risk}
