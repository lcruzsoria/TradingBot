"""Skill Barrido RTH: busca el setup del barrido del RTH en NY Open (solo perfil Barrido_NYAM, índices USA).

Reutiliza la mecánica de la skill Pattern (TBR activas, plazos, histórico, avisos a Cortex y dibujo de las entradas) pero con sus reglas
propias (`deteccion.py`), su hexágono y su bloque de ajustes `BARRIDO_RTH_*` de tradingbot.env.
"""
from __future__ import annotations

from ...core import register_skill
from ..pattern.skill import PatternSkill
from . import deteccion  # noqa: F401  (registra el patrón barrido_rth)


@register_skill("barrido_rth")
class BarridoRthSkill(PatternSkill):
    title = "Barrido RTH"
    description = ("Setup del perfil Barrido_NYAM: tras el RTH (09:00-10:00), la primera rotura de su High o su Low (una vela que cierra fuera) entre las 10:00 y las 11:00 y "
                   "la primera vela M5 posterior que cierra de nuevo dentro del rango (antes de las 12:00) da la entrada. Stop en el swing del "
                   "barrido, objetivo 1 en el lado contrario del RTH y objetivo 2 en lo más cercano entre Asia/London y el 50 % del "
                   "NDOG/NWOG. Cortex lo valida; solo informa, no envía órdenes.")
    slot = 4
