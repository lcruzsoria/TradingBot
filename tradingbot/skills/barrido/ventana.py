"""Setup «Ventana 9:55» (perfil `ventana9_55`, solo Nasdaq): el barrido de la vela de las 09:55 por la de las 10:00. Funciones puras.

Es una HIPÓTESIS SIN VALIDAR: solo simula, como todo el bot con SETUP_SEND_ORDERS=false.

Reglas del usuario (2026-11-20), velas de `BARRIDO_VENTANA_955_TF` (M5), hora de NY, sin zona (no importa dónde esté el precio respecto al RTH):

1. Vela 1: la de las 09:55 (`BARRIDO_VENTANA_955_VELA`). Su color no importa.
2. Vela 2: la siguiente (10:00). Corto si supera el High de la vela 1 y cierra NEGRA; largo si baja del Low de la vela 1 y cierra BLANCA.
   Si toca los dos lados decide su color. Sin barrido del lado de su color no hay setup.
3. Entrada: a mercado al cierre de la vela 2 (la apertura de la de las 10:05), en contra del barrido.
4. Stop: en la punta de la vela 2 (su High en un corto, su Low en un largo).
5. Objetivo: `BARRIDO_VENTANA_955_RR` (3) R. Sin breakeven. Si al final del día de trading no ha tocado ni stop ni objetivo, cierra por tiempo.

Solo los mercados de `BARRIDO_VENTANA_955_MARKETS` (NAS100). Backtest NAS100 feb-2024 a nov-2026: 236 operaciones, +49,7 R con 3R.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from ...timeframes import parse_timeframe
from .._comun.contratos import DETECTED, Figure, PatternHit
from . import rth as _rth
from .rth import Contexto, contextos, es_indice_usa, hora_ny, minutos as _minutos  # noqa: F401  (los usa la skill y los tests)

KEY = "ventana_955"
TITLE = "Ventana 9:55"
DEFAULT_TF = "5m"
DEFAULT_VELA = "09:55"
DEFAULT_RR = 3.0
DEFAULT_MARKETS = "NAS100"
PREFIX = "BARRIDO_VENTANA_955"


def minutos(text: str, name: str) -> int:
    try:
        return _minutos(text, name)
    except ValueError:
        raise ValueError(f"{PREFIX}_{name}={text!r}: usa el formato HH:MM.") from None


@dataclass(frozen=True)
class Ajustes:
    """Ajustes del setup (bloque BARRIDO_VENTANA_955 de tradingbot.env, ya sin prefijo)."""
    tf: str = DEFAULT_TF
    vela: int = minutos(DEFAULT_VELA, "VELA")
    rr: float = DEFAULT_RR
    markets: tuple = (DEFAULT_MARKETS,)

    @classmethod
    def desde(cls, settings) -> "Ajustes":
        get = (lambda key, default: default) if settings is None else settings.get
        tf = str(get("TF", DEFAULT_TF))
        parse_timeframe(tf)
        try:
            rr = float(str(get("RR", DEFAULT_RR)).replace(",", "."))
        except ValueError:
            raise ValueError(f"{PREFIX}_RR debe ser un número.") from None
        if rr <= 0:
            raise ValueError(f"{PREFIX}_RR debe ser mayor que 0.")
        markets = tuple(m.strip().upper() for m in str(get("MARKETS", DEFAULT_MARKETS)).split(",") if m.strip())
        return replace(cls(), tf=tf, vela=minutos(get("VELA", DEFAULT_VELA), "VELA"), rr=rr, markets=markets)

    def admite(self, symbol: str) -> bool:
        name = symbol.strip().upper()
        return any(name.startswith(m) for m in self.markets)


def analizar(ctx: Contexto, a: Ajustes = Ajustes()) -> tuple[list[PatternHit], list[Figure]]:
    """Resultado del día de `ctx` (cero o uno) y su dibujo."""
    if len(ctx.ts) == 0 or not es_indice_usa(ctx.symbol) or not a.admite(ctx.symbol):
        return [], []
    midnight = (ctx.rth.day.toordinal() - 719163) * 86400 + ctx.ahead             # medianoche de NY, en hora del servidor
    t1 = midnight + a.vela * 60
    i = int(np.searchsorted(ctx.ts, t1, "left"))                                   # vela 1 (09:55) y vela 2 (la siguiente)
    step = ctx.tf_minutes * 60
    if i + 1 > ctx.last_bar or int(ctx.ts[i]) != t1 or int(ctx.ts[i + 1]) != t1 + step:
        return [], []
    h1, l1 = float(ctx.high[i]), float(ctx.low[i])
    j = i + 1
    o2, h2, l2, c2 = float(ctx.open[j]), float(ctx.high[j]), float(ctx.low[j]), float(ctx.close[j])
    if c2 < o2 and h2 > h1:
        direction, stop, side, sign = "short", h2, "High", -1.0
    elif c2 > o2 and l2 < l1:
        direction, stop, side, sign = "long", l2, "Low", 1.0
    else:
        return [], []
    risk = abs(c2 - stop)
    if risk <= 0:
        return [], []
    target = c2 + sign * a.rr * risk
    levels = {"stop": stop, "target": target}
    detail = (f"la vela de las {hora_ny(ctx, j)} barre el {side} de la de las {hora_ny(ctx, i)} ({h1 if sign < 0 else l1:.5g}) y cierra "
              f"{'negra' if sign < 0 else 'blanca'} en {c2:.5g}. Entrada a mercado a ese cierre, en contra del barrido, stop en su "
              f"{'máximo' if sign < 0 else 'mínimo'} ({stop:.5g}, {risk:.5g} puntos) y objetivo {a.rr:g} R ({target:.5g})")
    ts_hit = int(ctx.ts[j]) + step
    figures = []
    if j + 1 < len(ctx.ts):
        fig = _rth._figura_posicion(ctx, direction, j + 1, c2, stop, target, f"Ventana 9:55 {'▲' if sign > 0 else '▼'}", None, KEY)
        figures = [replace(fig, levels={**fig.levels, "entrada_ts": float(ctx.ts[j])})]
    return [PatternHit(KEY, TITLE, direction, int(j), c2, detail, levels, ts_hit, DETECTED)], figures
