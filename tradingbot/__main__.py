"""Punto de entrada: python -m tradingbot [--demo] [--profile demo] [--symbol EURUSD] [--timeframe 15m]

Las opciones de la línea de comandos mandan sobre tradingbot.env (APP_PROFILE, APP_DEMO, FEED_SYMBOL, FEED_TIMEFRAME).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .skills.bias import BiasEngine
from .core import EventBus, Services, SkillManager
from . import envconfig, settings
from .config import (DEFAULT_CONFIG_FILE, DEFAULT_ENV_FILE, ConfigError, load_app_config, load_profiles,
                     select_profile)
from .timeframes import TIMEFRAMES


def parse_args(argv):
    p = argparse.ArgumentParser(prog="tradingbot", description="TradingBot: MT5 + sesgo de sesión")
    p.add_argument("--profile", help="perfil del .env (por defecto APP_PROFILE o MT5_DEFAULT)")
    p.add_argument("--env", type=Path, default=DEFAULT_ENV_FILE, help=f"fichero de cuentas (por defecto {DEFAULT_ENV_FILE})")
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG_FILE, help="config.toml")
    p.add_argument("--demo", action=argparse.BooleanOptionalAction, default=None,
                   help="usar datos sintéticos, sin MT5 (--no-demo: conectar aunque APP_DEMO=true)")
    p.add_argument("--symbol", help="símbolo inicial")
    p.add_argument("--timeframe", choices=list(TIMEFRAMES), help="timeframe inicial")
    p.add_argument("--theme", help="paleta de arranque (sustituye a UI_THEME de tradingbot.env)")
    p.add_argument("--screenshot", type=Path, help=argparse.SUPPRESS)  # solo desarrollo
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    import pyqtgraph as pg
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QMessageBox

    from .ui import theme
    from .ui.main_window import MainWindow

    app = QApplication(sys.argv[:1])

    try:
        env = envconfig.load()
        cfg = load_app_config(args.config, env)
        theme_name, palette = theme.resolve(cfg["theme"], startup=args.theme or env.get("UI_THEME"))
        theme.apply(palette)
        app.setStyleSheet(theme.stylesheet())
        pg.setConfigOptions(antialias=False, background=theme.CHART_BG, foreground=theme.MUTED)
        if args.symbol:
            cfg["app"]["symbol"] = args.symbol.strip()
        if args.timeframe:
            cfg["app"]["timeframe"] = args.timeframe
        cfg["app"]["watchlist"] = settings.load_watchlist(cfg["app"]["watchlist"])
        engine = BiasEngine.from_config(cfg["bias"])

        demo = cfg["app"]["demo"] if args.demo is None else args.demo
        if demo:
            from .skills.feed.demo_data import DemoSource
            source, subtitle = DemoSource(), "Modo demo sin conexión a MT5"
        else:
            from .skills.feed.mt5_client import Mt5Source
            profiles, default = load_profiles(args.env)
            profile = select_profile(profiles, default, args.profile or cfg["app"]["profile"])
            source = Mt5Source(profile, int(cfg["app"]["max_bars"]))
            subtitle = f"Perfil {profile.label}"
    except (ConfigError, ValueError) as exc:
        QMessageBox.critical(None, "TradingBot", f"{exc}\n\nPuedes probar la interfaz sin MT5 con  --demo  (o APP_DEMO=true en tradingbot.env)")
        return 2

    try:
        import tradingbot.skills  # noqa: F401  (registra todas las skills de la carpeta)
        bus = EventBus()
        manager = SkillManager(bus, Services(source, engine, cfg, env), cfg["skills"])
    except ValueError as exc:
        QMessageBox.critical(None, "TradingBot", f"Configuración de skills no válida:\n{exc}")
        return 2

    app.aboutToQuit.connect(manager.stop)   # cierra el hilo de cada skill y la conexión con MT5
    window = MainWindow(bus, manager, cfg, subtitle, demo=demo, theme_name=theme_name)
    window.show()
    if args.screenshot:
        def shoot():
            window.grab().save(str(args.screenshot))
            app.quit()
        window.first_loaded.connect(lambda: QTimer.singleShot(1200, shoot))
    QTimer.singleShot(0, window.start)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
