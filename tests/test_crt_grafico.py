"""Botón CRT del perfil CRT: marca en el gráfico los CRT del backtest, con su etiqueta y la ficha al pasar el ratón."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crt_scenarios import AHEAD, scenario                                           # noqa: E402
from tradingbot.skills.stats.backtest import Backtest, Group                        # noqa: E402

C2 = int(pd.Timestamp("2026-10-13 06:00").value // 10**9 // 60)                     # inicio de C2 (minutos, hora NY)
D1_FVG = int(pd.Timestamp("2026-10-12 12:00").value // 10**9 // 60)                 # primera vela del FVG de M15 (minutos, hora NY)


def raw(ops: list[tuple]) -> dict:
    """Operaciones CRT en NAS100: (inicio de C2, dirección 0 largo / 1 corto, LTF, entrada, resultado, máscara de FVG de MTF)."""
    keys = ("c", "d", "l", "n", "o", "t", "m", "q", "z", "e", "x", "r", "k", "h", "pe", "ps", "pt", "pa", "pb", "pc", "ti", "tv", "tj", "th", "tq", "tt",
            "f15a", "f15b", "f15t")
    cols = {k: [] for k in keys}
    for c2, d, ltf, entry, out, mtf in ops:
        # el corto del escenario: entra en 103.1 a las 06:55 (C2 + 55 min), stop 108.5 (extremo de las 06:35), objetivo 92.3, iFVG 106.1-107.3
        # (de las 06:25 a la inversión de las 06:45), CISD en 103.2 a las 06:50 con la secuencia desde las 06:15
        vals = (c2, d, ltf, entry, out, mtf, 0, 2, 3, c2 + 55, c2 + 70, 1.9, 0.1, -1, 103.1, 108.5, 92.3, 106.1, 107.3, 103.2,
                c2 + 25, c2 + 45, c2 + 50, c2 + 35, c2 + 15, c2 + 35,
                107.5, 110.0, D1_FVG)                                                              # FVG de M15 del día 1
        for k, v in zip(keys, vals):
            cols[k].append(v)
    return {"key": "crt:indices", "nombre": "Índices", "tipo": "crt", "perfil": "crt", "perfil_nombre": "CRT",
            "cats": {"m": ["NAS100.s"], "o": ["objetivo", "stop", "breakeven", "tiempo"],
                     "z": ["Asia", "London", "NY Open", "Fuera de TBR"], "p": ["CRT"]},
            "patrones": ["CRT"], "filtros": {"5:1": "M5 · 1"}, "ops": cols, "datos": []}


NEUTRAL = ("sin_sweep", "sin_evaluar")                                                  # velas HTF sin CRT: caja neutra


def real_pills(chart):
    """Las etiquetas de los CRT de verdad (sin las de las velas «sin sweep»)."""
    return [p for c, p in zip(chart._crts, chart._crt_pills) if c["state"] not in NEUTRAL]


def real_crts(chart):
    return [c for c in chart._crts if c["state"] not in NEUTRAL]


def backtest(ops=None, invalid=None, nosetup=None) -> Backtest:
    ops = ops or [(C2, 1, 5, 1, 0, 1), (C2, 1, 3, 1, 1, 1), (C2, 1, 5, 2, 2, 1)]
    group = raw(ops)
    if invalid:                                                                        # (C2, dirección, hora del extremo, precio, motivo)
        group["invalidos"] = {"m": [0] * len(invalid), "c": [x[0] for x in invalid], "d": [x[1] for x in invalid], "th": [x[2] for x in invalid],
                              "ps": [x[3] for x in invalid], "mo": [x[4] for x in invalid],
                              "motivos": ["sin FVG de MTF", "sin vuelta al FVG de MTF", "sin iFVG invertido"]}
    if nosetup:                                                                        # (C2, dirección, hora del extremo, precio, motivo)
        group["sin_setup"] = {"m": [0] * len(nosetup), "c": [x[0] for x in nosetup], "d": [x[1] for x in nosetup], "th": [x[2] for x in nosetup],
                              "ps": [x[3] for x in nosetup], "mo": [x[4] for x in nosetup],
                              "motivos": ["sin FVG tras el máximo", "sin cierre dentro de C1", "sin retesteo del FVG", "sin continuación tras el retesteo"]}
    return Backtest([Group("crt:indices", "Índices", group)], {})


def test_las_marcas_salen_de_las_operaciones_del_backtest_con_su_c1_y_c2():
    from tradingbot.skills.crt.chart import crt_marks as _all_marks

    def crt_marks(*a, **k):                                                              # sin las velas «sin sweep», que no son CRT
        return [m for m in _all_marks(*a, **k) if m["state"] not in NEUTRAL]
    df = scenario()
    ts, high, low = (df[k].to_numpy() for k in ("ts", "high", "low"))
    [mark] = crt_marks(backtest(), "NAS100.r", ts, high, low, AHEAD, ltf=5, entry=1)
    x0 = int(np.searchsorted(ts, int(pd.Timestamp("2026-10-13 06:00").value // 10**9) + AHEAD))
    assert (mark["x0"], mark["x1"], mark["xc1"]) == (x0, x0 + 36, x0 - 36)
    assert mark["direction"] == "short" and mark["state"] == "objetivo" and mark["label"] == "CRT"          # el M5 · entrada 1 es TP
    assert mark["c1"] == (100.0, 105.0) and mark["c2"] == (91.5, 108.5) and mark["htf"] == 180
    assert (mark["ltf"], mark["entry"], mark["mtf"], mark["fvg_all"]) == (5, 1, ["M15"], ["M15"])               # el FVG de M15 de la zona común
    assert mark["others"] == [(5, 2, "be"), (3, 1, "stop")] or sorted(mark["others"]) == [(3, 1, "stop"), (5, 2, "be")]
    assert mark["when"] == "13/10 06:00"
    i = lambda hhmm: int(np.searchsorted(ts, int(pd.Timestamp(f"2026-10-13 {hhmm}").value // 10**9) + AHEAD))          # noqa: E731
    assert mark["pos"] == {"x0": i("06:55"), "x1": i("07:10"), "entry": 103.1, "stop": 108.5, "target": 92.3}
    assert mark["ifvg"] == {"x0": i("06:25"), "x1": i("06:45"), "bottom": 106.1, "top": 107.3}
    assert mark["cisd"] == {"x0": i("06:15"), "x1": i("06:50"), "level": 103.2, "label": "CISD"} and mark["extreme"] == {"x": i("06:35"), "price": 108.5}
    first = int(np.searchsorted(ts, int(pd.Timestamp("2026-10-12 12:00").value // 10**9) + AHEAD))
    assert mark["fvgs"] == [{"tf": 15, "name": "M15", "x0": first, "x1": i("06:35"), "bottom": 107.5, "top": 110.0}]      # solo el M15 lo toca
    [other] = crt_marks(backtest(), "NAS100.r", ts, high, low, AHEAD, ltf=3, entry=1)                    # otro LTF: se enseña esa operación
    assert (other["ltf"], other["state"], other["mtf"]) == (3, "stop", ["M15"])


def test_un_sweep_invalidado_se_marca_sin_operacion_y_con_su_motivo():
    from tradingbot.skills.crt.chart import crt_marks as _all_marks

    def crt_marks(*a, **k):                                                              # sin las velas «sin sweep», que no son CRT
        return [m for m in _all_marks(*a, **k) if m["state"] not in NEUTRAL]
    df = scenario()
    ts, high, low = (df[k].to_numpy() for k in ("ts", "high", "low"))
    bt = backtest(invalid=[(C2, 0, C2 + 35, 108.5, 1), (C2, 1, C2 + 35, 108.5, 0)])      # el corto ya tiene operaciones: solo se marca el largo
    marks = crt_marks(bt, "NAS100.r", ts, high, low, AHEAD, ltf=5, entry=1)
    assert [(m["direction"], m["state"]) for m in marks] == [("long", "invalido"), ("short", "objetivo")] or         sorted((m["direction"], m["state"]) for m in marks) == [("long", "invalido"), ("short", "objetivo")]
    inv = next(m for m in marks if m["state"] == "invalido")
    assert inv["motivo"] == "sin vuelta al FVG de MTF" and inv["ltf"] is None and inv["extreme"]["price"] == 108.5


def test_solo_se_marcan_las_operaciones_del_ltf_y_la_entrada_elegidos():
    """Cada combinación del backtest tiene una sola operación abierta a la vez; mezclar combinaciones enseñaría operaciones solapadas."""
    from tradingbot.skills.crt.chart import crt_marks as _all_marks

    def crt_marks(*a, **k):                                                              # sin las velas «sin sweep», que no son CRT
        return [m for m in _all_marks(*a, **k) if m["state"] not in NEUTRAL]
    df = scenario()
    ts, high, low = (df[k].to_numpy() for k in ("ts", "high", "low"))
    bt = backtest([(C2, 1, 3, 2, 0, 1)])                                                # el CRT solo dio una operación, en M3 con la entrada 2
    [none] = crt_marks(bt, "NAS100.r", ts, high, low, AHEAD, ltf=5, entry=1)             # en M5 · 1 no hubo: no se rellena con otra combinación,
    assert none["state"] == "sin_operacion" and none["ltf"] is None and none["others"] == [(3, 2, "objetivo")]        # pero se marca, con las demás
    assert [m["ltf"] for m in crt_marks(bt, "NAS100.r", ts, high, low, AHEAD, ltf=3, entry=2)] == [3]


def test_sin_velas_de_la_c2_o_de_otro_mercado_no_hay_marcas():
    from tradingbot.skills.crt.chart import crt_marks as _all_marks

    def crt_marks(*a, **k):                                                              # sin las velas «sin sweep», que no son CRT
        return [m for m in _all_marks(*a, **k) if m["state"] not in NEUTRAL]
    df = scenario()
    ts, high, low = (df[k].to_numpy() for k in ("ts", "high", "low"))
    assert crt_marks(backtest(), "EURUSD", ts, high, low, AHEAD) == []                  # no es un mercado de ese backtest
    assert crt_marks(backtest([(C2 - 24 * 60 * 30, 1, 5, 1, 0, 1)]), "NAS100.r", ts, high, low, AHEAD) == []     # la C2 es de hace un mes
    assert crt_marks(None, "NAS100.r", ts, high, low, AHEAD) == []
    assert crt_marks(backtest(), "NAS100.r", ts[:0], high[:0], low[:0], AHEAD) == []


def test_la_h4_de_forex_dura_cuatro_horas():
    from tradingbot.skills.crt.chart import htf_minutes
    assert htf_minutes("NAS100.r") == 180 and htf_minutes("USTEC") == 180 and htf_minutes("EURUSD") == 240


def window(tmp_path, monkeypatch, strategy="crt"):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.envconfig import EnvConfig
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    monkeypatch.setattr("tradingbot.skills.crt.chart.no_entry_marks", lambda *a, **k: [])       # los «sin entrada» y los simulados tienen su propio test
    monkeypatch.setattr("tradingbot.skills.crt.chart.signal_marks", lambda *a, **k: [])
    cfg = {"app": {"symbol": "NAS100.r", "timeframe": "5m", "watchlist": ["NAS100.r"], "strategy": strategy}}
    return MainWindow(EventBus(), SkillManager(EventBus(), Services(None, None, cfg, EnvConfig()), [{"type": "setup"}]), cfg, "t")


def candles_event():
    df = scenario()
    df["time"] = pd.to_datetime(df["ts"], unit="s")
    return {"df": df, "symbol": "NAS100.r", "timeframe": "5m", "seconds": 0.1}


def test_el_boton_crt_solo_existe_en_el_perfil_crt(tmp_path, monkeypatch):
    crt = window(tmp_path, monkeypatch)
    assert crt.crt_btn.text() == "CRT" and not crt.crt_btn.isHidden() and crt.crt_btn.isChecked()
    other = window(tmp_path, monkeypatch, strategy="")
    assert other.crt_btn.isHidden()
    other.backtest = backtest()
    other._on_candles(candles_event())
    assert other.chart.crt_count == 0                                                    # fuera del perfil CRT no se marca nada


def test_el_grafico_marca_el_crt_con_etiqueta_discreta_y_ficha(tmp_path, monkeypatch):
    from PySide6.QtCore import QEvent
    win = window(tmp_path, monkeypatch)
    win.backtest = backtest()
    win._on_candles(candles_event())
    chart = win.chart
    assert len(real_pills(chart)) == 1
    pill = real_pills(chart)[0]
    assert "CRT bajista" in pill.toPlainText() and pill.toPlainText().strip().endswith("TP") and pill.result == "TP"
    assert not chart._card.isVisible()                                                   # la etiqueta sola es discreta: sin detalle
    violet = [it for it in chart._crt_items if hasattr(it, "brush") and it.brush().color().name().upper() == "#B388FF"]
    assert violet == []                                                                  # ya no se dibujan el iFVG ni el CISD
    labels = sorted(it.toPlainText() for it in chart._crt_items if hasattr(it, "toPlainText") and not it.__class__.__name__ == "CrtPill")
    assert labels == ["CISD 103.200", "entrada 103.100"]                                 # la línea del CISD y la entrada: el BPR va sin etiqueta
    from tradingbot.ui.chart import HTF_BOX
    boxes = [it for it in chart._crt_items if hasattr(it, "pen") and hasattr(it, "rect") and it.pen().color().name().upper() == HTF_BOX]
    assert len(boxes) == 1 + sum(c["state"] in NEUTRAL for c in chart._crts)         # C2 (y las velas sin sweep) en gris claro, no del color de las velas
    tinted = [it for it in chart._crt_items if hasattr(it, "pen") and hasattr(it, "rect") and it.pen().color().name().upper() == "#EF5350"]
    assert len(tinted) >= 1                                                              # C1 (y C3) de un CRT con operación, del color de su lado (bajista: rojo)
    zones = [it for it in chart._crt_items if hasattr(it, "rect") and hasattr(it, "brush") and it.brush().color().alpha() == 60]
    assert len(zones) == 2                                                               # la operación: zona verde hasta el objetivo y roja hasta el stop
    chart.resize(900, 500)
    vb = chart.getPlotItem().getViewBox()
    vb.setXRange(0, 80, padding=0)
    vb.setYRange(88, 112, padding=0)
    vb.updateMatrix()
    chart._mouse_moved(pill.sceneBoundingRect().center())                                # al pasar el ratón
    text = chart._card.toPlainText()
    assert chart._card.isVisible() and "CRT bajista" in text and "TP" in text
    assert "LTF (FVG, retesteo y entrada)" in text and "M5" in text and "CISD" in text and "103.200" in text and "13/10 06:00" in text
    assert "M3·1" in text                                                                # y los otros LTF del backtest
    assert "103.1" in text and "108.5" in text and "92.3" in text and "103.2" in text    # entrada, SL, TP y CISD
    chart.leaveEvent(QEvent(QEvent.Type.Leave))
    assert not chart._card.isVisible()
    win.crt_btn.setChecked(False)                                                        # el botón las quita y las vuelve a poner
    assert chart.crt_count == 0 and not chart._crt_items
    win.crt_btn.setChecked(True)
    assert len(real_pills(chart)) == 1 and chart.crt_count == len(chart._crts)


def test_la_etiqueta_de_un_invalidado_lo_dice(tmp_path, monkeypatch):
    win = window(tmp_path, monkeypatch)
    win.backtest = backtest(invalid=[(C2, 0, C2 + 35, 108.5, 2)])
    win._on_candles(candles_event())
    pills = win.chart._crt_pills
    inv = next(p for p in pills if p.result == "Invalidado")
    assert "CRT alcista" in inv.toPlainText() and inv.toPlainText().strip().endswith("Invalidado")


def test_un_crt_alcista_lleva_la_etiqueta_debajo_y_en_verde(tmp_path, monkeypatch):
    from tradingbot.ui.chart import CRT_COLORS
    win = window(tmp_path, monkeypatch)
    win.backtest = backtest([(C2, 0, 5, 1, 1, 1)])                                       # largo, SL, FVG de M15
    win._on_candles(candles_event())
    pill = real_pills(win.chart)[0]
    assert "CRT alcista" in pill.toPlainText() and pill.result == "SL" and pill._bar.name().upper() == CRT_COLORS["long"]
    assert real_crts(win.chart)[0]["mtf"] == ["M15"]


def test_un_sweep_sin_setup_se_marca_con_su_motivo_y_distinto_del_invalidado(tmp_path, monkeypatch):
    from tradingbot.skills.crt.chart import crt_marks as _all_marks

    def crt_marks(*a, **k):                                                              # sin las velas «sin sweep», que no son CRT
        return [m for m in _all_marks(*a, **k) if m["state"] not in NEUTRAL]
    df = scenario()
    ts, high, low = (df[k].to_numpy() for k in ("ts", "high", "low"))
    both = backtest(invalid=[(C2, 0, C2 + 35, 108.5, 1)], nosetup=[(C2, 0, C2 + 35, 108.5, 2)])
    assert [m["state"] for m in crt_marks(both, "NAS100.r", ts, high, low, AHEAD) if m["direction"] == "long"] == ["invalido"]      # el invalidado manda
    bt = backtest(nosetup=[(C2, 0, C2 + 35, 108.5, 0)])                                # el largo no tiene operación: solo sin setup
    sin = next(m for m in crt_marks(bt, "NAS100.r", ts, high, low, AHEAD) if m["direction"] == "long")
    assert sin["state"] == "sin_setup" and sin["motivo"] == "sin FVG tras el máximo" and sin["ltf"] is None
    win = window(tmp_path, monkeypatch)
    win.backtest = bt
    win._on_candles(candles_event())
    assert any(p.result == "Sin setup" and p.toPlainText().strip().endswith("Sin setup") for p in win.chart._crt_pills)


def test_la_etiqueta_del_crt_se_queda_al_borde_si_su_c2_empieza_fuera_de_la_vista(tmp_path, monkeypatch):
    win = window(tmp_path, monkeypatch)
    win.backtest = backtest()
    win._on_candles(candles_event())
    chart = win.chart
    crt, pill = real_crts(chart)[0], real_pills(chart)[0]
    vb = chart.getPlotItem().getViewBox()
    left = float(crt["x0"]) + 5
    vb.setXRange(left, left + 25, padding=0)                                             # la vista empieza dentro de C2
    chart._fit_pills()
    assert pill.pos().x() >= vb.viewRange()[0][0] - 1e-6                               # la etiqueta sigue a la vista (dice si es bajista o alcista)
    vb.setXRange(float(crt["x0"]) - 3, float(crt["x0"]) + 30, padding=0)                 # C2 entera a la vista: la etiqueta, en su sitio
    chart._fit_pills()
    assert pill.pos().x() == float(crt["x0"])


def test_las_velas_sin_sweep_tambien_llevan_caja_neutra(tmp_path, monkeypatch):
    from tradingbot.skills.crt.chart import crt_marks
    df = scenario()
    ts, high, low = (df[k].to_numpy() for k in ("ts", "high", "low"))
    marks = crt_marks(backtest(), "NAS100.r", ts, high, low, AHEAD, ltf=5, entry=1)
    none = [m for m in marks if m["state"] in NEUTRAL]
    assert none and all(m["ltf"] is None and m["motivo"] for m in none)
    assert sorted(m["x0"] for m in marks) == [m["x0"] for m in marks]                      # y ninguna caja pisa a otra: una por vela HTF
    assert len({m["x0"] for m in marks}) == len(marks)
    win = window(tmp_path, monkeypatch)
    win.backtest = backtest()
    win._on_candles(candles_event())
    texts = [p.toPlainText() for p in win.chart._crt_pills]
    assert any("sin sweep" in t or "sin evaluar" in t for t in texts) and any("CRT bajista" in t for t in texts)


def test_el_setup_sin_toque_de_la_zona_se_marca_setup_ok_sin_entrada():
    from crt_scenarios import eurusd
    from tradingbot.skills.crt import engine
    from tradingbot.skills.crt.chart import no_entry_marks
    df = eurusd()
    cfg = engine.Cfg(240, 17 * 3600, 17 * 3600, AHEAD)
    cut = df[df["ts"] < pd.Timestamp("2026-11-02 22:00").value // 10**9 + AHEAD].reset_index(drop=True)      # hasta justo después de invertirse el iFVG (21:55)
    assert [x for x in no_entry_marks(cut, "EURUSD", AHEAD, 5) if x["when"] == "02/11 21:00"] == []       # C2 sigue en curso: aún puede tocarla
    bars = df.copy()
    bars.loc[bars["ts"] >= pd.Timestamp("2026-11-02 22:00").value // 10**9 + AHEAD, ["open", "high", "low", "close"]] = 1.1200      # tras invertirse sube hasta el extremo opuesto de C1 (1.11976) sin volver a la zona
    marks = no_entry_marks(bars, "EURUSD", AHEAD, 5)
    m = [x for x in marks if x["when"] == "02/11 21:00"]
    assert len(m) == 1 and m[0]["state"] == "sin_entrada" and m[0]["direction"] == "long" and "pos" not in m[0]
    assert (m[0]["common"]["bottom"], m[0]["common"]["top"]) == (pytest.approx(1.11793), pytest.approx(1.11809))
    assert m[0]["cisd"]["level"] == pytest.approx(1.11814)
    assert [x for x in engine.find_zone_setups(df, df, 5, cfg)[0].no_entry if ny_2100(x)] == []           # con el toque real no es «sin entrada»


def test_el_setup_con_retest_pero_sin_cierre_sobre_el_cisd_se_marca_setup_ok_sin_cierre():
    from crt_scenarios import eurusd
    from tradingbot.skills.crt.chart import no_entry_marks
    df = eurusd()
    bars = df.copy()
    bars.loc[bars["ts"] >= pd.Timestamp("2026-11-02 22:15").value // 10**9 + AHEAD, ["open", "high", "low", "close"]] = 1.1180      # tras el retest cierra por debajo de la zona: el retest se invalida y nunca cierra sobre el CISD (1.11841)
    m = [x for x in no_entry_marks(bars, "EURUSD", AHEAD, 5) if x["when"] == "02/11 21:00"]
    assert len(m) == 1 and m[0]["state"] == "sin_cierre" and m[0]["direction"] == "long" and "pos" not in m[0]
    assert m[0]["touch"]["when"] == "02/11 22:15" and m[0]["cisd"]["level"] > 0


def test_la_etiqueta_y_la_ficha_dicen_los_tf_la_zona_comun_el_retest_y_el_cisd(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from crt_scenarios import eurusd
    from tradingbot.skills.crt.chart import signal_marks
    from tradingbot.ui.chart import CrtPill
    df = eurusd()
    mark = [m for m in signal_marks(df, "EURUSD", AHEAD, 5) if m["when"] == "02/11 21:00"][0]
    assert mark["touch"]["when"] == "02/11 22:15"
    win = window(tmp_path, monkeypatch)
    pill = CrtPill(mark)
    assert "FVG" not in pill.toPlainText()                                                       # la etiqueta discreta no lleva los TF: salen al desplegarla
    chart = win.chart
    chart.set_crts([mark])
    chart.resize(900, 500)
    vb = chart.getPlotItem().getViewBox()
    vb.setXRange(mark["x0"] - 20, mark["x0"] + 120, padding=0)
    vb.setYRange(1.1170, 1.1205, padding=0)
    vb.updateMatrix()
    chart._mouse_moved(chart._crt_pills[0].sceneBoundingRect().center())
    text = chart._card.toPlainText()
    assert "BPR M5" in text and "1.11815" in text and "1.11818" in text                          # la zona común (BPR), con su TF; ya no se enseñan el FVG ni el iFVG por separado
    assert "Retest del BPR" in text and "02/11 22:15" in text                                    # el retest
    assert "CISD" in text and "1.11849" in text                                                  # el nivel del CISD


def test_un_setup_valido_que_el_bot_no_opero_se_dibuja_con_el_resultado_que_habria_dado():
    from crt_scenarios import eurusd
    from tradingbot.skills.crt.chart import signal_marks
    df = eurusd()
    marks = [m for m in signal_marks(df, "EURUSD", AHEAD, 5) if m["when"] == "02/11 21:00"]
    assert len(marks) == 1
    m = marks[0]
    assert m["direction"] == "long" and m["simulated"] and m["state"] in ("objetivo", "stop", "be", "tiempo", "abierta")
    assert m["pos"]["entry"] == pytest.approx(1.11858) and m["pos"]["stop"] == pytest.approx(1.1177) and m["pos"]["target"] == pytest.approx(1.12034)
    assert (m["common"]["bottom"], m["common"]["top"]) == (pytest.approx(1.11815), pytest.approx(1.11818)) and m["cisd"]["level"] == pytest.approx(1.11849)
    assert m["touch"]["when"] == "02/11 22:15"


def test_el_estado_de_un_setup_es_el_mismo_en_5m_y_en_15m():
    from crt_scenarios import eurusd
    from tradingbot.skills.crt.chart import retime, zone_marks
    df = eurusd()
    marks = zone_marks(df, "EURUSD", AHEAD, 5)
    ts5 = df["ts"].to_numpy()
    ts15 = np.unique(ts5 // 900 * 900)                                                           # las velas de 15 min con las mismas horas
    m5 = [m for m in marks if m["when"] == "02/11 21:00"][0]
    m15 = [m for m in retime(marks, ts5, ts15) if m["when"] == "02/11 21:00"][0]
    assert m15["state"] == m5["state"] and m15["direction"] == m5["direction"] and m15["simulated"] == m5["simulated"]
    assert (m15["common"]["bottom"], m15["common"]["top"], m15["cisd"]["level"]) == (m5["common"]["bottom"], m5["common"]["top"], m5["cisd"]["level"])
    assert ts15[m15["pos"]["x0"]] == ts5[m5["pos"]["x0"]] // 900 * 900                              # la entrada, en la vela de 15 min que la contiene
    assert ts15[m15["touch"]["x"]] == ts5[m5["touch"]["x"]] // 900 * 900                            # el retest, en la vela de 15 min que lo contiene
    assert ts15[m15["x0"]] == pd.Timestamp("2026-11-02 21:00").value // 10**9 + AHEAD               # C2 empieza donde empieza
    waiting = [m for m in marks if m["state"] == "sin_entrada"]
    assert [m["state"] for m in retime(waiting, ts5, ts15)] == ["sin_entrada"] * len(waiting)
