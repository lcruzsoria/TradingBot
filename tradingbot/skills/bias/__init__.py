"""Skill Bias: sesgo (Bullish / Bearish / No Bias) de la sesión del día en curso.

- skill.py    la skill (hexágono 1)
- engine.py   motor: ejecuta las reglas activas y decide el sesgo
- rules.py    reglas (cada criterio, una clase con @register_rule)
- context.py  velas del día y del día anterior que reciben las reglas
- models.py   tipos: Bias, BiasResult, Direction, RuleVote
- filter.py   filtro de operativa (qué dirección se permite)
- execution.py  Bias Execution: GO / NO GO de cada setup y su motivo
- schedule.py   recálculo programado (3 h en índices USA, 4 h en el resto)
"""
from .engine import BiasEngine
from .filter import TradeFilter
from .models import Bias, BiasResult, Direction, RuleVote

__all__ = ["Bias", "BiasEngine", "BiasResult", "Direction", "RuleVote", "TradeFilter"]
