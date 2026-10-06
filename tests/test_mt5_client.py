"""Prueba la lógica de Mt5Source con un módulo MetaTrader5 simulado (el real solo existe en Windows)."""
import sys
import types

import numpy as np
import pytest

from tradingbot import mt5_client
from tradingbot.config import Mt5Profile
from tradingbot.mt5_client import Mt5Error, Mt5Source


class FakeMt5(types.ModuleType):
    ACCOUNT_TRADE_MODE_DEMO = 0
    ACCOUNT_TRADE_MODE_REAL = 2
    TIMEFRAME_M1, TIMEFRAME_M3, TIMEFRAME_M5, TIMEFRAME_M15 = 1, 3, 5, 15

    def __init__(self, total_bars=120_000, login=26231460, trade_mode=0):
        super().__init__("MetaTrader5")
        self.total, self._login, self._mode = total_bars, login, trade_mode
        self.init_kwargs = None
        self.shutdown_called = False
        # velas ascendentes en el tiempo: la posición 0 es la MÁS RECIENTE
        self.ts = 1_700_000_000 + np.arange(total_bars) * 900

    def initialize(self, **kw):
        self.init_kwargs = kw
        return True

    def shutdown(self):
        self.shutdown_called = True

    def last_error(self):
        return (1, "fake")

    def account_info(self):
        return types.SimpleNamespace(login=self._login, server="VantageMarkets-Demo", trade_mode=self._mode,
                                     currency="USD", balance=100000.0, equity=100125.99, profit=125.99)

    def login(self, *a, **k):
        return False

    def symbol_select(self, symbol, enable):
        return symbol != "NOEXISTE"

    def symbol_info_tick(self, symbol):
        if symbol == "NOEXISTE":
            return None
        if symbol == "SINPRECIO":
            return types.SimpleNamespace(bid=0.0, ask=0.0, time=0)
        return types.SimpleNamespace(bid=1.12138, ask=1.12152, time=1_700_000_000)

    def copy_rates_from_pos(self, symbol, tf, start_pos, count):
        end = self.total - start_pos
        begin = max(0, end - count)
        if end <= 0:
            return None
        rows = np.zeros(end - begin, dtype=[("time", "i8"), ("open", "f8"), ("high", "f8"), ("low", "f8"),
                                           ("close", "f8"), ("tick_volume", "i8")])
        rows["time"] = self.ts[begin:end]
        rows["open"] = rows["high"] = rows["low"] = rows["close"] = np.arange(begin, end, dtype=float)
        return rows


@pytest.fixture
def install(monkeypatch):
    def _install(**kw):
        fake = FakeMt5(**kw)
        monkeypatch.setitem(sys.modules, "MetaTrader5", fake)
        return fake
    monkeypatch.setattr(mt5_client.time, "sleep", lambda s: None)
    return _install


PROFILE = Mt5Profile("demo", 26231460, "VantageMarkets-Demo")


def test_carga_todas_las_velas_en_orden(install):
    fake = install(total_bars=120_000)
    src = Mt5Source(PROFILE)
    assert "DEMO 26231460" in src.connect()
    seen = []
    df = src.load_candles("EURUSD", "15m", seen.append)
    assert len(df) == 120_000                      # 3 bloques de 50.000 (50k + 50k + 20k)
    assert seen == [50_000, 100_000, 120_000]
    assert df["ts"].is_monotonic_increasing and df["ts"].is_unique
    assert df["close"].iloc[-1] == 119_999          # la última vela es la más reciente


def test_respeta_max_bars(install):
    install(total_bars=120_000)
    src = Mt5Source(PROFILE, max_bars=60_000)
    src.connect()
    assert len(src.load_candles("EURUSD", "5m")) == 60_000


def test_sin_password_se_engancha_al_terminal(install):
    fake = install()
    Mt5Source(PROFILE).connect()
    assert "login" not in fake.init_kwargs and "password" not in fake.init_kwargs


def test_cuenta_distinta_cancela(install):
    fake = install(login=999)
    with pytest.raises(Mt5Error, match="999"):
        Mt5Source(PROFILE).connect()
    assert fake.shutdown_called


def test_perfil_demo_con_cuenta_real_cancela(install):
    fake = install(trade_mode=FakeMt5.ACCOUNT_TRADE_MODE_REAL)
    with pytest.raises(Mt5Error, match="NO es demo"):
        Mt5Source(PROFILE).connect()
    assert fake.shutdown_called


def test_simbolo_inexistente(install):
    install()
    src = Mt5Source(PROFILE)
    src.connect()
    with pytest.raises(Mt5Error, match="NOEXISTE"):
        src.load_candles("NOEXISTE", "15m")


def test_sin_conexion(install):
    install()
    with pytest.raises(Mt5Error):
        Mt5Source(PROFILE).load_candles("EURUSD", "15m")


def test_conexion_devuelve_cuenta_y_saldo(install):
    install()
    assert Mt5Source(PROFILE).connect() == "MT5 DEMO 26231460  USD 100,000.00"


def test_cotizaciones(install):
    install()
    src = Mt5Source(PROFILE)
    src.connect()
    q = src.quotes(["EURUSD", "NOEXISTE", "SINPRECIO"])
    assert q["EURUSD"].bid == 1.12138 and q["EURUSD"].ask == 1.12152 and q["EURUSD"].ts == 1_700_000_000
    assert q["NOEXISTE"] is None and q["SINPRECIO"] is None
    assert "NOEXISTE" in src._missing   # no se reintenta cada segundo


def test_cuenta(install):
    install()
    src = Mt5Source(PROFILE)
    src.connect()
    acc = src.account()
    assert (acc.balance, acc.equity, acc.profit, acc.currency) == (100000.0, 100125.99, 125.99, "USD")
