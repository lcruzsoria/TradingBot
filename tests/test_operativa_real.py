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
        return types.SimpleNamespace(login=getattr(self, "at", 7), trade_mode=self.mode, currency="USD", balance=50_000.0,
                                     equity=getattr(self, "equity", 50_000.0), profit=0.0)

    def login(self, login, password=None, server=None):
        self.logins = getattr(self, "logins", []) + [login]
        if getattr(self, "can_login", True):
            self.at = login
        return getattr(self, "can_login", True)

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


def test_no_abre_en_un_simbolo_que_el_broker_no_deja_operar(fake):
    mt5, src = fake()
    base = mt5.symbol_info
    mt5.symbol_info = lambda s: types.SimpleNamespace(**{**vars(base(s)), "trade_mode": 0})
    with pytest.raises(TradeError, match="no se puede operar"):
        src.open_market("NAS100", "long", 500.0, 95.0, 110.0)
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


def test_el_cierre_se_lee_de_las_operaciones_de_mt5(fake):
    mt5, src = fake()
    src.open_market("NAS100", "long", 500.0, 95.0, 110.0)
    assert src.closing(555) is None                                                 # sigue abierta
    mt5.positions.clear()
    mt5.history_deals_get = lambda position=None: (
        types.SimpleNamespace(entry=0, volume=90.9, price=100.5, time=1000, time_msc=1_000_000, reason=3, profit=0.0,
                              commission=-3.0, swap=0.0, fee=0.0),
        types.SimpleNamespace(entry=1, volume=90.9, price=110.0, time=5000, time_msc=5_000_000, reason=5, profit=863.55,
                              commission=-3.0, swap=-1.5, fee=0.0))
    assert src.closing(555) == {"price": 110.0, "ts": 5000, "profit": 856.05, "reason": "tp"}


# -- Setup en un perfil que opera de verdad -------------------------------------------------------------------------
def fresh_order(**kw):
    from dataclasses import replace
    from tradingbot.skills.setup import live
    now = live.server_now(None)
    return replace(ORDER, entry_ts=now - 60, close_ts=now + 3600, **kw)


class FakeSource:
    def __init__(self, fail=None):
        self.fail, self.calls, self.deal = fail, [], None

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

    def closing(self, ticket):
        return self.deal


def run_live(source, tmp_path):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus, got = EventBus(), {"executed": [], "closed": [], "account": [], "skipped": []}
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
    bus.publish("setup.order", {"order": fresh_order()}, source="cortex")
    wait(got["executed"])
    setup = manager.skills["setup"]
    manager.stop()
    p = got["executed"][0].payload
    assert source.calls == [("open", "NAS100", "long", 500.0, 95.0, 110.0)]         # 1 % de 50.000
    assert p["sent"] is True and "posición 555" in p["note"] and p["risk_amount"] == 499.95
    o = setup.positions[0]
    assert (o.ticket, o.volume, o.price, o.signal_price, o.risk_money) == (555, 90.9, 100.5, 100.0, 499.95)   # entrada: la de MT5
    assert any(e.payload.get("live") and e.payload["balance"] == 50_000.0 for e in got["account"])   # saldo real en la cabecera
    assert (tmp_path / "operativa_real.json").exists()                              # desde cuándo cuenta el Forwardtest


def test_las_senales_de_antes_del_arranque_no_se_abren_ni_cuentan(tmp_path):
    source = FakeSource()
    manager, bus, got = run_live(source, tmp_path)
    bus.publish("setup.order", {"order": ORDER}, source="cortex")                  # repaso al arrancar: entrada de hace años
    wait(got["skipped"])
    manager.stop()
    assert source.calls == [] and got["executed"] == [] and "antes" in got["skipped"][0].payload["note"]


def test_si_mt5_no_la_acepta_no_cuenta(tmp_path):
    manager, bus, got = run_live(FakeSource(fail="mercado cerrado"), tmp_path)
    bus.publish("setup.order", {"order": fresh_order()}, source="cortex")
    wait(got["skipped"])
    setup = manager.skills["setup"]
    manager.stop()
    assert got["executed"] == [] and got["skipped"][0].payload["note"] == "mercado cerrado" and setup.positions == []


def test_breakeven_en_mt5_y_el_cierre_es_el_de_la_cuenta(tmp_path):
    source = FakeSource()
    manager, bus, got = run_live(source, tmp_path)
    order = fresh_order()
    bus.publish("setup.order", {"order": order}, source="cortex")
    wait(got["executed"])
    t0 = order.entry_ts
    # +1 R desde la entrada real (100,5 con stop 95: 5,5 puntos) sin tocar el objetivo: el stop real pasa a 100,5
    df = pd.DataFrame({"ts": [t0, t0 + 900], "high": [101.0, 106.1], "low": [99.0, 101.0], "close": [100.5, 105.0]})
    bus.publish("setup.candles", {"symbol": "NAS100", "timeframe": "15m", "df": df}, source="cortex")
    time.sleep(0.3)
    assert ("stop", 555, 100.5) in source.calls and manager.skills["setup"].positions[0].be_sent
    assert got["closed"] == []                                                      # la simulada ya no cierra nada
    source.deal = {"price": 100.5, "ts": t0 + 1800, "profit": -6.0, "reason": "sl"}  # MT5 la cierra en el stop movido
    bus.publish("setup.candles", {"symbol": "NAS100", "timeframe": "15m", "df": df}, source="cortex")
    wait(got["closed"])
    manager.stop()
    p = got["closed"][0].payload
    c = p["closed"]
    assert (c.result, c.exit_price, c.exit_ts, c.r) == ("breakeven", 100.5, t0 + 1800, round(-6.0 / 499.95, 4))
    assert c.max_r == round(5.6 / 5.5, 4) and p["sent"] is True and p["real"]["profit"] == -6.0
    assert manager.skills["setup"].positions == [] and [c for c in source.calls if c[0] == "stop"] == [("stop", 555, 100.5)]


def test_cierre_por_tiempo_lo_hace_el_bot(tmp_path):
    from dataclasses import replace
    source = FakeSource()
    manager, bus, got = run_live(source, tmp_path)
    bus.publish("setup.order", {"order": fresh_order()}, source="cortex")
    wait(got["executed"])
    setup = manager.skills["setup"]
    setup.positions = [replace(setup.positions[0], close_ts=setup.server_now() - 1)]     # ya es la hora de cierre
    source.deal = {"price": 103.0, "ts": setup.server_now(), "profit": 227.25, "reason": "bot"}
    setup.tick()
    wait(got["closed"])
    manager.stop()
    assert ("close", 555) in source.calls and got["closed"][0].payload["closed"].result == "tiempo"
    assert got["closed"][0].payload["closed"].r == round(227.25 / 499.95, 4)


# -- challenge simulado: +8 % pasa de fase, -6 % de equity lo suspende ---------------------------------------------
def test_challenge_pasa_a_la_fase_2_con_el_8_por_ciento(tmp_path):
    from tradingbot.skills.setup.challenge import Challenge
    ch = Challenge(tmp_path / "challenge.json")
    assert [e["kind"] for e in ch.update(100_000, 100_000, "USD")] == ["inicio"]
    assert ch.levels() == (108_000.0, 94_000.0)
    assert ch.update(107_999, 108_500) == []                                       # el objetivo es de saldo, no de equity
    event = ch.update(108_100, 108_100)[0]
    assert event["kind"] == "fase" and event["phase"] == 1 and event["new"]["phase"] == 2
    assert ch.phase == 2 and ch.levels() == (116_748.0, 101_614.0)                 # la fase 2 empieza con el saldo de ese momento
    assert Challenge(tmp_path / "challenge.json").phase == 2                       # sigue al reiniciar
    assert ch.update(116_748, 116_748)[0]["kind"] == "superado" and ch.update(130_000, 130_000) == []


def test_challenge_se_suspende_con_el_6_por_ciento_de_drawdown(tmp_path):
    from tradingbot.skills.setup.challenge import Challenge
    ch = Challenge(tmp_path / "challenge.json")
    ch.update(100_000, 100_000)
    assert ch.update(99_000, 94_001) == []
    assert ch.update(99_000, 94_000)[0]["kind"] == "suspendido" and ch.failed
    assert ch.update(120_000, 120_000) == [] and ch.failed                          # suspendido: ya no cambia


def test_setup_avisa_del_challenge_y_al_suspender_cierra_y_no_abre_mas(tmp_path):
    source = FakeSource()
    manager, bus, got = run_live(source, tmp_path)
    events = []
    bus.subscribe("t", "setup.challenge", events.append)
    bus.publish("setup.order", {"order": fresh_order()}, source="cortex")
    wait(got["executed"])
    setup = manager.skills["setup"]
    setup.tick()                                                                    # 50.000: empieza la fase 1
    source.account = lambda: AccountSnapshot(50_000.0, 46_900.0, -3_100.0, "USD")   # equity -6,2 %
    setup.tick()
    wait(events, 2)
    bus.publish("setup.order", {"order": fresh_order()}, source="cortex")
    wait(got["skipped"])
    manager.stop()
    assert [e.payload["kind"] for e in events] == ["inicio", "suspendido"]
    assert ("close", 555) in source.calls and "suspendido" in got["skipped"][0].payload["note"]
    assert len([c for c in source.calls if c[0] == "open"]) == 1


def test_el_aviso_de_telegram_del_challenge():
    from tradingbot.skills.telegram import messages
    p = {"kind": "suspendido", "phase": 2, "phases": 2, "start": 108_100.0, "balance": 103_000.0, "equity": 101_600.0,
         "target": 116_748.0, "floor": 101_614.0, "target_pct": 8.0, "max_dd_pct": 6.0, "currency": "USD"}
    text = messages.challenge(p, "puprime_live")
    assert "suspendido" in text and "101,600.00 USD" in text and "puprime_live" in text


# -- otro proceso cambia el terminal de cuenta (la sincronización de otros perfiles) ------------------------------------
def test_si_el_terminal_esta_en_otra_cuenta_vuelve_a_la_suya(monkeypatch):
    mt5 = FakeMt5()
    monkeypatch.setitem(sys.modules, "MetaTrader5", mt5)
    src = Mt5Source(Mt5Profile("puprime_live", 7, "PUPrime-Demo", send_orders=True))
    src.connect()
    mt5.at = 114285263                                                   # la sincronización ha entrado en la de MetaQuotes
    assert src.account().balance == 50_000.0 and mt5.at == 7 and mt5.logins == [7]
    mt5.at, mt5.can_login = 114285263, False                             # y si no puede volver, no hay lectura (ni órdenes)
    assert src.account() is None
    with pytest.raises(TradeError, match="no se pudo volver"):
        src.open_market("NAS100", "long", 500.0, 95.0, 110.0)
    assert mt5.sent == []


def test_una_lectura_a_medias_no_es_la_cuenta(monkeypatch, tmp_path):
    from tradingbot.skills.setup.challenge import Challenge
    mt5 = FakeMt5()
    monkeypatch.setitem(sys.modules, "MetaTrader5", mt5)
    src = Mt5Source(Mt5Profile("puprime_live", 7, "PUPrime-Demo", send_orders=True))
    src.connect()
    mt5.equity = 0.0                                                     # saldo 50.000 y equity 0: el terminal cambiando de cuenta
    assert src.account() is None
    ch = Challenge(tmp_path / "challenge.json")
    ch.update(100_000, 100_000)
    assert ch.update(100_000, 0.0) == [] and not ch.failed               # el aviso de las 01:40: ya no suspende


def test_la_sincronizacion_no_cambia_de_cuenta_con_un_bot_que_opera_de_verdad(monkeypatch, tmp_path):
    from tradingbot import sync
    profiles = {"puprime_live": Mt5Profile("puprime_live", 7, "PUPrime-Demo", send_orders=True),
                "puprime": Mt5Profile("puprime", 7, "PUPrime-Demo"),
                "metaquotes": Mt5Profile("metaquotes", 114285263, "MetaQuotes-Demo")}
    done, lines = [], []
    monkeypatch.setattr(sync, "load_profiles", lambda _env: (profiles, "puprime"))
    monkeypatch.setattr(sync, "acquire_lock", lambda: tmp_path / "lock")
    monkeypatch.setattr(sync, "running_profiles", lambda names, root=None: {"puprime_live"})
    monkeypatch.setattr(sync, "sync_profile", lambda name, *a, **k: done.append(name) or "al día")
    monkeypatch.setattr(sync, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("builtins.print", lambda *a, **k: lines.append(a[0]))
    sync.main(["--sync-forwardtest", "--perfiles", "puprime", "metaquotes", "puprime_live"])
    assert done == ["puprime"]
    assert any("metaquotes: no se toca" in line for line in lines)


def test_las_operaciones_recuperadas_cuentan_en_el_challenge(tmp_path):
    import json
    from tradingbot.skills.setup.challenge import Challenge
    path = tmp_path / "challenge.json"
    ch = Challenge(path)
    ch.update(100_000, 100_000)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["ajuste_recuperadas"] = 1_791.40                                # no están en MT5, sí en el challenge
    path.write_text(json.dumps(data), encoding="utf-8")
    ch = Challenge(path)
    assert ch.update(100_000, 100_000) == [] and ch.summary()["adjustment"] == 1_791.40
    assert [e["kind"] for e in ch.update(106_300, 106_300)] == ["fase"]   # 106.300 + 1.791,40 >= 108.000


def test_las_velas_solo_de_su_cuenta(monkeypatch):
    mt5 = FakeMt5()
    monkeypatch.setitem(sys.modules, "MetaTrader5", mt5)
    src = Mt5Source(Mt5Profile("puprime_live", 7, "PUPrime-Demo", send_orders=True))
    src.connect()
    mt5.at = 114285263
    src._require()                                                       # vuelve a la suya antes de leer nada
    assert mt5.at == 7
    mt5.at, mt5.can_login = 114285263, False
    with pytest.raises(TradeError, match="otro broker"):
        src._require()


def test_la_cabecera_suma_las_recuperadas_al_saldo_real(tmp_path):
    import json
    (tmp_path / "challenge.json").write_text(json.dumps({"fase": 1, "estado": "en curso", "saldo_inicio_fase": 50_000.0,
                                                         "ajuste_recuperadas": 1_791.40}), encoding="utf-8")
    (tmp_path / "cuenta.json").write_text(json.dumps({"capital_inicial": 50_000.0, "moneda": "USD", "operaciones": []}),
                                          encoding="utf-8")
    source = FakeSource()
    manager, bus, got = run_live(source, tmp_path)
    wait(got["account"])
    manager.stop()
    p = [e.payload for e in got["account"] if e.payload.get("live")][-1]
    assert (p["balance"], p["real_balance"], p["recovered"]) == (51_791.40, 50_000.0, 1_791.40)
    assert p["balance"] - p["initial"] == pytest.approx(1_791.40)        # resultado del Forwardtest
    assert p["risk_amount"] == 500.0                                     # el riesgo de las órdenes, del saldo real
