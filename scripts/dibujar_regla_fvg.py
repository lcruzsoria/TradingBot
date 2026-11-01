"""Dibuja cómo se entiende la regla del FVG de MTF (propuesta para confirmar): esquema de las dos direcciones y la operación real del 05/10/2026.

Regla dibujada: el FVG de MTF es de la MISMA dirección que el sweep (sweep de máximos -> FVG alcista; sweep de mínimos -> FVG bajista) y está
DENTRO de la mecha del sweep, entre el cuerpo de la vela y el extremo (en un sweep de máximos, por debajo del extremo; en uno de mínimos, por encima).

Uso: uv run python scripts/dibujar_regla_fvg.py [--png]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from backtest_crt import cache_path                                                    # noqa: E402
from dibujar_crt import (AHEAD, AMBER, BLUE, CHROME, GREEN, GREY, INK, MUTED, PURPLE, RED, W, Chart, bars_of, esc, fmt_ny,   # noqa: E402
                         textwrap)
from tradingbot.skills.crt import engine                                               # noqa: E402

HEIGHT = 1085
OUT = ROOT / "docs" / "estrategia_crt" / "regla_fvg_mtf"
PW, PH = 545, 330                                                                      # tamaño de cada esquema


def panel(x0: float, y0: float, up: bool) -> str:
    """Esquema de un sweep. up: sweep de máximos (FVG alcista bajo el extremo). Si no, el espejo (FVG bajista sobre el extremo)."""
    fy = (lambda y: y0 + y) if up else (lambda y: y0 + PH - y)                         # el espejo da la vuelta a la geometría
    fx = lambda x: x0 + x                                                              # noqa: E731
    col, fvg = (GREEN, "alcista") if up else (RED, "bajista")
    s = [f'<rect x="{x0}" y="{y0}" width="{PW}" height="{PH}" rx="12" fill="#fff" stroke="#cbd5e1"/>']

    def candle(x, o, hi, lo, cl, w=26, color=None):
        a, b, c_, d = fy(o), fy(hi), fy(lo), fy(cl)
        color = color or (GREEN if (d <= a if up else d >= a) else RED)
        return (f'<line x1="{fx(x)}" y1="{b}" x2="{fx(x)}" y2="{c_}" stroke="{color}" stroke-width="2.2"/>'
                f'<rect x="{fx(x) - w / 2}" y="{min(a, d)}" width="{w}" height="{max(abs(a - d), 2)}" fill="{color}"/>')

    # CRH (extremo de C1)
    s.append(f'<line x1="{fx(30)}" y1="{fy(130)}" x2="{fx(PW - 20)}" y2="{fy(130)}" stroke="{BLUE}" stroke-width="1.6" stroke-dasharray="6 4"/>')
    s.append(f'<text x="{fx(PW - 22)}" y="{fy(147)}" font-size="12" font-weight="700" fill="{BLUE}" text-anchor="end">{"máximo" if up else "mínimo"} de C1 (CRH)</text>')
    # C1 y C2 (H3). En el esquema alcista: C1 sube, C2 sube más allá del CRH y cierra dentro del rango
    s.append(candle(70, 250, 130, 270, 160, 32))
    s.append(f'<text x="{fx(70)}" y="{y0 + PH - 14}" font-size="13" font-weight="700" fill="{MUTED}" text-anchor="middle">C1</text>')
    s.append(f'<rect x="{fx(160)}" y="{min(fy(50), fy(150))}" width="60" height="{abs(fy(50) - fy(150))}" fill="{AMBER}" opacity="0.2"/>')
    s.append(candle(190, 150, 50, 240, 230, 32, RED if up else GREEN))
    s.append(f'<text x="{fx(190)}" y="{y0 + PH - 14}" font-size="13" font-weight="700" fill="{AMBER}" text-anchor="middle">C2 (H3)</text>')
    s.append(f'<text x="{fx(232)}" y="{fy(158) + (0 if up else 4)}" font-size="12" font-weight="700" fill="#b45309">mecha del sweep</text>')
    # FVG de MTF dentro de la mecha: zona 78-112 (por debajo del extremo 50 y por encima del cuerpo 150) y sus tres velas
    s.append(f'<rect x="{fx(240)}" y="{min(fy(78), fy(112))}" width="{280}" height="{abs(fy(78) - fy(112))}" fill="{col}" opacity="0.2"/>'
             f'<rect x="{fx(240)}" y="{min(fy(78), fy(112))}" width="{280}" height="{abs(fy(78) - fy(112))}" fill="none" stroke="{col}" stroke-width="1.4" stroke-dasharray="5 3"/>')
    s.append(candle(262, 140, 112, 146, 118, 22, col))
    s.append(candle(294, 114, 70, 118, 76, 22, col))
    s.append(candle(326, 80, 56, 78, 62, 22, col))
    for k, xx in enumerate((262, 294, 326), 1):
        s.append(f'<text x="{fx(xx)}" y="{fy(184) + (0 if up else 2)}" font-size="11" fill="{MUTED}" text-anchor="middle">{k}</text>')
    # extremo del sweep
    s.append(f'<circle cx="{fx(190)}" cy="{fy(50)}" r="6" fill="none" stroke="{RED}" stroke-width="2.4"/>')
    s.append(f'<text x="{fx(176)}" y="{fy(50) + 4}" font-size="12" font-weight="700" fill="{RED}" text-anchor="end">extremo del sweep</text>')
    # rótulos del FVG
    ys = fy(212 if up else 230)
    s.append(f'<text x="{fx(240)}" y="{ys}" font-size="13" font-weight="700" fill="{col}">FVG {fvg} de MTF (M15 / M30 / H1)</text>')
    s.append(f'<text x="{fx(240)}" y="{ys + 18}" font-size="12.5" fill="#334155">{"por debajo" if up else "por encima"} del extremo, dentro de la mecha</text>')
    title = "Sweep ALCISTA: barre un máximo (→ corto)" if up else "Sweep BAJISTA: barre un mínimo (→ largo)"
    s.append(f'<text x="{x0 + 16}" y="{y0 + 26}" font-size="15" font-weight="700" fill="{INK}">{title}</text>')
    return "".join(s)


def real_chart(box: tuple) -> tuple[str, list]:
    sym, df = pd.read_pickle(cache_path("puprime", "NAS100", 5))
    e = int(pd.Timestamp("2026-10-05 04:30").timestamp()) + AHEAD
    w = df[(df["ts"] >= e - 6 * 86400) & (df["ts"] <= e + 86400)].reset_index(drop=True)
    cfg = engine.Cfg(180, 18 * 3600, 18 * 3600, AHEAD)
    h3 = engine.aggregate(w, 180, cfg, cfg.origin)
    c2 = h3[h3["ts"] == int(pd.Timestamp("2026-10-05 03:00").timestamp()) + AHEAD].iloc[0]
    c1 = h3[h3["ts"] == int(c2["ts"]) - 180 * 60].iloc[0]
    body_top, extreme, crh = float(max(c2["open"], c2["close"])), float(c2["high"]), float(c1["high"])
    ext_ts = int(pd.Timestamp("2026-10-05 04:15").timestamp()) + AHEAD
    mb = bars_of(engine.aggregate(w, 15, cfg))
    # FVG alcistas de MTF (de las últimas 36 h) cuya zona cae en la mecha de C2 (cuerpo -> extremo): el más estrecho de cada timeframe
    best = {}
    for m in (15, 30, 60):
        mt = engine.aggregate(w, m, cfg)
        for i in range(2, len(mt)):
            if mt["ts"][i] + m * 60 > ext_ts:
                break
            lo, hi = float(mt["high"][i - 2]), float(mt["low"][i])
            if hi > lo and hi >= body_top and lo <= extreme and int(mt["ts"][i]) >= ext_ts - 36 * 3600:
                if m not in best or hi - lo < best[m][2] - best[m][1]:
                    best[m] = (m, lo, hi, int(mt["ts"][i - 2]), int(mt["ts"][i]) + m * 60)
    zones = sorted(best.values())
    a = int(np.searchsorted(mb["ts"], min(z[3] for z in zones) - 10 * 900))
    b = int(np.searchsorted(mb["ts"], e + 90 * 60))
    ch = Chart(mb, a, b, box, extra=(extreme, body_top, crh), pad=0.10)
    ch.frame()
    c2a = int(np.searchsorted(mb["ts"], int(c2["ts"])))
    c2b = int(np.searchsorted(mb["ts"], int(c2["ts"]) + 180 * 60)) - 1
    ch.band(c2a, c2b, AMBER, 0.10)
    ch.zone(c2a, c2b, body_top, extreme, AMBER, 0.22, dash=False)                        # la mecha de C2
    for z in zones:
        ia = int(np.searchsorted(mb["ts"], z[3]))
        ch.zone(ia, c2b, z[1], z[2], GREEN, 0.15 if z[0] != 60 else 0.2)
    # regla anterior (mal): el FVG bajista que contenía el extremo
    for stp in engine.find_setups(w, w, 5, engine.Rule(), cfg)[0]:
        if int(w["ts"][stp["jc"]]) + 5 * 60 == e:
            for zz in stp["zones"]:
                ch.zone(int(np.searchsorted(mb["ts"], zz[3] - zz[0] * 60)), b, zz[1], zz[2], "#475569", 0.35)
    ch.candles()
    ch.hline(crh, a, b, BLUE, "6 4", 1.4)
    ch.text(ch.X(a) + 8, ch.Y(crh) + 17, f"máximo de C1 (CRH) {crh:,.2f}", BLUE, 12, "700")
    ie = int(np.searchsorted(mb["ts"], ext_ts - ((ext_ts - AHEAD) % 900)))
    ch.dot(ie, extreme, RED, 7, ring=True)
    ch.text(ch.X(ie) + 14, ch.Y(extreme) - 12, f"extremo del sweep {extreme:,.2f}", RED, 12, "700")
    ch.text(ch.X(c2a) - 6, ch.Y(body_top) + 26, f"mecha de C2: {body_top:,.2f} → {extreme:,.2f}", "#b45309", 12, "700", "end")
    ch.text(ch.x0 + 14, ch.y0 + 22, "Verde: FVG ALCISTAS de MTF que caen en la mecha (el más estrecho de cada timeframe)", GREEN, 13, "700")
    for k, z in enumerate(zones):
        ch.text(ch.x0 + 14, ch.y0 + 42 + k * 17, f"M{z[0]}: {z[1]:,.2f}–{z[2]:,.2f} (formado {fmt_ny(z[4], '%d/%m %H:%M')})", GREEN, 12, "600")
    ch.text(ch.x0 + 14, ch.y0 + 48 + len(zones) * 17 + 8, "Gris: la regla que tenía implementada (FVG bajista que contenía el extremo)  ✗", MUTED, 12, "700")
    ch.text(ch.x0 + 14, ch.y0 + ch.h - 12, f"MTF M15 · {fmt_ny(mb['ts'][a], '%d/%m %H:%M')} – {fmt_ny(mb['ts'][b], '%d/%m %H:%M')} NY · franja ámbar: C2 (H3)", MUTED, 12, "500")
    return ch.svg(), zones


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--png", action="store_true")
    args = ap.parse_args()
    chart, zones = real_chart((40, 478, 1120, 420))
    markers = "".join(f'<marker id="arr-{c[1:]}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
                      f'<path d="M0 0 L10 5 L0 10 z" fill="{c}"/></marker>' for c in (GREEN, RED, BLUE, AMBER, PURPLE, GREY, MUTED, INK))
    notes = [("Así he entendido la regla",
              "El FVG de MTF que confirma el sweep es de la misma dirección que el sweep y queda dentro de su mecha, entre el cuerpo de C2 y el extremo: "
              "sweep de máximos → FVG alcista por debajo del extremo; sweep de mínimos → FVG bajista por encima.", BLUE),
             ("Qué estaba mal",
              "Yo exigía un FVG de la dirección contraria (bajista en un sweep de máximos) que ya existía y contenía el extremo, por encima de él. "
              "Es lo contrario de lo que pides.", RED),
             ("Lo que necesito que confirmes",
              "1) «Toca la mecha» = la zona del FVG cae dentro de la mecha (cuerpo de C2 → extremo), aunque sobresalga algo por arriba. "
              "2) ¿Vale cualquier FVG de las últimas horas (como estos, de la apertura del domingo) o solo uno formado dentro de C2?", AMBER)]
    cw = (W - 80 - 40) / 3
    boxes = []
    for k, (head, body, color) in enumerate(notes):
        x = 40 + k * (cw + 20)
        boxes.append(f'<rect x="{x:.1f}" y="925" width="{cw:.1f}" height="135" rx="12" fill="#f8fafc" stroke="{color}" stroke-width="1.5"/>'
                     f'<text x="{x + 14:.1f}" y="950" font-size="14" font-weight="700" fill="{color if color != AMBER else "#b45309"}">{esc(head)}</text>')
        for j, line in enumerate(textwrap.wrap(body, int((cw - 28) / 6.4))):
            boxes.append(f'<text x="{x + 14:.1f}" y="{972 + j * 17}" font-size="12.5" fill="#334155">{esc(line)}</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {HEIGHT}" width="{W}" height="{HEIGHT}" '
           f'font-family="Segoe UI, Helvetica, Arial, sans-serif"><defs>{markers}</defs><rect width="{W}" height="{HEIGHT}" fill="#f1f5f9"/>'
           f'<text x="40" y="44" font-size="26" font-weight="700" fill="{INK}">Regla del FVG de MTF: cómo la he entendido</text>'
           f'<text x="40" y="72" font-size="14" fill="#475569">El FVG va a favor del sweep y dentro de su mecha. Arriba, el esquema; abajo, la operación real del 05/10/2026.</text>'
           f'{panel(40, 92, True)}{panel(615, 92, False)}'
           f'<text x="40" y="460" font-size="16" font-weight="700" fill="{INK}">Aplicado a la operación del 05/10/2026 (sweep alcista de H3, corto en NAS100)</text>'
           f'{chart}{"".join(boxes)}</svg>')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    svg_path = OUT.with_suffix(".svg")
    svg_path.write_text(svg, encoding="utf-8")
    print("zonas:", [(m, round(lo, 2), round(hi, 2)) for m, lo, hi, *_ in zones])
    if args.png:
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{HEIGHT}",
                        f"--screenshot={OUT.with_suffix('.png')}", svg_path.resolve().as_uri()], check=True, capture_output=True)
        print("PNG listo")


if __name__ == "__main__":
    main()
