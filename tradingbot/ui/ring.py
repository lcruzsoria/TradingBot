"""Panel de hexágonos: cada hexágono es una skill; las líneas son los mensajes entre ellas."""
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


def hexagon(cx: float, cy: float, s: float) -> QPolygonF:
    """Hexágono con el lado plano arriba (vértices a 0, 60, 120... grados)."""
    return QPolygonF([QPointF(cx + s * math.cos(math.radians(a)), cy + s * math.sin(math.radians(a)))
                      for a in range(0, 360, 60)])


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
        self._timer = QTimer(self)
        self._timer.setInterval(33)
        self._timer.timeout.connect(self.update)

    # -- datos ---------------------------------------------------------------------------------
    def set_skills(self, infos: list[SkillInfo]) -> None:
        self.infos = {i.key: i for i in infos}
        self.views = {i.key: _View() for i in infos}
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

    def _ensure_timer(self) -> None:
        if not self._timer.isActive():
            self._timer.start()

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
        slot, _ = self._hit(event.position())
        self.setCursor(Qt.CursorShape.PointingHandCursor if slot is not None else Qt.CursorShape.ArrowCursor)

    # -- dibujo --------------------------------------------------------------------------------
    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        now = time.monotonic()
        s, pos = self._geometry()
        cx, cy, _ = pos["center"]
        occupied = {info.slot: key for key, info in self.infos.items()}

        # anillos de fondo
        ring_pen = QPen(QColor(theme.RING_DOT)); ring_pen.setStyle(Qt.PenStyle.DotLine); ring_pen.setWidthF(1.0)
        p.setPen(ring_pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        for r in (1.95 * s, 2.55 * s):
            p.drawEllipse(QPointF(cx, cy), r, r)

        # conexiones en reposo: radios hacia el centro y entre vecinos del anillo
        edge_pen = QPen(QColor(theme.EDGE)); edge_pen.setWidthF(1.2)
        p.setPen(edge_pen)
        for slot in RING_SLOTS:
            if slot in occupied and "center" in occupied:
                p.drawLine(QPointF(cx, cy), QPointF(*pos[slot][:2]))
            nxt = (slot + 1) % 6
            if slot in occupied and nxt in occupied:
                p.drawLine(QPointF(*pos[slot][:2]), QPointF(*pos[nxt][:2]))

        # mensajes en vuelo
        self._flows = [f for f in self._flows if now - f.t0 < FLOW_SECONDS]
        for f in self._flows:
            t = (now - f.t0) / FLOW_SECONDS
            a, b = (self._center_of(f.src, pos) if f.src in self.infos else None), self._center_of(f.dst, pos)
            fade = max(0.0, 1.0 - t)
            if a is not None:
                pen = QPen(QColor(theme.ACCENT)); pen.setWidthF(2.2)
                c = pen.color(); c.setAlphaF(0.25 + 0.6 * fade); pen.setColor(c)
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

        # el temporizador solo corre mientras haya animación
        if not self._flows and not any(v.state == "working" for v in self.views.values()):
            self._timer.stop()

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
        view = self.views[key]
        fill, border = theme.hex_style(view.state)
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
            glow = QColor(theme.ACCENT); glow.setAlphaF(0.55 * pulse)
            gp = QPen(glow); gp.setWidthF(5.0)
            p.setPen(gp); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPolygon(hexagon(cx, cy, size * 0.94))
        bp = QPen(QColor(border)); bp.setWidthF(2.0 if view.state != "idle" else 1.4)
        p.setPen(bp)
        p.setBrush(QColor(fill))
        p.drawPolygon(poly)

        # texto: nombre y, debajo, la descripción corta del estado
        title_font = QFont(self.font()); title_font.setBold(True)
        title_font.setPointSizeF(10.5 if size > 40 else 8.5)
        p.setFont(title_font)
        p.setPen(QColor(theme.TEXT))
        title = self.infos[key].title
        p.drawText(QRectF(cx - size, cy - size * 0.42, 2 * size, size * 0.5), Qt.AlignmentFlag.AlignCenter, title)
        sub_font = QFont(self.font()); sub_font.setPointSizeF(7.8 if size > 40 else 6.5)
        p.setFont(sub_font)
        p.setPen(QColor(theme.BEAR if view.state == "error" else theme.MUTED))
        text = "error" if view.state == "error" else (view.caption or (f"x {view.handled}" if view.handled else ""))
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
                  "Créala en <i>tradingbot/skills/</i> y actívala en <i>config.toml</i> con este slot: <b>%s</b>.</span>")
