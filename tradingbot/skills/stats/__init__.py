"""Skill Stats: estadísticas de la sesión y resultados del backtest (satélite aux3).

- skill.py      la skill: escucha a Cortex y Setup y publica las cifras (stats.session) y el backtest (stats.backtest)
- session.py    cifras de la sesión: GO / NO GO y operaciones simuladas (acierto, R, drawdown, libros por grupo)
- backtest.py   lee backtest.json.gz (cada operación de los backtests; se regenera con scripts/exportar_backtest.py) y calcula
                todas las cifras de la ventana Backtest, también filtrando por años y horas
"""
