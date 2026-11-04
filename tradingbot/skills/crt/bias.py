"""Sesgo del perfil CRT: zonas de reversión en HTF (1h, 4h o 1d) que dan puntos a un setup. Independiente del sesgo de los demás perfiles.

Para un setup largo cuentan las zonas de SOPORTE y para uno corto las de RESISTENCIA, nacidas antes de la vela C2 del setup (la del patrón de doble FVG +
CISD) y como mucho `lookback_days` días antes de su hora de creación. La validación es **por regla y de mayor a menor timeframe** (1d, 4h, 1h): en
cuanto una regla se cumple en un TF, ese TF le da su **punto** y no se mira en los menores. Con `puntos >= min_score` el setup es GO:
  1. FVG en HTF a la izquierda del precio (hueco entre la vela 1 y la 3), con el CRT formándose dentro de esa zona.
  2. Rejection block: la zona que define la mecha de un swing de 1 vela a cada lado (configurable) cuya mecha ocupa más del 50 % de su vela (configurable)
     (largo: del mínimo al borde inferior del cuerpo del swing low).
  3. Order block (OB): la última vela contraria antes de un impulso que deja un FVG (largo: la vela bajista, la alcista siguiente y un FVG alcista entre el
     máximo de la bajista y el mínimo de la vela posterior; sin FVG no hay OB). La zona es el rango completo de la vela.
«Dentro» = la zona común del CRT (BPR) se solapa con la zona HTF, que tiene que estar a favor (largo: FVG alcista, soporte) y sin mitigar
(ninguna vela volvió a entrar en ella entre su creación y la C2). Desactivado (`CRT_BIAS_ENABLED=false`) el sesgo es 0 y el setup es siempre GO; encendido
pero sin `CRT_BIAS_ENFORCE` se calcula y se enseña en la tarjeta y la orden, y no anula ningún trade.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from ..bias.models import Bias, BiasResult, RuleVote
from . import engine

RULES = (("fvg", "FVG en HTF"), ("rejection", "Rejection block en HTF"), ("ob", "Order Block en HTF"))
TF_MINUTES = {"1h": 60, "4h": 240, "1d": 1440}


@dataclass(frozen=True)
class CrtBiasCfg:
    enabled: bool = False                                        # CRT_BIAS_ENABLED: apagado, el sesgo es 0 y todo es GO
    enforce: bool = False                                        # CRT_BIAS_ENFORCE: con el sesgo encendido, un setup sin puntos suficientes es NO GO; apagado solo se calcula y se enseña
    lookback_days: float = 10.0                                  # CRT_BIAS_LOOKBACK_DAYS: antigüedad máxima de una zona respecto a la C2 del setup
    min_score: float = 1.0                                       # CRT_BIAS_MIN_SCORE: puntos para dar GO
    tfs: tuple[str, ...] = ("1h", "4h", "1d")                    # CRT_BIAS_TFS
    swing_width: int = 1                                         # CRT_BIAS_SWING_WIDTH: velas a cada lado que tiene que superar un swing (rejection block)
    rb_min_wick_pct: float = 50.0                                # CRT_BIAS_RB_MIN_WICK_PCT: la mecha del swing, más del x % del tamaño de su vela


def parse_tfs(values: list[str]) -> tuple[str, ...]:
    tfs = tuple(v.strip().lower() for v in values if v.strip())
    bad = [v for v in tfs if v not in TF_MINUTES]
    if bad:
        raise ValueError(f"CRT_BIAS_TFS: {', '.join(bad)} no vale; usa {', '.join(TF_MINUTES)}")
    return tfs


def load_cfg(settings) -> CrtBiasCfg:
    """Lee el bloque CRT_BIAS_* de tradingbot.env (`settings` = self.settings de la skill, con el prefijo CRT_)."""
    days = settings.get_float("BIAS_LOOKBACK_DAYS", 10.0)
    score = settings.get_float("BIAS_MIN_SCORE", 1.0)
    if days <= 0:
        raise ValueError("CRT_BIAS_LOOKBACK_DAYS debe ser mayor que 0")
    if score < 0:
        raise ValueError("CRT_BIAS_MIN_SCORE no puede ser negativo")
    width, wick = settings.get_int("BIAS_SWING_WIDTH", 1), settings.get_float("BIAS_RB_MIN_WICK_PCT", 50.0)
    if width < 1:
        raise ValueError("CRT_BIAS_SWING_WIDTH debe ser 1 o más")
    if not 0 <= wick < 100:
        raise ValueError("CRT_BIAS_RB_MIN_WICK_PCT debe estar entre 0 y 100")
    return CrtBiasCfg(settings.get_bool("BIAS_ENABLED", False), settings.get_bool("BIAS_ENFORCE", False), days, score,
                      parse_tfs(settings.get_list("BIAS_TFS", list(CrtBiasCfg.tfs))), width, wick)


def htf_candles(df: pd.DataFrame, minutes: int, cfg: engine.Cfg) -> pd.DataFrame:
    """Velas de `minutes` minutos (1h alineadas a la hora; 4h y 1d a la hora de inicio del día de trading del mercado)."""
    origin = 0 if minutes == 60 else cfg.origin
    return engine.aggregate(df, minutes, cfg, origin)


def zones(df: pd.DataFrame, direction: str, cfg: engine.Cfg, tfs=("1h", "4h", "1d"), swing_width: int = 1, min_wick: float = 0.5, horizon_days: float = 10.0) -> list[dict]:
    """Zonas de reversión de las velas de `df` a favor de `direction` ("long": soporte; "short": resistencia), con su hora de creación (cierre de la
    vela que la completa): {rule, tf, bottom, top, created, candle}. `swing_width`: velas a cada lado de un swing; `min_wick`: fracción mínima del tamaño
    de la vela que tiene que ocupar la mecha de un rejection block. Cada zona lleva `dead`: la hora de la primera vela de `df` que la mitiga (el precio entra en ella
    después de crearse: largo, un mínimo por debajo de su techo; corto, un máximo por encima de su base) en los `horizon_days` siguientes, o None."""
    long = direction == "long"
    out = []
    for name in tfs:
        m = TF_MINUTES[name]
        c = htf_candles(df, m, cfg)
        if len(c) < 3:
            continue
        ts, o, h, l, cl = (c[k].to_numpy() for k in ("ts", "open", "high", "low", "close"))
        ts = ts.astype(np.int64)
        step, n = m * 60, len(c)
        for i in range(2, n):                                                               # 1. FVG
            if ts[i] - ts[i - 2] > 2 * step + 3600:
                continue
            if long and h[i - 2] < l[i]:
                out.append({"rule": "fvg", "tf": name, "bottom": float(h[i - 2]), "top": float(l[i]), "created": int(ts[i]) + step, "candle": int(ts[i - 2])})
            elif not long and l[i - 2] > h[i]:
                out.append({"rule": "fvg", "tf": name, "bottom": float(h[i]), "top": float(l[i - 2]), "created": int(ts[i]) + step, "candle": int(ts[i - 2])})
        w = swing_width
        for j in range(w, n - w):                                                           # 2. rejection block
            near = slice(j - w, j + w + 1)
            size = h[j] - l[j]
            if size <= 0:
                continue
            if long and l[j] <= l[near].min() and (min(o[j], cl[j]) - l[j]) / size > min_wick:
                out.append({"rule": "rejection", "tf": name, "bottom": float(l[j]), "top": float(min(o[j], cl[j])), "created": int(ts[j + w]) + step, "candle": int(ts[j])})
            elif not long and h[j] >= h[near].max() and (h[j] - max(o[j], cl[j])) / size > min_wick:
                out.append({"rule": "rejection", "tf": name, "bottom": float(max(o[j], cl[j])), "top": float(h[j]), "created": int(ts[j + w]) + step, "candle": int(ts[j])})
        for j in range(n - 2):                                                              # 3. order block: la vela contraria y un impulso que deja un FVG
            if ts[j + 2] - ts[j] > 2 * step + 3600:
                continue
            if long and cl[j] < o[j] and cl[j + 1] > o[j + 1] and h[j] < l[j + 2]:
                out.append({"rule": "ob", "tf": name, "bottom": float(l[j]), "top": float(h[j]), "created": int(ts[j + 2]) + step, "candle": int(ts[j])})
            elif not long and cl[j] > o[j] and cl[j + 1] < o[j + 1] and l[j] > h[j + 2]:
                out.append({"rule": "ob", "tf": name, "bottom": float(l[j]), "top": float(h[j]), "created": int(ts[j + 2]) + step, "candle": int(ts[j])})
    dts, dlow, dhigh = (df[k].to_numpy() for k in ("ts", "low", "high"))
    dts = dts.astype(np.int64)
    for z in out:                                                                           # una zona mitigada (el precio ya volvió a entrar en ella) ya no vale
        a, b = np.searchsorted(dts, [z["created"], z["created"] + int(horizon_days * 86400)])
        hit = np.flatnonzero(dlow[a:b] <= z["top"]) if long else np.flatnonzero(dhigh[a:b] >= z["bottom"])
        z["dead"] = int(dts[a + hit[0]]) if len(hit) else None
    return out


def zone_text(z: dict, ahead: int = 0) -> str:
    """La zona HTF que da un punto: su TF, la vela que la define (hora NY de su primera vela) y su rango."""
    when = datetime.fromtimestamp(int(z["candle"]) - ahead, timezone.utc)
    return f"{z['tf']} · vela {when:%d/%m %H:%M} NY · {z['bottom']:.5g}-{z['top']:.5g}"


@dataclass
class SetupBias:
    """Puntos de un setup: las zonas que cuentan (una por punto) y el resultado para la tarjeta del sesgo."""
    enabled: bool
    direction: str
    min_score: float
    enforce: bool = True                                         # False: se calcula y se enseña pero no anula el trade
    zones: list[dict] = field(default_factory=list)
    when: datetime | None = None
    ahead: int = 0                                               # servidor - Nueva York (s): para dar la hora de la vela de cada zona

    @property
    def score(self) -> float:
        return float(len(self.zones)) if self.enabled else 0.0

    @property
    def go(self) -> bool:
        return (not self.enabled) or (not self.enforce) or self.score >= self.min_score

    def counts(self) -> dict[str, int]:
        return {key: sum(z["rule"] == key for z in self.zones) for key, _ in RULES}

    def summary(self) -> str:
        if not self.enabled:
            return "Sesgo CRT deshabilitado (CRT_BIAS_ENABLED=false): sesgo 0, el setup es siempre GO"
        side = "soporte" if self.direction == "long" else "resistencia"
        info = "" if self.enforce else " · informativo (CRT_BIAS_ENFORCE=false): no anula el trade"
        if not self.zones:
            return f"Sin zonas HTF de {side} para el setup {self.direction}: 0 puntos (hacen falta {self.min_score:g}){info}"
        listed = "; ".join(f"{dict(RULES)[z['rule']]} {z['tf']} {z['bottom']:.5g}-{z['top']:.5g}" for z in self.zones)
        return f"{len(self.zones)} regla(s) validada(s) con zonas HTF de {side}, un punto cada una (hacen falta {self.min_score:g}): {listed}{info}"

    def result(self) -> BiasResult:
        """El sesgo del setup para la tarjeta: Bullish (largo) o Bearish (corto) si llega a los puntos; si no, No Bias."""
        sign = 1 if self.direction == "long" else -1
        counts = self.counts()
        votes = tuple(RuleVote(title, sign if counts[key] and self.enabled else 0,
                               "deshabilitada" if not self.enabled else
                               "; ".join(zone_text(z, self.ahead) for z in self.zones if z["rule"] == key) or "sin zona",
                               float(counts[key]) if counts[key] and self.enabled else 1.0,
                               tuple(z for z in self.zones if z["rule"] == key) if self.enabled else ()) for key, title in RULES)
        if self.enabled and self.score >= self.min_score:
            bias = Bias.BULLISH if sign > 0 else Bias.BEARISH
        else:
            bias = Bias.NO_BIAS
        day = self.when.date() if self.when else None
        return BiasResult(bias, day, votes, {}, self.summary(), sign * self.score, max(self.min_score, 1e-9))


def zone_cache(df: pd.DataFrame, cfg: engine.Cfg, bias_cfg: CrtBiasCfg) -> dict:
    """Las zonas HTF de todo el histórico de `df`, por (dirección, TF), para evaluar muchos setups sin recalcularlas (backtest): una zona solo usa velas
    cerradas hasta su hora de creación, así que filtrarlas por `created` da lo mismo que calcularlas con el histórico anterior a cada setup."""
    return {(d, tf): zones(df, d, cfg, (tf,), bias_cfg.swing_width, bias_cfg.rb_min_wick_pct / 100, bias_cfg.lookback_days) for d in ("long", "short") for tf in bias_cfg.tfs}


def evaluate(df: pd.DataFrame, direction: str, c2_start: int, common: tuple[float, float], cfg: engine.Cfg, bias_cfg: CrtBiasCfg,
             ahead: int = 0, cache: dict | None = None) -> SetupBias:
    """Los puntos de un setup: para cada regla, la primera zona a favor que se cumple yendo del TF mayor al menor (1d, 4h, 1h): creada antes de la C2
    (hora de servidor `c2_start`), como mucho `lookback_days` antes, y solapada con la zona común `common` (mínimo, máximo) del CRT. Una regla da como
    mucho un punto, el del TF mayor en que se cumple; en cuanto se cumple no se sigue con los TF menores. `cache` (`zone_cache`): zonas ya calculadas."""
    when = datetime.fromtimestamp(c2_start - ahead, timezone.utc)
    if not bias_cfg.enabled:
        return SetupBias(False, direction, bias_cfg.min_score, bias_cfg.enforce, [], when, ahead)
    lo, hi = min(common), max(common)
    first = c2_start - int(bias_cfg.lookback_days * 86400)
    history = df[df["ts"] < c2_start] if cache is None else None
    pending = [key for key, _ in RULES]
    found = []
    for tf in sorted(bias_cfg.tfs, key=lambda t: TF_MINUTES[t], reverse=True):               # del mayor al menor
        if not pending:
            break                                                                              # todas las reglas ya tienen su punto
        every = cache[(direction, tf)] if cache is not None else zones(history, direction, cfg, (tf,), bias_cfg.swing_width, bias_cfg.rb_min_wick_pct / 100, bias_cfg.lookback_days)
        ok = [z for z in every
              if z["rule"] in pending and first <= z["created"] <= c2_start and z["bottom"] <= hi and z["top"] >= lo
              and (z.get("dead") is None or z["dead"] >= c2_start)]                                  # sin mitigar antes de la C2
        for key in list(pending):
            hits = sorted((z for z in ok if z["rule"] == key), key=lambda z: z["created"])
            if hits:
                found.append(hits[-1])                                                         # la más reciente de ese TF; el TF mayor ya da el punto
                pending.remove(key)
    found.sort(key=lambda z: [k for k, _ in RULES].index(z["rule"]))
    return SetupBias(True, direction, bias_cfg.min_score, bias_cfg.enforce, found, when, ahead)
