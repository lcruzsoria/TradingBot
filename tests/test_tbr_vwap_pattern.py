"""Patrón «TBR con VWAP» (perfil de estrategia tbrvwap): detección con el VWAP del día y cableado del perfil."""
from datetime import date

import numpy as np
import pytest

from tradingbot.config import STRATEGY_PATTERNS, strategy_skills
from tradingbot.skills.pattern.patterns import DETECTED, PATTERN_REGISTRY, ActiveTbr, PatternContext
from tradingbot.skills.pattern.tbr_vwap import KEY, TbrVwap

AHEAD = 7 * 3600
DAY = date(2024, 3, 5)
T0 = int(np.datetime64("2024-03-05T10:00:00").astype("datetime64[s]").astype(np.int64)) + AHEAD     # 10:00 NY, en hora de servidor
TBR = ActiveTbr("NY_AM", "NY Open", DAY, 110.0, 100.0, 0, 1)

# (open, high, low, close): 8 velas de la propia TBR alrededor de 104, y después el escenario largo (venía de arriba, retest del VWAP)
BASE = [(104.0, 104.5, 103.5, 104.0)] * 8
LONG = [(107.0, 108.0, 106.5, 107.5), (107.5, 108.0, 106.0, 107.0), (107.0, 107.2, 103.5, 105.0), (105.2, 106.0, 104.8, 105.5)]


def ctx_for(rows, volume=True, first_bar=8):
    o, h, l, c = (np.array(x, dtype=float) for x in zip(*rows))
    ts = T0 + np.arange(len(rows)) * 900
    return PatternContext("NAS100", "15m", 15, ts, o, h, l, c, TBR, first_bar, len(rows) - 1, False, "", "", AHEAD, 0,
                          day_end=18 * 60, volume=np.full(len(rows), 1000.0) if volume else None)


def test_detecta_el_retest_largo_y_entra_al_cierre_de_la_vela():
    pattern = TbrVwap()
    hits = pattern.detect(ctx_for(BASE + LONG))
    assert len(hits) == 1
    h = hits[0]
    assert (h.key, h.title, h.status, h.direction, h.x, h.price) == (KEY, "TBR con VWAP", DETECTED, "long", 10, 105.0)
    assert h.ts == T0 + 11 * 900                                    # la posición vive desde la vela siguiente al retest
    assert h.levels["target"] == 110.0 and h.levels["stop"] < 105.0 < h.levels["target"]
    figs = pattern.figures(ctx_for(BASE + LONG))
    assert [(f.kind, f.direction, f.levels["entrada"]) for f in figs] == [("pos", "long", 105.0)]


def test_sin_volumen_no_hay_vwap_ni_senal():
    assert TbrVwap().detect(ctx_for(BASE + LONG, volume=False)) == []


def test_sin_retest_no_hay_senal():
    assert TbrVwap().detect(ctx_for(BASE + LONG[:2])) == []


def test_el_perfil_de_estrategia_solo_busca_su_patron():
    assert KEY in PATTERN_REGISTRY and not PATTERN_REGISTRY[KEY].default_on
    assert STRATEGY_PATTERNS["tbrvwap"] == (KEY,)
    skills = [{"type": "pattern"}, {"type": "tbr"}, {"type": "calendario"}, {"type": "setup"}]
    assert [s["type"] for s in strategy_skills(skills, "tbrvwap")] == ["pattern", "tbr", "setup"]


def test_ajustes_no_validos():
    class S:
        def __init__(self, **kw): self.kw = kw
        def get(self, key, default=None): return self.kw.get(key, default)
    assert TbrVwap(S(TBR_VWAP_STOP_FRAC="0.5")).params.stop_frac == 0.5
    with pytest.raises(ValueError):
        TbrVwap(S(TBR_VWAP_STOP_FRAC="0"))
    with pytest.raises(ValueError):
        TbrVwap(S(TBR_VWAP_MIN_RR="x"))
