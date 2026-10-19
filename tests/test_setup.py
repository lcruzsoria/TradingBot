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
    # órdenes de Cortex; la conexión solo para el capital inicial y la hora del servidor para consolidar
    assert SetupSkill.subscribes == ("setup.order", "setup.candles", "feed.connected", "clock.offset")
    assert SetupSkill.slot == "aux1"


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


def test_las_posiciones_abiertas_se_guardan_en_disco_y_siguen_al_reiniciar():
    import json
    import pandas as pd
    from tradingbot.skills.setup import store
    order = Order("EURUSD", "15m", "long", "Patrón de prueba", "p", "NY Open", date(2026, 10, 6), 105.0, 95.0, 100.0, 100.0, 95.0, 110.0,
                  "Bullish", 3.0, "GO", None, 1000, 1000 + 24 * 3600)
    manager, bus, executed = run_skill()
    bus.publish("setup.order", {"order": order}, source="cortex")
    wait(executed)
    manager.stop()
    saved = json.loads(store.DEFAULT_FILE.read_text(encoding="utf-8"))                # JSON legible, para consultarlo
    assert [(o["symbol"], o["direction"], o["stop"], o["target"]) for o in saved] == [("EURUSD", "long", 95.0, 110.0)]
    manager, bus, executed = run_skill()                                               # al reiniciar, la sigue
    time.sleep(0.3)
    setup = manager.skills["setup"]
    assert setup.positions == [order] and setup.caption == "1 posición(es) abierta(s)"
    closed = []
    bus.subscribe("t", "setup.closed", closed.append)
    df = pd.DataFrame({"ts": [1000, 1900], "high": [101.0, 111.0], "low": [99.0, 100.5], "close": [100.5, 110.0]})
    bus.publish("setup.candles", {"symbol": "EURUSD", "timeframe": "15m", "df": df}, source="cortex")
    wait(closed)
    manager.stop()
    assert closed[0].payload["closed"].result == "objetivo" and store.load() == []    # cerrada: sale del fichero


def test_cortex_sabe_que_mercados_estan_ocupados_al_reiniciar():
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.skills.setup import store
    import tradingbot.skills  # noqa: F401
    order = Order("EURUSD", "15m", "long", "Patrón de prueba", "p", "NY Open", date(2026, 10, 6), 105.0, 95.0, 100.0, 100.0, 95.0, 110.0,
                  "Bullish", 3.0, "GO", None, 1000, 1000 + 24 * 3600)
    store.save([order])
    manager = SkillManager(EventBus(), Services(None, None, {"app": {}}, EnvConfig()), [{"type": "cortex"}])
    manager.start()
    time.sleep(0.3)
    cortex = manager.skills["cortex"]
    manager.stop()
    assert cortex._open == {"EURUSD": order} and ("EURUSD", "NY Open", date(2026, 10, 6)) in cortex._used
