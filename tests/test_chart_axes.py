"""Gráfico: eje de tiempo en hora de Nueva York y ejes redimensionables."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def candles(n=500):
    # velas M15 desde el miércoles 7 oct 2026 a las 01:00 del servidor (= 18:00 del martes en Nueva York)
    t0 = int(datetime(2026, 10, 7, 1, 0, tzinfo=timezone.utc).timestamp())
    ts = np.arange(n, dtype=np.int64) * 900 + t0
    close = 1.10 + np.sin(np.arange(n) / 20) * 0.01
    return pd.DataFrame({"ts": ts, "open": close, "high": close + 0.001, "low": close - 0.001, "close": close})


def test_el_eje_de_tiempo_va_en_hora_de_nueva_york(qapp):
    from tradingbot.ui.chart import ChartView
    chart = ChartView()
    chart.set_candles(candles())
    assert chart.time_axis.tickStrings([0], 1, 1) == ["06 oct 18:00"]      # servidor 01:00 - 7 h (estimado)
    chart.set_ny_shift(6 * 3600)
    assert chart.time_axis.tickStrings([0], 1, 1) == ["06 oct 19:00"]
    assert chart.time_axis.tickStrings([-1, 10_000], 1, 1) == ["", ""]


def test_arrastrar_el_eje_de_precio_lo_redimensiona_y_doble_clic_lo_restaura(qapp):
    from tradingbot.ui.chart import ChartView
    chart = ChartView()
    chart.set_candles(candles())
    vb = chart.getPlotItem().getViewBox()
    assert chart.price_auto
    y0, y1 = vb.viewRange()[1]
    chart.scale_price(2.0)                                               # arrastrar hacia abajo: comprime
    z0, z1 = vb.viewRange()[1]
    assert not chart.price_auto and (z1 - z0) == pytest.approx(2 * (y1 - y0))
    assert (z0 + z1) / 2 == pytest.approx((y0 + y1) / 2)                 # alrededor del centro
    assert vb.state["mouseEnabled"] == [True, True]                      # con escala manual se mueve en vertical
    chart.reset_price_scale()
    assert chart.price_auto and vb.state["mouseEnabled"] == [True, False]


def test_arrastrar_el_eje_de_tiempo_cambia_las_velas_visibles_con_el_borde_derecho_fijo(qapp):
    from tradingbot.ui.chart import ChartView
    chart = ChartView()
    chart.set_candles(candles())
    vb = chart.getPlotItem().getViewBox()
    x0, x1 = vb.viewRange()[0]
    chart.scale_time(0.5)                                                # arrastrar a la derecha: menos velas
    n0, n1 = vb.viewRange()[0]
    assert n1 == pytest.approx(x1) and (n1 - n0) == pytest.approx((x1 - x0) / 2)
    chart.scale_time(0.0001)                                             # nunca menos de MIN_BARS
    m0, m1 = vb.viewRange()[0]
    assert m1 - m0 == pytest.approx(chart.MIN_BARS)
    chart.scale_price(3.0)
    chart.reset_time_scale()                                             # doble clic en el eje de tiempo
    assert vb.viewRange()[0] == pytest.approx([x0, x1]) and chart.price_auto


def test_los_ejes_responden_al_raton(qapp):
    from tradingbot.ui.chart import ChartView, ScaleAxis
    chart = ChartView()
    assert isinstance(chart.getPlotItem().getAxis("right"), ScaleAxis)
    assert chart.price_axis.vertical and not chart.time_axis.vertical
    assert chart.price_axis.chart is chart and chart.time_axis.chart is chart


def test_la_ventana_pasa_el_desfase_medido_al_eje(qapp, tmp_path, monkeypatch):
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui.main_window import MainWindow
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": ["EURUSD"]}}
    bus = EventBus()
    win = MainWindow(bus, SkillManager(bus, Services(None, None, cfg), []), cfg, "t")
    df = candles()
    df["time"] = pd.to_datetime(df["ts"], unit="s")
    win._on_candles({"df": df, "symbol": "EURUSD", "timeframe": "15m", "seconds": 0.1})
    assert "06 oct 2026" in win.chart_stats.text() and "Nueva York (estimada)" in win.chart_stats.text()
    summer = 3 * 3600                                                    # servidor UTC+3 con NY en horario de verano
    win._on_quotes({"quotes": {}, "account": None, "server_offset": summer, "offset_source": "detectado"})
    assert win.chart.time_axis.ny_shift == win.ny_shift and not win.ny_estimated
    assert "estimada" not in win.chart_stats.text()
