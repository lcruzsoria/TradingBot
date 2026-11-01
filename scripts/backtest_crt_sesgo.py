"""Sesgo de tendencia para el CRT: ¿mejoran los sweeps a favor de la tendencia global y de un nivel de D1 a los que van en contra?

Sobre los setups del backtest CRT (mismas reglas, sin tocar nada) se calcula, con las velas D1 YA CERRADAS en el inicio de C2 (sin
look-ahead), si cada setup va a favor, en contra o neutral respecto a cada criterio. Se fijaron antes de ver los resultados:
- EMA30:        cierre de la última D1 cerrada sobre (bajo) su EMA de 30 días -> a favor de los largos (cortos).
- Estructura:   fractales de 2 velas en D1 (confirmados 2 velas después): HH+HL = alcista, LH+LL = bajista, otra cosa = neutral.
- CRT anidado:  el extremo del sweep supera el mínimo (largos) o el máximo (cortos) de la D1 anterior cerrada, o sea, el sweep de H3/H4
                es a la vez un sweep de D1. Es sí/no (no hay neutral).
- Premium/discount: posición del extremo del sweep dentro del rango (máximo y mínimo) de las últimas 5 D1 cerradas (semana) o 20 (mes):
                por debajo del 50 % (discount) es a favor de los largos, por encima (premium) a favor de los cortos. Es sí/no.
- Momentum:     (control) cierre de la última D1 cerrada sobre (bajo) el de hace 20 velas.
Las D1 empiezan a la hora de apertura del HTF del mercado (18:00 NY en índices, 17:00 en forex). Se filtran los setups ANTES de entrar,
así los descartados no bloquean operaciones. Criterios de aprobación del backtest CRT: >= 100 ops, R neto > +0.05 con t > 2, positivo
en los dos periodos y R neto > 0 en el control, todo sobre los setups «a favor».

    uv run python scripts/backtest_crt_sesgo.py --mercado indices
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import backtest_crt as bt                                                              # noqa: E402
from backtest_orb_nasdaq import summary, table                                         # noqa: E402
from tradingbot.skills.crt import engine                                               # noqa: E402
from tradingbot.skills.crt.engine import Rule                                          # noqa: E402

EMA_SPAN, MOM_BARS, FRACTAL = 30, 20, 2
CRITERIA = {"ema": f"EMA{EMA_SPAN} D1", "estructura": "estructura D1", "anidado": "CRT anidado (sweep de D1)", "pd5": "premium/discount semana (5 D1)",
            "pd20": "premium/discount mes (20 D1)", "momentum": f"momentum {MOM_BARS} D1"}


def daily_context(base: pd.DataFrame) -> dict:
    """Por cada D1: tendencia (EMA30, estructura, momentum) conocida al CIERRE de esa vela, y su máximo y mínimo."""
    d1 = engine.aggregate(base, 1440, bt.CFG, bt.CFG.origin)
    n = len(d1)
    c, h, l = d1["close"].to_numpy(), d1["high"].to_numpy(), d1["low"].to_numpy()
    ema = pd.Series(c).ewm(span=EMA_SPAN, adjust=False).mean().to_numpy()
    ema_side = np.where(np.arange(n) < EMA_SPAN, 0, np.sign(c - ema)).astype(int)
    mom = np.zeros(n, dtype=int)
    mom[MOM_BARS:] = np.sign(c[MOM_BARS:] - c[:-MOM_BARS]).astype(int)
    struct = np.zeros(n, dtype=int)
    sh, sl = [], []                                                                    # (índice, precio) de los swings confirmados
    for k in range(n):
        i = k - FRACTAL                                                                # el swing de la vela i se confirma al cerrar la i+2
        if i >= FRACTAL:
            around = np.r_[np.arange(i - FRACTAL, i), np.arange(i + 1, i + FRACTAL + 1)]
            if h[i] > h[around].max():
                sh.append(h[i])
            if l[i] < l[around].min():
                sl.append(l[i])
        if len(sh) >= 2 and len(sl) >= 2:
            struct[k] = 1 if (sh[-1] > sh[-2] and sl[-1] > sl[-2]) else -1 if (sh[-1] < sh[-2] and sl[-1] < sl[-2]) else 0
    rng = {w: (pd.Series(h).rolling(w).max().to_numpy(), pd.Series(l).rolling(w).min().to_numpy()) for w in (5, 20)}
    return {"rng": rng, "end": d1["ts"].to_numpy() + 86400, "ema": ema_side, "estructura": struct, "momentum": mom, "high": h, "low": l}


def classify(setups: list, ctx: dict) -> list[dict]:
    """+1 a favor, -1 en contra, 0 neutral (o sin histórico) de cada criterio para cada setup."""
    out = []
    for st in setups:
        k = int(np.searchsorted(ctx["end"], st["C2"], "right")) - 1                    # última D1 cerrada al empezar C2
        want = -st["sign"]                                                             # +1 largo, -1 corto
        r = {}
        if k < 0:
            r = {"ema": 0, "estructura": 0, "momentum": 0, "anidado": 0, "pd5": 0, "pd20": 0}
        else:
            for name in ("ema", "estructura", "momentum"):
                r[name] = int(ctx[name][k]) * want
            ext = st["sign"] * st["stop"]                                              # extremo real del sweep
            for w in (5, 20):
                hi, lo = ctx["rng"][w][0][k], ctx["rng"][w][1][k]
                if np.isnan(hi) or hi <= lo:
                    r[f"pd{w}"] = 0
                else:
                    pos = (ext - lo) / (hi - lo)                                       # 0 = mínimo del rango, 1 = máximo
                    r[f"pd{w}"] = 1 if (pos < 0.5 if want > 0 else pos > 0.5) else -1
            r["anidado"] = 1 if (ext < ctx["low"][k] if want > 0 else ext > ctx["high"][k]) else -1
        out.append(r)
    return out


def cell(t: pd.DataFrame) -> str:
    s = summary(t)
    return f"{s['operaciones']} ops, {s['R medio']:+.3f} R, t {s['estadístico t']:+.2f}" if s.get("operaciones") else "sin operaciones"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mercado", choices=sorted(bt.MARKETS), default="indices")
    args = ap.parse_args()
    mk = bt.configure(args.mercado)
    ltfs, rule = (5, 3), Rule()
    P, C = (f"{p}/{w}" for p, w in bt.DATASETS)
    data = {f"{p}/{w}": {tf: pd.read_pickle(bt.cache_path(p, w, tf))[1] for tf in (5, 3)} for p, w in bt.DATASETS}
    cut = bt.TRAIN_END
    sub, ctxs = {}, {}
    for k, frames in data.items():
        ctx = daily_context(frames[5])
        for tf in ltfs:
            st, _ = bt.find_setups(frames[5], frames[tf], tf, rule)
            cls = classify(st, ctx)
            sub[(k, tf, "todos")] = st
            for crit in CRITERIA:
                for lab, val in (("favor", 1), ("contra", -1)):
                    sub[(k, tf, crit, lab)] = [s for s, c in zip(st, cls) if c[crit] == val]
            print(k, f"M{tf}", len(st), "setups", {c: (sum(x[c] == 1 for x in cls), sum(x[c] == -1 for x in cls)) for c in CRITERIA}, flush=True)

    def run(k: str, tf: int, key: tuple, v: int) -> pd.DataFrame:
        return bt.run_variant(data[k][tf], sub[(k, tf, *key)], v, tf, rule)

    rows, passed, total = [], 0, 0
    for tf in ltfs:
        for v, vname in bt.VARIANTS.items():
            base_t = run(P, tf, ("todos",), v)
            for crit, cname in CRITERIA.items():
                fav, con = run(P, tf, (crit, "favor"), v), run(P, tf, (crit, "contra"), v)
                ctrl = run(C, tf, (crit, "favor"), v)
                s, c = summary(fav), summary(ctrl)
                p1, p2 = bt.by_period(fav, cut)
                s1, s2 = summary(p1), summary(p2)
                ok1 = s.get("operaciones", 0) >= bt.MIN_OPS and s["R medio"] > bt.MIN_MEAN and s["estadístico t"] > bt.MIN_T
                ok2 = bool(s1.get("operaciones")) and bool(s2.get("operaciones")) and s1["R medio"] > 0 and s2["R medio"] > 0
                ok3 = bool(c.get("operaciones")) and c["R medio"] > 0
                total += crit != "momentum"
                passed += (ok1 and ok2 and ok3) and crit != "momentum"
                rows.append([f"M{tf} · {v}", cname, cell(base_t), cell(fav), cell(con), f"{bt.val(s1)} / {bt.val(s2)}", cell(ctrl),
                             "**Pasa**" if ok1 and ok2 and ok3 else "no"])
                print(rows[-1], flush=True)
    head = ["LTF · entrada", "Criterio", "Sin filtro", "A favor", "En contra", "Periodos (a favor)", f"Control a favor", "Resultado"]
    out = [f"# CRT con sesgo de tendencia en {mk['title']} ({mk['htf']})", "",
           "Script: `scripts/backtest_crt_sesgo.py`. Criterios fijados antes de ver resultados (cabecera del script). Los setups se filtran "
           "con las D1 cerradas al empezar C2. **Neutral** (sin histórico o estructura mixta) no aparece ni en «a favor» ni en «en contra».",
           "", f"- Se da por bueno si, sobre los «a favor»: ≥ {bt.MIN_OPS} ops, R neto > +{bt.MIN_MEAN} con t > {bt.MIN_T}; positivo en "
           f"los dos periodos (hasta 2022 / 2023 en adelante) y R neto > 0 en el control ({mk['control']}).",
           f"- El momentum es solo control y no cuenta en el total. Combinaciones evaluadas: {total}, **pasan {passed}**.", "",
           table(rows, head), ""]
    doc = bt.DOC.with_name(f"RESULTADOS_sesgo{mk['suffix']}.md")
    doc.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"escrito {doc}; pasan {passed} de {total}")


if __name__ == "__main__":
    main()
