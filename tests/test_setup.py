"""Skill Setup (ejecutor): solo actúa cuando Cortex le da la orden de operar."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import time
from datetime import date

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.cortex.order import Order

ORDER = Order("EURUSD", "15m", "long", "Patrón de prueba", "p", "NY Open", date(2026, 10, 6), 105.0, 95.0, 100.0, 105.0, 95.0, 115.0,
              "Bullish", 3.0, "Long a favor del sesgo Bullish (puntuación +3)")


def run_skill(env_text=""):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus, executed = EventBus(), []
    bus.subscribe("t", "setup.executed", executed.append)
    manager = SkillManager(bus, Services(None, None, {"app": {}}, EnvConfig(parse(env_text))), [{"type": "setup"}])
    manager.start()
    return manager, bus, executed


def wait(executed, n=1):
    deadline = time.time() + 3
    while len(executed) < n and time.time() < deadline:
        time.sleep(0.02)
    time.sleep(0.15)


def test_setup_solo_ejecuta_las_ordenes_de_cortex():
    manager, bus, executed = run_skill()
    bus.publish("setup.order", {"order": ORDER}, source="pattern")                 # de otra skill: se rechaza
    time.sleep(0.3)
    assert executed == [] and manager.skills["setup"].caption == "orden rechazada"
    bus.publish("setup.order", {"order": ORDER}, source="cortex")
    wait(executed)
    manager.stop()
    assert len(executed) == 1
    p = executed[0].payload
    assert p["order"] is ORDER and p["sent"] is False and "simulación" in p["note"]      # por ahora no se envía a MT5
    assert manager.skills["setup"].caption == "simulada: Long EURUSD"


def test_setup_solo_esta_conectado_a_cortex():
    from tradingbot.skills.setup.skill import SetupSkill
    assert SetupSkill.subscribes == ("setup.order",) and SetupSkill.slot == "aux1"      # no escucha a Pattern, Bias ni velas


def test_enviar_ordenes_reales_a_mt5_aun_no_esta_implementado():
    manager, bus, executed = run_skill("SETUP_SEND_ORDERS=true\n")
    bus.publish("setup.order", {"order": ORDER}, source="cortex")
    time.sleep(0.3)
    manager.stop()
    assert manager.skills["setup"].state.value == "error" and "SETUP_SEND_ORDERS" in manager.skills["setup"].note
    assert executed == []


def test_el_registro_anota_la_orden_preparada(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": ["EURUSD"]}}
    win = MainWindow(EventBus(), SkillManager(EventBus(), Services(None, None, cfg, EnvConfig()), []), cfg, "t")
    win._on_setup_executed({"order": ORDER, "sent": False, "note": "Modo simulación: la orden está lista pero no se ha enviado a MT5."})
    text = win.log_view.toPlainText()
    assert "setup: orden preparada (simulación) - Long EURUSD 15m" in text
