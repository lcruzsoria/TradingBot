"""Skill Setup: el ejecutor. Solo recibe órdenes de Cortex (activo, temporalidad, sesgo, TBR y patrón ya validados) y las
mete en la cuenta del broker. Por ahora funciona en modo simulación: no envía nada a MT5.

- skill.py      la skill (satélite aux1)
- positions.py  seguimiento de las posiciones simuladas (stop, objetivo, stop a breakeven y cierre por tiempo)
- store.py      las posiciones abiertas en disco (data/perfiles/<perfil>/abiertas.json)
- account.py    la cuenta virtual del perfil: capital inicial + resultado de las operaciones (data/perfiles/<perfil>/cuenta.json)
"""
