"""Backtest completo de CRT-C2 para la ventana Backtest del bot: las 2 entradas, los 2 LTF (M5, M3), índices y forex.

Para cada mercado y LTF busca los setups con el motor (tradingbot/skills/crt/engine.py, find_c2_setups) y simula las dos entradas (1 orden límite
en el nivel de C1, 2 a mercado tras el retesteo del FVG). A cada operación le pone la TBR en cuyo horario se da la entrada (Asia 20:00-00:00,
London 02:00-05:00, NY Open 10:00-12:00 NY; el resto, «Fuera de TBR»). Guarda las operaciones en analisis/crt_operaciones.pkl y AÑADE dos grupos
(Índices y Forex, perfil «CRT-C2») a tradingbot/skills/stats/backtest.json.gz sin tocar el resto del fichero.

Uso (desde la raíz del proyecto):
    uv run python scripts/exportar_backtest_crt.py --descargar     # velas M5 y M3 de MT5 que falten (solo lectura)
    uv run python scripts/exportar_backtest_crt.py --simular       # simula y guarda analisis/crt_operaciones.pkl (tarda unos minutos)
    uv run python scripts/exportar_backtest_crt.py                 # escribe los grupos en backtest.json.gz
    uv run python scripts/exportar_backtest_crt.py --simular --sin-sesgo --cuartos 2    # otras reglas: sin sesgo D1, límite de 2 cuartos
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import backtest_crt as bc                                                              # noqa: E402
from backtest_patrones import AHEAD                                                    # noqa: E402
from tradingbot.skills.crt import engine                                               # noqa: E402

OUT = ROOT / "tradingbot" / "skills" / "stats" / "backtest.json.gz"
TRADES = ROOT / "analisis" / "crt_operaciones.pkl"
PROFILE, PROFILE_NAME = "crt", "CRT-C2"
LTFS = (3, 5)
ENTRIES = {1: "Orden límite en el nivel de C1", 2: "A mercado tras el retesteo del FVG"}
# Objetivos: código -> (nombre, regla). 1R sin BE; 2R con BE a 1R (el del bot); extremo opuesto de C1 con BE a 1R
TARGETS = {1: ("1R", engine.Rule(rr=1.0, be_at=0.0)), 2: ("2R", engine.Rule()),
           3: ("Extremo de C1", engine.Rule(target_c1=True, min_rr=2.0))}       # regla 1: si el extremo de C1 da menos de 2 R, se descarta
GROUPS = {"indices": ("Índices", [("puprime", "NAS100"), ("puprime", "SP500"), ("puprime", "DJ30")]),
          "forex": ("Forex", [("puprime", "EURUSD"), ("puprime", "GBPUSD")])}
ZONES = ("Asia", "London", "NY Open", "Fuera de TBR")
TBR_HOURS = (("Asia", 20 * 60, 24 * 60), ("London", 2 * 60, 5 * 60), ("NY Open", 10 * 60, 12 * 60))     # TBR de tradingbot.env
OUTCOMES = ["objetivo", "stop", "breakeven", "tiempo"]
OUTCOME_OF = {"objetivo": "objetivo", "stop": "stop", "BE": "breakeven", "sesión": "tiempo", "fin de datos": "tiempo"}
EPOCH = pd.Timestamp("1970-01-01")
RULES = {"sesgo": True, "cuartos": 1.0}                                                 # sesgo D1 y límite de profundidad (cuartos de C1)


def tbr_zone(ts: pd.Series) -> pd.Series:
    """TBR en cuyo horario cae la hora de entrada (NY); si no cae en ninguna, «Fuera de TBR»."""
    minute = ts.dt.hour * 60 + ts.dt.minute
    out = pd.Series("Fuera de TBR", index=ts.index, dtype=object)
    for name, a, b in TBR_HOURS:
        out[(minute >= a) & (minute < b)] = name
    return out


def near_hour(ts: pd.Series) -> pd.Series:
    """Hora en punto (0-23) a la que está pegada la hora de entrada si dista 15 min o menos (03:00 vale de 02:45 a 03:15); si no, -1."""
    minute, hour = ts.dt.minute, ts.dt.hour
    return pd.Series(np.where(minute <= 15, hour, np.where(minute >= 45, (hour + 1) % 24, -1)), index=ts.index).astype(int)


# -- descarga y simulación ---------------------------------------------------------------------------
def download_missing() -> None:
    for _, (_, symbols) in GROUPS.items():
        for profile, want in symbols:
            for tf in (5, 3):
                path = bc.cache_path(profile, want, tf)
                if path.exists():
                    continue
                try:
                    bc.download(profile, want, tf)
                except Exception as err:                                               # noqa: BLE001
                    print(f"  fallo {profile} {want} M{tf}: {err}", flush=True)


def execute_c2(views: dict, st: dict, mode: int, rule: engine.Rule) -> dict | None:
    """Entrada y gestión de un setup CRT-C2 (espacio del corto) y su fila del backtest, o None si no hay entrada."""
    sgn, cfg = st["sign"], bc.CFG
    L = views[sgn]
    ep = engine.c2_entry(L, st, mode, cfg)
    if ep is None:
        return None
    sub = st["lim"] if mode == 1 else st["mkt"]
    st2 = {**st, "stop": sub["stop"]}
    La = engine.c2_view(L, sgn, mode)                       # límite: velas con el spread del ask en un corto (ver c2_view)
    ts, start, entry, hx, risk = L["ts"], ep["start"], ep["entry"], sub["stop"], ep["risk"]
    reach = engine.max_r(La, st2, ep)
    if rule.target_c1 and rule.min_rr and engine.planned_rr(st2, ep) < rule.min_rr - 1e-9:       # el extremo de C1 queda demasiado cerca
        return {"_skip": True, "entrada (NY)": pd.Timestamp(int(ts[start]) - AHEAD, unit="s"), "dirección": st["dirección"],
                "entrada": sgn * entry, "stop": sgn * hx, "objetivo": sgn * st["c1"][0], "riesgo": risk,
                "R planificado": engine.planned_rr(st2, ep), "R máx": reach, "C2": st["C2"]}
    mg = engine.manage(La, st2, ep, rule)
    if mg is None:
        return None
    j = mg["exit_index"]
    cost = 0.0 if mode == 1 else mg["cost"]                 # límite: el spread ya está en las velas; mercado: spread de la vela / riesgo
    fvg = sub["fvg"]
    level = st["c1"][1] if mode == 1 else sub["level"]      # límite: el nivel de C1 donde espera la orden; mercado: el mínimo de la vela de retesteo
    t_trig = ts[sub["jl"]] if mode == 1 else ts[sub["jm"]]
    t_back = ts[sub["below"]] if mode == 1 else ts[sub["jt"]]
    return {"entrada (NY)": pd.Timestamp(int(ts[start]) - AHEAD, unit="s"), "cierre (NY)": pd.Timestamp(int(ts[j]) - AHEAD, unit="s"),
            "dirección": st["dirección"], "FVG MTF": "", "C2 cierra dentro": st["inside"], "entrada": sgn * entry,
            "stop": sgn * hx, "objetivo": sgn * mg["target"], "salida": sgn * mg["exit_price"], "riesgo": risk,
            "riesgo %": 100 * risk / abs(entry), "cómo": mg["cómo"], "R bruto": mg["gross"], "coste (R)": cost,
            "R neto": mg["gross"] - cost, "R planificado": (entry - mg["target"]) / risk, "R máx": reach,
            "C2": st["C2"], "_ts_entry": int(ts[start]), "_ts_exit": int(ts[j]),
            # para auditar en el gráfico: el FVG de LTF (en vez del iFVG), el nivel de entrada y las horas de cada paso (hora de servidor)
            "iFVG bajo": min(sgn * fvg[0], sgn * fvg[1]), "iFVG alto": max(sgn * fvg[0], sgn * fvg[1]),
            "CISD": sgn * level, "t iFVG": int(ts[sub["ih"]]), "t inversión": int(ts[fvg[2]]), "t CISD": int(t_trig),
            "t extremo": int(ts[sub["ih"]]), "t secuencia": int(ts[sub["ih"]]), "t vuelta": int(t_back),
            **{f"FVG{tf} bajo": float("nan") for tf in engine.MTF}, **{f"FVG{tf} alto": float("nan") for tf in engine.MTF},
            **{f"FVG{tf} t": 0 for tf in engine.MTF}}


def run_c2(ltf: pd.DataFrame, setups: list, mode: int, rule: engine.Rule) -> pd.DataFrame:
    """Todas las operaciones de una entrada y un objetivo: por hora de entrada, y si ya hay una abierta no se abre otra (tampoco al revés)."""
    views = {1: engine.view(ltf, 1), -1: engine.view(ltf, -1)}
    skipped, cands = [], []
    for st in setups:
        r = execute_c2(views, st, mode, rule)
        if r is None:
            continue
        if r.get("_skip"):
            skipped.append(r)
            continue
        cands.append(r)
    rows, last_exit = [], 0
    for r in sorted(cands, key=lambda x: x["_ts_entry"]):
        if r.pop("_ts_entry") <= last_exit:
            continue
        last_exit = r.pop("_ts_exit")
        rows.append(r)
    out = pd.DataFrame(rows)
    out.attrs["descartados"] = skipped
    return out


def simulate() -> pd.DataFrame:
    rows, funnels, data, invalid, valid = [], [], [], [], []
    for gkey, (gname, symbols) in GROUPS.items():
        bc.configure("indices" if gkey == "indices" else "forex")                    # fija el mercado (H3 / H4 y cierre de sesión)
        for profile, want in symbols:
            sym, base = pd.read_pickle(bc.cache_path(profile, want, 5))
            for tf in LTFS:
                _, ltf = pd.read_pickle(bc.cache_path(profile, want, tf))
                t0 = time.time()
                setups, funnel = engine.find_c2_setups(base, ltf, bc.CFG, bias=RULES["sesgo"], cuartos=RULES["cuartos"])
                row = {"grupo": gkey, "mercado": sym, "ltf": tf, **funnel}
                valid += [{"grupo": gkey, "mercado": sym, "C2": s["C2"], "d": int(s["sign"] > 0)} for s in setups]
                invalid += [{"grupo": gkey, "mercado": sym, "ltf": tf, "C2": x["C2"], "d": int(x["sign"] > 0), "motivo": x["motivo"],
                             "t extremo": int(ltf["ts"].iloc[x["ih"]]), "precio": x["sign"] * x["stop"]} for x in setups.invalid]
                for entry in ENTRIES:
                    for code, (_, rule) in TARGETS.items():
                        t = run_c2(ltf, setups, entry, rule)
                        if code == 2:
                            row[f"entrada {entry}"] = len(t)
                        if len(t):
                            rows.append(t.assign(grupo=gkey, mercado=sym, ltf=tf, entrada_modelo=entry, objetivo_cod=code))
                funnels.append(row)
                data.append({"grupo": gkey, "mercado": sym, "ltf": tf, "velas": len(ltf),
                             "desde": pd.Timestamp(int(ltf["ts"].iloc[0]) - AHEAD, unit="s"),
                             "hasta": pd.Timestamp(int(ltf["ts"].iloc[-1]) - AHEAD, unit="s")})
                print(f"{sym} M{tf}: {len(setups)} setups, " + ", ".join(f"e{e}={row[f'entrada {e}']}" for e in ENTRIES)
                      + f" ({time.time() - t0:.0f} s)", flush=True)
    trades = pd.concat(rows, ignore_index=True)
    trades["zona"] = tbr_zone(trades["entrada (NY)"])
    TRADES.parent.mkdir(exist_ok=True)
    pd.to_pickle({"operaciones": trades, "embudo": pd.DataFrame(funnels), "datos": pd.DataFrame(data), "reglas": dict(RULES),
                  "invalidos": pd.DataFrame(invalid), "validos": pd.DataFrame(valid)}, TRADES)
    print(f"{len(trades)} operaciones -> {TRADES}")
    return trades


# -- exportación ---------------------------------------------------------------------------------------
def ny_min(s: pd.Series) -> list[int]:
    """Minutos NY desde 1970 de una hora de servidor (segundos)."""
    return ((s.astype(np.int64) - AHEAD) // 60).tolist()


def minutes(s: pd.Series) -> list[int]:
    return ((pd.to_datetime(s) - EPOCH) // pd.Timedelta(minutes=1)).astype(np.int64).tolist()


def floats(s: pd.Series, digits: int = 6) -> list:
    return [None if math.isnan(v) or math.isinf(v) else round(float(v), digits) for v in s.to_numpy(dtype=float)]


def group_json(gkey: str, saved: dict, updated: str) -> dict:
    gname, symbols = GROUPS[gkey]
    t = saved["operaciones"]
    t = t[t["grupo"] == gkey].reset_index(drop=True)
    markets = sorted(t["mercado"].unique())
    cats = {"m": markets, "o": OUTCOMES, "z": list(ZONES), "p": [PROFILE_NAME]}
    outcome = t["cómo"].map(OUTCOME_OF)
    held = ((pd.to_datetime(t["cierre (NY)"]) - pd.to_datetime(t["entrada (NY)"])) // pd.Timedelta(minutes=1)) / t["ltf"]
    cols = {"m": t["mercado"].map({m: i for i, m in enumerate(markets)}).astype(int).tolist(),
            "o": outcome.map({o: i for i, o in enumerate(OUTCOMES)}).astype(int).tolist(),
            "z": t["zona"].map({z: i for i, z in enumerate(ZONES)}).astype(int).tolist(),
            "d": (t["dirección"] == "short").astype(int).tolist(),
            "e": minutes(t["entrada (NY)"]), "x": minutes(t["cierre (NY)"]),
            "l": t["ltf"].astype(int).tolist(), "n": t["entrada_modelo"].astype(int).tolist(),
            "t": [0] * len(t), "q": t["objetivo_cod"].astype(int).tolist(),
            "pe": floats(t["entrada"], 5), "ps": floats(t["stop"], 5), "pt": floats(t["objetivo"], 5),        # entrada, stop y objetivo
            "pa": floats(t["iFVG bajo"], 5), "pb": floats(t["iFVG alto"], 5), "pc": floats(t["CISD"], 5),     # FVG de LTF y nivel de entrada
            "ti": ny_min(t["t iFVG"]), "tv": ny_min(t["t inversión"]), "tj": ny_min(t["t CISD"]), "th": ny_min(t["t extremo"]),
            "tq": ny_min(t["t secuencia"]), "tt": ny_min(t["t vuelta"]),                                                                    # horas de cada paso
            **{f"f{tf}{k}": v for tf in engine.MTF for k, v in (
                ("a", floats(t[f"FVG{tf} bajo"], 5)), ("b", floats(t[f"FVG{tf} alto"], 5)),
                ("t", [-1 if x == 0 else (int(x) - AHEAD) // 60 for x in t[f"FVG{tf} t"]]))},          # (sin FVG de MTF en CRT-C2)
            "c": ((t["C2"].astype(np.int64) - AHEAD) // 60).tolist(),                       # inicio de la vela HTF del sweep (minutos NY)
            "h": near_hour(pd.to_datetime(t["entrada (NY)"])).tolist(),
            "r": floats(t["R neto"]), "k": floats(t["coste (R)"]), "rk": floats(t["riesgo %"], 3), "v": held.round().astype(int).tolist()}
    combos = {f"{ltf}:{e}": f"M{ltf} · {e}. {name}" for ltf in LTFS for e, name in ENTRIES.items()}
    funnel = saved["embudo"][saved["embudo"]["grupo"] == gkey]
    data = saved["datos"][saved["datos"]["grupo"] == gkey]
    rules = saved.get("reglas", RULES)
    return {
        "key": f"{PROFILE}:{gkey}", "nombre": gname, "tipo": "crt", "perfil": PROFILE, "perfil_nombre": PROFILE_NAME,
        "fichero": TRADES.name, "cats": cats, "ops": cols, "patrones": [PROFILE_NAME], "filtros": combos, "actualizado": updated,
        "descripcion": "CRT-C2 · sweep H3 (H4 en forex) a favor de la tendencia D1 → FVG en LTF tras el máximo → cierre dentro de C1 → "
                       "retesteo · orden límite en el nivel de C1 o entrada a mercado · stop en el máximo del sweep · spread real",
        "ltf": list(LTFS), "entradas": {str(e): n for e, n in ENTRIES.items()},
        "datos": [{"mercado": f"{r['mercado']} · M{r['ltf']}", "velas M15": int(r["velas"]), "desde (NY)": r["desde"].strftime("%Y-%m-%d"),
                   "hasta (NY)": r["hasta"].strftime("%Y-%m-%d"), "TBR evaluadas": None} for _, r in data.iterrows()],
        "embudo_crt": [{"mercado": r["mercado"], "ltf": int(r["ltf"]), "sweeps": int(r["velas HTF con sweep"]),
                        "d1": int(r["contra la tendencia D1"]), "fvg": int(r["con FVG tras el extremo"]), "toque": int(r["con cierre dentro de C1"]),
                        "ifvg": int(r["con retesteo"]), "e1": int(r["entrada 1"]), "e2": int(r["entrada 2"]), "inv": int(r["invalidados"])}
                       for _, r in funnel.iterrows()],
        "invalidos": invalid_cols(saved, gkey, markets),
        "metodologia": methodology(gkey, rules)}


REASONS = list(engine.C2_REASONS)


def invalid_cols(saved: dict, gkey: str, markets: list[str]) -> dict:
    """Sweeps invalidados (profundidad excesiva o el precio llegó al extremo opuesto de C1 sin completar el patrón), para marcarlos en el gráfico.
    Una fila por vela C2 y dirección: solo si ningún LTF dio setup válido en ella (si varios los invalidan, vale el motivo del primero)."""
    inv, val = saved.get("invalidos"), saved.get("validos")
    if inv is None or not len(inv):
        return {}
    inv = inv[inv["grupo"] == gkey]
    if val is not None and len(val):
        ok = set(map(tuple, val[val["grupo"] == gkey][["mercado", "C2", "d"]].to_numpy().tolist()))
        inv = inv[[(m, c, d) not in ok for m, c, d in inv[["mercado", "C2", "d"]].to_numpy().tolist()]]
    inv = inv.sort_values(["mercado", "C2", "d", "ltf"]).drop_duplicates(["mercado", "C2", "d"]).reset_index(drop=True)
    inv = inv[inv["mercado"].isin(markets)].reset_index(drop=True)
    return {"m": inv["mercado"].map({m: i for i, m in enumerate(markets)}).astype(int).tolist(),
            "c": ((inv["C2"].astype(np.int64) - AHEAD) // 60).tolist(), "d": inv["d"].astype(int).tolist(),
            "th": ny_min(inv["t extremo"]), "ps": floats(inv["precio"], 5),
            "mo": inv["motivo"].map({r: i for i, r in enumerate(REASONS)}).astype(int).tolist(), "motivos": REASONS}


def methodology(gkey: str, rules: dict) -> list[list[str]]:
    htf = "H3 (velas alineadas a las 18:00 NY)" if gkey == "indices" else "H4 (velas alineadas a las 17:00 NY)"
    close = "18:00" if gkey == "indices" else "17:00"
    cuartos = rules.get("cuartos", 1.0)
    bias = ("Solo C2 a favor de la tendencia D1: cierre del día anterior por encima de su EMA30 con pendiente positiva en 5 días para los "
            "largos (por debajo y negativa para los cortos). Las demás no se operan ni se cuentan como invalidadas (columna «Contra D1» del embudo)."
            if rules.get("sesgo", True) else "Sin sesgo: se operan todas las C2 que barren un extremo de C1.")
    return [
        ["Qué es", "CRT-C2: Candle Range Theory operando dentro de la vela C2 (C1 = rango, C2 = manipulación, C3 = expansión). Backtest con el mismo "
                   "motor que la skill (tradingbot/skills/crt/engine.py, find_c2_setups). Las TBR solo sirven para clasificar cada entrada."],
        ["Patrón", f"Una vela {htf} (C2) toma con una mecha el máximo (mínimo) de la anterior (si tomó antes el otro extremo, el sweep es el del otro "
                   "lado). El extremo del sweep es su máximo vigente: uno nuevo reinicia el patrón. La vela siguiente al máximo, bajista, deja un "
                   "FVG bajista en el LTF (M5 o M3); el precio cierra por debajo del nivel de C1 y vuelve a tocar el FVG (vela de retesteo)."],
        ["Sesgo", bias],
        ["Profundidad", f"La profundidad del sweep (máximo menos nivel de C1) no puede superar {cuartos:g} cuarto(s) de la altura de C1, redondeado "
                        "al entero superior en pips (forex) o puntos (índices). Si lo supera, el setup queda invalidado («sweep demasiado profundo»)."],
        ["Invalidados", "También se invalida si el precio llega al extremo opuesto de C1 sin completar el patrón. No se opera y se marca en el "
                        "gráfico («Invalidado»). La columna Invalidados del embudo los cuenta."],
        ["Entradas", "1: venta límite en el nivel de C1; se llena cuando el precio vuelve a subir hasta él tras cerrar por debajo (si en la misma "
                     "vela supera el máximo, queda en pérdida). 2: a mercado, al cierre de la primera vela que cierra por debajo del mínimo de la "
                     "vela de retesteo. Las dos antes de que cierre C2. Cada una es un backtest."],
        ["Objetivos", "Tres variantes, cada una con su backtest: 1R (sin BE), 2R (a 1R el stop pasa a la entrada, el que usa el bot) y el "
                      "extremo opuesto de C1 (también con BE a 1R; si da menos de 2R, la operación se descarta). Si ese extremo ya está alcanzado "
                      "o por encima de la entrada, no hay operación."],
        ["Gestión", f"Stop en el máximo del sweep, sin límite de tamaño. A las {close} NY no se abren entradas y lo abierto se cierra. Una operación a "
                    "la vez por mercado, entrada y LTF. Stop y objetivo en la misma vela: cuenta el stop."],
        ["TBR", "Una entrada está «dentro de una TBR» si su hora cae en el horario de Asia (20:00-00:00), London (02:00-05:00) o NY Open "
                "(10:00-12:00), hora de Nueva York; si no, «Fuera de TBR». Es la hora de la entrada, no del sweep."],
        ["Hora en punto", "Cada entrada lleva además la hora en punto a la que está pegada si dista 15 min o menos (03:00 vale de 02:45 a 03:15). "
                          "Se puede combinar con la TBR."],
        ["Costes", "Entrada a mercado: spread real de MT5 en la vela de entrada, una vez por operación (R neto = R bruto - spread / riesgo). Orden "
                   "límite: las velas son del bid; un corto vende en el bid y recompra en el ask (stop y objetivo se ven en bid + spread), y un largo "
                   "compra en el ask (el límite exige bajar un spread más). El límite no ahorra el spread: lo paga por otro lado."],
        ["Datos", "Velas M5 y M3 de MT5 (PUPrime). El HTF y el D1 salen de las M5. En las M3 muchas velas traen el spread a 0, así que "
                  "el coste de las entradas a mercado en M3 puede estar subestimado."],
        ["Límites", "Cada entrada, objetivo y LTF es una prueba distinta sobre los mismos setups: con tantas combinaciones algún resultado "
                    "positivo puede ser azar. Mira la consistencia entre mercados, entradas y periodos."]]


def write(saved: dict) -> None:
    raw = json.loads(gzip.decompress(OUT.read_bytes()).decode("utf-8"))
    raw["grupos"] = [g for g in raw["grupos"] if g.get("perfil") != PROFILE]
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for gkey in GROUPS:
        raw["grupos"].append(group_json(gkey, saved, updated))
    OUT.write_bytes(gzip.compress(json.dumps(raw, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), 9, mtime=0))
    n = sum(len(g["ops"]["e"]) for g in raw["grupos"] if g.get("perfil") == PROFILE)
    print(f"{OUT} ({OUT.stat().st_size / 1024:.0f} KB): grupos CRT-C2 con {n} operaciones")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--descargar", action="store_true", help="descarga las velas M5 y M3 que falten y termina")
    ap.add_argument("--simular", action="store_true", help="simula y guarda analisis/crt_operaciones.pkl antes de exportar")
    ap.add_argument("--sin-sesgo", action="store_true", help="no filtra por la tendencia D1")
    ap.add_argument("--cuartos", type=float, default=1.0, help="límite de profundidad del sweep en cuartos de la altura de C1 (0 = sin límite)")
    args = ap.parse_args()
    RULES["sesgo"] = not args.sin_sesgo
    RULES["cuartos"] = args.cuartos if args.cuartos > 0 else 1e9
    if args.descargar:
        download_missing()
        return
    if args.simular or not TRADES.exists():
        simulate()
    write(pd.read_pickle(TRADES))


if __name__ == "__main__":
    main()
