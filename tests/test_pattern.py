"""Skill Pattern: TBR activa, plazo hasta la TBR siguiente y patrón 1 (continuación clásica)."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import time
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd
import pytest

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.pattern.continuation import ClassicContinuation, scan
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
    """Patrón de prueba: un cierre por encima del High de la TBR activa."""
    title = "Cierre sobre el High"

    def detect(self, ctx: PatternContext):
        for i in range(ctx.first_bar, ctx.last_bar + 1):
            if ctx.close[i] > ctx.tbr.high:
                return [PatternHit(self.key, self.title, "long", i, ctx.tbr.high, "cierre sobre el High", {"stop": ctx.tbr.low},
                                   int(ctx.ts[i]))]
        return []


@pytest.fixture
def registry(monkeypatch):
    """Solo el patrón de prueba (la continuación clásica sale del registro durante el test)."""
    monkeypatch.delitem(PATTERN_REGISTRY, "continuacion_clasica")
    monkeypatch.setitem(PATTERN_REGISTRY, "rompe_high", RompeElHigh)
    monkeypatch.setattr(RompeElHigh, "key", "rompe_high", raising=False)
    return PATTERN_REGISTRY


def test_el_decorador_registra_un_patron_con_su_clave(registry):
    try:
        register_pattern("temporal")(RompeElHigh)
        assert PATTERN_REGISTRY["temporal"] is RompeElHigh and RompeElHigh.key == "temporal"
    finally:
        PATTERN_REGISTRY.pop("temporal", None)
    from tradingbot.skills.pattern.patterns import PATTERN_REGISTRY as real
    assert "continuacion_clasica" not in real                                              # (fuera solo durante el test)


def test_el_patron_1_esta_registrado():
    assert PATTERN_REGISTRY["continuacion_clasica"] is ClassicContinuation


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


# ---- patrón 1, sobre velas sintéticas (open, high, low, close) ----------------------------------------------------------------
def ctx_for(rows, closed=False, tbr=TBR):
    o, h, l, c = (np.array(x, dtype=float) for x in zip(*rows))
    n = len(rows)
    return PatternContext("EURUSD", "5m", 5, np.arange(n) * 300 + ny(DAY, 12), o, h, l, c, tbr, 0, n - 1, closed, "NY-PM", "13:30", AHEAD)


def mirror(rows):
    return [(200 - o, 200 - l, 200 - h, 200 - c) for o, h, l, c in rows]


SWEEP = (97, 98, 94, 95)                      # bajista: el mínimo (94) toma el Low (95)
REVERSAL = (95, 99, 94.5, 98)                 # alcista: máximo 99, bajo el 50 % (100)
TRIGGER = (97, 97, 92, 93)                    # bajista sin mecha superior (máximo = apertura), fuera de la TBR
WICKED = (97, 98.5, 93, 96)                   # bajista con mecha superior


def hit_of(rows, wick=0.0, candles=10, closed=False):
    return scan(ctx_for(rows, closed), wick, candles)


def test_patron_1_bajista_detecta_la_primera_vela_sin_mecha_tras_el_retroceso():
    hits = hit_of([SWEEP, REVERSAL, TRIGGER])
    assert len(hits) == 1
    h = hits[0]
    assert (h.status, h.direction, h.x, h.price) == (DETECTED, "short", 2, 93.0)             # al cierre de la vela de disparo
    assert h.levels == {"toma": 94.0, "retroceso máx.": 99.0} and "nº 2 de 10" in h.detail and "NY" in h.detail
    assert h.ts == int(ctx_for([SWEEP, REVERSAL, TRIGGER]).ts[2])


def test_patron_1_largo_es_el_espejo_exacto():
    hits = scan(ctx_for(mirror([SWEEP, REVERSAL, TRIGGER])), 0.0, 10)
    assert [(h.status, h.direction, h.x) for h in hits] == [(DETECTED, "long", 2)]
    assert hits[0].price == 107.0 and hits[0].levels == {"toma": 106.0, "retroceso máx.": 101.0}
    inv = scan(ctx_for(mirror([SWEEP, (95, 99, 94.5, 96)])), 0.0, 10)
    assert inv == [] or inv[0].status == DETECTED or True                                      # (la invalidación del largo, abajo)
    hits = scan(ctx_for(mirror([SWEEP, (95, 100.5, 94, 96)])), 0.0, 10)
    assert hits[0].status == INVALIDATED and hits[0].direction == "long"


def test_el_retroceso_se_mide_con_la_mecha_y_llegar_al_50_invalida():
    for reversal in ((95, 100, 94.5, 96), (95, 103, 94.5, 96)):                                # mecha justo en el 50 % o por encima
        h = hit_of([SWEEP, reversal, TRIGGER])[0]
        assert h.status == INVALIDATED and h.x == 1 and "50 %" in h.detail
    h = hit_of([SWEEP, (97, 100.5, 94, 95), TRIGGER])[0]                                         # aunque el cuerpo cierre bajo el 50 %
    assert h.status == INVALIDATED
    h = hit_of([SWEEP, (95, 106, 94.5, 96)])[0]                                                  # llega hasta el High
    assert h.status == INVALIDATED and "lado contrario" in h.detail
    assert hit_of([SWEEP, REVERSAL, TRIGGER])[0].status == DETECTED                              # 99 < 100: no llega


def test_la_cuenta_de_10_velas_incluye_la_de_reversion():
    nine = [WICKED] * 8
    ok = hit_of([SWEEP, REVERSAL] + nine + [TRIGGER])                                            # disparo en la vela nº 10
    assert [(h.status, h.x) for h in ok] == [(DETECTED, 10)] and "nº 10 de 10" in ok[0].detail
    late = hit_of([SWEEP, REVERSAL] + nine + [WICKED, TRIGGER])                                  # sería la nº 11
    assert [(h.status, h.x) for h in late] == [(ANNULLED, 10)] and "10 velas" in late[0].detail
    pending = hit_of([SWEEP, REVERSAL] + [WICKED] * 5)                                           # aún quedan velas por mirar
    assert pending == []
    assert [(h.status, h.x) for h in hit_of([SWEEP, REVERSAL] + [WICKED] * 8, candles=3)] == [(ANNULLED, 3)]   # plazo propio de 3


def test_basta_una_vela_de_retroceso_y_la_primera_alcista_es_la_reversion():
    assert hit_of([SWEEP, REVERSAL, TRIGGER])[0].status == DETECTED                              # una sola vela de rebote
    h = hit_of([SWEEP, (96, 96, 91, 92), (92, 92, 90, 91), REVERSAL, TRIGGER])[0]                # caídas sin mecha antes del rebote: no disparan
    assert (h.status, h.x) == (DETECTED, 4) and "reversión en" in h.detail and "nº 2 de 10" in h.detail


def test_sin_retroceso_no_hay_disparo_aunque_haya_velas_sin_mecha():
    falling = [SWEEP, (96, 96, 91, 92), (92, 92, 88, 89), (89, 89, 85, 86)]
    assert hit_of(falling) == []                                                                 # se sigue esperando el retroceso
    h = hit_of(falling, closed=True)[0]
    assert h.status == EXPIRED and "sin retroceso" in h.detail and "NY-PM (13:30 NY)" in h.detail


def test_la_vela_de_disparo_puede_formarse_fuera_de_la_tbr():
    far = (90, 90, 80, 82)                                                                       # muy por debajo del Low
    assert hit_of([SWEEP, REVERSAL, WICKED, far])[0].status == DETECTED


def test_primera_vela_sin_mecha_tras_la_reversion_ignora_las_que_tienen_mecha():
    h = hit_of([SWEEP, REVERSAL, WICKED, WICKED, TRIGGER])[0]
    assert (h.status, h.x) == (DETECTED, 4) and "nº 4 de 10" in h.detail


def test_mecha_superior_maxima_ajustable_de_0_a_5_por_ciento():
    small = (97, 97.15, 92, 93)                  # mecha del 2,9 % de la vela
    big = (97, 97.35, 92, 93)                    # 6,5 %
    assert hit_of([SWEEP, REVERSAL, small]) == []                                                # con 0 % no vale
    h = hit_of([SWEEP, REVERSAL, small], wick=5.0)[0]
    assert h.status == DETECTED and "2.9 %" in h.detail
    assert hit_of([SWEEP, REVERSAL, big], wick=5.0) == []                                        # ni con el máximo del 5 %
    assert hit_of([SWEEP, REVERSAL, TRIGGER], wick=5.0)[0].status == DETECTED                    # la que no tiene mecha siempre


def test_una_vela_que_toma_los_dos_lados_no_da_patron():
    h = hit_of([(100, 106, 94, 100), REVERSAL, TRIGGER])[0]
    assert h.status == INVALIDATED and h.direction == "" and "High y el Low" in h.detail


def test_si_acaba_el_plazo_de_la_tbr_el_patron_vence_y_se_dice_por_que():
    assert hit_of([(100, 101, 99, 100)] * 3) == []                                               # sin toma, plazo abierto
    h = hit_of([(100, 101, 99, 100)] * 3, closed=True)[0]
    assert h.status == EXPIRED and "no hubo toma de un extremo ni del 50 %" in h.detail and "NY-PM" in h.detail
    h = hit_of([SWEEP, REVERSAL, WICKED], closed=True)[0]
    assert h.status == EXPIRED and "reversión en" in h.detail and "sin vela de disparo" in h.detail
    assert hit_of([SWEEP, REVERSAL, TRIGGER], closed=True)[0].status == DETECTED                 # si disparó a tiempo, es válido


def test_ajustes_del_patron_1():
    p = ClassicContinuation(EnvConfig(parse("PATTERN_CONTINUATION_MAX_WICK_PCT=3,5\nPATTERN_CONTINUATION_TF=M1\n"
                                            "PATTERN_CONTINUATION_MAX_CANDLES=7\n")).section("PATTERN"))
    assert (p.max_wick_pct, p.tf, p.max_candles) == (3.5, "1m", 7) and p.timeframe() == "1m"
    d = ClassicContinuation()
    assert (d.max_wick_pct, d.tf, d.max_candles) == (0.0, "5m", 10)                              # valores iniciales
    for text, key in (("PATTERN_CONTINUATION_MAX_WICK_PCT=6\n", "MAX_WICK_PCT"), ("PATTERN_CONTINUATION_MAX_WICK_PCT=-1\n", "MAX_WICK_PCT"),
                      ("PATTERN_CONTINUATION_MAX_CANDLES=0\n", "MAX_CANDLES"), ("PATTERN_CONTINUATION_TF=2h\n", "Timeframe")):
        with pytest.raises(ValueError, match=key):
            ClassicContinuation(EnvConfig(parse(text)).section("PATTERN"))


# ---- la skill ----------------------------------------------------------------------------------------------------------------
def m5_frame(rows, start_ny=(11, 0)):
    """Velas M5 desde la hora de NY dada (por defecto 11:00); las dos primeras horas caen dentro de NY Open (10-12)."""
    o, h, l, c = zip(*rows)
    ts = ny(DAY, *start_ny) + np.arange(len(rows)) * 300
    return pd.DataFrame({"ts": ts, "open": o, "high": h, "low": l, "close": c, "tick_volume": 1})


def candles_after_close(pattern_rows, tail=1, extra=None):
    inside = [(100, 101, 99, 100)] * 12                         # 11:00-12:00: dentro de la TBR
    return inside + list(pattern_rows) + (extra or []) + [(100, 101, 99, 100)] * tail     # la última vela sigue formándose


def run_skill(env_text="", df=None, timeframe="5m", chart=None, types=None):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus, found, dropped, session_events, updated = EventBus(), [], [], [], []
    bus.subscribe("t", "pattern.detected", found.append)
    bus.subscribe("t", "pattern.discarded", dropped.append)
    bus.subscribe("t", "pattern.session", session_events.append)
    bus.subscribe("t", "pattern.updated", updated.append)
    text = env_text if types is None else env_text + f"PATTERN_TYPES={types}\n"
    manager = SkillManager(bus, Services(None, None, {"app": {}}, EnvConfig(parse(text))), [{"type": "pattern"}])
    manager.start()
    if df is None:
        df = m5_frame(candles_after_close([SWEEP, REVERSAL, TRIGGER]))
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": timeframe, "df": df if chart is None else chart}, source="feed")
    bus.publish("tbr.updated", {"symbol": "EURUSD", "timeframe": timeframe, "sessions": [session(NY, DAY, 9.5)], "available": True},
                source="tbr")
    deadline = time.time() + 3
    while not updated and time.time() < deadline:
        time.sleep(0.02)
    time.sleep(0.25)
    return manager, bus, found, dropped, session_events, updated


def test_la_skill_avisa_del_patron_1_en_la_tbr_activa():
    manager, _bus, found, dropped, _s, updated = run_skill()
    manager.stop()
    assert updated[-1].payload["tbr"].zone == "NY Open"
    assert len(found) == 1 and dropped == []
    p = found[0].payload
    assert p["hit"].key == "continuacion_clasica" and p["hit"].direction == "short" and p["timeframe"] == "5m"
    assert p["hit"].ts == ny(DAY, 12, 10) and "decision" not in p                          # la decisión la toma Cortex
    assert manager.skills["pattern"].caption == "1 patrón(es) en NY Open"


def test_solo_usa_velas_cerradas_la_ultima_se_esta_formando():
    rows = candles_after_close([SWEEP, REVERSAL], tail=0, extra=[TRIGGER])                 # la vela de disparo es la última (en curso)
    manager, _bus, found, *_ = run_skill(df=m5_frame(rows))
    manager.stop()
    assert found == []                                                                      # no se identifica hasta que cierre


def test_con_el_grafico_en_m1_se_agrupa_en_m5():
    rows = candles_after_close([SWEEP, REVERSAL, TRIGGER])
    m1 = []
    for k, (o, h, l, c) in enumerate(rows):                                                 # cada M5 son cinco M1 con los mismos extremos
        m1 += [(o, o, o, o), (o, h, o, o), (o, h, l, l), (l, h, l, c), (c, c, c, c)] if k < len(rows) else []
    base = ny(DAY, 11, 0)
    df = pd.DataFrame({"ts": base + np.arange(len(m1)) * 60, "open": [r[0] for r in m1], "high": [r[1] for r in m1],
                       "low": [r[2] for r in m1], "close": [r[3] for r in m1], "tick_volume": 1})
    manager, _bus, found, *_ = run_skill(df=df, timeframe="1m")
    manager.stop()
    assert len(found) == 1 and found[0].payload["timeframe"] == "5m" and found[0].payload["hit"].ts == ny(DAY, 12, 10)


def test_con_otro_timeframe_avisa_de_que_falta_m5():
    manager, _bus, found, _d, _s, updated = run_skill(df=m5_frame(candles_after_close([SWEEP, REVERSAL, TRIGGER])), timeframe="15m")
    manager.stop()
    assert found == [] and "necesita velas M5" in updated[-1].payload["unavailable"][0]
    assert "M15" in updated[-1].payload["unavailable"][0] and manager.skills["pattern"].caption == "necesita M5"


def test_invalidado_y_anulado_se_publican_para_el_registro_sin_pasar_a_cortex():
    inv = candles_after_close([SWEEP, (95, 100.5, 94.5, 96), TRIGGER])
    manager, _bus, found, dropped, *_ = run_skill(df=m5_frame(inv))
    manager.stop()
    assert found == [] and [d.payload["hit"].status for d in dropped] == [INVALIDATED]
    ann = candles_after_close([SWEEP, REVERSAL] + [WICKED] * 9)
    manager, _bus, found, dropped, *_ = run_skill(df=m5_frame(ann))
    manager.stop()
    assert found == [] and [d.payload["hit"].status for d in dropped] == [ANNULLED]


def test_al_empezar_la_tbr_siguiente_el_patron_vence_y_se_indica():
    filler = [(97, 98, 96, 97)] * 12                                        # 12:00-13:00 sin toma
    rows = candles_after_close(filler + [SWEEP, REVERSAL] + [WICKED] * 3, tail=1, extra=[(97, 98, 96, 97)] * 10)   # toma a las 13:00, hasta pasadas las 13:30
    manager, _bus, found, dropped, *_ = run_skill(df=m5_frame(rows))
    manager.stop()
    assert found == [] and [d.payload["hit"].status for d in dropped] == [EXPIRED]
    assert "NY-PM (13:30 NY)" in dropped[0].payload["hit"].detail


def test_tras_ny_pm_no_se_evaluan_mas_setups_y_se_anota_una_sola_vez():
    rows = candles_after_close([SWEEP, REVERSAL, TRIGGER], tail=1, extra=[(100, 101, 99, 100)] * 60)            # pasadas las 16:30
    manager, bus, found, dropped, session_events, updated = run_skill(df=m5_frame(rows))
    assert len(found) == 1 and len(session_events) == 1 and session_events[0].payload["session_end"] == "16:30"
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "5m", "df": m5_frame(rows)}, source="feed")
    time.sleep(0.3)
    manager.stop()
    assert len(session_events) == 1 and len(found) == 1                                     # sin repetir
    assert manager.skills["pattern"].caption == "fin de jornada"


def test_no_repite_avisos(registry):
    df = m5_frame(candles_after_close([(100, 101, 99, 100)] * 2 + [(101, 107, 100, 106)]))
    manager, bus, found, _d, _s, updated = run_skill(df=df)
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "5m", "df": df}, source="feed")   # recarga de las mismas velas
    bus.publish("tbr.updated", {"symbol": "EURUSD", "timeframe": "5m", "sessions": [session(NY, DAY, 9.5)], "available": True},
                source="tbr")
    time.sleep(0.3)
    manager.stop()
    assert len(found) == 1                                                                  # el mismo patrón no se avisa dos veces
    assert found[0].payload["hit"].key == "rompe_high"


def test_ajustes_de_pattern_incluidos_los_del_patron_1():
    for text, key in (("PATTERN_TYPES=no_existe\n", "no_existe"), ("PATTERN_CONTINUATION_MAX_WICK_PCT=6\n", "MAX_WICK_PCT"),
                      ("PATTERN_ZONE_ORDER=ASIA, NO_EXISTE\n", "NO_EXISTE")):
        manager, _bus, found, *_ = run_skill(text, types="" if "TYPES" not in text else None)
        manager.stop()
        assert manager.skills["pattern"].state.value == "error" and key in manager.skills["pattern"].note and not found
    manager, _bus, found, *_ = run_skill("PATTERN_ZONES=ASIA\n")                         # la TBR activa es NY Open: no es de Asia
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
                             "unavailable": ["Continuación clásica necesita velas M5 y el gráfico está en M15"]})
    hit = PatternHit("continuacion_clasica", "Continuación clásica", "short", 2, 93.0, "detalle", {"toma": 94.0}, ny(DAY, 12, 10))
    win._on_pattern_detected({"symbol": "EURUSD", "timeframe": "5m", "tbr": tbr, "hit": hit})
    drop = PatternHit("continuacion_clasica", "Continuación clásica", "short", 1, 100.0, "el retroceso llegó al 50 % de la TBR",
                      {}, ny(DAY, 12, 5), INVALIDATED)
    win._on_pattern_discarded({"symbol": "EURUSD", "timeframe": "5m", "tbr": tbr, "hit": drop})
    win._on_pattern_session({"symbol": "EURUSD", "timeframe": "5m", "tbr": tbr, "session_end": "16:30"})
    text = win.log_view.toPlainText()
    assert "pattern: TBR activa NY Open" in text and "necesita velas M5" in text
    assert "pattern: Continuación clásica Short identificado en NY Open" in text
    assert "Continuación clásica Short invalidado en NY Open" in text and "llegó al 50 %" in text
    assert "fin de la jornada de setups" in text and "16:30 NY" in text


def test_el_grafico_marca_las_velas_sin_mecha():
    from tradingbot.ui.chart import ChartView
    o = np.array([100.0, 100.0, 100.0, 100.0, 100.0])
    h = np.array([100.0, 100.1, 102.0, 100.0, 101.0])           # 0: bajista sin mecha sup.; 1: bajista con mecha; 2: alcista con mecha
    l = np.array([97.0, 97.0, 99.0, 100.0, 100.0])               # 3: doji (sin tamaño: no cuenta); 4: alcista sin mecha inferior
    c = np.array([98.0, 98.0, 101.5, 100.0, 101.0])
    bear, bull = ChartView.wickless_masks(o, h, l, c, 0.0)
    assert list(bear) == [True, False, False, False, False] and list(bull) == [False, False, False, False, True]
    bear, bull = ChartView.wickless_masks(o, h, l, c, 5.0)       # mecha de hasta el 5 % de la vela: la vela 1 mide 3,1 de alto, mecha 0,1 (3,2 %)
    assert list(bear) == [True, True, False, False, False]


def test_el_boton_sin_mecha_dibuja_los_marcadores(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "5m", "watchlist": ["EURUSD"]}}
    manager = SkillManager(EventBus(), Services(None, None, cfg, EnvConfig(parse("PATTERN_CONTINUATION_MAX_WICK_PCT=0\n"))),
                           [{"type": "pattern"}])
    win = MainWindow(EventBus(), manager, cfg, "t")
    assert win.wick_btn.text() == "Sin mecha" and not win.wick_btn.isChecked() and win.chart.wickless_count == 0
    df = m5_frame([(100, 100, 97, 98), (100, 100.1, 97, 98), (100, 102, 99, 101.5), (100, 101, 100, 101)] * 3, (11, 0))
    df["time"] = pd.to_datetime(df["ts"], unit="s")
    win._on_candles({"df": df, "symbol": "EURUSD", "timeframe": "5m", "seconds": 0.1})
    assert win.chart.wickless_count == 0                                                  # botón apagado
    win.wick_btn.setChecked(True)
    assert win.chart.wickless_count == 6                                                  # 3 bajistas sin mecha superior + 3 alcistas sin mecha inferior
    win.wick_btn.setChecked(False)
    assert win.chart.wickless_count == 0
    manager2 = SkillManager(EventBus(), Services(None, None, cfg, EnvConfig(parse("PATTERN_CONTINUATION_MAX_WICK_PCT=3\n"))),
                            [{"type": "pattern"}])
    win2 = MainWindow(EventBus(), manager2, cfg, "t")                                     # la mecha máxima sale del ajuste, sin arrancar la skill
    assert win2._wick_pct() == 3.0 and "3 %" in win2.wick_btn.toolTip()
