"""Modelo 90M tCISD («Freedom Model») de Bucko Trades (Quarterly Theory): funciones puras, sin depender de otra skill.

Es una HIPÓTESIS SIN VALIDAR: solo simula. Versión mecánica del modelo del curso, sobre NAS100 con SP500 y DJ30 como activos correlacionados:

1. Ventana: todo ocurre entre las 09:00 y las 10:30 de NY (la barrida del SSMT y la entrada).
2. SSMT secuencial en esa ventana. `ciclo="90m"`: el cuarto de 09:00-10:30 frente al de 07:30-09:00 (velas de 5 min); `ciclo="dia"`: NY AM frente a Londres
   (velas de 15 min). Uno de los activos rompe el máximo (mínimo) del cuarto anterior y otro no. Alcista por debajo del True Open del ciclo, bajista por encima.
3. tCISD: la primera vela que rompe el extremo es la vela del tCISD; en un SSMT alcista debe cerrar bajista (si no, se usa la vela bajista más reciente a su
   izquierda; al revés en el bajista). Se marca su apertura y el tCISD queda confirmado con el primer cierre con cuerpo por encima (alcista) o por debajo (bajista).
   Mientras se confirma, algún activo debe seguir sin romper el extremo (si todos lo rompen, el SSMT se ha invalidado).
4. Entrada tras el retest del tCISD. `entrada="rechazo"`: la primera vela que toca la apertura de la vela del tCISD y cierra de nuevo del lado bueno; se entra al cierre.
   `entrada="nivel"`: orden en la apertura de la vela del tCISD, al tocarla. Si antes un cierre pasa al otro lado del cuerpo, el tCISD se descarta.
5. Stop en el extremo del SSMT (la mecha más extrema desde la barrida hasta la entrada), objetivo a `rr` R (3 por defecto en el curso). Una operación por día.
"""
from __future__ import annotations

import numpy as np

DAY = 86400
HORA = 3600
VENTANA = (9 * HORA, 10 * HORA + 1800)                       # 09:00-10:30 NY
CICLOS = {"90m": {"prev": (7 * HORA + 1800, 9 * HORA), "actual": 9 * HORA, "true_open": 7 * HORA + 1800},
          "dia": {"prev": (0, 6 * HORA), "actual": 6 * HORA, "true_open": 0}}
MAX_ATRAS = 30                                                    # velas hacia la izquierda para buscar la vela del tCISD


def agregar(serie: tuple, ahead: int, minutos: int) -> tuple:
    """Velas de `minutos` minutos a partir de otras más finas: (ts, open, high, low, close)."""
    ts, o, h, l, c = serie
    paso = minutos * 60
    g = (ts - ahead) // paso
    cortes = np.flatnonzero(np.diff(g)) + 1
    ini = np.concatenate(([0], cortes))
    fin = np.concatenate((cortes, [len(ts)]))
    return (ts[ini], o[ini], np.maximum.reduceat(h, ini), np.minimum.reduceat(l, ini), c[fin - 1])


def alinear(series: dict) -> dict:
    """Deja solo las velas comunes a todos los activos."""
    comun = None
    for ts, *_ in series.values():
        comun = ts if comun is None else np.intersect1d(comun, ts)
    return {s: tuple(np.asarray(a)[np.searchsorted(v[0], comun)] for a in v) for s, v in series.items()}


def _primeros(h, l, ini, fin, prev_hi, prev_lo, lado: str) -> dict:
    """Primera vela (posición) del tramo [ini, fin) en que cada activo rompe el extremo del cuarto anterior."""
    out = {}
    for s in h:
        seg = h[s][ini:fin] > prev_hi[s] if lado == "alto" else l[s][ini:fin] < prev_lo[s]
        hit = np.flatnonzero(seg)
        if hit.size:
            out[s] = ini + int(hit[0])
    return out


def modelo(series: dict, symbol: str, ahead: int, tf_minutes: int, ciclo: str = "90m", rr: float = 3.0, entrada: str = "rechazo", holgura: float = 0.0) -> list[dict]:
    """Operaciones del modelo sobre `symbol` (la serie `series` ya alineada, velas de `tf_minutes`, ts en hora del servidor).

    `holgura`: puntos que el precio debe atravesar el nivel para dar la orden por llenada (con `entrada="nivel"`; 0 = basta con tocarlo)."""
    cfg = CICLOS[ciclo]
    syms = list(series)
    ts = series[symbol][0]
    o, h, l, c = (series[symbol][i] for i in (1, 2, 3, 4))
    H = {s: series[s][2] for s in syms}
    L = {s: series[s][3] for s in syms}
    O = {s: series[s][1] for s in syms}
    ny = ts - ahead
    dia, seg = ny // DAY, ny % DAY
    bar = tf_minutes * 60
    out = []
    for d in np.unique(dia):
        idx = np.flatnonzero(dia == d)
        s0 = int(idx[0])
        sec = seg[idx]
        p = idx[(sec >= cfg["prev"][0]) & (sec < cfg["prev"][1])]
        cur = idx[(sec >= cfg["actual"]) & (sec < VENTANA[1])]
        if len(p) < (cfg["prev"][1] - cfg["prev"][0]) // bar * 0.8 or len(cur) == 0:
            continue
        ini, fin = int(cur[0]), int(cur[-1]) + 1
        prev_hi = {s: float(H[s][p].max()) for s in syms}
        prev_lo = {s: float(L[s][p].min()) for s in syms}
        to = idx[sec >= cfg["true_open"]]
        if len(to) == 0:
            continue
        true_open = {s: float(O[s][int(to[0])]) for s in syms}
        candidatos = []
        for lado, direccion in (("alto", "short"), ("bajo", "long")):
            first = _primeros(H, L, ini, fin, prev_hi, prev_lo, lado)
            if not first:
                continue                                              # (que el resto no rompa nunca se comprueba al confirmarse el tCISD, no mirando toda la ventana)
            lead = min(first, key=first.get)
            js = first[lead]
            if seg[js] < VENTANA[0]:
                continue                                              # la barrida ocurrió antes de la ventana
            if (direccion == "long" and not L[lead][js] < true_open[lead]) or (direccion == "short" and not H[lead][js] > true_open[lead]):
                continue                                              # el SSMT debe formarse del lado bueno del True Open
            candidatos.append((js, direccion, first))
        for js, direccion, first in sorted(candidatos, key=lambda x: x[0]):
            largo = direccion == "long"
            mala = (lambda i: c[i] < o[i]) if largo else (lambda i: c[i] > o[i])           # color que debe tener la vela del tCISD
            k = js
            while not mala(k) and js - k < MAX_ATRAS and k > s0:
                k -= 1
            if not mala(k):
                continue
            nivel, base = float(o[k]), float(c[k])                    # apertura de la vela del tCISD (borde del cuerpo) y su cierre
            m = None
            for i in range(js if k < js else js + 1, fin):
                if (c[i] > nivel) if largo else (c[i] < nivel):
                    m = i
                    break
            if m is None:
                continue
            if all(first.get(s, 10 ** 9) <= m for s in syms):
                continue                                              # al confirmarse, todos habían roto: SSMT invalidado
            e = precio = None
            for i in range(m + 1, fin):
                if (c[i] < base) if largo else (c[i] > base):
                    break                                             # el cierre pasa al otro lado del cuerpo: tCISD descartado
                toca = (l[i] <= nivel - (holgura if entrada == "nivel" else 0)) if largo else (h[i] >= nivel + (holgura if entrada == "nivel" else 0))
                if not toca:
                    continue
                if entrada == "rechazo":
                    if (c[i] > nivel) if largo else (c[i] < nivel):
                        e, precio = i, float(c[i])
                        break
                else:
                    e, precio = i, nivel
                    break
            if e is None:
                continue
            extremo = float(l[js:e + 1].min() if largo else h[js:e + 1].max())
            riesgo = (precio - extremo) if largo else (extremo - precio)
            if riesgo <= 0:
                continue
            stop = extremo
            target = precio + rr * riesgo if largo else precio - rr * riesgo
            out.append({"day": int(d), "direction": direccion, "ciclo": ciclo, "sweep_ts": int(ts[js]), "conf_ts": int(ts[m]), "entry_idx": int(e),
                        "entry_ts": int(ts[e]) + (bar if entrada == "rechazo" else 0), "entry": precio, "stop": stop, "target": target, "risk": riesgo})
            break                                                     # una operación por día
    return out
