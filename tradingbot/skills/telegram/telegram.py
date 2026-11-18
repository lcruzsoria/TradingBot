"""Conexión con Telegram: la API de bots por HTTPS, sin librerías extra (urllib).

El token y el chat son secretos: no van en tradingbot.env (que está en el repositorio) sino en el fichero de cuentas, fuera
del repo (el mismo de MT5, C:\\Users\\claude\\mt5\\.env), o en variables de entorno:

    TELEGRAM_TOKEN=123456:ABC...      el que da @BotFather al crear el bot
    TELEGRAM_CHAT_ID=123456789        tu chat con el bot (scripts/telegram_chat_id.py lo averigua)
"""
from __future__ import annotations

import http.client
import json
import secrets
import socket
import urllib.error
import urllib.request
from pathlib import Path

from .secrets import secret

API = "https://api.telegram.org/bot{token}/{method}"
TIMEOUT = 10


class TelegramError(RuntimeError):
    pass


CONNECT_TIMEOUT = 2.0      # por dirección: una que no contesta en 2 s no va a contestar (se pasa a la siguiente)
_last_good: dict[str, tuple] = {}     # host -> última dirección que conectó: se prueba la primera


class _Ipv6FirstConnection(http.client.HTTPSConnection):
    """Conexión HTTPS que prueba antes la última dirección que funcionó y, si no hay, las IPv6: desde esta red la ruta IPv4
    de Telegram llegó a tardar segundos. Cada dirección tiene CONNECT_TIMEOUT para conectar: a veces una se queda colgada
    (1 de cada 8 conexiones esperaba los 10 s enteros antes de probar la otra) y los comandos tardaban en contestar."""

    def connect(self) -> None:
        infos = socket.getaddrinfo(self.host, self.port, 0, socket.SOCK_STREAM)
        good = _last_good.get(self.host)
        infos.sort(key=lambda info: (info[4] != good, info[0] != socket.AF_INET6))
        error: OSError | None = None
        for attempt in (min(CONNECT_TIMEOUT, self.timeout or CONNECT_TIMEOUT), self.timeout):   # rápido y, si todas fallan, con calma
            for family, kind, proto, _name, address in infos:
                sock = socket.socket(family, kind, proto)
                sock.settimeout(attempt)
                try:
                    sock.connect(address)
                    tls = self._context.wrap_socket(sock, server_hostname=self.host)    # el saludo TLS, con el mismo plazo
                    tls.settimeout(self.timeout)
                    self.sock = tls
                except OSError as exc:
                    sock.close()
                    error = exc
                    continue
                _last_good[self.host] = address
                return
            if attempt == self.timeout:
                break
        _last_good.pop(self.host, None)
        raise error or OSError(f"sin dirección para {self.host}")


class _Ipv6FirstHandler(urllib.request.HTTPSHandler):
    def https_open(self, req):
        return self.do_open(_Ipv6FirstConnection, req, context=self._context)


_OPENER = urllib.request.build_opener(_Ipv6FirstHandler)


def credentials(env_file: Path | str | None = None) -> tuple[str | None, str | None]:
    """(token, chat): primero las variables de entorno y, si faltan, el fichero de cuentas."""
    return secret("TELEGRAM_TOKEN", env_file), secret("TELEGRAM_CHAT_ID", env_file)


def call(token: str, method: str, params: dict | None = None) -> dict:
    """Llama a un método de la API de bots y devuelve su `result`. Los fallos, como TelegramError (sin el token)."""
    return _post(token, method, json.dumps(params or {}).encode("utf-8"), "application/json")


def _post(token: str, method: str, data: bytes, content_type: str) -> dict:
    request = urllib.request.Request(API.format(token=token, method=method), data=data,
                                     headers={"Content-Type": content_type})
    try:
        with _OPENER.open(request, timeout=TIMEOUT) as response:
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


def multipart(fields: dict, file_field: str, filename: str, content: bytes, mime: str) -> tuple[bytes, str]:
    """El cuerpo «multipart/form-data» de una subida (campos de texto y un fichero) y su cabecera Content-Type."""
    boundary = "tb" + secrets.token_hex(12)
    crlf = "\r\n"
    body = b"".join(f'--{boundary}{crlf}Content-Disposition: form-data; name="{k}"{crlf}{crlf}{v}{crlf}'.encode("utf-8")
                    for k, v in fields.items())
    head = (f'--{boundary}{crlf}Content-Disposition: form-data; name="{file_field}"; filename="{filename}"{crlf}'
            f"Content-Type: {mime}{crlf}{crlf}")
    body += head.encode("utf-8") + content + f"{crlf}--{boundary}--{crlf}".encode("utf-8")
    return body, f"multipart/form-data; boundary={boundary}"


def send_photo(token: str, chat: str, png: bytes, caption: str = "") -> dict:
    fields = {"chat_id": chat, "parse_mode": "HTML"}
    if caption:
        fields["caption"] = caption
    body, content_type = multipart(fields, "photo", "tradingbot.png", png, "image/png")
    return _post(token, "sendPhoto", body, content_type)
