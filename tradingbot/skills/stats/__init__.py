"""Skill Stats: estadísticas de la sesión y resultados del backtest (satélite aux3).

- skill.py      la skill: escucha a Cortex y Setup y publica las cifras (stats.session) y el backtest (stats.backtest)
- session.py    cifras de la sesión: GO / NO GO y operaciones simuladas (acierto, R, drawdown, libros por grupo)
- backtest.py   lectura de backtest.json (resumen de los Excel del backtest; se regenera con scripts/exportar_backtest.py)
"""
