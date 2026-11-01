"""Dibuja un setup CRT del motor sobre velas reales, con sus pasos numerados: contexto en M15 (C1, C2, C3) y detalle en LTF.

Pasos (corto; el largo es el espejo): 1) C2 barre el máximo de C1 con una mecha (extremo del sweep); 2) tras el extremo nace un FVG de MTF y el
precio vuelve a él; 3) en LTF el tramo de vuelta deja un FVG que el precio invierte = CISD; 4) entrada con el stop en el extremo.
El dibujo sale del propio motor (tradingbot/skills/crt/engine.py): si el motor no da setup en esa C2, lo dice.

    uv run python scripts/dibujar_setup_c2.py --simbolo EURUSD --c2 "2026-10-28 01:00"
    uv run python scripts/dibujar_setup_c2.py --simbolo NAS100 --c2 "2026-10-14 06:00" --ltf 3 --entrada 4

Escribe docs/estrategia_crt/setup_c2_<simbolo>_<fecha>.svg y el PNG (con Chrome headless). `--c2` es la hora NY de inicio de C2.
"""
from __future__ import annotations

import argparse
import html
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import backtest_crt as bt                                                              # noqa: E402
from tradingbot.skills.crt import engine                                               # noqa: E402

AHEAD = 7 * 3600
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
GREEN, RED, AMBER, VIOLET, INK, MUTED = "#16a34a", "#dc2626", "#d97706", "#7c3aed", "#0f172a", "#475569"
W, H = 1100, 1480
X0, X1 = 70, 1060
ENTRY_NAMES = {1: "apertura de la vela siguiente al CISD", 2: "retesteo del iFVG", 3: "primera vela sin mecha", 4: "cierre de la vela del CISD"}


def ny(ts: int) -> pd.Timestamp:
    return pd.Timestamp(int(ts) - AHEAD, unit="s")


def agg(df: pd.DataFrame, minutes: int) -> pd.DataFrame:
    g = df.set_index("ny").resample(f"{minutes}min", label="left", closed="left")
    out = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(), "close": g["close"].last()}).dropna()
    return out.reset_index()


class Panel:
    """Un gráfico de velas con su escala: x en velas, y en precio."""

    def __init__(self, df: pd.DataFrame, y0: int, y1: int, lo: float, hi: float, ticks: int):
        self.df, self.y0, self.y1, self.lo, self.hi, self.n = df.reset_index(drop=True), y0, y1, lo, hi, len(df)
        self.parts = [f'<rect x="{X0}" y="{y0}" width="{X1 - X0}" height="{y1 - y0}" fill="white" stroke="#e5e7eb"/>']
        digits = 5 if hi < 10 else 2
        step = (hi - lo) / 6
        mag = 10 ** np.floor(np.log10(step))
        step = mag * min((1, 2, 5, 10), key=lambda k: abs(k * mag - step))
        for p in np.arange(np.ceil(lo / step) * step, hi, step):
            self.parts += [f'<line x1="{X0}" x2="{X1}" y1="{self.py(p):.1f}" y2="{self.py(p):.1f}" stroke="#eef0f3"/>',
                           f'<text x="{X0 - 6}" y="{self.py(p) + 4:.1f}" font-size="10" text-anchor="end" fill="{MUTED}">{p:.{digits}f}</text>']
        every = max(self.n // ticks, 1)
        for k in range(0, self.n, every):
            self.parts.append(f'<text x="{self.px(k):.1f}" y="{y1 + 15}" font-size="10" text-anchor="middle" fill="{MUTED}">{self.df.ny[k]:%d/%m %H:%M}</text>')
        bw = (X1 - X0) / self.n * 0.65
        for i, r in self.df.iterrows():
            col = GREEN if r.close >= r.open else RED
            self.parts += [f'<line x1="{self.px(i):.1f}" x2="{self.px(i):.1f}" y1="{self.py(r.high):.1f}" y2="{self.py(r.low):.1f}" stroke="{col}"/>',
                           f'<rect x="{self.px(i) - bw / 2:.1f}" y="{self.py(max(r.open, r.close)):.1f}" width="{bw:.1f}" '
                           f'height="{max(abs(self.py(r.open) - self.py(r.close)), 1):.1f}" fill="{col}"/>']

    def px(self, i: float) -> float:
        return X0 + (i + 0.5) * (X1 - X0) / self.n

    def py(self, p: float) -> float:
        return self.y1 - (p - self.lo) / (self.hi - self.lo) * (self.y1 - self.y0)

    def idx(self, t: pd.Timestamp) -> float:
        """Índice de la vela que contiene la hora `t` (acotado a los bordes)."""
        k = int(np.searchsorted(self.df.ny.to_numpy(), np.datetime64(t), "right")) - 1
        return float(min(max(k, 0), self.n - 1))

    def text(self, x: float, y: float, s: str, color: str, size: int = 11, anchor: str = "start", bold: bool = False) -> None:
        w = ' font-weight="700"' if bold else ""
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}"{w} text-anchor="{anchor}" fill="{color}">{html.escape(s)}</text>')

    def hline(self, p: float, color: str, dash: str = "", x_from: float | None = None, width: float = 1.0) -> None:
        d = f' stroke-dasharray="{dash}"' if dash else ""
        xa = X0 if x_from is None else x_from
        self.parts.append(f'<line x1="{xa:.1f}" x2="{X1}" y1="{self.py(p):.1f}" y2="{self.py(p):.1f}" stroke="{color}" stroke-width="{width}"{d}/>')

    def box(self, a: float, b: float, lo: float, hi: float, color: str, opacity: float, dash: str = "") -> None:
        d = f' stroke-dasharray="{dash}"' if dash else ""
        lo, hi = max(lo, self.lo), min(hi, self.hi)                                 # recortado a la escala del gráfico
        left = self.px(a) - (X1 - X0) / self.n / 2
        self.parts.append(f'<rect x="{left:.1f}" y="{self.py(hi):.1f}" width="{max(self.px(b) - left, 2):.1f}" '
                          f'height="{max(self.py(lo) - self.py(hi), 1):.1f}" fill="{color}" fill-opacity="{opacity}" stroke="{color}"{d}/>')

    def dot(self, x: float, p: float, color: str, r: int = 6, fill: bool = False) -> None:
        f = color if fill else "none"
        self.parts.append(f'<circle cx="{self.px(x):.1f}" cy="{self.py(p):.1f}" r="{r}" fill="{f}" stroke="{color}" stroke-width="2"/>')


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--simbolo", default="EURUSD", help="EURUSD, GBPUSD (H4) o NAS100 (H3); PUPrime")
    ap.add_argument("--c2", required=True, help="inicio de C2, hora NY (AAAA-MM-DD HH:MM)")
    ap.add_argument("--ltf", type=int, choices=(1, 3, 5), default=5)
    ap.add_argument("--entrada", type=int, choices=(1, 2, 3, 4), default=1)
    args = ap.parse_args()
    want = args.simbolo.upper()
    forex = want in ("EURUSD", "GBPUSD")
    mk = bt.configure("forex" if forex else "indices")
    cfg, htf_min = bt.CFG, mk["htf_min"]
    _, base = pd.read_pickle(bt.cache_path("puprime", want, 5))
    _, ltf = pd.read_pickle(bt.cache_path("puprime", want, args.ltf))
    c2_ts = int(pd.Timestamp(args.c2).timestamp()) + AHEAD
    base = base[base.ts >= c2_ts - 14 * 86400].reset_index(drop=True)
    ltf = ltf[ltf.ts >= c2_ts - 14 * 86400].reset_index(drop=True)
    setups, _ = engine.find_setups(base, ltf, args.ltf, engine.Rule(), cfg)
    found = [s for s in setups if s["C2"] == c2_ts]
    if not found:
        print(f"el motor no da ningún setup en la C2 de {args.c2} NY ({want})")
        return
    st = found[0]
    sgn = st["sign"]
    L = engine.view(ltf, sgn)
    ep = engine.entry_point(L, st, args.entrada, args.ltf, engine.Rule(), cfg)
    res = engine.manage(L, st, ep, engine.Rule()) if ep else None
    ts = ltf.ts.to_numpy()
    stop = sgn * st["stop"]
    t_ext, t_touch, t_cisd = ny(ts[st["ih"]]), ny(ts[st["jt"]]), ny(ts[st["jc"]])
    f_bot, f_top = sorted((sgn * st["z_bottom"], sgn * st["z_top"]))
    t_f0, t_f2 = ny(ts[st["kf"] - 2]), ny(ts[st["kf"]])
    c1_lo, c1_hi = sorted((sgn * st["c1"][0], sgn * st["c1"][1]))
    zones = [(m, *sorted((sgn * b, sgn * t)), ny(fm)) for m, b, t, fm in st["zones"]]
    entry = sgn * ep["entry"] if ep else None
    risk = ep["risk"] if ep else None
    target = sgn * res["target"] if res else None
    t_in = ny(ts[ep["start"]]) if ep else None
    t_out = ny(ts[res["exit_index"]]) if res else None

    base["ny"] = pd.to_datetime(base.ts - AHEAD, unit="s")
    ltf["ny"] = pd.to_datetime(ltf.ts - AHEAD, unit="s")
    t_c2 = ny(c2_ts)
    t_c1, t_c3, t_end = t_c2 - pd.Timedelta(minutes=htf_min), t_c2 + pd.Timedelta(minutes=htf_min), t_c2 + pd.Timedelta(minutes=2 * htf_min)
    d15 = agg(base[(base.ny >= t_c1) & (base.ny < t_end)], 15)
    z0 = min(t_ext, t_f0) - pd.Timedelta(minutes=45)
    z1 = min(max([t for t in (t_in, t_out) if t is not None] + [t_cisd]) + pd.Timedelta(minutes=45), t_end)
    zoom = ltf[(ltf.ny >= z0) & (ltf.ny <= z1)].iloc[:160].reset_index(drop=True)
    unit, pips, dec = (1e-4, "pips", 5) if forex else (1.0, "pts", 2)

    def rng(df: pd.DataFrame, extra: list[float]) -> tuple[float, float]:
        lo, hi = min(df.low.min(), *extra), max(df.high.max(), *extra)
        pad = (hi - lo) * 0.08
        return lo - pad, hi + pad

    p1 = Panel(d15, 100, 400, *rng(d15, [c1_lo, c1_hi, stop]), ticks=12)
    for (a, b), fill, nm in (((t_c1, t_c2), "#e2e8f0", "C1"), ((t_c2, t_c3), "#fde68a", "C2"), ((t_c3, t_end), "#bbf7d0", "C3")):
        xa = X0 + p1.idx(a) * (X1 - X0) / p1.n
        xb = X1 if b == t_end else X0 + (p1.idx(b)) * (X1 - X0) / p1.n
        p1.parts.insert(1, f'<rect x="{xa:.1f}" y="100" width="{xb - xa:.1f}" height="300" fill="{fill}" opacity="0.35"/>')
        p1.parts.append(f'<text x="{(xa + xb) / 2:.1f}" y="94" font-size="14" font-weight="700" text-anchor="middle" fill="{INK}">{nm}</text>')
    swept, opp = (c1_hi, c1_lo) if sgn > 0 else (c1_lo, c1_hi)
    p1.hline(swept, RED, "6 4")
    p1.text(X0 + 4, p1.py(swept) + (13 if sgn < 0 else -5), f"{'máximo' if sgn > 0 else 'mínimo'} de C1 {swept:.{dec}f} (lo barre C2)", RED)
    p1.hline(opp, GREEN, "6 4")
    p1.text(X1 - 4, p1.py(opp) + (13 if sgn > 0 else -5), f"{'mínimo' if sgn > 0 else 'máximo'} de C1 {opp:.{dec}f}", GREEN, anchor="end")
    p1.dot(p1.idx(t_ext), stop, RED, 7)
    p1.text(p1.px(p1.idx(t_ext)) + 12, p1.py(stop) + (-8 if sgn > 0 else 14), f"① sweep {stop:.{dec}f}", RED, 12, bold=True)
    for m, lo_z, hi_z, fm in zones:
        a = p1.idx(fm - pd.Timedelta(minutes=3 * m))
        p1.box(a, min(a + 8, p1.n - 1), lo_z, hi_z, AMBER, 0.4)
        p1.text(p1.px(a), p1.py(lo_z if sgn > 0 else hi_z) + (14 if sgn > 0 else -6), f"② FVG M{m} {lo_z:.{dec}f}–{hi_z:.{dec}f}", AMBER, 12, bold=True)

    p2 = Panel(zoom, 500, 860, *rng(zoom, [stop] + ([entry] if entry else [])), ticks=12)
    p2.text(X0, 492, f"M{args.ltf}: el mismo tramo, ampliado", INK, 13, bold=True)
    for m, lo_z, hi_z, fm in zones:
        p2.box(p2.idx(fm - pd.Timedelta(minutes=m)), p2.n - 1, lo_z, hi_z, AMBER, 0.15, "4 3")
    p2.box(p2.idx(t_f0), p2.idx(t_cisd), f_bot, f_top, VIOLET, 0.3, "4 3")
    p2.text(p2.px(p2.idx(t_f0)) - 4, p2.py(f_top) - 8, f"③ iFVG {f_bot:.{dec}f}–{f_top:.{dec}f}", VIOLET, anchor="end")
    close_cisd = float(ltf.loc[ltf.ny == t_cisd, "close"].iloc[0])
    p2.dot(p2.idx(t_cisd), close_cisd, VIOLET)
    p2.text(p2.px(p2.idx(t_cisd)) + 8, p2.py(close_cisd) - 10, f"CISD {t_cisd:%H:%M}", VIOLET)
    p2.dot(p2.idx(t_ext), stop, RED, 6)
    p2.hline(stop, RED, width=1.3)
    p2.text(X1 - 4, p2.py(stop) + (-5 if sgn > 0 else 14), f"SL {stop:.{dec}f}", RED, anchor="end")
    if ep:
        xi = p2.px(p2.idx(t_in))
        p2.hline(entry, INK, x_from=xi, width=1.3)
        p2.dot(p2.idx(t_in), entry, INK, 5, True)
        p2.text(xi + 8, p2.py(entry) + (16 if sgn > 0 else -8), f"④ entrada {entry:.{dec}f} ({t_in:%H:%M})", INK, 12, bold=True)
        if p2.lo <= target <= p2.hi:
            p2.hline(target, GREEN, "6 3", x_from=xi)
            p2.text(X1 - 4, p2.py(target) - 5, f"TP 2R {target:.{dec}f}", GREEN, anchor="end")
    # ---- detalle: la creación del iFVG y del CISD tras el toque (sin los 90 minutos de relleno del gráfico anterior) ----
    det = ltf[(ltf.ny >= t_touch - pd.Timedelta(minutes=40)) & (ltf.ny <= (t_in or t_cisd) + pd.Timedelta(minutes=45))].iloc[:90]
    zl = [lo_z if sgn > 0 else hi_z for _, lo_z, hi_z, _ in zones]
    p3 = Panel(det, 940, 1205, *rng(det, [f_bot, f_top] + zl + ([entry] if entry else [])), ticks=12)
    p3.text(X0, 932, f"Detalle en M{args.ltf}: toque del FVG de MTF → iFVG → CISD → entrada", INK, 13, bold=True)
    for m, lo_z, hi_z, fm in zones:
        p3.box(0, p3.n - 1, lo_z, hi_z, AMBER, 0.15, "4 3")
    p3.parts.append(f'<line x1="{p3.px(p3.idx(t_touch)):.1f}" x2="{p3.px(p3.idx(t_touch)):.1f}" y1="940" y2="1205" stroke="{AMBER}" stroke-dasharray="3 3"/>')
    p3.text(p3.px(p3.idx(t_touch)) + 4, 954, f"toque del FVG de MTF {t_touch:%H:%M}", AMBER, 12, bold=True)
    p3.box(p3.idx(t_f0), p3.idx(t_cisd), f_bot, f_top, VIOLET, 0.35, "4 3")
    for k, (tt, lab) in enumerate(((t_f0, "1"), (t_f0 + (t_f2 - t_f0) / 2, "2"), (t_f2, "3"))):
        j = p3.idx(tt)
        p3.text(p3.px(j), p3.py(f_top) + (-8 if sgn > 0 else 16) - 14 * 0, lab, VIOLET, 12, "middle", True)
    p3.text(X0 + 8, 1236 - 4, f"③ iFVG de M{args.ltf}: hueco entre las velas 1 y 3 ({t_f0:%H:%M}–{t_f2:%H:%M}) = {f_bot:.{dec}f}–{f_top:.{dec}f} ({(f_top - f_bot) / unit:.1f} {pips})", VIOLET, 12, bold=True)
    p3.hline(f_bot, VIOLET, "2 3")
    p3.dot(p3.idx(t_cisd), close_cisd, VIOLET, 7)
    p3.text(p3.px(p3.idx(t_cisd)) - 8, p3.py(close_cisd) + 34, f"cierre {close_cisd:.{dec}f} bajo la base {f_bot:.{dec}f} = inversión = CISD ({t_cisd:%H:%M})", VIOLET, 12, "end", True)
    if ep:
        xi = p3.px(p3.idx(t_in))
        p3.hline(entry, INK, x_from=xi, width=1.3)
        p3.dot(p3.idx(t_in), entry, INK, 5, True)
        p3.text(xi + 10, p3.py(entry) + 16, f"④ entrada {entry:.{dec}f} ({t_in:%H:%M})", INK, 12, bold=True)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">',
           f'<rect width="{W}" height="{H}" fill="white"/>',
           f'<text x="{X0}" y="34" font-size="20" font-weight="700" fill="{INK}">{want} · {t_c2:%d/%m/%Y} · setup dentro de C2 '
           f'({"largo" if sgn < 0 else "corto"}) · {ENTRY_NAMES[args.entrada]}</text>',
           f'<text x="{X0}" y="58" font-size="13" fill="{MUTED}">Hora de Nueva York. Arriba el contexto en M15 (C1, C2, C3); '
           f'abajo el tramo del setup en M{args.ltf}.</text>'] + p1.parts + p2.parts + p3.parts
    ty = 1262
    lines = [("El setup, paso a paso", True),
             (f"① C2 ({t_c2:%H:%M}) barre el {'máximo' if sgn > 0 else 'mínimo'} de C1 ({swept:.{dec}f}); el extremo es {stop:.{dec}f} "
              f"a las {t_ext:%H:%M} ({abs(stop - swept) / unit:.1f} {pips} más allá).", False),
             ("② FVG de MTF nacido tras el extremo: " + "; ".join(f"M{m} {lo_z:.{dec}f}–{hi_z:.{dec}f} (formado a las {fm:%H:%M})"
                                                                  for m, lo_z, hi_z, fm in zones)
              + f". El precio vuelve a él a las {t_touch:%H:%M}.", False),
             (f"③ iFVG de M{args.ltf} {f_bot:.{dec}f}–{f_top:.{dec}f} (velas {t_f0:%H:%M}–{t_f2:%H:%M}); se invierte con el cierre de las "
              f"{t_cisd:%H:%M}: CISD.", False)]
    if ep:
        lines.append((f"④ Entrada a {entry:.{dec}f} a las {t_in:%H:%M}, stop en {stop:.{dec}f}: riesgo {risk / unit:.1f} {pips}. "
                      f"Con TP 2R y BE a 1R: «{res['cómo']}» a las {t_out:%d/%m %H:%M}, {res['gross']:+.2f} R bruto.", False))
    else:
        lines.append(("④ No hay entrada con ese modelo dentro de C2.", False))
    lines.append((f"Desde la vuelta al FVG hasta el CISD pasan {int((t_cisd - t_touch).total_seconds() // 60)} min; "
                  f"desde el extremo hasta el CISD, {int((t_cisd - t_ext).total_seconds() // 60)} min.", False))
    for text, bold in lines:
        attrs = 'font-size="15" font-weight="700"' if bold else 'font-size="13"'
        out.append(f'<text x="{X0}" y="{ty}" {attrs} fill="{INK}">{html.escape(text)}</text>')
        ty += 28 if bold else 23
    out.append("</svg>")
    svg = ROOT / "docs" / "estrategia_crt" / f"setup_c2_{want.lower()}_{t_c2:%Y-%m-%d_%H%M}.svg"
    svg.write_text("\n".join(out), encoding="utf-8")
    png = svg.with_suffix(".png")
    subprocess.run([CHROME, "--headless", "--disable-gpu", f"--screenshot={png}", f"--window-size={W},{H}",
                    "--default-background-color=FFFFFFFF", svg.as_uri()], check=True, capture_output=True)
    print(png)


if __name__ == "__main__":
    main()
