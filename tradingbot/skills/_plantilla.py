"""Plantilla para crear una skill nueva.

1. Copia este fichero con otro nombre SIN guion bajo inicial (p. ej. risk.py).
2. Cambia la clave de @register_skill, el título, los temas y la lógica de handle().
3. Actívala en config.toml:

       [[skills]]
       type = "risk"
       slot = 2            # 0-5 (anillo, horario desde arriba), "center" o "aux1".."aux3"

Cómo se comunica una skill:
  - subscribes: temas que quiere recibir. Cada mensaje llega a handle(event).
  - self.publish(tema, {...}): envía un mensaje a quien esté suscrito a ese tema.
  - interval: si lo defines, tick() se ejecuta periódicamente (p. ej. cada 5 s).
  - self.set_caption("texto"): línea que se ve bajo el nombre en el hexágono.
  - Si handle() lanza una excepción, el hexágono se pone en rojo y las demás skills siguen.

Temas que ya existen (payload entre llaves):
  feed.load {symbol, timeframe}      pide cargar velas            (ui -> feed)
  feed.connected {info, symbols}     conexión con MT5 abierta     (feed)
  candles.loaded {symbol, timeframe, df, seconds}                 (feed)
  quotes.updated {quotes, account}   cada segundo                 (quotes)
  bias.recalc {}                     pide recalcular el sesgo     (ui -> bias)
  bias.updated {result, symbol, timeframe}                        (bias)
  trade.request {request_id, direction}   "¿puedo operar?"        (cualquiera -> cortex)
  trade.verdict {request_id, direction, allowed, reason}          (cortex)
"""
from ..core import Event, Skill, register_skill


# @register_skill("mi_skill")        # <- descomenta al copiar la plantilla
class PlantillaSkill(Skill):
    title = "Mi skill"
    description = "Qué hace esta skill, en una frase."
    subscribes = ("trade.verdict",)
    publishes = ("mi_skill.listo",)
    slot = 2

    def handle(self, event: Event) -> None:
        # event.topic, event.payload, event.source
        self.set_caption(f"recibido {event.topic}")
        self.publish("mi_skill.listo", {"ok": True})
