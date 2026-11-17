"""Challenge simulado sobre la cuenta real de un perfil que opera de verdad (MT5_<PERFIL>_SEND_ORDERS=true).

Como el de una empresa de fondeo: cada fase empieza con el saldo de la cuenta en ese momento. Se pasa de fase cuando el saldo
llega a +SETUP_CHALLENGE_TARGET_PCT % (8 %) y la cuenta queda suspendida si el equity (saldo más lo flotante) cae a
-SETUP_CHALLENGE_MAX_DD_PCT % (6 %) del inicio de la fase: el bot cierra lo abierto y no abre nada más. Superada la última
fase (SETUP_CHALLENGE_PHASES, 2), el challenge queda superado y el bot sigue operando.

El estado vive en `data/perfiles/<perfil>/challenge.json` (JSON legible); para empezar de cero, se borra ese fichero.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

DEFAULT_TARGET_PCT = 8.0
DEFAULT_MAX_DD_PCT = 6.0
DEFAULT_PHASES = 2
FILE = "challenge.json"

RUNNING, PASSED, FAILED = "en curso", "superado", "suspendido"


class Challenge:
    def __init__(self, path: Path | str, target_pct: float = DEFAULT_TARGET_PCT, max_dd_pct: float = DEFAULT_MAX_DD_PCT,
                 phases: int = DEFAULT_PHASES, now=datetime.now) -> None:
        if target_pct <= 0 or max_dd_pct <= 0 or phases < 1:
            raise ValueError(f"Challenge: objetivo ({target_pct:g} %) y drawdown máximo ({max_dd_pct:g} %) deben ser mayores "
                             f"que 0, y las fases ({phases}), 1 o más.")
        self.path, self.target_pct, self.max_dd_pct, self.phases, self._now = Path(path), target_pct, max_dd_pct, phases, now
        self.state: dict = {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("saldo_inicio_fase"), (int, float)):
                self.state = data
        except (OSError, ValueError):
            pass

    @property
    def started(self) -> bool:
        return bool(self.state)

    @property
    def status(self) -> str:
        return self.state.get("estado", RUNNING)

    @property
    def phase(self) -> int:
        return int(self.state.get("fase", 1))

    @property
    def failed(self) -> bool:
        return self.status == FAILED

    @property
    def adjustment(self) -> float:
        """Lo que suman las operaciones recuperadas: las que el bot habría hecho con el equipo suspendido. No están en MT5,
        pero cuentan en el challenge (se suman al saldo y al equity reales). En challenge.json, «ajuste_recuperadas»."""
        return float(self.state.get("ajuste_recuperadas") or 0.0)

    def levels(self) -> tuple[float, float]:
        """(saldo objetivo de la fase, equity mínimo antes de suspender)."""
        start = float(self.state["saldo_inicio_fase"])
        return round(start * (1 + self.target_pct / 100), 2), round(start * (1 - self.max_dd_pct / 100), 2)

    def summary(self, currency: str = "") -> dict:
        target, floor = self.levels() if self.started else (None, None)
        return {"phase": self.phase, "phases": self.phases, "status": self.status, "start": self.state.get("saldo_inicio_fase"),
                "target": target, "floor": floor, "target_pct": self.target_pct, "max_dd_pct": self.max_dd_pct,
                "currency": currency, "adjustment": self.adjustment}

    def update(self, balance: float, equity: float, currency: str = "") -> list[dict]:
        """Mira la cuenta y devuelve lo que acaba de pasar: «inicio», «fase» (pasa a la siguiente), «superado» o
        «suspendido» (cada evento con el resumen del challenge, el saldo y el equity)."""
        if balance <= 0 or equity <= 0:                 # lectura a medias (el terminal cambiando de cuenta): no es la cuenta
            return []
        extra = self.adjustment                         # operaciones recuperadas (no están en MT5) que sí cuentan en el challenge
        balance, equity = balance + extra, equity + extra
        events = []
        if not self.started:
            self.state = {"fase": 1, "estado": RUNNING, "saldo_inicio_fase": float(balance), "saldo_inicial": float(balance),
                          "desde": self._stamp(), "historial": []}
            events.append(self._event("inicio", balance, equity, currency))
        if self.status != RUNNING:
            return self._save(events)
        target, floor = self.levels()
        if equity <= floor:
            self.state["estado"] = FAILED
            events.append(self._event("suspendido", balance, equity, currency))
        elif balance >= target:
            if self.phase < self.phases:
                done = self._event("fase", balance, equity, currency)
                self.state.update(fase=self.phase + 1, saldo_inicio_fase=float(balance))
                done["new"] = self.summary(currency)
                events.append(done)
            else:
                self.state["estado"] = PASSED
                events.append(self._event("superado", balance, equity, currency))
        return self._save(events)

    def _event(self, kind: str, balance: float, equity: float, currency: str) -> dict:
        event = {"kind": kind, "at": self._stamp(), "balance": round(float(balance), 2), "equity": round(float(equity), 2),
                 **self.summary(currency)}
        if kind != "inicio":
            self.state.setdefault("historial", []).append({k: event[k] for k in ("kind", "at", "phase", "balance", "equity")})
        return event

    def _stamp(self) -> str:
        return self._now().isoformat(timespec="seconds")

    def _save(self, events: list[dict]) -> list[dict]:
        if events:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(self.path)
        return events
