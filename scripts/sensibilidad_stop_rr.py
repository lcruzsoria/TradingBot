"""Sensibilidad al stop y al RR de los patrones Continuación y Reversión: ¿mejora ampliando el stop? Solo lee velas de MT5.

Reutiliza las entradas de backtest_patrones (entrada en el 0,5) y las vuelve a simular con el stop ampliado a k veces el original y un
objetivo de m veces el nuevo riesgo. Salida: tablas por consola.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import backtest_patrones as bp  # noqa: E402
from tradingbot.config import load_profiles, select_profile  # noqa: E402
from tradingbot.envconfig import EnvConfig  # noqa: E402
from tradingbot.skills.feed.mt5_client import Mt5Source  # noqa: E402
from tradingbot.skills.tbr.zones import zones_from_settings  # noqa: E402

KS = (1.0, 1.25, 1.5, 2.0, 3.0)         # stop = k x riesgo original
MS = (1.0, 1.5, 2.0)                    # objetivo = m x riesgo nuevo
CALLS_PER_TRADE = 1 + len(bp.TP_MULTS) + len(bp.HOLDS)


def main() -> None:
    profiles, default = load_profiles()
    source = Mt5Source(select_profile(profiles, default, None), 2_000_000)
    source.connect()
    env = EnvConfig().section("TBR")
    order, zones = zones_from_settings(env, bp.ZONE_ORDER), zones_from_settings(env)
    calls: list = []
    real = bp.simulate

    def spy(h, l, c, t, direction, entry, stop, target, max_hold):
        calls.append((h, l, c, t, direction, entry, stop))
        return real(h, l, c, t, direction, entry, stop, target, max_hold)

    bp.simulate = spy
    rows = []
    for want in bp.SYMBOLS:
        sym = source.resolve_symbol(want)
        calls.clear()
        trades, _f, _i = bp.run_symbol(source, sym, order, zones)
        main_calls = calls[::CALLS_PER_TRADE]
        for tr, (h, l, c, t, d, entry, stop) in zip(trades, main_calls):
            risk0 = abs(entry - stop)
            for k in KS:
                risk = k * risk0
                stp = entry - risk if d == "long" else entry + risk
                for m in MS:
                    tgt = entry + m * risk if d == "long" else entry - m * risk
                    _, _, rg, _, _ = real(h, l, c, t, d, entry, stp, tgt, bp.MAX_HOLD)
                    rows.append({"mercado": sym, "patrón": tr["patrón"], "k": k, "RR": m, "bruto": rg,
                                 "neto": rg - tr["spread (precio)"] / risk, "gana": rg > 0})
        print(sym, len(trades), "operaciones")
    source.close()
    df = pd.DataFrame(rows)
    pd.set_option("display.width", 200)

    def summ(g):
        return pd.Series({"operaciones": len(g) , "win %": 100 * g["gana"].mean(), "R bruto": g["bruto"].mean(), "R neto": g["neto"].mean(),
                          "t neto": g["neto"].mean() / (g["neto"].std() / np.sqrt(len(g)))})

    tot = df.groupby(["k", "RR"]).apply(summ).round(3)
    print("\nTODOS LOS MERCADOS Y PATRONES\n", tot)
    by_m = df.groupby(["mercado", "k", "RR"]).apply(summ).round(3)
    by_p = df.groupby(["patrón", "k", "RR"]).apply(summ).round(3)
    print("\nMEJOR R neto POR MERCADO\n", by_m.sort_values("R neto", ascending=False).groupby(level=0).head(3).sort_index(level=0))
    print("\nPOR PATRÓN\n", by_p)



if __name__ == "__main__":
    main()
