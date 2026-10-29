"""Patrón «Continuación»: rotura con cuerpo de la TBR en M15, fibonacci del swing high al swing low posterior y entrada en el 0,5."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pandas as pd
import pytest

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.pattern.continuacion import Continuacion, analyze
from tradingbot.skills.pattern.patterns import DETECTED, EXPIRED, INVALIDATED, PATTERN_REGISTRY, PatternContext

from tests.test_pattern import DAY, NY, TBR, ny, run_skill, session

# TBR 95-105. Velas M15 (open, high, low, close): 0-7 dentro de la TBR, 8 en adelante tras su cierre; swing_bars = 1 (tres velas).
ROWS = [(101, 103, 100, 102), (102, 103, 99, 100), (100, 101, 97, 98), (98, 100, 98, 99.5), (99.5, 102, 99, 101),
        (101, 102, 100, 101.5), (101.5, 103, 101, 102.5), (102.5, 104, 102, 103.5),
        (103.5, 104.5, 103, 104),      # 8: no rompe (cierra bajo el High)
        (104, 108, 103.5, 107),        # 9: ROTURA CON CUERPO (cierra sobre el High 105)
        (107, 111, 106.5, 109),        # 10: swing high (111): su máximo es el más alto de las tres velas 9, 10 y 11
        (109, 110.5, 105, 106),        # 11: confirma el swing high: el 0 es 111
        (106, 108, 103, 104),          # 12: swing low (103)
        (104, 109, 104, 108),          # 13: confirma el swing low: el 1 es 103 y el 0,5 es 107
        (108, 113, 107.5, 112),        # 14: supera el 0 (113 > 111): activa el tramo, sin tocar aún el 0,5
        (112, 114, 106, 107)]          # 15: retrocede al 0,5: entrada


def ctx_for(rows, first_bar=8, last_bar=None, closed=False, start_bar=0, tbr=TBR):
    o, h, l, c = (np.array(x, dtype=float) for x in zip(*rows))
    ts = ny(DAY, 10, 0) + np.arange(len(rows)) * 900
    return PatternContext("EURUSD", "15m", 15, ts, o, h, l, c, tbr, first_bar, len(rows) - 1 if last_bar is None else last_bar, closed,
                          "NY-PM", "13:30", 7 * 3600, start_bar)


def mirror(rows):
    return [(200 - o, 200 - l, 200 - h, 200 - c) for o, h, l, c in rows]


def test_alcista_fibo_del_swing_high_al_swing_low_posterior_y_entrada_en_el_05():
    hits, figs = analyze(ctx_for(ROWS), 1)
    assert len(hits) == 1
    h = hits[0]
    assert (h.key, h.status, h.direction, h.x, h.price) == ("continuacion", DETECTED, "long", 15, 107.0)    # entrada en el 0,5
    assert h.levels["stop"] == 103.0 and h.levels["target"] == 115.0                                      # swing low y -0,5: 2R
    assert (115 - 107) == pytest.approx((107 - 103) * 2)
    assert [f.kind for f in figs] == ["fib", "pos"]                                                       # el fibonacci y la posición
    f = figs[0]
    assert (f.kind, f.zone, f.direction, f.state) == ("fib", "NY Open", "long", "entrada")
    assert f.levels == {"-0,5": 115.0, "0": 111.0, "0,5": 107.0, "1": 103.0}
    assert f.x0_ts == int(ctx_for(ROWS).ts[10])                                                           # desde el swing high (la vela 10)


def test_bajista_es_el_espejo_exacto():
    hits, figs = analyze(ctx_for(mirror(ROWS)), 1)
    h = hits[0]
    assert (h.status, h.direction, h.x, h.price) == (DETECTED, "short", 15, 93.0)
    assert h.levels["stop"] == 97.0 and h.levels["target"] == 85.0
    assert figs[0].levels == {"-0,5": 85.0, "0": 89.0, "0,5": 93.0, "1": 97.0} and figs[0].direction == "short"


def test_el_fibo_se_dibuja_con_los_dos_swing_points_y_no_hay_entrada_hasta_que_retrocede():
    hits, figs = analyze(ctx_for(ROWS, last_bar=14), 1)                                                   # activado, sin retroceso aún
    assert hits == [] and len(figs) == 1 and figs[0].state == "en curso"
    assert figs[0].levels == {"-0,5": 115.0, "0": 111.0, "0,5": 107.0, "1": 103.0}                        # el tramo queda fijo
    hits, figs = analyze(ctx_for(ROWS, last_bar=13), 1)                                                   # swing low confirmado, sin activar
    assert hits == [] and figs[0].levels["1"] == 103.0 and figs[0].levels["0"] == 111.0
    assert analyze(ctx_for(ROWS, last_bar=11), 1) == ([], [])                                             # aún no hay swing low
    assert analyze(ctx_for(ROWS, last_bar=8), 1) == ([], [])                                              # sin rotura: nada


def test_entra_en_el_05_sin_necesidad_de_superar_antes_el_0():
    rows = ROWS[:14] + [(108, 110, 106, 107)]                              # toca el 0,5 (107) sin que su máximo supere el 0 (111)
    hits, figs = analyze(ctx_for(rows), 1)
    assert [(h.status, h.x, h.price) for h in hits] == [(DETECTED, 14, 107.0)] and figs[0].state == "entrada"


def test_sin_el_swing_del_1_formado_no_hay_trade():
    assert analyze(ctx_for(ROWS[:13]), 1) == ([], [])                      # el swing low (12) aún no está confirmado: no hay 1, no hay stop
    confirma = ROWS[:13] + [(109, 110, 106, 108)]                          # 13: confirma el swing low y toca el 0,5: basta para entrar
    assert [(h.status, h.x) for h in analyze(ctx_for(confirma), 1)[0]] == [(DETECTED, 13)]
    sin_tocar = ROWS[:13] + [(109, 110, 108, 109)]                         # 13: confirma el swing low sin llegar al 0,5 (107): aún no hay entrada
    assert analyze(ctx_for(sin_tocar), 1)[0] == []
    siguiente = sin_tocar + [(108, 110, 106.5, 109)]                       # 14: la primera que retrocede al 0,5 (abre sobre él)
    assert [(h.status, h.x) for h in analyze(ctx_for(siguiente), 1)[0]] == [(DETECTED, 14)]


def test_perder_el_1_antes_de_la_entrada_invalida_el_patron():
    rows = ROWS[:14] + [(108, 109, 101, 102)]                              # 14: pierde el 103 (mínimo 101) sin haber entrado
    hits, figs = analyze(ctx_for(rows), 1)
    assert [(h.status, h.x) for h in hits] == [(INVALIDATED, 14)] and [f.state for f in figs] == ["invalidada"]


def test_la_entrada_no_cruza_el_nivel_si_abre_por_debajo_del_05():
    rows = ROWS[:14] + [(105, 110, 104, 108)]                              # 14 abre en 105, ya por debajo del 0,5 (107): no es un retroceso
    assert analyze(ctx_for(rows), 1)[0] == []


def test_un_swing_high_mas_alto_antes_del_swing_low_sustituye_al_0():
    rows = ROWS[:9] + [(104, 108, 103.5, 107), (107, 111, 106.5, 109), (109, 110, 108, 109.5), (109.5, 113, 109, 112),
                       (112, 112.5, 108, 109), (109, 110, 105, 106), (106, 110, 106, 109)]
    # 10: swing high 111, 12: swing high más alto 113 (sin swing low entre medias), 14: swing low 105 confirmado en 15
    hits, figs = analyze(ctx_for(rows), 1)
    assert figs[0].levels["0"] == 113.0 and figs[0].levels["1"] == 105.0


def test_perder_el_1_con_el_tramo_activo_invalida_el_patron():
    rows = ROWS[:15] + [(112, 112.5, 102, 103)]                            # activado en la 14; la 15 pierde el 103 (y toca el 0,5)
    hits, figs = analyze(ctx_for(rows), 1)
    assert [(h.status, h.x) for h in hits] == [(INVALIDATED, 15)]
    assert hits[0].levels["fibo 0,5"] == 107.0 and [f.state for f in figs] == ["invalidada"]       # con el fibo formado: se dibuja y Cortex lo anota «I»


def test_una_mecha_sola_no_activa_la_tbr_solo_el_cuerpo():
    wick = ROWS[:9] + [(104, 108, 103.5, 104.5)]                         # el máximo supera el High pero cierra dentro
    assert analyze(ctx_for(wick), 1) == ([], [])


def test_una_toma_previa_con_mecha_de_cualquier_lado_bloquea_la_continuacion():
    pre = ROWS[:8] + [(103.5, 106, 103, 104)]                          # 8: toma el High con la mecha (106) y cierra dentro
    rows = pre + ROWS[9:]                                              # y después llega la rotura con cuerpo
    assert analyze(ctx_for(rows), 1) == ([], [])
    assert analyze(ctx_for(mirror(rows)), 1) == ([], [])               # y el espejo con el Low
    other = ROWS[:8] + [(103.5, 104.5, 94, 104)] + ROWS[9:]            # una mecha por el Low antes de romper el High también:
    assert analyze(ctx_for(other), 1) == ([], [])                      # lo primero que pasa en la TBR (mecha) la hace de Reversión


def test_swing_bars_cambia_que_cuenta_como_pivote():
    rows = ROWS[:9] + [(104, 108, 103.5, 107), (107, 111, 106.5, 109), (109, 110.5, 105, 106), (106, 108, 103, 104), (104, 109, 104, 108)]
    assert analyze(ctx_for(rows), 1)[1][0].levels["1"] == 103.0
    assert analyze(ctx_for(rows), 2) == ([], [])                           # con dos velas a cada lado aún no se confirma el swing low


def test_al_acabar_el_plazo_de_la_tbr_vence_con_el_motivo():
    no_break = analyze(ctx_for(ROWS[:9], closed=True), 1)[0][0]
    assert no_break.status == EXPIRED and "no hubo rotura con cuerpo" in no_break.detail and "NY-PM (13:30 NY)" in no_break.detail
    no_entry = analyze(ctx_for(ROWS[:15], closed=True), 1)[0][0]
    assert no_entry.status == EXPIRED and "sin reversión al 0,5" in no_entry.detail
    found, figures = analyze(ctx_for(ROWS[:15], closed=True), 1)                                           # setup formado que vence por tiempo:
    assert found[0].levels["fibo 0,5"] == 107.0 and [f.state for f in figures] == ["vencida"]            # lleva sus niveles (NO GO «T»)
    assert analyze(ctx_for(ROWS, closed=True), 1)[0][0].status == DETECTED                               # si revirtió a tiempo, vale


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
    assert p["timeframe"] == "15m" and p["hit"].direction == "long" and p["hit"].price == 107.0 and p["tbr"].zone == "NY Open"
    assert p["hit"].ts == ny(DAY, 10, 0) + 15 * 900
    figs = [f for f in updated[-1].payload["figures"] if f.kind == "fib"]
    assert len(figs) == 1 and figs[0].levels["1"] == 103.0 and updated[-1].payload["tfs"] == {"continuacion": "15m"}
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
    assert win.chart.fib_count == 1 and len(win.chart._fib_items) == 4 * 2                     # cuatro niveles con su etiqueta, sin título
    assert [t.toPlainText() for t in win.chart._fib_items[1::2]] == ["-0,5", "0", "0,5", "1"]       # el nivel, sin el precio
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


def test_el_grafico_dibuja_una_sola_entrada_por_tbr_la_que_opera_cortex(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.skills.pattern.patterns import Figure
    from tradingbot.ui.chart import NO_GO_OPACITY, NO_GO_PILL_OPACITY
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
    titles = lambda: [f["label"] for f in win.chart._fibs]                                      # noqa: E731
    assert titles() == ["NY Open ▲ Rev"] and win.chart._fibs[0]["decision"] == "GO"           # solo la que opera Cortex
    assert [p["label"] for p in win.chart._positions] == ["NY Open ▲ Rev"]
    assert all(item.opacity() == 1 for item in win.chart._fib_items)
    verdicts = {"long": ("NO GO", "Bearish -4"), "short": ("GO", "Bearish -4")}               # el largo va contra el sesgo
    monkeypatch.setattr(win, "_entry_decision", lambda index, direction: verdicts[direction])
    win._apply_fibs()
    assert titles() == ["NY Open ▼"] and [p["label"] for p in win.chart._positions] == ["NY Open ▼"]
    en_curso = Figure("fib", "otro", "NY Open", "long", ny(DAY, 11, 30), ny(DAY, 13, 0), {"0": 99.0, "0,5": 97.0, "1": 95.0},
                      "en curso", "NY Open ▲ Otro", day)
    win._on_pattern_updated({"symbol": "EURUSD", "timeframe": "5m", "tbr": None, "hits": [], "figures": figures + [en_curso]})
    assert titles() == ["NY Open ▼"]                                                          # la TBR ya dio su entrada
    monkeypatch.setattr(win, "_entry_decision", lambda index, direction: ("NO GO", "lateral +0"))
    win._apply_fibs()                                                                          # ninguna se opera: la primera, atenuada
    assert titles() == ["NY Open ▲ Rev"]
    items = win.chart._fib_items
    assert len(items) == 6 and all(item.opacity() == NO_GO_OPACITY for item in items)         # sus niveles, atenuados y sin título
    pill, = win.chart._pos_pills                                                                # la píldora: veredicto primero, resultado al final
    assert pill.opacity() == NO_GO_PILL_OPACITY and pill.toPlainText().strip().startswith("✕") and pill.result == "SL"
    assert pill.border.color().name().upper() == "#EF5350"                                       # borde rojo: saltó el stop


def test_la_posicion_se_dibuja_con_entrada_stop_y_objetivo_y_su_resultado():
    from tradingbot.skills.pattern.trade import outcome
    pos = analyze(ctx_for(ROWS), 1)[1][1]
    assert (pos.kind, pos.direction, pos.state) == ("pos", "long", "abierta")                              # aún no llega a 115 ni a 103
    assert pos.levels == {"entrada": 107.0, "stop": 103.0, "objetivo": 115.0} and pos.x0_ts == int(ctx_for(ROWS).ts[15])
    hits, figs = analyze(ctx_for(ROWS + [(107, 115.5, 106, 115)]), 1)                                      # la vela siguiente llega al objetivo
    assert figs[1].state == "objetivo"
    stop_first = ROWS + [(107, 116, 102.5, 105)]                                                            # caben objetivo y stop: cuenta el stop
    assert analyze(ctx_for(stop_first), 1)[1][1].state == "stop"
    h = np.array([105.0, 108.0, 120.0]); l = np.array([100.0, 99.0, 101.0])
    assert outcome(h, l, 0, "long", 98.0, 118.0) == ("target", 2) and outcome(h, l, 0, "short", 121.0, 99.5) == ("target", 1)
    assert outcome(h, l, 0, "long", 99.5, 150.0) == ("stop", 1) and outcome(h, l, 0, "long", 90.0, 150.0) == (None, 2)
    short = analyze(ctx_for(mirror(ROWS)), 1)[1][1]
    assert short.direction == "short" and short.levels == {"entrada": 93.0, "stop": 97.0, "objetivo": 85.0}


def test_el_grafico_dibuja_las_posiciones_como_tradingview_y_el_boton_las_apaga(tmp_path, monkeypatch):
    from PySide6.QtCore import QEvent
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
    assert len(win.chart._pos_items) == 2 + 1 + 1 + 1                                                       # dos zonas, el borde verde (TP), la línea de entrada y su píldora
    assert win.chart._pos_items[2].pen().color().name().upper() == "#26A69A"
    pill = win.chart._pos_pills[0]
    assert "NY Open ▲ 2.0R" in pill.toPlainText() and pill.result == "TP" and not win.chart._card.isVisible()   # el detalle, oculto
    win.chart.resize(800, 500)
    win.chart.getPlotItem().getViewBox().setXRange(0, 40, padding=0)
    win.chart.getPlotItem().getViewBox().setYRange(90, 120, padding=0)
    win.chart.getPlotItem().getViewBox().updateMatrix()
    center = pill.sceneBoundingRect().center()
    win.chart._mouse_moved(center)                                                                         # al pasar el ratón, la ficha
    card = win.chart._card
    assert card.isVisible() and "Largo" in card.toPlainText() and "116.5" in card.toPlainText()
    win.chart.leaveEvent(QEvent(QEvent.Type.Leave))
    assert not card.isVisible()
    click = type("Click", (), {"scenePos": lambda self: center})()
    win.chart._chart_clicked(click)                                                                          # al pulsar, se queda fija...
    win.chart.leaveEvent(QEvent(QEvent.Type.Leave))
    assert card.isVisible()
    win.chart._chart_clicked(click)                                                                          # ...hasta pulsarla otra vez
    assert not card.isVisible()
    vb = win.chart.getPlotItem().getViewBox()
    vb.setXRange(0, 14, padding=0)                                                              # la entrada (vela 12) pegada al eje
    vb.updateMatrix()
    assert pill.sceneBoundingRect().right() <= vb.sceneBoundingRect().right()                  # se corre a la izquierda: se ve entera
    assert pill.pos().x() < 12
    assert win.chart._positions[0]["x0"] == 12 and win.chart._positions[0]["x1"] > 12                      # 11:00 es la vela M5 número 12
    win.pos_btn.setChecked(False)
    assert win.chart.position_count == 0 and win.chart._pos_items == []
    win.pos_btn.setChecked(True)
    assert win.chart.position_count == 1
    win._on_candles({"df": df, "symbol": "GBPUSD", "timeframe": "5m", "seconds": 0.1})                    # otro activo: se olvidan
    assert win.chart.position_count == 0


def test_el_caso_a_ideal_y_el_b_flexible_disparan_y_se_identifican():
    ideal = analyze(ctx_for(ROWS[:14] + [(108, 110, 106, 107)]), 1)[0][0]                     # el swing low del stop (103) está dentro de la TBR 95-105
    assert ideal.status == DETECTED and ideal.variant == "A. Ideal" and "Caso A. Ideal" in ideal.detail
    flexible_rows = ROWS[:11] + [(109, 110.5, 107.2, 108), (108, 108.5, 106.2, 107.5), (107.5, 111, 107.2, 110), (110, 111, 108.2, 109)]
    # 12: swing low en 106,2 (por encima del High de la TBR: fuera del rango); 13: lo confirma; 14: retrocede al 0,5 (108,6)
    flexible = analyze(ctx_for(flexible_rows), 1)[0][0]
    assert flexible.status == DETECTED and flexible.variant == "B. Flexible" and "Caso B. Flexible" in flexible.detail


def test_el_caso_viaja_a_la_orden_al_diario_y_a_la_senal(tmp_path):
    from datetime import date
    from tradingbot.skills.cortex.order import build_order
    from tradingbot.skills.cortex.validation import Decision
    from tradingbot.skills.stats.journal import Journal
    from tradingbot.skills.setup.positions import Closed
    from types import SimpleNamespace
    from tradingbot.skills.pattern.patterns import PatternHit
    hit = PatternHit("continuacion", "Continuación", "long", 1, 100.0, "d", {"stop": 95.0, "target": 110.0}, 1_000, DETECTED, "B. Flexible")
    payload = {"symbol": "EURUSD", "timeframe": "15m", "hit": hit, "tbr": TBR}
    order = build_order(payload, Decision(True, "ok"), SimpleNamespace(bias=SimpleNamespace(value="Bullish"), score=4.0))
    assert order.caso == "B. Flexible"
    j = Journal(tmp_path)
    j.opened(order)
    j.closed(order, Closed("objetivo", 110.0, 2_000, 2.0, 1.0))
    back = Journal(tmp_path).load_recent().trades[0].order
    assert back.caso == "B. Flexible"                                                       # sobrevive al diario
    from tradingbot.skills.stats.skill import _signal
    assert _signal({"decision": Decision(True, "ok"), "hit": hit, "tbr": TBR, "symbol": "EURUSD", "timeframe": "15m"}).variant == "B. Flexible"


def test_tocar_el_extremo_contrario_de_la_tbr_sin_fibo_definido_invalida_el_setup():
    rows = ROWS[:12] + [(106, 107, 94, 100), (100, 109, 99, 108)]       # 12: el mínimo (94) toca el Low de la TBR (95) antes del swing low
    for r in (rows, mirror(rows)):
        hits, figs = analyze(ctx_for(r), 1)
        assert len(hits) == 1 and hits[0].status == INVALIDATED and hits[0].x == 12 and hits[0].levels
        assert "antes de definir el fibo" in hits[0].detail and figs == []


def test_tocar_el_extremo_contrario_con_el_fibo_ya_definido_no_cambia_nada():
    hits, _ = analyze(ctx_for(ROWS), 1)                                  # el 1 (103) se confirma antes de cualquier toque
    assert hits[0].status == DETECTED
