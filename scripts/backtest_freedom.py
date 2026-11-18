"""Backtest del modelo 90M tCISD («Freedom Model», Quarterly Theory) en NAS100.s con SP500.s y DJ30.s como activos correlacionados (velas M5 de analisis/5m/puprime).

Usa `modelo` (skills/smt/freedom.py) y `resolve` de Setup (stop antes que objetivo en la misma vela; cierre por tiempo a las 18:00 NY). Sin costes.

    uv run --with pyarrow python scripts/backtest_freedom.py [--velas RUTA] [--symbol NAS100.s]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tradingbot.skills.barrido.rth import cierre_del_dia  # noqa: E402
from tradingbot.skills.setup.positions import resolve  # noqa: E402
from tradingbot.skills.smt.freedom import agregar, alinear, modelo  # noqa: E402

SYMBOLS = ("NAS100.s", "SP500.s", "DJ30.s")
AHEAD = 7 * 3600
DEFAULT_CANDLES = Path("C:/Users/claude/DEV/TradingBot/analisis/5m/puprime")


def cargar(velas: Path) -> dict:
    out = {}
    for sym in SYMBOLS:
        df = pd.read_parquet(velas / f"{sym}.parquet").iloc[:-1]
        out[sym] = tuple(df[k].to_numpy(np.int64 if k == "ts" else float) for k in ("ts", "open", "high", "low", "close"))
    return alinear(out)


def simular(series: dict, symbol: str, trades: list[dict], tf_min: int) -> list[dict]:
    ts, _o, h, l, c = series[symbol]
    out = []
    for t in trades:
        cierre = min(t["entry_ts"] + 86400, cierre_del_dia(t["entry_ts"], AHEAD, 18 * 60))
        order = SimpleNamespace(direction=t["direction"], price=t["entry"], stop=t["stop"], target=t["target"], entry_ts=t["entry_ts"], close_ts=cierre, be_price=None)
        done = resolve(order, ts, h, l, c, None, tf_min * 60)
        if done is not None:
            out.append({**t, "result": done.result, "r": done.r, "exit_ts": done.exit_ts})
    return out


def resumen(rows: list[dict]) -> str:
    if not rows:
        return "n=0"
    r = np.array([t["r"] for t in rows])
    cum = np.cumsum([t["r"] for t in sorted(rows, key=lambda t: t["exit_ts"])])
    dd = float((np.maximum.accumulate(cum) - cum).max())
    riesgo = np.median([t["risk"] for t in rows])
    return f"n={len(r)} acierto {100 * (r > 0).mean():.0f} % R={r.sum():+.1f} ({r.mean():+.3f}/op) DD {dd:.1f} R, riesgo mediano {riesgo:.0f} pts"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--velas", default=str(DEFAULT_CANDLES))
    ap.add_argument("--symbol", default="NAS100.s")
    args = ap.parse_args()
    base = cargar(Path(args.velas))
    s15 = {s: agregar(v, AHEAD, 15) for s, v in base.items()}
    t0, t1 = (pd.Timestamp(int(base[args.symbol][0][k]) - AHEAD, unit="s").date() for k in (0, -1))
    print(f"{args.symbol} con {', '.join(s for s in SYMBOLS if s != args.symbol)}: {t0} .. {t1}\n")
    print("Entrada «nivel» exigiendo que el precio atraviese el nivel (90m, 2R / 3R):")
    for hol in (0.0, 2.0, 5.0, 10.0):
        r2 = simular(base, args.symbol, modelo(base, args.symbol, AHEAD, 5, "90m", 2.0, "nivel", hol), 5)
        r3 = simular(base, args.symbol, modelo(base, args.symbol, AHEAD, 5, "90m", 3.0, "nivel", hol), 5)
        print(f"   holgura {hol:4.0f} pts  2R: {resumen(r2)}")
        print(f"                       3R: {resumen(r3)}")
    print()
    for ciclo, series, tf in (("90m", base, 5), ("dia", s15, 15)):
        for entrada in ("rechazo", "nivel"):
            for rr in (2.0, 3.0):
                rows = simular(series, args.symbol, modelo(series, args.symbol, AHEAD, tf, ciclo, rr, entrada), tf)
                print(f"ciclo {ciclo:3s} (velas {tf:2d}m) entrada {entrada:7s} {rr:g}R: {resumen(rows)}")
                if ciclo == "90m" and entrada == "rechazo" and rr == 3.0:
                    for y in sorted({pd.Timestamp(t["day"] * 86400, unit="s").year for t in rows}):
                        print(f"      {y}: {resumen([t for t in rows if pd.Timestamp(t['day'] * 86400, unit='s').year == y])}")
                    for d in ("long", "short"):
                        print(f"      {d}: {resumen([t for t in rows if t['direction'] == d])}")


if __name__ == "__main__":
    main()
