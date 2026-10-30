"""Estudio del precio frente a la EMA 10 y el VWAP en velas M15 del Nasdaq: qué pasa después en cada situación. Solo LEE velas de MT5.

Fase de EXPLORACIÓN: solo mira el periodo de entrenamiento (NAS100 de PUPrime hasta el 31/12/2022). Los datos de 2023 en adelante,
SP500, DJ30 y el NAS100 de MetaQuotes se reservan para probar después las estrategias que salgan de aquí, con criterios fijados
antes de verlos (scripts/backtest_ema_vwap.py).

Definiciones (velas M15, hora de Nueva York):
- EMA 10 de los cierres M15. VWAP del día de trading (reinicio a las 18:00 NY, el mismo cálculo del bot: precio típico ponderado
  por el tick volume del broker). ATR 14 (media de los rangos verdaderos) para medir los movimientos.
- Estado de cada vela al cierre: «encima» si cierra por encima de la EMA 10 y del VWAP, «debajo» si cierra por debajo de los
  dos, «mixto» si está entre ellos.
- Lo que pasa después: cierre de k velas más tarde menos el cierre actual, en ATR (positivo = sube), sin salir del día de trading.
  El coste de una operación es el spread de la vela en ATR.
- Para que el estadístico t no se infle con muestras solapadas, cada tabla usa como mucho una muestra cada k velas.

Uso (desde la raíz del proyecto):
    uv run python scripts/estudio_ema_vwap.py --descargar      # descarga M15 con volumen (cambia la cuenta del terminal de MT5)
    uv run python scripts/estudio_ema_vwap.py                  # con las velas ya descargadas

Salida: docs/estudio_ema_vwap/EXPLORACION.md.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from backtest_patrones import AHEAD, intraday_start                                   # noqa: E402
from tradingbot.skills.levels.daylevels import vwap                                   # noqa: E402

BAR = 15
DAY_START = 18 * 60                                     # día de trading de los índices: de 18:00 a 17:00 NY
TRAIN_END = pd.Timestamp("2023-01-01")
DATASETS = (("puprime", "NAS100"), ("puprime", "SP500"), ("puprime", "DJ30"), ("metaquotes", "NAS100"))   # MetaQuotes al final
HORIZONS = (1, 4, 8, 16)                                # velas M15: 15 min, 1 h, 2 h, 4 h
SESSIONS = (("Asia 18-02", 18 * 60, 26 * 60), ("Londres 02-08", 2 * 60, 8 * 60), ("NY mañana 08-12", 8 * 60, 12 * 60),
            ("NY tarde 12-17", 12 * 60, 17 * 60))
DOC = ROOT / "docs" / "estudio_ema_vwap" / "EXPLORACION.md"


def cache_path(profile: str, want: str) -> Path:
    return ROOT / "analisis" / f"m15_{profile}_{want.lower()}.pkl"


def download(profile: str, want: str) -> None:
    """Velas M15 con spread (en precio) y tick volume. Todos los perfiles comparten el terminal: cambia su cuenta."""
    from tradingbot.config import load_profiles, select_profile
    from tradingbot.skills.feed.mt5_client import CHUNK, Mt5Source
    profiles, default = load_profiles()
    source = Mt5Source(select_profile(profiles, default, profile), 2_000_000)
    print("conectado:", source.connect(), flush=True)
    sym = source.resolve_symbol(want)
    mt5 = source._mt5
    mt5.symbol_select(sym, True)
    point = mt5.symbol_info(sym).point
    frames, pos = [], 0
    while True:
        rates = None
        for _ in range(6):                              # la primera petición puede llegar antes de que MT5 sincronice
            rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M15, pos, CHUNK)
            if rates is not None and len(rates):
                break
            time.sleep(2)
        if rates is None or len(rates) == 0:
            break
        frames.append(pd.DataFrame(rates))
        pos += len(rates)
        if len(rates) < CHUNK:
            break
    source.close()
    df = pd.concat(frames).drop_duplicates("time").sort_values("time").reset_index(drop=True)
    df = df.rename(columns={"time": "ts"})[["ts", "open", "high", "low", "close", "tick_volume", "spread"]]
    df["spread"] = df["spread"].astype(float) * point
    df = df.iloc[intraday_start(df["ts"].to_numpy()):-1].reset_index(drop=True)
    pd.to_pickle((sym, df), cache_path(profile, want))
    print(f"  {sym}: {len(df)} velas M15", flush=True)


def features(df: pd.DataFrame) -> pd.DataFrame:
    """Añade hora NY, día de trading, EMA 10, VWAP, ATR 14 y el estado de cada vela."""
    d = df.copy()
    ts = d["ts"].to_numpy()
    d["ny"] = pd.to_datetime(ts - AHEAD, unit="s")
    d["minuto"] = d["ny"].dt.hour * 60 + d["ny"].dt.minute
    d["día"] = ((ts - AHEAD) // 60 - DAY_START + 1440) // 1440            # día de trading (empieza a las 18:00 NY)
    d["ema"] = d["close"].ewm(span=10, adjust=False).mean()
    d["vwap"], _ = vwap(ts, d["high"].to_numpy(), d["low"].to_numpy(), d["close"].to_numpy(), d["tick_volume"].to_numpy(),
                        AHEAD, DAY_START)
    prev = d["close"].shift(1)
    tr = np.maximum(d["high"] - d["low"], np.maximum((d["high"] - prev).abs(), (d["low"] - prev).abs()))
    d["atr"] = tr.rolling(14, min_periods=14).mean()
    above = (d["close"] > d["ema"]) & (d["close"] > d["vwap"])
    below = (d["close"] < d["ema"]) & (d["close"] < d["vwap"])
    d["estado"] = np.where(above, "encima", np.where(below, "debajo", "mixto"))
    d["coste"] = d["spread"] / d["atr"]
    for k in HORIZONS:
        same_day = d["día"].shift(-k) == d["día"]
        d[f"r{k}"] = np.where(same_day, (d["close"].shift(-k) - d["close"]) / d["atr"], np.nan)
    return d.dropna(subset=["atr", "vwap"])


def session_of(minute: pd.Series) -> pd.Series:
    """Sesión de cada vela por su minuto NY (Asia cruza la medianoche)."""
    out = pd.Series("", index=minute.index)
    for name, a, b in SESSIONS:
        if b > 1440:
            mask = (minute >= a) | (minute < b - 1440)
        else:
            mask = (minute >= a) & (minute < b)
        out[mask] = name
    return out


def stat(x: pd.Series) -> tuple[int, float, float]:
    x = x.dropna()
    n = len(x)
    if n < 30:
        return n, float("nan"), float("nan")
    return n, float(x.mean()), float(x.mean() / (x.std(ddof=1) / np.sqrt(n)))


def table(rows: list, head: list) -> str:
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" if i == 0 else "---:" for i in range(len(head))) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def fmt(n: int, m: float, t: float) -> str:
    return "-" if np.isnan(m) else f"{m:+.3f} (t {t:+.1f}, {n})"


def by(d: pd.DataFrame, groups: dict, k: int) -> list:
    """Una fila por grupo: R en ATR a k velas, muestreado cada k velas para no solapar."""
    sampled = d.iloc[::k]
    rows = []
    for name, mask in groups.items():
        rows.append([name, fmt(*stat(sampled.loc[mask.reindex(sampled.index, fill_value=False), f"r{k}"]))])
    return rows


def explore(d: pd.DataFrame, sym: str) -> str:
    d = d[d["ny"] < TRAIN_END].copy()
    d["sesión"] = session_of(d["minuto"])
    out = [f"# Exploración: precio frente a la EMA 10 y el VWAP en M15 ({sym}, PUPrime, entrenamiento)", "",
           f"Periodo: {d['ny'].iloc[0]:%d/%m/%Y} – {d['ny'].iloc[-1]:%d/%m/%Y} ({len(d):,} velas M15). Los datos posteriores y los "
           "demás mercados se reservan para la prueba.".replace(",", "."), "",
           f"Movimientos en ATR 14 de M15. Coste medio de una operación (spread / ATR): {d['coste'].mean():.3f} ATR (mediano "
           f"{d['coste'].median():.3f}). Para ganar algo, una señal tiene que mover el precio bastante más que eso.", "",
           "Cada celda: movimiento medio del cierre k velas después (en ATR, positivo = sube), estadístico t y número de muestras "
           "(una cada k velas). Un largo gana ese número; un corto, el mismo con el signo cambiado.", ""]

    # 1. estado
    out += ["## 1. Según el estado al cierre", ""]
    head = ["Estado"] + [f"{k} velas ({k * BAR} min)" for k in HORIZONS]
    rows = []
    for st in ("encima", "mixto", "debajo"):
        rows.append([st] + [by(d, {st: d["estado"] == st}, k)[0][1] for k in HORIZONS])
    out += [table(rows, head), ""]

    # 2. estado por sesión
    out += ["## 2. Estado por sesión (a 4 velas, 1 h)", ""]
    rows = []
    for name, _, _ in SESSIONS:
        s = d["sesión"] == name
        rows.append([name] + [by(d, {st: s & (d["estado"] == st)}, 4)[0][1] for st in ("encima", "mixto", "debajo")])
    out += [table(rows, ["Sesión", "encima", "mixto", "debajo"]), ""]

    # 3. cambios de estado (eventos)
    prev = d["estado"].shift(1)
    events = {"entra en «encima» (venía de mixto / debajo)": (d["estado"] == "encima") & (prev != "encima"),
              "entra en «debajo» (venía de mixto / encima)": (d["estado"] == "debajo") & (prev != "debajo"),
              "sale de «encima» a mixto": (d["estado"] == "mixto") & (prev == "encima"),
              "sale de «debajo» a mixto": (d["estado"] == "mixto") & (prev == "debajo")}
    out += ["## 3. Cambios de estado (la vela en que cambia)", "",
            table([[name] + [fmt(*stat(d.loc[mask, f"r{k}"])) for k in HORIZONS] for name, mask in events.items()], head), ""]

    # 4. retroceso a la EMA dentro de la tendencia
    up_before = (d["estado"].shift(1) == "encima") & (d["estado"].shift(2) == "encima")
    dn_before = (d["estado"].shift(1) == "debajo") & (d["estado"].shift(2) == "debajo")
    pull = {"tendencia arriba: la vela toca la EMA y cierra encima de los dos": up_before & (d["low"] <= d["ema"]) & (d["estado"] == "encima"),
            "tendencia abajo: la vela toca la EMA y cierra debajo de los dos": dn_before & (d["high"] >= d["ema"]) & (d["estado"] == "debajo"),
            "tendencia arriba: la vela toca el VWAP y cierra encima de los dos": up_before & (d["low"] <= d["vwap"]) & (d["estado"] == "encima"),
            "tendencia abajo: la vela toca el VWAP y cierra debajo de los dos": dn_before & (d["high"] >= d["vwap"]) & (d["estado"] == "debajo")}
    out += ["## 4. Retroceso a la media dentro de la tendencia", "",
            table([[name] + [fmt(*stat(d.loc[mask, f"r{k}"])) for k in HORIZONS] for name, mask in pull.items()], head), ""]

    # 5. distancia al VWAP
    z = (d["close"] - d["vwap"]) / d["atr"]
    bands = {"≤ −4 ATR": z <= -4, "−4 a −2": (z > -4) & (z <= -2), "−2 a −1": (z > -2) & (z <= -1), "−1 a 0": (z > -1) & (z <= 0),
             "0 a 1": (z > 0) & (z <= 1), "1 a 2": (z > 1) & (z <= 2), "2 a 4": (z > 2) & (z <= 4), "≥ 4 ATR": z > 4}
    out += ["## 5. Distancia del cierre al VWAP (en ATR)", "",
            table([[name] + [by(d, {name: mask}, k)[0][1] for k in HORIZONS] for name, mask in bands.items()], ["Distancia"] + head[1:]), ""]

    # 6. pendiente de la EMA y estado
    slope = d["ema"] - d["ema"].shift(4)
    combo = {"encima y EMA subiendo": (d["estado"] == "encima") & (slope > 0), "encima y EMA bajando": (d["estado"] == "encima") & (slope < 0),
             "debajo y EMA bajando": (d["estado"] == "debajo") & (slope < 0), "debajo y EMA subiendo": (d["estado"] == "debajo") & (slope > 0)}
    out += ["## 6. Estado y pendiente de la EMA (4 velas)", "",
            table([[name] + [by(d, {name: mask}, k)[0][1] for k in HORIZONS] for name, mask in combo.items()], head), ""]

    # 7. día entero: deriva de fondo
    out += ["## 7. Referencia: deriva de fondo", "",
            f"Cualquier vela, sin condición: " + ", ".join(f"{k} velas {fmt(*stat(d.iloc[::k][f'r{k}']))}" for k in HORIZONS) + ".",
            "Una condición solo aporta algo si se separa de esta deriva (el Nasdaq subió mucho en estos años).", ""]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--descargar", action="store_true", help="descarga las velas M15 (cambia la cuenta del terminal de MT5)")
    args = ap.parse_args()
    if args.descargar:
        for profile, want in DATASETS:
            download(profile, want)
    sym, df = pd.read_pickle(cache_path("puprime", "NAS100"))
    text = explore(features(df), sym)
    DOC.parent.mkdir(parents=True, exist_ok=True)
    DOC.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
