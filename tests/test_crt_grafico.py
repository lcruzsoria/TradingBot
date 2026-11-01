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


def raw(ops: list[tuple]) -> dict:
    """Operaciones CRT en NAS100: (inicio de C2, dirección 0 largo / 1 corto, LTF, entrada, resultado, máscara de FVG de MTF)."""
    cols = {k: [] for k in ("c", "d", "l", "n", "o", "t", "m", "q", "z", "e", "x", "r", "k", "h")}
    for c2, d, ltf, entry, out, mtf in ops:
        for k, v in zip(("c", "d", "l", "n", "o", "t", "m", "q", "z", "e", "x", "r", "k", "h"),
                        (c2, d, ltf, entry, out, mtf, 0, 2, 3, c2 + 60, c2 + 90, 1.9, 0.1, -1)):
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
    chart.resize(900, 500)
    vb = chart.getPlotItem().getViewBox()
    vb.setXRange(0, 80, padding=0)
    vb.setYRange(88, 112, padding=0)
    vb.updateMatrix()
    chart._mouse_moved(pill.sceneBoundingRect().center())                                # al pasar el ratón
    text = chart._card.toPlainText()
    assert chart._card.isVisible() and "CRT bajista" in text and "TP" in text
    assert "FVG en MTF" in text and "M15" in text and "M5" in text and "Vela siguiente al CISD" in text and "13/10 06:00" in text
    assert "M3·1 SL" in text.replace(" ", " ") or "M3·1" in text                         # y los otros LTF del backtest
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
