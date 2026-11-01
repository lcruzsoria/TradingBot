"""Motor de la estrategia CRT: el setup se define DENTRO de C2 (la vela HTF que manipula a C1).

C1 = rango, C2 = manipulación, C3 = expansión. Corto (el largo es el espejo, ver `view`):
  1. C2 supera el máximo de C1 con una mecha (el extremo del sweep, que va subiendo mientras C2 sigue haciendo máximos). Si C2 ya había
     tomado el mínimo de C1 antes, el sweep es el del mínimo (un largo), no este.
  2. Tras ese extremo, el desplazamiento a la baja deja un FVG BAJISTA de MTF (M5/M15) que nace DESPUÉS del extremo, y el precio
     vuelve a él (basta con que lo toque la mecha).
  3. En LTF (M5/M3/M1), después del toque, el precio deja un FVG ALCISTA (su 3.ª vela cierra tras el toque; sin plazo) que invierte con un
     cierre por debajo de su base: es el iFVG y esa inversión es el CISD.
  4. Entrada en corto, con el stop en el extremo del sweep. Todo ocurre antes de que cierre C2: no se espera a saber si C2 cierra dentro.
Si el precio llega al extremo opuesto de C1 (el objetivo) sin haber completado los pasos 2 y 3, el setup queda INVALIDADO (`Setups.invalid`).
Lo usan la skill CRT (en directo) y scripts/backtest_crt.py (histórico): es el mismo código, así lo probado es lo que se opera.
Reglas completas en docs/estrategia_crt/GUIA.md.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

MTF = (5, 15)                                            # timeframes del FVG de confirmación (minutos)


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
    close_inside: bool = False                           # informativo, con look-ahead: C2 cierra dentro del rango de C1
    rr: float = 2.0
    target_c1: bool = False                               # objetivo en el extremo opuesto de C1 (cortos: su mínimo) en vez de rr veces el riesgo
    min_rr: float = 0.0                                  # con el objetivo en C1: se descarta el setup si el extremo de C1 queda a menos de
                                                         # min_rr veces el riesgo de la entrada (se anota el R máximo que habría llegado a dar)
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

class Setups(list):
    """Lista de setups válidos; `invalid` guarda los invalidados (el precio llegó al extremo opuesto de C1 sin completar el setup)."""

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.invalid: list[dict] = []


def find_setups(base: pd.DataFrame, ltf: pd.DataFrame, ltf_min: int, rule: Rule, cfg: Cfg) -> tuple[list, dict]:
    """Todos los setups (sweep + FVG de MTF tras el extremo + vuelta + iFVG invertido) de las velas dadas, sin entrada todavía.

    `base` son las velas de las que salen el HTF y el MTF (en el backtest, M5) y `ltf` las de la entrada (M5, M3 o M1).
    """
    htf = aggregate(base, cfg.htf_min, cfg, cfg.origin)
    mtf = {m: aggregate(base, m, cfg) for m in MTF}
    funnel = {"velas HTF con sweep": 0, "con FVG de MTF formado tras el extremo": 0, "con vuelta al FVG": 0, "con iFVG": 0, "con CISD": 0,
              "invalidados": 0}
    setups = Setups()
    for sign, name in ((1, "short"), (-1, "long")):
        L, H = view(ltf, sign), view(htf, sign)
        fv = {m: bearish_fvgs(view(mtf[m], sign), m) for m in MTF}
        lts, lo_, hi_, cl_ = L["ts"], L["low"], L["high"], L["close"]

        def pool_after(extreme_ts: int, until: int) -> list:
            """FVG de MTF cuya primera vela termina después del extremo (nacen del desplazamiento) y que se forman antes de `until`."""
            out = []
            for m in MTF:
                f = fv[m]
                lo = int(np.searchsorted(f["formed"], extreme_ts + 2 * m * 60, "right"))
                hi = int(np.searchsorted(f["formed"], until, "right"))
                out += [(m, float(f["bottom"][q]), float(f["top"][q]), int(f["formed"][q])) for q in range(lo, hi)]
            return out

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
            if s0 > a and lo_[a:s0].min() < c1l:                                # C2 tomó antes el otro extremo de C1: el sweep es el del otro lado
                continue
            funnel["velas HTF con sweep"] += 1
            ks_all = 2 + a + np.flatnonzero(lo_[a + 2:b] > hi_[a:b - 2])        # velas 3 de los FVG alcistas de LTF (espacio del corto)
            hx, ih, jt, pool, hit = float(hi_[s0]), s0, None, None, []
            seen_zone = seen_touch = seen_ifvg = False
            trig = None
            for j in range(s0, b):
                if lo_[j] < c1l:                                                # llega al extremo opuesto de C1 sin setup: invalidado
                    reason = ("sin FVG de MTF" if not seen_zone else "sin vuelta al FVG de MTF" if not seen_touch
                              else "sin iFVG invertido")
                    setups.invalid.append({"sign": sign, "dirección": name, "C2": s2, "ih": ih, "stop": hx, "motivo": reason,
                                           "c1": (c1l, c1h)})
                    funnel["invalidados"] += 1
                    break
                if hi_[j] > hx:                                                 # extremo nuevo: lo anterior ya no vale
                    hx, ih, jt, pool, hit = float(hi_[j]), j, None, None, []
                    continue
                if pool is None:
                    pool = pool_after(int(lts[ih]), int(lts[b - 1]))
                seen_zone = seen_zone or any(z[3] <= lts[j] for z in pool)      # ya existe algún FVG de MTF nacido tras el extremo
                if jt is None:                                                  # primera vuelta al FVG de MTF: lo toca la mecha
                    hit = [z for z in pool if z[3] <= lts[j] and hi_[j] >= z[1]]
                    if not hit:
                        continue
                    jt, seen_touch = j, True
                ks = ks_all[(ks_all < j) & (ks_all > jt)]                       # FVG de LTF cuya 3.ª vela cierra después del toque
                alive = [int(k) for k in ks if cl_[k + 1:j].size == 0 or cl_[k + 1:j].min() >= hi_[k - 2]]      # aún sin invertir
                seen_ifvg |= bool(alive)
                done = [k for k in alive if cl_[j] < hi_[k - 2]]                # el cierre de esta vela lo invierte: CISD
                if not done:
                    continue
                kf = max(done)
                trig = {"sign": sign, "dirección": name, "C2": s2, "jc": j, "ih": ih, "stop": hx, "level": float(hi_[kf - 2]),
                        "z_bottom": float(hi_[kf - 2]), "z_top": float(lo_[kf]),
                        "mtf": "/".join(sorted({f"M{z[0]}" for z in hit}, key=lambda x: int(x[1:]))),
                        "inside": bool(c1l <= H["close"][i] <= c1h),
                        "c2_end": s2 + cfg.htf_min * 60,                        # la entrada tiene que abrirse antes (si C2 sigue en curso, no se sabe por las velas)
                        # detalle para dibujar la operación (índices sobre las velas `ltf`; zonas en el espacio del corto)
                        "s0": s0, "kf": kf, "m_inv": j, "jt": jt, "seq": (kf - 2, ih), "c1": (c1l, c1h), "zones": hit}
                break
            funnel["con FVG de MTF formado tras el extremo"] += seen_zone
            funnel["con vuelta al FVG"] += seen_touch
            funnel["con iFVG"] += seen_ifvg
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
    limit = min(end, st["c2_end"])                        # la entrada tiene que abrirse antes de que cierre C2
    fill = None
    if variant == 1:
        e = jc + 1
        if e >= n or ts[e] - ts[jc] > 2 * step or ts[e] >= limit:
            return None
        entry, start = o[e], e
    elif variant == 2:
        zb = st["z_bottom"]
        risk0 = hx - zb
        if risk0 <= 0:
            return None
        target0, cont, k, start = (st["c1"][0] if rule.target_c1 else zb - rule.rr * risk0), False, jc + 1, None
        if target0 >= zb:                                 # el extremo de C1 queda por encima de la entrada: no hay objetivo válido
            return None
        while k < n and ts[k] < limit and ts[k] - ts[k - 1] <= 2 * step:
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
    elif variant == 4:                                    # al cierre de la vela del CISD: a mercado, sin esperar a la siguiente
        if ts[jc] + step >= limit:
            return None
        entry, start = c[jc], jc + 1
    else:
        k, start = jc + 1, None
        while k < min(n, closed) and ts[k] < limit and ts[k] - ts[k - 1] <= 2 * step:
            if h[k] >= hx:
                break
            if c[k] < o[k] and h[k] <= o[k] + 1e-9:       # bajista sin mecha en el lado del extremo
                e = k + 1
                if e < n and ts[e] - ts[k] <= 2 * step and ts[e] < limit:
                    entry, start = o[e], e
                break
            k += 1
        if start is None:
            return None
    risk = hx - entry
    if risk <= 0:
        return None
    return {"entry": float(entry), "start": int(start), "fill": fill, "risk": float(risk), "end": int(end)}


def planned_rr(st: dict, ep: dict) -> float:
    """R que da la entrada si el objetivo es el extremo opuesto de C1 (espacio del corto: su mínimo)."""
    return float((ep["entry"] - st["c1"][0]) / ep["risk"])


def max_r(L: dict, st: dict, ep: dict) -> float:
    """El R máximo que habría dado la entrada: lo más lejos que llega el precio a favor antes de tocar el stop o de cerrar la sesión."""
    ts, h, l = L["ts"], L["high"], L["low"]
    j, n = ep["start"], len(ts)
    while j < n and ts[j] < ep["end"] and h[j] < st["stop"]:
        j += 1
    return float(max((ep["entry"] - l[ep["start"]:j].min()) / ep["risk"], 0.0)) if j > ep["start"] else 0.0


def manage(L: dict, st: dict, ep: dict, rule: Rule) -> dict | None:
    """Gestión de una entrada con las velas dadas: stop, objetivo, BE y cierre de sesión. Devuelve la fila del backtest."""
    ts, h, l, c, sp = L["ts"], L["high"], L["low"], L["close"], L["spread"]
    n, hx, entry, risk, start, fill, end = len(ts), st["stop"], ep["entry"], ep["risk"], ep["start"], ep["fill"], ep["end"]
    target = st["c1"][0] if rule.target_c1 else entry - rule.rr * risk
    if target >= entry:                                   # objetivo en C1 ya alcanzado o por encima de la entrada: no se opera
        return None
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
