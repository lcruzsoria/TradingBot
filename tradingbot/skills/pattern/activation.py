"""Primer hecho de una TBR activa: toma de un extremo (patrón 1) o toma del 50 % (patrón 2).

Entre los dos patrones solo se activa uno por TBR: el que tenga el primer hecho. El otro se descarta sin avisar.

- Toma de un extremo: una vela pierde el Low o supera el High (con la mecha o con el cuerpo).
- Toma del 50 %: una vela cruza el 50 % viniendo del lado en que estaba el precio (su cierre anterior; si cierra justo en el 50 %,
  su apertura). De abajo hacia arriba la dirección es bajista; de arriba hacia abajo, alcista.
- Si una misma vela toma el 50 % y el extremo del lado de donde venía el precio, vale como toma de un extremo (la extremo fue antes
  en el tiempo). Si toma el 50 % y el extremo contrario, es la activación del patrón 2, que queda invalidada.
"""
from __future__ import annotations

from dataclasses import dataclass

from .patterns import PatternContext


@dataclass(frozen=True)
class FirstEvent:
    kind: str                 # "extreme" o "mid"
    index: int                # vela del hecho
    side: str                 # extreme: "low", "high" o "both"; mid: "below" o "above" (de dónde venía el precio)
    contrary_taken: bool = False   # mid: la misma vela tomó también el extremo contrario


def first_event(ctx: PatternContext) -> FirstEvent | None:
    """Primer hecho de la TBR activa dentro del plazo, o None si todavía no ha pasado nada."""
    tbr = ctx.tbr
    o, h, l, c = ctx.open, ctx.high, ctx.low, ctx.close
    for i in range(ctx.first_bar, ctx.last_bar + 1):
        prev = c[i - 1] if i > 0 else o[i]
        if prev == tbr.mid:
            prev = o[i]
        origin = "below" if prev < tbr.mid else "above" if prev > tbr.mid else None
        took_low, took_high = l[i] < tbr.low, h[i] > tbr.high
        mid_taken = (origin == "below" and h[i] > tbr.mid) or (origin == "above" and l[i] < tbr.mid)
        if not (took_low or took_high or mid_taken):
            continue
        if took_low and took_high:
            return FirstEvent("extreme", i, "both")
        if mid_taken:
            took_origin_extreme = (origin == "below" and took_low) or (origin == "above" and took_high)
            if took_origin_extreme:
                return FirstEvent("extreme", i, "low" if took_low else "high")
            return FirstEvent("mid", i, origin, took_high if origin == "below" else took_low)
        return FirstEvent("extreme", i, "low" if took_low else "high")
    return None
