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
from datetime import datetime, timezone

import numpy as np
import pandas as pd

MTF = (15,)                                              # timeframes del FVG de confirmación (minutos)
ZONE_TFS = (15, 5)                                       # timeframes del FVG (no invertido) y del iFVG de la zona común; el iFVG es de un TF igual o menor que el FVG


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


MAX_SL_INDICES = 125.0                                   # stop máximo (distancia de la entrada al extremo del sweep): en índices, puntos; mayor => no se opera (0 = sin límite)
MAX_SL_FOREX = 25 * 1e-4                                 # en forex, 25 pips (la skill lo cambia con CRT_MAX_SL_INDICES_POINTS / CRT_MAX_SL_FOREX_PIPS)


def max_sl(cfg: Cfg) -> float:
    """El stop máximo del mercado de `cfg` (forex = H4, índices = H3), en unidades de precio; 0 = sin límite."""
    return MAX_SL_FOREX if cfg.htf_min == 240 else MAX_SL_INDICES


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
    return {"formed": ts[i] + minutes * 60, "first": ts[i - 2], "bottom": h[i], "top": l[i - 2]}


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
        self.waiting: list[dict] = []                    # setups completos (BPR, iFVG invertido y retest) a los que solo les falta que una vela cierre más allá del CISD, con C2 en curso
        self.no_entry: list[dict] = []                   # «Setup OK sin entrada»: la zona común existe pero el precio siguió sin tocarla
        self.no_close: list[dict] = []                   # «Setup OK sin cierre»: BPR, iFVG invertido y retest hechos, pero ninguna vela cerró más allá del CISD
        self.contacts: list[tuple] = []                  # (C2, sign, nivel del BPR, hora) del primer contacto con un BPR de cada nivel (0: FVG e iFVG de M15, 1: los dos de M5, 2: FVG de M15 e iFVG de M5)


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
# Corto (el largo es el espejo, ver `view`):
#   1. C2 supera el máximo de C1 (sweep). Si C2 tomó antes el mínimo de C1, el sweep es el del otro lado.
#   2. Quedan un FVG bajista «normal» (M15 o M5, `ZONE_TFS`, nacido dentro de C2) y un FVG alcista de LTF (el iFVG: M15 o M5, nacido dentro de C1 o de C2),
#      que comparten una zona (se solapan): la zona común. El iFVG tiene que ser de un TF igual o menor que el del FVG (con un FVG de
#      M5 vale M5 o M3, no M15) y no puede ser el mismo hueco. Se busca siempre la combinación del TF mayor posible: si hay varias, manda la del FVG de
#      mayor TF. El iFVG queda invertido cuando el precio cae y cierra bajo su base.
#      El primer hueco en nacer es siempre el iFVG, y tiene que seguir activo (sin cerrarse del todo con mecha o cuerpo, ni invertirse) hasta que nace el FVG normal.
#      La zona común es el BPR: es la única zona de retest válida (tocar el FVG sin tocar el BPR no vale). El CISD queda siempre más allá del BPR.
#      CISD = el extremo de la secuencia de velas que genera el iFVG (largo: el máximo de las velas bajistas seguidas que incluyen su vela central; corto: el mínimo).
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


H12_LOOKBACK = 20                                                    # velas de H12 (10 días) cuyo máximo o mínimo puede barrerse
SWING_TF, SWING_LOOKBACK = 240, 60                                   # los swings (pivote clásico de 3 velas) se miran en H4, hasta 60 velas atrás (10 días)


def _stamp(ts: int, ahead: int, day: bool = False) -> str:
    """Fecha (y hora) en Nueva York de una hora de servidor. Con `day`, la del día de la sesión que ese inicio abre (las velas diarias empiezan a las 17:00 / 18:00)."""
    t = datetime.fromtimestamp(ts - ahead + (12 * 3600 if day else 0), timezone.utc)
    return t.strftime("%d/%m" if day else "%d/%m %H:%M")


def sweep_levels(s2: int, hv: dict, dv: dict, tv: dict, sv: dict, ahead: int, names: tuple) -> list[tuple[float, str]]:
    """Niveles que C2 puede barrer además del extremo de C1 (en el espacio del corto: máximos): el máximo del día anterior (PDH), los swings de H4
    (pivote clásico de 3 velas) y el máximo de las velas de H12 de los últimos 10 días. Solo cuentan los que siguen intactos: ninguna vela HTF los superó
    entre su formación y el inicio de C2. `hv`, `dv`, `tv` y `sv`: velas HTF, diarias, H12 y H4 (en el espacio del corto). `names`: cómo se llaman los
    niveles de ese lado (PDH y máx H12 en un corto; PDL y mín H12 en un largo)."""
    out = []

    def intact(level: float, since: int) -> bool:
        a, b = int(np.searchsorted(hv["ts"], since)), int(np.searchsorted(hv["ts"], s2))
        return a >= b or float(hv["high"][a:b].max()) < level

    j = int(np.searchsorted(dv["ts"] + 1440 * 60, s2, side="right")) - 1            # el último día cerrado
    if j >= 0 and intact(float(dv["high"][j]), int(dv["ts"][j]) + 1440 * 60):
        out.append((float(dv["high"][j]), f"{names[0]} día {_stamp(int(dv['ts'][j]), ahead, True)}"))
    j = int(np.searchsorted(sv["ts"] + SWING_TF * 60, s2, side="right")) - 1        # la última vela de H4 cerrada
    for q in range(max(1, j - SWING_LOOKBACK), j):                                  # pivote en q: confirmado por la vela q + 1 (cerrada)
        hq = float(sv["high"][q])
        if hq > sv["high"][q - 1] and hq > sv["high"][q + 1] and intact(hq, int(sv["ts"][q + 1]) + SWING_TF * 60):
            out.append((hq, f"swing H4 {_stamp(int(sv['ts'][q]), ahead)}"))
    j = int(np.searchsorted(tv["ts"] + 720 * 60, s2, side="right")) - 1             # las velas de H12 cerradas de los últimos 10 días
    for q in range(max(0, j - H12_LOOKBACK), j + 1):
        if intact(float(tv["high"][q]), int(tv["ts"][q]) + 720 * 60):
            out.append((float(tv["high"][q]), f"{names[1]} H12 {_stamp(int(tv['ts'][q]), ahead)}"))
    return out


def find_zone_setups(base: pd.DataFrame, ltf: pd.DataFrame, ltf_min: int, cfg: Cfg, fvg_series: dict | None = None, hist: pd.DataFrame | None = None,
                     retest: bool = True) -> tuple[list, dict]:
    """Todos los setups de zona común de las velas dadas, con el índice de la vela que cierra bajo el CISD (`jc`); la entrada va aparte
    (`entry_point`, variante 1 = apertura de la vela siguiente). `base` da el HTF (y el FVG normal si no se pasan `fvg_series`) y `ltf` las velas del iFVG, del CISD
    y de la entrada (de `ltf_min` minutos). `fvg_series`: {TF en minutos: velas de ese TF} de los FVG normales (TF >= `ltf_min`); sin ella se agrupan desde `base`
    los múltiplos de `ltf_min`. `hist`: velas de largo recorrido (de un TF corto) de las que salen los niveles que C2 puede barrer (PDH/PDL, swings de
    H4, H12); sin ellas se usan las de `base`. `retest=False` (experimento): el BPR no necesita retest, vale la vela que cierra más allá del CISD una vez invertido el iFVG."""
    htf = aggregate(base, cfg.htf_min, cfg, cfg.origin)
    src = base if hist is None else hist
    big = {"h": aggregate(src, cfg.htf_min, cfg, cfg.origin), "d": aggregate(src, 1440, cfg, cfg.origin), "t": aggregate(src, 720, cfg, cfg.origin),
           "s": aggregate(src, SWING_TF, cfg, cfg.origin)}
    mtf = ({m: fvg_series[m] for m in ZONE_TFS if m >= ltf_min and m in fvg_series} if fvg_series is not None
           else {m: aggregate(base, m, cfg) for m in ZONE_TFS if m >= ltf_min and m % ltf_min == 0})
    funnel = {"velas HTF con sweep": 0, "con FVG de MTF y de LTF con zona común": 0, "con pullback a la zona": 0, "con CISD": 0, "invalidados": 0,
              "setup OK sin entrada": 0}
    setups = Setups()
    for sign, name in ((1, "short"), (-1, "long")):
        L, H = view(ltf, sign), view(htf, sign)
        bv = {k: view(v, sign) for k, v in big.items()}
        names = ("PDH", "máx") if sign > 0 else ("PDL", "mín")
        fv = {m: bearish_fvgs(view(mtf[m], sign), m) for m in mtf}                          # el FVG normal es de sentido contrario al iFVG (un largo: iFVG bajista que se invierte, FVG alcista); el iFVG no puede ser de mayor TF que el FVG
        lts, lo_, hi_, cl_, op_ = L["ts"], L["low"], L["high"], L["close"], L["open"]
        cisd_cache: dict = {}

        def cisd_of(k: int) -> tuple[int, float]:
            """CISD del iFVG cuya 3.ª vela es `k`: el extremo de la secuencia de velas (en el corto, alcistas) que genera el iFVG, que incluye a su vela central; se
            amplía hacia atrás y hacia delante mientras las velas sigan en la misma dirección (3, 4, 5 o más). Se mira en las velas del TF del iFVG, que es el TF
            menor de los dos huecos y donde se valida el BPR. Devuelve (índice de la primera vela de la secuencia, extremo)."""
            if k not in cisd_cache:
                a_, b_ = k - 1, k - 1
                while a_ - 1 >= 0 and cl_[a_ - 1] > op_[a_ - 1] and lts[a_] - lts[a_ - 1] <= ltf_min * 60 + 3600:
                    a_ -= 1
                while b_ + 1 < len(lts) and cl_[b_ + 1] > op_[b_ + 1] and lts[b_ + 1] - lts[b_] <= ltf_min * 60 + 3600:
                    b_ += 1                                                                  # la secuencia puede ser de 3, 4, 5 o más velas del mismo color
                cisd_cache[k] = (a_, float(lo_[a_:b_ + 1].min()))
            return cisd_cache[k]

        def closes_beyond_cisd(p: tuple, j: int, after: int) -> bool:
            """La vela `j` (del TF del iFVG, el menor de los dos) es la del retest `after` o posterior a ella y cierra con cuerpo más allá del CISD de la pareja `p`."""
            return j >= after and float(cl_[j]) < cisd_of(p[0])[1]

        for i in range(1, len(H["ts"])):
            s2 = int(H["ts"][i])
            if s2 - int(H["ts"][i - 1]) > cfg.htf_min * 60:
                continue
            c1h, c1l = H["high"][i - 1], H["low"][i - 1]
            a, b = int(np.searchsorted(lts, s2)), int(np.searchsorted(lts, s2 + cfg.htf_min * 60))
            if b - a < 4:
                continue
            top = float(hi_[a:b].max())
            cands = [(float(c1h), "vela C1")]                                    # lo que C2 puede barrer: el máximo de C1 o un nivel anterior (PDH, swing de H4, H12)
            cands += [(p, n) for p, n in sweep_levels(s2, bv["h"], bv["d"], bv["t"], bv["s"], cfg.ahead, names) if p < top]
            broke = [(p, n) for p, n in cands if top > p]
            if not broke:
                continue
            swept_level = min(broke, key=lambda x: x[0])[0]                        # el más bajo: el primero que barre el precio (arranca el patrón)
            swept_name = max(broke, key=lambda x: x[0])[1]                         # la etiqueta, la del nivel más profundo que barre C2 (vela C1, PDH/PDL, swing de H4, H12)
            rel = np.flatnonzero(hi_[a:b] > swept_level)
            s0 = a + int(rel[0])
            if s0 > a and lo_[a:s0].min() < c1l:                                # C2 tomó antes el otro extremo de C1: el sweep es el del otro lado
                continue
            funnel["velas HTF con sweep"] += 1
            a1 = int(np.searchsorted(lts, int(H["ts"][i - 1])))
            ks_all = 2 + a1 + np.flatnonzero((lo_[a1 + 2:b] > hi_[a1:b - 2]) & (lts[a1 + 2:b] - lts[a1:b - 2] <= 2 * ltf_min * 60))     # velas 3 de los FVG alcistas de LTF (los iFVG) nacidos dentro de C1 o de C2, de tres velas seguidas (sin el corte de la sesión en medio)
            zones = [(m, float(f["bottom"][q]), float(f["top"][q]), int(f["formed"][q])) for m, f in fv.items()
                     for q in np.flatnonzero((f["first"] >= s2) & (f["formed"] <= s2 + cfg.htf_min * 60 + 3600))]
            pairs = []                                                          # (k, zona de MTF, zona común) con zona común no vacía
            for k in ks_all:
                for m, zb, zt, formed in zones:
                    if int(lts[k]) + ltf_min * 60 > formed:                     # el primer hueco siempre es el iFVG: el FVG normal se forma después de él
                        continue
                    f_mid = int(np.searchsorted(lts, formed - 2 * m * 60))      # vela de desplazamiento del FVG (la central): ahí puede cerrarse y a la vez invertirse el iFVG
                    if k + 1 < f_mid and lo_[k + 1:f_mid].min() <= hi_[k - 2]:   # el iFVG tiene que seguir activo (sin cerrarse del todo, con mecha o cuerpo) hasta que nace el FVG
                        continue
                    f_end = int(np.searchsorted(lts, formed - m * 60))            # fin de la vela de desplazamiento del FVG (la central)
                    wick = False
                    for q in range(max(f_mid, k + 1), f_end):                   # desde la vela de desplazamiento del FVG hasta que nace: puede cerrar y invertir el iFVG, pero no mitigarlo solo con mecha
                        if cl_[q] < hi_[k - 2]:
                            break
                        if lo_[q] <= hi_[k - 2]:
                            wick = True
                            break
                    if wick:
                        continue
                    cb, ct = max(float(hi_[k - 2]), zb), min(float(lo_[k]), zt)
                    if cb < ct and cisd_of(k)[1] < cb:                          # BPR (zona común) no vacío y con el CISD más allá de él (largo: un máximo por encima del BPR)
                        pairs.append((int(k), (m, zb, zt, formed), (cb, ct)))
            if not pairs:                                                       # barre C1 pero no se forma ningún BPR: sweep sin setup
                setups.nosetup.append({"sign": sign, "dirección": name, "C2": s2, "ih": a + int(np.argmax(hi_[a:b])), "stop": top,
                                       "motivo": "sin BPR (iFVG y FVG de sentido contrario)"})
                continue
            funnel["con FVG de MTF y de LTF con zona común"] += 1
            pid = lambda p: (p[0], p[1][3], p[1][0])                        # identidad de una pareja: iFVG (vela 3), FVG (cierre y TF)
            hx, ih, touched, inverted, dead, seen_touch, trig, invalidated = float(hi_[s0]), s0, {}, {}, set(), False, None, False
            contact: dict = {}                                              # primer contacto (vela) de cada pareja con su BPR
            lvl = lambda p: 0 if ltf_min == 15 else (1 if p[1][0] == 5 else 2)   # orden de búsqueda: los dos huecos de M15, si no los dos de M5 y solo después FVG de M15 con iFVG de M5
            for j in range(s0, b):
                if lo_[j] < c1l:                                                # llega al extremo opuesto de C1 sin setup: invalidado
                    setups.invalid.append({"sign": sign, "dirección": name, "C2": s2, "ih": ih, "stop": hx,
                                           "motivo": "sin CISD tras el toque" if seen_touch else "sin pullback a la zona común", "c1": (c1l, c1h), "sweep": swept_name})
                    funnel["invalidados"] += 1
                    invalidated = True
                    break
                if hi_[j] > hx:
                    hx, ih = float(hi_[j]), j
                for k, z, common in pairs:
                    key = (k, z[3], z[0])                                       # cada pareja (iFVG, FVG) tiene su propio estado
                    if key in dead:
                        continue
                    if k not in inverted:                                       # el iFVG se invierte: una vela cierra bajo su base
                        if k < j and cl_[j] < hi_[k - 2]:
                            inverted[k] = j
                    if not retest:                                              # sin retest: con el iFVG invertido y los dos FVG formados, la pareja ya vale
                        if k in inverted and z[3] <= lts[j] and key not in touched:
                            contact.setdefault(key, j)
                            touched[key] = j
                            seen_touch = True
                    elif k in inverted and inverted[k] < j and z[3] <= lts[j] and hi_[j] >= common[0]:        # la vela llega a la zona común, con los dos FVG ya formados
                        contact.setdefault(key, j)
                        if cl_[j] > common[1]:                                  # y cierra con cuerpo al otro lado de ella: el retest la invalida
                            dead.add(key)
                            seen_touch = True
                        elif key not in touched:
                            touched[key] = j                                    # pullback a la zona común: tiene que rebotar y cerrar sobre el CISD
                            seen_touch = True
                done = [p for p in pairs if pid(p) in touched and pid(p) not in dead and touched[pid(p)] <= j and closes_beyond_cisd(p, j, touched[pid(p)])     # tocada (en esa misma vela o antes) y una vela del TF menor cierra bajo el CISD
                        and not any(lvl(q) < lvl(p) and contact.get(pid(q), j + 1) <= j for q in pairs)]                                       # y ningún BPR de un nivel anterior tuvo ya su retest: ese es el válido
                if done:
                    k, z, common = max(done, key=lambda p: (-p[1][0], p[0], p[1][3]))             # a igual hora, la del FVG de menor TF (con el iFVG de M5: antes la de M5 que la mixta)
                    trig = {"sign": sign, "dirección": name, "C2": s2, "jc": j, "ih": ih, "stop": hx, "level": cisd_of(k)[1],
                            "z_bottom": common[0], "z_top": common[1], "mtf": f"M{z[0]}", "inside": bool(c1l <= H["close"][i] <= c1h),
                            "c2_end": s2 + cfg.htf_min * 60, "c1": (c1l, c1h), "sweep": swept_name, "sweep_level": float(swept_level), "kf": k, "jt": touched[(k, z[3], z[0])], "inv": inverted[k], "s0": s0,
                            "cisd": cisd_of(k), "ifvg": (float(hi_[k - 2]), float(lo_[k])), "zones": [z], "common": common}
                    break
            for lv in {lvl(p) for p in pairs}:
                hits = [contact[pid(p)] for p in pairs if lvl(p) == lv and pid(p) in contact]
                if hits:
                    setups.contacts.append((s2, sign, lv, int(lts[min(hits)])))
            funnel["con pullback a la zona"] += seen_touch
            if not trig and not invalidated and b >= len(lts) and lts[-1] + ltf_min * 60 < s2 + cfg.htf_min * 60:   # C2 sigue en curso: ¿solo falta el cierre más allá del CISD?
                wait = [p for p in pairs if pid(p) in touched and pid(p) not in dead
                        and not any(lvl(q) < lvl(p) and contact.get(pid(q), b) < b for q in pairs)]                # (mismo criterio de nivel que el cierre válido)
                if wait:
                    k, z, common = max(wait, key=lambda p: (-p[1][0], p[0], p[1][3]))
                    setups.waiting.append({"sign": sign, "dirección": name, "C2": s2, "ltf": ltf_min, "mtf": f"M{z[0]}", "stop": hx, "level": cisd_of(k)[1],
                                           "z_bottom": common[0], "z_top": common[1], "t_touch": int(lts[touched[(k, z[3], z[0])]]), "c1": (c1l, c1h),
                                           "sweep": swept_name})
            if not trig and touched and (invalidated or dead or lts[-1] + ltf_min * 60 >= s2 + cfg.htf_min * 60):    # con retest y sin cierre sobre el CISD: ya no puede darse (C2 acabó, retest invalidado o llegó al otro extremo de C1)
                lost = [p for p in pairs if pid(p) in touched and not any(lvl(q) < lvl(p) and contact.get(pid(q), b) < b for q in pairs)]
                if lost:
                    k, z, common = max(lost, key=lambda p: (-p[1][0], p[0], p[1][3]))
                    setups.no_close.append({"sign": sign, "dirección": name, "C2": s2, "ih": ih, "stop": hx, "c1": (c1l, c1h), "sweep": swept_name, "sweep_level": float(swept_level),
                                            "kf": k, "zones": [z], "common": common, "ifvg": (float(hi_[k - 2]), float(lo_[k])), "cisd": cisd_of(k), "inv": inverted[k],
                                            "jt": touched[(k, z[3], z[0])], "end": j if invalidated else b - 1})
            if trig:
                funnel["con CISD"] += 1
                setups.append(trig)
            elif (live := [p for p in pairs if p[0] in inverted and pid(p) not in dead and pid(p) not in touched])                     and (invalidated or lts[-1] + ltf_min * 60 >= s2 + cfg.htf_min * 60):    # una pareja viva con el iFVG invertido, sin retest, y C2 acabó (o el precio siguió)
                k, z, common = max(live, key=lambda p: (-p[1][0], p[0], p[1][3]))
                funnel["setup OK sin entrada"] += 1
                setups.no_entry.append({"sign": sign, "dirección": name, "C2": s2, "ih": ih, "stop": hx, "c1": (c1l, c1h), "sweep": swept_name, "sweep_level": float(swept_level), "kf": k, "zones": [z],
                                        "common": common, "ifvg": (float(hi_[k - 2]), float(lo_[k])), "cisd": cisd_of(k),
                                        "inv": inverted[k], "end": j if invalidated else b - 1})
            elif not invalidated:                                               # pareja(s) formadas pero ninguna llegó a entrada ni a «setup OK»
                setups.nosetup.append({"sign": sign, "dirección": name, "C2": s2, "ih": ih, "stop": hx,
                                       "motivo": "BPR sin retest válido y cierre sobre el CISD" if seen_touch else "BPR sin invertirse el iFVG"})
    setups.sort(key=lambda s: s["jc"] * 10 + (0 if s["sign"] > 0 else 1))
    return setups, funnel


def m15_retests(series15: pd.DataFrame, cfg: Cfg, hist: pd.DataFrame | None = None) -> dict:
    """(C2, sign) -> hora del primer retest de un BPR de M15 (iFVG y FVG de M15). Si ese BPR ya tuvo su retest, es el válido y no se sustituye por uno de M5."""
    contacts = find_zone_setups(series15, series15, 15, cfg, {15: series15}, hist)[0].contacts
    return {(c2, sign): t for c2, sign, lv, t in contacts if lv == 0}


def find_multi_setups(series: dict, cfg: Cfg, hist: pd.DataFrame | None = None) -> tuple[list, dict]:
    """Los setups de BPR de todas las combinaciones de timeframes: iFVG y FVG normal (de sentido contrario) los dos de 15 min, los dos de 5 o FVG de 15 con iFVG
    de 5. `series` = {TF en minutos: velas de ese TF} (las que haya de 5 y 15). Cada combinación se evalúa con las velas del TF del iFVG (el menor de los dos):
    la inversión, el retest, el CISD, el cierre sobre el CISD y la entrada (a la apertura de la vela siguiente de ese TF). Si el BPR de M15 de una C2 ya tuvo su
    retest, los setups de M5 de esa C2 y lado posteriores a él se descartan. Cada setup lleva `ltf` (TF del iFVG) y sus índices son de las velas de ese TF.
    Salen en orden de la hora de su cierre sobre el CISD."""
    out, funnel, first15 = Setups(), {}, {}
    for i in sorted((t for t in series if t in ZONE_TFS), reverse=True):                    # primero M15: si su BPR ya tuvo el retest, no se sustituye por uno de M5
        fvg = {m: v for m, v in series.items() if m >= i and m in ZONE_TFS}
        setups, f = find_zone_setups(series[i], series[i], i, cfg, fvg, hist)
        for c2, sign, lv, t in setups.contacts:
            if lv == 0:
                first15[(c2, sign)] = min(t, first15.get((c2, sign), t))
        for st in setups:
            st["ltf"] = i
            st["t_cisd"] = int(series[i]["ts"].iloc[st["jc"]])
            if i == 15 or st["t_cisd"] < first15.get((st["C2"], st["sign"]), st["t_cisd"] + 1):
                out.append(st)
        out.waiting += [w for w in setups.waiting if i == 15 or w["t_touch"] < first15.get((w["C2"], w["sign"]), w["t_touch"] + 1)]
        out.no_close += [dict(w, ltf=i) for w in setups.no_close if i == 15 or int(series[i]["ts"].iloc[w["jt"]]) < first15.get((w["C2"], w["sign"]), 1 << 62)]
        for k, v in f.items():
            funnel[k] = funnel.get(k, 0) + v
    out.sort(key=lambda st: (st["t_cisd"], -st["ltf"]))
    return out, funnel


# -- entradas y gestión --------------------------------------------------------------------------------------------------

def entry_point(L: dict, st: dict, variant: int, ltf_min: int, rule: Rule, cfg: Cfg, closed: int | None = None, ignore_sl: bool = False) -> dict | None:
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
    limit_sl = 0 if ignore_sl else max_sl(cfg)
    if limit_sl and risk > limit_sl + 1e-9:               # el stop es demasiado grande (forex > 25 pips, índices > 125 puntos): la entrada se cancela
        return None
    return {"entry": float(entry), "start": int(start), "fill": fill, "risk": float(risk), "end": int(end)}


def sl_blocked(L: dict, st: dict, variant: int, ltf_min: int, rule: Rule, cfg: Cfg, closed: int | None = None) -> float | None:
    """Si el setup habría dado entrada de no ser por el límite del stop (`max_sl`), el riesgo de esa entrada (distancia al extremo del sweep); si no, None."""
    if entry_point(L, st, variant, ltf_min, rule, cfg, closed) is not None:
        return None
    ep = entry_point(L, st, variant, ltf_min, rule, cfg, closed, ignore_sl=True)
    return None if ep is None else float(ep["risk"])


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
