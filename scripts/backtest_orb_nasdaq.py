"""Backtest de la estrategia ORB (rango de apertura de 15 minutos) en NAS100 (velas M5, perfil PUPrime). Solo LEE velas de MT5.

Tres sesiones (--sesion), todas en hora de Nueva York; el ORB son sus tres primeras velas M5 y el trade vale hasta la siguiente
referencia horaria:
  0100        ORB 01:00-01:15; la rotura vale hasta la apertura de Nueva York (09:30), y se cierra a esa hora.
  londres     ORB 03:00-03:15 (las 08:00 de Londres); hasta las 09:30, como la 0100. Hora fija de NY: las 2-3 semanas al año en
              que EE. UU. y Europa cambian de hora en fechas distintas, Londres abre a las 04:00 NY.
  nueva_york  ORB 09:30-09:45; hasta el cierre del contado (16:00).

Reglas (ejemplo de la 0100):
- ORB: máximo y mínimo de las velas M5 de las 01:00, 01:05 y 01:10 (el rango acaba a las 01:15).
- Rotura con cuerpo: la primera vela M5 desde las 01:15 que CIERRA por encima del máximo (largo) o por debajo del mínimo (corto)
  del ORB. Una mecha sola no cuenta. Vale hasta la apertura de Nueva York: la vela tiene que cerrar como tarde a las 09:30.
- Entrada a mercado al cierre de la vela de rotura. Una sola operación por día.
- Stop en el extremo opuesto del ORB más un colchón del 20 % de su ancho (configurable: --colchon): largo, mínimo - 0,2 x ancho;
  corto, máximo + 0,2 x ancho. Objetivo a la misma distancia que el stop (1:1).
- Si a las 09:30 no ha tocado ni el stop ni el objetivo, se cierra al cierre de la vela de las 09:25 (el trade vale hasta la
  apertura de Nueva York). Otras salidas, en la sensibilidad.
- Si en una vela caben el stop y el objetivo, cuenta el stop. La vela de la entrada no cuenta (se entra a su cierre).
- Costes: el spread real de MT5 en la vela de la entrada, una vez por operación (R neto = R bruto - spread / riesgo). Sin comisiones
  ni deslizamiento.

CRITERIOS, FIJADOS ANTES DE VER RESULTADOS (variante principal de cada sesión: colchón 20 %, 1:1, salida a su hora límite). Se da por buena si cumple
TODOS:
  1. Al menos 300 operaciones.
  2. R neto medio > +0,05 y estadístico t > 2 en todo el histórico.
  3. R neto medio positivo en las dos mitades del histórico (partido por la fecha de entrada).
El resto de variantes son sensibilidad: no se elige la mejor por su resultado (con muchas pruebas, alguna sale bien por azar). El
colchón, que es configurable, se elige solo con la 1.ª mitad y se mide en la 2.ª.

Uso (desde la raíz del proyecto):
    uv run python scripts/backtest_orb_nasdaq.py
    uv run python scripts/backtest_orb_nasdaq.py --cache            # reutiliza las velas ya descargadas
    uv run python scripts/backtest_orb_nasdaq.py --colchon 0.3
    uv run python scripts/backtest_orb_nasdaq.py --cache --sesion londres

Salida: docs/backtest_orb_nasdaq/RESULTADOS_<sesión>.md (resumen, se sube a git) y analisis/backtest_orb_nasdaq_<sesión>.csv
(operaciones, ignorada).
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from backtest_patrones import AHEAD, intraday_start, stats                       # noqa: E402

NY_OPEN = 9 * 60 + 30
NY_CLOSE = 16 * 60
BAR = 5
ORB_MINUTES = 15                            # el ORB son las tres primeras velas M5 de la sesión
# sesión -> (nombre, inicio del ORB y hora límite en minutos NY): la rotura tiene que cerrar como tarde a la hora límite, y a esa
# hora se cierra la operación si no ha tocado ni el stop ni el objetivo
SESSIONS = {"0100": ("01:00", 60, NY_OPEN), "londres": ("apertura de Londres", 180, NY_OPEN),
            "nueva_york": ("apertura de Nueva York", NY_OPEN, NY_CLOSE)}
CACHE = ROOT / "analisis" / "orb_nasdaq_m5.pkl"
CSV = ROOT / "analisis" / "backtest_orb_nasdaq_{}.csv"
DOC = ROOT / "docs" / "backtest_orb_nasdaq" / "RESULTADOS_{}.md"
MIN_TRADES, MIN_MEAN, MIN_T = 300, 0.05, 2.0
DAYS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")


@dataclass(frozen=True)
class Params:
    buffer: float = 0.2                     # colchón del stop, en anchos del ORB
    rr: float = 1.0                         # objetivo en R
    exit_min: int = NY_OPEN                 # cierre por tiempo (minutos NY); las velas que cierran después no cuentan
    side: str = "ambos"                     # "ambos", "long" o "short"
    start: int = 60                         # inicio del ORB (minutos NY)
    deadline: int = NY_OPEN                 # la rotura tiene que cerrar como tarde aquí

    @property
    def orb_bars(self) -> tuple[int, ...]:
        return tuple(range(self.start, self.start + ORB_MINUTES, BAR))


def hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


# -- datos ---------------------------------------------------------------------------------------------
def load(profile: str, want: str, use_cache: bool) -> tuple[str, pd.DataFrame]:
    """Velas M5 con su spread (en precio) del perfil de MT5, desde que el histórico es intradía."""
    if use_cache and CACHE.exists():
        sym, df = pd.read_pickle(CACHE)
        return sym, df
    from tradingbot.config import load_profiles, select_profile
    from tradingbot.skills.feed.mt5_client import CHUNK, Mt5Source
    profiles, default = load_profiles()
    source = Mt5Source(select_profile(profiles, default, profile), 2_000_000)
    print("conectado:", source.connect())
    sym = source.resolve_symbol(want)
    if not sym:
        raise SystemExit(f"El perfil {profile} no tiene {want}")
    mt5 = source._mt5
    point = mt5.symbol_info(sym).point
    frames, pos = [], 0
    while True:
        rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M5, pos, CHUNK)
        if rates is None or len(rates) == 0:
            break
        frames.append(pd.DataFrame(rates))
        pos += len(rates)
        if len(rates) < CHUNK:
            break
    source.close()
    df = pd.concat(frames).drop_duplicates("time").sort_values("time").reset_index(drop=True)
    df = df.rename(columns={"time": "ts"})[["ts", "open", "high", "low", "close", "spread"]]
    df["spread"] = df["spread"].astype(float) * point
    df = df.iloc[intraday_start(df["ts"].to_numpy()):-1].reset_index(drop=True)      # la última vela sigue formándose
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    pd.to_pickle((sym, df), CACHE)
    return sym, df


# -- simulación ----------------------------------------------------------------------------------------
def trades(df: pd.DataFrame, p: Params) -> tuple[pd.DataFrame, dict]:
    """Una operación por día como mucho, con las reglas de `p`. Devuelve las operaciones y el embudo de días."""
    ny = df["ts"].to_numpy() - AHEAD
    day, mins = ny // 86400, (ny % 86400) // 60
    o, h, l, c, sp = (df[k].to_numpy() for k in ("open", "high", "low", "close", "spread"))
    rows, funnel = [], {"días": 0, "con ORB": 0, "con rotura": 0}
    starts = np.flatnonzero(np.r_[True, day[1:] != day[:-1]])
    ends = np.r_[starts[1:], len(day)]
    for a, b in zip(starts, ends):
        weekday = int((day[a] + 3) % 7)
        if weekday > 4:
            continue
        funnel["días"] += 1
        m = mins[a:b]
        orb = [a + k for k in np.flatnonzero(np.isin(m, p.orb_bars))]
        if len(orb) != len(p.orb_bars):
            continue
        hi, lo = float(h[orb].max()), float(l[orb].min())
        width = hi - lo
        if width <= 0:
            continue
        funnel["con ORB"] += 1
        scan = [a + k for k in np.flatnonzero((m >= p.start + ORB_MINUTES) & (m + BAR <= p.deadline))]
        hit = next((i for i in scan if c[i] > hi or c[i] < lo), None)
        if hit is None:
            continue
        funnel["con rotura"] += 1
        long = c[hit] > hi
        if p.side != "ambos" and p.side != ("long" if long else "short"):
            continue
        entry = float(c[hit])
        stop = lo - p.buffer * width if long else hi + p.buffer * width
        risk = abs(entry - stop)
        target = entry + p.rr * risk if long else entry - p.rr * risk
        after = [i for i in range(hit + 1, b) if mins[i] + BAR <= p.exit_min]
        result, gross, last = "tiempo", 0.0, hit
        for i in after:
            last = i
            if (l[i] <= stop) if long else (h[i] >= stop):
                result, gross = "stop", -1.0
                break
            if (h[i] >= target) if long else (l[i] <= target):
                result, gross = "objetivo", p.rr
                break
        if result == "tiempo":
            gross = ((c[last] - entry) if long else (entry - c[last])) / risk
        cost = float(sp[hit]) / risk
        rows.append({"día": pd.Timestamp(int(day[a]) * 86400, unit="s").date(), "día semana": DAYS[weekday],
                     "dirección": "long" if long else "short",
                     "entrada (NY)": pd.Timestamp(int(ny[hit]) + BAR * 60, unit="s"),      # al cierre de la vela de rotura
                     "cierre (NY)": pd.Timestamp(int(ny[last]) + BAR * 60, unit="s"),
                     "ORB alto": hi, "ORB bajo": lo, "ancho ORB": width, "ancho ORB %": 100 * width / entry,
                     "entrada": entry, "stop": stop, "objetivo": target, "riesgo %": 100 * risk / entry,
                     "spread": float(sp[hit]), "resultado": result, "velas": last - hit,
                     "R bruto": gross, "coste (R)": cost, "R neto": gross - cost})
    out = pd.DataFrame(rows)
    if len(out):
        widths = out["ancho ORB"]
        out["ancho relativo"] = widths / widths.shift(1).rolling(20, min_periods=10).median()
    return out, funnel


# -- informe -------------------------------------------------------------------------------------------
def summary(t: pd.DataFrame, net: str = "R neto") -> dict:
    if not len(t):
        return {"operaciones": 0}
    return stats(t[net], t["cierre (NY)"])


def row(name: str, t: pd.DataFrame, net: str = "R neto") -> list:
    s = summary(t, net)
    if not s.get("operaciones"):
        return [name, 0, "-", "-", "-", "-", "-", "-"]
    pf = s["profit factor"]
    return [name, s["operaciones"], f"{s['win rate %']:.1f} %", f"{s['R medio']:+.3f}", f"{s['R total']:+.1f}",
            "-" if pd.isna(pf) else f"{pf:.2f}", f"{s['máx. drawdown (R)']:.1f}", f"{s['estadístico t']:+.2f}"]


HEAD = ["", "Ops", "Acierto", "R medio", "R total", "PF", "Máx. DD", "t"]


def table(rows: list, head: list = HEAD) -> str:
    lines = ["| " + " | ".join(str(x) for x in head) + " |", "|" + "|".join("---" if i == 0 else "---:" for i in range(len(head))) + "|"]
    lines += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return "\n".join(lines)


def halves(t: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    mid = t["entrada (NY)"].median()
    return t[t["entrada (NY)"] <= mid], t[t["entrada (NY)"] > mid]


def report(sym: str, df: pd.DataFrame, base: Params, session: str) -> str:
    main, funnel = trades(df, base)
    main.to_csv(str(CSV).format(session), index=False)
    title = SESSIONS[session][0]
    bars = ", ".join(hhmm(b) for b in base.orb_bars)
    first_scan, limit, last_bar = hhmm(base.start + ORB_MINUTES), hhmm(base.deadline), hhmm(base.deadline - BAR)
    ny = df["ts"].to_numpy() - AHEAD
    hours = pd.Series((ny % 86400) // 3600).value_counts().reindex(range(24), fill_value=0)
    first, last = pd.Timestamp(int(ny[0]), unit="s"), pd.Timestamp(int(ny[-1]), unit="s")
    s = summary(main)
    h1, h2 = halves(main)
    s1, s2 = summary(h1), summary(h2)
    checks = [(f"al menos {MIN_TRADES} operaciones", s.get("operaciones", 0) >= MIN_TRADES, f"{s.get('operaciones', 0)}"),
              (f"R neto medio > +{MIN_MEAN} y t > {MIN_T}", s.get("operaciones", 0) > 0 and s["R medio"] > MIN_MEAN and s["estadístico t"] > MIN_T,
               f"{s.get('R medio', 0):+.3f} R, t {s.get('estadístico t', 0):+.2f}" if s.get("operaciones") else "-"),
              ("R neto medio positivo en las dos mitades", bool(s1.get("operaciones")) and bool(s2.get("operaciones"))
               and s1["R medio"] > 0 and s2["R medio"] > 0,
               f"{s1.get('R medio', 0):+.3f} / {s2.get('R medio', 0):+.3f} R" if s1.get("operaciones") and s2.get("operaciones") else "-")]
    passed = all(ok for _, ok, _ in checks)

    out = [f"# Backtest ORB {title} en {sym} (M5, PUPrime)", "",
           f"Script: `scripts/backtest_orb_nasdaq.py --sesion {session}` → operaciones en `analisis/backtest_orb_nasdaq_{session}.csv` "
           f"(no se sube a git). "
           f"Solo lee velas de MT5.", "",
           "## Reglas (hora de Nueva York)", "",
           f"- **ORB:** máximo y mínimo de las velas M5 de las {bars}.",
           f"- **Rotura con cuerpo:** la primera vela M5 desde las {first_scan} que cierra fuera del ORB, como tarde a las {limit}. "
           "Una operación por día.",
           f"- **Entrada** al cierre de esa vela. **Stop** en el extremo opuesto del ORB ± {base.buffer:.0%} de su ancho. "
           f"**Objetivo** {base.rr:g}:1 (a la misma distancia que el stop).",
           f"- Sin stop ni objetivo a las {limit}: se cierra al cierre de la vela de las {last_bar}. Si caben stop y objetivo en una "
           "vela, cuenta el stop.",
           "- **Costes:** spread real de MT5 en la vela de la entrada (R neto = R bruto − spread / riesgo). Sin comisiones ni "
           "deslizamiento.", "",
           "## Datos", "",
           f"- {len(df):,} velas M5 de {sym} del {first:%d/%m/%Y} al {last:%d/%m/%Y} (hora de NY, servidor = NY + "
           f"{AHEAD // 3600} h).".replace(",", "."),
           f"- Días laborables: {funnel['días']}; con las tres velas del ORB: {funnel['con ORB']}; con rotura antes de las {limit}: "
           f"{funnel['con rotura']} ({100 * funnel['con rotura'] / max(1, funnel['con ORB']):.0f} %).",
           f"- Comprobación del horario: velas con hora NY 17 (la pausa diaria de los índices): {int(hours[17])} de "
           f"{len(df):,}.".replace(",", "."), "",
           "## Veredicto (criterios fijados antes de ver los resultados)", "",
           table([[name, value, "sí" if ok else "**no**"] for name, ok, value in checks], ["Criterio", "Valor", "Cumple"]), "",
           f"**{'Pasa' if passed else 'No pasa'}.**", "",
           "## Resultado de la variante principal", "",
           table([row("Todas", main), row("Sin costes (R bruto)", main, "R bruto"),
                  row("Long", main[main["dirección"] == "long"]), row("Short", main[main["dirección"] == "short"]),
                  row("1.ª mitad", h1), row("2.ª mitad", h2)]), ""]
    if len(main):
        res = main["resultado"].value_counts()
        out += [f"Cómo terminan: objetivo {int(res.get('objetivo', 0))}, stop {int(res.get('stop', 0))}, a las {limit} "
                f"{int(res.get('tiempo', 0))}. Coste medio {main['coste (R)'].mean():.3f} R (mediano "
                f"{main['coste (R)'].median():.3f} R); riesgo medio {main['riesgo %'].mean():.2f} % del precio; ancho medio del "
                f"ORB {main['ancho ORB %'].mean():.2f} %.", "",
                "## Por año", "", table([row(str(y), g) for y, g in main.groupby(pd.to_datetime(main["entrada (NY)"]).dt.year)]), "",
                "## Por día de la semana", "", table([row(d, main[main["día semana"] == d]) for d in DAYS[:5]]), "",
                "## Por hora de la rotura", "",
                table([row(f"{hh:02d}:00", g) for hh, g in main.groupby(pd.to_datetime(main["entrada (NY)"]).dt.hour)]), "",
                "## Por ancho del ORB", "",
                "Ancho frente a la mediana de los 20 días anteriores con operación.", "",
                table([row(name, main[mask]) for name, mask in (
                    ("estrecho (< 0,7)", main["ancho relativo"] < 0.7),
                    ("normal (0,7 - 1,3)", main["ancho relativo"].between(0.7, 1.3)),
                    ("ancho (> 1,3)", main["ancho relativo"] > 1.3))]), ""]

    # sensibilidad
    out += ["## Sensibilidad", "", "Cambiando una cosa cada vez sobre la variante principal.", ""]
    sens = []
    for buf in (0.0, 0.1, 0.2, 0.3, 0.5):
        sens.append(row(f"colchón {buf:.0%}" + (" (principal)" if buf == base.buffer else ""), trades(df, replace(base, buffer=buf))[0]))
    for rr in (1.5, 2.0):
        sens.append(row(f"objetivo {rr:g}:1", trades(df, replace(base, rr=rr))[0]))
    for minute in (12 * 60, 14 * 60, NY_CLOSE):
        if minute > base.deadline:                  # salir más tarde que la hora límite (la rotura sigue valiendo hasta ella)
            sens.append(row(f"salida a las {hhmm(minute)}", trades(df, replace(base, exit_min=minute))[0]))
    if base.deadline > 12 * 60:                     # Nueva York: salir antes, a mediodía
        sens.append(row("rotura y salida hasta las 12:00", trades(df, replace(base, deadline=12 * 60, exit_min=12 * 60))[0]))
    out += [table(sens), ""]

    # el colchón se elige con la 1.ª mitad y se mide en la 2.ª
    if len(main):
        cut = main["entrada (NY)"].median()
        wf = []
        for buf in (0.0, 0.1, 0.2, 0.3, 0.5):
            t = trades(df, replace(base, buffer=buf))[0]
            a, b = t[t["entrada (NY)"] <= cut], t[t["entrada (NY)"] > cut]
            wf.append((buf, summary(a).get("R medio", -9), b))
        best = max(wf, key=lambda x: x[1])
        out += ["## Colchón elegido con la 1.ª mitad", "",
                f"Con la 1.ª mitad el mejor colchón es el {best[0]:.0%} ({best[1]:+.3f} R). En la 2.ª mitad, sin haberla visto:", "",
                table([row(f"colchón {best[0]:.0%}, 2.ª mitad", best[2])]), ""]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--perfil", default="puprime")
    ap.add_argument("--simbolo", default="NAS100")
    ap.add_argument("--colchon", type=float, default=0.2, help="colchón del stop en anchos del ORB (0,2 = 20 %%)")
    ap.add_argument("--sesion", choices=list(SESSIONS), default="0100", help="sesión del ORB (por defecto la 01:00)")
    ap.add_argument("--cache", action="store_true", help="reutiliza las velas guardadas en analisis/orb_nasdaq_m5.pkl")
    args = ap.parse_args()
    sym, df = load(args.perfil, args.simbolo, args.cache)
    _, start, deadline = SESSIONS[args.sesion]
    text = report(sym, df, Params(buffer=args.colchon, start=start, deadline=deadline, exit_min=deadline), args.sesion)
    doc = Path(str(DOC).format(args.sesion))
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(text + "\n", encoding="utf-8")
    print(text)
    print(f"\nInforme: {doc}\nOperaciones: {str(CSV).format(args.sesion)}")


if __name__ == "__main__":
    main()
