"""Grupo de Barrido_NYAM de la ventana Backtest: un botón por setup (Todos, RTH, Asia, PDH/PDL de Asia y de Londres)."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from tradingbot.skills.stats.backtest import Group, load  # noqa: E402

PATTERNS = ["Todos", "Barrido RTH", "Barrido de Asia", "Barrido PDH/PDL Asia", "Barrido PDH/PDL Londres"]


def raw_group() -> dict:
    """Cuatro operaciones a mano, una por setup: mercado (m), patrón (p), TBR (z), R neto (r)."""
    n = 4
    return {"key": "barrido_nyam:indices", "nombre": "Índices", "tipo": "barrido", "perfil": "barrido_nyam", "perfil_nombre": "Barrido_NYAM",
            "cats": {"m": ["NAS100.s"], "p": PATTERNS[1:], "z": ["RTH", "Asia", "London"], "o": ["objetivo", "stop", "breakeven", "tiempo"],
                     "s": ["a favor", "en contra", "sin sesgo"]},
            "patrones": PATTERNS, "filtros": {"sin filtro de sesgo": "Todas las operaciones"}, "zonas": ["RTH", "Asia", "London"],
            "ops": {"m": [0] * n, "p": [0, 1, 2, 3], "z": [0, 1, 1, 2], "o": [0, 1, 0, 0], "d": [0, 1, 0, 1], "s": [2] * n, "f": [0] * n,
                    "e": [1000 + 100 * i for i in range(n)], "x": [1050 + 100 * i for i in range(n)], "v": [10] * n,
                    "r": [2.0, -1.0, 3.0, 1.0], "k": [0.0] * n, "rk": [0.1] * n}}


def test_cada_patron_de_barrido_da_sus_propias_operaciones_y_todos_las_suma():
    g = Group("barrido_nyam:indices", "Índices", raw_group())
    assert g.is_barrido and g.patterns == PATTERNS and list(g.filters) == ["sin filtro de sesgo"]
    f = next(iter(g.filters))
    assert len(g.view("Todos", f).main) == 4
    assert [round(g.view(p, f).main.stats()["total"], 2) for p in PATTERNS[1:]] == [2.0, -1.0, 3.0, 1.0]
    v = g.view("Todos", f)
    assert [p for p, _ in v.outcomes] == PATTERNS[1:]                                  # «Cómo terminan», una fila por setup
    assert [(z, len(o)) for z, o in v.zones] == [("RTH", 1), ("Asia", 2), ("London", 1)]
    assert [(p, len(o)) for p, o in g.view("Barrido de Asia", f).outcomes] == [("Barrido de Asia", 1)]


def test_la_ventana_backtest_tiene_un_boton_por_setup_de_barrido():
    from PySide6.QtWidgets import QApplication
    from tradingbot.ui.backtest_dialog import BacktestDialog
    QApplication.instance() or QApplication([])
    bt = load()
    g = bt.group("barrido_nyam:indices")
    assert g is not None and g.is_barrido and g.patterns == PATTERNS
    dlg = BacktestDialog(None, bt)
    dlg.set_group("barrido_nyam:indices")
    assert dlg.profile_key == "barrido_nyam" and list(dlg.pattern_btns) == PATTERNS
    assert dlg.pattern == "Todos" and dlg.pattern_btns["Todos"].isChecked()
    counts = {}
    for name in PATTERNS:
        dlg.set_pattern(name)
        counts[name] = int(dlg.blocks["n"].value.text().replace(".", ""))
        assert dlg.pattern_btns[name].isChecked() and counts[name] == len(g.view(name, dlg.filter).main) > 0
    assert counts["Todos"] == sum(counts[p] for p in PATTERNS[1:])
