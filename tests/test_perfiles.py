"""Perfiles: una cuenta por perfil con su saldo virtual, el stop a breakeven y la cabecera con el resultado del perfil."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import time
from datetime import date, datetime

import pandas as pd
import pytest

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.cortex.order import Order
from tradingbot.skills.feed.datasource import AccountSnapshot, Quote
from tradingbot.skills.setup.account import Schedule, VirtualAccount, outcome
from tradingbot.skills.setup.positions import Closed, resolve

M15 = 900


def order(direction="long", price=100.0, stop=95.0, target=110.0, entry_ts=0):
    return Order("NAS100", "15m", direction, "Patrón de prueba", "p", "NY Open", date(2026, 10, 19), 0, 0, 0, price, stop,
                 target, "Bullish", 3.0, "GO", None, entry_ts, entry_ts + 24 * 3600)


def bars(rows, step=M15):
    """rows: (high, low, close) por vela, desde ts = 0."""
    return ([i * step for i in range(len(rows))], [r[0] for r in rows], [r[1] for r in rows], [r[2] for r in rows])


# -- breakeven ---------------------------------------------------------------------------------
def test_con_un_1r_a_favor_al_cierre_de_m15_el_stop_pasa_a_la_entrada_y_cierra_a_0():
    ts, high, low, close = bars([(105.5, 99.0, 105.2), (106.0, 99.9, 100.5), (101.0, 98.0, 99.0)])
    closed = resolve(order(), ts, high, low, close, be_r=1.0, bar_seconds=M15)
    assert closed.result == "breakeven" and closed.r == 0 and closed.exit_price == 100.0
    assert closed.exit_ts == M15 and closed.be_ts == 0 and outcome(closed.r) == "B"


def test_sin_breakeven_la_misma_operacion_acaba_en_stop():
    ts, high, low, close = bars([(105.5, 99.0, 105.2), (106.0, 99.9, 100.5), (101.0, 94.0, 95.0)])
    closed = resolve(order(), ts, high, low, close)
    assert closed.result == "stop" and closed.r == -1 and closed.be_ts is None


def test_el_breakeven_solo_se_mira_al_cierre_de_las_velas_de_15_min():
    # Velas de 5 min: la primera (0-5) cierra +1 R, pero no es cierre de M15; la tercera (10-15) sí, y ya está a +0,4 R.
    ts, high, low, close = bars([(105.5, 99.5, 105.1), (105.0, 101.0, 103.0), (103.0, 101.0, 102.0), (102.0, 99.0, 99.5),
                                 (99.0, 94.0, 94.5)], step=300)
    closed = resolve(order(), ts, high, low, close, be_r=1.0, bar_seconds=300)
    assert closed.result == "stop" and closed.be_ts is None


def test_la_vela_que_aun_se_forma_no_mueve_el_stop_y_en_cortos_tambien_funciona():
    ts, high, low, close = bars([(101.0, 94.0, 94.5)])
    assert resolve(order("short", 100.0, 105.0, 90.0), ts, high, low, close, be_r=1.0, bar_seconds=M15) is None
    ts, high, low, close = bars([(101.0, 94.0, 94.5), (100.2, 96.0, 99.0)])
    closed = resolve(order("short", 100.0, 105.0, 90.0), ts, high, low, close, be_r=1.0, bar_seconds=M15)
    assert closed.result == "breakeven" and closed.r == 0


# -- cuenta virtual ----------------------------------------------------------------------------
def test_la_cuenta_virtual_empieza_con_el_saldo_y_suma_r_por_riesgo(tmp_path):
    path = tmp_path / "cuenta.json"
    acc = VirtualAccount(path, now=lambda: datetime(2026, 10, 19, 9, 0))
    assert acc.book(order(), Closed("objetivo", 110, 1, 2.0, 10.0), 1.0) is None       # sin capital inicial no apunta
    assert acc.start(100_000, "USD") and not acc.start(5, "EUR")                         # solo la primera vez
    assert acc.book(order(), Closed("objetivo", 110, 1, 2.0, 10.0), 1.0) == 2000.0      # +2 R con riesgo 1 % de 100.000
    assert acc.book(order(), Closed("stop", 95, 2, -1.0, -5.0), 1.0) == -1020.0         # 1 % de 102.000
    assert acc.book(order(), Closed("breakeven", 100, 3, 0.0, 0.0), 1.0) == 0.0
    again = VirtualAccount(path)                                                         # sigue ahí al reiniciar
    assert again.initial == 100_000 and again.balance == 100_980 and again.since == "2026-10-19T09:00:00"
    s = again.summary(1.0, [order()])
    assert (s["wins"], s["losses"], s["breakeven"]) == (1, 1, 1) and s["currency"] == "USD"
    assert s["open"] == [{"symbol": "NAS100", "direction": "long", "price": 100.0, "stop": 95.0}]


class FakeSource:
    def account(self):
        return AccountSnapshot(50_000.0, 50_000.0, 0.0, "USD")


def wait_for(items, n=1, seconds=3.0):
    deadline = time.time() + seconds
    while len(items) < n and time.time() < deadline:
        time.sleep(0.02)


def test_setup_fija_el_capital_al_conectar_y_consolida_el_forwardtest(tmp_path):
    """Setup cierra la operación, Stats la anota en el diario del perfil y, con la hora del servidor, la vela de 3 h del
    cierre ya terminó (todo ocurrió en 1970): pasa al saldo virtual."""
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus, accounts, closed, consolidated = EventBus(), [], [], []
    bus.subscribe("t", "setup.account", accounts.append)
    bus.subscribe("t", "setup.closed", closed.append)
    bus.subscribe("t", "setup.consolidated", consolidated.append)
    folder = tmp_path / "perfiles" / "puprime"
    cfg = {"app": {"data_dir": str(folder)}}
    manager = SkillManager(bus, Services(FakeSource(), None, cfg, EnvConfig(parse(""))),
                           [{"type": "setup"}, {"type": "stats"}])
    manager.start()
    bus.publish("feed.connected", {"info": "", "symbols": []}, source="feed")
    bus.publish("setup.order", {"order": order()}, source="cortex")
    df = pd.DataFrame({"ts": [0, M15, 2 * M15], "high": [105.5, 106.0, 101.0], "low": [99.0, 99.9, 98.0],
                       "close": [105.2, 100.5, 99.0]})
    bus.publish("setup.candles", {"symbol": "NAS100", "timeframe": "15m", "df": df}, source="cortex")
    wait_for(closed)
    deadline = time.time() + 3
    while not list(folder.glob("forwardtest/*.jsonl")) and time.time() < deadline:
        time.sleep(0.02)
    time.sleep(0.1)
    bus.publish("clock.offset", {"server_offset": 3 * 3600, "offset_source": "detectado"}, source="quotes")
    wait_for(consolidated)
    time.sleep(0.1)
    manager.stop()
    p = closed[0].payload
    assert p["closed"].result == "breakeven" and p["consolidate_at"] == 3 * 3600 and p["consolidate_hours"] == 3
    c = consolidated[0].payload
    assert [t["result"] for t in c["trades"]] == ["breakeven"] and c["balance"] == 50_000.0
    last = accounts[-1].payload
    assert last["started"] and last["initial"] == 50_000 and last["breakeven"] == 1 and last["open"] == []
    assert last["pending"] == 0
    assert (folder / "cuenta.json").exists() and (folder / "abiertas.json").exists()   # los datos van en su perfil


# -- consolidación del forwardtest ------------------------------------------------------------
H = 3600


def closing(symbol, exit_ts, r, entry_ts):
    from dataclasses import replace
    o = replace(order(entry_ts=entry_ts), symbol=symbol)
    return o,Closed("objetivo" if r > 0 else "stop" if r < 0 else "breakeven", 100.0, exit_ts, r, 0.0)


def test_cada_cierre_se_consolida_al_terminar_su_vela_de_3h_indices_o_4h_resto():
    sched = Schedule()
    assert sched.due("NAS100", 10 * H + 5) == 12 * H and sched.due("USTEC.s", 12 * H) == 15 * H     # índices: 3 h
    assert sched.due("EURUSD", 10 * H + 5) == 12 * H and sched.due("XAUUSD", 12 * H + 1) == 16 * H  # resto: 4 h
    with pytest.raises(ValueError, match="SETUP_CONSOLIDATE_HOURS"):
        Schedule(3, 5)


def test_la_cuenta_consolida_lo_que_toca_y_deja_lo_demas_pendiente(tmp_path):
    acc = VirtualAccount(tmp_path / "cuenta.json")
    closes = [closing("NAS100", 10 * H, -1.0, 9 * H), closing("EURUSD", 13 * H, 2.0, 11 * H),
              closing("US500", 11 * H, 0.0, 10 * H)]
    assert acc.consolidate(closes, 20 * H, 1.0, Schedule()) == [] and len(acc.pending) == 3    # sin capital: nada
    acc.start(100_000, "USD")
    new = acc.consolidate(closes, 12 * H, 1.0, Schedule())        # a las 12: la vela de 9-12 de los índices terminó
    assert [t["symbol"] for t in new] == ["NAS100", "US500"] and acc.balance == 99_000
    assert acc.pending == [16 * H]                                # EURUSD (cerró a las 13): al acabar la vela de 12-16
    assert acc.summary(1.0)["pending"] == 1 and acc.summary(1.0)["next_at"] == 16 * H
    assert acc.consolidate(closes, 15 * H, 1.0, Schedule()) == []
    assert [t["symbol"] for t in acc.consolidate(closes, 16 * H, 1.0, Schedule())] == ["EURUSD"]
    assert acc.balance == 99_000 + 1_980 and acc.pending == []    # +2 R con el 1 % de 99.000
    assert acc.consolidate(closes, 30 * H, 1.0, Schedule()) == []                     # nunca dos veces la misma
    again = VirtualAccount(tmp_path / "cuenta.json")
    assert again.balance == 100_980 and (again.count("G"), again.count("P"), again.count("B")) == (1, 1, 1)


def test_el_diario_da_todas_las_cerradas_sin_repetir(tmp_path):
    from tradingbot.skills.stats.journal import Journal
    months = iter([datetime(2026, 9, 30, 22), datetime(2026, 10, 1, 9), datetime(2026, 10, 1, 9, 5)])
    j = Journal(tmp_path, now=lambda: next(months))
    a, b = closing("NAS100", 10 * H, -1.0, 9 * H), closing("EURUSD", 13 * H, 2.0, 11 * H)
    j.closed(*a)
    j.closed(*b)
    j.closed(*b)                                                  # repetida (p. ej. tras reiniciar): una sola vez
    got = j.closes()
    assert sorted((o.symbol, c.r) for o, c in got) == [("EURUSD", 2.0), ("NAS100", -1.0)]


# -- configuración -----------------------------------------------------------------------------
def test_los_perfiles_tienen_nombre_visible_y_terminal_propio(tmp_path):
    from tradingbot.config import load_profiles
    env = tmp_path / ".env"
    env.write_text("MT5_DEFAULT=metaquotes\nMT5_PATH=C:\\mt5\\terminal64.exe\n"
                   "MT5_METAQUOTES_LOGIN=1\nMT5_METAQUOTES_SERVER=MetaQuotes-Demo\n"
                   "MT5_PUPRIME_LOGIN=2\nMT5_PUPRIME_SERVER=PUPrime-Demo\nMT5_PUPRIME_NAME=PUPrime-Demo\n"
                   "MT5_PUPRIME_PATH=C:\\puprime\\terminal64.exe\n", encoding="utf-8")
    profiles, default = load_profiles(env)
    assert default == "metaquotes" and profiles["metaquotes"].display == "metaquotes"
    assert profiles["puprime"].display == "PUPrime-Demo" and profiles["puprime"].label.startswith("PUPrime-Demo - 2 @")
    assert profiles["puprime"].terminal_path == "C:\\puprime\\terminal64.exe"
    assert profiles["metaquotes"].terminal_path == "C:\\mt5\\terminal64.exe"


def test_el_ultimo_perfil_elegido_se_recuerda(tmp_path):
    from tradingbot import settings
    path = tmp_path / "s.json"
    assert settings.load_profile(path) is None
    settings.save_watchlist(["NAS100"], path)
    settings.save_profile("PUPrime", path)
    assert settings.load_profile(path) == "puprime" and settings.load_watchlist([], path) == ["NAS100"]


def test_cada_perfil_tiene_su_lista_de_quotes(tmp_path):
    from tradingbot import settings
    path = tmp_path / "s.json"
    settings.save_watchlist(["NAS100", "USOIL"], path)                       # la de antes de los perfiles: la común
    settings.save_watchlist(["NAS100", "XAUUSD.s"], path, profile="PUPrime")
    assert settings.load_watchlist([], path, profile="puprime") == ["NAS100", "XAUUSD.s"]
    assert settings.load_watchlist([], path, profile="metaquotes") == ["NAS100", "USOIL"]   # sin lista propia: la común
    assert settings.load_watchlist([], path) == ["NAS100", "USOIL"]


# PUPrime-Demo: los mercados llevan el sufijo .s y el petróleo se llama CL-OIL.s; tiene acciones DOW, CL y SPX.
PUPRIME = ["NAS100.s", "NAS100ft.s", "SP500.s", "SP500ft.s", "SPX", "DJ30.s", "DJ30ft.s", "DOW", "EURUSD", "EURUSD.s",
           "XAUUSD.s", "XAUUSD.crp", "CL-OIL.s", "CL", "BTCUSD", "BTCUSD#", "ETHUSD"]


def names(listing):
    return {n.lower(): n for n in listing}


@pytest.mark.parametrize("ours, theirs", [
    ("NAS100", "NAS100.s"), ("nas100", "NAS100.s"), ("SP500", "SP500.s"), ("DJ30", "DJ30.s"), ("EURUSD", "EURUSD"),
    ("XAUUSD", "XAUUSD.s"), ("USOIL", "CL-OIL.s"), ("BTCUSD", "BTCUSD"), ("ETHUSD", "ETHUSD"), ("US500", "SP500.s"),
    ("GER40", None)])
def test_los_mercados_se_traducen_al_nombre_del_broker(ours, theirs):
    from tradingbot.skills.feed.mt5_client import equivalent
    assert equivalent(ours, names(PUPRIME)) == theirs


def test_la_equivalencia_propia_del_perfil_manda(tmp_path):
    from tradingbot.config import ConfigError, load_profiles
    from tradingbot.skills.feed.mt5_client import equivalent
    env = tmp_path / ".env"
    env.write_text("MT5_PUPRIME_LOGIN=2\nMT5_PUPRIME_SERVER=PUPrime-Demo\n"
                   "MT5_PUPRIME_SYMBOLS=NAS100=NAS100ft.s, usoil = CL-OIL.s\n", encoding="utf-8")
    profile = load_profiles(env)[0]["puprime"]
    assert profile.symbol_map == {"nas100": "NAS100ft.s", "usoil": "CL-OIL.s"}
    assert equivalent("NAS100", names(PUPRIME), profile.symbol_map) == "NAS100ft.s"
    assert equivalent("NAS100", names(PUPRIME), {"nas100": "NOEXISTE"}) is None   # si el broker no lo tiene, se avisa
    env.write_text("MT5_PUPRIME_LOGIN=2\nMT5_PUPRIME_SERVER=PUPrime-Demo\nMT5_PUPRIME_SYMBOLS=NAS100\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="MT5_PUPRIME_SYMBOLS"):
        load_profiles(env)


def test_al_cambiar_de_perfil_se_arranca_igual_pero_con_el_otro():
    from tradingbot.__main__ import relaunch_args
    assert relaunch_args(["--theme", "negro", "--profile", "metaquotes"], "puprime") == \
        ["-m", "tradingbot", "--theme", "negro", "--profile", "puprime"]
    assert relaunch_args(["--profile=metaquotes"], "puprime") == ["-m", "tradingbot", "--profile", "puprime"]


def test_los_datos_antiguos_pasan_al_perfil_por_defecto(tmp_path, monkeypatch):
    from tradingbot import __main__ as entry
    from tradingbot import config
    monkeypatch.setattr(entry, "PROJECT_ROOT", tmp_path)
    (tmp_path / "data" / "setup").mkdir(parents=True)
    (tmp_path / "data" / "setup" / "abiertas.json").write_text("[]", encoding="utf-8")
    (tmp_path / "data" / "forwardtest").mkdir()
    entry.migrate_legacy_data("puprime", "metaquotes")                                   # otro perfil: no se toca
    assert not config.profile_dir("puprime").exists()
    entry.migrate_legacy_data("metaquotes", "metaquotes")
    assert (config.profile_dir("metaquotes") / "abiertas.json").exists()
    assert (config.profile_dir("metaquotes") / "forwardtest").is_dir()
    assert not (tmp_path / "data" / "forwardtest").exists()


# -- letra ---------------------------------------------------------------------------------------
def test_ui_font_elige_la_letra_del_mockup_o_la_clasica():
    from tradingbot.ui import theme
    try:
        theme.set_font("mockup")
        sheet = theme.stylesheet()
        assert '"Inter"' in sheet.split("font-family:")[1].split(";")[0] and "font-weight: 700" not in sheet
        theme.set_font("clasica")
        assert "font-weight: 700" in theme.stylesheet() and theme.font_families()[0] == "Segoe UI"
        with pytest.raises(theme.ThemeError):
            theme.set_font("comic")
    finally:
        theme.set_font(None)


# -- cabecera ------------------------------------------------------------------------------------
def make_window(tmp_path, monkeypatch, app_extra=None):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui.main_window import MainWindow
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "NAS100", "timeframe": "15m", "watchlist": ["NAS100"], **(app_extra or {})}}
    return MainWindow(EventBus(), SkillManager(EventBus(), Services(None, None, cfg, EnvConfig()), []), cfg, "t")


def test_la_cabecera_muestra_el_saldo_virtual_el_resultado_y_g_p_b(tmp_path, monkeypatch):
    win = make_window(tmp_path, monkeypatch, {"profiles": [("metaquotes", "metaquotes"), ("puprime", "PUPrime-Demo")],
                                               "profile_name": "puprime"})
    assert win.profile_box.currentText() == "PUPrime-Demo" and win.profile_box.count() == 2
    assert not hasattr(win, "stat_open")                                                 # «Mercados abiertos» ya no está
    win._on_setup_account({"started": True, "initial": 100_000.0, "balance": 102_350.0, "currency": "USD",
                           "since": "2026-10-19T09:00:00", "wins": 7, "losses": 3, "breakeven": 1, "risk_pct": 1.0,
                           "risk_amount": 1023.5, "open": [{"symbol": "NAS100", "direction": "long", "price": 100.0,
                                                            "stop": 95.0}]})
    assert win.stat_balance.value.text() == "102,350.00"
    assert win.stat_result.value.text() == "+2.35%" and "capital inicial 100,000" in win.stat_result.sub.text()
    assert "#9E9E9E" in win.stat_trades.value.text() and win.stat_trades.sub.text() == "ninguna hoy"   # sin forwardtest de hoy
    win.last_quotes = {"nas100": Quote("NAS100", 102.5, 102.6, 0)}                       # +0,5 R flotante
    win._apply_account(None)
    assert win.stat_pnl.value.text() == "+511.75" and "equity 102,861.75" in win.stat_balance.sub.text()


def test_la_tarjeta_operaciones_muestra_solo_el_dia_en_curso(tmp_path, monkeypatch):
    from dataclasses import replace
    from datetime import timezone
    from tradingbot.skills.stats.session import TradeStats
    from tradingbot.ui.stats_dialog import _ny_today
    win = make_window(tmp_path, monkeypatch)
    noon = _ny_today().replace(hour=12, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    now = int(noon.timestamp()) + win.ny_shift                                  # hoy a mediodía NY, hora del servidor
    s = TradeStats()
    for i, (r, when) in enumerate(((2.0, now - 60), (-1.0, now - 120), (0.0, now - 180), (2.0, now - 2 * 86400))):
        o = replace(order(), entry_ts=when, symbol=f"M{i}")
        s.executed(o)
        s.closed(o, Closed("objetivo" if r > 0 else "stop", 0.0, when + 60, r, 0.1))
    s.executed(replace(order(), entry_ts=now - 30, symbol="ABIERTA"))
    win._on_stats_session({"stats": s})
    text = win.stat_trades.value.text()
    assert "1 G" in text and "1 P" in text and "1 B" in text                     # la de hace dos días no cuenta
    assert win.stat_trades.sub.text() == "3 cerradas · 1 abierta hoy · +1.00 R"


# -- perfil Calendario: la cuenta de PUPrime, solo con su estrategia y 25.000 USD simulados --------------------------
def test_un_perfil_con_base_usa_la_cuenta_de_otro_y_trae_su_estrategia_y_capital(tmp_path):
    from tradingbot.config import load_profiles, strategy_skills
    env = tmp_path / ".env"
    env.write_text("MT5_PUPRIME_LOGIN=7\nMT5_PUPRIME_SERVER=PUPrime-Demo\nMT5_PUPRIME_PASSWORD=x\n"
                   "MT5_CALENDARIO_BASE=puprime\nMT5_CALENDARIO_NAME=Calendario\nMT5_CALENDARIO_STRATEGY=Calendario\n"
                   "MT5_CALENDARIO_CAPITAL=25000\n", encoding="utf-8")
    profiles, _ = load_profiles(env)
    cal, pup = profiles["calendario"], profiles["puprime"]
    assert (cal.login, cal.server, cal.password) == (pup.login, pup.server, pup.password)
    assert (cal.strategy, cal.capital, cal.currency, cal.display) == ("calendario", 25_000.0, "USD", "Calendario")
    assert pup.strategy == "" and pup.capital is None
    kept = strategy_skills([{"type": t} for t in ("cortex", "pattern", "tbr", "calendario")], "calendario")
    assert [s["type"] for s in kept] == ["cortex", "calendario"]


def test_la_base_tiene_que_ser_otro_perfil(tmp_path):
    from tradingbot.config import ConfigError, load_profiles
    env = tmp_path / ".env"
    env.write_text("MT5_A_BASE=nadie\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_profiles(env)


def test_el_capital_simulado_fijo_no_depende_del_saldo_de_mt5(tmp_path):
    acc = VirtualAccount(tmp_path / "cuenta.json")
    assert acc.start(25_000, "USD") and acc.initial == 25_000 and acc.currency == "USD"
    assert not acc.start(100_000, "EUR") and VirtualAccount(tmp_path / "cuenta.json").initial == 25_000


def test_la_lista_de_mercados_de_un_perfil_de_estrategia_no_hereda_la_comun(tmp_path):
    from tradingbot import settings
    path = tmp_path / "s.json"
    settings.save_watchlist(["EURUSD", "XAUUSD"], path)
    assert settings.load_watchlist(["NAS100", "DJ30"], path, profile="calendario", common=False) == ["NAS100", "DJ30"]
    assert settings.load_watchlist(["NAS100", "DJ30"], path, profile="calendario") == ["EURUSD", "XAUUSD"]
    settings.save_watchlist(["DJ30"], path, profile="calendario")
    assert settings.load_watchlist(["NAS100"], path, profile="calendario", common=False) == ["DJ30"]
