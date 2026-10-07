"""Bus de eventos y skills: comunicación entre ellas sin interfaz gráfica."""
import threading
import time

import pytest

import tradingbot.skills  # noqa: F401  (registra las skills)
from tradingbot.skills.bias import BiasEngine, Direction
from tradingbot.core import EventBus, Services, Skill, SkillManager, SkillState, register_skill
from tradingbot.core.bus import matches
from tradingbot.skills.feed.demo_data import DemoSource


def wait_for(cond, timeout=5.0):
    end = time.time() + timeout
    while time.time() < end:
        if cond():
            return True
        time.sleep(0.02)
    return False


def test_patrones():
    assert matches("*", "a.b") and matches("a.b", "a.b") and matches("a.*", "a.b")
    assert not matches("a.*", "b.a") and not matches("a.b", "a.c")


def test_bus_entrega_taps_y_no_a_si_mismo():
    bus, got, tapped = EventBus(), [], []
    bus.subscribe("x", "t.*", got.append)
    bus.subscribe("y", "t.uno", got.append)
    bus.add_tap(lambda ev, targets: tapped.append((ev.topic, sorted(targets))))
    bus.publish("t.uno", {"v": 1}, source="y")          # y no recibe su propio mensaje
    assert [e.topic for e in got] == ["t.uno"] and tapped == [("t.uno", ["x"])]


def test_suscriptor_roto_no_afecta_a_los_demas():
    bus, got = EventBus(), []
    bus.subscribe("roto", "*", lambda e: 1 / 0)
    bus.subscribe("ok", "*", got.append)
    bus.publish("a")
    assert len(got) == 1


@pytest.fixture
def system():
    bus = EventBus()
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": ["EURUSD", "NOEXISTE"]}}
    engine = BiasEngine.from_config({"rules": [{"type": "prev_day_break"}, {"type": "above_below_open"}]})
    services = Services(DemoSource(), engine, cfg)
    manager = SkillManager(bus, services, [{"type": "cortex", "slot": "center"}, {"type": "feed", "slot": 0},
                                           {"type": "bias", "slot": 1}, {"type": "quotes", "slot": 5}])
    events = []
    bus.subscribe("test", "*", events.append)
    manager.start()
    yield bus, manager, events
    manager.stop()


def test_cadena_feed_bias_cortex(system):
    bus, manager, events = system
    bus.publish("feed.load", {"symbol": "EURUSD", "timeframe": "15m"}, source="ui")
    assert wait_for(lambda: any(e.topic == "bias.updated" for e in events))
    topics = [e.topic for e in events]
    assert topics.index("feed.connected") < topics.index("candles.loaded") < topics.index("bias.updated")

    # Cortex ya conoce el Bias: responde a una petición de operar según ese sesgo
    bias = next(e for e in events if e.topic == "bias.updated").payload["result"]
    assert wait_for(lambda: manager.skills["cortex"].filter.result is not None)
    bus.publish("trade.request", {"request_id": 7, "direction": Direction.LONG}, source="test")
    bus.publish("trade.request", {"request_id": 8, "direction": Direction.SHORT}, source="test")
    assert wait_for(lambda: sum(e.topic == "trade.verdict" for e in events) == 2)
    verdicts = {e.payload["request_id"]: e.payload["allowed"] for e in events if e.topic == "trade.verdict"}
    assert verdicts == {7: bias.allows(Direction.LONG), 8: bias.allows(Direction.SHORT)}


def test_quotes_empieza_al_conectar_y_publica(system):
    bus, manager, events = system
    time.sleep(1.3)
    assert not any(e.topic == "quotes.updated" for e in events)       # aún sin conexión
    bus.publish("feed.load", {"symbol": "EURUSD", "timeframe": "15m"}, source="ui")
    assert wait_for(lambda: any(e.topic == "quotes.updated" for e in events))
    q = next(e for e in events if e.topic == "quotes.updated").payload
    assert q["quotes"]["EURUSD"] is not None and q["quotes"]["NOEXISTE"] is None and q["account"].currency == "USD"


def test_recalcular_bias(system):
    bus, _, events = system
    bus.publish("bias.recalc", source="ui")           # sin velas: se ignora
    time.sleep(0.3)
    assert not any(e.topic == "bias.updated" for e in events)
    bus.publish("feed.load", {"symbol": "EURUSD", "timeframe": "5m"}, source="ui")
    assert wait_for(lambda: any(e.topic == "bias.updated" for e in events))
    n = sum(e.topic == "bias.updated" for e in events)
    bus.publish("bias.recalc", source="ui")
    assert wait_for(lambda: sum(e.topic == "bias.updated" for e in events) == n + 1)


def test_skill_con_error_no_tumba_el_sistema():
    @register_skill("rota_test")
    class Rota(Skill):
        subscribes = ("boom",)
        slot = 3

        def handle(self, event):
            raise RuntimeError("fallo")

    bus = EventBus()
    events = []
    bus.subscribe("t", "*", events.append)
    manager = SkillManager(bus, Services(None, None, {"app": {}}), [{"type": "rota_test"}])
    manager.start()
    try:
        bus.publish("boom")
        assert wait_for(lambda: manager.skills["rota_test"].state is SkillState.ERROR)
        assert any(e.topic == "skill.error" for e in events)
        bus.publish("boom")                              # el hilo sigue vivo
        assert wait_for(lambda: manager.skills["rota_test"].handled == 2)
    finally:
        manager.stop()


def test_config_de_skills_valida():
    with pytest.raises(ValueError, match="desconocida"):
        SkillManager(EventBus(), Services(None, None, {"app": {}}), [{"type": "no_existe"}])
    with pytest.raises(ValueError, match="slot"):
        SkillManager(EventBus(), Services(None, None, {"app": {}}),
                     [{"type": "feed", "slot": 2}, {"type": "bias", "slot": 2}])
    m = SkillManager(EventBus(), Services(None, None, {"app": {}}), [{"type": "feed", "enabled": False}])
    assert m.skills == {}


def test_cada_skill_tiene_su_carpeta():
    """Cada skill vive en tradingbot/skills/<clave>/skill.py (también las futuras)."""
    from pathlib import Path
    from tradingbot.core.skill import SKILL_REGISTRY
    root = Path(tradingbot.skills.__file__).parent
    assert {"feed", "quotes", "bias", "cortex", "tbr", "levels", "setup"} <= set(SKILL_REGISTRY)
    for key, cls in SKILL_REGISTRY.items():
        if not cls.__module__.startswith("tradingbot."):
            continue                                    # skills de prueba definidas dentro de los tests
        assert cls.__module__ == f"tradingbot.skills.{key}.skill", f"{key} no está en su carpeta"
        assert (root / key / "__init__.py").exists()
    assert not [p.name for p in root.glob("*.py") if p.name != "__init__.py"]   # nada suelto en skills/
