"""El dibujo de un setup ejecutado (comando /dibujar de Telegram): velas, caja de la TBR con el color de su zona, fibo (1, 0,5, 0 y
-0,2) y la posición con su SL y su TP. Se dibuja con Qt sobre una imagen en memoria, como la tarjeta del panel.

Criterio de colores:
- la TBR, del color de su zona (los de la skill TBR: Asia, London, NY Open);
- el tramo del SL (de la entrada al stop), rosa;
- el tramo del TP (de la entrada al objetivo), verde si el trade acabó en TP (o sigue abierto) y gris claro si no llegó
  (SL, breakeven o tiempo);
- velas alcistas verdes y bajistas grises, para que el rojo y el verde del trade no se confundan con ellas.
"""
from __future__ import annotations

import numpy as np
from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QGuiApplication, QImage, QPainter, QPen

from ...clock import ny_from_server
from ..bias.rules import fmt_price
from ..tbr.zones import KNOWN_ZONES, Zone

WIDTH, HEIGHT = 1200, 760
LEFT, RIGHT, TOP, BOTTOM = 40, 230, 96, 40
BARS_BEFORE = 3                                              # velas antes de la TBR
BARS_AFTER = 6                                               # velas después de la salida
UP, DOWN = "#26A69A", "#5C6370"
SL_PINK, TP_GREEN, TP_GRAY = "#D81B60", "#2E7D32", "#9E9E9E"
ONE, ZERO, HALF, TARGET = "#6A1B9A", "#6A1B9A", "#2E7D32", "#1565C0"
SIDE = {"long": "largo", "short": "corto"}
RESULT = {"objetivo": "TP", "stop": "SL", "breakeven": "BE", "tiempo": "T"}
FALLBACK_COLOR = "#9E9E9E"


def zone_of(name: str, zones: list[Zone] | None = None) -> Zone | None:
    """La zona por su nombre («London»): de las del bot si se dan y, si no, de las conocidas."""
    for z in zones or []:
        if z.name == name:
            return z
    for key, zname, hours, color in KNOWN_ZONES:
        if zname == name:
            start, end = (int(p[:2]) * 60 + int(p[3:]) for p in hours.split("-"))
            return Zone(key, zname, start, end, color)
    return None


def _need_qt() -> None:
    if QGuiApplication.instance() is None:
        raise RuntimeError("el dibujo del setup necesita la aplicación de Qt en marcha")


def tbr_bars(ts: np.ndarray, zone: Zone, offset: int | None, before: int) -> tuple[int, int] | None:
    """(primera, última) vela de la TBR más reciente de la zona que termina antes de la vela `before`."""
    inside = np.zeros(len(ts), dtype=bool)
    for i in range(min(before, len(ts))):
        ny, _ = ny_from_server(int(ts[i]), offset)
        minute = ny.hour * 60 + ny.minute
        inside[i] = (zone.start <= minute < zone.end) if zone.start < zone.end else (minute >= zone.start or minute < zone.end)
    idx = np.flatnonzero(inside)
    if not len(idx):
        return None
    last = int(idx[-1])
    first = last
    while first > 0 and inside[first - 1] and ts[first] - ts[first - 1] <= 3600:       # velas seguidas de la franja
        first -= 1
    return first, last


def _same(a: float, b: float) -> bool:
    return abs(a - b) <= 1e-6 * max(abs(b), 1e-9)


def _swing(df, first: int, entry: int, stop: float, zero: float, long: bool) -> tuple[int | None, int | None]:
    """Las velas del 1 (el extremo que fija el stop) y del 0 (el del lado contrario, después), si se reconocen."""
    hi, lo = df["high"].to_numpy(), df["low"].to_numpy()
    one = zero_i = None
    for i in range(first, entry):
        if _same(lo[i] if long else hi[i], stop):
            one = i
    if one is not None:
        for i in range(one, entry):
            if _same(hi[i] if long else lo[i], zero):
                zero_i = i
                break
    return one, zero_i


def render(order: dict, closed: dict | None, df, offset: int | None, zones: list[Zone] | None = None) -> bytes:
    """El PNG de un setup. `order` y `closed` son los del diario del forwardtest (cierre en `closed`; None si sigue abierto)."""
    _need_qt()
    ts = df["ts"].to_numpy()
    o, h, l, c = (df[k].to_numpy() for k in ("open", "high", "low", "close"))
    long = order["direction"] == "long"
    entry_px, stop, target = float(order["price"]), float(order["stop"]), float(order["target"])
    zero = 2 * entry_px - stop                                # el fibo: 1 = stop, 0,5 = entrada, 0, -0,2 = objetivo
    zone = zone_of(order.get("tbr_zone", ""), zones)
    color = zone.color if zone else FALLBACK_COLOR
    entry_i = int(np.searchsorted(ts, int(order["entry_ts"])))
    entry_i = min(entry_i, len(ts) - 1)
    result = closed["result"] if closed else None
    exit_i = min(int(np.searchsorted(ts, int(closed["exit_ts"]))), len(ts) - 1) if closed and closed.get("exit_ts") else len(ts) - 1
    exit_i = max(exit_i, entry_i)
    box = tbr_bars(ts, zone, offset, entry_i) if zone else None
    first = max((box[0] if box else entry_i - 12) - BARS_BEFORE, 0)
    last = min(max(exit_i + BARS_AFTER, entry_i + 8), len(ts) - 1)
    n = last - first + 1
    tbr_hi, tbr_lo = float(order["tbr_high"]), float(order["tbr_low"])
    top = max(float(h[first:last + 1].max()), stop, target, tbr_hi)
    bot = min(float(l[first:last + 1].min()), stop, target, tbr_lo)
    pad = (top - bot) * 0.06
    top, bot = top + pad, bot - pad

    image = QImage(WIDTH, HEIGHT, QImage.Format.Format_RGB32)
    image.fill(QColor("#FFFFFF"))
    p = QPainter(image)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    def X(i):
        return LEFT + (i - first + 0.5) * (WIDTH - LEFT - RIGHT) / (n + 1)

    def Y(price):
        return TOP + (top - price) * (HEIGHT - TOP - BOTTOM) / (top - bot)

    cw = (WIDTH - LEFT - RIGHT) / (n + 1) * 0.7

    def font(size, bold=False):
        f = QFont("Segoe UI", 1)
        f.setPixelSize(size)
        f.setBold(bold)
        return f

    def text(x, y, s, col, size=13, bold=False):
        p.setFont(font(size, bold))
        p.setPen(QColor(col))
        p.drawText(int(x), int(y), s)

    def fill(x0, x1, p0, p1, col, alpha):
        q = QColor(col)
        q.setAlpha(alpha)
        p.fillRect(QRectF(x0, min(Y(p0), Y(p1)), x1 - x0, abs(Y(p0) - Y(p1))), q)

    # TBR: caja del color de su zona, de la primera a la última vela de la franja
    if box:
        fill(X(box[0]) - cw / 2, X(box[1]) + cw / 2, tbr_hi, tbr_lo, color, 45)
        for price, name in ((tbr_hi, "High"), (tbr_lo, "Low")):
            p.setPen(QPen(QColor(color), 1.5))
            p.drawLine(int(X(box[0]) - cw / 2), int(Y(price)), int(WIDTH - RIGHT), int(Y(price)))
        dark = QColor(color).darker(130).name()
        text(X(box[0]), Y(tbr_hi) - 6, f"High de la TBR {order.get('tbr_zone', '')}: {fmt_price(tbr_hi)}", dark, 13, True)
        text(X(box[0]), Y(tbr_lo) + 16, f"Low de la TBR {order.get('tbr_zone', '')}: {fmt_price(tbr_lo)}", dark, 13, True)

    # posición: SL rosa siempre; TP verde solo si el trade fue (o va) a TP, gris claro si no
    x0, x1 = X(entry_i) - cw / 2, X(exit_i) + cw / 2
    reached = result in (None, "objetivo")
    fill(x0, x1, entry_px, stop, SL_PINK, 50)
    fill(x0, x1, entry_px, target, TP_GREEN if reached else TP_GRAY, 55 if reached else 70)

    for i in range(first, last + 1):
        col = QColor(UP if c[i] >= o[i] else DOWN)
        p.setPen(QPen(col, 1.2))
        p.drawLine(int(X(i)), int(Y(h[i])), int(X(i)), int(Y(l[i])))
        y1, y2 = Y(max(o[i], c[i])), Y(min(o[i], c[i]))
        p.fillRect(QRectF(X(i) - cw / 2, y1, cw, max(y2 - y1, 1.5)), col)
        if (i - first) % 4 == 0:
            ny, _ = ny_from_server(int(ts[i]), offset)
            text(X(i) - 18, HEIGHT - 16, ny.strftime("%H:%M"), "#666666", 12)

    def dot(i, price, col):
        p.setPen(QPen(QColor(col), 1.5))
        p.setBrush(QColor(col))
        p.drawEllipse(int(X(i)) - 5, int(Y(price)) - 5, 10, 10)
        p.setBrush(Qt.BrushStyle.NoBrush)

    one_i, zero_i = _swing(df, box[1] + 1 if box else first, entry_i, stop, zero, long)
    if one_i is not None:
        dot(one_i, stop, ONE)
        text(X(one_i) - 4, Y(stop) + (-12 if not long else 24), "1", ONE, 14, True)
    if zero_i is not None:
        dot(zero_i, zero, ZERO)
        text(X(zero_i) - 4, Y(zero) + (24 if not long else -12), "0", ZERO, 14, True)
    dot(entry_i, entry_px, HALF)

    # niveles del fibo, a la derecha
    for name, price, col in (("1 · stop", stop, ONE), ("0,5 · entrada", entry_px, HALF), ("0", zero, ZERO),
                             ("-0,2 · objetivo", target, TARGET)):
        p.setPen(QPen(QColor(col), 1.2, Qt.PenStyle.DashLine))
        p.drawLine(int(X(one_i if one_i is not None else entry_i) - cw), int(Y(price)), int(WIDTH - RIGHT), int(Y(price)))
        text(WIDTH - RIGHT + 8, Y(price) + 4, f"{name}  {fmt_price(price)}", col, 13, True)

    # cajas SL / TP rotuladas y la salida
    risk = abs(entry_px - stop)
    rr = abs(target - entry_px) / risk if risk else 0
    text(x0 + 6, Y(stop) + (14 if not long else -6), f"SL  {fmt_price(stop)}  (1R)", "#AD1457", 13, True)
    text(x0 + 6, Y(target) + (-6 if not long else 16), f"TP  {fmt_price(target)}  (RR {rr:.1f})".replace(".", ","),
         "#1B5E20" if reached else "#757575", 13, True)
    ny_entry_hm = ny_from_server(int(ts[entry_i]), offset)[0].strftime("%H:%M")
    if closed:
        short = RESULT.get(result, str(result))
        ny_exit, _ = ny_from_server(int(ts[exit_i]), offset)
        col = {"TP": "#2E7D32", "SL": "#B71C1C"}.get(short, "#616161")
        level = stop if short == "SL" else target if short == "TP" else entry_px
        text(X(exit_i) - 60, Y(level) + (-10 if (short == "SL") != long else 22),
             f"{short} ({ny_exit.strftime('%H:%M')} NY): {float(closed['r']):+.2f} R".replace(".", ","), col, 14, True)

    # cabecera
    day = order.get("tbr_day")
    day = f"{str(day)[8:10]}/{str(day)[5:7]}" if day and len(str(day)) >= 10 else ""
    text(LEFT, 30, f"{order['symbol']}, TBR de {order.get('tbr_zone', '')}, {day}: {order['pattern']} {SIDE.get(order['direction'], '')}"
         + (f" · {order['caso']}" if order.get("caso") else ""), "#111111", 21, True)
    if closed:
        peak = f" · máx. {float(closed['max_r']):+.2f} R".replace(".", ",") if closed.get("max_r") is not None else ""
        sub = f"Resultado {RESULT.get(result, result)} {float(closed['r']):+.2f} R{peak}".replace(".", ",")
    else:
        sub = "Operación abierta"
    text(LEFT, 54, sub, "#444444", 14)
    text(LEFT, 74, f"Entrada {SIDE.get(order['direction'], '')} {ny_entry_hm} NY · sesgo {order.get('bias', '')} · entrada {fmt_price(entry_px)} · stop {fmt_price(stop)} · objetivo {fmt_price(target)}",
         "#666666", 13)
    p.end()
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(data)
