"""Configuración de arranque: tradingbot.env.

Fichero de texto CLAVE=valor, organizado en bloques por skill. Cada clave empieza por el nombre de su bloque
(UI_THEME, FEED_..., BIAS_...), así cada skill lee solo lo suyo con `section("BIAS")`.

Prioridad: variable de entorno del proceso (la fija scripts/run.ps1 o el usuario) > valor del fichero > valor por
defecto del código.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Mapping

from .config import PROJECT_ROOT

ENV_FILE = PROJECT_ROOT / "tradingbot.env"
LINE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")
TRUE = {"1", "true", "si", "sí", "yes", "on"}
FALSE = {"0", "false", "no", "off", ""}


def parse(text: str) -> dict[str, str]:
    """Claves activas del fichero (las comentadas con # se ignoran)."""
    values: dict[str, str] = {}
    for raw in text.splitlines():
        match = LINE.match(raw)
        if match:
            values[match.group(1).upper()] = match.group(2).strip().strip('"').strip("'")
    return values


class EnvConfig:
    def __init__(self, values: Mapping[str, str] | None = None, path: Path | None = None) -> None:
        self.values = dict(values or {})
        self.path = path

    def get(self, key: str, default: str | None = None) -> str | None:
        value = self.values.get(key.upper())
        return default if value is None or value == "" else value

    def get_bool(self, key: str, default: bool = False) -> bool:
        value = self.values.get(key.upper())
        if value is None:
            return default
        low = value.strip().lower()
        if low in TRUE:
            return True
        if low in FALSE:
            return False
        raise ValueError(f"{key}={value!r} no es un sí/no válido (usa true o false).")

    def get_int(self, key: str, default: int | None = None) -> int | None:
        value = self.get(key)
        try:
            return default if value is None else int(value)
        except ValueError:
            raise ValueError(f"{key}={value!r} debe ser un número entero.") from None

    def get_float(self, key: str, default: float | None = None) -> float | None:
        value = self.get(key)
        try:
            return default if value is None else float(value.replace(",", "."))
        except ValueError:
            raise ValueError(f"{key}={value!r} debe ser un número.") from None

    def get_list(self, key: str, default: list[str] | None = None) -> list[str]:
        value = self.get(key)
        return list(default or []) if value is None else [v.strip() for v in value.split(",") if v.strip()]

    def section(self, prefix: str) -> "EnvConfig":
        """Solo las claves de un bloque, sin su prefijo: section('UI').get('THEME')."""
        head = prefix.upper().rstrip("_") + "_"
        return EnvConfig({k[len(head):]: v for k, v in self.values.items() if k.startswith(head)}, self.path)

    def __contains__(self, key: str) -> bool:
        return key.upper() in self.values


def load(path: Path | None = None, environ: Mapping[str, str] | None = None) -> EnvConfig:
    """Lee tradingbot.env; las variables de entorno con el mismo nombre tienen prioridad."""
    path = path or ENV_FILE
    environ = os.environ if environ is None else environ
    values = parse(path.read_text(encoding="utf-8-sig")) if path.exists() else {}
    for key in list(values):
        if key in environ:
            values[key] = environ[key]
    return EnvConfig(values, path)


def set_value(path: Path, key: str, value: str) -> None:
    """Fija CLAVE=valor conservando comentarios y alternativas.

    Si existen líneas `CLAVE=...` o `#CLAVE=...`, se deja activa (sin #) la que tiene ese valor y se comentan las
    demás; si el valor no aparece, se activa una línea nueva junto a ellas. Si la clave no existe, se añade al final.
    """
    key = key.upper()
    pattern = re.compile(rf"^\s*#?\s*{re.escape(key)}\s*=\s*(.*?)\s*$", re.IGNORECASE)
    lines = path.read_text(encoding="utf-8-sig").splitlines() if path.exists() else []
    hits = [i for i, line in enumerate(lines) if pattern.match(line)]
    found = False
    for i in hits:
        current = pattern.match(lines[i]).group(1)
        if current == value and not found:
            lines[i], found = f"{key}={value}", True
        else:
            lines[i] = f"#{key}={current}"
    if not found:
        if hits:
            lines.insert(hits[0], f"{key}={value}")
        else:
            lines.append(f"{key}={value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
