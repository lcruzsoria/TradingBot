"""Protección global: ninguna prueba puede modificar los ficheros de configuración reales del proyecto."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PROTECTED = [ROOT / "tradingbot.env", ROOT / "config.toml"]


@pytest.fixture(scope="session", autouse=True)
def config_files_untouched():
    before = {p: p.read_bytes() for p in PROTECTED if p.exists()}
    yield
    changed = [p.name for p, data in before.items() if p.read_bytes() != data]
    for p in PROTECTED:
        if p in before:
            p.write_bytes(before[p])          # se restauran igualmente
    assert not changed, f"Una prueba modificó ficheros reales del proyecto: {changed}"


@pytest.fixture(autouse=True)
def forwardtest_journal_in_tmp(tmp_path, monkeypatch):
    """El diario del forwardtest de las pruebas va a una carpeta temporal, nunca a data/forwardtest."""
    from tradingbot.skills.stats import journal
    monkeypatch.setattr(journal, "DEFAULT_DIR", tmp_path / "forwardtest")
