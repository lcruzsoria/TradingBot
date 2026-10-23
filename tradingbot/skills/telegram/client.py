"""Conexión con Telegram: la API de bots por HTTPS, sin librerías extra (urllib).

El token y el chat son secretos: no van en tradingbot.env (que está en el repositorio) sino en el fichero de cuentas, fuera
del repo (el mismo de MT5, C:\\Users\\claude\\mt5\\.env), o en variables de entorno:

    TELEGRAM_TOKEN=123456:ABC...      el que da @BotFather al crear el bot
    TELEGRAM_CHAT_ID=123456789        tu chat con el bot (scripts/telegram_chat_id.py lo averigua)
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from ...config import DEFAULT_ENV_FILE
from ...envconfig import parse

API = "https://api.telegram.org/bot{token}/{method}"
TIMEOUT = 10


class TelegramError(RuntimeError):
    pass


def credentials(env_file: Path | str | None = None) -> tuple[str | None, str | None]:
    """(token, chat): primero las variables de entorno y, si faltan, el fichero de cuentas."""
    token, chat = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat:
        return token, chat
    path = Path(env_file or DEFAULT_ENV_FILE)
    try:
        values = parse(path.read_text(encoding="utf-8"))
    except OSError:
        values = {}
    return token or values.get("TELEGRAM_TOKEN") or None, chat or values.get("TELEGRAM_CHAT_ID") or None


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
