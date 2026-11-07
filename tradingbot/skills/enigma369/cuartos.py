"""Enigma369: traducción de los cuartos (Quarterly Theory Cycles) a un número del 1 al 9 por zona.

Capas, en hora de Nueva York. El día de trading empieza a las 18:00 NY, con la sesión Asia (como el indicador;
ENIGMA369_ANCHOR_HOUR lo cambia, p. ej. 17 para el cierre de los futuros CME):
  semana : cuarto del mes (1.ª a 4.ª semana, según el lunes de esa semana). La 5.ª semana es Q0 y no cuenta
  dia    : lunes = 1 ... jueves = 4. Viernes (y fin de semana) = Q0, no cuenta
  sesion : sesión de 6 h (Asia 1, London 2, NY AM 3, NY PM 4)
  cuarto : ciclo de 90 min dentro de la sesión
  micro  : ciclo de 22,5 min dentro del de 90 min

Dos modos, cada uno con 4 capas visibles (y su timeframe de velas):
  semana → cuarto   (velas de 5m)
  dia    → micro    (velas de 1m)

Regla:
  1. Cada capa aporta un dígito 1-4 (su cuarto). El color es ese dígito: 1 gris, 2 rojo (rosado), 3 verde, 4 azul, todos en tonos pastel.
  2. El código de una zona son los dígitos de su capa y de las dos capas de arriba (menos si no las hay).
  3. Número de la zona = suma de los dígitos del código reducida a una cifra (444 = 12 → 3). Toda zona de lunes a jueves lleva número.
  4. Son críticos los números 3, 6 y 9.
  5. Q0 (viernes, sábado, domingo y 5.ª semana): se ven en amarillo, como en el indicador, pero no cuentan: sin número
     ni alineaciones. Sus sesiones y cuartos conservan su color 1-4, sin número.
  6. Alineación = 2 o más zonas seguidas con el mismo dígito (mismo color) y número crítico cada una.
     Opacidad del área: 2 zonas 0,14 / 3 zonas 0,28 / 4 zonas 0,42.
"""
from __future__ import annotations

import numpy as np

DEFAULT_ANCHOR_HOUR = 18
MODES = {"semana": ("semana", "dia", "sesion", "cuarto"), "dia": ("dia", "sesion", "cuarto", "micro")}
MODE_TIMEFRAMES = {"semana": "5m", "dia": "1m"}
LAYER_NAMES = {"semana": "Semana", "dia": "Día", "sesion": "Sesión", "cuarto": "Cuarto", "micro": "Micro"}
SESSION_NAMES = {1: "Asia", 2: "London", 3: "NY AM", 4: "NY PM"}
DAY_NAMES = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves"}
CRITICAL = (3, 6, 9)
OPACITY = {2: 0.14, 3: 0.28, 4: 0.42}
DEFAULT_COLORS = {0: "#EFD9A8", 1: "#B2B6C1", 2: "#E398A1", 3: "#A6CFA9", 4: "#98AEF8"}   # tonos pastel del indicador; 0 = Q0 (amarillo)
WEEKDAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
SESSION_LABELS = {1: "Asia", 2: "London", 3: "NY AM", 4: "NY PM"}
MAX_BARS = 3000          # solo se calculan las zonas de las últimas velas


def reduce_digit(total: int) -> int:
    """Suma de dígitos reducida a una cifra del 1 al 9 (12 → 3)."""
    return 1 + (total - 1) % 9 if total > 0 else 0


def layer_digits(ts, ahead: int, anchor_hour: int = DEFAULT_ANCHOR_HOUR) -> dict[str, np.ndarray]:
    """Dígito 1-4 de cada capa para cada vela (0 = Q0: viernes, fin de semana o 5.ª semana).

    `ts`: marcas de tiempo del servidor en segundos; `ahead`: segundos que el servidor va por delante de Nueva York
    (la hora de pared de NY, así el cambio de horario no desplaza las capas).
    """
    wall = np.asarray(ts, dtype=np.int64) - int(ahead)
    minutes = ((wall % 86400) / 60.0 - anchor_hour * 60) % 1440
    day = (wall + (24 - anchor_hour) * 3600) // 86400                      # día de trading (días desde 1970-01-01)
    weekday = (day + 3) % 7                                                 # lunes = 0
    monday = (day - weekday).astype("datetime64[D]")
    day_of_month = (monday - monday.astype("datetime64[M]")).astype(np.int64)    # 0-based
    week = day_of_month // 7 + 1
    return {
        "semana": np.where(week <= 4, week, 0).astype(np.int8),
        "dia": np.where(weekday <= 3, weekday + 1, 0).astype(np.int8),
        "sesion": (minutes // 360 + 1).astype(np.int8),
        "cuarto": (minutes % 360 // 90 + 1).astype(np.int8),
        "micro": (minutes % 90 // 22.5 + 1).astype(np.int8),
        "weekday": weekday.astype(np.int8),
    }


def zone_ref(layer: str, digit: int) -> str:
    """Referencia del periodo: W1-W4 (semana), Monday-Sunday (día), Asia / London / NY AM / NY PM (sesión), Q1-Q4 (90 min), M1-M4 (micro)."""
    return {"semana": f"W{digit}", "dia": WEEKDAY_NAMES[digit - 1] if 1 <= digit <= 4 else "", "sesion": SESSION_LABELS.get(digit, ""),
            "cuarto": f"Q{digit}", "micro": f"M{digit}"}[layer]


def zone_text(layer: str, digits: dict[str, int], number: int, code: str) -> str:
    """Texto de la franja: «referencia código · número» (W2 · 2, Tuesday 22 · 4, London 222 · 6, Q3 223 · 7);
    en Q0, el nombre que da el indicador (Friday, Asia, Q2...)."""
    if number:
        ref = zone_ref(layer, digits[layer])
        return f"{ref} · {number}" if layer == "semana" else f"{ref} {code} · {number}"
    if layer == "dia":
        return WEEKDAY_NAMES[digits["weekday"]]
    if layer == "sesion":
        return SESSION_LABELS[digits[layer]]
    if layer == "semana":
        return f"W{digits[layer]}" if digits[layer] else "Q0"
    return f"Q{digits[layer]}"


def zones_at(digits: dict[str, int], layers: tuple[str, ...]) -> list[dict]:
    """Una zona por capa: dígito, código (los dígitos de su capa y las dos de arriba), suma, número y texto.

    En Q0 (viernes, sábado, domingo o 5.ª semana) las zonas se ven pero no cuentan: número 0.
    """
    out_of_count = digits["semana"] == 0 or digits["dia"] == 0
    zones = []
    for i, layer in enumerate(layers):
        window = "".join(str(digits[c]) for c in layers[max(0, i - 2): i + 1])
        total = sum(int(ch) for ch in window)
        number = 0 if out_of_count else reduce_digit(total)
        zones.append(dict(layer=layer, digit=digits[layer], code=window, total=total, number=number,
                          text=zone_text(layer, digits, number, window)))
    return zones


def alignments(zones: list[dict]) -> list[dict]:
    """Tramos de 2 o más zonas seguidas con el mismo dígito y número crítico: {first, last, n, digit, label}."""
    runs, i = [], 0
    while i < len(zones):
        if zones[i]["number"] not in CRITICAL:
            i += 1
            continue
        j = i
        while j + 1 < len(zones) and zones[j + 1]["number"] in CRITICAL and zones[j + 1]["digit"] == zones[i]["digit"]:
            j += 1
        if j > i:
            runs.append(dict(first=i, last=j, n=j - i + 1, digit=zones[i]["digit"],
                             label=" · ".join([zones[j]["code"], "".join(str(z["number"]) for z in zones[i:j + 1])])))
        i = j + 1
    return runs


def compute(ts, ahead: int, mode: str = "semana", anchor_hour: int = DEFAULT_ANCHOR_HOUR, colors=None) -> dict:
    """Zonas de las últimas velas: filas (franjas bajo el gráfico) y áreas de alineación para el gráfico de precio.

    Devuelve {"layers", "rows": [[segmento]], "areas": [área]} con las posiciones en índices de vela (x0 = primera vela - 0,5).
    segmento = {x0, x1, layer, digit, code, number, color}; área = {x0, x1, n, digit, color, opacity, label, first, last}.
    """
    colors = {**DEFAULT_COLORS, **(colors or {})}
    layers = MODES[mode]
    ts = np.asarray(ts)
    n = len(ts)
    first = max(0, n - MAX_BARS)
    dig = layer_digits(ts[first:], ahead, anchor_hour)
    names = ("semana", "dia", "sesion", "cuarto", "micro", "weekday")
    stack = np.stack([dig[c] for c in names], axis=1)
    cache: dict[tuple, tuple] = {}
    rows: list[list[dict]] = [[] for _ in layers]
    areas: list[dict] = []
    open_rows: list[dict | None] = [None] * len(layers)
    open_area: dict | None = None
    area_key = None
    for k in range(len(stack)):
        key = tuple(stack[k])
        if key not in cache:
            zones = zones_at(dict(zip(names, map(int, key))), layers)
            cache[key] = (zones, alignments(zones))
        zones, runs = cache[key]
        x = first + k
        for i, z in enumerate(zones):
            cur = open_rows[i]
            sig = (z["code"], z["digit"], z["number"], z["text"])
            if cur is not None and cur["sig"] == sig:
                cur["x1"] = x + 0.5
            else:
                cur = dict(x0=x - 0.5, x1=x + 0.5, layer=z["layer"], digit=z["digit"], code=z["code"], number=z["number"], text=z["text"],
                           color=colors.get(z["digit"], "#555555"), sig=sig)
                rows[i].append(cur)
                open_rows[i] = cur
        # área: la alineación más larga (la de más zonas) de esta vela; su recuadro sigue mientras no cambie ninguna de sus zonas
        best = max(runs, key=lambda r: r["n"]) if runs else None
        new_key = None if best is None else (best["first"], best["last"], tuple(zones[j]["code"] for j in range(best["first"], best["last"] + 1)))
        if new_key is not None and new_key == area_key and open_area is not None:
            open_area["x1"] = x + 0.5
        elif new_key is not None:
            open_area = dict(x0=x - 0.5, x1=x + 0.5, n=best["n"], digit=best["digit"], color=colors[best["digit"]],
                             opacity=OPACITY[min(best["n"], 4)], label=best["label"], first=layers[best["first"]], last=layers[best["last"]])
            areas.append(open_area)
            area_key = new_key
        else:
            open_area, area_key = None, None
    for segs in rows:
        for s in segs:
            s.pop("sig", None)
    return {"layers": layers, "rows": rows, "areas": areas}


def last_zones(ts, ahead: int, mode: str = "semana", anchor_hour: int = DEFAULT_ANCHOR_HOUR) -> list[dict]:
    """Las zonas de la última vela (para el subtítulo del panel)."""
    dig = layer_digits(np.asarray(ts)[-1:], ahead, anchor_hour)
    return zones_at({c: int(v[0]) for c, v in dig.items()}, MODES[mode])
