"""Setup «Continuación del RTH» (perfil `barrido_nyam`): la rotura del TBR RTH en NY AM tras tocar su 50 %, a favor de la rotura. Funciones puras.

Es una HIPÓTESIS SIN VALIDAR: solo simula, como todo el bot con SETUP_SEND_ORDERS=false.

Reglas (velas de `BARRIDO_CONTINUACION_TF`, M5 al inicio; todo debe ocurrir entre las 10:00 y las 11:00 de NY):

1. El RTH (TBR 09:00-10:00 NY) define el rango.
2. Primera confirmación: desde las 10:00 el precio, aún dentro del rango, toca el 50 % del RTH (vale la mecha; no importa de qué lado).
3. Rotura: una vela M5 que CIERRA fuera del rango (cuerpo fuera) por cualquiera de los dos lados, después del toque del 50 % y antes de las 11:00
   (la vela debe abrir antes de `BARRIDO_CONTINUACION_END`). La primera vela que cierra fuera decide: si aún no se ha tocado el 50 %, no hay setup hoy.
   El toque de la propia vela que rompe no cuenta.
4. Entrada: a mercado al cierre de esa vela, a favor de la rotura (sobre el High: largo; bajo el Low: corto).
5. Stop fijo a `BARRIDO_CONTINUACION_STOP_POINTS` (40) puntos de la entrada y objetivo a `BARRIDO_CONTINUACION_RR` (2) R. Sin breakeven
   (en el backtest lo empeora). Si no hay rotura antes de las 11:00, el setup queda anulado. Cierre por tiempo al final del día de trading.

Solo los mercados de `BARRIDO_CONTINUACION_MARKETS` (NAS100 al inicio: es el único con el stop validado).
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from ...timeframes import parse_timeframe
from .._comun.contratos import DETECTED, Figure, PatternHit
from . import stops
from . import rth as _rth
from .rth import Contexto, contextos, es_indice_usa, hora_ny, minutos as _minutos  # noqa: F401  (los usa la skill y los tests)

KEY = "barrido_continuacion"
TITLE = "Continuación del RTH"
DEFAULT_TF = "5m"
DEFAULT_START = "10:00"
DEFAULT_END = "11:00"
DEFAULT_STOP_POINTS = 40.0
DEFAULT_RR = 2.0
DEFAULT_MARKETS = "NAS100"
PREFIX = "BARRIDO_CONTINUACION"


def minutos(text: str, name: str) -> int:
    try:
        return _minutos(text, name)
    except ValueError:
        raise ValueError(f"{PREFIX}_{name}={text!r}: usa el formato HH:MM.") from None


@dataclass(frozen=True)
class Ajustes:
    """Ajustes de la skill (bloque BARRIDO_CONTINUACION de tradingbot.env, ya sin prefijo)."""
    tf: str = DEFAULT_TF
    start: int = minutos(DEFAULT_START, "START")
    end: int = minutos(DEFAULT_END, "END")
    stop_points: float = DEFAULT_STOP_POINTS
    rr: float = DEFAULT_RR
    markets: tuple = (DEFAULT_MARKETS,)
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
        markets = tuple(m.strip().upper() for m in str(get("MARKETS", DEFAULT_MARKETS)).split(",") if m.strip())
        a = cls(tf, minutos(get("START", DEFAULT_START), "START"), minutos(get("END", DEFAULT_END), "END"), points, rr, markets,
                stops.leer(settings, PREFIX, points, 0.0))
        if a.end <= a.start:
            raise ValueError(f"{PREFIX}_END={a.end // 60:02d}:{a.end % 60:02d} debe ser posterior a START.")
        return a

    def stop_de(self, symbol: str) -> tuple[float, float]:
        return stops.de(self.stop_mercado, symbol, self.stop_points, 0.0)

    def admite(self, symbol: str) -> bool:
        name = symbol.strip().upper()
        return any(name.startswith(m) for m in self.markets)


def analizar(ctx: Contexto, a: Ajustes = Ajustes()) -> tuple[list[PatternHit], list[Figure]]:
    """Resultados del día del RTH de `ctx` (cero o uno) y su dibujo."""
    if len(ctx.ts) == 0 or not es_indice_usa(ctx.symbol) or not a.admite(ctx.symbol):
        return [], []
    rth = ctx.rth
    midnight = (rth.day.toordinal() - 719163) * 86400 + ctx.ahead             # medianoche de NY, en hora del servidor
    first = int(np.searchsorted(ctx.ts, max(midnight + a.start * 60, rth.close_ts), "left"))
    last = min(ctx.last_bar, int(np.searchsorted(ctx.ts, midnight + a.end * 60, "left")) - 1)
    mid = (rth.high + rth.low) / 2
    touched = False
    for i in range(first, last + 1):
        if ctx.close[i] > rth.high or ctx.close[i] < rth.low:
            if not touched:
                return [], []                                                 # rompe sin haber tocado el 50 %: sin setup
            up = bool(ctx.close[i] > rth.high)
            direction, side = ("long", "High") if up else ("short", "Low")
            close = float(ctx.close[i])
            sign = 1.0 if up else -1.0
            puntos, _ = a.stop_de(ctx.symbol)
            stop, target = close - sign * puntos, close + sign * puntos * a.rr
            detail = (f"el precio toca el 50 % del RTH ({mid:.5g}) y a las {hora_ny(ctx, i)} una vela cierra fuera del {side} del RTH "
                      f"({rth.high if up else rth.low:.5g}) en {close:.5g}. Entrada a mercado a ese cierre, a favor de la rotura, stop fijo a "
                      f"{puntos:g} puntos ({stop:.5g}) y objetivo a {a.rr:g} R ({target:.5g}). Sin breakeven")
            ts_hit = int(ctx.ts[i]) + ctx.tf_minutes * 60
            figures = []
            if i + 1 < len(ctx.ts):
                fig = _rth._figura_posicion(ctx, direction, i + 1, close, stop, target, f"Continuación {'▲' if up else '▼'}", None, KEY)
                figures = [replace(fig, levels={**fig.levels, "entrada_ts": float(ctx.ts[i])})]
            return [PatternHit(KEY, TITLE, direction, int(i), close, detail, {"stop": stop, "target": target}, ts_hit, DETECTED)], figures
        if ctx.low[i] <= mid <= ctx.high[i]:
            touched = True
    return [], []
