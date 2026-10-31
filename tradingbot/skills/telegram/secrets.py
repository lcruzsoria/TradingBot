"""Secretos de la skill Telegram (token de Telegram, chat, clave del panel): nunca en tradingbot.env, que está en el repositorio.

Se buscan primero en las variables de entorno y, si no están, en el fichero de cuentas, fuera del repo (el mismo de MT5,
C:\\Users\\claude\\mt5\\.env, o el que se pase con --env).
"""
from __future__ import annotations

import os
from pathlib import Path

from ...config import DEFAULT_ENV_FILE
from ...envconfig import parse


def secret(key: str, env_file: Path | str | None = None) -> str | None:
    value = os.environ.get(key)
    if value:
        return value
    try:
        values = parse(Path(env_file or DEFAULT_ENV_FILE).read_text(encoding="utf-8"))
    except OSError:
        return None
    return values.get(key.upper()) or None
