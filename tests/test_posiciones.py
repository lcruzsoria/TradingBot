"""Seguimiento de las posiciones simuladas: stop, objetivo y cierre por tiempo."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import time
from datetime import date

import numpy as np
import pandas as pd
import pytest

from tradingbot.skills.cortex.order import Order
from tradingbot.skills.setup.positions import resolve, trackable

T0 = 1_000_000                       # hora de servidor de la vela de entrada
STEP = 900


def order(direction="long", entry=100.0, stop=99.0, target=102.0, close_after=4):
    return Order("NAS100.r", "15m", direction, "Calendario", "calendario", "", date(2026, 10, 12), entry, entry, entry, entry,
                 stop, target, "sin consultar", 0.0, "prueba", "10:00 NY", T0, T0 + close_after * STEP)


def bars(rows):
    """rows: lista de (high, low, close); una vela cada 15 min desde T0."""
    ts = np.array([T0 + i * STEP for i in range(len(rows))])
    h, l, c = (np.array([r[k] for r in rows], dtype=float) for k in range(3))
    return ts, h, l, c


def test_objetivo_stop_y_el_stop_va_primero():
    assert resolve(order(), *bars([(100.5, 99.5, 100), (102.5, 100, 102)])).result == "objetivo"
    cerrada = resolve(order(), *bars([(100.5, 98.5, 99)]))
    assert cerrada.result == "stop" and cerrada.r == -1.0 and cerrada.exit_price == 99.0
    assert resolve(order(), *bars([(102.5, 98.5, 100)])).result == "stop"           # caben los dos: cuenta el stop


def test_corto_se_resuelve_al_reves():
    o = order("short", stop=101.0, target=98.0)
    assert resolve(o, *bars([(100.5, 97.5, 98)])).r == pytest.approx(2.0)
    assert resolve(o, *bars([(101.5, 99.5, 101)])).r == -1.0


def test_cierre_por_tiempo_solo_con_una_vela_posterior():
    seguidas = [(100.5, 99.5, 100.2)] * 4                      # velas 0..3, antes de close_ts (T0 + 4 velas)
    assert resolve(order(), *bars(seguidas)) is None            # la última aún puede estar formándose
    cerrada = resolve(order(), *bars(seguidas + [(101, 100, 100.6)]))       # llega la vela de las 10:00
    assert cerrada.result == "tiempo" and cerrada.exit_price == 100.2 and cerrada.r == pytest.approx(0.2)
    assert cerrada.pct == pytest.approx(0.2) and cerrada.exit_ts == T0 + 3 * STEP


def test_ignora_las_velas_anteriores_a_la_entrada_y_sigue_abierta():
    ts, h, l, c = bars([(150, 50, 100)] + [(100.5, 99.5, 100)] * 2)
    o = Order(**{**order().__dict__, "entry_ts": T0 + STEP})
    assert resolve(o, ts, h, l, c) is None                      # el barrido de la vela 0 es anterior a la entrada


def test_solo_se_siguen_las_ordenes_con_horas():
    assert trackable(order())
    assert not trackable(Order(**{**order().__dict__, "entry_ts": None}))


def test_setup_cierra_la_posicion_con_las_velas_que_reenvia_cortex():
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.envconfig import EnvConfig, parse
    import tradingbot.skills  # noqa: F401
    bus, closed = EventBus(), []
    bus.subscribe("t", "setup.closed", closed.append)
    manager = SkillManager(bus, Services(None, None, {"app": {}}, EnvConfig(parse(""))), [{"type": "setup"}])
    manager.start()
    bus.publish("setup.order", {"order": order()}, source="cortex")
    time.sleep(0.2)
    assert len(manager.skills["setup"].positions) == 1
    df = pd.DataFrame(bars([(100.5, 99.5, 100), (102.5, 100, 102)]), index=["ts", "high", "low", "close"]).T
    bus.publish("setup.candles", {"symbol": "EURUSD", "timeframe": "15m", "df": df}, source="cortex")       # otro mercado
    time.sleep(0.2)
    assert closed == []
    bus.publish("setup.candles", {"symbol": "NAS100.r", "timeframe": "15m", "df": df}, source="cortex")
    time.sleep(0.3)
    manager.stop()
    assert len(closed) == 1 and closed[0].payload["closed"].result == "objetivo" and closed[0].payload["sent"] is False
    assert manager.skills["setup"].positions == []


def test_si_el_mercado_cierra_la_posicion_cierra_al_precio_de_cierre():
    o = order(close_after=500)
    ts, h, l, c = bars([(100.5, 99.5, 100.4), (100.8, 100.0, 100.6), (100.9, 100.2, 100.5)])
    ts[2] += 48 * 3600                                                    # fin de semana sin velas entre la 2.ª y la 3.ª
    cerrada = resolve(o, ts, h, l, c, bar_seconds=STEP)
    assert cerrada.result == "tiempo" and cerrada.exit_price == 100.6 and cerrada.exit_ts == int(ts[1])
    ts[2] = T0 + 2 * STEP + 3600                                          # parón de 1 h: el mercado sigue abierto
    assert resolve(o, ts, h, l, c, bar_seconds=STEP) is None


def test_si_el_mercado_esta_cerrado_ahora_cierra_con_la_ultima_vela():
    o = order(close_after=500)
    ts, h, l, c = bars([(100.5, 99.5, 100.4), (100.8, 100.0, 100.6)])
    assert resolve(o, ts, h, l, c, bar_seconds=STEP, now=T0 + 2 * STEP + 600) is None             # velas al día
    cerrada = resolve(o, ts, h, l, c, bar_seconds=STEP, now=T0 + 2 * STEP + 3 * 3600)
    assert cerrada.result == "tiempo" and cerrada.exit_price == 100.6


def test_el_cierre_guarda_el_maximo_a_favor_en_r():
    o = order(close_after=500)
    # entra en 100 con stop 99 (1 R): llega a 101.6 (1,6 R), el stop pasa a la entrada y vuelve a 100 -> breakeven con máx 1,6 R
    rows = [(101.6, 99.8, 101.2), (100.5, 99.9, 100.2), (100.2, 99.9, 100.0)]
    c = resolve(o, *bars(rows), be_r=1.0, bar_seconds=STEP)
    assert c.result == "breakeven" and c.max_r == pytest.approx(1.6)
    stop = resolve(order(), *bars([(100.4, 98.5, 99.0)]))
    assert stop.result == "stop" and stop.max_r == pytest.approx(0.4)               # llegó a +0,4 R y acabó en stop
    short = resolve(order("short", stop=101.0, target=98.0), *bars([(100.5, 99.2, 99.4), (100.0, 97.9, 98.0)]))
    assert short.result == "objetivo" and short.max_r == pytest.approx(2.1)           # corto: el mínimo manda


def test_el_maximo_se_guarda_en_el_diario_y_los_diarios_antiguos_se_leen(tmp_path):
    from datetime import date
    from tradingbot.skills.stats.journal import Journal
    from tradingbot.skills.setup.positions import Closed
    o = order()
    j = Journal(tmp_path)
    j.opened(o)
    j.closed(o, Closed("breakeven", 100.0, T0 + STEP, 0.0, 0.0, T0, 1.57))
    s = j.load_recent()
    assert s.trades[0].closed.max_r == 1.57
    old = tmp_path / "2026-10.jsonl"
    old.write_text(old.read_text(encoding="utf-8").replace(', "max_r": 1.57', ""), encoding="utf-8")   # diario de antes de este campo
    assert Journal(tmp_path).load_recent().trades[0].closed.max_r is None
