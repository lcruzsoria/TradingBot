import os
import time
from datetime import datetime, timezone

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

import tradingbot.skills  # noqa: F401
from tradingbot.clock import NY, OffsetDetector, format_offset, ny_from_server
from tradingbot.core import EventBus, Services, SkillManager
from tradingbot.datasource import Quote


def server_epoch(y, mo, d, h, mi, s=0):
    """Marca de tiempo de MT5: la hora del servidor tratada como si fuera UTC."""
    return int(datetime(y, mo, d, h, mi, s, tzinfo=timezone.utc).timestamp())


def test_conversion_a_nueva_york_respeta_el_horario_de_verano_de_ee_uu():
    assert NY is not None
    summer, est = ny_from_server(server_epoch(2026, 10, 7, 21, 30), 3 * 3600)      # servidor UTC+3, NY en EDT
    assert (summer.strftime("%H:%M"), summer.tzname(), est) == ("14:30", "EDT", False)
    winter, _ = ny_from_server(server_epoch(2026, 12, 7, 21, 30), 2 * 3600)        # servidor UTC+2, NY en EST
    assert (winter.strftime("%H:%M"), winter.tzname()) == ("14:30", "EST")


def test_sin_desfase_conocido_se_estima_servidor_igual_a_ny_mas_7h():
    ny, estimated = ny_from_server(server_epoch(2026, 10, 7, 21, 30), None)
    assert ny.strftime("%H:%M") == "14:30" and estimated is True


def test_formato_del_desfase():
    assert [format_offset(s) for s in (10800, 7200, 0, -18000, 19800)] == ["UTC+3", "UTC+2", "UTC+0", "UTC-5", "UTC+5:30"]


def feed(det, offset, seconds=6, latency=1.0, start=1_800_000_000.0):
    for i in range(seconds):
        wall = start + i
        det.observe(int(wall - latency) + offset, wall)
    return det.offset


def test_detecta_el_desfase_con_ticks_en_vivo():
    assert feed(OffsetDetector(), 3 * 3600) == 10800
    assert feed(OffsetDetector(), 2 * 3600, latency=2.0) == 7200
    assert feed(OffsetDetector(), -5 * 3600) == -18000


def test_no_se_fia_de_mercados_cerrados_ni_de_saltos():
    det = OffsetDetector()
    for i in range(8):
        det.observe(1_800_000_000 + 10800 - 7200, 1_800_000_000 + i)       # mismo tick de siempre: mercado cerrado
    assert det.offset is None
    det = OffsetDetector()
    for i in range(8):
        det.observe(1_800_000_000 + 10800 - 7200 + i * 3600, 1_800_000_000 + i)   # salto de horas entre muestras
    assert det.offset is None


def test_no_se_fia_si_el_reloj_del_pc_esta_desincronizado():
    det = OffsetDetector()
    for i in range(8):
        wall = 1_800_000_000 + i
        det.observe(int(wall) + 10800 + 300, wall)                          # PC 5 minutos atrasado
    assert det.offset is None


def test_se_adapta_si_el_servidor_cambia_de_horario():
    det = OffsetDetector()
    feed(det, 3 * 3600)
    assert det.offset == 10800
    feed(det, 2 * 3600, start=1_800_000_100.0)
    assert det.offset == 7200


class LiveSource:
    """Fuente simulada: un tick nuevo en cada llamada (como un mercado activo), con el servidor a +3 h."""
    def __init__(self):
        self.n = 0
        self.t0 = int(time.time())

    def quotes(self, symbols):
        self.n += 1
        return {s: Quote(s, 1.0, 1.0001, self.t0 + self.n + 3 * 3600) for s in symbols}

    def account(self):
        return None


def run_quotes(app_cfg, wait=0.8, env=None):
    bus, events = EventBus(), []
    bus.subscribe("t", "quotes.updated", events.append)
    manager = SkillManager(bus, Services(LiveSource(), None, app_cfg, env), [{"type": "quotes", "slot": 5, "interval": 0.05}])
    manager.start()
    bus.publish("feed.connected", {}, source="ui")
    time.sleep(wait)
    manager.stop()
    return events


def test_la_skill_quotes_detecta_y_publica_el_desfase():
    events = run_quotes({"app": {"watchlist": ["EURUSD"]}})
    assert events[0].payload["server_offset"] is None                       # al principio aún no lo sabe
    last = events[-1].payload
    assert last["server_offset"] == 10800 and last["offset_source"] == "detectado"


def test_el_desfase_configurado_manda_sobre_la_deteccion():
    from tradingbot.envconfig import EnvConfig
    env = EnvConfig({"QUOTES_SERVER_UTC_OFFSET": "2"})               # en tradingbot.env
    last = run_quotes({"app": {"watchlist": ["EURUSD"]}}, wait=0.3, env=env)[-1].payload
    assert last["server_offset"] == 7200 and last["offset_source"] == "configurado"


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])


def test_la_caja_ultimo_tick_muestra_nueva_york(qapp, tmp_path, monkeypatch):
    from tradingbot import settings
    from tradingbot.ui.main_window import MainWindow
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": ["EURUSD"]}}
    bus = EventBus()
    win = MainWindow(bus, SkillManager(bus, Services(None, None, cfg), []), cfg, "t")
    ts = server_epoch(2026, 10, 7, 21, 30, 5)
    win._show_last_tick(ts, 3 * 3600, "detectado")
    assert win.stat_tick.value.text() == "14:30:05" and win.stat_tick.sub.text() == "Nueva York (EDT)"
    assert "21:30:05" in win.stat_tick.toolTip() and "UTC+3" in win.stat_tick.toolTip()
    win._show_last_tick(ts, None, None)
    assert win.stat_tick.value.text() == "14:30:05" and win.stat_tick.sub.text() == "Nueva York (estimada)"
