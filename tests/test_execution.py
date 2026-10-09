"""Bias Execution (GO / NO GO de los setups), recálculo programado del Bias y Registro con detalle."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import date, datetime

import pytest

from tradingbot.clock import NY
from tradingbot.skills.bias import Bias, BiasResult
from tradingbot.skills.bias.execution import ExecutionGate
from tradingbot.skills.bias.schedule import next_recalc
from tradingbot.skills.setup.setups import Setup


def setup(direction="long", status="armed", kind="continuation", entry=105.0):
    return Setup("NY-AM", "NY_AM", date(2026, 10, 6), direction, 105.0, 95.0, 100.0, 4, status, retest_x=5,
                 rebreak_x=6, entry=entry, stop=99.5, target=115.0, kind=kind)


def result(bias, day_open=100.0):
    return BiasResult(bias, date(2026, 10, 6), levels={"Apertura": day_open})


def test_go_a_favor_del_sesgo():
    d = ExecutionGate().evaluate(setup("long"), result(Bias.BULLISH))
    assert d.allowed and d.verdict == "GO" and all(c.passed for c in d.checks)
    assert ExecutionGate().evaluate(setup("long", "filled"), result(Bias.BULLISH)).allowed


def test_no_go_contra_el_sesgo():
    d = ExecutionGate().evaluate(setup("long"), result(Bias.BEARISH))
    assert not d.allowed and d.reason.startswith("Sesgo: Long contra el sesgo Bearish")
    assert ExecutionGate().evaluate(setup("short"), result(Bias.BEARISH)).allowed


def test_sin_sesgo_no_se_opera_salvo_que_se_permita():
    assert "No Bias" in ExecutionGate().evaluate(setup(), result(Bias.NO_BIAS)).reason
    assert ExecutionGate(allow_no_bias=True).evaluate(setup(), result(Bias.NO_BIAS)).allowed
    assert "aún no está calculado" in ExecutionGate().evaluate(setup(), None).reason


def test_esperando_pasos_caducado_e_invalidado():
    d = ExecutionGate().evaluate(setup(status="sweep", entry=None), result(Bias.BULLISH))
    assert not d.allowed and d.reason == "Armado: esperando el retest del 50 %"
    d = ExecutionGate().evaluate(setup(status="retest", entry=None), result(Bias.BULLISH))
    assert d.reason == "Armado: esperando la segunda ruptura"
    d = ExecutionGate().evaluate(setup(status="expired"), result(Bias.BULLISH))
    assert not d.allowed and d.reason.startswith("Vigente: caducado")
    assert not ExecutionGate().evaluate(setup(status="invalid"), result(Bias.BULLISH)).allowed


def test_premium_discount_solo_en_reversiones():
    cheap = setup("short", kind="reversal", entry=99.0)                # vende en descuento: mal
    assert "descuento" in ExecutionGate().evaluate(cheap, result(Bias.BEARISH)).reason
    assert ExecutionGate(premium_discount=False).evaluate(cheap, result(Bias.BEARISH)).allowed
    cont = setup("short", entry=99.0)                                  # una continuación no se filtra
    assert ExecutionGate().evaluate(cont, result(Bias.BEARISH)).allowed


def ny(h, m=0, d=6):
    return datetime(2026, 10, d, h, m, tzinfo=NY)


@pytest.mark.parametrize("now, anchor, hours, expected", [
    (ny(19, 10), 18 * 60, 3, ny(21)),                 # índice USA: 18, 21, 00...
    (ny(21, 0), 18 * 60, 3, ny(0, 0, 7)),             # justo en la hora: la siguiente
    (ny(2, 0), 18 * 60, 3, ny(3)),                    # ancla del día anterior
    (ny(18, 5), 17 * 60, 4, ny(21)),                  # resto: 17, 21, 01...
    (ny(12, 0), 17 * 60, 4, ny(13)),
])
def test_proximo_recalculo(now, anchor, hours, expected):
    assert next_recalc(now, anchor, hours) == expected


def test_el_registro_enlaza_el_detalle():
    from PySide6.QtWidgets import QApplication
    QApplication.instance() or QApplication([])
    from tradingbot.ui.logview import LogView
    log = LogView()
    log.add("bias: Bullish", "línea 1\nlínea 2", "go")
    log.add("feed: velas cargadas")
    html = log.toHtml()
    assert "detalle:1" in html and html.count("detalle:") == 1
    assert "bias: Bullish" in log.toPlainText() and "+ detalle" in log.toPlainText()
