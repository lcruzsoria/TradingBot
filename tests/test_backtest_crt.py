"""Grupos CRT-C2 de la ventana Backtest: filtros por LTF, modelo de entrada y objetivo, zonas TBR y botones."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from tradingbot.skills.stats.backtest import CRT_ZONES, Group, load                  # noqa: E402

DAY = 1440


def raw_group() -> dict:
    """Seis operaciones CRT a mano: mercado (m), LTF (l), entrada (n), FVG de MTF tocados (t: 1 M15), TBR (z), R neto (r)."""
    e0 = int(pd.Timestamp("2025-03-03 03:00").value // 10**9 // 60)               # minutos desde 1970 (hora NY)
    n = 6
    return {"key": "crt:indices", "nombre": "Índices", "tipo": "crt", "perfil": "crt", "perfil_nombre": "CRT",
            "cats": {"m": ["NAS100.s", "SP500.s"], "o": ["objetivo", "stop", "breakeven", "tiempo"], "z": list(CRT_ZONES), "p": ["CRT"]},
            "patrones": ["CRT"], "filtros": {"5:1": "M5 · 1", "5:2": "M5 · 2", "3:1": "M3 · 1"},
            "ops": {"m": [0, 0, 1, 1, 0, 1], "l": [5, 5, 5, 3, 5, 5], "n": [1, 1, 1, 1, 2, 1], "t": [1] * 6,
                    "z": [0, 3, 1, 3, 2, 3], "d": [0, 1, 0, 1, 0, 1], "o": [0, 1, 0, 1, 0, 1], "h": [3, -1, 4, -1, 3, 4], "q": [2] * 6,
                    "e": [e0 + i * DAY for i in range(n)], "x": [e0 + i * DAY + 60 for i in range(n)],
                    "r": [1.9, -1.0, 1.9, -1.0, 1.9, -1.0], "k": [0.1] * n, "rk": [0.2] * n, "v": [10] * n},
            "datos": [{"mercado": "NAS100.s · M5", "velas M15": 100, "desde (NY)": "2018-09-10", "hasta (NY)": "2026-10-30"},
                      {"mercado": "NAS100.s · M3", "velas M15": 100, "desde (NY)": "2024-01-04", "hasta (NY)": "2026-10-30"}]}


def test_el_grupo_crt_filtra_por_ltf_entrada_y_tf_del_fvg():
    g = Group("crt:indices", "Índices", raw_group())
    assert g.is_crt and not g.is_calendar
    n = lambda **kw: len(g.view("CRT", "5:1", crt=(kw.get("mtf", 0), kw.get("ltf", 5), kw.get("entry", 1))).main)        # noqa: E731
    assert n() == 4                                   # M5, entrada 1: operaciones 0, 1, 2 y 5
    assert n(ltf=3) == 1 and n(entry=2) == 1
    assert g.crt_mask(0, 5, 2).sum() == 1


def test_el_grupo_crt_separa_las_zonas_tbr_y_el_rendimiento_en_todos_los_casos():
    g = Group("crt:indices", "Índices", raw_group())
    v = g.view("CRT", "5:1", crt=(0, 5, 1))
    zones = {k: o.stats().get("n", 0) for k, o in v.zones}
    assert zones == {"Asia": 1, "London": 1, "NY Open": 0, "Fuera de TBR": 1 + 1, "Dentro de alguna TBR": 2, "Todas": 4}
    assert sum(zones[z] for z in CRT_ZONES) == zones["Todas"]                        # no se pierde ninguna operación
    assert v.extra["mtf"] == []                                                      # CRT-C2 no usa FVG de MTF
    near = {k: o.stats().get("n", 0) for k, o in v.extra["cercania"]}                 # ops. 0, 1, 2 y 5 (M5, entrada 1): h = 3, -1, 4, 4
    assert near == {"±15 min de la hora en punto": 3, "Resto de horas": 1, "En TBR · ±15 min de la hora": 2, "En TBR · resto": 0,
                    "Fuera de TBR · ±15 min de la hora": 1, "Fuera de TBR · resto": 1}
    assert {k: o.stats().get("n", 0) for k, o in v.extra["horas"]} == {"03:00": 1, "04:00": 2}
    assert [k for k, _ in v.filters] == ["5:1", "5:2", "3:1"]
    assert v.main.stats()["total"] == pytest.approx(1.9 - 1.0 + 1.9 - 1.0)
    assert sorted(m for m, _ in v.markets) == ["NAS100.s", "SP500.s"]
    assert g.dates_of(3) == ("2024-01-04", "2026-10-30") and g.period_of(5) == "2018-2026"


def test_el_grupo_crt_separa_los_tres_objetivos():
    raw = raw_group()
    for col, extra in (("m", [0, 0]), ("l", [5, 5]), ("n", [1, 1]), ("t", [1, 1]), ("z", [0, 0]), ("d", [0, 0]), ("o", [0, 1]), ("h", [3, 3]),
                       ("e", [raw["ops"]["e"][0] + 10, raw["ops"]["e"][0] + 20]), ("x", [raw["ops"]["x"][0] + 10, raw["ops"]["x"][0] + 20]),
                       ("r", [0.9, 3.4]), ("k", [0.1, 0.1]), ("rk", [0.2, 0.2]), ("v", [3, 30]), ("q", [1, 3])):
        raw["ops"][col] = list(raw["ops"][col]) + extra                              # una operación con objetivo 1R y otra con el extremo de C1
    g = Group("crt:indices", "Índices", raw)
    main = lambda q: g.view("CRT", "", crt=(0, 5, 1, "Todas", "Todas", q)).main                # noqa: E731
    assert (len(main(2)), len(main(1)), len(main(3))) == (4, 1, 1)
    assert main(1).stats()["total"] == pytest.approx(0.9) and main(3).stats()["total"] == pytest.approx(3.4)
    assert len(g.view("CRT", "", crt=(0, 5, 1)).main) == 4                           # por defecto, 2R
    old = raw_group()
    del old["ops"]["q"]                                                                # un fichero anterior a los objetivos: todo es 2R
    assert len(Group("crt:indices", "Índices", old).view("CRT", "", crt=(0, 5, 1, "Todas", "Todas", 2)).main) == 4


def test_el_grupo_crt_filtra_por_tbr_y_por_cercania_a_la_hora_en_punto():
    g = Group("crt:indices", "Índices", raw_group())
    n = lambda tbr="Todas", near="Todas": len(g.view("CRT", "", crt=(0, 5, 1, tbr, near)).main)        # noqa: E731
    assert (n(), n("Dentro de TBR"), n("Fuera de TBR"), n("Asia"), n("London"), n("NY Open")) == (4, 2, 2, 1, 1, 0)
    assert (n(near="±15 min de la hora"), n(near="Resto")) == (3, 1)
    assert n("Dentro de TBR", "±15 min de la hora") == 2 and n("Fuera de TBR", "±15 min de la hora") == 1
    v = g.view("CRT", "", crt=(0, 5, 1, "London", "Todas"))                          # la tabla de zonas no lleva el filtro de TBR
    assert {k: o.stats().get("n", 0) for k, o in v.zones}["Asia"] == 1 and len(v.main) == 1
    assert len(g.view("CRT", "", crt=(0, 5, 1)).main) == 4                           # una tupla corta se completa con los valores por defecto


def test_zona_tbr_de_la_hora_de_entrada():
    import exportar_backtest_crt as ex
    hours = pd.to_datetime(["2025-03-03 21:00", "2025-03-03 00:00", "2025-03-03 03:30", "2025-03-03 04:59", "2025-03-03 05:00",
                            "2025-03-03 10:00", "2025-03-03 11:59", "2025-03-03 12:00", "2025-03-03 19:59"])
    got = ex.tbr_zone(pd.Series(hours)).tolist()
    assert got == ["Asia", "Fuera de TBR", "London", "London", "Fuera de TBR", "NY Open", "NY Open", "Fuera de TBR", "Fuera de TBR"]
    near = ex.near_hour(pd.Series(pd.to_datetime(["2025-03-03 02:44", "2025-03-03 02:45", "2025-03-03 03:00", "2025-03-03 03:15",
                                                    "2025-03-03 03:16", "2025-03-03 23:50", "2025-03-03 00:10"])))
    assert near.tolist() == [-1, 3, 3, 3, -1, 0, 0]                              # 03:00 vale de 02:45 a 03:15; 23:50 es la hora 0


def test_la_ventana_crt_con_los_datos_reales_y_sus_botones():
    from PySide6.QtWidgets import QApplication
    from tradingbot.ui.backtest_dialog import BacktestDialog
    QApplication.instance() or QApplication([])
    bt = load()
    assert bt.group("crt:indices") is not None and bt.group("crt:forex") is not None
    dlg = BacktestDialog(None, bt)
    dlg.set_group("crt:indices")
    assert dlg.profile_key == "crt" and list(dlg.group_btns) == ["crt:indices", "crt:forex"]
    assert dlg.pattern_labelled.itemAt(0).widget().isHidden() and not dlg.crt_layouts[0].itemAt(0).widget().isHidden()
    assert (dlg.crt_mtf, dlg.crt_ltf, dlg.crt_entry) == (0, 3, 1)             # por defecto M3 y la orden límite
    g = bt.group("crt:indices")
    first = dlg.blocks["n"].value.text()
    assert first != "-" and len(dlg.by_filter.rows) == 4 and len(dlg.by_mtf.rows) == 0
    assert [r[0].text() for r in dlg.by_zone.rows] == list(CRT_ZONES) + ["Dentro de alguna TBR", "Todas"]
    for ltf in (5, 3):                                                              # los 2 LTF y los 2 modelos de entrada se pintan
        dlg.set_crt_ltf(ltf)
        for entry in (1, 2):
            dlg.set_crt_entry(entry)
            n = len(g.view("CRT", "", crt=dlg.crt).main)
            assert n and dlg.blocks["n"].value.text().replace(".", "") == str(n)
            assert dlg.crt_btns["ltf"][str(ltf)].isChecked() and dlg.crt_btns["entry"][str(entry)].isChecked()
    dlg.set_crt_ltf(5)
    dlg.set_crt_entry(1)
    counts = {}
    for target in (1, 2, 3):                                                        # los tres objetivos son tres backtests
        dlg.set_crt_target(target)
        counts[target] = int(dlg.blocks["n"].value.text().replace(".", ""))
        assert dlg.crt_btns["target"][str(target)].isChecked()
        assert counts[target] == len(g.view("CRT", "", crt=dlg.crt).main)
    assert counts[1] and counts[2] and counts[3]
    dlg.set_crt_target(2)
    total = int(dlg.blocks["n"].value.text().replace(".", ""))
    dlg.set_crt_tbr("Dentro de TBR")                                                # solo las entradas dentro de alguna TBR
    inside = int(dlg.blocks["n"].value.text().replace(".", ""))
    dlg.set_crt_near("±15 min de la hora")                                          # y a ±15 min de una hora en punto
    both = int(dlg.blocks["n"].value.text().replace(".", ""))
    assert 0 < both < inside < total and dlg.crt_btns["tbr"]["Dentro de TBR"].isChecked() and dlg.crt_btns["near"]["±15 min de la hora"].isChecked()
    assert [r[0].text() for r in dlg.by_zone.rows][-1] == "Todas" and len(dlg.by_near.rows) == 6 and dlg.by_round.rows
    dlg.set_crt_tbr("Todas")
    dlg.set_crt_near("Todas")
    dlg.set_crt_ltf(3)
    dlg.set_group("crt:forex")                                                      # otro grupo de mercados: se queda la selección
    assert dlg.crt_ltf == 3 and dlg.group_key == "crt:forex" and dlg.compare.rows
    assert "EURUSD" in "".join(r[0].text() for r in dlg.by_market.rows)
    dlg.by_year.click(2024)
    assert dlg.years == {2024} and dlg.blocks["n"].value.text() != "-"
    dlg.set_group("puprime:indices")                                                # los patrones vuelven con sus botones
    assert not dlg.pattern_labelled.itemAt(0).widget().isHidden() and dlg.crt_layouts[0].itemAt(0).widget().isHidden()
    assert dlg.profile_key == "puprime" and dlg.by_mtf.isHidden() and dlg.crt_funnel.isHidden()
