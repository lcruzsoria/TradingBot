"""Dibuja la regla del FVG de MTF del CRT: esquema del corto y del largo.

Corto: la vela C2 de H3 toma el máximo de C1 y vuelve al rango; esa mecha toca un FVG BAJISTA de MTF (M15/M30/H1) creado antes, en la bajada,
que queda entero POR ENCIMA del máximo de C1. Largo: el espejo (FVG alcista por debajo del mínimo de C1).

Uso: uv run python scripts/dibujar_regla_fvg.py [--png]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from dibujar_crt import AMBER, BLUE, CHROME, GREEN, GREY, INK, MUTED, PURPLE, RED, W, esc, textwrap          # noqa: E402

PW, PH = 545, 330                                                                      # tamaño de cada esquema
HEIGHT = 640
OUT = ROOT / "docs" / "estrategia_crt" / "regla_fvg_mtf"


def panel(x0: float, y0: float, up: bool) -> str:
    """Esquema de un sweep. up: sweep del máximo (corto), FVG bajista por encima de C1. Si no, el espejo (largo)."""
    fy = (lambda y: y0 + 18 + y) if up else (lambda y: y0 + PH - 18 - y)                         # el espejo da la vuelta a la geometría
    fx = lambda x: x0 + x                                                              # noqa: E731
    col = RED if up else GREEN
    fvg = "bajista" if up else "alcista"
    s = [f'<rect x="{x0}" y="{y0}" width="{PW}" height="{PH}" rx="12" fill="#fff" stroke="#cbd5e1"/>']

    def candle(x, o, hi, lo, cl, color, w=24):
        a, b, c_, d = fy(o), fy(hi), fy(lo), fy(cl)
        return (f'<line x1="{fx(x)}" y1="{b}" x2="{fx(x)}" y2="{c_}" stroke="{color}" stroke-width="2.2"/>'
                f'<rect x="{fx(x) - w / 2}" y="{min(a, d)}" width="{w}" height="{max(abs(a - d), 2)}" fill="{color}"/>')

    # FVG de MTF creado antes, en el tramo que lleva el precio hacia C1 (en el corto: una bajada)
    zt, zb = 70, 102
    s.append(f'<rect x="{fx(50)}" y="{min(fy(zt), fy(zb))}" width="{455}" height="{abs(fy(zt) - fy(zb))}" fill="{col}" opacity="0.18"/>'
             f'<rect x="{fx(50)}" y="{min(fy(zt), fy(zb))}" width="{455}" height="{abs(fy(zt) - fy(zb))}" fill="none" stroke="{col}" stroke-width="1.4" stroke-dasharray="5 3"/>')
    s.append(candle(70, 46, 40, zt, 66, col))                                          # vela 1: su mínimo (en el corto) es el borde alto de la zona
    s.append(candle(100, 68, 62, 150, 140, col))                                       # vela 2: la caída fuerte que deja el hueco
    s.append(candle(130, 138, zb, 160, 152, col))                                      # vela 3: su máximo es el borde bajo de la zona
    for k, xx in enumerate((70, 100, 130), 1):
        s.append(f'<text x="{fx(xx)}" y="{fy(32) + (0 if up else 4)}" font-size="11" fill="{MUTED}" text-anchor="middle">{k}</text>')
    # tramo hasta C1 (el precio baja y rebota) y CRH
    s.append(candle(165, 150, 143, 192, 186, col, 18))
    s.append(candle(195, 186, 180, 215, 208, col, 18))
    s.append(f'<line x1="{fx(225)}" y1="{fy(168)}" x2="{fx(PW - 20)}" y2="{fy(168)}" stroke="{BLUE}" stroke-width="1.6" stroke-dasharray="6 4"/>')
    s.append(f'<text x="{fx(PW - 24)}" y="{fy(184) + (0 if up else 0)}" font-size="12" font-weight="700" fill="{BLUE}" text-anchor="end">{"máximo" if up else "mínimo"} de C1 (CRH)</text>')
    s.append(candle(260, 232, 168, 262, 200, GREEN if up else RED, 28))               # C1 dentro del rango
    s.append(f'<text x="{fx(260)}" y="{y0 + PH - 14}" font-size="13" font-weight="700" fill="{MUTED}" text-anchor="middle">C1 (H3)</text>')
    s.append(f'<line x1="{fx(350)}" y1="{fy(88)}" x2="{fx(350)}" y2="{fy(236)}" stroke="{AMBER}" stroke-width="2.4"/>')
    s.append(f'<rect x="{fx(336)}" y="{min(fy(196), fy(214))}" width="28" height="{abs(fy(196) - fy(214))}" fill="{AMBER}"/>')
    s.append(f'<text x="{fx(350)}" y="{y0 + PH - 14}" font-size="13" font-weight="700" fill="{AMBER}" text-anchor="middle">C2 (H3)</text>')
    s.append(f'<circle cx="{fx(350)}" cy="{fy(88)}" r="6" fill="none" stroke="{INK}" stroke-width="2.4"/>')
    s.append(f'<text x="{fx(366)}" y="{fy(88) + 4}" font-size="12" font-weight="700" fill="{INK}">toca el FVG</text>')
    # rótulos
    ty = fy(128 if up else 138)
    s.append(f'<text x="{fx(150)}" y="{ty}" font-size="13" font-weight="700" fill="{col if up else "#15803d"}">FVG {fvg} de MTF (M15 / M30 / H1), creado antes</text>')
    s.append(f'<text x="{fx(150)}" y="{ty + 17}" font-size="12.5" fill="#334155">{"por encima" if up else "por debajo"} del {"máximo" if up else "mínimo"} de C1: tendencia {"bajista" if up else "alcista"}</text>')
    title = "CORTO: C2 toma el máximo de C1 y vuelve al rango" if up else "LARGO: C2 toma el mínimo de C1 y vuelve al rango"
    s.append(f'<text x="{x0 + 16}" y="{y0 + 26}" font-size="15" font-weight="700" fill="{INK}">{title}</text>')
    return "".join(s)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--png", action="store_true")
    args = ap.parse_args()
    notes = [("Corto (paso 1 y 2)",
              "1) En H3, C2 toma el máximo de C1 y vuelve a entrar en su rango. 2) Esa mecha toca un FVG BAJISTA de MTF (M15, M30 o H1) creado antes, "
              "en el desarrollo de la bajada, que queda por encima del máximo de C1. Asegura tendencia bajista y liquidez interna tomada.", RED),
             ("Largo (el espejo)",
              "1) C2 toma el mínimo de C1 y vuelve a entrar en su rango. 2) Esa mecha toca un FVG ALCISTA de MTF creado antes, en la subida, "
              "que queda por debajo del mínimo de C1.", GREEN),
             ("Qué cambia en el código",
              "Antes se aceptaba también un FVG cuyo borde coincidía con el extremo de C1 (formado dentro de C1, sin tendencia detrás). "
              "Ahora la zona entera tiene que estar más allá del extremo de C1 y sin mitigar. Con NAS100 quita el 7 % de los setups.", AMBER)]
    cw = (W - 80 - 40) / 3
    boxes = []
    for k, (head, body, color) in enumerate(notes):
        x = 40 + k * (cw + 20)
        boxes.append(f'<rect x="{x:.1f}" y="450" width="{cw:.1f}" height="165" rx="12" fill="#f8fafc" stroke="{color}" stroke-width="1.5"/>'
                     f'<text x="{x + 14:.1f}" y="476" font-size="14.5" font-weight="700" fill="{color if color != AMBER else "#b45309"}">{esc(head)}</text>')
        for j, line in enumerate(textwrap.wrap(body, int((cw - 28) / 6.4))):
            boxes.append(f'<text x="{x + 14:.1f}" y="{500 + j * 18}" font-size="13" fill="#334155">{esc(line)}</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {HEIGHT}" width="{W}" height="{HEIGHT}" '
           f'font-family="Segoe UI, Helvetica, Arial, sans-serif"><rect width="{W}" height="{HEIGHT}" fill="#f1f5f9"/>'
           f'<text x="40" y="44" font-size="26" font-weight="700" fill="{INK}">Regla del FVG de MTF</text>'
           f'<text x="40" y="72" font-size="14" fill="#475569">El FVG se creó antes, en el desarrollo del precio, y queda más allá del extremo de C1: la mecha de C2 lo toca.</text>'
           f'{panel(40, 92, True)}{panel(615, 92, False)}{"".join(boxes)}</svg>')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    svg_path = OUT.with_suffix(".svg")
    svg_path.write_text(svg, encoding="utf-8")
    print("escrito", svg_path)
    if args.png:
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{HEIGHT}",
                        f"--screenshot={OUT.with_suffix('.png')}", svg_path.resolve().as_uri()], check=True, capture_output=True)
        print("PNG listo")


if __name__ == "__main__":
    main()
