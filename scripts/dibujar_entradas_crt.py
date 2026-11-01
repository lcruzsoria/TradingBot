"""Dibujo de los 4 modelos de entrada del CRT sobre un mismo corto: dónde entra cada uno y cuánto riesgo le deja hasta el stop.

Uso: uv run python scripts/dibujar_entradas_crt.py   ->  docs/estrategia_crt/entradas_crt.svg y .png
"""
from __future__ import annotations

import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "docs" / "estrategia_crt" / "entradas_crt"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
W, H = 680, 565
BULL, BEAR = ("#9FE1CB", "#0F6E56"), ("#F5C4B3", "#993C1D")
COLORS = {1: "#378ADD", 2: "#7F77DD", 3: "#D4537E", 4: "#EF9F27"}
NAMES = {1: ("Vela siguiente al CISD", "a la apertura de la vela posterior a la del CISD"),
         2: ("Retesteo del iFVG", "cuando el precio vuelve a tocar el iFVG (si no vuelve, no hay entrada)"),
         3: ("Primera vela sin mecha", "a la apertura de la vela posterior a la primera bajista sin mecha"),
         4: ("Cierre del CISD", "al cierre de la propia vela del CISD, sin esperar a la siguiente")}
# (x, apertura, cierre, máximo, mínimo) en coordenadas del dibujo (y menor = precio más alto)
CANDLES = [(110, 175, 150, 143, 180), (155, 150, 125, 118, 155), (200, 127, 100, 80, 125), (245, 102, 148, 95, 152),
           (290, 148, 182, 143, 188), (335, 188, 205, 184, 210), (380, 205, 235, 205, 240), (425, 235, 150, 143, 240),
           (470, 150, 260, 148, 265), (515, 260, 330, 262, 335), (560, 330, 395, 332, 400)]
SL, FVG_TOP, FVG_BOT = 80, 125, 143
ENTRY = {1: (335, 188), 2: (425, 143), 3: (425, 235), 4: (290, 182)}


def svg() -> str:
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{round(1000 * H / W)}" viewBox="0 0 {W} {H}" '
         'font-family="Segoe UI, Arial, sans-serif"><rect width="680" height="565" fill="#ffffff"/>',
         '<text x="20" y="26" font-size="16" font-weight="600" fill="#222">Los 4 modelos de entrada del CRT, sobre el mismo corto</text>',
         f'<rect x="100" y="{FVG_TOP}" width="165" height="{FVG_BOT - FVG_TOP}" fill="#CECBF6" stroke="#7F77DD" stroke-width="0.8"/>',
         f'<line x1="200" y1="{SL}" x2="600" y2="{SL}" stroke="#E24B4A" stroke-dasharray="5 4"/>',
         f'<text x="606" y="{SL + 4}" font-size="12" fill="#A32D2D">SL</text>',
         '<text x="200" y="66" font-size="12" fill="#333" text-anchor="middle">Sweep</text>',
         f'<text x="96" y="{FVG_BOT - 2}" font-size="12" fill="#534AB7" text-anchor="end">iFVG</text>',
         '<line x1="110" y1="175" x2="310" y2="175" stroke="#7F77DD" stroke-dasharray="3 3"/>',
         '<text x="96" y="192" font-size="12" fill="#534AB7" text-anchor="end">Nivel CISD</text>']
    for x, op, cl, hi, lo in CANDLES:
        fill, line = BULL if cl < op else BEAR
        o.append(f'<line x1="{x}" y1="{hi}" x2="{x}" y2="{lo}" stroke="#333"/>'
                 f'<rect x="{x - 9}" y="{min(op, cl)}" width="18" height="{abs(cl - op)}" fill="{fill}" stroke="{line}" stroke-width="0.8"/>')
    for m, (x, y) in ENTRY.items():
        o.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{COLORS[m]}" stroke="#333" stroke-width="0.8"/>'
                 f'<text x="{x}" y="{y + 4.5}" font-size="12" font-weight="600" fill="#ffffff" text-anchor="middle">{m}</text>')
    o.append('<text x="20" y="428" font-size="13" font-weight="600" fill="#222">Modelo · dónde entra · riesgo hasta el SL (barra)</text>')
    for i, m in enumerate(sorted(NAMES)):
        y, (name, how) = 450 + i * 21, NAMES[m]
        risk = ENTRY[m][1] - SL
        o += [f'<circle cx="28" cy="{y - 4}" r="7" fill="{COLORS[m]}" stroke="#333" stroke-width="0.8"/>'
              f'<text x="28" y="{y}" font-size="11" font-weight="600" fill="#ffffff" text-anchor="middle">{m}</text>',
              f'<text x="44" y="{y}" font-size="12" fill="#222"><tspan font-weight="600">{name}:</tspan> {how}</text>',
              f'<rect x="{W - 20 - risk * 0.55:.0f}" y="{y - 9}" width="{risk * 0.55:.0f}" height="8" fill="{COLORS[m]}" opacity="0.8"/>']
    o.append('<text x="20" y="545" font-size="11" fill="#555">Riesgo = distancia de la entrada al SL. El 2 deja el menor, pero puede no llegar a entrar;</text>'
             '<text x="20" y="559" font-size="11" fill="#555">el 4 es la entrada más temprana de las que entran siempre, y el 3 es la más tardía.</text>')
    return "".join(o) + "</svg>"


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.with_suffix(".svg").write_text(svg(), encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", f"--window-size=1000,{round(1000 * H / W)}",
                    f"--screenshot={OUT.with_suffix('.png')}", OUT.with_suffix(".svg").resolve().as_uri()], check=True, capture_output=True)
    print("escrito", OUT.with_suffix(".png"))
