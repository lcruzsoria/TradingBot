"""Confirmaciones opcionales de la entrada de Reversión: CISD y BPR con retest.

Todo se calcula en el espacio del corto (el tramo que barre el lado de la TBR sube y la reversión baja); el largo es el espejo con los
precios cambiados de signo. `Wh`, `Wl`, `Wo`, `Wc` son máximos, mínimos, aperturas y cierres en ese espacio.

- CISD: la secuencia de velas alcistas (del mismo color) que incluye la mecha pivote, ampliada hacia atrás y hacia delante mientras sigan
  alcistas; su nivel es el mínimo de la secuencia (como en el CRT). Confirma la primera vela posterior a la secuencia que cierra por debajo.
- BPR: un iFVG (hueco alcista dentro de la secuencia del CISD) que se invierte (una vela cierra bajo su base) y un FVG bajista posterior;
  su zona común es el BPR. Confirma la vela que, tras un retest del BPR (el precio sube hasta él sin cerrar por encima), cierra bajo el CISD.
  Las velas del BPR y del CISD son del timeframe que se pide (M5 o M3), no las M15 del patrón.
"""
from __future__ import annotations

import numpy as np

MODES = ("none", "cisd", "bpr")


def cisd_run(Wo, Wc, Wl, anchor: int, floor: int, end: int) -> tuple[int, int, float]:
    """(primera vela, última vela, nivel) de la secuencia alcista que incluye la vela `anchor` (o la anterior, si `anchor` no es alcista;
    si tampoco lo es, la propia vela `anchor`). El nivel es el mínimo de la secuencia."""
    if Wc[anchor] <= Wo[anchor]:
        if anchor - 1 >= floor and Wc[anchor - 1] > Wo[anchor - 1]:
            anchor -= 1
        else:
            return anchor, anchor, float(Wl[anchor])
    a = b = anchor
    while a - 1 >= floor and Wc[a - 1] > Wo[a - 1]:
        a -= 1
    while b + 1 <= end and Wc[b + 1] > Wo[b + 1]:
        b += 1
    return a, b, float(Wl[a:b + 1].min())


def cisd_confirmation(Wh, Wl, Wo, Wc, anchor: int, floor: int, end: int) -> int | None:
    """Índice de la primera vela posterior a la secuencia del CISD que cierra por debajo de su nivel (None si no llega)."""
    _a, b, level = cisd_run(Wo, Wc, Wl, anchor, floor, end)
    for t in range(b + 1, end + 1):
        if Wc[t] < level:
            return t
    return None


def bpr_confirmation(Wh, Wl, Wo, Wc, anchor: int, floor: int, end: int) -> int | None:
    """Índice de la vela que cierra bajo el CISD tras un BPR invertido y un retest, o None. Con varias parejas (iFVG, FVG) gana la más temprana."""
    a, b, level = cisd_run(Wo, Wc, Wl, anchor, floor, end)
    best = None
    for k in range(max(a + 1, 2), min(b + 1, end) + 1):                          # 3.ª vela del iFVG: su vela central (k - 1) está en la secuencia
        if not Wl[k] > Wh[k - 2]:
            continue
        base = float(Wh[k - 2])
        for m in range(k + 1, end + 1):                                          # 3.ª vela del FVG bajista, que nace después del iFVG
            if not Wh[m] < Wl[m - 2]:
                continue
            f = m - 1                                                            # vela de desplazamiento del FVG
            if f > k + 1 and Wl[k + 1:f].min() <= base:
                continue                                                         # el iFVG tiene que seguir sin mitigarse hasta que nace el FVG
            if f > k and Wc[f] >= base and Wl[f] <= base:
                continue                                                         # la vela de desplazamiento lo mitiga solo con la mecha
            cb, ct = max(base, float(Wh[m])), min(float(Wl[k]), float(Wl[m - 2]))
            if not (cb < ct and level < cb):
                continue
            inv = touched = None
            for t in range(k + 1, end + 1):
                if touched is not None and touched < t and Wc[t] < level:
                    best = t if best is None else min(best, t)
                    break
                if inv is None:
                    if Wc[t] < base:
                        inv = t
                elif inv < t and t > m and Wh[t] >= cb:                          # retest del BPR con el iFVG ya invertido y los dos huecos formados
                    if Wc[t] > ct:
                        break                                                    # cierra al otro lado de la zona: el retest la invalida
                    if touched is None:
                        touched = t
    return best
