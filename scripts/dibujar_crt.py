"""Dibuja una operación real del backtest CRT paso a paso: 1) HTF con la vela del sweep, 2) FVG de MTF tocado, 3) iFVG, CISD y entrada.

Vuelve a buscar el setup con el motor (tradingbot/skills/crt/engine.py) sobre las velas M5 descargadas, comprueba que coincide con la
operación pedida y escribe tres SVG en docs/estrategia_crt/operacion_<fecha>/ (los PNG se hacen con Chrome, ver --png).

Uso (desde la raíz del proyecto, con las velas de scripts/backtest_crt.py --descargar):
    uv run python scripts/dibujar_crt.py --entrada "2025-03-13 06:55"
"""
from __future__ import annotations

import argparse
import html
import subprocess
import sys
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from backtest_crt import cache_path                                                    # noqa: E402
from tradingbot.skills.crt import engine                                               # noqa: E402

AHEAD = 7 * 3600
GREEN, RED, BLUE, AMBER, PURPLE, GREY, INK, MUTED = "#16a34a", "#dc2626", "#2563eb", "#d97706", "#7c3aed", "#94a3b8", "#0f172a", "#64748b"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
W = 1200


def fmt_ny(ts: int, fmt: str = "%d/%m %H:%M") -> str:
    return pd.Timestamp(int(ts) - AHEAD, unit="s").strftime(fmt)


def esc(text: str) -> str:
    return html.escape(str(text), quote=False)


class Chart:
    """Velas en un rectángulo SVG: eje X por número de vela (sin huecos de fin de semana) y precios a la derecha."""

    def __init__(self, bars: dict, i0: int, i1: int, box: tuple, extra=(), right: int = 104, pad: float = 0.07):
        self.b, self.i0, self.i1 = bars, i0, i1
        self.x0, self.y0, self.w, self.h = box
        self.pw = self.w - right
        n = i1 - i0 + 1
        self.step = self.pw / n
        self.bw = max(self.step * 0.64, 1.2)
        lows, highs = bars["low"][i0:i1 + 1], bars["high"][i0:i1 + 1]
        lo, hi = min(float(lows.min()), *extra) if len(extra) else float(lows.min()), max(float(highs.max()), *extra) if len(extra) else float(highs.max())
        span = hi - lo
        self.pmin, self.pmax = lo - span * pad, hi + span * pad
        self.out: list[str] = []
        self.cid = f"clip{abs(hash((box, i0, i1))) % 10**8}"

    def X(self, i: float) -> float:
        return self.x0 + (i - self.i0 + 0.5) * self.step

    def Y(self, p: float) -> float:
        return self.y0 + self.h * (1 - (p - self.pmin) / (self.pmax - self.pmin))

    def add(self, s: str) -> None:
        self.out.append(s)

    def frame(self) -> None:
        self.add(f'<rect x="{self.x0}" y="{self.y0}" width="{self.w}" height="{self.h}" rx="12" fill="#fff" stroke="#cbd5e1"/>')
        self.add(f'<clipPath id="{self.cid}"><rect x="{self.x0}" y="{self.y0}" width="{self.pw}" height="{self.h}"/></clipPath>')
        # precios (derecha) y rejilla
        for k in range(6):
            p = self.pmin + (self.pmax - self.pmin) * k / 5
            y = self.Y(p)
            self.add(f'<line x1="{self.x0}" y1="{y:.1f}" x2="{self.x0 + self.pw}" y2="{y:.1f}" stroke="#eef2f7"/>')
            self.add(f'<text x="{self.x0 + self.pw + 6}" y="{y + 4:.1f}" font-size="11" fill="{MUTED}">{p:,.2f}</text>')
        # horas (abajo): unas 8 marcas
        n = self.i1 - self.i0 + 1
        every = max(int(round(n / 8)), 1)
        for i in range(self.i0, self.i1 + 1, every):
            x = self.X(i)
            self.add(f'<line x1="{x:.1f}" y1="{self.y0 + self.h - 5}" x2="{x:.1f}" y2="{self.y0 + self.h}" stroke="{GREY}"/>')
            self.add(f'<text x="{x:.1f}" y="{self.y0 + self.h + 15}" font-size="11" fill="{MUTED}" text-anchor="middle">'
                     f'{fmt_ny(self.b["ts"][i])}</text>')

    def clipped(self, content: str) -> str:
        return f'<g clip-path="url(#{self.cid})">{content}</g>'

    def band(self, ia: int, ib: int, color: str, opacity: float = 0.14) -> None:
        xa, xb = self.X(ia) - self.step / 2, self.X(ib) + self.step / 2
        self.add(self.clipped(f'<rect x="{xa:.1f}" y="{self.y0}" width="{xb - xa:.1f}" height="{self.h}" fill="{color}" opacity="{opacity}"/>'))

    def candles(self, bars_up: str = GREEN, bars_dn: str = RED) -> None:
        o, h, l, c = (self.b[k] for k in ("open", "high", "low", "close"))
        parts = []
        for i in range(self.i0, self.i1 + 1):
            col = bars_up if c[i] >= o[i] else bars_dn
            x = self.X(i)
            top, bot = self.Y(max(o[i], c[i])), self.Y(min(o[i], c[i]))
            parts.append(f'<line x1="{x:.1f}" y1="{self.Y(h[i]):.1f}" x2="{x:.1f}" y2="{self.Y(l[i]):.1f}" stroke="{col}" stroke-width="1.3"/>')
            parts.append(f'<rect x="{x - self.bw / 2:.1f}" y="{top:.1f}" width="{self.bw:.1f}" height="{max(bot - top, 1):.1f}" fill="{col}"/>')
        self.add(self.clipped("".join(parts)))

    def outline(self, ia: int, ib: int, color: str, width: float = 2.0) -> None:
        """Marco alrededor de varias velas."""
        lo = min(float(self.b["low"][ia:ib + 1].min()), 1e18)
        hi = float(self.b["high"][ia:ib + 1].max())
        xa, xb = self.X(ia) - self.step / 2 - 1, self.X(ib) + self.step / 2 + 1
        self.add(self.clipped(f'<rect x="{xa:.1f}" y="{self.Y(hi) - 4:.1f}" width="{xb - xa:.1f}" height="{self.Y(lo) - self.Y(hi) + 8:.1f}" '
                              f'rx="4" fill="none" stroke="{color}" stroke-width="{width}"/>'))

    def zone(self, ia: float, ib: float, bottom: float, top: float, color: str, opacity: float = 0.28, dash: bool = True) -> None:
        xa, xb = self.X(ia) - self.step / 2, self.X(ib) + self.step / 2
        ya, yb = self.Y(top), self.Y(bottom)
        self.add(self.clipped(f'<rect x="{xa:.1f}" y="{ya:.1f}" width="{xb - xa:.1f}" height="{max(yb - ya, 2):.1f}" fill="{color}" opacity="{opacity}"/>'
                              f'<rect x="{xa:.1f}" y="{ya:.1f}" width="{xb - xa:.1f}" height="{max(yb - ya, 2):.1f}" fill="none" stroke="{color}" '
                              f'stroke-width="1.2"{" stroke-dasharray=\"5 3\"" if dash else ""}/>'))

    def hline(self, price: float, ia: float, ib: float, color: str, dash: str = "", width: float = 1.5, label: str = "") -> None:
        y = self.Y(price)
        xa, xb = self.X(ia) - self.step / 2, self.X(ib) + self.step / 2
        self.add(self.clipped(f'<line x1="{xa:.1f}" y1="{y:.1f}" x2="{xb:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="{width}"'
                              f'{f" stroke-dasharray=\"{dash}\"" if dash else ""}/>'))
        if label:
            self.add(f'<rect x="{self.x0 + self.pw + 2}" y="{y - 9:.1f}" width="{self.w - self.pw - 4}" height="18" rx="4" fill="{color}"/>'
                     f'<text x="{self.x0 + self.pw + 6}" y="{y + 4:.1f}" font-size="11" font-weight="700" fill="#fff">{esc(label)}</text>')

    def text(self, x: float, y: float, s: str, color: str = INK, size: int = 13, weight: str = "600", anchor: str = "start") -> None:
        lines = s.split("\n")
        tspans = "".join(f'<tspan x="{x:.1f}" dy="{0 if k == 0 else size + 3}">{esc(line)}</tspan>' for k, line in enumerate(lines))
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}" '
                 f'style="paint-order:stroke;stroke:#fff;stroke-width:4px;stroke-linejoin:round">{tspans}</text>')

    def arrow(self, x1: float, y1: float, x2: float, y2: float, color: str) -> None:
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="1.6" marker-end="url(#arr-{color[1:]})"/>')

    def dot(self, i: float, price: float, color: str, r: float = 5, ring: bool = False) -> None:
        self.add(f'<circle cx="{self.X(i):.1f}" cy="{self.Y(price):.1f}" r="{r}" fill="{"none" if ring else color}" stroke="{color}" stroke-width="2.2"/>')

    def svg(self) -> str:
        return "".join(self.out)


def page(title: str, subtitle: str, chart: Chart, cards: list[tuple[str, str, str]], height: int) -> str:
    markers = "".join(f'<marker id="arr-{c[1:]}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
                      f'<path d="M0 0 L10 5 L0 10 z" fill="{c}"/></marker>' for c in (GREEN, RED, BLUE, AMBER, PURPLE, GREY, MUTED, INK))
    n = len(cards)
    cw = (W - 80 - 20 * (n - 1)) / n
    ytop = chart.y0 + chart.h + 40
    box = []
    for k, (head, body, color) in enumerate(cards):
        x = 40 + k * (cw + 20)
        box.append(f'<rect x="{x:.1f}" y="{ytop}" width="{cw:.1f}" height="{height - ytop - 24}" rx="12" fill="#f8fafc" stroke="{color}" stroke-width="1.5"/>'
                   f'<text x="{x + 16:.1f}" y="{ytop + 26}" font-size="15" font-weight="700" fill="{color}">{esc(head)}</text>')
        lines = [w for para in body.split("\n") for w in (textwrap.wrap(para, int((cw - 32) / 6.5)) or [""])]
        for j, line in enumerate(lines):
            box.append(f'<text x="{x + 16:.1f}" y="{ytop + 50 + j * 19}" font-size="13" fill="#334155">{esc(line)}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" height="{height}" '
            f'font-family="Segoe UI, Helvetica, Arial, sans-serif"><defs>{markers}</defs><rect width="{W}" height="{height}" fill="#f1f5f9"/>'
            f'<text x="40" y="44" font-size="26" font-weight="700" fill="{INK}">{esc(title)}</text>'
            f'<text x="40" y="72" font-size="14" fill="#475569">{esc(subtitle)}</text>{chart.svg()}{"".join(box)}</svg>')


def bars_of(df: pd.DataFrame) -> dict:
    return {k: df[k].to_numpy().astype(float) if k != "ts" else df[k].to_numpy().astype(np.int64) for k in ("ts", "open", "high", "low", "close")}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--entrada", required=True, help='hora NY de la entrada, p. ej. "2025-03-13 06:55"')
    ap.add_argument("--perfil", default="puprime")
    ap.add_argument("--mercado", default="NAS100")
    ap.add_argument("--variante", type=int, default=1)
    ap.add_argument("--png", action="store_true", help="convierte los SVG a PNG con Chrome")
    args = ap.parse_args()

    sym, df5 = pd.read_pickle(cache_path(args.perfil, args.mercado, 5))
    entry_ts = int(pd.Timestamp(args.entrada).timestamp()) + AHEAD
    w = df5[(df5["ts"] >= entry_ts - 14 * 86400) & (df5["ts"] <= entry_ts + 2 * 86400)].reset_index(drop=True)
    cfg = engine.Cfg(engine.INDICES.htf_min, engine.INDICES.origin, engine.INDICES.session_end, AHEAD)
    rule = engine.Rule()
    setups, _ = engine.find_setups(w, w, 5, rule, cfg)
    found = None
    for st in setups:
        L = engine.view(w, st["sign"])
        ep = engine.entry_point(L, st, args.variante, 5, rule, cfg)
        if ep is not None and int(L["ts"][ep["start"]]) == entry_ts:
            found = (st, L, ep)
            break
    if found is None:
        raise SystemExit(f"No hay ninguna entrada CRT a las {args.entrada} NY en {sym}")
    st, L, ep = found
    res = engine.manage(L, st, ep, rule)
    sgn = st["sign"]
    px = lambda v: sgn * v                                                              # noqa: E731  (espacio del corto -> precio real)
    bars = bars_of(w)
    ts = bars["ts"]
    hx, entry, risk = px(st["stop"]), px(ep["entry"]), ep["risk"]
    target, be = px(ep["entry"] - rule.rr * risk), px(ep["entry"] - risk)
    ih, jc, start, jx = st["ih"], st["jc"], ep["start"], res["exit_index"]
    c1l, c1h = (px(st["c1"][0]), px(st["c1"][1]))
    crh = c1h if sgn > 0 else c1l                                                       # el extremo de C1 que se barre
    side = "corto" if sgn > 0 else "largo"
    out = ROOT / "docs" / "estrategia_crt" / f"operacion_{pd.Timestamp(args.entrada):%Y-%m-%d}"
    out.mkdir(parents=True, exist_ok=True)
    result = f"{res['cómo']} · {res['gross']:+.2f} R bruto"
    head = f"{sym} · {side} · entrada {fmt_ny(ts[start], '%d/%m/%Y %H:%M')} NY · resultado: {result} ({fmt_ny(ts[jx], '%H:%M')})"

    # ---- 1. HTF ---------------------------------------------------------------------------------------------------
    up = sgn > 0                                                                        # corto: el sweep está arriba
    h3 = engine.aggregate(w, cfg.htf_min, cfg, cfg.origin)
    hb = bars_of(h3)
    i2 = int(np.searchsorted(hb["ts"], st["C2"]))
    i0, i1 = max(i2 - 30, 0), min(i2 + 10, len(h3) - 1)
    ch = Chart(hb, i0, i1, (40, 100, 1120, 470), extra=(entry, hx, target, crh))
    ch.frame()
    ch.band(i2 - 1, i2 - 1, BLUE, 0.13)
    ch.band(i2, i2, AMBER, 0.16)
    ch.candles()
    ch.hline(crh, i2 - 1, i1, BLUE, "6 4", 1.6)
    ch.text(ch.X(i2 - 1) - 20, ch.Y(crh) + (16 if up else -8), f"{'máximo' if up else 'mínimo'} de C1 = CRH {crh:,.2f}", BLUE, 12, "700", "end")
    ch.text(ch.X(i2 - 1), ch.y0 + 22, "C1", BLUE, 14, "700", "middle")
    ch.text(ch.X(i2), ch.y0 + 22, "C2", AMBER, 14, "700", "middle")
    c2h, c2c = (hb["high"][i2], hb["close"][i2]) if up else (hb["low"][i2], hb["close"][i2])
    ch.dot(i2, c2h, RED, 5, ring=True)
    ys, yc = (ch.y0 + 70, ch.y0 + ch.h - 80) if up else (ch.y0 + ch.h - 80, ch.y0 + 70)   # el texto del sweep va en el lado del sweep
    ch.arrow(ch.X(i2) - 26, ys + (42 if up else -26), ch.X(i2) - 3, ch.Y(c2h) + (-6 if up else 6), RED)
    ch.text(ch.X(i2) - 34, ys, f"El {'máximo' if up else 'mínimo'} de C2 ({c2h:,.2f}) supera el\nde C1 ({crh:,.2f}): sweep de\nliquidez externa", RED, 13, "700", "end")
    ch.arrow(ch.X(i2) - 26, yc + (-10 if up else 36), ch.X(i2) - 3, ch.Y(c2c) + (4 if up else -4), INK)
    ch.text(ch.X(i2) - 34, yc + (6 if up else 0), f"C2 cierra en {c2c:,.2f}:\ndentro del rango de C1", INK, 13, "700", "end")
    for price, col, lab in ((entry, BLUE, "Entrada"), (hx, RED, "SL"), (target, GREEN, "TP 2R")):
        ch.hline(price, i2, i2 + 3, col, "", 2.0, f"{lab} {price:,.2f}")
    low_i = int(np.argmin(hb["low"][i0:i2])) + i0 if up else int(np.argmax(hb["high"][i0:i2])) + i0
    far = hb["low"][low_i] if up else hb["high"][low_i]
    move = 100 * abs(crh - far) / far
    ch.text(ch.x0 + 14, ch.y0 + ch.h - 12, f"HTF H3 (índices), velas alineadas a las 18:00 NY · {fmt_ny(hb['ts'][i0], '%d/%m')} – {fmt_ny(hb['ts'][i1], '%d/%m/%Y')} · "
            f"líneas cortas: entrada, stop y objetivo de la operación", MUTED, 12, "500")
    cards = [("Paso 1 · sweep en el HTF (liquidez externa)",
              f"C1 ({fmt_ny(hb['ts'][i2 - 1], '%d/%m %H:%M')}): {'máx' if up else 'mín'} {crh:,.2f}, rango {c1l:,.2f}–{c1h:,.2f}\n"
              f"C2 ({fmt_ny(hb['ts'][i2], '%d/%m %H:%M')}): {'máx' if up else 'mín'} {c2h:,.2f}, cierre {c2c:,.2f}", BLUE),
             ("Lo que se comprueba",
              f"✓ C2 {'supera el máximo' if up else 'rompe el mínimo'} de C1 → dirección: {side}\n"
              f"✓ C2 cierra dentro del rango de C1 (no es una rotura)\n"
              f"✓ C2 no barre el otro extremo de C1", GREEN),
             ("Contexto del mercado",
              f"En la ventana, el {'mínimo' if up else 'máximo'} fue {far:,.2f} ({fmt_ny(hb['ts'][low_i], '%d/%m')}) y desde ahí el precio "
              f"{'subió' if up else 'bajó'} un {move:.1f} % hasta el extremo de C1: la zona de {'máximos' if up else 'mínimos'} acumula stops "
              f"que el mercado busca antes de girar.", MUTED)]
    (out / "1_htf.svg").write_text(page("1 · HTF: la vela que se opera y su contexto", head, ch, cards, 810), encoding="utf-8")

    # ---- 2. MTF ---------------------------------------------------------------------------------------------------
    zones = sorted(st["zones"], key=lambda z: z[0])
    z = next((z for z in zones if z[0] == 15), zones[0])
    m = z[0]
    mt = engine.aggregate(w, m, cfg)
    mb = bars_of(mt)
    z_bot, z_top = (px(z[1]), px(z[2])) if up else (px(z[2]), px(z[1]))
    i3 = int(np.searchsorted(mb["ts"], z[3] - m * 60))                                   # tercera vela del FVG
    isw = int(np.searchsorted(mb["ts"], ts[ih] - ((ts[ih] - AHEAD) % (m * 60))))          # vela de MTF que contiene el extremo
    a, b = max(i3 - 2 - 10, 0), min(isw + 12, len(mt) - 1)
    ch = Chart(mb, a, b, (40, 100, 1120, 470), extra=(z_bot, z_top, hx, crh), pad=0.14)
    ch.frame()
    c2a = int(np.searchsorted(mb["ts"], st["C2"]))
    ch.band(c2a, int(np.searchsorted(mb["ts"], st["C2"] + cfg.htf_min * 60)) - 1, AMBER, 0.10)
    ch.zone(i3 - 2, b, z_bot, z_top, "#ea580c", 0.26)
    ch.candles()
    ch.outline(i3 - 2, i3, "#ea580c", 2.0)
    box_y = ch.Y(max(mb["high"][i3 - 2:i3 + 1].max(), z_top)) if up else ch.Y(min(mb["low"][i3 - 2:i3 + 1].min(), z_bot))
    for k, idx in enumerate((i3 - 2, i3 - 1, i3), 1):
        ch.text(ch.X(idx), box_y - 12 if up else box_y + 24, str(k), "#ea580c", 14, "700", "middle")
    ch.hline(crh, a, b, BLUE, "6 4", 1.4)
    ch.text(ch.X(b) - 4, ch.Y(crh) + (16 if up else -8), f"CRH (máximo de C1) {crh:,.2f}", BLUE, 12, "700", "end")
    ch.dot(isw, hx, RED, 7, ring=True)
    ch.text(ch.X(i3 - 2) - 6, box_y - 54 if up else box_y + 70, f"FVG {'bajista' if up else 'alcista'} M{m}: {z_bot:,.2f}–{z_top:,.2f}\n"
            f"vela 3 cerrada {fmt_ny(z[3], '%d/%m %H:%M')}, sin mitigar", "#c2410c", 13, "700")
    right = ch.X(isw) < ch.x0 + 0.62 * ch.pw                                              # hay sitio libre a la derecha del extremo
    d = 1 if right else -1
    ch.arrow(ch.X(isw) + d * 56, ch.Y(hx) + (-46 if up else 46), ch.X(isw) + d * 9, ch.Y(hx) + (-6 if up else 6), RED)
    ch.text(ch.X(isw) + d * 62, ch.Y(hx) + (-52 if up else 52), f"El {'máximo' if up else 'mínimo'} del sweep ({fmt_ny(ts[ih], '%H:%M')}, {hx:,.2f})\nentra en el FVG",
            RED, 13, "700", "start" if right else "end")
    ch.text(ch.x0 + 14, ch.y0 + ch.h - 12, f"MTF M{m} · {fmt_ny(mb['ts'][a], '%d/%m %H:%M')} – {fmt_ny(mb['ts'][b], '%d/%m %H:%M')} NY · franja ámbar: la vela C2 (H3)", MUTED, 12, "500")
    others = [f"M{o[0]} {min(px(o[1]), px(o[2])):,.2f}–{max(px(o[1]), px(o[2])):,.2f}" for o in zones if o[0] != m]
    cards = [("Paso 2 · FVG de MTF tocado (liquidez interna)",
              f"FVG {'bajista' if up else 'alcista'} de M{m}: el hueco que dejan la mecha de la vela 1 y la de la 3. Zona {z_bot:,.2f}–{z_top:,.2f}, "
              f"formada el {fmt_ny(z[3] - m * 60, '%d/%m')} a las {fmt_ny(z[3] - m * 60, '%H:%M')}–{fmt_ny(z[3], '%H:%M')}."
              + (f" También tocado: {', '.join(others)}." if others else ""), "#c2410c"),
             ("Lo que se comprueba",
              f"✓ El FVG ya estaba formado cuando empezó el sweep\n"
              f"✓ Sin mitigar: el precio no había entrado en la zona desde su formación\n"
              f"✓ El extremo del sweep ({hx:,.2f}) cae dentro de la zona", GREEN),
             ("Por qué importa", "Además de la liquidez externa (el extremo de C1) el precio ha tomado liquidez interna: "
                                 "un desequilibrio que ya existía. Es la confirmación de que el sweep llegó a una zona con órdenes. "
                                 "Siguiente paso: bajar a M5 y buscar el iFVG.", MUTED)]
    (out / "2_mtf_fvg.svg").write_text(page("2 · MTF: el sweep toca un FVG (M15/M30/H1)", head, ch, cards, 810), encoding="utf-8")

    # ---- 3. LTF: iFVG, CISD y entrada ------------------------------------------------------------------------------
    sa, se = st["seq"]
    kf, mi = st["kf"], st["m_inv"]
    a, b = max(sa - 22, 0), min(jx + 14, len(w) - 1)
    f_bot, f_top = (px(L["high"][kf - 2]), px(L["low"][kf])) if up else (px(L["low"][kf]), px(L["high"][kf - 2]))
    level = px(st["level"])
    base_fvg = f_bot if up else f_top                                                   # la base del FVG que se invierte
    ch = Chart(bars, a, b, (40, 100, 1120, 500), extra=(entry, hx, target, be, level), pad=0.13)
    ch.frame()
    ch.band(sa, se, GREY, 0.2)
    ch.zone(kf - 2, mi + 1, min(f_bot, f_top), max(f_bot, f_top), PURPLE, 0.22)
    ch.candles()
    ch.outline(kf - 2, kf, PURPLE, 1.8)
    ch.hline(level, sa, jc, PURPLE, "6 4", 1.6, f"CISD {level:,.2f}")
    ch.hline(hx, ih, jx, RED, "", 1.8, f"SL {hx:,.2f}")
    ch.hline(entry, start, jx, BLUE, "", 1.8, f"Entrada {entry:,.2f}")
    ch.hline(be, start, jx, AMBER, "5 4", 1.3, f"1R · BE {be:,.2f}")
    ch.hline(target, start, jx, GREEN, "", 1.8, f"TP 2R {target:,.2f}")
    sgn_y = 1 if up else -1                                                             # +1: los textos "bajo la vela" van hacia abajo
    ch.text(ch.X((sa + se) / 2), ch.y0 + (ch.h - 40 if up else 36), f"secuencia {'alcista' if up else 'bajista'}\ndel sweep ({fmt_ny(ts[sa], '%H:%M')}–{fmt_ny(ts[se], '%H:%M')})", MUTED, 12, "700", "middle")
    ch.dot(ih, hx, RED, 6, ring=True)
    ch.text(ch.X(ih) - 12, ch.Y(hx) + (-10 if up else 22), f"extremo del sweep {fmt_ny(ts[ih], '%H:%M')}", RED, 12, "700", "end")
    box_lo, box_hi = float(bars["low"][kf - 2:kf + 1].min()), float(bars["high"][kf - 2:kf + 1].max())
    ch.text(ch.X(kf - 1), ch.Y(box_lo) + 26 if up else ch.Y(box_hi) - 22,
            f"FVG {'alcista' if up else 'bajista'} M5 ({fmt_ny(ts[kf], '%H:%M')})\nse convertirá en iFVG", PURPLE, 12, "700", "middle")
    cy = bars["close"][jc]
    ty = ch.y0 + 64 if up else ch.y0 + ch.h - 90                                        # zona libre sobre (o bajo) las velas
    if mi == jc:
        txt = (f"{fmt_ny(ts[jc], '%H:%M')} la vela cierra {'bajo' if up else 'sobre'} la base del FVG ({base_fvg:,.2f}) → iFVG\n"
               f"y {'bajo' if up else 'sobre'} la apertura de la secuencia ({level:,.2f}) → CISD")
        ch.arrow(ch.X(ih) - 30, ty + (22 if up else -6), ch.X(jc) - 4, ch.Y(cy) + (-4 if up else 4), PURPLE)
        ch.text(ch.X(ih) - 36, ty, txt, PURPLE, 12, "700", "end")
    else:
        cm = bars["close"][mi]
        ch.arrow(ch.X(ih) - 30, ty + (22 if up else -6), ch.X(mi) - 3, ch.Y(cm) + (-4 if up else 4), PURPLE)
        ch.text(ch.X(ih) - 36, ty, f"{fmt_ny(ts[mi], '%H:%M')} cierra {'bajo' if up else 'sobre'} la base del FVG: iFVG", PURPLE, 12, "700", "end")
        ty2 = ty + (46 if up else -46)
        ch.arrow(ch.X(ih) - 30, ty2 + (22 if up else -6), ch.X(jc) - 3, ch.Y(cy) + (-4 if up else 4), PURPLE)
        ch.text(ch.X(ih) - 36, ty2, f"{fmt_ny(ts[jc], '%H:%M')} CISD: cierra {cy:,.2f}, {'bajo' if up else 'sobre'} {level:,.2f}", PURPLE, 12, "700", "end")
    ch.dot(jc, cy, PURPLE, 6)
    ch.arrow(ch.X(start) + 34, ch.Y(entry) + sgn_y * -40, ch.X(start) + 3, ch.Y(entry) + sgn_y * -4, BLUE)
    ch.text(ch.X(start) + 40, ch.Y(entry) + sgn_y * -50, f"{fmt_ny(ts[start], '%H:%M')} ENTRADA 1: a mercado en la\napertura de la vela siguiente\na la del CISD ({entry:,.2f})", BLUE, 12, "700")
    ch.dot(jx, px(res["exit_price"]), GREEN, 7)
    ch.text(ch.X(jx) - 8, ch.Y(px(res["exit_price"])) + (24 if up else -14), f"{fmt_ny(ts[jx], '%H:%M')} objetivo 2R", GREEN, 12, "700", "end")
    ch.text(ch.x0 + 14, ch.y0 + ch.h - 12, f"LTF M5 · {fmt_ny(ts[a], '%d/%m %H:%M')} – {fmt_ny(ts[b], '%d/%m %H:%M')} NY", MUTED, 12, "500")
    cards = [("Paso 3 · iFVG en M5", f"El tramo {'alcista' if up else 'bajista'} del sweep dejó un FVG {'alcista' if up else 'bajista'} en M5 (zona {min(f_bot, f_top):,.2f}–{max(f_bot, f_top):,.2f}). "
                                    f"La vela de las {fmt_ny(ts[mi], '%H:%M')} cierra {'bajo' if up else 'sobre'} su base ({base_fvg:,.2f}): el FVG se invierte (iFVG).", PURPLE),
             ("Paso 4 · CISD", f"La secuencia de velas {'alcistas' if up else 'bajistas'} que hizo el sweep abrió en {level:,.2f}. "
                               f"A las {fmt_ny(ts[jc], '%H:%M')} una vela cierra {'por debajo' if up else 'por encima'} ({cy:,.2f}): cambio de entrega. "
                               f"Se mide en el mismo TF (M5).", PURPLE),
             ("Paso 5 · entrada y gestión", f"Entrada 1 en M5: a mercado en {entry:,.2f}. Stop en el extremo del sweep ({hx:,.2f}), riesgo {risk:,.2f} pts. "
                                            f"TP 2R en {target:,.2f}; a 1R ({be:,.2f}) el stop pasa a la entrada. "
                                            f"Resultado: {res['cómo']}, {res['gross']:+.2f} R bruto ({res['gross'] - res['cost']:+.2f} R con spread).", BLUE)]
    (out / "3_entrada_ltf.svg").write_text(page("3 · LTF (M5): iFVG, CISD y entrada", head, ch, cards, 840), encoding="utf-8")
    print(f"escritos en {out}")
    if args.png:
        for svg in sorted(out.glob("*.svg")):
            height = 840 if svg.name.startswith("3") else 810
            subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{height}",
                            f"--screenshot={svg.with_suffix('.png')}", svg.resolve().as_uri()], check=True, capture_output=True)
        print("PNG listos")


if __name__ == "__main__":
    main()
