"""Backtest del patrón de entrada del usuario (sin iFVG), con límite a la profundidad del sweep. Corto; el largo es el espejo.

1) C2 supera el nivel de C1 y marca máximos; el máximo vigente es el extremo (un máximo nuevo reinicia el patrón).
2) La vela siguiente al máximo es bajista y deja un FVG bajista en LTF (máximo de la vela del extremo + 2 por debajo del mínimo del extremo).
3) El precio cierra por debajo del nivel de C1; 4) vuelve a tocar el FVG (vela de retesteo);
5) entrada al cierre de la primera vela que cierra por debajo del mínimo de la vela de retesteo, antes de que C2 cierre.
Stop en el máximo (sin límite de tamaño), objetivo 2R, sin BE. Límite: profundidad del sweep (máximo − nivel de C1) respecto a la altura de C1;
si la supera, el setup queda invalidado. Se guardan todos los casos y el límite se aplica al analizar (la profundidad solo crece, así que no
cambia qué patrón se completa). Una sola operación abierta a la vez por mercado/LTF/límite.

Uso: uv run python scripts/estudio_retesteo_crt.py   → analisis/estudio_retesteo_crt.pkl
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
TARGETS = {"1R": 1.0, "1.5R": 1.5, "2R": 2.0, "3R": 3.0, "c1": "c1"}       # múltiplos del riesgo o el extremo opuesto de C1


def run(profile: str, want: str, cfg: engine.Cfg, ltf_min: int) -> pd.DataFrame:
    sym, base = pd.read_pickle(ROOT / "analisis" / f"crt_{profile}_{want}_m5.pkl")
    df = base if ltf_min == 5 else pd.read_pickle(ROOT / "analisis" / f"crt_{profile}_{want}_m{ltf_min}.pkl")[1]
    htf = engine.aggregate(base, cfg.htf_min, cfg, cfg.origin)
    rows = []
    for sign, side in ((1, "short"), (-1, "long")):
        L, H = engine.view(df, sign), engine.view(htf, sign)
        lts, o, h, l, c, sp = L["ts"], L["open"], L["high"], L["low"], L["close"], L["spread"]
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
                continue                                            # tomó primero el extremo opuesto
            s0 = a + int(up[0])
            ext, ie, fvg, below, touch = -np.inf, s0, None, None, None
            for j in range(s0, b - 1):
                if l[j] < c1l:
                    break
                if h[j] > ext:
                    ext, ie, fvg, below, touch = h[j], j, None, None, None
                    continue
                if fvg is None and j == ie + 2 and o[ie + 1] > c[ie + 1] and l[ie] > h[j]:
                    fvg = (h[j], l[ie], j)                          # (base, techo, tercera vela)
                if fvg is not None and below is None and j > fvg[2] and c[j] < c1h:
                    below = j
                if fvg is not None and below is not None and touch is None and j > below and h[j] >= fvg[0]:
                    touch = j
                elif touch is not None and j > touch and c[j] < l[touch]:
                    entry, stop = c[j], ext
                    risk = stop - entry
                    if risk <= 0:
                        break
                    start, end_ts = j + 1, engine.session_end(int(lts[j]), cfg)
                    e = start
                    while e < len(lts) and lts[e] < end_ts:
                        e += 1
                    if e <= start:
                        break
                    hs, ls = h[start:e], l[start:e]
                    hit = np.nonzero(hs >= stop)[0]
                    i_stop = int(hit[0]) if len(hit) else len(hs)
                    row = dict(mercado=sym, ltf=ltf_min, lado=side, t=int(lts[j]), c2=int(H["ts"][i]), coste=sp[j] / risk, riesgo=risk,
                               rango_c1=c1h - c1l, prof=ext - c1h, fvg_tam=fvg[1] - fvg[0], t_max=int(lts[ie]), t_touch=int(lts[touch]),
                               room=(entry - c1l) / risk)
                    for tag, tgt in TARGETS.items():
                        price = c1l if tgt == "c1" else entry - tgt * risk
                        if price >= entry:                          # el extremo de C1 ya está por encima de la entrada: no hay objetivo
                            row[f"bruto_{tag}"], row[f"sal_{tag}"] = np.nan, 0
                            continue
                        tg = np.nonzero(ls[:i_stop] <= price)[0]
                        if len(tg):
                            r, x = (entry - price) / risk, start + int(tg[0])
                        elif len(hit):
                            r, x = -1.0, start + i_stop
                        else:
                            r, x = (entry - c[e - 1]) / risk, e - 1
                        row[f"bruto_{tag}"], row[f"sal_{tag}"] = r, int(lts[x])
                    rows.append(row)
                    break
    return pd.DataFrame(rows)


def main() -> None:
    parts = []
    for prof, want, cfg in DATASETS:
        for ltf in LTFS:
            r = run(prof, want, cfg, ltf)
            r["clave"] = f"{prof}/{want}"
            parts.append(r)
            print(prof, want, ltf, len(r), flush=True)
    d = pd.concat(parts, ignore_index=True)
    d["fecha"] = pd.to_datetime(d["t"] - engine.INDICES.ahead, unit="s")
    d.to_pickle(ROOT / "analisis" / "estudio_retesteo_crt.pkl")
    print(len(d))


if __name__ == "__main__":
    main()
