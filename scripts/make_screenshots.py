"""Genera una captura de la interfaz con cada paleta en screenshots/<paleta>.png (con datos sintéticos).

Uso (desde la carpeta del proyecto):
    uv run python scripts/make_screenshots.py                  # todas las paletas
    uv run python scripts/make_screenshots.py matrix blanco    # solo algunas
    uv run python scripts/make_screenshots.py --symbol XAUUSD --timeframe 5m
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main() -> int:
    from tradingbot.ui import theme

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("palettes", nargs="*", help=f"paletas a capturar (por defecto todas: {', '.join(theme.PRESETS)})")
    parser.add_argument("--out", type=Path, default=ROOT / "screenshots", help="carpeta de salida")
    parser.add_argument("--symbol", default="NAS100", help="mercado que se carga en el gráfico")
    parser.add_argument("--timeframe", default="15m", help="timeframe del gráfico (1m 3m 5m 15m 1h 3h 4h 7h 12h 1d 1w)")
    parser.add_argument("--wait", type=float, default=6.0, help="segundos de espera tras cargar (para que se mida la hora de NY)")
    args = parser.parse_args()

    unknown = [p for p in args.palettes if p not in theme.PRESETS]
    if unknown:
        parser.error(f"paleta desconocida: {', '.join(unknown)}. Opciones: {', '.join(theme.PRESETS)}")
    names = args.palettes or list(theme.PRESETS)

    import pyqtgraph as pg
    from PySide6.QtCore import QEventLoop, QTimer
    from PySide6.QtWidgets import QApplication

    import tradingbot.skills  # noqa: F401  (registra las skills)
    from tradingbot.skills.bias import BiasEngine
    from tradingbot.config import load_app_config
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.skills.feed.demo_data import DemoSource
    from tradingbot.ui.main_window import MainWindow

    app = QApplication(sys.argv[:1])
    cfg = load_app_config()                         # watchlist de config.toml y valores por defecto del código, no tus ajustes
    cfg["app"]["symbol"], cfg["app"]["timeframe"] = args.symbol, args.timeframe
    args.out.mkdir(parents=True, exist_ok=True)

    for name in names:
        theme.apply(theme.PRESETS[name])
        app.setStyleSheet(theme.stylesheet())
        pg.setConfigOptions(antialias=False, background=theme.CHART_BG, foreground=theme.MUTED)
        bus = EventBus()
        manager = SkillManager(bus, Services(DemoSource(), BiasEngine.from_config(cfg["bias"]), cfg), cfg["skills"])
        window = MainWindow(bus, manager, cfg, "Capturas de las paletas", demo=True, theme_name=name)
        window.resize(1540, 960)
        window.show()

        loop = QEventLoop()
        window.first_loaded.connect(lambda: QTimer.singleShot(int(args.wait * 1000), loop.quit))
        QTimer.singleShot(0, window.start)
        loop.exec()

        path = args.out / f"{name}.png"
        window.grab().save(str(path))
        window.close()                              # detiene las skills y cierra la conexión
        print(f"{name:8s} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
