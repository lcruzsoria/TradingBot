"""Skill Pattern: TBR activa, plazo hasta la TBR siguiente y marco para registrar patrones (de momento no hay ninguno definido)."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import time
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd
import pytest

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.pattern.patterns import (ANNULLED, DETECTED, EXPIRED, INVALIDATED, PATTERN_REGISTRY, ActiveTbr, Pattern,
                                                PatternContext, PatternHit, active_tbr, register_pattern, window_for)
from tradingbot.skills.tbr.zones import Session, Zone, zones_from_settings

ASIA = Zone("ASIA", "Asia", 1200, 0, "#FFD60A")
LONDON = Zone("LONDON", "London", 120, 300, "#FF3B30")
NY = Zone("NY_AM", "NY Open", 600, 720, "#00C853")
NYPM = Zone("NY_PM", "NY-PM", 810, 990, "#A64DFF")
ORDER = [ASIA, LONDON, NY, NYPM]
AHEAD = 7 * 3600
DAY = date(2026, 10, 6)


def session(zone, day, x1, high=105.0, low=95.0, complete=True):
    return Session(zone, day, x1 - 10, x1, complete, high, low)


TBR = ActiveTbr("NY_AM", "NY Open", DAY, 105.0, 95.0, -0.5, 9.5)


class RompeElHigh(Pattern):
    """Patrón de prueba: el primer cierre por encima del High de la TBR activa."""
    title = "Cierre sobre el High"

    def detect(self, ctx: PatternContext):
        for i in range(ctx.first_bar, ctx.last_bar + 1):
            if ctx.close[i] > ctx.tbr.high:
                return [PatternHit(self.key, self.title, "long", i, ctx.tbr.high, "cierre sobre el High", {"stop": ctx.tbr.low},
                                   int(ctx.ts[i]))]
        return []


class EnM5(RompeElHigh):
    """Igual, pero trabaja siempre con velas M5."""
    title = "Cierre sobre el High (M5)"

    def timeframe(self):
        return "5m"


class Descarta(Pattern):
    """Patrón de prueba que siempre se invalida en la primera vela tras el cierre de la TBR."""
    title = "Siempre invalidado"

    def detect(self, ctx: PatternContext):
        if ctx.first_bar > ctx.last_bar:
            return []
        return [PatternHit(self.key, self.title, "short", ctx.first_bar, ctx.tbr.mid, "motivo de prueba", {}, int(ctx.ts[ctx.first_bar]),
                           INVALIDATED)]


@pytest.fixture
def registry(monkeypatch):
    """Solo los patrones de prueba (los patrones reales salen del registro durante el test)."""
    for real in ("continuacion", "reversion"):
        monkeypatch.delitem(PATTERN_REGISTRY, real)
    for key, cls in (("rompe_high", RompeElHigh), ("en_m5", EnM5), ("descarta", Descarta)):
        monkeypatch.setitem(PATTERN_REGISTRY, key, cls)
        monkeypatch.setattr(cls, "key", key, raising=False)
    return PATTERN_REGISTRY


def test_el_patron_continuacion_esta_registrado():
    from tradingbot.skills.pattern.continuacion import Continuacion
    assert PATTERN_REGISTRY["continuacion"] is Continuacion


def test_el_decorador_registra_un_patron_con_su_clave(registry):
    try:
        register_pattern("temporal")(RompeElHigh)
        assert PATTERN_REGISTRY["temporal"] is RompeElHigh and RompeElHigh.key == "temporal"
    finally:
        PATTERN_REGISTRY.pop("temporal", None)


def test_la_tbr_activa_es_la_ultima_cerrada():
    sessions = [session(ASIA, date(2026, 10, 5), 20.5), session(LONDON, DAY, 50.5, 108, 92),
                session(NY, DAY, 90.5, complete=False)]
    tbr = active_tbr(sessions)
    assert (tbr.zone, tbr.high, tbr.low, tbr.mid) == ("London", 108.0, 92.0, 100.0)     # la de NY aún no ha cerrado
    assert tbr.first_bar == 51 and tbr.range == 16.0
    assert active_tbr(sessions, ["asia"]).zone == "Asia"                                 # solo las zonas pedidas
    assert active_tbr([session(NY, DAY, 90.5, complete=False)]) is None
    assert active_tbr([]) is None


def ny(day, hour, minute=0):
    """Hora de NY como segundos de servidor (servidor = NY + 7 h)."""
    return int(datetime(day.year, day.month, day.day, hour, minute, tzinfo=timezone.utc).timestamp()) + AHEAD


def test_el_plazo_termina_cuando_empieza_la_tbr_siguiente():
    asia = window_for(ActiveTbr("ASIA", "Asia", date(2026, 10, 5), 105, 95, 0, 1), ORDER, AHEAD)
    assert asia.close_ts == ny(DAY, 0) and asia.end_ts == ny(DAY, 2) and asia.next_zone == "London"     # Asia -> London 02:00
    london = window_for(ActiveTbr("LONDON", "London", DAY, 105, 95, 0, 1), ORDER, AHEAD)
    assert london.close_ts == ny(DAY, 5) and london.end_ts == ny(DAY, 10) and london.next_zone == "NY Open"   # y no Pre-NY (09:00)
    nyo = window_for(TBR, ORDER, AHEAD)
    assert nyo.close_ts == ny(DAY, 12) and nyo.end_ts == ny(DAY, 13, 30) and nyo.next_zone == "NY-PM"
    assert nyo.next_hours == "13:30" and nyo.session_end_ts == ny(DAY, 16, 30) and nyo.session_end_hours == "16:30"
    assert london.session_end_ts is None and asia.session_end_ts is None                 # solo tras NY PM se acaba la jornada
    assert window_for(ActiveTbr("OTRA", "Otra", DAY, 105, 95, 0, 1), ORDER, AHEAD) is None   # fuera del ciclo: sin límite


def test_las_zonas_del_ciclo_se_leen_de_tradingbot_env_aunque_no_esten_activas():
    env = EnvConfig(parse("TBR_ZONES=ASIA, LONDON, NY_AM\n")).section("TBR")
    zones = zones_from_settings(env, ["ASIA", "LONDON", "NY_AM", "NY_PM"])
    assert [z.name for z in zones] == ["Asia", "London", "NY Open", "NY-PM"] and zones[-1].hours == "13:30-16:30"
    assert [z.name for z in zones_from_settings(env)] == ["Asia", "London", "NY Open"]      # las activas siguen siendo tres


# ---- la skill ----------------------------------------------------------------------------------------------------------------
def m5_frame(rows, start_ny=(11, 0)):
    """Velas M5 (open, high, low, close) desde la hora de NY dada (por defecto 11:00; hasta las 12:00 es NY Open)."""
    o, h, l, c = zip(*rows)
    ts = ny(DAY, *start_ny) + np.arange(len(rows)) * 300
    return pd.DataFrame({"ts": ts, "open": o, "high": h, "low": l, "close": c, "tick_volume": 1})


FLAT = (100, 101, 99, 100)
BREAK = (101, 107, 100, 106)                                   # cierra sobre el High (105)


def candles_after_close(pattern_rows, tail=1, extra=None):
    inside = [FLAT] * 12                                       # 11:00-12:00: dentro de la TBR
    return inside + list(pattern_rows) + (extra or []) + [FLAT] * tail     # la última vela sigue formándose


def run_skill(env_text="", df=None, timeframe="5m"):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus, found, dropped, session_events, updated = EventBus(), [], [], [], []
    bus.subscribe("t", "pattern.detected", found.append)
    bus.subscribe("t", "pattern.discarded", dropped.append)
    bus.subscribe("t", "pattern.session", session_events.append)
    bus.subscribe("t", "pattern.updated", updated.append)
    manager = SkillManager(bus, Services(None, None, {"app": {}}, EnvConfig(parse(env_text))), [{"type": "pattern"}])
    manager.start()
    if df is None:
        df = m5_frame(candles_after_close([FLAT, FLAT, BREAK]))
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": timeframe, "df": df}, source="feed")
    bus.publish("tbr.updated", {"symbol": "EURUSD", "timeframe": timeframe, "sessions": [session(NY, DAY, 9.5)], "available": True},
                source="tbr")
    deadline = time.time() + 3
    while not updated and time.time() < deadline:
        time.sleep(0.02)
    time.sleep(0.25)
    return manager, bus, found, dropped, session_events, updated


def test_sin_patrones_definidos_la_skill_lo_dice(monkeypatch):
    for real in ("continuacion", "reversion"):
        monkeypatch.delitem(PATTERN_REGISTRY, real)
    manager, _bus, found, dropped, _s, updated = run_skill()
    manager.stop()
    assert manager.skills["pattern"].caption == "sin patrones definidos" and found == [] and dropped == []
    assert updated[-1].payload["tbr"].zone == "NY Open"                                    # aun así conoce la TBR activa


def test_la_skill_avisa_del_patron_identificado_en_la_tbr_activa(registry):
    manager, _bus, found, dropped, _s, updated = run_skill("PATTERN_TYPES=rompe_high\n")
    manager.stop()
    assert len(found) == 1 and dropped == []
    p = found[0].payload
    assert p["hit"].key == "rompe_high" and p["hit"].direction == "long" and p["timeframe"] == "5m"
    assert p["hit"].ts == ny(DAY, 12, 10) and p["tbr"].zone == "NY Open" and "decision" not in p   # la decisión la toma Cortex
    assert manager.skills["pattern"].caption == "1 patrón(es) en NY Open"


def test_solo_usa_velas_cerradas_la_ultima_se_esta_formando(registry):
    rows = candles_after_close([FLAT, FLAT], tail=0, extra=[BREAK])                        # el cierre sobre el High es la última vela
    manager, _bus, found, *_ = run_skill("PATTERN_TYPES=rompe_high\n", df=m5_frame(rows))
    manager.stop()
    assert found == []                                                                      # no se identifica hasta que cierre


def test_un_patron_puede_pedir_su_timeframe_y_m1_se_agrupa(registry):
    rows = candles_after_close([FLAT, FLAT, BREAK])
    m1 = []
    for o, h, l, c in rows:                                                                 # cada M5 son cinco M1 con los mismos extremos
        m1 += [(o, o, o, o), (o, h, o, o), (o, h, l, l), (l, h, l, c), (c, c, c, c)]
    df = pd.DataFrame({"ts": ny(DAY, 11, 0) + np.arange(len(m1)) * 60, "open": [r[0] for r in m1], "high": [r[1] for r in m1],
                       "low": [r[2] for r in m1], "close": [r[3] for r in m1], "tick_volume": 1})
    manager, _bus, found, *_ = run_skill("PATTERN_TYPES=en_m5\n", df=df, timeframe="1m")
    manager.stop()
    assert len(found) == 1 and found[0].payload["timeframe"] == "5m" and found[0].payload["hit"].ts == ny(DAY, 12, 10)


def test_con_otro_timeframe_avisa_de_que_falta_el_del_patron(registry):
    manager, _bus, found, _d, _s, updated = run_skill("PATTERN_TYPES=en_m5\n", timeframe="15m")
    manager.stop()
    assert found == [] and "necesita velas M5" in updated[-1].payload["unavailable"][0]
    assert "M15" in updated[-1].payload["unavailable"][0] and manager.skills["pattern"].caption == "necesita M5"


def test_los_resultados_que_no_son_identificacion_van_al_registro_sin_pasar_a_cortex(registry):
    manager, _bus, found, dropped, *_ = run_skill("PATTERN_TYPES=descarta\n")
    manager.stop()
    assert found == [] and [d.payload["hit"].status for d in dropped] == [INVALIDATED]


def test_tras_ny_pm_no_se_evaluan_mas_setups_y_se_anota_una_sola_vez(registry):
    rows = candles_after_close([FLAT, FLAT, BREAK], tail=1, extra=[FLAT] * 60)              # pasadas las 16:30
    manager, bus, found, dropped, session_events, updated = run_skill("PATTERN_TYPES=rompe_high\nPATTERN_UNTIL=NY_AM@16:30\n",
                                                                      df=m5_frame(rows))
    assert len(found) == 1 and len(session_events) == 1 and session_events[0].payload["session_end"] == "16:30"
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "5m", "df": m5_frame(rows)}, source="feed")
    time.sleep(0.3)
    manager.stop()
    assert len(session_events) == 1 and len(found) == 1                                     # sin repetir
    assert manager.skills["pattern"].caption == "fin de jornada"


def test_no_repite_avisos(registry):
    manager, bus, found, _d, _s, updated = run_skill("PATTERN_TYPES=rompe_high\n")
    df = m5_frame(candles_after_close([FLAT, FLAT, BREAK]))
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "5m", "df": df}, source="feed")   # recarga de las mismas velas
    bus.publish("tbr.updated", {"symbol": "EURUSD", "timeframe": "5m", "sessions": [session(NY, DAY, 9.5)], "available": True},
                source="tbr")
    time.sleep(0.3)
    manager.stop()
    assert len(found) == 1                                                                  # el mismo patrón no se avisa dos veces


def test_ajustes_de_pattern(registry):
    for text, key in (("PATTERN_TYPES=no_existe\n", "no_existe"), ("PATTERN_ZONE_ORDER=ASIA, NO_EXISTE\n", "NO_EXISTE")):
        manager, _bus, found, *_ = run_skill(text)
        manager.stop()
        assert manager.skills["pattern"].state.value == "error" and key in manager.skills["pattern"].note and not found
    manager, _bus, found, *_ = run_skill("PATTERN_TYPES=rompe_high\nPATTERN_ZONES=ASIA\n")   # la TBR activa es NY Open: no es de Asia
    manager.stop()
    assert found == []


def test_el_registro_anota_tbr_activa_patron_y_descartes(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "5m", "watchlist": ["EURUSD"]}}
    win = MainWindow(EventBus(), SkillManager(EventBus(), Services(None, None, cfg, EnvConfig()), []), cfg, "t")
    tbr = active_tbr([session(NY, DAY, 9.5)])
    win._on_pattern_updated({"symbol": "EURUSD", "timeframe": "5m", "tbr": tbr, "hits": [], "errors": [],
                             "unavailable": ["Mi patrón necesita velas M5 y el gráfico está en M15"]})
    hit = PatternHit("mi_patron", "Mi patrón", "short", 2, 93.0, "detalle", {"toma": 94.0}, ny(DAY, 12, 10))
    win._on_pattern_detected({"symbol": "EURUSD", "timeframe": "5m", "tbr": tbr, "hit": hit})
    for status, state in ((INVALIDATED, "invalidado"), (ANNULLED, "anulado"), (EXPIRED, "vencido")):
        drop = PatternHit("mi_patron", "Mi patrón", "short", 1, 100.0, f"motivo {state}", {}, ny(DAY, 12, 5), status)
        win._on_pattern_discarded({"symbol": "EURUSD", "timeframe": "5m", "tbr": tbr, "hit": drop})
    win._on_pattern_session({"symbol": "EURUSD", "timeframe": "5m", "tbr": tbr, "session_end": "16:30"})
    text = win.log_view.toPlainText()
    assert "pattern: TBR activa NY Open" in text and "necesita velas M5" in text
    assert "pattern: Mi patrón Short identificado en NY Open" in text
    assert all(f"Mi patrón Short {s} en NY Open" in text and f"motivo {s}" in text for s in ("invalidado", "anulado", "vencido"))
    assert "fin de la jornada de setups" in text and "16:30 NY" in text


def test_history_tbrs_devuelve_las_pasadas_sin_las_activas():
    from datetime import date
    from types import SimpleNamespace as NS
    from tradingbot.skills.pattern.patterns import history_tbrs

    def sess(key, day, x1, complete=True):
        return NS(zone=NS(key=key, name=key), day=date(2026, 10, day), high=2.0, low=1.0, x0=x1 - 1, x1=x1, complete=complete)

    sessions = [sess("ASIA", 5, 10), sess("LONDON", 5, 20), sess("ASIA", 12, 30), sess("LONDON", 12, 40), sess("LONDON", 13, 50, False)]
    skip = {("ASIA", date(2026, 10, 12)), ("LONDON", date(2026, 10, 12))}                # las activas
    got = history_tbrs(sessions, None, skip, 30)
    assert [(t.key, t.day.day) for t in got] == [("ASIA", 5), ("LONDON", 5)]             # de la más antigua a la más reciente
    assert history_tbrs(sessions, None, skip, 5) == []                                   # fuera de los últimos 5 días
    assert [t.key for t in history_tbrs(sessions, ["LONDON"], skip, 30)] == ["LONDON"]


def test_plazo_ampliado_de_ny_open_hasta_el_final_de_ny_pm():
    normal = window_for(TBR, ORDER, AHEAD)
    ampliado = window_for(TBR, ORDER, AHEAD, ("NY_AM",))
    assert normal.end_ts == ny(DAY, 13, 30) and normal.limit_verb == "empezara"
    assert ampliado.end_ts == ny(DAY, 16, 30) == ampliado.session_end_ts and ampliado.limit_verb == "terminara"
    assert ampliado.next_zone == "NY-PM" and ampliado.next_hours == "16:30" and ampliado.close_ts == normal.close_ts
    asia = window_for(ActiveTbr("ASIA", "Asia", date(2026, 10, 5), 105, 95, 0, 1), ORDER, AHEAD, ("NY_AM",))
    assert asia.end_ts == window_for(ActiveTbr("ASIA", "Asia", date(2026, 10, 5), 105, 95, 0, 1), ORDER, AHEAD).end_ts   # solo NY Open


def test_plazo_de_asia_hasta_el_inicio_de_ny_open():
    asia = ActiveTbr("ASIA", "Asia", date(2026, 10, 5), 105, 95, 0, 1)
    normal = window_for(asia, ORDER, AHEAD)
    largo = window_for(asia, ORDER, AHEAD, (), {"ASIA": "NY_AM"})
    assert normal.next_zone == "London" and largo.next_zone == "NY Open" and largo.next_hours == "10:00"
    assert largo.end_ts == ny(date(2026, 10, 6), 10, 0) and largo.close_ts == normal.close_ts and largo.limit_verb == "empezara"
    assert largo.session_end_ts is None                      # la jornada solo termina tras NY PM


def test_pattern_until_por_defecto_y_validacion():
    manager, _bus, _found, *_ = run_skill("")
    manager.stop()
    assert manager.skills["pattern"].until == {"ASIA": "@05:00", "LONDON": "NY_AM:FIN", "NY_AM": "@18:00"}
    assert manager.skills["pattern"].extend == []
    for text in ("PATTERN_UNTIL=ASIA\n", "PATTERN_UNTIL=ASIA:NO_EXISTE\n"):
        manager, _bus, found, *_ = run_skill(text)
        manager.stop()
        assert manager.skills["pattern"].state.value == "error" and "PATTERN_UNTIL" in manager.skills["pattern"].note and not found


def test_cada_entrada_dibujada_lleva_su_go_o_no_go_con_el_sesgo_de_su_vela(tmp_path, monkeypatch):
    import numpy as np
    import pandas as pd
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.envconfig import EnvConfig
    from tradingbot.ui.main_window import MainWindow
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": ["EURUSD"]}}
    win = MainWindow(EventBus(), SkillManager(EventBus(), Services(None, None, cfg, EnvConfig()), []), cfg, "t")
    win.candles = pd.DataFrame({"ts": np.arange(6) * 900, "open": 1.0, "high": 1.1, "low": 0.9, "close": 1.0})
    win._hist_data = {"scores": np.array([5.0, 5.0, -3.0, -1.0, 0.0, 5.0]), "min_score": 3.0,
                      "lateral": np.array([False, True, False, False, False, False])}
    assert win._entry_decision(0, "long") == ("GO", "Bullish +5")
    assert win._entry_decision(0, "short") == ("NO GO", "Bullish +5")
    assert win._entry_decision(1, "long") == ("NO GO", "lateral +5")        # el filtro de lateralidad anula el sesgo
    assert win._entry_decision(2, "short") == ("GO", "Bearish -3")
    assert win._entry_decision(3, "long") == ("NO GO", "No Bias -1")        # sin sesgo: NO GO (CORTEX_ALLOW_NO_BIAS=false)
    win._hist_data = None
    assert win._entry_decision(0, "long") == ("", "")                       # sin historial de sesgo no se marca nada


def test_plazo_de_london_hasta_el_final_de_ny_open():
    london = ActiveTbr("LONDON", "London", DAY, 105, 95, 0, 1)
    normal = window_for(london, ORDER, AHEAD)
    largo = window_for(london, ORDER, AHEAD, (), {"LONDON": "NY_AM:FIN"})
    assert normal.end_ts == ny(DAY, 10, 0)
    assert largo.end_ts == ny(DAY, 12, 0) and largo.next_zone == "NY Open" and largo.next_hours == "12:00"
    assert largo.limit_verb == "terminara" and largo.session_end_ts is None and largo.close_ts == normal.close_ts


def test_plazo_de_ny_open_hasta_las_1800():
    largo = window_for(TBR, ORDER, AHEAD, (), {"NY_AM": "@18:00"})
    assert largo.end_ts == ny(DAY, 18, 0) == largo.session_end_ts and largo.session_end_hours == "18:00"
    assert largo.next_hours == "18:00" and largo.limit_verb == "terminara" and largo.close_ts == window_for(TBR, ORDER, AHEAD).close_ts
    manager, _bus, found, *_ = run_skill("PATTERN_UNTIL=NY_AM@25:00\n")
    manager.stop()
    assert manager.skills["pattern"].state.value == "error" and "HH:MM" in manager.skills["pattern"].note


def test_la_posicion_dibujada_se_cierra_por_tiempo_a_las_24_h():
    import numpy as np
    from tradingbot.skills.pattern.trade import position_figure
    n = 120
    ts = np.arange(n) * 900
    flat = np.full(n, 100.0)
    ctx = PatternContext("X", "15m", 15, ts, flat, flat + 0.1, flat - 0.1, flat, TBR, 0, n - 1, True)
    pos = position_figure(ctx, "p", "NY Open", "long", 2, 100.0, 90.0, 120.0, "Patrón")
    assert pos.state == "tiempo" and pos.x1_ts == int(ts[2 + 95]) + 900              # 96 velas M15 (de la 2 a la 97) = 24 h; ya no sigue abierta
    corta = position_figure(PatternContext("X", "15m", 15, ts[:50], flat[:50], flat[:50] + 0.1, flat[:50] - 0.1, flat[:50], TBR, 0, 49, True),
                            "p", "NY Open", "long", 2, 100.0, 90.0, 120.0, "Patrón")
    assert corta.state == "abierta"                                                  # los datos acaban antes de las 24 h
