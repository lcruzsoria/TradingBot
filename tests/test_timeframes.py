import numpy as np
import pandas as pd
import pytest

import tradingbot.skills  # noqa: F401
from tradingbot.skills.feed.datasource import aggregate_candles, normalize_candles
from tradingbot.skills.feed.demo_data import DemoSource
from tradingbot.timeframes import DERIVED, NATIVE, TIMEFRAMES, base_timeframe, display_label, minutes, mt5_constant


def test_lista_de_timeframes_y_nombres_en_pantalla():
    assert list(TIMEFRAMES) == ["1m", "3m", "5m", "15m", "1h", "3h", "4h", "7h", "12h", "1d", "1w"]
    assert [display_label(k) for k in TIMEFRAMES] == ["M1", "M3", "M5", "M15", "H1", "H3", "H4", "H7", "H12", "1D", "1W"]
    assert minutes("7h") == 420 and minutes("1w") == 10080
    with pytest.raises(ValueError):
        minutes("2h")


def test_h7_es_derivado_y_el_resto_son_nativos_de_mt5():
    assert DERIVED == {"7h": "1h"} and base_timeframe("7h") == "1h" and base_timeframe("4h") == "4h"
    assert set(TIMEFRAMES) - set(NATIVE) == {"7h"}
    fake = type("M", (), {n: i for i, n in enumerate(NATIVE.values())})
    assert mt5_constant(fake, "1d") == list(NATIVE).index("1d")
    with pytest.raises(ValueError, match="no es un timeframe nativo"):
        mt5_constant(fake, "7h")


def hourly(days=3):
    ts = 1_700_006_400 - 1_700_006_400 % 86400 + np.arange(days * 24) * 3600      # desde medianoche
    price = 100 + np.arange(len(ts), dtype=float)
    return normalize_candles(pd.DataFrame({"ts": ts, "open": price, "high": price + 0.5, "low": price - 0.5,
                                           "close": price + 0.25, "tick_volume": 10}))


def test_agrupar_en_7h_alinea_con_la_medianoche_y_acorta_la_ultima_del_dia():
    df = hourly(2)
    out = aggregate_candles(df, 7 * 3600)
    day = df["ts"].iloc[0]
    assert list(out["ts"].iloc[:4] - day) == [0, 7 * 3600, 14 * 3600, 21 * 3600]    # 00, 07, 14, 21 h
    assert list(out["ts"].iloc[4:8] - day) == [86400 + h * 3600 for h in (0, 7, 14, 21)]   # cada día empieza de cero
    first = out.iloc[0]
    assert first["open"] == df["open"].iloc[0] and first["close"] == df["close"].iloc[6]
    assert first["high"] == df["high"].iloc[:7].max() and first["low"] == df["low"].iloc[:7].min()
    assert first["tick_volume"] == 70 and out.iloc[3]["tick_volume"] == 30           # la de 21-24 h solo tiene 3 velas
    assert out["tick_volume"].sum() == df["tick_volume"].sum()


def test_agrupar_en_dias_y_semanas():
    df = hourly(10)
    assert len(aggregate_candles(df, 86400)) == 10
    weeks = aggregate_candles(df, 604800, anchor=3 * 86400)       # semanas que empiezan en domingo
    assert (weeks["ts"] - 3 * 86400) .mod(604800).eq(0).all()
    assert weeks["tick_volume"].sum() == df["tick_volume"].sum()


@pytest.mark.parametrize("tf", list(TIMEFRAMES))
def test_la_fuente_demo_genera_todos_los_timeframes(tf):
    df = DemoSource().load_candles("EURUSD", tf)
    assert len(df) > 50 and df["ts"].is_monotonic_increasing and df["ts"].is_unique
    assert (df["high"] >= df[["open", "close"]].max(axis=1) - 1e-12).all()
    assert (df["low"] <= df[["open", "close"]].min(axis=1) + 1e-12).all()


def test_los_timeframes_largos_terminan_en_el_mismo_precio():
    d = DemoSource()
    closes = {tf: d.load_candles("EURUSD", tf)["close"].iloc[-1] for tf in ("1m", "15m", "1h", "7h", "1d", "1w")}
    assert max(closes.values()) - min(closes.values()) < 1e-9


def test_bias_no_se_calcula_con_velas_semanales_pero_si_con_diarias():
    import time
    from tradingbot.skills.bias import BiasEngine
    from tradingbot.core import EventBus, Services, SkillManager

    bus, events = EventBus(), []
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": []}}
    engine = BiasEngine.from_config({"rules": [{"type": "prev_day_break"}]})
    manager = SkillManager(bus, Services(DemoSource(), engine, cfg), [{"type": "feed", "slot": 0}, {"type": "bias", "slot": 1}])
    bus.subscribe("t", "*", events.append)
    manager.start()

    def wait(cond, timeout=5):
        end = time.time() + timeout
        while time.time() < end and not cond():
            time.sleep(0.02)
        return cond()

    try:
        bus.publish("feed.load", {"symbol": "EURUSD", "timeframe": "1d"}, source="ui")
        assert wait(lambda: any(e.topic == "bias.updated" for e in events))     # diarias: sí
        n = sum(e.topic == "bias.updated" for e in events)
        bus.publish("feed.load", {"symbol": "EURUSD", "timeframe": "1w"}, source="ui")
        assert wait(lambda: sum(e.topic == "candles.loaded" for e in events) == 2)
        time.sleep(0.4)
        assert sum(e.topic == "bias.updated" for e in events) == n               # semanales: se conserva el último
        assert manager.skills["bias"].caption == "sin velas semanales"
    finally:
        manager.stop()
