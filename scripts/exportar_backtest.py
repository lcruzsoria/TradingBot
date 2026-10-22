"""Exporta las operaciones de los backtests al fichero que muestra la ventana Backtest (skill Stats).

Lee lo que generan `scripts/backtest_patrones.py` (por cada perfil de MT5, en `analisis/<perfil>/`, un Excel por grupo de
mercados: hoja «Operaciones» y las hojas que no se pueden recalcular, como las mejoras de stop y RR o el embudo), `scripts/comparativa_mercados.py` (las notas) y
`scripts/lunes_hora_fija.py` (la estrategia Calendario, `analisis/lunes_hora_fija.pkl`, con la configuración del bloque
CALENDARIO de tradingbot.env), y escribe `tradingbot/skills/stats/backtest.json.gz`: cada operación en columnas, comprimido, para
que la ventana funcione sin MT5 ni la carpeta `analisis/` y pueda recalcularlo todo al filtrar por años u horas.

Comprueba que las cifras que calcula la ventana coinciden con la hoja Resumen de cada Excel (el drawdown puede variar unas
décimas de R por el orden entre operaciones que cierran en la misma vela).

Cada perfil (puprime, metaquotes) y Calendario son un «perfil» en la ventana Backtest: se elige arriba, antes de los mercados.

Uso (desde la raíz del proyecto, después de regenerar los backtests):
    uv run --with openpyxl python scripts/exportar_backtest.py
    uv run --with openpyxl python scripts/exportar_backtest.py --analisis ruta/a/analisis
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tradingbot.envconfig import load as load_env                                     # noqa: E402
from tradingbot.skills.stats.backtest import DAYS, Group                              # noqa: E402

OUT = ROOT / "tradingbot" / "skills" / "stats" / "backtest.json.gz"
PROFILES = (("puprime", "PUPrime"), ("metaquotes", "MetaQuotes"))      # carpetas analisis/<perfil>/
GROUPS = (("indices", "Índices americanos", "backtest_indices.xlsx"), ("forex", "Forex", "backtest_forex.xlsx"),
          ("oro", "Oro", "backtest_oro.xlsx"), ("cripto", "Cripto", "backtest_cripto.xlsx"))
STATIC = {"Metodología": "metodologia", "Datos": "datos", "Mejoras (stop y RR)": "mejoras", "Embudo": "embudo"}
# Columna del Excel -> columna corta de cada operación (decimales)
FLOAT_COLS = {"R neto": "r", "coste (R)": "k", "R neto TP 1R": "tp1", "R neto TP 1.5R": "tp15", "R neto TP 2R": "tp2",
              "R neto TP 2.5R": "tp25", "R neto TP 3R": "tp3", "R neto 12 h": "h12", "R neto 48 h": "h48",
              "MAE (R)": "mae", "MFE (R)": "mfe", "riesgo %": "rk"}
EPOCH = pd.Timestamp("1970-01-01")


def clean(v):
    """Valor listo para JSON: fechas en ISO, decimales a 3 cifras y NaN / infinito como None."""
    if isinstance(v, (datetime, pd.Timestamp)):
        return v.strftime("%Y-%m-%d")
    if isinstance(v, (float, np.floating)):
        return None if math.isnan(v) or math.isinf(v) else round(float(v), 3)
    if isinstance(v, np.integer):
        return int(v)
    return v


def minutes(s: pd.Series) -> list[int]:
    """Minutos desde 1970 de una columna de fechas (hora de Nueva York, sin zona)."""
    return ((pd.to_datetime(s) - EPOCH) // pd.Timedelta(minutes=1)).astype(np.int64).tolist()


def codes(s: pd.Series, names: list[str]) -> list[int]:
    return s.map({n: i for i, n in enumerate(names)}).astype(int).tolist()


def floats(s: pd.Series, digits: int = 3) -> list:
    return [None if math.isnan(v) or math.isinf(v) else round(float(v), digits) for v in s.to_numpy(dtype=float)]


def sheet(path: Path, name: str) -> list[dict]:
    df = pd.read_excel(path, sheet_name=name)
    return [{k: clean(v) for k, v in row.items()} for row in df.to_dict("records")]


# -- patrones ----------------------------------------------------------------------------------------
def pattern_group(key: str, name: str, path: Path, profile: str, profile_name: str) -> dict:
    ops = pd.read_excel(path, sheet_name="Operaciones",
                        usecols=lambda c: not str(c).startswith(("R bruto k", "R neto k", "cierre k")))
    cats = {"m": sorted(ops["mercado"].unique()), "p": ["Continuación", "Reversión"],
            "z": sorted(ops["zona"].unique()), "o": ["objetivo", "stop", "breakeven", "tiempo"], "s": ["a favor", "en contra", "sin sesgo"]}
    overlap = ops["solapada (todas)"].astype(bool).astype(int) + 2 * ops["solapada (GO de Cortex)"].astype(bool).astype(int)
    cols = {"m": codes(ops["mercado"], cats["m"]), "p": codes(ops["patrón"], cats["p"]), "z": codes(ops["zona"], cats["z"]),
            "o": codes(ops["resultado"], cats["o"]), "s": codes(ops["sesgo vs operación"], cats["s"]),
            "d": (ops["dirección"] == "short").astype(int).tolist(), "f": overlap.tolist(),
            "e": minutes(ops["entrada (NY)"]), "x": minutes(ops["cierre (NY)"]), "v": ops["velas"].astype(int).tolist()}
    cols.update({short: floats(ops[col], 6 if short in ("r", "k") else 3) for col, short in FLOAT_COLS.items()})
    out = {"key": f"{profile}:{key}", "nombre": name, "tipo": "patrones", "perfil": profile, "perfil_nombre": profile_name,
           "fichero": path.name, "cats": cats, "ops": cols,
           "actualizado": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")}
    for sheet_name, short in STATIC.items():
        rows = sheet(path, sheet_name)
        out[short] = [[r["tema"], r["explicación"]] for r in rows] if short == "metodologia" else rows
    for r in out["mejoras"]:
        r["n"], r["wr"] = r.pop("operaciones", None), r.pop("win rate %", None)
    check(Group(out["key"], f"{profile_name} · {name}", out), pd.read_excel(path, sheet_name="Resumen"))
    return out


def check(group: Group, summary: pd.DataFrame) -> None:
    """Las cifras que calculará la ventana deben coincidir con la hoja Resumen del Excel."""
    worst = 0.0
    for _, row in summary.iterrows():
        got = group.view(row["patrón"], row["filtro"]).main.stats()
        if got["n"] != row["operaciones"] or abs(got["total"] - row["R total"]) > 0.02 or abs(got["wr"] - row["win rate %"]) > 500.5 / got["n"]:
            # (el acierto admite unas pocas operaciones: el Excel cuenta como ganadas las que con spread de 2 R dan +1e-13 R, que aquí son empates)
            raise SystemExit(f"{group.name}: {row['patrón']} / {row['filtro']} no cuadra con la hoja Resumen "
                             f"({got['n']} ops, {got['total']:.3f} R frente a {row['operaciones']}, {row['R total']:.3f} R)")
        worst = max(worst, abs(got["dd"] - row["máx. drawdown (R)"]))
    print(f"  {group.name}: {len(group.ops)} operaciones; cuadra con el Resumen (drawdown ±{worst:.2f} R)")


# -- Calendario (largos a hora fija) -----------------------------------------------------------------
CAL_EXIT_HOUR = 10                          # el pkl siempre cierra por tiempo a las 10:00 NY


def calendar_group(path: Path) -> dict:
    """Las entradas de scripts/lunes_hora_fija.py con el stop y RR de tradingbot.env (todos los días, horas y lados, para los
    controles) y la rejilla de stops y RR de los largos en los días configurados."""
    env = load_env().section("calendario")
    stop = float(env.get_float("STOP_PCT", 0.5))
    rr = float(env.get_float("RR", 2.0))
    hour = int(env.get("ENTRY_HOUR", "02:00").split(":")[0])
    days = [DAYS.index(d.lower().replace("miercoles", "miércoles")) for d in env.get_list("DAYS", ["lunes"])]
    symbols = env.get_list("SYMBOLS", ["NAS100", "DJ30"])
    df = pd.read_pickle(path)
    df = df[df["stop %"] > 0]                                         # las filas con stop 0 son la deriva pura, en %
    df = df.assign(net=df["R bruto"] - df["coste"])
    key = ["mercado", "día", "hora", "dir"]
    base = df[(df["stop %"] == stop) & (df["RR"] == rr)].sort_values(key).reset_index(drop=True)
    if base.empty:
        raise SystemExit(f"Calendario: el pkl no tiene stop {stop} % / RR {rr}; ejecuta scripts/lunes_hora_fija.py")
    grid = df[df["dow"].isin(days) & (df["dir"] == "long")]
    combos = sorted(grid.groupby(["stop %", "RR"]).groups)
    wide = grid.pivot_table(index=key, columns=["stop %", "RR"], values="net").reindex(columns=combos)
    wide = wide.reindex(pd.MultiIndex.from_frame(base[key]))
    markets = sorted(base["mercado"].unique())
    day = pd.to_datetime(base["día"])
    res = np.where(base["R bruto"] <= -1, "stop", np.where(base["R bruto"] >= rr, "objetivo", "tiempo"))
    cats = {"m": markets, "o": ["objetivo", "stop", "tiempo"]}
    cols = {"m": codes(base["mercado"], markets), "d": (base["dir"] == "short").astype(int).tolist(),
            "o": codes(pd.Series(res), cats["o"]), "e": minutes(day + pd.to_timedelta(base["hora"], unit="h")),
            "x": minutes(day + pd.Timedelta(hours=CAL_EXIT_HOUR)), "r": floats(base["net"], 6), "k": floats(base["coste"], 6)}
    labels = []
    for i, (sp, r) in enumerate(combos):
        cols[f"g{i}"] = floats(wide[(sp, r)])
        labels.append(f"stop {sp:g} % · RR {r:g}" + ("  (el bot)" if (sp, r) == (stop, rr) else ""))
    mine = [m for m in markets if m.split(".")[0].lower() in [s.lower() for s in symbols]]
    day_names = ", ".join(DAYS[d] for d in days)
    when = base.groupby("mercado")["día"].agg(["min", "max"])
    print(f"  Calendario: {len(base)} entradas (todas las horas, días y lados), rejilla de {len(combos)} stops / RR")
    return {
        "key": "calendario", "nombre": "Calendario", "tipo": "calendario", "perfil": "calendario", "perfil_nombre": "Calendario",
        "fichero": path.name, "cats": cats, "ops": cols,
        "patrones": ["Calendario"], "filtros": {"config. del bot": f"{', '.join(symbols)} (el bot)", "los 4 índices": "Los 4 índices"},
        "alcance": {"config. del bot": mine, "los 4 índices": markets},
        "dias": days, "hora": hour, "stop": stop, "rr": rr, "rejilla": labels,
        "descripcion": f"largos a hora fija ({day_names} {hour:02d}:00 NY) · stop {stop:g} % · RR {rr:g} · spread real",
        "actualizado": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d"),
        "datos": [{"mercado": m, "velas M15": None, "desde (NY)": r["min"].strftime("%Y-%m-%d"),
                   "hasta (NY)": r["max"].strftime("%Y-%m-%d"), "TBR evaluadas": None} for m, r in when.iterrows()],
        "metodologia": [
            ["Qué es", f"Estrategia de la skill Calendario: largo a mercado los {day_names} a las {hour:02d}:00 NY, sin patrones "
                       "ni TBR (scripts/lunes_hora_fija.py)."],
            ["Operación", f"Stop al {stop:g} % del precio, objetivo a {rr:g} veces el stop y cierre por tiempo a las "
                          f"{CAL_EXIT_HOUR}:00 NY si no se toca ninguno. Stop primero si caben los dos en una vela."],
            ["Configuración", "La del bloque CALENDARIO de tradingbot.env al exportar (mercados, días, hora, stop y RR)."],
            ["Costes", "Spread real de MT5 en la vela de la entrada, una vez por operación."],
            ["Controles", "«Por lado» compara con los cortos y «Por día» con los demás días, con la misma hora, stop y RR: si solo "
                          "gana el largo del día elegido, la ventaja es de calendario."],
            ["Horas", "Al elegir una hora en su histograma, la operación pasa a entrar a esa hora (00, 02, 05 u 08 NY)."],
            ["Sensibilidad", "La rejilla de stops (0,15-0,75 %) y RR (1-2) del script, con la misma entrada."],
            ["Límites", "Se eligió la mejor combinación de muchas probadas: parte de la ventaja puede ser azar."]]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--analisis", type=Path, default=ROOT / "analisis", help="carpeta con los backtests (por defecto analisis/)")
    ap.add_argument("--calendario", type=Path, default=None, help="pkl de Calendario (por defecto analisis/lunes_hora_fija.pkl)")
    ap.add_argument("--salida", type=Path, default=OUT)
    args = ap.parse_args()

    out = {"generado": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "grupos": [], "comparativa": {}}
    for profile, profile_name in PROFILES:
        for key, name, file in GROUPS:
            path = args.analisis / profile / file
            if path.exists():
                out["grupos"].append(pattern_group(key, name, path, profile, profile_name))
            else:
                print(f"  (sin {profile}/{file}: se omite {profile_name} · {name})")
    cal = args.calendario or args.analisis / "lunes_hora_fija.pkl"
    if cal.exists():
        out["grupos"].append(calendar_group(cal))
    else:
        print("  (sin lunes_hora_fija.pkl: se omite Calendario)")
    comp = args.analisis / "comparativa_mercados.xlsx"
    if comp.exists():
        bot = sheet(comp, "Lo que opera el bot")
        out["comparativa"] = {"notas": [r["nota"] for r in sheet(comp, "Notas")],
                              "notas_mercado": {r["mercado"]: r["nota"] for r in bot if r.get("nota")}}
    if not out["grupos"]:
        raise SystemExit(f"No hay backtests en {args.analisis}: ejecuta antes scripts/backtest_patrones.py")
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(out, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    args.salida.write_bytes(gzip.compress(raw, 9, mtime=0))
    print(f"Backtest: {args.salida} ({args.salida.stat().st_size / 1024:.0f} KB, {len(raw) / 1024:.0f} KB sin comprimir)")


if __name__ == "__main__":
    main()
