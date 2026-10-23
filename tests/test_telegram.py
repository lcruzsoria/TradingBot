"""Skill Telegram: avisos al móvil de las operaciones de Setup (sin conectar con Telegram: el envío se intercepta)."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import time
from datetime import date
from types import SimpleNamespace

import pandas as pd
import pytest

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.cortex.order import Order
from tradingbot.skills.setup.positions import Closed

ORDER = Order("EURUSD", "15m", "short", "Continuación", "continuacion", "NY Open", date(2026, 10, 23), 1.1, 1.09, 1.095, 1.09500,
              1.09600, 1.09300, "Bearish", -3.0, "Short a favor del sesgo", None, 1000, 1000 + 24 * 3600)
REPLAY = Order(*[*ORDER.__dict__.values()][:-2], 400, 400 + 24 * 3600)                   # una del repaso al arrancar
TP = Closed("objetivo", 1.093, 1900, 2.0, 0.18, None, 2.4, -0.3)


@pytest.fixture
def sent(monkeypatch):
    from tradingbot.skills.telegram import client
    out = []
    monkeypatch.setattr(client, "send_message", lambda token, chat, text: out.append((token, chat, text)))
    monkeypatch.setenv("TELEGRAM_TOKEN", "t0k3n")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    return out


def run_skill(env_text, app=None):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus = EventBus()
    manager = SkillManager(bus, Services(None, None, {"app": dict(app or {})}, EnvConfig(parse(env_text))), [{"type": "telegram"}])
    manager.start()
    time.sleep(0.2)
    return manager, bus


def settle(manager, bus, *events):
    for topic, payload, source in events:
        bus.publish(topic, payload, source=source)
    time.sleep(0.4)
    manager.stop()
    return manager.skills["telegram"]


def candles(symbol="EURUSD", last=1000):
    return "candles.loaded", {"symbol": symbol, "timeframe": "15m", "df": pd.DataFrame({"ts": [last - 900, last]})}, "feed"


def test_apagada_por_defecto_no_manda_nada(sent):
    manager, bus = run_skill("")
    skill = settle(manager, bus, candles(), ("setup.executed", {"order": ORDER}, "setup"))
    assert sent == [] and skill.caption == "apagado" and skill.state.value == "ok"


def test_avisa_de_lo_que_abre_y_cierra_setup_en_directo_y_no_del_repaso(sent):
    manager, bus = run_skill("TELEGRAM_ENABLED=true\n", {"profile_name": "puprime"})
    skill = settle(manager, bus, candles(),
                   ("setup.executed", {"order": REPLAY}, "setup"),                     # anterior al arranque: no se avisa
                   ("setup.closed", {"order": REPLAY, "closed": TP}, "setup"),
                   ("setup.executed", {"order": ORDER}, "setup"),
                   ("setup.closed", {"order": ORDER, "closed": TP}, "setup"))
    texts = [t for _, _, t in sent]
    assert all(token == "t0k3n" and chat == "42" for token, chat, _ in sent)
    assert len(texts) == 3 and "en marcha" in texts[0]                                # aviso de arranque, abre y cierra
    assert "Abre Corto EURUSD" in texts[1] and "Continuación · NY Open 23/10" in texts[1] and "Stop 1.09600" in texts[1]
    assert "TP +2.00 R · Corto EURUSD" in texts[2] and "máx. +2.40 R" in texts[2] and "perfil puprime" in texts[2]
    assert skill.caption == "3 aviso(s)"


def test_el_cierre_de_una_abierta_antes_de_reiniciar_si_se_avisa(sent):
    from tradingbot.skills.setup import store
    store.save([REPLAY])                                                               # Setup la recupera del disco al arrancar
    manager, bus = run_skill("TELEGRAM_ENABLED=true\nTELEGRAM_NOTIFY_START=false\n")
    settle(manager, bus, candles(), ("setup.closed", {"order": REPLAY, "closed": TP}, "setup"))
    assert len(sent) == 1 and "TP +2.00 R" in sent[0][2]


def test_go_y_nogo_solo_si_se_piden(sent):
    hit = SimpleNamespace(direction="long", title="Reversión", ts=1000)
    go = {"symbol": "EURUSD", "timeframe": "15m", "tbr": SimpleNamespace(zone="London"), "hit": hit,
          "decision": SimpleNamespace(allowed=True, reason="Long a favor del sesgo")}
    nogo = dict(go, decision=SimpleNamespace(allowed=False, reason="Long contra el sesgo Bearish"))
    manager, bus = run_skill("TELEGRAM_ENABLED=true\nTELEGRAM_NOTIFY_START=false\n")
    settle(manager, bus, candles(), ("cortex.decision", go, "cortex"), ("cortex.decision", nogo, "cortex"))
    assert sent == []                                                                  # por defecto, solo abre y cierra
    manager, bus = run_skill("TELEGRAM_ENABLED=true\nTELEGRAM_NOTIFY_START=false\nTELEGRAM_NOTIFY=go, nogo\n")
    settle(manager, bus, candles(), ("cortex.decision", go, "cortex"), ("cortex.decision", nogo, "cortex"))
    assert [t.split("\n")[0] for _, _, t in sent] == ["<b>✓ GO Largo EURUSD</b> 15m", "<b>✕ NO GO Largo EURUSD</b> 15m"]


def test_sin_token_o_con_un_aviso_desconocido_la_skill_avisa_del_error(monkeypatch, tmp_path):
    monkeypatch.delenv("TELEGRAM_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    manager, bus = run_skill("TELEGRAM_ENABLED=true\n", {"env_file": str(tmp_path / "no-existe.env")})
    skill = settle(manager, bus)
    assert skill.state.value == "error" and "TELEGRAM_TOKEN" in skill.note
    monkeypatch.setenv("TELEGRAM_TOKEN", "t")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "1")
    manager, bus = run_skill("TELEGRAM_ENABLED=true\nTELEGRAM_NOTIFY=abre, todo\n")
    skill = settle(manager, bus)
    assert skill.state.value == "error" and "todo" in skill.note


def test_el_token_se_lee_del_fichero_de_cuentas(monkeypatch, tmp_path):
    from tradingbot.skills.telegram import client
    monkeypatch.delenv("TELEGRAM_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    env = tmp_path / ".env"
    env.write_text("MT5_DEFAULT=demo\nTELEGRAM_TOKEN=abc:123\nTELEGRAM_CHAT_ID=777\n", encoding="utf-8")
    assert client.credentials(env) == ("abc:123", "777")
    assert client.credentials(tmp_path / "otro.env") == (None, None)
