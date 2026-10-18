"""Resultados del backtest de los patrones (Continuación y Reversión) por grupo de mercados, para la ventana Backtest.

Los lee de `backtest.json`, que resume los Excel de `scripts/backtest_patrones.py` (lo genera `scripts/exportar_backtest.py`).
No calcula nada: da acceso a las filas por patrón y filtro y una lectura corta de cada resultado.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_FILE = Path(__file__).with_name("backtest.json")
PATTERNS = ("Ambos", "Continuación", "Reversión")
# Filtro del backtest -> nombre en la ventana. El primero es lo que hace el bot (GO de Cortex y una posición a la vez).
FILTERS = {"una posición a la vez (GO de Cortex)": "Lo que opera el bot",
           "a favor del sesgo (Cortex)": "A favor del sesgo",
           "sin filtro de sesgo": "Sin filtro",
           "en contra del sesgo": "En contra del sesgo",
           "sin sesgo / lateral": "Sin sesgo o lateral",
           "una posición a la vez (todas)": "Una posición (todas)"}
MAIN_FILTERS = tuple(FILTERS)[:3]                   # los que se eligen arriba; el resto sale en el libro «Por filtro»
BOT_FILTER = MAIN_FILTERS[0]
SIGNIFICANT_T = 2.0                                 # |t| por debajo de 2: no se distingue de cero


def verdict(t: float | None, mean: float | None) -> tuple[str, int]:
    """Lectura corta de un resultado: (texto, signo) con signo +1 ventaja, -1 pierde, 0 sin ventaja clara."""
    if t is None or mean is None:
        return "Sin datos", 0
    if t >= SIGNIFICANT_T:
        return "Ventaja positiva", 1
    if t <= -SIGNIFICANT_T:
        return "Pierde (significativo)", -1
    return "Sin ventaja clara", 0


@dataclass
class Group:
    """Un grupo de mercados (índices, forex, oro, cripto) con todas sus hojas."""
    key: str
    name: str
    raw: dict = field(repr=False)

    def table(self, name: str) -> list[dict]:
        return self.raw.get(name) or []

    def row(self, pattern: str, filt: str | None = None, sheet: str = "resumen", **match) -> dict | None:
        """Primera fila de `sheet` con ese patrón, filtro (si la hoja lo tiene) y columnas extra (p. ej. mercado=...)."""
        for r in self.table(sheet):
            if r.get("patrón") != pattern or (filt is not None and "filtro" in r and r["filtro"] != filt):
                continue
            if all(r.get(k) == v for k, v in match.items()):
                return r
        return None

    def rows(self, sheet: str, pattern: str, filt: str | None = None) -> list[dict]:
        """Filas de `sheet` de un patrón (y filtro, si la hoja lo tiene)."""
        return [r for r in self.table(sheet) if r.get("patrón") == pattern
                and (filt is None or "filtro" not in r or r["filtro"] == filt)]

    def breakdown(self, sheet: str, key: str, pattern: str, filt: str | None = None) -> list[dict]:
        """Filas de `sheet` partidas por la columna `key`. Si la hoja no trae «Ambos», se suman Continuación y Reversión
        (operaciones, ganadas y R total; profit factor, drawdown y t no se pueden sumar y quedan en None)."""
        rows = self.rows(sheet, pattern, filt)
        if rows or pattern != "Ambos":
            return rows
        merged: dict = {}
        for r in (r for p in PATTERNS[1:] for r in self.rows(sheet, p, filt)):
            m = merged.setdefault(r[key], {key: r[key], "n": 0, "wins": 0.0, "total": 0.0})
            n = r.get("n") or 0
            m["n"] += n
            m["wins"] += n * (r.get("wr") or 0) / 100
            m["total"] += r.get("total") or 0
        return [{"patrón": "Ambos", key: m[key], "n": m["n"], "wr": 100 * m["wins"] / m["n"] if m["n"] else None,
                 "total": m["total"], "mean": m["total"] / m["n"] if m["n"] else None, "pf": None, "dd": None, "t": None}
                for m in merged.values()]

    def curve(self, pattern: str, filt: str) -> list[tuple[str, float]]:
        """Curva de R acumulado [(fecha, R)] o [] si el backtest no la guardó."""
        return [(d, r) for d, r in self.raw.get("curvas", {}).get(f"{pattern}|{filt}", [])]

    @property
    def markets(self) -> list[dict]:
        return self.table("datos")

    @property
    def period(self) -> str:
        """«2018-2026» con el primer y el último año de datos de sus mercados."""
        starts = [str(m.get("desde (NY)") or "")[:4] for m in self.markets]
        ends = [str(m.get("hasta (NY)") or "")[:4] for m in self.markets]
        starts, ends = [s for s in starts if s], [e for e in ends if e]
        return f"{min(starts)}-{max(ends)}" if starts and ends else "-"

    @property
    def updated(self) -> str:
        return self.raw.get("actualizado", "")


@dataclass
class Backtest:
    groups: list[Group]
    comparison: dict
    generated: str = ""
    source: str = ""

    def group(self, key: str) -> Group | None:
        return next((g for g in self.groups if g.key == key), None)


def load(path: str | Path | None = None) -> Backtest:
    """Lee el resumen del backtest. Lanza FileNotFoundError / ValueError si falta o no es válido."""
    path = Path(path) if path else DEFAULT_FILE
    if not path.exists():
        raise FileNotFoundError(f"No está el resumen del backtest ({path}). Genéralo con scripts/exportar_backtest.py")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        groups = [Group(g["key"], g["nombre"], g) for g in data["grupos"]]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ValueError(f"{path.name} no es un resumen de backtest válido: {exc}") from None
    return Backtest(groups, data.get("comparativa") or {}, data.get("generado", ""), str(path))
