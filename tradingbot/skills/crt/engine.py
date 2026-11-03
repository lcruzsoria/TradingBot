"""Motor de la estrategia CRT: el setup se define DENTRO de C2 (la vela HTF que manipula a C1).

C1 = rango, C2 = manipulación, C3 = expansión. Corto (el largo es el espejo, ver `view`):
  1. C2 supera el máximo de C1 con una mecha (el extremo del sweep, que va subiendo mientras C2 sigue haciendo máximos). Si C2 ya había
     tomado el mínimo de C1 antes, el sweep es el del mínimo (un largo), no este.
  2. Tras ese extremo, el desplazamiento a la baja deja un FVG BAJISTA de MTF (M15) que nace DESPUÉS del extremo, y el precio
     vuelve a él (basta con que lo toque la mecha).
  3. En LTF (M5/M3/M1), después del toque, el precio deja un FVG ALCISTA (su 3.ª vela cierra tras el toque; sin plazo) que invierte con un
     cierre por debajo de su base: es el iFVG y esa inversión es el CISD.
  4. Entrada en corto, con el stop en el extremo del sweep. Todo ocurre antes de que cierre C2: no se espera a saber si C2 cierra dentro.
Si el precio llega al extremo opuesto de C1 (el objetivo) sin haber completado los pasos 2 y 3, el setup queda INVALIDADO (`Setups.invalid`).
Lo usan la skill CRT (en directo) y scripts/backtest_crt.py (histórico): es el mismo código, así lo probado es lo que se opera.
Reglas completas en docs/estrategia_crt/GUIA.md.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

MTF = (15,)                                              # timeframes del FVG de confirmación (minutos)
ZONE_TFS = (15, 5, 3)                                    # timeframes del FVG (no invertido) y del iFVG de la zona común; el iFVG es de un TF igual o menor que el FVG


@dataclass(frozen=True)
class Cfg:
    """Mercado: velas HTF, cierre de sesión y desfase del servidor respecto a Nueva York."""
    htf_min: int = 180                                   # índices H3 (180), forex H4 (240)
    origin: int = 18 * 3600                              # las velas HTF empiezan a esta hora NY (segundos desde las 00:00)
    session_end: int = 18 * 3600                         # a esta hora NY no se abren entradas y lo abierto se cierra
    ahead: int = 7 * 3600                                # servidor = NY + ahead
    unit: float = 1.0                                    # un pip (forex) o un punto (índices), para redondear el límite de profundidad


INDICES = Cfg(180, 18 * 3600, 18 * 3600)
FOREX = Cfg(240, 17 * 3600, 17 * 3600, unit=1e-4)


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
        self.nosetup: list[dict] = []                    # sweeps cuyo patrón no se completó ni se invalidó (la vela C2 acabó antes)
        self.no_entry: list[dict] = []                   # «Setup OK sin entrada»: la zona común existe pero el precio siguió sin tocarla


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


# -- CRT por zona común: FVG de MTF ∩ iFVG de LTF ---------------------------------------------------------------------------
# Corto (el largo es el espejo, ver `view`). Todo dentro de C2:
#   1. C2 supera el máximo de C1 (sweep). Si C2 tomó antes el mínimo de C1, el sweep es el del otro lado.
#   2. Durante la subida quedan un FVG alcista «normal» (M15 o M5, `ZONE_TFS`) y un FVG alcista de LTF (el iFVG: M5, M3 o M1), los dos nacidos
#      dentro de C2, que comparten una zona (se solapan): la zona común. El iFVG tiene que ser de un TF igual o menor que el del FVG (con un FVG de
#      M5 vale M5 o M3, no M15) y no puede ser el mismo hueco. Se busca siempre la combinación del TF mayor posible: si hay varias, manda la del FVG de
#      mayor TF. El iFVG queda invertido cuando el precio cae y cierra bajo su base.
#      CISD = el mínimo de la vela de desplazamiento que lo creó (la vela central del FVG de LTF).
#   3. Con el iFVG ya invertido y los dos FVG formados, el precio vuelve a la zona común (pullback): una vela posterior a la inversión la toca con la
#      mecha sin cerrar al otro lado de ella. Si después del retest (o en él) una vela CIERRA con cuerpo al otro lado de la zona, esa pareja queda invalidada
#      (hay que buscar otra, más abajo): tiene que haber un rebote y luego el cierre sobre el CISD.
#   4. Después de ese toque, la primera vela que cierra con el cuerpo por debajo del CISD da la entrada: a la apertura de la vela siguiente.
# Stop en el máximo del sweep (el máximo de C2 hasta ese momento) y objetivo a `rr` veces el riesgo. Si el precio llega al extremo opuesto de
# C1 sin haberse completado, el setup queda invalidado. Si la zona común existe y el iFVG se invierte pero el precio sigue sin volver a ella, no
# hay entrada: «Setup OK sin entrada» (`Setups.no_entry`). Ver docs/estrategia_crt.
def bullish_fvgs(v: dict, minutes: int) -> dict:
    """FVG alcistas (en el espacio del corto): máximo de la vela 1 por debajo del mínimo de la vela 3. `formed` = cierre de la vela 3."""
    ts, h, l = v["ts"], v["high"], v["low"]
    i = np.arange(2, len(ts))
    ok = (l[i] > h[i - 2]) & (ts[i] - ts[i - 2] <= 2 * minutes * 60 + 3600)
    i = i[ok]
    return {"formed": ts[i] + minutes * 60, "first": ts[i - 2], "bottom": h[i - 2], "top": l[i]}


def find_zone_setups(base: pd.DataFrame, ltf: pd.DataFrame, ltf_min: int, cfg: Cfg, fvg_series: dict | None = None) -> tuple[list, dict]:
    """Todos los setups de zona común de las velas dadas, con el índice de la vela que cierra bajo el CISD (`jc`); la entrada va aparte
    (`entry_point`, variante 1 = apertura de la vela siguiente). `base` da el HTF (y el FVG normal si no se pasan `fvg_series`) y `ltf` las velas del iFVG, del CISD
    y de la entrada (de `ltf_min` minutos). `fvg_series`: {TF en minutos: velas de ese TF} de los FVG normales (TF >= `ltf_min`); sin ella se agrupan desde `base`
    los múltiplos de `ltf_min`."""
    htf = aggregate(base, cfg.htf_min, cfg, cfg.origin)
    mtf = ({m: fvg_series[m] for m in ZONE_TFS if m >= ltf_min and m in fvg_series} if fvg_series is not None
           else {m: aggregate(base, m, cfg) for m in ZONE_TFS if m >= ltf_min and m % ltf_min == 0})
    funnel = {"velas HTF con sweep": 0, "con FVG de MTF y de LTF con zona común": 0, "con pullback a la zona": 0, "con CISD": 0, "invalidados": 0,
              "setup OK sin entrada": 0}
    setups = Setups()
    for sign, name in ((1, "short"), (-1, "long")):
        L, H = view(ltf, sign), view(htf, sign)
        fv = {m: bullish_fvgs(view(mtf[m], sign), m) for m in mtf}                          # el iFVG (LTF) no puede ser de mayor TF que el FVG
        lts, lo_, hi_, cl_ = L["ts"], L["low"], L["high"], L["close"]
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
            ks_all = 2 + a + np.flatnonzero(lo_[a + 2:b] > hi_[a:b - 2])        # velas 3 de los FVG alcistas de LTF nacidos dentro de C2
            zones = [(m, float(f["bottom"][q]), float(f["top"][q]), int(f["formed"][q])) for m, f in fv.items()
                     for q in np.flatnonzero((f["first"] >= s2) & (f["formed"] <= s2 + cfg.htf_min * 60 + 3600))]
            pairs = []                                                          # (k, zona de MTF, zona común) con zona común no vacía
            for k in ks_all:
                for m, zb, zt, formed in zones:
                    if m == ltf_min and formed == int(lts[k]) + m * 60:         # el mismo hueco: el FVG normal y el iFVG tienen que ser dos distintos
                        continue
                    cb, ct = max(float(hi_[k - 2]), zb), min(float(lo_[k]), zt)
                    if cb < ct:
                        pairs.append((int(k), (m, zb, zt, formed), (cb, ct)))
            if not pairs:
                continue
            funnel["con FVG de MTF y de LTF con zona común"] += 1
            pid = lambda p: (p[0], p[1][3], p[1][0])                        # identidad de una pareja: iFVG (vela 3), FVG (cierre y TF)
            hx, ih, touched, inverted, dead, seen_touch, trig, invalidated = float(hi_[s0]), s0, {}, {}, set(), False, None, False
            for j in range(s0, b):
                if lo_[j] < c1l:                                                # llega al extremo opuesto de C1 sin setup: invalidado
                    setups.invalid.append({"sign": sign, "dirección": name, "C2": s2, "ih": ih, "stop": hx,
                                           "motivo": "sin CISD tras el toque" if seen_touch else "sin pullback a la zona común", "c1": (c1l, c1h)})
                    funnel["invalidados"] += 1
                    invalidated = True
                    break
                if hi_[j] > hx:
                    hx, ih = float(hi_[j]), j
                done = [p for p in pairs if pid(p) in touched and pid(p) not in dead and touched[pid(p)] < j and cl_[j] < lo_[p[0] - 1]]     # tocada antes y cierra bajo el CISD
                if done:
                    k, z, common = max(done, key=lambda p: (p[1][0], p[0], p[1][3]))              # la del FVG de mayor TF
                    trig = {"sign": sign, "dirección": name, "C2": s2, "jc": j, "ih": ih, "stop": hx, "level": float(lo_[k - 1]),
                            "z_bottom": common[0], "z_top": common[1], "mtf": f"M{z[0]}", "inside": bool(c1l <= H["close"][i] <= c1h),
                            "c2_end": s2 + cfg.htf_min * 60, "c1": (c1l, c1h), "kf": k, "jt": touched[(k, z[3], z[0])], "inv": inverted[k], "s0": s0,
                            "cisd": (k - 1, float(lo_[k - 1])), "ifvg": (float(hi_[k - 2]), float(lo_[k])), "zones": [z], "common": common}
                    break
                for k, z, common in pairs:
                    key = (k, z[3], z[0])                                       # cada pareja (iFVG, FVG) tiene su propio estado
                    if key in dead:
                        continue
                    if k not in inverted:                                       # el iFVG se invierte: una vela cierra bajo su base
                        if k < j and cl_[j] < hi_[k - 2]:
                            inverted[k] = j
                    elif inverted[k] < j and z[3] <= lts[j] and hi_[j] >= common[0]:        # la vela llega a la zona común, con los dos FVG ya formados
                        if cl_[j] > common[1]:                                  # y cierra con cuerpo al otro lado de ella: el retest la invalida
                            dead.add(key)
                            seen_touch = True
                        elif key not in touched:
                            touched[key] = j                                    # pullback a la zona común: tiene que rebotar y cerrar sobre el CISD
                            seen_touch = True
            funnel["con pullback a la zona"] += seen_touch
            if trig:
                funnel["con CISD"] += 1
                setups.append(trig)
            elif not seen_touch and inverted and (invalidated or lts[-1] + ltf_min * 60 >= s2 + cfg.htf_min * 60):    # invertido y el precio siguió (o C2 acabó) sin el pullback
                k, z, common = max((p for p in pairs if p[0] in inverted), key=lambda p: (p[1][0], p[0], p[1][3]))
                funnel["setup OK sin entrada"] += 1
                setups.no_entry.append({"sign": sign, "dirección": name, "C2": s2, "ih": ih, "stop": hx, "c1": (c1l, c1h), "kf": k, "zones": [z],
                                        "common": common, "ifvg": (float(hi_[k - 2]), float(lo_[k])), "cisd": (k - 1, float(lo_[k - 1])),
                                        "inv": inverted[k], "end": j if invalidated else b - 1})
    setups.sort(key=lambda s: s["jc"] * 10 + (0 if s["sign"] > 0 else 1))
    return setups, funnel


def find_multi_setups(series: dict, cfg: Cfg) -> tuple[list, dict]:
    """Los setups de zona común de todas las combinaciones de timeframes: FVG normal y iFVG de 15, 5 o 3 minutos con TF del FVG >= TF del iFVG. `series` =
    {TF en minutos: velas de ese TF} (las que haya de 3, 5 y 15). Cada combinación se evalúa con las velas del TF del iFVG: la inversión, el CISD, el cierre
    sobre el CISD y la entrada (a la apertura de la vela siguiente de ese TF). Cada setup lleva `ltf` (TF del iFVG, que es el de su CISD y su entrada) y sus
    índices son de las velas de ese TF. Salen en orden de la hora de su cierre sobre el CISD."""
    out, funnel = [], {}
    for i in sorted(t for t in series if t in ZONE_TFS):
        fvg = {m: v for m, v in series.items() if m >= i and m in ZONE_TFS}
        setups, f = find_zone_setups(series[i], series[i], i, cfg, fvg)
        for st in setups:
            st["ltf"] = i
            st["t_cisd"] = int(series[i]["ts"].iloc[st["jc"]])
        out += setups
        for k, v in f.items():
            funnel[k] = funnel.get(k, 0) + v
    out.sort(key=lambda st: (st["t_cisd"], -st["ltf"]))
    return out, funnel


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


# -- CRT-C2: el patrón del usuario (sin iFVG), con sesgo D1 y orden límite ---------------------------------------------------
# Corto (el largo es el espejo): C2 supera el nivel de C1 y marca máximos (un máximo nuevo reinicia el patrón). La vela siguiente al máximo es
# bajista y deja un FVG bajista en LTF; el precio cierra por debajo del nivel de C1 y vuelve a tocar el FVG (vela de retesteo).
#   Tras el retesteo el precio tiene que continuar en la dirección contraria al sweep: si rompe por encima del máximo, el setup se invalida.
#   Entrada 1 (orden en el nivel de C1): se activa al volver el precio al nivel de C1 tras el retesteo.
#   Entrada 2 (a mercado): al cierre de la primera vela que cierra por debajo del mínimo de la vela de retesteo.
# Stop en el máximo del sweep (sin límite de tamaño). Se invalida si la profundidad del sweep (máximo - nivel de C1) supera `cuartos` cuartos
# de la altura de C1, redondeados al entero superior en pips/puntos, o si el precio llega al extremo opuesto de C1 sin completar el patrón.
# Sesgo: solo C2 a favor de la tendencia D1 (cierre sobre/bajo la EMA30 y pendiente de 5 días; corto = bajista).
C2_REASONS = ("sin FVG tras el extremo", "sin cierre dentro de C1", "sin retesteo", "sweep demasiado profundo",
              "rompió el máximo tras el retesteo")
NOSETUP_REASONS = ("sin FVG tras el máximo", "sin cierre dentro de C1", "sin retesteo del FVG", "sin continuación tras el retesteo")


def d1_bias(base: pd.DataFrame, cfg: Cfg) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(horas de las velas D1, tendencia alcista, tendencia bajista) de cada vela D1: cierre sobre/bajo la EMA30 y pendiente de 5 días."""
    d1 = aggregate(base, 1440, cfg, cfg.origin)
    close = d1["close"].to_numpy()
    ema = pd.Series(close).ewm(span=30, adjust=False).mean().to_numpy()
    slope = np.r_[np.full(5, 0.0), ema[5:] - ema[:-5]]
    return d1["ts"].to_numpy(), (close > ema) & (slope > 0), (close < ema) & (slope < 0)


def find_c2_setups(base: pd.DataFrame, ltf: pd.DataFrame, cfg: Cfg, bias: bool = True, cuartos: float = 1.0) -> tuple[list, dict]:
    """Todos los setups CRT-C2 de las velas dadas (`base` M5 para HTF y D1, `ltf` M5 o M3), con la entrada límite y la de mercado de cada uno."""
    htf = aggregate(base, cfg.htf_min, cfg, cfg.origin)
    d1ts, d1_up, d1_down = d1_bias(base, cfg)
    funnel = {"velas HTF con sweep": 0, "contra la tendencia D1": 0, "con FVG tras el extremo": 0, "con cierre dentro de C1": 0,
              "con retesteo": 0, "con entrada límite": 0, "con entrada a mercado": 0, "invalidados": 0}
    setups = Setups()
    for sign, name in ((1, "short"), (-1, "long")):
        L, H = view(ltf, sign), view(htf, sign)
        lts, op_, hi_, lo_, cl_, sp = L["ts"], L["open"], L["high"], L["low"], L["close"], L["spread"]
        spe = sp if sign < 0 else np.zeros_like(sp)              # el largo compra en el ask: el límite exige bajar un spread más
        for i in range(1, len(H["ts"])):
            s2 = int(H["ts"][i])
            if s2 - int(H["ts"][i - 1]) > cfg.htf_min * 60 or H["high"][i] <= H["high"][i - 1]:
                continue
            c1h, c1l = float(H["high"][i - 1]), float(H["low"][i - 1])
            a, b = int(np.searchsorted(lts, s2)), int(np.searchsorted(lts, s2 + cfg.htf_min * 60))
            if b - a < 5:
                continue
            rel = np.flatnonzero(hi_[a:b] > c1h)
            if not len(rel):
                continue
            s0 = a + int(rel[0])
            if s0 > a and lo_[a:s0].min() < c1l:                                # C2 tomó antes el otro extremo de C1: el sweep es el del otro lado
                continue
            funnel["velas HTF con sweep"] += 1
            if bias:
                k = int(np.searchsorted(d1ts, s2, "right")) - 2                # último día D1 completo antes de C2
                if k < 6 or not (d1_down[k] if sign > 0 else d1_up[k]):
                    funnel["contra la tendencia D1"] += 1
                    continue
            limit = math.ceil(cuartos * 0.25 * (c1h - c1l) / cfg.unit - 1e-9) * cfg.unit      # profundidad máxima del sweep
            ext, ih, fvg, below, touch, lim, mkt = -np.inf, s0, None, None, None, None, None
            seen = [False, False, False]                                        # FVG, cierre dentro de C1, retesteo
            deep, opposite, broke = False, False, False
            for j in range(s0, b):
                if lo_[j] < c1l:                                                # llega al extremo opuesto de C1
                    opposite = True
                    break
                if fvg is not None and below is not None and touch is None and j > below and hi_[j] >= fvg[0]:
                    touch = j                                                   # retesteo: el precio vuelve a tocar el FVG
                    seen[2] = True
                if touch is not None and hi_[j] > ext:                          # rompe por encima del máximo tras el retesteo: setup invalidado
                    broke = True
                    break
                if hi_[j] > ext:                                                # máximo nuevo antes del retesteo: se reinicia el patrón
                    ext, ih, fvg, below, touch = float(hi_[j]), j, None, None, None
                    continue
                if fvg is None and j == ih + 2 and op_[ih + 1] > cl_[ih + 1] and lo_[ih] > hi_[j]:
                    fvg = (float(hi_[j]), float(lo_[ih]), j)                    # (base, techo, tercera vela)
                    seen[0] = True
                if fvg is not None and below is None and j > fvg[2] and cl_[j] < c1h:
                    below = j
                    seen[1] = True
                if touch is None or j <= touch:
                    continue
                # tras el retesteo: el precio continúa en la dirección contraria al sweep
                if lim is None and lo_[j] <= c1h + spe[j]:                      # la orden en el nivel de C1 se activa al volver a él (el largo paga el spread)
                    if ext - c1h > limit:
                        deep = True
                    else:
                        lim = {"jl": j, "stop": ext, "ih": ih, "fvg": fvg, "below": below, "touch": touch}
                if mkt is None and j + 1 < b and cl_[j] < lo_[touch]:
                    if ext - c1h > limit:
                        deep = True
                    else:
                        mkt = {"jm": j, "jt": touch, "stop": ext, "ih": ih, "fvg": fvg, "below": below, "level": float(lo_[touch])}
            funnel["con FVG tras el extremo"] += seen[0]
            funnel["con cierre dentro de C1"] += seen[1]
            funnel["con retesteo"] += seen[2]
            funnel["con entrada límite"] += lim is not None
            funnel["con entrada a mercado"] += mkt is not None
            if lim is None and mkt is None:
                if deep or opposite or broke:
                    reason = 3 if deep else 4 if broke else (0 if not seen[0] else 1 if not seen[1] else 2)
                    setups.invalid.append({"sign": sign, "dirección": name, "C2": s2, "ih": ih, "stop": ext if np.isfinite(ext) else float(hi_[s0]), "motivo": C2_REASONS[reason],
                                           "c1": (c1l, c1h)})
                    funnel["invalidados"] += 1
                else:                                                           # la vela C2 acabó sin completar el patrón ni llegar al extremo opuesto
                    stage = 0 if not seen[0] else 1 if not seen[1] else 2 if not seen[2] else 3
                    setups.nosetup.append({"sign": sign, "dirección": name, "C2": s2, "ih": ih, "motivo": NOSETUP_REASONS[stage],
                                           "stop": ext if np.isfinite(ext) else float(hi_[s0])})
                continue
            setups.append({"sign": sign, "dirección": name, "C2": s2, "c1": (c1l, c1h), "s0": s0, "lim": lim, "mkt": mkt,
                           "inside": bool(c1l <= H["close"][i] <= c1h), "c2_end": s2 + cfg.htf_min * 60})
    setups.sort(key=lambda s: (s["lim"] or s["mkt"])["ih"] * 10 + (0 if s["sign"] > 0 else 1))
    return setups, funnel


def c2_view(L: dict, sign: int, mode: int) -> dict:
    """Velas con las que se gestiona la entrada límite (modo 1): son del bid, así que en un corto stop y objetivo (recompra en el ask) se ven en
    bid + spread. El largo (visto en espejo) vende en el bid y no necesita ajuste; su entrada ya exige el spread (ver find_c2_setups)."""
    if mode != 1 or sign < 0:
        return L
    sp = L["spread"]
    return {**L, "high": L["high"] + sp, "low": L["low"] + sp, "close": L["close"] + sp}


def c2_entry(L: dict, st: dict, mode: int, cfg: Cfg) -> dict | None:
    """Entrada del setup CRT-C2 (modo 1: límite en el nivel de C1, 2: a mercado tras el retesteo), en el espacio del corto."""
    sub = st["lim"] if mode == 1 else st["mkt"]
    if sub is None:
        return None
    ts, cl = L["ts"], L["close"]
    if mode == 1:                                                  # la orden espera por debajo del precio: si la vela abre ya más allá del nivel, se llena en la apertura
        j = sub["jl"]
        entry, start, fill = float(min(st["c1"][1], L["open"][j] - (L["spread"][j] if st["sign"] < 0 else 0.0))), j, j
    else:
        entry, start, fill = float(cl[sub["jm"]]), sub["jm"] + 1, None
    risk = sub["stop"] - entry
    if risk <= 0 or start >= len(ts):
        return None
    return {"entry": entry, "start": int(start), "fill": fill, "risk": float(risk), "end": int(session_end(int(ts[start]), cfg)),
            "stop": float(sub["stop"])}
