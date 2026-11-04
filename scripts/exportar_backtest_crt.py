"""Backtest del CRT por BPR para la ventana Backtest del bot: iFVG y FVG de sentido contrario, los dos de 15 min, los dos de 5 o FVG de 15 con iFVG de 5 (en ese orden), una sola entrada.

Para cada mercado busca los setups con el motor de la skill (`engine.find_zone_setups`: iFVG invertido, pullback a la zona común, cierre con cuerpo sobre el
CISD, entrada a la apertura de la vela siguiente de ese TF; stop en el extremo del sweep) y los simula con objetivo 1R, 2R (el del bot) y 3R, con BE a +1R.
Cada TF del iFVG (5 y 15 min) se simula por separado, una operación a la vez por mercado; el TF del FVG normal queda en la columna `t` para filtrar.
A cada operación le pone la TBR en cuyo horario se da la entrada (Asia 20:00-00:00, London 02:00-05:00, NY Open 10:00-12:00 NY; el resto, «Fuera de TBR»).
Coste = spread supuesto (índices 1,5 pb, forex 0,7 pb: los parquet no traen el spread). Guarda las operaciones en analisis/crt_operaciones.pkl y SUSTITUYE los
grupos del perfil `crt` (Índices y Forex) de tradingbot/skills/stats/backtest.json.gz sin tocar el resto del fichero.

Uso (desde la raíz del proyecto):
    uv run --with pyarrow python scripts/descargar_velas.py --tf 5m      # y 15m: velas de MT5 (solo lectura) en analisis/<tf>/puprime
    uv run --with pyarrow python scripts/exportar_backtest_crt.py --simular    # simula y guarda analisis/crt_operaciones.pkl (unos minutos)
    uv run --with pyarrow python scripts/exportar_backtest_crt.py              # escribe los grupos en backtest.json.gz
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

from tradingbot.skills.crt import engine                                               # noqa: E402

AHEAD = 7 * 3600                                                                       # servidor del broker = NY + 7 h
OUT = ROOT / "tradingbot" / "skills" / "stats" / "backtest.json.gz"
TRADES = ROOT / "analisis" / "crt_operaciones.pkl"
DATA = ROOT / "analisis"
PROFILE, PROFILE_NAME = "crt", "CRT"
LTFS = (5, 15)                                                                          # TF del iFVG
ENTRIES = {1: "A la apertura de la vela siguiente al cierre con cuerpo sobre el CISD"}
# Objetivos: código -> (nombre, regla); BE a +1R en todos (como el bot)
TARGETS = {1: ("1R", engine.Rule(rr=1.0, be_at=1.0)), 2: ("2R", engine.Rule(rr=2.0, be_at=1.0)), 3: ("3R", engine.Rule(rr=3.0, be_at=1.0))}
GROUPS = {"indices": ("Índices", ("NAS100.s", "SP500.s", "DJ30.s")), "forex": ("Forex", ("EURUSD", "GBPUSD"))}
SINCE = {"indices": "2024-01-01", "forex": "2024-02-01"}                                 # el histórico del backtest empieza aquí aunque haya velas anteriores
SPREAD_BP = {"indices": 1.5, "forex": 0.7}
MTF_BIT = {15: 1, 5: 2}                                                                 # columna t: TF del FVG normal
ZONES = ("Asia", "London", "NY Open", "Fuera de TBR")
TBR_HOURS = (("Asia", 20 * 60, 24 * 60), ("London", 2 * 60, 5 * 60), ("NY Open", 10 * 60, 12 * 60))     # TBR de tradingbot.env
OUTCOMES = ["objetivo", "stop", "breakeven", "tiempo"]
OUTCOME_OF = {"objetivo": "objetivo", "stop": "stop", "BE": "breakeven", "sesión": "tiempo", "fin de datos": "tiempo"}
EPOCH = pd.Timestamp("1970-01-01")
INVALID_REASONS = ["sin pullback a la zona común", "sin CISD tras el toque"]
SL_REASONS = ["setup OK sin entrada: el stop supera el máximo permitido"]
NO_ENTRY_REASONS = ["setup OK sin entrada: el precio no volvió a la zona común", "sin BPR (iFVG y FVG de sentido contrario)",
                    "BPR sin retest válido y cierre sobre el CISD", "BPR sin invertirse el iFVG"]


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


# -- simulación ----------------------------------------------------------------------------------------------
def load(tf: int, sym: str) -> pd.DataFrame:
    df = pd.read_parquet(DATA / f"{tf}m" / "puprime" / f"{sym}.parquet")[["ts", "open", "high", "low", "close"]]
    return df.sort_values("ts").drop_duplicates("ts").reset_index(drop=True)


def trade_row(ts: np.ndarray, st: dict, ep: dict, res: dict, kind: str) -> dict:
    """La fila del backtest de una operación (`ts`: horas de las velas del TF del iFVG)."""
    sgn, j = st["sign"], res["exit_index"]
    price = abs(ep["entry"])
    cost = price * SPREAD_BP[kind] / 1e4 / ep["risk"]
    m, zb, zt, formed = st["zones"][0]
    first = formed - 3 * m * 60                                                         # primera vela del FVG normal
    k = st["kf"]
    row = {"entrada (NY)": pd.Timestamp(int(ts[ep["start"]]) - AHEAD, unit="s"), "cierre (NY)": pd.Timestamp(int(ts[j]) - AHEAD, unit="s"),
           "dirección": st["dirección"], "entrada": sgn * ep["entry"], "stop": sgn * st["stop"], "objetivo": sgn * res["target"],
           "salida": sgn * res["exit_price"], "riesgo": ep["risk"], "riesgo %": 100 * ep["risk"] / price, "cómo": res["cómo"],
           "R bruto": res["gross"], "coste (R)": cost, "R neto": res["gross"] - cost, "C2": st["C2"], "t": MTF_BIT[m],
           "iFVG bajo": min(sgn * st["ifvg"][0], sgn * st["ifvg"][1]), "iFVG alto": max(sgn * st["ifvg"][0], sgn * st["ifvg"][1]),
           "CISD": sgn * st["level"], "t iFVG": int(ts[k - 2]), "t inversión": int(ts[st["inv"]]), "t CISD": int(ts[st["jc"]]),
           "t extremo": int(ts[st["ih"]]), "t secuencia": int(ts[k - 1]), "t vuelta": int(ts[st["jt"]])}
    for tf in MTF_BIT:
        mine = tf == m
        row[f"FVG{tf} bajo"] = min(sgn * zb, sgn * zt) if mine else float("nan")
        row[f"FVG{tf} alto"] = max(sgn * zb, sgn * zt) if mine else float("nan")
        row[f"FVG{tf} t"] = int(first) if mine else 0
    return row


def simulate() -> pd.DataFrame:
    rows, funnels, data, invalid, valid, noentry, slbig = [], [], [], [], [], [], []
    for gkey, (gname, symbols) in GROUPS.items():
        kind = "indices" if gkey == "indices" else "forex"
        base = engine.INDICES if kind == "indices" else engine.FOREX
        cfg = engine.Cfg(base.htf_min, base.origin, base.session_end, AHEAD)
        for sym in symbols:
            series = {m: load(m, sym) for m in engine.ZONE_TFS}
            start = max(max(int(d["ts"].iloc[0]) for d in series.values()),            # el tramo común a los dos TF, desde la fecha fija del histórico
                        int(pd.Timestamp(SINCE[kind]).timestamp()) + AHEAD)
            series = {m: d[d["ts"] >= start].reset_index(drop=True) for m, d in series.items()}
            views = {m: {1: engine.view(d, 1), -1: engine.view(d, -1)} for m, d in series.items()}
            first15 = engine.m15_retests(series[15], cfg)                                # el BPR de M15 que ya tuvo su retest no se sustituye por uno de M5
            for ltf in LTFS:
                t0 = time.time()
                fvg = {m: v for m, v in series.items() if m >= ltf}
                setups, funnel = engine.find_zone_setups(series[ltf], series[ltf], ltf, cfg, fvg)
                ts = series[ltf]["ts"].to_numpy().astype(np.int64)
                if ltf == 5:
                    setups[:] = [x for x in setups if int(ts[x["jc"]]) < first15.get((x["C2"], x["sign"]), 1 << 62)]
                valid += [{"grupo": gkey, "mercado": sym, "C2": s["C2"], "d": int(s["sign"] > 0)} for s in setups]
                invalid += [{"grupo": gkey, "mercado": sym, "ltf": ltf, "C2": x["C2"], "d": int(x["sign"] > 0), "motivo": x["motivo"],
                             "t extremo": int(ts[x["ih"]]), "precio": x["sign"] * x["stop"]} for x in setups.invalid]
                noentry += [{"grupo": gkey, "mercado": sym, "ltf": ltf, "C2": x["C2"], "d": int(x["sign"] > 0), "motivo": NO_ENTRY_REASONS[0],
                             "t extremo": int(ts[x["ih"]]), "precio": x["sign"] * x["stop"]} for x in setups.no_entry]
                noentry += [{"grupo": gkey, "mercado": sym, "ltf": ltf, "C2": x["C2"], "d": int(x["sign"] > 0), "motivo": x["motivo"],
                             "t extremo": int(ts[x["ih"]]), "precio": x["sign"] * x["stop"]} for x in setups.nosetup]
                entries = 0
                for code, (_, rule) in TARGETS.items():
                    busy, mine = -1, []
                    for st in setups:                                                   # por la hora del cierre sobre el CISD
                        L = views[ltf][st["sign"]]
                        ep = engine.entry_point(L, st, 1, ltf, rule, cfg)
                        if ep is None:
                            if code == 2 and engine.sl_blocked(L, st, 1, ltf, rule, cfg) is not None:      # habría entrada, pero el stop supera el máximo
                                slbig.append({"grupo": gkey, "mercado": sym, "ltf": ltf, "C2": st["C2"], "d": int(st["sign"] > 0), "motivo": SL_REASONS[0],
                                              "t extremo": int(ts[st["ih"]]), "precio": st["sign"] * st["stop"]})
                            continue
                        res = engine.manage(L, st, ep, rule)
                        if res is None or int(ts[ep["start"]]) < busy:                  # una operación a la vez por mercado y TF
                            continue
                        busy = int(ts[res["exit_index"]])
                        mine.append(trade_row(ts, st, ep, res, kind))
                    if code == 2:
                        entries = len(mine)
                    if mine:
                        rows.append(pd.DataFrame(mine).assign(grupo=gkey, mercado=sym, ltf=ltf, entrada_modelo=1, objetivo_cod=code))
                funnels.append({"grupo": gkey, "mercado": sym, "ltf": ltf, **funnel, "entradas": entries})
                data.append({"grupo": gkey, "mercado": sym, "ltf": ltf, "velas": len(series[ltf]),
                             "desde": pd.Timestamp(int(ts[0]) - AHEAD, unit="s"), "hasta": pd.Timestamp(int(ts[-1]) - AHEAD, unit="s")})
                print(f"{sym} iFVG M{ltf}: {len(setups)} setups, {entries} operaciones a 2R ({time.time() - t0:.0f} s)", flush=True)
    trades = pd.concat(rows, ignore_index=True)
    trades["zona"] = tbr_zone(trades["entrada (NY)"])
    TRADES.parent.mkdir(exist_ok=True)
    pd.to_pickle({"operaciones": trades, "embudo": pd.DataFrame(funnels), "datos": pd.DataFrame(data),
                  "invalidos": pd.DataFrame(invalid), "validos": pd.DataFrame(valid), "sinsetup": pd.DataFrame(noentry), "slgrande": pd.DataFrame(slbig)}, TRADES)
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
            "t": t["t"].astype(int).tolist(), "q": t["objetivo_cod"].astype(int).tolist(),
            "pe": floats(t["entrada"], 5), "ps": floats(t["stop"], 5), "pt": floats(t["objetivo"], 5),        # entrada, stop y objetivo
            "pa": floats(t["iFVG bajo"], 5), "pb": floats(t["iFVG alto"], 5), "pc": floats(t["CISD"], 5),     # iFVG y CISD
            "ti": ny_min(t["t iFVG"]), "tv": ny_min(t["t inversión"]), "tj": ny_min(t["t CISD"]), "th": ny_min(t["t extremo"]),
            "tq": ny_min(t["t secuencia"]), "tt": ny_min(t["t vuelta"]),                                        # horas de cada paso
            **{f"f{tf}{k}": v for tf in MTF_BIT for k, v in (
                ("a", floats(t[f"FVG{tf} bajo"], 5)), ("b", floats(t[f"FVG{tf} alto"], 5)),
                ("t", [-1 if x == 0 else (int(x) - AHEAD) // 60 for x in t[f"FVG{tf} t"]]))},                  # el FVG normal en su TF
            "c": ((t["C2"].astype(np.int64) - AHEAD) // 60).tolist(),                       # inicio de la vela HTF del sweep (minutos NY)
            "h": near_hour(pd.to_datetime(t["entrada (NY)"])).tolist(),
            "r": floats(t["R neto"]), "k": floats(t["coste (R)"]), "rk": floats(t["riesgo %"], 3), "v": held.round().astype(int).tolist()}
    combos = {f"{ltf}:1": f"iFVG M{ltf}" for ltf in LTFS}
    funnel = saved["embudo"][saved["embudo"]["grupo"] == gkey]
    data = saved["datos"][saved["datos"]["grupo"] == gkey]
    return {
        "key": f"{PROFILE}:{gkey}", "nombre": gname, "tipo": "crt", "perfil": PROFILE, "perfil_nombre": PROFILE_NAME,
        "fichero": TRADES.name, "cats": cats, "ops": cols, "patrones": [PROFILE_NAME], "filtros": combos, "actualizado": updated,
        "descripcion": "CRT por zona común · sweep de C1 en C2 (H3 en índices, H4 en forex) → FVG normal (M15 o M5) + iFVG (M15 o M5) que se solapan → "
                       "iFVG invertido, pullback a la zona común y cierre con cuerpo sobre el CISD · stop en el extremo del sweep · spread supuesto",
        "ltf": list(LTFS), "entradas": {str(e): n for e, n in ENTRIES.items()},
        "datos": [{"mercado": f"{r['mercado']} · M{r['ltf']}", "velas M15": int(r["velas"]), "desde (NY)": r["desde"].strftime("%Y-%m-%d"),
                   "hasta (NY)": r["hasta"].strftime("%Y-%m-%d"), "TBR evaluadas": None} for _, r in data.iterrows()],
        "embudo_crt": [{"mercado": r["mercado"], "ltf": int(r["ltf"]), "sweeps": int(r["velas HTF con sweep"]),
                        "fvg": int(r["con FVG de MTF y de LTF con zona común"]), "toque": int(r["con pullback a la zona"]),
                        "ifvg": int(r["con CISD"]), "e1": int(r["entradas"]), "inv": int(r["invalidados"])}
                       for _, r in funnel.iterrows()],
        "sl_grande": marks_cols(saved, "slgrande", gkey, markets, SL_REASONS, []),
        "invalidos": marks_cols(saved, "invalidos", gkey, markets, INVALID_REASONS, ["validos"]),
        "sin_setup": marks_cols(saved, "sinsetup", gkey, markets, NO_ENTRY_REASONS, ["validos", "invalidos"]),
        "metodologia": methodology(gkey)}


def marks_cols(saved: dict, table: str, gkey: str, markets: list[str], reasons: list[str], skip: list[str]) -> dict:
    """Columnas de los sweeps invalidados o «sin entrada» para marcarlos en el gráfico: una fila por vela C2 y dirección, solo si ningún TF dio
    operación válida en ella (ni invalidada, en los «sin entrada»); si varios TF coinciden vale el primero."""
    df = saved.get(table)
    if df is None or not len(df):
        return {}
    df = df[df["grupo"] == gkey]
    taken = set()
    for key in skip:
        other = saved.get(key)
        if other is not None and len(other):
            other = other[other["grupo"] == gkey]
            taken |= set(map(tuple, other[["mercado", "C2", "d"]].to_numpy().tolist()))
    df = df[[(m, c, d) not in taken for m, c, d in df[["mercado", "C2", "d"]].to_numpy().tolist()]]
    df = df.assign(_mo=df["motivo"].map({r: i for i, r in enumerate(reasons)})).sort_values(["mercado", "C2", "d", "_mo", "ltf"]).drop_duplicates(["mercado", "C2", "d"]).reset_index(drop=True)
    df = df[df["mercado"].isin(markets)].reset_index(drop=True)
    return {"m": df["mercado"].map({m: i for i, m in enumerate(markets)}).astype(int).tolist(),
            "c": ((df["C2"].astype(np.int64) - AHEAD) // 60).tolist(), "d": df["d"].astype(int).tolist(),
            "th": ny_min(df["t extremo"]), "ps": floats(df["precio"], 5),
            "mo": df["motivo"].map({r: i for i, r in enumerate(reasons)}).astype(int).tolist(), "motivos": list(reasons)}


def methodology(gkey: str) -> list[list[str]]:
    htf = "H3 (velas alineadas a las 18:00 NY)" if gkey == "indices" else "H4 (velas alineadas a las 17:00 NY)"
    close = "18:00" if gkey == "indices" else "17:00"
    return [
        ["Qué es", "CRT por zona común: Candle Range Theory con un doble FVG (FVG normal + iFVG) dentro de la vela C2. Backtest con el mismo motor que la "
                   "skill (tradingbot/skills/crt/engine.py, find_zone_setups). Las TBR solo sirven para clasificar cada entrada."],
        ["Sweep", f"Una vela {htf} (C2) toma con una mecha el máximo (mínimo) de la anterior (C1); si tomó antes el otro extremo, el sweep es el del otro "
                  "lado. El extremo del sweep es su máximo vigente: uno nuevo reinicia el patrón."],
        ["Doble FVG", "Un iFVG (nacido en C1 o en C2; M15 o M5, de TF igual o menor que el del FVG) y un FVG normal de sentido contrario nacido en C2 (M15 o M5) que se solapan: el hueco que "
                      "comparten es la zona común. El primero de los dos en nacer tiene que seguir sin cerrarse del todo (con mecha o cuerpo) hasta que empieza "
                      "a formarse el segundo."],
        ["iFVG e inversión", "El iFVG se invierte cuando una vela cierra al otro lado de su base. CISD = el extremo de la vela de desplazamiento que lo creó."],
        ["Pullback", "Con el iFVG invertido y los dos FVG formados, el precio vuelve a la zona común: una vela la toca con la mecha sin cerrar al otro lado. "
                     "Si una vela cierra con cuerpo al otro lado de la zona, esa pareja queda invalidada y se busca otra."],
        ["Entrada", "La primera vela que cierra con cuerpo más allá del CISD tras el pullback da la entrada: a la apertura de la vela siguiente del TF "
                    "del iFVG (el CISD y la entrada son de ese TF). Antes de que cierre C2."],
        ["Objetivos", "Tres backtests: 1R, 2R (el del bot) y 3R, los tres con breakeven al tocar +1R."],
        ["Gestión", f"Stop en el extremo del sweep; si la distancia de la entrada al stop supera el máximo (125 puntos en índices, 25 pips en forex) no se entra y se marca «SL grande». A las {close} NY no se abren entradas y lo abierto se cierra. Una operación a la "
                    "vez por mercado y TF del iFVG. Stop y objetivo en la misma vela: cuenta el stop."],
        ["Invalidados", "Si el precio llega al extremo opuesto de C1 sin completar el patrón, no se opera y se marca en el gráfico. El «setup OK sin entrada» "
                        "(zona común e iFVG invertido pero sin pullback) también se marca."],
        ["TBR", "Una entrada está «dentro de una TBR» si su hora cae en el horario de Asia (20:00-00:00), London (02:00-05:00) o NY Open "
                "(10:00-12:00), hora de Nueva York; si no, «Fuera de TBR». Es la hora de la entrada, no del sweep."],
        ["Hora en punto", "Cada entrada lleva además la hora en punto a la que está pegada si dista 15 min o menos (03:00 vale de 02:45 a 03:15). "
                          "Se puede combinar con la TBR."],
        ["Costes", "Spread supuesto por operación (índices 1,5 pb, forex 0,7 pb del precio de entrada; R neto = R bruto - coste / riesgo): las velas "
                   "descargadas no traen el spread."],
        ["Datos", "Velas M5 y M15 de MT5 (PUPrime) desde enero de 2024 (índices) o febrero de 2024 (forex). El HTF sale de las M5. El filtro «TF del FVG» "
                  "separa las operaciones según el TF del FVG normal (M15 o M5)."],
        ["Límites", "Cada objetivo y TF del iFVG es una prueba distinta sobre los mismos setups: con tantas combinaciones algún resultado "
                    "positivo puede ser azar. Mira la consistencia entre mercados y periodos."]]


def write(saved: dict) -> None:
    raw = json.loads(gzip.decompress(OUT.read_bytes()).decode("utf-8"))
    raw["grupos"] = [g for g in raw["grupos"] if g.get("perfil") != PROFILE]
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for gkey in GROUPS:
        raw["grupos"].append(group_json(gkey, saved, updated))
    OUT.write_bytes(gzip.compress(json.dumps(raw, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), 9, mtime=0))
    n = sum(len(g["ops"]["e"]) for g in raw["grupos"] if g.get("perfil") == PROFILE)
    print(f"{OUT} ({OUT.stat().st_size / 1024:.0f} KB): grupos CRT con {n} operaciones")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--simular", action="store_true", help="simula y guarda analisis/crt_operaciones.pkl antes de exportar")
    args = ap.parse_args()
    if args.simular or not TRADES.exists():
        simulate()
    write(pd.read_pickle(TRADES))


if __name__ == "__main__":
    main()
