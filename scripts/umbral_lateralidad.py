"""Umbral del filtro de lateralidad (eficiencia mínima del precio en las 6 h previas al bloque): ¿0,20 mejora a 0,15?

Toma las operaciones del backtest de patrones (Excel) y vuelve a calcular, con cada umbral, qué sesgo habría tenido el bot en la
vela de cada entrada, con dos juegos de reglas: las del backtest y las que usa el bot ahora. Mide las operaciones a favor del
sesgo (las que Cortex dejaría pasar) y cuántas quedan fuera. Solo lee MT5 y el Excel.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import backtest_patrones as bp                                            # noqa: E402
from tradingbot.config import load_profiles, select_profile               # noqa: E402
from tradingbot.skills.bias.history import block_ids, efficiency, score_history   # noqa: E402
from tradingbot.skills.feed.mt5_client import Mt5Source                   # noqa: E402

RULESETS = {
    "reglas del backtest": [("prev_day_break", 2.0), ("tdo", 2.0), ("midnight", 1.0), ("htf_break", 2.0)],
    "reglas del bot ahora": [("above_below_open", 1.0), ("htf_sweep", 2.0), ("htf_break", 2.0), ("sma", 2.0)],
}
THRESHOLDS = (0.0, 0.10, 0.15, 0.20, 0.25, 0.30)
MIN_SCORE = 3.0


def stats(r: pd.Series) -> dict:
    n = len(r)
    sd = r.std(ddof=1) if n > 2 else 0.0
    return {"operaciones": n, "win %": 100 * (r > 0).mean() if n else np.nan, "R neto": r.mean() if n else np.nan,
            "t": r.mean() / (sd / np.sqrt(n)) if sd > 0 else 0.0}


def main(path: str = "analisis/backtest_ny_extendido.xlsx") -> None:
    trades = pd.read_excel(path, sheet_name="Operaciones")
    profiles, default = load_profiles()
    source = Mt5Source(select_profile(profiles, default, None), 2_000_000)
    source.connect()
    rows = []
    for sym, g in trades.groupby("mercado"):
        df = source.load_candles(sym, "15m").reset_index(drop=True)
        df = df.iloc[bp.intraday_start(df["ts"].to_numpy()):].reset_index(drop=True)
        ts = df["ts"].to_numpy().astype(np.int64)
        o, h, l, c = (df[k].to_numpy().astype(float) for k in ("open", "high", "low", "close"))
        idx = np.searchsorted(ts, ((g["entrada (NY)"] - pd.Timestamp("1970-01-01")) // pd.Timedelta(seconds=1)).to_numpy() + bp.AHEAD)
        ids = block_ids(ts - bp.AHEAD, 18 * 3600, 3)
        k = int(round(6 * 3600 / 900))
        eff = efficiency(c, k)
        want = np.where(g["dirección"].to_numpy() == "long", 1, -1)
        for name, rules in RULESETS.items():
            score = score_history(ts, o, h, l, c, rules, bp.AHEAD, 18 * 60, 3, 3, 30)[idx]
            for thr in THRESHOLDS:
                lateral = (eff < thr)[ids][idx]
                bias = np.where(lateral, 0, np.where(score >= MIN_SCORE, 1, np.where(score <= -MIN_SCORE, -1, 0)))
                for i, r in enumerate(g["R neto"].to_numpy()):
                    rows.append((name, thr, sym, bias[i] == want[i], bias[i] == -want[i], bias[i] == 0, r))
        print(sym, "ok")
    source.close()
    df = pd.DataFrame(rows, columns=["reglas", "umbral", "mercado", "a favor", "en contra", "sin sesgo", "R"])
    pd.set_option("display.width", 200)
    for name in RULESETS:
        d = df[df["reglas"] == name]
        out = []
        for thr, gg in d.groupby("umbral"):
            fav, contra, sin = gg[gg["a favor"]]["R"], gg[gg["en contra"]]["R"], gg[gg["sin sesgo"]]["R"]
            out.append({"umbral": thr, **{f"favor {k}": v for k, v in stats(fav).items()},
                        "contra R": contra.mean(), "contra n": len(contra), "sin sesgo n": len(sin), "sin sesgo R": sin.mean()})
        print(f"\n{name}\n", pd.DataFrame(out).round(3).to_string(index=False))
    print("\nA favor del sesgo por mercado, umbral 0,15 y 0,20 (reglas del bot ahora)")
    d = df[(df["reglas"] == "reglas del bot ahora") & df["umbral"].isin([0.15, 0.20]) & df["a favor"]]
    print(d.groupby(["mercado", "umbral"])["R"].agg(["count", "mean"]).round(3))


if __name__ == "__main__":
    main(*sys.argv[1:])
