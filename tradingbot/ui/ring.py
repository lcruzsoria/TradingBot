"""Panel de hexágonos: cada hexágono es una skill; las líneas son los mensajes entre ellas.

En reposo el anillo se mueve muy poco: los anillos de fondo giran despacio y un punto de luz recorre cada radio.
Los avisos de trading son discretos: al entrar en un trade (`trade_opened`) Cortex se ilumina una vez en verde
(largo) o rojo (corto) y muestra «▲ Long US100»; al cerrar (`trade_closed`) Setup hace lo mismo con el resultado
en R (verde si gana, rojo si pierde, gris si cierra por tiempo).
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QWidget

from ..core import SkillInfo
from ..core.skill import AUX_SLOTS, RING_SLOTS
from . import theme

FLOW_SECONDS = 0.8
GLOW_SECONDS = 1.2           # el brillo de una entrada o un cierre se apaga en este tiempo
LABEL_SECONDS = 4.0          # el texto («▲ Long US100», «+1.80 R») se queda este tiempo y luego se desvanece


@dataclass
class _View:
    state: str = "idle"
    handled: int = 0
    caption: str = ""
    note: str = ""


@dataclass
class _Flow:
    src: str
    dst: str
    topic: str
    t0: float


@dataclass
class _Highlight:
    color: str
    text: str
    t0: float


def hexagon(cx: float, cy: float, s: float) -> QPolygonF:
    """Hexágono con el lado plano arriba (vértices a 0, 60, 120... grados)."""
    return QPolygonF([QPointF(cx + s * math.cos(math.radians(a)), cy + s * math.sin(math.radians(a)))
                      for a in range(0, 360, 60)])


def _alpha(color: str, a: float) -> QColor:
    c = QColor(color)
    c.setAlphaF(max(0.0, min(1.0, a)))
    return c


def _glow(age: float) -> float:
    """Subida rápida (0,12 s) y bajada suave hasta GLOW_SECONDS: 0..1."""
    if age < 0 or age > GLOW_SECONDS:
        return 0.0
    if age < 0.12:
        return age / 0.12
    return (1 - (age - 0.12) / (GLOW_SECONDS - 0.12)) ** 2


def _label(age: float) -> float:
    """Opacidad del texto: entero hasta el último medio segundo de LABEL_SECONDS."""
    return max(0.0, min(1.0, (LABEL_SECONDS - age) / 0.5))


class RingView(QWidget):
    skill_clicked = Signal(str)          # clave de la skill
    free_slot_clicked = Signal(object)   # slot libre (0-5 o "aux1"...)

    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(330, 330)
        self.setMouseTracking(True)
        self.infos: dict[str, SkillInfo] = {}
        self.views: dict[str, _View] = {}
        self.last_in: dict[str, str] = {}
        self.last_out: dict[str, str] = {}
        self.selected: str | None = None
        self._flows: list[_Flow] = []
        self.highlights: dict[str, _Highlight] = {}   # clave de la skill -> aviso de entrada o cierre
        self._hover: str | None = None
        self._timer = QTimer(self)
        self._timer.setInterval(33)
        self._timer.timeout.connect(self.update)

    # -- datos ---------------------------------------------------------------------------------
    def set_skills(self, infos: list[SkillInfo]) -> None:
        self.infos = {i.key: i for i in infos}
        self.views = {i.key: _View() for i in infos}
        self._ensure_timer()
        self.update()

    def update_state(self, payload: dict) -> None:
        view = self.views.get(payload["key"])
        if view:
            view.state, view.handled = payload["state"], payload["handled"]
            view.caption, view.note = payload["caption"], payload["note"]
            self._ensure_timer()
            self.update()

    def flash(self, src: str, targets: list[str], topic: str) -> None:
        now = time.monotonic()
        if src in self.infos:
            self.last_out[src] = topic
        for dst in targets:
            if dst in self.infos:
                self.last_in[dst] = topic
                self._flows.append(_Flow(src, dst, topic, now))
        self._ensure_timer()

    def trade_opened(self, direction: str, symbol: str = "") -> None:
        """Entrada en un trade: Cortex brilla una vez (verde largo, rojo corto) y muestra la dirección."""
        long = str(direction).lower() == "long"
        text = f"{'▲ Long' if long else '▼ Short'} {symbol}".strip()
        self._highlight(self._key_at("center"), theme.BULL if long else theme.BEAR, text)

    def trade_closed(self, result: str, r: float, symbol: str = "") -> None:
        """Cierre de una posición: Setup brilla con el color del resultado y muestra los R."""
        color = {"objetivo": theme.BULL, "stop": theme.BEAR}.get(result, theme.MUTED)
        key = "setup" if "setup" in self.infos else self._key_at("center")
        self._highlight(key, color, f"{r:+.2f} R")

    def _highlight(self, key: str | None, color: str, text: str) -> None:
        if key:
            self.highlights[key] = _Highlight(color, text, time.monotonic())
            self._ensure_timer()

    def _key_at(self, slot) -> str | None:
        return next((k for k, i in self.infos.items() if i.slot == slot), None)

    def _ensure_timer(self) -> None:
        if not self._timer.isActive():
            self._timer.start()

    def showEvent(self, event) -> None:  # noqa: N802
        self._ensure_timer()
        super().showEvent(event)

    def hideEvent(self, event) -> None:  # noqa: N802
        self._timer.stop()                   # no gastar CPU con el panel oculto o la ventana minimizada
        super().hideEvent(event)

    # -- geometría -----------------------------------------------------------------------------
    def _geometry(self):
        """(tamaño del hexágono, {slot: (cx, cy, size)}) para el tamaño actual del widget."""
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        s = max(20.0, min(62.0, (min(w, h) / 2 - 8) / 2.82))
        d = 1.95 * s
        pos: dict = {"center": (cx, cy, s)}
        for k in RING_SLOTS:
            a = math.radians(-90 + 60 * k)
            pos[k] = (cx + d * math.cos(a), cy + d * math.sin(a), s)
        a_size = s * 0.5
        margin = a_size + 4
        pos["aux1"] = (margin, margin, a_size)
        pos["aux2"] = (w - margin, h - margin, a_size)
        pos["aux3"] = (margin, h - margin, a_size)
        return s, pos

    def _slot_of(self, key: str):
        return self.infos[key].slot

    def _center_of(self, key: str, pos: dict):
        cx, cy, _ = pos[self._slot_of(key)]
        return QPointF(cx, cy)

    def _hit(self, point: QPointF):
        _, pos = self._geometry()
        occupied = {info.slot: key for key, info in self.infos.items()}
        for slot, (cx, cy, size) in pos.items():
            if slot in AUX_SLOTS and slot not in occupied:
                continue
            if hexagon(cx, cy, size).containsPoint(point, Qt.FillRule.WindingFill):
                return slot, occupied.get(slot)
        return None, None

    # -- interacción ---------------------------------------------------------------------------
    def mousePressEvent(self, event) -> None:  # noqa: N802
        slot, key = self._hit(event.position())
        if slot is None:
            return
        if key:
            self.selected = key
            self.skill_clicked.emit(key)
        else:
            self.free_slot_clicked.emit(slot)
        self.update()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        slot, key = self._hit(event.position())
        self._hover = key
        self.setCursor(Qt.CursorShape.PointingHandCursor if slot is not None else Qt.CursorShape.ArrowCursor)

    def leaveEvent(self, event) -> None:  # noqa: N802
        self._hover = None
        super().leaveEvent(event)

    # -- dibujo --------------------------------------------------------------------------------
    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        now = time.monotonic()
        s, pos = self._geometry()
        cx, cy, _ = pos["center"]
        center = QPointF(cx, cy)
        occupied = {info.slot: key for key, info in self.infos.items()}
        self.highlights = {k: h for k, h in self.highlights.items() if now - h.t0 < LABEL_SECONDS}

        # anillos de fondo que giran despacio en sentidos opuestos
        for i, r in enumerate((1.95 * s, 2.55 * s)):
            pen = QPen(QColor(theme.RING_DOT)); pen.setWidthF(1.0)
            pen.setDashPattern([1.0, 5.0] if i == 0 else [6.0, 6.0])
            pen.setDashOffset(now * (1.5 if i == 0 else -0.9))
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(center, r, r)

        # conexiones en reposo, con un punto de luz que recorre cada radio hacia fuera
        edge_pen = QPen(QColor(theme.EDGE)); edge_pen.setWidthF(1.2)
        for slot in RING_SLOTS:
            end = QPointF(*pos[slot][:2])
            if slot in occupied and "center" in occupied:
                p.setPen(edge_pen)
                p.drawLine(center, end)
                t = (now * 0.4 + slot / 6) % 1.0
                dot = QPointF(cx + (end.x() - cx) * t, cy + (end.y() - cy) * t)
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(_alpha(theme.ACCENT, 0.45 * math.sin(math.pi * t)))
                p.drawEllipse(dot, 1.8, 1.8)
            nxt = (slot + 1) % 6
            if slot in occupied and nxt in occupied:
                p.setPen(edge_pen)
                p.drawLine(end, QPointF(*pos[nxt][:2]))

        # mensajes en vuelo
        self._flows = [f for f in self._flows if now - f.t0 < FLOW_SECONDS]
        for f in self._flows:
            if f.src not in self.infos:
                continue
            t = (now - f.t0) / FLOW_SECONDS
            a, b = self._center_of(f.src, pos), self._center_of(f.dst, pos)
            fade = max(0.0, 1.0 - t)
            pen = QPen(_alpha(theme.ACCENT, 0.25 + 0.6 * fade)); pen.setWidthF(2.2)
            p.setPen(pen)
            p.drawLine(a, b)
            dot = QPointF(a.x() + (b.x() - a.x()) * t, a.y() + (b.y() - a.y()) * t)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(theme.TEXT))
            p.drawEllipse(dot, 3.6, 3.6)

        # hexágonos (huecos libres del anillo primero, para quedar al fondo)
        for slot in RING_SLOTS:
            if slot not in occupied:
                self._draw_free(p, pos[slot])
        for slot, key in occupied.items():
            self._draw_skill(p, key, pos[slot], now)

    def _draw_free(self, p: QPainter, geo) -> None:
        cx, cy, size = geo
        pen = QPen(QColor(theme.FREE_LINE)); pen.setStyle(Qt.PenStyle.DashLine); pen.setWidthF(1.0)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPolygon(hexagon(cx, cy, size * 0.94))
        p.setPen(QColor(theme.FREE_TEXT))
        font = QFont(self.font()); font.setPointSizeF(8.5); p.setFont(font)
        p.drawText(QRectF(cx - size, cy - 9, 2 * size, 18), Qt.AlignmentFlag.AlignCenter, "Libre")

    def _draw_skill(self, p: QPainter, key: str, geo, now: float) -> None:
        cx, cy, size = geo
        if key == self._hover:
            size *= 1.03
        view = self.views[key]
        fill, border = theme.hex_style(view.state)
        hl = self.highlights.get(key)
        glow = _glow(now - hl.t0) if hl else 0.0
        poly = hexagon(cx, cy, size * 0.94)
        if key == self.selected:
            sel = QPen(QColor(theme.SELECT)); sel.setWidthF(1.4)
            p.setPen(sel); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPolygon(hexagon(cx, cy, size * 1.06))
        # halo cuando trabaja o acaba de recibir un mensaje
        pulse = 0.0
        if view.state == "working":
            pulse = 0.5 + 0.5 * math.sin(now * 9)
        for f in self._flows:
            if f.dst == key:
                pulse = max(pulse, 1.0 - (now - f.t0) / FLOW_SECONDS)
        if pulse > 0:
            gp = QPen(_alpha(theme.ACCENT, 0.55 * pulse)); gp.setWidthF(5.0)
            p.setPen(gp); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPolygon(poly)
        # brillo de una entrada o un cierre: dos capas suaves del color del aviso
        if glow > 0:
            for width, alpha in ((10.0, 0.18), (5.0, 0.5)):
                gp = QPen(_alpha(hl.color, alpha * glow)); gp.setWidthF(width)
                gp.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                p.setPen(gp); p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawPolygon(poly)
            fill = theme.mix(fill, hl.color, 0.28 * glow)
            border = theme.mix(border, hl.color, glow)
        bp = QPen(QColor(border)); bp.setWidthF(2.0 if view.state != "idle" or glow else 1.4)
        p.setPen(bp)
        p.setBrush(QColor(fill))
        p.drawPolygon(poly)

        # texto: nombre y, debajo, la descripción corta del estado (o el aviso de trading mientras dura)
        title_font = QFont(self.font()); title_font.setBold(True)
        title_font.setPointSizeF(10.5 if size > 40 else 8.5)
        p.setFont(title_font)
        p.setPen(QColor(theme.TEXT))
        title = self.infos[key].title
        p.drawText(QRectF(cx - size, cy - size * 0.42, 2 * size, size * 0.5), Qt.AlignmentFlag.AlignCenter, title)
        sub_font = QFont(self.font()); sub_font.setPointSizeF(7.8 if size > 40 else 6.5)
        if hl:
            sub_font.setBold(True)
            color, text = _alpha(hl.color, _label(now - hl.t0)), hl.text
        else:
            caption = view.caption
            tone = theme.BULL if caption.startswith("Bullish") else theme.BEAR if caption.startswith("Bearish") else theme.MUTED
            color = QColor(theme.BEAR if view.state == "error" else tone if key == "bias" else theme.MUTED)
            text = "error" if view.state == "error" else (view.caption or (f"x {view.handled}" if view.handled else ""))
        p.setFont(sub_font)
        p.setPen(color)
        text = QFontMetrics(sub_font).elidedText(text, Qt.TextElideMode.ElideRight, int(size * 1.45))
        p.drawText(QRectF(cx - size, cy + size * 0.06, 2 * size, size * 0.4), Qt.AlignmentFlag.AlignCenter, text)


def describe_skill(info: SkillInfo, view: _View, last_in: str | None, last_out: str | None) -> str:
    """Texto (HTML) del panel de detalle de una skill."""
    state = {"idle": "en espera", "ok": "activa", "working": "trabajando", "error": "con error"}.get(view.state, view.state)
    color = theme.BEAR if view.state == "error" else theme.BULL if view.state in ("ok", "working") else theme.MUTED
    listens = ", ".join(info.subscribes) or "nada"
    says = ", ".join(info.publishes) or "nada"
    rows = [
        f"<b>{info.title}</b> <span style='color:{color}'>({state})</span>",
        f"<span style='color:{theme.MUTED}'>{info.description}</span>",
        f"<span style='color:{theme.MUTED}'>Escucha:</span> {listens}",
        f"<span style='color:{theme.MUTED}'>Publica:</span> {says}",
        f"<span style='color:{theme.MUTED}'>Mensajes procesados:</span> {view.handled}",
    ]
    if last_in:
        rows.append(f"<span style='color:{theme.MUTED}'>Último recibido:</span> {last_in}")
    if last_out:
        rows.append(f"<span style='color:{theme.MUTED}'>Último enviado:</span> {last_out}")
    if view.note and view.state == "error":
        rows.append(f"<span style='color:{theme.BEAR}'>{view.note}</span>")
    return "<br>".join(rows)


FREE_SLOT_TEXT = ("<b>Slot libre</b><br><span style='color:%s'>Aquí puede vivir una skill nueva (Risk, Exit, Macro...). "
                  "Créala copiando la carpeta <i>tradingbot/skills/_plantilla/</i> y actívala en <i>config.toml</i> con este slot: <b>%s</b>.</span>")
