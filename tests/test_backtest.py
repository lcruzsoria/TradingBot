"""Skill Stats (sesión y backtest) y ventana Backtest."""
import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import date, datetime
from types import SimpleNamespace

import pytest

from tradingbot.core import Event, EventBus, Services, SkillManager
from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.cortex.order import Order
from tradingbot.skills.setup.positions import Closed
from tradingbot.skills.stats.backtest import BOT_FILTER, DEFAULT_FILE, Backtest, Group, load, summarize, verdict
import tradingbot.skills  # noqa: F401

ORDER = Order("NAS100", "15m", "long", "Continuación", "continuacion", "London", date(2026, 10, 6), 105.0, 95.0, 100.0, 105.0,
              95.0, 115.0, "Bullish", 3.0, "GO", entry_ts=1_000_000, close_ts=1_086_400)

def _min(y, mo, d, h):
    """Minutos desde 1970 de una hora de Nueva York (así guarda el backtest la entrada y el cierre)."""
    return int((datetime(y, mo, d, h) - datetime(1970, 1, 1)).total_seconds() // 60)


# Cinco operaciones a mano. «Lo que opera el bot» (no en contra del sesgo y sin solaparse con otra GO): 1, 4 y 5.
#   1 lun 02-03-2020 03h Continuación largo London  +2 R  a favor
#   2 mar 03-03-2020 10h Reversión    corto NY Open -1 R  en contra
#   3 lun 03-05-2021 03h Continuación largo London  -1 R  sin sesgo, solapada con otra GO (bit 2)
#   4 mar 04-05-2021 21h Continuación corto Asia    +2 R  a favor
#   5 lun 03-01-2022 10h Reversión    largo NY Open -1 R  a favor, solapada solo con otra cualquiera (bit 1)
ENTRIES = [(2020, 3, 2, 3), (2020, 3, 3, 10), (2021, 5, 3, 3), (2021, 5, 4, 21), (2022, 1, 3, 10)]
GROUP = {"key": "indices", "nombre": "Índices americanos", "tipo": "patrones", "actualizado": "2026-10-18",
         "datos": [{"mercado": "NAS100.r", "velas M15": 1000, "desde (NY)": "2018-09-10", "hasta (NY)": "2026-10-16",
                    "TBR evaluadas": 60}],
         "cats": {"m": ["DJ30.r", "NAS100.r"], "p": ["Continuación", "Reversión"], "z": ["Asia", "London", "NY Open"],
                  "o": ["objetivo", "stop", "tiempo"], "s": ["a favor", "en contra", "sin sesgo"]},
         "ops": {"m": [1, 1, 0, 1, 0], "p": [0, 1, 0, 0, 1], "z": [1, 2, 1, 0, 2], "d": [0, 1, 0, 1, 0], "o": [0, 1, 1, 0, 1],
                 "s": [0, 1, 2, 0, 0], "f": [0, 0, 2, 0, 1], "e": [_min(*e) for e in ENTRIES],
                 "x": [_min(*e) + 300 for e in ENTRIES], "v": [20, 4, 4, 20, 4],
                 "r": [2.0, -1.0, -1.0, 2.0, -1.0], "k": [0.1, 0.1, 0.1, 0.1, 0.1],
                 **{c: [2.0, -1.0, -1.0, 2.0, -1.0] for c in ("tp1", "tp15", "tp2", "tp25", "tp3", "h12", "h48")},
                 "mae": [0.5, 1.0, 1.0, 0.5, 1.0], "mfe": [2.0, 0.3, 0.3, 2.0, 0.3], "rk": [0.2] * 5}}


def stats_skill(env=None):
    bus = EventBus()
    out = []
    bus.subscribe("test", "stats.*", out.append)
    skill = SkillManager(bus, Services(None, None, {"app": {}}, env or EnvConfig()), [{"type": "stats"}]).skills["stats"]
    return skill, out


def test_la_skill_va_en_el_satelite_aux3_y_lleva_la_sesion():
    skill, out = stats_skill()
    assert skill.slot == "aux3" and skill.title == "Stats"
    skill.on_start()
    assert {e.topic for e in out} == {"stats.session", "stats.backtest"}
    skill.handle(Event("cortex.decision", {"decision": SimpleNamespace(allowed=True)}, "cortex"))
    skill.handle(Event("setup.executed", {"order": ORDER}, "setup"))
    assert skill.caption == "1 abierta(s)"
    skill.handle(Event("setup.closed", {"order": ORDER, "closed": Closed("objetivo", 115.0, 1_010_000, 2.0, 9.5)}, "setup"))
    last = [e for e in out if e.topic == "stats.session"][-1].payload["stats"]
    assert (last.go, len(last.done), last.total_r) == (1, 1, 2.0) and skill.caption == "1 ops · +2.00 R"
    assert last is not skill.stats and last.trades[0] is not skill.stats.trades[0]        # copia: la lee otro hilo
    skill.handle(Event("stats.reset", {}, "ui"))
    assert skill.stats.trades == [] and skill.stats.go == 0


def test_backtest_que_falta_se_avisa_sin_romper_la_skill(tmp_path):
    skill, out = stats_skill(EnvConfig(parse(f"STATS_BACKTEST_FILE={tmp_path / 'no.json'}")))
    skill.on_start()
    bt = [e for e in out if e.topic == "stats.backtest"][-1].payload
    assert bt["backtest"] is None and "exportar_backtest" in bt["error"] and skill.caption == "sin backtest"


def test_cifras_y_seleccion_por_anios_y_horas(tmp_path):
    path = tmp_path / "bt.json"
    path.write_text(json.dumps({"generado": "x", "grupos": [GROUP], "comparativa": {}}), encoding="utf-8")
    g = load(path).group("indices")
    s = summarize([2.0, -1.0, -1.0, 2.0])
    assert (s["n"], s["wr"], s["total"], s["pf"], s["dd"], s["streak"]) == (4, 50.0, 2.0, 2.0, -2.0, 2)
    bot = g.view("Ambos", BOT_FILTER)
    assert g.period == "2018-2026" and bot.main.stats()["n"] == 3 and bot.main.stats()["total"] == 3.0
    assert [(z, len(o)) for z, o in bot.zones] == [("Asia", 1), ("London", 1), ("NY Open", 1)]
    assert [(d, len(o)) for d, o in bot.days][:2] == [("lunes", 2), ("martes", 1)]
    assert g.view("Ambos", "sin filtro de sesgo").main.stats()["n"] == 5
    assert g.view("Reversión", "en contra del sesgo").main.stats()["total"] == -1.0
    # años: la selección filtra todo menos su propio histograma
    y2020 = g.view("Ambos", BOT_FILTER, years={2020})
    assert len(y2020.main) == 1 and [y for y, _ in y2020.years] == [2020, 2021, 2022]
    assert [(f, len(o)) for f, o in y2020.filters][:3] == [(BOT_FILTER, 1), ("a favor del sesgo (Cortex)", 1),
                                                         ("sin filtro de sesgo", 2)]
    h10 = g.view("Ambos", BOT_FILTER, hours={10})
    assert h10.main.stats()["total"] == -1.0 and [y for y, _ in h10.years] == [2022] and [h for h, _ in h10.hours] == [3, 10, 21]
    assert len(g.view("Ambos", BOT_FILTER, years={2020}, hours={10}).main) == 0
    assert [(m, g, len(o)) for m, g, o in load(path).compare(BOT_FILTER, years={2021})] == [
        ("NAS100.r", "Índices americanos", 1), ("DJ30.r", "Índices americanos", 0)]
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        load(path)
    assert verdict(-2.5, -0.1)[1] == -1 and verdict(2.1, 0.1)[1] == 1 and verdict(-1.0, -0.05)[1] == 0


@pytest.mark.skipif(not DEFAULT_FILE.exists(), reason="sin backtest.json.gz")
def test_ventana_backtest_con_el_resumen_real():
    from PySide6.QtWidgets import QApplication
    from tradingbot.ui.backtest_dialog import BacktestDialog
    QApplication.instance() or QApplication([])
    bt = load()
    assert [g.key for g in bt.groups] == ["puprime:indices", "puprime:forex", "puprime:oro", "puprime:cripto", "metaquotes:indices",
                                          "metaquotes:forex", "metaquotes:oro", "calendario"]
    assert [p for p, _ in bt.profiles] == ["puprime", "metaquotes", "calendario"]
    dlg = BacktestDialog(None, bt)
    assert dlg.group_key == "puprime:indices" and dlg.profile_key == "puprime" and dlg.blocks["n"].value.text() != "-"
    assert dlg.by_market.rows and dlg.compare.rows and dlg.by_year.values
    for g in bt.groups:                                                            # todas las combinaciones se pintan
        dlg.set_group(g.key)
        assert list(dlg.pattern_btns) == g.patterns and list(dlg.filter_btns) == list(g.filters)
        for p in g.patterns:
            dlg.set_pattern(p)
            for f in g.filters:
                dlg.set_filter(f)
                assert len(dlg.by_filter.rows) == len(g.all_filters) and dlg.blocks["n"].value.text() != "-"
    dlg.set_group("calendario")                                                    # su propio patrón, sin zonas ni embudo
    assert dlg.pattern == "Calendario" and dlg.by_zone.isHidden() and dlg.funnel.isHidden() and dlg.compare.isHidden()
    assert [r[0].text() for r in dlg.by_day.rows][0] == "Lunes" and "largos a hora fija" in dlg.subtitle.text()
    dlg.set_group("puprime:indices")
    assert dlg.pattern == "Ambos" and not dlg.by_zone.isHidden()
    total = dlg.blocks["n"].value.text()                                          # pulsar un año recalcula todo
    dlg.by_year.click(2024)
    assert dlg.years == {2024} and dlg.blocks["n"].value.text() != total and not dlg.selection_bar.isHidden()
    assert "2024" in dlg.selection_label.text() and dlg.by_year.clear_btn.isVisibleTo(dlg) and dlg.compare.rows
    dlg.by_hour.click(dlg.by_hour.keys[0])
    assert dlg.hours == {dlg.by_hour.keys[0]} and "no cambia" in dlg.funnel.note.text()
    dlg.by_year.click(2024)                                                         # otro clic lo quita
    assert dlg.years == set() and dlg.hours
    dlg.clear_selection()
    assert dlg.blocks["n"].value.text() == total and dlg.selection_bar.isHidden()
    dlg.set_group("calendario")                                                    # en Calendario la hora es la de entrada
    bot_hour = dlg.blocks["mean"].value.text()
    dlg.by_hour.click(5)
    assert dlg.blocks["mean"].value.text() != bot_hour and "sustituye" in dlg.selection_label.text()
    dlg.set_group("puprime:indices")
    assert not dlg.hours                                                           # otro grupo: selección limpia
    dlg.set_backtest(None, "falta el fichero")
    assert dlg.empty.text() == "falta el fichero" and dlg.scroll.isHidden()


def test_ventana_backtest_con_datos_minimos():
    from PySide6.QtWidgets import QApplication
    from tradingbot.ui.backtest_dialog import BacktestDialog
    QApplication.instance() or QApplication([])
    dlg = BacktestDialog(None, Backtest([Group("indices", "Índices americanos", GROUP)], {}))
    assert dlg.blocks["n"].value.text() == "3" and dlg.blocks["wr"].value.text() == "66.7 %"
    assert "Sin ventaja clara" in dlg.verdict.text() and dlg.selection_bar.isHidden()
    assert [r[0].text() for r in dlg.by_zone.rows] == ["Asia", "London", "NY Open"]
    assert dlg.by_year.keys == [2020, 2021, 2022]
    dlg.by_year.click(2021)
    assert dlg.blocks["n"].value.text() == "1" and dlg.blocks["total"].value.text() == "+2 R"
    dlg.by_year.click(2020)                                                          # un solo año: sustituye al anterior
    assert dlg.years == {2020} and dlg.blocks["n"].value.text() == "1" and dlg.blocks["total"].value.text() == "+2 R"
    dlg.by_hour.click(10)                                                            # la de 2020 a las 10 va en contra
    assert dlg.blocks["n"].value.text() == "-" and "Sin operaciones" in dlg.verdict.text()
    dlg.by_year.cleared.emit()                                                       # «Quitar» del histograma de años
    assert dlg.years == set() and dlg.blocks["n"].value.text() == "1"
    dlg.by_hour.click(3)                                                             # otra hora sustituye a las 10
    assert dlg.hours == {3} and dlg.blocks["n"].value.text() == "1"
    dlg.by_hour.click(3)                                                             # y otro clic en la misma la quita
    assert dlg.hours == set() and dlg.blocks["n"].value.text() == "3"


def _profile_group(profile, name, key="indices"):
    g = json.loads(json.dumps(GROUP))
    g.update({"key": f"{profile}:{key}", "perfil": profile, "perfil_nombre": name})
    g["cats"]["o"] = ["objetivo", "stop", "breakeven", "tiempo"]
    return g


def test_la_ventana_elige_el_perfil_y_cada_perfil_trae_sus_grupos(tmp_path):
    from PySide6.QtWidgets import QApplication
    from tradingbot.ui.backtest_dialog import BacktestDialog
    QApplication.instance() or QApplication([])
    forex = _profile_group("puprime", "PUPrime", "forex")
    cal = {**json.loads(json.dumps(GROUP)), "key": "calendario", "nombre": "Calendario", "perfil": "calendario", "perfil_nombre": "Calendario"}
    path = tmp_path / "bt.json"
    path.write_text(json.dumps({"generado": "x", "comparativa": {}, "grupos": [
        _profile_group("puprime", "PUPrime"), forex, _profile_group("metaquotes", "MetaQuotes"), cal]}), encoding="utf-8")
    bt = load(path)
    assert [p for p, _ in bt.profiles] == ["puprime", "metaquotes", "calendario"]
    assert [g.key for g in bt.groups_of("puprime")] == ["puprime:indices", "puprime:forex"]
    dlg = BacktestDialog(None, bt)
    assert dlg.profile_key == "puprime" and list(dlg.profile_btns) == ["puprime", "metaquotes", "calendario"]
    assert list(dlg.group_btns) == ["puprime:indices", "puprime:forex"]            # solo los mercados del perfil elegido
    dlg.set_group("puprime:forex")
    dlg.set_profile("metaquotes")                                                  # se queda en el mismo grupo si el perfil lo tiene...
    assert dlg.group_key == "metaquotes:indices" and list(dlg.group_btns) == ["metaquotes:indices"]
    dlg.set_group("puprime:forex")
    dlg.set_profile("metaquotes")
    assert dlg.group_key == "metaquotes:indices"                                    # ...y si no, el primero
    dlg.set_profile("calendario")
    assert dlg.group_key == "calendario" and dlg.profile_btns["calendario"].isChecked()
    # la comparativa de mercados solo cuenta los del perfil
    assert {grp for _m, grp, _o in bt.compare(BOT_FILTER, profile="puprime")} == {"Índices americanos"}
    assert len(bt.compare(BOT_FILTER, profile="puprime")) == 4                       # 2 mercados por grupo y 2 grupos
    assert dlg.outcomes.headers[3] == "Breakeven" if hasattr(dlg.outcomes, "headers") else True
