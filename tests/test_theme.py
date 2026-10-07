import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from tradingbot import envconfig
from tradingbot.ui import theme
from tradingbot.ui.theme import PRESETS, ThemeError


@pytest.fixture(autouse=True)
def restore_theme(tmp_path, monkeypatch):
    monkeypatch.setattr(envconfig, "ENV_FILE", tmp_path / "tradingbot.env")
    yield
    theme.apply(PRESETS[theme.DEFAULT_PRESET])


def test_preset_negro_es_fondo_negro_con_texto_azul_verde_y_rojo():
    p = PRESETS["negro"]
    assert p.bg == "#000000" and p.chart_bg == "#000000"
    r, g, b = (int(p.text[i:i + 2], 16) for i in (1, 3, 5))
    assert b > r and b > g                                   # texto azul
    assert int(p.bull[3:5], 16) > int(p.bull[1:3], 16)       # verde domina sobre rojo
    assert int(p.bear[1:3], 16) > int(p.bear[3:5], 16)       # rojo domina sobre verde
    assert theme.DEFAULT_PRESET == "matrix"                                   # la paleta por defecto es Matrix


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
    monkeypatch.setattr(envconfig, "ENV_FILE", tmp_path / "tradingbot.env")
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


def _luminance(hex_color):
    def channel(i):
        c = int(hex_color[i:i + 2], 16) / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel(1) + 0.7152 * channel(3) + 0.0722 * channel(5)


def _contrast(a, b):
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def test_preset_matrix_verde_fosforo_sobre_negro_con_rojo_para_lo_bajista():
    p = PRESETS["matrix"]
    assert p.bg == "#000000" and p.chart_bg == "#000000"
    assert p.text == "#00ff41"                                  # el verde de la lluvia de código
    for color in (p.text, p.muted, p.accent, p.bull):
        r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
        assert g > r and g > b                                  # todos los textos y velas alcistas son verdes
    assert int(p.bear[1:3], 16) > int(p.bear[3:5], 16)          # lo bajista, rojo (la «pastilla roja»)
    assert p.bear != p.bull


@pytest.mark.parametrize("name", list(PRESETS))
def test_todas_las_paletas_son_legibles_sobre_su_fondo(name):
    p = PRESETS[name]
    assert theme.validate({k: v for k, v in p.__dict__.items()}) == p.__dict__     # colores #RRGGBB válidos
    assert _contrast(p.text, p.bg) >= 7 and _contrast(p.text, p.panel) >= 7
    assert _contrast(p.muted, p.bg) >= 4.5 and _contrast(p.muted, p.panel) >= 4.5
    assert _contrast(p.bull, p.chart_bg) >= 4.5 and _contrast(p.bear, p.chart_bg) >= 4.5


def test_matrix_aparece_en_el_desplegable_y_se_aplica(qapp, tmp_path, monkeypatch):
    from tradingbot.ui.theme_dialog import ThemeDialog
    monkeypatch.setattr(theme, "LOCAL_THEME_FILE", tmp_path / "theme.local.json")
    monkeypatch.setattr(envconfig, "ENV_FILE", tmp_path / "tradingbot.env")
    seen = []
    dlg = ThemeDialog(None, "negro", PRESETS["negro"], lambda name, pal: seen.append((name, pal)))
    names = [dlg.preset_box.itemData(i) for i in range(dlg.preset_box.count())]
    assert names == ["negro", "pizarra", "matrix", "blanco"]
    assert dlg.preset_box.itemText(2) == "Matrix (verde sobre negro)"
    dlg.preset_box.setCurrentIndex(2)
    dlg.preset_box.activated.emit(2)
    assert seen[-1] == ("matrix", PRESETS["matrix"]) and dlg.swatches["text"].text() == "#00FF41"
    dlg.save()
    assert theme.resolve({}, tmp_path / "theme.local.json") == ("matrix", PRESETS["matrix"])


def test_preset_blanco_fondo_blanco_y_velas_huecas_como_la_referencia():
    p = PRESETS["blanco"]
    assert p.bg == "#ffffff" and p.chart_bg == "#ffffff"
    theme.apply(p)
    assert theme.CANDLE_UP_FILL == "#ffffff"                                  # alcista: cuerpo hueco (blanco)
    assert theme.CANDLE_DOWN_FILL != theme.CANDLE_UP_FILL                      # bajista: relleno gris azulado
    assert theme.CANDLE_UP_LINE == theme.CANDLE_DOWN_LINE == "#364e8e"         # mismo borde y mecha azul marino
    r, g, b = (int(theme.CANDLE_DOWN_FILL[i:i + 2], 16) for i in (1, 3, 5))
    assert b > r and b > g                                                      # gris azulado


def test_las_paletas_oscuras_conservan_las_velas_rellenas_de_verde_y_rojo():
    for name in ("negro", "pizarra", "matrix"):
        p = PRESETS[name]
        theme.apply(p)
        assert (theme.CANDLE_UP_FILL, theme.CANDLE_UP_LINE) == (p.bull, p.bull)
        assert (theme.CANDLE_DOWN_FILL, theme.CANDLE_DOWN_LINE) == (p.bear, p.bear)


def test_las_velas_siguen_a_bull_y_bear_hasta_que_se_personalizan():
    theme.apply(theme.build_palette("negro", {"bull": "#123456"}))
    assert theme.CANDLE_UP_FILL == "#123456"                                   # vacío: sigue a bull
    pal = theme.build_palette("negro", {"candle_up_fill": "#ffffff", "candle_up_line": "#000000"})
    theme.apply(pal)
    assert (theme.CANDLE_UP_FILL, theme.CANDLE_UP_LINE) == ("#ffffff", "#000000")
    assert theme.diff_from_preset("negro", pal) == {"candle_up_fill": "#ffffff", "candle_up_line": "#000000"}
    assert theme.validate({"candle_up_fill": ""}) == {"candle_up_fill": ""}     # vuelve a seguir a bull
    with pytest.raises(ThemeError):
        theme.validate({"candle_up_fill": "blanco"})
    with pytest.raises(ThemeError):
        theme.validate({"bull": ""})                                            # el resto de campos no admiten vacío


@pytest.mark.parametrize("name", list(PRESETS))
def test_las_velas_se_distinguen_del_fondo(name):
    p = PRESETS[name]
    for key in theme.CANDLE_KEYS:
        if key.endswith("_line"):
            assert _contrast(theme.effective(p, key), p.chart_bg) >= 3, key     # borde y mecha visibles


def test_dialogo_muestra_y_edita_los_colores_de_vela(qapp, tmp_path, monkeypatch):
    from tradingbot.ui.theme_dialog import ThemeDialog
    monkeypatch.setattr(theme, "LOCAL_THEME_FILE", tmp_path / "theme.local.json")
    monkeypatch.setattr(envconfig, "ENV_FILE", tmp_path / "tradingbot.env")
    seen = []
    dlg = ThemeDialog(None, "negro", PRESETS["negro"], lambda n, p: seen.append(p))
    assert dlg.swatches["candle_up_fill"].text() == PRESETS["negro"].bull.upper()    # efectivo: sigue a bull
    dlg.set_color("candle_up_fill", "#ffffff")
    assert dlg.swatches["candle_up_fill"].text() == "#FFFFFF" and seen[-1].candle_up_fill == "#ffffff"
    dlg.save()
    name, pal = theme.resolve({}, tmp_path / "theme.local.json")
    assert name == "negro" and pal.candle_up_fill == "#ffffff"


def test_el_grafico_pinta_velas_huecas_con_la_paleta_blanco(qapp):
    import numpy as np
    import pandas as pd
    from tradingbot.ui.chart import ChartView

    theme.apply(PRESETS["blanco"])
    chart = ChartView()
    n = 40
    base = 100 + np.cumsum(np.random.default_rng(1).normal(0, 1, n))
    df = pd.DataFrame({"ts": 1_700_000_000 + np.arange(n) * 900, "open": base, "close": base + 0.5,
                       "high": base + 1, "low": base - 1})
    chart.set_candles(df)
    chart.apply_theme()
    assert chart.item._up_fill.name() == "#ffffff" and chart.item._down_fill.name() == "#8a98bb"
    assert chart.item._up_line.name() == "#364e8e"
    chart.resize(500, 300)
    chart.grab()                                                               # pinta sin errores


def test_colores_del_grafico_derivados_en_las_paletas_oscuras():
    for name in ("negro", "pizarra", "matrix"):
        p = PRESETS[name]
        theme.apply(p)
        assert theme.CHART_TEXT == p.muted and theme.CHART_GRID == ""            # rejilla clásica
        assert (theme.LEVEL_HIGH, theme.LEVEL_LOW, theme.LEVEL_OPEN) == (p.bear, p.bull, p.accent)
        assert theme.LEVEL_LABEL == ""                                            # etiqueta = color de su línea


def test_colores_del_grafico_de_la_paleta_blanco():
    theme.apply(PRESETS["blanco"])
    assert theme.CHART_TEXT == "#1d1d1f"                                          # números del eje casi negros
    assert theme.CHART_GRID == "#f1f2f5" and _contrast(theme.CHART_GRID, "#ffffff") < 1.2   # rejilla casi invisible
    assert theme.LEVEL_HIGH == theme.LEVEL_LOW == "#4a8f86" and theme.LEVEL_OPEN == "#4558b8"
    assert theme.LEVEL_LABEL == "#4a5fc1"


def test_los_nuevos_campos_admiten_vacio_pero_no_el_fondo():
    for key in ("chart_text", "chart_grid", "level_high", "level_low", "level_open", "level_label"):
        assert theme.validate({key: ""}) == {key: ""}
    with pytest.raises(ThemeError):
        theme.validate({"chart_bg": ""})


@pytest.mark.parametrize("name", list(PRESETS))
def test_el_texto_del_eje_y_los_niveles_se_leen_sobre_el_fondo(name):
    p = PRESETS[name]
    assert _contrast(theme.effective(p, "chart_text"), p.chart_bg) >= 4.5
    for key in ("level_high", "level_low", "level_open"):
        assert _contrast(theme.effective(p, key), p.chart_bg) >= 3, key
    if p.level_label:
        assert _contrast(p.level_label, p.chart_bg) >= 4.5


def test_el_grafico_aplica_texto_rejilla_y_niveles_de_la_paleta(qapp):
    from tradingbot.ui.chart import ChartView
    chart = ChartView()
    axis = lambda n: chart.getPlotItem().getAxis(n)
    for name, grid_x in (("negro", False), ("blanco", True)):
        theme.apply(PRESETS[name])
        chart.apply_theme()
        assert axis("right").textPen().color().name() == theme.CHART_TEXT
        assert bool(axis("bottom").grid) is grid_x                                # vertical solo con rejilla propia
    theme.apply(PRESETS["blanco"])
    chart.apply_theme()
    assert axis("bottom").grid == 255 and axis("right").pen().color().name() == "#f1f2f5"
    chart.set_levels({"Máx. previo": 101.0, "Mín. previo": 99.0, "Apertura": 100.0})
    colors = [ln.pen.color().name() for ln in chart._lines]
    assert colors == ["#4a8f86", "#4a8f86", "#4558b8"]
    assert all(ln.label.color.name() == "#4a5fc1" for ln in chart._lines)         # etiquetas azules
    theme.apply(PRESETS["negro"])
    chart.apply_theme()
    assert [ln.pen.color().name() for ln in chart._lines] == [PRESETS["negro"].bear, PRESETS["negro"].bull, PRESETS["negro"].accent]
    assert chart._lines[0].label.color.name() == PRESETS["negro"].bear           # etiqueta = color de su línea


def test_el_editor_tiene_pestanas_interfaz_y_grafico(qapp, tmp_path, monkeypatch):
    from tradingbot.ui.theme_dialog import ThemeDialog
    monkeypatch.setattr(theme, "LOCAL_THEME_FILE", tmp_path / "theme.local.json")
    monkeypatch.setattr(envconfig, "ENV_FILE", tmp_path / "tradingbot.env")
    dlg = ThemeDialog(None, "negro", PRESETS["negro"], lambda n, p: None)
    assert [dlg.tabs.tabText(i) for i in range(dlg.tabs.count())] == ["Interfaz", "Gráfico"]
    assert set(dlg.swatches) == set(theme.LABELS)
    assert dlg.swatches["level_label"].text() == "COLOR DE SU LÍNEA"
    dlg.set_color("level_label", "#4a5fc1")
    assert dlg.swatches["level_label"].text() == "#4A5FC1"
    dlg._choose_preset("blanco")
    assert dlg.swatches["chart_grid"].text() == "#F1F2F5" and dlg.swatches["chart_text"].text() == "#1D1D1F"
