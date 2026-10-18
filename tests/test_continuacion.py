"""Patrón «Continuación»: rotura con cuerpo de la TBR en M15, fibonacci desde el swing previo y entrada en el 0,5."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pandas as pd
import pytest

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.pattern.continuacion import Continuacion, analyze
from tradingbot.skills.pattern.patterns import DETECTED, EXPIRED, PATTERN_REGISTRY, PatternContext

from tests.test_pattern import DAY, NY, TBR, ny, run_skill, session

# TBR 95-105. Velas M15 (open, high, low, close): 0-7 dentro de la TBR (con un pivote bajo en la 2), 8 en adelante tras su cierre.
ROWS = [(101, 103, 100, 102), (102, 103, 99, 100), (100, 101, 97, 98), (98, 100, 98, 99.5), (99.5, 102, 99, 101),
        (101, 102, 100, 101.5), (101.5, 103, 101, 102.5), (102.5, 104, 102, 103.5),
        (103.5, 104.5, 103, 104),      # 8: no rompe (cierra bajo el High)
        (104, 108, 103.5, 107),        # 9: ROTURA CON CUERPO (cierra sobre el High 105)
        (107, 110, 106, 109),          # 10: el precio sigue (nuevo máximo, 110)
        (109, 109.5, 104, 105),        # 11: baja pero no llega al 0,5 (103,5)
        (105, 106, 103, 105)]          # 12: baja hasta el 0,5: entrada


def ctx_for(rows, first_bar=8, last_bar=None, closed=False, start_bar=0, tbr=TBR):
    o, h, l, c = (np.array(x, dtype=float) for x in zip(*rows))
    ts = ny(DAY, 10, 0) + np.arange(len(rows)) * 900
    return PatternContext("EURUSD", "15m", 15, ts, o, h, l, c, tbr, first_bar, len(rows) - 1 if last_bar is None else last_bar, closed,
                          "NY-PM", "13:30", 7 * 3600, start_bar)


def mirror(rows):
    return [(200 - o, 200 - l, 200 - h, 200 - c) for o, h, l, c in rows]


def test_alcista_rotura_con_cuerpo_swing_previo_fibo_y_entrada_en_el_05():
    hits, figs = analyze(ctx_for(ROWS), 2)
    assert len(hits) == 1
    h = hits[0]
    assert (h.key, h.status, h.direction, h.x, h.price) == ("continuacion", DETECTED, "long", 12, 103.5)    # entrada en el 0,5
    assert h.levels["stop"] == 97.0 and h.levels["target"] == 116.5                                       # swing y -0,5: 2R
    assert (110 - 103.5) * 2 == pytest.approx(116.5 - 103.5) and (103.5 - 97) * 2 == pytest.approx(13.0)
    assert [f.kind for f in figs] == ["fib", "pos"]                                                       # el fibonacci y la posición
    f = figs[0]
    assert (f.kind, f.zone, f.direction, f.state) == ("fib", "NY Open", "long", "entrada")
    assert f.levels == {"-0,5": 116.5, "0": 110.0, "0,5": 103.5, "1": 97.0}
    assert f.x0_ts == int(ctx_for(ROWS).ts[2])                                                            # desde el swing (la vela 2)


def test_bajista_es_el_espejo_exacto():
    hits, figs = analyze(ctx_for(mirror(ROWS)), 2)
    h = hits[0]
    assert (h.status, h.direction, h.x, h.price) == (DETECTED, "short", 12, 96.5)
    assert h.levels["stop"] == 103.0 and h.levels["target"] == 83.5
    assert figs[0].levels == {"-0,5": 83.5, "0": 90.0, "0,5": 96.5, "1": 103.0} and figs[0].direction == "short"


def test_fibo_en_curso_el_0_se_actualiza_hasta_que_revierte():
    hits, figs = analyze(ctx_for(ROWS, last_bar=10), 2)
    assert hits == [] and len(figs) == 1 and figs[0].state == "en curso"
    assert figs[0].levels["0"] == 110.0 and figs[0].levels["0,5"] == 103.5                                # el máximo sube a 110
    hits, figs = analyze(ctx_for(ROWS, last_bar=9), 2)
    assert hits == [] and figs[0].levels["0"] == 108.0 and figs[0].levels["0,5"] == 102.5                 # justo en la rotura
    assert hits == [] and analyze(ctx_for(ROWS, last_bar=8), 2) == ([], [])                              # sin rotura: nada


def test_una_mecha_sola_no_activa_la_tbr_solo_el_cuerpo():
    wick = ROWS[:9] + [(104, 108, 103.5, 104.5)]                         # el máximo supera el High pero cierra dentro
    assert analyze(ctx_for(wick), 2) == ([], [])
    body = ROWS[:9] + [(104, 106, 103.5, 105.1)]                         # cierra apenas por encima: rotura con cuerpo
    hits, figs = analyze(ctx_for(body), 2)
    assert hits == [] and figs[0].state == "en curso"


def test_sin_pivote_el_swing_es_el_minimo_mas_bajo_antes_de_la_rotura():
    rows = [(104, 105, 103, 104), (103, 104, 102, 103), (102, 103, 101, 102), (101.5, 102, 100, 101), (101, 108, 100.5, 107)]
    hits, figs = analyze(ctx_for(rows, first_bar=3), 2)
    assert figs[0].levels["1"] == 100.0 and figs[0].x0_ts == int(ctx_for(rows).ts[3])


def test_swing_bars_cambia_que_cuenta_como_pivote():
    lows = [100, 99, 97, 98, 99, 98.5, 99.5, 102, 103]
    rows = [(l + 2, l + 3, l, l + 1.5) for l in lows] + [(104, 108, 103.5, 107)]                  # rotura con cuerpo en la vela 9
    assert analyze(ctx_for(rows), 1)[1][0].levels["1"] == 98.5                                    # con 1 vela a cada lado, el último pivote es la 5
    assert analyze(ctx_for(rows), 2)[1][0].levels["1"] == 97.0                                    # con 2, la 5 ya no es pivote: el último es la 2


def test_al_acabar_el_plazo_de_la_tbr_vence_con_el_motivo():
    no_break = analyze(ctx_for(ROWS[:9], closed=True), 2)[0][0]
    assert no_break.status == EXPIRED and "no hubo rotura con cuerpo" in no_break.detail and "NY-PM (13:30 NY)" in no_break.detail
    no_entry = analyze(ctx_for(ROWS[:12], closed=True), 2)[0][0]
    assert no_entry.status == EXPIRED and "sin reversión al 0,5" in no_entry.detail
    assert analyze(ctx_for(ROWS[:12], closed=True), 2)[1] == []                                           # y ya no se dibuja
    assert analyze(ctx_for(ROWS, closed=True), 2)[0][0].status == DETECTED                               # si revirtió a tiempo, vale


def test_ajustes_del_patron():
    p = Continuacion(EnvConfig(parse("PATTERN_CONTINUACION_TF=M5\nPATTERN_CONTINUACION_SWING_BARS=3\n")).section("PATTERN"))
    assert (p.tf, p.swing_bars, p.timeframe()) == ("5m", 3, "5m")
    d = Continuacion()
    assert (d.tf, d.swing_bars) == ("15m", 1) and PATTERN_REGISTRY["continuacion"] is Continuacion
    for text, key in (("PATTERN_CONTINUACION_SWING_BARS=0\n", "SWING_BARS"), ("PATTERN_CONTINUACION_TF=2h\n", "Timeframe")):
        with pytest.raises(ValueError, match=key):
            Continuacion(EnvConfig(parse(text)).section("PATTERN"))


def m5_from_m15(rows, start=(10, 0)):
    """Cada vela M15 son tres M5 con los mismos extremos: (open), (high-low), (close)."""
    m5 = []
    for o, h, l, c in rows:
        m5 += [(o, o, o, o), (o, h, l, c), (c, c, c, c)]
    arr = np.array(m5, dtype=float)
    return pd.DataFrame({"ts": ny(DAY, *start) + np.arange(len(m5)) * 300, "open": arr[:, 0], "high": arr[:, 1], "low": arr[:, 2],
                         "close": arr[:, 3], "tick_volume": 1})


def test_la_skill_con_el_grafico_en_m5_agrupa_en_m15_y_publica_el_fibo():
    rows = ROWS + [(105, 106, 104, 105)]                                              # la última vela M15 sigue formándose
    manager, _bus, found, dropped, _s, updated = run_skill("PATTERN_TYPES=continuacion\n", df=m5_from_m15(rows))
    manager.stop()
    assert len(found) == 1 and dropped == []
    p = found[0].payload
    assert p["timeframe"] == "15m" and p["hit"].direction == "long" and p["hit"].price == 103.5 and p["tbr"].zone == "NY Open"
    assert p["hit"].ts == ny(DAY, 10, 0) + 12 * 900
    figs = [f for f in updated[-1].payload["figures"] if f.kind == "fib"]
    assert len(figs) == 1 and figs[0].levels["1"] == 97.0 and updated[-1].payload["tfs"] == {"continuacion": "15m"}
    assert manager.skills["pattern"].caption == "1 patrón(es) en NY Open"


def test_las_tbr_sin_activar_no_dejan_fibo():
    rows = ROWS[:9]                                                                    # ninguna rotura con cuerpo
    manager, _bus, found, dropped, _s, updated = run_skill("PATTERN_TYPES=continuacion\n", df=m5_from_m15(rows + [(104, 104.5, 103, 104)]))
    manager.stop()
    assert found == [] and updated[-1].payload["figures"] == []


def test_el_grafico_dibuja_los_fibo_y_el_boton_los_apaga(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.skills.pattern.patterns import Figure
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "5m", "watchlist": ["EURUSD", "GBPUSD"]}}
    win = MainWindow(EventBus(), SkillManager(EventBus(), Services(None, None, cfg, EnvConfig()), [{"type": "pattern"}]), cfg, "t")
    assert win.fibo_btn.text() == "Fibo" and win.fibo_btn.isChecked() and win.chart.fib_count == 0
    df = m5_from_m15(ROWS)
    df["time"] = pd.to_datetime(df["ts"], unit="s")
    win._on_candles({"df": df, "symbol": "EURUSD", "timeframe": "5m", "seconds": 0.1})
    fig = Figure("fib", "continuacion", "NY Open", "long", ny(DAY, 10, 30), ny(DAY, 13, 15),
                 {"-0,5": 116.5, "0": 110.0, "0,5": 103.5, "1": 97.0}, "entrada", "NY Open ▲")
    win._on_pattern_updated({"symbol": "EURUSD", "timeframe": "5m", "tbr": None, "hits": [], "figures": [fig]})
    assert win.chart.fib_count == 1 and len(win.chart._fib_items) == 4 * 2 + 1                 # cuatro niveles con su etiqueta y el título
    assert win.chart._fibs[0]["x0"] == 6 and win.chart._fibs[0]["x1"] > win.chart._fibs[0]["x0"]   # 10:30 es la vela M5 número 6
    win.fibo_btn.setChecked(False)
    assert win.chart.fib_count == 0 and win.chart._fib_items == []
    win.fibo_btn.setChecked(True)
    assert win.chart.fib_count == 1
    win._on_pattern_updated({"symbol": "EURUSD", "timeframe": "5m", "tbr": None, "hits": []})  # ya no hay figuras: se limpian
    assert win.chart.fib_count == 0
    win._on_pattern_updated({"symbol": "EURUSD", "timeframe": "5m", "tbr": None, "hits": [], "figures": [fig]})
    win._on_candles({"df": df, "symbol": "GBPUSD", "timeframe": "5m", "seconds": 0.1})         # otro activo: se olvidan
    assert win.chart.fib_count == 0


def test_la_segunda_entrada_de_una_sesion_se_ve_atenuada_y_tachada_con_su_no_go(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.skills.pattern.patterns import Figure
    from tradingbot.ui.chart import NO_GO_OPACITY
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "5m", "watchlist": ["EURUSD"]}}
    win = MainWindow(EventBus(), SkillManager(EventBus(), Services(None, None, cfg, EnvConfig()), [{"type": "pattern"}]), cfg, "t")
    monkeypatch.setattr(win, "_entry_decision", lambda index, direction: ("GO", "sin sesgo +1"))   # el sesgo dejaría pasar las dos
    df = m5_from_m15(ROWS)
    df["time"] = pd.to_datetime(df["ts"], unit="s")
    win._on_candles({"df": df, "symbol": "EURUSD", "timeframe": "5m", "seconds": 0.1})
    day = DAY.isoformat()
    figures = [Figure("fib", "reversion", "NY Open", "long", ny(DAY, 10, 0), ny(DAY, 12, 0), {"0": 104.0, "0,5": 100.0, "1": 96.0},
                      "entrada", "NY Open ▲ Rev"),
               Figure("pos", "reversion", "NY Open", "long", ny(DAY, 10, 30), ny(DAY, 10, 45),
                      {"entrada": 100.0, "stop": 96.0, "objetivo": 108.0}, "stop", "NY Open ▲ Rev", day),
               Figure("fib", "continuacion", "NY Open", "short", ny(DAY, 10, 15), ny(DAY, 13, 0), {"0": 92.0, "0,5": 98.0, "1": 104.0},
                      "entrada", "NY Open ▼"),
               Figure("pos", "continuacion", "NY Open", "short", ny(DAY, 11, 0), ny(DAY, 12, 0),
                      {"entrada": 98.0, "stop": 104.0, "objetivo": 86.0}, "objetivo", "NY Open ▼", day)]
    win._on_pattern_updated({"symbol": "EURUSD", "timeframe": "5m", "tbr": None, "hits": [], "figures": figures})
    rev, cont = win.chart._fibs
    assert rev["decision"] == "GO" and (cont["decision"], cont["reason"]) == ("NO GO", "sesión ya operada")
    items = win.chart._fib_items
    assert all(item.opacity() == 1 for item in items[:7])                                       # la que se opera, normal
    assert all(item.opacity() == NO_GO_OPACITY for item in items[7:13])                        # la otra, atenuada...
    assert "line-through" in items[13].toHtml() and "NO GO: sesión ya operada" in items[13].toPlainText()   # ...y tachada con el motivo
    assert [p["decision"] for p in win.chart._positions] == ["GO", "NO GO"]
    assert min(item.opacity() for item in win.chart._pos_items) == NO_GO_OPACITY


def test_el_pico_justo_antes_de_la_vela_de_rotura_es_el_swing_y_no_el_maximo_de_la_tbr():
    rows = [(100, 104, 99, 101), (101, 105, 100, 104),                      # 1: el máximo de la TBR (105)
            (104, 104.5, 101, 102), (102, 102.8, 100, 101),                 # dentro de la TBR
            (101, 102.5, 100, 102),                                         # primera vela tras el cierre
            (102, 103, 101, 101.5),                                         # 5: el pico inmediatamente anterior a la rotura (103)
            (101.5, 102, 93, 94)]                                           # 6: cierra bajo el Low (95): rotura con cuerpo
    hits, figs = analyze(ctx_for(rows, first_bar=4), 2)
    assert figs[0].direction == "short" and figs[0].levels["1"] == 103.0                                    # el 1 en el pico de la vela 5
    assert figs[0].x0_ts == int(ctx_for(rows).ts[5]) and figs[0].levels["0"] == 93.0
    long_rows = mirror(rows)
    assert analyze(ctx_for(long_rows, first_bar=4), 2)[1][0].levels["1"] == 97.0                            # y su espejo en el largo


def test_por_defecto_el_swing_es_el_patron_de_tres_velas():
    rows = [(100, 104, 99, 101), (101, 105, 100, 104), (104, 104.5, 101, 102), (102, 102.8, 100, 101), (101, 102.5, 100, 102),
            (102, 103, 101, 101.5), (101.5, 102, 93, 94)]
    # la vela 5 tiene el máximo más alto de las tres (4, 5 y 6): ese es el swing, aunque otras velas anteriores lleguen más arriba
    assert analyze(ctx_for(rows, first_bar=4), Continuacion().swing_bars)[1][0].levels["1"] == 103.0


PIVOTS = ROWS[:9] + [(104, 108, 103.5, 107),          # 9: rotura con cuerpo
                     (107, 109, 106.5, 108.5),        # 10: primer pivote: su máximo (109) es el más alto de las tres velas 9, 10 y 11
                     (108.5, 108.8, 107, 108),        # 11: confirma el pivote 10 (no toca el 0,5: 103)
                     (108, 111, 107.5, 110.5),        # 12: nuevo máximo...
                     (110.5, 110.9, 109, 109.5),      # 13: ...que se confirma como pivote más alto: el 0 pasa a 111 (0,5 = 104)
                     (109.5, 110, 103, 103.5),        # 14: baja hasta el 0,5: entrada
                     (103.5, 120, 103, 119)]          # 15: el precio sigue después (no mueve el 0 ya fijado)


def test_el_0_es_el_pivote_de_tres_velas_con_el_extremo_en_la_del_medio():
    hits, figs = analyze(ctx_for(PIVOTS), 1)
    assert [(h.status, h.x, h.price) for h in hits] == [(DETECTED, 14, 104.0)]                           # 0,5 de 97 a 111
    assert hits[0].levels["target"] == 118.0 and figs[0].levels["0"] == 111.0 and figs[0].levels["-0,5"] == 118.0
    hits, figs = analyze(ctx_for(PIVOTS, last_bar=11), 1)                                                # solo el primer pivote (109)
    assert hits == [] and figs[0].levels["0"] == 109.0 and figs[0].levels["0,5"] == 103.0
    sh, sf = analyze(ctx_for(mirror(PIVOTS)), 1)                                                         # el corto: el bajo más bajo en la del medio
    assert sh[0].direction == "short" and sf[0].levels["0"] == 89.0 and sf[0].levels["1"] == 103.0 and sh[0].price == 96.0


def test_la_vela_que_confirma_el_pivote_puede_ser_la_que_toca_el_05():
    rows = ROWS[:9] + [(104, 108, 103.5, 107), (107, 110, 106, 109), (109, 109.5, 103, 103.5)]
    hits, figs = analyze(ctx_for(rows), 1)
    assert [(h.status, h.x, h.price) for h in hits] == [(DETECTED, 11, 103.5)] and figs[0].levels["0"] == 110.0


def test_la_posicion_se_dibuja_con_entrada_stop_y_objetivo_y_su_resultado():
    from tradingbot.skills.pattern.trade import outcome
    pos = analyze(ctx_for(PIVOTS[:15]), 1)[1][1]
    assert (pos.kind, pos.direction, pos.state) == ("pos", "long", "abierta")                              # aún no llega a 118 ni a 97
    assert pos.levels == {"entrada": 104.0, "stop": 97.0, "objetivo": 118.0} and pos.x0_ts == int(ctx_for(PIVOTS).ts[14])
    assert analyze(ctx_for(PIVOTS), 1)[1][1].state == "objetivo"                                           # la vela 15 (máx. 120) lo alcanza
    hits, figs = analyze(ctx_for(PIVOTS[:15] + [(103.5, 118.5, 103, 118)]), 1)                              # la vela siguiente llega al objetivo
    assert figs[1].state == "objetivo" and figs[1].x1_ts == int(ctx_for(PIVOTS[:15] + [(0, 0, 0, 0)]).ts[15]) + 900
    stop_first = PIVOTS[:15] + [(103.5, 119, 96, 100)]                                                      # caben objetivo y stop: cuenta el stop
    assert analyze(ctx_for(stop_first), 1)[1][1].state == "stop"
    h = np.array([105.0, 108.0, 120.0]); l = np.array([100.0, 99.0, 101.0])
    assert outcome(h, l, 0, "long", 98.0, 118.0) == ("target", 2) and outcome(h, l, 0, "short", 121.0, 99.5) == ("target", 1)
    assert outcome(h, l, 0, "long", 99.5, 150.0) == ("stop", 1) and outcome(h, l, 0, "long", 90.0, 150.0) == (None, 2)
    short = analyze(ctx_for(mirror(PIVOTS)), 1)[1][1]
    assert short.direction == "short" and short.levels == {"entrada": 96.0, "stop": 103.0, "objetivo": 82.0}


def test_el_grafico_dibuja_las_posiciones_como_tradingview_y_el_boton_las_apaga(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.skills.pattern.patterns import Figure
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "5m", "watchlist": ["EURUSD", "GBPUSD"]}}
    win = MainWindow(EventBus(), SkillManager(EventBus(), Services(None, None, cfg, EnvConfig()), [{"type": "pattern"}]), cfg, "t")
    assert win.pos_btn.text() == "Entradas" and win.pos_btn.isChecked() and win.chart.position_count == 0
    df = m5_from_m15(ROWS)
    df["time"] = pd.to_datetime(df["ts"], unit="s")
    win._on_candles({"df": df, "symbol": "EURUSD", "timeframe": "5m", "seconds": 0.1})
    pos = Figure("pos", "continuacion", "NY Open", "long", ny(DAY, 11, 0), ny(DAY, 12, 30),
                 {"entrada": 103.5, "stop": 97.0, "objetivo": 116.5}, "objetivo", "NY Open ▲")
    win._on_pattern_updated({"symbol": "EURUSD", "timeframe": "5m", "tbr": None, "hits": [], "figures": [pos]})
    assert win.chart.position_count == 1 and win.chart.fib_count == 0
    assert len(win.chart._pos_items) == 2 + 1 + 3                                                           # dos zonas, la línea de entrada y tres etiquetas
    assert win.chart._positions[0]["x0"] == 12 and win.chart._positions[0]["x1"] > 12                      # 11:00 es la vela M5 número 12
    win.pos_btn.setChecked(False)
    assert win.chart.position_count == 0 and win.chart._pos_items == []
    win.pos_btn.setChecked(True)
    assert win.chart.position_count == 1
    win._on_candles({"df": df, "symbol": "GBPUSD", "timeframe": "5m", "seconds": 0.1})                    # otro activo: se olvidan
    assert win.chart.position_count == 0
