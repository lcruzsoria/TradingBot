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
from tradingbot.skills.setup.account import VirtualAccount, outcome
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


def test_setup_fija_el_capital_al_conectar_y_lleva_el_saldo_al_cerrar(tmp_path):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus, accounts, closed = EventBus(), [], []
    bus.subscribe("t", "setup.account", accounts.append)
    bus.subscribe("t", "setup.closed", closed.append)
    cfg = {"app": {"data_dir": str(tmp_path / "perfiles" / "puprime")}}
    manager = SkillManager(bus, Services(FakeSource(), None, cfg, EnvConfig(parse(""))), [{"type": "setup"}])
    manager.start()
    bus.publish("feed.connected", {"info": "", "symbols": []}, source="feed")
    bus.publish("setup.order", {"order": order()}, source="cortex")
    df = pd.DataFrame({"ts": [0, M15, 2 * M15], "high": [105.5, 106.0, 101.0], "low": [99.0, 99.9, 98.0],
                       "close": [105.2, 100.5, 99.0]})
    bus.publish("setup.candles", {"symbol": "NAS100", "timeframe": "15m", "df": df}, source="cortex")
    deadline = time.time() + 3
    while not closed and time.time() < deadline:
        time.sleep(0.02)
    time.sleep(0.15)
    manager.stop()
    p = closed[0].payload
    assert p["closed"].result == "breakeven" and p["amount"] == 0.0 and p["balance"] == 50_000.0
    last = accounts[-1].payload
    assert last["started"] and last["initial"] == 50_000 and last["breakeven"] == 1 and last["open"] == []
    assert (tmp_path / "perfiles" / "puprime" / "cuenta.json").exists()                  # los datos van en su perfil
    assert (tmp_path / "perfiles" / "puprime" / "abiertas.json").exists()


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
    trades = win.stat_trades.value.text()
    assert "7 G" in trades and "3 P" in trades and "1 B" in trades and "#9E9E9E" in trades
    assert win.stat_trades.sub.text().startswith("11 cerradas desde el")
    win.last_quotes = {"nas100": Quote("NAS100", 102.5, 102.6, 0)}                       # +0,5 R flotante
    win._apply_account(None)
    assert win.stat_pnl.value.text() == "+511.75" and "equity 102,861.75" in win.stat_balance.sub.text()
