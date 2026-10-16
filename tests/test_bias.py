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


# -- reglas TDO y Midnight ---------------------------------------------------------------------------------
from tradingbot.skills.bias.rules import AboveBelowMidnight, AboveBelowTdo   # noqa: E402


def test_regla_tdo_vota_segun_el_precio_y_el_nivel():
    candles = make_candles((1.0, 1.1), 1.04, 1.06)                       # el último precio es 1,06
    sobre = BiasEngine([AboveBelowTdo()]).evaluate(candles, levels={"tdo": 1.05})
    assert sobre.votes[0].vote == 1 and "sobre el TDO" in sobre.votes[0].detail and sobre.levels["TDO"] == 1.05
    bajo = BiasEngine([AboveBelowTdo()]).evaluate(candles, levels={"tdo": 1.08})
    assert bajo.votes[0].vote == -1 and "bajo el TDO" in bajo.votes[0].detail
    en_nivel = BiasEngine([AboveBelowTdo(tolerance_pct=1)]).evaluate(candles, levels={"tdo": 1.055})
    assert en_nivel.votes[0].vote == 0                                   # dentro de la zona neutra
    sin = BiasEngine([AboveBelowTdo()]).evaluate(candles)
    assert sin.votes[0].vote == 0 and "Sin TDO" in sin.votes[0].detail


def test_regla_midnight_no_vota_hasta_que_existe():
    candles = make_candles((1.0, 1.1), 1.04, 1.06)
    antes = BiasEngine([AboveBelowMidnight()]).evaluate(candles, levels={"tdo": 1.05})
    assert antes.votes[0].vote == 0 and "Aún no hay Midnight" in antes.votes[0].detail
    despues = BiasEngine([AboveBelowMidnight()]).evaluate(candles, levels={"tdo": 1.05, "midnight": 1.1})
    assert despues.votes[0].vote == -1 and despues.levels["Midnight"] == 1.1


def test_tdo_y_midnight_juntos_dan_sesgo_y_opuestos_se_anulan():
    candles = make_candles((1.0, 1.1), 1.04, 1.06)
    eng = BiasEngine([AboveBelowTdo(), AboveBelowMidnight()], min_score=2)
    assert eng.evaluate(candles, levels={"tdo": 1.0, "midnight": 1.03}).bias is Bias.BULLISH      # +1 +1
    assert eng.evaluate(candles, levels={"tdo": 1.0, "midnight": 1.09}).bias is Bias.NO_BIAS      # +1 -1
    assert eng.evaluate(candles, levels={"tdo": 1.09, "midnight": 1.08}).bias is Bias.BEARISH     # -1 -1
    # con la ruptura del día anterior (peso 2) por delante de ambos
    full = BiasEngine([PrevDayBreak(), AboveBelowTdo(), AboveBelowMidnight()], min_score=2)
    assert full.evaluate(make_candles((1.0, 1.1), 1.10, 1.12), levels={"tdo": 1.0, "midnight": 1.11}).score == 4        # +2 +1 +1


def test_la_skill_bias_recalcula_cuando_llegan_los_niveles_del_dia():
    import time
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.envconfig import EnvConfig
    from tradingbot.skills.levels.daylevels import Line
    import tradingbot.skills  # noqa: F401
    bus, events = EventBus(), []
    bus.subscribe("t", "bias.updated", events.append)
    engine_ = BiasEngine([PrevDayBreak(), AboveBelowTdo(), AboveBelowMidnight()], min_score=2)
    manager = SkillManager(bus, Services(None, engine_, {"app": {}}, EnvConfig()), [{"type": "bias"}])
    manager.start()
    df = make_candles((1.0, 1.1), 1.04, 1.06)
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "15m", "df": df}, source="feed")
    deadline = time.time() + 3
    while not events and time.time() < deadline:
        time.sleep(0.02)
    assert events[-1].payload["result"].votes[1].detail.startswith("Sin TDO")       # aún sin niveles
    lines = [Line("tdo", 1.0, 0, 9), Line("midnight", 1.03, 4, 9), Line("tdo", 1.05, 20, 30), Line("midnight", 1.09, 12, 30)]
    bus.publish("levels.updated", {"symbol": "EURUSD", "timeframe": "15m", "lines": lines, "days": [], "day_start": 1020,
                                   "available": True}, source="levels")
    while len(events) < 2 and time.time() < deadline:
        time.sleep(0.02)
    manager.stop()
    p = events[-1].payload
    assert p["reason"].startswith("niveles del día")
    votes = p["result"].votes
    # el TDO de hoy es el último (1,05); el Midnight válido es el posterior a él: ninguno (el de x0=12 es de ayer)
    assert votes[1].vote == 1 and "1.05" in votes[1].detail
    assert votes[2].vote == 0 and "Aún no hay Midnight" in votes[2].detail


# -- barrido de la vela anterior (H3 / H4) ------------------------------------------------------------------------
from tradingbot.skills.bias.htf import htf_blocks, htf_sweep, sweep_vote      # noqa: E402
from tradingbot.skills.bias.rules import HtfSweepRule                         # noqa: E402

AHEAD_H = 7 * 3600
NY_START = int(pd.Timestamp("2026-10-06 17:00").timestamp())                  # 17:00 NY (como época ingenua)


def htf_frame(blocks, hours=4, tf_min=15):
    """Velas M15 de bloques de `hours` horas desde las 17:00 NY; cada bloque = (high, low, close): high y low en la primera
    y la segunda vela, y el cierre en la última."""
    rows, n = [], hours * 60 // tf_min
    for b, (hi, lo, cl) in enumerate(blocks):
        for i in range(n):
            ts = NY_START + b * hours * 3600 + i * tf_min * 60 + AHEAD_H
            h = hi if i == 0 else lo + 0.5 if i == 1 else cl
            l = lo if i == 1 else hi - 0.5 if i == 0 else cl
            rows.append((ts, cl, max(h, cl), min(l, cl), cl))
    return pd.DataFrame(rows, columns=["ts", "open", "high", "low", "close"])


def test_voto_de_barrido_de_la_vela_anterior():
    assert sweep_vote(105, 95, 107, 98, 101)[0] == -1       # barre el High y cierra dentro: bajista
    assert sweep_vote(105, 95, 102, 93, 99)[0] == 1         # barre el Low y cierra dentro: alcista
    assert sweep_vote(105, 95, 107, 98, 106)[0] == 0        # barre el High pero cierra fuera: ruptura
    assert sweep_vote(105, 95, 102, 93, 94)[0] == 0         # barre el Low pero cierra fuera
    assert sweep_vote(105, 95, 107, 93, 100)[0] == 0        # barre los dos lados
    assert sweep_vote(105, 95, 104, 96, 100)[0] == 0        # no barre ninguno
    assert sweep_vote(105, 95, 107, 98, 105)[0] == -1       # cerrar justo en el High anterior cuenta como dentro


def test_el_sesgo_de_la_vela_actual_usa_la_n1_y_la_n2():
    # n-2: 95-105; n-1: barre el High (107) y cierra en 101; vela 0 (en curso): da igual lo que haga
    df = htf_frame([(105, 95, 100), (107, 98, 101), (120, 80, 110)])
    r = htf_sweep(df, AHEAD_H, 17 * 60, 4, 15)
    assert r.vote == -1 and "bajista" in r.detail and "21:00" in r.detail and "17:00" in r.detail
    alcista = htf_sweep(htf_frame([(105, 95, 100), (102, 93, 99), (110, 90, 100)]), AHEAD_H, 17 * 60, 4, 15)
    assert alcista.vote == 1 and "alcista" in alcista.detail
    # la vela en curso no cuenta: con solo dos velas no hay sesgo aunque la segunda barra el High
    assert htf_sweep(htf_frame([(105, 95, 100), (107, 98, 101)]), AHEAD_H, 17 * 60, 4, 15).vote == 0


def test_velas_h3_en_indices_alineadas_con_las_18_ny():
    t0, hi, lo, cl = htf_blocks(htf_frame([(105, 95, 100), (107, 98, 101)], hours=3)["ts"].to_numpy(),
                                [1] * 24, [1] * 24, [1] * 24, AHEAD_H, 18 * 60, 3)
    # los datos empiezan a las 17:00 NY: el primer bloque H3 es el de las 15:00 (parcial) y los siguientes empiezan a las 18:00
    assert [pd.Timestamp(int(x), unit="s").strftime("%H:%M") for x in t0] == ["15:00", "18:00", "21:00"][:len(t0)]


def test_el_timeframe_del_grafico_mayor_que_el_bloque_no_vota():
    df = htf_frame([(105, 95, 100), (107, 98, 101), (110, 90, 100)], hours=4, tf_min=60)
    assert htf_sweep(df, AHEAD_H, 17 * 60, 3, 240).vote == 0


def test_regla_htf_sweep_vota_y_el_sesgo_la_usa():
    candles = make_candles((1.0, 1.1), 1.04, 1.06)
    bajista = BiasEngine([HtfSweepRule()]).evaluate(candles, htf=htf_sweep(
        htf_frame([(105, 95, 100), (107, 98, 101), (110, 90, 100)]), AHEAD_H, 17 * 60, 4, 15))
    assert bajista.votes[0].vote == -1 and bajista.votes[0].weight == 2 and bajista.bias is Bias.BEARISH
    sin = BiasEngine([HtfSweepRule()]).evaluate(candles)
    assert sin.votes[0].vote == 0 and sin.bias is Bias.NO_BIAS


def test_la_skill_bias_evalua_el_barrido_de_la_vela_anterior():
    import time
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.envconfig import EnvConfig
    import tradingbot.skills  # noqa: F401
    bus, events = EventBus(), []
    bus.subscribe("t", "bias.updated", events.append)
    manager = SkillManager(bus, Services(None, BiasEngine([HtfSweepRule()]), {"app": {}}, EnvConfig()), [{"type": "bias"}])
    manager.start()
    df = htf_frame([(105, 95, 100), (107, 98, 101), (110, 90, 100)])
    df["time"], df["tick_volume"] = pd.to_datetime(df["ts"], unit="s"), 1
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "15m", "df": df}, source="feed")   # no es índice: H4
    deadline = time.time() + 3
    while not events and time.time() < deadline:
        time.sleep(0.02)
    manager.stop()
    result = events[-1].payload["result"]
    assert result.votes[0].vote == -1 and result.bias is Bias.BEARISH and "H4" in result.votes[0].detail


# -- continuación de la vela anterior (n-1 cierra fuera del rango de la n-2) ------------------------------------------
from tradingbot.skills.bias.htf import break_vote, htf_break                   # noqa: E402
from tradingbot.skills.bias.rules import HtfBreakRule                          # noqa: E402


def test_voto_de_continuacion_de_la_vela_anterior():
    assert break_vote(105, 95, 107, 98, 106)[0] == 1 and "alcista" in break_vote(105, 95, 107, 98, 106)[1]   # cierra sobre el High
    assert break_vote(105, 95, 102, 90, 94)[0] == -1 and "bajista" in break_vote(105, 95, 102, 90, 94)[1]    # cierra bajo el Low
    assert break_vote(105, 95, 106, 98, 105)[0] == 0       # cerrar justo en el High no es cerrar por encima
    assert break_vote(105, 95, 104, 96, 100)[0] == 0       # interna a la n-2: sin sesgo
    assert break_vote(105, 95, 108, 92, 107)[0] == 0       # barre los dos lados con mecha: sin sesgo aunque cierre fuera
    assert break_vote(105, 95, 108, 92, 93)[0] == 0 and "el High y el Low" in break_vote(105, 95, 108, 92, 93)[1]


def test_la_continuacion_usa_la_n1_y_la_n2_y_complementa_al_barrido():
    # n-2: 95-105. n-1 cierra en 108: continuación alcista (aunque su máximo supere el High, no cerró dentro: sin barrido)
    df = htf_frame([(105, 95, 100), (110, 98, 108), (120, 80, 110)])
    brk = htf_break(df, AHEAD_H, 17 * 60, 4, 15)
    assert brk.vote == 1 and "alcista" in brk.detail and "21:00" in brk.detail
    assert htf_sweep(df, AHEAD_H, 17 * 60, 4, 15).vote == 0                    # cerrar fuera: el barrido no puntúa
    bajista = htf_break(htf_frame([(105, 95, 100), (102, 90, 92), (110, 90, 100)]), AHEAD_H, 17 * 60, 4, 15)
    assert bajista.vote == -1 and "bajista" in bajista.detail
    # cerrar dentro: puntúa el barrido, no la continuación
    dentro = htf_frame([(105, 95, 100), (107, 98, 101), (110, 90, 100)])
    assert htf_break(dentro, AHEAD_H, 17 * 60, 4, 15).vote == 0 and htf_sweep(dentro, AHEAD_H, 17 * 60, 4, 15).vote == -1
    assert htf_break(htf_frame([(105, 95, 100), (107, 98, 101)]), AHEAD_H, 17 * 60, 4, 15).vote == 0   # faltan velas
    envolvente = htf_frame([(105, 95, 100), (110, 90, 108), (110, 90, 100)])      # la n-1 barre los dos lados y cierra sobre el High
    assert htf_break(envolvente, AHEAD_H, 17 * 60, 4, 15).vote == 0 and htf_sweep(envolvente, AHEAD_H, 17 * 60, 4, 15).vote == 0
    interna = htf_frame([(105, 95, 100), (103, 97, 100), (110, 90, 100)])         # la n-1 es interna a la n-2
    assert htf_break(interna, AHEAD_H, 17 * 60, 4, 15).vote == 0 and htf_sweep(interna, AHEAD_H, 17 * 60, 4, 15).vote == 0


def test_regla_htf_break_vota_y_la_skill_la_usa():
    import time
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.envconfig import EnvConfig
    import tradingbot.skills  # noqa: F401
    candles = make_candles((1.0, 1.1), 1.04, 1.06)
    df = htf_frame([(105, 95, 100), (110, 98, 108), (120, 80, 110)])
    res = BiasEngine([HtfBreakRule()]).evaluate(candles, htf_break=htf_break(df, AHEAD_H, 17 * 60, 4, 15))
    assert res.votes[0].vote == 1 and res.votes[0].weight == 2 and res.bias is Bias.BULLISH
    assert BiasEngine([HtfBreakRule()]).evaluate(candles).votes[0].vote == 0
    bus, events = EventBus(), []
    bus.subscribe("t", "bias.updated", events.append)
    manager = SkillManager(bus, Services(None, BiasEngine([HtfSweepRule(), HtfBreakRule()]), {"app": {}}, EnvConfig()),
                           [{"type": "bias"}])
    manager.start()
    df["time"], df["tick_volume"] = pd.to_datetime(df["ts"], unit="s"), 1
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "15m", "df": df}, source="feed")
    deadline = time.time() + 3
    while not events and time.time() < deadline:
        time.sleep(0.02)
    manager.stop()
    votes = events[-1].payload["result"].votes
    assert [v.vote for v in votes] == [0, 1] and "continuación alcista" in votes[1].detail     # no puntúan a la vez
