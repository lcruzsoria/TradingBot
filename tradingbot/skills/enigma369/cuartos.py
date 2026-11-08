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
  2. El código de una zona son los dígitos de su capa y de las tres capas de arriba (menos si no las hay: 4 cifras en el último nivel).
  3. Número de la zona = suma de los dígitos del código reducida a una cifra (4444 = 16 → 7). Toda zona de lunes a jueves lleva número.
  4. Son críticos los números 3, 6 y 9.
  5. Q0 (viernes, sábado, domingo y 5.ª semana): se ven en amarillo, como en el indicador, pero no cuentan: sin número
     ni alineaciones. Sus sesiones y cuartos conservan su color 1-4, sin número.
  6. Alineación = 2 o más zonas seguidas con el mismo dígito (mismo color) y número crítico cada una.
     Opacidad del área: 2 zonas 0,14 / 3 zonas 0,28 / 4 zonas 0,42.
  7. Combinación de color = 3 o más zonas seguidas del mismo color (crítico o no): se marca en el gráfico con una franja
     del color en el borde superior y su código.
"""
from __future__ import annotations

from datetime import datetime, timezone

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
MAX_BARS = 20000         # solo se calculan las zonas de las últimas velas (= FEED_MAX_BARS por defecto: unas 3 semanas en M1)


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
    month = monday.astype("datetime64[M]").astype(np.int64) % 12                    # 0-based: enero = 0
    return {
        "mes": (month % 3 + 1).astype(np.int8),                                     # mes dentro del trimestre (1-3), el del lunes de la semana
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
            "cuarto": f"Q{digit}", "micro": f"M{digit}", "mes": f"Mes {digit}"}[layer]


def zone_text(layer: str, digits: dict[str, int], number: int, code: str) -> str:
    """Texto de la franja: «referencia código · número» (W2 · 2, Tuesday 22 · 4, London 222 · 6, Q3 2223 · 9);
    en Q0, el nombre que da el indicador (Friday, Asia, Q2...)."""
    if number:
        ref = zone_ref(layer, digits[layer])
        return f"{ref} · {number}" if layer in ("semana", "mes") else f"{ref} {code} · {number}"
    if layer == "dia":
        return WEEKDAY_NAMES[digits["weekday"]]
    if layer == "sesion":
        return SESSION_LABELS[digits[layer]]
    if layer == "semana":
        return f"W{digits[layer]}" if digits[layer] else "Q0"
    return zone_ref(layer, digits[layer])


def zones_at(digits: dict[str, int], layers: tuple[str, ...]) -> list[dict]:
    """Una zona por capa: dígito, código (los dígitos de su capa y las tres de arriba), suma, número y texto.
    `ref_number` es el número que tendría si contara (solo orientativo en Q0).

    En Q0 (viernes, sábado, domingo o 5.ª semana) las zonas se ven pero no cuentan: número 0.
    """
    out_of_count = digits["semana"] == 0 or digits["dia"] == 0
    ref = {**digits, "semana": digits["semana"] or 5, "dia": digits["dia"] or digits["weekday"] + 1}   # Q0 de referencia: 5.ª semana; viernes 5, sábado 6, domingo 7
    zones = []
    for i, layer in enumerate(layers):
        window = "".join(str(digits[c]) for c in layers[max(0, i - 3): i + 1])
        total = sum(int(ch) for ch in "".join(str(ref[c]) for c in layers[max(0, i - 3): i + 1]))
        number = 0 if out_of_count else reduce_digit(total)
        text = zone_text(layer, digits, number, window)
        zones.append(dict(layer=layer, digit=digits[layer], code=window, total=total, number=number, ref_number=reduce_digit(total), text=text,
                          ref=f"{zone_ref(layer, digits[layer])} · {number}" if number else text, num=str(number) if number else ""))
    return zones


def alignments(zones: list[dict], key: str = "number") -> list[dict]:
    """Tramos de 2 o más zonas seguidas con el mismo dígito y número crítico: {first, last, n, digit, label}."""
    runs, i = [], 0
    while i < len(zones):
        if zones[i][key] not in CRITICAL:
            i += 1
            continue
        j = i
        while j + 1 < len(zones) and zones[j + 1][key] in CRITICAL and zones[j + 1]["digit"] == zones[i]["digit"]:
            j += 1
        if j > i:
            runs.append(dict(first=i, last=j, n=j - i + 1, digit=zones[i]["digit"],
                             label=" · ".join([zones[j]["code"], "".join(str(z[key]) for z in zones[i:j + 1])])))
        i = j + 1
    return runs


def same_color_runs(zones: list[dict], min_n: int = 3) -> list[dict]:
    """Tramos de `min_n` o más zonas seguidas con el mismo dígito (mismo color), sea o no crítico su número.
    Cuenta el color, no el número: en Q0 (viernes...) la sesión, el cuarto y el micro conservan su color 1-4, así que también cuentan
    (solo se excluyen las zonas amarillas, dígito 0)."""
    runs, i = [], 0
    while i < len(zones):
        if not zones[i]["digit"]:
            i += 1
            continue
        j = i
        while j + 1 < len(zones) and zones[j + 1]["digit"] == zones[i]["digit"]:
            j += 1
        if j - i + 1 >= min_n:
            runs.append(dict(first=i, last=j, n=j - i + 1, digit=zones[i]["digit"], label="".join(str(z["digit"]) for z in zones[i:j + 1]), number=zones[j]["number"]))
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
    triples: list[dict] = []
    open_triples: dict[tuple, dict] = {}
    for k in range(len(stack)):
        key = tuple(stack[k])
        if key not in cache:
            zones = zones_at(dict(zip(names, map(int, key))), layers)
            cache[key] = (zones, alignments(zones), same_color_runs(zones))
        zones, runs, triples_now = cache[key]
        x = first + k
        for i, z in enumerate(zones):
            cur = open_rows[i]
            sig = (z["code"], z["digit"], z["number"], z["text"])
            if cur is not None and cur["sig"] == sig:
                cur["x1"] = x + 0.5
            else:
                cur = dict(x0=x - 0.5, x1=x + 0.5, layer=z["layer"], digit=z["digit"], code=z["code"], number=z["number"], text=z["text"], ref=z["ref"], num=z["num"],
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
        # combinaciones de 3 o más zonas seguidas del mismo color: una marca por cada tramo, mientras no cambie ninguna de sus zonas
        keys = {(r["first"], r["last"], tuple(zones[j]["code"] for j in range(r["first"], r["last"] + 1))): r for r in triples_now}
        for tk in [k for k in open_triples if k not in keys]:
            del open_triples[tk]
        for tk, r in keys.items():
            if tk in open_triples:
                open_triples[tk]["x1"] = x + 0.5
            else:
                open_triples[tk] = dict(x0=x - 0.5, x1=x + 0.5, n=r["n"], digit=r["digit"], color=colors[r["digit"]], label=r["label"], number=r["number"],
                                        first=layers[r["first"]], last=layers[r["last"]])
                triples.append(open_triples[tk])
    for segs in rows:
        for s in segs:
            s.pop("sig", None)
    lines = quarter_lines(ts, ahead, anchor_hour, colors, layers[-1])
    lines += [ln for ln in triple_lines(ts, ahead, anchor_hour, list(open_triples.values()), layers) if all(abs(ln["x"] - o["x"]) > 1e-6 for o in lines)]
    return {"layers": layers, "rows": rows, "areas": areas, "triples": triples, "quarter_lines": lines}


def quarter_lines(ts, ahead: int, anchor_hour: int = DEFAULT_ANCHOR_HOUR, colors=None, layer: str = "cuarto") -> list[dict]:
    """Inicio y fin del cuarto (90 min) o del micro (22,5 min) en curso, para dibujarlos como líneas punteadas verticales sobre el precio.

    [{x, kind: "start" | "end", color}] en índices de vela; el fin cae después de la última vela (proyectado)."""
    period = 1350 if layer == "micro" else 5400
    ts = np.asarray(ts, dtype=np.int64)
    if len(ts) < 2:
        return []
    colors = {**DEFAULT_COLORS, **(colors or {})}
    last = int(ts[-1])
    since = (last - int(ahead) - anchor_hour * 3600) % 86400
    start = last - (since % period)
    step = max(1, int(np.median(np.diff(ts[-200:]))))
    digit = int(layer_digits(np.array([last]), ahead, anchor_hour)[layer][0])
    x_start = int(np.searchsorted(ts, start)) - 0.5
    x_end = len(ts) - 1.5 + (start + period - last) / step
    return [dict(x=x_start, kind="start", color=colors.get(digit, "#555555")), dict(x=x_end, kind="end", color=colors.get(digit, "#555555"))]


LAYER_SECONDS = {"micro": 1350, "cuarto": 5400, "sesion": 21600, "dia": 86400}


def triple_lines(ts, ahead: int, anchor_hour: int, active: list[dict], layers: tuple[str, ...]) -> list[dict]:
    """Líneas verticales de inicio y fin de cada combinación de color activa (la de la última vela), del color de sus zonas.

    La combinación acaba cuando cambia su capa más fina; el fin se proyecta después de la última vela."""
    ts = np.asarray(ts, dtype=np.int64)
    if len(ts) < 2:
        return []
    last = int(ts[-1])
    step = max(1, int(np.median(np.diff(ts[-200:]))))
    since = (last - int(ahead) - anchor_hour * 3600) % 86400
    out = []
    for t in active:
        period = LAYER_SECONDS.get(t["last"])
        if period is None:
            continue
        start = last - (since % period)
        out += [dict(x=t["x0"], kind="start", color=t["color"]), dict(x=len(ts) - 1.5 + (start + period - last) / step, kind="end", color=t["color"])]
    return out


def last_zones(ts, ahead: int, mode: str = "semana", anchor_hour: int = DEFAULT_ANCHOR_HOUR) -> list[dict]:
    """Las zonas de la última vela (para el subtítulo del panel)."""
    dig = layer_digits(np.asarray(ts)[-1:], ahead, anchor_hour)
    return zones_at({c: int(v[0]) for c, v in dig.items()}, MODES[mode])


BIG_LAYERS = ("mes", "semana", "dia", "sesion")


def upcoming_big(now_wall: datetime, hours: float, anchor_hour: int = DEFAULT_ANCHOR_HOUR, min_n: int = 3) -> list[dict]:
    """Alineaciones de `min_n` o más zonas seguidas que EMPIEZAN en las próximas `hours` horas, en dos juegos de capas:
    semana-día-sesión y mes-semana-día-sesión (con el mes dentro del trimestre).

    `now_wall`: hora de pared de Nueva York (sin zona). Devuelve [{start, n, label, text, layers}] con start en hora de NY."""
    base = int(now_wall.replace(tzinfo=timezone.utc).timestamp() // 900 * 900)
    found = {}
    for layers in (BIG_LAYERS, BIG_LAYERS[1:]):                       # primero las de 4 niveles: mandan si empiezan a la vez
        prev = None
        for k in range(-1, int(hours * 4) + 2):
            ts = base + k * 900
            dig = layer_digits(np.array([ts]), 0, anchor_hour)
            zones = zones_at({c: int(v[0]) for c, v in dig.items()}, layers)
            runs = [r for r in alignments(zones) if r["n"] >= min_n]
            key = tuple((r["first"], r["label"]) for r in runs)
            if runs and key != prev and k >= 0:
                r = runs[0]
                start = datetime.fromtimestamp(ts, timezone.utc).replace(tzinfo=None)
                found.setdefault(start, dict(start=start, n=r["n"], label=r["label"], layers=layers[r["first"]: r["last"] + 1],
                                             text=" · ".join(z["text"] for z in zones[r["first"]: r["last"] + 1])))
            prev = key
    return sorted(found.values(), key=lambda x: x["start"])
