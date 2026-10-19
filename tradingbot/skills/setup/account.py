"""Cuenta virtual del perfil: el capital inicial más el resultado, en dinero, de las operaciones del forwardtest.

Vive en `data/perfiles/<perfil>/cuenta.json` (JSON legible). El capital inicial es el saldo de la cuenta de MT5 el día que el
perfil empieza a contar (la primera conexión). Las operaciones no se apuntan al cerrar, sino al **consolidar**: el diario del
forwardtest del perfil se pasa a la cuenta al cierre de cada vela de 3 h (índices) o de 4 h (el resto) posterior al cierre
de la operación. Cada una suma o resta su resultado en R por el riesgo (SETUP_RISK_PCT % del saldo virtual en ese momento).
No se envía nada a MT5: es la cuenta «como si».
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from ...config import PROJECT_ROOT
from ..levels.daylevels import DEFAULT_US_INDICES, is_us_index

DEFAULT_FILE = PROJECT_ROOT / "data" / "setup" / "cuenta.json"      # sin perfil (pruebas, arranques antiguos)
DEFAULT_INDEX_HOURS = 3           # SETUP_CONSOLIDATE_INDEX_HOURS: velas tras las que se consolidan los índices USA
DEFAULT_OTHER_HOURS = 4           # SETUP_CONSOLIDATE_HOURS: las del resto de mercados


def file_for(app_cfg: dict | None) -> Path:
    folder = ((app_cfg or {}).get("app") or {}).get("data_dir")
    return Path(folder) / "cuenta.json" if folder else DEFAULT_FILE


def outcome(r: float) -> str:
    """G (ganada), P (perdida) o B (breakeven: 0 R, el stop ya estaba en la entrada)."""
    return "G" if r > 0 else "P" if r < 0 else "B"


def trade_id(order) -> str:
    """Lo que identifica una operación en la cuenta (el mismo criterio que el diario del forwardtest)."""
    return f"{order.symbol}|{order.timeframe}|{order.direction}|{order.pattern_key}|{int(order.entry_ts or 0)}"


class Schedule:
    """Cuándo se consolida cada cierre: al terminar la vela de 3 h (índices USA) o de 4 h (resto) en la que cerró, en hora
    del servidor (las velas de MT5 empiezan a medianoche del servidor; 3 y 4 dividen las 24 h)."""

    def __init__(self, index_hours: int = DEFAULT_INDEX_HOURS, other_hours: int = DEFAULT_OTHER_HOURS,
                 indices=DEFAULT_US_INDICES) -> None:
        for name, hours in (("SETUP_CONSOLIDATE_INDEX_HOURS", index_hours), ("SETUP_CONSOLIDATE_HOURS", other_hours)):
            if hours <= 0 or 24 % hours:
                raise ValueError(f"{name}={hours} debe dividir el día en velas enteras (1, 2, 3, 4, 6, 8, 12 o 24).")
        self.index_hours, self.other_hours, self.indices = index_hours, other_hours, tuple(indices)

    def hours(self, symbol: str) -> int:
        return self.index_hours if is_us_index(symbol, self.indices) else self.other_hours

    def due(self, symbol: str, exit_ts: int) -> int:
        """Hora (servidor) del cierre de la vela en la que se cerró la operación: entonces pasa a la cuenta."""
        period = self.hours(symbol) * 3600
        return (int(exit_ts) // period + 1) * period


class VirtualAccount:
    def __init__(self, path: Path | str | None = None, now=datetime.now) -> None:
        self.path = Path(path or DEFAULT_FILE)
        self._now = now
        self.initial: float | None = None
        self.currency = ""
        self.since: str | None = None
        self.trades: list[dict] = []
        self.pending: list[int] = []                    # hora (servidor) de consolidación de las cerradas aún sin pasar
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if isinstance(data, dict) and isinstance(data.get("capital_inicial"), (int, float)):
            self.initial = float(data["capital_inicial"])
            self.currency = str(data.get("moneda") or "")
            self.since = data.get("desde")
            self.trades = [t for t in data.get("operaciones") or [] if isinstance(t, dict) and "importe" in t]

    @property
    def started(self) -> bool:
        return self.initial is not None

    @property
    def balance(self) -> float:
        return (self.initial or 0.0) + sum(float(t["importe"]) for t in self.trades)

    def count(self, kind: str) -> int:
        return sum(1 for t in self.trades if outcome(float(t.get("r", 0))) == kind)

    def start(self, balance: float, currency: str) -> bool:
        """Fija el capital inicial (solo la primera vez). True si acaba de empezar."""
        if self.started or balance <= 0:
            return False
        self.initial, self.currency = float(balance), currency
        self.since = self._now().isoformat(timespec="seconds")
        self.save()
        return True

    def risk_amount(self, risk_pct: float) -> float:
        return self.balance * risk_pct / 100

    def book(self, order, closed, risk_pct: float, due: int | None = None) -> float | None:
        """Apunta una operación cerrada y devuelve su importe (None si la cuenta aún no tiene capital inicial)."""
        if not self.started:
            return None
        amount = round(closed.r * self.risk_amount(risk_pct), 2)
        self.trades.append({"id": trade_id(order), "at": self._now().isoformat(timespec="seconds"), "symbol": order.symbol,
                            "direction": order.direction, "pattern": order.pattern, "result": closed.result,
                            "r": round(closed.r, 4), "cierre_ts": int(closed.exit_ts), "consolidada_ts": due,
                            "importe": amount, "saldo": round(self.balance + amount, 2)})
        self.save()
        return amount

    def consolidate(self, closes, server_now: int, risk_pct: float, schedule: Schedule) -> list[dict]:
        """Pasa a la cuenta las cerradas del diario cuya vela de consolidación ya terminó (por orden de consolidación y de
        cierre) y deja en `pending` las demás. Devuelve las que acaba de apuntar."""
        booked = {t.get("id") for t in self.trades}
        waiting = sorted(((schedule.due(o.symbol, c.exit_ts), int(c.exit_ts), o, c) for o, c in closes
                          if trade_id(o) not in booked), key=lambda x: x[:2])
        if not self.started:
            self.pending = [due for due, *_ in waiting]
            return []
        new = []
        for due, _, order, closed in waiting:
            if due <= server_now:
                self.book(order, closed, risk_pct, due)
                new.append(self.trades[-1])
        self.pending = [due for due, *_ in waiting if due > server_now]
        return new

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"capital_inicial": self.initial, "moneda": self.currency, "desde": self.since, "operaciones": self.trades}
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def summary(self, risk_pct: float, positions=()) -> dict:
        """Lo que se publica para la cabecera (setup.account): saldo virtual, G/P/B, las cerradas pendientes de consolidar
        (y la próxima consolidación, en hora del servidor) y las abiertas con su riesgo."""
        risk = self.risk_amount(risk_pct)
        return {"started": self.started, "initial": self.initial, "balance": self.balance, "currency": self.currency,
                "since": self.since, "wins": self.count("G"), "losses": self.count("P"), "breakeven": self.count("B"),
                "pending": len(self.pending), "next_at": min(self.pending) if self.pending else None,
                "risk_pct": risk_pct, "risk_amount": risk,
                "open": [{"symbol": o.symbol, "direction": o.direction, "price": o.price, "stop": o.stop} for o in positions]}
