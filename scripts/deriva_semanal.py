"""Deriva por día de la semana de la ventana Asia + London (de las 20:00 NY del día anterior a las 10:00 NY) en los índices americanos.

Contraste independiente del backtest de los patrones: usa velas H1 de MT5 (hasta ~18 años de historia) y no depende de ningún patrón.
Solo lee velas de MT5 (el bot no envía órdenes).

Uso:  uv run python scripts/deriva_semanal.py
"""
import sys; sys.path.insert(0,".")
import numpy as np, pandas as pd
from tradingbot.config import load_profiles, select_profile
from tradingbot.skills.feed.mt5_client import Mt5Source
AHEAD = 7*3600
p, d = load_profiles()
s = Mt5Source(select_profile(p, d, None), 2_000_000); s.connect()
for sym in ("NAS100.r","SP500.r","DJ30.r","US2000.r"):
    df = s.load_candles(sym, "1h")
    ny = pd.to_datetime(df["ts"] - AHEAD, unit="s")
    df = df.assign(ny=ny).set_index("ny")
    print(f"\n{sym}: {len(df)} velas H1 ({df.index[0]:%Y-%m-%d} a {df.index[-1]:%Y-%m-%d})")
    # ventana Asia+London: de las 20:00 NY del día anterior a las 10:00 NY (open de la vela de las 20:00 -> open de las 10:00)
    opens = df["open"]
    rows = []
    for day in pd.date_range(df.index[0].normalize() + pd.Timedelta(days=1), df.index[-1].normalize(), freq="D"):
        a, b = day - pd.Timedelta(hours=4), day + pd.Timedelta(hours=10)      # 20:00 del día anterior -> 10:00
        if a in opens.index and b in opens.index:
            rows.append((day, np.log(opens[b] / opens[a]) * 100))
    r = pd.DataFrame(rows, columns=["día","ret %"]).set_index("día")["ret %"]
    g = r.groupby(r.index.dayofweek).agg(["count", "mean", "std"])
    g["t"] = g["mean"] / (g["std"] / np.sqrt(g["count"]))
    g.index = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"][:len(g)] if len(g)==7 else [["lunes","martes","miércoles","jueves","viernes","sábado","domingo"][i] for i in g.index]
    print(g.round(3).to_string())
s.close()
