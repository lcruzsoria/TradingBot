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


def _where(order) -> str:
    zone = f" · {_e(order.tbr_zone)} {_day(order.tbr_day)}" if order.tbr_zone else ""
    return f"{_e(order.pattern)}{zone}"


def _levels(order) -> str:
    parts = [f"Entrada {fmt_price(order.price)}"]
    if order.stop is not None:
        parts.append(f"Stop {fmt_price(order.stop)}")
    if order.target is not None:
        parts.append(f"Obj. {fmt_price(order.target)}")
    return " · ".join(parts)


def _footer(profile: str | None) -> str:
    return f"\n<i>perfil {_e(profile)}</i>" if profile else ""


def opened(order, profile: str | None = None) -> str:
    return (f"🟡 <b>Abre {SIDE.get(order.direction, order.direction)} {_e(order.symbol)}</b> {_e(order.timeframe)}\n"
            f"{_where(order)}\n{_levels(order)}\n"
            f"Sesgo {_e(order.bias)} {order.score:+g}{_footer(profile)}")


def closed(order, result, profile: str | None = None) -> str:
    icon, short = RESULT.get(result.result, ("•", result.result))
    peak = f" · máx. {result.max_r:+.2f} R" if result.max_r is not None else ""
    return (f"{icon} <b>{short} {result.r:+.2f} R · {SIDE.get(order.direction, order.direction)} {_e(order.symbol)}</b>"
            f" {_e(order.timeframe)}\n{_where(order)}\n"
            f"Entrada {fmt_price(order.price)} → salida {fmt_price(result.exit_price)}{peak}{_footer(profile)}")


def decision(payload: dict, profile: str | None = None) -> str:
    hit, tbr, dec = payload["hit"], payload.get("tbr"), payload["decision"]
    zone = f" · {_e(tbr.zone)}" if tbr is not None and getattr(tbr, "zone", "") else ""
    head = "✓ GO" if dec.allowed else "✕ NO GO"
    return (f"<b>{head} {SIDE.get(hit.direction, hit.direction)} {_e(payload['symbol'])}</b> {_e(payload['timeframe'])}\n"
            f"{_e(hit.title)}{zone}\n{_e(dec.reason)}{_footer(profile)}")


def started(profile: str | None = None) -> str:
    return f"🤖 <b>TradingBot en marcha</b>{_footer(profile)}"
