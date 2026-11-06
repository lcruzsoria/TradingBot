"""Patrón «Reversión»: toma de un lado de la TBR solo con mecha en M15, fibonacci mecha pivote -> pivote siguiente, entrada en el 0,5."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from functools import partial

import pytest

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.pattern.patterns import DETECTED, EXPIRED, INVALIDATED, PATTERN_REGISTRY
from tradingbot.skills.pattern.reversion import Reversion, analyze as _analyze

from tests.test_continuacion import ctx_for, m5_from_m15, mirror
from tests.test_pattern import run_skill

analyze = partial(_analyze, mode="mecha")          # los tests de abajo (hasta el de la skill) son del fibo con la mecha de la toma como 1

# TBR 95-105 (50 % = 100). Velas M15 (open, high, low, close); las 0-2 dentro de la TBR y la 3 en adelante tras su cierre.
ROWS = [(100, 101, 99, 100), (100, 102, 99, 101), (101, 103, 100, 102),
        (102, 104, 101, 103),          # 3: no toma nada
        (103, 106, 102, 104.5),        # 4: TOMA CON MECHA del High (máx. 106) y cierra dentro: mecha pivote
        (104.5, 104.8, 101, 102),      # 5: confirma la mecha pivote (su máximo es el más alto de las tres 3, 4 y 5)
        (102, 102.5, 98, 99),          # 6
        (99, 100, 96, 97),             # 7: el pivote bajo que genera a continuación (mínimo 96): el 0
        (97, 99.5, 96.5, 98.5),        # 8: lo confirma (no llega al 0,5: 101)
        (98.5, 101.5, 98, 101)]        # 9: retrocede hasta el 0,5: entrada

# Fibo por defecto: 0 = swing low tras la mecha (vela 7, 96), 1 = swing high siguiente (vela 9, 101,5: por encima del máximo de la vela del 0, 100)
ROWS_SWING = ROWS[:9] + [(98.5, 101.5, 98, 101),        # 9: swing high (el 1), lo confirma la 10
                         (101, 101.2, 97.5, 98),        # 10: máximo más bajo que el de la 9 (confirma); cierra bajo el 0,5 (98,75)
                         (98, 99.2, 97, 98.9)]          # 11: abre bajo el 0,5 y sube hasta él: entrada


def run(rows, **kw):
    return analyze(ctx_for(rows, first_bar=3, **kw), 1)


def test_bajista_mecha_pivote_pivote_siguiente_y_entrada_en_el_05():
    hits, figs = run(ROWS)
    assert len(hits) == 1
    h = hits[0]
    assert (h.key, h.status, h.direction, h.x, h.price) == ("reversion", DETECTED, "short", 9, 101.0)   # el 0,5 entre 106 y 96
    assert h.levels["stop"] == 106.0 and h.levels["target"] == 91.0                                      # stop en la mecha: 2R
    f = figs[0]
    assert (f.kind, f.key, f.direction, f.state) == ("fib", "reversion", "short", "entrada")
    assert f.levels == {"-0,5": 91.0, "0": 96.0, "0,5": 101.0, "1": 106.0} and f.x0_ts == int(ctx_for(ROWS).ts[4])
    assert "mecha pivote" in h.detail and "RR 2" in h.detail


def test_alcista_es_el_espejo_exacto():
    hits, figs = analyze(ctx_for(mirror(ROWS), first_bar=3), 1)
    h = hits[0]
    assert (h.status, h.direction, h.x, h.price) == (DETECTED, "long", 9, 99.0)
    assert h.levels["stop"] == 94.0 and h.levels["target"] == 109.0 and figs[0].levels["1"] == 94.0 and figs[0].levels["0"] == 104.0


def test_una_rotura_con_cuerpo_no_es_reversion():
    body = list(ROWS)
    body[4] = (103, 106, 102, 105.5)                                  # cierra sobre el High: rotura con cuerpo (es de Continuación)
    assert run(body) == ([], [])


def test_si_antes_de_confirmar_la_mecha_una_vela_cierra_fuera_se_invalida():
    rows = ROWS[:5] + [(104.5, 107, 104, 106)]                        # tras la mecha, una vela cierra por encima del High
    h = run(rows)[0][0]
    assert h.status == INVALIDATED and "ya no es reversión" in h.detail


def test_si_ya_confirmada_la_mecha_una_vela_cierra_fuera_antes_de_la_entrada_se_anula():
    rows = ROWS[:6] + [(102, 105.8, 100.5, 105.5)]                    # 6: cierra sobre el High (sin superar la mecha) antes del 0,5
    hits, figs = run(rows)
    assert [(h.status, h.x) for h in hits] == [(INVALIDATED, 6)] and figs == []
    assert "rotura con cuerpo" in hits[0].detail
    h = analyze(ctx_for(mirror(rows), first_bar=3), 1)[0][0]           # y su espejo: cierre bajo el Low
    assert (h.status, h.direction, h.x) == (INVALIDATED, "long", 6)


def test_una_rotura_con_cuerpo_despues_de_la_entrada_no_la_anula():
    hits, _ = run(ROWS + [(101, 105.8, 100.5, 105.5)])
    assert [(h.status, h.x) for h in hits] == [(DETECTED, 9)]


def test_una_misma_vela_con_mecha_en_los_dos_lados_no_da_patron():
    h = run([ROWS[0], ROWS[1], ROWS[2], (100, 106, 94, 100)])[0][0]
    assert h.status == INVALIDATED and h.direction == "" and "High y el Low" in h.detail


def test_el_0_se_desplaza_al_siguiente_pivote_mientras_no_revierta_al_0_5():
    rows = ROWS[:9] + [(98.5, 99.0, 93, 94),                          # 9: no revierte (máx. 99 < 101) y baja más
                       (94, 96, 93.5, 95)]                            # 10: confirma el pivote bajo 93: el 0 pasa del 96 al 93 (0,5 en 99,5)
    hits, figs = run(rows)
    assert hits == [] and figs[0].levels == {"-0,5": 86.5, "0": 93.0, "0,5": 99.5, "1": 106.0} and figs[0].state == "en curso"
    hits, figs = run(rows + [(95, 99.6, 94.5, 99)])                   # 11: revierte al 0,5 del fibo vigente (99,5): entrada
    assert [(h.status, h.x, h.price) for h in hits] == [(DETECTED, 11, 99.5)] and figs[0].levels["0"] == 93.0


def test_si_el_precio_supera_la_mecha_pivote_antes_de_la_entrada_se_invalida():
    rows = ROWS[:9] + [(98.5, 106.5, 98, 104)]
    h = run(rows)[0][0]
    assert (h.status, h.x) == (INVALIDATED, 9) and "superó la mecha pivote" in h.detail
    hit, figs = run(rows)
    assert hit[0].levels["fibo 0,5"] == 101.0 and [f.state for f in figs] == ["invalidada"]       # el 0 ya estaba fijado: se dibuja y Cortex lo anota «I»


def test_sin_toma_con_mecha_nada_y_al_acabar_el_plazo_vence():
    assert run(ROWS[:4]) == ([], [])
    h = run(ROWS[:4], closed=True)[0][0]
    assert h.status == EXPIRED and "no hubo toma con mecha" in h.detail and "NY-PM (13:30 NY)" in h.detail
    assert run(ROWS[:5]) == ([], [])                                  # mecha tomada pero aún sin pivote confirmado
    assert run(ROWS[:5], closed=True)[0][0].status == EXPIRED
    no_entry = run(ROWS[:9], closed=True)[0][0]
    assert no_entry.status == EXPIRED and "sin retroceso al 0,5" in no_entry.detail


def test_ajustes_del_patron_reversion():
    p = Reversion(EnvConfig(parse("PATTERN_REVERSION_TF=M5\nPATTERN_REVERSION_SWING_BARS=2\n")).section("PATTERN"))
    assert (p.tf, p.swing_bars) == ("5m", 2)
    d = Reversion()
    assert (d.tf, d.swing_bars) == ("15m", 1) and PATTERN_REGISTRY["reversion"] is Reversion
    for text, key in (("PATTERN_REVERSION_SWING_BARS=0\n", "SWING_BARS"), ("PATTERN_REVERSION_TF=2h\n", "Timeframe")):
        with pytest.raises(ValueError, match=key):
            Reversion(EnvConfig(parse(text)).section("PATTERN"))


def test_la_skill_detecta_la_reversion_con_el_grafico_en_m5():
    inside = [(100, 101, 99, 100)] * 8                                # 10:00-12:00, dentro de la TBR
    rows = inside + ROWS_SWING[4:] + [(101, 102, 100, 101)]                 # 12:00-13:15 (el plazo de NY Open acaba a las 13:30); la última sigue formándose
    manager, _bus, found, dropped, _s, updated = run_skill("PATTERN_TYPES=reversion\n", df=m5_from_m15(rows))
    manager.stop()
    assert len(found) == 1 and dropped == []
    p = found[0].payload
    assert p["timeframe"] == "15m" and p["hit"].key == "reversion" and p["hit"].direction == "short" and p["hit"].price == 98.75
    fig = updated[-1].payload["figures"][0]
    assert fig.key == "reversion" and fig.levels["1"] == 101.5 and fig.levels["0"] == 96.0


def test_stop_y_objetivo_en_los_niveles_configurados():
    from tradingbot.envconfig import EnvConfig, parse
    from tradingbot.skills.pattern.fibo import level_settings
    from tradingbot.skills.pattern.reversion import Reversion
    pat = Reversion(EnvConfig(parse("PATTERN_STOP_LEVEL=0.9\nPATTERN_TARGET_LEVEL=-0.2\n")).section("PATTERN"))
    hits, figs = pat.detect(ctx_for(ROWS_SWING, first_bar=3)), pat.figures(ctx_for(ROWS_SWING, first_bar=3))
    h, f = hits[0], figs[0]
    # el 0 en 96 y el 1 (swing high) en 101,5: stop en el 0,9 = 100,95, objetivo en el -0,2 = 94,9; entrada en el 0,5 = 98,75
    assert h.levels["stop"] == pytest.approx(100.95) and h.levels["target"] == pytest.approx(94.9)
    assert set(f.levels) == {"-0,2", "0", "0,5", "0,9", "1"} and f.target == "-0,2"
    assert "stop en el 0,9 y objetivo en el -0,2" in h.detail
    assert level_settings(lambda k, d: d) == (1.0, -0.2)                                  # por defecto: stop en el 1, objetivo en el -0,2
    for bad in ({"STOP_LEVEL": "0.4"}, {"TARGET_LEVEL": "0.6"}, {"STOP_LEVEL": "x"}):
        with pytest.raises(ValueError):
            level_settings(lambda k, d, b=bad: b.get(k, d))


# -- confirmaciones opcionales (CISD en M15; BPR + retest + cierre bajo el CISD en velas menores) ---------------------------------------------
import numpy as np

from tradingbot.skills.pattern import confirm as confirmation


def test_cisd_confirma_con_el_cierre_bajo_el_minimo_de_la_secuencia_alcista():
    ctx = ctx_for(ROWS, first_bar=3)
    # la secuencia alcista que incluye la mecha pivote (velas 1-4) tiene su mínimo en 99: cierra bajo él la vela 7 (cierre 97)
    assert confirmation.cisd_confirmation(ctx.high, ctx.low, ctx.open, ctx.close, 4, 0, 9) == 7
    hits, _ = analyze(ctx, 1, confirm="cisd")
    assert (hits[0].status, hits[0].x) == (DETECTED, 9)


def test_sin_cierre_bajo_el_cisd_no_hay_entrada():
    rows = list(ROWS)
    rows[1] = (100, 102, 90, 101)                                     # la secuencia llega hasta 90: ninguna vela cierra por debajo
    hits, _ = analyze(ctx_for(rows, first_bar=3), 1, confirm="cisd")
    assert not [h for h in hits if h.status == DETECTED]


def test_el_cisd_es_el_espejo_en_largo():
    ctx = ctx_for(mirror(ROWS), first_bar=3)
    hits, _ = analyze(ctx, 1, confirm="cisd")
    assert (hits[0].status, hits[0].direction, hits[0].x) == (DETECTED, "long", 9)


BPR = np.array([(10, 11, 9.5, 10.8), (10.8, 12, 10.5, 11.9), (12, 14, 11.8, 13.9),      # secuencia alcista con el iFVG (11 - 11,8)
                (13.9, 14.1, 12, 13.2), (13.2, 13.3, 10, 10.2),                          # la 4 lo invierte (cierra bajo 11)
                (10.2, 10.8, 9.8, 10),                                                   # nace el FVG bajista (10,8 - 12): BPR 11 - 11,8
                (10, 11.5, 10, 11.2),                                                    # retest del BPR sin cerrar sobre él
                (11, 11.1, 9, 9.2)])                                                     # cierra bajo el CISD (9,5)


def bpr(rows):
    o, h, l, c = rows.T
    return confirmation.bpr_confirmation(h, l, o, c, 2, 0, len(rows) - 1)


def test_bpr_retest_y_cierre_bajo_el_cisd():
    assert bpr(BPR) == 7


def test_el_retest_que_cierra_al_otro_lado_del_bpr_lo_invalida():
    rows = BPR.copy()
    rows[6] = (10, 12.5, 10, 12)                                      # cierra por encima de la zona común
    assert bpr(rows) is None


def test_sin_retest_no_hay_confirmacion_bpr():
    rows = BPR.copy()
    rows[6] = (10, 10.5, 9.9, 10.1)                                   # no sube hasta el BPR
    assert bpr(rows) is None


# -- fibo por defecto: del swing low (0) al swing high posterior (1), como en Continuación, tras la toma con mecha ---------------------------------
def test_el_fibo_va_del_swing_posterior_a_la_mecha_al_swing_opuesto_y_entra_en_el_05():
    hits, figs = _analyze(ctx_for(ROWS_SWING, first_bar=3), 1)
    h = hits[0]
    assert (h.status, h.direction, h.x, h.price) == (DETECTED, "short", 11, 98.75)
    assert h.levels["stop"] == 101.5 and h.levels["target"] == pytest.approx(93.25)                  # stop en el 1 (el swing high), objetivo -0,5
    assert figs[0].levels == {"-0,5": pytest.approx(93.25), "0": 96.0, "0,5": 98.75, "1": 101.5} and figs[0].x0_ts == int(ctx_for(ROWS_SWING).ts[7])
    assert "swing low (0)" in h.detail and "swing high (1)" in h.detail                               # en el corto el 0 es el swing low y el 1 el high
    hm, fm = _analyze(ctx_for(mirror(ROWS_SWING), first_bar=3), 1)
    assert (hm[0].status, hm[0].direction, hm[0].x, hm[0].price) == (DETECTED, "long", 11, 101.25) and fm[0].levels["1"] == 98.5


def test_el_1_tiene_que_quedar_mas_alla_del_extremo_de_la_vela_del_0():
    rows = list(ROWS_SWING)
    rows[9] = (98.5, 99.8, 98, 99)                                     # un swing high por debajo del máximo de la vela del 0 (100): no define el fibo
    hits, figs = _analyze(ctx_for(rows[:11], first_bar=3), 1)
    assert hits == [] and figs == []


def test_sin_swing_high_posterior_no_hay_fibo_y_vence():
    h = _analyze(ctx_for(ROWS[:9], first_bar=3, closed=True), 1)[0][0]
    assert h.status == EXPIRED and "sin swing high y swing low posteriores" in h.detail


def test_perder_la_mecha_antes_de_tener_el_fibo_invalida():
    rows = ROWS[:7] + [(99, 106.5, 98, 105)]                           # supera la mecha (106) antes de que haya swing low
    h = _analyze(ctx_for(rows, first_bar=3), 1)[0][0]
    assert h.status == INVALIDATED and "perdió la mecha pivote" in h.detail


def test_la_vela_que_confirma_el_swing_no_puede_ser_la_entrada():
    rows = ROWS[:9] + [(98.5, 101.5, 98, 101), (101, 101.2, 98.7, 98.8)]          # 10 confirma el 1 y ya toca el 0,5: aún no se podía saber
    assert _analyze(ctx_for(rows, first_bar=3), 1)[0] == []
