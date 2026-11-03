"""Rehace el forwardtest del perfil CRT con la regla de la zona común: las operaciones que habría abierto el bot desde que empezó el perfil.

El forwardtest se escribe en directo con la regla que tenía el bot en cada momento. Cuando la regla cambia (como pasó el 03/11/2026 con la zona común:
iFVG invertido, pullback a la zona y cierre sobre el CISD), las operaciones antiguas quedan con entradas, horas y resultados que la regla actual no daría
(y Telegram las sigue enseñando). Este script vuelve a buscar los setups con las velas M5 de MT5 desde el inicio de la cuenta virtual del perfil y
rehace, con el mismo motor, Cortex (una posición por mercado) y Setup (stop, objetivo, breakeven, cierre por tiempo y consolidación):
  - el diario del forwardtest (data/perfiles/crt/forwardtest/AAAA-MM.jsonl): abre y cierra de cada operación,
  - las posiciones abiertas (data/perfiles/crt/abiertas.json),
  - la cuenta virtual (data/perfiles/crt/cuenta.json): mismo capital inicial, operaciones consolidadas con el riesgo del saldo de ese momento.
Sin `--aplicar` solo enseña lo que haría. Con `--aplicar` hace antes una copia de la carpeta del perfil en data/backup-forwardtest-<fecha>-crt-zona.
PARA EL BOT ANTES DE APLICAR y arráncalo después: el bot guarda estos ficheros mientras corre.

Uso (desde la raíz del proyecto, con el bot parado si se aplica):
    uv run python scripts/rehacer_forwardtest_crt.py            # solo muestra
    uv run python scripts/rehacer_forwardtest_crt.py --aplicar
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tradingbot import envconfig                                                       # noqa: E402
from tradingbot.config import load_profiles, profile_dir, select_profile                 # noqa: E402
from tradingbot.skills.cortex.order import build_calendar_order                         # noqa: E402
from tradingbot.skills.crt import bias as crt_bias, engine                              # noqa: E402
from tradingbot.skills.crt.skill import DEFAULT_SYMBOLS, build_signal                   # noqa: E402
from tradingbot.skills.feed.mt5_client import Mt5Source                                 # noqa: E402
from tradingbot.skills.levels.daylevels import DEFAULT_US_INDICES, is_us_index           # noqa: E402
from tradingbot.skills.setup import store                                               # noqa: E402
from tradingbot.skills.setup.account import Schedule, VirtualAccount                    # noqa: E402
from tradingbot.skills.setup.positions import resolve                                   # noqa: E402
from tradingbot.skills.stats.journal import Journal                                     # noqa: E402

AHEAD = 7 * 3600                                       # servidor = NY + 7 h
STEP = 300
NY, LOCAL = ZoneInfo("America/New_York"), ZoneInfo("Europe/Madrid")


def local_naive(server_ts: int) -> datetime:
    """Hora local (la de las marcas `at` del diario) de una hora de servidor."""
    ny = datetime.fromtimestamp(int(server_ts) - AHEAD, timezone.utc).replace(tzinfo=None).replace(tzinfo=NY)
    return ny.astimezone(LOCAL).replace(tzinfo=None)


def server_from_local(text: str) -> int:
    """Hora (servidor) de una marca local naive del diario o de la cuenta."""
    ny = datetime.fromisoformat(text).replace(tzinfo=LOCAL).astimezone(NY)
    return int(ny.replace(tzinfo=timezone.utc).timestamp()) + AHEAD


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--perfil", default="crt")
    ap.add_argument("--aplicar", action="store_true", help="escribe el diario, las abiertas y la cuenta (con copia previa)")
    ap.add_argument("--barras", type=int, default=20000, help="velas M5 que se piden a MT5 por mercado")
    args = ap.parse_args()

    env = envconfig.load()
    crt, setup = env.section("CRT"), env.section("SETUP")
    symbols = crt.get_list("SYMBOLS", DEFAULT_SYMBOLS)
    entry_model = crt.get_int("ENTRY", 1)
    rr = crt.get_float("RR", 2.0)
    bias_cfg = crt_bias.load_cfg(crt)
    risk_pct = setup.get_float("RISK_PCT", 1.0)
    be_pct = setup.get_float("BE_TRIGGER_PCT", 1.0)
    be_r = be_pct / risk_pct if be_pct > 0 else None
    schedule = Schedule(setup.get_int("CONSOLIDATE_INDEX_HOURS", 3), setup.get_int("CONSOLIDATE_HOURS", 4), env.get_list("LEVELS_US_INDICES", list(DEFAULT_US_INDICES)))
    indices = env.get_list("LEVELS_US_INDICES", list(DEFAULT_US_INDICES))
    rule = engine.Rule(rr=rr, be_at=0.0)

    folder = profile_dir(args.perfil)
    account = VirtualAccount(folder / "cuenta.json")
    if not account.started or not account.since:
        sys.exit("El perfil no tiene cuenta virtual (cuenta.json con capital inicial y fecha de inicio): no hay desde cuándo rehacer.")
    since = server_from_local(account.since)
    print(f"Perfil {args.perfil}: cuenta desde {account.since} (servidor {since}), capital {account.initial:,.0f} {account.currency}, riesgo {risk_pct:g} %, BE a +{be_r:g} R")

    profiles, default = load_profiles()
    source = Mt5Source(select_profile(profiles, default, args.perfil), 2_000_000)
    print("conectado:", source.connect(), flush=True)
    orders, bars = [], {}
    for want in symbols:
        symbol = source.resolve_symbol(want)
        mt5 = source._mt5
        mt5.symbol_select(symbol, True)
        series = {}
        for m in engine.ZONE_TFS:                                                # velas de 3, 5 y 15 min de MT5 (las de 15 también se podrían agrupar desde las de 5)
            raw = pd.DataFrame(mt5.copy_rates_from_pos(symbol, getattr(mt5, f"TIMEFRAME_M{m}"), 0, args.barras)).rename(columns={"time": "ts"})
            series[m] = raw[["ts", "open", "high", "low", "close"]].iloc[:-1].reset_index(drop=True)      # sin la vela que se está formando
        df = series[5]
        bars[symbol] = df                                                       # con estas velas se sigue la posición (el TF del perfil)
        base = engine.INDICES if is_us_index(symbol, indices) else engine.FOREX
        cfg = engine.Cfg(base.htf_min, base.origin, base.session_end, AHEAD)
        setups, _ = engine.find_multi_setups(series, cfg)
        zones = crt_bias.zone_cache(df, cfg, bias_cfg)
        views = {m: {1: engine.view(d, 1), -1: engine.view(d, -1)} for m, d in series.items()}
        seen = set()
        for st in setups:                                                       # por la hora del cierre sobre el CISD: el primero de cada C2 y lado
            m = st["ltf"]
            key = (st["C2"], st["sign"])
            ep = engine.entry_point(views[m][st["sign"]], st, entry_model, m, rule, cfg)
            if ep is None or key in seen:
                continue
            ts = series[m]["ts"].to_numpy().astype(np.int64)
            if int(ts[ep["start"]]) < since:
                continue
            seen.add(key)
            sgn = st["sign"]
            points = crt_bias.evaluate(df, st["dirección"], int(st["C2"]), (sgn * st["z_bottom"], sgn * st["z_top"]), cfg, bias_cfg, AHEAD, zones)
            payload = build_signal(symbol, "5m", st, ep, ts, AHEAD, rule, entry_model, points)
            payload["combinacion"] = f"FVG {st['mtf']} + iFVG M{m}"
            if not points.go:                                                      # CRT_BIAS_ENFORCE=true y sin los puntos: NO GO
                continue
            order = build_calendar_order(payload, payload["bias_result"], payload["reason"])
            orders.append((order, payload["combinacion"]))
        print(f"  {symbol}: velas M3/M5/M15 hasta {local_naive(int(df['ts'].iloc[-1]))}, setups {len(setups)}", flush=True)
    source.close()

    now = max(int(df["ts"].iloc[-1]) for df in bars.values()) + STEP
    taken, last_exit, order_combo = [], {}, {}                                  # Cortex: una posición por mercado
    combos = {id(o): c for o, c in orders}
    for order in sorted((o for o, _ in orders), key=lambda o: o.entry_ts):
        prev = last_exit.get(order.symbol, -1)
        if prev is None or order.entry_ts <= prev:                              # sigue abierta (None) o cierra a la vez/después de la entrada
            continue
        df = bars[order.symbol]
        closed = resolve(order, df["ts"].to_numpy(), df["high"].to_numpy(), df["low"].to_numpy(), df["close"].to_numpy(), be_r, STEP, now)
        last_exit[order.symbol] = None if closed is None else int(closed.exit_ts)
        taken.append((order, closed))
        order_combo[id(order)] = combos[id(order)]

    print(f"\n{len(taken)} operaciones desde {account.since}:")
    for order, closed in taken:
        res = "abierta" if closed is None else f"{closed.result} {closed.r:+.2f} R (cierra {local_naive(closed.exit_ts):%d/%m %H:%M})"
        print(f"  {local_naive(order.entry_ts):%d/%m %H:%M} {order.symbol:9} {order.direction:5} entrada {order.price:.5g} stop {order.stop:.5g} obj. {order.target:.5g} · "
              f"sesgo {order.bias} {order.score:+g} · {order_combo[id(order)]} · {res}")
    done = [c for _, c in taken if c is not None]
    print(f"cerradas {len(done)}: {sum(c.r for c in done):+.2f} R; abiertas {sum(c is None for _, c in taken)}")
    if not args.aplicar:
        print("\n(Solo muestra. Con el bot parado, --aplicar rehace el diario, las abiertas y la cuenta.)")
        return

    backup = ROOT / "data" / f"backup-forwardtest-{datetime.now():%Y%m%d-%H%M}-crt-zona"
    shutil.copytree(folder, backup / args.perfil)
    print("copia en", backup)
    journal_dir = folder / "forwardtest"
    for old in journal_dir.glob("*.jsonl"):
        old.unlink()
    events = []
    for order, closed in taken:
        events.append((order.entry_ts + STEP, 0, order, None))
        if closed is not None:
            events.append((closed.exit_ts + STEP, 1, order, closed))
    for ts, kind, order, closed in sorted(events, key=lambda e: e[:2]):
        stamp = local_naive(ts)
        journal = Journal(journal_dir, now=lambda stamp=stamp: stamp)
        journal.opened(order) if kind == 0 else journal.closed(order, closed)
    store.save([o for o, c in taken if c is None], folder / "abiertas.json")
    account.trades, account.pending = [], []
    waiting = sorted(((schedule.due(o.symbol, c.exit_ts), int(c.exit_ts), o, c) for o, c in taken if c is not None), key=lambda x: x[:2])
    for due, _, order, closed in waiting:
        if due <= now:
            account._now = lambda due=due: local_naive(due)
            account.book(order, closed, risk_pct, due)
    account.save()
    print(f"cuenta: {len(account.trades)} operaciones consolidadas, saldo {account.balance:,.2f} {account.currency}; "
          f"{sum(1 for d, *_ in waiting if d > now)} cerrada(s) pendiente(s) de consolidar")
    print("Arranca el bot: leerá el diario, las abiertas y la cuenta nuevos.")


if __name__ == "__main__":
    main()
