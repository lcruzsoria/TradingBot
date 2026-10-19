"""Cuenta virtual del perfil: el capital inicial más el resultado, en dinero, de las operaciones simuladas de Setup.

Vive en `data/perfiles/<perfil>/cuenta.json` (JSON legible). El capital inicial es el saldo de la cuenta de MT5 el día que el
perfil empieza a contar (la primera conexión); desde ahí cada operación cerrada suma o resta su resultado en R por el riesgo
de la operación (SETUP_RISK_PCT % del saldo virtual en ese momento). No se envía nada a MT5: es la cuenta «como si».
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from ...config import PROJECT_ROOT

DEFAULT_FILE = PROJECT_ROOT / "data" / "setup" / "cuenta.json"      # sin perfil (pruebas, arranques antiguos)


def file_for(app_cfg: dict | None) -> Path:
    folder = ((app_cfg or {}).get("app") or {}).get("data_dir")
    return Path(folder) / "cuenta.json" if folder else DEFAULT_FILE


def outcome(r: float) -> str:
    """G (ganada), P (perdida) o B (breakeven: 0 R, el stop ya estaba en la entrada)."""
    return "G" if r > 0 else "P" if r < 0 else "B"


class VirtualAccount:
    def __init__(self, path: Path | str | None = None, now=datetime.now) -> None:
        self.path = Path(path or DEFAULT_FILE)
        self._now = now
        self.initial: float | None = None
        self.currency = ""
        self.since: str | None = None
        self.trades: list[dict] = []
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

    def book(self, order, closed, risk_pct: float) -> float | None:
        """Apunta una operación cerrada y devuelve su importe (None si la cuenta aún no tiene capital inicial)."""
        if not self.started:
            return None
        amount = round(closed.r * self.risk_amount(risk_pct), 2)
        self.trades.append({"at": self._now().isoformat(timespec="seconds"), "symbol": order.symbol,
                            "direction": order.direction, "pattern": order.pattern, "result": closed.result,
                            "r": round(closed.r, 4), "importe": amount, "saldo": round(self.balance + amount, 2)})
        self.save()
        return amount

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"capital_inicial": self.initial, "moneda": self.currency, "desde": self.since, "operaciones": self.trades}
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def summary(self, risk_pct: float, positions=()) -> dict:
        """Lo que se publica para la cabecera (setup.account): saldo virtual, G/P/B y las abiertas con su riesgo."""
        risk = self.risk_amount(risk_pct)
        return {"started": self.started, "initial": self.initial, "balance": self.balance, "currency": self.currency,
                "since": self.since, "wins": self.count("G"), "losses": self.count("P"), "breakeven": self.count("B"),
                "risk_pct": risk_pct, "risk_amount": risk,
                "open": [{"symbol": o.symbol, "direction": o.direction, "price": o.price, "stop": o.stop} for o in positions]}
