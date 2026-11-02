"""Backtest del CRT (variante B) en NAS100 (HTF H3) o forex (HTF H4, --mercado forex): el setup dentro de C2 y cuatro entradas.

REGLAS (las del usuario, ver docs/estrategia_crt/GUIA.md) Y CRITERIOS, FIJADOS ANTES DE VER LOS RESULTADOS:
- HTF = H3 con las velas alineadas a las 18:00 NY (18, 21, 0, 3 ... 15; forex H4 a las 17:00). C1 = rango, C2 = manipulación, C3 =
  expansión. Sweep: una vela H3 (C2) supera con una mecha el máximo (o mínimo) de la anterior (C1). Máximo barrido -> corto; mínimo
  barrido -> largo. El largo se calcula como el corto con los precios cambiados de signo (mismo código para las dos direcciones).
  Si C2 supera los dos extremos de C1 antes de la entrada, ese setup se descarta. No se espera a que C2 cierre: todo ocurre dentro de C2.
- MTF = M15 (se agrega de M5). Paso 2 del setup: tras el extremo del sweep (el más alto de C2 hasta el momento), el
  desplazamiento deja un FVG bajista de MTF que nace DESPUÉS del extremo (su primera vela termina después de él), y el precio vuelve a
  él: basta con que lo toque la mecha. Vale cualquier FVG de M15 formado tras el extremo. Un extremo nuevo reinicia todo.
    * FVG: tres velas con hueco entre el mínimo de la 1.ª y el máximo de la 3.ª (bajista) o al revés (alcista).
- LTF = M5 y M3 (backtests separados; el TF donde aparece el iFVG es el TF de entrada).
    * iFVG (cortos): FVG alcista de LTF (3.ª vela desde 120 min antes de la vuelta al FVG de MTF) posterior al extremo, sin cerrar por
      debajo de su base antes. Se invierte cuando una vela cierra por debajo de su base: esa inversión es el CISD.
- Entradas (cada una es un backtest), siempre antes de que cierre C2:
    1. A la apertura de la vela siguiente a la del CISD.
    2. Retesteo del iFVG: el precio continúa (nuevo mínimo bajo el de la vela del CISD) y vuelve a la base del iFVG; orden límite en
       esa base. Se cancela si toca el stop o si llega al objetivo sin retestear.
    3. Primera vela sin mecha tras el CISD (sin mecha en el lado del extremo: bajista con máximo = apertura, en cortos). Entrada a la
       apertura de la vela siguiente.
    4. Al cierre de la vela del CISD.
- Stop en el extremo del sweep (sin colchón; el spread se descuenta como coste). Objetivo 2R (o el extremo opuesto de C1 con
  --objetivo-c1, descartando los setups que no dan --min-rr y anotando el R máximo que habrían dado). A 1R el stop pasa a la entrada
  (BE). Stop y objetivo en la misma vela: cuenta el stop. A las 18:00 NY (17:00 en forex) no se abren entradas y lo abierto se cierra al
  cierre de la última vela anterior. Una operación a la vez (se descartan setups que llegan con otra operación abierta).
- Costes: spread real de MT5 en la vela de entrada (R neto = R bruto - spread / riesgo).
- Se da por buena (cada una de las combinaciones LTF x entrada) si cumple TODOS:
    1. NAS100 de PUPrime, todo el histórico: >= 100 operaciones y R neto medio > +0,05 con t > 2.
    2. R neto medio positivo en 2018-2022 y en 2023 en adelante (con al menos una operación en cada periodo).
    3. R neto medio > 0 en el control: NAS100 (USTEC) de MetaQuotes.

Uso (desde la raíz del proyecto):
    uv run python scripts/backtest_crt.py --descargar     # velas M5 y M3 de MT5 (solo lectura)
    uv run python scripts/backtest_crt.py

Salida: docs/estrategia_crt/RESULTADOS.md y analisis/backtest_crt_<mercado>_m<tf>_e<entrada>.csv (operaciones).
"""
from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from backtest_orb_nasdaq import row, summary, table                                   # noqa: E402
from backtest_patrones import AHEAD                                                   # noqa: E402
from estudio_ema_vwap import TRAIN_END                                                # noqa: E402
from tradingbot.skills.crt import engine                                              # noqa: E402
from tradingbot.skills.crt.engine import Cfg, Rule, view                              # noqa: E402

DOC = ROOT / "docs" / "estrategia_crt" / "RESULTADOS.md"
CFG = engine.INDICES                                     # mercado en curso (lo fija configure)
LTFS = (5, 3)
VARIANTS = {1: "vela siguiente al CISD", 2: "retesteo del iFVG", 3: "primera vela sin mecha", 4: "cierre del CISD"}
MIN_OPS, MIN_MEAN, MIN_T = 100, 0.05, 2.0
INVALID_REASONS = ("sin FVG de MTF", "sin vuelta al FVG de MTF", "sin iFVG invertido")
DATASETS = (("puprime", "NAS100"), ("metaquotes", "NAS100"))                          # el control, al final
MARKETS = {
    "indices": dict(htf="H3", htf_min=180, origin=18 * 3600, session_end=18 * 3600, suffix="", unit=1.0, unit_name="pts",
                    datasets=(("puprime", "NAS100"), ("metaquotes", "NAS100")), title="NAS100",
                    primary="NAS100 de PUPrime", control="NAS100 (USTEC) de MetaQuotes"),
    # Forex: velas H4 alineadas a las 17:00 NY (las H4 nativas de MT5, servidor = NY + 7 h) y cierre de sesión a las 17:00 NY, el
    # corte del día FX. Referencia EURUSD, control GBPUSD (los dos de PUPrime).
    "forex": dict(htf="H4", htf_min=240, origin=17 * 3600, session_end=17 * 3600, suffix="_forex", unit=0.0001, unit_name="pips",
                  datasets=(("puprime", "EURUSD"), ("puprime", "GBPUSD")), title="EURUSD y GBPUSD",
                  primary="EURUSD de PUPrime", control="GBPUSD de PUPrime"),
}


def configure(name: str) -> dict:
    """Aplica el mercado elegido a las constantes que usan el resto de funciones."""
    global CFG, DATASETS
    m = MARKETS[name]
    CFG, DATASETS = Cfg(m["htf_min"], m["origin"], m["session_end"], AHEAD, m["unit"]), m["datasets"]
    return m


# -- datos ---------------------------------------------------------------------------------------------------------------

def cache_path(profile: str, want: str, tf: int) -> Path:
    return ROOT / "analisis" / f"crt_{profile}_{want.lower()}_m{tf}.pkl"


def download(profile: str, want: str, tf: int) -> None:
    """Velas M<tf> con spread (en precio) y tick volume. Todos los perfiles comparten el terminal: cambia su cuenta."""
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
        for _ in range(6):                               # la primera petición puede llegar antes de que MT5 sincronice
            rates = mt5.copy_rates_from_pos(sym, getattr(mt5, f"TIMEFRAME_M{tf}"), pos, CHUNK)
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
    ts = df["ts"].to_numpy()
    step, start = np.diff(ts), 0
    for i in range(0, max(len(step) - 200, 1), 50):      # antes, MT5 solo tiene velas de varias horas o diarias
        if np.median(step[i:i + 200]) <= tf * 60:
            start = i
            break
    df = df.iloc[start:-1].reset_index(drop=True)        # sin la última vela, que puede estar abierta
    cache_path(profile, want, tf).parent.mkdir(exist_ok=True)
    pd.to_pickle((sym, df), cache_path(profile, want, tf))
    print(f"  {sym} M{tf}: {len(df)} velas ({pd.Timestamp(int(ts[start]) - AHEAD, unit='s')} -> "
          f"{pd.Timestamp(int(ts[-2]) - AHEAD, unit='s')} NY)", flush=True)


def find_setups(base: pd.DataFrame, ltf: pd.DataFrame, ltf_min: int, rule: Rule) -> tuple[list, dict]:
    """Los setups del histórico (motor compartido con la skill CRT) con el mercado en curso."""
    return engine.find_setups(base, ltf, ltf_min, rule, CFG)


def mtf_zones(st: dict, sgn: int) -> dict:
    """La zona del FVG de MTF que toca el extremo del sweep en cada timeframe (la última formada): base, techo y hora de servidor de su
    primera vela (0 y NaN si ese timeframe no lo toca). Para dibujarlo en el gráfico."""
    out = {}
    for tf in engine.MTF:
        zones = [z for z in st["zones"] if z[0] == tf]
        if zones:
            z = max(zones, key=lambda q: q[3])
            lo, hi = sorted((sgn * z[1], sgn * z[2]))
            out |= {f"FVG{tf} bajo": lo, f"FVG{tf} alto": hi, f"FVG{tf} t": int(z[3] - 3 * tf * 60)}
        else:
            out |= {f"FVG{tf} bajo": float("nan"), f"FVG{tf} alto": float("nan"), f"FVG{tf} t": 0}
    return out


def execute(L: dict, st: dict, variant: int, ltf_min: int, rule: Rule) -> dict | None:
    """Entrada y gestión de un setup (espacio del corto) y su fila del backtest, o None si no hay entrada."""
    ep = engine.entry_point(L, st, variant, ltf_min, rule, CFG)
    if ep is None:
        return None
    reach = engine.max_r(L, st, ep)
    if rule.target_c1 and rule.min_rr and engine.planned_rr(st, ep) < rule.min_rr - 1e-9:       # el extremo de C1 queda demasiado cerca
        sgn = st["sign"]
        return {"_skip": True, "entrada (NY)": pd.Timestamp(int(L["ts"][ep["start"]]) - AHEAD, unit="s"), "dirección": st["dirección"],
                "FVG MTF": st["mtf"], "entrada": sgn * ep["entry"], "stop": sgn * st["stop"], "objetivo": sgn * st["c1"][0],
                "riesgo": ep["risk"], "R planificado": engine.planned_rr(st, ep), "R máx": reach, "C2": st["C2"]}
    mg = engine.manage(L, st, ep, rule)
    if mg is None:
        return None
    ts, sgn, start, j, entry, hx, risk = L["ts"], st["sign"], ep["start"], mg["exit_index"], ep["entry"], st["stop"], ep["risk"]
    return {"entrada (NY)": pd.Timestamp(int(ts[start]) - AHEAD, unit="s"), "cierre (NY)": pd.Timestamp(int(ts[j]) - AHEAD, unit="s"),
            "dirección": st["dirección"], "FVG MTF": st["mtf"], "C2 cierra dentro": st["inside"], "entrada": sgn * entry,
            "stop": sgn * hx, "objetivo": sgn * mg["target"], "salida": sgn * mg["exit_price"], "riesgo": risk,
            "riesgo %": 100 * risk / abs(entry), "cómo": mg["cómo"], "R bruto": mg["gross"], "coste (R)": mg["cost"],
            "R neto": mg["gross"] - mg["cost"], "R planificado": (ep["entry"] - mg["target"]) / risk, "R máx": reach,
            "C2": st["C2"], "_ts_entry": int(ts[start]), "_ts_exit": int(ts[j]),
            # para auditar el criterio en el gráfico: el iFVG invertido, el CISD y las horas de cada paso (hora de servidor)
            "iFVG bajo": min(sgn * st["z_bottom"], sgn * st["z_top"]), "iFVG alto": max(sgn * st["z_bottom"], sgn * st["z_top"]),
            "CISD": sgn * st["level"], "t iFVG": int(ts[st["kf"] - 2]), "t inversión": int(ts[st["m_inv"]]), "t CISD": int(ts[st["jc"]]),
            "t extremo": int(ts[st["ih"]]), "t vuelta": int(ts[st["jt"]]), "t secuencia": int(ts[st["seq"][0]]), **mtf_zones(st, sgn)}


def run_variant(ltf: pd.DataFrame, setups: list, variant: int, ltf_min: int, rule: Rule) -> pd.DataFrame:
    views = {1: view(ltf, 1), -1: view(ltf, -1)}
    rows, skipped, cands = [], [], []
    for st in setups:
        r = execute(views[st["sign"]], st, variant, ltf_min, rule)
        if r is None:
            continue
        if r.get("_skip"):                                 # descartado: no se opera, solo se anota lo que habría dado
            skipped.append(r)
            continue
        if rule.close_inside and not r["C2 cierra dentro"]:
            continue
        cands.append(r)
    last_exit = 0
    for r in sorted(cands, key=lambda x: x["_ts_entry"]):   # por hora de entrada: si ya hay una operación abierta no se abre otra (tampoco en sentido contrario)
        if r.pop("_ts_entry") <= last_exit:
            continue
        last_exit = r.pop("_ts_exit")
        rows.append(r)
    out = pd.DataFrame(rows)
    out.attrs["descartados"] = skipped                  # lista de filas (un DataFrame en attrs rompe pd.concat)
    return out


def by_period(t: pd.DataFrame, cut: pd.Timestamp = TRAIN_END) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not len(t):
        return t, t
    return t[t["entrada (NY)"] < cut], t[t["entrada (NY)"] >= cut]


def val(x: dict) -> str:
    return f"{x['R medio']:+.3f} R, t {x['estadístico t']:+.2f}" if x.get("operaciones") else "sin operaciones"


# -- informe -------------------------------------------------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--descargar", action="store_true", help="descarga las velas M5 y M3 de MT5 y termina")
    ap.add_argument("--mercado", choices=sorted(MARKETS), default="indices",
                    help="indices (NAS100, HTF H3) o forex (EURUSD/GBPUSD, HTF H4)")
    ap.add_argument("--ltf", type=int, nargs="+", choices=(3, 5), default=list(LTFS),
                    help="timeframes de entrada (iFVG, CISD y entrada). Con M1 el histórico de MT5 solo llega a 2024: el criterio (2) "
                         "usa dos mitades por fecha")
    ap.add_argument("--min-rr", type=float, default=2.0, help="con --objetivo-c1: se descarta el setup si el extremo de C1 da menos de este "
                                                               "R (se anota el R máximo que habría dado)")
    ap.add_argument("--objetivo-c1", action="store_true", help="objetivo en el extremo opuesto de C1 (si barrió el máximo, va a por el "
                                                               "mínimo) en vez de 2R")
    args = ap.parse_args()
    mk = configure(args.mercado)
    ltfs = tuple(args.ltf)
    htf, unit, unit_name = mk["htf"], mk["unit"], mk["unit_name"]
    if args.descargar:
        for profile, want in DATASETS:
            for tf in ltfs:
                try:
                    download(profile, want, tf)
                except Exception as err:                       # noqa: BLE001
                    print(f"  fallo {profile} {want} M{tf}: {err}", flush=True)
        return
    base_rule = Rule(target_c1=args.objetivo_c1, min_rr=args.min_rr if args.objetivo_c1 else 0.0)
    suffix = mk["suffix"] + ("_m1" if ltfs == (1,) else "") + ("_objetivo_c1" if args.objetivo_c1 else "")
    doc = DOC.with_name(f"RESULTADOS{suffix}.md")

    def key(profile: str, want: str) -> str:
        return f"{profile}/{want}"

    raw = {}
    for profile, want in DATASETS:
        for tf in sorted({5, *ltfs}):
            sym, df = pd.read_pickle(cache_path(profile, want, tf))
            raw[(key(profile, want), tf)] = (f"{sym} ({profile})", df)
    P, C = key(*DATASETS[0]), key(*DATASETS[1])
    first = pd.Timestamp(int(raw[(P, min(ltfs))][1]["ts"].iloc[0]) - AHEAD, unit="s")
    last = pd.Timestamp(int(raw[(P, min(ltfs))][1]["ts"].iloc[-1]) - AHEAD, unit="s")
    if first < TRAIN_END - pd.Timedelta(days=730):
        cut, lab1, lab2 = TRAIN_END, "hasta 2022", "2023 en adelante"
    else:                                                   # histórico corto (M1): dos mitades por fecha
        cut = first + (last - first) / 2
        lab1, lab2 = f"1.ª mitad (hasta {cut:%Y-%m})", f"2.ª mitad (desde {cut:%Y-%m})"

    results, funnels, setups_by = {}, {}, {}
    for profile, want in DATASETS:
        k = key(profile, want)
        base = raw[(k, 5)][1]
        for tf in ltfs:
            st, fn = find_setups(base, raw[(k, tf)][1], tf, base_rule)
            setups_by[(k, tf)], funnels[(k, tf)] = st, fn
            for v in VARIANTS:
                t = run_variant(raw[(k, tf)][1], st, v, tf, base_rule)
                results[(k, tf, v)] = t
                if len(t):
                    t.to_csv(ROOT / "analisis" / f"backtest_crt_{profile}_{want.lower()}_m{tf}_e{v}{suffix}.csv", index=False)
            print(f"{k} M{tf}: {len(st)} setups", flush=True)

    verdict, summ = [], {}
    for tf in ltfs:
        for v, vname in VARIANTS.items():
            t, ctrl = results[(P, tf, v)], results[(C, tf, v)]
            s, c = summary(t), summary(ctrl)
            p1, p2 = by_period(t, cut)
            s1, s2 = summary(p1), summary(p2)
            ok1 = s.get("operaciones", 0) >= MIN_OPS and s["R medio"] > MIN_MEAN and s["estadístico t"] > MIN_T
            ok2 = bool(s1.get("operaciones")) and bool(s2.get("operaciones")) and s1["R medio"] > 0 and s2["R medio"] > 0
            ok3 = bool(c.get("operaciones")) and c["R medio"] > 0
            summ[(tf, v)] = (ok1, ok2, ok3)
            verdict.append([f"M{tf} · {v}. {vname}", f"{s.get('operaciones', 0)} ops, {val(s)}", "sí" if ok1 else "**no**",
                            f"{val(s1)} / {val(s2)}", "sí" if ok2 else "**no**", val(c), "sí" if ok3 else "**no**",
                            "**Pasa**" if ok1 and ok2 and ok3 else "No pasa"])
    n_pass = sum(all(x) for x in summ.values())

    out = [f"# Backtest: CRT (variante B) en {mk['title']}, {htf} → M15 → {'/'.join(f'M{x}' for x in ltfs)}" + (
               (" · objetivo en el extremo de C1" if args.objetivo_c1 else "")), "",
           *(["**Forex:** velas H4 alineadas a las 17:00 NY, sin entradas a las 17:00 NY y lo abierto se cierra (el corte del día FX; "
              "las 18:00 eran el cierre de los índices). Mismas reglas que en NAS100 para FVG, iFVG, CISD, entradas y gestión.", ""]
             if args.mercado == "forex" else []),
           "Script: `scripts/backtest_crt.py`. Solo lee velas M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están "
           "en la cabecera del script y en `GUIA.md`; se fijaron antes de ver los resultados.", "",
           f"- **Se da por buena (cada combinación LTF × entrada) si:** (1) {mk['primary']}, todo el histórico: ≥ {MIN_OPS} "
           f"operaciones y R neto > +{MIN_MEAN} con t > {MIN_T}; (2) R neto positivo en los dos periodos ({lab1}; {lab2}); (3) R neto "
           f"> 0 en el control ({mk['control']}).",
           f"- Son {3 * len(ltfs)} combinaciones, así que algún t alto por azar es esperable: se mira la consistencia, no un solo número.", "",
           "## Veredicto", "",
           table(verdict, ["Combinación", mk["primary"], "(1)", f"{lab1} / {lab2}", "(2)", f"Control: {mk['control']}", "(3)",
                           "Resultado"]),
           "", f"**{n_pass} de {3 * len(ltfs)} combinaciones pasan.**", "",
           "## Datos", ""]
    for (k, tf), (name, df) in raw.items():
        a, z = pd.Timestamp(int(df["ts"].iloc[0]) - AHEAD, unit="s"), pd.Timestamp(int(df["ts"].iloc[-1]) - AHEAD, unit="s")
        out.append(f"- {name} M{tf}: {len(df)} velas, {a:%Y-%m-%d} → {z:%Y-%m-%d} (NY).")
    out += ["", "## Embudo (cuántos pasos pasan)", ""]
    frows = []
    for (k, tf), fn in funnels.items():
        frows.append([f"{raw[(k, tf)][0]} M{tf}"] + [fn[x] for x in fn] + [len(setups_by[(k, tf)])])
    out += [table(frows, ["Mercado", *list(next(iter(funnels.values())).keys()), "setups finales"]), "",
            "## Invalidados", "",
            "Un setup queda **invalidado** si el precio llega al extremo opuesto de C1 (el objetivo) antes de encontrar el FVG de MTF, la vuelta a él o "
            "el iFVG invertido. No se opera; se anota por qué. Detalle en `analisis/backtest_crt_*_invalidados.csv`.", ""]
    irows = []
    for (k, tf) in funnels:
        inv = pd.DataFrame(setups_by[(k, tf)].invalid)
        by = inv["motivo"].value_counts() if len(inv) else pd.Series(dtype=int)
        irows.append([f"{raw[(k, tf)][0]} M{tf}", len(inv)] + [int(by.get(m, 0)) for m in INVALID_REASONS])
        if len(inv) and k == P:
            inv["C2 (NY)"] = pd.to_datetime(inv["C2"] - AHEAD, unit="s")
            inv[["C2 (NY)", "dirección", "motivo", "stop"]].to_csv(
                ROOT / "analisis" / f"backtest_crt_{DATASETS[0][0]}_{DATASETS[0][1].lower()}_m{tf}_invalidados.csv", index=False)
    out += [table(irows, ["Mercado", "Invalidados", *INVALID_REASONS]), ""]
    out += [f"## Resultados en {mk['primary']} (R neto, con spread)", ""]
    for tf in ltfs:
        rows = []
        for v, vname in VARIANTS.items():
            t = results[(P, tf, v)]
            p1, p2 = by_period(t, cut)
            rows += [row(f"M{tf} · {v}. {vname}", t), row(f"  {lab1}", p1), row(f"  {lab2}", p2),
                     row("  sin costes (R bruto)", t, "R bruto")]
            if len(t):
                rows += [row("  largos", t[t["dirección"] == "long"]), row("  cortos", t[t["dirección"] == "short"])]
        out += [table(rows), ""]
    out += [f"## Control: {mk['control']}", ""]
    rows = []
    for tf in ltfs:
        for v, vname in VARIANTS.items():
            t = results[(C, tf, v)]
            p1, p2 = by_period(t, cut)
            rows += [row(f"M{tf} · {v}. {vname}", t), row(f"  {lab1}", p1), row(f"  {lab2}", p2)]
    out += [table(rows), "", f"## Cómo terminan y riesgo ({mk['primary']})", ""]
    rows = []
    for tf in ltfs:
        for v, vname in VARIANTS.items():
            t = results[(P, tf, v)]
            if not len(t):
                continue
            ends = ", ".join(f"{x} {n}" for x, n in t["cómo"].value_counts().items())
            rows.append([f"M{tf} · {v}", ends, f"{t['riesgo'].median() / unit:.1f}", f"{t['riesgo'].quantile(.1) / unit:.1f}",
                         f"{t['riesgo'].quantile(.9) / unit:.1f}", f"{t['coste (R)'].mean():.3f}",
                         f"{(t['coste (R)'] > 0.2).mean() * 100:.0f} %"])
    out += [table(rows, ["Combinación", "Cierres", f"Riesgo mediano ({unit_name})", "p10", "p90", "Coste medio (R)",
                         "Coste > 0,2 R"]), "", f"## Por año ({mk['primary']})", ""]
    for tf in ltfs:
        for v, vname in VARIANTS.items():
            t = results[(P, tf, v)]
            if len(t):
                out += [f"**M{tf} · {v}. {vname}**", "",
                        table([row(str(y), g) for y, g in t.groupby(t["entrada (NY)"].dt.year)]), ""]
    if base_rule.min_rr and base_rule.target_c1:
        out += [f"## Descartados: el extremo de C1 da menos de {base_rule.min_rr:g} R ({mk['primary']})", "",
                "No se operan. Se anota el R máximo que habría dado la entrada (lo más lejos que llega el precio a favor antes del stop o del "
                "cierre de sesión), para ver si el filtro descarta ganadoras. Detalle en `analisis/backtest_crt_*_descartados.csv`.", ""]
        rows = []
        for tf in ltfs:
            for v, vname in VARIANTS.items():
                sk, kept = pd.DataFrame(results[(P, tf, v)].attrs["descartados"]), results[(P, tf, v)]
                if len(sk):
                    sk.to_csv(ROOT / "analisis" / f"backtest_crt_{DATASETS[0][0]}_{DATASETS[0][1].lower()}_m{tf}_e{v}{suffix}_descartados.csv", index=False)
                rows.append([f"M{tf} · {v}. {vname}", len(kept), len(sk),
                             f"{sk['R planificado'].median():.2f}" if len(sk) else "-", f"{sk['R máx'].median():.2f}" if len(sk) else "-",
                             f"{(sk['R máx'] >= 1).mean() * 100:.0f} %" if len(sk) else "-",
                             f"{(sk['R máx'] >= base_rule.min_rr).mean() * 100:.0f} %" if len(sk) else "-"])
        out += [table(rows, ["Combinación", "Operadas", "Descartadas", "R planificado mediano", "R máx mediano", "Llegaron a 1 R",
                             f"Llegaron a {base_rule.min_rr:g} R"]), ""]
    out += ["## Sensibilidad (no cuenta para el veredicto)", "",
            "Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).",
            ""]
    sens = []
    for label, rule in (("exigir que C2 cierre dentro de C1 (look-ahead)", replace(base_rule, close_inside=True)),
                        ("sin BE", replace(base_rule, be_at=0.0)), ("objetivo 3R", replace(base_rule, rr=3.0))):
        for tf in ltfs:
            st = setups_by[(P, tf)]                                   # los setups no dependen de estas reglas
            for v in VARIANTS:
                sens.append(row(f"{label}: M{tf} · {v}", run_variant(raw[(P, tf)][1], st, v, tf, rule)))
    out += [table(sens)]
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
