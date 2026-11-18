"""Setup «Barrido del PDH/PDL en Londres» (modelo Greenbird, perfil `barrido_nyam`): el de `pdh.py` con el rango de la TBR de Londres.

Es una HIPÓTESIS SIN VALIDAR: solo simula, como todo el bot con SETUP_SEND_ORDERS=false.

Mismas reglas que el PDH/PDL de Asia (ver `pdh.py`), con estas diferencias (velas de `BARRIDO_LONDRES_TF`, M5 al inicio):

1. Nivel fresco: el PDH (PDL) del día de trading anterior (18:00-18:00 NY) no lo ha tocado el precio desde las 18:00 hasta las 02:00. Si Asia
   ya lo tomó, está mitigado y no vale.
2. Barrido: entre `BARRIDO_LONDRES_START` (02:00 NY) y `BARRIDO_LONDRES_END` (03:00 NY), con un High (Low) por encima (debajo) del nivel: es el
   alto (bajo) del rango de Londres que se está formando.
3. Entrada: la primera vela que cierra de vuelta por debajo del PDH (por encima del PDL), con cierre a las 03:00 como tarde.
4. Stop: el de Asia, fijo a 30 puntos de la entrada si cubre el swing; si no, el swing más 5 puntos.
5. Objetivo: el extremo opuesto de Londres ya formado en la entrada, mientras el precio siga dentro; si no hay o no llega, sale por TIEMPO, al precio de
   mercado cuando cierra la TBR de Londres (05:00 NY), o antes en el stop; el riesgo es variable.
   El extremo contrario de Londres solo se guarda como referencia. La señal se da al cierre de Londres, con la entrada ya fijada.

Solo índices USA (NAS100, SP500, DJ30...), no Forex.
"""
from __future__ import annotations

from dataclasses import dataclass

from . import pdh as _pdh
from .pdh import Contexto, es_indice_usa, hora_ny  # noqa: F401  (los usa la skill y los tests)

KEY = "barrido_pdh_londres"
TITLE = "Barrido PDH/PDL Londres"
ZONA = "LONDON"                  # la TBR cuyo rango da el objetivo
DEFAULT_START = "02:00"
DEFAULT_END = "03:00"
PREFIX = "BARRIDO_LONDRES"


@dataclass(frozen=True)
class Ajustes(_pdh.Ajustes):
    """Ajustes de la skill (bloque BARRIDO_LONDRES de tradingbot.env, ya sin prefijo): los de `pdh.py` con la ventana de Londres."""
    start: int = _pdh.minutos(DEFAULT_START, "START", PREFIX)
    end: int = _pdh.minutos(DEFAULT_END, "END", PREFIX)

    @classmethod
    def desde(cls, settings) -> "Ajustes":
        return super().desde(settings, DEFAULT_START, DEFAULT_END, PREFIX)


def analizar(ctx: Contexto, a: Ajustes = Ajustes()):
    return _pdh.analizar(ctx, a, KEY, TITLE, "Londres")


def contextos(symbol, tf_minutes, ts, o, h, l, c, sessions, ahead, day_end=0, be_r=None):
    """Un contexto por cada Londres cerrada (ver `pdh.contextos`), con salida al cierre del rango."""
    return _pdh.contextos(symbol, tf_minutes, ts, o, h, l, c, sessions, ahead, day_end, be_r, ZONA, True)
