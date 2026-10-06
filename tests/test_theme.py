import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from tradingbot.ui import theme
from tradingbot.ui.theme import PRESETS, ThemeError


@pytest.fixture(autouse=True)
def restore_theme():
    yield
    theme.apply(PRESETS[theme.DEFAULT_PRESET])


def test_preset_negro_es_fondo_negro_con_texto_azul_verde_y_rojo():
    p = PRESETS["negro"]
    assert p.bg == "#000000" and p.chart_bg == "#000000"
    r, g, b = (int(p.text[i:i + 2], 16) for i in (1, 3, 5))
    assert b > r and b > g                                   # texto azul
    assert int(p.bull[3:5], 16) > int(p.bull[1:3], 16)       # verde domina sobre rojo
    assert int(p.bear[1:3], 16) > int(p.bear[3:5], 16)       # rojo domina sobre verde
    assert theme.DEFAULT_PRESET == "negro"


def test_mix():
    assert theme.mix("#000000", "#ffffff", 0.0) == "#000000"
    assert theme.mix("#000000", "#ffffff", 1.0) == "#ffffff"
    assert theme.mix("#000000", "#ffffff", 0.5) == "#808080"


def test_validacion_de_colores():
    assert theme.validate({"bull": "#00FF88"}) == {"bull": "#00ff88"}
    for bad in ({"bull": "verde"}, {"bull": "#12345"}, {"nada": "#000000"}, {"bull": 5}):
        with pytest.raises(ThemeError):
            theme.validate(bad)
    with pytest.raises(ThemeError, match="desconocido"):
        theme.build_palette("no_existe")


def test_resolve_prioridad(tmp_path):
    local = tmp_path / "theme.local.json"
    # solo config.toml
    name, pal = theme.resolve({"preset": "negro", "bull": "#00ff00"}, local)
    assert name == "negro" and pal.bull == "#00ff00" and pal.bear == PRESETS["negro"].bear
    # el fichero local manda sobre config.toml (incluido el preset)
    local.write_text(json.dumps({"preset": "pizarra", "colors": {"bear": "#ff0000"}}))
    name, pal = theme.resolve({"preset": "negro", "bull": "#00ff00"}, local)
    assert name == "pizarra" and pal.bear == "#ff0000" and pal.bull == PRESETS["pizarra"].bull


def test_guardar_y_cargar_solo_guarda_lo_cambiado(tmp_path):
    local = tmp_path / "theme.local.json"
    pal = theme.build_palette("negro", {"text": "#ffffff"})
    theme.save_local("negro", pal, local)
    assert json.loads(local.read_text()) == {"preset": "negro", "colors": {"text": "#ffffff"}}
    assert theme.resolve({}, local) == ("negro", pal)


def test_fichero_local_corrupto(tmp_path):
    local = tmp_path / "theme.local.json"
    local.write_text("{no es json")
    with pytest.raises(ThemeError):
        theme.resolve({}, local)


def test_apply_actualiza_colores_y_hoja_de_estilos():
    theme.apply(theme.build_palette("negro", {"bull": "#12ab34"}))
    assert theme.BULL == "#12ab34" and theme.BG == "#000000"
    assert "#12ab34" in theme.stylesheet()
    fill, border = theme.hex_style("error")
    assert border == theme.BEAR


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def test_dialogo_cambia_color_y_avisa(qapp, tmp_path, monkeypatch):
    from tradingbot.ui.theme_dialog import ThemeDialog

    monkeypatch.setattr(theme, "LOCAL_THEME_FILE", tmp_path / "theme.local.json")
    seen = []
    dlg = ThemeDialog(None, "negro", PRESETS["negro"], lambda name, pal: seen.append((name, pal)))
    dlg.set_color("bull", "#00ff88")
    assert seen[-1][1].bull == "#00ff88" and dlg.swatches["bull"].text() == "#00FF88"
    dlg._choose_preset("pizarra")
    assert seen[-1][0] == "pizarra" and seen[-1][1] == PRESETS["pizarra"]
    dlg.set_color("bear", "#ff0000")
    dlg.save()
    saved = json.loads((tmp_path / "theme.local.json").read_text())
    assert saved == {"preset": "pizarra", "colors": {"bear": "#ff0000"}}


def test_ventana_aplica_el_tema_en_vivo(qapp):
    from PySide6.QtWidgets import QApplication
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui.main_window import MainWindow

    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": []}}
    bus = EventBus()
    win = MainWindow(bus, SkillManager(bus, Services(None, None, cfg), []), cfg, "t", theme_name="negro")
    win.apply_theme("pizarra", PRESETS["pizarra"])
    assert win.theme_name == "pizarra" and theme.BG == PRESETS["pizarra"].bg
    assert PRESETS["pizarra"].bg in QApplication.instance().styleSheet()
