"""Skill Setup: continuación sobre una TBR (toma de liquidez, retest del 50 %, segunda ruptura, entrada límite)."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import time

import numpy as np
import pandas as pd

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.setup.setups import detect
from tradingbot.skills.tbr.zones import Zone, compute

from tests.test_tbr import AHEAD, candles

WINDOW = 96
# TBR 10:00-11:00 (velas 0-3): High 105, Low 95, 50 % = 100, rango 10.
BOX_H = [101, 105, 102, 101]
BOX_L = [99, 98, 95, 99]


def run(after_h, after_l, mirror=False, zones=None, window=WINDOW):
    """Detecta sobre la TBR más las velas `after_*`. `mirror`: precios espejo (200 - precio) para probar el corto."""
    highs, lows = BOX_H + list(after_h), BOX_L + list(after_l)
    if mirror:
        highs, lows = [200 - x for x in lows], [200 - x for x in highs]
    ts, high, low = candles(10, len(highs), highs=highs, lows=lows)
    sessions = compute(ts, high, low, [Zone("NY_AM", "NY-AM", 600, 660, "#00C853")], AHEAD, 15, days=1)
    return detect(sessions, high, low, window, zones)


def only(setups):
    assert len(setups) == 1
    return setups[0]


def test_largo_completo_hasta_el_objetivo():
    # 4: toma el High (106). 5: toca el 50 % (mín. 99,5). 6: rompe otra vez (107). 7: retest del High (llena). 8: objetivo.
    s = only(run([106, 104, 107, 106, 116], [101, 99.5, 102, 104, 110]))
    assert (s.direction, s.status, s.zone) == ("long", "target", "NY-AM")
    assert (s.entry, s.stop, s.target) == (105, 99.5, 115)           # stop: mínimo del paso 2; objetivo: nivel -1
    assert (s.sweep_x, s.retest_x, s.rebreak_x, s.fill_x, s.end_x) == (4, 5, 6, 7, 8)
    assert abs(s.rr - 10 / 5.5) < 1e-9
    assert (s.high, s.mid, s.low) == (105, 100, 95)


def test_orden_activa_y_entrada_en_curso_y_stop():
    armed = only(run([106, 104, 107, 108], [101, 99.5, 102, 106]))     # aún no vuelve al High: orden límite activa
    assert armed.status == "armed" and armed.fill_x is None and armed.label.endswith("orden límite activa")
    filled = only(run([106, 104, 107, 106], [101, 99.5, 102, 104]))    # llenada y sin resolver
    assert filled.status == "filled" and filled.fill_x == 7
    stop = only(run([106, 104, 107, 106, 106], [101, 99.5, 102, 104, 99]))   # cae bajo el mínimo del paso 2
    assert stop.status == "stop" and stop.end_x == 8


def test_si_en_una_vela_caben_stop_y_objetivo_cuenta_el_stop():
    s = only(run([106, 104, 107, 106, 116], [101, 99.5, 102, 104, 99]))
    assert s.status == "stop"


def test_sin_toque_del_50_no_hay_setup_y_espera():
    s = only(run([106, 105.5], [101, 101]))                            # nunca baja al 50 %
    assert s.status == "sweep" and s.retest_x is None
    s = only(run([106, 105.5, 107, 106], [101, 101, 102, 103]))        # rompe de nuevo, pero sin tocar el 50 %
    assert s.status == "sweep"
    caducado = only(run([106] + [105.5] * 10, [101] * 11, window=6))   # pasa la ventana sin tocar el 50 %
    assert caducado.status == "expired" and "50 %" in caducado.note


def test_espera_la_segunda_ruptura():
    s = only(run([106, 104, 103], [101, 99.5, 100.5]))
    assert s.status == "retest" and s.retest_x == 5 and s.entry is None


def test_se_invalida_si_toma_el_lado_contrario():
    s = only(run([106, 104], [101, 94]))                               # el retest baja del Low (95)
    assert s.status == "invalid" and "lado contrario" in s.note
    s = only(run([106, 104, 103, 107], [101, 99.5, 94, 102]))          # lo toma antes de la segunda ruptura
    assert s.status == "invalid"


def test_la_orden_caduca_si_el_precio_llega_al_objetivo_sin_llenarla():
    s = only(run([106, 104, 107, 116], [101, 99.5, 102, 109]))
    assert s.status == "expired" and "objetivo" in s.note


def test_corto_es_el_espejo():
    s = only(run([106, 104, 107, 106, 116], [101, 99.5, 102, 104, 110], mirror=True))
    assert (s.direction, s.status) == ("short", "target")
    assert (s.entry, s.stop, s.target) == (95, 100.5, 85)
    assert s.side == "low" and s.level == 95 and (s.high, s.low) == (105, 95)


def test_un_setup_por_tbr_y_lado_y_filtro_de_zonas():
    after_h, after_l = [106, 104, 107, 106, 116], [101, 99.5, 102, 104, 110]
    assert len(run(after_h, after_l)) == 1
    assert run(after_h, after_l, zones=["LONDON"]) == []
    assert len(run(after_h, after_l, zones=["ny_am"])) == 1


def run_skill(env_text):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus, events = EventBus(), []
    bus.subscribe("t", "setup.updated", events.append)
    manager = SkillManager(bus, Services(None, None, {"app": {}}, EnvConfig(parse(env_text))),
                           [{"type": "tbr"}, {"type": "setup"}])
    manager.start()
    highs, lows = BOX_H + [106, 104, 107, 108], BOX_L + [101, 99.5, 102, 106]
    ts, high, low = candles(10, len(highs), highs=highs, lows=lows)
    df = pd.DataFrame({"ts": ts, "high": high, "low": low, "close": np.asarray(low, dtype=float)})
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "15m", "df": df}, source="feed")
    deadline = time.time() + 3
    while not events and time.time() < deadline:
        time.sleep(0.02)
    manager.stop()
    return manager.skills["setup"], events


def test_la_skill_publica_los_setups_de_las_tbr():
    skill, events = run_skill("TBR_ZONES=ny_am\nTBR_NY_AM_HOURS=10:00-11:00\nTBR_DAYS=1\n")
    p = events[-1].payload
    assert p["symbol"] == "EURUSD" and p["last"].status == "armed" and p["last"].direction == "long"
    assert p["last"].entry == 105 and p["last"].target == 115 and p["bars"] == 8


def test_la_skill_rechaza_valores_no_validos():
    for text, key in (("SETUP_WINDOW_HOURS=0\n", "SETUP_WINDOW_HOURS"), ("SETUP_TP_RANGES=-1\n", "SETUP_TP_RANGES"),
                      ("SETUP_TYPES=reversal\n", "SETUP_TYPES")):
        skill, events = run_skill(text)
        assert skill.state.value == "error" and key in skill.note and not events
