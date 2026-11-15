"""Enigma369 en la ventana Backtest: zona del máximo y el mínimo de cada día (grupo de tipo «extremos», de scripts/exportar_backtest_enigma369.py).

Cada extremo (columnas en `ops`) apunta a su día (columnas en `dias`), que guarda cuántas velas hay en cada zona: con eso cada % de extremos se
compara con el % de tiempo de esa misma selección de días. Todo se recalcula aquí con el año, el mes y el día elegidos en los histogramas.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

SESSIONS = ("Asia", "London", "NY AM", "NY PM")
CELLS = [(s, q) for s in range(1, 5) for q in range(1, 5)]                # (sesión, cuarto), en el orden de las velas
CRITICAL = (3, 6, 9)
SIDES = {"Ambos": None, "Máximo": 0, "Mínimo": 1}
# condición -> (columna del extremo, columna de tiempo del día, columna por sesión-cuarto del día, necesita velas de 3 min)
CONDITIONS = {"Cuarto 3-6-9": ("n", "crit", "fc", False), "Alineación 3-6-9 hasta el cuarto": ("a", "ba", "fa", False),
              "Combinación de color hasta el cuarto": ("c", "bt", "ft", False), "Micro 3-6-9": ("mn", "mcrit", "c3c", True),
              "Alineación 3-6-9 hasta el micro": ("ma", "bma", "c3a", True), "Combinación de color hasta el micro": ("mc", "bmt", "c3t", True)}


def cell_name(s: int, q: int) -> str:
    return f"{SESSIONS[s - 1]} Q{q}"


def z_score(hits: int, n: int, p: float) -> float | None:
    """Binomial: cuántas desviaciones se aleja `hits` de lo esperado con probabilidad `p` en `n` extremos."""
    if n <= 0 or not 0 < p < 1:
        return None
    return (hits - n * p) / math.sqrt(n * p * (1 - p))


@dataclass
class Share:
    """% de extremos en una zona frente al % de tiempo de esa zona."""
    hits: int
    n: int
    base: float                       # fracción de tiempo (0-1)
    ctrl: float | None = None         # fracción esperada manteniendo la sesión-cuarto de cada extremo (control por horario)
    ctrl_var: float = 0.0             # varianza de los aciertos esperados con ese control (suma de p(1-p))

    @property
    def pct(self) -> float | None:
        return 100 * self.hits / self.n if self.n else None

    @property
    def excess(self) -> float | None:
        """Puntos de diferencia entre el % de extremos y el % de tiempo."""
        return None if self.pct is None else self.pct - 100 * self.base

    @property
    def ratio(self) -> float | None:
        return self.pct / (100 * self.base) if self.pct is not None and self.base > 0 else None

    @property
    def z(self) -> float | None:
        return z_score(self.hits, self.n, self.base)

    @property
    def ctrl_excess(self) -> float | None:
        return None if self.pct is None or self.ctrl is None else self.pct - 100 * self.ctrl

    @property
    def z_ctrl(self) -> float | None:
        """Como z, pero frente a lo esperado por horario."""
        if self.ctrl is None or not self.n or self.ctrl_var <= 0:
            return None
        return (self.hits - self.n * self.ctrl) / math.sqrt(self.ctrl_var)


@dataclass
class Selection:
    """Extremos y días elegidos. `ext`: columnas de los extremos; `days`: máscara de días (por índice de día)."""
    ext: dict
    days: np.ndarray
    dcols: dict
    cats: list = field(default_factory=list)

    @property
    def n(self) -> int:
        return len(self.ext["d"])

    @property
    def n_days(self) -> int:
        return int(self.days.sum())

    def _time(self, col: str, micro: bool = False) -> float:
        d, sel = self.dcols, self.days
        total = d["k3"][sel].sum() if micro else d["k"][sel].sum()
        if not total:
            return 0.0
        if col == "crit":
            part = d["bn"][sel][:, [2, 5, 8]].sum()
        elif col == "mcrit":
            part = d["bmn"][sel][:, [2, 5, 8]].sum()
        else:
            part = d[col][sel].sum()
        return float(part) / float(total)

    def _by_cell(self, ccol: str, micro: bool) -> np.ndarray:
        """Probabilidad de la condición en cada sesión-cuarto, en los días elegidos (los de velas de 3 min para el micro)."""
        d, sel = self.dcols, self.days
        if micro:
            sel = sel & (d["k3"] > 0)
            bars = d["c3"][sel].sum(axis=0).astype(float)
            return np.divide(d[ccol][sel].sum(axis=0), bars, out=np.zeros(16), where=bars > 0)
        if not sel.any():
            return np.zeros(16)
        bits = (d[ccol][sel][:, None] >> np.arange(16)) & 1
        return bits.mean(axis=0)

    def condition(self, name: str) -> Share:
        col, tcol, ccol, micro = CONDITIONS[name]
        e = self.ext
        mask = e["mi"] > 0 if micro else np.ones(self.n, dtype=bool)
        hits = np.isin(e[col], CRITICAL) if col in ("n", "mn") else e[col] > 0
        n = int(mask.sum())
        p = self._by_cell(ccol, micro)[((e["s"] - 1) * 4 + e["q"] - 1)[mask]]
        return Share(int((hits & mask).sum()), n, self._time(tcol, micro), float(p.mean()) if n else None, float((p * (1 - p)).sum()))

    def cells(self) -> list[tuple[tuple[int, int], Share]]:
        d = self.dcols
        k = d["k"][self.days].sum()
        per = d["bs"][self.days].sum(axis=0)
        code = (self.ext["s"] - 1) * 4 + self.ext["q"] - 1
        counts = np.bincount(code, minlength=16)
        return [(c, Share(int(counts[i]), self.n, float(per[i]) / k if k else 0.0)) for i, c in enumerate(CELLS)]

    def sessions(self) -> list[tuple[int, Share]]:
        cells = self.cells()
        return [(s, Share(sum(sh.hits for (cs, _), sh in cells if cs == s), self.n, sum(sh.base for (cs, _), sh in cells if cs == s)))
                for s in range(1, 5)]

    def numbers(self) -> list[tuple[int, Share]]:
        d = self.dcols
        k = d["k"][self.days].sum()
        per = d["bn"][self.days].sum(axis=0)
        counts = np.bincount(self.ext["n"], minlength=10)
        counted = int((self.ext["n"] > 0).sum())
        k_counted = per.sum()
        return [(i + 1, Share(int(counts[i + 1]), counted, float(per[i]) / k_counted if k_counted else 0.0)) for i in range(9)] if k else []

    def micros(self) -> list[tuple[int, Share]]:
        d = self.dcols
        k3 = d["k3"][self.days].sum()
        per = d["bm"][self.days].sum(axis=0)
        mi = self.ext["mi"]
        n = int((mi > 0).sum())
        return [(i, Share(int((mi == i).sum()), n, float(per[i - 1]) / k3 if k3 else 0.0)) for i in range(1, 5)]

    def opening(self) -> int:
        return int(self.ext["g"].sum())


class Extremes:
    """Los extremos de un grupo de tipo «extremos», listos para elegir por lado, filtro, año, mes y día."""

    def __init__(self, raw: dict) -> None:
        self.cats = list((raw.get("cats") or {}).get("m") or [])
        ops, dias = raw.get("ops") or {}, raw.get("dias") or {}
        self.ext = {k: np.asarray(v, dtype=np.int64) for k, v in ops.items()}
        self.dcols = {k: np.asarray(v, dtype=np.int64) for k, v in dias.items()}
        t = self.dcols.get("t", np.zeros(0, dtype=np.int64))
        date = t.astype("datetime64[D]")
        self.dcols["year"] = date.astype("datetime64[Y]").astype(np.int64) + 1970
        self.dcols["month"] = date.astype("datetime64[M]").astype(np.int64) % 12 + 1

    def __len__(self) -> int:
        return len(self.ext.get("d", []))

    def _day_mask(self, filt: str, years=(), months=(), days=()) -> np.ndarray:
        d = self.dcols
        mask = np.ones(len(d.get("t", [])), dtype=bool)
        if filt == "cuentan":
            mask &= d["q0"] == 0
        if years:
            mask &= np.isin(d["year"], list(years))
        if months:
            mask &= np.isin(d["month"], list(months))
        if days:
            mask &= np.isin(d["wd"], list(days))
        return mask

    def select(self, pattern: str = "Ambos", filt: str = "cuentan", years=(), months=(), days=(), market: int | None = None) -> Selection:
        """`filt`: «cuentan» (sin Q0), «todos»; con «_sa» detrás quita los extremos de la vela de apertura (18:00: el hueco del día)."""
        base, _, no_open = filt.partition("_")
        dmask = self._day_mask(base, years, months, days)
        if market is not None:
            dmask &= self.dcols["m"] == market
        emask = dmask[self.ext["i"]] if len(self) else np.zeros(0, dtype=bool)
        side = SIDES.get(pattern)
        if side is not None:
            emask &= self.ext["d"] == side
        if no_open:
            emask &= self.ext["g"] == 0
        return Selection({k: v[emask] for k, v in self.ext.items()}, dmask, self.dcols, self.cats)

    def split(self, key: str, values, pattern: str, filt: str, years=(), months=(), days=()) -> list[tuple[int, Selection]]:
        """Una selección por cada valor de `key` (year, month, wd), sin su propio filtro y con los demás."""
        arg = {"year": "years", "month": "months", "wd": "days"}[key]
        out = []
        for v in values:
            chosen = {"years": years, "months": months, "days": days, arg: (v,)}
            sel = self.select(pattern, filt, **chosen)
            if sel.n:
                out.append((v, sel))
        return out

    @property
    def years(self) -> list[int]:
        return sorted(set(self.dcols["year"].tolist()))
