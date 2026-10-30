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
    uv run python scripts/backtest_orb_nasdaq.py --cache --rejilla 15      # todos los ORB de 15 min, de 00:00 a 23:45
    uv run python scripts/backtest_orb_nasdaq.py --cache --rejilla 30      # todos los de 30 min

Rejilla (--rejilla N): un ORB de N minutos que empieza cada 15 minutos, de 00:00 a 23:45 (96 ORB). La rotura vale durante
--ventana minutos desde el final del ORB (por defecto 360, 6 h, como Londres y Nueva York) y a esa hora se cierra la operación.
Mismas reglas y criterios que arriba. Un fichero por hora con sus 4 ORB en docs/backtest_orb_nasdaq/orbs_<N>m/ y un RESUMEN.md con
la clasificación. Con 96 pruebas, alguna saldrá con t > 2 por azar: el resumen marca además las que superan el umbral corregido por
comparaciones múltiples (Bonferroni, t > 3,1) y elige con la 1.ª mitad del histórico para medir en la 2.ª.

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
GRID_STEP = 15                              # la rejilla prueba un ORB que empieza cada 15 minutos
GRID_WINDOW = 360                           # la rotura vale 6 h desde el final del ORB, y a las 6 h se cierra
BONFERRONI_T = 3.1                          # t para un 5 % de falsos positivos con 96 pruebas (0,05 / 96, una cola)
GRID_DIR = ROOT / "docs" / "backtest_orb_nasdaq" / "orbs_{}m"
DAYS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")


@dataclass(frozen=True)
class Params:
    buffer: float = 0.2                     # colchón del stop, en anchos del ORB
    rr: float = 1.0                         # objetivo en R
    exit_min: int = NY_OPEN                 # cierre por tiempo (minutos NY); las velas que cierran después no cuentan
    side: str = "ambos"                     # "ambos", "long" o "short"
    start: int = 60                         # inicio del ORB (minutos NY desde las 00:00 del día)
    deadline: int = NY_OPEN                 # la rotura tiene que cerrar como tarde aquí (puede pasar de 1440: el día siguiente)
    minutes: int = ORB_MINUTES              # duración del ORB

    @property
    def orb_bars(self) -> tuple[int, ...]:
        return tuple(range(self.start, self.start + self.minutes, BAR))


def hhmm(minutes: int) -> str:
    minutes %= 1440
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
    """Una operación por ORB (uno al día) como mucho, con las reglas de `p`. Devuelve las operaciones y el embudo de días.

    Trabaja en tiempo absoluto: el ORB, la ventana de la rotura y la salida por tiempo pueden pasar de medianoche (`deadline` y
    `exit_min` mayores de 1440). Solo cuentan los ORB con todas sus velas (así se saltan fines de semana, festivos y la pausa
    diaria de las 17:00).
    """
    ny = df["ts"].to_numpy() - AHEAD
    h, l, c, sp = (df[k].to_numpy() for k in ("high", "low", "close", "spread"))
    need = p.minutes // BAR
    rows, funnel = [], {"días": 0, "con ORB": 0, "con rotura": 0}
    for d in np.unique(ny // 86400):
        base = int(d) * 86400
        funnel["días"] += 1
        t0 = base + p.start * 60
        i0, i1 = np.searchsorted(ny, (t0, t0 + p.minutes * 60))
        if i1 - i0 != need or ny[i0] != t0:
            continue
        hi, lo = float(h[i0:i1].max()), float(l[i0:i1].min())
        width = hi - lo
        if width <= 0:
            continue
        funnel["con ORB"] += 1
        j1 = np.searchsorted(ny, base + (p.deadline - BAR) * 60, "right")     # velas que cierran como tarde a la hora límite
        seg = c[i1:j1]
        broke = np.flatnonzero((seg > hi) | (seg < lo))
        if not len(broke):
            continue
        funnel["con rotura"] += 1
        hit = i1 + int(broke[0])
        long = c[hit] > hi
        if p.side != "ambos" and p.side != ("long" if long else "short"):
            continue
        entry = float(c[hit])
        stop = lo - p.buffer * width if long else hi + p.buffer * width
        risk = abs(entry - stop)
        target = entry + p.rr * risk if long else entry - p.rr * risk
        k0, k1 = hit + 1, int(np.searchsorted(ny, base + (p.exit_min - BAR) * 60, "right"))
        result, gross, last = "tiempo", 0.0, hit
        if k1 > k0:
            hs, ls = h[k0:k1], l[k0:k1]
            stops = np.flatnonzero(ls <= stop if long else hs >= stop)
            targets = np.flatnonzero(hs >= target if long else ls <= target)
            first_stop = int(stops[0]) if len(stops) else None
            first_target = int(targets[0]) if len(targets) else None
            if first_stop is not None and (first_target is None or first_stop <= first_target):   # en la misma vela, el stop
                result, gross, last = "stop", -1.0, k0 + first_stop
            elif first_target is not None:
                result, gross, last = "objetivo", p.rr, k0 + first_target
            else:
                last = k1 - 1
        if result == "tiempo":
            gross = ((c[last] - entry) if long else (entry - c[last])) / risk
        cost = float(sp[hit]) / risk
        rows.append({"día": pd.Timestamp(base, unit="s").date(), "día semana": DAYS[int((d + 3) % 7)],
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
    first_scan, limit, last_bar = hhmm(base.start + base.minutes), hhmm(base.deadline), hhmm(base.deadline - BAR)
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
           f"- Días con mercado: {funnel['días']}; con todas las velas del ORB: {funnel['con ORB']}; con rotura antes de las {limit}: "
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


# -- rejilla de ORB -----------------------------------------------------------------------------------
def verdict_of(t: pd.DataFrame) -> dict:
    """Cifras y criterios de un ORB (los mismos de la variante principal)."""
    s, g = summary(t), summary(t, "R bruto")
    n = s.get("operaciones", 0)
    if not n:
        return {"ops": 0, "pasa": False}
    h1, h2 = halves(t)
    s1, s2 = summary(h1), summary(h2)
    m1, m2 = s1.get("R medio", float("nan")), s2.get("R medio", float("nan"))
    ok = n >= MIN_TRADES and s["R medio"] > MIN_MEAN and s["estadístico t"] > MIN_T and m1 > 0 and m2 > 0
    return {"ops": n, "acierto %": s["win rate %"], "R neto": s["R medio"], "t": s["estadístico t"], "R total": s["R total"],
            "PF": s["profit factor"], "máx. DD": s["máx. drawdown (R)"], "R bruto": g["R medio"], "t bruto": g["estadístico t"],
            "coste (R)": float(t["coste (R)"].mean()), "ancho ORB %": float(t["ancho ORB %"].mean()),
            "R neto 1.ª mitad": m1, "R neto 2.ª mitad": m2, "pasa": ok, "Bonferroni": ok and s["estadístico t"] > BONFERRONI_T,
            "R neto long": summary(t[t["dirección"] == "long"]).get("R medio", float("nan")),
            "R neto short": summary(t[t["dirección"] == "short"]).get("R medio", float("nan"))}


def _f(v, fmt: str) -> str:
    return "-" if v is None or (isinstance(v, float) and np.isnan(v)) else format(v, fmt)


def orb_section(df: pd.DataFrame, p: Params) -> tuple[str, dict]:
    """Apartado de un ORB en el fichero de su hora, y su fila para el resumen."""
    t, funnel = trades(df, p)
    v = verdict_of(t)
    end, limit = hhmm(p.start + p.minutes), hhmm(p.deadline)
    head = (f"### ORB {hhmm(p.start)}–{end}\n\nRotura con cuerpo desde las {end} hasta las {limit}"
            f"{' (día siguiente)' if p.deadline >= 1440 else ''}; a esa hora se cierra. ORB completos: {funnel['con ORB']}; "
            f"con rotura: {funnel['con rotura']}.\n")
    if not v["ops"]:
        return head + "\nSin operaciones.\n", v
    h1, h2 = halves(t)
    res = t["resultado"].value_counts()
    lines = [head, f"**{'Pasa' if v['pasa'] else 'No pasa'} los criterios**"
             + (" y supera el umbral corregido por comparaciones múltiples." if v["Bonferroni"] else ".")
             + f" Coste medio {v['coste (R)']:.3f} R; ancho medio del ORB {v['ancho ORB %']:.2f} %; cómo terminan: objetivo "
             f"{int(res.get('objetivo', 0))}, stop {int(res.get('stop', 0))}, por tiempo {int(res.get('tiempo', 0))}.", "",
             table([row("Todas (con spread)", t), row("Sin costes", t, "R bruto"),
                    row("Long", t[t["dirección"] == "long"]), row("Short", t[t["dirección"] == "short"]),
                    row("1.ª mitad", h1), row("2.ª mitad", h2)]), "",
             "Por año (R neto medio y operaciones): " + ", ".join(
                 f"{y} {summary(g)['R medio']:+.3f} ({len(g)})" for y, g in t.groupby(pd.to_datetime(t["entrada (NY)"]).dt.year)) + ".", "",
             "Sensibilidad (R neto medio y t): " + ", ".join(
                 f"{name} {summary(tt).get('R medio', 0):+.3f} (t {summary(tt).get('estadístico t', 0):+.2f})"
                 for name, tt in (("colchón 0 %", trades(df, replace(p, buffer=0.0))[0]),
                                  ("colchón 50 %", trades(df, replace(p, buffer=0.5))[0]),
                                  ("objetivo 1,5:1", trades(df, replace(p, rr=1.5))[0]),
                                  ("objetivo 2:1", trades(df, replace(p, rr=2.0))[0]))) + ".", ""]
    return "\n".join(lines), v


def run_grid(sym: str, df: pd.DataFrame, minutes: int, window: int, buffer: float) -> Path:
    """Los 96 ORB de `minutes` minutos: un fichero por hora (sus 4 ORB) y un RESUMEN.md con la clasificación."""
    folder = Path(str(GRID_DIR).format(minutes))
    folder.mkdir(parents=True, exist_ok=True)
    ny = df["ts"].to_numpy() - AHEAD
    first, last = pd.Timestamp(int(ny[0]), unit="s"), pd.Timestamp(int(ny[-1]), unit="s")
    rules = (f"Reglas: ORB de {minutes} min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde "
             f"{window // 60} h después de su final; stop en el extremo opuesto ± {buffer:.0%} del ancho; objetivo 1:1; a las "
             f"{window // 60} h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). {sym} de PUPrime, del "
             f"{first:%d/%m/%Y} al {last:%d/%m/%Y}, hora de Nueva York.")
    summary_rows = []
    for hour in range(24):
        parts = [f"# ORB de {minutes} min de las {hour:02d}:00 en {sym} (M5, PUPrime)", "", rules, "",
                 f"Criterios (fijados antes de ver resultados): al menos {MIN_TRADES} operaciones, R neto medio > +{MIN_MEAN} con "
                 f"t > {MIN_T}, y R neto medio positivo en las dos mitades del histórico.", ""]
        compare = []
        for quarter in range(0, 60, GRID_STEP):
            start = hour * 60 + quarter
            p = Params(buffer=buffer, start=start, minutes=minutes, deadline=start + minutes + window,
                       exit_min=start + minutes + window)
            text, v = orb_section(df, p)
            parts.append(text)
            summary_rows.append({"ORB": hhmm(start), "minutos": minutes, **v})
            compare.append([f"{hhmm(start)}–{hhmm(start + minutes)}", v["ops"], _f(v.get("acierto %"), ".1f"),
                            _f(v.get("R neto"), "+.3f"), _f(v.get("t"), "+.2f"), _f(v.get("R bruto"), "+.3f"),
                            _f(v.get("coste (R)"), ".3f"), "sí" if v["pasa"] else "no"])
            print(f"  ORB {hhmm(start)} ({minutes} min): {v['ops']} ops, R neto {_f(v.get('R neto'), '+.3f')}, t {_f(v.get('t'), '+.2f')}",
                  flush=True)
        parts[6:6] = ["## Los 4 ORB de esta hora", "",
                      table(compare, ["ORB", "Ops", "Acierto %", "R neto", "t", "Sin costes", "Coste (R)", "Pasa"]), "",
                      "## Detalle", ""]
        (folder / f"ORB_{hour:02d}h.md").write_text("\n".join(parts) + "\n", encoding="utf-8")
    grid = pd.DataFrame(summary_rows)
    grid.to_csv(ROOT / "analisis" / f"orbs_{minutes}m_resumen.csv", index=False)
    (folder / "RESUMEN.md").write_text(grid_summary(grid, minutes, rules) + "\n", encoding="utf-8")
    return folder


def grid_summary(grid: pd.DataFrame, minutes: int, rules: str) -> str:
    played = grid[grid["ops"] > 0]
    n = len(played)
    pos, neg = int((played["t"] > MIN_T).sum()), int((played["t"] < -MIN_T).sum())
    passed, bonf = played[played["pasa"]], played[played["Bonferroni"]]

    def rows_of(frame: pd.DataFrame) -> list:
        return [[r["ORB"], r["ops"], f"{r['acierto %']:.1f}", f"{r['R neto']:+.3f}", f"{r['t']:+.2f}", f"{r['R bruto']:+.3f}",
                 f"{r['coste (R)']:.3f}", f"{r['R neto 1.ª mitad']:+.3f}", f"{r['R neto 2.ª mitad']:+.3f}",
                 f"{r['R neto long']:+.3f}", f"{r['R neto short']:+.3f}", "sí" if r["pasa"] else "no"] for _, r in frame.iterrows()]

    head = ["ORB", "Ops", "Acierto %", "R neto", "t", "Sin costes", "Coste", "1.ª mitad", "2.ª mitad", "Long", "Short", "Pasa"]
    # elegir con la 1.ª mitad y medir en la 2.ª
    pick = played.sort_values("R neto 1.ª mitad", ascending=False).head(5)
    out = [f"# Resumen de los ORB de {minutes} min en NAS100", "", rules, "",
           "## Lo importante", "",
           f"- ORB con operaciones: {n}. Con t > {MIN_T}: **{pos}**; con t < −{MIN_T}: {neg}. Solo por azar se esperarían unos "
           f"{0.025 * n:.1f} de cada lado.",
           f"- Pasan los criterios (≥ {MIN_TRADES} operaciones, R neto > +{MIN_MEAN} con t > {MIN_T} y las dos mitades en "
           f"positivo): **{len(passed)}**" + (f" ({', '.join(passed['ORB'])})" if len(passed) else "") + ".",
           f"- Superan además el umbral corregido por comparaciones múltiples (t > {BONFERRONI_T}): **{len(bonf)}**"
           + (f" ({', '.join(bonf['ORB'])})" if len(bonf) else "") + ".",
           f"- R neto medio de todos los ORB: {played['R neto'].mean():+.3f} R; sin costes: {played['R bruto'].mean():+.3f} R; coste "
           f"medio {played['coste (R)'].mean():.3f} R.", "",
           "## Elegidos con la 1.ª mitad, medidos en la 2.ª", "",
           "Los 5 mejores ORB por su R neto en la 1.ª mitad del histórico, y lo que hicieron después sin haberlos visto. Si la ventaja "
           "fuera real, la 2.ª mitad seguiría en positivo.", "",
           table(rows_of(pick), head), "",
           "## Los 10 mejores por t (todo el histórico)", "",
           table(rows_of(played.sort_values("t", ascending=False).head(10)), head), "",
           "## Todos los ORB", "",
           f"Ficheros por hora en esta carpeta (`ORB_HHh.md`). Ordenados por hora de inicio:", "",
           table(rows_of(grid[grid["ops"] > 0]), head)]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--perfil", default="puprime")
    ap.add_argument("--simbolo", default="NAS100")
    ap.add_argument("--colchon", type=float, default=0.2, help="colchón del stop en anchos del ORB (0,2 = 20 %%)")
    ap.add_argument("--sesion", choices=list(SESSIONS), default="0100", help="sesión del ORB (por defecto la 01:00)")
    ap.add_argument("--rejilla", type=int, choices=(15, 30, 45, 60), help="prueba todos los ORB de esa duración (min), de 00:00 a 23:45")
    ap.add_argument("--ventana", type=int, default=GRID_WINDOW, help="rejilla: minutos que vale la rotura desde el final del ORB")
    ap.add_argument("--cache", action="store_true", help="reutiliza las velas guardadas en analisis/orb_nasdaq_m5.pkl")
    args = ap.parse_args()
    sym, df = load(args.perfil, args.simbolo, args.cache)
    if args.rejilla:
        folder = run_grid(sym, df, args.rejilla, args.ventana, args.colchon)
        print(f"\nRejilla: {folder}")
        return
    _, start, deadline = SESSIONS[args.sesion]
    text = report(sym, df, Params(buffer=args.colchon, start=start, deadline=deadline, exit_min=deadline), args.sesion)
    doc = Path(str(DOC).format(args.sesion))
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(text + "\n", encoding="utf-8")
    print(text)
    print(f"\nInforme: {doc}\nOperaciones: {str(CSV).format(args.sesion)}")


if __name__ == "__main__":
    main()
