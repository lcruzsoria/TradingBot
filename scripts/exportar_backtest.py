"""Resume los Excel del backtest de patrones en el JSON que muestra la ventana Backtest (skill Stats).

Lee lo que generan `scripts/backtest_patrones.py` (un Excel por grupo de mercados) y `scripts/comparativa_mercados.py`, y escribe
`tradingbot/skills/stats/backtest.json`: un fichero pequeño que sí se sube a git, para que la ventana funcione sin MT5 y sin la
carpeta `analisis/`. No calcula nada nuevo: copia las cifras de las hojas y reduce las curvas de capital a unos cientos de puntos.

Uso (desde la raíz del proyecto, después de regenerar los Excel):
    uv run --with openpyxl python scripts/exportar_backtest.py
    uv run --with openpyxl python scripts/exportar_backtest.py --analisis ruta/a/analisis
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
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
