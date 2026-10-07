"""Carga de configuración: perfiles MT5 (.env) y ajustes de la app (config.toml)."""
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


DEFAULT_SKILLS = ({"type": "cortex"}, {"type": "feed"}, {"type": "bias"}, {"type": "quotes"})


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


def load_app_config(path: Path | None = None) -> dict:
    """Carga config.toml aplicando valores por defecto."""
    path = path or DEFAULT_CONFIG_FILE
    data: dict = {}
    if path.exists():
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    app = {"symbol": "EURUSD", "timeframe": "15m", "max_bars": 2_000_000, "watchlist": list(DEFAULT_WATCHLIST),
           **data.get("app", {})}
    return {"app": app, "bias": data.get("bias", {}), "theme": data.get("theme", {}), "skills": data.get("skills") or [dict(d) for d in DEFAULT_SKILLS]}
