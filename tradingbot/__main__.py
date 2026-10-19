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
from .config import (DEFAULT_CONFIG_FILE, DEFAULT_ENV_FILE, DEMO_PROFILE, PROJECT_ROOT, ConfigError,
                     load_app_config, load_profiles, profile_dir, select_profile)
from .timeframes import TIMEFRAMES


def parse_args(argv):
    p = argparse.ArgumentParser(prog="tradingbot", description="TradingBot: MT5 + sesgo de sesión")
    p.add_argument("--profile", help="perfil del .env (por defecto el último elegido en la app, APP_PROFILE o MT5_DEFAULT)")
    p.add_argument("--env", type=Path, default=DEFAULT_ENV_FILE, help=f"fichero de cuentas (por defecto {DEFAULT_ENV_FILE})")
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG_FILE, help="config.toml")
    p.add_argument("--demo", action=argparse.BooleanOptionalAction, default=None,
                   help="usar datos sintéticos, sin MT5 (--no-demo: conectar aunque APP_DEMO=true)")
    p.add_argument("--symbol", help="símbolo inicial")
    p.add_argument("--timeframe", choices=list(TIMEFRAMES), help="timeframe inicial")
    p.add_argument("--theme", help="paleta de arranque (sustituye a UI_THEME de tradingbot.env)")
    p.add_argument("--screenshot", type=Path, help=argparse.SUPPRESS)  # solo desarrollo
    return p.parse_args(argv)


def load_fonts(app, theme) -> None:
    """Carga las letras de tradingbot/ui/fonts (si las hay) y pone la del tema como letra por defecto de la app."""
    from PySide6.QtGui import QFont, QFontDatabase
    if theme.FONTS_DIR.is_dir():
        for path in sorted(theme.FONTS_DIR.iterdir()):
            if path.suffix.lower() in (".ttf", ".otf"):
                QFontDatabase.addApplicationFont(str(path))
    available = set(QFontDatabase.families())
    family = next((f for f in theme.font_families() if f in available), None)
    if family:
        app.setFont(QFont(family, 9))


def migrate_legacy_data(name: str, default: str) -> None:
    """Antes de los perfiles, las posiciones abiertas y el forwardtest iban en data/setup y data/forwardtest: pasan a la
    carpeta del perfil por defecto (la cuenta que se usaba) la primera vez que arranca."""
    if name != default or profile_dir(name).exists():
        return
    legacy = {PROJECT_ROOT / "data" / "setup" / "abiertas.json": profile_dir(name) / "abiertas.json",
              PROJECT_ROOT / "data" / "forwardtest": profile_dir(name) / "forwardtest"}
    for old, new in legacy.items():
        if old.exists():
            new.parent.mkdir(parents=True, exist_ok=True)
            old.replace(new)


def relaunch_args(argv: list[str], profile: str) -> list[str]:
    """Los argumentos para volver a arrancar con otro perfil: los mismos, sin el --profile que hubiera."""
    out, skip = [], False
    for arg in argv:
        if skip:
            skip = False
        elif arg == "--profile":
            skip = True
        elif not arg.startswith("--profile="):
            out.append(arg)
    return ["-m", "tradingbot", *out, "--profile", profile]


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    args = parse_args(argv)

    import pyqtgraph as pg
    from PySide6.QtCore import QProcess, QTimer
    from PySide6.QtWidgets import QApplication, QMessageBox

    from .ui import theme
    from .ui.main_window import MainWindow

    app = QApplication(sys.argv[:1])

    try:
        env = envconfig.load()
        cfg = load_app_config(args.config, env)
        theme_name, palette = theme.resolve(cfg["theme"], startup=args.theme or env.get("UI_THEME"))
        theme.apply(palette)
        theme.set_font(env.get("UI_FONT"))
        load_fonts(app, theme)
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
            cfg["app"]["data_dir"] = str(profile_dir(DEMO_PROFILE))
            cfg["app"]["profiles"], cfg["app"]["profile_name"] = [], None
        else:
            from .skills.feed.mt5_client import Mt5Source
            profiles, default = load_profiles(args.env)
            saved = settings.load_profile()                      # el último elegido en el selector de la cabecera
            if saved not in profiles:
                saved = None
            profile = select_profile(profiles, default, args.profile or saved or cfg["app"]["profile"])
            source = Mt5Source(profile, int(cfg["app"]["max_bars"]))
            subtitle = f"Perfil {profile.label}"
            migrate_legacy_data(profile.name, default or next(iter(profiles)))
            cfg["app"]["data_dir"] = str(profile_dir(profile.name))
            cfg["app"]["profiles"] = [(p.name, p.display) for p in profiles.values()]
            cfg["app"]["profile_name"] = profile.name
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
    def switch_profile(name: str) -> None:
        """Cambio de perfil desde la cabecera: se guarda y el bot vuelve a arrancar con la otra cuenta."""
        settings.save_profile(name)
        if QProcess.startDetached(sys.executable, relaunch_args(argv, name), str(PROJECT_ROOT))[0]:
            app.quit()
        else:
            QMessageBox.warning(None, "TradingBot", f"No se pudo volver a arrancar con el perfil {name}. "
                                                    "Ciérralo y arráncalo de nuevo: se abrirá con ese perfil.")

    window = MainWindow(bus, manager, cfg, subtitle, demo=demo, theme_name=theme_name, switch_profile=switch_profile)
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
