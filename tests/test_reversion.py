"""Patrón «Reversión»: toma de un lado de la TBR solo con mecha en M15, fibonacci mecha pivote -> pivote siguiente, entrada en el 0,5."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.pattern.patterns import DETECTED, EXPIRED, INVALIDATED, PATTERN_REGISTRY
from tradingbot.skills.pattern.reversion import Reversion, analyze

from tests.test_continuacion import ctx_for, m5_from_m15, mirror
from tests.test_pattern import run_skill

# TBR 95-105 (50 % = 100). Velas M15 (open, high, low, close); las 0-2 dentro de la TBR y la 3 en adelante tras su cierre.
ROWS = [(100, 101, 99, 100), (100, 102, 99, 101), (101, 103, 100, 102),
        (102, 104, 101, 103),          # 3: no toma nada
        (103, 106, 102, 104.5),        # 4: TOMA CON MECHA del High (máx. 106) y cierra dentro: mecha pivote
        (104.5, 104.8, 101, 102),      # 5: confirma la mecha pivote (su máximo es el más alto de las tres 3, 4 y 5)
        (102, 102.5, 98, 99),          # 6
        (99, 100, 96, 97),             # 7: el pivote bajo que genera a continuación (mínimo 96): el 0
        (97, 99.5, 96.5, 98.5),        # 8: lo confirma (no llega al 0,5: 101)
        (98.5, 101.5, 98, 101)]        # 9: retrocede hasta el 0,5: entrada


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
    assert "mecha pivote" in h.detail and "2R" in h.detail


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


def test_una_misma_vela_con_mecha_en_los_dos_lados_no_da_patron():
    h = run([ROWS[0], ROWS[1], ROWS[2], (100, 106, 94, 100)])[0][0]
    assert h.status == INVALIDATED and h.direction == "" and "High y el Low" in h.detail


def test_el_0_se_desplaza_al_pivote_mas_bajo_antes_de_revertir_al_05():
    rows = ROWS[:9] + [(98.5, 99.0, 93, 94),                          # 9: no revierte (máx. 99 < 101) y baja más
                       (94, 96, 93.5, 95),                            # 10: confirma el pivote bajo 93 (el 0 pasa a 93)
                       (95, 99.6, 94.5, 99)]                          # 11: 0,5 nuevo = (93+106)/2 = 99,5 -> entrada
    hits, figs = run(rows)
    assert [(h.status, h.x, h.price) for h in hits] == [(DETECTED, 11, 99.5)]
    assert figs[0].levels["0"] == 93.0 and hits[0].levels["target"] == 86.5
    hits, figs = run(rows[:11])                                       # antes de la entrada: el 0 ya es el nuevo pivote
    assert hits == [] and figs[0].levels["0"] == 93.0 and figs[0].state == "en curso"


def test_si_el_precio_supera_la_mecha_pivote_antes_de_la_entrada_se_invalida():
    rows = ROWS[:9] + [(98.5, 106.5, 98, 104)]
    h = run(rows)[0][0]
    assert (h.status, h.x) == (INVALIDATED, 9) and "superó la mecha pivote" in h.detail
    assert run(rows)[1] == []


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
    rows = inside + ROWS[4:] + [(101, 102, 100, 101)]                 # 12:00-13:15 (el plazo de NY Open acaba a las 13:30); la última sigue formándose
    manager, _bus, found, dropped, _s, updated = run_skill("PATTERN_TYPES=reversion\n", df=m5_from_m15(rows))
    manager.stop()
    assert len(found) == 1 and dropped == []
    p = found[0].payload
    assert p["timeframe"] == "15m" and p["hit"].key == "reversion" and p["hit"].direction == "short" and p["hit"].price == 101.0
    fig = updated[-1].payload["figures"][0]
    assert fig.key == "reversion" and fig.levels["1"] == 106.0 and fig.levels["0"] == 96.0
