"""Skills: unidades de trabajo que viven en el panel de hexágonos.

Cada skill es un "actor": tiene su propio hilo y su cola de mensajes, se suscribe a los
temas que le interesan y publica los suyos en el bus. Para crear una nueva:

    from tradingbot.core import Skill, register_skill

    @register_skill("risk")
    class RiskSkill(Skill):
        title = "Risk"
        description = "Valida el tamaño de cada operación"
        subscribes = ("trade.request",)
        publishes = ("risk.verdict",)
        slot = 2                       # posición en el anillo (0-5), "center" o "aux1".."aux3"

        def handle(self, event):
            self.publish("risk.verdict", {"ok": True})
"""
from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar

from .bus import Event, EventBus

SKILL_REGISTRY: dict[str, type["Skill"]] = {}
RING_SLOTS = (0, 1, 2, 3, 4, 5)          # sentido horario empezando arriba
AUX_SLOTS = ("aux1", "aux2", "aux3")


class SkillState(str, Enum):
    IDLE = "idle"
    WORKING = "working"
    OK = "ok"
    ERROR = "error"


def register_skill(key: str):
    def decorator(cls: type["Skill"]) -> type["Skill"]:
        cls.key = key
        SKILL_REGISTRY[key] = cls
        return cls
    return decorator


@dataclass(frozen=True)
class SkillInfo:
    key: str
    title: str
    description: str
    slot: int | str
    subscribes: tuple[str, ...]
    publishes: tuple[str, ...]


@dataclass
class Services:
    """Recursos compartidos que reciben todas las skills."""
    source: Any            # DataSource (MT5 real o sintético)
    engine: Any            # BiasEngine
    app_cfg: dict
    env: Any = None        # EnvConfig de tradingbot.env (opcional)


class Skill:
    key: ClassVar[str] = ""
    title: ClassVar[str] = ""
    description: ClassVar[str] = ""
    subscribes: ClassVar[tuple[str, ...]] = ()
    publishes: ClassVar[tuple[str, ...]] = ()
    slot: ClassVar[int | str] = 0
    interval: ClassVar[float | None] = None   # segundos entre llamadas a tick(); None = sin tarea periódica

    def __init__(self, bus: EventBus, services: Services, params: dict | None = None, slot: int | str | None = None):
        self.bus = bus
        self.services = services
        self.params = params or {}
        self.slot = self.slot if slot is None else slot
        self.state = SkillState.IDLE
        self.handled = 0
        self.caption = ""
        self.note = ""
        self._queue: queue.Queue[Event | None] = queue.Queue()
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    # -- API para quien escribe una skill --------------------------------------------------
    def handle(self, event: Event) -> None:
        """Se llama una vez por cada mensaje recibido (en el hilo de la skill)."""

    def tick(self) -> None:
        """Tarea periódica opcional (si `interval` está definido)."""

    def on_start(self) -> None: ...

    def on_stop(self) -> None: ...

    @property
    def settings(self):
        """Bloque de tradingbot.env de esta skill (claves <SKILL>_..., sin el prefijo).

        Ejemplo: con BIAS_MIN_VOTES=2 en tradingbot.env, la skill «bias» lee self.settings.get_int("MIN_VOTES").
        """
        from ..envconfig import EnvConfig
        env = self.services.env
        return env.section(self.key) if env is not None else EnvConfig()

    def publish(self, topic: str, payload: dict | None = None) -> None:
        self.bus.publish(topic, payload, source=self.key)

    def set_caption(self, text: str) -> None:
        if text != self.caption:
            self.caption = text
            self._announce()

    # -- ciclo de vida ----------------------------------------------------------------------
    @property
    def info(self) -> SkillInfo:
        return SkillInfo(self.key, self.title or self.key, self.description, self.slot, self.subscribes, self.publishes)

    def start(self) -> None:
        for pattern in self.subscribes:
            self.bus.subscribe(self.key, pattern, self._queue.put)
        self._thread = threading.Thread(target=self._run, name=f"skill-{self.key}", daemon=True)
        self._thread.start()

    def stop(self, timeout: float = 3.0) -> None:
        self._stop.set()
        self._queue.put(None)
        if self._thread:
            self._thread.join(timeout)
        self.bus.unsubscribe(self.key)

    def _announce(self) -> None:
        self.bus.publish("skill.state", {"key": self.key, "state": self.state.value, "handled": self.handled,
                                         "caption": self.caption, "note": self.note}, source=self.key)

    def _set_state(self, state: SkillState, note: str = "") -> None:
        self.state, self.note = state, note
        self._announce()

    def _run(self) -> None:
        try:
            self.on_start()
        except Exception as exc:  # noqa: BLE001
            self._set_state(SkillState.ERROR, f"{type(exc).__name__}: {exc}")
        self._announce()
        next_tick = time.monotonic() + (self.interval or 0)
        while not self._stop.is_set():
            timeout = max(0.0, next_tick - time.monotonic()) if self.interval else 0.5
            try:
                event = self._queue.get(timeout=timeout)
            except queue.Empty:
                event = None
            if self._stop.is_set():
                break
            if event is not None:
                self._dispatch(event)
            if self.interval and time.monotonic() >= next_tick:
                self._guarded(self.tick)
                next_tick = time.monotonic() + self.interval
        try:
            self.on_stop()
        except Exception:  # noqa: BLE001
            pass

    def _dispatch(self, event: Event) -> None:
        self._guarded(lambda: self.handle(event))
        self.handled += 1
        if self.state is SkillState.OK:
            self._announce()

    def _guarded(self, fn) -> None:
        self._set_state(SkillState.WORKING)
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 - una skill rota no debe tumbar a las demás
            self._set_state(SkillState.ERROR, f"{type(exc).__name__}: {exc}")
            self.publish("skill.error", {"key": self.key, "error": f"{type(exc).__name__}: {exc}"})
        else:
            self._set_state(SkillState.OK)


class SkillManager:
    """Crea las skills activas a partir de config.toml y gestiona su ciclo de vida."""

    def __init__(self, bus: EventBus, services: Services, skill_cfgs: list[dict]):
        self.bus = bus
        self.skills: dict[str, Skill] = {}
        used: dict[int | str, str] = {}
        for cfg in skill_cfgs:
            if not cfg.get("enabled", True):
                continue
            key = cfg.get("type")
            if key not in SKILL_REGISTRY:
                raise ValueError(f"Skill desconocida: {key!r}. Disponibles: {', '.join(SKILL_REGISTRY)}")
            params = {k: v for k, v in cfg.items() if k not in ("type", "enabled", "slot")}
            skill = SKILL_REGISTRY[key](bus, services, params, cfg.get("slot"))
            if skill.slot in used:
                raise ValueError(f"El slot {skill.slot!r} lo usan a la vez '{used[skill.slot]}' y '{key}'.")
            used[skill.slot] = key
            self.skills[key] = skill

    def infos(self) -> list[SkillInfo]:
        return [s.info for s in self.skills.values()]

    def start(self) -> None:
        for skill in self.skills.values():
            skill.start()

    def stop(self) -> None:
        for skill in self.skills.values():
            skill.stop()
