"""Backtest del setup «Continuación del RTH» (perfil Barrido_NYAM) en NAS100.s con las velas de M5 de analisis/5m/puprime.

Usa el código del bot: `contextos` + `analizar` (skills/barrido/continuacion.py) y `resolve` (skills/setup/positions.py). El informe completo
sale del exportador (scripts/exportar_backtest_barrido.py); aquí solo está la simulación, que ese script reutiliza.

    uv run --with pyarrow python scripts/backtest_barrido_continuacion.py [--velas RUTA] [--desde 2024-01-01]
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tradingbot.envconfig import load  # noqa: E402
from tradingbot.skills.barrido.continuacion import Ajustes, analizar, contextos  # noqa: E402
from tradingbot.skills.barrido.rth import cierre_del_dia  # noqa: E402
from tradingbot.skills.setup.positions import resolve  # noqa: E402
from tradingbot.skills.tbr.zones import compute, zones_from_settings  # noqa: E402

SYMBOLS = ("NAS100.s", "SP500.s", "DJ30.s")
AHEAD = 7 * 3600
TF_MIN = 5
DAY_END = 18 * 60
DEFAULT_CANDLES = Path("C:/Users/claude/DEV/TradingBot/analisis/5m/puprime")


def trades_of(symbol: str, df: pd.DataFrame, zones, ajustes: Ajustes, since: date | None) -> list[dict]:
    ts = df["ts"].to_numpy(dtype=np.int64)
    o, h, l, c = (df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    sessions = compute(ts, h, l, zones, AHEAD, TF_MIN, days=int((ts[-1] - ts[0]) // 86400) + 3)
    out = []
    for ctx in contextos(symbol, TF_MIN, ts, o, h, l, c, sessions, AHEAD, DAY_END, None):
        if since is not None and ctx.tbr.day < since:
            continue
        for hit in analizar(ctx, ajustes)[0]:
            if hit.status != "detected":
                continue
            close_ts = min(hit.ts + 24 * 3600, cierre_del_dia(hit.ts, AHEAD, DAY_END))
            order = SimpleNamespace(direction=hit.direction, price=hit.price, stop=hit.levels["stop"], target=hit.levels["target"],
                                    entry_ts=hit.ts, close_ts=close_ts)
            closed = resolve(order, ts, h, l, c, None, TF_MIN * 60)
            out.append({"symbol": symbol, "day": ctx.tbr.day, "direction": hit.direction, "entry_ts": hit.ts, "entry": hit.price,
                        "stop": order.stop, "target": order.target, "be": None,
                        "result": closed.result if closed else "abierta", "r": closed.r if closed else None,
                        "exit_ts": closed.exit_ts if closed else None, "risk": abs(hit.price - order.stop)})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--desde", default="2024-01-01")
    ap.add_argument("--velas", default=str(DEFAULT_CANDLES))
    args = ap.parse_args()
    env = load(ROOT / "tradingbot.env")
    ajustes = Ajustes.desde(env.section("BARRIDO_CONTINUACION"))
    zones = zones_from_settings(env.section("TBR"), ["PRE_NY"])
    for sym in SYMBOLS:
        if not ajustes.admite(sym):
            continue
        df = pd.read_parquet(Path(args.velas) / f"{sym}.parquet").iloc[:-1].reset_index(drop=True)
        rows = [t for t in trades_of(sym, df, zones, ajustes, date.fromisoformat(args.desde)) if t["r"] is not None]
        r = np.array([t["r"] for t in rows])
        print(f"{sym}: {len(rows)} operaciones, acierto {100 * (r > 0).mean():.0f} %, {r.sum():+.1f} R ({r.mean():+.3f} R/op)")


if __name__ == "__main__":
    main()
