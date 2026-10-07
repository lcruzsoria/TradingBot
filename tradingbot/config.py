"""Carga de configuración: perfiles MT5 (.env), ajustes de tradingbot.env y lo que queda en config.toml.

Los ajustes de arranque y de cada skill viven en tradingbot.env (bloques APP_, FEED_, BIAS_, QUOTES_...). Aquí están
sus valores por defecto: una clave que falta o está vacía usa el de este fichero.
config.toml conserva solo la watchlist inicial, los colores sueltos ([theme]) y la disposición de las skills.
"""
from __future__ import annotations

import os
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENV_FILE = Path(os.environ.get("TRADINGBOT_ENV", r"C:\Users\claude\mt5\.env"))
DEFAULT_CONFIG_FILE = PROJECT_ROOT / "config.toml"


DEFAULT_WATCHLIST = ("NAS100", "SP500", "DJ30", "EURUSD", "XAUUSD", "USOIL", "BTCUSD", "ETHUSD")


DEFAULT_SKILLS = ({"type": "cortex"}, {"type": "feed"}, {"type": "bias"}, {"type": "tbr"}, {"type": "levels"},
                  {"type": "quotes"})

# Valores por defecto de tradingbot.env
DEFAULT_SYMBOL = "EURUSD"                                     # FEED_SYMBOL
DEFAULT_MAX_BARS = 2_000_000                                  # FEED_MAX_BARS
DEFAULT_BIAS_RULES = ("prev_day_break", "above_below_open")   # BIAS_RULES
DEFAULT_MIN_VOTES = 1                                         # BIAS_MIN_VOTES
DEFAULT_REQUIRE_ALL = False                                   # BIAS_REQUIRE_ALL

# Ajustes que estaban en config.toml y ahora van en tradingbot.env: (sección, clave) -> clave nueva
MOVED_TO_ENV = {
    ("app", "symbol"): "FEED_SYMBOL", ("app", "timeframe"): "FEED_TIMEFRAME", ("app", "max_bars"): "FEED_MAX_BARS",
    ("app", "server_utc_offset_hours"): "QUOTES_SERVER_UTC_OFFSET",
    ("bias", "min_votes"): "BIAS_MIN_VOTES", ("bias", "require_all"): "BIAS_REQUIRE_ALL",
    ("bias", "rules"): "BIAS_RULES",
}


class ConfigError(Exception):
    """Error de configuración legible para el usuario."""


@dataclass(frozen=True)
class Mt5Profile:
    name: str
    login: int
    server: str
    password: str | None = None
    terminal_path: str | None = None

    @property
    def is_demo(self) -> bool:
        return "demo" in self.name.lower()

    @property
    def label(self) -> str:
        return f"{self.name} - {self.login} @ {self.server}"


def parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        raise ConfigError(f"No existe el fichero de cuentas: {path}")
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_profiles(path: Path = DEFAULT_ENV_FILE) -> tuple[dict[str, Mt5Profile], str | None]:
    """Lee los perfiles MT5_<NOMBRE>_LOGIN/_SERVER/_PASSWORD del .env.

    Devuelve (perfiles por nombre en minúsculas, perfil por defecto).
    """
    values = parse_env_file(path)
    terminal_path = values.get("MT5_PATH") or None
    profiles: dict[str, Mt5Profile] = {}
    for key in values:
        match = re.fullmatch(r"MT5_(.+)_LOGIN", key)
        if not match:
            continue
        tag = match.group(1)
        raw_login = values[key]
        server = values.get(f"MT5_{tag}_SERVER", "")
        if not raw_login.isdigit() or not server:
            raise ConfigError(f"Perfil '{tag.lower()}': MT5_{tag}_LOGIN debe ser numérico y MT5_{tag}_SERVER no puede estar vacío.")
        password = values.get(f"MT5_{tag}_PASSWORD") or os.environ.get(f"MT5_{tag}_PASSWORD") or None
        profiles[tag.lower()] = Mt5Profile(tag.lower(), int(raw_login), server, password, terminal_path)
    if not profiles:
        raise ConfigError(f"No hay ningún perfil (MT5_<NOMBRE>_LOGIN) en {path}")
    default = (values.get("MT5_DEFAULT") or "").lower() or None
    return profiles, default


def select_profile(profiles: dict[str, Mt5Profile], default: str | None, requested: str | None) -> Mt5Profile:
    name = (requested or default or next(iter(profiles))).lower()
    if name not in profiles:
        raise ConfigError(f"Perfil '{name}' no encontrado. Disponibles: {', '.join(profiles)}")
    return profiles[name]


def load_app_config(path: Path | None = None, env=None) -> dict:
    """Carga config.toml y le añade los ajustes de tradingbot.env (`env`, un EnvConfig).

    Sin `env` se usan los valores por defecto del código (así las capturas no dependen de tu tradingbot.env).
    """
    from .envconfig import EnvConfig
    path = path or DEFAULT_CONFIG_FILE
    data: dict = {}
    if path.exists():
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    moved = [f"[{sec}] {key} -> {new}" for (sec, key), new in MOVED_TO_ENV.items() if key in data.get(sec, {})]
    if moved:
        raise ConfigError(f"Estos ajustes de {path.name} ahora van en tradingbot.env. Muévelos y bórralos de "
                          f"{path.name}:\n  " + "\n  ".join(moved))
    env = env if env is not None else EnvConfig()
    app = {"watchlist": list(DEFAULT_WATCHLIST), **data.get("app", {}), **app_settings(env)}
    return {"app": app, "bias": bias_settings(env.section("BIAS")), "theme": data.get("theme", {}),
            "skills": data.get("skills") or [dict(d) for d in DEFAULT_SKILLS]}


def app_settings(env) -> dict:
    """Bloques APP_ y FEED_ de tradingbot.env, validados y con sus valores por defecto."""
    from .timeframes import DEFAULT_TIMEFRAME, parse_timeframe
    feed = env.section("FEED")
    max_bars = feed.get_int("MAX_BARS", DEFAULT_MAX_BARS)
    if max_bars <= 0:
        raise ConfigError(f"FEED_MAX_BARS={max_bars} debe ser mayor que 0.")
    try:
        timeframe = parse_timeframe(feed.get("TIMEFRAME", DEFAULT_TIMEFRAME))
    except ValueError as exc:
        raise ConfigError(f"FEED_TIMEFRAME: {exc}") from None
    return {
        "symbol": feed.get("SYMBOL", DEFAULT_SYMBOL).strip(),    # tal cual: MT5 distingue mayúsculas
        "timeframe": timeframe,
        "max_bars": max_bars,
        "profile": env.get("APP_PROFILE"),                         # None = MT5_DEFAULT del .env de cuentas
        "demo": env.get_bool("APP_DEMO", False),
    }


def bias_settings(bias) -> dict:
    """Bloque BIAS_ de tradingbot.env (ya sin prefijo) en el formato de BiasEngine.from_config.

    BIAS_RULES lista las reglas activas, separadas por comas (vacía: las de ejemplo; "ninguna": sin reglas).
    Los parámetros de cada regla van en BIAS_<REGLA>_<PARÁMETRO>, por ejemplo BIAS_ABOVE_BELOW_OPEN_TOLERANCE_PCT=0.1
    llega a la regla above_below_open como tolerance_pct=0.1.
    """
    names = [n.lower() for n in bias.get_list("RULES", list(DEFAULT_BIAS_RULES))]
    if names == ["ninguna"]:
        names = []
    rules = []
    for name in names:
        head = name.upper() + "_"
        params = {k[len(head):].lower(): _scalar(v) for k, v in bias.values.items() if k.startswith(head) and v != ""}
        rules.append({"type": name, **params})
    min_votes = bias.get_int("MIN_VOTES", DEFAULT_MIN_VOTES)
    if min_votes < 1:
        raise ConfigError(f"BIAS_MIN_VOTES={min_votes} debe ser 1 o más.")
    return {"rules": rules, "min_votes": min_votes, "require_all": bias.get_bool("REQUIRE_ALL", DEFAULT_REQUIRE_ALL)}


def _scalar(text: str):
    """Convierte el texto de un parámetro en número cuando lo es (admite coma decimal)."""
    for cast in (int, lambda t: float(t.replace(",", "."))):
        try:
            return cast(text)
        except ValueError:
            pass
    return text
