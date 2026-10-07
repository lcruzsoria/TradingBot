import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from tradingbot import envconfig
from tradingbot.envconfig import EnvConfig, load, parse, set_value
from tradingbot.ui import theme
from tradingbot.ui.theme import PRESETS, ThemeError

SAMPLE = """\
# ---- UI - interfaz ----
UI_THEME=matrix
#UI_THEME=negro
  ui_extra = "con comillas"
APP_AUTO_UPDATE=true
BIAS_MIN_VOTES=2
BIAS_RATIO=1,5
BIAS_RULES=prev_day_break, above_below_open
"""


def test_parse_ignora_comentarios_y_normaliza():
    values = parse(SAMPLE)
    assert values["UI_THEME"] == "matrix" and "UI_EXTRA" in values and values["UI_EXTRA"] == "con comillas"
    assert list(values).count("UI_THEME") == 1                     # la línea comentada no cuenta


def test_tipos_y_bloques_por_skill():
    env = EnvConfig(parse(SAMPLE))
    assert env.get_bool("APP_AUTO_UPDATE") is True and env.get_bool("NO_EXISTE", default=True) is True
    bias = env.section("BIAS")
    assert bias.get_int("MIN_VOTES") == 2 and bias.get_float("RATIO") == 1.5
    assert bias.get_list("RULES") == ["prev_day_break", "above_below_open"]
    assert env.section("ui").get("THEME") == "matrix" and env.section("UI").get("NADA", "x") == "x"
    with pytest.raises(ValueError, match="entero"):
        EnvConfig({"A": "dos"}).get_int("A")
    with pytest.raises(ValueError, match="true o false"):
        EnvConfig({"A": "quizás"}).get_bool("A")


def test_las_variables_de_entorno_mandan_sobre_el_fichero(tmp_path):
    f = tmp_path / "tradingbot.env"
    f.write_text(SAMPLE, encoding="utf-8")
    assert load(f, environ={}).get("UI_THEME") == "matrix"
    assert load(f, environ={"UI_THEME": "blanco"}).get("UI_THEME") == "blanco"
    assert load(tmp_path / "no_existe.env", environ={}).values == {}


def test_set_value_activa_la_opcion_elegida_y_comenta_las_demas(tmp_path):
    f = tmp_path / "tradingbot.env"
    f.write_text("# cabecera\nUI_THEME=matrix\n#UI_THEME=negro\n#UI_THEME=blanco\nOTRA=1\n", encoding="utf-8")
    set_value(f, "UI_THEME", "blanco")
    assert f.read_text(encoding="utf-8") == "# cabecera\n#UI_THEME=matrix\n#UI_THEME=negro\nUI_THEME=blanco\nOTRA=1\n"
    set_value(f, "UI_THEME", "pizarra")              # opción que no estaba: se activa junto a las demás
    lines = f.read_text(encoding="utf-8").splitlines()
    assert "UI_THEME=pizarra" in lines and "#UI_THEME=blanco" in lines and lines[0] == "# cabecera"
    assert parse(f.read_text(encoding="utf-8"))["UI_THEME"] == "pizarra"
    set_value(f, "NUEVA_CLAVE", "7")                 # clave nueva: al final
    assert f.read_text(encoding="utf-8").splitlines()[-1] == "NUEVA_CLAVE=7"


def test_el_tradingbot_env_del_proyecto():
    text = envconfig.ENV_FILE.read_text(encoding="utf-8")
    env = load(environ={})
    active = env.get("UI_THEME")                       # la que elija el usuario (botón Skins > Guardar)
    assert active in PRESETS
    alternatives = {line.split("=", 1)[1] for line in text.splitlines() if line.startswith("#UI_THEME=")}
    assert alternatives == set(PRESETS) - {active}                             # el resto, comentadas
    assert theme.DEFAULT_PRESET == "matrix"                                     # sin UI_THEME, Matrix
    assert {p.stem for p in (envconfig.ENV_FILE.parent / "screenshots").glob("*.png")} == set(PRESETS)
    assert env.get_bool("APP_AUTO_UPDATE") is True
    assert "contraseña" in text.lower() and "PASSWORD" not in text            # aviso, y sin secretos


def test_la_paleta_de_arranque_manda(tmp_path):
    local = tmp_path / "theme.local.json"
    assert theme.resolve({}, local, startup="blanco") == ("blanco", PRESETS["blanco"])
    assert theme.resolve({}, local, startup=" Matrix ")[0] == "matrix"
    # colores guardados para OTRA paleta no se aplican; los de la misma, sí
    theme.save_local("negro", theme.build_palette("negro", {"text": "#ffffff"}), local)
    assert theme.resolve({}, local, startup="matrix")[1] == PRESETS["matrix"]
    assert theme.resolve({}, local, startup="negro")[1].text == "#ffffff"
    assert theme.resolve({"bull": "#00ff00"}, local, startup="matrix")[1].bull == "#00ff00"      # config.toml sin preset
    assert theme.resolve({"preset": "negro", "bull": "#00ff00"}, local, startup="matrix")[1].bull == PRESETS["matrix"].bull
    with pytest.raises(ThemeError, match="UI_THEME"):
        theme.resolve({}, local, startup="rosa")
    assert theme.resolve({}, tmp_path / "nada.json")[0] == "matrix"             # sin nada: Matrix


def test_cada_skill_lee_su_bloque():
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    env = EnvConfig(parse("BIAS_MIN_VOTES=2\nFEED_ALGO=x\n"))
    manager = SkillManager(EventBus(), Services(None, None, {"app": {}}, env), [{"type": "bias"}, {"type": "feed"}])
    assert manager.skills["bias"].settings.get_int("MIN_VOTES") == 2
    assert manager.skills["feed"].settings.get("ALGO") == "x" and manager.skills["feed"].settings.get("MIN_VOTES") is None
    sin_env = SkillManager(EventBus(), Services(None, None, {"app": {}}), [{"type": "bias"}])
    assert sin_env.skills["bias"].settings.values == {}


def test_guardar_en_el_editor_fija_la_paleta_de_arranque(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot.ui.theme_dialog import ThemeDialog
    QApplication.instance() or QApplication([])
    env_file = tmp_path / "tradingbot.env"
    env_file.write_text("UI_THEME=matrix\n#UI_THEME=negro\n#UI_THEME=pizarra\n#UI_THEME=blanco\n", encoding="utf-8")
    monkeypatch.setattr(envconfig, "ENV_FILE", env_file)
    monkeypatch.setattr(theme, "LOCAL_THEME_FILE", tmp_path / "theme.local.json")
    dlg = ThemeDialog(None, "matrix", PRESETS["matrix"], lambda *_: None)
    dlg._choose_preset("blanco")
    dlg.save()
    assert load(env_file, environ={}).get("UI_THEME") == "blanco"
    assert "blanco" in dlg.hint.text() and "tradingbot.env" in dlg.hint.text()
