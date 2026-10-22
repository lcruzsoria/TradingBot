"""Backtest de los patrones (scripts/backtest_patrones.py): la simulación de cada operación, con el breakeven del bot."""
import importlib.util
from pathlib import Path

import numpy as np

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def load_script():
    import sys
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("backtest_patrones", SCRIPTS / "backtest_patrones.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bars(*rows):
    h, l, c = (np.array(x, dtype=float) for x in zip(*rows))
    return h, l, c


def test_el_breakeven_pasa_el_stop_a_la_entrada_tras_un_cierre_a_1r_y_cierra_a_cero():
    sim = load_script().simulate
    h, l, c = bars((101, 99.5, 100.5), (103, 100.5, 102.5), (102, 99.8, 100.5), (101, 99, 100))      # largo: entrada 100, stop 99, 2R = 102
    assert sim(h, l, c, 0, "long", 100.0, 99.0, 102.0, 10) == ("objetivo", 1, 2.0, 0.5, 3.0)           # sin breakeven: el objetivo va antes
    h, l, c = bars((101, 99.5, 101.2), (101.5, 100.2, 101), (101, 99.9, 100.5), (101, 99, 100))
    res = sim(h, l, c, 0, "long", 100.0, 99.0, 102.0, 10, be_r=1.0)                                    # la vela 0 cierra a +1,2 R
    assert res[:3] == ("breakeven", 2, 0.0)                                                            # la 2 toca la entrada (99,9 <= 100)
    assert sim(h, l, c, 0, "long", 100.0, 99.0, 102.0, 10)[0] == "stop"                                # sin breakeven acaba en stop (la vela 3)


def test_el_breakeven_corto_es_el_espejo_y_no_se_activa_con_una_mecha_sin_cierre():
    sim = load_script().simulate
    h, l, c = bars((100.5, 98.5, 99.5), (101, 99, 100.2))                                              # corto: entrada 100, stop 101
    assert sim(h, l, c, 0, "short", 100.0, 101.0, 98.0, 10, be_r=1.0)[0] == "stop"                     # la mecha llegó a 98,5 pero no cerró a +1 R
    h, l, c = bars((100.5, 98.5, 98.9), (100.1, 99, 99.5))
    assert sim(h, l, c, 0, "short", 100.0, 101.0, 98.0, 10, be_r=1.0)[:3] == ("breakeven", 1, 0.0)    # cierra a +1,1 R y luego vuelve a la entrada
