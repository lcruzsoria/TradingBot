"""Perfiles que operan de verdad en su cuenta demo (MT5_<PERFIL>_SEND_ORDERS=true), como puprime_live."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import sys
import time
import types
from datetime import date

import pandas as pd
import pytest

from tradingbot.config import ConfigError, Mt5Profile, load_profiles
from tradingbot.envconfig import EnvConfig
from tradingbot.skills.cortex.order import Order
from tradingbot.skills.feed import mt5_client
from tradingbot.skills.feed.datasource import AccountSnapshot, Fill
from tradingbot.skills.feed.mt5_client import Mt5Source, TradeError

ORDER = Order("NAS100", "15m", "long", "Patrón de prueba", "p", "NY Open", date(2026, 11, 17), 105.0, 95.0, 100.0, 100.0, 95.0,
              110.0, "Bullish", 3.0, "GO", None, 1000, 1000 + 24 * 3600)


# -- el perfil ---------------------------------------------------------------------------------------------------
def test_puprime_live_usa_la_cuenta_de_puprime_y_opera_con_su_saldo(tmp_path):
    env = tmp_path / ".env"
    env.write_text("MT5_PUPRIME_LOGIN=7\nMT5_PUPRIME_SERVER=PUPrime-Demo\nMT5_PUPRIME_PASSWORD=x\n"
                   "MT5_PUPRIME_LIVE_BASE=puprime\nMT5_PUPRIME_LIVE_NAME=puprime-live\nMT5_PUPRIME_LIVE_SEND_ORDERS=true\n",
                   encoding="utf-8")
    profiles, _ = load_profiles(env)
    live, pup = profiles["puprime_live"], profiles["puprime"]
    assert (live.login, live.server, live.password) == (pup.login, pup.server, pup.password)
    assert live.send_orders and live.base == "puprime" and live.capital is None and live.display == "puprime-live"
    assert not pup.send_orders and pup.base == ""


def test_operar_de_verdad_no_admite_capital_simulado(tmp_path):
    env = tmp_path / ".env"
    env.write_text("MT5_A_LOGIN=7\nMT5_A_SERVER=S\nMT5_A_SEND_ORDERS=true\nMT5_A_CAPITAL=1000\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="saldo real"):
        load_profiles(env)


def test_sin_mercados_propios_usa_los_del_perfil_base(tmp_path):
    from tradingbot import settings
    path = tmp_path / "s.json"
    settings.save_watchlist(["NAS100ft.s", "EURUSD"], path, profile="puprime")
    assert settings.load_watchlist(["X"], path, profile="puprime_live", base="puprime") == ["NAS100ft.s", "EURUSD"]
    settings.save_watchlist(["GBPUSD"], path, profile="puprime_live")              # si se cambian en el perfil, los suyos
    assert settings.load_watchlist(["X"], path, profile="puprime_live", base="puprime") == ["GBPUSD"]


# -- Mt5Source: órdenes a MT5 (con un MetaTrader5 simulado) --------------------------------------------------------
class FakeMt5(types.ModuleType):
    ACCOUNT_TRADE_MODE_DEMO, ACCOUNT_TRADE_MODE_REAL = 0, 2
    ORDER_TYPE_BUY, ORDER_TYPE_SELL = 0, 1
    POSITION_TYPE_BUY, POSITION_TYPE_SELL = 0, 1
    TRADE_ACTION_DEAL, TRADE_ACTION_SLTP = 1, 6
    ORDER_TIME_GTC = 0
    ORDER_FILLING_FOK, ORDER_FILLING_IOC, ORDER_FILLING_RETURN = 0, 1, 2
    TRADE_RETCODE_PLACED, TRADE_RETCODE_DONE, TRADE_RETCODE_DONE_PARTIAL = 10008, 10009, 10010

    def __init__(self, trade_mode=0):
        super().__init__("MetaTrader5")
        self.mode = trade_mode
        self.sent = []
        self.positions = {}

    def initialize(self, **kw):
        return True

    def shutdown(self):
        pass

    def last_error(self):
        return (1, "fake")

    def account_info(self):
        return types.SimpleNamespace(login=7, trade_mode=self.mode, currency="USD", balance=50_000.0, equity=50_000.0,
                                     profit=0.0)

    def symbols_get(self):
        return [types.SimpleNamespace(name="NAS100.s", visible=True)]

    def symbol_select(self, symbol, enable):
        return True

    def symbol_info(self, symbol):
        return types.SimpleNamespace(name=symbol, digits=2, volume_min=0.1, volume_max=100.0, volume_step=0.1,
                                     trade_tick_size=0.01, trade_tick_value=0.01, filling_mode=2)

    def symbol_info_tick(self, symbol):
        return types.SimpleNamespace(bid=100.4, ask=100.5, time=0)

    def order_calc_profit(self, kind, symbol, volume, price, close):
        return (close - price) * volume * (1 if kind == self.ORDER_TYPE_BUY else -1)   # 1 USD por punto y lote

    def order_send(self, request):
        self.sent.append(request)
        if request["action"] == self.TRADE_ACTION_DEAL and "position" not in request:
            self.positions[555] = types.SimpleNamespace(ticket=555, symbol=request["symbol"], type=request["type"],
                                                        volume=request["volume"], tp=request["tp"], magic=request["magic"],
                                                        time_msc=1)
        elif request["action"] == self.TRADE_ACTION_DEAL:
            self.positions.pop(request["position"], None)
        return types.SimpleNamespace(retcode=self.TRADE_RETCODE_DONE, order=555, price=request.get("price", 0),
                                     volume=request.get("volume", 0), comment="done")

    def positions_get(self, ticket=None, symbol=None):
        return tuple(p for t, p in self.positions.items() if ticket in (None, t) and symbol in (None, p.symbol))

    def history_deals_get(self, position=None):
        return (types.SimpleNamespace(profit=-412.5, commission=-3.0, swap=0.0, fee=0.0),)


@pytest.fixture
def fake(monkeypatch):
    def _install(**kw):
        mt5 = FakeMt5(**kw)
        monkeypatch.setitem(sys.modules, "MetaTrader5", mt5)
        src = Mt5Source(Mt5Profile("puprime_live", 7, "PUPrime-Demo"))
        src.connect()
        return mt5, src
    return _install


def test_abre_con_los_lotes_que_arriesgan_lo_pedido(fake):
    mt5, src = fake()
    fill = src.open_market("NAS100", "long", 500.0, 95.0, 110.0)
    req = mt5.sent[-1]
    # entra a 100,5 (ask): 5,5 puntos de stop x 1 USD por lote -> 500 / 5,5 = 90,9 -> 90,9 lotes (paso 0,1)
    assert (req["symbol"], req["type"], req["sl"], req["tp"], req["volume"]) == ("NAS100.s", 0, 95.0, 110.0, 90.9)
    assert req["type_filling"] == mt5.ORDER_FILLING_IOC and req["magic"] == mt5_client.MAGIC
    assert fill == Fill(555, "NAS100.s", 90.9, 100.5, 499.95)


def test_no_abre_si_no_llega_al_lote_minimo_o_el_precio_ya_paso(fake):
    mt5, src = fake()
    with pytest.raises(TradeError, match="lote mínimo"):
        src.open_market("NAS100", "long", 0.10, 95.0, 110.0)
    with pytest.raises(TradeError, match="fuera del stop"):
        src.open_market("NAS100", "long", 500.0, 101.0, 110.0)
    assert mt5.sent == []


def test_solo_opera_en_cuentas_demo(fake):
    mt5, src = fake(trade_mode=2)
    with pytest.raises(TradeError, match="NO es demo"):
        src.open_market("NAS100", "long", 500.0, 95.0, 110.0)
    assert mt5.sent == []


def test_mueve_el_stop_y_cierra(fake):
    mt5, src = fake()
    src.open_market("NAS100", "long", 500.0, 95.0, 110.0)
    assert src.set_stop(555, 100.5) and mt5.sent[-1]["sl"] == 100.5 and mt5.sent[-1]["tp"] == 110.0
    assert src.close_position(555) and mt5.sent[-1]["type"] == mt5.ORDER_TYPE_SELL and mt5.sent[-1]["price"] == 100.4
    assert not src.close_position(555)                                              # ya cerrada: nada que hacer
    assert src.realized(555) == -415.5


# -- Setup en un perfil que opera de verdad -------------------------------------------------------------------------
class FakeSource:
    def __init__(self, fail=None):
        self.fail, self.calls = fail, []

    def account(self):
        return AccountSnapshot(50_000.0, 50_000.0, 0.0, "USD")

    def open_market(self, symbol, direction, risk, stop, target, comment):
        self.calls.append(("open", symbol, direction, risk, stop, target))
        if self.fail:
            raise TradeError(self.fail)
        return Fill(555, "NAS100.s", 90.9, 100.5, 499.95)

    def set_stop(self, ticket, stop):
        self.calls.append(("stop", ticket, stop))
        return True

    def close_position(self, ticket):
        self.calls.append(("close", ticket))
        return True

    def realized(self, ticket):
        return 1000.0


def run_live(source, tmp_path):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus, got = EventBus(), {"executed": [], "closed": [], "account": []}
    for topic in got:
        bus.subscribe("t", f"setup.{topic}", got[topic].append)
    cfg = {"app": {"send_orders": True, "data_dir": str(tmp_path)}}
    manager = SkillManager(bus, Services(source, None, cfg, EnvConfig()), [{"type": "setup"}])
    manager.start()
    return manager, bus, got


def wait(items, n=1):
    deadline = time.time() + 3
    while len(items) < n and time.time() < deadline:
        time.sleep(0.02)
    time.sleep(0.15)


def test_setup_envia_la_orden_con_el_1_por_ciento_del_saldo_real(tmp_path):
    source = FakeSource()
    manager, bus, got = run_live(source, tmp_path)
    bus.publish("setup.order", {"order": ORDER}, source="cortex")
    wait(got["executed"])
    setup = manager.skills["setup"]
    manager.stop()
    p = got["executed"][0].payload
    assert source.calls == [("open", "NAS100", "long", 500.0, 95.0, 110.0)]         # 1 % de 50.000
    assert p["sent"] is True and "posición 555" in p["note"] and p["risk_amount"] == 499.95
    assert setup.positions[0].ticket == 555 and setup.positions[0].volume == 90.9
    assert any(e.payload.get("live") and e.payload["balance"] == 50_000.0 for e in got["account"])   # saldo real en la cabecera


def test_si_mt5_no_la_acepta_sigue_como_simulada(tmp_path):
    manager, bus, got = run_live(FakeSource(fail="mercado cerrado"), tmp_path)
    bus.publish("setup.order", {"order": ORDER}, source="cortex")
    wait(got["executed"])
    setup = manager.skills["setup"]
    manager.stop()
    p = got["executed"][0].payload
    assert p["sent"] is False and "mercado cerrado" in p["note"] and setup.positions[0].ticket is None


def test_breakeven_y_cierre_se_hacen_tambien_en_mt5(tmp_path):
    source = FakeSource()
    manager, bus, got = run_live(source, tmp_path)
    manager.skills["setup"].server_now = lambda: 3700          # hora del servidor de las velas: el mercado sigue abierto
    bus.publish("setup.order", {"order": ORDER}, source="cortex")
    wait(got["executed"])
    # +1 R (105) sin tocar el objetivo: el stop real pasa a la entrada real
    df = pd.DataFrame({"ts": [1000, 1900], "high": [101.0, 105.5], "low": [99.0, 101.0], "close": [100.5, 105.0]})
    bus.publish("setup.candles", {"symbol": "NAS100", "timeframe": "15m", "df": df}, source="cortex")
    time.sleep(0.3)
    assert ("stop", 555, 100.5) in source.calls and manager.skills["setup"].positions[0].be_sent
    df = pd.DataFrame({"ts": [1000, 1900, 2800], "high": [101.0, 105.5, 111.0], "low": [99.0, 101.0, 104.0],
                       "close": [100.5, 105.0, 110.0]})
    bus.publish("setup.candles", {"symbol": "NAS100", "timeframe": "15m", "df": df}, source="cortex")
    wait(got["closed"])
    manager.stop()
    p = got["closed"][0].payload
    assert p["closed"].result == "objetivo" and p["sent"] is True
    assert p["real"] == {"ticket": 555, "volume": 90.9, "closed_by_bot": True, "profit": 1000.0}
    assert [c for c in source.calls if c[0] == "stop"] == [("stop", 555, 100.5)]       # el stop se mueve una sola vez
