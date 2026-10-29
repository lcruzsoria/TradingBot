"""Texto de los avisos de Telegram (HTML de Telegram: <b>, <i>, sin más)."""
from __future__ import annotations

import html
from datetime import date

from ..bias.rules import fmt_price

SIDE = {"long": "Largo", "short": "Corto"}
RESULT = {"objetivo": ("✅", "TP"), "stop": ("❌", "SL"), "breakeven": ("⚪", "BE"), "tiempo": ("⏱", "T")}


def _e(value) -> str:
    return html.escape(str(value))


def _day(value) -> str:
    return value.strftime("%d/%m") if isinstance(value, date) else _e(value or "")


def _strategy(title) -> str:
    """Primera línea de cada aviso: qué estrategia lo origina (varias comparten la cuenta del perfil)."""
    return f"<b>Estrategia:</b> {_e(title)}\n"


def _where(order) -> str:
    """Zona TBR y día, si la estrategia los tiene (Calendario no): línea propia tras la cabecera, vacía si no hay."""
    return f"{_e(order.tbr_zone)} {_day(order.tbr_day)}\n" if order.tbr_zone else ""


def _levels(order) -> str:
    parts = [f"Entrada {fmt_price(order.price)}"]
    if order.stop is not None:
        parts.append(f"Stop {fmt_price(order.stop)}")
    if order.target is not None:
        parts.append(f"Obj. {fmt_price(order.target)}")
    return " · ".join(parts)


def _bias_text(bias, score, lateral: bool = False, efficiency=None) -> str:
    """«Bearish -4», «No Bias · lateral -4 · ef. 0.08»: la eficiencia del precio explica por qué el filtro de lateralidad
    anula una puntuación (la de las reglas) que por sí sola daría sesgo."""
    ef = f" · ef. {efficiency:.2f}" if efficiency is not None else ""
    return f"{_e(bias)}{' · lateral' if lateral else ''} {score:+g}{ef}"


def _footer(profile: str | None) -> str:
    return f"\n<i>perfil {_e(profile)}</i>" if profile else ""


def opened(order, profile: str | None = None) -> str:
    return (f"{_strategy(order.pattern)}🟡 <b>Abre {SIDE.get(order.direction, order.direction)} {_e(order.symbol)}</b> "
            f"{_e(order.timeframe)}\n{_where(order)}{_levels(order)}\n"
            f"Sesgo {_bias_text(order.bias, order.score, order.lateral, order.efficiency)}{_footer(profile)}")


def closed(order, result, profile: str | None = None) -> str:
    icon, short = RESULT.get(result.result, ("•", result.result))
    peak = f" · máx. {result.max_r:+.2f} R" if result.max_r is not None else ""
    return (f"{_strategy(order.pattern)}{icon} <b>{short} {result.r:+.2f} R · {SIDE.get(order.direction, order.direction)} "
            f"{_e(order.symbol)}</b> {_e(order.timeframe)}\n{_where(order)}"
            f"Entrada {fmt_price(order.price)} → salida {fmt_price(result.exit_price)}{peak}{_footer(profile)}")


def decision(payload: dict, profile: str | None = None) -> str:
    hit, tbr, dec = payload["hit"], payload.get("tbr"), payload["decision"]
    zone = f"{_e(tbr.zone)}\n" if tbr is not None and getattr(tbr, "zone", "") else ""
    head = "✓ GO" if dec.allowed else "✕ NO GO"
    return (f"{_strategy(hit.title)}<b>{head} {SIDE.get(hit.direction, hit.direction)} {_e(payload['symbol'])}</b> "
            f"{_e(payload['timeframe'])}\n{zone}{_e(dec.reason)}{_footer(profile)}")


def started(profile: str | None = None) -> str:
    return f"🤖 <b>TradingBot en marcha</b>{_footer(profile)}"


# -- respuestas a los comandos (lo mismo que enseña el panel) -------------------------------------------------------
COMMANDS = (("panel", "Imagen del panel"), ("captura", "Captura de la ventana del bot"),
            ("dibujar", "Dibuja los setups ejecutados hoy (/dibujar 2, /dibujar nas100)"),
            ("estado", "Abiertas, resultado de hoy y sesgo"), ("abiertas", "Operaciones abiertas con su R"),
            ("hoy", "Cierres y resultado de hoy"), ("sesgo", "Sesgo de cada mercado"),
            ("decisiones", "Últimos GO / NO GO de Cortex"), ("ayuda", "Lista de comandos"))


def _r(value) -> str:
    return "–" if value is None else f"{value:+.2f} R"


def _header(s: dict) -> str:
    profile = f" · {_e(s['profile'])}" if s.get("profile") else ""
    return f"<b>TradingBot{profile}</b> <i>{_e(s['updated'])}</i>"


def open_positions(s: dict) -> str:
    if not s["open"]:
        return "<b>Abiertas</b>\nNinguna operación abierta."
    lines = ["<b>Abiertas</b>"]
    for o in s["open"]:
        now = f" · precio {fmt_price(o['price'])}" if o.get("price") is not None else ""
        lines.append(f"🟡 <b>{_e(o['side'])} {_e(o['symbol'])}</b> {_e(o['timeframe'])} · {_r(o['r_now'])}\n"
                     f"{_e(o['pattern'])} · {_e(o['zone'])}\n"
                     f"Entrada {fmt_price(o['entry'])} · Stop {fmt_price(o['stop'])} · Obj. {fmt_price(o['target'])}{now}")
    return "\n".join(lines)


def today(s: dict) -> str:
    t = s["today"]
    if not t["count"]:
        return "<b>Hoy</b>\nAún no ha cerrado ninguna."
    head = (f"<b>Hoy</b> {_r(t['r'])}\n{t['count']} cerrada(s): {t['TP']} TP · {t['SL']} SL · {t['BE']} BE"
            + (f" · {t['T']} T" if t["T"] else ""))
    rows = [c for c in s["closed"] if c["closed_day"] == t["day"]]
    icon = {short: ico for ico, short in RESULT.values()}
    lines = [f"{icon.get(c['result'], '•')} {_e(c['result'])} {_r(c['r'])} · {_e(c['side'])} {_e(c['symbol'])} · {_e(c['pattern'])}"
             for c in rows]
    return "\n".join([head, *lines])


def bias(s: dict) -> str:
    if not s["bias"]:
        return "<b>Sesgo</b>\nTodavía no hay sesgo calculado."
    icon = {"Bullish": "🟢", "Bearish": "🔴"}
    return "<b>Sesgo</b>\n" + "\n".join(
        f"{icon.get(b['bias'], '⚪')} <b>{_e(b['symbol'])}</b> "
        f"{_bias_text(b['bias'], b['score'], b['lateral'], b.get('efficiency'))}" for b in s["bias"])


def decisions(s: dict) -> str:
    if not s["decisions"]:
        return "<b>Decisiones de Cortex</b>\nNinguna desde que arrancó el bot."
    return "<b>Decisiones de Cortex</b>\n" + "\n".join(
        f"{'✓ GO' if d['go'] else '✕ NO GO'} {_e(d['side'])} {_e(d['symbol'])} {_e(d['timeframe'])} · {_e(d['pattern'])} · "
        f"{_e(d['at'])}\n<i>{_e(d['reason'])}</i>" for d in s["decisions"][:8])


def status(s: dict) -> str:
    return "\n\n".join([_header(s), today(s), open_positions(s), bias(s)])


def help_text(extra: tuple = ()) -> str:
    """La lista de comandos; `extra` son los de cada cuenta (/puprime, /metaquotes...), que dependen de los perfiles."""
    return "<b>Comandos</b>\n" + "\n".join(f"/{c} · {_e(d)}" for c, d in (*COMMANDS, *extra))


def answer(command: str, s: dict) -> str | None:
    """La respuesta al comando (sin la barra ni el @bot), o None si no es uno de los nuestros."""
    table = {"estado": status, "abiertas": open_positions, "hoy": today, "sesgo": bias, "decisiones": decisions}
    if command in table:
        return table[command](s)
    if command in ("ayuda", "start", "help"):
        return help_text()
    return None
