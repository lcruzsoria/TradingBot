"""La imagen del panel: una tarjeta PNG pensada para el móvil con lo mismo que el panel web (resultado de hoy, abiertas, cierres y
sesgo). Se dibuja con Qt sobre una imagen en memoria, sin ventana: funciona con la app minimizada."""
from __future__ import annotations

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QGuiApplication, QImage, QPainter, QPen

from ..bias.rules import fmt_price

WIDTH = 820
PAD = 28
BG, PANEL, LINE = "#0B0E14", "#121722", "#222A3A"
TEXT, MUTED, ACCENT = "#D6DBE6", "#8B93A7", "#4A90E2"
GREEN, RED, GRAY, YELLOW = "#2ECC71", "#EF5350", "#9E9E9E", "#F2C94C"
RESULT_COLOR = {"TP": GREEN, "SL": RED, "BE": GRAY, "T": MUTED}
BIAS_COLOR = {"Bullish": GREEN, "Bearish": RED}
MAX_CLOSED = 8
MAX_OPERATIONS = 14                                          # cierres de la tarjeta del forwardtest de una cuenta


def _r(value) -> str:
    return "–" if value is None else f"{value:+.2f} R"


def _tone(value) -> str:
    return GREEN if value and value > 0 else RED if value and value < 0 else TEXT


class _Canvas:
    """Un lienzo muy alto sobre el que se va dibujando de arriba abajo; al final se recorta a lo usado."""

    def __init__(self) -> None:
        self.image = QImage(WIDTH, 3000, QImage.Format.Format_ARGB32)
        self.image.fill(QColor(BG))
        self.p = QPainter(self.image)
        self.p.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.y = PAD

    def font(self, size: float, bold: bool = False) -> QFont:
        f = QFont("Segoe UI", 1)
        f.setPixelSize(int(size))
        f.setBold(bold)
        return f

    def text(self, x: float, y: float, text: str, color: str, size: float = 17, bold: bool = False, right: bool = False,
             width: float | None = None) -> float:
        """Escribe `text` con su base en `y`; con `right`, alineado a la derecha en `x`. Devuelve lo que ocupa de ancho."""
        font = self.font(size, bold)
        fm = QFontMetrics(font)
        if width is not None:
            text = fm.elidedText(text, Qt.TextElideMode.ElideRight, int(width))
        w = fm.horizontalAdvance(text)
        self.p.setFont(font)
        self.p.setPen(QColor(color))
        self.p.drawText(int(x - w if right else x), int(y), text)
        return w

    def box(self, x: float, y: float, w: float, h: float, fill: str = PANEL, border: str = LINE, radius: float = 12,
            stripe: str | None = None) -> None:
        self.p.setBrush(QColor(fill))
        self.p.setPen(QPen(QColor(border), 1.2))
        self.p.drawRoundedRect(QRectF(x, y, w, h), radius, radius)
        if stripe:
            self.p.setPen(Qt.PenStyle.NoPen)
            self.p.setBrush(QColor(stripe))
            self.p.drawRoundedRect(QRectF(x, y + 8, 5, h - 16), 2.5, 2.5)

    def label(self, text: str) -> None:
        self.y += 18
        self.text(PAD, self.y + 12, text.upper(), MUTED, 14, True)
        self.y += 28

    def chip(self, x_right: float, y_mid: float, text: str, color: str) -> None:
        font = self.font(15, True)
        w = QFontMetrics(font).horizontalAdvance(text) + 18
        rect = QRectF(x_right - w, y_mid - 13, w, 26)
        self.p.setBrush(Qt.BrushStyle.NoBrush)
        self.p.setPen(QPen(QColor(color), 1.5))
        self.p.drawRoundedRect(rect, 7, 7)
        self.text(x_right - w / 2 - QFontMetrics(font).horizontalAdvance(text) / 2, y_mid + 5.5, text, color, 15, True)

    def png(self) -> bytes:
        self.p.end()
        cropped = self.image.copy(0, 0, WIDTH, min(int(self.y + PAD), self.image.height()))
        data = QByteArray()
        buffer = QBuffer(data)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        cropped.save(buffer, "PNG")
        return bytes(data)


def _need_qt() -> None:
    if QGuiApplication.instance() is None:                  # Qt cierra el proceso si se dibuja texto sin aplicación
        raise RuntimeError("la imagen del panel necesita la aplicación de Qt en marcha")


def _header(c: _Canvas, s: dict, title: str = "TradingBot") -> None:
    w = c.text(PAD, c.y + 24, title, TEXT, 28, True)
    if s.get("profile"):
        c.text(PAD + w + 12, c.y + 24, f"· {s['profile']}", MUTED, 19)
    c.text(WIDTH - PAD, c.y + 24, s["updated"], MUTED, 16, right=True)
    c.y += 46


def _figures(c: _Canvas, s: dict, inner: float) -> None:
    """Tres cifras: resultado de hoy, abiertas y saldo."""
    t = s["today"]
    virtual, broker = s.get("virtual"), s.get("broker")
    if virtual:
        third = ("Saldo virtual", f"{virtual['balance']:,.0f} {virtual['currency']}")
    elif broker:
        third = ("Equity", f"{broker['equity']:,.0f} {broker['currency']}")
    else:
        third = ("Saldo", "–")
    gap = 12
    bw = (inner - 2 * gap) / 3
    for i, (name, value, color) in enumerate((("Hoy", _r(t["r"]), _tone(t["r"])), ("Abiertas", str(len(s["open"])), TEXT),
                                              (third[0], third[1], TEXT))):
        x = PAD + i * (bw + gap)
        c.box(x, c.y, bw, 82, radius=14)
        c.text(x + 16, c.y + 30, name, MUTED, 15)
        c.text(x + 16, c.y + 64, value, color, 26, True, width=bw - 32)
    c.y += 82


def _open(c: _Canvas, s: dict, inner: float) -> None:
    c.label("Abiertas")
    if not s["open"]:
        c.text(PAD, c.y + 18, "Ninguna operación abierta.", MUTED, 17)
        c.y += 34
    for o in s["open"]:
        h = 130
        c.box(PAD, c.y, inner, h, stripe=YELLOW)
        c.text(PAD + 22, c.y + 34, f"{o['side']} {o['symbol']}", TEXT, 21, True)
        c.text(WIDTH - PAD - 18, c.y + 34, _r(o["r_now"]), _tone(o["r_now"]), 21, True, right=True)
        meta = f"{o['pattern']}" + (f" · {o['zone']}" if o["zone"] else "") + f" · {o['timeframe']}"
        c.text(PAD + 22, c.y + 60, meta, MUTED, 15, width=inner - 44)
        col = (inner - 44) / 3
        for i, (name, value, color) in enumerate((("Entrada", o["entry"], MUTED), ("Stop", o["stop"], RED),
                                                  ("Objetivo", o["target"], GREEN))):
            x = PAD + 22 + i * col
            c.text(x, c.y + 86, name, color, 14)
            c.text(x, c.y + 112, fmt_price(value) if value is not None else "–", TEXT, 19, True)
        if o.get("price") is not None:
            c.text(WIDTH - PAD - 18, c.y + 112, f"ahora {fmt_price(o['price'])}", MUTED, 15, right=True)
        c.y += h + 10


def _today(c: _Canvas, s: dict) -> None:
    t = s["today"]
    c.label("Hoy")
    if t["count"]:
        x = PAD
        x += c.text(x, c.y + 18, f"{t['count']} cerrada(s):  ", MUTED, 17)
        for short, n in (("TP", t["TP"]), ("SL", t["SL"]), ("BE", t["BE"]), ("T", t["T"])):
            if n or short != "T":
                x += c.text(x, c.y + 18, f"{n} {short}   ", RESULT_COLOR[short], 17, True)
        c.text(WIDTH - PAD, c.y + 18, _r(t["r"]), _tone(t["r"]), 19, True, right=True)
    else:
        c.text(PAD, c.y + 18, "Aún no ha cerrado ninguna.", MUTED, 17)
    c.y += 34


def _closed(c: _Canvas, s: dict, inner: float, limit: int) -> None:
    c.label("Últimos cierres")
    rows = s["closed"][:limit]
    if not rows:
        c.text(PAD, c.y + 18, "Sin cierres este mes.", MUTED, 17)
        c.y += 34
        return
    row_h = 62
    c.box(PAD, c.y, inner, row_h * len(rows) + 8)
    for i, r in enumerate(rows):
        y = c.y + 4 + i * row_h
        if i:
            c.p.setPen(QPen(QColor(LINE), 1))
            c.p.drawLine(PAD + 16, int(y), WIDTH - PAD - 16, int(y))
        c.text(PAD + 20, y + 26, f"{r['side']} {r['symbol']}", TEXT, 18, True, width=inner - 200)
        day = f"{r['day'][8:10]}/{r['day'][5:7]}" if len(r["day"]) == 10 else r["day"]
        detail = f"{r['pattern']}" + (f" · {r['zone']}" if r["zone"] else "") + f" · {day}"
        if r.get("max_r") is not None:
            detail += f" · máx. {_r(r['max_r'])}"
        c.text(PAD + 20, y + 48, detail, MUTED, 14, width=inner - 200)
        c.chip(WIDTH - PAD - 18, y + 22, r["result"], RESULT_COLOR.get(r["result"], MUTED))
        c.text(WIDTH - PAD - 18, y + 52, _r(r["r"]), _tone(r["r"]), 15, right=True)
    c.y += row_h * len(rows) + 8


def _bias(c: _Canvas, s: dict) -> None:
    c.label("Sesgo")
    if not s["bias"]:
        c.text(PAD, c.y + 18, "Esperando al sesgo…", MUTED, 17)
        c.y += 34
        return
    x, row_y = PAD, c.y
    for b in s["bias"]:
        name = b["symbol"]
        state = b["bias"] + (" · lateral" if b["lateral"] else "")
        score = f"{b['score']:+g}"
        fm = QFontMetrics(c.font(16, True))
        fs = QFontMetrics(c.font(16))
        width = fm.horizontalAdvance(name) + fs.horizontalAdvance(f"  {state}  {score}") + 28
        if x + width > WIDTH - PAD:
            x, row_y = PAD, row_y + 46
        c.box(x, row_y, width, 36, radius=9)
        tx = x + 14
        tx += c.text(tx, row_y + 25, name, TEXT, 16, True)
        tx += c.text(tx, row_y + 25, f"  {state}", BIAS_COLOR.get(b["bias"], MUTED), 16)
        c.text(tx, row_y + 25, f"  {score}", MUTED, 16)
        x += width + 8
    c.y = row_y + 44


def render(s: dict) -> bytes:
    """El PNG del panel a partir de la foto que da `PanelState.snapshot()`."""
    _need_qt()
    c = _Canvas()
    inner = WIDTH - 2 * PAD
    _header(c, s)
    _figures(c, s, inner)
    _open(c, s, inner)
    _today(c, s)
    _closed(c, s, inner, MAX_CLOSED)
    _bias(c, s)
    return c.png()


def render_operations(s: dict) -> bytes:
    """El PNG del forwardtest de una cuenta: solo las operaciones (abiertas, resultado de hoy y últimos cierres), sin cifras
    de saldo ni sesgo. Es lo que manda el comando de cada perfil (/puprime, /metaquotes...)."""
    _need_qt()
    c = _Canvas()
    inner = WIDTH - 2 * PAD
    _header(c, s, "Forwardtest")
    _open(c, s, inner)
    _today(c, s)
    _closed(c, s, inner, MAX_OPERATIONS)
    return c.png()
