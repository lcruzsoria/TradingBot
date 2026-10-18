"""Tabla comparativa de los backtests de los patrones (Continuación y Reversión) en todos los mercados del bot.

Lee los Excel que genera backtest_patrones.py (analisis/backtest_indices.xlsx, _forex, _oro y _cripto) y escribe
analisis/comparativa_mercados.xlsx: una fila por mercado, con lo que operaría el bot (GO de Cortex, una posición abierta a la vez y una
sesión un trade) y sin ningún filtro. Uso: uv run --with openpyxl python scripts/comparativa_mercados.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

FILES = [("Índices americanos", "analisis/backtest_indices.xlsx"), ("Forex", "analisis/backtest_forex.xlsx"),
         ("Oro", "analisis/backtest_oro.xlsx"), ("Cripto", "analisis/backtest_cripto.xlsx")]
NOTES = {"BTCUSD.bc": "spread de MT5 irreal (siempre 1 punto): el neto no incluye costes",
         "ETHUSD.bc": "spread de MT5 irreal (2,5-3,9 USD hasta 2023, 0,01 después): el neto es poco fiable"}


def stats(g: pd.DataFrame) -> dict:
    r = g["R neto"]
    n = len(r)
    sd = r.std(ddof=1) if n > 2 else 0.0
    wins, losses = r[r > 0].sum(), -r[r < 0].sum()
    eq = r.reindex(g.sort_values("cierre (NY)").index).cumsum()
    return {"operaciones": n, "win rate %": 100 * (r > 0).mean(), "R bruto medio": g["R bruto"].mean(), "R neto medio": r.mean(),
            "R neto total": r.sum(), "profit factor": wins / losses if losses else np.nan,
            "t": r.mean() / (sd / np.sqrt(n)) if sd > 0 else 0.0,
            "máx. drawdown (R)": -(eq.cummax().clip(lower=0) - eq).max(), "coste medio (R)": g["coste (R)"].mean(),
            "coste mediano (R)": g["coste (R)"].median()}


def main() -> None:
    bot, raw, meta = [], [], []
    for group, path in FILES:
        ops = pd.read_excel(path, sheet_name="Operaciones")
        info = pd.read_excel(path, sheet_name="Datos").set_index("mercado")
        take = (ops["sesgo vs operación"] != "en contra") & ~ops["solapada (GO de Cortex)"]
        for sym, g in ops.groupby("mercado"):
            years = (info.loc[sym, "hasta (NY)"] - info.loc[sym, "desde (NY)"]).days / 365.25
            head = {"grupo": group, "mercado": sym, "desde": info.loc[sym, "desde (NY)"].date(), "años": round(years, 1)}
            raw.append({**head, **stats(g)})
            bot.append({**head, **stats(g[take.reindex(g.index)]), "nota": NOTES.get(sym, "")})
        for label, rows in (("Todos los mercados del grupo, sin filtro", ops), ("Todos los del grupo, lo que opera el bot", ops[take])):
            meta.append({"grupo": group, "caso": label, **stats(rows)})
    bot, raw, meta = pd.DataFrame(bot), pd.DataFrame(raw), pd.DataFrame(meta)
    out = Path("analisis/comparativa_mercados.xlsx")
    notes = pd.DataFrame({"nota": [
        "Patrones Continuación y Reversión en M15, entrada en el 0,5 del fibonacci, stop en el swing o la mecha pivote, objetivo 2R, cierre por tiempo a las 24 h.",
        "Plazos: Asia hasta London, London hasta las 12:00 y NY Open hasta las 18:00 (hora de Nueva York). Spread real de MT5 una vez por operación.",
        "«Lo que opera el bot»: no va contra el sesgo (CORTEX_ALLOW_NO_BIAS=true), una sola posición abierta a la vez y una sesión (TBR) un trade.",
        "En cada grupo la regla de una sola posición se aplica entre los mercados del grupo (no entre grupos).",
        "R = distancia entre la entrada y el stop. R bruto = sin spread. t: por debajo de 2 en valor absoluto, no distinguible de cero.",
        "Cripto: el spread que devuelve MT5 no es realista (BTC siempre 1 punto; ETH inflado hasta 2023): usar el R bruto como referencia.",
        "Datos: MT5 Vantage demo; histórico intradía real según el mercado (columna desde)."]})
    with pd.ExcelWriter(out) as xw:
        bot.to_excel(xw, sheet_name="Lo que opera el bot", index=False)
        raw.to_excel(xw, sheet_name="Sin filtro", index=False)
        meta.to_excel(xw, sheet_name="Por grupo", index=False)
        notes.to_excel(xw, sheet_name="Notas", index=False)
        for ws in xw.book.worksheets:
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = min(max(len(str(c.value or "")) for c in col[:60]) + 2, 70)
            ws.freeze_panes = "A2"
    pd.set_option("display.width", 250)
    cols = ["mercado", "años", "operaciones", "win rate %", "R bruto medio", "R neto medio", "R neto total", "profit factor", "t"]
    print("LO QUE OPERA EL BOT\n", bot[cols].round(3).to_string(index=False))
    print("\nSIN FILTRO\n", raw[cols].round(3).to_string(index=False))
    print("\nPOR GRUPO\n", meta[["grupo", "caso", "operaciones", "win rate %", "R bruto medio", "R neto medio", "R neto total", "t"]].round(3).to_string(index=False))
    print("Excel:", out)


if __name__ == "__main__":
    main()
