"""Tema visual de TradingBot: paletas, personalización y hoja de estilos (QSS).

Una paleta tiene 10 colores base; el resto de tonos (fondos de tarjetas, bordes de estado,
hexágonos...) se derivan mezclándolos, así al cambiar un color todo queda coherente.

La paleta de arranque se elige en tradingbot.env (UI_THEME). Encima se aplican, solo si son de esa misma paleta,
los colores sueltos de [theme] en config.toml y los guardados desde el editor de la app (theme.local.json).
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
    accent: str      # color de acento (selección, botones activos, hexágonos)
    bull: str        # verde: alcista / positivo
    bear: str        # rojo: bajista / negativo
    warn: str        # ámbar: avisos
    chart_bg: str    # fondo del gráfico
    # Formato de las velas. Vacío = sigue a bull/bear con cuerpo relleno (el formato clásico). Con valores
    # propios se pueden hacer velas huecas: relleno blanco para las alcistas, relleno gris para las bajistas.
    candle_up_fill: str = ""
    candle_up_line: str = ""
    candle_down_fill: str = ""
    candle_down_line: str = ""
    # Resto de colores del gráfico. Vacío = valor derivado (ver `effective`).
    chart_text: str = ""     # números del eje (vacío: texto secundario)
    chart_grid: str = ""     # rejilla (vacío: rejilla horizontal muy tenue, como siempre; con valor: color exacto y vertical)
    level_high: str = ""     # línea del máximo previo (vacío: bear)
    level_low: str = ""      # línea del mínimo previo (vacío: bull)
    level_open: str = ""     # línea de la apertura del día (vacío: acento)
    level_label: str = ""    # texto de las etiquetas de nivel (vacío: el color de su línea)


LABELS = {
    "bg": "Fondo",
    "panel": "Paneles",
    "border": "Bordes",
    "text": "Texto principal",
    "muted": "Texto secundario",
    "accent": "Color de acento",
    "bull": "Verde (alcista)",
    "bear": "Rojo (bajista)",
    "warn": "Ámbar (avisos)",
    "chart_bg": "Fondo del gráfico",
    "candle_up_fill": "Vela alcista: relleno",
    "candle_up_line": "Vela alcista: borde y mecha",
    "candle_down_fill": "Vela bajista: relleno",
    "candle_down_line": "Vela bajista: borde y mecha",
    "chart_text": "Números del eje",
    "chart_grid": "Rejilla",
    "level_high": "Nivel: máximo previo",
    "level_low": "Nivel: mínimo previo",
    "level_open": "Nivel: apertura del día",
    "level_label": "Nivel: texto de la etiqueta",
}
CANDLE_KEYS = ("candle_up_fill", "candle_up_line", "candle_down_fill", "candle_down_line")
# Pestañas del editor de colores
UI_KEYS = ("bg", "panel", "border", "text", "muted", "accent", "bull", "bear", "warn")
CHART_KEYS = ("chart_bg", "chart_text", "chart_grid", "level_high", "level_low", "level_open", "level_label") + CANDLE_KEYS
# Campos que pueden quedar vacíos (= derivados de otros)
OPTIONAL_KEYS = frozenset(CHART_KEYS) - {"chart_bg"}

PRESETS: dict[str, Palette] = {
    # Fondo negro; texto en azul, con verde y rojo para alcista / bajista.
    "negro": Palette(bg="#000000", panel="#07090e", border="#1a2638", text="#6cb2ff", muted="#4a82c0",
                     accent="#2f8cff", bull="#19d98b", bear="#ff4757", warn="#ffb020", chart_bg="#000000"),
    # Azul pizarra, la paleta de la referencia visual inicial.
    "pizarra": Palette(bg="#0e1621", panel="#152131", border="#233449", text="#dbe4f0", muted="#8391a6",
                       accent="#7f9fd0", bull="#3fbc9e", bear="#e86672", warn="#dfa74a", chart_bg="#111b29"),
    # Verde fósforo sobre negro, como la lluvia de código de la película. El rojo es el de la «pastilla roja»
    # (para lo bajista) y el ámbar el de los terminales antiguos (avisos).
    "matrix": Palette(bg="#000000", panel="#020a03", border="#064d12", text="#00ff41", muted="#00a62c",
                      accent="#39ff6e", bull="#00ff41", bear="#ff2a4a", warn="#ffb000", chart_bg="#000000"),
    # Fondo blanco y velas huecas (referencia: gráfico claro de TradingView). Las velas no usan verde/rojo: todas llevan
    # borde y mecha azul marino; las alcistas tienen el cuerpo blanco y las bajistas gris azulado.
    "blanco": Palette(bg="#ffffff", panel="#fbfbfc", border="#dcdfe6", text="#1d1d1f", muted="#6b6e7b",
                      accent="#364e8e", bull="#087f6c", bear="#d0303d", warn="#a86200", chart_bg="#ffffff",
                      candle_up_fill="#ffffff", candle_up_line="#364e8e",
                      candle_down_fill="#8a98bb", candle_down_line="#364e8e",
                      # Eje con números casi negros, rejilla casi invisible y niveles discontinuos apagados con la
                      # etiqueta en azul (PDH/PWH en verde azulado, D OPEN en azul), como en la referencia.
                      chart_text="#1d1d1f", chart_grid="#f1f2f5",
                      level_high="#4a8f86", level_low="#4a8f86", level_open="#4558b8", level_label="#4a5fc1"),
}
DEFAULT_PRESET = "matrix"   # paleta si tradingbot.env no indica otra (UI_THEME)


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
        if key in OPTIONAL_KEYS and value == "":
            continue                                   # vacío = valor derivado
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


def resolve(cfg_theme: dict | None, local_path: Path | None = None, startup: str | None = None) -> tuple[str, Palette]:
    """Devuelve (preset, paleta) de arranque.

    - Con `startup` (UI_THEME de tradingbot.env o --theme): esa paleta manda. Los colores de config.toml y de
      theme.local.json solo se aplican si se guardaron para esa misma paleta.
    - Sin `startup`: preset de config.toml, sustituido por el de theme.local.json si existe (comportamiento anterior).
    """
    cfg_theme = dict(cfg_theme or {})
    cfg_preset = cfg_theme.pop("preset", None)
    local_preset, local_colors = load_local(local_path)
    if startup:
        name = startup.strip().lower()
        if name not in PRESETS:
            raise ThemeError(f"UI_THEME={startup!r} no existe. Opciones: {', '.join(PRESETS)}")
        colors = dict(cfg_theme) if cfg_preset in (None, name) else {}
        if local_preset == name:
            colors.update(local_colors)
        return name, build_palette(name, colors)
    if local_preset:
        return local_preset, build_palette(local_preset, local_colors)
    preset = cfg_preset or DEFAULT_PRESET
    return preset, build_palette(preset, {**cfg_theme, **local_colors})


# -- colores activos (se actualizan con apply) ----------------------------------------------
BG = PANEL = PANEL_ALT = CHART_BG = BORDER = TEXT = MUTED = ACCENT = SELECT = ""
ACTIVE_BG = ACTIVE_BORDER = BULL = BEAR = NEUTRAL = WARN = ""
EDGE = RING_DOT = FREE_LINE = FREE_TEXT = ""
CANDLE_UP_FILL = CANDLE_UP_LINE = CANDLE_DOWN_FILL = CANDLE_DOWN_LINE = ""
CHART_TEXT = CHART_GRID = LEVEL_HIGH = LEVEL_LOW = LEVEL_OPEN = LEVEL_LABEL = ""
_current: Palette = PRESETS[DEFAULT_PRESET]


def effective(palette: Palette, key: str) -> str:
    """Color real de un campo: los de vela vacíos siguen a bull/bear."""
    value = getattr(palette, key)
    if value:
        return value
    fallback = {
        "chart_text": palette.muted,
        "chart_grid": mix(palette.chart_bg, palette.border, 0.07),
        "level_high": palette.bear, "level_low": palette.bull, "level_open": palette.accent,
        "level_label": palette.accent,
    }
    if key in fallback:
        return fallback[key]
    return palette.bull if key.startswith("candle_up") else palette.bear


def current() -> Palette:
    return _current


def apply(palette: Palette) -> None:
    """Fija la paleta activa. Después hay que volver a aplicar la hoja de estilos."""
    global _current, BG, PANEL, PANEL_ALT, CHART_BG, BORDER, TEXT, MUTED, ACCENT, SELECT
    global ACTIVE_BG, ACTIVE_BORDER, BULL, BEAR, NEUTRAL, WARN, EDGE, RING_DOT, FREE_LINE, FREE_TEXT
    global CANDLE_UP_FILL, CANDLE_UP_LINE, CANDLE_DOWN_FILL, CANDLE_DOWN_LINE
    global CHART_TEXT, CHART_GRID, LEVEL_HIGH, LEVEL_LOW, LEVEL_OPEN, LEVEL_LABEL
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
    CANDLE_UP_FILL, CANDLE_UP_LINE = effective(palette, "candle_up_fill"), effective(palette, "candle_up_line")
    CANDLE_DOWN_FILL, CANDLE_DOWN_LINE = effective(palette, "candle_down_fill"), effective(palette, "candle_down_line")
    CHART_TEXT = effective(palette, "chart_text")
    CHART_GRID = palette.chart_grid                       # vacío = rejilla clásica (ver chart.py)
    LEVEL_HIGH, LEVEL_LOW = effective(palette, "level_high"), effective(palette, "level_low")
    LEVEL_OPEN, LEVEL_LABEL = effective(palette, "level_open"), palette.level_label   # etiqueta vacía = color de su línea


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
QLabel#MkPrice {{ font-size: 16px; font-weight: 700; background: transparent; }}
QLabel#MkSub {{ color: {MUTED}; font-size: 10px; background: transparent; }}
QLabel#MkBadge {{ background: {PANEL_ALT}; color: {MUTED}; border: 1px solid {BORDER}; border-radius: 3px; padding: 0px 5px; font-size: 10px; }}
QFrame#MarketCard[stale="true"] QLabel#MkPrice {{ color: {MUTED}; }}
QFrame#MarketCard[stale="true"] QLabel#MkSymbol {{ color: {MUTED}; }}

/* Tarjeta del Bias: se tiñe según el estado */
QFrame#BiasCard {{ border-radius: 6px; border: 1px solid {BORDER}; background: {PANEL}; }}
QFrame#BiasCard[state="bull"] {{ background: {mix(PANEL, BULL, 0.18)}; border: 1px solid {BULL}; }}
QFrame#BiasCard[state="bear"] {{ background: {mix(PANEL, BEAR, 0.18)}; border: 1px solid {BEAR}; }}
QFrame#BiasCard[state="none"] {{ background: {PANEL_ALT}; border: 1px solid {MUTED}; }}
QFrame#BiasCard QLabel#CardTitle {{ background: transparent; }}
QLabel#BiasValue {{ font-size: 20px; font-weight: 800; background: transparent; color: {NEUTRAL}; }}
QFrame#BiasCard[state="bull"] QLabel#BiasValue {{ color: {BULL}; }}
QFrame#BiasCard[state="bear"] QLabel#BiasValue {{ color: {BEAR}; }}
QLabel#BiasDetail {{ color: {MUTED}; font-size: 10px; background: transparent; }}

QLabel#Chip {{ border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: 600; background: {mix(PANEL, TEXT, 0.06)}; color: {MUTED}; }}
QLabel#Chip[allowed="true"] {{ background: {mix(PANEL, BULL, 0.20)}; color: {BULL}; }}
QLabel#Chip[allowed="false"] {{ background: {mix(PANEL, BEAR, 0.18)}; color: {mix(BEAR, TEXT, 0.15)}; }}

QLabel#ErrorBanner {{ background: {mix(PANEL, BEAR, 0.16)}; border: 1px solid {mix(BG, BEAR, 0.55)}; border-radius: 4px; padding: 8px 10px; }}

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

QLineEdit {{ background: {PANEL_ALT}; border: 1px solid {BORDER}; border-radius: 4px; padding: 5px 8px;
    selection-background-color: {ACTIVE_BG}; }}
QLineEdit:focus {{ border-color: {ACCENT}; }}
QComboBox QLineEdit {{ border: none; background: transparent; padding: 0; }}
QListWidget {{ background: {mix(BG, PANEL, 0.5)}; border: 1px solid {BORDER}; border-radius: 4px; padding: 2px; outline: 0; }}
QListWidget::item {{ padding: 3px 6px; border-radius: 3px; }}
QListWidget::item:hover {{ background: {PANEL_ALT}; }}
QListWidget::item:selected {{ background: {ACTIVE_BG}; color: {TEXT}; }}

QProgressBar {{ background: transparent; border: none; max-height: 3px; }}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 1px; }}

QPlainTextEdit, QTextBrowser#LogView {{ background: {mix(BG, PANEL, 0.5)}; border: 1px solid {BORDER}; border-radius: 4px; padding: 6px;
    font-family: "Cascadia Mono", Consolas, monospace; font-size: 11px; color: {MUTED}; }}
QScrollBar:vertical {{ background: transparent; width: 8px; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 4px; min-height: 24px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
"""
