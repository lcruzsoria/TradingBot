"""Backtest del CRT (variante B) en NAS100 (HTF H3) o forex (HTF H4, --mercado forex): sweep en el HTF, FVG tocado en MTF, iFVG en M5/M3, CISD y tres entradas.

REGLAS (las del usuario, ver docs/estrategia_crt/GUIA.md) Y CRITERIOS, FIJADOS ANTES DE VER LOS RESULTADOS:
- HTF = H3 con las velas alineadas a las 18:00 NY (18, 21, 0, 3 ... 15). Sweep: una vela H3 (C2) supera el máximo (o mínimo) de la
  anterior (C1). Máximo barrido -> corto; mínimo barrido -> largo. El largo se calcula como el corto con los precios cambiados
  de signo, así que las dos direcciones usan exactamente el mismo código.
- "Cierra dentro del rango": en vivo no se conoce hasta que C2 termina. El CISD es solo el cierre más allá de la apertura de la
  secuencia del sweep (antes se le exigía además un cierre dentro del rango de C1, que retrasaba la entrada: es la fila «CISD con
  cierre dentro de C1» de la sensibilidad). Para exigir que C2 cierre dentro de C1: --esperar-c2 (sin look-ahead) o, con look-ahead
  y solo informativo, la fila «C2 cierra dentro de C1».
- Si C2 supera los dos extremos de C1 a la vez, ese setup se descarta.
- MTF = M15, M30 y H1 (se agregan de M5). Criterio 2: el máximo del sweep (el más alto de C2 hasta el momento) está dentro de un
  FVG bajista de MTF (largos: el mínimo dentro de un FVG alcista). Definiciones operativas:
    * FVG: tres velas con hueco entre el mínimo de la 1.ª y el máximo de la 3.ª (bajista) o al revés (alcista).
    * Ya formado: la 3.ª vela está cerrada antes de la primera vela LTF que supera el máximo de C1.
    * Sin mitigar: desde que se forma hasta que empieza el sweep, ningún precio ha entrado en la zona.
    * Antigüedad máxima: 10 días (sensibilidad: 3 y 30).
    * Toca: el extremo del sweep cae dentro de la zona del FVG (sin tolerancia; sensibilidad con tolerancia).
- LTF = M5 y M3 (dos backtests separados; el TF donde aparece el iFVG es el TF de entrada).
    * iFVG (cortos): FVG alcista del tramo alcista que lleva al extremo del sweep (3.ª vela entre 120 min antes y la vela del extremo,
      sin cerrar por debajo de su base antes del extremo). Se invierte cuando una vela cierra por debajo de su base.
    * CISD: tras la inversión, cierre por debajo de la apertura de la secuencia de velas alcistas consecutivas que terminó en el
      extremo del sweep. Tiene que ocurrir dentro de C2.
- Entradas (cada una es un backtest):
    1. A la apertura de la vela siguiente a la del CISD.
    2. Retesteo del iFVG: el precio continúa (nuevo mínimo bajo el de la vela del CISD) y vuelve a la base del iFVG; orden límite en
       esa base. Se cancela si toca el stop o si llega al objetivo sin retestear.
    3. Primera vela sin mecha tras el CISD (sin mecha en el lado del extremo: bajista con máximo = apertura, en cortos). Entrada a la
       apertura de la vela siguiente.
- Stop en el extremo del sweep (sin colchón; el spread se descuenta como coste). Objetivo 2R. A 1R el stop pasa a la entrada (BE).
  Stop y objetivo en la misma vela: cuenta el stop. A las 18:00 NY no se abren entradas y lo abierto se cierra al cierre de la última
  vela anterior. Una operación a la vez (se descartan setups que llegan con otra operación abierta).
- Costes: spread real de MT5 en la vela de entrada (R neto = R bruto - spread / riesgo).
- Se da por buena (cada una de las 6 combinaciones LTF x entrada) si cumple TODOS:
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
VARIANTS = {1: "vela siguiente al CISD", 2: "retesteo del iFVG", 3: "primera vela sin mecha"}
MIN_OPS, MIN_MEAN, MIN_T = 100, 0.05, 2.0
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
    CFG, DATASETS = Cfg(m["htf_min"], m["origin"], m["session_end"], AHEAD), m["datasets"]
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
    mg = engine.manage(L, st, ep, rule)
    if mg is None:
        return None
    ts, sgn, start, j, entry, hx, risk = L["ts"], st["sign"], ep["start"], mg["exit_index"], ep["entry"], st["stop"], ep["risk"]
    return {"entrada (NY)": pd.Timestamp(int(ts[start]) - AHEAD, unit="s"), "cierre (NY)": pd.Timestamp(int(ts[j]) - AHEAD, unit="s"),
            "dirección": st["dirección"], "FVG MTF": st["mtf"], "C2 cierra dentro": st["inside"], "entrada": sgn * entry,
            "stop": sgn * hx, "objetivo": sgn * mg["target"], "salida": sgn * mg["exit_price"], "riesgo": risk,
            "riesgo %": 100 * risk / abs(entry), "cómo": mg["cómo"], "R bruto": mg["gross"], "coste (R)": mg["cost"],
            "R neto": mg["gross"] - mg["cost"], "C2": st["C2"], "_ts_exit": int(ts[j]),
            # para auditar el criterio en el gráfico: el iFVG invertido, el CISD y las horas de cada paso (hora de servidor)
            "iFVG bajo": min(sgn * st["z_bottom"], sgn * st["z_top"]), "iFVG alto": max(sgn * st["z_bottom"], sgn * st["z_top"]),
            "CISD": sgn * st["level"], "t iFVG": int(ts[st["kf"] - 2]), "t inversión": int(ts[st["m_inv"]]), "t CISD": int(ts[st["jc"]]),
            "t extremo": int(ts[st["ih"]]), "t secuencia": int(ts[st["seq"][0]]), **mtf_zones(st, sgn)}


def run_variant(ltf: pd.DataFrame, setups: list, variant: int, ltf_min: int, rule: Rule) -> pd.DataFrame:
    views = {1: view(ltf, 1), -1: view(ltf, -1)}
    rows, last_exit = [], 0
    for st in setups:
        L = views[st["sign"]]
        if int(L["ts"][st["jc"]]) < last_exit:             # sigue abierta la operación anterior
            continue
        r = execute(L, st, variant, ltf_min, rule)
        if r is None:
            continue
        if rule.close_inside and not r["C2 cierra dentro"]:
            continue
        last_exit = r.pop("_ts_exit")
        rows.append(r)
    return pd.DataFrame(rows)


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
    ap.add_argument("--ltf", type=int, nargs="+", choices=(1, 3, 5), default=list(LTFS),
                    help="timeframes de entrada (iFVG, CISD y entrada). Con M1 el histórico de MT5 solo llega a 2024: el criterio (2) "
                         "usa dos mitades por fecha")
    ap.add_argument("--esperar-c2", action="store_true", help="espera al cierre de C2 dentro del rango de C1 (sin look-ahead) y "
                                                                "busca el CISD hasta el final de C3")
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
    base_rule = Rule(wait_c2=args.esperar_c2)
    suffix = mk["suffix"] + ("_m1" if ltfs == (1,) else "") + ("_esperar_c2" if args.esperar_c2 else "")
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

    out = [f"# Backtest: CRT (variante B) en {mk['title']}, {htf} → M15/M30/H1 → {'/'.join(f'M{x}' for x in ltfs)}" + (
               " · esperando al cierre de C2" if args.esperar_c2 else ""), "",
           *(["**Variante sin look-ahead:** C2 tiene que haber cerrado dentro del rango de C1 (cierre real del HTF) y el CISD y la "
              "entrada se buscan desde el cierre de C2 hasta el final de C3. Si el precio supera el extremo del sweep en C3, el setup "
              "se anula.", ""] if args.esperar_c2 else []),
           *(["**Forex:** velas H4 alineadas a las 17:00 NY, sin entradas a las 17:00 NY y lo abierto se cierra (el corte del día FX; "
              "las 18:00 eran el cierre de los índices). Mismas reglas que en NAS100 para FVG, iFVG, CISD, entradas y gestión.", ""]
             if args.mercado == "forex" else []),
           "Script: `scripts/backtest_crt.py`. Solo lee velas M1, M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están "
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
    out += [table(frows, ["Mercado", *list(next(iter(funnels.values())).keys()), "setups finales"]), ""]
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
    out += ["## Sensibilidad (no cuenta para el veredicto)", "",
            "Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).",
            ""]
    sens = []
    for label, rule in (("regla anterior: el FVG solo tiene que llegar más allá del extremo de C1", replace(base_rule, fvg_above=False)),
                        ("antigüedad del FVG 3 días", replace(base_rule, lookback_days=3)),
                        ("antigüedad del FVG 30 días", replace(base_rule, lookback_days=30)),
                        ("tolerancia al tocar el FVG 0,05 % del precio", replace(base_rule, touch_tol=0.0005)),
                        ("CISD con cierre dentro de C1 (la versión anterior)", replace(base_rule, inside_c1=True)),
                        ("exigir que C2 cierre dentro de C1 (look-ahead)", replace(base_rule, close_inside=True)),
                        ("sin BE", replace(base_rule, be_at=0.0)), ("objetivo 3R", replace(base_rule, rr=3.0))):
        for tf in ltfs:
            if (rule.lookback_days, rule.touch_tol, rule.fvg_above, rule.inside_c1) != (base_rule.lookback_days, base_rule.touch_tol,
                                                                                       base_rule.fvg_above, base_rule.inside_c1):
                st, _ = find_setups(raw[(P, 5)][1], raw[(P, tf)][1], tf, rule)
            else:
                st = setups_by[(P, tf)]
            for v in VARIANTS:
                sens.append(row(f"{label}: M{tf} · {v}", run_variant(raw[(P, tf)][1], st, v, tf, rule)))
    out += [table(sens)]
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
