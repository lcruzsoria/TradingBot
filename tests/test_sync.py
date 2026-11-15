"""Puesta al día del forwardtest de los perfiles con el bot cerrado (tradingbot/sync.py)."""
import os
import time
from datetime import date
from pathlib import Path

from tradingbot import sync
from tradingbot.envconfig import EnvConfig, parse


def test_un_perfil_sin_pid_o_con_pid_muerto_no_cuenta_como_abierto(tmp_path):
    (tmp_path / "puprime").mkdir()
    (tmp_path / "crt").mkdir()
    (tmp_path / "crt" / "bot.pid").write_text(str(os.getpid()), encoding="utf-8")          # este proceso vive
    (tmp_path / "puprime" / "bot.pid").write_text("999999", encoding="utf-8")              # un pid que no existe
    assert sync.running_profiles(["crt", "puprime", "metaquotes"], tmp_path) == {"crt"}
    assert not (tmp_path / "puprime" / "bot.pid").exists()                                  # y se limpia el rastro del bot que se cerró mal


def test_register_bot_escribe_el_pid(tmp_path):
    sync.register_bot("CRT", tmp_path)
    assert sync.pid_file("crt", tmp_path).read_text(encoding="utf-8") == str(os.getpid())


def test_solo_una_sincronizacion_a_la_vez(tmp_path):
    lock = sync.acquire_lock(tmp_path)
    assert lock is not None
    assert sync.acquire_lock(tmp_path) is None                                              # el proceso que la tiene sigue vivo
    lock.write_text(f"999999 {time.time()}", encoding="utf-8")                              # pero si el dueño murió, se puede tomar
    assert sync.acquire_lock(tmp_path) is not None
    lock.write_text(f"{os.getpid()} {time.time() - 3 * 3600}", encoding="utf-8")            # o si lleva demasiado tiempo
    assert sync.acquire_lock(tmp_path) is not None


def test_como_se_pone_al_dia_cada_estrategia():
    assert sync.how("crt") == "crt" and sync.how("enigma369") == "nada"
    assert [sync.how(s) for s in ("", "calendario", "barrido_nyam", "tbrvwap")] == ["skills"] * 4


def test_dias_de_velas_hasta_el_inicio_del_forwardtest():
    env = EnvConfig(parse("STATS_FORWARD_START=2026-10-19\nFEED_SWEEP_DAYS=10\n"))
    assert sync.sweep_days(env, date(2026, 11, 15)) == 30                                   # 27 días + 3 de margen
    assert sync.sweep_days(env, date(2026, 10, 21)) == 10                                   # nunca menos que FEED_SWEEP_DAYS
    assert sync.sweep_days(env, date(2027, 6, 1)) == sync.SWEEP_DAYS_MAX                    # con tope
    assert sync.sweep_days(EnvConfig(parse("FEED_SWEEP_DAYS=7\n")), date(2026, 11, 15)) == 7


def test_resumen_del_perfil(tmp_path):
    (tmp_path / "forwardtest").mkdir()
    (tmp_path / "forwardtest" / "2026-11.jsonl").write_text('{"t": "open"}\n{"t": "close"}\n', encoding="utf-8")
    (tmp_path / "cuenta.json").write_text('{"capital_inicial": 100, "operaciones": [{"saldo": 101.5}]}', encoding="utf-8")
    assert sync.diary_count(tmp_path) == 2 and sync.account_summary(tmp_path) == "1 operaciones, saldo 101.5"
    assert sync.account_summary(tmp_path / "otro") == "sin cuenta" and sync.diary_count(tmp_path / "otro") == 0
