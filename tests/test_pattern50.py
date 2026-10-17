"""Patrón 2 (continuación 50 %): activación al tomar el 50 %, límite en el extremo contrario y exclusividad con el patrón 1."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.pattern import continuation, continuation50
from tradingbot.skills.pattern.activation import first_event
from tradingbot.skills.pattern.patterns import ANNULLED, DETECTED, EXPIRED, INVALIDATED, PATTERN_REGISTRY

from tests.test_pattern import candles_after_close, ctx_for, m5_frame, mirror, run_skill

# TBR 95-105, 50 % = 100. Bajista: el precio sube desde la mitad baja y toma el 50 %.
DRIFT = (97, 98, 96, 97.5)                  # alcista, en la mitad baja, sin tomar nada
ACTIVATION = (97.5, 101, 97, 100.5)         # toma el 50 % (máximo 101) sin tocar el High
WICKED = (100.5, 101.5, 98, 99)             # bajista con mecha superior (y por encima del 50 %)
TRIGGER = (98.5, 98.5, 94, 95)              # bajista sin mecha superior, con el máximo bajo el 50 %


def scan50(rows, wick=0.0, candles=10, closed=False):
    return continuation50.scan(ctx_for(rows, closed), wick, candles)


def test_patron_2_bajista_dispara_con_la_primera_vela_sin_mecha_bajo_el_50():
    hits = scan50([DRIFT, ACTIVATION, WICKED, TRIGGER])
    assert len(hits) == 1
    h = hits[0]
    assert (h.key, h.status, h.direction, h.x, h.price) == ("continuacion_50", DETECTED, "short", 3, 95.0)
    assert h.levels == {"toma 50 %": 100.0, "máx. antes del disparo": 101.5}
    assert "de abajo hacia arriba" in h.detail and "nº 3 de 10" in h.detail and "bajo el 50 %" in h.detail


def test_la_vela_de_disparo_debe_estar_bajo_el_50():
    above = (101, 101, 99, 100)                                       # sin mecha superior, pero su máximo está sobre el 50 %
    assert scan50([DRIFT, ACTIVATION, above]) == []                  # no vale: se sigue esperando
    h = scan50([DRIFT, ACTIVATION, above, TRIGGER])[0]
    assert (h.status, h.x) == (DETECTED, 3)


def test_la_vela_que_toma_el_50_no_es_la_de_disparo_y_el_disparo_va_desde_la_siguiente():
    bearish_activation = (101, 101, 95.5, 96)                          # toma el 50 % (viniendo de abajo) y cierra bajista sin mecha
    ctx = ctx_for([DRIFT, bearish_activation])
    assert first_event(ctx).kind == "mid" and first_event(ctx).index == 1
    assert scan50([DRIFT, bearish_activation]) == []                  # ella no dispara


def test_si_la_vela_que_toma_el_50_toma_tambien_el_high_se_invalida():
    h = scan50([DRIFT, (97.5, 106, 97, 100.5), TRIGGER])[0]
    assert (h.status, h.direction, h.x) == (INVALIDATED, "short", 1) and "tomó también el High" in h.detail


def test_nunca_puede_tocar_el_extremo_contrario_antes_del_disparo():
    for rows in ([DRIFT, ACTIVATION, (100, 105, 99, 100), TRIGGER], [DRIFT, ACTIVATION, (100, 107, 99, 100), TRIGGER]):
        h = scan50(rows)[0]
        assert (h.status, h.x) == (INVALIDATED, 2) and "tocó el High" in h.detail
    assert scan50([DRIFT, ACTIVATION, (100, 104.9, 99, 100), TRIGGER])[0].status == DETECTED       # sin llegar al High


def test_la_cuenta_de_10_velas_incluye_la_vela_que_toma_el_50():
    ok = scan50([DRIFT, ACTIVATION] + [WICKED] * 8 + [TRIGGER])                                    # la de activación es la 1; disparo en la nº 10
    assert [(h.status, h.x) for h in ok] == [(DETECTED, 10)] and "nº 10 de 10" in ok[0].detail
    late = scan50([DRIFT, ACTIVATION] + [WICKED] * 9 + [TRIGGER])                                  # sería la nº 11
    assert [(h.status, h.x) for h in late] == [(ANNULLED, 10)]
    assert scan50([DRIFT, ACTIVATION] + [WICKED] * 4) == []                                        # aún quedan velas por mirar


def test_mecha_superior_maxima_ajustable():
    small = (98.5, 98.65, 94, 95)                                                                   # mecha del 3 %
    assert scan50([DRIFT, ACTIVATION, small]) == []
    assert scan50([DRIFT, ACTIVATION, small], wick=5.0)[0].status == DETECTED


def test_patron_2_alcista_es_el_espejo_exacto():
    hits = continuation50.scan(ctx_for(mirror([DRIFT, ACTIVATION, WICKED, TRIGGER])), 0.0, 10)
    assert [(h.status, h.direction, h.x) for h in hits] == [(DETECTED, "long", 3)] and hits[0].price == 105.0
    assert "de arriba hacia abajo" in hits[0].detail
    assert continuation50.scan(ctx_for(mirror([DRIFT, (97.5, 106, 97, 100.5), TRIGGER])), 0.0, 10)[0].status == INVALIDATED
    assert continuation50.scan(ctx_for(mirror([DRIFT, ACTIVATION, (100, 105, 99, 100), TRIGGER])), 0.0, 10)[0].status == INVALIDATED


def test_al_acabar_el_plazo_de_la_tbr_vence_pero_sin_activacion_no_avisa():
    h = scan50([DRIFT, ACTIVATION, WICKED], closed=True)[0]
    assert h.status == EXPIRED and "toma del 50 %" in h.detail and "NY-PM (13:30 NY)" in h.detail
    assert scan50([DRIFT, DRIFT, DRIFT], closed=True) == []                                         # no hubo activación: silencio


def test_solo_se_activa_un_patron_por_tbr():
    low_first = [(97, 98, 94, 95), (95, 99, 94.5, 98), (97, 97, 92, 93)]                            # toma el Low antes que el 50 %: patrón 1
    assert first_event(ctx_for(low_first)).kind == "extreme"
    assert scan50(low_first) == [] and continuation.scan(ctx_for(low_first), 0.0, 10)[0].status == DETECTED
    mid_first = [DRIFT, ACTIVATION, (100.5, 100.5, 93, 94), (94, 94, 90, 91)]                       # toma el 50 % y luego el Low: patrón 2
    assert first_event(ctx_for(mid_first)).kind == "mid"
    assert continuation.scan(ctx_for(mid_first), 0.0, 10) == []                                     # el patrón 1 se descarta sin aviso
    assert [(h.status, h.x) for h in scan50(mid_first)] == [(DETECTED, 3)]
    tie = [DRIFT, (97, 101, 94, 100)]                                                                # 50 % y Low (de donde venía) en la misma vela
    assert first_event(ctx_for(tie)).kind == "extreme"                                               # vale como toma de un extremo
    assert scan50(tie + [TRIGGER]) == []


def test_ajustes_del_patron_2():
    p = continuation50.HalfContinuation(EnvConfig(parse("PATTERN_CONTINUATION50_MAX_WICK_PCT=2\nPATTERN_CONTINUATION50_TF=M1\n"
                                                        "PATTERN_CONTINUATION50_MAX_CANDLES=6\n")).section("PATTERN"))
    assert (p.max_wick_pct, p.tf, p.max_candles) == (2.0, "1m", 6)
    d = continuation50.HalfContinuation()
    assert (d.max_wick_pct, d.tf, d.max_candles) == (0.0, "5m", 10) and PATTERN_REGISTRY["continuacion_50"] is continuation50.HalfContinuation
    for text in ("PATTERN_CONTINUATION50_MAX_WICK_PCT=7\n", "PATTERN_CONTINUATION50_MAX_CANDLES=0\n"):
        with pytest.raises(ValueError, match="CONTINUATION50"):
            continuation50.HalfContinuation(EnvConfig(parse(text)).section("PATTERN"))


def test_la_skill_activa_solo_el_patron_que_tiene_el_primer_hecho():
    rows = candles_after_close([DRIFT, ACTIVATION, WICKED, TRIGGER])
    manager, _bus, found, dropped, *_ = run_skill(df=m5_frame(rows))
    manager.stop()
    assert [(f.payload["hit"].key, f.payload["hit"].direction) for f in found] == [("continuacion_50", "short")]
    assert dropped == []                                                                            # el patrón 1 se descarta sin avisar
    rows = candles_after_close([(97, 98, 94, 95), (95, 99, 94.5, 98), (97, 97, 92, 93)])
    manager, _bus, found, dropped, *_ = run_skill(df=m5_frame(rows))
    manager.stop()
    assert [f.payload["hit"].key for f in found] == ["continuacion_clasica"] and dropped == []
