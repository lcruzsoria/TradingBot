"""Resume los backtests en el JSON que muestra la ventana Backtest (skill Stats).

Lee lo que generan `scripts/backtest_patrones.py` (un Excel por grupo de mercados), `scripts/comparativa_mercados.py` y
`scripts/lunes_hora_fija.py` (la estrategia Calendario, `analisis/lunes_hora_fija.pkl`), y escribe
`tradingbot/skills/stats/backtest.json`: un fichero pequeño que sí se sube a git, para que la ventana funcione sin MT5 y sin la
carpeta `analisis/`. De los patrones copia las cifras de las hojas; de Calendario calcula las mismas cifras a partir de las
operaciones del pkl, con la configuración del bloque CALENDARIO de tradingbot.env. Las curvas se reducen a unos cientos de puntos.

Uso (desde la raíz del proyecto, después de regenerar los Excel):
    uv run --with openpyxl python scripts/exportar_backtest.py
    uv run --with openpyxl python scripts/exportar_backtest.py --analisis ruta/a/analisis
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tradingbot.envconfig import load as load_env                    # noqa: E402

OUT = ROOT / "tradingbot" / "skills" / "stats" / "backtest.json"
GROUPS = (("indices", "Índices americanos", "backtest_indices.xlsx"), ("forex", "Forex", "backtest_forex.xlsx"),
          ("oro", "Oro", "backtest_oro.xlsx"), ("cripto", "Cripto", "backtest_cripto.xlsx"))
CURVE_POINTS = 160                         # puntos por curva de capital
# Columnas de las hojas de resultados -> clave corta del JSON
METRICS = {"operaciones": "n", "win rate %": "wr", "R medio": "mean", "R total": "total", "profit factor": "pf",
           "ganancia media (R)": "avg_win", "pérdida media (R)": "avg_loss", "máx. drawdown (R)": "dd",
           "racha perdedora máx.": "streak", "estadístico t": "t"}
DROP = {"mejor (R)", "peor (R)", "desv. típica (R)"}           # no se muestran: fuera del JSON para que pese menos


def clean(v):
    """Valor de una celda listo para JSON: fechas en ISO, decimales a 3 cifras y NaN / infinito como None."""
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d")
    if isinstance(v, float):
        return None if math.isnan(v) or math.isinf(v) else round(v, 3)
    return v


def rows(wb, sheet: str) -> list[dict]:
    """Filas de una hoja como diccionarios (cabecera de la primera fila; las métricas con su clave corta)."""
    if sheet not in wb.sheetnames:
        return []
    it = wb[sheet].iter_rows(values_only=True)
    head = list(next(it, ()))
    return [{METRICS.get(h, h): clean(v) for h, v in zip(head, r) if h not in DROP} for r in it if any(v is not None for v in r)]


def curves(wb) -> dict[str, list]:
    """Curva de R acumulado por «patrón|filtro», reducida a CURVE_POINTS puntos [fecha, R acumulado] (siempre con el último)."""
    if "Curva de capital (R)" not in wb.sheetnames:
        return {}
    raw: dict[str, list] = {}
    it = wb["Curva de capital (R)"].iter_rows(values_only=True)
    next(it, None)
    for pattern, filt, when, _r, acc in it:
        if pattern is None or when is None:
            continue
        raw.setdefault(f"{pattern}|{filt}", []).append((when, acc))
    out = {}
    for key, pts in raw.items():
        step = max(1, len(pts) // CURVE_POINTS)
        keep = pts[::step]
        if keep[-1] is not pts[-1]:
            keep.append(pts[-1])
        out[key] = [[w.strftime("%Y-%m-%d"), round(float(a), 2)] for w, a in keep]
    return out


def group(path: Path) -> dict:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    data = {
        "metodologia": [[r["tema"], r["explicación"]] for r in rows(wb, "Metodología")],
        "datos": rows(wb, "Datos"),
        "resumen": rows(wb, "Resumen"),
        "por_mercado": rows(wb, "Por mercado"),
        "por_zona": rows(wb, "Por zona"),
        "por_direccion": rows(wb, "Por dirección"),
        "por_anio": rows(wb, "Por año"),
        "por_hora": rows(wb, "Por hora"),
        "por_dia": rows(wb, "Por día semana"),
        "mitades": rows(wb, "Mitades (robustez)"),
        "sensibilidad": rows(wb, "Sensibilidad"),
        "mejoras": rows(wb, "Mejoras (stop y RR)"),
        "resultados": rows(wb, "Resultados y MAE-MFE"),
        "embudo": rows(wb, "Embudo"),
        "curvas": curves(wb),
    }
    wb.close()
    return data


# -- Calendario (largos a hora fija) -----------------------------------------------------------------
CAL_PATTERN = "Calendario"
CAL_DAYS = ("lunes", "martes", "miércoles", "jueves", "viernes")
CAL_EXIT_HOUR = 10                          # el pkl siempre cierra por tiempo a las 10:00 NY


def stats(net: pd.Series) -> dict:
    """Las mismas cifras que las hojas del backtest de patrones, a partir del R neto de cada operación (en orden)."""
    n = len(net)
    if not n:
        return {"n": 0}
    won, lost = net[net > 0], net[net < 0]
    acc = net.cumsum().to_numpy()
    dd = float((acc - np.maximum.accumulate(np.maximum(acc, 0.0))).min())
    streak = run = 0
    for v in net:
        run = run + 1 if v <= 0 else 0
        streak = max(streak, run)
    sd = net.std()
    return {"n": n, "wr": 100 * len(won) / n, "mean": net.mean(), "total": net.sum(),
            "pf": won.sum() / -lost.sum() if len(lost) and lost.sum() else None,
            "avg_win": won.mean() if len(won) else None, "avg_loss": lost.mean() if len(lost) else None,
            "dd": min(dd, 0.0), "streak": streak, "t": net.mean() / (sd / math.sqrt(n)) if n > 2 and sd > 0 else None}


def row(net: pd.Series, **extra) -> dict:
    return {k: clean(float(v)) if isinstance(v, (float, np.floating)) else v for k, v in {**extra, **stats(net)}.items()}


def calendar(path: Path) -> dict:
    """Grupo «Calendario» con la configuración del bot (tradingbot.env) sobre las operaciones de scripts/lunes_hora_fija.py."""
    env = load_env().section("calendario")
    stop = float(env.get_float("STOP_PCT", 0.5))
    rr = float(env.get_float("RR", 2.0))
    hour = int(env.get("ENTRY_HOUR", "02:00").split(":")[0])
    days = [CAL_DAYS.index(d.lower().replace("miercoles", "miércoles")) for d in env.get_list("DAYS", ["lunes"])]
    symbols = env.get_list("SYMBOLS", ["NAS100", "DJ30"])
    df = pd.read_pickle(path)
    df = df[df["stop %"] > 0].copy()                                  # las filas con stop 0 son la deriva pura, en %
    df["net"] = df["R bruto"] - df["coste"]
    df["sym"] = df["mercado"].str.split(".").str[0].str.lower()
    df = df.sort_values(["día", "mercado"])
    if not ((df["stop %"] == stop) & (df["RR"] == rr) & (df["hora"] == hour)).any():
        raise SystemExit(f"Calendario: el pkl no tiene stop {stop} % / RR {rr} / {hour:02d}:00; ejecuta scripts/lunes_hora_fija.py")
    mine = df["sym"].isin([w.lower() for w in symbols])
    long_days = df["dow"].isin(days) & (df["dir"] == "long")
    same = (df["stop %"] == stop) & (df["RR"] == rr)
    filters = {"config. del bot": mine, "los 4 índices": df["mercado"].notna()}
    names = {"config. del bot": f"{', '.join(symbols)} (el bot)", "los 4 índices": "Los 4 índices"}
    out = {k: [] for k in ("resumen", "por_mercado", "por_direccion", "por_anio", "por_hora", "por_dia", "mitades",
                           "sensibilidad", "resultados")}
    out["curvas"] = {}
    for filt, scope in filters.items():
        sel = df[same & (df["hora"] == hour) & long_days & scope]
        base = dict(patrón=CAL_PATTERN, filtro=filt)
        out["resumen"].append(row(sel["net"], **base))
        for m, g in sel.groupby("mercado"):
            out["por_mercado"].append(row(g["net"], mercado=m, **base))
        for y, g in sel.groupby("año"):
            out["por_anio"].append(row(g["net"], año=int(y), **base))
        half = len(sel) // 2
        out["mitades"] += [row(sel["net"].iloc[:half], mitad="1ª mitad", **base),
                           row(sel["net"].iloc[half:], mitad="2ª mitad", **base)]
        for d, g in df[same & scope & (df["hora"] == hour) & df["dow"].isin(days)].groupby("dir"):   # control: los cortos
            out["por_direccion"].append(row(g["net"], dirección=d, **base))
        for h, g in df[same & scope & long_days].groupby("hora"):
            out["por_hora"].append(row(g["net"], **{"hora (NY)": int(h)}, **base))
        for d, g in df[same & scope & (df["hora"] == hour) & (df["dir"] == "long")].groupby("dow"):  # control: otros días
            out["por_dia"].append(row(g["net"], **{"día semana": CAL_DAYS[int(d)]}, **base))
        for (sp, r), g in df[(df["hora"] == hour) & long_days & scope].groupby(["stop %", "RR"]):
            label = f"stop {sp:g} % · RR {r:g}" + ("  (el bot)" if (sp, r) == (stop, rr) else "")
            out["sensibilidad"].append(row(g["net"], variante=label, **base))
        out["sensibilidad"].append(row(sel["R bruto"], variante=f"stop {stop:g} % · RR {rr:g} sin costes (R bruto)", **base))
        acc = sel.groupby("día")["net"].sum().cumsum()
        step = max(1, len(acc) // CURVE_POINTS)
        pts = [[d.strftime("%Y-%m-%d"), round(float(v), 2)] for d, v in list(acc.items())[::step]]
        if len(acc) and pts[-1][0] != acc.index[-1].strftime("%Y-%m-%d"):
            pts.append([acc.index[-1].strftime("%Y-%m-%d"), round(float(acc.iloc[-1]), 2)])
        out["curvas"][f"{CAL_PATTERN}|{filt}"] = pts
        if filt == "config. del bot":
            res = np.where(sel["R bruto"] <= -1, "stop", np.where(sel["R bruto"] >= rr, "objetivo", "tiempo"))
            out["resultados"].append({"patrón": CAL_PATTERN, "objetivo": int((res == "objetivo").sum()),
                                      "stop": int((res == "stop").sum()), "tiempo": int((res == "tiempo").sum()), "n": len(sel),
                                      "MAE medio (R)": None, "MFE medio (R)": None, "velas medias en la operación": None,
                                      "riesgo medio %": stop, "coste medio (R)": clean(float(sel["coste"].mean()))})
    when = df.groupby("mercado")["día"].agg(["min", "max"])
    out["datos"] = [{"mercado": m, "velas M15": None, "desde (NY)": r["min"].strftime("%Y-%m-%d"),
                     "hasta (NY)": r["max"].strftime("%Y-%m-%d"), "TBR evaluadas": None} for m, r in when.iterrows()]
    day_names = ", ".join(CAL_DAYS[d] for d in days)
    out["metodologia"] = [
        ["Qué es", f"Estrategia de la skill Calendario: largo a mercado los {day_names} a las {hour:02d}:00 NY, sin patrones ni "
                   "TBR (scripts/lunes_hora_fija.py)."],
        ["Operación", f"Stop al {stop:g} % del precio, objetivo a {rr:g} veces el stop y cierre por tiempo a las "
                      f"{CAL_EXIT_HOUR}:00 NY si no se toca ninguno. Stop primero si caben los dos en una vela."],
        ["Configuración", "La del bloque CALENDARIO de tradingbot.env al exportar (mercados, días, hora, stop y RR)."],
        ["Costes", "Spread real de MT5 en la vela de la entrada, una vez por operación."],
        ["Controles", "«Por lado» compara con los cortos y «Por día» con los demás días, con la misma hora, stop y RR: si solo "
                      "gana el largo del día elegido, la ventaja es de calendario."],
        ["Sensibilidad", "La rejilla de stops (0,15-0,75 %) y RR (1-2) del script, con la misma hora y días."],
        ["Límites", "Se eligió la mejor combinación de muchas probadas: parte de la ventaja puede ser azar."]]
    out.update(key="calendario", nombre="Calendario", fichero=path.name, patrones=[CAL_PATTERN], filtros=names,
               descripcion=f"largos a hora fija ({day_names} {hour:02d}:00 NY) · stop {stop:g} % · RR {rr:g} · spread real",
               actualizado=datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d"))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--analisis", type=Path, default=ROOT / "analisis", help="carpeta con los Excel (por defecto analisis/)")
    ap.add_argument("--salida", type=Path, default=OUT)
    args = ap.parse_args()

    out = {"generado": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "grupos": [], "comparativa": {}}
    for key, name, file in GROUPS:
        path = args.analisis / file
        if not path.exists():
            print(f"  (sin {file}: se omite {name})")
            continue
        g = group(path)
        g.update(key=key, nombre=name, fichero=file,
                 actualizado=datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d"))
        out["grupos"].append(g)
        print(f"  {name}: {sum(r['n'] or 0 for r in g['resumen'] if r['patrón'] == 'Ambos' and r['filtro'] == 'sin filtro de sesgo')} "
              f"operaciones, {len(g['curvas'])} curvas")
    cal = args.analisis / "lunes_hora_fija.pkl"
    if cal.exists():
        g = calendar(cal)
        out["grupos"].append(g)
        print(f"  Calendario: {g['resumen'][0]['n']} operaciones con la configuración del bot")
    else:
        print("  (sin lunes_hora_fija.pkl: se omite Calendario)")
    comp = args.analisis / "comparativa_mercados.xlsx"
    if comp.exists():
        wb = openpyxl.load_workbook(comp, read_only=True, data_only=True)
        out["comparativa"] = {"bot": rows(wb, "Lo que opera el bot"), "sin_filtro": rows(wb, "Sin filtro"),
                              "por_grupo": rows(wb, "Por grupo"), "notas": [r["nota"] for r in rows(wb, "Notas")]}
        wb.close()
    if not out["grupos"]:
        raise SystemExit(f"No hay Excel de backtest en {args.analisis}: ejecuta antes scripts/backtest_patrones.py")
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"JSON: {args.salida} ({args.salida.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
