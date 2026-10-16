"""Descarga velas M5 de MT5 (solo lectura) y las guarda en analisis/m5/<símbolo>.parquet para los análisis del sesgo.

Uso (desde la raíz del proyecto):
    uv run python scripts/descargar_m5.py
    uv run python scripts/descargar_m5.py --simbolos NAS100.r EURUSD --velas 150000
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tradingbot.config import load_profiles, select_profile                      # noqa: E402
from tradingbot.skills.feed.mt5_client import Mt5Source                          # noqa: E402

SYMBOLS = ("NAS100.r", "SP500.r", "DJ30.r", "EURUSD", "GBPUSD", "XAUUSD")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--simbolos", nargs="+", default=list(SYMBOLS))
    ap.add_argument("--velas", type=int, default=200_000, help="velas M5 a pedir por mercado (el broker limita)")
    ap.add_argument("--salida", default="analisis/m5")
    args = ap.parse_args()
    out = Path(args.salida)
    out.mkdir(parents=True, exist_ok=True)
    profiles, default = load_profiles()
    source = Mt5Source(select_profile(profiles, default, None), 2_000_000)
    print("conectado:", source.connect())
    for want in args.simbolos:
        sym = source.resolve_symbol(want)
        if not sym:
            print("  sin símbolo:", want)
            continue
        df = source.load_candles(sym, "5m").tail(args.velas).reset_index(drop=True)
        df.to_parquet(out / f"{sym}.parquet")
        print(f"  {sym}: {len(df)} velas M5 ({df['time'].iloc[0]} -> {df['time'].iloc[-1]})")
    source.close()


if __name__ == "__main__":
    main()
