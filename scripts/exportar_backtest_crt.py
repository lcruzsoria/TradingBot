"""Backtest completo de CRT para la ventana Backtest del bot: las 4 entradas, los 3 LTF (M5, M3, M1), índices y forex.

Para cada mercado y LTF busca los setups con el motor (tradingbot/skills/crt/engine.py, el mismo que usa la skill) y simula las tres
entradas (1 vela siguiente al CISD, 2 retesteo del iFVG, 3 primera vela sin mecha, 4 cierre del CISD). A cada operación le pone la TBR en cuyo horario se da la
entrada (Asia 20:00-00:00, London 02:00-05:00, NY Open 10:00-12:00 NY; el resto, «Fuera de TBR») y el timeframe del FVG de MTF que toca.
Guarda las operaciones en analisis/crt_operaciones.pkl y AÑADE dos grupos (Índices y Forex, perfil «CRT») a
tradingbot/skills/stats/backtest.json.gz sin tocar el resto del fichero.

Uso (desde la raíz del proyecto):
    uv run python scripts/exportar_backtest_crt.py --descargar     # velas M5, M3 y M1 de MT5 que falten (solo lectura)
    uv run python scripts/exportar_backtest_crt.py --simular       # simula y guarda analisis/crt_operaciones.pkl (tarda unos minutos)
    uv run python scripts/exportar_backtest_crt.py                 # escribe los grupos en backtest.json.gz
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
PROFILE, PROFILE_NAME = "crt", "CRT"
LTFS = (5, 3, 1)
ENTRIES = {1: "Vela siguiente al CISD", 2: "Retesteo del iFVG", 3: "Primera vela sin mecha", 4: "Cierre del CISD"}
# Objetivos: código -> (nombre, regla). 1R sin BE; 2R con BE a 1R (el del bot); extremo opuesto de C1 con BE a 1R
TARGETS = {1: ("1R", engine.Rule(rr=1.0, be_at=0.0)), 2: ("2R", engine.Rule()), 3: ("Extremo de C1", engine.Rule(target_c1=True))}
GROUPS = {"indices": ("Índices", [("puprime", "NAS100"), ("puprime", "SP500"), ("puprime", "DJ30")]),
          "forex": ("Forex", [("puprime", "EURUSD"), ("puprime", "GBPUSD")])}
ZONES = ("Asia", "London", "NY Open", "Fuera de TBR")
TBR_HOURS = (("Asia", 20 * 60, 24 * 60), ("London", 2 * 60, 5 * 60), ("NY Open", 10 * 60, 12 * 60))     # TBR de tradingbot.env
OUTCOMES = ["objetivo", "stop", "breakeven", "tiempo"]
OUTCOME_OF = {"objetivo": "objetivo", "stop": "stop", "BE": "breakeven", "sesión": "tiempo", "fin de datos": "tiempo"}
MTF_BITS = {"M15": 1, "M30": 2, "M60": 4}
EPOCH = pd.Timestamp("1970-01-01")


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


def mtf_bits(text: str) -> int:
    return sum(MTF_BITS[x] for x in str(text).split("/") if x in MTF_BITS)


# -- descarga y simulación ---------------------------------------------------------------------------
def download_missing() -> None:
    for _, (_, symbols) in GROUPS.items():
        for profile, want in symbols:
            for tf in (5, 3, 1):
                path = bc.cache_path(profile, want, tf)
                if path.exists():
                    continue
                try:
                    bc.download(profile, want, tf)
                except Exception as err:                                               # noqa: BLE001
                    print(f"  fallo {profile} {want} M{tf}: {err}", flush=True)


def simulate() -> pd.DataFrame:
    rows, funnels, data = [], [], []
    for gkey, (gname, symbols) in GROUPS.items():
        bc.configure("indices" if gkey == "indices" else "forex")                    # fija el mercado (H3 / H4 y cierre de sesión)
        for profile, want in symbols:
            sym, base = pd.read_pickle(bc.cache_path(profile, want, 5))
            for tf in LTFS:
                _, ltf = pd.read_pickle(bc.cache_path(profile, want, tf))
                t0 = time.time()
                setups, funnel = bc.find_setups(base, ltf, tf, engine.Rule())          # los setups no dependen del objetivo
                row = {"grupo": gkey, "mercado": sym, "ltf": tf, **funnel}
                for entry in ENTRIES:
                    for code, (_, rule) in TARGETS.items():
                        t = bc.run_variant(ltf, setups, entry, tf, rule)
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
    pd.to_pickle({"operaciones": trades, "embudo": pd.DataFrame(funnels), "datos": pd.DataFrame(data)}, TRADES)
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
    cats = {"m": markets, "o": OUTCOMES, "z": list(ZONES), "p": ["CRT"]}
    outcome = t["cómo"].map(OUTCOME_OF)
    held = ((pd.to_datetime(t["cierre (NY)"]) - pd.to_datetime(t["entrada (NY)"])) // pd.Timedelta(minutes=1)) / t["ltf"]
    cols = {"m": t["mercado"].map({m: i for i, m in enumerate(markets)}).astype(int).tolist(),
            "o": outcome.map({o: i for i, o in enumerate(OUTCOMES)}).astype(int).tolist(),
            "z": t["zona"].map({z: i for i, z in enumerate(ZONES)}).astype(int).tolist(),
            "d": (t["dirección"] == "short").astype(int).tolist(),
            "e": minutes(t["entrada (NY)"]), "x": minutes(t["cierre (NY)"]),
            "l": t["ltf"].astype(int).tolist(), "n": t["entrada_modelo"].astype(int).tolist(),
            "t": t["FVG MTF"].map(mtf_bits).astype(int).tolist(), "q": t["objetivo_cod"].astype(int).tolist(),
            "pe": floats(t["entrada"], 5), "ps": floats(t["stop"], 5), "pt": floats(t["objetivo"], 5),        # entrada, stop y objetivo
            "pa": floats(t["iFVG bajo"], 5), "pb": floats(t["iFVG alto"], 5), "pc": floats(t["CISD"], 5),     # iFVG invertido y nivel del CISD
            "ti": ny_min(t["t iFVG"]), "tv": ny_min(t["t inversión"]), "tj": ny_min(t["t CISD"]), "th": ny_min(t["t extremo"]),
            "tq": ny_min(t["t secuencia"]),                                                                    # horas de cada paso
            **{f"f{tf}{k}": v for tf in engine.MTF for k, v in (
                ("a", floats(t[f"FVG{tf} bajo"], 5)), ("b", floats(t[f"FVG{tf} alto"], 5)),
                ("t", [-1 if x == 0 else (int(x) - AHEAD) // 60 for x in t[f"FVG{tf} t"]]))},          # FVG de MTF: base, techo y primera vela
            "c": ((t["C2"].astype(np.int64) - AHEAD) // 60).tolist(),                       # inicio de la vela HTF del sweep (minutos NY)
            "h": near_hour(pd.to_datetime(t["entrada (NY)"])).tolist(),
            "r": floats(t["R neto"]), "k": floats(t["coste (R)"]), "rk": floats(t["riesgo %"], 3), "v": held.round().astype(int).tolist()}
    combos = {f"{ltf}:{e}": f"M{ltf} · {e}. {name}" for ltf in LTFS for e, name in ENTRIES.items()}
    funnel = saved["embudo"][saved["embudo"]["grupo"] == gkey]
    data = saved["datos"][saved["datos"]["grupo"] == gkey]
    return {
        "key": f"{PROFILE}:{gkey}", "nombre": gname, "tipo": "crt", "perfil": PROFILE, "perfil_nombre": PROFILE_NAME,
        "fichero": TRADES.name, "cats": cats, "ops": cols, "patrones": ["CRT"], "filtros": combos, "actualizado": updated,
        "descripcion": "CRT variante B · sweep H3 (H4 en forex) → FVG de MTF → iFVG + CISD en LTF · stop en el extremo del sweep · spread real",
        "ltf": list(LTFS), "entradas": {str(e): n for e, n in ENTRIES.items()},
        "datos": [{"mercado": f"{r['mercado']} · M{r['ltf']}", "velas M15": int(r["velas"]), "desde (NY)": r["desde"].strftime("%Y-%m-%d"),
                   "hasta (NY)": r["hasta"].strftime("%Y-%m-%d"), "TBR evaluadas": None} for _, r in data.iterrows()],
        "embudo_crt": [{"mercado": r["mercado"], "ltf": int(r["ltf"]), "sweeps": int(r["velas HTF con sweep"]),
                        "fvg": int(r["con FVG de MTF sin mitigar al alcance"]), "toque": int(r["con el extremo tocando el FVG"]),
                        "ifvg": int(r["con iFVG"]), "cisd": int(r["con CISD"]), "e1": int(r["entrada 1"]), "e2": int(r["entrada 2"]),
                        "e3": int(r["entrada 3"]), "e4": int(r["entrada 4"])} for _, r in funnel.iterrows()],
        "metodologia": methodology(gkey)}


def methodology(gkey: str) -> list[list[str]]:
    htf = "H3 (velas alineadas a las 18:00 NY)" if gkey == "indices" else "H4 (velas alineadas a las 17:00 NY)"
    close = "18:00" if gkey == "indices" else "17:00"
    return [
        ["Qué es", f"Candle Range Theory, variante B (docs/estrategia_crt/GUIA.md). Backtest con el mismo motor que la skill CRT "
                   f"(tradingbot/skills/crt/engine.py), sin sesgo ni TBR: las TBR solo sirven para clasificar cada entrada."],
        ["Pasos", f"1) Una vela {htf} toma el máximo (mínimo) de la anterior y vuelve a entrar en su rango. 2) Esa mecha toca un FVG de MTF "
                  "(M15, M30 o H1) creado antes: bajista y entero por encima del máximo de C1 en cortos; alcista y por debajo del mínimo en largos. "
                  "3) En el LTF (M5, M3 o M1) el precio invierte un FVG del tramo del sweep (iFVG). 4) Una vela cierra más allá de la apertura "
                  "de la secuencia que hizo el sweep (CISD)."],
        ["Entradas", "1: a mercado en la apertura de la vela siguiente a la del CISD. 2: retesteo del iFVG tras una continuación (orden "
                     "límite en su base). 3: primera vela sin mecha tras el CISD, entrando en la siguiente apertura. Cada una es un backtest."],
        ["Objetivos", "Tres variantes, cada una con su backtest: 1R (sin BE), 2R (a 1R el stop pasa a la entrada, el que usa el bot) y el "
                      "extremo opuesto de C1 (también con BE a 1R). Si ese extremo ya está alcanzado o por encima de la entrada, no hay operación."],
        ["Gestión", f"Stop en el extremo del sweep, objetivo 2R (por defecto), a 1R el stop pasa a la entrada. A las {close} NY no se abren entradas y lo "
                    "abierto se cierra. Una operación a la vez por mercado, entrada y LTF. Stop y objetivo en la misma vela: cuenta el stop."],
        ["TBR", "Una entrada está «dentro de una TBR» si su hora cae en el horario de Asia (20:00-00:00), London (02:00-05:00) o NY Open "
                "(10:00-12:00), hora de Nueva York; si no, «Fuera de TBR». Es la hora de la entrada, no del sweep."],
        ["Hora en punto", "Cada entrada lleva además la hora en punto a la que está pegada si dista 15 min o menos (03:00 vale de 02:45 a 03:15; 04:00, de 03:45 a 04:15). Se puede combinar con la TBR para ver las entradas en TBR y cerca de una hora exacta."],
        ["TF del FVG", "Una operación cuenta en cada timeframe de MTF (M15, M30, H1) cuyo FVG toca el extremo del sweep: puede tocar varios."],
        ["Costes", "Spread real de MT5 en la vela de entrada, una vez por operación (R neto = R bruto - spread / riesgo)."],
        ["Datos", "Velas M5, M3 y M1 de MT5 (PUPrime). El HTF y el MTF salen de las M5; M1 solo llega a 2024 por el tope de velas del terminal."],
        ["Límites", "Cada entrada y LTF es una prueba distinta sobre los mismos setups: con tantas combinaciones algún resultado "
                    "positivo puede ser azar. Mira la consistencia entre mercados, entradas y periodos."]]


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
    ap.add_argument("--descargar", action="store_true", help="descarga las velas M5, M3 y M1 que falten y termina")
    ap.add_argument("--simular", action="store_true", help="simula y guarda analisis/crt_operaciones.pkl antes de exportar")
    args = ap.parse_args()
    if args.descargar:
        download_missing()
        return
    if args.simular or not TRADES.exists():
        simulate()
    write(pd.read_pickle(TRADES))


if __name__ == "__main__":
    main()
