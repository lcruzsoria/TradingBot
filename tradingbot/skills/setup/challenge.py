"""Challenge simulado sobre la cuenta real de un perfil que opera de verdad (MT5_<PERFIL>_SEND_ORDERS=true).

Como el de una empresa de fondeo, por fases, cada una con su objetivo y su drawdown máximo (SETUP_CHALLENGE_TARGET_PCT y
SETUP_CHALLENGE_MAX_DD_PCT, un valor por fase: 8,8 y 6,5):
  - la fase empieza con el saldo de la cuenta en ese momento;
  - si el equity (saldo más lo flotante) cae al drawdown máximo desde ese saldo, el intento falla: el bot cierra lo
    abierto, la cuenta queda congelada el resto del día y a las 00:00 el challenge vuelve a empezar en la fase 1 (nuevo
    intento, mismas reglas, con el saldo de ese momento);
  - si el saldo llega al objetivo, la fase está superada: el bot cierra lo abierto y la cuenta queda congelada el resto
    del día; la fase siguiente empieza a las 00:00 del día siguiente (hora de este equipo);
  - superada la última fase (SETUP_CHALLENGE_PHASES, 2), el challenge queda superado y el bot sigue operando.

Las operaciones recuperadas (las que el bot no pudo hacer con el equipo suspendido; no están en MT5) cuentan: su resultado,
«ajuste_recuperadas», se suma al saldo y al equity reales.

El estado vive en `data/perfiles/<perfil>/challenge.json` (JSON legible); para empezar de cero, se borra ese fichero.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_TARGET_PCT = (8.0, 8.0)
DEFAULT_MAX_DD_PCT = (6.0, 5.0)
DEFAULT_PHASES = 2
FILE = "challenge.json"

RUNNING, FROZEN, PASSED, FAILED = "en curso", "congelado", "superado", "suspendido"


def per_phase(value, phases: int) -> tuple[float, ...]:
    """Un valor por fase a partir de un número o una lista («8» o «6,5»): si faltan, se repite el último."""
    if isinstance(value, (int, float)):
        items = [float(value)]
    elif isinstance(value, str):
        items = [float(v) for v in value.replace(";", ",").split(",") if v.strip()]
    else:
        items = [float(v) for v in value]
    if not items:
        raise ValueError("hace falta al menos un valor")
    return tuple(items[i] if i < len(items) else items[-1] for i in range(phases))


class Challenge:
    def __init__(self, path: Path | str, target_pct=DEFAULT_TARGET_PCT, max_dd_pct=DEFAULT_MAX_DD_PCT,
                 phases: int = DEFAULT_PHASES, now=datetime.now) -> None:
        if phases < 1:
            raise ValueError(f"Challenge: las fases ({phases}) deben ser 1 o más.")
        self.targets, self.max_dds = per_phase(target_pct, phases), per_phase(max_dd_pct, phases)
        if any(v <= 0 for v in (*self.targets, *self.max_dds)):
            raise ValueError(f"Challenge: objetivos ({self.targets}) y drawdowns máximos ({self.max_dds}) deben ser mayores que 0.")
        self.path, self.phases, self._now = Path(path), phases, now
        self.state: dict = {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8-sig"))
            if isinstance(data, dict) and isinstance(data.get("saldo_inicio_fase"), (int, float)):
                self.state = data
        except (OSError, ValueError):
            pass

    # -- estado ---------------------------------------------------------------------------------------------
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
    def frozen(self) -> bool:
        return self.status == FROZEN

    @property
    def next_phase(self) -> int:
        """La fase que empieza al acabar la congelación: la siguiente si se superó, la 1 si se tocó el drawdown."""
        return int(self.state.get("siguiente_fase") or self.phase + 1)

    @property
    def attempt(self) -> int:
        return int(self.state.get("intento", 1))

    @property
    def blocks_trading(self) -> str | None:
        """Por qué el bot no puede abrir operaciones ahora (None si puede)."""
        if self.failed:
            return "challenge suspendido (drawdown máximo alcanzado): el bot ya no abre operaciones"
        if self.frozen:
            why = "drawdown máximo alcanzado" if self.state.get("motivo") == "drawdown" else f"fase {self.phase} superada"
            return (f"challenge: {why}, cuenta congelada hasta las {self.frozen_until:%d/%m %H:%M}; "
                    f"entonces empieza la fase {self.next_phase}")
        return None

    @property
    def frozen_until(self) -> datetime | None:
        raw = self.state.get("congelada_hasta")
        return datetime.fromisoformat(raw) if raw else None

    @property
    def target_pct(self) -> float:
        return self.targets[min(self.phase, self.phases) - 1]

    @property
    def max_dd_pct(self) -> float:
        return self.max_dds[min(self.phase, self.phases) - 1]

    @property
    def adjustment(self) -> float:
        """Lo que suman las operaciones recuperadas: las que el bot habría hecho con el equipo suspendido. No están en MT5,
        pero cuentan en el challenge (se suman al saldo y al equity reales). En challenge.json, «ajuste_recuperadas»."""
        return float(self.state.get("ajuste_recuperadas") or 0.0)

    def rules(self) -> list[dict]:
        return [{"phase": i + 1, "target_pct": self.targets[i], "max_dd_pct": self.max_dds[i]} for i in range(self.phases)]

    def levels(self) -> tuple[float, float]:
        """(saldo objetivo de la fase, equity mínimo antes de suspender)."""
        start = float(self.state["saldo_inicio_fase"])
        return round(start * (1 + self.target_pct / 100), 2), round(start * (1 - self.max_dd_pct / 100), 2)

    def summary(self, currency: str = "") -> dict:
        target, floor = self.levels() if self.started else (None, None)
        until = self.frozen_until
        return {"phase": self.phase, "phases": self.phases, "status": self.status, "start": self.state.get("saldo_inicio_fase"),
                "target": target, "floor": floor, "target_pct": self.target_pct, "max_dd_pct": self.max_dd_pct,
                "currency": currency, "adjustment": self.adjustment, "rules": self.rules(),
                "frozen_until": until.isoformat(timespec="minutes") if until else None,
                "next_phase": self.next_phase if self.frozen else None, "reason": self.state.get("motivo"),
                "attempt": self.attempt, "marks": history_marks(self.state)}

    # -- lo que pasa al mirar la cuenta ---------------------------------------------------------------------
    def update(self, balance: float, equity: float, currency: str = "") -> list[dict]:
        """Mira la cuenta y devuelve lo que acaba de pasar: «inicio» (empieza una fase), «fase» (superada: cuenta congelada
        hasta mañana), «superado» o «suspendido» (cada evento con el resumen del challenge, el saldo y el equity)."""
        if balance <= 0 or equity <= 0:                 # lectura a medias (el terminal cambiando de cuenta): no es la cuenta
            return []
        extra = self.adjustment                         # operaciones recuperadas (no están en MT5) que sí cuentan en el challenge
        balance, equity = balance + extra, equity + extra
        events = []
        if not self.started:
            self.state = {"fase": 1, "estado": RUNNING, "saldo_inicio_fase": float(balance), "saldo_inicial": float(balance),
                          "desde": self._stamp(), "historial": []}
            events.append(self._event("inicio", balance, equity, currency))
        if self.frozen and self._now() >= self.frozen_until:          # 00:00 del día siguiente: la fase siguiente (o la 1)
            restart = self.state.get("motivo") == "drawdown"
            self.state.update(fase=self.next_phase, estado=RUNNING, saldo_inicio_fase=float(balance), congelada_hasta=None,
                              siguiente_fase=None, motivo=None, intento=self.attempt + (1 if restart else 0))
            events.append(self._event("inicio", balance, equity, currency))
        if self.status != RUNNING:
            return self._save(events)
        target, floor = self.levels()
        tomorrow = (self._now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        if equity <= floor:                             # drawdown: congelada hoy y mañana a las 00:00, otra vez la fase 1
            self.state.update(estado=FROZEN, congelada_hasta=tomorrow.isoformat(timespec="seconds"), siguiente_fase=1,
                              motivo="drawdown")
            events.append(self._frozen_event("suspendido", balance, equity, currency, tomorrow))
        elif balance >= target:
            if self.phase < self.phases:
                self.state.update(estado=FROZEN, congelada_hasta=tomorrow.isoformat(timespec="seconds"),
                                  siguiente_fase=self.phase + 1, motivo="objetivo")
                events.append(self._frozen_event("fase", balance, equity, currency, tomorrow))
            else:
                self.state["estado"] = PASSED
                events.append(self._event("superado", balance, equity, currency))
        return self._save(events)

    def _frozen_event(self, kind: str, balance: float, equity: float, currency: str, tomorrow: datetime) -> dict:
        event = self._event(kind, balance, equity, currency)
        n = self.next_phase
        event["next"] = {"phase": n, "phases": self.phases, "target_pct": self.targets[n - 1], "max_dd_pct": self.max_dds[n - 1],
                         "from": tomorrow.isoformat(timespec="minutes")}
        return event

    def _event(self, kind: str, balance: float, equity: float, currency: str) -> dict:
        event = {"kind": kind, "at": self._stamp(), "balance": round(float(balance), 2), "equity": round(float(equity), 2),
                 **self.summary(currency)}
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


# -- marcas en las curvas: el challenge real (Forwardtest) y simulado sobre el histórico (Backtest) ----------------------
MARK_COLORS = {"fase": "#22c55e", "superado": "#facc15", "drawdown1": "#ef4444", "drawdown2": "#a855f7"}
MARK_TEXT = {"fase": "Fase 2", "superado": "Superado", "drawdown1": "DD fase 1", "drawdown2": "DD fase 2"}


def mark_key(kind: str, phase: int) -> str:
    """Color de la línea: verde al pasar a la fase 2, amarillo challenge superado, rojo drawdown en la fase 1 y morado en la 2."""
    if kind == "fase":
        return "fase"
    if kind == "superado":
        return "superado"
    return "drawdown1" if phase <= 1 else "drawdown2"


def history_marks(state: dict) -> list[dict]:
    """Los momentos que se marcan en la curva del Forwardtest: fase superada, challenge superado y drawdown."""
    return [{"kind": h["kind"], "at": h["at"], "phase": int(h.get("phase", 1))} for h in state.get("historial") or []
            if h.get("kind") in ("fase", "superado", "suspendido")]


def simulate(times, rs, day_of, risk_pct: float = 1.0, targets=DEFAULT_TARGET_PCT, max_dds=DEFAULT_MAX_DD_PCT,
             phases: int = DEFAULT_PHASES) -> list[dict]:
    """El challenge sobre una lista de operaciones (hora de cierre y R, por orden de cierre), con el saldo que crece o baja un
    `risk_pct` % del saldo por cada R. Mismas reglas que en vivo: al superar una fase o tocar el drawdown no se opera el resto
    de ese día (`day_of(hora)` da el día) y al día siguiente empieza la fase siguiente o, tras drawdown o superado, la 1.
    Devuelve los eventos: {"i": índice de la operación, "t": hora, "kind": fase / superado / drawdown, "phase", "key"}."""
    targets, max_dds = per_phase(targets, phases), per_phase(max_dds, phases)
    balance, start, phase, frozen, nxt, out = 1.0, 1.0, 1, None, 1, []
    for i, (t, r) in enumerate(zip(times, rs)):
        day = day_of(t)
        if frozen is not None:
            if day <= frozen:
                continue                                # cuenta congelada: ese día no se opera
            frozen, phase, start = None, nxt, balance
        balance *= 1 + float(r) * risk_pct / 100
        kind = None
        if balance <= start * (1 - max_dds[phase - 1] / 100):
            kind, nxt = "drawdown", 1
        elif balance >= start * (1 + targets[phase - 1] / 100):
            kind, nxt = ("fase", phase + 1) if phase < phases else ("superado", 1)
        if kind:
            out.append({"i": i, "t": t, "kind": kind, "phase": phase, "key": mark_key(kind, phase)})
            frozen = day
    return out
