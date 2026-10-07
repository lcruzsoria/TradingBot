import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "make_screenshots.py"


def run(*args):
    env = {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env, timeout=120)


def test_genera_una_captura_por_paleta_con_su_nombre(tmp_path):
    result = run("blanco", "matrix", "--out", str(tmp_path), "--wait", "0.3")
    assert result.returncode == 0, result.stderr
    for name in ("blanco", "matrix"):
        png = tmp_path / f"{name}.png"
        assert png.exists() and png.stat().st_size > 50_000, name           # una ventana completa, no una imagen vacía
    assert sorted(p.name for p in tmp_path.iterdir()) == ["blanco.png", "matrix.png"]


def test_paleta_desconocida_da_un_error_claro(tmp_path):
    result = run("rosa", "--out", str(tmp_path))
    assert result.returncode != 0 and "paleta desconocida" in result.stderr and "matrix" in result.stderr


def test_las_capturas_incluidas_en_el_proyecto_son_una_por_paleta():
    from tradingbot.ui.theme import PRESETS
    shots = {p.stem for p in (ROOT / "screenshots").glob("*.png")}
    assert shots == set(PRESETS)        # si añades una paleta, vuelve a ejecutar scripts/make_screenshots.py
