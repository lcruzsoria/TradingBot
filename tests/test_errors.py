import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from tradingbot.core import EventBus, Services, SkillManager
from tradingbot.ui.errors import explain_error
from tradingbot.ui.main_window import MainWindow


def test_explicaciones():
    assert "Editar" in explain_error("Mt5Error: El símbolo 'X' no existe en este broker. Nombres parecidos: Y.")
    assert "historial" in explain_error("Mt5Error: Sin velas para EURUSD 15m: (-1, 'x')")
    assert "MT5 no responde" in explain_error("Mt5Error: No se pudo activar el símbolo 'A' en MT5: (-1, 'Terminal: Call failed')")
    assert "otra cuenta" in explain_error("Mt5Error: El terminal está en la cuenta 5, pero el perfil 'demo' es la 6.")
    assert "Registro" in explain_error("algo raro")


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def test_la_ventana_muestra_el_motivo_del_error_y_lo_oculta_al_reintentar(qapp, tmp_path, monkeypatch):
    from tradingbot import settings
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": ["EURUSD"]}}
    bus = EventBus()
    win = MainWindow(bus, SkillManager(bus, Services(None, None, cfg), []), cfg, "t")
    win.connected = True
    win._on_failed({"stage": "load", "symbol": "EURUSD", "timeframe": "15m",
                    "error": "Mt5Error: Sin velas para EURUSD 15m: (-1, 'x')"})
    text = win.error_banner.text()
    assert not win.error_banner.isHidden() and "EURUSD" in text and "Sin velas" in text and "historial" in text
    assert "Sin velas" in win.status.toolTip() and win.status.text() == "Error al cargar"
    win.load_candles()                                   # reintentar oculta el aviso
    assert win.error_banner.isHidden()
