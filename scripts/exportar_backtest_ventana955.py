"""Backtest del perfil Ventana9_55 (setup «Ventana 9:55», solo NAS100) para la ventana Backtest del bot.

Simula con el mismo código del bot (`contextos` + `analizar` de skills/barrido/ventana.py y `resolve` de Setup) con las velas M5 de
analisis/5m/puprime y SUSTITUYE el grupo del perfil `ventana9_55` de tradingbot/skills/stats/backtest.json.gz sin tocar el resto del fichero.

    uv run --with pyarrow python scripts/exportar_backtest_ventana955.py [--velas RUTA] [--desde 2024-01-01] [--solo-mostrar]
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import backtest_barrido_rth as b_rth        # noqa: E402
from tradingbot.envconfig import load      # noqa: E402
from tradingbot.skills.barrido.rth import cierre_del_dia  # noqa: E402
from tradingbot.skills.barrido.ventana import Ajustes, analizar, contextos  # noqa: E402
from tradingbot.skills.setup.positions import resolve  # noqa: E402
from tradingbot.skills.tbr.zones import compute, zones_from_settings  # noqa: E402

OUT = ROOT / "tradingbot" / "skills" / "stats" / "backtest.json.gz"
PROFILE, PROFILE_NAME = "ventana9_55", "Ventana9_55"
CAPITAL = 25_000.0
AHEAD = 7 * 3600
TF_MIN = 5
DAY_END = 18 * 60
SYMBOLS = ("NAS100.s",)
NAME = "Ventana 9:55"
OUTCOMES = ["objetivo", "stop", "breakeven", "tiempo"]
ZONES = ["RTH"]
FILTER = "sin filtro de sesgo"


def trades_of(symbol: str, df: pd.DataFrame, zones, ajustes: Ajustes, since: date | None) -> list[dict]:
    ts = df["ts"].to_numpy(dtype=np.int64)
    o, h, l, c = (df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    sessions = compute(ts, h, l, zones, AHEAD, TF_MIN, days=int((ts[-1] - ts[0]) // 86400) + 3)
    out = []
    for ctx in contextos(symbol, TF_MIN, ts, o, h, l, c, sessions, AHEAD, DAY_END, None):
        if since is not None and ctx.tbr.day < since:
            continue
        for hit in analizar(ctx, ajustes)[0]:
            close_ts = min(hit.ts + 24 * 3600, cierre_del_dia(hit.ts, AHEAD, DAY_END))
            order = SimpleNamespace(direction=hit.direction, price=hit.price, stop=hit.levels["stop"], target=hit.levels["target"],
                                    entry_ts=hit.ts, close_ts=close_ts, be_price=None, be_stop=None)
            closed = resolve(order, ts, h, l, c, None, TF_MIN * 60)
            out.append({"symbol": symbol, "day": ctx.tbr.day, "direction": hit.direction, "entry_ts": hit.ts, "entry": hit.price,
                        "stop": order.stop, "target": order.target, "result": closed.result if closed else "abierta",
                        "r": closed.r if closed else None, "exit_ts": closed.exit_ts if closed else None,
                        "risk": abs(hit.price - order.stop)})
    return out


def simulate(velas: Path, since: date | None) -> tuple[list[dict], dict, Ajustes]:
    env = load(ROOT / "tradingbot.env")
    ajustes = Ajustes.desde(env.section("BARRIDO_VENTANA_955"))
    zones = zones_from_settings(env.section("TBR"), ["PRE_NY"])
    trades, periods = [], {}
    for sym in SYMBOLS:
        df = pd.read_parquet(velas / f"{sym}.parquet").iloc[:-1].reset_index(drop=True)
        periods[sym] = (len(df), pd.Timestamp(int(df["ts"].iloc[0]) - AHEAD, unit="s").date(), pd.Timestamp(int(df["ts"].iloc[-1]) - AHEAD, unit="s").date())
        trades += [t for t in trades_of(sym, df, zones, ajustes, since) if t["r"] is not None]
    return trades, periods, ajustes


def group_json(trades: list[dict], periods: dict, updated: str, ajustes: Ajustes) -> dict:
    markets = sorted({t["symbol"] for t in trades} | set(periods))
    trades = sorted(trades, key=lambda t: (t["exit_ts"], t["entry_ts"]))
    outcome = {"objetivo": "objetivo", "stop": "stop", "breakeven": "breakeven"}
    cols = {"m": [markets.index(t["symbol"]) for t in trades], "p": [0] * len(trades), "z": [0] * len(trades),
            "o": [OUTCOMES.index(outcome.get(t["result"], "tiempo")) for t in trades],
            "d": [int(t["direction"] == "short") for t in trades], "s": [2] * len(trades), "f": [0] * len(trades),
            "e": [(int(t["entry_ts"]) - AHEAD) // 60 for t in trades], "x": [(int(t["exit_ts"]) - AHEAD) // 60 for t in trades],
            "v": [max(0, (int(t["exit_ts"]) - int(t["entry_ts"])) // 300) for t in trades],
            "r": [round(float(t["r"]), 6) for t in trades], "k": [0.0] * len(trades),
            "rk": [round(100 * t["risk"] / t["entry"], 3) for t in trades]}
    return {
        "key": f"{PROFILE}:indices", "nombre": "Nasdaq", "tipo": "barrido", "perfil": PROFILE, "perfil_nombre": PROFILE_NAME, "actualizado": updated,
        "cats": {"m": markets, "p": [NAME], "z": ZONES, "o": OUTCOMES, "s": ["a favor", "en contra", "sin sesgo"]}, "ops": cols,
        "patrones": ["Todos", NAME], "filtros": {FILTER: "Todas las operaciones"}, "zonas": ZONES,
        "descripcion": f"Ventana 9:55 en NAS100 M5 · la vela de las 10:00 barre la de las 09:55 y cierra del color contrario · stop en su punta · "
                       f"objetivo {ajustes.rr:g}R · sin costes (el spread no se simula)",
        "datos": [{"mercado": m, "velas M5": periods[m][0], "desde (NY)": str(periods[m][1]), "hasta (NY)": str(periods[m][2]), "TBR evaluadas": None}
                  for m in markets if m in periods],
        "metodologia": [
            ["Qué es", "El setup del perfil Ventana9_55, simulado con el mismo código que la skill Barrido del bot (contextos + analizar de ventana.py) "
                       "y la regla de cierre de Setup (stop, objetivo o fin del día de trading, 18:00 NY)."],
            ["Velas", "Vela 1: la de las 09:55 NY, de cualquier color. Vela 2: la de las 10:00; corto si supera el High de la 1 y cierra negra, largo si baja "
                      "del Low de la 1 y cierra blanca (si toca los dos lados decide su color). Sin condición de zona ni del 50 %."],
            ["Entrada y salida", f"A mercado al cierre de la vela 2 (10:05), en contra del barrido; stop en la punta de la vela 2; objetivo {ajustes.rr:g}R; "
                                 "sin breakeven. Si no toca nada, cierra al final del día de trading."],
            ["Límites", "Sin costes ni deslizamiento. Solo NAS100. Una operación al día como máximo."]]}


def write(group: dict) -> None:
    raw = json.loads(gzip.decompress(OUT.read_bytes()).decode("utf-8"))
    raw["grupos"] = [g for g in raw["grupos"] if g.get("perfil") != PROFILE] + [group]
    OUT.write_bytes(gzip.compress(json.dumps(raw, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), 9, mtime=0))
    print(f"{OUT} ({OUT.stat().st_size / 1024:.0f} KB): {len(group['ops']['e'])} operaciones de {PROFILE_NAME}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--velas", default=str(b_rth.DEFAULT_CANDLES), help="carpeta con <símbolo>.parquet de M5")
    ap.add_argument("--desde", help="solo los días de NY desde esta fecha (AAAA-MM-DD); por defecto, todo el histórico")
    ap.add_argument("--solo-mostrar", action="store_true", help="no escribe el fichero: solo imprime el resumen")
    args = ap.parse_args()
    trades, periods, ajustes = simulate(Path(args.velas), date.fromisoformat(args.desde) if args.desde else None)
    risk = load(ROOT / "tradingbot.env").section("SETUP").get_float("RISK_PCT", 1.0)
    r = np.array([t["r"] for t in trades])
    print(f"{NAME}: {len(trades)} operaciones, {r.sum():+.2f} R, acierto {100 * (r > 0).mean():.0f} %")
    for y in sorted({t["day"].year for t in trades}):
        print(f"  {y}: {sum(t['r'] for t in trades if t['day'].year == y):+.1f} R")
    rows, balance, dd = b_rth.account(trades, CAPITAL, risk)
    print(f"Cuenta de {CAPITAL:,.0f} USD al {risk:g} %: saldo {balance:,.2f} USD ({balance - CAPITAL:+,.2f}), drawdown máximo {dd:.2f} %")
    if not args.solo_mostrar:
        write(group_json(trades, periods, datetime.now(timezone.utc).strftime("%Y-%m-%d"), ajustes))


if __name__ == "__main__":
    main()
