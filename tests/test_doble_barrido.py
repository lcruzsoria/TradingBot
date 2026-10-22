"""Patrón «Doble barrido»: NY Open cierra sobre los High de Asia y London, vuelve bajo ambos y se vende en el retesteo del más alto."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import timedelta

import numpy as np
import pytest

from tradingbot.skills.pattern.doble_barrido import DobleBarrido, analyze
from tradingbot.skills.pattern.patterns import DETECTED, EXPIRED, PATTERN_REGISTRY, ActiveTbr, PatternContext, PeerTbr

from tests.test_pattern import AHEAD, DAY, TBR, ny, run_skill, session, ASIA, LONDON, NY, m5_frame, FLAT

# Asia 100-110, London 98-106: el más alto de los dos High es el de Asia (110) y el Low más bajo, el de London (98).
# Velas M5 (open, high, low, close) desde el inicio de NY Open (10:00).
ROWS = [(100, 101, 99, 100),
        (100, 107, 100, 106.5),         # 1: cierra sobre el High de London (106), no sobre el de Asia
        (106.5, 111.5, 106, 111),       # 2: cierra sobre el High de Asia (110): ya ha cerrado sobre los dos
        (111, 113, 110.5, 112),         # 3: swing high (113)
        (112, 112.5, 108, 109),         # 4: lo confirma
        (109, 109.5, 105, 105.5),       # 5: pasa por debajo de los dos High (105 < 106)
        (105.5, 107, 105, 106.5),       # 6
        (106.5, 110.5, 106, 108)]       # 7: retesteo del High de Asia (110) con la mecha: entrada


def peers(asia=(110.0, 100.0), london=(106.0, 98.0), flip=False):
    """Asia (20:00 del día anterior a 00:00), London y NY Open del día; `flip` las refleja (200 - precio) para el lado alcista."""
    def peer(key, zone, day, hl, start, close):
        high, low = (200 - hl[1], 200 - hl[0]) if flip else hl
        return PeerTbr(key, zone, day, high, low, start, close)
    prev = DAY - timedelta(days=1)
    return (peer("ASIA", "Asia", prev, asia, ny(prev, 20, 0), ny(DAY, 0, 0)),
            peer("LONDON", "London", DAY, london, ny(DAY, 2, 0), ny(DAY, 5, 0)),
            peer("NY_AM", "NY Open", DAY, (105.0, 95.0), ny(DAY, 10, 0), ny(DAY, 12, 0)))


def ctx_for(rows, tbr=TBR, closed=False, peer_list=None, day_end=0):
    o, h, l, c = (np.array(x, dtype=float) for x in zip(*rows))
    ts = ny(DAY, 10, 0) + np.arange(len(rows)) * 300
    return PatternContext("EURUSD", "5m", 5, ts, o, h, l, c, tbr, 24, len(rows) - 1, closed, "NY-PM", "13:30", AHEAD, 0,
                          day_end=day_end, peers=peers() if peer_list is None else peer_list)


def mirror(rows):
    return [(200 - o, 200 - l, 200 - h, 200 - c) for o, h, l, c in rows]


def test_bajista_entra_en_el_retesteo_del_high_de_asia_con_stop_en_el_swing_y_objetivo_en_el_low_de_london():
    hits, figs = analyze(ctx_for(ROWS))
    assert len(hits) == 1
    h = hits[0]
    assert (h.key, h.status, h.direction, h.x, h.price) == ("doble_barrido", DETECTED, "short", 7, 110.0)
    assert h.levels == {"stop": pytest.approx(111.854), "target": 98.0} and "retesteo" in h.detail     # 0,618 entre el nivel (110) y el swing (113)
    assert [(f.kind, f.direction, f.levels["entrada"], f.levels["objetivo"]) for f in figs] == [("pos", "short", 110.0, 98.0)]
    assert figs[0].levels["stop"] == pytest.approx(111.854)
    assert analyze(ctx_for(ROWS), 1.0)[0][0].levels["stop"] == 113.0                                   # con 1, el propio swing


def test_alcista_es_el_espejo_exacto():
    hits, figs = analyze(ctx_for(mirror(ROWS), peer_list=peers(flip=True)))
    h = hits[0]
    assert (h.status, h.direction, h.x, h.price) == (DETECTED, "long", 7, 90.0)
    assert h.levels == {"stop": pytest.approx(88.146), "target": 102.0} and figs[0].direction == "long"


def test_el_orden_de_los_dos_high_es_indiferente():
    swapped = peers(asia=(106.0, 98.0), london=(110.0, 100.0))          # ahora el más alto es el de London
    h = analyze(ctx_for(ROWS, peer_list=swapped))[0][0]
    assert (h.status, h.price, h.levels["target"]) == (DETECTED, 110.0, 98.0)


def test_solo_con_mecha_sobre_los_high_no_hay_toma():
    rows = ROWS[:2] + [(106.5, 111.5, 106, 109.5), (109.5, 112, 105, 106)]   # la mecha supera el High de Asia pero ninguna vela cierra sobre él
    assert analyze(ctx_for(rows, closed=True)) == ([], [])


def test_un_dia_sin_setup_ny_solo_toma_el_high_de_london():
    rows = [(100, 101, 99, 100), (100, 107, 100, 106.5), (106.5, 109, 100, 101), (101, 102, 95, 96)]   # nunca cierra sobre el High de Asia
    assert analyze(ctx_for(rows, closed=True)) == ([], [])


def test_basta_la_mecha_para_pasar_bajo_los_dos_high():
    rows = list(ROWS)
    rows[5] = (109, 109.5, 105, 107)                                      # cierra sobre el High de London, pero su mecha lo cruzó
    h = analyze(ctx_for(rows))[0][0]
    assert (h.status, h.x) == (DETECTED, 7)


def test_el_swing_es_el_maximo_absoluto_hasta_pasar_bajo_los_dos_high():
    rows = list(ROWS)
    rows[4] = (112, 114, 108, 109)                                        # 4: un máximo más alto que el del 3 antes de bajar de los dos High
    h = analyze(ctx_for(rows))[0][0]
    assert (h.status, h.x, h.levels["stop"]) == (DETECTED, 7, pytest.approx(112.472))   # no invalida: el swing se desplaza al nuevo máximo


def test_si_cae_de_golpe_el_swing_es_el_maximo_del_tramo():
    rows = ROWS[:3] + [(111, 112, 105, 105.5),      # 3: baja de los dos High en la vela del máximo (112)
                       (105.5, 108, 105, 107),      # 4: sigue bajo el nivel
                       (107, 110.5, 106.5, 108)]    # 5: retesteo
    h = analyze(ctx_for(rows))[0][0]
    assert (h.status, h.x, h.levels["stop"]) == (DETECTED, 5, pytest.approx(111.236))


def test_sin_retesteo_hasta_el_cierre_del_dia_vence():
    rows = ROWS[:7]
    assert analyze(ctx_for(rows)) == ([], [])                          # aún queda día
    hits, figs = analyze(ctx_for(rows, closed=True))
    assert [(h.status, h.direction) for h in hits] == [(EXPIRED, "short")] and hits[0].levels == {"stop": pytest.approx(111.854), "target": 98.0}


def test_el_retesteo_despues_del_cierre_del_dia_no_cuenta():
    late = ROWS[:7] + [(106.5, 106.8, 106, 106.5)] * 60 + [(106.5, 110.5, 106, 108)]
    assert analyze(ctx_for(late, day_end=11 * 60))[0][0].status == EXPIRED   # el día de trading acaba a las 11:00 NY


def test_solo_se_busca_en_ny_open_y_necesita_las_tbr_de_asia_y_london():
    london = ActiveTbr("LONDON", "London", DAY, 106.0, 98.0, 0, 5)
    assert analyze(ctx_for(ROWS, tbr=london)) == ([], [])
    assert analyze(ctx_for(ROWS, peer_list=peers()[1:])) == ([], [])    # sin Asia
    stale = tuple(p for p in peers() if p.key != "ASIA") + (PeerTbr("ASIA", "Asia", DAY - timedelta(days=4), 110.0, 100.0,
                                                                  ny(DAY - timedelta(days=4), 20, 0), ny(DAY - timedelta(days=3), 0, 0)),)
    assert analyze(ctx_for(ROWS, peer_list=stale)) == ([], [])          # una Asia de hace días no es la del día


def test_ajustes_por_defecto():
    d = DobleBarrido()
    assert d.tf == "5m" and PATTERN_REGISTRY["doble_barrido"] is DobleBarrido
    assert d.stop_fib == 0.618 and DobleBarrido.title == "Doble barrido TBR"
    from tradingbot.envconfig import EnvConfig, parse
    for bad in ("0", "1.5"):
        with pytest.raises(ValueError, match="STOP_FIB"):
            DobleBarrido(EnvConfig(parse(f"PATTERN_DOBLE_BARRIDO_STOP_FIB={bad}\n")).section("PATTERN"))


def test_la_skill_pasa_las_tbr_de_asia_y_london_y_avisa_del_patron():
    frame = m5_frame(ROWS + [FLAT] * 17 + [FLAT], start_ny=(10, 0))        # 10:00-12:00 es NY Open
    sessions = [session(ASIA, DAY - timedelta(days=1), 5, 110, 100), session(LONDON, DAY, 10, 106, 98), session(NY, DAY, 15)]
    from tests.test_pattern import EnvConfig, parse, time
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus, found = EventBus(), []
    bus.subscribe("t", "pattern.detected", found.append)
    manager = SkillManager(bus, Services(None, None, {"app": {}}, EnvConfig(parse("PATTERN_TYPES=doble_barrido\n"))), [{"type": "pattern"}])
    manager.start()
    bus.publish("candles.loaded", {"symbol": "EURUSD", "timeframe": "5m", "df": frame}, source="feed")
    bus.publish("tbr.updated", {"symbol": "EURUSD", "timeframe": "5m", "sessions": sessions, "available": True}, source="tbr")
    deadline = time.time() + 3
    while not found and time.time() < deadline:
        time.sleep(0.02)
    manager.stop()
    assert len(found) == 1
    hit = found[0].payload["hit"]
    assert (hit.key, hit.direction, hit.price, hit.levels["stop"], hit.levels["target"]) == ("doble_barrido", "short", 110.0, pytest.approx(111.854), 98.0)


def test_las_tomas_pueden_ser_antes_de_ny_open_pero_la_entrada_no():
    early = ctx_for(ROWS)
    object.__setattr__(early, "start_bar", 6)                           # NY Open empieza en la vela 6: el cierre sobre los High fue antes
    h = analyze(early)[0][0]
    assert (h.status, h.x, h.price) == (DETECTED, 7, 110.0)
    late = ctx_for(ROWS)
    object.__setattr__(late, "start_bar", 8)                            # NY Open empieza tras el retesteo: ese toque no vale como entrada
    assert analyze(late) == ([], [])
    rows = ROWS + [(108, 108.5, 104, 105), (105, 110.2, 104.5, 109)]    # 8: vuelve bajo el nivel; 9: lo retestea ya en NY Open: entrada
    hit = analyze(late.__class__(**{**late.__dict__, "ts": ctx_for(rows).ts, "open": ctx_for(rows).open, "high": ctx_for(rows).high,
                                    "low": ctx_for(rows).low, "close": ctx_for(rows).close, "last_bar": len(rows) - 1}))[0][0]
    assert (hit.status, hit.x, hit.price) == (DETECTED, 9, 110.0)


def test_un_retesteo_ya_en_curso_al_empezar_ny_open_no_es_entrada():
    rows = ROWS[:7] + [(106.5, 110.5, 106, 110.2), (110.2, 110.8, 109, 110)]   # 7 y 8 siguen tocando el nivel sin haber bajado de él
    ctx = ctx_for(rows)
    object.__setattr__(ctx, "start_bar", 8)
    assert analyze(ctx) == ([], [])


def test_un_solo_trade_al_dia_aunque_el_otro_lado_tambien_de_entrada():
    rows = ROWS + [(108, 108, 95, 96),          # 8: cierra bajo el Low más bajo (98): toma del lado alcista; swing low 95
                   (99, 101, 98.5, 100.5),      # 9: lo confirma y vuelve sobre los dos Low
                   (100.5, 100.8, 97.5, 98)]    # 10: retestea el Low de London (98): sería un largo
    hits, figs = analyze(ctx_for(rows))
    assert [(h.direction, h.x) for h in hits] == [("short", 7)] and len(figs) == 1      # solo el primero


def test_el_breakeven_de_este_patron_salta_en_cuanto_el_precio_toca_1r():
    from types import SimpleNamespace
    from tradingbot.skills.setup.positions import resolve
    ts = np.arange(5, dtype=np.int64) * 300 + ny(DAY, 11, 0)
    high = np.array([110.0, 109.0, 108.5, 110.2, 109.0])
    low = np.array([108.0, 106.9, 106.0, 108.0, 107.0])                # 1: el mínimo toca 107 = 1 R a favor (entrada 110, stop 113)
    close = np.array([109.0, 108.0, 107.5, 109.0, 108.0])             # ningún cierre llega a 107
    order = SimpleNamespace(direction="short", pattern_key="doble_barrido", price=110.0, stop=113.0, target=98.0,
                            entry_ts=int(ts[0]), close_ts=int(ts[0]) + 3600)
    done = resolve(order, ts, high, low, close, 1.0, 300)
    assert (done.result, done.r, done.exit_ts, done.be_ts) == ("breakeven", 0.0, int(ts[3]), int(ts[1]))
    other = SimpleNamespace(**{**order.__dict__, "pattern_key": "continuacion"})
    assert resolve(other, ts, high, low, close, 1.0, 300) is None      # los demás patrones siguen esperando al cierre de la vela de 15 min
