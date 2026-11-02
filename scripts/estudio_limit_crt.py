"""Variante con orden límite: mismo patrón que estudio_retesteo_crt.py hasta el primer cierre bajo el nivel de C1 (máximo → FVG bajista en la vela
siguiente → cierre bajo el nivel), pero en vez de esperar al retesteo del FVG y a una vela que cierre bajo su mínimo, se deja una orden límite de
venta EN el nivel de C1: se llena cuando el precio vuelve a subir hasta el nivel (rompe el sweep) antes de que cierre C2. Stop en el máximo del
sweep (el vigente al llenarse; si en la misma vela lo supera, queda en pérdida), objetivo en múltiplos del riesgo. El riesgo es la profundidad
del sweep. El largo es el espejo. Coste: sin spread en la entrada (límite) y con él para comparar.

Uso: uv run python scripts/estudio_limit_crt.py [--real]  → analisis/estudio_limit_crt[_real].pkl (--real: bid/ask con el spread de cada vela, sin coste aparte)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tradingbot.skills.crt import engine  # noqa: E402

DATASETS = [("puprime", "nas100", engine.INDICES), ("metaquotes", "nas100", engine.INDICES), ("puprime", "dj30", engine.INDICES),
            ("puprime", "sp500", engine.INDICES), ("puprime", "eurusd", engine.FOREX), ("puprime", "gbpusd", engine.FOREX)]
LTFS = (3, 5)
TARGETS = {"1R": 1.0, "2R": 2.0, "3R": 3.0, "c1": "c1"}


def run(profile: str, want: str, cfg: engine.Cfg, ltf_min: int, real: bool = False) -> pd.DataFrame:
    sym, base = pd.read_pickle(ROOT / "analisis" / f"crt_{profile}_{want}_m5.pkl")
    df = base if ltf_min == 5 else pd.read_pickle(ROOT / "analisis" / f"crt_{profile}_{want}_m{ltf_min}.pkl")[1]
    htf = engine.aggregate(base, cfg.htf_min, cfg, cfg.origin)
    rows = []
    for sign, side in ((1, "short"), (-1, "long")):
        L, H = engine.view(df, sign), engine.view(htf, sign)
        lts, o, h, l, c, sp = L["ts"], L["open"], L["high"], L["low"], L["close"], L["spread"]
        # real: las velas son del bid. Corto: vende en el bid (límite) y recompra en el ask (stop y objetivo se ven en bid + spread).
        # Largo (visto en espejo): compra en el ask (el límite exige bajar un spread más) y vende en el bid.
        spc = sp if (real and sign > 0) else np.zeros_like(sp)
        spe = sp if (real and sign < 0) else np.zeros_like(sp)
        for i in range(1, len(H["ts"])):
            if H["ts"][i] - H["ts"][i - 1] > cfg.htf_min * 60 * 1.5:
                continue
            c1l, c1h = H["low"][i - 1], H["high"][i - 1]
            if not H["high"][i] > c1h:
                continue
            a, b = np.searchsorted(lts, [H["ts"][i], H["ts"][i] + cfg.htf_min * 60])
            if b - a < 5:
                continue
            up, dn = np.nonzero(h[a:b] > c1h)[0], np.nonzero(l[a:b] < c1l)[0]
            if len(dn) and dn[0] <= up[0]:
                continue
            s0 = a + int(up[0])
            ext, ie, fvg, below = -np.inf, s0, None, None
            for j in range(s0, b):
                if l[j] < c1l:
                    break
                if fvg is not None and below is not None and j > below and h[j] >= c1h + spe[j]:     # se llena la orden límite en el nivel
                    entry, stop = c1h, ext
                    risk = stop - entry
                    end_ts = engine.session_end(int(lts[j]), cfg)
                    e = j + 1
                    while e < len(lts) and lts[e] < end_ts:
                        e += 1
                    stop_now = h[j] + spc[j] >= stop                                                    # en la propia vela de llenado
                    hs, ls = h[j + 1:e] + spc[j + 1:e], l[j + 1:e] + spc[j + 1:e]
                    hit = np.nonzero(hs >= stop)[0]
                    i_stop = int(hit[0]) if len(hit) else len(hs)
                    row = dict(mercado=sym, ltf=ltf_min, lado=side, t=int(lts[j]), c2=int(H["ts"][i]), coste=sp[j] / risk, riesgo=risk,
                               rango_c1=c1h - c1l, prof=ext - c1h, espera=j - below, t_max=int(lts[ie]))
                    for tag, tgt in TARGETS.items():
                        price = c1l if tgt == "c1" else entry - tgt * risk
                        if stop_now:
                            r, x = -1.0, j
                        else:
                            tg = np.nonzero(ls[:i_stop] <= price)[0]
                            if len(tg):
                                r, x = (entry - price) / risk, j + 1 + int(tg[0])
                            elif len(hit):
                                r, x = -1.0, j + 1 + i_stop
                            elif e > j + 1:
                                r, x = (entry - c[e - 1]) / risk, e - 1
                            else:
                                r, x = 0.0, j
                        row[f"bruto_{tag}"], row[f"sal_{tag}"] = r, int(lts[x])
                    rows.append(row)
                    break
                if h[j] > ext:
                    ext, ie, fvg, below = h[j], j, None, None
                    continue
                if fvg is None and j == ie + 2 and o[ie + 1] > c[ie + 1] and l[ie] > h[j]:
                    fvg = (h[j], l[ie], j)
                if fvg is not None and below is None and j > fvg[2] and c[j] < c1h:
                    below = j
    return pd.DataFrame(rows)


def main() -> None:
    real = "--real" in sys.argv
    parts = []
    for prof, want, cfg in DATASETS:
        for ltf in LTFS:
            r = run(prof, want, cfg, ltf, real)
            r["clave"] = f"{prof}/{want}"
            parts.append(r)
            print(prof, want, ltf, len(r), flush=True)
    d = pd.concat(parts, ignore_index=True)
    d.to_pickle(ROOT / "analisis" / ("estudio_limit_crt_real.pkl" if real else "estudio_limit_crt.pkl"))
    print(len(d))


if __name__ == "__main__":
    main()
