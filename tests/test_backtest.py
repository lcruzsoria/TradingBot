"""Skill Stats (sesión y backtest) y ventana Backtest."""
import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import date
from types import SimpleNamespace

import pytest

from tradingbot.core import Event, EventBus, Services, SkillManager
from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.cortex.order import Order
from tradingbot.skills.setup.positions import Closed
from tradingbot.skills.stats.backtest import BOT_FILTER, DEFAULT_FILE, Backtest, Group, load, verdict
import tradingbot.skills  # noqa: F401

ORDER = Order("NAS100", "15m", "long", "Continuación", "continuacion", "London", date(2026, 10, 6), 105.0, 95.0, 100.0, 105.0,
              95.0, 115.0, "Bullish", 3.0, "GO", entry_ts=1_000_000, close_ts=1_086_400)

GROUP = {"key": "indices", "nombre": "Índices americanos", "actualizado": "2026-10-18",
         "datos": [{"mercado": "NAS100.r", "velas M15": 1000, "desde (NY)": "2018-09-10", "hasta (NY)": "2026-10-16",
                    "TBR evaluadas": 60}],
         "resumen": [{"patrón": "Ambos", "filtro": BOT_FILTER, "n": 100, "wr": 34.0, "mean": -0.05, "total": -5.0, "pf": 0.9,
                      "avg_win": 1.9, "avg_loss": -1.05, "dd": -12.0, "streak": 7, "t": -0.4}],
         "por_zona": [{"patrón": "Continuación", "zona": "Asia", "filtro": BOT_FILTER, "n": 10, "wr": 30.0, "total": -3.0},
                      {"patrón": "Reversión", "zona": "Asia", "filtro": BOT_FILTER, "n": 30, "wr": 40.0, "total": 3.0},
                      {"patrón": "Continuación", "zona": "London", "filtro": BOT_FILTER, "n": 5, "wr": 20.0, "total": -1.0}],
         "curvas": {f"Ambos|{BOT_FILTER}": [["2018-09-10", -1.0], ["2026-10-16", -5.0]]}}


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


def test_lectura_del_backtest(tmp_path):
    path = tmp_path / "bt.json"
    path.write_text(json.dumps({"generado": "x", "grupos": [GROUP], "comparativa": {}}), encoding="utf-8")
    g = load(path).group("indices")
    assert g.period == "2018-2026" and g.row("Ambos", BOT_FILTER)["n"] == 100 and g.row("Ambos", "otro") is None
    zones = g.breakdown("por_zona", "zona", "Ambos", BOT_FILTER)                  # sin filas «Ambos»: suma los dos patrones
    asia = next(z for z in zones if z["zona"] == "Asia")
    assert asia["n"] == 40 and asia["total"] == 0.0 and asia["wr"] == pytest.approx(37.5) and asia["t"] is None
    assert len(g.breakdown("por_zona", "zona", "Reversión", BOT_FILTER)) == 1
    assert g.curve("Ambos", BOT_FILTER)[-1] == ("2026-10-16", -5.0) and g.curve("Reversión", BOT_FILTER) == []
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        load(path)
    assert verdict(-2.5, -0.1)[1] == -1 and verdict(2.1, 0.1)[1] == 1 and verdict(-1.0, -0.05)[1] == 0


@pytest.mark.skipif(not DEFAULT_FILE.exists(), reason="sin backtest.json")
def test_ventana_backtest_con_el_resumen_real():
    from PySide6.QtWidgets import QApplication
    from tradingbot.ui.backtest_dialog import BacktestDialog
    QApplication.instance() or QApplication([])
    bt = load()
    assert [g.key for g in bt.groups] == ["indices", "forex", "oro", "cripto", "calendario"]
    dlg = BacktestDialog(None, bt)
    assert dlg.group_key == "indices" and dlg.blocks["n"].value.text() != "-"
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
    dlg.set_group("indices")
    assert dlg.pattern == "Ambos" and not dlg.by_zone.isHidden()
    dlg.set_backtest(None, "falta el fichero")
    assert dlg.empty.text() == "falta el fichero" and dlg.scroll.isHidden()


def test_ventana_backtest_con_datos_minimos():
    from PySide6.QtWidgets import QApplication
    from tradingbot.ui.backtest_dialog import BacktestDialog
    QApplication.instance() or QApplication([])
    dlg = BacktestDialog(None, Backtest([Group("indices", "Índices americanos", GROUP)], {}))
    assert dlg.blocks["n"].value.text() == "100" and dlg.blocks["wr"].value.text() == "34.0 %"
    assert "Sin ventaja clara" in dlg.verdict.text()
    assert [r[0].text() for r in dlg.by_zone.rows] == ["Asia", "London"]
    dlg.set_pattern("Reversión")                                                   # sin fila en el resumen
    assert dlg.blocks["n"].value.text() == "-"
