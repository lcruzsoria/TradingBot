"""Panel de hexágonos: cada hexágono es una skill; las líneas son los mensajes entre ellas.

El anillo está siempre vivo: los anillos de fondo giran, unas chispas orbitan, los hexágonos respiran y el de
Cortex lleva un borde de luz que da vueltas. Cuando el bot entra en un trade (`celebrate`) todo estalla: onda
expansiva, rayos desde Cortex a cada skill, confeti, los hexágonos rebotan en cadena y aparece el rótulo
LONG / SHORT con el mercado. Una posición ganada (`win`) lanza una lluvia dorada más corta.
"""
from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QFont, QFontMetrics, QPainter, QPainterPath, QPen,
                           QPolygonF, QRadialGradient)
from PySide6.QtWidgets import QWidget

from ..core import SkillInfo
from ..core.skill import AUX_SLOTS, RING_SLOTS
from . import theme

FLOW_SECONDS = 0.8
CELEBRATE_SECONDS = 2.8      # duración del efecto de entrada en un trade
WIN_SECONDS = 2.0            # duración de la lluvia por posición ganada
ORBITERS = 7                 # chispas que orbitan el anillo exterior en reposo


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
class _Particle:
    x: float                 # posición relativa al centro del anillo, en unidades de hexágono
    y: float
    vx: float
    vy: float
    t0: float
    life: float
    color: str
    size: float
    spin: float              # >0: confeti rectangular que gira; 0: chispa redonda con estela


@dataclass
class _Burst:
    kind: str                # "entry" o "win"
    t0: float
    color: str
    title: str
    subtitle: str


def hexagon(cx: float, cy: float, s: float) -> QPolygonF:
    """Hexágono con el lado plano arriba (vértices a 0, 60, 120... grados)."""
    return QPolygonF([QPointF(cx + s * math.cos(math.radians(a)), cy + s * math.sin(math.radians(a)))
                      for a in range(0, 360, 60)])


def _alpha(color: str, a: float) -> QColor:
    c = QColor(color)
    c.setAlphaF(max(0.0, min(1.0, a)))
    return c


def _ease_out_back(t: float) -> float:
    """0 -> 1 pasándose un poco y volviendo (el «pop» de los rótulos)."""
    t = max(0.0, min(1.0, t))
    c = 1.9
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def _bounce(t: float) -> float:
    """Rebote amortiguado: 0 en reposo, sube y oscila hasta apagarse."""
    if t <= 0:
        return 0.0
    return math.sin(t * 16) * math.exp(-t * 4.2)


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
        self._bursts: list[_Burst] = []
        self._particles: list[_Particle] = []
        self._hover: str | None = None
        self._spin = 0.0                 # ángulo acumulado de los anillos de fondo (acelera con un trade)
        self._last = time.monotonic()
        self._rng = random.Random()
        self._timer = QTimer(self)
        self._timer.setInterval(16)
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

    def celebrate(self, direction: str, symbol: str = "") -> None:
        """Efecto de entrada en un trade: verde si es largo, rojo si es corto."""
        now = time.monotonic()
        long = str(direction).lower() == "long"
        color = theme.BULL if long else theme.BEAR
        self._bursts.append(_Burst("entry", now, color, "LONG" if long else "SHORT", symbol))
        palette = [color, color, theme.ACCENT, theme.WARN, theme.TEXT, theme.mix(color, theme.TEXT, 0.5)]
        rng = self._rng
        for i in range(110):                                     # confeti en todas direcciones
            a = rng.uniform(0, math.tau)
            v = rng.uniform(1.6, 5.2)
            self._particles.append(_Particle(0.0, 0.0, v * math.cos(a), v * math.sin(a) - 1.2, now + rng.uniform(0, 0.12),
                                             rng.uniform(1.4, 2.6), rng.choice(palette), rng.uniform(0.07, 0.15),
                                             rng.uniform(4, 14) * rng.choice((-1, 1)) if i % 2 else 0.0))
        self._ensure_timer()

    def win(self, r: float = 0.0, symbol: str = "") -> None:
        """Lluvia dorada cuando una posición cierra en positivo."""
        now = time.monotonic()
        self._bursts.append(_Burst("win", now, theme.WARN, f"+{r:.2f} R" if r else "WIN", symbol))
        rng = self._rng
        for _ in range(60):
            self._particles.append(_Particle(rng.uniform(-3, 3), rng.uniform(-3.4, -2.6), rng.uniform(-0.4, 0.4),
                                             rng.uniform(0.2, 1.4), now + rng.uniform(0, 0.6), rng.uniform(1.4, 2.2),
                                             rng.choice((theme.WARN, theme.WARN, theme.TEXT, theme.BULL)),
                                             rng.uniform(0.08, 0.14), rng.uniform(5, 12) * rng.choice((-1, 1))))
        self._ensure_timer()

    def _ensure_timer(self) -> None:
        if not self._timer.isActive():
            self._last = time.monotonic()
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

    # -- estado de los efectos -----------------------------------------------------------------
    def _energy(self, now: float) -> float:
        """1 justo al entrar en un trade y baja hasta 0: acelera giros, brillos y respiración."""
        e = 0.0
        for b in self._bursts:
            span = CELEBRATE_SECONDS if b.kind == "entry" else WIN_SECONDS
            e = max(e, (1.0 - (now - b.t0) / span) * (1.0 if b.kind == "entry" else 0.5))
        return max(0.0, e)

    def _step(self, now: float) -> float:
        dt = min(0.05, max(0.0, now - self._last))
        self._last = now
        self._bursts = [b for b in self._bursts
                        if now - b.t0 < (CELEBRATE_SECONDS if b.kind == "entry" else WIN_SECONDS)]
        alive = []
        for pt in self._particles:
            if now < pt.t0:
                alive.append(pt)
                continue
            if now - pt.t0 > pt.life:
                continue
            drag = 0.985 if pt.spin else 0.97
            pt.vx *= drag
            pt.vy = pt.vy * drag + 3.2 * dt              # gravedad suave
            pt.x += pt.vx * dt
            pt.y += pt.vy * dt
            alive.append(pt)
        self._particles = alive
        self._spin += dt * (10 + 260 * self._energy(now))
        return dt

    # -- dibujo --------------------------------------------------------------------------------
    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        now = time.monotonic()
        self._step(now)
        energy = self._energy(now)
        s, pos = self._geometry()
        cx, cy, _ = pos["center"]
        center = QPointF(cx, cy)
        occupied = {info.slot: key for key, info in self.infos.items()}
        entry = next((b for b in reversed(self._bursts) if b.kind == "entry"), None)
        tint = entry.color if entry else theme.ACCENT

        # resplandor de fondo que late con la energía
        glow_r = 2.9 * s
        bg = QRadialGradient(center, glow_r)
        bg.setColorAt(0.0, _alpha(tint, 0.10 + 0.35 * energy))
        bg.setColorAt(0.55, _alpha(tint, 0.03 + 0.12 * energy))
        bg.setColorAt(1.0, _alpha(tint, 0.0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(bg))
        p.drawEllipse(center, glow_r, glow_r)

        # anillos de fondo que giran en sentidos opuestos
        for i, r in enumerate((1.95 * s, 2.55 * s)):
            pen = QPen(theme.mix(theme.RING_DOT, tint, energy) if energy else QColor(theme.RING_DOT))
            pen.setWidthF(1.0 + 1.5 * energy)
            pen.setDashPattern([1.0, 5.0] if i == 0 else [6.0, 6.0])
            pen.setDashOffset((self._spin if i == 0 else -self._spin * 0.6) / 4)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(center, r, r)

        # chispas orbitando el anillo exterior, con estela
        r_orb = 2.55 * s
        for k in range(ORBITERS):
            base = math.radians(self._spin * (1.4 if k % 2 else -1.0)) + k * math.tau / ORBITERS
            for j in range(6):
                a = base - j * 0.045 * (1 if k % 2 else -1)
                pt = QPointF(cx + r_orb * math.cos(a), cy + r_orb * math.sin(a))
                fade = 1 - j / 6
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(_alpha(tint if energy > 0.05 else theme.ACCENT, (0.25 + 0.6 * energy) * fade + 0.1 * fade))
                p.drawEllipse(pt, (1.9 + 1.6 * energy) * fade, (1.9 + 1.6 * energy) * fade)

        # conexiones en reposo con un brillo que recorre cada radio hacia fuera
        edge_pen = QPen(QColor(theme.EDGE)); edge_pen.setWidthF(1.2)
        for slot in RING_SLOTS:
            end = QPointF(*pos[slot][:2])
            if slot in occupied and "center" in occupied:
                p.setPen(edge_pen)
                p.drawLine(center, end)
                t = (now * 0.55 + slot / 6) % 1.0
                dot = QPointF(cx + (end.x() - cx) * t, cy + (end.y() - cy) * t)
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(_alpha(theme.ACCENT, 0.55 * math.sin(math.pi * t)))
                p.drawEllipse(dot, 2.0, 2.0)
            nxt = (slot + 1) % 6
            if slot in occupied and nxt in occupied:
                p.setPen(edge_pen)
                p.drawLine(end, QPointF(*pos[nxt][:2]))

        # mensajes en vuelo: cometa con estela
        self._flows = [f for f in self._flows if now - f.t0 < FLOW_SECONDS]
        for f in self._flows:
            if f.src not in self.infos:
                continue
            t = (now - f.t0) / FLOW_SECONDS
            a, b = self._center_of(f.src, pos), self._center_of(f.dst, pos)
            fade = max(0.0, 1.0 - t)
            pen = QPen(_alpha(theme.ACCENT, 0.2 + 0.6 * fade)); pen.setWidthF(2.2)
            p.setPen(pen)
            p.drawLine(a, b)
            p.setPen(Qt.PenStyle.NoPen)
            for j in range(5):
                tj = max(0.0, t - j * 0.035)
                dot = QPointF(a.x() + (b.x() - a.x()) * tj, a.y() + (b.y() - a.y()) * tj)
                p.setBrush(_alpha(theme.TEXT if j == 0 else theme.ACCENT, 1 - j / 5))
                p.drawEllipse(dot, 3.8 - j * 0.6, 3.8 - j * 0.6)

        # entrada en un trade: rayos eléctricos de Cortex a cada skill y ondas expansivas
        if entry:
            self._draw_entry_back(p, entry, now, s, pos, occupied, center)

        # hexágonos (huecos libres del anillo primero, para quedar al fondo)
        for slot in RING_SLOTS:
            if slot not in occupied:
                self._draw_free(p, pos[slot], now)
        for slot, key in occupied.items():
            self._draw_skill(p, key, pos[slot], now, energy, entry, center, s)

        self._draw_particles(p, now, center, s)
        for b in self._bursts:
            self._draw_banner(p, b, now, center, s)

    def _draw_entry_back(self, p: QPainter, b: _Burst, now: float, s: float, pos: dict, occupied: dict,
                         center: QPointF) -> None:
        t = now - b.t0
        # destello general
        if t < 0.35:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(_alpha(b.color, 0.28 * (1 - t / 0.35)))
            p.drawRect(self.rect())
        # rayos en zigzag que tiemblan
        if t < 1.1:
            rng = random.Random(int(now * 30))
            for slot in RING_SLOTS:
                if slot not in occupied:
                    continue
                end = QPointF(*pos[slot][:2])
                path = QPainterPath(center)
                dx, dy = end.x() - center.x(), end.y() - center.y()
                nx, ny = -dy, dx
                norm = math.hypot(nx, ny) or 1
                for i in range(1, 8):
                    k = i / 8
                    off = rng.uniform(-0.12, 0.12) * s
                    path.lineTo(center.x() + dx * k + nx / norm * off, center.y() + dy * k + ny / norm * off)
                path.lineTo(end)
                fade = 1 - t / 1.1
                for width, alpha in ((7.0, 0.18), (3.0, 0.5), (1.2, 1.0)):
                    pen = QPen(_alpha(b.color if width > 2 else theme.TEXT, alpha * fade)); pen.setWidthF(width)
                    pen.setCapStyle(Qt.PenCapStyle.RoundCap); pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                    p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
                    p.drawPath(path)
        # tres ondas expansivas escalonadas, una de ellas hexagonal
        for i, delay in enumerate((0.0, 0.18, 0.4)):
            tt = (t - delay) / 1.3
            if not 0 < tt < 1:
                continue
            r = s * (0.6 + 3.4 * (1 - (1 - tt) ** 3))
            pen = QPen(_alpha(b.color if i != 1 else theme.WARN, 0.9 * (1 - tt))); pen.setWidthF(6 * (1 - tt) + 1)
            p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
            if i == 1:
                p.drawPolygon(hexagon(center.x(), center.y(), r))
            else:
                p.drawEllipse(center, r, r)

    def _draw_free(self, p: QPainter, geo, now: float) -> None:
        cx, cy, size = geo
        pen = QPen(QColor(theme.FREE_LINE)); pen.setStyle(Qt.PenStyle.DashLine); pen.setWidthF(1.0)
        pen.setDashOffset(-now * 4)                              # el contorno discontinuo corre despacio
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPolygon(hexagon(cx, cy, size * 0.94))
        p.setPen(QColor(theme.FREE_TEXT))
        font = QFont(self.font()); font.setPointSizeF(8.5); p.setFont(font)
        p.drawText(QRectF(cx - size, cy - 9, 2 * size, 18), Qt.AlignmentFlag.AlignCenter, "Libre")

    def _draw_skill(self, p: QPainter, key: str, geo, now: float, energy: float, entry: _Burst | None,
                    center: QPointF, s: float) -> None:
        cx, cy, size = geo
        view = self.views[key]
        fill, border = theme.hex_style(view.state)
        phase = hash(key) % 628 / 100
        # respiración suave + rebote en cadena desde el centro al entrar en un trade
        scale = 1 + 0.012 * math.sin(now * 1.6 + phase) + (0.04 if key == self._hover else 0)
        if entry:
            dist = math.hypot(cx - center.x(), cy - center.y()) / (2 * s)
            scale += 0.22 * _bounce(now - entry.t0 - 0.08 - 0.22 * dist)
        size *= scale
        poly = hexagon(cx, cy, size * 0.94)
        if key == self.selected:
            sel = QPen(QColor(theme.SELECT)); sel.setWidthF(1.4)
            sel.setDashPattern([4.0, 3.0]); sel.setDashOffset(now * 8)
            p.setPen(sel); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPolygon(hexagon(cx, cy, size * 1.08))
        # halo cuando trabaja, acaba de recibir un mensaje o el bot entra en un trade
        pulse = 0.0
        if view.state == "working":
            pulse = 0.5 + 0.5 * math.sin(now * 9)
        for f in self._flows:
            if f.dst == key:
                pulse = max(pulse, 1.0 - (now - f.t0) / FLOW_SECONDS)
        glow_color = theme.ACCENT
        if energy > 0:
            pulse = max(pulse, energy)
            glow_color = entry.color if entry else theme.WARN
        if pulse > 0:
            for width, alpha in ((14.0, 0.12), (8.0, 0.25), (4.0, 0.55)):
                gp = QPen(_alpha(glow_color, alpha * pulse)); gp.setWidthF(width)
                gp.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                p.setPen(gp); p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawPolygon(poly)
        # relleno con un degradado radial que se enciende con la energía
        grad = QRadialGradient(QPointF(cx, cy - size * 0.3), size * 1.2)
        top = theme.mix(fill, glow_color, 0.35 * energy) if energy else fill
        grad.setColorAt(0.0, QColor(theme.mix(top, theme.TEXT, 0.10)))
        grad.setColorAt(1.0, QColor(top))
        bp = QPen(QColor(border)); bp.setWidthF(2.0 if view.state != "idle" else 1.4)
        p.setPen(bp)
        p.setBrush(QBrush(grad))
        p.drawPolygon(poly)
        # Cortex (el centro) lleva un borde de luz que gira sin parar
        if self.infos[key].slot == "center":
            cone = QConicalGradient(QPointF(cx, cy), -self._spin * 2.2)
            hot = entry.color if entry else theme.ACCENT
            cone.setColorAt(0.0, _alpha(hot, 1.0))
            cone.setColorAt(0.18, _alpha(theme.TEXT, 0.9))
            cone.setColorAt(0.35, _alpha(hot, 0.0))
            cone.setColorAt(0.5, _alpha(hot, 0.0))
            cone.setColorAt(0.68, _alpha(hot, 0.8))
            cone.setColorAt(0.85, _alpha(hot, 0.0))
            cone.setColorAt(1.0, _alpha(hot, 1.0))
            cp = QPen(QBrush(cone), 2.6 + 2.5 * energy)
            cp.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            p.setPen(cp); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawPolygon(hexagon(cx, cy, size * 1.0))

        # texto: nombre y, debajo, la descripción corta del estado
        title_font = QFont(self.font()); title_font.setBold(True)
        title_font.setPointSizeF(10.5 if size > 40 else 8.5)
        p.setFont(title_font)
        p.setPen(QColor(theme.TEXT))
        title = self.infos[key].title
        p.drawText(QRectF(cx - size, cy - size * 0.42, 2 * size, size * 0.5), Qt.AlignmentFlag.AlignCenter, title)
        sub_font = QFont(self.font()); sub_font.setPointSizeF(7.8 if size > 40 else 6.5)
        p.setFont(sub_font)
        caption = view.caption
        tone = theme.BULL if caption.startswith("Bullish") else theme.BEAR if caption.startswith("Bearish") else theme.MUTED
        p.setPen(QColor(theme.BEAR if view.state == "error" else tone if key == "bias" else theme.MUTED))
        text = "error" if view.state == "error" else (view.caption or (f"x {view.handled}" if view.handled else ""))
        text = QFontMetrics(sub_font).elidedText(text, Qt.TextElideMode.ElideRight, int(size * 1.45))
        p.drawText(QRectF(cx - size, cy + size * 0.06, 2 * size, size * 0.4), Qt.AlignmentFlag.AlignCenter, text)

    def _draw_particles(self, p: QPainter, now: float, center: QPointF, s: float) -> None:
        for pt in self._particles:
            age = now - pt.t0
            if age < 0:
                continue
            fade = 1 - age / pt.life
            x, y = center.x() + pt.x * s, center.y() + pt.y * s
            size = pt.size * s
            if pt.spin:
                p.save()
                p.translate(x, y)
                p.rotate(math.degrees(age * pt.spin))
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(_alpha(pt.color, fade))
                # el ancho oscila: parece que el papel da vueltas en el aire
                p.drawRect(QRectF(-size / 2, -size * 0.3 * abs(math.cos(age * pt.spin * 0.7)), size,
                                  size * 0.6 * abs(math.cos(age * pt.spin * 0.7)) + 0.6))
                p.restore()
            else:
                tail = QPointF(x - pt.vx * s * 0.06, y - pt.vy * s * 0.06)
                pen = QPen(_alpha(pt.color, 0.7 * fade)); pen.setWidthF(size * 0.7)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                p.setPen(pen)
                p.drawLine(tail, QPointF(x, y))
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(_alpha(theme.TEXT, fade))
                p.drawEllipse(QPointF(x, y), size * 0.35, size * 0.35)

    def _draw_banner(self, p: QPainter, b: _Burst, now: float, center: QPointF, s: float) -> None:
        span = CELEBRATE_SECONDS if b.kind == "entry" else WIN_SECONDS
        t = now - b.t0
        pop = _ease_out_back(t / 0.45)
        fade = 1.0 if t < span - 0.6 else max(0.0, (span - t) / 0.6)
        if pop <= 0 or fade <= 0:
            return
        y = center.y() - (0 if b.kind == "entry" else s * 1.05)
        p.save()
        p.translate(center.x(), y - (t * s * 0.12 if b.kind == "win" else 0))
        p.scale(pop, pop)
        big = QFont(self.font()); big.setBold(True); big.setPointSizeF(max(14.0, s * (0.5 if b.kind == "entry" else 0.36)))
        big.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 112)
        fm = QFontMetrics(big)
        w = fm.horizontalAdvance(b.title) + s * 0.6
        h = fm.height() + s * 0.12
        pill = QRectF(-w / 2, -h / 2, w, h)
        # pastilla con brillo
        for grow, alpha in ((10, 0.10), (5, 0.22)):
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(_alpha(b.color, alpha * fade))
            p.drawRoundedRect(pill.adjusted(-grow, -grow, grow, grow), h / 2 + grow, h / 2 + grow)
        p.setBrush(_alpha(theme.mix(theme.BG, b.color, 0.25), 0.92 * fade))
        pen = QPen(_alpha(b.color, fade)); pen.setWidthF(2.0)
        p.setPen(pen)
        p.drawRoundedRect(pill, h / 2, h / 2)
        # brillo que barre la pastilla de izquierda a derecha
        sweep = (t * 1.4) % 1.6 - 0.3
        sx = -w / 2 + sweep * w
        clip = QPainterPath(); clip.addRoundedRect(pill, h / 2, h / 2)
        p.setClipPath(clip)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(_alpha(theme.TEXT, 0.22 * fade))
        p.drawPolygon(QPolygonF([QPointF(sx, -h / 2), QPointF(sx + h * 0.5, -h / 2),
                                 QPointF(sx + h * 0.1, h / 2), QPointF(sx - h * 0.4, h / 2)]))
        p.setClipping(False)
        p.setFont(big)
        p.setPen(_alpha(theme.TEXT, fade))
        p.drawText(pill, Qt.AlignmentFlag.AlignCenter, b.title)
        if b.subtitle:
            small = QFont(self.font()); small.setBold(True); small.setPointSizeF(max(8.0, s * 0.18))
            p.setFont(small)
            p.setPen(_alpha(b.color, fade))
            p.drawText(QRectF(-w, h / 2 + 2, 2 * w, s * 0.4), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                       b.subtitle)
        p.restore()


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
