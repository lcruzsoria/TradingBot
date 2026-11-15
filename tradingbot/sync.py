"""Pone al día el forwardtest de los perfiles cuyo bot no está abierto.

Cada perfil escribe su forwardtest (diario, posiciones abiertas y cuenta virtual) solo mientras su bot corre. Con la ventana de otro perfil
abierta, los demás se quedaban parados. Esta herramienta los pone al día: `python -m tradingbot --sync-forwardtest` recorre los perfiles
(menos los que tienen su bot abierto) y, según su estrategia:
  - TBR, Barrido, Calendario...: arranca sus skills sin ventana (sin Telegram), deja que Pattern y Cortex repasen lo ocurrido desde
    STATS_FORWARD_START (lo repetido no se anota dos veces) y se cierra al terminar el barrido;
  - CRT: rehace su forwardtest con `scripts/rehacer_forwardtest_crt.py --aplicar`;
  - Enigma369: no opera, no hay nada que poner al día.
El bot lo lanza solo al arrancar y cada SYNC_MINUTES (tradingbot.env, bloque SYNC); también se puede ejecutar a mano (--dry-run: trabaja sobre
una copia y enseña lo que cambiaría, sin tocar los datos).
"""
from __future__ import annotations

import argparse
import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import date, datetime, timedelta
from pathlib import Path

from . import envconfig, settings
from .config import (DEFAULT_CONFIG_FILE, DEFAULT_ENV_FILE, PROFILES_DIR, PROJECT_ROOT, STRATEGY_TIMEFRAMES, load_app_config, load_profiles,
                     profile_dir, strategy_skills)

NO_SYNC_SKILLS = ("telegram",)                  # nada de avisos por Telegram de lo que se repasa: ya pasó
QUIET_SECONDS = 30                               # sin novedades de Pattern, Cortex o Setup durante ese tiempo: el repaso ha terminado
MAX_SECONDS = 20 * 60                            # y lo que se espera como máximo a un perfil
BUSY_TOPICS = ("candles.loaded", "pattern.", "bias.", "cortex.", "setup.", "stats.", "calendar.", "feed.")
LOCK_STALE_MINUTES = 40
REBUILD_EVERY_HOURS = 6                          # CRT se rehace entero: no hace falta cada hora
DEFAULT_SYNC_MINUTES = 60
SWEEP_DAYS_MAX = 45
STATE_FILE = "sincronizacion.json"


# -- qué bots están abiertos --------------------------------------------------------------------------------
def pid_alive(pid: int) -> bool:
    """Si hay un proceso con ese pid."""
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)       # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        code = ctypes.c_ulong()
        ok = ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
        ctypes.windll.kernel32.CloseHandle(handle)
        return bool(ok) and code.value == 259                                  # STILL_ACTIVE
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def pid_file(profile: str, root: Path | None = None) -> Path:
    return (root or PROFILES_DIR) / profile.lower() / "bot.pid"


def register_bot(profile: str, root: Path | None = None) -> None:
    """El bot de este perfil está abierto: la sincronización no lo toca mientras dure."""
    path = pid_file(profile, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(os.getpid()), encoding="utf-8")
    atexit.register(lambda: path.unlink(missing_ok=True) if path.exists() and path.read_text(encoding="utf-8").strip() == str(os.getpid()) else None)


def running_profiles(names: list[str], root: Path | None = None) -> set[str]:
    """Los perfiles (de `names`) con su bot abierto."""
    out = set()
    for name in names:
        path = pid_file(name, root)
        try:
            pid = int(path.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            continue
        if pid_alive(pid):
            out.add(name)
        else:
            path.unlink(missing_ok=True)                                      # el bot se cerró sin limpiar
    return out


def acquire_lock(root: Path | None = None) -> Path | None:
    """Una sola sincronización a la vez; None si ya hay otra en marcha."""
    path = (root or PROFILES_DIR.parent) / "sync.lock"
    try:
        pid, stamp = path.read_text(encoding="utf-8").split()
        if pid_alive(int(pid)) and time.time() - float(stamp) < LOCK_STALE_MINUTES * 60:
            return None
    except (OSError, ValueError):
        pass
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{os.getpid()} {time.time()}", encoding="utf-8")
    atexit.register(lambda: path.unlink(missing_ok=True))
    return path


# -- estado de cada perfil -----------------------------------------------------------------------------------
def how(strategy: str) -> str:
    """Cómo se pone al día un perfil según su estrategia: 'skills' (arrancándolas sin ventana), 'crt' (su script) o 'nada'."""
    if strategy == "crt":
        return "crt"
    if strategy == "enigma369":
        return "nada"
    return "skills"


def read_state(folder: Path) -> dict:
    try:
        return json.loads((folder / STATE_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def write_state(folder: Path, **values) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / STATE_FILE).write_text(json.dumps({**read_state(folder), **values}, ensure_ascii=False, indent=1), encoding="utf-8")


def diary_count(folder: Path) -> int:
    return sum(len(f.read_text(encoding="utf-8").splitlines()) for f in (folder / "forwardtest").glob("*.jsonl")) if (folder / "forwardtest").exists() else 0


def account_summary(folder: Path) -> str:
    try:
        data = json.loads((folder / "cuenta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "sin cuenta"
    trades = data.get("operaciones", [])
    balance = trades[-1]["saldo"] if trades else data.get("capital_inicial")
    return f"{len(trades)} operaciones, saldo {balance}"


# -- repaso sin ventana --------------------------------------------------------------------------------------
def sweep_days(env, today: date | None = None) -> int:
    """Días de velas que hay que cargar para repasar desde STATS_FORWARD_START (con un margen), sin bajar de los FEED_SWEEP_DAYS."""
    base = env.section("FEED").get_int("SWEEP_DAYS", 10) or 10
    raw = env.section("STATS").get("FORWARD_START", "")
    try:
        start = date.fromisoformat(raw) if raw else None
    except ValueError:
        start = None
    if start is None:
        return base
    return min(max(base, ((today or date.today()) - start).days + 3), SWEEP_DAYS_MAX)


def catch_up(name: str, folder: Path | None = None, log=print) -> bool:
    """Arranca las skills del perfil `name` sin ventana y espera a que repasen lo ocurrido. `folder`: otra carpeta de datos (para probar)."""
    from .core import EventBus, Services, SkillManager
    from .skills.bias import BiasEngine
    from .skills.feed.mt5_client import Mt5Source
    import tradingbot.skills  # noqa: F401  (registra todas las skills de la carpeta)

    env = envconfig.load()
    cfg = load_app_config(DEFAULT_CONFIG_FILE, env)
    cfg["app"]["env_file"] = str(DEFAULT_ENV_FILE)
    profiles, default = load_profiles(DEFAULT_ENV_FILE)
    profile = profiles[name]
    env.values["FEED_SWEEP_DAYS"] = str(sweep_days(env))
    source = Mt5Source(profile, int(cfg["app"]["max_bars"]))
    cfg["app"]["data_dir"] = str(folder or profile_dir(profile.name))
    cfg["app"]["profiles"] = [(p.name, p.display) for p in profiles.values()]
    cfg["app"]["profile_name"] = profile.name
    cfg["app"]["strategy"] = profile.strategy
    cfg["app"]["capital"], cfg["app"]["currency"] = profile.capital, profile.currency
    strategy = profile.strategy or ""
    if strategy:
        cfg["skills"] = strategy_skills(cfg["skills"], strategy)
        own = env.section(strategy).get_list("SYMBOLS", []) or cfg["app"]["watchlist"]
        cfg["app"]["watchlist"] = settings.load_watchlist(own, profile=profile.name, common=False)
        cfg["app"]["symbol"] = next((s for s in cfg["app"]["watchlist"] if s.lower().startswith(cfg["app"]["symbol"].lower())), cfg["app"]["watchlist"][0])
        if strategy in STRATEGY_TIMEFRAMES:
            cfg["app"]["timeframe"] = STRATEGY_TIMEFRAMES[strategy]
    else:
        cfg["app"]["watchlist"] = settings.load_watchlist(cfg["app"]["watchlist"], profile=profile.name)
    cfg["skills"] = [s for s in cfg["skills"] if s.get("type") not in NO_SYNC_SKILLS]
    bus = EventBus()
    manager = SkillManager(bus, Services(source, BiasEngine.from_config(cfg["bias"]), cfg, env), cfg["skills"])
    seen = {"end": False, "last": time.monotonic(), "failed": ""}

    def tap(event, _names) -> None:
        if event.topic == "feed.sweep" and event.payload.get("stage") == "end":
            seen["end"] = True
        if event.topic == "feed.failed":
            seen["failed"] = event.payload.get("error", "")
        if event.topic.startswith(BUSY_TOPICS):
            seen["last"] = time.monotonic()

    bus.add_tap(tap)
    manager.start()
    bus.publish("feed.load", {"symbol": cfg["app"]["symbol"], "timeframe": cfg["app"]["timeframe"]}, source="ui")
    started = time.monotonic()
    try:
        while time.monotonic() - started < MAX_SECONDS:
            time.sleep(1)
            if seen["failed"]:
                log(f"  {name}: MT5 no carga ({seen['failed']})")
                return False
            if seen["end"] and time.monotonic() - seen["last"] > QUIET_SECONDS:
                return True
        log(f"  {name}: el repaso no termina en {MAX_SECONDS // 60} min")
        return False
    finally:
        manager.stop()


def rebuild_crt(apply: bool, log=print) -> bool:
    cmd = [sys.executable, "-X", "utf8", str(PROJECT_ROOT / "scripts" / "rehacer_forwardtest_crt.py")] + (["--aplicar"] if apply else [])
    done = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    lines = done.stdout.strip().splitlines()
    log("\n".join("  " + line for line in lines[-3:]) if lines else "  (sin salida)")
    if done.returncode:
        log("  " + done.stderr.strip().splitlines()[-1] if done.stderr.strip() else f"  error {done.returncode}")
    return done.returncode == 0


def sync_profile(name: str, strategy: str, dry_run: bool, log=print) -> str:
    """Pone al día un perfil. Devuelve lo que ha hecho, en una línea."""
    folder = profile_dir(name)
    mode = how(strategy)
    if mode == "nada":
        return "no opera: nada que poner al día"
    before = (diary_count(folder), account_summary(folder))
    if mode == "crt":
        last = read_state(folder).get("rehecho")
        if not dry_run and last and datetime.now() - datetime.fromisoformat(last) < timedelta(hours=REBUILD_EVERY_HOURS):
            return f"rehecho hace menos de {REBUILD_EVERY_HOURS} h"
        ok = rebuild_crt(not dry_run, log)
        if ok and not dry_run:
            write_state(folder, rehecho=datetime.now().isoformat(timespec="seconds"))
        return ("(solo muestra) " if dry_run else "") + ("rehecho" if ok else "ha fallado")
    scratch = None
    try:
        if dry_run:
            scratch = Path(tempfile.mkdtemp(prefix=f"sync-{name}-"))
            if folder.exists():
                shutil.copytree(folder, scratch, dirs_exist_ok=True)
        work = scratch or folder
        ok = catch_up(name, work, log)
        after = (diary_count(work), account_summary(work))
        if ok and not dry_run:
            write_state(folder, repasado=datetime.now().isoformat(timespec="seconds"))
        verdict = "al día" if ok else "no se pudo"
        return f"{'(solo muestra, copia) ' if dry_run else ''}{verdict}: diario {before[0]} -> {after[0]} líneas; cuenta {before[1]} -> {after[1]}"
    finally:
        if scratch is not None:
            shutil.rmtree(scratch, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="tradingbot --sync-forwardtest", description="Pone al día el forwardtest de los perfiles con el bot cerrado")
    ap.add_argument("--sync-forwardtest", action="store_true")
    ap.add_argument("--perfiles", nargs="+", help="solo estos perfiles (por defecto, los de SYNC_PROFILES o todos)")
    ap.add_argument("--dry-run", action="store_true", help="trabaja sobre una copia y enseña lo que cambiaría")
    ap.add_argument("--env", type=Path, default=DEFAULT_ENV_FILE)
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG_FILE)
    args, _ = ap.parse_known_args(argv)
    log_file = PROJECT_ROOT / "data" / "sync.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(text: str) -> None:
        line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {text}"
        with log_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        try:
            print(line, flush=True)
        except (OSError, ValueError):                  # sin consola (pythonw)
            pass

    if acquire_lock() is None:
        log("ya hay otra sincronización en marcha")
        return 0
    env = envconfig.load()
    profiles, _default = load_profiles(args.env)
    wanted = args.perfiles or env.section("SYNC").get_list("PROFILES", []) or list(profiles)
    busy = running_profiles(wanted)
    status = 0
    for name in wanted:
        if name not in profiles:
            log(f"{name}: no es un perfil")
            continue
        if name in busy:
            log(f"{name}: su bot está abierto, se actualiza solo")
            continue
        try:
            log(f"{name}: {sync_profile(name, profiles[name].strategy or '', args.dry_run, log)}")
        except Exception as exc:                          # noqa: BLE001 - un perfil que falla no para a los demás
            status = 1
            log(f"{name}: error {type(exc).__name__}: {exc}")
    return status
