"""Backtest del setup «Barrido de Asia» (perfil Barrido_ASIA) en NAS100.s, SP500.s y DJ30.s con las velas de M5 de analisis/5m/puprime.

Usa exactamente el código del bot: `contextos` + `analizar` (skills/barrido_asia/deteccion.py) para detectar el setup y `resolve`
(skills/setup/positions.py) para cerrar la posición simulada (stop, objetivo en el otro lado de Asia, o fin del día de trading).
La cuenta simulada es la del perfil: capital inicial y riesgo por operación de tradingbot.env (MT5_BARRIDO_ASIA_CAPITAL, SETUP_RISK_PCT);
cada operación suma su R por el riesgo sobre el saldo con el que se consolida (misma regla que `VirtualAccount`).

    uv run --with pyarrow python scripts/backtest_barrido_asia.py [--desde 2026-11-01] [--velas RUTA] [--informe docs/barrido_asia/BACKTEST.md]
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
from tradingbot.skills.barrido_asia.deteccion import Ajustes, analizar, cierre_del_dia, contextos  # noqa: E402
from tradingbot.skills.setup.account import Schedule  # noqa: E402
from tradingbot.skills.setup.positions import resolve  # noqa: E402
from tradingbot.skills.tbr.zones import compute, zones_from_settings  # noqa: E402

SYMBOLS = ("NAS100.s", "SP500.s", "DJ30.s")
AHEAD = 7 * 3600                      # servidor del broker = NY + 7 h (como el resto de scripts)
TF_MIN = 5
DAY_END = 18 * 60                     # el día de trading de los índices USA acaba a las 18:00 NY
DEFAULT_CANDLES = Path("C:/Users/claude/DEV/TradingBot/analisis/5m/puprime")


def trades_of(symbol: str, df: pd.DataFrame, zones, ajustes: Ajustes, since: date | None) -> list[dict]:
    ts = df["ts"].to_numpy(dtype=np.int64)
    o, h, l, c = (df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    sessions = compute(ts, h, l, zones, AHEAD, TF_MIN, days=int((ts[-1] - ts[0]) // 86400) + 3)
    out = []
    for ctx in contextos(symbol, TF_MIN, ts, o, h, l, c, sessions, AHEAD, DAY_END):
        if since is not None and (ctx.tbr.day.toordinal() + 1) < since.toordinal():      # el día de la rotura es el de la medianoche en que cierra Asia
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


def account(trades: list[dict], capital: float, risk_pct: float) -> tuple[list[dict], float, float]:
    """Cada operación cerrada suma su R por el riesgo sobre el saldo del momento en que se consolida. Devuelve (operaciones con su saldo,
    saldo final, máximo drawdown en %)."""
    sched = Schedule()
    closed = sorted((t for t in trades if t["r"] is not None), key=lambda t: (sched.due(t["symbol"], t["exit_ts"]), t["exit_ts"]))
    balance, peak, dd = capital, capital, 0.0
    rows = []
    for t in closed:
        pnl = t["r"] * risk_pct / 100 * balance
        balance += pnl
        peak = max(peak, balance)
        dd = max(dd, (peak - balance) / peak * 100)
        rows.append({**t, "pnl": pnl, "balance": balance})
    return rows, balance, dd


def summary(rows: list[dict]) -> dict:
    r = [t["r"] for t in rows]
    n = len(r)
    return {"n": n, "tp": sum(t["result"] == "objetivo" for t in rows), "sl": sum(t["result"] == "stop" for t in rows),
            "be": sum(t["result"] == "breakeven" for t in rows), "tiempo": sum(t["result"] == "tiempo" for t in rows),
            "wins": sum(x > 0 for x in r), "r_total": sum(r), "r_avg": (sum(r) / n) if n else 0.0,
            "winrate": (100 * sum(x > 0 for x in r) / n) if n else 0.0}


def line(name: str, s: dict) -> str:
    return (f"| {name} | {s['n']} | {s['tp']} | {s['sl']} | {s['be']} | {s['tiempo']} | {s['winrate']:.0f} % | {s['r_avg']:+.2f} | "
            f"{s['r_total']:+.2f} |")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--desde", help="solo los días de NY desde esta fecha (AAAA-MM-DD); por defecto, todo el histórico")
    ap.add_argument("--velas", default=str(DEFAULT_CANDLES), help="carpeta con <símbolo>.parquet de M5")
    ap.add_argument("--informe", help="guarda el informe en este fichero Markdown")
    args = ap.parse_args()
    since = date.fromisoformat(args.desde) if args.desde else None
    env = load(ROOT / "tradingbot.env")
    ajustes = Ajustes.desde(env.section("BARRIDO_ASIA"))
    zones = zones_from_settings(env.section("TBR"), ["ASIA"])
    capital = float(env.get("MT5_BARRIDO_ASIA_CAPITAL", 10000) if env.get("MT5_BARRIDO_NYAM_CAPITAL") else 10000)
    risk_pct = env.section("SETUP").get_float("RISK_PCT", 1.0)
    trades, periods = [], {}
    for sym in SYMBOLS:
        df = pd.read_parquet(Path(args.velas) / f"{sym}.parquet")
        df = df.iloc[:-1].reset_index(drop=True)                      # la última vela puede seguir formándose: solo cerradas
        periods[sym] = (pd.Timestamp(int(df["ts"].iloc[0]) - AHEAD, unit="s").date(), pd.Timestamp(int(df["ts"].iloc[-1]) - AHEAD, unit="s").date())
        trades += trades_of(sym, df, zones, ajustes, since)
    rows, balance, dd = account(trades, capital, risk_pct)
    open_trades = [t for t in trades if t["r"] is None]
    out = [f"# Backtest Barrido de Asia ({'desde ' + args.desde if since else 'todo el histórico'})", "",
           f"Velas M5 de PUPrime-Demo: " + ", ".join(f"{s} {a}..{b}" for s, (a, b) in periods.items()) + ".",
           f"Reglas: rotura {ajustes.start // 60:02d}:{ajustes.start % 60:02d}-{ajustes.end // 60:02d}:{ajustes.end % 60:02d} NY, entrada hasta "
           f"{ajustes.entry_end // 60:02d}:{ajustes.entry_end % 60:02d}, stop fijo {ajustes.stop_points:g} puntos (swing + {ajustes.stop_buffer:g} "
           f"si queda más lejos), objetivo en el lado contrario de Asia, sin breakeven.",
           f"Cuenta simulada: {capital:,.0f} USD, riesgo {risk_pct:g} % por operación (sobre el saldo en que se consolida).", "",
           "| Mercado | Operaciones | Objetivo | SL | BE | Tiempo | Acierto | R medio | R total |", "|---|---|---|---|---|---|---|---|---|"]
    for sym in SYMBOLS:
        out.append(line(sym, summary([t for t in rows if t["symbol"] == sym])))
    out.append(line("**Total**", summary(rows)))
    out += ["", f"**Saldo final {balance:,.2f} USD** ({balance - capital:+,.2f} USD, {100 * (balance / capital - 1):+.2f} %), "
                f"drawdown máximo {dd:.2f} %." + (f" Operaciones aún abiertas al final de los datos: {len(open_trades)}." if open_trades else ""), "",
            "## Por mes", "", "| Mes | Operaciones | R total | PnL (USD) |", "|---|---|---|---|"]
    by_month = {}
    for t in rows:
        by_month.setdefault(t["day"].strftime("%Y-%m"), []).append(t)
    for month in sorted(by_month):
        m = by_month[month]
        out.append(f"| {month} | {len(m)} | {sum(t['r'] for t in m):+.2f} | {sum(t['pnl'] for t in m):+,.2f} |")
    out += ["", "## Operaciones", "", "| Día NY | Mercado | Lado | Entrada | Stop | Objetivo | Resultado | R | PnL (USD) | Saldo |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for t in sorted(rows, key=lambda t: t["entry_ts"]):
        out.append(f"| {t['day']} | {t['symbol']} | {'largo' if t['direction'] == 'long' else 'corto'} | {t['entry']:.2f} | {t['stop']:.2f} | "
                   f"{t['target']:.2f} | {t['result']} | {t['r']:+.2f} | {t['pnl']:+,.2f} | {t['balance']:,.2f} |")
    text = "\n".join(out) + "\n"
    print(text)
    if args.informe:
        Path(args.informe).parent.mkdir(parents=True, exist_ok=True)
        Path(args.informe).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
