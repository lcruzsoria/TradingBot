"""Ajustes de arranque y de las skills en tradingbot.env (bloques APP_, FEED_, QUOTES_, BIAS_)."""
import re

import pytest

from tradingbot import envconfig
from tradingbot.skills.bias import BiasEngine
from tradingbot.config import (DEFAULT_BIAS_RULES, DEFAULT_MAX_BARS, DEFAULT_SYMBOL, ConfigError,
                               load_app_config)
from tradingbot.envconfig import EnvConfig, parse
from tradingbot.timeframes import parse_timeframe


def cfg_from(text: str, tmp_path, toml: str = "") -> dict:
    path = tmp_path / "config.toml"
    path.write_text(toml, encoding="utf-8")
    return load_app_config(path, EnvConfig(parse(text)))


def test_sin_tradingbot_env_se_usan_los_valores_del_codigo(tmp_path):
    cfg = cfg_from("", tmp_path)
    assert cfg["app"]["symbol"] == DEFAULT_SYMBOL and cfg["app"]["timeframe"] == "15m"
    assert cfg["app"]["max_bars"] == DEFAULT_MAX_BARS
    assert cfg["app"]["profile"] is None and cfg["app"]["demo"] is False
    assert [r["type"] for r in cfg["bias"]["rules"]] == list(DEFAULT_BIAS_RULES)
    assert cfg["bias"]["min_votes"] == 1 and cfg["bias"]["require_all"] is False


def test_los_valores_de_tradingbot_env_mandan(tmp_path):
    cfg = cfg_from("""
APP_PROFILE=real
APP_DEMO=true
FEED_SYMBOL= NAS100FT.r
FEED_TIMEFRAME=H4
FEED_MAX_BARS=5000
BIAS_RULES=above_below_open
BIAS_MIN_VOTES=2
BIAS_REQUIRE_ALL=true
BIAS_ABOVE_BELOW_OPEN_TOLERANCE_PCT=0,25
""", tmp_path)
    app = cfg["app"]
    assert (app["profile"], app["demo"], app["symbol"], app["timeframe"], app["max_bars"]) == \
        ("real", True, "NAS100FT.r", "4h", 5000)                   # el símbolo conserva sus mayúsculas
    assert cfg["bias"] == {"rules": [{"type": "above_below_open", "tolerance_pct": 0.25}],
                           "min_votes": 2, "require_all": True}
    engine = BiasEngine.from_config(cfg["bias"])
    assert engine.min_votes == 2 and engine.require_all and engine.rules[0].params == {"tolerance_pct": 0.25}


def test_claves_vacias_usan_el_valor_por_defecto_y_ninguna_apaga_las_reglas(tmp_path):
    cfg = cfg_from("FEED_SYMBOL=\nAPP_PROFILE=\nBIAS_RULES=\nBIAS_ABOVE_BELOW_OPEN_TOLERANCE_PCT=\n", tmp_path)
    assert cfg["app"]["symbol"] == DEFAULT_SYMBOL and cfg["app"]["profile"] is None
    assert cfg["bias"]["rules"] == [{"type": t} for t in DEFAULT_BIAS_RULES]
    assert cfg_from("BIAS_RULES=Ninguna\n", tmp_path)["bias"]["rules"] == []


@pytest.mark.parametrize("text, match", [
    ("FEED_TIMEFRAME=H2", "FEED_TIMEFRAME"),
    ("FEED_MAX_BARS=0", "FEED_MAX_BARS"),
    ("FEED_MAX_BARS=muchas", "entero"),
    ("BIAS_MIN_VOTES=0", "BIAS_MIN_VOTES"),
    ("APP_DEMO=quizás", "true o false"),
])
def test_valores_no_validos(tmp_path, text, match):
    with pytest.raises((ConfigError, ValueError), match=match):
        cfg_from(text, tmp_path)


def test_regla_desconocida_en_bias_rules(tmp_path):
    with pytest.raises(ValueError, match="no_existe"):
        BiasEngine.from_config(cfg_from("BIAS_RULES=prev_day_break, no_existe", tmp_path)["bias"])


def test_ajustes_antiguos_de_config_toml_avisan_de_su_clave_nueva(tmp_path):
    toml = '[app]\nsymbol = "EURUSD"\nserver_utc_offset_hours = 3\n[bias]\nmin_votes = 1\n'
    with pytest.raises(ConfigError) as err:
        cfg_from("", tmp_path, toml)
    assert all(k in str(err.value) for k in ("FEED_SYMBOL", "QUOTES_SERVER_UTC_OFFSET", "BIAS_MIN_VOTES"))
    assert cfg_from("", tmp_path, '[app]\nwatchlist = ["DJ30"]\n')["app"]["watchlist"] == ["DJ30"]


def test_timeframe_por_clave_o_por_nombre_en_pantalla():
    assert parse_timeframe("M15") == parse_timeframe("15m") == "15m"
    assert parse_timeframe(" h7 ") == "7h" and parse_timeframe("1D") == "1d" and parse_timeframe("1w") == "1w"
    with pytest.raises(ValueError, match="M15"):
        parse_timeframe("M2")


def test_quotes_lee_su_bloque():
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    env = EnvConfig(parse("QUOTES_INTERVAL=0,5\nQUOTES_SERVER_UTC_OFFSET=-4.5\n"))
    skill = SkillManager(EventBus(), Services(None, None, {"app": {}}, env), [{"type": "quotes"}]).skills["quotes"]
    skill.on_start()
    assert skill.interval == 0.5 and skill.fixed_offset == -16200
    skill.services.env = EnvConfig({"QUOTES_INTERVAL": "0"})
    with pytest.raises(ValueError, match="QUOTES_INTERVAL"):
        skill.on_start()


def test_el_tradingbot_env_del_proyecto_documenta_cada_clave_con_sus_valores_por_defecto():
    lines = envconfig.ENV_FILE.read_text(encoding="utf-8").splitlines()
    keys = [m.group(1) for line in lines if (m := re.match(r"#?([A-Z][A-Z0-9_]+)=", line))]
    for key in ("APP_PROFILE", "APP_DEMO", "FEED_SYMBOL", "FEED_TIMEFRAME", "FEED_MAX_BARS", "QUOTES_INTERVAL",
                "QUOTES_SERVER_UTC_OFFSET", "BIAS_RULES", "BIAS_MIN_VOTES", "BIAS_REQUIRE_ALL", "TBR_SHOW",
                "TBR_DAYS", "TBR_OPACITY", "TBR_MAX_TF_MINUTES", "TBR_ZONES", "TBR_ASIA_HOURS", "TBR_NY_PM_COLOR",
                "LEVELS_SHOW_TDO", "LEVELS_SHOW_MIDNIGHT", "LEVELS_SHOW_PDHL", "LEVELS_SEPARATORS",
                "LEVELS_DAYS", "LEVELS_MAX_TF_MINUTES", "LEVELS_TDO_COLOR", "LEVELS_SEPARATOR_COLOR",
                "LEVELS_DAY_START", "LEVELS_INDEX_DAY_START", "LEVELS_US_INDICES"):
        assert key in keys, f"falta {key} en tradingbot.env"
    for i, line in enumerate(lines):                       # cada grupo de claves, con su comentario encima
        if re.match(r"[A-Z]", line):
            j = i - 1
            while re.match(r"[A-Z]", lines[j]):
                j -= 1
            assert lines[j].startswith("#"), f"{line} no tiene comentario"
    # tal como se sube al repositorio, el fichero equivale a los valores por defecto del código
    from tradingbot.config import DEFAULT_CONFIG_FILE
    project, defaults = load_app_config(DEFAULT_CONFIG_FILE, envconfig.load(environ={})), load_app_config(DEFAULT_CONFIG_FILE)
    assert project["app"] == defaults["app"]
    rules = lambda cfg: [(r["type"], float(r.get("tolerance_pct", 0))) for r in cfg["bias"]["rules"]]  # noqa: E731
    assert rules(project) == rules(defaults)
    assert {k: project["bias"][k] for k in ("min_votes", "require_all")} == \
        {k: defaults["bias"][k] for k in ("min_votes", "require_all")}


def test_las_opciones_de_la_linea_de_comandos_mandan(monkeypatch):
    from tradingbot.__main__ import parse_args
    assert parse_args([]).demo is None                      # sin opción: decide APP_DEMO
    assert parse_args(["--demo"]).demo is True and parse_args(["--no-demo"]).demo is False


def test_las_zonas_tbr_del_proyecto_son_las_del_codigo():
    from tradingbot.skills.tbr.zones import zones_from_settings
    assert zones_from_settings(envconfig.load(environ={}).section("TBR")) == zones_from_settings(EnvConfig())
