"""Prueba la lógica de Mt5Source con un módulo MetaTrader5 simulado (el real solo existe en Windows)."""
import sys
import types

import numpy as np
import pytest

from tradingbot.skills.feed import mt5_client
from tradingbot.config import Mt5Profile
from tradingbot.skills.feed.mt5_client import Mt5Error, Mt5Source


class FakeMt5(types.ModuleType):
    ACCOUNT_TRADE_MODE_DEMO = 0
    ACCOUNT_TRADE_MODE_REAL = 2
    TIMEFRAME_M1, TIMEFRAME_M3, TIMEFRAME_M5, TIMEFRAME_M15 = 1, 3, 5, 15
    TIMEFRAME_H1, TIMEFRAME_H3, TIMEFRAME_H4, TIMEFRAME_H12 = 16385, 16387, 16388, 16396
    TIMEFRAME_D1, TIMEFRAME_W1 = 16408, 32769

    def __init__(self, total_bars=120_000, login=26231460, trade_mode=0):
        super().__init__("MetaTrader5")
        self.total, self._login, self._mode = total_bars, login, trade_mode
        self.init_kwargs = None
        self.shutdown_called = False
        self.names = ["EURUSD", "NAS100FT.r", "NAS100", "SINPRECIO"]   # como el real: distingue mayúsculas
        self.selected = []
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

    def symbols_get(self):
        return [types.SimpleNamespace(name=n, visible=True) for n in self.names]

    def symbol_select(self, symbol, enable):
        self.selected.append(symbol)
        return symbol in self.names

    def symbol_info_tick(self, symbol):
        if symbol not in self.names:
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
    with pytest.raises(Mt5Error, match="no existe"):
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


def test_el_simbolo_se_respeta_aunque_se_escriba_con_otras_mayusculas(install):
    """Regresión: 'NAS100FT.R' se convertía en un símbolo inexistente (el real es 'NAS100FT.r')."""
    fake = install(total_bars=100)
    src = Mt5Source(PROFILE)
    src.connect()
    assert src.resolve_symbol("NAS100FT.R") == "NAS100FT.r" and src.resolve_symbol("nas100ft.r") == "NAS100FT.r"
    df = src.load_candles("NAS100FT.R", "15m")
    assert len(df) == 100 and "NAS100FT.r" in fake.selected and "NAS100FT.R" not in fake.selected
    q = src.quotes(["NAS100FT.R"])
    assert q["NAS100FT.R"] is not None and q["NAS100FT.R"].bid == 1.12138


def test_simbolo_inexistente_sugiere_nombres_parecidos(install):
    install()
    src = Mt5Source(PROFILE)
    src.connect()
    with pytest.raises(Mt5Error) as err:
        src.load_candles("NAS100FT.x", "15m")
    msg = str(err.value)
    assert "no existe" in msg and "NAS100" in msg and "NAS100FT.r" in msg
    assert src.similar_symbols("ZZZ") == []


def test_todos_los_simbolos_del_broker(install):
    install()
    src = Mt5Source(PROFILE)
    src.connect()
    assert src.all_symbols() == ["EURUSD", "NAS100", "NAS100FT.r", "SINPRECIO"]


def test_h7_se_construye_agrupando_velas_de_1h(install):
    """MT5 no tiene H7: se piden velas de 1h y se agrupan en bloques de 7 horas."""
    fake = install(total_bars=500)
    fake.ts = (1_700_006_400 - 1_700_006_400 % 86400) + __import__("numpy").arange(500) * 3600   # velas de 1 h
    asked = []
    original = fake.copy_rates_from_pos
    fake.copy_rates_from_pos = lambda s, tf, pos, n: (asked.append(tf), original(s, tf, pos, n))[1]
    src = Mt5Source(PROFILE)
    src.connect()
    h1 = src.load_candles("EURUSD", "1h")
    h7 = src.load_candles("EURUSD", "7h")
    assert set(asked) == {FakeMt5.TIMEFRAME_H1} and len(h7) < len(h1) / 3
    assert h7["tick_volume"].sum() == h1["tick_volume"].sum()


def test_timeframes_nativos_usan_su_constante(install):
    fake = install(total_bars=50)
    src = Mt5Source(PROFILE)
    src.connect()
    asked = []
    original = fake.copy_rates_from_pos
    fake.copy_rates_from_pos = lambda s, tf, pos, n: (asked.append(tf), original(s, tf, pos, n))[1]
    for tf in ("3h", "4h", "12h", "1d", "1w"):
        src.load_candles("EURUSD", tf)
    assert asked == [FakeMt5.TIMEFRAME_H3, FakeMt5.TIMEFRAME_H4, FakeMt5.TIMEFRAME_H12,
                     FakeMt5.TIMEFRAME_D1, FakeMt5.TIMEFRAME_W1]
