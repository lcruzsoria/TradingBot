"""Lo que ha pasado en la sesión del bot: GO / NO GO de Cortex y el resultado de las operaciones simuladas de Setup.

Lo lleva la skill Stats (en su hilo) y la ventana Estadísticas lo pinta a partir de las copias que publica en `stats.session`.
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


@dataclass
class Trade:
    order: object                        # Order de Cortex
    closed: object | None = None         # Closed de Setup, o None mientras sigue abierta

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
    """Lo que ha pasado en la sesión: GO / NO GO de Cortex y las operaciones simuladas (se pierde al reiniciar el bot)."""
    go: int = 0
    nogo: int = 0
    trades: list[Trade] = field(default_factory=list)

    # -- registro ----------------------------------------------------------------------------
    def decision(self, allowed: bool) -> None:
        if allowed:
            self.go += 1
        else:
            self.nogo += 1

    def executed(self, order) -> None:
        self.trades.append(Trade(order))

    def closed(self, order, closed) -> None:
        if closed is None:
            return
        for t in self.trades:
            if t.order is order and t.closed is None:
                t.closed = closed
                return
        self.trades.append(Trade(order, closed))        # no la vimos entrar (p. ej. ventana creada después)

    def reset(self) -> None:
        self.go = self.nogo = 0
        self.trades.clear()

    def snapshot(self) -> TradeStats:
        """Copia independiente (para pasarla a otro hilo: la skill sigue anotando sobre la suya)."""
        return TradeStats(self.go, self.nogo, [Trade(t.order, t.closed) for t in self.trades])

    def only(self, keep: Callable[[Trade], bool]) -> TradeStats:
        """Las mismas cifras con solo las operaciones que cumplan `keep` (los GO / NO GO de Cortex no se filtran)."""
        return TradeStats(self.go, self.nogo, [t for t in self.trades if keep(t)])

    # -- cifras ------------------------------------------------------------------------------
    @property
    def done(self) -> list[Trade]:
        """Cerradas, en orden de salida."""
        return sorted((t for t in self.trades if t.closed), key=lambda t: t.closed.exit_ts)

    @property
    def open(self) -> list[Trade]:
        return [t for t in self.trades if t.closed is None]

    @property
    def wins(self) -> int:
        return sum(1 for t in self.done if t.r > 0)

    @property
    def losses(self) -> int:
        return sum(1 for t in self.done if t.r < 0)

    @property
    def flat(self) -> int:
        return sum(1 for t in self.done if t.r == 0)

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
                g.open += 1
                continue
            g.wins += t.r > 0
            g.losses += t.r < 0
            g.flat += t.r == 0
            g.r += t.r
            g.pct += t.closed.pct
        fixed = [rows.pop(name) for name in names]
        return fixed + sorted(rows.values(), key=lambda g: (-g.r, -g.n, g.name))

    def breakdown(self, key: Callable[[object], str]) -> list[tuple[str, int, int, float]]:
        """(nombre, cerradas, ganadas, R total) por grupo con alguna cerrada, de más a menos R."""
        return [(g.name, g.n, g.wins, g.r) for g in self.groups(lambda t: key(t.order)) if g.n]
