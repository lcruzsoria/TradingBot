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
    assert [c.reduce_digit(n) for n in (3, 9, 10, 12, 16)] == [3, 9, 1, 3, 7]       # 444 = 12 = 3; 4444 = 16 = 7


def test_every_zone_has_a_number_between_1_and_9():
    ts = np.arange(srv(2026, 11, 9, 0, 0), srv(2026, 11, 12, 18, 0), 300)     # de lunes a jueves a las 18:00 (luego es viernes, Q0)
    for mode in c.MODES:
        res = c.compute(ts, AHEAD, mode)
        for row in res["rows"]:
            assert row and all(1 <= s["number"] <= 9 for s in row)


def test_tuesday_0220_has_four_digits_at_the_last_level():
    z = zones(srv(2026, 11, 10, 2, 20))
    assert [x["code"] for x in z] == ["2", "22", "222", "2222"]
    assert [x["number"] for x in z] == [2, 4, 6, 8]
    assert c.alignments(z) == []
    micro = zones(srv(2026, 11, 10, 2, 20), mode="dia")                       # el micro suma también el día: 2 + 2 + 2 + 3 = 9
    assert (micro[3]["code"], micro[3]["number"]) == ("2223", 9)
    z = zones(srv(2026, 11, 9, 9, 0))                                         # lunes 09:00: 2133 · 69
    (run,) = c.alignments(z)
    assert (run["n"], run["digit"], run["label"]) == (2, 3, "2133 · 69")


def test_anchor_17_moves_the_sessions_one_hour():
    z = zones(srv(2026, 11, 10, 2, 20), anchor=17)                           # 9 h 20 min tras las 17:00: sesión 2, cuarto 3
    assert [x["code"] for x in z] == ["2", "22", "222", "2223"]
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
    ts = np.arange(srv(2026, 11, 9, 0, 0), srv(2026, 11, 9, 18, 0), 300)
    res = c.compute(ts, AHEAD, anchor_hour=18)
    area = next(a for a in res["areas"] if a["label"] == "2133 · 69")
    assert (area["color"], area["opacity"], area["first"], area["last"]) == ("#A6CFA9", 0.14, "sesion", "cuarto")
    assert (area["x1"] - area["x0"]) == 18                                    # 90 min en velas de 5m


def test_combinaciones_de_tres_zonas_del_mismo_color():
    ts = np.arange(srv(2026, 11, 10, 0, 0), srv(2026, 11, 10, 2, 20), 300)      # martes de la 2.ª semana: London (2), cuarto 2 de 01:30 a 03:00 → 2222
    res = c.compute(ts, AHEAD, anchor_hour=18)
    (tri,) = [t for t in res["triples"] if t["label"] == "2222"]
    assert (tri["n"], tri["color"], tri["first"], tri["last"], tri["number"]) == (4, "#E398A1", "semana", "cuarto", 8)
    assert tri["x1"] - tri["x0"] == 10                                         # activa: lleva 50 min (01:30-02:20)
    assert c.same_color_runs(zones(srv(2026, 11, 9, 9, 0))) == []              # 2133: solo dos zonas seguidas del mismo color
    assert c.same_color_runs(zones(srv(2026, 11, 13, 2, 20))) == []            # viernes en modo semana: solo sesión y cuarto tienen color (2 zonas)
    fri = c.compute(np.arange(srv(2026, 11, 13, 0, 0), srv(2026, 11, 13, 12, 0), 60), AHEAD, "dia")["triples"]   # viernes en modo día: dia amarillo, sesión-cuarto-micro del mismo color
    assert [(t["label"], t["n"], t["first"], t["color"]) for t in fri] == [("222", 3, "sesion", "#E398A1"), ("333", 3, "sesion", "#A6CFA9")]
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    from tradingbot.ui.chart import ChartView
    xs = [ln for ln in res["quarter_lines"] if ln["color"] == "#E398A1"]
    assert sorted(ln["x"] for ln in xs) == [tri["x0"], tri["x0"] + 18]          # 02:20: la combinación 2222 está activa (01:30-03:00): líneas de inicio y fin (las del cuarto coinciden)
    chart = ChartView()
    chart.set_enigma(res["areas"], res["quarter_lines"], res["triples"])
    assert len(chart.enigma._triples) == len(res["triples"]) >= 1
    chart.resize(800, 400)
    chart.grab()                                                               # pinta sin errores


def test_ventanas_de_reversion_asia_q1_ny_am_q3_ny_pm_q3():
    ts = np.arange(srv(2026, 11, 9, 18, 0), srv(2026, 11, 10, 17, 0), 300)     # día de trading del martes, en 5m
    res = c.compute(ts, AHEAD, anchor_hour=18)
    got = [(w["label"], w["same"], w["color"], w["x1"] - w["x0"]) for w in res["windows"]]
    assert got == [("Asia Q1", True, "#B2B6C1", 18), ("NY AM Q3", True, "#A6CFA9", 18), ("NY PM Q3", False, "#A6CFA9", 18)]
    assert res["windows"][1]["x0"] == (srv(2026, 11, 10, 9, 0) - ts[0]) // 300 - 0.5
    fri = np.arange(srv(2026, 11, 12, 18, 0), srv(2026, 11, 13, 17, 0), 300)    # viernes (Q0): no se marca
    assert c.compute(fri, AHEAD)["windows"] == []
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    from tradingbot.ui.chart import ChartView
    chart = ChartView()
    chart.set_enigma(res["areas"], res["quarter_lines"], res["triples"], res["windows"])
    assert len(chart.enigma._windows) == 3
    chart.resize(800, 400)
    chart.grab()


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
    ts = np.arange(srv(2026, 11, 9, 0, 0), srv(2026, 11, 9, 18, 0), 300)
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
    z = zones(srv(2026, 11, 10, 2, 20))                                        # martes 02:20: 222 · 6, 2222 · 8
    assert [x["text"] for x in z] == ["W2 · 2", "Tuesday 22 · 4", "London 222 · 6", "Q2 2222 · 8"]
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


def test_selector_de_timeframes_90m_y_6h_solo_en_enigma369():
    import pandas as pd
    from tradingbot.timeframes import selector_timeframes, display_label
    from tradingbot.skills.feed.datasource import aggregate_candles, normalize_candles
    assert "90m" not in selector_timeframes("crt") and "6h" not in selector_timeframes("") and "7h" in selector_timeframes("crt")
    enig = selector_timeframes("enigma369")
    assert "90m" in enig and "6h" in enig and "7h" not in enig and enig.index("90m") == enig.index("1h") + 1
    assert (display_label("90m"), display_label("6h")) == ("M90", "H6")
    # las velas de 90 m y 6 h empiezan a las 18:00 NY (01:00 del servidor): 01:00, 02:30...
    ts = np.arange(0, 86400 * 2, 900, dtype=np.int64)                                # M15 de dos días (servidor)
    m15 = normalize_candles(pd.DataFrame({"ts": ts, "open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5, "tick_volume": 1}))
    out90 = aggregate_candles(m15, 5400, day_offset=3600)
    assert {int(t % 5400) for t in out90["ts"]} == {3600}                                  # siempre 01:00 + k·90 min
    out6 = aggregate_candles(m15, 21600, day_offset=3600)
    assert {int(t % 86400) // 3600 for t in out6["ts"]} == {1, 7, 13, 19}


def test_lineas_punteadas_del_cuarto_en_curso():
    ts = np.arange(25 * 3600 + 86400 * 2, 25 * 3600 + 86400 * 2 + 6 * 3600 + 20 * 60, 300)     # M5; última vela a las 06:15 NY +...
    lines = c.compute(ts, 25200, "semana", 18)["quarter_lines"]
    assert [ln["kind"] for ln in lines] == ["start", "end"]
    n = len(ts)
    assert lines[0]["x"] < n - 1 < lines[1]["x"]
    assert abs((lines[1]["x"] - lines[0]["x"]) - 90 / 5) < 1e-6                             # 90 min = 18 velas de M5


def test_lineas_punteadas_del_micro_en_modo_dia():
    ts = np.arange(25 * 3600 + 86400 * 2, 25 * 3600 + 86400 * 2 + 3 * 3600 + 600, 60)          # M1
    lines = c.compute(ts, 25200, "dia", 18)["quarter_lines"]
    assert [ln["kind"] for ln in lines] == ["start", "end"]
    assert lines[0]["x"] < len(ts) - 1 < lines[1]["x"]
    assert abs((lines[1]["x"] - lines[0]["x"]) - 22.5) < 1e-6                                  # 22,5 min = 22,5 velas de M1


def test_backtest_de_extremos_en_la_ventana():
    from tradingbot.skills.stats.backtest import Backtest, Group
    from tradingbot.skills.stats.extremos import CONDITIONS, Extremes
    # dos días de un mercado: el máximo en Asia Q1 (combinación de color) y el mínimo en NY AM Q3
    bs = [0] * 16
    bs[0], bs[10] = 6, 6
    day = {"t": [20403, 20404], "wd": [0, 1], "q0": [0, 0], "k": [92, 92], "bs": [[6] * 15 + [2]] * 2, "bn": [[10] * 9, [10] * 9],
           "ba": [2, 2], "bt": [6, 6], "fc": [0, 0], "fa": [0, 0], "ft": [1, 1], "k3": [0, 0], "bm": [[0] * 4] * 2, "bmn": [[0] * 9] * 2,
           "bma": [0, 0], "bmt": [0, 0], "c3": [[0] * 16] * 2, "c3c": [[0] * 16] * 2, "c3a": [[0] * 16] * 2, "c3t": [[0] * 16] * 2, "m": [0, 0]}
    ops = {"i": [0, 0, 1, 1], "d": [0, 1, 0, 1], "e": [1, 2, 3, 4], "x": [1, 2, 3, 4], "s": [1, 3, 1, 3], "q": [1, 3, 1, 3],
           "nw": [2] * 4, "nd": [3] * 4, "ns": [5] * 4, "n": [5, 3, 6, 9], "a": [0] * 4, "c": [3, 0, 3, 0], "g": [1, 0, 0, 0],
           "mi": [0] * 4, "mn": [0] * 4, "ma": [0] * 4, "mc": [0] * 4, "m": [0] * 4}
    raw = {"key": "enigma369:indices", "nombre": "Índices", "tipo": "extremos", "perfil": "enigma369", "perfil_nombre": "Enigma369",
           "cats": {"m": ["NAS100.s"]}, "ops": ops, "dias": day, "patrones": ["Ambos", "Máximo", "Mínimo"],
           "filtros": {"cuentan": "Días que cuentan", "cuentan_sa": "Sin apertura", "todos": "Todos"}}
    g = Group(raw["key"], raw["nombre"], raw)
    x = Extremes(raw)
    sel = x.select()
    combo = sel.condition("Combinación de color hasta el cuarto")
    assert (combo.hits, combo.n, round(combo.base, 4), combo.ctrl) == (2, 4, round(6 / 92, 4), 0.5)   # Asia Q1 lo cumple los dos días: el horario lo explica
    assert sel.condition("Cuarto 3-6-9").hits == 3
    assert x.select("Máximo", "cuentan_sa").n == 1                                    # sin el máximo de la vela de apertura
    assert dict((c, s.hits) for c, s in sel.cells())[(3, 3)] == 2
    assert [k for k, _ in x.split("wd", range(5), "Ambos", "cuentan")] == [0, 1]
    assert set(CONDITIONS) >= {"Micro 3-6-9"}
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    from tradingbot.ui.backtest_dialog import BacktestDialog
    d = BacktestDialog(None, Backtest([g], {}))
    assert d.extremos.isVisibleTo(d) and not d.curve_card.isVisibleTo(d)
    d.extremos.by_day.click(1)
    assert d.days == {1} and d.extremos.tiles["days"].value.text() == "1"
    d.set_pattern("Mínimo")
    assert len(d.extremos.cells.rows) == 16
