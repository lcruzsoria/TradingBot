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
            "f15a", "f15b", "f15t", "f30a", "f30b", "f30t", "f60a", "f60b", "f60t")
    cols = {k: [] for k in keys}
    for c2, d, ltf, entry, out, mtf in ops:
        # el corto del escenario: entra en 103.1 a las 06:55 (C2 + 55 min), stop 108.5 (extremo de las 06:35), objetivo 92.3, iFVG 106.1-107.3
        # (de las 06:25 a la inversión de las 06:45), CISD en 103.2 a las 06:50 con la secuencia desde las 06:15
        vals = (c2, d, ltf, entry, out, mtf, 0, 2, 3, c2 + 55, c2 + 70, 1.9, 0.1, -1, 103.1, 108.5, 92.3, 106.1, 107.3, 103.2,
                c2 + 25, c2 + 45, c2 + 50, c2 + 35, c2 + 15, c2 + 35,
                107.5, 110.0, D1_FVG, float("nan"), float("nan"), -1, float("nan"), float("nan"), -1)     # FVG de M15 del día 1; M30 y H1 no
        for k, v in zip(keys, vals):
            cols[k].append(v)
    return {"key": "crt:indices", "nombre": "Índices", "tipo": "crt", "perfil": "crt", "perfil_nombre": "CRT",
            "cats": {"m": ["NAS100.s"], "o": ["objetivo", "stop", "breakeven", "tiempo"],
                     "z": ["Asia", "London", "NY Open", "Fuera de TBR"], "p": ["CRT"]},
            "patrones": ["CRT"], "filtros": {"5:1": "M5 · 1"}, "ops": cols, "datos": []}


def backtest(ops=None) -> Backtest:
    ops = ops or [(C2, 1, 5, 1, 0, 1), (C2, 1, 3, 1, 1, 3), (C2, 1, 5, 2, 2, 1)]
    return Backtest([Group("crt:indices", "Índices", raw(ops))], {})


def test_las_marcas_salen_de_las_operaciones_del_backtest_con_su_c1_y_c2():
    from tradingbot.skills.crt.chart import crt_marks
    df = scenario()
    ts, high, low = (df[k].to_numpy() for k in ("ts", "high", "low"))
    [mark] = crt_marks(backtest(), "NAS100.r", ts, high, low, AHEAD, ltf=5, entry=1)
    x0 = int(np.searchsorted(ts, int(pd.Timestamp("2026-10-13 06:00").value // 10**9) + AHEAD))
    assert (mark["x0"], mark["x1"], mark["xc1"]) == (x0, x0 + 36, x0 - 36)
    assert mark["direction"] == "short" and mark["state"] == "objetivo" and mark["label"] == "CRT"          # el M5 · entrada 1 es TP
    assert mark["c1"] == (100.0, 105.0) and mark["c2"] == (91.5, 108.5) and mark["htf"] == 180
    assert (mark["ltf"], mark["entry"], mark["mtf"], mark["fvg_all"]) == (5, 1, ["M15"], ["M15", "M30"])
    assert mark["others"] == [(5, 2, "be"), (3, 1, "stop")] or sorted(mark["others"]) == [(3, 1, "stop"), (5, 2, "be")]
    assert mark["when"] == "13/10 06:00"
    i = lambda hhmm: int(np.searchsorted(ts, int(pd.Timestamp(f"2026-10-13 {hhmm}").value // 10**9) + AHEAD))          # noqa: E731
    assert mark["pos"] == {"x0": i("06:55"), "x1": i("07:10"), "entry": 103.1, "stop": 108.5, "target": 92.3}
    assert mark["ifvg"] == {"x0": i("06:25"), "x1": i("06:45"), "bottom": 106.1, "top": 107.3}
    assert mark["cisd"] == {"x0": i("06:15"), "x1": i("06:50"), "level": 103.2} and mark["extreme"] == {"x": i("06:35"), "price": 108.5}
    first = int(np.searchsorted(ts, int(pd.Timestamp("2026-10-12 12:00").value // 10**9) + AHEAD))
    assert mark["fvgs"] == [{"tf": 15, "name": "M15", "x0": first, "x1": i("06:35"), "bottom": 107.5, "top": 110.0}]      # solo el M15 lo toca
    [other] = crt_marks(backtest(), "NAS100.r", ts, high, low, AHEAD, ltf=3, entry=1)                    # otro LTF: se enseña esa operación
    assert (other["ltf"], other["state"], other["mtf"]) == (3, "stop", ["M15", "M30"])


def test_sin_velas_de_la_c2_o_de_otro_mercado_no_hay_marcas():
    from tradingbot.skills.crt.chart import crt_marks
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
    assert chart.crt_count == 1 and len(chart._crt_pills) == 1
    pill = chart._crt_pills[0]
    assert "CRT bajista" in pill.toPlainText() and pill.toPlainText().strip().endswith("TP") and pill.result == "TP"
    assert not chart._card.isVisible()                                                   # la etiqueta sola es discreta: sin detalle
    violet = [it for it in chart._crt_items if hasattr(it, "brush") and it.brush().color().name().upper() == "#B388FF"]
    assert len(violet) == 1                                                              # el iFVG invertido, pintado en el LTF
    assert sorted(it.toPlainText().split()[0] for it in chart._crt_items if hasattr(it, "toPlainText")) == ["CISD", "▼"]     # solo la etiqueta y el CISD: sin nombres de vela ni de zonas
    orange = [it for it in chart._crt_items if hasattr(it, "brush") and it.brush().color().name().upper() == "#FFA726"]
    assert len(orange) == 1                                                              # el FVG de MTF del paso 2, en naranja
    from tradingbot.ui.chart import HTF_BOX
    boxes = [it for it in chart._crt_items if hasattr(it, "pen") and hasattr(it, "rect") and it.pen().color().name().upper() == HTF_BOX]
    assert len(boxes) == 2                                                               # C1 y C2 en gris claro, no del color de las velas
    chart.resize(900, 500)
    vb = chart.getPlotItem().getViewBox()
    vb.setXRange(0, 80, padding=0)
    vb.setYRange(88, 112, padding=0)
    vb.updateMatrix()
    chart._mouse_moved(pill.sceneBoundingRect().center())                                # al pasar el ratón
    text = chart._card.toPlainText()
    assert chart._card.isVisible() and "CRT bajista" in text and "TP" in text
    assert "FVG en MTF" in text and "M15" in text and "M5" in text and "Vela siguiente al CISD" in text and "13/10 06:00" in text
    assert "M3·1" in text                                                                # y los otros LTF del backtest
    assert "FVG M15" in text and "107.500" in text and "110.000" in text                 # la zona del FVG de MTF, en la ficha
    assert "103.1" in text and "108.5" in text and "92.3" in text and "iFVG invertido" in text and "103.2" in text   # entrada, SL, TP, iFVG y CISD
    chart.leaveEvent(QEvent(QEvent.Type.Leave))
    assert not chart._card.isVisible()
    win.crt_btn.setChecked(False)                                                        # el botón las quita y las vuelve a poner
    assert chart.crt_count == 0 and not chart._crt_items
    win.crt_btn.setChecked(True)
    assert chart.crt_count == 1


def test_un_crt_alcista_lleva_la_etiqueta_debajo_y_en_verde(tmp_path, monkeypatch):
    from tradingbot.ui.chart import CRT_COLORS
    win = window(tmp_path, monkeypatch)
    win.backtest = backtest([(C2, 0, 5, 1, 1, 4)])                                       # largo, SL, FVG de H1
    win._on_candles(candles_event())
    pill = win.chart._crt_pills[0]
    assert "CRT alcista" in pill.toPlainText() and pill.result == "SL" and pill._bar.name().upper() == CRT_COLORS["long"]
    assert win.chart._crts[0]["mtf"] == ["H1"]
