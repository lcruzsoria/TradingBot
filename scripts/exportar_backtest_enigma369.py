"""Enigma369 en la ventana Backtest: en qué zona (día, sesión, cuarto y micro) se hace el máximo y el mínimo de cada día en los índices USA.

Para cada día de trading (18:00-17:00 NY) de NAS100, SP500 y DJ30 busca la vela del máximo y la del mínimo y guarda sus zonas con las reglas de
la skill (tradingbot/skills/enigma369/cuartos.py): sesión, cuarto, número de cada capa (modo semana: semana, día, sesión, cuarto), si el cuarto
es 3, 6 o 9, y si está en una alineación 3-6-9 o en una combinación de 3+ colores que llegue hasta el cuarto. El micro (22,5 min, modo día: día,
sesión, cuarto, micro) sale de las velas de 3 min, que empiezan más tarde. Para comparar con el azar guarda también, por día, cuántas velas hay
en cada sesión-cuarto, con cada número y en cada condición: el «tiempo» de cada zona.

Velas de 15 min de MT5 (PUPrime, servidor = NY + 7 h) desde que son intradía (sep. 2018); las de 3 min, desde feb. 2025. SUSTITUYE el grupo del
perfil `enigma369` de tradingbot/skills/stats/backtest.json.gz sin tocar el resto del fichero.

Uso (desde la raíz del proyecto):
    uv run --with pyarrow python scripts/exportar_backtest_enigma369.py
"""
from __future__ import annotations

import gzip
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tradingbot.skills.enigma369 import cuartos                                       # noqa: E402

AHEAD = 7 * 3600                                                                       # servidor del broker = NY + 7 h
OUT = ROOT / "tradingbot" / "skills" / "stats" / "backtest.json.gz"
DATA = next((p for p in (ROOT / "analisis", ROOT.parents[2] / "analisis") if p.exists()), ROOT / "analisis")   # en un worktree, la del repo
PROFILE, PROFILE_NAME = "enigma369", "Enigma369"
SYMBOLS = ("NAS100.s", "SP500.s", "DJ30.s")
SINCE = "2018-09-13"                                                                   # antes, los ficheros de 15 min solo traen una vela al día
MIN_BARS = {15: 80, 3: 400}                                                            # día casi completo (de 92 velas de 15 min / 460 de 3 min)
LAYERS = ("semana", "dia", "sesion", "cuarto", "micro", "weekday")


def load(tf: int, sym: str) -> pd.DataFrame:
    d = pd.read_parquet(DATA / f"{tf}m" / "puprime" / f"{sym}.parquet")
    d = d[d["ts"] >= int(pd.Timestamp(SINCE).timestamp()) + AHEAD].reset_index(drop=True)
    wall = d["ts"].to_numpy() - AHEAD
    d["day"] = (wall + 6 * 3600) // 86400                                              # día de trading (empieza a las 18:00 NY)
    return d


def zone_cols(ts: np.ndarray, mode: str) -> pd.DataFrame:
    """Por vela: dígitos de las capas, números (las 4 capas del modo) y si hay alineación 3-6-9 o combinación de color hasta la última capa."""
    dig = cuartos.layer_digits(ts, AHEAD)
    stack = np.stack([dig[k] for k in LAYERS], axis=1)
    keys, inv = np.unique(stack, axis=0, return_inverse=True)
    rows = []
    for k in keys:
        zones = cuartos.zones_at(dict(zip(LAYERS, map(int, k))), cuartos.MODES[mode])
        al = [r["n"] for r in cuartos.alignments(zones) if r["last"] == 3]
        tri = [r["n"] for r in cuartos.same_color_runs(zones) if r["last"] == 3]
        rows.append({"n1": zones[0]["number"], "n2": zones[1]["number"], "n3": zones[2]["number"], "n4": zones[3]["number"],
                     "al": al[0] if al else 0, "tri": tri[0] if tri else 0})
    out = pd.DataFrame(rows).iloc[inv.ravel()].reset_index(drop=True)
    for k in ("sesion", "cuarto", "micro", "weekday"):
        out[k] = dig[k].astype(int)
    out["counts"] = ((dig["semana"] > 0) & (dig["dia"] > 0)).astype(int)                # fuera de Q0: los números cuentan
    return out


def market(sym: str) -> tuple[list[dict], list[dict], dict]:
    d15, d3 = load(15, sym), load(3, sym)
    d15 = pd.concat([d15, zone_cols(d15["ts"].to_numpy(), "semana")], axis=1)
    d3 = pd.concat([d3, zone_cols(d3["ts"].to_numpy(), "dia")], axis=1)
    n15, n3 = d15.groupby("day").size(), d3.groupby("day").size()
    ok15, ok3 = set(n15[n15 >= MIN_BARS[15]].index), set(n3[n3 >= MIN_BARS[3]].index)
    by3 = {k: g for k, g in d3[d3["day"].isin(ok3)].groupby("day")}
    days, exts = [], []
    for day, g in d15[d15["day"].isin(ok15)].groupby("day"):
        wd = int(g["weekday"].iloc[-1])
        if wd > 4:
            continue
        cell = (g["sesion"] - 1) * 4 + (g["cuarto"] - 1)
        rec = {"t": int(day), "wd": wd, "q0": int(not g["counts"].iloc[-1]), "k": len(g),
               "bs": np.bincount(cell, minlength=16).tolist(),                         # velas en cada sesión-cuarto
               "bn": np.bincount(g["n4"], minlength=10)[1:].tolist(),                  # velas con cuarto de número 1..9
               "ba": int((g["al"] > 0).sum()), "bt": int((g["tri"] > 0).sum())}
        first = g.groupby(cell).first()                                                # el cuarto no cambia dentro de su sesión-cuarto
        for key, flag in (("fc", first["n4"].isin(cuartos.CRITICAL)), ("fa", first["al"] > 0), ("ft", first["tri"] > 0)):
            rec[key] = int(sum(1 << int(c) for c in first.index[flag.to_numpy()]))    # bit i: la sesión-cuarto i cumple la condición
        h3 = by3.get(day)
        if h3 is not None:
            c3 = (h3["sesion"] - 1) * 4 + (h3["cuarto"] - 1)
            rec.update({"k3": len(h3), "bm": np.bincount(h3["micro"], minlength=5)[1:].tolist(),
                        "bmn": np.bincount(h3["n4"], minlength=10)[1:].tolist(),
                        "bma": int((h3["al"] > 0).sum()), "bmt": int((h3["tri"] > 0).sum()),
                        "c3": np.bincount(c3, minlength=16).tolist(),                  # velas de 3 min por sesión-cuarto y, de ellas, con micro 3-6-9,
                        "c3c": np.bincount(c3[h3["n4"].isin(cuartos.CRITICAL)], minlength=16).tolist(),   # alineación o combinación
                        "c3a": np.bincount(c3[h3["al"] > 0], minlength=16).tolist(),
                        "c3t": np.bincount(c3[h3["tri"] > 0], minlength=16).tolist()})
        days.append(rec)
        for side, col, fn in ((0, "high", "idxmax"), (1, "low", "idxmin")):
            r = g.loc[getattr(g[col], fn)()]
            e = {"i": len(days) - 1, "d": side, "e": int((r["ts"] - AHEAD) // 60), "s": int(r["sesion"]), "q": int(r["cuarto"]),
                 "nw": int(r["n1"]), "nd": int(r["n2"]), "ns": int(r["n3"]), "n": int(r["n4"]), "a": int(r["al"]), "c": int(r["tri"]),
                 "g": int(r.name == g.index[0]), "mi": 0, "mn": 0, "ma": 0, "mc": 0}
            if h3 is not None:
                m = h3.loc[getattr(h3[col], fn)()]
                e.update({"mi": int(m["micro"]), "mn": int(m["n4"]), "ma": int(m["al"]), "mc": int(m["tri"])})
            exts.append(e)
    info = {"mercado": sym, "velas M15": len(d15), "desde (NY)": str(pd.Timestamp(min(ok15) * 86400, unit="s").date()),
            "hasta (NY)": str(pd.Timestamp(max(ok15) * 86400, unit="s").date()), "TBR evaluadas": None,
            "velas M3": len(d3), "M3 desde": str(pd.Timestamp(min(ok3) * 86400, unit="s").date()) if ok3 else ""}
    return days, exts, info


def methodology() -> list[list[str]]:
    return [
        ["Qué es", "Dónde se hace el máximo y el mínimo de cada día de trading (18:00-17:00 NY) según los cuartos de Enigma369, y si esa zona es "
                   "3, 6 o 9 o está en una alineación de color. No es una estrategia: no hay operaciones ni R."],
        ["Zonas", "Las de la skill Enigma369: sesión de 6 h (Asia 18-00, London 00-06, NY AM 06-12, NY PM 12-18), cuarto de 90 min y micro de "
                  "22,5 min. Número del cuarto = suma de los dígitos semana, día, sesión y cuarto (modo semana) reducida a una cifra; el del micro, "
                  "de día, sesión, cuarto y micro (modo día)."],
        ["Condiciones", "Cuarto 3-6-9: el número del cuarto es crítico. Alineación: 2 o más zonas seguidas del mismo color con número crítico que "
                        "llegan hasta el cuarto (o el micro). Combinación de color: 3 o más zonas seguidas del mismo color hasta el cuarto (o el micro)."],
        ["Lo esperado", "Cada cifra se compara con el tiempo: la parte de las velas de esos mismos días que cae en esa zona o condición. "
                        "Si el máximo cayera al azar, el % de extremos sería igual al % de tiempo. Ratio = % extremos / % tiempo; z: binomial "
                        "(por debajo de 2 en valor absoluto, no se distingue del azar)."],
        ["Control por horario", "Los extremos se concentran en unas sesiones-cuarto (NY PM Q3, NY AM Q3, Asia Q1...) por el horario del mercado. "
                                "«Esperado por horario» mantiene la sesión-cuarto de cada extremo y mira con qué frecuencia esa misma sesión-cuarto "
                                "cumple la condición en esos días: si el % de extremos lo supera (z horario ≥ 2), la condición añade algo al horario."],
        ["Histogramas", "Puntos de diferencia entre el % de extremos y el % de tiempo (verde: más extremos de lo esperado). Por día, mes y año: "
                        "la de la medida elegida (combinación de color, alineación o 3-6-9, hasta el cuarto o el micro), con el control por "
                        "horario en el tooltip. Se pulsan para filtrar. Con un día de la semana fijo, la combinación hasta el cuarto es siempre la "
                        "misma sesión-cuarto (lunes Asia Q1, martes London Q2, miércoles NY AM Q3, jueves NY PM Q4): ahí el horario lo explica todo."],
        ["Q0", "Viernes, fin de semana y 5.ª semana no llevan número: el filtro «Días que cuentan» los quita. La sesión y el cuarto sí cuentan."],
        ["Apertura", "Si el extremo es la primera vela del día (18:00) suele ser el hueco de apertura (un 6-7 % de los extremos). Cae en Asia Q1 "
                     "M1, que en modo día es la combinación 1-1-1: los filtros «sin la vela de apertura» lo quitan para ver si queda efecto."],
        ["Datos", "Velas M15 de MT5 (PUPrime) desde septiembre de 2018 para sesión, cuarto y números; velas M3 desde febrero de 2025 para el "
                  "micro (con M15 no se ve el micro de 22,5 min). Una vela de M3 que cruza el borde del micro cuenta en el micro en que empieza."],
        ["Límites", "Un día tiene un solo máximo y un solo mínimo, y suelen estar en sesiones distintas: no son independientes. Con muchas "
                    "celdas y condiciones, alguna diferencia saldrá por azar: mira si se repite por año y por mercado."]]


def write() -> None:
    cols: dict[str, list] = {}
    day_cols: dict[str, list] = {}
    data = []
    for m, sym in enumerate(SYMBOLS):
        days, exts, info = market(sym)
        base = len(day_cols.get("t", []))
        for rec in days:
            rec = {**rec, "m": m}
            for k in ("t", "wd", "q0", "k", "bs", "bn", "ba", "bt", "fc", "fa", "ft", "k3", "bm", "bmn", "bma", "bmt", "c3", "c3c", "c3a", "c3t", "m"):
                empty = [0] * {"bm": 4, "bmn": 9}.get(k, 16) if k in ("bm", "bmn", "c3", "c3c", "c3a", "c3t") else 0   # días sin velas de 3 min
                day_cols.setdefault(k, []).append(rec.get(k, empty))
        for e in exts:
            e = {**e, "i": e["i"] + base, "m": m}
            for k, v in e.items():
                cols.setdefault(k, []).append(v)
        data.append(info)
        print(f"  {sym}: {len(days)} días ({info['desde (NY)']} a {info['hasta (NY)']}), micro desde {info['M3 desde']}")
    cols["x"] = cols["e"]
    raw = json.loads(gzip.decompress(OUT.read_bytes()).decode("utf-8"))
    raw["grupos"] = [g for g in raw["grupos"] if g.get("perfil") != PROFILE]
    raw["grupos"].append({
        "key": f"{PROFILE}:indices", "nombre": "Índices", "tipo": "extremos", "perfil": PROFILE, "perfil_nombre": PROFILE_NAME,
        "cats": {"m": list(SYMBOLS)}, "ops": cols, "dias": day_cols, "patrones": ["Ambos", "Máximo", "Mínimo"],
        "filtros": {"cuentan": "Días que cuentan (sin Q0)", "cuentan_sa": "Sin Q0 ni la vela de apertura", "todos": "Todos los días",
                    "todos_sa": "Todos sin la vela de apertura"},
        "actualizado": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "descripcion": "Enigma369 · zona del máximo y el mínimo de cada día · cuarto 3-6-9, alineación y combinación de color",
        "datos": data, "metodologia": methodology()})
    OUT.write_bytes(gzip.compress(json.dumps(raw, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), 9, mtime=0))
    print(f"{OUT} ({OUT.stat().st_size / 1024:.0f} KB): grupo Enigma369 con {len(cols['e'])} extremos")


if __name__ == "__main__":
    write()
