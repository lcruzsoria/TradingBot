"""Backtest del retest del VWAP en la TBR (scripts/backtest_vwap_tbr.py): fontanería de punta a punta y ausencia de sesgo de futuro."""
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.tbr.zones import zones_from_settings

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
AHEAD = 7 * 3600


def load_script():
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("backtest_vwap_tbr", SCRIPTS / "backtest_vwap_tbr.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["backtest_vwap_tbr"] = module                                   # los @dataclass del script lo necesitan
    spec.loader.exec_module(module)
    return module


def random_walk_candles(days: int, seed: int = 7) -> pd.DataFrame:
    """Velas M15 sintéticas, de lunes a viernes las 24 h (hora del servidor = NY + 7 h), de un paseo aleatorio sin memoria."""
    rng = np.random.default_rng(seed)
    start = int(pd.Timestamp("2022-01-03", tz="UTC").timestamp())              # lunes
    ts = np.array([start + d * 86400 + k * 900 for d in range(days) if d % 7 < 5 for k in range(96)], dtype=np.int64)
    n = len(ts)
    close = 10_000 + np.cumsum(rng.normal(0, 4, n))
    open_ = np.r_[close[0], close[:-1]]
    spread_up, spread_dn = rng.uniform(0, 3, n), rng.uniform(0, 3, n)
    high, low = np.maximum(open_, close) + spread_up, np.minimum(open_, close) - spread_dn
    return pd.DataFrame({"ts": ts, "time": pd.to_datetime(ts, unit="s"), "open": open_, "high": high, "low": low, "close": close,
                         "tick_volume": rng.integers(100, 2000, n)})


class FakeSource:
    def __init__(self, df):
        self.df = df

    def connect(self):
        return True

    def load_candles(self, sym, tf):
        return self.df.copy()


def run(monkeypatch, days):
    module = load_script()
    import analisis_setups
    monkeypatch.setattr(analisis_setups, "spread_prices", lambda source, sym, df: np.full(len(df), 0.5))
    env = EnvConfig(parse("")).section("TBR")
    order = zones_from_settings(env, module.ZONE_ORDER)
    trades, info = module.run_symbol(FakeSource(random_walk_candles(days)), "NAS100.r", order, zones_from_settings(env), None, module.MAX_HOLD)
    return module, pd.DataFrame(trades), info


def test_las_operaciones_son_coherentes(monkeypatch):
    module, trades, info = run(monkeypatch, 300)
    primary = trades[trades["variante"] == module.PRIMARY]
    assert len(primary) > 20 and info["TBR evaluadas"] > 100
    assert set(trades["variante"]) <= {v.name for v in module.VARIANTS} and module.CONTROL in set(trades["variante"])
    long_, short = primary[primary["dirección"] == "long"], primary[primary["dirección"] == "short"]
    assert len(long_) and len(short)
    assert ((long_["stop"] < long_["entrada"]) & (long_["entrada"] < long_["objetivo"])).all()
    assert ((short["objetivo"] < short["entrada"]) & (short["entrada"] < short["stop"])).all()
    assert (primary["R potencial"] >= 1.0 - 1e-9).all()                         # min_rr
    assert (primary["coste (R)"] > 0).all() and np.isfinite(primary["R neto"]).all()
    assert (primary["cierre (NY)"] >= primary["entrada (NY)"]).all()
    assert primary.groupby(["mercado", "zona", "día"]).size().max() == 1       # como mucho una operación por TBR


def test_sin_sesgo_de_futuro_en_un_paseo_aleatorio_el_r_bruto_es_cero(monkeypatch):
    """Un precio sin memoria no puede dar ventaja: si el R bruto medio saliera claramente positivo, el simulador usaría el futuro."""
    module, trades, _ = run(monkeypatch, 6000)
    for name in (module.PRIMARY, module.CONTROL):
        r = trades[trades["variante"] == name]["R bruto"]
        assert len(r) > 500
        se = r.std(ddof=1) / np.sqrt(len(r))
        assert abs(r.mean()) < 3.5 * se, f"{name}: R bruto medio {r.mean():+.3f} (error típico {se:.3f})"
    assert (trades["R neto"] <= trades["R bruto"]).all()                        # los costes solo restan


def test_el_informe_y_el_veredicto_con_los_criterios_fijados(monkeypatch):
    module, trades, info = run(monkeypatch, 300)
    report = module.build_report(trades, pd.DataFrame([info]), None)
    assert "## Veredicto" in report and "NO cumple los criterios" in report         # un paseo aleatorio no puede pasarlos
    primary, control = trades[trades["variante"] == module.PRIMARY], trades[trades["variante"] == module.CONTROL]
    results = module.evaluate(primary, control)
    assert [name.split()[0] for name, _, _ in results] == ["Al", "R", "R", "Mejora"] and not all(ok for _, ok, _ in results)
    good = primary.copy()
    good["R neto"] = 0.5                                                          # una serie claramente ganadora, repetida hasta 600
    good = pd.concat([good] * (600 // max(len(good), 1) + 1), ignore_index=True)
    good["entrada (NY)"] = pd.date_range("2020-01-01", periods=len(good), freq="h")
    good["cierre (NY)"] = good["entrada (NY)"] + pd.Timedelta(hours=1)
    good["R neto"] = np.where(np.arange(len(good)) % 2 == 0, 1.0, 0.0)              # media 0,5 con varianza
    verdict = module.evaluate(good, control)
    assert verdict[0][1] and verdict[1][1] and verdict[3][1]                       # >= 500 operaciones, mitades positivas, mejora a la base
