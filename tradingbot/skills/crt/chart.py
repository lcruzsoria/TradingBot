"""Los CRT del gráfico (botón CRT del perfil CRT): los del backtest, los que el bot operó en directo (`live_marks`) y los «Setup OK sin Entrada»
(`no_entry_marks`).

Las marcas del backtest (`crt_marks`):

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

from ...timeframes import minutes
from ..calendario.chart import market_key
from ..levels.daylevels import DEFAULT_US_INDICES, is_us_index
from ..stats.backtest import CRT_ENTRIES, CRT_MTF_BITS, CRT_MTF_NAMES
from . import engine

HTF_MINUTES = {"indices": 180, "forex": 240}
AUDIT_COLS = ("pe", "ps", "pt", "pa", "pb", "pc", "ti", "tv", "tj", "th", "tq", "tt")      # columnas del backtest para auditar la operación
MTF_TFS = {15: "M15"}                                            # f15a, f15b, f15t...: el FVG de MTF tocado en cada TF
STATES = {"objetivo": "objetivo", "stop": "stop", "breakeven": "be", "tiempo": "tiempo", "invalido": "invalido"}       # resultado del backtest -> estado del gráfico
RESULT_WORDS = {"objetivo": "TP", "stop": "SL", "be": "BE", "tiempo": "T", "invalido": "Invalidado", "sin_setup": "Sin setup",
                "sin_operacion": "Sin operación", "sin_sweep": "Sin sweep"}
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
    invalid: dict[tuple, tuple] = {}                           # (inicio de C2, dirección) -> (hora del extremo, precio, motivo, estado)
    for table, state in (("invalidos", "invalido"), ("sin_setup", "sin_setup")):            # invalidados y sweeps sin setup
        for group in backtest.groups_of("crt"):
            inv = group.raw.get(table) if group.is_crt else None
            if not inv:
                continue
            for i, m in enumerate(inv["m"]):
                if market_key(group.raw["cats"]["m"][m]) == key and (int(inv["c"][i]), int(inv["d"][i])) not in trades \
                        and (int(inv["c"][i]), int(inv["d"][i])) not in invalid:
                    invalid[(int(inv["c"][i]), int(inv["d"][i]))] = (int(inv["th"][i]), float(inv["ps"][i]), inv["motivos"][inv["mo"][i]], state)
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
            th, price, reason, state = invalid[(c2_min, direction)]
            n_ext = min(max(int(np.searchsorted(ts, th * 60 + ahead, "right")) - 1, 0), n - 1)
            out.append({
                "x0": x0, "x1": x1, "xc1": xc1, "direction": "short" if direction else "long", "state": state, "label": "CRT",
                "c1": (float(np.min(lows[xc1:x0])), float(np.max(highs[xc1:x0]))),
                "c2": (float(np.min(lows[x0:x1])), float(np.max(highs[x0:x1]))), "x2": x2,
                "c3": (float(np.min(lows[x1:x2])), float(np.max(highs[x1:x2]))) if x2 > x1 else None,
                "mtf": [], "ltf": None, "entry": None, "htf": htf, "motivo": reason, "start": start, "fvg_all": [], "others": [],
                "when": datetime.fromtimestamp(start - ahead, timezone.utc).strftime("%d/%m %H:%M"),
                "extreme": {"x": n_ext, "price": price}})
            continue
        rows = sorted(rows, key=lambda r: (ltf_pref.index(r[0]), entry_pref.index(r[1])))
        if (rows[0][0], rows[0][1]) != (ltf, entry):            # solo se dibuja la operación del LTF y la entrada elegidos: cada combinación del
            out.append({                                        # backtest tiene una sola operación abierta a la vez, y mezclarlas las solapaba
                "x0": x0, "x1": x1, "xc1": xc1, "direction": "short" if direction else "long", "state": "sin_operacion", "label": "CRT",
                "c1": (float(np.min(lows[xc1:x0])), float(np.max(highs[xc1:x0]))),
                "c2": (float(np.min(lows[x0:x1])), float(np.max(highs[x0:x1]))), "x2": x2,
                "c3": (float(np.min(lows[x1:x2])), float(np.max(highs[x1:x2]))) if x2 > x1 else None,
                "mtf": [], "ltf": None, "entry": None, "htf": htf, "start": start, "fvg_all": [],
                "motivo": f"sin operación en M{ltf} · entrada {entry}",
                "when": datetime.fromtimestamp(start - ahead, timezone.utc).strftime("%d/%m %H:%M"),
                "others": [(r[0], r[1], STATES.get(r[2], "tiempo")) for r in rows]})
            continue
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
    marked = {c for c, _ in set(trades) | set(invalid)}
    origin = 18 * 60 if htf == 180 else 17 * 60                 # las velas HTF empiezan a las 18:00 NY (índices) o a las 17:00 NY (forex)
    first_min, last_min = int(ts[0]) // 60 - ahead // 60, int(ts[-1]) // 60 - ahead // 60
    for c2_min in range(((first_min - origin) // htf) * htf + origin, last_min + 1, htf):
        if c2_min in marked:
            continue
        start = c2_min * 60 + ahead                              # las velas que no barren C1 también llevan caja: «sin sweep»
        x0 = int(np.searchsorted(ts, start, "left"))
        x1 = int(np.searchsorted(ts, start + htf * 60, "left"))
        if x0 >= n or ts[x0] - start > htf * 60 or x1 <= x0:
            continue
        xp = int(np.searchsorted(ts, start - htf * 60, "left"))      # la vela anterior (C1), con las velas cargadas
        prev = xp < x0 and ts[xp] < start
        sweeps = prev and (float(np.max(highs[x0:x1])) > float(np.max(highs[xp:x0])) or float(np.min(lows[x0:x1])) < float(np.min(lows[xp:x0])))
        direction, c1_box, xc1 = "none", (float(np.min(lows[x0:x1])), float(np.max(highs[x0:x1]))), x0
        if prev and not sweeps:
            state, motivo = "sin_sweep", "no barre ningún extremo de C1"
        else:                                                    # barre C1 (o no hay vela anterior) pero el backtest no la evaluó: fin de semana o fuera de su histórico
            state, motivo = "sin_evaluar", "el backtest no evalúa esta vela (fuera de su histórico o tras el cierre del fin de semana)"
            if prev:                                             # el lado lo da el primer extremo de C1 que toma la vela
                c1_lo, c1_hi = float(np.min(lows[xp:x0])), float(np.max(highs[xp:x0]))
                up = np.flatnonzero(highs[x0:x1] > c1_hi)
                dn = np.flatnonzero(lows[x0:x1] < c1_lo)
                direction = "short" if len(up) and (not len(dn) or up[0] <= dn[0]) else "long"
                c1_box, xc1 = (c1_lo, c1_hi), xp
        out.append({"x0": x0, "x1": x1, "xc1": xc1, "direction": direction, "state": state, "label": "CRT",
                    "c1": c1_box,
                    "c2": (float(np.min(lows[x0:x1])), float(np.max(highs[x0:x1]))), "x2": x1, "c3": None,
                    "mtf": [], "ltf": None, "entry": None, "htf": htf, "motivo": motivo, "start": start,
                    "fvg_all": [], "others": [], "when": datetime.fromtimestamp(start - ahead, timezone.utc).strftime("%d/%m %H:%M")})
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


LIVE_BARS = 2 * 1440                                             # minutos de velas anteriores a la entrada con los que la skill busca el setup


def live_marks(trades, df, symbol: str, ahead: int, ltf: int = 5, entry: int = 1, rule=None, indices=DEFAULT_US_INDICES) -> list[dict]:
    """Marcas (formato de ChartView.set_crts) de las operaciones que el bot hizo en directo: `trades` son `Trade` del forwardtest.

    El setup no se guarda con la orden: se vuelve a buscar con el motor sobre las velas cargadas, igual que la skill al dar la señal
    (los 2 días antes de la entrada, la entrada en la vela que abrió la orden) y se dibuja lo que la dio: el FVG de MTF, el iFVG de LTF,
    la zona que comparten, el CISD, el toque de la zona y la posición. Solo salen las del timeframe del gráfico."""
    rule = rule or engine.Rule(be_at=0.0)
    ts = df["ts"].to_numpy().astype(np.int64)
    highs, lows = df["high"].to_numpy(), df["low"].to_numpy()
    n = len(ts)
    base = engine.INDICES if is_us_index(symbol, indices) else engine.FOREX
    cfg = engine.Cfg(base.htf_min, base.origin, base.session_end, ahead)
    htf, step, out = base.htf_min, ltf * 60, []
    for trade in trades:
        order, closed = trade.order, trade.closed
        if order.symbol != symbol or order.pattern_key != "crt" or not order.entry_ts or minutes(order.timeframe) != ltf:
            continue
        x_in = int(np.searchsorted(ts, order.entry_ts, "left"))
        if x_in >= n or int(ts[x_in]) != order.entry_ts:
            continue
        lo = max(0, x_in + 1 - LIVE_BARS // ltf)
        sub = df.iloc[lo:x_in + 1].reset_index(drop=True)
        closed_bars = len(sub) - 1
        setups, _ = engine.find_zone_setups(sub.iloc[:closed_bars], sub.iloc[:closed_bars], ltf, cfg)
        views = {1: engine.view(sub, 1), -1: engine.view(sub, -1)}
        st = ep = None
        for cand in reversed(setups):
            if cand["dirección"] != order.direction:
                continue
            ep = engine.entry_point(views[cand["sign"]], cand, entry, ltf, rule, cfg, closed_bars)
            if ep is not None and int(views[1]["ts"][ep["start"]]) == order.entry_ts:
                st = cand
                break
        if st is None:
            continue
        sgn = st["sign"]                                               # el motor ve el largo como un corto con los precios cambiados de signo

        def zone(a: float, b: float) -> tuple[float, float]:
            return min(sgn * a, sgn * b), max(sgn * a, sgn * b)

        start = int(st["C2"])
        x0 = int(np.searchsorted(ts, start, "left"))
        x1 = int(np.searchsorted(ts, start + htf * 60, "left"))
        xc1 = int(np.searchsorted(ts, start - htf * 60, "left"))
        x2 = int(np.searchsorted(ts, start + 2 * htf * 60, "left"))
        if x1 <= x0 or xc1 >= x0:
            continue
        end = int(np.searchsorted(ts, closed.exit_ts, "left")) if closed else n - 1
        zb, zt = zone(st["z_bottom"], st["z_top"])
        state = STATES.get(closed.result, "tiempo") if closed else "abierta"
        out.append({
            "x0": x0, "x1": x1, "xc1": xc1, "direction": order.direction, "state": state, "label": "CRT",
            "c1": (float(np.min(lows[xc1:x0])), float(np.max(highs[xc1:x0]))),
            "c2": (float(np.min(lows[x0:x1])), float(np.max(highs[x0:x1]))), "x2": x2,
            "c3": (float(np.min(lows[x1:x2])), float(np.max(highs[x1:x2]))) if x2 > x1 else None,
            "mtf": [f"M{z[0]}" for z in st["zones"]], "ltf": ltf, "entry": entry, "entry_name": CRT_ENTRIES[entry], "htf": htf, "start": start,
            "fvg_all": [f"M{z[0]}" for z in st["zones"]], "others": [], "live": True,
            "when": datetime.fromtimestamp(start - ahead, timezone.utc).strftime("%d/%m %H:%M"),
            "pos": {"x0": x_in, "x1": max(end, x_in), "entry": order.price, "stop": order.stop, "target": order.target},
            "ifvg": {"x0": lo + st["kf"] - 2, "x1": lo + st["jc"], "bottom": zone(*st["ifvg"])[0], "top": zone(*st["ifvg"])[1]},
            "common": {"x0": lo + st["kf"] - 2, "x1": lo + st["jc"], "bottom": zb, "top": zt},
            "cisd": {"x0": lo + st["cisd"][0], "x1": lo + st["jc"], "level": sgn * st["cisd"][1], "label": "CISD"},
            "touch": {"x": lo + st["jt"], "price": zt if order.direction == "long" else zb,
                      "when": datetime.fromtimestamp(int(ts[lo + st["jt"]]) - ahead, timezone.utc).strftime("%d/%m %H:%M")},
            "extreme": {"x": lo + st["ih"], "price": order.stop},
            "fvgs": [{"tf": m, "name": f"M{m}", "x0": int(np.searchsorted(ts, formed - 3 * m * 60, "left")), "x1": lo + st["jc"],
                      "bottom": zone(b, t)[0], "top": zone(b, t)[1]} for m, b, t, formed in st["zones"]]})
    return out


NO_ENTRY_DAYS = 4                                                # días de velas en los que se buscan los «Setup OK sin entrada»


def no_entry_marks(df, symbol: str, ahead: int, ltf: int = 5, indices=DEFAULT_US_INDICES) -> list[dict]:
    """Marcas de los CRT de las últimas velas que dejaron la zona común (FVG de MTF ∩ iFVG de LTF) sin que el precio la tocara: «Setup OK sin
    Entrada». Se dibujan el FVG, el iFVG, la zona común y el CISD, sin posición."""
    ts_all = df["ts"].to_numpy().astype(np.int64)
    keep = NO_ENTRY_DAYS * 1440 // ltf
    lo = max(0, len(ts_all) - keep)
    sub = df.iloc[lo:].reset_index(drop=True)
    ts, highs, lows = ts_all[lo:], sub["high"].to_numpy(), sub["low"].to_numpy()
    n = len(ts)
    base = engine.INDICES if is_us_index(symbol, indices) else engine.FOREX
    cfg = engine.Cfg(base.htf_min, base.origin, base.session_end, ahead)
    htf, out = base.htf_min, []
    for st in engine.find_zone_setups(sub, sub, ltf, cfg)[0].no_entry:
        sgn, start = st["sign"], int(st["C2"])

        def zone(a: float, b: float) -> tuple[float, float]:
            return min(sgn * a, sgn * b), max(sgn * a, sgn * b)

        x0 = int(np.searchsorted(ts, start, "left"))
        x1 = int(np.searchsorted(ts, start + htf * 60, "left"))
        xc1 = int(np.searchsorted(ts, start - htf * 60, "left"))
        x2 = int(np.searchsorted(ts, start + 2 * htf * 60, "left"))
        if x1 <= x0 or xc1 >= x0 or x0 >= n:
            continue
        end = min(int(st["end"]), n - 1)
        zb, zt = zone(*st["common"])
        out.append({
            "x0": lo + x0, "x1": lo + x1, "xc1": lo + xc1, "direction": "short" if sgn > 0 else "long", "state": "sin_entrada", "label": "CRT",
            "c1": (float(np.min(lows[xc1:x0])), float(np.max(highs[xc1:x0]))), "c2": (float(np.min(lows[x0:x1])), float(np.max(highs[x0:x1]))),
            "x2": lo + x2, "c3": (float(np.min(lows[x1:x2])), float(np.max(highs[x1:x2]))) if x2 > x1 else None,
            "mtf": [f"M{z[0]}" for z in st["zones"]], "ltf": ltf, "entry": None, "htf": htf, "start": start, "others": [], "live": True,
            "fvg_all": [f"M{z[0]}" for z in st["zones"]], "motivo": "Setup OK sin Entrada: el precio siguió sin tocar la zona común",
            "when": datetime.fromtimestamp(start - ahead, timezone.utc).strftime("%d/%m %H:%M"),
            "ifvg": {"x0": lo + st["kf"] - 2, "x1": lo + end, "bottom": zone(*st["ifvg"])[0], "top": zone(*st["ifvg"])[1]},
            "common": {"x0": lo + st["kf"] - 2, "x1": lo + end, "bottom": zb, "top": zt},
            "cisd": {"x0": lo + st["cisd"][0], "x1": lo + end, "level": sgn * st["cisd"][1], "label": "CISD"},
            "extreme": {"x": lo + st["ih"], "price": sgn * st["stop"]},
            "fvgs": [{"tf": m, "name": f"M{m}", "x0": int(np.searchsorted(ts, formed - 3 * m * 60, "left")) + lo, "x1": lo + end,
                      "bottom": zone(b, t)[0], "top": zone(b, t)[1]} for m, b, t, formed in st["zones"]]})
    return out
