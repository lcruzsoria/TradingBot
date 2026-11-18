"""Análisis del SMT secuencial entre NAS100.s, SP500.s y DJ30.s con las velas de M5 de analisis/5m/puprime (Quarterly Theory).

Con el mismo código que la skill SMT (`detectar`): cuántos SSMT hay por ciclo y cuarto, cómo de correlacionados van los tres índices por sesión
y qué hace el NAS100 después de un SSMT frente a los cuartos en que los tres rompen el mismo extremo (sin divergencia).

    uv run --with pyarrow python scripts/analizar_smt.py [--velas RUTA] [--desde 2024-01-01]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tradingbot.skills.smt import ciclos  # noqa: E402
from tradingbot.skills.smt.smt import detectar  # noqa: E402

SYMBOLS = ("NAS100.s", "SP500.s", "DJ30.s")
AHEAD = 7 * 3600
TF_MIN = 5
DEFAULT_CANDLES = Path("C:/Users/claude/DEV/TradingBot/analisis/5m/puprime")
SESIONES = (("Asia", 18, 24), ("Londres", 0, 6), ("NY AM", 6, 12), ("NY PM", 12, 18))      # horas de NY


def cargar(velas: Path, desde: str | None) -> dict:
    out = {}
    for sym in SYMBOLS:
        df = pd.read_parquet(velas / f"{sym}.parquet").iloc[:-1]
        if desde:
            df = df[df["ts"] >= int(pd.Timestamp(desde).timestamp()) + AHEAD]
        out[sym] = tuple(df[k].to_numpy(np.int64 if k == "ts" else float) for k in ("ts", "open", "high", "low", "close"))
    return out


def correlacion(series: dict) -> None:
    """Correlación de los retornos de 5 min entre cada par, por sesión (hora de NY), y cuántas velas se mueven en sentido contrario."""
    common = series[SYMBOLS[0]][0]
    for s in SYMBOLS[1:]:
        common = np.intersect1d(common, series[s][0])
    close = {s: series[s][4][np.searchsorted(series[s][0], common)] for s in SYMBOLS}
    ret = {s: np.diff(np.log(close[s])) for s in SYMBOLS}
    hour = ((common[1:] - AHEAD) % 86400) // 3600
    print("== Correlación de retornos de 5 min por sesión (NY) y % de velas con signo contrario")
    for name, a, b in SESIONES:
        m = (hour >= a) & (hour < b)
        cells = []
        for i, x in enumerate(SYMBOLS):
            for y in SYMBOLS[i + 1:]:
                c = np.corrcoef(ret[x][m], ret[y][m])[0, 1]
                opp = 100 * np.mean(np.sign(ret[x][m]) * np.sign(ret[y][m]) < 0)
                cells.append(f"{x[:5]}-{y[:5]} {c:.2f} ({opp:.0f} % opuestas)")
        print(f"   {name:8s}", " | ".join(cells))


def movimiento(series: dict, e, sym: str = SYMBOLS[0]) -> float | None:
    """Puntos que se mueve `sym` desde el cierre de la vela del barrido hasta el final del cuarto, con el signo de la dirección esperada
    (SSMT bajista: negativo = a favor)."""
    ts, _o, _h, _l, c = series[sym]
    i, j = int(np.searchsorted(ts, e.ts)), int(np.searchsorted(ts, e.ts_fin)) - 1
    if i >= len(ts) or j <= i or j >= len(ts):
        return None
    move = float(c[j] - c[i])
    return -move if e.direccion == "bajista" else move          # positivo = el precio se movió en el sentido que anticipa el SSMT


def movimiento_desde(series: dict, e, t0: int, sym: str = SYMBOLS[0]) -> float | None:
    """Como `movimiento`, pero desde la vela de la hora `t0` (servidor): lo que se sabe a esa hora."""
    ts, _o, _h, _l, c = series[sym]
    i, j = int(np.searchsorted(ts, t0)), int(np.searchsorted(ts, e.ts_fin)) - 1
    if i >= len(ts) or j <= i or j >= len(ts):
        return None
    move = float(c[j] - c[i])
    return -move if e.direccion == "bajista" else move


def resumen(nombre: str, mov: list[float]) -> str:
    if not mov:
        return f"{nombre}: n=0"
    r = np.array(mov)
    return f"{nombre}: n={len(r)}, a favor {100 * (r > 0).mean():.0f} %, media {r.mean():+.1f} pts, mediana {np.median(r):+.1f}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--velas", default=str(DEFAULT_CANDLES))
    ap.add_argument("--desde", default=None, help="solo desde esta fecha (AAAA-MM-DD)")
    args = ap.parse_args()
    series = cargar(Path(args.velas), args.desde)
    t0, t1 = (pd.Timestamp(int(series[SYMBOLS[0]][0][k]) - AHEAD, unit="s").date() for k in (0, -1))
    print(f"Velas M5 de {', '.join(SYMBOLS)}: {t0} .. {t1}\n")
    correlacion(series)
    for ciclo in ("dia", "90m", "semana"):
        con = detectar(series, ciclo, AHEAD, TF_MIN, divergencia=True)
        sin = detectar(series, ciclo, AHEAD, TF_MIN, divergencia=False)
        print(f"\n== Ciclo {ciclos.ETIQUETAS[ciclo]}: {len(con)} SSMT (bajistas {sum(e.direccion == 'bajista' for e in con)}, alcistas {sum(e.direccion == 'alcista' for e in con)}) "
              f"y {len(sin)} cuartos en que los tres rompen el mismo extremo")
        for q in sorted({e.etiqueta for e in con}):
            print(f"   {q}: {sum(e.etiqueta == q for e in con)} SSMT, {sum(e.etiqueta == q for e in sin)} sin divergencia")
        # Comparación sin mirar al futuro: lo que se sabe en la vela del barrido (¿los otros activos ya han roto en esa misma vela o antes?)
        simultaneo = [e for e in sin if len(set(e.tiempos)) == 1]
        rezagados = [e for e in sin if len(set(e.tiempos)) > 1]          # los otros rompen más tarde: al barrer, iban rezagados
        print("   Qué hace el NAS100 desde el cierre de la vela del barrido hasta el final del cuarto (a favor = sentido que anticipa el SSMT):")
        for nombre, lst in (("al barrer, otro activo no rompe (y nunca rompe: SSMT al final del cuarto)", con),
                            ("al barrer, otro activo no rompe todavía (pero rompe después)", rezagados),
                            ("los tres rompen en la misma vela", simultaneo),
                            ("SSMT con el barrido sobre/bajo el True Open", [e for e in con if e.true_open_ok]),
                            ("SSMT con el barrido al otro lado del True Open", [e for e in con if e.true_open_ok is False])):
            print("     " + resumen(nombre, [m for e in lst if (m := movimiento(series, e)) is not None]))
        # Señal que se puede operar: a mitad del cuarto, ¿el otro activo sigue sin romper el extremo? (se decide a esa hora y se mide hasta el final)
        dur = ciclos.CICLOS[ciclo]
        vivos, muertos = [], []
        for e in con + sin:
            mid = ciclos.inicio(e.cuarto, ciclo) + dur // 2 + AHEAD
            if e.ts >= mid:
                continue                                                   # el barrido llega después de la mitad: no cuenta
            (vivos if (bool(e.fallan) or max(e.tiempos) >= mid) else muertos).append((e, mid))
        print("   A mitad del cuarto, desde esa hora hasta el final (sin mirar al futuro):")
        print("     " + resumen("el otro activo SIGUE sin romper el extremo", [m for e, mid in vivos if (m := movimiento_desde(series, e, mid)) is not None]))
        print("     " + resumen("los tres YA han roto el extremo", [m for e, mid in muertos if (m := movimiento_desde(series, e, mid)) is not None]))


if __name__ == "__main__":
    main()
