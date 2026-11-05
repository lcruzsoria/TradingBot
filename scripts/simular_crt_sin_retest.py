"""Experimento CRT: el mismo backtest que `exportar_backtest_crt.py --simular`, pero sin exigir el retest del BPR (`engine.find_zone_setups(retest=False)`).

Con el iFVG invertido y los dos FVG formados, la entrada es la apertura de la vela siguiente a la que cierra con cuerpo más allá del CISD. No toca la ventana
Backtest ni el forwardtest: guarda las operaciones en analisis/crt_operaciones_sin_retest.pkl. Compáralas con las de la regla vigente
(analisis/crt_operaciones.pkl) con `comparar_crt_sin_retest.py`.

Uso (desde la raíz del proyecto, con las velas de analisis/5m y analisis/15m al día, ver descargar_velas.py):
    uv run --with pyarrow python scripts/simular_crt_sin_retest.py
"""
from __future__ import annotations

import functools
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import exportar_backtest_crt as ex                                                     # noqa: E402
from tradingbot.skills.crt import engine                                               # noqa: E402

ex.TRADES = ROOT / "analisis" / "crt_operaciones_sin_retest.pkl"
vigente = engine.find_zone_setups
engine.find_zone_setups = functools.partial(vigente, retest=False)
try:
    ex.simulate()
finally:
    engine.find_zone_setups = vigente
