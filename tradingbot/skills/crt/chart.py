"""Los CRT que salieron en el backtest, como marcas del gráfico (botón CRT del perfil CRT).

Cada marca es una vela C2 (manipulación) del HTF (H3 en índices, H4 en el resto) que barrió el extremo de la anterior (C1) y de la que el backtest sacó
alguna operación. El backtest guarda de cada operación su mercado, el inicio de C2 (columna `c`, minutos de Nueva York), el timeframe del
FVG de MTF que toca la mecha, el LTF y el modelo de entrada con los que entró y cómo acabó. Los rangos de C1 y C2 se rehacen con las
velas cargadas: solo salen los CRT cuya C2 está entre ellas (FEED_MAX_BARS por mercado y timeframe).

De cada CRT se enseña la operación del LTF y la entrada que se piden (el timeframe del gráfico y CRT_ENTRY); si el CRT no dio esa
operación no se marca (en esa combinación no hubo operación: o ya había otra abierta o no se dio). En la ficha salen las demás.
"""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np

from ..calendario.chart import market_key
from ..levels.daylevels import DEFAULT_US_INDICES, is_us_index
from ..stats.backtest import CRT_ENTRIES, CRT_MTF_BITS, CRT_MTF_NAMES

HTF_MINUTES = {"indices": 180, "forex": 240}
AUDIT_COLS = ("pe", "ps", "pt", "pa", "pb", "pc", "ti", "tv", "tj", "th", "tq", "tt")      # columnas del backtest para auditar la operación
MTF_TFS = {15: "M15"}                                            # f15a, f15b, f15t...: el FVG de MTF tocado en cada TF
STATES = {"objetivo": "objetivo", "stop": "stop", "breakeven": "be", "tiempo": "tiempo", "invalido": "invalido"}       # resultado del backtest -> estado del gráfico
RESULT_WORDS = {"objetivo": "TP", "stop": "SL", "be": "BE", "tiempo": "T", "invalido": "Invalidado"}
LTF_ORDER = (3, 5)


def htf_minutes(symbol: str, indices=DEFAULT_US_INDICES) -> int:
    """Minutos de la vela HTF de un mercado: H3 en los índices americanos, H4 en el resto."""
    return HTF_MINUTES["indices" if is_us_index(symbol, indices) else "forex"]


def mtf_names(mask: int) -> list[str]:
    """Nombres de los timeframes de MTF cuyo FVG toca el extremo del sweep (máscara de la columna `t`)."""
    return [CRT_MTF_NAMES[tf] for tf, bit in CRT_MTF_BITS.items() if mask & bit]


def crt_marks(backtest, symbol: str, ts, highs, lows, ahead: int, ltf: int = 5, entry: int = 1, indices=DEFAULT_US_INDICES) -> list[dict]:
    """Marcas (formato de ChartView.set_crts) de los CRT del backtest en `symbol` que caen dentro de las velas dadas.

    `ts`: horas de las velas (servidor); `ahead`: segundos que el servidor va por delante de Nueva York; `ltf` y `entry`: la operación
    que se enseña de cada CRT (LTF en minutos y modelo de entrada 1, 2, 3 o 4). Solo cuentan las operaciones con objetivo 2R, las del bot.
    """
    ts = np.asarray(ts, dtype=np.int64)
    n = len(ts)
    if backtest is None or not n:
        return []
    key = market_key(symbol)
    trades: dict[tuple, list[tuple]] = {}                      # (inicio de C2, dirección) -> [(ltf, entrada, resultado, FVG, detalle)]
    for group in backtest.groups_of("crt"):
        if not group.is_crt or "c" not in (group.raw.get("ops") or {}):
            continue
        ops = group.ops
        ok = np.array([market_key(m) == key for m in ops.cats["m"]], dtype=bool)         # por categoría, no por operación
        mask = ok[ops["m"]] if len(ops) else np.zeros(0, dtype=bool)
        if "q" in group.raw["ops"]:
            mask &= ops["q"] == 2
        chosen = ops.take(mask)
        audit = all(k in group.raw["ops"] for k in AUDIT_COLS)                       # entrada, stop, objetivo, iFVG y horas de cada paso
        names = chosen.names("o")
        for i in range(len(chosen)):
            detail = {k: float(chosen[k][i]) for k in AUDIT_COLS} | {"e": int(chosen["e"][i]), "x": int(chosen["x"][i])} if audit else {}
            if audit:
                detail["fvg"] = {}
                for tf in MTF_TFS:
                    if f"f{tf}a" in group.raw["ops"] and int(chosen[f"f{tf}t"][i]) >= 0 and not np.isnan(chosen[f"f{tf}a"][i]):
                        detail["fvg"][tf] = (float(chosen[f"f{tf}a"][i]), float(chosen[f"f{tf}b"][i]), int(chosen[f"f{tf}t"][i]))
            trades.setdefault((int(chosen["c"][i]), int(chosen["d"][i])), []).append(
                (int(chosen["l"][i]), int(chosen["n"][i]), str(names[i]), int(chosen["t"][i]), detail))
    invalid: dict[tuple, tuple] = {}                           # (inicio de C2, dirección) -> (hora del extremo, precio, motivo): sweeps invalidados
    for group in backtest.groups_of("crt"):
        inv = group.raw.get("invalidos") if group.is_crt else None
        if not inv:
            continue
        for i, m in enumerate(inv["m"]):
            if market_key(group.raw["cats"]["m"][m]) == key and (int(inv["c"][i]), int(inv["d"][i])) not in trades:
                invalid[(int(inv["c"][i]), int(inv["d"][i]))] = (int(inv["th"][i]), float(inv["ps"][i]), inv["motivos"][inv["mo"][i]])
    if not trades and not invalid:
        return []
    htf = htf_minutes(symbol, indices)
    ltf_pref = [ltf] + [x for x in LTF_ORDER if x != ltf]
    entry_pref = [entry] + [x for x in CRT_ENTRIES if x != entry]
    out = []
    for c2_min, direction in sorted(set(trades) | set(invalid)):
        rows = trades.get((c2_min, direction))
        start = c2_min * 60 + ahead
        x0 = int(np.searchsorted(ts, start, "left"))
        if x0 >= n or ts[x0] - start > htf * 60:                # la C2 no está entre las velas cargadas
            continue
        x1 = int(np.searchsorted(ts, start + htf * 60, "left"))
        xc1 = int(np.searchsorted(ts, start - htf * 60, "left"))
        x2 = int(np.searchsorted(ts, start + 2 * htf * 60, "left"))        # fin de C3, la vela de expansión donde se busca el setup
        if x1 <= x0 or xc1 >= x0:
            continue
        if rows is None:                                        # sin operación: el precio llegó al extremo opuesto de C1 sin completar el setup
            th, price, reason = invalid[(c2_min, direction)]
            n_ext = min(max(int(np.searchsorted(ts, th * 60 + ahead, "right")) - 1, 0), n - 1)
            out.append({
                "x0": x0, "x1": x1, "xc1": xc1, "direction": "short" if direction else "long", "state": "invalido", "label": "CRT",
                "c1": (float(np.min(lows[xc1:x0])), float(np.max(highs[xc1:x0]))),
                "c2": (float(np.min(lows[x0:x1])), float(np.max(highs[x0:x1]))), "x2": x2,
                "c3": (float(np.min(lows[x1:x2])), float(np.max(highs[x1:x2]))) if x2 > x1 else None,
                "mtf": [], "ltf": None, "entry": None, "htf": htf, "motivo": reason, "start": start, "fvg_all": [], "others": [],
                "when": datetime.fromtimestamp(start - ahead, timezone.utc).strftime("%d/%m %H:%M"),
                "extreme": {"x": n_ext, "price": price}})
            continue
        rows = sorted(rows, key=lambda r: (ltf_pref.index(r[0]), entry_pref.index(r[1])))
        if (rows[0][0], rows[0][1]) != (ltf, entry):            # solo las operaciones del LTF y la entrada elegidos: cada combinación del
            continue                                            # backtest tiene una sola operación abierta a la vez, y mezclarlas las solapaba
        best = rows[0]
        state = STATES.get(best[2], "tiempo")
        fvg = sorted({name for r in rows for name in mtf_names(r[3])}, key=lambda s: list(CRT_MTF_NAMES.values()).index(s))
        mark = {
            "x0": x0, "x1": x1, "xc1": xc1, "direction": "short" if direction else "long", "state": state, "label": "CRT",
            "c1": (float(np.min(lows[xc1:x0])), float(np.max(highs[xc1:x0]))),
            "c2": (float(np.min(lows[x0:x1])), float(np.max(highs[x0:x1]))), "x2": x2,
            "c3": (float(np.min(lows[x1:x2])), float(np.max(highs[x1:x2]))) if x2 > x1 else None,
            "mtf": mtf_names(best[3]), "ltf": best[0], "entry": best[1], "entry_name": CRT_ENTRIES[best[1]], "htf": htf,
            "start": start, "fvg_all": fvg, "when": datetime.fromtimestamp(start - ahead, timezone.utc).strftime("%d/%m %H:%M"),
            "others": [(r[0], r[1], STATES.get(r[2], "tiempo")) for r in rows[1:]]}
        if best[4]:
            mark.update(audit_marks(best[4], ts, ahead, n, best[1]))
        out.append(mark)
    return sorted(out, key=lambda m: m["x0"])


def audit_marks(d: dict, ts, ahead: int, n: int, entry: int = 1) -> dict:
    """La operación enseñada, para comprobar el criterio en el gráfico: entrada, stop y objetivo; el iFVG invertido; el CISD y el extremo
    del sweep. Los índices son de la vela que contiene cada hora (las del backtest son aperturas de velas del LTF)."""

    def at(minute: float) -> int:
        return min(max(int(np.searchsorted(ts, int(minute) * 60 + ahead, "right")) - 1, 0), n - 1)

    x_in, x_out = at(d["e"]), at(d["x"])
    return {"pos": {"x0": x_in, "x1": max(x_out, x_in), "entry": d["pe"], "stop": d["ps"], "target": d["pt"]},
            "ifvg": {"x0": at(d["ti"]), "x1": at(d["tv"]), "bottom": d["pa"], "top": d["pb"]},
            "cisd": {"x0": at(d["tq"]), "x1": at(d["tj"]), "level": d["pc"], "label": "límite" if entry == 1 else "ruptura"},
            "extreme": {"x": at(d["th"]), "price": d["ps"]},
            "fvgs": [{"tf": tf, "name": MTF_TFS[tf], "x0": at(t), "x1": max(at(d["tt"]), at(t) + 1), "bottom": a, "top": b}
                     for tf, (a, b, t) in sorted(d.get("fvg", {}).items())]}
