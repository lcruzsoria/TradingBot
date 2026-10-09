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


def setup(direction="short", kind="reversal", entry=105.0, confirm_x=10):
    return Setup("NY-AM", "NY_AM", date(2026, 10, 6), "high", 105.0, 8, kind, direction, confirm_x, entry)


def result(bias, day_open=100.0):
    return BiasResult(bias, date(2026, 10, 6), levels={"Apertura": day_open})


def test_go_a_favor_del_sesgo_y_en_premium():
    d = ExecutionGate().evaluate(setup("short"), 11, result(Bias.BEARISH))     # venta a 105 sobre la apertura 100
    assert d.allowed and d.verdict == "GO" and all(c.passed for c in d.checks)


def test_no_go_contra_el_sesgo():
    d = ExecutionGate().evaluate(setup("short"), 11, result(Bias.BULLISH))
    assert not d.allowed and d.reason.startswith("Sesgo: Short contra el sesgo Bullish")


def test_sin_sesgo_no_se_opera_salvo_que_se_permita():
    assert "No Bias" in ExecutionGate().evaluate(setup(), 11, result(Bias.NO_BIAS)).reason
    assert ExecutionGate(allow_no_bias=True).evaluate(setup(), 11, result(Bias.NO_BIAS)).allowed
    assert "aún no está calculado" in ExecutionGate().evaluate(setup(), 11, None).reason


def test_pendiente_y_setup_caducado():
    d = ExecutionGate().evaluate(setup(direction=None, kind="pending", entry=None, confirm_x=None), 11, result(Bias.BEARISH))
    assert not d.allowed and d.reason.startswith("Confirmado")
    old = ExecutionGate(max_age_bars=2).evaluate(setup(confirm_x=3), 11, result(Bias.BEARISH))   # hace 7 velas
    assert not old.allowed and old.reason.startswith("Vigente: confirmado hace 7")


def test_premium_discount_solo_en_reversiones():
    cheap = setup("short", entry=99.0)                                         # vende en descuento: mal
    assert "descuento" in ExecutionGate().evaluate(cheap, 11, result(Bias.BEARISH)).reason
    assert ExecutionGate(premium_discount=False).evaluate(cheap, 11, result(Bias.BEARISH)).allowed
    cont = setup("short", kind="continuation", entry=99.0)                     # una continuación no se filtra
    assert ExecutionGate().evaluate(cont, 11, result(Bias.BEARISH)).allowed


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
