"""Skill Calendario (largos a hora fija) y su paso por Cortex hasta Setup, en simulación."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import time
from datetime import datetime, timezone

import pandas as pd
import pytest

from tradingbot.envconfig import EnvConfig, parse

AHEAD = 7 * 3600                                  # servidor = NY + 7 h


def candles(ny_start: str, n: int = 8, step_min: int = 15) -> pd.DataFrame:
    """Velas M15 que empiezan a la hora de Nueva York dada, con la hora de servidor (+7 h) como marca."""
    t0 = int(datetime.fromisoformat(ny_start).replace(tzinfo=timezone.utc).timestamp()) + AHEAD
    ts = [t0 + i * step_min * 60 for i in range(n)]
    px = [100.0 + i for i in range(n)]
    return pd.DataFrame({"ts": ts, "open": px, "high": [p + 1 for p in px], "low": [p - 1 for p in px], "close": px})


def run(env_text="", skills=("calendario", "cortex", "setup")):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus = EventBus()
    out = {"signal": [], "order": [], "executed": []}
    bus.subscribe("t", "calendar.signal", out["signal"].append)
    bus.subscribe("t", "setup.order", out["order"].append)
    bus.subscribe("t", "setup.executed", out["executed"].append)
    manager = SkillManager(bus, Services(None, None, {"app": {}}, EnvConfig(parse(env_text))), [{"type": s} for s in skills])
    manager.start()
    bus.publish("clock.offset", {"server_offset": None, "offset_source": "test"}, source="quotes")   # None = +7 h estimado
    return manager, bus, out


def loaded(bus, df, symbol="NAS100.r", tf="15m"):
    bus.publish("candles.loaded", {"symbol": symbol, "timeframe": tf, "df": df}, source="feed")
    time.sleep(0.4)


def test_lunes_a_las_0200_da_senal_y_llega_simulada_a_setup():
    manager, bus, out = run()
    loaded(bus, candles("2026-10-12 01:30"))           # lunes 12/10/2026: velas 01:30...03:15, incluye la de las 02:00 (2 de las últimas)
    loaded(bus, candles("2026-10-12 01:45", n=2))      # la vela de las 02:00 es la última que se ve
    manager.stop()
    assert len(out["signal"]) == 1                    # no se repite para el mismo día
    s = out["signal"][0].payload
    assert s["symbol"] == "NAS100.r" and s["direction"] == "long" and s["price"] == 101.0
    assert s["stop"] == pytest.approx(101.0 * 0.995) and s["target"] == pytest.approx(101.0 * 1.01)
    o = out["executed"][0].payload["order"]
    assert o.pattern_key == "calendario" and o.tbr_zone == "" and "10:00 NY" in o.close_at
    assert out["executed"][0].payload["sent"] is False         # simulación: no se envía a MT5
    assert manager.skills["cortex"].caption in ("GO Long calendario", "NAS100.r: posición cerrada")      # cerrada si las velas ya la resuelven


def test_no_da_senal_otro_dia_otro_mercado_u_otra_hora():
    manager, bus, out = run()
    loaded(bus, candles("2026-10-13 01:45", n=2))                        # martes
    loaded(bus, candles("2026-10-12 01:45", n=2), symbol="EURUSD")       # mercado no configurado
    loaded(bus, candles("2026-10-12 03:00", n=2))                        # lunes, pero a las 03:00
    manager.stop()
    assert out["signal"] == [] and out["executed"] == []


def test_respeta_el_sufijo_del_broker_y_no_pasa_a_mayusculas():
    manager, bus, out = run("CALENDARIO_SYMBOLS=nas100ft\n")
    loaded(bus, candles("2026-10-12 01:45", n=2), symbol="NAS100FT.r")
    manager.stop()
    assert out["signal"][0].payload["symbol"] == "NAS100FT.r"


def test_con_calendar_use_bias_cortex_exige_sesgo():
    manager, bus, out = run("CORTEX_CALENDAR_USE_BIAS=true\n")
    loaded(bus, candles("2026-10-12 01:45", n=2))
    manager.stop()
    assert len(out["signal"]) == 1 and out["order"] == []           # sin sesgo calculado: NO GO
    assert manager.skills["cortex"].caption == "NO GO Long calendario"


@pytest.mark.parametrize("env", ["CALENDARIO_DAYS=sabado\n", "CALENDARIO_ENTRY_HOUR=25:00\n", "CALENDARIO_EXIT_HOUR=01:00\n",
                                 "CALENDARIO_STOP_PCT=0\n", "CALENDARIO_DIRECTION=short\n"])
def test_ajustes_no_validos_ponen_la_skill_en_error(env):
    manager, bus, out = run(env, skills=("calendario",))
    loaded(bus, candles("2026-10-12 01:45", n=2))
    manager.stop()
    assert manager.skills["calendario"].state.value == "error"


# -- entradas del backtest en el gráfico (perfil Calendario) ---------------------------------------------------------
def test_las_entradas_del_backtest_se_dibujan_solo_donde_hay_velas():
    import numpy as np
    from tradingbot.skills.calendario.chart import backtest_positions, market_key
    from tradingbot.skills.stats.backtest import Group

    def minutes(ny):                                          # minutos desde 1970 de una hora de NY
        return int(datetime.fromisoformat(ny).replace(tzinfo=timezone.utc).timestamp() // 60)

    raw = {"cats": {"m": ["NAS100.r", "SP500.r"], "o": ["objetivo", "stop", "tiempo"]}, "dias": [0], "hora": 2, "stop": 1.0,
           "rr": 2.0, "ops": {"m": [0, 0, 0, 1], "d": [0, 0, 1, 0], "o": [0, 2, 0, 0],
                              "e": [minutes("2026-10-19 02:00"), minutes("2026-10-12 02:00"), minutes("2026-10-19 02:00"),
                                    minutes("2026-10-19 02:00")],
                              "x": [minutes("2026-10-19 10:00")] * 3 + [minutes("2026-10-19 10:00")],
                              "r": [1.9, 0.1, -1, 1], "k": [0.0] * 4}}
    group = Group("calendario", "Calendario", raw)
    df = candles("2026-10-19 01:00", n=40)                    # 01:00-11:00: solo está cargado el lunes 19 (el 12 queda fuera)
    ts = df["ts"].to_numpy()
    out = backtest_positions(group, "NAS100.s", ts, df["open"].to_numpy(), df["high"].to_numpy(), df["low"].to_numpy(), AHEAD)
    assert len(out) == 1                                      # ni el lunes sin velas, ni el corto, ni otro mercado
    pos = out[0]
    assert ts[pos["x0"]] == int(datetime.fromisoformat("2026-10-19 02:00").replace(tzinfo=timezone.utc).timestamp()) + AHEAD
    assert pos["entry"] == 104.0 and pos["stop"] == pytest.approx(104 * 0.99) and pos["target"] == pytest.approx(104 * 1.02)
    assert pos["state"] == "objetivo" and pos["x1"] > pos["x0"] and pos["direction"] == "long"
    assert market_key("NAS100.r") == market_key("USTEC.s") == "nas100" and market_key("DJ30.r") == market_key("US30")
