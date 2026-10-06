"""Tema visual de TradingBot: paletas, personalización y hoja de estilos (QSS).

Una paleta tiene 10 colores base; el resto de tonos (fondos de tarjetas, bordes de estado,
hexágonos...) se derivan mezclándolos, así al cambiar un color todo queda coherente.

Orden de prioridad:  preset  ->  [theme] de config.toml  ->  theme.local.json (editor de la app).
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, fields, replace
from pathlib import Path

from ..config import PROJECT_ROOT

LOCAL_THEME_FILE = PROJECT_ROOT / "theme.local.json"
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


class ThemeError(ValueError):
    """Color o preset no válido."""


@dataclass(frozen=True)
class Palette:
    bg: str          # fondo de la ventana
    panel: str       # paneles y tarjetas
    border: str      # bordes finos
    text: str        # texto principal
    muted: str       # texto secundario
    accent: str      # azul de acento (selección, botones activos, hexágonos)
    bull: str        # verde: alcista / positivo
    bear: str        # rojo: bajista / negativo
    warn: str        # ámbar: avisos
    chart_bg: str    # fondo del gráfico


LABELS = {
    "bg": "Fondo",
    "panel": "Paneles",
    "border": "Bordes",
    "text": "Texto principal",
    "muted": "Texto secundario",
    "accent": "Azul de acento",
    "bull": "Verde (alcista)",
    "bear": "Rojo (bajista)",
    "warn": "Ámbar (avisos)",
    "chart_bg": "Fondo del gráfico",
}

PRESETS: dict[str, Palette] = {
    # Fondo negro; texto en azul, con verde y rojo para alcista / bajista.
    "negro": Palette(bg="#000000", panel="#07090e", border="#1a2638", text="#6cb2ff", muted="#4a82c0",
                     accent="#2f8cff", bull="#19d98b", bear="#ff4757", warn="#ffb020", chart_bg="#000000"),
    # Azul pizarra, la paleta de la referencia visual inicial.
    "pizarra": Palette(bg="#0e1621", panel="#152131", border="#233449", text="#dbe4f0", muted="#8391a6",
                       accent="#7f9fd0", bull="#3fbc9e", bear="#e86672", warn="#dfa74a", chart_bg="#111b29"),
}
DEFAULT_PRESET = "negro"


# -- utilidades de color ---------------------------------------------------------------------
def mix(a: str, b: str, t: float) -> str:
    """Mezcla dos colores #RRGGBB: t=0 devuelve a, t=1 devuelve b."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


def validate(colors: dict) -> dict:
    valid = {f.name for f in fields(Palette)}
    for key, value in colors.items():
        if key not in valid:
            raise ThemeError(f"Color desconocido '{key}'. Opciones: {', '.join(sorted(valid))}")
        if not isinstance(value, str) or not HEX.match(value):
            raise ThemeError(f"Color '{key}' no válido: {value!r}. Usa el formato #RRGGBB (por ejemplo #19d98b).")
    return {k: v.lower() for k, v in colors.items()}


def build_palette(preset: str, overrides: dict | None = None) -> Palette:
    if preset not in PRESETS:
        raise ThemeError(f"Preset de tema desconocido: {preset!r}. Opciones: {', '.join(PRESETS)}")
    return replace(PRESETS[preset], **validate(overrides or {}))


def diff_from_preset(preset: str, palette: Palette) -> dict:
    base = asdict(PRESETS[preset])
    return {k: v for k, v in asdict(palette).items() if v != base[k]}


# -- persistencia -----------------------------------------------------------------------------
def load_local(path: Path | None = None) -> tuple[str | None, dict]:
    path = path or LOCAL_THEME_FILE
    if not path.exists():
        return None, {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ThemeError(f"No se pudo leer {path.name}: {exc}") from exc
    return data.get("preset"), data.get("colors", {})


def save_local(preset: str, palette: Palette, path: Path | None = None) -> None:
    path = path or LOCAL_THEME_FILE
    path.write_text(json.dumps({"preset": preset, "colors": diff_from_preset(preset, palette)}, indent=2),
                    encoding="utf-8")


def resolve(cfg_theme: dict | None, local_path: Path | None = None) -> tuple[str, Palette]:
    """Combina preset, [theme] de config.toml y theme.local.json. Devuelve (preset, paleta)."""
    cfg_theme = dict(cfg_theme or {})
    cfg_preset = cfg_theme.pop("preset", DEFAULT_PRESET)
    local_preset, local_colors = load_local(local_path)
    if local_preset:
        return local_preset, build_palette(local_preset, local_colors)
    return cfg_preset, build_palette(cfg_preset, {**cfg_theme, **local_colors})


# -- colores activos (se actualizan con apply) ----------------------------------------------
BG = PANEL = PANEL_ALT = CHART_BG = BORDER = TEXT = MUTED = ACCENT = SELECT = ""
ACTIVE_BG = ACTIVE_BORDER = BULL = BEAR = NEUTRAL = WARN = ""
EDGE = RING_DOT = FREE_LINE = FREE_TEXT = ""
_current: Palette = PRESETS[DEFAULT_PRESET]


def current() -> Palette:
    return _current


def apply(palette: Palette) -> None:
    """Fija la paleta activa. Después hay que volver a aplicar la hoja de estilos."""
    global _current, BG, PANEL, PANEL_ALT, CHART_BG, BORDER, TEXT, MUTED, ACCENT, SELECT
    global ACTIVE_BG, ACTIVE_BORDER, BULL, BEAR, NEUTRAL, WARN, EDGE, RING_DOT, FREE_LINE, FREE_TEXT
    _current = palette
    BG, PANEL, BORDER, TEXT, MUTED = palette.bg, palette.panel, palette.border, palette.text, palette.muted
    ACCENT, BULL, BEAR, WARN, CHART_BG = palette.accent, palette.bull, palette.bear, palette.warn, palette.chart_bg
    SELECT = mix(palette.accent, palette.text, 0.35)
    PANEL_ALT = mix(palette.panel, palette.text, 0.07)
    ACTIVE_BG = mix(palette.panel, palette.accent, 0.38)
    ACTIVE_BORDER = palette.accent
    NEUTRAL = mix(palette.muted, palette.text, 0.25)
    EDGE = mix(palette.bg, palette.accent, 0.32)
    RING_DOT = mix(palette.bg, palette.accent, 0.18)
    FREE_LINE = mix(palette.bg, palette.muted, 0.45)
    FREE_TEXT = mix(palette.bg, palette.muted, 0.55)


def hex_style(state: str) -> tuple[str, str]:
    """(relleno, borde) de un hexágono según el estado de la skill."""
    if state == "error":
        return mix(PANEL, BEAR, 0.22), BEAR
    if state == "working":
        return mix(PANEL, ACCENT, 0.36), mix(ACCENT, TEXT, 0.40)
    if state == "ok":
        return mix(PANEL, ACCENT, 0.22), mix(ACCENT, TEXT, 0.05)
    return mix(PANEL, ACCENT, 0.10), mix(BG, ACCENT, 0.55)


apply(PRESETS[DEFAULT_PRESET])


def stylesheet() -> str:
    """Hoja de estilos Qt con la paleta activa."""
    p = _current
    font = '"Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif'
    ok_border, ok_bg = mix(BG, BULL, 0.45), mix(PANEL, BULL, 0.14)
    busy_border, busy_bg = mix(BG, WARN, 0.45), mix(PANEL, WARN, 0.14)
    err_border, err_bg = mix(BG, BEAR, 0.45), mix(PANEL, BEAR, 0.14)
    return f"""
* {{ font-family: {font}; font-size: 12px; color: {TEXT}; }}
QMainWindow, QWidget#Root {{ background: {BG}; }}
QDialog {{ background: {BG}; }}
QToolTip {{ background: {PANEL_ALT}; color: {TEXT}; border: 1px solid {BORDER}; padding: 4px 6px; }}

/* Cabecera */
QFrame#Toolbar {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 6px; }}
QLabel#Brand {{ font-size: 14px; font-weight: 700; }}
QLabel#Muted {{ color: {MUTED}; }}
QLabel#Tiny {{ color: {MUTED}; font-size: 11px; }}
QLabel#StatusChip {{ border-radius: 4px; padding: 3px 9px; border: 1px solid {BORDER}; color: {MUTED}; }}
QLabel#StatusChip[state="ok"] {{ color: {BULL}; border-color: {ok_border}; background: {ok_bg}; }}
QLabel#StatusChip[state="busy"] {{ color: {WARN}; border-color: {busy_border}; background: {busy_bg}; }}
QLabel#StatusChip[state="error"] {{ color: {BEAR}; border-color: {err_border}; background: {err_bg}; }}
QLabel#AccountChip {{ border-radius: 4px; padding: 3px 9px; border: 1px solid {ok_border}; color: {BULL}; background: {ok_bg}; }}
QLabel#DemoBadge {{ background: {WARN}; color: {BG}; border-radius: 4px; padding: 3px 8px; font-weight: 700; }}
QLabel#StatLabel {{ color: {MUTED}; font-size: 11px; }}
QLabel#StatValue {{ font-size: 19px; font-weight: 700; }}
QLabel#StatSub {{ color: {MUTED}; font-size: 11px; }}
QFrame#StatDivider {{ background: {BORDER}; max-width: 1px; min-width: 1px; border: none; }}

/* Paneles */
QFrame#Card {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 6px; }}
QLabel#CardTitle {{ font-size: 13px; font-weight: 700; }}
QLabel#CardNote {{ color: {MUTED}; font-size: 11px; }}
QLabel#SkillDetail {{ font-size: 11px; background: transparent; }}

/* Tarjetas de mercado */
QFrame#MarketCard {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 6px; }}
QFrame#MarketCard:hover {{ border-color: {mix(BORDER, ACCENT, 0.5)}; }}
QFrame#MarketCard[selected="true"] {{ border: 1px solid {SELECT}; }}
QLabel#MkSymbol {{ font-weight: 700; font-size: 12px; background: transparent; }}
QLabel#MkPrice {{ font-size: 19px; font-weight: 700; background: transparent; }}
QLabel#MkSub {{ color: {MUTED}; font-size: 10px; background: transparent; }}
QLabel#MkBadge {{ background: {PANEL_ALT}; color: {MUTED}; border: 1px solid {BORDER}; border-radius: 3px; padding: 0px 5px; font-size: 10px; }}
QFrame#MarketCard[stale="true"] QLabel#MkPrice {{ color: {MUTED}; }}
QFrame#MarketCard[stale="true"] QLabel#MkSymbol {{ color: {MUTED}; }}

/* Tarjeta del Bias: se tiñe según el estado */
QFrame#BiasCard {{ border-radius: 6px; border: 1px solid {BORDER}; background: {PANEL}; }}
QFrame#BiasCard[state="bull"] {{ background: {mix(PANEL, BULL, 0.18)}; border: 1px solid {BULL}; }}
QFrame#BiasCard[state="bear"] {{ background: {mix(PANEL, BEAR, 0.18)}; border: 1px solid {BEAR}; }}
QFrame#BiasCard[state="none"] {{ background: {PANEL_ALT}; border: 1px solid {MUTED}; }}
QLabel#BiasCaption {{ color: {MUTED}; font-size: 12px; background: transparent; }}
QLabel#BiasValue {{ font-size: 38px; font-weight: 800; background: transparent; color: {NEUTRAL}; }}
QFrame#BiasCard[state="bull"] QLabel#BiasValue {{ color: {BULL}; }}
QFrame#BiasCard[state="bear"] QLabel#BiasValue {{ color: {BEAR}; }}
QLabel#BiasDetail {{ color: {MUTED}; background: transparent; }}

QLabel#Chip {{ border-radius: 4px; padding: 6px 10px; font-weight: 600; background: {mix(PANEL, TEXT, 0.06)}; color: {MUTED}; }}
QLabel#Chip[allowed="true"] {{ background: {mix(PANEL, BULL, 0.20)}; color: {BULL}; }}
QLabel#Chip[allowed="false"] {{ background: {mix(PANEL, BEAR, 0.18)}; color: {mix(BEAR, TEXT, 0.15)}; }}

/* Controles */
QComboBox {{ background: {PANEL_ALT}; border: 1px solid {BORDER}; border-radius: 4px; padding: 4px 8px; min-width: 96px; }}
QComboBox:hover {{ border-color: {ACCENT}; }}
QComboBox QAbstractItemView {{ background: {PANEL}; border: 1px solid {BORDER}; selection-background-color: {ACTIVE_BG}; }}

QPushButton {{ background: {PANEL_ALT}; border: 1px solid {BORDER}; border-radius: 4px; padding: 5px 12px; }}
QPushButton:hover {{ border-color: {ACCENT}; }}
QPushButton:disabled {{ color: {mix(BG, MUTED, 0.55)}; border-color: {mix(BG, BORDER, 0.6)}; }}
QPushButton#Primary {{ background: {ACTIVE_BG}; border: 1px solid {ACTIVE_BORDER}; font-weight: 600; }}
QPushButton#Primary:hover {{ background: {mix(ACTIVE_BG, ACCENT, 0.25)}; }}
QPushButton[chip="true"] {{ padding: 4px 11px; font-weight: 600; color: {MUTED}; }}
QPushButton[chip="true"]:checked {{ background: {ACTIVE_BG}; border: 1px solid {ACTIVE_BORDER}; color: {TEXT}; }}

QProgressBar {{ background: transparent; border: none; max-height: 3px; }}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 1px; }}

QPlainTextEdit {{ background: {mix(BG, PANEL, 0.5)}; border: 1px solid {BORDER}; border-radius: 4px; padding: 6px;
    font-family: "Cascadia Mono", Consolas, monospace; font-size: 11px; color: {MUTED}; }}
QScrollBar:vertical {{ background: transparent; width: 8px; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 4px; min-height: 24px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
"""
