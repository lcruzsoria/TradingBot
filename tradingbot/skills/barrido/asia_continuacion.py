"""Setup «Continuación de Asia» (perfil `barrido_nyam`): la rotura del rango de Asia en la primera media hora de la madrugada, a favor de la rotura.

Es la inversión del antiguo Barrido de Asia (reversión), que en el forward test perdía casi todas las operaciones. Es una HIPÓTESIS SIN VALIDAR:
solo simula, como todo el bot con SETUP_SEND_ORDERS=false.

Reglas (velas de `BARRIDO_ASIA_CONTINUACION_TF`, M5 al inicio):

1. El rango de Asia (TBR 20:00-00:00 NY) tiene que haber terminado.
2. Rotura: la primera vela, desde `..._START` (00:00 NY), que CIERRA fuera del rango. Debe abrir antes de `..._END` (00:30 NY); si la primera
   rotura llega después, no hay setup.
3. Entrada: a mercado al cierre de esa vela, a favor de la rotura (sobre el High: largo; bajo el Low: corto).
4. Stop fijo a `..._STOP_POINTS` (30 en NAS100; por mercado con `STOP_POINTS_<MERCADO>`) y objetivo a `..._RR` (3) R. Sin breakeven;
   si no llega ninguno, la posición cierra a final del día de trading.

Solo índices USA (NAS100, SP500, DJ30...), no Forex.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date

import numpy as np

from ...timeframes import parse_timeframe
from .._comun.contratos import DETECTED, Figure, PatternHit
from . import asia as _asia
from . import stops
from .asia import Contexto, contextos, es_indice_usa, hora_ny  # noqa: F401  (los usa la skill y el backtest)

KEY = "barrido_asia_continuacion"
TITLE = "Continuación de Asia"
DEFAULT_TF = "5m"
DEFAULT_START = "00:00"
DEFAULT_END = "00:30"
DEFAULT_STOP_POINTS = 30.0
DEFAULT_RR = 3.0
PREFIX = "BARRIDO_ASIA_CONTINUACION"


def minutos(text: str, name: str) -> int:
    try:
        return _asia.minutos(text, name)
    except ValueError:
        raise ValueError(f"{PREFIX}_{name}={text!r}: usa el formato HH:MM.") from None


@dataclass(frozen=True)
class Ajustes:
    """Ajustes de la skill (bloque BARRIDO_ASIA_CONTINUACION de tradingbot.env, ya sin prefijo)."""
    tf: str = DEFAULT_TF
    start: int = minutos(DEFAULT_START, "START")
    end: int = minutos(DEFAULT_END, "END")
    stop_points: float = DEFAULT_STOP_POINTS
    rr: float = DEFAULT_RR
    stop_mercado: tuple = ()

    @classmethod
    def desde(cls, settings) -> "Ajustes":
        get = (lambda key, default: default) if settings is None else settings.get
        tf = str(get("TF", DEFAULT_TF))
        parse_timeframe(tf)
        try:
            points, rr = float(get("STOP_POINTS", DEFAULT_STOP_POINTS)), float(get("RR", DEFAULT_RR))
        except ValueError:
            raise ValueError(f"{PREFIX}_STOP_POINTS y {PREFIX}_RR deben ser números.") from None
        if points <= 0 or rr <= 0:
            raise ValueError(f"{PREFIX}_STOP_POINTS y {PREFIX}_RR deben ser mayores que 0.")
        a = cls(tf, minutos(get("START", DEFAULT_START), "START"), minutos(get("END", DEFAULT_END), "END"), points, rr,
                stops.leer(settings, PREFIX, points, 0.0))
        if a.end <= a.start:
            raise ValueError(f"{PREFIX}_END={a.end // 60:02d}:{a.end % 60:02d} debe ser posterior a START.")
        return a

    def stop_de(self, symbol: str) -> tuple[float, float]:
        return stops.de(self.stop_mercado, symbol, self.stop_points, 0.0)


def analizar(ctx: Contexto, a: Ajustes = Ajustes()) -> tuple[list[PatternHit], list[Figure]]:
    """Resultados de la noche de Asia de `ctx` (cero o uno) y su dibujo."""
    if len(ctx.ts) == 0 or not es_indice_usa(ctx.symbol):
        return [], []
    asia = ctx.asia
    midnight = (asia.day.toordinal() + 1 - date(1970, 1, 1).toordinal()) * 86400 + ctx.ahead      # medianoche de NY en que cierra Asia
    first = int(np.searchsorted(ctx.ts, max(midnight + a.start * 60, asia.close_ts), "left"))
    last_break = int(np.searchsorted(ctx.ts, midnight + a.end * 60, "left")) - 1
    if first >= len(ctx.ts) or first > ctx.last_bar:
        return [], []
    outside = np.flatnonzero((ctx.close[first:ctx.last_bar + 1] > asia.high) | (ctx.close[first:ctx.last_bar + 1] < asia.low))
    if not outside.size:
        return [], []
    i = first + int(outside[0])
    if i > last_break:
        return [], []                                                         # la primera rotura llegó fuera de la ventana
    up = bool(ctx.close[i] > asia.high)
    direction, side = ("long", "High") if up else ("short", "Low")
    close = float(ctx.close[i])
    sign = 1.0 if up else -1.0
    puntos, _ = a.stop_de(ctx.symbol)
    stop, target = close - sign * puntos, close + sign * puntos * a.rr
    detail = (f"la vela de las {hora_ny(ctx, i)} cierra fuera del {side} de Asia ({asia.high if up else asia.low:.5g}) en {close:.5g}. Entrada a mercado a "
              f"ese cierre, a favor de la rotura, stop fijo a {puntos:g} puntos ({stop:.5g}) y objetivo a {a.rr:g} R ({target:.5g}). Sin breakeven")
    ts_hit = int(ctx.ts[i]) + ctx.tf_minutes * 60
    figures = []
    if i + 1 < len(ctx.ts):
        fig = _asia._figura_posicion(ctx, direction, i + 1, close, stop, target, f"Asia {'▲' if up else '▼'} continuación", KEY)
        figures = [replace(fig, levels={**fig.levels, "entrada_ts": float(ctx.ts[i])})]
    return [PatternHit(KEY, TITLE, direction, int(i), close, detail, {"stop": stop, "target": target}, ts_hit, DETECTED)], figures
