import pytest

from tradingbot.config import ConfigError, load_profiles, select_profile


def write_env(tmp_path, text):
    p = tmp_path / ".env"
    p.write_text(text, encoding="utf-8")
    return p


def test_lee_varios_perfiles(tmp_path, monkeypatch):
    monkeypatch.delenv("MT5_REAL_PASSWORD", raising=False)
    env = write_env(tmp_path, """
MT5_DEFAULT=demo
MT5_DEMO_LOGIN=26231460
MT5_DEMO_SERVER=VantageMarkets-Demo
MT5_DEMO_PASSWORD=
MT5_REAL_LOGIN=111
MT5_REAL_SERVER=Vantage-Live
MT5_REAL_PASSWORD="secreto"
""")
    profiles, default = load_profiles(env)
    assert set(profiles) == {"demo", "real"} and default == "demo"
    assert profiles["demo"].password is None and profiles["demo"].is_demo
    assert profiles["real"].password == "secreto" and not profiles["real"].is_demo
    assert select_profile(profiles, default, None).name == "demo"
    assert select_profile(profiles, default, "REAL").login == 111


def test_password_desde_entorno(tmp_path, monkeypatch):
    monkeypatch.setenv("MT5_DEMO_PASSWORD", "desde-entorno")
    env = write_env(tmp_path, "MT5_DEMO_LOGIN=1\nMT5_DEMO_SERVER=S\n")
    assert load_profiles(env)[0]["demo"].password == "desde-entorno"


def test_errores(tmp_path):
    with pytest.raises(ConfigError):
        load_profiles(tmp_path / "no_existe.env")
    with pytest.raises(ConfigError):
        load_profiles(write_env(tmp_path, "MT5_DEMO_LOGIN=abc\nMT5_DEMO_SERVER=S\n"))
    profiles, default = load_profiles(write_env(tmp_path, "MT5_DEMO_LOGIN=1\nMT5_DEMO_SERVER=S\n"))
    with pytest.raises(ConfigError):
        select_profile(profiles, default, "otro")
