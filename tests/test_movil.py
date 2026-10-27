"""Skill Móvil: avisos por Telegram (sin conectar con Telegram: el envío se intercepta) y panel web de solo lectura."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import time
from dataclasses import replace
from datetime import date
from types import SimpleNamespace

import pandas as pd
import pytest

from tradingbot.envconfig import EnvConfig, parse
from tradingbot.skills.cortex.order import Order
from tradingbot.skills.setup.positions import Closed

ORDER = Order("EURUSD", "15m", "short", "Continuación", "continuacion", "NY Open", date(2026, 10, 23), 1.1, 1.09, 1.095, 1.09500,
              1.09600, 1.09300, "Bearish", -3.0, "Short a favor del sesgo", None, 1000, 1000 + 24 * 3600)
REPLAY = replace(ORDER, entry_ts=400, close_ts=400 + 24 * 3600)                   # una del repaso al arrancar
TP = Closed("objetivo", 1.093, 1900, 2.0, 0.18, None, 2.4, -0.3)


PHOTOS: list = []                                                                      # las imágenes que se «mandan»
INBOX: list = []                                                                       # lo que «llega» al bot por Telegram


def fake_updates(token, offset=None):
    if offset == -1:
        return INBOX[-1:]
    return [u for u in INBOX if offset is None or u["update_id"] >= offset]


@pytest.fixture
def sent(monkeypatch):
    from tradingbot.skills.movil import telegram as client
    out = []
    INBOX.clear()
    monkeypatch.setattr(client, "send_message", lambda token, chat, text: out.append((token, chat, text)))
    monkeypatch.setattr(client, "get_updates", fake_updates)
    PHOTOS.clear()
    monkeypatch.setattr(client, "send_photo", lambda token, chat, png, caption="": PHOTOS.append((chat, png, caption)))
    monkeypatch.setattr(client, "set_commands", lambda token, commands: None)
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
    assert texts[1].startswith("<b>Estrategia:</b> Continuación\n")                  # la estrategia, por delante de todo
    assert "Abre Corto EURUSD" in texts[1] and "NY Open 23/10" in texts[1] and "Stop 1.09600" in texts[1]
    assert texts[2].startswith("<b>Estrategia:</b> Continuación\n")
    assert "TP +2.00 R · Corto EURUSD" in texts[2] and "máx. +2.40 R" in texts[2] and "perfil puprime" in texts[2]
    assert skill.caption == "3 aviso(s)"


def test_el_cierre_de_una_abierta_antes_de_reiniciar_si_se_avisa(sent):
    from tradingbot.skills.setup import store
    store.save([REPLAY])                                                               # Setup la recupera del disco al arrancar
    manager, bus = run_skill("TELEGRAM_ENABLED=true\nTELEGRAM_NOTIFY_START=false\n")
    settle(manager, bus, candles(), ("setup.closed", {"order": REPLAY, "closed": TP}, "setup"))
    assert len(sent) == 1 and "TP +2.00 R" in sent[0][2]


def test_el_aviso_de_calendario_lleva_su_estrategia_y_no_zona_tbr():
    from tradingbot.skills.cortex.order import build_calendar_order
    from tradingbot.skills.movil import messages
    signal = {"symbol": "NAS100ft.s", "timeframe": "15m", "direction": "long", "price": 29171.5, "stop": 29025.64,
              "target": 29463.22, "day": date(2026, 10, 26), "entry_ts": 1000, "close_ts": 2000, "close_at": "10:00 NY"}
    bias = SimpleNamespace(bias=SimpleNamespace(value="No Bias"), score=4.0)
    text = messages.opened(build_calendar_order(signal, bias, "Calendario"), "puprime")
    assert text.split("\n") == ["<b>Estrategia:</b> Calendario (largo a hora fija)", "🟡 <b>Abre Largo NAS100ft.s</b> 15m",
                                "Entrada 29,171.50 · Stop 29,025.64 · Obj. 29,463.22", "Sesgo No Bias +4", "<i>perfil puprime</i>"]


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
    assert [t.split("\n")[:2] for _, _, t in sent] == [["<b>Estrategia:</b> Reversión", "<b>✓ GO Largo EURUSD</b> 15m"],
                                                       ["<b>Estrategia:</b> Reversión", "<b>✕ NO GO Largo EURUSD</b> 15m"]]


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


def message(update_id, text, chat=42):
    return {"update_id": update_id, "message": {"chat": {"id": chat}, "text": text}}


def test_los_comandos_de_telegram_contestan_con_lo_del_panel_solo_a_tu_chat(sent, monkeypatch, tmp_path):
    from tradingbot.skills.setup import store
    store.save([ORDER], tmp_path / "perfil" / "abiertas.json")
    INBOX.append(message(1, "/estado"))                                                # con el bot parado: no se contesta
    manager, bus = run_skill("TELEGRAM_ENABLED=true\nTELEGRAM_NOTIFY_START=false\n", {"data_dir": str(tmp_path / "perfil"),
                                                                                       "profile_name": "puprime"})
    skill = manager.skills["movil"]
    bus.publish("quotes.updated", {"quotes": {"EURUSD": SimpleNamespace(bid=1.0945)}, "account": None}, source="quotes")
    bus.publish("bias.updated", {"symbol": "EURUSD", "timeframe": "15m", "result": SimpleNamespace(
        bias=SimpleNamespace(value="Bearish"), score=-3.0, lateral=False)}, source="bias")
    time.sleep(0.3)
    INBOX.extend([message(2, "/estado"), message(3, "/abiertas@mi_bot"), message(4, "/hoy", chat=999),   # otro chat: se ignora
                  message(5, "hola"), message(6, "/ayuda"), message(7, "/loquesea")])
    skill.tick()
    manager.stop()
    texts = [t for _, chat, t in sent]
    assert all(chat == "42" for _, chat, _ in sent) and len(texts) == 4                  # estado, abiertas, ayuda y un comando desconocido (da la ayuda)
    assert "TradingBot · puprime" in texts[0] and "Corto EURUSD" in texts[0] and "+0.50 R" in texts[0] and "Bearish" in texts[0]
    assert texts[1].startswith("<b>Abiertas</b>") and "Entrada 1.09500" in texts[1] and "precio 1.09450" in texts[1]
    assert texts[2].startswith("<b>Comandos</b>") and "/estado" in texts[2] and texts[3] == texts[2]
    assert skill._offset == 8
    skill.tick()                                                                         # lo ya contestado no se repite
    assert len(sent) == 4


def test_sin_comandos_no_se_pregunta_a_telegram(sent, monkeypatch):
    from tradingbot.skills.movil import telegram as client
    monkeypatch.setattr(client, "get_updates", lambda *a: pytest.fail("no debería preguntar"))
    manager, bus = run_skill("TELEGRAM_ENABLED=true\nTELEGRAM_NOTIFY_START=false\nTELEGRAM_COMMANDS=false\n")
    manager.skills["movil"].tick()
    manager.stop()
    assert sent == []


def test_panel_manda_la_imagen_del_panel_con_los_datos(sent, tmp_path):
    from PySide6.QtWidgets import QApplication
    from tradingbot.skills.setup import store
    QApplication.instance() or QApplication([])
    store.save([ORDER], tmp_path / "perfil" / "abiertas.json")
    manager, bus = run_skill("TELEGRAM_ENABLED=true\nTELEGRAM_NOTIFY_START=false\n", {"data_dir": str(tmp_path / "perfil"),
                                                                                       "profile_name": "puprime"})
    skill = manager.skills["movil"]
    INBOX.append(message(1, "/panel"))
    skill.tick()
    manager.stop()
    [(chat, png, caption)] = PHOTOS
    assert chat == "42" and png[:4] == b"\x89PNG" and len(png) > 5000 and "puprime" in caption and sent == []


def test_captura_pide_la_ventana_a_la_interfaz_y_manda_lo_que_devuelve(sent):
    pedidas = []
    manager, bus = run_skill("TELEGRAM_ENABLED=true\nTELEGRAM_NOTIFY_START=false\n")
    bus.subscribe("ui", "movil.capture.request", pedidas.append)
    skill = manager.skills["movil"]
    INBOX.append(message(1, "/captura"))
    skill.tick()
    assert len(pedidas) == 1 and PHOTOS == []                                          # espera a que la ventana conteste
    bus.publish("movil.capture", {"request_id": "tg", "png": b"\x89PNG-ventana"}, source="ui")
    time.sleep(0.4)
    bus.publish("movil.capture", {"request_id": "otra", "png": b"\x89PNG-no-pedida"}, source="ui")      # sin pedirla: se ignora
    time.sleep(0.3)
    manager.stop()
    assert [p[1] for p in PHOTOS] == [b"\x89PNG-ventana"]


def test_captura_sin_respuesta_de_la_ventana_avisa(sent, monkeypatch):
    from tradingbot.skills.movil import skill as movil
    monkeypatch.setattr(movil, "CAPTURE_TIMEOUT", 0.0)
    manager, bus = run_skill("TELEGRAM_ENABLED=true\nTELEGRAM_NOTIFY_START=false\n")
    skill = manager.skills["movil"]
    INBOX.append(message(1, "/captura"))
    skill.tick()
    time.sleep(0.05)
    skill.tick()
    manager.stop()
    assert PHOTOS == [] and "no ha contestado" in sent[-1][2]


def test_la_ventana_contesta_a_la_peticion_de_captura(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from tradingbot import settings
    from tradingbot.core import EventBus, Services, SkillManager
    from tradingbot.ui.main_window import MainWindow
    import tradingbot.skills  # noqa: F401
    QApplication.instance() or QApplication([])
    monkeypatch.setattr(settings, "SETTINGS_FILE", tmp_path / "s.json")
    cfg = {"app": {"symbol": "EURUSD", "timeframe": "15m", "watchlist": ["EURUSD"]}}
    win = MainWindow(EventBus(), SkillManager(EventBus(), Services(None, None, cfg, EnvConfig()), []), cfg, "t")
    got = []
    win.bus.subscribe("t", "movil.capture", got.append)
    win._on_capture_request({"request_id": "tg"})
    assert got[0].payload["request_id"] == "tg" and got[0].payload["png"][:4] == b"\x89PNG" and len(got[0].payload["png"]) > 5000


def test_la_subida_de_la_imagen_es_un_multipart_valido():
    from tradingbot.skills.movil import telegram as client
    body, kind = client.multipart({"chat_id": "42", "caption": "hola"}, "photo", "x.png", b"\x89PNG-datos", "image/png")
    boundary = kind.split("boundary=")[1]
    end = ("--" + boundary + "--" + chr(13) + chr(10)).encode()
    crlf = chr(13) + chr(10)
    assert kind.startswith("multipart/form-data") and body.endswith(end)
    assert ("name=\"chat_id\"" + crlf + crlf + "42" + crlf).encode() in body
    assert b"filename=\"x.png\"" in body and b"\x89PNG-datos" in body
