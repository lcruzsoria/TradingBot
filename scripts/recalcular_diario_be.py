"""Recalcula los cierres de los diarios del forwardtest de los perfiles TBR con la regla actual de breakeven (toque de +1 R, sin esperar al cierre).

Hasta el commit «Breakeven al tocar +1 R» Continuación y Reversión esperaban a que una vela M15 cerrara con +1 R, así que los cierres anotados antes
pueden salir «stop» u «objetivo» donde la regla actual da «breakeven» (0 R). Para cada cierre del diario vuelve a seguir la posición con las velas de MT5
(`setup.positions.resolve`, la misma función del bot) y, si el resultado cambia, reescribe el cierre y rehace la cuenta virtual con esos importes.
Sin `--aplicar` solo enseña lo que cambiaría. Con `--aplicar` hace antes una copia de la carpeta de cada perfil en data/backup-forwardtest-<fecha>-be.
PARA EL BOT DEL PERFIL ANTES DE APLICAR y arráncalo después: el bot guarda estos ficheros mientras corre.

Uso (desde la raíz del proyecto):
    uv run python scripts/recalcular_diario_be.py                              # puprime, puprime2 y metaquotes, solo muestra
    uv run python scripts/recalcular_diario_be.py --perfiles puprime --aplicar
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tradingbot.config import load_profiles, profile_dir, select_profile                 # noqa: E402
from tradingbot.skills.feed.mt5_client import Mt5Source                                  # noqa: E402
from tradingbot.skills.setup import store                                                # noqa: E402
from tradingbot.skills.setup.account import Schedule, VirtualAccount, trade_id           # noqa: E402
from tradingbot.skills.setup.positions import resolve                            # noqa: E402

BARS = 8000                                      # velas M15 que se piden por mercado (unos 80 días)


def tf_seconds(tf: str) -> int:
    return int(tf[:-1]) * (60 if tf.endswith("m") else 3600)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--perfiles", nargs="+", default=["puprime", "puprime2", "metaquotes"])
    ap.add_argument("--be-r", type=float, default=1.0, help="R a los que el stop pasa a la entrada (SETUP_BE_TRIGGER_PCT / SETUP_RISK_PCT)")
    ap.add_argument("--aplicar", action="store_true")
    args = ap.parse_args()
    profiles, default = load_profiles()
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    for name in args.perfiles:
        folder = profile_dir(name)
        files = sorted((folder / "forwardtest").glob("*.jsonl"))
        lines = {f: f.read_text(encoding="utf-8").splitlines() for f in files}
        source = Mt5Source(select_profile(profiles, default, name), 2_000_000)
        print(f"\n== {name}: {sum(len(v) for v in lines.values())} líneas, conectado: {source.connect()}")
        candles: dict[tuple, tuple | None] = {}
        changes, odd, kept, skipped = [], [], 0, Counter()
        for f in files:
            for i, line in enumerate(lines[f]):
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("t") != "close" or not isinstance(rec.get("closed"), dict):
                    continue
                order = store.order_from_json(rec["order"])
                key = (order.symbol, order.timeframe)
                if key not in candles:
                    try:
                        df = source.load_recent(order.symbol, order.timeframe, BARS)
                        candles[key] = tuple(df[c].to_numpy() for c in ("ts", "high", "low", "close"))
                    except Exception as exc:                                # noqa: BLE001 - sin velas de ese mercado no se toca
                        print(f"  sin velas de {order.symbol} {order.timeframe}: {type(exc).__name__}")
                        candles[key] = None
                data = candles[key]
                if data is None:
                    skipped["sin velas"] += 1
                    continue
                ts, high, low, close = data
                bar = tf_seconds(order.timeframe)
                new = resolve(order, ts, high, low, close, args.be_r, bar, int(ts[-1]) + bar)
                old = rec["closed"]
                if new is None:
                    skipped["no se puede seguir (sin velas de la entrada)"] += 1
                    continue
                if new.result == old.get("result") and int(new.exit_ts) == int(old.get("exit_ts", -1)):
                    kept += 1
                    continue
                if new.result == "breakeven" and old.get("result") != "breakeven":
                    changes.append((f, i, order, old, new))
                else:                                                       # no lo explica el breakeven (velas distintas a las del bot en directo): no se toca
                    odd.append((f, order, old, new))
        moved = Counter(f"{o['result']} -> {n.result}" for _, _, _, o, n in changes)
        print(f"  cierres sin cambio: {kept}; pasan a breakeven: {len(changes)} {dict(moved)}; dudosos sin tocar: {len(odd)}; sin velas: {dict(skipped)}")
        for f, i, order, old, new in changes[:80]:
            print(f"   {f.name} {order.symbol:11} {order.direction:5} {order.pattern_key:12} día TBR {order.tbr_day}: {old['result']} {old['r']:+.2f} R -> "
                  f"{new.result} {new.r:+.2f} R")
        for f, order, old, new in odd:
            print(f"   SIN TOCAR (no es de breakeven) {f.name} {order.symbol:11} {order.direction:5} {order.pattern_key:12} día TBR {order.tbr_day}: "
                  f"{old['result']} {old['r']:+.2f} R vs {new.result} {new.r:+.2f} R")
        if not changes:
            source.close()
            continue
        # La cuenta virtual: mismos cierres, con los resultados nuevos, en el orden en que se consolidaron
        account = VirtualAccount(folder / "cuenta.json")
        replaced = {trade_id(o): n for _, _, o, _, n in changes}
        if account.started and account.trades:
            first = account.trades[0]
            risk_pct = round(100 * float(first["importe"]) / (float(first["r"]) * account.initial), 4) if float(first["r"]) else 1.0
        else:
            risk_pct = 1.0
        before = (len(account.trades), account.balance)
        schedule = Schedule()

        def replay(swap: dict) -> tuple[list[dict], float]:
            """Las operaciones de la cuenta (con los cierres de `swap`) en orden de consolidación, con importe y saldo de cada una."""
            out, bal = [], account.initial or 0.0
            for t in account.trades:
                if t["id"] in swap:
                    n = swap[t["id"]]
                    t = {**t, "result": n.result, "r": round(n.r, 4) + 0.0, "cierre_ts": int(n.exit_ts)}
                out.append({**t, "consolidada_ts": schedule.due(t["symbol"], t["cierre_ts"])})
            out.sort(key=lambda t: (t["consolidada_ts"], t["cierre_ts"]))
            for t in out:
                t["importe"] = round(float(t["r"]) * bal * risk_pct / 100, 2)
                bal = round(bal + t["importe"], 2)
                t["saldo"] = bal
            return out, bal

        base_balance = replay({})[1]
        if abs(base_balance - before[1]) > 0.5:
            print(f"  AVISO: rehacer la cuenta sin cambios da {base_balance:,.2f}, no {before[1]:,.2f}: no se toca la cuenta de {name}")
            source.close()
            continue
        trades, balance = replay(replaced)
        print(f"  cuenta: {before[0]} operaciones, saldo {before[1]:,.2f} -> {balance:,.2f} {account.currency} (riesgo {risk_pct:g} %)")
        if not args.aplicar:
            source.close()
            continue
        backup = ROOT / "data" / f"backup-forwardtest-{stamp}-be" / name
        shutil.copytree(folder, backup)
        for f in files:
            edited = False
            for fi, i, order, old, new in changes:
                if fi == f:
                    rec = json.loads(lines[f][i])
                    rec["closed"].update({"result": new.result, "exit_price": new.exit_price, "exit_ts": int(new.exit_ts), "r": new.r + 0.0, "pct": new.pct + 0.0,
                                          "be_ts": new.be_ts, "max_r": new.max_r, "min_r": new.min_r})
                    lines[f][i] = json.dumps(rec, ensure_ascii=False)
                    edited = True
            if edited:
                f.write_text("\n".join(lines[f]) + "\n", encoding="utf-8")
        account.trades = trades
        account.save()
        print(f"  aplicado (copia en {backup})")
        source.close()
    if not args.aplicar:
        print("\n(Solo muestra. Con el bot del perfil parado, --aplicar reescribe los cierres y la cuenta.)")


if __name__ == "__main__":
    main()
