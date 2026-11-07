"""Skill Enigma369: cuartos → números 1-9, alineaciones 3-6-9, áreas del gráfico y franjas."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import datetime, timezone

import numpy as np
import pytest

from tradingbot.config import STRATEGY_SKILLS_OFF, STRATEGY_SKILLS_ON, STRATEGY_TIMEFRAMES, strategy_skills
from tradingbot.skills.enigma369 import cuartos as c

AHEAD = 7 * 3600                      # servidor = Nueva York + 7 h


def srv(y, m, d, h, mi):
    return int(datetime(y, m, d, h, mi, tzinfo=timezone.utc).timestamp()) + AHEAD


def zones(ts, anchor=18, mode="semana"):
    return c.last_zones([ts], AHEAD, mode, anchor)


def test_digit_sum_reduces_to_one_digit():
    assert [c.reduce_digit(n) for n in (3, 9, 10, 12)] == [3, 9, 1, 3]       # 444 = 12 = 3


def test_every_zone_has_a_number_between_1_and_9():
    ts = np.arange(srv(2026, 11, 9, 0, 0), srv(2026, 11, 12, 18, 0), 300)     # de lunes a jueves a las 18:00 (luego es viernes, Q0)
    for mode in c.MODES:
        res = c.compute(ts, AHEAD, mode)
        for row in res["rows"]:
            assert row and all(1 <= s["number"] <= 9 for s in row)


def test_tuesday_0220_is_222_66():
    z = zones(srv(2026, 11, 10, 2, 20))
    assert [x["code"] for x in z] == ["2", "22", "222", "222"]
    assert [x["number"] for x in z] == [2, 4, 6, 6]
    (run,) = c.alignments(z)
    assert (run["n"], run["digit"], run["label"]) == (2, 2, "222 · 66")


def test_anchor_17_moves_the_sessions_one_hour():
    z = zones(srv(2026, 11, 10, 2, 20), anchor=17)                           # 9 h 20 min tras las 17:00: sesión 2, cuarto 3
    assert [x["code"] for x in z] == ["2", "22", "222", "223"]
    assert c.alignments(z) == []


def test_friday_weekend_and_fifth_week_are_yellow_q0_without_numbers():
    for ts in (srv(2026, 11, 13, 2, 20), srv(2026, 11, 12, 18, 30), srv(2026, 11, 14, 10, 0), srv(2026, 11, 15, 10, 0)):   # vie, jueves 18:30 (ya es viernes), sáb, dom
        z = zones(ts)
        assert [x["number"] for x in z] == [0, 0, 0, 0] and z[1]["digit"] == 0 and c.alignments(z) == []
        assert all(x["digit"] > 0 for x in z[2:])                              # sesión y cuarto conservan su color 1-4
    assert [zones(srv(2026, 11, d, 2, 20))[1]["text"] for d in (13, 14, 15)] == ["Friday", "Saturday", "Sunday"]
    assert zones(srv(2026, 11, 13, 2, 20))[2]["text"] == "London"
    assert zones(srv(2026, 11, 8, 18, 30))[1]["digit"] == 1                    # domingo 18:30 ya es lunes
    fifth = zones(srv(2026, 11, 30, 10, 0))                                    # lunes 30: 5.ª semana
    assert fifth[0]["digit"] == 0 and all(x["number"] == 0 for x in fifth)
    assert c.DEFAULT_COLORS[0] == "#EFD9A8"


def test_alignment_needs_same_digit_and_critical_numbers():
    ts = srv(2026, 11, 11, 9, 50)                                             # 233 / 334: sin alineación
    assert c.alignments(zones(ts)) == []
    z = [dict(layer="a", digit=3, number=3), dict(layer="b", digit=3, number=6), dict(layer="c", digit=3, number=9), dict(layer="d", digit=3, number=4)]
    assert [(r["n"], c.OPACITY[r["n"]]) for r in c.alignments([{**x, "code": "x"} for x in z])] == [(3, 0.28)]


def test_areas_follow_the_aligned_span_and_use_the_zone_color():
    ts = np.arange(srv(2026, 11, 10, 0, 0), srv(2026, 11, 10, 6, 0), 300)
    res = c.compute(ts, AHEAD, anchor_hour=18)
    area = next(a for a in res["areas"] if a["label"] == "222 · 66")
    assert (area["color"], area["opacity"], area["first"], area["last"]) == ("#E398A1", 0.14, "sesion", "cuarto")
    assert (area["x1"] - area["x0"]) == 18                                    # 90 min en velas de 5m


def test_day_micro_mode_has_four_rows_and_micro_segments():
    ts = np.arange(srv(2026, 11, 10, 0, 0), srv(2026, 11, 10, 3, 0), 60)
    res = c.compute(ts, AHEAD, "dia")
    assert res["layers"] == ("dia", "sesion", "cuarto", "micro")
    assert len(res["rows"][3]) >= 8                                           # un micro cada 22,5 min


def test_profile_wiring():
    skills = strategy_skills([{"type": "pattern"}, {"type": "tbr"}, {"type": "bias"}, {"type": "feed"}], "enigma369")
    assert [s["type"] for s in skills] == ["bias", "feed", "enigma369"]
    assert STRATEGY_TIMEFRAMES["enigma369"] == "5m" and "enigma369" in STRATEGY_SKILLS_ON and "enigma369" in STRATEGY_SKILLS_OFF


def test_chart_paints_areas_and_stripes_render():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    from tradingbot.ui.chart import ChartView
    from tradingbot.ui.enigma_stripes import EnigmaStripes
    ts = np.arange(srv(2026, 11, 10, 0, 0), srv(2026, 11, 10, 6, 0), 300)
    res = c.compute(ts, AHEAD, anchor_hour=18)
    chart = ChartView()
    chart.set_enigma(res["areas"])
    assert chart.enigma_item_count == len(res["areas"]) >= 1
    chart.set_enigma([])
    assert chart.enigma_item_count == 0
    stripes = EnigmaStripes()
    now = c.last_zones(ts[-1:], AHEAD, "semana", 18)
    stripes.set_data({"available": True, "mode": "semana", "now": now, "alignments_now": c.alignments(now), **res}, {"semana": "Semana"})
    assert stripes.rows.segment_count == sum(len(r) for r in res["rows"])
    stripes.set_data({"available": False, "mode": "dia", "reason": "solo índices USA"}, {})
    assert stripes.rows.segment_count == 0 and stripes.buttons["dia"].isChecked()


def test_futures_weekend_gap_like_the_indicator():
    """MNQ1! en M5 (captura del indicador): el jueves a las 18:05 empieza Friday (Asia), amarillo, con la semana 4 (azul); sin barras
    el fin de semana; el domingo a las 18:00 empieza Asia del lunes, gris, ya en la semana 1 de noviembre."""
    start = zones(srv(2026, 10, 29, 18, 5))
    assert [x["digit"] for x in start] == [4, 0, 1, 1] and start[1]["text"] == "Friday" and start[2]["text"] == "Asia"
    assert zones(srv(2026, 10, 29, 17, 55))[1]["digit"] == 4                         # justo antes: aún jueves
    assert zones(srv(2026, 10, 30, 17, 55))[2]["text"] == "NY PM"                    # último tramo del viernes
    monday = zones(srv(2026, 11, 1, 18, 5))
    assert [x["digit"] for x in monday[:3]] == [1, 1, 1] and monday[2]["text"] == "Asia 111 · 3" and monday[0]["text"] == "W1 · 1"


def test_zone_labels_carry_the_period_reference_and_number():
    z = zones(srv(2026, 11, 10, 2, 20))                                        # martes 02:20: 222 · 66
    assert [x["text"] for x in z] == ["W2 · 2", "Tuesday 22 · 4", "London 222 · 6", "Q2 222 · 6"]
    assert [zones(srv(2026, 11, 3 + 7 * w, 10, 0))[0]["text"][:2] for w in range(3)] == ["W1", "W2", "W3"]
    micro = zones(srv(2026, 11, 10, 2, 20), mode="dia")
    assert micro[3]["text"].startswith("M") and micro[3]["layer"] == "micro"


def test_q0_numeros_de_referencia_y_aviso_telegram():
    import calendar
    from tradingbot.skills.telegram import messages
    ts = calendar.timegm((2027, 1, 1, 7 + 6, 0, 0))                      # viernes 1 ene 2027, 06:00 NY: día Q0
    from tradingbot.skills.enigma369 import cuartos
    now = cuartos.last_zones([ts], 25200, "semana", 18)
    assert all(z["number"] == 0 for z in now) and all(1 <= z["ref_number"] <= 9 for z in now)
    refs = cuartos.alignments(now, "ref_number")
    p = {"symbol": "NAS100.s", "timeframe": "M5", "now": now, "alignments_now": [], "ref_alignments_now": refs}
    text = messages.enigma(p)
    assert "Enigma369" in text and "Números de referencia" in text


def test_alineaciones_grandes_con_mes_y_aviso_previo():
    from tradingbot.skills.telegram import messages
    from datetime import datetime
    found = c.upcoming_big(datetime(2026, 12, 22, 9, 0), 48)
    assert [(x["start"], x["n"]) for x in found] == [(datetime(2026, 12, 22, 18), 3), (datetime(2026, 12, 23, 6), 4), (datetime(2026, 12, 23, 12), 3)]
    assert found[1]["text"].startswith("Mes 3")
    assert [x["start"] for x in c.upcoming_big(datetime(2026, 11, 17, 9, 0), 48)] == [datetime(2026, 11, 18, 6)]   # sin mes: semana-día-sesión
    assert c.upcoming_big(datetime(2027, 1, 1, 0, 0), 24) == []                                                     # 1 ene 2027: Q0
    assert "Madrid" in messages.enigma_ahead(found[1], 90)
