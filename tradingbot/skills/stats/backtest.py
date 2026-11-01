"""Backtests de las estrategias (patrones Continuación y Reversión por grupo de mercados, y Calendario), para la ventana Backtest.

Lee `backtest.json.gz` (lo genera `scripts/exportar_backtest.py` a partir de los Excel y el pkl de `analisis/`), que guarda cada
operación del backtest. Todas las cifras se calculan aquí a partir de ellas, así que la ventana puede quedarse con solo un
año, un mes, un día de la semana o una hora de entrada (al pulsar los histogramas) y recalcular todo lo demás. Solo las hojas que necesitan volver a
simular (mejoras de stop y RR, embudo de las TBR) llegan ya hechas y no se filtran.
"""
from __future__ import annotations

import gzip
import json
import math
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

import numpy as np

DEFAULT_FILE = Path(__file__).with_name("backtest.json.gz")
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
DAYS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
MONTHS = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")
INT_COLS = {"m", "p", "z", "d", "o", "s", "f", "e", "x", "v", "l", "n", "t", "h", "c"}     # el resto son decimales (None -> NaN)
OVERLAP_ALL, OVERLAP_GO = 1, 2                      # bits de la columna «f»: solapada con otra (todas / GO de Cortex)
# CRT: columnas l (LTF en minutos: 5, 3, 1), n (entrada 1, 2, 3), t (máscara del timeframe del FVG de MTF que toca el extremo del sweep)
# h (hora en punto 0-23 a la que está pegada la hora de entrada si dista 15 min o menos; -1 si no) y c (inicio de la vela H3 / H4 del
# sweep, en minutos NY: con él el gráfico marca cada CRT)
CRT_MTF_BITS = {15: 1, 30: 2, 60: 4}
CRT_MTF_NAMES = {0: "Todos", 15: "M15", 30: "M30", 60: "H1"}
CRT_LTFS = (5, 3, 1)
CRT_ENTRIES = {1: "Vela siguiente al CISD", 2: "Retesteo del iFVG", 3: "Primera vela sin mecha"}
CRT_ZONES = ("Asia", "London", "NY Open", "Fuera de TBR")
CRT_TBR = ("Todas", "Dentro de TBR", "Asia", "London", "NY Open", "Fuera de TBR")          # filtro por la TBR de la hora de entrada
CRT_NEAR = ("Todas", "±15 min de la hora", "Resto")                                          # y por la cercanía a una hora en punto
CRT_TARGETS = {1: "1R", 2: "2R", 3: "Extremo de C1"}   # columna q: el objetivo con el que se simuló cada operación (cada uno su backtest)
CRT_DEFAULT = (0, 5, 1, CRT_TBR[0], CRT_NEAR[0], 2)   # (TF del FVG: 0 = todos, LTF, entrada, TBR, cercanía a la hora en punto, objetivo)
# Sensibilidad de los patrones: columna de cada operación -> variante
SENSITIVITY = (("tp1", "objetivo 1R"), ("tp15", "objetivo 1.5R"), ("tp2", "objetivo 2R"), ("tp25", "objetivo 2.5R"),
               ("tp3", "objetivo 3R"), ("h12", "objetivo 2R, máx. 12 h"), ("r", "objetivo 2R, máx. 24 h"),
               ("h48", "objetivo 2R, máx. 48 h"))


def verdict(t: float | None, mean: float | None) -> tuple[str, int]:
    """Lectura corta de un resultado: (texto, signo) con signo +1 ventaja, -1 pierde, 0 sin ventaja clara."""
    if t is None or mean is None:
        return "Sin datos", 0
    if t >= SIGNIFICANT_T:
        return "Ventaja positiva", 1
    if t <= -SIGNIFICANT_T:
        return "Pierde (significativo)", -1
    return "Sin ventaja clara", 0


def summarize(net) -> dict:
    """Cifras de una serie de R neto por operación, ya en orden de cierre (las mismas que las hojas del backtest)."""
    net = np.asarray(net, dtype=float)
    n = len(net)
    if not n:
        return {"n": 0}
    won, lost = net[net > 0], net[net < 0]
    acc = np.cumsum(net)
    dd = float((acc - np.maximum.accumulate(np.maximum(acc, 0.0))).min())
    longest = run = 0
    for losing in net < 0:
        run = run + 1 if losing else 0
        longest = max(longest, run)
    sd = float(net.std(ddof=1)) if n > 2 else 0.0
    mean = float(net.mean())
    return {"n": n, "wr": 100 * len(won) / n, "mean": mean, "total": float(net.sum()),
            "pf": float(won.sum() / -lost.sum()) if len(lost) else None,
            "avg_win": float(won.mean()) if len(won) else None, "avg_loss": float(lost.mean()) if len(lost) else None,
            "dd": min(dd, 0.0), "streak": longest, "t": mean / (sd / math.sqrt(n)) if sd > 0 else None}


class Ops:
    """Operaciones de un backtest en columnas (numpy), siempre ordenadas por la hora de cierre."""

    def __init__(self, cols: dict[str, np.ndarray], cats: dict[str, list[str]]) -> None:
        self.cols, self.cats = cols, cats

    @classmethod
    def from_json(cls, data: dict, cats: dict[str, list[str]]) -> Ops:
        cols = {k: np.asarray(v, dtype=np.int64 if k in INT_COLS else float) for k, v in data.items()}
        n = len(cols["e"]) if "e" in cols else 0
        for k in INT_COLS | {"r", "k"}:                       # un grupo sin operaciones (o sin alguna columna) también vale
            cols.setdefault(k, np.zeros(n, dtype=np.int64 if k in INT_COLS else float))
        order = np.lexsort((cols["e"], cols["x"]))           # por cierre y, a igual cierre, por entrada
        return cls({k: v[order] for k, v in cols.items()}, cats)

    def __len__(self) -> int:
        return len(self.cols["e"])

    def __getitem__(self, name: str) -> np.ndarray:
        return self.cols[name]

    def take(self, mask) -> Ops:
        return Ops({k: v[mask] for k, v in self.cols.items()}, self.cats)

    def names(self, cat: str) -> np.ndarray:
        """Nombres de una columna de categorías (mercado, patrón, zona...)."""
        if not len(self):
            return np.asarray([], dtype=object)
        return np.asarray(self.cats[cat], dtype=object)[self.cols[cat]]

    @cached_property
    def year(self) -> np.ndarray:
        """Año de la entrada (hora de Nueva York)."""
        return self.cols["e"].astype("datetime64[m]").astype("datetime64[Y]").astype(np.int64) + 1970

    @property
    def hour(self) -> np.ndarray:
        return (self.cols["e"] // 60) % 24

    @property
    def weekday(self) -> np.ndarray:
        """0 lunes ... 6 domingo (el 1-1-1970 fue jueves)."""
        return (self.cols["e"] // 1440 + 3) % 7

    @cached_property
    def month(self) -> np.ndarray:
        """Mes de la entrada, 1 enero ... 12 diciembre."""
        return self.cols["e"].astype("datetime64[m]").astype("datetime64[M]").astype(np.int64) % 12 + 1

    def stats(self, col: str = "r") -> dict:
        return summarize(self.cols[col])

    def split(self, keys: np.ndarray, order: list | None = None) -> list[tuple[object, Ops]]:
        """(clave, operaciones) por cada valor de `keys`: primero los de `order` (aunque no tengan) y luego el resto."""
        found = list(dict.fromkeys(keys.tolist()))
        rest = [k for k in found if k not in (order or [])]
        wanted = list(order or []) + sorted(rest, key=lambda k: (isinstance(k, str), k if not isinstance(k, str) else 0, str(k)))
        return [(k, self.take(keys == k)) for k in wanted]

    def curve(self) -> tuple[np.ndarray, np.ndarray]:
        """(hora de cierre en segundos, R acumulado) tras cada operación."""
        return self.cols["x"] * 60.0, np.cumsum(self.cols["r"])

    def halves(self, median: float | None = None) -> list[tuple[str, Ops]]:
        """Las operaciones partidas por la mediana de las entradas (la de `median` si se da)."""
        if not len(self):
            return [("1ª mitad", self), ("2ª mitad", self)]
        mid = float(np.median(self.cols["e"])) if median is None else median
        return [("1ª mitad", self.take(self.cols["e"] <= mid)), ("2ª mitad", self.take(self.cols["e"] > mid))]


@dataclass
class View:
    """Todo lo que pinta la ventana para una elección (patrón, filtro, año, mes, día y hora). Cada lista: [(clave, operaciones)].

    Cada histograma (años, meses, días, horas) lleva los filtros de los demás pero no el suyo, para poder elegir otra barra.
    """
    main: Ops
    years: list                     # sin el filtro de años (para poder elegir otros)
    hours: list                     # sin el filtro de horas
    months: list                    # sin el filtro de meses (1-12)
    markets: list
    zones: list
    sides: list
    filters: list                   # [(clave del filtro, operaciones)]
    days: list                      # sin el filtro de días (0 lunes ... 6 domingo)
    halves: list
    sensitivity: list               # [(variante, R neto por operación)]
    outcomes: list                  # [(patrón, operaciones)]
    extra: dict = field(default_factory=dict)       # CRT: {"mtf": [(TF del FVG, operaciones)]}


@dataclass
class Group:
    """Un backtest: un grupo de mercados con los patrones, o la estrategia Calendario."""
    key: str
    name: str
    raw: dict = field(repr=False)

    @cached_property
    def ops(self) -> Ops:
        return Ops.from_json(self.raw.get("ops") or {}, self.raw.get("cats") or {})

    def table(self, name: str) -> list:
        """Hojas que llegan ya hechas (datos, metodología, mejoras, embudo)."""
        return self.raw.get(name) or []

    @property
    def patterns(self) -> list[str]:
        return list(self.raw.get("patrones") or PATTERNS)

    @property
    def filters(self) -> dict[str, str]:
        """Filtros que se eligen arriba -> nombre en la ventana."""
        own = self.raw.get("filtros")
        return dict(own) if own else {k: FILTERS[k] for k in MAIN_FILTERS}

    @property
    def all_filters(self) -> dict[str, str]:
        """Todos los filtros del grupo, para el libro «Por filtro»."""
        own = self.raw.get("filtros")
        return dict(own) if own else dict(FILTERS)

    @property
    def description(self) -> str:
        return self.raw.get("descripcion") or "patrones Continuación y Reversión en M15 · objetivo 2R · spread real"

    @property
    def markets(self) -> list[dict]:
        return self.table("datos")

    @property
    def dates(self) -> tuple[str, str]:
        """(primera, última) fecha de datos de sus mercados, «AAAA-MM-DD»; vacías si el fichero no las trae."""
        starts = [str(m.get("desde (NY)") or "")[:10] for m in self.markets]
        ends = [str(m.get("hasta (NY)") or "")[:10] for m in self.markets]
        starts, ends = [s for s in starts if s], [e for e in ends if e]
        return (min(starts), max(ends)) if starts and ends else ("", "")

    def dates_of(self, ltf: int | None = None) -> tuple[str, str]:
        """Como `dates`, pero en CRT solo de las velas del LTF (M5, M3 o M1) elegido: M1 llega mucho menos atrás."""
        if ltf is None or not self.is_crt:
            return self.dates
        rows = [m for m in self.markets if str(m.get("mercado") or "").endswith(f"M{ltf}")]
        starts = [str(m.get("desde (NY)") or "")[:10] for m in rows]
        ends = [str(m.get("hasta (NY)") or "")[:10] for m in rows]
        starts, ends = [x for x in starts if x], [x for x in ends if x]
        return (min(starts), max(ends)) if starts and ends else ("", "")

    def period_of(self, ltf: int | None = None) -> str:
        start, end = self.dates_of(ltf)
        return f"{start[:4]}-{end[:4]}" if start else "-"

    @property
    def period(self) -> str:
        """«2018-2026» con el primer y el último año de datos de sus mercados."""
        start, end = self.dates
        return f"{start[:4]}-{end[:4]}" if start else "-"

    @property
    def updated(self) -> str:
        return self.raw.get("actualizado", "")

    @property
    def profile(self) -> str:
        """Perfil de MT5 con el que se hizo el backtest (puprime, metaquotes, calendario); vacío en los ficheros antiguos."""
        return self.raw.get("perfil", "")

    @property
    def profile_name(self) -> str:
        return self.raw.get("perfil_nombre") or self.profile.capitalize()

    @property
    def is_calendar(self) -> bool:
        return self.raw.get("tipo") == "calendario"

    @property
    def is_crt(self) -> bool:
        return self.raw.get("tipo") == "crt"

    # -- selección ---------------------------------------------------------------------------
    @staticmethod
    def _in(values: np.ndarray, chosen) -> np.ndarray:
        return np.isin(values, list(chosen)) if chosen else np.ones(len(values), dtype=bool)

    def filter_mask(self, pattern: str, filt: str, ops: Ops | None = None) -> np.ndarray:
        """Operaciones de un patrón con un filtro (sin años ni horas)."""
        ops = ops or self.ops
        if self.is_calendar:
            return np.isin(ops.names("m"), self.raw["alcance"][filt])
        if self.is_crt:                                       # CRT no usa sesgo ni solapes: sus filtros son el LTF y la entrada
            return np.ones(len(ops), dtype=bool)
        s, flags = ops.names("s"), ops["f"]
        mask = {"sin filtro de sesgo": np.ones(len(ops), dtype=bool),
                "a favor del sesgo (Cortex)": s == "a favor",
                "en contra del sesgo": s == "en contra",
                "sin sesgo / lateral": s == "sin sesgo",
                "una posición a la vez (todas)": (flags & OVERLAP_ALL) == 0,
                "una posición a la vez (GO de Cortex)": (s != "en contra") & ((flags & OVERLAP_GO) == 0)}[filt]
        if pattern != "Ambos":
            mask &= ops.names("p") == pattern
        return mask

    def view(self, pattern: str, filt: str, years=(), hours=(), days=(), months=(), crt: tuple | None = None) -> View:
        if self.is_calendar:
            return self._calendar_view(filt, years, hours, days, months)
        if self.is_crt:
            return self._crt_view(years, hours, days, months, tuple(crt or ()) + CRT_DEFAULT[len(crt or ()):])
        return self._pattern_view(pattern, filt, years, hours, days, months)

    def crt_mask(self, mtf: int, ltf: int, entry: int, ops: Ops | None = None, target: int = 2) -> np.ndarray:
        """Operaciones CRT de un LTF, una entrada y un objetivo (1R, 2R o extremo de C1) y, si mtf != 0, con un FVG de ese timeframe
        de MTF tocado por el extremo del sweep. Los ficheros anteriores a los objetivos no traen la columna q: todo es 2R."""
        ops = ops or self.ops
        mask = (ops["l"] == ltf) & (ops["n"] == entry)
        if "q" in (self.raw.get("ops") or {}):
            mask &= ops["q"] == target
        if mtf:
            mask &= (ops["t"] & CRT_MTF_BITS[mtf]) != 0
        return mask

    @staticmethod
    def crt_tbr_mask(ops: Ops, tbr: str) -> np.ndarray:
        """Entradas dentro de una TBR (cualquiera, o la elegida) o fuera de todas."""
        zone = ops.names("z")
        if tbr == "Todas":
            return np.ones(len(ops), dtype=bool)
        if tbr == "Dentro de TBR":
            return zone != CRT_ZONES[-1]
        return zone == tbr

    @staticmethod
    def crt_near_mask(ops: Ops, near: str) -> np.ndarray:
        """Entradas a 15 min o menos de una hora en punto (o el resto)."""
        if near == CRT_NEAR[0]:
            return np.ones(len(ops), dtype=bool)
        return (ops["h"] >= 0) if near == CRT_NEAR[1] else (ops["h"] < 0)

    def _crt_view(self, years, hours, days, months, crt: tuple) -> View:
        """CRT: una entrada y un LTF a la vez (si no, la misma operación contaría varias veces); el timeframe del FVG filtra."""
        mtf, ltf, entry, tbr, near, target = crt
        ops = self.ops
        y, h = self._in(ops.year, years), self._in(ops.hour, hours)
        d, mo = self._in(ops.weekday, days), self._in(ops.month, months)
        chosen = y & h & d & mo
        core = self.crt_mask(mtf, ltf, entry, target=target)
        in_tbr, in_near = self.crt_tbr_mask(ops, tbr), self.crt_near_mask(ops, near)
        base = core & in_tbr & in_near
        main = ops.take(base & chosen)
        # las tablas de zona y de hora en punto llevan el filtro del otro pero no el suyo, para poder compararlas
        by_zone = ops.take(core & in_near & chosen)
        inside = by_zone.take(by_zone.names("z") != CRT_ZONES[-1])
        zones = by_zone.split(by_zone.names("z"), list(CRT_ZONES)) + [("Dentro de alguna TBR", inside), ("Todas", by_zone)]
        by_hour_tbr = ops.take(core & in_tbr & chosen)
        near_rows = [("±15 min de la hora en punto", by_hour_tbr.take(by_hour_tbr["h"] >= 0)),
                     ("Resto de horas", by_hour_tbr.take(by_hour_tbr["h"] < 0))]
        inside_all = ops.take(core & chosen)
        cross = []
        for name, zmask in (("En TBR", inside_all.names("z") != CRT_ZONES[-1]), ("Fuera de TBR", inside_all.names("z") == CRT_ZONES[-1])):
            part = inside_all.take(zmask)
            cross += [(f"{name} · ±15 min de la hora", part.take(part["h"] >= 0)), (f"{name} · resto", part.take(part["h"] < 0))]
        round_hours = [(f"{hh:02d}:00", by_hour_tbr.take(by_hour_tbr["h"] == hh)) for hh in range(24)]
        round_hours = [(k, o) for k, o in round_hours if len(o)]
        no_mtf = self.crt_mask(0, ltf, entry, target=target) & in_tbr & in_near & chosen
        mtf_rows = [(CRT_MTF_NAMES[tf], ops.take(no_mtf & ((ops["t"] & bit) != 0))) for tf, bit in CRT_MTF_BITS.items()]
        combos = {}
        for key in self.all_filters:
            lt, en = (int(x) for x in key.split(":"))
            combos[key] = ops.take(self.crt_mask(mtf, lt, en, target=target) & in_tbr & in_near & chosen)
        return View(
            main=main,
            years=self._split(ops, base & h & d & mo, "year"),
            hours=self._split(ops, base & y & d & mo, "hour"),
            months=self._split(ops, base & y & h & d, "month"),
            markets=main.split(main.names("m")),
            zones=zones,
            sides=main.split(main["d"], [0, 1]),
            filters=list(combos.items()),
            days=self._split(ops, base & y & h & mo, "weekday", list(range(7))),
            halves=main.halves(),
            sensitivity=[("Sin costes (R bruto)", main["r"] + main["k"])],
            outcomes=[("CRT", main)],
            extra={"mtf": mtf_rows, "cercania": near_rows + cross, "horas": round_hours})

    @staticmethod
    def _split(ops: Ops, mask, key: str, order: list | None = None) -> list:
        chosen = ops.take(mask)
        return chosen.split(getattr(chosen, key), order)

    def _pattern_view(self, pattern: str, filt: str, years, hours, days, months) -> View:
        ops = self.ops
        y, h = self._in(ops.year, years), self._in(ops.hour, hours)
        d, mo = self._in(ops.weekday, days), self._in(ops.month, months)
        chosen = y & h & d & mo
        base = self.filter_mask(pattern, filt)
        main = ops.take(base & chosen)
        median = float(np.median(ops["e"][chosen])) if chosen.any() else None
        sens = [(label, main[col]) for col, label in SENSITIVITY if col in main.cols] + [("2R sin costes (R bruto)", main["r"] + main["k"])]
        pats = PATTERNS[1:] if pattern == "Ambos" else (pattern,)
        return View(
            main=main,
            years=self._split(ops, base & h & d & mo, "year"),
            hours=self._split(ops, base & y & d & mo, "hour"),
            months=self._split(ops, base & y & h & d, "month"),
            markets=main.split(main.names("m")),
            zones=main.split(main.names("z"), ["Asia", "London", "NY Open"]),
            sides=main.split(main["d"], [0, 1]),
            filters=[(f, ops.take(self.filter_mask(pattern, f) & chosen)) for f in self.all_filters],
            days=self._split(ops, base & y & h & mo, "weekday", list(range(5))),
            halves=main.halves(median),
            sensitivity=sens,
            outcomes=[(p, main.take(main.names("p") == p)) for p in pats])

    def _calendar_view(self, filt: str, years, hours, days, months) -> View:
        """Calendario: la operación del bot es largo, en los días y a la hora configurados. Los controles (los cortos, los
        demás días, las demás horas) salen de las mismas velas; al elegir una hora o un día en su histograma, cambia la del
        bot."""
        ops, cfg = self.ops, self.raw
        scope = self.filter_mask("", filt)
        in_years, in_months = self._in(ops.year, years), self._in(ops.month, months)
        hour_set = set(hours) or {cfg["hora"]}
        on_days = np.isin(ops.weekday, list(set(days) or set(cfg["dias"])))
        long = ops["d"] == 0
        at_hour = np.isin(ops.hour, list(hour_set))
        main_mask = scope & on_days & long & at_hour & in_years & in_months
        main = ops.take(main_mask)
        # rejilla de stop y RR: columnas g0, g1... con el R neto de la misma entrada con otro stop / RR (largos en sus días)
        sens = [(label, main[f"g{i}"]) for i, label in enumerate(cfg.get("rejilla") or [])]
        sens.append((f"stop {cfg['stop']:g} % · RR {cfg['rr']:g} sin costes (R bruto)", main["r"] + main["k"]))
        sides = ops.take(scope & on_days & at_hour & in_years & in_months)
        return View(
            main=main,
            years=self._split(ops, scope & on_days & long & at_hour & in_months, "year"),
            hours=self._split(ops, scope & on_days & long & in_years & in_months, "hour"),
            months=self._split(ops, scope & on_days & long & at_hour & in_years, "month"),
            markets=main.split(main.names("m")),
            zones=[],
            sides=sides.split(sides["d"], [0, 1]),
            filters=[(f, ops.take(self.filter_mask("", f) & on_days & long & at_hour & in_years & in_months))
                     for f in self.all_filters],
            days=self._split(ops, scope & long & at_hour & in_years & in_months, "weekday", list(range(5))),
            halves=main.halves(),
            sensitivity=sens,
            outcomes=[("Calendario", main)])


@dataclass
class Backtest:
    groups: list[Group]
    comparison: dict
    generated: str = ""
    source: str = ""

    def group(self, key: str) -> Group | None:
        return next((g for g in self.groups if g.key == key), None)

    @property
    def profiles(self) -> list[tuple[str, str]]:
        """(clave, nombre) de los perfiles que tienen backtest, en el orden del fichero."""
        found: dict[str, str] = {}
        for g in self.groups:
            found.setdefault(g.profile, g.profile_name)
        return list(found.items())

    def groups_of(self, profile: str) -> list[Group]:
        return [g for g in self.groups if g.profile == profile]

    def profile_dates(self, profile: str) -> tuple[str, str]:
        """(primera, última) fecha de datos de todos los mercados del perfil; vacías si no las hay."""
        spans = [g.dates for g in self.groups_of(profile) if g.dates[0]]
        return (min(s for s, _ in spans), max(e for _, e in spans)) if spans else ("", "")

    def compare(self, filt: str, years=(), hours=(), profile: str | None = None, days=(), months=()) -> list[tuple[str, str, Ops]]:
        """(mercado, grupo, operaciones) de todos los mercados de los patrones (los del `profile` si se da), con ese filtro y el
        año, la hora, el día y el mes elegidos."""
        out = []
        for g in self.groups:
            if g.is_calendar or g.is_crt or (profile is not None and g.profile != profile):
                continue
            ops = g.ops
            sel = (g.filter_mask("Ambos", filt) & g._in(ops.year, years) & g._in(ops.hour, hours)
                   & g._in(ops.weekday, days) & g._in(ops.month, months))
            chosen = ops.take(sel)
            names = ops.names("m")
            for m in dict.fromkeys(names.tolist()):
                out.append((m, g.name, chosen.take(chosen.names("m") == m)))
        return out

    def compare_crt(self, profile: str, crt: tuple, years=(), hours=(), days=(), months=()) -> list[tuple[str, str, Ops]]:
        """(mercado, grupo, operaciones) de todos los mercados CRT del perfil con el TF del FVG, el LTF y la entrada elegidos."""
        out = []
        for g in self.groups_of(profile):
            if not g.is_crt:
                continue
            ops = g.ops
            mtf, ltf, entry, tbr, near, target = tuple(crt) + CRT_DEFAULT[len(crt):]
            sel = (g.crt_mask(mtf, ltf, entry, target=target) & g.crt_tbr_mask(ops, tbr) & g.crt_near_mask(ops, near)
                   & g._in(ops.year, years) & g._in(ops.hour, hours)
                   & g._in(ops.weekday, days) & g._in(ops.month, months))
            chosen = ops.take(sel)
            names = chosen.names("m")
            for m in ops.cats["m"]:
                out.append((m, g.name, chosen.take(names == m)))
        return out

    def note(self, market: str) -> str:
        return (self.comparison.get("notas_mercado") or {}).get(market, "")


def load(path: str | Path | None = None) -> Backtest:
    """Lee el backtest (.json.gz o .json). Lanza FileNotFoundError / ValueError si falta o no es válido."""
    path = Path(path) if path else DEFAULT_FILE
    if not path.exists():
        raise FileNotFoundError(f"No está el backtest ({path}). Genéralo con scripts/exportar_backtest.py")
    try:
        text = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
        data = json.loads(text.decode("utf-8"))
        groups = [Group(g["key"], g["nombre"], g) for g in data["grupos"]]
        for g in groups:
            if "ops" not in g.raw or "cats" not in g.raw:
                raise KeyError(f"el grupo {g.name} no trae operaciones")
    except (OSError, json.JSONDecodeError, KeyError, TypeError, UnicodeDecodeError) as exc:
        raise ValueError(f"{path.name} no es un backtest válido: {exc}") from None
    return Backtest(groups, data.get("comparativa") or {}, data.get("generado", ""), str(path))
