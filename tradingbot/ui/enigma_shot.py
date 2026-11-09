"""Imagen de Enigma369 para Telegram (/enigma369_1m, /enigma369_5m): las últimas horas de gráfico con sus zonas y las franjas del selector.

Se dibuja fuera de la ventana (un widget que no se muestra) y en el hilo de la interfaz: la skill Telegram pide la imagen y la recibe en PNG.
"""
from __future__ import annotations

from PySide6.QtCore import QBuffer, QByteArray, QIODevice
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from . import theme
from .bias_hist import PRICE_AXIS_WIDTH
from .chart import ChartView
from .enigma_stripes import EnigmaStripes

NAMES = {"semana": "Semana", "dia": "Día", "sesion": "Sesión", "cuarto": "Cuarto 90m", "micro": "Micro"}
SIZE = (1280, 860)


def render(p: dict) -> bytes:
    """`p`: symbol, timeframe, bars (las que se ven), title, df (velas) y enigma (lo mismo que publica enigma369.updated)."""
    box = QWidget()
    box.setStyleSheet(f"background: {theme.PANEL};")
    lay = QVBoxLayout(box)
    lay.setContentsMargins(10, 8, 10, 8)
    lay.setSpacing(4)
    title = QLabel(p.get("title", ""))
    title.setObjectName("Brand")
    lay.addWidget(title)
    chart = ChartView()
    chart.getPlotItem().getAxis("right").setWidth(PRICE_AXIS_WIDTH)    # el de las franjas: las velas quedan sobre sus zonas
    lay.addWidget(chart, 1)
    stripes = EnigmaStripes()
    stripes.link_to(chart)
    lay.addWidget(stripes)
    box.resize(*SIZE)
    chart.set_candles(p["df"], view_bars=int(p["bars"]))
    e = p["enigma"]
    chart.set_enigma(e.get("areas", []), e.get("quarter_lines"), e.get("triples"), e.get("windows"))
    stripes.set_data(e, NAMES)
    box.grab()                                        # primera pasada: coloca los widgets y el rango del gráfico
    stripes.rows.sync_x()
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    box.grab().save(buffer, "PNG")
    box.deleteLater()
    return bytes(data)
