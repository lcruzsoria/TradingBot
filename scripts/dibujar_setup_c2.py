"""Dibuja el setup CRT definido DENTRO de C2 sobre velas reales: EURUSD, 28/10/2026 (H4: C1 21:00, C2 01:00, C3 05:00, hora de Nueva York).

Pasos del setup (largo): 1) C2 barre el mínimo de C1 con una mecha; 2) el desplazamiento deja un FVG alcista de MTF (M15) y el precio vuelve a él;
3) en LTF (M5/M3/M1) el retroceso deja un FVG bajista que el precio invierte (cierre por encima) = CISD; 4) entrada en largo con el stop en el
mínimo de la mecha. Escribe docs/estrategia_crt/setup_c2_2026-10-28.svg y el PNG (con Chrome headless).

    uv run python scripts/dibujar_setup_c2.py
"""
from __future__ import annotations

import html
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from backtest_crt import cache_path                                                    # noqa: E402
from tradingbot.skills.crt import engine                                               # noqa: E402

AHEAD = 7 * 3600
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
GREEN, RED, AMBER, VIOLET, BLUE, INK, MUTED = "#16a34a", "#dc2626", "#d97706", "#7c3aed", "#2563eb", "#0f172a", "#475569"
W, H = 1100, 1130
X0, X1 = 70, 1060


def candles(tf: int, a: str, b: str) -> pd.DataFrame:
    _, df = pd.read_pickle(cache_path("puprime", "EURUSD", tf))
    df["ny"] = pd.to_datetime(df["ts"] - AHEAD, unit="s")
    return df[(df.ny >= a) & (df.ny < b)].reset_index(drop=True)


def main() -> None:
    m5 = candles(5, "2026-10-27 21:00", "2026-10-28 17:00")
    d = m5[(m5.ny >= "2026-10-27 21:00") & (m5.ny < "2026-10-28 09:00")]
    d15 = d.groupby(d.ny.dt.floor("15min")).agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"))
    d15 = d15.rename_axis("ny").reset_index()
    c1 = d15[:16]
    c1l, c1h = c1.low.min(), c1.high.max()
    low = d15[16:32].low.min()
    i_low = int(d15[16:32].low.idxmin())
    zb, zt = 1.1116, 1.11195                                                            # FVG alcista de M15 (formado a las 03:45)
    # --- el setup en M5: FVG bajista del retroceso (03:40-03:50) y su inversión (cierre por encima) ---
    t5 = m5.set_index("ny")
    gap_top, gap_bot = float(t5.loc["2026-10-28 03:40", "low"]), float(t5.loc["2026-10-28 03:50", "high"])
    inv = t5[(t5.index > "2026-10-28 03:50") & (t5.close > gap_top)].index[0]
    entry_bar = t5.index[t5.index.get_loc(inv) + 1]
    entry = float(t5.loc[entry_bar, "open"])
    risk = entry - low
    # gestión con el motor (largo = corto con los precios cambiados): objetivo 2R, BE a 1R, cierre a las 17:00 NY
    L = engine.view(m5, -1)
    start = int(m5.index[m5.ny == entry_bar][0])
    end = int(m5.ts.iloc[-1]) + 300
    res = engine.manage(L, {"stop": -low, "c1": (-c1h, -c1l)}, {"entry": -entry, "start": start, "fill": None, "risk": risk, "end": end},
                        engine.Rule(rr=2.0, be_at=1.0))
    tp = entry + 2 * risk
    exit_time = m5.ny[res["exit_index"]]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">',
           f'<rect width="{W}" height="{H}" fill="white"/>',
           f'<text x="{X0}" y="34" font-size="20" font-weight="700" fill="{INK}">EURUSD · 28/10/2026 · el setup dentro de C2 (largo)</text>',
           f'<text x="{X0}" y="58" font-size="13" fill="{MUTED}">Hora de Nueva York. Arriba el contexto en M15; abajo el mismo tramo en M5, donde se ve el iFVG y la entrada.</text>']

    def panel(df: pd.DataFrame, y0: int, y1: int, lo: float, hi: float, per_hour: int, t0: pd.Timestamp):
        n = len(df)

        def px(i: float) -> float:
            return X0 + (i + 0.5) * (X1 - X0) / n

        def py(p: float) -> float:
            return y1 - (p - lo) / (hi - lo) * (y1 - y0)

        def pi(ts: pd.Timestamp) -> float:                                              # índice (fraccionario) de una hora
            return float(df.index[df.ny >= ts][0]) if (df.ny >= ts).any() else n

        bw = (X1 - X0) / n * 0.65
        g = [f'<rect x="{X0}" y="{y0}" width="{X1 - X0}" height="{y1 - y0}" fill="white" stroke="#e5e7eb"/>']
        for p in np.arange(np.ceil(lo * 2000) / 2000, hi, 0.0005):
            g += [f'<line x1="{X0}" x2="{X1}" y1="{py(p):.1f}" y2="{py(p):.1f}" stroke="#eef0f3"/>',
                  f'<text x="{X0 - 6}" y="{py(p) + 4:.1f}" font-size="10" text-anchor="end" fill="{MUTED}">{p:.4f}</text>']
        for k in range(0, n, per_hour):
            g.append(f'<text x="{X0 + k * (X1 - X0) / n:.1f}" y="{y1 + 15}" font-size="10" text-anchor="middle" fill="{MUTED}">{df.ny[k]:%H:%M}</text>')
        return g, px, py, pi, bw

    def draw_candles(g, df, px, py, bw):
        for i, r in df.iterrows():
            col = GREEN if r.close >= r.open else RED
            g += [f'<line x1="{px(i):.1f}" x2="{px(i):.1f}" y1="{py(r.high):.1f}" y2="{py(r.low):.1f}" stroke="{col}"/>',
                  f'<rect x="{px(i) - bw / 2:.1f}" y="{py(max(r.open, r.close)):.1f}" width="{bw:.1f}" '
                  f'height="{max(abs(py(r.open) - py(r.close)), 1):.1f}" fill="{col}"/>']

    # ---------------- panel 1: M15 ----------------
    Y0a, Y1a = 100, 400
    g, px, py, pi, bw = panel(d15, Y0a, Y1a, 1.1110, 1.1140, 4, d15.ny[0])
    for (a, b), fill, name in (((0, 16), "#e2e8f0", "C1 · rango (21:00)"), ((16, 32), "#fde68a", "C2 · manipulación (01:00)"),
                               ((32, 48), "#bbf7d0", "C3 · expansión (05:00)")):
        xa, xb = X0 + a * (X1 - X0) / 48, X0 + b * (X1 - X0) / 48
        g += [f'<rect x="{xa:.1f}" y="{Y0a}" width="{xb - xa:.1f}" height="{Y1a - Y0a}" fill="{fill}" opacity="0.35"/>',
              f'<text x="{(xa + xb) / 2:.1f}" y="{Y0a - 6}" font-size="13" font-weight="700" text-anchor="middle" fill="{INK}">{name}</text>']
    draw_candles(g, d15, px, py, bw)
    g += [f'<line x1="{X0}" x2="{X1}" y1="{py(c1l):.1f}" y2="{py(c1l):.1f}" stroke="{RED}" stroke-dasharray="6 4"/>',
          f'<text x="{X0 + 4}" y="{py(c1l) + 13:.1f}" font-size="11" fill="{RED}">mínimo de C1 {c1l:.5f}</text>',
          f'<line x1="{X0}" x2="{X1}" y1="{py(c1h):.1f}" y2="{py(c1h):.1f}" stroke="{GREEN}" stroke-dasharray="6 4"/>',
          f'<text x="{X1 - 4}" y="{py(c1h) - 5:.1f}" font-size="11" text-anchor="end" fill="{GREEN}">máximo de C1 {c1h:.5f}</text>',
          f'<circle cx="{px(i_low):.1f}" cy="{py(low):.1f}" r="7" fill="none" stroke="{RED}" stroke-width="2"/>',
          f'<text x="{px(i_low) + 12:.1f}" y="{py(low) + 4:.1f}" font-size="12" font-weight="700" fill="{RED}">① sweep {low:.5f}</text>']
    f0 = int(d15.index[d15.ny == "2026-10-28 03:00"][0])
    g += [f'<rect x="{px(f0):.1f}" y="{py(zt):.1f}" width="{px(f0 + 8) - px(f0):.1f}" height="{py(zb) - py(zt):.1f}" fill="{AMBER}" opacity="0.4" '
          f'stroke="{AMBER}"/>',
          f'<text x="{px(f0 + 1):.1f}" y="{py(zb) + 14:.1f}" font-size="12" font-weight="700" fill="{AMBER}">② FVG alcista M15 {zb:.4f}–{zt:.5f}</text>']
    out += g

    # ---------------- panel 2: M5 ----------------
    z = m5[(m5.ny >= "2026-10-28 03:00") & (m5.ny < "2026-10-28 09:00")].reset_index(drop=True)
    Y0b, Y1b = 500, 860
    g, px, py, pi, bw = panel(z, Y0b, Y1b, 1.1110, 1.1145, 12, z.ny[0])
    n = len(z)
    g += [f'<text x="{X0}" y="{Y0b - 8}" font-size="13" font-weight="700" fill="{INK}">M5: el mismo tramo (03:00–09:00), dentro de C2 y C3</text>',
          f'<rect x="{X0 + pi(pd.Timestamp("2026-10-28 05:00")) * (X1 - X0) / n:.1f}" y="{Y0b}" '
          f'width="{(X1 - X0) - pi(pd.Timestamp("2026-10-28 05:00")) * (X1 - X0) / n:.1f}" height="{Y1b - Y0b}" fill="#bbf7d0" opacity="0.3"/>',
          f'<text x="{X1 - 6}" y="{Y0b + 16}" font-size="12" text-anchor="end" fill="{MUTED}">C3 (desde las 05:00)</text>']
    draw_candles(g, z, px, py, bw)
    j_in, j_gap0, j_gap1, j_inv, j_ent = (pi(pd.Timestamp(t)) for t in ("2026-10-28 03:45", "2026-10-28 03:40", "2026-10-28 03:55", inv, entry_bar))
    g += [f'<rect x="{px(j_in):.1f}" y="{py(zt):.1f}" width="{px(n - 1) - px(j_in):.1f}" height="{py(zb) - py(zt):.1f}" fill="{AMBER}" opacity="0.18" '
          f'stroke="{AMBER}" stroke-dasharray="4 3"/>',
          f'<text x="{px(j_in) + 4:.1f}" y="{py(zb) + 13:.1f}" font-size="11" fill="{AMBER}">FVG M15 {zb:.4f}–{zt:.5f}: el precio vuelve (03:45–03:50)</text>',
          f'<rect x="{px(j_gap0):.1f}" y="{py(gap_top):.1f}" width="{px(j_inv) - px(j_gap0):.1f}" height="{py(gap_bot) - py(gap_top):.1f}" '
          f'fill="{VIOLET}" opacity="0.35" stroke="{VIOLET}" stroke-dasharray="4 3"/>',
          f'<line x1="{px(j_gap0):.1f}" x2="{px(j_gap0):.1f}" y1="{py(gap_top):.1f}" y2="{py(1.1139):.1f}" stroke="{VIOLET}" stroke-dasharray="2 3"/>',
          f'<text x="{px(j_gap0) - 4:.1f}" y="{py(1.1139) - 2:.1f}" font-size="11" fill="{VIOLET}">③ iFVG: FVG bajista {gap_bot:.5f}–{gap_top:.5f}</text>',
          f'<circle cx="{px(j_inv):.1f}" cy="{py(float(t5.loc[inv, "close"])):.1f}" r="6" fill="none" stroke="{VIOLET}" stroke-width="2"/>',
          f'<line x1="{px(j_inv):.1f}" x2="{px(j_inv):.1f}" y1="{py(float(t5.loc[inv, "close"])) - 6:.1f}" y2="{py(1.1135):.1f}" stroke="{VIOLET}" stroke-dasharray="2 3"/>',
          f'<text x="{px(j_inv) + 4:.1f}" y="{py(1.1135) - 2:.1f}" font-size="11" fill="{VIOLET}">cierra por encima = inversión (CISD) {inv:%H:%M}</text>']
    xs = px(j_ent)
    g += [f'<line x1="{xs:.1f}" x2="{X1}" y1="{py(entry):.1f}" y2="{py(entry):.1f}" stroke="{INK}" stroke-width="1.3"/>',
          f'<circle cx="{xs:.1f}" cy="{py(entry):.1f}" r="5" fill="{INK}"/>',
          f'<text x="{xs + 8:.1f}" y="{py(entry) + 16:.1f}" font-size="12" font-weight="700" fill="{INK}">④ entrada {entry:.5f} ({entry_bar:%H:%M})</text>',
          f'<line x1="{xs:.1f}" x2="{X1}" y1="{py(low):.1f}" y2="{py(low):.1f}" stroke="{RED}" stroke-width="1.4"/>',
          f'<text x="{X1 - 4}" y="{py(low) + 14:.1f}" font-size="11" text-anchor="end" fill="{RED}">SL {low:.5f} (mínimo de la mecha) · riesgo {risk * 1e4:.1f} pips</text>',
          f'<line x1="{xs:.1f}" x2="{X1}" y1="{py(min(tp, 1.1144)):.1f}" y2="{py(min(tp, 1.1144)):.1f}" stroke="{GREEN}" stroke-width="1.2" stroke-dasharray="6 3"/>',
          f'<text x="{X1 - 4}" y="{py(min(tp, 1.1144)) - 5:.1f}" font-size="11" text-anchor="end" fill="{GREEN}">TP 2R {tp:.5f}</text>',
          f'<line x1="{X0}" x2="{X1}" y1="{py(c1h):.1f}" y2="{py(c1h):.1f}" stroke="{GREEN}" stroke-dasharray="2 4" opacity="0.7"/>',
          f'<text x="{X1 - 4}" y="{py(c1h) - 5:.1f}" font-size="11" text-anchor="end" fill="{GREEN}">máximo de C1 {c1h:.5f} ({(c1h - entry) / risk:.2f} R desde la entrada)</text>']
    out += g
    # ---------------- texto ----------------
    ty = Y1b + 52
    ltf = {}
    for tf in (3, 1):
        x = candles(tf, "2026-10-28 03:30", "2026-10-28 06:00")
        ltf[tf] = x
    lines = [("El setup, paso a paso", True),
             (f"① C2 (01:00) barre el mínimo de C1 ({c1l:.5f}) con una mecha hasta {low:.5f} ({(c1l - low) * 1e4:.1f} pips).", False),
             (f"② El desplazamiento alcista deja un FVG de M15 en {zb:.4f}–{zt:.5f} (se forma a las 03:45). El precio vuelve a él entre las 03:45 y las 03:50.", False),
             (f"③ En M5 el retroceso deja un FVG bajista {gap_bot:.5f}–{gap_top:.5f}; a las {inv:%H:%M} una vela cierra por encima ({float(t5.loc[inv, 'close']):.5f}): "
              "el FVG se invierte = CISD.", False),
             (f"④ Entrada en largo a {entry:.5f} (apertura de la vela siguiente), stop en {low:.5f}. Riesgo {risk * 1e4:.1f} pips, TP 2R en {tp:.5f}.", False),
             (f"Con la gestión del bot (TP 2R, BE a 1R): resultado «{res['cómo']}» a las {exit_time:%d/%m %H:%M}, {res['gross']:+.2f} R bruto.", False),
             ("Se repite en M3 (inversión 03:57) y M1 (03:55–03:59, según el FVG bajista elegido). El máximo de C1 queda a solo "
              f"{(c1h - entry) / risk:.2f} R de la entrada.", False),
             ("Diferencia con el motor actual: ahí el extremo del sweep tenía que tocar un FVG ya existente; aquí el FVG nace del propio desplazamiento "
              "y el precio vuelve a él.", False)]
    for text, bold in lines:
        attrs = 'font-size="15" font-weight="700"' if bold else 'font-size="13"'
        out.append(f'<text x="{X0}" y="{ty}" {attrs} fill="{INK}">{html.escape(text)}</text>')
        ty += 28 if bold else 23
    out.append("</svg>")
    svg = ROOT / "docs" / "estrategia_crt" / "setup_c2_2026-10-28.svg"
    svg.write_text("\n".join(out), encoding="utf-8")
    png = svg.with_suffix(".png")
    subprocess.run([CHROME, "--headless", "--disable-gpu", f"--screenshot={png}", f"--window-size={W},{H}",
                    "--default-background-color=FFFFFFFF", svg.as_uri()], check=True, capture_output=True)
    print(png, f"entrada {entry:.5f} riesgo {risk * 1e4:.1f} pips, {res['cómo']} {res['gross']:+.2f}R {exit_time}")


if __name__ == "__main__":
    main()
