"""Descarga velas de MT5 (solo lectura) de un timeframe y las guarda en analisis/<tf>/<carpeta>/<símbolo>.parquet para los backtests.

Uso (desde la raíz del proyecto):
    uv run --with pyarrow python scripts/descargar_velas.py --tf 3m --perfil crt
    uv run --with pyarrow python scripts/descargar_velas.py --tf 15m --simbolos NAS100.s EURUSD --velas 100000
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tradingbot.config import load_profiles, select_profile                      # noqa: E402
from tradingbot.skills.feed.mt5_client import Mt5Source                          # noqa: E402

SYMBOLS = ("NAS100.s", "SP500.s", "DJ30.s", "EURUSD", "GBPUSD")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tf", default="3m", help="timeframe de MT5: 3m, 5m, 15m...")
    ap.add_argument("--simbolos", nargs="+", default=list(SYMBOLS))
    ap.add_argument("--velas", type=int, default=200_000, help="velas a pedir por mercado (el broker limita)")
    ap.add_argument("--perfil", default="crt")
    ap.add_argument("--carpeta", default="puprime", help="subcarpeta de salida (el broker)")
    ap.add_argument("--salida", default="analisis")
    args = ap.parse_args()
    out = Path(args.salida) / args.tf / args.carpeta
    out.mkdir(parents=True, exist_ok=True)
    profiles, default = load_profiles()
    source = Mt5Source(select_profile(profiles, default, args.perfil), 2_000_000)
    print("conectado:", source.connect())
    for want in args.simbolos:
        sym = source.resolve_symbol(want)
        if not sym:
            print("  sin símbolo:", want)
            continue
        df = source.load_candles(sym, args.tf).tail(args.velas).reset_index(drop=True)
        df.to_parquet(out / f"{sym}.parquet")
        print(f"  {sym}: {len(df)} velas {args.tf} ({df['time'].iloc[0]} -> {df['time'].iloc[-1]})", flush=True)
    source.close()


if __name__ == "__main__":
    main()
