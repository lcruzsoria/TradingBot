"""Setup «Barrido PDH/PDL Pre-NY» (modelo Greenbird, perfil `barrido_nyam`): el barrido del PDH/PDL de `pdh.py` entre las 05:00 y las 09:00, con objetivo fijo a 2R.

Es una HIPÓTESIS SIN VALIDAR: solo simula, como todo el bot con SETUP_SEND_ORDERS=false. Salió de explorar el barrido del PDH/PDL en todas las sesiones
(scripts/explorar_barrido_pdh_sesiones.py): entre las 04:00 y las 09:30 con nivel fresco y 2R dio de +0,17 a +0,50 R/op; sin exigir el nivel fresco, ~0.

Reglas (velas de `BARRIDO_PRENY_TF`, M5 al inicio), las de `pdh.py` salvo la ventana y el objetivo:

1. PDH / PDL: máximo y mínimo del día de trading anterior (18:00-18:00 NY).
2. Nivel fresco: el precio no lo ha tocado desde las 18:00 hasta el inicio de la ventana (05:00). Si Asia o Londres ya lo tomaron, no hay setup.
3. Barrido: entre `BARRIDO_PRENY_START` (05:00 NY) y `BARRIDO_PRENY_END` (09:00 NY) una vela supera el nivel.
4. Entrada: la primera vela, desde la del barrido (inclusive), que CIERRA de vuelta por debajo del PDH (por encima del PDL), a mercado a su cierre. La
   vela debe cerrar antes de las 09:00. Si no cierra de vuelta dentro de la ventana, no hay setup.
5. Stop: fijo, a `BARRIDO_PRENY_STOP_POINTS` (por mercado con `STOP_POINTS_<MERCADO>`) puntos de la entrada si con eso queda cubierto el swing (el extremo desde
   el barrido hasta la entrada); si no, el swing más `BARRIDO_PRENY_STOP_BUFFER`.
6. Objetivo: `BARRIDO_PRENY_RR` (2) R. Sin breakeven; si no llega ni el objetivo ni el stop, cierra a final del día de trading.
7. Una sola operación al día: la del primer lado (PDH o PDL) cuya vela de entrada cierra antes.

Solo índices USA (NAS100, SP500, DJ30...), no Forex.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from .._comun.contratos import DETECTED, Figure, PatternHit
from . import pdh as _pdh
from .pdh import Contexto, es_indice_usa, hora_ny  # noqa: F401  (los usa la skill y los tests)

KEY = "barrido_pdh_preny"
TITLE = "Barrido PDH/PDL Pre-NY"
ZONA = "LONDON"                  # el contexto se apoya en Londres, ya cerrada a las 05:00: de ahí salen el día y el PDH/PDL
DEFAULT_START = "05:00"
DEFAULT_END = "09:00"
DEFAULT_RR = 2.0
PREFIX = "BARRIDO_PRENY"


@dataclass(frozen=True)
class Ajustes(_pdh.Ajustes):
    """Ajustes de la skill (bloque BARRIDO_PRENY de tradingbot.env, ya sin prefijo): los de `pdh.py` con la ventana pre-NY y el objetivo en R."""
    start: int = _pdh.minutos(DEFAULT_START, "START", PREFIX)
    end: int = _pdh.minutos(DEFAULT_END, "END", PREFIX)
    rr: float = DEFAULT_RR

    @classmethod
    def desde(cls, settings) -> "Ajustes":
        a = super().desde(settings, DEFAULT_START, DEFAULT_END, PREFIX)
        try:
            rr = float(DEFAULT_RR if settings is None else settings.get("RR", DEFAULT_RR))
        except ValueError:
            raise ValueError(f"{PREFIX}_RR debe ser un número.") from None
        if rr <= 0:
            raise ValueError(f"{PREFIX}_RR={rr:g} debe ser mayor que 0.")
        return replace(a, rr=rr)


def analizar(ctx: Contexto, a: Ajustes = Ajustes()) -> tuple[list[PatternHit], list[Figure]]:
    """Resultado del día de `ctx` (cero o uno) y su dibujo: el barrido de `pdh.analizar` con el objetivo fijo a `a.rr` R."""
    hits, figures = _pdh.analizar(ctx, a, KEY, TITLE, "Londres")
    if not hits:
        return [], []
    h = hits[0]
    up = h.direction == "short"
    sign = 1.0 if up else -1.0                                                # corto: el stop va por encima de la entrada
    stop = h.levels["stop"]
    riesgo = sign * (stop - h.price)
    target = h.price - sign * a.rr * riesgo
    detail = (h.detail.split(" y objetivo")[0].split(" y sin objetivo")[0].split(" y salida")[0]
              + f" y objetivo fijo a {a.rr:g} R ({target:.5g}). Sin breakeven; si no llega ninguno, cierra a final del día de trading. Riesgo fijo")
    hit = PatternHit(KEY, TITLE, h.direction, h.x, h.price, detail, {"stop": stop, "target": target}, h.ts, DETECTED)
    figs = []
    if figures and h.x + 1 < len(ctx.ts):
        name = "PDH" if up else "PDL"
        fig = _pdh._figura_posicion(ctx, h.direction, h.x + 1, h.price, stop, target, f"{name} {'▼' if up else '▲'} pre-NY", KEY, False)
        figs = [Figure(fig.kind, fig.key, fig.zone, fig.direction, fig.x0_ts, fig.x1_ts, {**fig.levels, "entrada_ts": float(ctx.ts[h.x])},
                       fig.state, fig.label, fig.day)]
    return [hit], figs


def contextos(symbol, tf_minutes, ts, o, h, l, c, sessions, ahead, day_end=0, be_r=None):
    """Un contexto por cada día con Londres cerrada (ver `pdh.contextos`), con la posición abierta hasta el final del día de trading."""
    return _pdh.contextos(symbol, tf_minutes, ts, o, h, l, c, sessions, ahead, day_end, be_r, ZONA, False)
