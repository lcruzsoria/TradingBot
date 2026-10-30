"""Patrón «TBR con VWAP»: retest del VWAP dentro de la TBR y continuación hasta el extremo de su rango.

Es la estrategia del perfil `tbrvwap` (MT5_<PERFIL>_STRATEGY=tbrvwap). La lógica de la señal está en `vwap_retest.py` (ver ahí las
reglas) y es la misma que mide `scripts/backtest_vwap_tbr.py`. Es una HIPÓTESIS SIN VALIDAR: por eso `default_on = False` (solo la
busca el perfil de estrategia, o PATTERN_TYPES=tbr_vwap) y solo simula, como todo el bot con SETUP_SEND_ORDERS=false.

Entrada a mercado al cierre de la vela M15 del retest (el bot solo ve velas cerradas); stop y objetivo según `Params`; una operación
como mucho por TBR. Ajustes (bloque PATTERN de tradingbot.env): TBR_VWAP_TF, TBR_VWAP_LOOKBACK, TBR_VWAP_STOP_FRAC, TBR_VWAP_TARGET,
TBR_VWAP_MIN_RR.
"""
from __future__ import annotations

import numpy as np

from ...timeframes import parse_timeframe
from ..levels.daylevels import vwap as day_vwap
from .continuacion import _when
from .patterns import DETECTED, Figure, Pattern, PatternContext, PatternHit, register_pattern
from .trade import MAX_HOLD_SECONDS, day_close
from .vwap_retest import Params, Signal, find_signal
from ..setup.positions import resolve
from types import SimpleNamespace

KEY = "tbr_vwap"
TITLE = "TBR con VWAP"
DEFAULT_TF = "15m"


@register_pattern(KEY)
class TbrVwap(Pattern):
    title = TITLE
    default_on = False                     # hipótesis por validar: solo el perfil tbrvwap (o PATTERN_TYPES=tbr_vwap) la busca

    def __init__(self, settings=None) -> None:
        super().__init__(settings)
        get = (lambda key, default: default) if settings is None else settings.get
        self.tf = parse_timeframe(str(get("TBR_VWAP_TF", DEFAULT_TF)))
        try:
            self.params = Params(lookback=int(get("TBR_VWAP_LOOKBACK", Params.lookback)),
                                 stop_frac=float(get("TBR_VWAP_STOP_FRAC", Params.stop_frac)),
                                 target=float(get("TBR_VWAP_TARGET", Params.target)),
                                 min_rr=float(get("TBR_VWAP_MIN_RR", Params.min_rr)))
        except ValueError as exc:
            raise ValueError(f"PATTERN_TBR_VWAP_*: valor no numérico ({exc}).") from None
        if self.params.lookback < 0 or self.params.stop_frac <= 0 or self.params.min_rr < 0:
            raise ValueError("PATTERN_TBR_VWAP_*: LOOKBACK >= 0, STOP_FRAC > 0 y MIN_RR >= 0.")

    def timeframe(self) -> str:
        return self.tf

    def _signal(self, ctx: PatternContext) -> tuple[Signal | None, np.ndarray | None]:
        if ctx.volume is None or len(ctx.ts) == 0:
            return None, None
        vw, _ = day_vwap(ctx.ts, ctx.high, ctx.low, ctx.close, ctx.volume, ctx.ahead, ctx.day_end)
        end = ctx.last_bar
        if ctx.day_end:                                                   # se busca hasta el cierre del día de trading
            limit = day_close(int(ctx.ts[min(ctx.first_bar, len(ctx.ts) - 1)]), ctx.ahead, ctx.day_end)
            end = min(end, int(np.searchsorted(ctx.ts, limit, "left")) - 1)
        if ctx.first_bar > end:
            return None, vw
        return find_signal(ctx.open, ctx.high, ctx.low, ctx.close, vw, ctx.tbr.high, ctx.tbr.low, ctx.first_bar, end, self.params), vw

    def detect(self, ctx: PatternContext) -> list[PatternHit]:
        sig, _ = self._signal(ctx)
        if sig is None:
            return []
        t = sig.bar
        entry_ts = int(ctx.ts[t]) + ctx.tf_minutes * 60                   # la posición vive desde la vela siguiente
        side = "VWAP por encima" if sig.direction == "long" else "VWAP por debajo"
        detail = (f"retest del VWAP ({sig.vwap:.5g}) dentro de la TBR {ctx.tbr.zone} en {_when(ctx, t)}: la vela lo toca y cierra "
                  f"{'por encima' if sig.direction == 'long' else 'por debajo'} ({side} en las velas previas). Entrada a mercado al "
                  f"cierre ({sig.entry:.5g}), stop en {sig.stop:.5g} y objetivo en el extremo de la TBR ({sig.target:.5g})")
        return [PatternHit(KEY, TITLE, sig.direction, int(t), float(sig.entry), detail,
                           {"stop": sig.stop, "target": sig.target, "vwap": sig.vwap}, entry_ts, DETECTED)]

    def figures(self, ctx: PatternContext) -> list[Figure]:
        sig, _ = self._signal(ctx)
        if sig is None:
            return []
        t, tf_sec = sig.bar, ctx.tf_minutes * 60
        start = int(ctx.ts[t]) + tf_sec
        close = start + MAX_HOLD_SECONDS
        if ctx.day_end:
            close = min(close, day_close(start - 1, ctx.ahead, ctx.day_end))
        kind, exit_ts = None, int(ctx.ts[-1]) + tf_sec
        order = SimpleNamespace(direction=sig.direction, pattern_key=KEY, price=sig.entry, stop=sig.stop, target=sig.target,
                                entry_ts=start, close_ts=close)
        done = resolve(order, ctx.ts, ctx.high, ctx.low, ctx.close, ctx.be_r, tf_sec)
        if done is not None:
            kind, exit_ts = done.result, done.exit_ts + tf_sec
        state = {"objetivo": "objetivo", "stop": "stop", "breakeven": "be", "tiempo": "tiempo"}.get(kind, "abierta")
        return [Figure("pos", KEY, ctx.tbr.zone, sig.direction, start, exit_ts,
                       {"entrada": float(sig.entry), "stop": float(sig.stop), "objetivo": float(sig.target)}, state,
                       f"{ctx.tbr.zone} {'▲' if sig.direction == 'long' else '▼'} VWAP", ctx.tbr.day.isoformat())]
