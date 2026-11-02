"""Estudio de patrones CRT con la entrada fijada por el usuario: la primera vela LTF que cierra por debajo del nivel barrido de C1 tras haber
estado por encima (corto; el largo es el espejo). Entrada al cierre de esa vela, stop en el extremo del sweep (el máximo desde que superó el
nivel), objetivo 2R, sin BE. Una operación por C2, dentro de C2, y una sola abierta a la vez. Solo cuenta si C2 no tomó antes el otro extremo
de C1 (ni lo toma antes de la entrada).

Para cada operación se guardan características de las velas que quedaron por encima del nivel (cuántas, profundidad, mecha del extremo,
vela de entrada...) y el resultado, para ver qué patrón se repite más con 2R. Salida: analisis/estudio_patrones_crt.pkl.

Uso: uv run python scripts/estudio_patrones_crt.py
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
LTFS = (5, 3)
RR = 2.0


def atr(df: pd.DataFrame, n: int = 14) -> np.ndarray:
    h, l, c = df["high"].to_numpy(), df["low"].to_numpy(), df["close"].to_numpy()
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    return pd.Series(tr).rolling(n, min_periods=3).mean().to_numpy()


def run(profile: str, want: str, cfg: engine.Cfg, ltf_min: int) -> pd.DataFrame:
    sym, base = pd.read_pickle(ROOT / "analisis" / f"crt_{profile}_{want}_m5.pkl")
    df = base if ltf_min == 5 else pd.read_pickle(ROOT / "analisis" / f"crt_{profile}_{want}_m{ltf_min}.pkl")[1]
    htf = engine.aggregate(base, cfg.htf_min, cfg, cfg.origin)
    av = atr(df)
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
            if b - a < 3:
                continue
            up = np.nonzero(h[a:b] > c1h)[0]
            dn = np.nonzero(l[a:b] < c1l)[0]
            if len(dn) and dn[0] <= up[0]:
                continue                                       # tomó primero el extremo opuesto
            s0 = a + int(up[0])
            ext, ie, closes_above = -np.inf, s0, 0
            for j in range(s0, b - 1):
                if l[j] < c1l:
                    break
                if h[j] > ext:
                    ext, ie = h[j], j
                if c[j] >= c1h:
                    closes_above += 1
                    continue
                # j = primera vela que cierra por debajo del nivel tras haber estado por encima: entrada al cierre
                entry, stop = c[j], ext
                risk = stop - entry
                if risk <= 0:
                    break
                start, end_ts = j + 1, engine.session_end(int(lts[j]), cfg)
                e = start
                while e < len(lts) and lts[e] < end_ts:
                    e += 1
                hs, ls = h[start:e], l[start:e]
                hit = np.nonzero(hs >= stop)[0]
                i_stop = int(hit[0]) if len(hit) else len(hs)
                tg = np.nonzero(ls[:i_stop] <= entry - RR * risk)[0]
                if len(tg):
                    r, x = RR, start + int(tg[0])
                elif len(hit):
                    r, x = -1.0, start + i_stop
                elif e > start:
                    r, x = (entry - c[e - 1]) / risk, e - 1
                else:
                    break
                rng_e = max(h[ie] - l[ie], 1e-12)
                rng_j = max(h[j] - l[j], 1e-12)
                rows.append(dict(
                    mercado=sym, ltf=ltf_min, lado=side, t=int(lts[j]), c2=int(H["ts"][i]), t_sal=int(lts[x]), R=r - sp[j] / risk, bruto=r,
                    ganada=float(r >= RR), coste=sp[j] / risk, riesgo=risk, rango_c1=c1h - c1l, prof=ext - c1h, nbar=j - s0 + 1,
                    ncierres_sobre=closes_above, mecha_ext=(h[ie] - max(o[ie], c[ie])) / rng_e, cuerpo_ent=(o[j] - c[j]) / rng_j,
                    cierre_bajo=(c[j] - l[j]) / rng_j, pos_c2=(lts[j] - H["ts"][i]) / (cfg.htf_min * 60), atr=av[j],
                    room=(c[j] - c1l) / risk, ext_es_s0=int(ie == s0), unit=1.0))
                break
    return pd.DataFrame(rows)


def one_at_a_time(g: pd.DataFrame) -> pd.DataFrame:
    g = g.sort_values("t")
    last, keep = 0, []
    for t, t_sal in zip(g["t"].to_numpy(), g["t_sal"].to_numpy()):
        keep.append(t > last)
        if t > last:
            last = t_sal
    return g[np.array(keep)]


def main() -> None:
    parts = []
    for prof, want, cfg in DATASETS:
        for ltf in LTFS:
            r = run(prof, want, cfg, ltf)
            r["clave"] = f"{prof}/{want}"
            parts.append(r)
            print(prof, want, ltf, len(r), flush=True)
    d = pd.concat(parts, ignore_index=True)
    d = pd.concat([one_at_a_time(g) for _, g in d.groupby(["clave", "ltf"], sort=False)], ignore_index=True)
    d["fecha"] = pd.to_datetime(d["t"] - engine.INDICES.ahead, unit="s")
    d.to_pickle(ROOT / "analisis" / "estudio_patrones_crt.pkl")
    print(len(d))


if __name__ == "__main__":
    main()
