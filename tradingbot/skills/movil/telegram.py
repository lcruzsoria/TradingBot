"""Conexión con Telegram: la API de bots por HTTPS, sin librerías extra (urllib).

El token y el chat son secretos: no van en tradingbot.env (que está en el repositorio) sino en el fichero de cuentas, fuera
del repo (el mismo de MT5, C:\\Users\\claude\\mt5\\.env), o en variables de entorno:

    TELEGRAM_TOKEN=123456:ABC...      el que da @BotFather al crear el bot
    TELEGRAM_CHAT_ID=123456789        tu chat con el bot (scripts/telegram_chat_id.py lo averigua)
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

from .secrets import secret

API = "https://api.telegram.org/bot{token}/{method}"
TIMEOUT = 10


class TelegramError(RuntimeError):
    pass


def credentials(env_file: Path | str | None = None) -> tuple[str | None, str | None]:
    """(token, chat): primero las variables de entorno y, si faltan, el fichero de cuentas."""
    return secret("TELEGRAM_TOKEN", env_file), secret("TELEGRAM_CHAT_ID", env_file)


def call(token: str, method: str, params: dict | None = None) -> dict:
    """Llama a un método de la API de bots y devuelve su `result`. Los fallos, como TelegramError (sin el token)."""
    data = json.dumps(params or {}).encode("utf-8")
    request = urllib.request.Request(API.format(token=token, method=method), data=data,
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8")).get("description", "")
        except ValueError:
            detail = ""
        raise TelegramError(f"Telegram respondió {exc.code}: {detail or exc.reason}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise TelegramError(f"sin conexión con Telegram ({getattr(exc, 'reason', exc)})") from None
    if not body.get("ok"):
        raise TelegramError(f"Telegram: {body.get('description', 'respuesta no válida')}")
    return body.get("result") or {}


def send_message(token: str, chat: str, text: str) -> dict:
    return call(token, "sendMessage", {"chat_id": chat, "text": text, "parse_mode": "HTML",
                                       "disable_web_page_preview": True})


def get_updates(token: str, offset: int | None = None) -> list:
    """Los mensajes que han llegado al bot desde `offset` (sin esperar: se pregunta cada pocos segundos)."""
    params: dict = {"timeout": 0, "allowed_updates": ["message"]}
    if offset is not None:
        params["offset"] = offset
    result = call(token, "getUpdates", params)
    return result if isinstance(result, list) else []


def set_commands(token: str, commands: list[tuple[str, str]]) -> None:
    """El menú de comandos que Telegram enseña al escribir «/»."""
    call(token, "setMyCommands", {"commands": [{"command": c, "description": d} for c, d in commands]})
