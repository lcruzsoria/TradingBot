"""Dibuja sobre velas reales el patrón de entrada propuesto por el usuario (sin iFVG): corto (el largo es el espejo).

1) C2 supera el nivel de C1 y marca un máximo (extremo del sweep); 2) la vela siguiente deja un FVG bajista en LTF (velas máximo, siguiente, siguiente+1);
3) el precio cierra por debajo del nivel de C1; 4) vuelve a tocar el FVG (vela de retesteo); 5) entrada al cierre de la primera vela que cierra por
debajo del mínimo de la vela de retesteo. Stop en el máximo, TP 2R.

    uv run python scripts/dibujar_patron_m3.py --simbolo EURUSD --c2 "2026-10-30 05:00" --ltf 3
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
import dibujar_setup_c2 as ds                                                          # noqa: E402

AHEAD, CHROME = ds.AHEAD, ds.CHROME
GREEN, RED, AMBER, INK, MUTED = ds.GREEN, ds.RED, ds.AMBER, ds.INK, ds.MUTED
W, H = 1100, 760


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--simbolo", default="EURUSD")
    ap.add_argument("--c2", required=True, help="inicio de C2, hora NY (AAAA-MM-DD HH:MM)")
    ap.add_argument("--ltf", type=int, choices=(3, 5), default=3)
    ap.add_argument("--hasta", type=int, default=0, help="minutos a mostrar tras la entrada (0 = hasta el cierre del trade)")
    args = ap.parse_args()
    want = args.simbolo.upper()
    forex = want in ("EURUSD", "GBPUSD")
    mk = bt.configure("forex" if forex else "indices")
    cfg, htf_min = bt.CFG, mk["htf_min"]
    _, base = pd.read_pickle(bt.cache_path("puprime", want, 5))
    _, df = pd.read_pickle(bt.cache_path("puprime", want, args.ltf))
    c2_ts = int(pd.Timestamp(args.c2).timestamp()) + AHEAD
    df = df[df.ts >= c2_ts - 2 * htf_min * 60].reset_index(drop=True)
    base = base[base.ts >= c2_ts - 2 * htf_min * 60].reset_index(drop=True)
    htf = bt.engine.aggregate(base, cfg.htf_min, cfg, cfg.origin)
    k = int(np.nonzero(htf.ts.to_numpy() == c2_ts)[0][0])
    c1h_r, c1l_r = htf.high.iloc[k - 1], htf.low.iloc[k - 1]
    sgn = 1 if htf.high.iloc[k] > c1h_r else -1                    # corto si C2 barrió el máximo (el largo es el espejo)
    L = bt.engine.view(df, sgn)
    ts, o, h, l, c = L["ts"], L["open"], L["high"], L["low"], L["close"]
    c1h, c1l = (c1h_r, c1l_r) if sgn > 0 else (-c1l_r, -c1h_r)
    a, b = np.searchsorted(ts, [c2_ts, c2_ts + htf_min * 60])
    s0 = a + int(np.argmax(h[a:b] > c1h))
    ext, ie, below, fvg, touch, ent = -np.inf, s0, None, None, None, None
    for j in range(s0, b):
        if h[j] > ext:                                              # máximo nuevo: se reinicia
            ext, ie, below, fvg, touch = h[j], j, None, None, None
            continue
        if fvg is None and j >= ie + 2 and l[ie] > h[j] and j == ie + 2:
            fvg = (h[j], l[ie], j)                                  # (base, techo, vela 3)
        if fvg and below is None and j > fvg[2] and c[j] < c1h:
            below = j
        if fvg and below is not None and touch is None and j > below and h[j] >= fvg[0]:
            touch = j
        elif touch is not None and ent is None and j > touch and c[j] < l[touch]:
            ent = j
            break
    if ent is None:
        print("el patrón no se completa en esa C2")
        return
    entry, stop = c[ent], ext
    risk = stop - entry
    target = entry - 2 * risk
    end = bt.engine.session_end(int(ts[ent]), cfg)
    x = ent + 1
    out_i, how = None, "sesión"
    while x < len(ts) and ts[x] < end:
        if h[x] >= stop:
            out_i, how = x, "stop"
            break
        if l[x] <= target:
            out_i, how = x, "objetivo"
            break
        x += 1
    if out_i is None:
        out_i = x - 1
    gross = (entry - (stop if how == "stop" else target if how == "objetivo" else c[out_i])) / risk
    cost = L["spread"][ent] / risk
    ny = lambda i: pd.Timestamp(int(ts[i]) - AHEAD, unit="s")             # noqa: E731
    df["ny"] = pd.to_datetime(df.ts - AHEAD, unit="s")
    t0 = pd.Timestamp(int(ts[a]) - AHEAD, unit="s") - pd.Timedelta(minutes=30)
    t1 = ny(ent) + pd.Timedelta(minutes=args.hasta or max(60, int((ny(out_i) - ny(ent)).total_seconds() // 60) + 15))
    zoom = df[(df.ny >= t0) & (df.ny <= t1)].reset_index(drop=True)
    unit, pips, dec = (1e-4, "pips", 5) if forex else (1.0, "pts", 2)
    sg = lambda p: sgn * p                                                  # noqa: E731
    lvl, ext_p, ent_p, stop_p, tgt_p = sg(c1h), sg(ext), sg(entry), sg(stop), sg(target)
    f_bot, f_top = sorted((sg(fvg[0]), sg(fvg[1])))
    lows = [sg(h[touch])] if sgn < 0 else [sg(l[touch])]
    lo_all = min([zoom.low.min(), tgt_p if tgt_p < zoom.low.min() else zoom.low.min(), ent_p, lvl]) if True else 0
    hi_all = max(zoom.high.max(), ext_p, lvl)
    pad = (hi_all - lo_all) * 0.08
    p = ds.Panel(zoom, 90, 560, lo_all - pad, hi_all + pad, ticks=14)
    c2_i, c1_end = p.idx(pd.Timestamp(int(ts[a]) - AHEAD, unit="s")), p.idx(pd.Timestamp(int(ts[a]) - AHEAD, unit="s"))
    p.hline(lvl, RED, "7 4", width=1.5)
    p.text(ds.X0 + 6, p.py(lvl) + (-6 if sgn > 0 else 14), f"nivel de C1 {lvl:.{dec}f} (sweep HTF)", RED, 12, bold=True)
    p.box(p.idx(ny(ie)), p.idx(ny(touch)), f_bot, f_top, AMBER, 0.3)
    p.text(p.px(p.idx(ny(touch))) + 14, p.py(f_top) + 4 if sgn > 0 else p.py(f_bot) + 4, f"② FVG {args.ltf}m {f_bot:.{dec}f}–{f_top:.{dec}f}", AMBER, 12, bold=True)
    p.dot(p.idx(ny(ie)), ext_p, RED, 8)
    p.text(p.px(p.idx(ny(ie))), p.py(ext_p) - 14, f"① máximo {ext_p:.{dec}f} ({ny(ie):%H:%M})", RED, 12, "middle", True)
    p.text(p.px(p.idx(ny(below))), p.py(c[below] * sgn) + 24, f"③ cierra bajo el nivel ({ny(below):%H:%M})", INK, 12, "middle", True)
    p.text(p.px(p.idx(ny(touch))), p.py(sg(h[touch])) - 30, f"④ retesteo del FVG ({ny(touch):%H:%M})", INK, 12, "middle", True)
    p.hline(sg(l[touch]), INK, "2 3", x_from=p.px(p.idx(ny(touch))))
    p.dot(p.idx(ny(ent)), ent_p, INK, 6, True)
    p.hline(ent_p, INK, x_from=p.px(p.idx(ny(ent))), width=1.3)
    p.text(p.px(p.idx(ny(ent))) + 10, p.py(ent_p) + 18, f"⑤ entrada {ent_p:.{dec}f} ({ny(ent):%H:%M})", INK, 12, bold=True)
    p.hline(stop_p, RED, x_from=p.px(p.idx(ny(ie))), width=1.3)
    p.text(ds.X1 - 4, p.py(stop_p) - 5, f"SL {stop_p:.{dec}f} ({risk / unit:.1f} {pips})", RED, 12, "end", True)
    p.hline(tgt_p, GREEN, "6 3", x_from=p.px(p.idx(ny(ent))))
    p.text(ds.X1 - 4, p.py(tgt_p) - 5, f"TP 2R {tgt_p:.{dec}f}", GREEN, 12, "end", True)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Arial, sans-serif">',
           f'<rect width="{W}" height="{H}" fill="white"/>',
           f'<text x="{ds.X0}" y="34" font-size="20" font-weight="700" fill="{INK}">{want} · {ny(a):%d/%m/%Y} · C2 {ny(a):%H:%M} NY · '
           f'{"corto" if sgn > 0 else "largo"} en M{args.ltf}</text>',
           f'<text x="{ds.X0}" y="58" font-size="13" fill="{MUTED}">Velas reales de M{args.ltf}, hora de Nueva York. Nivel de C1 (línea roja), FVG de M{args.ltf} '
           f'tras el máximo, retesteo y entrada.</text>'] + p.parts
    lines = [(f"① Máximo del sweep {ext_p:.{dec}f} a las {ny(ie):%H:%M} ({abs(ext_p - lvl) / unit:.1f} {pips} sobre el nivel de C1 {lvl:.{dec}f}).", 0),
             (f"② FVG de M{args.ltf} {f_bot:.{dec}f}–{f_top:.{dec}f} ({(f_top - f_bot) / unit:.1f} {pips}) entre las velas de las {ny(ie):%H:%M} y {ny(fvg[2]):%H:%M}.", 0),
             (f"③ Primer cierre bajo el nivel de C1: {ny(below):%H:%M}.   ④ Retesteo del FVG a las {ny(touch):%H:%M} (mínimo de esa vela {sg(l[touch]):.{dec}f}).", 0),
             (f"⑤ Entrada a las {ny(ent):%H:%M} al cierre de la primera vela bajo ese mínimo: {ent_p:.{dec}f}; stop {stop_p:.{dec}f}, riesgo {risk / unit:.1f} {pips}.", 0),
             (f"Con TP 2R y sin BE: «{how}» a las {ny(out_i):%d/%m %H:%M}, {gross:+.2f} R bruto, coste del spread {cost:.2f} R" + (" (la vela no trae spread)" if cost == 0 else "") + ".", 0)]
    ty = 600
    for text, _ in lines:
        svg.append(f'<text x="{ds.X0}" y="{ty}" font-size="13" fill="{INK}">{html.escape(text)}</text>')
        ty += 24
    svg.append("</svg>")
    path = ROOT / "docs" / "estrategia_crt" / f"patron_m{args.ltf}_{want.lower()}_{ny(a):%Y-%m-%d_%H%M}.svg"
    path.write_text("\n".join(svg), encoding="utf-8")
    png = path.with_suffix(".png")
    subprocess.run([CHROME, "--headless", "--disable-gpu", f"--screenshot={png}", f"--window-size={W},{H}",
                    "--default-background-color=FFFFFFFF", path.as_uri()], check=True, capture_output=True)
    print(png)


if __name__ == "__main__":
    main()
