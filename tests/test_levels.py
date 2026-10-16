"""Niveles del día (TDO, Midnight, PDH / PDL) y separadores de día."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.levels import daylevels as levels
from tradingbot.skills.levels.daylevels import compute, days, is_us_index, parse_time

AHEAD = 7 * 3600                                       # servidor = NY + 7 h
DAY0 = int(datetime(2026, 10, 6, tzinfo=timezone.utc).timestamp())   # martes 6 oct, 00:00 del servidor
FOREX, INDEX = 17 * 60, 18 * 60                        # inicio del día en NY: 17:00 / 18:00


def hourly(n_days: int = 3):
    """Velas H1 de 00:00 a 23:00 del servidor (00:00 servidor = 17:00 NY; 01:00 servidor = 18:00 NY)."""
    ts = [DAY0 + d * 86400 + h * 3600 for d in range(n_days) for h in range(24)]
    base = np.arange(len(ts), dtype=float)
    return np.array(ts, dtype=np.int64), base + 0.5, base + 1.0, base


def by_kind(lines, kind):
    return [line for line in lines if line.kind == kind]


def test_inicio_del_dia_segun_el_activo():
    assert parse_time("17:00", "K") == 1020 and parse_time("9:30", "K") == 570
    with pytest.raises(ValueError, match="HH:MM"):
        parse_time("25:00", "LEVELS_DAY_START")
    indices = levels.DEFAULT_US_INDICES
    assert is_us_index("NAS100.r", indices) and is_us_index("nas100ft.r", indices) and is_us_index("SP500", indices)
    assert not is_us_index("EURUSD", indices) and not is_us_index("XAUUSD", indices)
    ts, *_ = hourly(3)
    # forex: el día empieza a las 17:00 NY = vela 00:00 del servidor
    assert [d.x0 for d in days(ts, AHEAD, FOREX)] == [-0.5, 23.5, 47.5]
    # índices: a las 18:00 NY = vela 01:00 del servidor (la de las 00:00 es aún del día anterior)
    assert [d.x0 for d in days(ts, AHEAD, INDEX)] == [-0.5, 0.5, 24.5, 48.5]


def test_nombre_del_dia_centrado_entre_separadores():
    ts, *_ = hourly(3)
    d = days(ts, AHEAD, FOREX)
    # el día que empieza el lunes 5 a las 17:00 NY (servidor martes 00:00) es el MARTES
    assert [x.label for x in d] == ["MARTES", "MIÉRCOLES", "JUEVES"]
    assert d[1].center == (23.5 + 47.5) / 2                    # entre su separador y el siguiente
    assert d[-1].x1 == len(ts) - 0.5                           # el de hoy, hasta la última vela


def test_tdo_midnight_pdh_y_pdl_de_cada_dia():
    ts, o, h, l = hourly(3)
    lines = compute(ts, o, h, l, AHEAD, FOREX, days_back=10)
    tdo = by_kind(lines, "tdo")
    assert [t.price for t in tdo] == [0.5, 24.5, 48.5]                   # open de la vela de las 17:00 NY
    assert (tdo[0].x0, tdo[0].x1) == (-0.5, 23.5)
    assert tdo[-1].x1 == len(ts) - 1 + levels.EXTEND_BARS
    midnight = by_kind(lines, "midnight")                                # 00:00 NY = 07:00 del servidor
    assert [m.price for m in midnight] == [7.5, 31.5, 55.5] and midnight[0].x0 == 6.5
    pdh, pdl = by_kind(lines, "pdh"), by_kind(lines, "pdl")
    assert [p.price for p in pdh] == [24.0, 48.0] and [p.price for p in pdl] == [0.0, 24.0]
    assert (pdh[0].x0, pdh[0].x1) == (23.5, 47.5)
    # índices: el TDO es la vela de las 18:00 NY
    assert [t.price for t in by_kind(compute(ts, o, h, l, AHEAD, INDEX), "tdo")][1:] == [1.5, 25.5, 49.5]


def test_solo_los_ultimos_dias_y_sin_velas():
    ts, o, h, l = hourly(5)
    assert len(by_kind(compute(ts, o, h, l, AHEAD, FOREX, days_back=2), "tdo")) == 2
    assert compute(np.array([], dtype=np.int64), [], [], [], AHEAD, FOREX) == []
    assert days(np.array([], dtype=np.int64), AHEAD, FOREX) == []


def run_skill(env_text, timeframe="1h", symbol="EURUSD"):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus, events = EventBus(), []
    bus.subscribe("t", "levels.updated", events.append)
    manager = SkillManager(bus, Services(None, None, {"app": {}}, EnvConfig(parse(env_text))), [{"type": "levels"}])
    manager.start()
    ts, o, h, l = hourly(3)
    df = pd.DataFrame({"ts": ts, "open": o, "high": h, "low": l, "close": o})
    bus.publish("candles.loaded", {"symbol": symbol, "timeframe": timeframe, "df": df}, source="feed")
    deadline = time.time() + 3
    while not events and time.time() < deadline:
        time.sleep(0.02)
    manager.stop()
    return manager.skills["levels"], events


def test_la_skill_usa_la_hora_de_inicio_de_cada_activo():
    _, events = run_skill("LEVELS_PDHL_COLOR=#00ff00\n")
    p = events[-1].payload
    assert p["available"] and p["day_start"] == FOREX and len(p["days"]) == 3 and p["colors"]["pdhl"] == "#00FF00"
    assert {line.kind for line in p["lines"]} == {"tdo", "midnight", "pdh", "pdl"}
    _, events = run_skill("", symbol="NAS100.r")
    assert events[-1].payload["day_start"] == INDEX and len(events[-1].payload["days"]) == 4
    _, events = run_skill("LEVELS_US_INDICES=GER40\nLEVELS_INDEX_DAY_START=19:30\n", symbol="ger40.r")
    assert events[-1].payload["day_start"] == 19 * 60 + 30
    _, events = run_skill("LEVELS_SEPARATORS=false\n", timeframe="1d")
    assert events[-1].payload["available"] is False and events[-1].payload["lines"] == []
    skill, events = run_skill("LEVELS_DAY_START=5pm\n")
    assert skill.state.value == "error" and "LEVELS_DAY_START" in skill.note and not events


def test_los_botones_muestran_cada_nivel(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "1h", "watchlist": ["EURUSD"]}}
    bus = EventBus()
    env = EnvConfig(parse("LEVELS_SHOW_PDHL=true\n"))
    win = MainWindow(bus, SkillManager(bus, Services(None, None, cfg, env), [{"type": "levels"}]), cfg, "t")
    assert [b.text() for b in win.level_btns.values()] == ["TDO", "Midnight", "PDH/PDL"]
    assert win.level_btns["pdhl"].isChecked() and not win.level_btns["tdo"].isChecked()   # LEVELS_SHOW_PDHL
    ts, o, h, l = hourly(3)
    df = pd.DataFrame({"ts": ts, "open": o, "high": h, "low": l, "close": o, "time": pd.to_datetime(ts, unit="s")})
    win._on_candles({"df": df, "symbol": "EURUSD", "timeframe": "1h", "seconds": 0.1})
    win._on_day_levels({"symbol": "EURUSD", "timeframe": "1h", "lines": compute(ts, o, h, l, AHEAD, FOREX),
                        "days": days(ts, AHEAD, FOREX), "day_start": FOREX, "available": True, "estimated": False,
                        "max_tf": 720, "sma": df["close"].rolling(5).mean().to_numpy(), "sma_period": 5, "sma_style": "punteado",
                        "colors": {"tdo": "#787B86", "midnight": "#FF9800", "pdhl": "#2962FF", "separator": "#787B86",
                                   "sma": "#00ACC1"}})
    only_pdhl = win.chart.day_item_count                    # 2 curvas + 4 rótulos (PDH y PDL de 2 días)
    assert only_pdhl == 6
    win.level_btns["tdo"].setChecked(True)
    assert win.chart.day_item_count == only_pdhl + 1 + 3   # + curva TDO y sus 3 rótulos
    win.level_btns["tdo"].setChecked(False)
    win.level_btns["pdhl"].setChecked(False)
    assert win.chart.day_item_count == 0
    seps = win.chart.separators                             # no dependen de los botones
    assert list(seps._x) == [23.5, 47.5] and seps._labels == ["MARTES", "MIÉRCOLES", "JUEVES"]
    assert list(seps._centers) == [11.5, 35.5, 59.5]


def test_la_sma_se_calcula_con_las_velas_visibles_y_se_reconfigura():
    skill, events = run_skill("LEVELS_SMA_PERIOD=5\nLEVELS_SMA_COLOR=#ff0000\nLEVELS_SMA_STYLE=punteado\n")
    p = events[-1].payload
    assert p["sma_period"] == 5 and p["sma_style"] == "punteado" and p["colors"]["sma"] == "#FF0000"
    assert len(p["sma"]) == 72 and np.isnan(p["sma"][3]) and not np.isnan(p["sma"][4])      # los 4 primeros, sin media
    _, events = run_skill("")
    assert events[-1].payload["sma_period"] == 30 and events[-1].payload["sma_style"] == "normal"   # por defecto
    skill, events = run_skill("LEVELS_SMA_STYLE=rayas\n")
    assert skill.state.value == "error" and "LEVELS_SMA_STYLE" in skill.note
    skill, events = run_skill("LEVELS_SMA_PERIOD=0\n")
    assert skill.state.value == "error" and "LEVELS_SMA_PERIOD" in skill.note


def test_el_boton_sma_dibuja_y_configura_la_media(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import envconfig, settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    env_file = tmp_path / "tradingbot.env"
    env_file.write_text("LEVELS_SMA_PERIOD=30\n", encoding="utf-8")
    monkeypatch.setattr(envconfig, "ENV_FILE", env_file)
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "1h", "watchlist": ["EURUSD"]}}
    bus, published = EventBus(), []
    bus.subscribe("t", "levels.sma", published.append)
    win = MainWindow(bus, SkillManager(bus, Services(None, None, cfg, EnvConfig(parse(""))), [{"type": "levels"}]), cfg, "t")
    assert win.sma_btn.text() == "SMA" and not win.sma_btn.isChecked()
    ts, o, h, l = hourly(3)
    df = pd.DataFrame({"ts": ts, "open": o, "high": h, "low": l, "close": o, "time": pd.to_datetime(ts, unit="s")})
    win._on_candles({"df": df, "symbol": "EURUSD", "timeframe": "1h", "seconds": 0.1})
    win._on_day_levels({"symbol": "EURUSD", "timeframe": "1h", "lines": [], "days": [], "day_start": FOREX, "available": True,
                        "estimated": False, "max_tf": 720, "sma": df["close"].rolling(5).mean().to_numpy(), "sma_period": 5,
                        "sma_style": "discontinuo", "colors": {"sma": "#FF0000", "separator": "#787B86"}})
    assert not win.chart.sma_drawn                          # el botón está apagado
    win.sma_btn.setChecked(True)
    assert win.chart.sma_drawn
    win.sma_btn.setChecked(False)
    assert not win.chart.sma_drawn
    win._apply_sma(50, "#00FF00", "punteado")
    saved = envconfig.parse(env_file.read_text(encoding="utf-8"))
    assert saved["LEVELS_SMA_PERIOD"] == "50" and saved["LEVELS_SMA_COLOR"] == "#00FF00" and saved["LEVELS_SMA_STYLE"] == "punteado"
    assert published[-1].payload == {"period": 50, "color": "#00FF00", "style": "punteado"}


def test_cierre_de_mercados_futuros_de_indices_a_diario_y_forex_el_viernes():
    from zoneinfo import ZoneInfo
    from tradingbot.skills.levels.daylevels import market_close
    ny = ZoneInfo("America/New_York")
    at = lambda day, h, m=0, s=0: datetime(2025, 3, day, h, m, s, tzinfo=ny)      # noqa: E731  (lunes 3 ... domingo 9)
    jueves = market_close(at(6, 16, 59, 50), at(6, 17, 0, 10), 17 * 60)
    assert jueves["weekly"] is False and jueves["markets"] == ("Futuros de índices USA",) and jueves["when"] == at(6, 17)
    viernes = market_close(at(7, 16, 59, 50), at(7, 17, 0, 10), 17 * 60)
    assert viernes["weekly"] is True and viernes["markets"] == ("Futuros de índices USA", "Forex")
    assert market_close(at(6, 17, 0, 10), at(6, 17, 0, 30), 17 * 60) is None          # ya anotado en la comprobación anterior
    assert market_close(at(6, 10), at(6, 10, 0, 20), 17 * 60) is None                 # no es la hora
    assert market_close(at(8, 16, 59, 50), at(8, 17, 0, 10), 17 * 60) is None         # sábado: sin cierres
    assert market_close(at(9, 16, 59, 50), at(9, 17, 0, 10), 17 * 60) is None         # domingo


def test_el_registro_anota_el_cierre_de_mercados(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from zoneinfo import ZoneInfo
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "1h", "watchlist": ["EURUSD"]}}
    win = MainWindow(EventBus(), SkillManager(EventBus(), Services(None, None, cfg, EnvConfig()), [{"type": "levels"}]), cfg, "t")
    when = datetime(2025, 3, 7, 17, 0, tzinfo=ZoneInfo("America/New_York"))
    win._on_market_closed({"when": when, "weekly": True, "markets": ("Futuros de índices USA", "Forex"),
                           "index_reopen": 18 * 60, "reopen": 17 * 60})
    text = win.log_view.toPlainText()
    assert "cierre semanal a las 17:00 NY" in text and "Forex" in text
    win._on_market_closed({"when": when.replace(day=6), "weekly": False, "markets": ("Futuros de índices USA",),
                           "index_reopen": 18 * 60, "reopen": 17 * 60})
    assert "cierre de los futuros de índices USA a las 17:00 NY" in win.log_view.toPlainText()


def test_cambio_de_dia_de_trading_a_la_hora_de_cada_activo():
    from zoneinfo import ZoneInfo
    from tradingbot.skills.levels.daylevels import new_trading_day
    ny = ZoneInfo("America/New_York")
    at = lambda day, h, m=0, s=0: datetime(2025, 3, day, h, m, s, tzinfo=ny)      # noqa: E731  (lunes 3 ... domingo 9)
    forex = new_trading_day(at(3, 16, 59, 50), at(3, 17, 0, 10), 17 * 60)
    assert forex["day"] == "MARTES" and forex["when"] == at(3, 17)                    # el día lleva el nombre del que termina
    assert new_trading_day(at(3, 16, 59, 50), at(3, 17, 0, 10), 18 * 60) is None      # los índices aún no han cambiado
    indices = new_trading_day(at(3, 17, 59, 50), at(3, 18, 0, 10), 18 * 60)
    assert indices["day"] == "MARTES" and indices["when"] == at(3, 18)
    assert new_trading_day(at(9, 16, 59, 50), at(9, 17, 0, 10), 17 * 60)["day"] == "LUNES"   # domingo por la tarde
    assert new_trading_day(at(7, 16, 59, 50), at(7, 17, 0, 10), 17 * 60) is None     # viernes: el mercado cierra
    assert new_trading_day(at(8, 16, 59, 50), at(8, 17, 0, 10), 17 * 60) is None     # sábado
    assert new_trading_day(at(3, 17, 0, 10), at(3, 17, 0, 30), 17 * 60) is None      # ya anotado


def test_el_registro_anota_el_cambio_de_dia_de_cada_grupo_de_activos(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from zoneinfo import ZoneInfo
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "1h", "watchlist": ["EURUSD", "NAS100.r", "XAUUSD"]}}
    win = MainWindow(EventBus(), SkillManager(EventBus(), Services(None, None, cfg, EnvConfig()), [{"type": "levels"}]), cfg, "t")
    ny = ZoneInfo("America/New_York")
    base = {"day": "MARTES", "us_indices": ("NAS100", "SP500")}
    win._on_market_day({**base, "when": datetime(2025, 3, 3, 17, 0, tzinfo=ny), "index": False, "start": 17 * 60})
    win._on_market_day({**base, "when": datetime(2025, 3, 3, 18, 0, tzinfo=ny), "index": True, "start": 18 * 60})
    text = win.log_view.toPlainText()
    assert "nuevo día de trading (MARTES) a las 17:00 NY - Forex, metales y resto" in text
    assert "nuevo día de trading (MARTES) a las 18:00 NY - índices USA" in text


def test_el_boton_de_ajustes_de_la_sma_abre_su_ventana_y_aplica_los_cambios(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import envconfig, settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui import main_window
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    env_file = tmp_path / "tradingbot.env"
    env_file.write_text("LEVELS_SMA_PERIOD=30\n", encoding="utf-8")
    monkeypatch.setattr(envconfig, "ENV_FILE", env_file)
    opened = []

    class FakeDialog:
        DialogCode = main_window.SmaDialog.DialogCode

        def __init__(self, parent, period, color, style):
            opened.append((period, color, style))

        def exec(self):
            return self.DialogCode.Accepted

        def values(self):
            return 12, "#112233", "discontinuo"

    monkeypatch.setattr(main_window, "SmaDialog", FakeDialog)
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "1h", "watchlist": ["EURUSD"]}}
    bus, published = EventBus(), []
    bus.subscribe("t", "levels.sma", published.append)
    win = main_window.MainWindow(bus, SkillManager(bus, Services(None, None, cfg, EnvConfig(parse(""))), [{"type": "levels"}]), cfg, "t")
    assert win.sma_cfg_btn.text() == "⚙" and win.sma_cfg_btn.isVisibleTo(win)
    win.sma_cfg_btn.click()                                           # el botón de ajustes
    assert opened == [(30, "#00ACC1", "normal")]
    assert published[-1].payload == {"period": 12, "color": "#112233", "style": "discontinuo"}
    win.sma_btn.customContextMenuRequested.emit(win.sma_btn.rect().center())   # y el clic derecho
    assert opened[-1] == (12, "#112233", "discontinuo") and len(opened) == 2
