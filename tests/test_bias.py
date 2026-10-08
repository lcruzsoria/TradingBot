from datetime import date

import numpy as np
import pandas as pd
import pytest

from tradingbot.skills.bias import Bias, BiasEngine, Direction, TradeFilter
from tradingbot.skills.bias.rules import AboveBelowOpen, PrevDayBreak
from tradingbot.skills.feed.datasource import normalize_candles


def make_candles(prev_range, today_open, today_close):
    """Dos días: el anterior oscila en prev_range=(low, high); hoy abre y cierra en los valores dados."""
    rows = []
    t0 = pd.Timestamp("2026-10-05 00:00")
    lo, hi = prev_range
    for i in range(4):  # día previo
        p = lo if i % 2 == 0 else hi
        rows.append((t0 + pd.Timedelta(minutes=15 * i), p, hi if i % 2 else p, lo if i % 2 == 0 else p, (lo + hi) / 2))
    t1 = pd.Timestamp("2026-10-06 00:00")
    rows.append((t1, today_open, max(today_open, today_close), min(today_open, today_close), today_close))
    df = pd.DataFrame(rows, columns=["time", "open", "high", "low", "close"])
    df["ts"] = df["time"].astype("datetime64[s]").astype("int64")
    df["tick_volume"] = 1
    return normalize_candles(df[["ts", "open", "high", "low", "close", "tick_volume"]])


def engine(**kw):
    return BiasEngine([PrevDayBreak(), AboveBelowOpen()], **kw)


def test_bullish_cuando_rompe_maximo_previo_y_sube():
    res = engine().evaluate(make_candles((1.0, 1.1), 1.10, 1.12))
    assert res.bias is Bias.BULLISH
    assert res.day == date(2026, 10, 6)
    assert res.allows(Direction.LONG) and not res.allows(Direction.SHORT)


def test_bearish_cuando_rompe_minimo_previo_y_baja():
    res = engine().evaluate(make_candles((1.0, 1.1), 1.0, 0.98))
    assert res.bias is Bias.BEARISH
    assert res.allows(Direction.SHORT) and not res.allows(Direction.LONG)


def test_no_bias_con_senales_opuestas():
    # rompe el máximo previo (alcista) pero cierra bajo la apertura (bajista)
    res = engine(min_score=2).evaluate(make_candles((1.0, 1.1), 1.20, 1.15))
    assert res.bias is Bias.NO_BIAS
    assert res.allows(Direction.LONG) and res.allows(Direction.SHORT)


def test_no_bias_dentro_del_rango_y_en_la_apertura():
    res = engine().evaluate(make_candles((1.0, 1.1), 1.05, 1.05))
    assert res.bias is Bias.NO_BIAS


def test_require_all_exige_unanimidad():
    # solo 'above_below_open' es alcista; 'prev_day_break' no opina
    candles = make_candles((1.0, 1.1), 1.04, 1.06)
    assert engine().evaluate(candles).bias is Bias.BULLISH
    assert engine(require_all=True).evaluate(candles).bias is Bias.NO_BIAS


def test_puntuacion_minima():
    candles = make_candles((1.0, 1.1), 1.04, 1.06)
    assert engine(min_score=2).evaluate(candles).bias is Bias.NO_BIAS


def test_pesos_de_las_reglas():
    # rompe el máximo previo pero cierra bajo la apertura: con pesos iguales se anulan...
    candles = make_candles((1.0, 1.1), 1.20, 1.15)
    assert BiasEngine([PrevDayBreak(weight=1), AboveBelowOpen()]).evaluate(candles).bias is Bias.NO_BIAS
    # ...con los pesos por defecto (ruptura 2, apertura 1) la puntuación es +2 - 1 = +1
    res = engine().evaluate(candles)
    assert res.bias is Bias.BULLISH and res.score == 1 and res.min_score == 1
    assert [(v.weight, v.points) for v in res.votes] == [(2, 2), (1, -1)]
    assert "puntuación +1" in res.summary
    # con la puntuación mínima del tradingbot.env (2), ese conflicto es No Bias: no se opera
    assert engine(min_score=2).evaluate(candles).bias is Bias.NO_BIAS
    # la ruptura sola (+2) basta; la apertura sola (+1), no
    assert engine(min_score=2).evaluate(make_candles((1.0, 1.1), 1.12, 1.12)).bias is Bias.BULLISH
    assert engine(min_score=2).evaluate(make_candles((1.0, 1.1), 1.04, 1.06)).bias is Bias.NO_BIAS


def test_sin_datos_es_no_bias():
    empty = make_candles((1.0, 1.1), 1.0, 1.0).iloc[0:0]
    assert BiasEngine([PrevDayBreak()]).evaluate(empty).bias is Bias.NO_BIAS


def test_una_regla_con_error_no_rompe_el_motor():
    class Rota(PrevDayBreak):
        def evaluate(self, ctx):
            raise RuntimeError("fallo")
    res = BiasEngine([Rota(), AboveBelowOpen()]).evaluate(make_candles((1.0, 1.1), 1.04, 1.06))
    assert res.bias is Bias.BULLISH
    assert any("Error" in v.detail for v in res.votes)


def test_from_config_y_regla_desconocida():
    cfg = {"min_score": 1, "rules": [{"type": "prev_day_break"}, {"type": "above_below_open", "enabled": False}]}
    assert len(BiasEngine.from_config(cfg).rules) == 1
    with pytest.raises(ValueError):
        BiasEngine.from_config({"rules": [{"type": "no_existe"}]})


def test_trade_filter():
    f = TradeFilter()
    assert f.check(Direction.LONG)[0] is False  # sin bias calculado no se opera
    f.update(engine().evaluate(make_candles((1.0, 1.1), 1.10, 1.12)))
    assert f.check(Direction.LONG)[0] is True
    allowed, reason = f.check(Direction.SHORT)
    assert allowed is False and "bloqueado" in reason
