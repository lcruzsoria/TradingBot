"""Iconos dibujados con QPainter (no dependen de las fuentes del sistema, que a veces no tienen el glifo)."""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPixmap


def gear_icon(color: str, size: int = 16, scale: int = 2) -> QIcon:
    """Rueda dentada (ajustes) del color indicado."""
    px = size * scale
    pix = QPixmap(px, px)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    c = px / 2
    outer, body, hole, teeth = px * 0.47, px * 0.34, px * 0.14, 8
    path = QPainterPath()
    path.setFillRule(Qt.FillRule.OddEvenFill)
    step = 2 * math.pi / teeth
    points = []
    for i in range(teeth):                      # perfil con dientes: sube al radio exterior en un tramo de cada paso
        a0 = i * step
        for ang, radius in ((a0 - step * 0.16, body), (a0 - step * 0.10, outer), (a0 + step * 0.10, outer),
                            (a0 + step * 0.16, body)):
            points.append(QPointF(c + radius * math.cos(ang), c + radius * math.sin(ang)))
    path.moveTo(points[0])
    for pt in points[1:]:
        path.lineTo(pt)
    path.closeSubpath()
    path.addEllipse(QRectF(c - hole, c - hole, 2 * hole, 2 * hole))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(color))
    p.drawPath(path)
    p.end()
    pix.setDevicePixelRatio(scale)
    return QIcon(pix)
