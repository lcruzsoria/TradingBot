"""Skill Móvil: avisos por Telegram (sin conectar con Telegram: el envío se intercepta) y panel web de solo lectura."""
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
    from tradingbot.skills.movil import telegram as client
    out = []
    monkeypatch.setattr(client, "send_message", lambda token, chat, text: out.append((token, chat, text)))
    monkeypatch.setenv("TELEGRAM_TOKEN", "t0k3n")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    return out


def run_skill(env_text, app=None):
    from tradingbot.core import EventBus, Services, SkillManager
    import tradingbot.skills  # noqa: F401
    bus = EventBus()
    manager = SkillManager(bus, Services(None, None, {"app": dict(app or {})}, EnvConfig(parse(env_text))), [{"type": "movil"}])
    manager.start()
    time.sleep(0.2)
    return manager, bus


def settle(manager, bus, *events):
    for topic, payload, source in events:
        bus.publish(topic, payload, source=source)
    time.sleep(0.4)
    manager.stop()
    return manager.skills["movil"]


def candles(symbol="EURUSD", last=1000):
    return "candles.loaded", {"symbol": symbol, "timeframe": "15m", "df": pd.DataFrame({"ts": [last - 900, last]})}, "feed"


def test_apagada_por_defecto_no_manda_nada(sent):
    manager, bus = run_skill("")
    skill = settle(manager, bus, candles(), ("setup.executed", {"order": ORDER}, "setup"))
    assert sent == [] and skill.caption == "apagado" and skill.state.value == "ok" and skill.server is None


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
    from tradingbot.skills.movil import telegram as client
    monkeypatch.delenv("TELEGRAM_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    env = tmp_path / ".env"
    env.write_text("MT5_DEFAULT=demo\nTELEGRAM_TOKEN=abc:123\nTELEGRAM_CHAT_ID=777\n", encoding="utf-8")
    assert client.credentials(env) == ("abc:123", "777")
    assert client.credentials(tmp_path / "otro.env") == (None, None)


def get(port, path, token=None):
    import json
    import urllib.error
    import urllib.request
    request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", headers={"X-Panel-Token": token} if token else {})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if path.startswith("/api") else body
    except urllib.error.HTTPError as exc:
        return exc.code, None


def test_el_panel_sirve_la_pagina_y_el_estado_con_su_clave(monkeypatch, tmp_path):
    import json
    from tradingbot.skills.setup import store
    monkeypatch.setenv("PANEL_TOKEN", "clave-larga")
    data = tmp_path / "perfil"
    store.save([ORDER], data / "abiertas.json")
    (data / "forwardtest").mkdir(parents=True)
    from tradingbot.skills.movil import panel
    month = panel.journal.month_of(panel.datetime.now(panel.NY))
    today = panel.datetime.now(panel.NY).date().isoformat()
    close = {"t": "close", "order": {**store.order_to_json(ORDER), "tbr_day": today}, "closed": TP.__dict__}
    (data / "forwardtest" / f"{month}.jsonl").write_text(json.dumps(close) + "\nbasura\n", encoding="utf-8")
    manager, bus = run_skill("PANEL_ENABLED=true\nPANEL_PORT=0\n", {"data_dir": str(data), "profile_name": "puprime"})
    skill = manager.skills["movil"]
    port = skill.server.port
    bus.publish("quotes.updated", {"quotes": {"EURUSD": SimpleNamespace(bid=1.0945)}, "account": None}, source="quotes")
    bus.publish(*candles()[:2], source="feed")
    hit = SimpleNamespace(direction="long", title="Reversión", ts=1000)
    bus.publish("cortex.decision", {"symbol": "EURUSD", "timeframe": "15m", "tbr": SimpleNamespace(zone="London"), "hit": hit,
                                    "decision": SimpleNamespace(allowed=False, reason="contra el sesgo")}, source="cortex")
    time.sleep(0.4)
    try:
        code, page = get(port, "/")
        assert code == 200 and "<title>TradingBot</title>" in page                    # la página no lleva datos: sin clave
        assert get(port, "/api/estado")[0] == 401 and get(port, "/api/estado", "otra")[0] == 401
        code, state = get(port, "/api/estado", "clave-larga")
        assert code == 200 and state["profile"] == "puprime" and skill.caption == "panel :%d" % port
        [o] = state["open"]
        assert (o["symbol"], o["side"], o["entry"], o["price"], o["r_now"]) == ("EURUSD", "Corto", 1.095, 1.0945, 0.5)
        [c] = state["closed"]
        assert (c["result"], c["r"], c["max_r"]) == ("TP", 2.0, 2.4) and state["today"]["TP"] == 1 and state["today"]["r"] == 2.0
        assert [(d["go"], d["side"], d["reason"]) for d in state["decisions"]] == [(False, "Largo", "contra el sesgo")]
    finally:
        manager.stop()
    assert skill.server is None


def test_el_panel_no_se_abre_a_otros_equipos_sin_clave(monkeypatch, tmp_path):
    monkeypatch.delenv("PANEL_TOKEN", raising=False)
    manager, bus = run_skill("PANEL_ENABLED=true\nPANEL_HOST=0.0.0.0\nPANEL_PORT=0\n", {"env_file": str(tmp_path / "x.env")})
    skill = settle(manager, bus)
    assert skill.state.value == "error" and "PANEL_TOKEN" in skill.note and skill.server is None
