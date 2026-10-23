"""Averigua el TELEGRAM_CHAT_ID de tu chat con el bot y, si ya está puesto, manda un mensaje de prueba.

Pasos:
    1. En Telegram, habla con @BotFather, /newbot, y copia el token que te da.
    2. Ponlo en el fichero de cuentas (fuera del repo, C:\\Users\\claude\\mt5\\.env):  TELEGRAM_TOKEN=...
    3. Abre el chat con tu bot nuevo y mándale cualquier mensaje (p. ej. «hola»).
    4. Ejecuta (desde la carpeta del proyecto):
           uv run python scripts/telegram_chat_id.py
       y copia el TELEGRAM_CHAT_ID que sale al mismo fichero.
    5. Vuelve a ejecutarlo: con los dos puestos, manda un mensaje de prueba a tu chat.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main() -> int:
    from tradingbot.config import DEFAULT_ENV_FILE
    from tradingbot.skills.movil import telegram as client

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--env", type=Path, default=DEFAULT_ENV_FILE, help=f"fichero de cuentas (por defecto {DEFAULT_ENV_FILE})")
    args = parser.parse_args()

    token, chat = client.credentials(args.env)
    if not token:
        print(f"Falta TELEGRAM_TOKEN en {args.env} (o en la variable de entorno). Pídeselo a @BotFather.")
        return 1
    try:
        me = client.call(token, "getMe")
        print(f"Bot: @{me.get('username')} ({me.get('first_name')})")
        if chat:
            client.send_message(token, chat, "🤖 <b>TradingBot</b>: prueba de conexión correcta.")
            print(f"Mensaje de prueba enviado al chat {chat}. Ya puedes poner TELEGRAM_ENABLED=true en tradingbot.env.")
            return 0
        chats = {}
        for update in client.call(token, "getUpdates"):
            message = update.get("message") or update.get("edited_message") or {}
            c = message.get("chat") or {}
            if c.get("id") is not None:
                chats[c["id"]] = c.get("username") or c.get("title") or c.get("first_name") or ""
    except client.TelegramError as exc:
        print(exc)
        return 1
    if not chats:
        print("No hay mensajes: abre el chat con tu bot en Telegram, mándale «hola» y vuelve a ejecutar esto.")
        return 1
    for chat_id, name in chats.items():
        print(f"TELEGRAM_CHAT_ID={chat_id}    ({name})")
    print(f"Copia la línea a {args.env} y vuelve a ejecutar el script para mandar un mensaje de prueba.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
