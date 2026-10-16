"""Panel «Reglas del sesgo»: reglas activas con su peso y editor para elegir reglas y pesos."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication, QLabel

from tradingbot import envconfig, settings
from tradingbot.core import EventBus, Services, SkillManager
from tradingbot.envconfig import EnvConfig
from tradingbot.skills.bias import Bias, BiasEngine, BiasResult
from tradingbot.skills.bias.models import RuleVote
from tradingbot.skills.bias.rules import AboveBelowTdo, PrevDayBreak
from tradingbot.ui.main_window import MainWindow
from tradingbot.ui.rules_dialog import OVERLAPS, RulesDialog, rule_choices
from tradingbot.ui.widgets import RulesList


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def texts(widget):
    return [lbl.text() for lbl in widget.findChildren(QLabel)]


def test_el_motor_cambia_reglas_y_pesos_en_caliente_y_conserva_parametros():
    engine = BiasEngine([PrevDayBreak(), AboveBelowTdo(tolerance_pct=0.5)], min_score=2)
    engine.configure([("tdo", 1.5), ("midnight", 1.0)], min_score=3)
    assert [(r.key, r.weight) for r in engine.rules] == [("tdo", 1.5), ("midnight", 1.0)]
    assert engine.rules[0].params == {"tolerance_pct": 0.5} and engine.min_score == 3      # la regla que seguía activa conserva su tolerancia
    engine.configure([])
    assert engine.rules == [] and engine.min_score == 3
    with pytest.raises(ValueError, match="desconocida"):
        engine.configure([("no_existe", 1)])
    with pytest.raises(ValueError, match="peso"):
        engine.configure([("tdo", -1)])


def test_la_lista_muestra_una_linea_por_regla_con_su_peso(qapp):
    lista = RulesList()
    lista.set_rules([("Ruptura del día anterior", 2.0), ("Precio vs TDO", 1.0)])
    assert "+2" in texts(lista) and "+1" in texts(lista) and "Ruptura del día anterior" in texts(lista)
    votes = (RuleVote("Ruptura del día anterior", 1, "Precio 1.123 sobre el máximo previo 1.100", 2.0),
             RuleVote("Precio vs TDO", -1, "Precio 1.123 bajo el TDO 1.130", 1.0))
    lista.set_result(BiasResult(Bias.BULLISH, None, votes, {}, "resumen", 1.0, 2.0))
    shown = texts(lista)
    assert not any("1.123" in t for t in shown)                       # los precios van en la ayuda emergente
    assert any("Puntuación +1" in t and "mínimo 2" in t for t in shown)
    # si las reglas activas cambian, el sesgo mostrado ya no vale y se vuelve a la lista de reglas
    lista.set_rules([("Precio vs Midnight", 1.0)])
    assert "Precio vs Midnight" in texts(lista) and not any("Puntuación" in t for t in texts(lista))


def test_el_editor_devuelve_las_reglas_marcadas_con_su_peso(qapp):
    dialog = RulesDialog(None, [("prev_day_break", 2.0), ("tdo", 1.0)], 2.0)
    assert dialog.selection() == [("prev_day_break", 2.0), ("tdo", 1.0)] and dialog.min_score() == 2.0
    dialog.checks["midnight"].setChecked(True)
    dialog.spins["midnight"].setValue(1.5)
    dialog.checks["prev_day_break"].setChecked(False)
    dialog.min_spin.setValue(2.5)
    assert dialog.selection() == [("tdo", 1.0), ("midnight", 1.5)] and dialog.min_score() == 2.5
    assert not dialog.spins["prev_day_break"].isEnabled()
    assert {key for key, *_ in rule_choices()} >= {"prev_day_break", "tdo", "midnight", "above_below_open", "htf_sweep"}
    a, b = OVERLAPS[0]
    dialog.checks[a].setChecked(True)
    dialog.checks[b].setChecked(True)
    assert "contarían doble" in dialog.note.text()
    for check in dialog.checks.values():
        check.setChecked(False)
    assert "No Bias" in dialog.note.text()


def test_el_enlace_voto_de_cada_regla_abre_el_editor_y_aplica_y_guarda(qapp, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    env_file = tmp_path / "tradingbot.env"
    env_file.write_text("BIAS_RULES=prev_day_break, tdo, midnight\nBIAS_MIN_SCORE=2\n", encoding="utf-8")
    monkeypatch.setattr(envconfig, "ENV_FILE", env_file)
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": ["EURUSD"]}}
    engine = BiasEngine([PrevDayBreak(), AboveBelowTdo()], min_score=2)
    bus = EventBus()
    win = MainWindow(bus, SkillManager(bus, Services(None, engine, cfg, EnvConfig()), []), cfg, "t")
    assert "Voto de cada regla" in win.rules_panel.note.text() and "href" in win.rules_panel.note.text()
    assert [t for t in texts(win.rules_list) if t.startswith("+")] == ["+2", "+1"]
    win._apply_rules([("tdo", 1.5), ("midnight", 1.0)], 2.5)
    assert [(r.key, r.weight) for r in engine.rules] == [("tdo", 1.5), ("midnight", 1.0)] and engine.min_score == 2.5
    assert [t for t in texts(win.rules_list) if t.startswith("+")] == ["+1.5", "+1"]
    saved = envconfig.parse(env_file.read_text(encoding="utf-8"))
    assert saved["BIAS_RULES"] == "tdo, midnight" and saved["BIAS_TDO_WEIGHT"] == "1.5"
    assert saved["BIAS_MIDNIGHT_WEIGHT"] == "1" and saved["BIAS_MIN_SCORE"] == "2.5"
    assert "reglas actualizadas" in win.log_view.toPlainText()
    win._apply_rules([], 2.0)                                           # sin reglas: BIAS_RULES=ninguna
    assert envconfig.parse(env_file.read_text(encoding="utf-8"))["BIAS_RULES"] == "ninguna"
