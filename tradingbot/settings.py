"""Preferencias personales guardadas desde la app (settings.local.json, no se sube a git)."""
from __future__ import annotations

import json
from pathlib import Path

from .config import DEFAULT_WATCHLIST, PROJECT_ROOT

SETTINGS_FILE = PROJECT_ROOT / "settings.local.json"


def load_settings(path: Path | None = None) -> dict:
    path = path or SETTINGS_FILE
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"No se pudo leer {path.name}: {exc}. Corrígelo o bórralo.") from exc
    return data if isinstance(data, dict) else {}


def save_settings(data: dict, path: Path | None = None) -> None:
    path = path or SETTINGS_FILE
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def clean_symbols(symbols) -> list[str]:
    """Quita vacíos y repetidos (sin distinguir mayúsculas) conservando el orden y el texto original."""
    seen: set[str] = set()
    out: list[str] = []
    for s in symbols or []:
        s = str(s).strip()
        if s and s.lower() not in seen:
            seen.add(s.lower())
            out.append(s)
    return out


def load_watchlist(default: list[str], path: Path | None = None) -> list[str]:
    """Watchlist guardada desde la app; si no hay, la de config.toml."""
    saved = load_settings(path).get("watchlist")
    chosen = clean_symbols(saved) if isinstance(saved, list) else []
    return chosen or clean_symbols(default) or list(DEFAULT_WATCHLIST)


def save_watchlist(symbols: list[str], path: Path | None = None) -> None:
    data = load_settings(path)
    data["watchlist"] = clean_symbols(symbols)
    save_settings(data, path)
