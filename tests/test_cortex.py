"""Cortex: valida los patrones de Pattern con el sesgo y le pasa la orden a Setup."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import time
from datetime import date

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.bias.models import Bias, BiasResult
from tradingbot.skills.cortex.validation import validate
from tradingbot.skills.pattern.patterns import ActiveTbr, PatternHit

TBR = ActiveTbr("NY_AM", "NY Open", date(2026, 10, 6), 105.0, 95.0, -0.5, 9.5)


def bias(kind, score=3.0, lateral=False):
    return BiasResult(kind, None, (), {}, "resumen", score, 3.0, lateral)


def test_el_sesgo_valida_la_direccion_del_patron():
    assert validate("long", bias(Bias.BULLISH)).allowed and not validate("short", bias(Bias.BULLISH)).allowed
    assert validate("short", bias(Bias.BEARISH, -3.0)).allowed and not validate("long", bias(Bias.BEARISH, -3.0)).allowed
    go, no_go = validate("long", bias(Bias.BULLISH)), validate("long", bias(Bias.BEARISH, -3.0))
    assert go.verdict == "GO" and "a favor del sesgo Bullish" in go.reason
    assert no_go.verdict == "NO GO" and "contra el sesgo Bearish" in no_go.reason


def test_sin_sesgo_o_en_lateral_no_se_opera_salvo_que_se_permita():
    sin = validate("long", bias(Bias.NO_BIAS, 0.0))
    assert not sin.allowed and "sin sesgo" in sin.reason
    assert validate("long", bias(Bias.NO_BIAS, 0.0), allow_no_bias=True).allowed
    assert "lateral" in validate("long", bias(Bias.NO_BIAS, 3.0, lateral=True)).reason
    assert not validate("long", None).allowed and "aún no está calculado" in validate("long", None).reason


def run_skills(env_text="", with_setup=True):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus, decisions, orders, executed = EventBus(), [], [], []
    bus.subscribe("t", "cortex.decision", decisions.append)
    bus.subscribe("t", "setup.order", orders.append)
    bus.subscribe("t", "setup.executed", executed.append)
    skills = [{"type": "cortex"}] + ([{"type": "setup"}] if with_setup else [])
    manager = SkillManager(bus, Services(None, None, {"app": {}}, EnvConfig(parse(env_text))), skills)
    manager.start()
    return manager, bus, decisions, orders, executed


def pattern_event(symbol="EURUSD", direction="long"):
    hit = PatternHit("p", "Patrón de prueba", direction, 13, 105.0, "detalle", {"stop": 95.0, "target": 115.0})
    return {"symbol": symbol, "timeframe": "15m", "tbr": TBR, "hit": hit}


def wait(items, n=1):
    deadline = time.time() + 3
    while len(items) < n and time.time() < deadline:
        time.sleep(0.02)
    time.sleep(0.15)


def test_con_go_cortex_le_pasa_la_orden_completa_a_setup():
    manager, bus, decisions, orders, executed = run_skills()
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "15m", "df": None}, source="feed")
    bus.publish("bias.updated", {"result": bias(Bias.BULLISH), "symbol": "EURUSD", "timeframe": "15m"}, source="bias")
    bus.publish("pattern.detected", pattern_event(direction="long"), source="pattern")
    wait(executed)
    manager.stop()
    assert [d.payload["decision"].allowed for d in decisions] == [True] and len(orders) == 1
    assert orders[0].source == "cortex"                                                    # la orden viene de Cortex
    o = orders[0].payload["order"]
    assert (o.symbol, o.timeframe, o.direction, o.tbr_zone, o.pattern) == ("EURUSD", "15m", "long", "NY Open", "Patrón de prueba")
    assert (o.tbr_high, o.tbr_low, o.tbr_mid, o.stop, o.target, o.bias, o.score) == (105.0, 95.0, 100.0, 95.0, 115.0, "Bullish", 3.0)
    assert len(executed) == 1 and executed[0].payload["sent"] is False                      # Setup la recibe (en simulación)


def test_con_no_go_setup_no_recibe_nada():
    manager, bus, decisions, orders, executed = run_skills()
    bus.publish("bias.updated", {"result": bias(Bias.BEARISH, -3.0), "symbol": "EURUSD", "timeframe": "15m"}, source="bias")
    bus.publish("pattern.detected", pattern_event(direction="long"), source="pattern")
    wait(decisions)
    time.sleep(0.2)
    manager.stop()
    assert [d.payload["decision"].allowed for d in decisions] == [False]                   # se muestra como NO GO...
    assert "contra el sesgo Bearish" in decisions[0].payload["decision"].reason
    assert orders == [] and executed == []                                                 # ...y no hay orden


def test_cortex_espera_al_sesgo_del_mismo_mercado():
    manager, bus, decisions, orders, executed = run_skills()
    bus.publish("pattern.detected", pattern_event("GBPUSD"), source="pattern")
    bus.publish("bias.updated", {"result": bias(Bias.BEARISH, -3.0), "symbol": "EURUSD", "timeframe": "15m"}, source="bias")
    time.sleep(0.3)
    assert decisions == []                                                                 # el sesgo es de otro mercado
    bus.publish("bias.updated", {"result": bias(Bias.BULLISH), "symbol": "GBPUSD", "timeframe": "15m"}, source="bias")
    wait(orders)
    manager.stop()
    assert len(decisions) == 1 and len(orders) == 1


def test_ajuste_permitir_operar_sin_sesgo():
    manager, bus, decisions, orders, executed = run_skills("CORTEX_ALLOW_NO_BIAS=true\n", with_setup=False)
    bus.publish("bias.updated", {"result": bias(Bias.NO_BIAS, 0.0), "symbol": "EURUSD", "timeframe": "15m"}, source="bias")
    bus.publish("pattern.detected", pattern_event(), source="pattern")
    wait(orders)
    manager.stop()
    assert decisions[0].payload["decision"].allowed and len(orders) == 1


def test_el_registro_anota_el_go_y_el_no_go_de_cortex(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.skills.cortex.validation import Decision
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": ["EURUSD"]}}
    win = MainWindow(EventBus(), SkillManager(EventBus(), Services(None, None, cfg, EnvConfig()), []), cfg, "t")
    base = pattern_event()
    win._on_cortex_decision({**base, "decision": Decision(True, "Long a favor del sesgo Bullish"), "bias": Bias.BULLISH})
    win._on_cortex_decision({**base, "decision": Decision(False, "Long contra el sesgo Bearish"), "bias": Bias.BEARISH})
    text = win.log_view.toPlainText()
    assert "cortex: GO Long (Patrón de prueba, NY Open" in text and "Long a favor del sesgo Bullish" in text
    assert "cortex: NO GO Long" in text and "Long contra el sesgo Bearish" in text          # el denegado también se muestra


def test_con_una_posicion_abierta_no_se_abre_otra_hasta_que_cierre():
    manager, bus, decisions, orders, executed = run_skills()
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "15m", "df": None}, source="feed")
    bus.publish("bias.updated", {"result": bias(Bias.BULLISH), "symbol": "EURUSD", "timeframe": "15m"}, source="bias")
    hit = PatternHit("p", "Patrón de prueba", "long", 13, 105.0, "detalle", {"stop": 95.0, "target": 115.0}, 1_000_000)
    event = {"symbol": "EURUSD", "timeframe": "15m", "tbr": TBR, "hit": hit}
    bus.publish("pattern.detected", event, source="pattern")
    wait(orders)
    bus.publish("pattern.detected", {**event, "hit": PatternHit("q", "Otro patrón", "long", 20, 105.0, "d", {"stop": 95.0, "target": 115.0}, 1_001_000)},
                source="pattern")
    time.sleep(0.4)
    assert [d.payload["decision"].allowed for d in decisions] == [True, False]
    assert "ya hay una posición abierta en EURUSD" in decisions[1].payload["decision"].reason and len(orders) == 1
    o = orders[0].payload["order"]
    assert (o.entry_ts, o.close_ts) == (1_000_000, 1_000_000 + 24 * 3600)           # Setup puede seguirla: stop, objetivo o 24 h
    bus.publish("setup.closed", {"order": o, "closed": None, "sent": False}, source="setup")      # la posición cierra
    time.sleep(0.2)
    otra = ActiveTbr("LONDON", "London", date(2026, 10, 7), 105.0, 95.0, -0.5, 9.5)                 # otra sesión
    bus.publish("pattern.detected", {**event, "tbr": otra, "hit": PatternHit("r", "Tercer patrón", "long", 30, 105.0, "d", {"stop": 95.0, "target": 115.0}, 1_002_000)},
                source="pattern")
    wait(orders, 2)
    manager.stop()
    assert len(orders) == 2 and decisions[2].payload["decision"].allowed


def _dos_mercados(env_text):
    manager, bus, decisions, orders, executed = run_skills(env_text)
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "15m", "df": None}, source="feed")
    for sym in ("EURUSD", "GBPUSD"):
        bus.publish("bias.updated", {"result": bias(Bias.BULLISH), "symbol": sym, "timeframe": "15m"}, source="bias")
        hit = PatternHit("p", "Patrón de prueba", "long", 13, 105.0, "detalle", {"stop": 95.0, "target": 115.0}, 1_000_000)
        bus.publish("pattern.detected", {"symbol": sym, "timeframe": "15m", "tbr": TBR, "hit": hit}, source="pattern")
        time.sleep(0.4)
    manager.stop()
    return decisions, orders


def test_con_alcance_global_hay_una_sola_posicion_en_toda_la_cuenta():
    decisions, orders = _dos_mercados("CORTEX_POSITION_SCOPE=global\n")
    assert [d.payload["decision"].allowed for d in decisions] == [True, False] and len(orders) == 1
    assert "ya hay una posición abierta en EURUSD" in decisions[1].payload["decision"].reason          # GBPUSD queda bloqueado


def test_por_defecto_cada_mercado_tiene_su_posicion():
    decisions, orders = _dos_mercados("")                  # CORTEX_POSITION_SCOPE=mercado
    assert [d.payload["decision"].allowed for d in decisions] == [True, True] and len(orders) == 2


def test_una_misma_sesion_no_puede_dar_dos_trades_aunque_el_primero_ya_cerro():
    manager, bus, decisions, orders, executed = run_skills("CORTEX_POSITION_SCOPE=mercado\n")
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "15m", "df": None}, source="feed")
    bus.publish("bias.updated", {"result": bias(Bias.BULLISH), "symbol": "EURUSD", "timeframe": "15m"}, source="bias")
    def event(key, ts, tbr=TBR):
        hit = PatternHit(key, f"Patrón {key}", "long", 13, 105.0, "d", {"stop": 95.0, "target": 115.0}, ts)
        return {"symbol": "EURUSD", "timeframe": "15m", "tbr": tbr, "hit": hit}
    bus.publish("pattern.detected", event("a", 1_000_000), source="pattern")
    wait(orders)
    bus.publish("setup.closed", {"order": orders[0].payload["order"], "closed": None, "sent": False}, source="setup")   # cierra enseguida
    time.sleep(0.2)
    bus.publish("pattern.detected", event("b", 1_001_000), source="pattern")             # misma TBR: NO GO por la sesión
    time.sleep(0.4)
    manager.stop()
    assert [d.payload["decision"].allowed for d in decisions] == [True, False] and len(orders) == 1
    assert "ya dio un trade" in decisions[1].payload["decision"].reason and "NY Open del 06/10" in decisions[1].payload["decision"].reason


def test_si_la_operacion_ya_termino_con_las_velas_actuales_el_resultado_sale_al_momento():
    import numpy as np
    import pandas as pd
    manager, bus, decisions, orders, executed = run_skills()
    closed = []
    bus.subscribe("t", "setup.closed", closed.append)
    ts = 1_000_000 + np.arange(6) * 900
    df = pd.DataFrame({"ts": ts, "open": 105.0, "high": [105.5, 106, 116, 106, 106, 106], "low": [104.5, 104, 104, 104, 104, 104], "close": 105.0})
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "15m", "df": df}, source="feed")
    bus.publish("bias.updated", {"result": bias(Bias.BULLISH), "symbol": "EURUSD", "timeframe": "15m"}, source="bias")
    hit = PatternHit("p", "Patrón de prueba", "long", 1, 105.0, "detalle", {"stop": 95.0, "target": 115.0}, int(ts[1]))
    bus.publish("pattern.detected", {"symbol": "EURUSD", "timeframe": "15m", "tbr": TBR, "hit": hit}, source="pattern")
    wait(closed)
    manager.stop()
    assert len(closed) == 1 and closed[0].payload["closed"].result == "objetivo" and closed[0].payload["closed"].r == 1.0


def test_una_operacion_pasada_ya_cerrada_no_bloquea_a_la_siguiente_que_se_anuncia_a_la_vez():
    import numpy as np
    import pandas as pd
    manager, bus, decisions, orders, executed = run_skills()
    closed = []
    bus.subscribe("t", "setup.closed", closed.append)
    ts = 1_000_000 + np.arange(8) * 900
    df = pd.DataFrame({"ts": ts, "open": 105.0, "high": [105.5, 106, 116, 106, 106, 106, 106, 106], "low": 104.0, "close": 105.0})
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "15m", "df": df}, source="feed")
    # los dos patrones llegan antes que el sesgo (como al arrancar el bot), el posterior primero
    otra = ActiveTbr("LONDON", "London", date(2026, 10, 7), 105.0, 95.0, -0.5, 9.5)
    tarde = PatternHit("q", "Patrón tarde", "long", 5, 105.0, "d", {"stop": 95.0, "target": 115.0}, int(ts[5]))
    pronto = PatternHit("p", "Patrón pronto", "long", 1, 105.0, "d", {"stop": 95.0, "target": 115.0}, int(ts[1]))
    bus.publish("pattern.detected", {"symbol": "EURUSD", "timeframe": "15m", "tbr": otra, "hit": tarde}, source="pattern")
    bus.publish("pattern.detected", {"symbol": "EURUSD", "timeframe": "15m", "tbr": TBR, "hit": pronto}, source="pattern")
    bus.publish("bias.updated", {"result": bias(Bias.BULLISH), "symbol": "EURUSD", "timeframe": "15m"}, source="bias")
    wait(closed, 2)
    manager.stop()
    assert [d.payload["decision"].allowed for d in decisions] == [True, True] and len(orders) == 2       # el primero ya cerró a las 00:30
    assert decisions[0].payload["hit"].key == "p"                                                        # y se decide en orden de hora
