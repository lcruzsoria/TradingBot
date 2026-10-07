"""Humo de la interfaz sin pantalla (QT_QPA_PLATFORM=offscreen) con datos sintéticos."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from tradingbot.skills.feed.datasource import Quote
from tradingbot.ui.fmt import hace
from tradingbot.ui.widgets import MarketsGrid


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def test_hace():
    assert hace(0) == "hace 0 s" and hace(75) == "hace 1 min"
    assert hace(3 * 3600 + 19 * 60) == "hace 3 h 19 min" and hace(7200) == "hace 2 h"


def test_mercados_marca_cerrado_y_no_disponible(qapp):
    grid = MarketsGrid(["EURUSD", "GER40", "RARO"])
    now = 1_700_000_000
    grid.set_quotes({"EURUSD": Quote("EURUSD", 1.1, 1.1001, now),
                     "GER40": Quote("GER40", 25000.0, 25001.0, now - 3600),
                     "RARO": None})
    assert grid.cards["EURUSD"].property("stale") == "false"
    assert grid.cards["GER40"].property("stale") == "true" and not grid.cards["GER40"].badge.isHidden()
    assert "No disponible" in grid.cards["RARO"].spread.text() and "no disponible" in grid.cards["RARO"].toolTip()
    grid.set_selected("eurusd")
    assert grid.cards["EURUSD"].property("selected") == "true"
    assert grid.cards["GER40"].property("selected") == "false"


def test_anillo_clic_en_skill_y_en_hueco_libre(qapp):
    from PySide6.QtCore import QPointF
    from tradingbot.core import SkillInfo
    from tradingbot.ui.ring import RingView

    ring = RingView()
    ring.resize(392, 330)
    ring.set_skills([SkillInfo("cortex", "Cortex", "", "center", (), ()),
                     SkillInfo("feed", "Feed", "", 0, (), ()),
                     SkillInfo("watch", "Watch", "", "aux1", (), ())])
    _, pos = ring._geometry()
    assert ring._hit(QPointF(*pos["center"][:2]))[1] == "cortex"
    assert ring._hit(QPointF(*pos[0][:2]))[1] == "feed"
    assert ring._hit(QPointF(*pos["aux1"][:2]))[1] == "watch"
    assert ring._hit(QPointF(*pos[3][:2])) == (3, None)          # hueco libre del anillo
    assert ring._hit(QPointF(*pos["aux2"][:2])) == (None, None)  # satélite sin skill: no se puede pulsar


def test_anillo_estado_y_mensajes(qapp):
    from tradingbot.core import SkillInfo
    from tradingbot.ui.ring import RingView, describe_skill

    ring = RingView()
    ring.set_skills([SkillInfo("feed", "Feed", "Carga velas", 0, ("feed.load",), ("candles.loaded",)),
                     SkillInfo("bias", "Bias", "Sesgo", 1, ("candles.loaded",), ("bias.updated",))])
    ring.update_state({"key": "feed", "state": "error", "handled": 3, "caption": "", "note": "ValueError: x"})
    ring.flash("feed", ["bias"], "candles.loaded")
    assert ring.views["feed"].state == "error" and ring.last_in["bias"] == "candles.loaded"
    assert ring.last_out["feed"] == "candles.loaded"
    html = describe_skill(ring.infos["feed"], ring.views["feed"], None, "candles.loaded")
    assert "con error" in html and "ValueError: x" in html and "feed.load" in html
