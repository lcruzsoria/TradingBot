"""Backtest del sesgo (Bias) en M5: qué reglas, qué pesos, qué umbral y qué filtro de lateralidad predicen mejor.

Solo usa las velas M5 guardadas por scripts/descargar_m5.py (no toca MT5 ni envía órdenes).

Qué se mide. El Bias se calcula al abrirse cada vela HTF (bloque de 3 h en índices americanos, de 4 h en el resto) y se
mantiene hasta el siguiente bloque. Para cada bloque se compara el sesgo con lo que hizo el precio en él: la «ventaja» es
el movimiento del bloque (cierre menos apertura) en la dirección del sesgo, medido en rangos medios de bloque (los 30
anteriores). Con sesgo = 0 (No Bias) no se cuenta. Se calcula:

- ventaja media (en rangos de bloque), win rate, estadístico t y cobertura (% de bloques con sesgo);
- contradicciones: % de bloques con sesgo contrario a lo que hizo el precio en las 6 h anteriores (el problema de un sesgo
  alcista que prohíbe cortos con el precio bajista);
- laterales: % de bloques con sesgo cuando el mercado venía lateral (eficiencia del movimiento de las últimas 6 h < 0,15).

Búsqueda: pesos 0 / 1 / 2 de nueve reglas candidatas x umbral x filtro de lateralidad (sin sesgo si la eficiencia del
precio en las últimas K velas es menor que un valor). Se OPTIMIZA con el primer 60 % del histórico de cada mercado y se
VALIDA con el 40 % restante, que no se ha usado para elegir nada.

Uso:
    uv run python scripts/analisis_sesgo.py
    uv run python scripts/analisis_sesgo.py --perfil puprime      (velas de analisis/m5/<perfil>/, de descargar_m5.py --perfil)
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tradingbot.skills.bias.history import block_ids, rule_votes, sma_vote       # noqa: E402
from tradingbot.skills.levels.daylevels import DEFAULT_US_INDICES, is_us_index   # noqa: E402

AHEAD = 7 * 3600
DATA = Path("analisis/m5")
TRAIN = 0.6
BARS_6H = 72
RULES = ("prev_day_break", "tdo", "midnight", "htf_sweep", "htf_break", "sma30", "sma200", "mom6h", "mom24h")
CURRENT_DEFAULT = {"prev_day_break": 2, "tdo": 1, "midnight": 1}                  # reglas por defecto del bot
PROPUESTA = {"prev_day_break": 2, "tdo": 2, "midnight": 1, "htf_break": 2}           # elegida: ver docs/analisis_sesgo
CURRENT_LOCAL = {"prev_day_break": 2, "tdo": 2, "midnight": 1, "htf_sweep": 2, "htf_break": 2}   # + above_below_open (= tdo)
WEIGHTS = (0, 1, 2)
THRESHOLDS = (1, 2, 3, 4, 5, 6)
ER_BARS = (36, 72, 144)                      # ventanas de la eficiencia: 3 h, 6 h, 12 h
ER_MIN = (0.0, 0.10, 0.15, 0.20, 0.25, 0.30)


def efficiency(c: np.ndarray, k: int) -> np.ndarray:
    """Eficiencia del movimiento de las k velas anteriores: |cierre final - inicial| / suma de |cambios| (0 = lateral, 1 = tendencia)."""
    step = np.abs(np.diff(c, prepend=c[0]))
    csum = np.r_[0.0, np.cumsum(step)]
    i = np.arange(len(c))
    lo = np.maximum(i - k, 0)
    path = csum[i] - csum[lo + 1]                                           # suma de |cambios| en (lo, i-1]
    net = np.abs(c[np.maximum(i - 1, 0)] - c[lo])
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(path > 0, net / path, 0.0)
    out[:k] = 0.0
    return out


def load_symbol(path: Path) -> dict | None:
    df = pd.read_parquet(path)
    sym = path.stem
    ts = df["ts"].to_numpy().astype(np.int64)
    o, h, l, c = (df[k].to_numpy().astype(float) for k in ("open", "high", "low", "close"))
    index = is_us_index(sym, DEFAULT_US_INDICES)
    hours, anchor = (3, 18 * 60) if index else (4, 17 * 60)
    votes = rule_votes(ts, o, h, l, c, ["htf_sweep", "htf_break"], AHEAD, anchor, hours, 30)
    votes["sma30"] = sma_vote(o, c, 30)
    votes["sma200"] = sma_vote(o, c, 200)
    i = np.arange(len(c))
    for name, k in (("mom6h", BARS_6H), ("mom24h", 288)):                  # precio de apertura frente a hace k velas
        votes[name] = np.where(i >= k, np.sign(o - c[np.maximum(i - k - 1, 0)]), 0.0)
    fb = np.flatnonzero(np.r_[True, block_ids(ts - AHEAD, anchor * 60, hours)[1:] != block_ids(ts - AHEAD, anchor * 60, hours)[:-1]])
    ends = np.r_[fb[1:] - 1, len(ts) - 1]
    rng = np.array([h[a:b + 1].max() - l[a:b + 1].min() for a, b in zip(fb, ends)])
    trailing = pd.Series(rng).shift(1).rolling(30, min_periods=10).mean().to_numpy()
    ret = (c[ends] - o[fb]) / trailing
    keep = ~np.isnan(ret) & (fb >= 300)                                     # bloques con histórico para todas las reglas
    pre = np.where(fb >= BARS_6H, np.sign(c[np.maximum(fb - 1, 0)] - c[np.maximum(fb - 1 - BARS_6H, 0)]), 0.0)
    block = {
        "symbol": sym, "n": int(keep.sum()), "ret": ret[keep], "pre": pre[keep],
        "votes": np.column_stack([votes[k][fb][keep] for k in ("prev_day_break", "tdo", "midnight", "htf_sweep", "htf_break",
                                                               "sma30", "sma200", "mom6h", "mom24h")]),
        "er": {k: efficiency(c, k)[fb][keep] for k in ER_BARS},
        "when": pd.to_datetime(ts[fb][keep] - AHEAD, unit="s"),
    }
    cut = int(block["n"] * TRAIN)
    block["train"] = np.arange(block["n"]) < cut
    return block


def evaluate(bias: np.ndarray, d: dict) -> dict:
    """Métricas de un sesgo (+1/-1/0 por bloque) sobre los datos `d`."""
    m = bias != 0
    res = {}
    for name, sel in (("train", d["train"]), ("test", ~d["train"]), ("todo", np.ones(len(bias), bool))):
        s = m & sel
        n = int(s.sum())
        edge = bias[s] * d["ret"][s]
        mean = float(edge.mean()) if n else 0.0
        sd = float(edge.std(ddof=1)) if n > 2 else 0.0
        res[name] = {"n": n, "cobertura": n / max(int(sel.sum()), 1), "ventaja": mean,
                     "win": float((edge > 0).mean()) if n else 0.0,
                     "t": mean / (sd / np.sqrt(n)) if sd > 0 else 0.0,
                     "contradice": float((bias[s] * d["pre"][s] < 0).mean()) if n else 0.0,
                     "lateral": float((d["er"][72][s] < 0.15).mean()) if n else 0.0}
    return res


def make_bias(weights: dict, threshold: float, d: dict, er_k: int = 72, er_min: float = 0.0) -> np.ndarray:
    w = np.array([weights.get(k, 0) for k in RULES], dtype=float)
    score = d["votes"] @ w
    bias = np.where(score >= threshold, 1.0, np.where(score <= -threshold, -1.0, 0.0))
    if er_min > 0:
        bias = np.where(d["er"][er_k] < er_min, 0.0, bias)
    return bias


def merge(parts: list[dict]) -> dict:
    d = {"ret": np.concatenate([p["ret"] for p in parts]), "pre": np.concatenate([p["pre"] for p in parts]),
         "votes": np.vstack([p["votes"] for p in parts]), "train": np.concatenate([p["train"] for p in parts]),
         "er": {k: np.concatenate([p["er"][k] for p in parts]) for k in ER_BARS}}
    return d


def fmt(r: dict) -> str:
    return (f"n={r['n']:5d} cob={100 * r['cobertura']:4.1f}% ventaja={r['ventaja']:+.3f} win={100 * r['win']:4.1f}% "
            f"t={r['t']:+5.2f} contradice={100 * r['contradice']:4.1f}% lateral={100 * r['lateral']:4.1f}%")


def grid(d: dict) -> pd.DataFrame:
    """Todas las combinaciones de pesos x umbral x filtro, con métricas en entrenamiento y en validación."""
    combos = np.array(list(itertools.product(WEIGHTS, repeat=len(RULES))), dtype=np.float32)
    combos = combos[combos.sum(axis=1) > 0]
    V = d["votes"].astype(np.float32)
    ret = d["ret"].astype(np.float32)
    pre = d["pre"].astype(np.float32)
    splits = {"train": d["train"], "test": ~d["train"]}
    masks = {(0, 0.0): np.ones(len(ret), np.float32)}
    for k, thr in itertools.product(ER_BARS, ER_MIN[1:]):
        masks[(k, thr)] = (d["er"][k] >= thr).astype(np.float32)
    lateral = (d["er"][72] < 0.15).astype(np.float32)
    rows = []
    for start in range(0, len(combos), 1500):
        W = combos[start:start + 1500]
        S = V @ W.T                                                         # bloques x combinaciones
        for thr in THRESHOLDS:
            pos, neg = (S >= thr).astype(np.float32), (S <= -thr).astype(np.float32)
            sign = pos - neg
            contra = (sign * pre[:, None] < 0).astype(np.float32)
            for (k, er_min), mask in masks.items():
                for name, sel in splits.items():
                    vec = (mask * sel).astype(np.float32)
                    n = np.abs(sign).T @ vec
                    edge = sign.T @ (ret * vec)
                    sq = np.abs(sign).T @ (ret * ret * vec)
                    win = ((pos.T @ ((ret > 0) * vec)) + (neg.T @ ((ret < 0) * vec)))
                    contra_n = contra.T @ vec
                    lat_n = np.abs(sign).T @ (lateral * vec)
                    total = max(float(sel.sum()), 1.0)
                    mean = np.divide(edge, n, out=np.zeros_like(edge), where=n > 0)
                    var = np.divide(sq, n, out=np.zeros_like(sq), where=n > 0) - mean ** 2
                    se = np.sqrt(np.maximum(var, 1e-12) / np.maximum(n, 1))
                    cols = {"n": n, "cob": n / total, "ventaja": mean, "t": np.where(n > 2, mean / se, 0.0),
                            "win": np.divide(win, n, out=np.zeros_like(win), where=n > 0),
                            "contradice": np.divide(contra_n, n, out=np.zeros_like(contra_n), where=n > 0),
                            "lateral": np.divide(lat_n, n, out=np.zeros_like(lat_n), where=n > 0)}
                    if name == "train":
                        part = {f"{c}_train": v for c, v in cols.items()}
                        part.update({"umbral": thr, "er_k": k, "er_min": er_min})
                        part["idx"] = np.arange(start, start + len(W))
                        train_part = part
                    else:
                        test_part = {f"{c}_test": v for c, v in cols.items()}
                rows.append(pd.DataFrame({**train_part, **test_part}))
    out = pd.concat(rows, ignore_index=True)
    for j, r in enumerate(RULES):
        out[r] = combos[out["idx"].to_numpy(), j].astype(int)
    return out.drop(columns="idx")


def describe_row(r) -> str:
    w = " ".join(f"{k}={int(r[k])}" for k in RULES if r[k])
    f = f" ER{int(r['er_k'])}>={r['er_min']:.2f}" if r["er_min"] else ""
    return f"[{w}] umbral={int(r['umbral'])}{f}"


def final_report(parts: list[dict]) -> None:
    """Las tres configuraciones de interés, por mitad del histórico y por mercado."""
    configs = (("A reglas por defecto anteriores (umbral 2, sin filtro)", CURRENT_DEFAULT, 2, 0.0),
               ("B reglas locales anteriores (+barrido y continuación; umbral 3, sin filtro)", CURRENT_LOCAL, 3, 0.0),
               ("C propuesta: ruptura 2, TDO 2, Midnight 1, continuación 2; umbral 3; filtro de lateralidad 0,15 (6 h)",
                PROPUESTA, 3, 0.15),
               ("D propuesta sin filtro de lateralidad", PROPUESTA, 3, 0.0))
    d = merge(parts)
    for name, w, thr, er in configs:
        print(f"\n{name}")
        r = evaluate(make_bias(w, thr, d, 72, er), d)
        for k, label in (("train", "entren."), ("test", "valid."), ("todo", "todo   ")):
            print(f"   {label}: {fmt(r[k])}")
        for b in parts:
            rb = evaluate(make_bias(w, thr, b, 72, er), b)
            print(f"   {b['symbol']:9s} entren. ventaja={rb['train']['ventaja']:+.3f} (n={rb['train']['n']:4d})  "
                  f"valid. ventaja={rb['test']['ventaja']:+.3f} (n={rb['test']['n']:4d})  todo t={rb['todo']['t']:+.2f}")


def main() -> None:
    only_refs = "--referencias" in sys.argv
    profile = sys.argv[sys.argv.index("--perfil") + 1].lower() if "--perfil" in sys.argv else ""
    parts = []
    for path in sorted((DATA / profile).glob("*.parquet")):
        b = load_symbol(path)
        parts.append(b)
        print(f"  {b['symbol']}: {b['n']} bloques ({b['when'][0]:%Y-%m-%d} -> {b['when'][-1]:%Y-%m-%d})")
    d = merge(parts)
    print(f"\nTotal: {len(d['ret'])} bloques; entrenamiento {int(d['train'].sum())}, validación {int((~d['train']).sum())}")

    print("\n== Referencias ==")
    for name, w, thr in (("reglas por defecto del bot (ruptura x2, TDO, Midnight; umbral 2)", CURRENT_DEFAULT, 2),
                         ("tus reglas actuales (+barrido y continuación x2; umbral 3)", CURRENT_LOCAL, 3)):
        r = evaluate(make_bias(w, thr, d), d)
        print(f"{name}\n   entren.: {fmt(r['train'])}\n   valid. : {fmt(r['test'])}")
    print("\n== Cada regla sola (peso 1, umbral 1) ==")
    for k in RULES:
        r = evaluate(make_bias({k: 1}, 1, d), d)
        print(f"{k:15s} entren.: {fmt(r['train'])}\n{'':15s} valid. : {fmt(r['test'])}")

    final_report(parts)
    if only_refs:
        return
    res = grid(d)
    res.to_parquet(f"analisis/sesgo_grid{'_' + profile if profile else ''}.parquet")
    print(f"\nCombinaciones evaluadas: {len(res)}")
    ok = res[(res["cob_train"] >= 0.10) & (res["n_test"] >= 100)]
    best = ok.sort_values("t_train", ascending=False).head(25)
    print("\n== Las 25 mejores por t en ENTRENAMIENTO (cobertura >= 10 %), con su VALIDACIÓN ==")
    for _, r in best.iterrows():
        print(f"{describe_row(r)}\n   entren.: ventaja={r['ventaja_train']:+.3f} t={r['t_train']:+.2f} cob={100 * r['cob_train']:.1f}% "
              f"win={100 * r['win_train']:.1f}% contradice={100 * r['contradice_train']:.1f}% lateral={100 * r['lateral_train']:.1f}%\n"
              f"   valid. : ventaja={r['ventaja_test']:+.3f} t={r['t_test']:+.2f} cob={100 * r['cob_test']:.1f}% "
              f"win={100 * r['win_test']:.1f}% contradice={100 * r['contradice_test']:.1f}% lateral={100 * r['lateral_test']:.1f}%")


if __name__ == "__main__":
    main()
