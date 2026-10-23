"""Forwardtest: GO / NO GO de Cortex y el resultado de las operaciones simuladas de Setup desde que el bot opera.

Lo lleva la skill Stats (en su hilo), que lo guarda en el diario mensual (journal.py), y la ventana Forwardtest lo pinta a partir
de las copias que publica en `stats.session`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

SESSIONS = ("Asia", "Londres", "Nueva York", "Rollover")
ALIGNMENTS = ("A favor", "En contra", "Sin sesgo")


def session_of(ny: datetime) -> str:
    """Sesión por la hora de Nueva York de la entrada: Asia 18-03, Londres 03-08, Nueva York 08-17, Rollover 17-18."""
    h = ny.hour
    if 3 <= h < 8:
        return "Londres"
    if 8 <= h < 17:
        return "Nueva York"
    if h == 17:
        return "Rollover"
    return "Asia"


def alignment_of(order) -> str:
    """Si la operación iba a favor del sesgo vigente al entrar, en contra o sin sesgo."""
    bias = (order.bias or "").lower()
    if bias.startswith("bull"):
        return "A favor" if order.direction == "long" else "En contra"
    if bias.startswith("bear"):
        return "A favor" if order.direction == "short" else "En contra"
    return "Sin sesgo"


REASONS = (("plazo de la TBR", "T · plazo agotado"), ("ya hay una posición abierta", "Posición abierta en el mercado"), ("ya dio un trade", "Sesión TBR ya usada"),
           ("contra el sesgo", "Contra el sesgo"), ("a favor del sesgo", "A favor del sesgo"),
           ("permitido por CORTEX_ALLOW_NO_BIAS", "Sin sesgo (permitido)"), ("mercado lateral", "Mercado lateral"),
           ("sin sesgo claro", "Sin sesgo claro"), ("aún no está calculado", "Sesgo sin calcular"))


def reason_of(reason: str) -> str:
    """Motivo del GO / NO GO de Cortex agrupado (el texto completo lleva mercado, fechas y puntuación)."""
    for needle, name in REASONS:
        if needle in reason:
            return name
    head = reason.split(":", 1)[0].strip()
    return head[:1].upper() + head[1:] if head else "Sin motivo"


def trade_key(order) -> tuple | None:
    """Lo que identifica una operación: al arrancar, Cortex vuelve a anunciar los patrones recientes y no deben contar dos veces."""
    if not order.entry_ts:
        return None
    return (order.symbol, order.timeframe, order.direction, order.pattern_key, int(order.entry_ts))


@dataclass
class Signal:
    """Una señal que evalúa Cortex (un patrón detectado) y su veredicto."""
    allowed: bool
    symbol: str = ""
    timeframe: str = ""
    pattern: str = ""
    direction: str = ""
    reason: str = ""
    ts: int | None = None                # hora (servidor) de la vela del patrón
    zone: str = ""                       # TBR del patrón

    @property
    def key(self) -> tuple | None:
        return (self.symbol, self.timeframe, self.pattern, self.direction, self.ts, self.zone) if self.ts else None


@dataclass
class Trade:
    order: object                        # Order de Cortex
    closed: object | None = None         # Closed de Setup, o None mientras sigue abierta
    stale: bool = False                  # abierta en el diario de un arranque anterior y que Setup ya no sigue

    @property
    def r(self) -> float:
        return self.closed.r if self.closed else 0.0

    @property
    def duration(self) -> int | None:
        if self.closed and self.order.entry_ts:
            return max(0, self.closed.exit_ts - self.order.entry_ts)
        return None


@dataclass
class Group:
    """Una fila de un libro: las operaciones de un patrón, lado, sesión, mercado o sesgo."""
    name: str
    wins: int = 0
    losses: int = 0
    flat: int = 0                        # cerradas en 0 R
    open: int = 0
    r: float = 0.0
    pct: float = 0.0

    @property
    def n(self) -> int:
        return self.wins + self.losses + self.flat

    @property
    def win_rate(self) -> float | None:
        return 100 * self.wins / self.n if self.n else None

    @property
    def mean(self) -> float | None:
        return self.r / self.n if self.n else None


@dataclass
class TradeStats:
    """Señales de Cortex y operaciones simuladas (las de los últimos meses, que la skill recupera del diario al arrancar)."""
    signals: list[Signal] = field(default_factory=list)
    trades: list[Trade] = field(default_factory=list)
    since: str | None = None             # inicio de la etapa (fecha y hora local) si se empezó una con «Nueva etapa»

    # -- registro ----------------------------------------------------------------------------
    def decision(self, allowed: bool, signal: Signal | None = None) -> bool:
        """Anota un GO / NO GO; False si esa misma señal ya estaba (repetida al arrancar)."""
        signal = signal or Signal(allowed)
        signal.allowed = allowed
        if signal.key is not None and any(x.key == signal.key for x in self.signals):
            return False
        self.signals.append(signal)
        return True

    def find(self, order) -> Trade | None:
        key = trade_key(order)
        for t in self.trades:
            if t.order is order or (key is not None and trade_key(t.order) == key):
                return t
        return None

    def executed(self, order) -> bool:
        """Anota una operación nueva; False si ya estaba (y entonces vuelve a contar como seguida por Setup)."""
        known = self.find(order)
        if known is not None:
            known.stale = False
            return False
        self.trades.append(Trade(order))
        return True

    def closed(self, order, closed) -> bool:
        """Anota el cierre; False si no hay cierre o si ya estaba anotado."""
        if closed is None:
            return False
        t = self.find(order)
        if t is None:
            self.trades.append(Trade(order, closed))    # no la vimos entrar (p. ej. ventana creada después)
            return True
        if t.closed is not None:
            return False
        t.closed, t.stale = closed, False
        return True

    def reset(self, since: str | None = None) -> None:
        self.signals.clear()
        self.trades.clear()
        self.since = since

    def snapshot(self) -> TradeStats:
        """Copia independiente (para pasarla a otro hilo: la skill sigue anotando sobre la suya)."""
        return TradeStats(list(self.signals), [Trade(t.order, t.closed, t.stale) for t in self.trades], self.since)

    def only(self, keep: Callable[[Trade], bool], keep_signal: Callable[[Signal], bool] = lambda s: True) -> TradeStats:
        """Las mismas cifras con solo las operaciones (y señales) que cumplan el filtro."""
        return TradeStats([x for x in self.signals if keep_signal(x)], [t for t in self.trades if keep(t)], self.since)

    @property
    def go(self) -> int:
        return sum(1 for x in self.signals if x.allowed)

    @property
    def nogo(self) -> int:
        return sum(1 for x in self.signals if not x.allowed)

    # -- cifras ------------------------------------------------------------------------------
    @property
    def done(self) -> list[Trade]:
        """Cerradas, en orden de salida."""
        return sorted((t for t in self.trades if t.closed), key=lambda t: t.closed.exit_ts)

    @property
    def open(self) -> list[Trade]:
        """Abiertas que Setup sigue (sin las que quedaron sin seguimiento tras reiniciar el bot)."""
        return [t for t in self.trades if t.closed is None and not t.stale]

    @property
    def stale(self) -> list[Trade]:
        return [t for t in self.trades if t.closed is None and t.stale]

    @property
    def wins(self) -> int:
        return sum(1 for t in self.done if t.r > 0)

    @property
    def losses(self) -> int:
        return sum(1 for t in self.done if t.r < 0)

    @property
    def flat(self) -> int:
        return sum(1 for t in self.done if t.r == 0)

    def avg_max_r(self, result: str) -> float | None:
        """Máximo a favor medio (en R) de las operaciones cerradas con ese resultado («stop», «breakeven»...); None si no hay datos."""
        vals = [t.closed.max_r for t in self.done if t.closed.result == result and getattr(t.closed, "max_r", None) is not None]
        return sum(vals) / len(vals) if vals else None

    @property
    def by_time(self) -> int:
        return sum(1 for t in self.done if t.closed.result == "tiempo")

    @property
    def win_rate(self) -> float | None:
        n = len(self.done)
        return 100 * self.wins / n if n else None

    @property
    def total_r(self) -> float:
        return sum(t.r for t in self.done)

    @property
    def total_pct(self) -> float:
        return sum(t.closed.pct for t in self.done)

    @property
    def expectancy(self) -> float | None:
        n = len(self.done)
        return self.total_r / n if n else None

    @property
    def avg_win(self) -> float | None:
        won = [t.r for t in self.done if t.r > 0]
        return sum(won) / len(won) if won else None

    @property
    def avg_loss(self) -> float | None:
        lost = [t.r for t in self.done if t.r < 0]
        return sum(lost) / len(lost) if lost else None

    @property
    def avg_duration(self) -> float | None:
        secs = [t.duration for t in self.done if t.duration is not None]
        return sum(secs) / len(secs) if secs else None

    @property
    def profit_factor(self) -> float | None:
        gained = sum(t.r for t in self.done if t.r > 0)
        lost = -sum(t.r for t in self.done if t.r < 0)
        if lost:
            return gained / lost
        return float("inf") if gained else None

    @property
    def best_trade(self) -> Trade | None:
        return max(self.done, key=lambda t: t.r, default=None)

    @property
    def worst_trade(self) -> Trade | None:
        return min(self.done, key=lambda t: t.r, default=None)

    @property
    def best(self) -> float | None:
        t = self.best_trade
        return t.r if t else None

    @property
    def worst(self) -> float | None:
        t = self.worst_trade
        return t.r if t else None

    @property
    def equity(self) -> list[float]:
        """R acumulado tras cada cierre, empezando en 0."""
        out, acc = [0.0], 0.0
        for t in self.done:
            acc += t.r
            out.append(acc)
        return out

    @property
    def max_drawdown(self) -> float:
        """Mayor caída del R acumulado desde un máximo previo (en R, positiva)."""
        peak, dd = 0.0, 0.0
        for v in self.equity:
            peak = max(peak, v)
            dd = max(dd, peak - v)
        return dd

    @property
    def streak(self) -> int:
        """Racha actual: +n ganadas seguidas o -n perdidas seguidas (0 sin operaciones o si la última quedó en 0 R)."""
        n = 0
        for t in reversed(self.done):
            sign = (t.r > 0) - (t.r < 0)
            if sign == 0 or (n and (n > 0) != (sign > 0)):
                break
            n += sign
        return n

    def groups(self, key: Callable[[Trade], str], names: tuple[str, ...] | list[str] = ()) -> list[Group]:
        """Una fila por grupo: primero los de `names` (en su orden, aunque estén vacíos) y luego el resto, de más a menos R."""
        rows = {name: Group(name) for name in names}
        for t in self.trades:
            g = rows.setdefault(key(t), Group(key(t)))
            if t.closed is None:
                g.open += not t.stale
                continue
            g.wins += t.r > 0
            g.losses += t.r < 0
            g.flat += t.r == 0
            g.r += t.r
            g.pct += t.closed.pct
        fixed = [rows.pop(name) for name in names]
        return fixed + sorted(rows.values(), key=lambda g: (-g.r, -g.n, g.name))

    def signal_groups(self, key: Callable[[Signal], str]) -> list[tuple[str, int, int]]:
        """(nombre, GO, NO GO) de las señales de Cortex por grupo, de más a menos señales."""
        rows: dict[str, list[int]] = {}
        for x in self.signals:
            row = rows.setdefault(key(x), [0, 0])
            row[0 if x.allowed else 1] += 1
        return sorted(((k, go, nogo) for k, (go, nogo) in rows.items()), key=lambda r: (-(r[1] + r[2]), r[0]))

    def breakdown(self, key: Callable[[object], str]) -> list[tuple[str, int, int, float]]:
        """(nombre, cerradas, ganadas, R total) por grupo con alguna cerrada, de más a menos R."""
        return [(g.name, g.n, g.wins, g.r) for g in self.groups(lambda t: key(t.order)) if g.n]
