"""Sesgo del sweep de C1 sin ninguna regla de entrada: qué hace el precio después de que C2 barre un extremo de C1.

Corto (barrido del máximo; el largo es el espejo, así que positivo = el precio baja, a favor del CRT). Solo cuentan las C2 que no tomaron antes el otro
extremo de C1. Dos anclas, las dos conocidas en tiempo real:
  A) el cierre de la primera vela M5 que cierra por debajo del nivel de C1 dentro de C2: deriva a +1 h, +2 h, al cierre de C2 y al cierre de C3.
  B) el cierre de C2 si C2 cierra dentro del rango de C1 (la premisa clásica del CRT): deriva en C3, si C3 llega al otro extremo de C1 y si supera
     el máximo de C2.
Las derivas se miden en múltiplos de la altura de C1 y en pips/puntos, frente al spread medio de M5.

Uso: uv run python scripts/sesgo_sweep_crt.py  → analisis/sesgo_sweep_crt.pkl
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tradingbot.skills.crt import engine  # noqa: E402

DATASETS = [("puprime", "nas100", engine.INDICES, 1.0), ("metaquotes", "nas100", engine.INDICES, 1.0), ("puprime", "dj30", engine.INDICES, 1.0),
            ("puprime", "sp500", engine.INDICES, 1.0), ("puprime", "eurusd", engine.FOREX, 1e-4), ("puprime", "gbpusd", engine.FOREX, 1e-4)]


def run(profile: str, want: str, cfg: engine.Cfg, unit: float) -> pd.DataFrame:
    sym, df = pd.read_pickle(ROOT / "analisis" / f"crt_{profile}_{want}_m5.pkl")
    htf = engine.aggregate(df, cfg.htf_min, cfg, cfg.origin)
    rows = []
    span = cfg.htf_min * 60
    d1 = engine.aggregate(df, 1440, cfg, cfg.origin)
    d1c = d1["close"].to_numpy()
    ema = pd.Series(d1c).ewm(span=30, adjust=False).mean().to_numpy()
    d1ts = d1["ts"].to_numpy()
    for sign in (1, -1):
        L, H = engine.view(df, sign), engine.view(htf, sign)
        lts, h, l, c, sp = L["ts"], L["high"], L["low"], L["close"], L["spread"]
        Ht, Hh, Hl, Hc = H["ts"], H["high"], H["low"], H["close"]
        for i in range(1, len(Ht) - 1):
            if Ht[i] - Ht[i - 1] > span * 1.5 or Ht[i + 1] - Ht[i] > span * 1.5:
                continue
            c1l, c1h = Hl[i - 1], Hh[i - 1]
            if not Hh[i] > c1h:
                continue
            a, b = np.searchsorted(lts, [Ht[i], Ht[i] + span])
            e3 = np.searchsorted(lts, Ht[i] + 2 * span)
            if b - a < 5 or e3 - b < 5:
                continue
            up, dn = np.nonzero(h[a:b] > c1h)[0], np.nonzero(l[a:b] < c1l)[0]
            if len(dn) and dn[0] <= up[0]:
                continue
            rng = c1h - c1l
            k = int(np.searchsorted(d1ts, Ht[i], "right")) - 2               # último día D1 completo antes de C2
            if k < 6:
                continue
            slope = ema[k] - ema[k - 5]
            d_down = d1c[k] < ema[k] and slope < 0
            d_up = d1c[k] > ema[k] and slope > 0
            tendencia = (d_down if sign > 0 else d_up)                        # a favor: el sweep es contra la tendencia D1 (corto en bajista)
            contra = (d_up if sign > 0 else d_down)
            row = dict(a_favor=bool(tendencia), en_contra=bool(contra), hora=int(((Ht[i] - cfg.ahead) // 3600) % 24),
                       nivel12=bool(i >= 13 and c1h >= Hh[i - 12:i].max()), nivel30=bool(i >= 31 and c1h >= Hh[i - 30:i].max()),
                       nivel60=bool(i >= 61 and c1h >= Hh[i - 60:i].max()),
                       mercado=sym, lado="short" if sign > 0 else "long", t=int(Ht[i]), rango=rng / unit, spread=float(np.mean(sp[a:b])) / unit)
            # B: C2 cierra dentro de C1
            row["c2_dentro"] = bool(Hc[i] < c1h)
            row["c3_toca_otro_extremo"] = bool(Hl[i + 1] < c1l)
            row["c3_supera_max_c2"] = bool(Hh[i + 1] > Hh[i])
            row["deriva_B"] = (Hc[i] - Hc[i + 1]) / rng
            row["deriva_B_pips"] = (Hc[i] - Hc[i + 1]) / unit
            # A: primer cierre bajo el nivel
            s0 = a + int(up[0])
            below = np.nonzero(c[s0:b] < c1h)[0]
            if len(below):
                ja = s0 + int(below[0])
                p0 = c[ja]
                for tag, k in (("1h", 12), ("2h", 24)):
                    jk = min(ja + k, e3 - 1)
                    row[f"deriva_A_{tag}"] = (p0 - c[jk]) / rng
                    row[f"deriva_A_{tag}_pips"] = (p0 - c[jk]) / unit
                row["deriva_A_c2"] = (p0 - c[b - 1]) / rng
                row["deriva_A_c3"] = (p0 - c[e3 - 1]) / rng
                row["deriva_A_c3_pips"] = (p0 - c[e3 - 1]) / unit
                row["min_a_c3"] = (p0 - l[ja:e3].min()) / rng              # lo máximo que bajó (MFE) sin stop
                row["max_a_c3"] = (h[ja:e3].max() - p0) / rng              # lo máximo que subió (MAE) sin stop
                row["t_A"] = int(lts[ja])
            rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    parts = []
    for prof, want, cfg, unit in DATASETS:
        r = run(prof, want, cfg, unit)
        r["clave"] = f"{prof}/{want}"
        parts.append(r)
        print(prof, want, len(r), flush=True)
    d = pd.concat(parts, ignore_index=True)
    d["fecha"] = pd.to_datetime(d["t"] - engine.INDICES.ahead, unit="s")
    d.to_pickle(ROOT / "analisis" / "sesgo_sweep_crt.pkl")
    print(len(d))


if __name__ == "__main__":
    main()
