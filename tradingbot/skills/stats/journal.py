"""Diario del forwardtest: lo que pasa desde que el bot opera, en un fichero por mes que no se borra nunca.

Cada línea de `data/forwardtest/AAAA-MM.jsonl` es un JSON con `t` (tipo) y `at` (fecha y hora local en que se anotó):

- `signal`  una señal que evaluó Cortex: veredicto, motivo, mercado, temporalidad, patrón, lado, TBR y hora de la vela
- `open`    una operación simulada que abre Setup: la orden completa de Cortex (precio, stop, objetivo, sesgo, TBR...)
- `close`   su cierre: la orden otra vez (así cada mes se entiende solo) y el resultado (objetivo, stop o tiempo, R, %)
- `stage`   «Nueva etapa»: las cifras en vivo empiezan desde aquí; los meses guardados se ven completos

Al arrancar se cargan todos los meses desde el inicio del forwardtest (STATS_FORWARD_START), sea cual sea el perfil de MT5:
el diario es uno solo y acumula lo de todos. Cada mes también se abre suelto desde la ventana Forwardtest. Las líneas que no se entienden se saltan, para que un fichero a medio escribir no rompa nada.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, fields
from datetime import datetime
from pathlib import Path

from ...config import PROJECT_ROOT
from ..setup.positions import Closed
from ..setup.store import order_from_json as _order_from_json, order_to_json as _order_to_json
from .session import Signal, TradeStats

DEFAULT_DIR = PROJECT_ROOT / "data" / "forwardtest"
MONTH_FILE = re.compile(r"^(\d{4})-(\d{2})\.jsonl$")
MONTH_NAMES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre",
               "diciembre")


def month_of(when: datetime) -> str:
    return f"{when.year:04d}-{when.month:02d}"


def previous_month(month: str) -> str:
    y, m = (int(x) for x in month.split("-"))
    return f"{y - 1:04d}-12" if m == 1 else f"{y:04d}-{m - 1:02d}"


def next_month(month: str) -> str:
    y, m = (int(x) for x in month.split("-"))
    return f"{y + 1:04d}-01" if m == 12 else f"{y:04d}-{m + 1:02d}"


def month_label(month: str) -> str:
    y, m = (int(x) for x in month.split("-"))
    return f"{MONTH_NAMES[m - 1].capitalize()} {y}"


def _pick(cls, data: dict) -> dict:
    names = {f.name for f in fields(cls)}
    return {k: v for k, v in data.items() if k in names}


class Journal:
    def __init__(self, folder: Path | str | None = None, now=datetime.now) -> None:
        self.folder = Path(folder) if folder else DEFAULT_DIR
        self._now = now

    def path(self, month: str) -> Path:
        return self.folder / f"{month}.jsonl"

    def months(self) -> list[str]:
        """Meses con diario, del más reciente al más antiguo."""
        if not self.folder.is_dir():
            return []
        found = [f"{m.group(1)}-{m.group(2)}" for p in self.folder.iterdir() if (m := MONTH_FILE.match(p.name))]
        return sorted(found, reverse=True)

    # -- escribir ------------------------------------------------------------------------------
    def _write(self, record: dict) -> None:
        now = self._now()
        record = {"t": record.pop("t"), "at": now.isoformat(timespec="seconds"), **record}
        self.folder.mkdir(parents=True, exist_ok=True)
        with self.path(month_of(now)).open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def signal(self, signal: Signal) -> None:
        self._write({"t": "signal", **asdict(signal)})

    def opened(self, order) -> None:
        self._write({"t": "open", "order": _order_to_json(order)})

    def closed(self, order, closed) -> None:
        self._write({"t": "close", "order": _order_to_json(order), "closed": asdict(closed)})

    def stage(self) -> str:
        at = self._now().isoformat(timespec="seconds")
        self._write({"t": "stage"})
        return at

    # -- leer ----------------------------------------------------------------------------------
    def _records(self, month: str) -> list[dict]:
        path = self.path(month)
        if not path.exists():
            return []
        out = []
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if isinstance(rec, dict) and "t" in rec:
                out.append(rec)
        return out

    @staticmethod
    def _replay(stats: TradeStats, rec: dict, stale: bool) -> None:
        try:
            if rec["t"] == "signal":
                sig = Signal(**_pick(Signal, rec))
                stats.decision(sig.allowed, sig)
            elif rec["t"] == "open":
                order = _order_from_json(rec["order"])
                if stats.executed(order):
                    stats.trades[-1].stale = stale
            elif rec["t"] == "close":
                stats.closed(_order_from_json(rec["order"]), Closed(**_pick(Closed, rec["closed"])))
        except (KeyError, TypeError, ValueError):
            pass                                        # línea de otra versión o incompleta: se salta

    def load_recent(self, first: str | None = None) -> TradeStats:
        """Lo que vuelve a la memoria de la skill al arrancar: todos los meses desde `first` (AAAA-MM, el del inicio del
        forwardtest; sin él, todo el diario), desde la última «Nueva etapa».

        Las abiertas quedan «sin seguimiento» hasta que Setup las vuelva a anunciar (Cortex repite los patrones recientes).
        """
        current = month_of(self._now())
        records = [rec for m in sorted(self.months()) if (first is None or m >= first) and m <= current
                   for rec in self._records(m)]
        stages = [i for i, rec in enumerate(records) if rec["t"] == "stage"]
        stats = TradeStats(since=records[stages[-1]].get("at") if stages else None)
        for rec in records[stages[-1] + 1 if stages else 0:]:
            self._replay(stats, rec, stale=True)
        return stats

    def load_month(self, month: str) -> TradeStats:
        """Un mes guardado completo: sus señales y las operaciones que se abrieron en él (con su cierre aunque caiga en el
        mes siguiente). Las que no tienen cierre se ven sin seguimiento."""
        stats = TradeStats()
        before = TradeStats()                           # las abiertas el mes anterior cuentan en su mes, no en este
        for rec in self._records(previous_month(month)):
            if rec["t"] == "open":
                self._replay(before, rec, stale=True)
        for rec in self._records(month):
            if rec["t"] == "close":
                try:
                    if before.find(_order_from_json(rec["order"])) is not None:
                        continue
                except (KeyError, TypeError, ValueError):
                    continue
            self._replay(stats, rec, stale=True)
        for rec in self._records(next_month(month)):
            if rec["t"] == "close":
                try:
                    order = _order_from_json(rec["order"])
                except (KeyError, TypeError, ValueError):
                    continue
                if stats.find(order) is not None:
                    self._replay(stats, rec, stale=True)
        return stats
