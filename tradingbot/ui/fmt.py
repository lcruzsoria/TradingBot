"""Formato de fechas y números en español."""
from __future__ import annotations

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def miles(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def fecha_larga(d) -> str:
    return f"{DIAS[d.weekday()]} {d.day} {MESES[d.month - 1]} {d.year}"


def fecha_corta(d) -> str:
    return f"{d.day:02d} {MESES[d.month - 1]} {d.year}"


def fecha_hora(d) -> str:
    return f"{d.day:02d} {MESES[d.month - 1]} {d.hour:02d}:{d.minute:02d}"


def hace(segundos: int) -> str:
    """'hace 3 s', 'hace 5 min', 'hace 3 h 19 min'."""
    s = max(0, int(segundos))
    if s < 60:
        return f"hace {s} s"
    if s < 3600:
        return f"hace {s // 60} min"
    h, m = divmod(s // 60, 60)
    return f"hace {h} h {m} min" if m else f"hace {h} h"
