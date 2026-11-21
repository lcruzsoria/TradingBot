"""Valida el setup «Ventana 9:55» en otras horas (por defecto, el final del TBR de Asia y de Londres) con las velas M5 de NAS100.

Mismas reglas que skills/barrido/ventana.py, con la vela 1 a la hora que se pida (hora de NY):

1. Vela 1: la de la hora HH:MM, de cualquier color. Vela 2: la siguiente.
2. Corto si la vela 2 supera el High de la 1 y cierra negra; largo si baja del Low de la 1 y cierra blanca.
3. Entrada a mercado al cierre de la vela 2, stop en su punta, objetivo RR, sin breakeven; si no toca nada, cierra por tiempo
   (por defecto, al final del día de trading: 18:00 NY, como el bot; con --cierre, a otra hora).

El cierre de las posiciones es el `resolve` de Setup (si caben stop y objetivo en una vela cuenta el stop). Para las 09:55 el script
comprueba además que sus operaciones son exactamente las de `analizar` (el código del bot); si no casan, avisa.

Horas por defecto: 23:55 (última vela del TBR de Asia, 20:00-00:00), 04:55 (última del de Londres, 02:00-05:00) y 09:55 (referencia).

    uv run --with pyarrow python scripts/validar_ventana_horas.py [--horas 23:55,04:55,09:55] [--rr 2,3,4] [--velas RUTA]
                                                                 [--simbolo NAS100.s] [--desde 2024-01-01] [--cierre 18:00] [--todas]

--todas recorre además las 288 velas del día (solo 3R) y lista las mejores y las peores: sirve de contexto, no para elegir hora
(con 288 pruebas alguna sale buena por azar; mira la t y que lo sea en todos los años).
"""
from __future__ import annotations

import argparse
import math
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from tradingbot.skills.barrido.rth import cierre_del_dia  # noqa: E402
from tradingbot.skills.setup.positions import resolve  # noqa: E402

AHEAD = 7 * 3600                      # servidor del broker = NY + 7 h (como el resto de scripts)
TF_MIN = 5
STEP = TF_MIN * 60
DAY_END = 18 * 60
DEFAULT_CANDLES = Path("C:/Users/claude/DEV/TradingBot/analisis/5m/puprime")
NOMBRES = {"23:55": "fin del TBR de Asia", "04:55": "fin del TBR de Londres", "09:55": "Ventana 9:55 (referencia)"}


def hhmm(text: str) -> int:
    h, m = text.strip().split(":")
    value = int(h) * 60 + int(m)
    if not 0 <= value < 1440 or value % TF_MIN:
        raise ValueError(f"{text!r}: usa HH:MM en múltiplos de {TF_MIN} minutos")
    return value


def senales(ts: np.ndarray, o, h, l, c, vela: int) -> list[dict]:
    """Las señales de la vela 1 a `vela` minutos desde medianoche de NY: una por día como máximo."""
    ny = ts - AHEAD
    i = np.flatnonzero((ny % 86400 == vela * 60)[:-2] & (ts[1:-1] == ts[:-2] + STEP))     # vela 1 con su vela 2 justo detrás
    out = []
    for i in i.tolist():
        j = i + 1
        o2, h2, l2, c2 = float(o[j]), float(h[j]), float(l[j]), float(c[j])
        if c2 < o2 and h2 > h[i]:
            direction, stop = "short", h2
        elif c2 > o2 and l2 < l[i]:
            direction, stop = "long", l2
        else:
            continue
        if abs(c2 - stop) <= 0:
            continue
        out.append({"day": datetime.fromtimestamp(int(ny[i]), tz=timezone.utc).date(), "direction": direction, "entry_ts": int(ts[j]) + STEP,
                    "entry": c2, "stop": stop})
    return out


def operaciones(df: pd.DataFrame, vela: int, rr: float, cierre: int, since: date | None) -> list[dict]:
    ts = df["ts"].to_numpy(dtype=np.int64)
    o, h, l, c = (df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    out = []
    for s in senales(ts, o, h, l, c, vela):
        if since is not None and s["day"] < since:
            continue
        risk = abs(s["entry"] - s["stop"])
        sign = 1.0 if s["direction"] == "long" else -1.0
        target = s["entry"] + sign * rr * risk
        close_ts = min(s["entry_ts"] + 24 * 3600, cierre_del_dia(s["entry_ts"], AHEAD, cierre))
        order = SimpleNamespace(direction=s["direction"], price=s["entry"], stop=s["stop"], target=target, entry_ts=s["entry_ts"],
                                close_ts=close_ts, be_price=None, be_stop=None)
        closed = resolve(order, ts, h, l, c, None, STEP)
        if closed is None:
            continue
        out.append({**s, "target": target, "risk": risk, "result": closed.result, "r": float(closed.r), "exit_ts": closed.exit_ts,
                    "max_r": closed.max_r})
    return out


def estadisticas(trades: list[dict]) -> dict:
    r = np.array([t["r"] for t in trades], dtype=float)
    n = len(r)
    if not n:
        return {"n": 0}
    curve = np.cumsum(r)
    dd = float(np.max(np.maximum.accumulate(np.concatenate([[0.0], curve]))[1:] - curve))
    streak = worst = 0.0
    for x in r:                                   # peor racha: suma de R de pérdidas seguidas
        streak = streak + x if x < 0 else 0.0
        worst = min(worst, streak)
    gains, losses = r[r > 0].sum(), -r[r < 0].sum()
    sd = r.std(ddof=1) if n > 1 else 0.0
    years = {}
    for t in trades:
        years[t["day"].year] = years.get(t["day"].year, 0.0) + t["r"]
    half = n // 2
    return {"n": n, "wr": 100 * (r > 0).mean(), "total": r.sum(), "avg": r.mean(), "pf": gains / losses if losses else math.inf,
            "dd": dd, "racha": worst, "t": r.mean() / sd * math.sqrt(n) if sd else 0.0,
            "tp": sum(t["result"] == "objetivo" for t in trades), "sl": sum(t["result"] == "stop" for t in trades),
            "tiempo": sum(t["result"] == "tiempo" for t in trades),
            "largos": sum(t["r"] for t in trades if t["direction"] == "long"), "n_largos": sum(t["direction"] == "long" for t in trades),
            "cortos": sum(t["r"] for t in trades if t["direction"] == "short"), "n_cortos": sum(t["direction"] == "short" for t in trades),
            "mitad1": r[:half].sum(), "mitad2": r[half:].sum(), "riesgo": float(np.median([t["risk"] for t in trades])), "años": years}


def veredicto(s: dict) -> str:
    if s["n"] < 30:
        return "pocas operaciones: sin conclusión"
    todos = all(v > 0 for v in s["años"].values())
    if s["t"] >= 2 and todos and s["mitad1"] > 0 and s["mitad2"] > 0:
        return "PROMETEDOR (t ≥ 2, positivo todos los años y en las dos mitades)"
    if s["t"] >= 1 and s["total"] > 0:
        return "DUDOSO (positivo, pero no lo bastante sólido)"
    return "NO VALE (no se distingue del azar o pierde)"


def informe(nombre: str, vela: str, por_rr: dict[float, dict]) -> None:
    print(f"\n=== {vela} NY · {nombre} (vela 2: la siguiente) ===")
    print(f"{'RR':>4} {'ops':>5} {'acierto':>8} {'R total':>9} {'R/op':>7} {'PF':>5} {'DD R':>6} {'racha':>7} {'t':>6}  TP/SL/tiempo   largos        cortos        mitades")
    for rr, s in por_rr.items():
        if not s["n"]:
            print(f"{rr:>4g}     0")
            continue
        print(f"{rr:>4g} {s['n']:>5} {s['wr']:>7.0f}% {s['total']:>+9.1f} {s['avg']:>+7.3f} {s['pf']:>5.2f} {s['dd']:>6.1f} {s['racha']:>+7.1f} "
              f"{s['t']:>6.2f}  {s['tp']:>3}/{s['sl']:>3}/{s['tiempo']:>3}   {s['n_largos']:>3} {s['largos']:>+7.1f}   {s['n_cortos']:>3} {s['cortos']:>+7.1f}   "
              f"{s['mitad1']:>+6.1f} / {s['mitad2']:>+6.1f}")
    ref = por_rr.get(3.0) or next(iter(por_rr.values()))
    if ref["n"]:
        print("     por año (" + ("3R" if 3.0 in por_rr else "primer RR") + "): " + ", ".join(f"{y} {v:+.1f}" for y, v in sorted(ref["años"].items()))
              + f" · stop mediano {ref['riesgo']:.1f} puntos")
        print(f"     veredicto: {veredicto(ref)}")


def comprobar_955(df: pd.DataFrame, since: date | None, mias: list[dict]) -> None:
    """Las operaciones de las 09:55 a 3R deben ser las del código del bot (`analizar` de ventana.py)."""
    try:
        import exportar_backtest_ventana955 as exp
        from tradingbot.envconfig import load
        from tradingbot.skills.barrido.ventana import Ajustes
        from tradingbot.skills.tbr.zones import zones_from_settings
    except Exception as exc:                      # pragma: no cover
        print(f"(no se pudo comprobar contra el bot: {exc})")
        return
    env = load(ROOT / "tradingbot.env")
    bot = [t for t in exp.trades_of("NAS100.s", df, zones_from_settings(env.section("TBR"), ["PRE_NY"]), Ajustes(rr=3.0), since)
           if t["r"] is not None]
    a = {(t["entry_ts"], t["direction"], round(t["r"], 6)) for t in bot}
    b = {(t["entry_ts"], t["direction"], round(t["r"], 6)) for t in mias}
    if a == b:
        print(f"Comprobación: las {len(a)} operaciones de las 09:55 a 3R son las mismas que da el código del bot.")
    else:
        print(f"AVISO: las 09:55 no casan con el bot ({len(a)} del bot, {len(b)} del script, {len(a ^ b)} distintas). "
              "Puede ser algún día sin RTH completo (el bot exige la caja del RTH); revisa antes de fiarte de las otras horas.")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--velas", default=str(DEFAULT_CANDLES), help="carpeta con <símbolo>.parquet de M5")
    ap.add_argument("--simbolo", default="NAS100.s")
    ap.add_argument("--horas", default="23:55,04:55,09:55", help="hora de NY de la vela 1, separadas por comas")
    ap.add_argument("--rr", default="2,3,4", help="objetivos en R, separados por comas")
    ap.add_argument("--cierre", default="18:00", help="hora de NY del cierre por tiempo (por defecto la del bot)")
    ap.add_argument("--desde", help="solo los días de NY desde esta fecha (AAAA-MM-DD)")
    ap.add_argument("--todas", action="store_true", help="recorre también las 288 velas del día a 3R")
    args = ap.parse_args()
    since = date.fromisoformat(args.desde) if args.desde else None
    cierre = hhmm(args.cierre) if args.cierre != "24:00" else 1440
    df = pd.read_parquet(Path(args.velas) / f"{args.simbolo}.parquet").iloc[:-1].reset_index(drop=True)
    first, last = (pd.Timestamp(int(df["ts"].iloc[k]) - AHEAD, unit="s") for k in (0, -1))
    print(f"{args.simbolo}: {len(df)} velas M5, de {first:%Y-%m-%d} a {last:%Y-%m-%d} (NY). Cierre por tiempo: {args.cierre} NY. Sin costes ni spread.")
    rrs = [float(x) for x in args.rr.split(",") if x.strip()]
    for vela in [v.strip() for v in args.horas.split(",") if v.strip()]:
        por_rr = {rr: estadisticas(ops := operaciones(df, hhmm(vela), rr, cierre, since)) for rr in rrs}
        informe(NOMBRES.get(vela, "hora pedida"), vela, por_rr)
        if vela == "09:55" and args.cierre == "18:00":
            comprobar_955(df, since, operaciones(df, hhmm(vela), 3.0, cierre, since))
    if args.todas:
        rows = []
        for m in range(0, 1440, TF_MIN):
            s = estadisticas(operaciones(df, m, 3.0, cierre, since))
            if s["n"] >= 30:
                rows.append((f"{m // 60:02d}:{m % 60:02d}", s))
        rows.sort(key=lambda x: x[1]["t"], reverse=True)
        print(f"\n=== Las 288 velas a 3R ({len(rows)} con 30 operaciones o más), ordenadas por t ===")
        for label, s in rows[:15] + [("...", None)] + rows[-5:]:
            if s is None:
                print("  ...")
                continue
            print(f"  {label}  {s['n']:>4} ops  {s['total']:>+7.1f} R  t {s['t']:>5.2f}  años " + " ".join(f"{v:+.0f}" for _, v in sorted(s["años"].items())))
        print(f"  (con {len(rows)} pruebas, por azar se esperan ~{max(1, round(len(rows) * 0.023))} con t ≥ 2)")


if __name__ == "__main__":
    main()
