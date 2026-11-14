"""Backtest de los cuatro setups del perfil Barrido_NYAM para la ventana Backtest del bot.

Simula con el mismo código del bot (`contextos` + `analizar` de skills/barrido y `resolve` de Setup, ver scripts/backtest_barrido_*.py) los setups
RTH, Continuación de Asia, PDH/PDL de Asia y PDH/PDL de Londres en NAS100.s, SP500.s y DJ30.s con las velas M5 de analisis/5m/puprime y SUSTITUYE el grupo del perfil
`barrido_nyam` de tradingbot/skills/stats/backtest.json.gz sin tocar el resto del fichero. En la ventana, el selector Patrón elige Todos o cada setup.

    uv run --with pyarrow python scripts/exportar_backtest_barrido.py [--velas RUTA] [--desde 2024-01-01]
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import backtest_barrido_asia_continuacion as b_asia      # noqa: E402
import backtest_barrido_continuacion as b_con  # noqa: E402
import backtest_barrido_londres as b_lon    # noqa: E402
import backtest_barrido_pdh as b_pdh        # noqa: E402
import backtest_barrido_rth as b_rth        # noqa: E402
from tradingbot.envconfig import load      # noqa: E402
from tradingbot.skills.tbr.zones import zones_from_settings  # noqa: E402

OUT = ROOT / "tradingbot" / "skills" / "stats" / "backtest.json.gz"
PROFILE, PROFILE_NAME = "barrido_nyam", "Barrido_NYAM"
AHEAD = 7 * 3600
SYMBOLS = b_rth.SYMBOLS
# (módulo del backtest, bloque de ajustes, zonas TBR necesarias, nombre en la ventana, TBR donde se da)
SETUPS = ((b_rth, "BARRIDO_RTH", ["PRE_NY", "ASIA", "LONDON"], "Barrido RTH", "RTH"),
          (b_asia, "BARRIDO_ASIA_CONTINUACION", ["ASIA"], "Continuación de Asia", "Asia"),
          (b_pdh, "BARRIDO_PDH", ["ASIA"], "Barrido PDH/PDL Asia", "Asia"),
          (b_lon, "BARRIDO_LONDRES", ["LONDON"], "Barrido PDH/PDL Londres", "London"),
          (b_con, "BARRIDO_CONTINUACION", ["PRE_NY"], "Continuación RTH", "RTH"))
OUTCOMES = ["objetivo", "stop", "breakeven", "tiempo"]
OUTCOME_OF = {"objetivo": "objetivo", "stop": "stop", "breakeven": "breakeven", "tiempo": "tiempo"}
ZONES = ["RTH", "Asia", "London"]
FILTER = "sin filtro de sesgo"                       # el bloque de filtros de la ventana: aquí no hay sesgo, un solo filtro


def simulate(velas: Path, since: date | None) -> tuple[list[dict], dict]:
    env = load(ROOT / "tradingbot.env")
    trades, periods = [], {}
    for sym in SYMBOLS:
        df = pd.read_parquet(velas / f"{sym}.parquet").iloc[:-1].reset_index(drop=True)
        periods[sym] = (len(df), pd.Timestamp(int(df["ts"].iloc[0]) - AHEAD, unit="s").date(), pd.Timestamp(int(df["ts"].iloc[-1]) - AHEAD, unit="s").date())
        for mod, block, zone_keys, name, zone in SETUPS:
            ajustes = mod.Ajustes.desde(env.section(block))
            zones = zones_from_settings(env.section("TBR"), zone_keys)
            for t in mod.trades_of(sym, df, zones, ajustes, since):
                if t["r"] is not None:
                    trades.append({**t, "patron": name, "zona": zone})
    return trades, periods


def group_json(trades: list[dict], periods: dict, updated: str) -> dict:
    markets = sorted({t["symbol"] for t in trades} | set(periods))
    names = [s[3] for s in SETUPS]
    trades = sorted(trades, key=lambda t: (t["exit_ts"], t["entry_ts"]))
    cols = {"m": [markets.index(t["symbol"]) for t in trades], "p": [names.index(t["patron"]) for t in trades],
            "z": [ZONES.index(t["zona"]) for t in trades], "o": [OUTCOMES.index(OUTCOME_OF.get(t["result"], "tiempo")) for t in trades],
            "d": [int(t["direction"] == "short") for t in trades], "s": [2] * len(trades), "f": [0] * len(trades),
            "e": [(int(t["entry_ts"]) - AHEAD) // 60 for t in trades], "x": [(int(t["exit_ts"]) - AHEAD) // 60 for t in trades],
            "v": [max(0, (int(t["exit_ts"]) - int(t["entry_ts"])) // 300) for t in trades],
            "r": [round(float(t["r"]), 6) for t in trades], "k": [0.0] * len(trades),
            "rk": [round(100 * t["risk"] / t["entry"], 3) for t in trades]}
    return {
        "key": f"{PROFILE}:indices", "nombre": "Índices", "tipo": "barrido", "perfil": PROFILE, "perfil_nombre": PROFILE_NAME, "actualizado": updated,
        "cats": {"m": markets, "p": names, "z": ZONES, "o": OUTCOMES, "s": ["a favor", "en contra", "sin sesgo"]}, "ops": cols,
        "patrones": ["Todos"] + names, "filtros": {FILTER: "Todas las operaciones"}, "zonas": ZONES,
        "descripcion": "Barrido RTH, Continuación de Asia, Barrido PDH/PDL (Asia y Londres) y Continuación RTH (solo Nasdaq) del modelo Greenbird en M5 · stop 30 puntos o swing + 5 (continuación: 40 puntos, 2R) · "
                       "sin costes (el spread no se simula) · una posición por setup y mercado",
        "datos": [{"mercado": m, "velas M15": periods[m][0], "desde (NY)": str(periods[m][1]), "hasta (NY)": str(periods[m][2]), "TBR evaluadas": None}
                  for m in markets if m in periods],
        "metodologia": [
            ["Qué es", "Los cinco setups de barrido del perfil Barrido_NYAM, simulados con el mismo código que la skill Barrido del bot (contextos + analizar) y la "
                       "regla de cierre de Setup (stop, objetivo, breakeven del RTH o fin del día de trading / cierre de Londres). Los botones de Patrón eligen Todos o uno."],
            ["Barrido RTH", "Rotura del rango 09:00-10:00 con una vela M5 que cierra fuera entre las 10:00 y las 11:00; entrada en el primer cierre de vuelta dentro "
                            "antes de las 12:00; objetivo en el otro lado del RTH y breakeven al tomar el Low/High de NY Open."],
            ["Continuación de Asia", "La primera vela M5 que cierra fuera del rango de Asia entre las 00:00 y las 00:30 da la entrada a ese cierre, a favor de la rotura; stop fijo "
                                     "(30 puntos en el Nasdaq, 20 en el DJ30, 4,5 en el SP500) y objetivo 3R, sin breakeven. Sustituye al antiguo Barrido de Asia (reversión)."],
            ["Barrido PDH/PDL Asia", "PDH/PDL del día de trading 18:00-18:00 NY sin tocar hasta las 20:00; lo barre entre las 20:00 y las 21:00 y la primera vela que cierra de "
                                     "vuelta (con cierre antes de las 21:00) da la entrada; objetivo en el extremo opuesto de Asia ya formado si el precio sigue dentro del rango; si no hay (o no llega), "
                                     "sale por tiempo, al precio de mercado, cuando cierra Asia (00:00); el riesgo es variable."],
            ["Barrido PDH/PDL Londres", "Lo mismo con Londres: nivel sin tocar hasta las 02:00, barrido y entrada entre las 02:00 y las 03:00; objetivo en el extremo opuesto de Londres ya formado si "
                                        "el precio sigue dentro; si no hay (o no llega), sale por tiempo al precio de mercado cuando cierra Londres (05:00)."],
            ["Continuación RTH", "Solo Nasdaq: entre las 10:00 y las 11:00 el precio toca el 50 % del RTH y después una vela M5 cierra fuera del rango por cualquier lado; entrada a ese cierre, "
                                 "a favor de la rotura, stop 40 puntos y objetivo 2R, sin breakeven. Sin rotura antes de las 11:00 no hay operación."],
            ["Stop", "Barridos y PDH/PDL: fijo a 30 puntos de la entrada si cubre el swing; si no, el swing más 5 puntos. Las continuaciones usan su stop fijo."],
            ["Límites", "Sin costes ni deslizamiento. Cada setup se simula por separado: dos setups abiertos a la vez en el mismo mercado se cuentan los dos (el bot "
                        "solo deja una posición por mercado). Solo índices USA (NAS100, SP500, DJ30)."]]}


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
    trades, periods = simulate(Path(args.velas), date.fromisoformat(args.desde) if args.desde else None)
    env = load(ROOT / "tradingbot.env")
    risk = env.section("SETUP").get_float("RISK_PCT", 1.0)
    for _mod, _b, _z, name, _zone in SETUPS:
        own = [t for t in trades if t["patron"] == name]
        print(f"{name}: {len(own)} operaciones, {sum(t['r'] for t in own):+.2f} R")
    rows, balance, dd = b_rth.account(trades, 10_000.0, risk)
    print(f"Los cinco juntos ({len(rows)} operaciones): saldo {balance:,.2f} USD ({balance - 10_000:+,.2f}), drawdown máximo {dd:.2f} %")
    if not args.solo_mostrar:
        write(group_json(trades, periods, datetime.now(timezone.utc).strftime("%Y-%m-%d")))


if __name__ == "__main__":
    main()
