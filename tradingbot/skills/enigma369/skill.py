"""Skill Enigma369: cuartos de la Quarterly Theory traducidos a números 1-9; solo identificación visual (no opera)."""
from __future__ import annotations

import re

from ...core import Event, Skill, register_skill
from ...clock import server_minus_ny
from ...timeframes import display_label, minutes
from ..levels.daylevels import DEFAULT_US_INDICES, is_us_index
from . import cuartos

STRATEGY = "enigma369"
MAX_TF_MINUTES = 360
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


@register_skill("enigma369")
class Enigma369Skill(Skill):
    title = "Enigma369"
    description = ("Traduce los cuartos de la Quarterly Theory (semana, día, sesión, 90 min y micro de 22,5 min, en hora de Nueva York) "
                   "a un número del 1 al 9 por zona y pinta en el gráfico las alineaciones de 3, 6 y 9. Solo índices USA; "
                   "solo identificación visual, no opera.")
    subscribes = ("candles.loaded", "clock.offset", "enigma369.mode")
    publishes = ("enigma369.updated",)
    slot = "aux2"

    def on_start(self) -> None:
        self.error = "Configuración Enigma369 no válida"
        self.offset: int | None = None
        self._last: dict | None = None
        app = (self.services.app_cfg or {}).get("app", {})
        self.active = str(app.get("strategy") or "") == STRATEGY
        try:
            self._load_settings()
        except ValueError as exc:
            self.error = str(exc)
            raise
        self.error = ""
        self.set_caption("esperando velas" if self.active else f"solo en el perfil {STRATEGY}")

    def _load_settings(self) -> None:
        s = self.settings                                                    # tradingbot.env, bloque ENIGMA369
        self.anchor = s.get_int("ANCHOR_HOUR", cuartos.DEFAULT_ANCHOR_HOUR)
        if not 0 <= self.anchor <= 23:
            raise ValueError(f"ENIGMA369_ANCHOR_HOUR={self.anchor} debe estar entre 0 y 23 (hora de Nueva York)")
        self.mode = (s.get("MODE", "semana") or "semana").lower()
        if self.mode not in cuartos.MODES:
            raise ValueError(f"ENIGMA369_MODE={self.mode}: usa {' o '.join(cuartos.MODES)}")
        self.colors = dict(cuartos.DEFAULT_COLORS)
        for digit in cuartos.DEFAULT_COLORS:
            value = s.get(f"COLOR_{digit}")
            if value:
                if not HEX.match(value):
                    raise ValueError(f"ENIGMA369_COLOR_{digit}={value} debe ser #RRGGBB")
                self.colors[digit] = value
        opacity = s.get_float("STRIPE_OPACITY", 100.0)
        if not 0 <= opacity <= 100:
            raise ValueError(f"ENIGMA369_STRIPE_OPACITY={opacity:g} debe estar entre 0 y 100 (%)")
        self.stripe_opacity = opacity / 100
        self.symbols = s.get_list("SYMBOLS", [])
        env = self.services.env
        self.indices = env.get_list("LEVELS_US_INDICES", list(DEFAULT_US_INDICES)) if env is not None else list(DEFAULT_US_INDICES)

    def handle(self, event: Event) -> None:
        if self.error:
            raise ValueError(self.error)
        if event.topic == "clock.offset":
            if event.payload.get("server_offset") == self.offset:
                return
            self.offset = event.payload.get("server_offset")
        elif event.topic == "enigma369.mode":
            mode = event.payload.get("mode")
            if mode not in cuartos.MODES or mode == self.mode:
                return
            self.mode = mode
        elif event.payload.get("background"):                # barrido de la watchlist: no se pinta
            return
        else:
            self._last = event.payload
        if self.active and self._last is not None:
            self.update(self._last)

    def update(self, p: dict) -> None:
        symbol, tf = p["symbol"], p["timeframe"]
        base = {"symbol": symbol, "timeframe": tf, "mode": self.mode, "anchor": self.anchor, "stripe_opacity": self.stripe_opacity, "wanted_tf": cuartos.MODE_TIMEFRAMES[self.mode]}
        if not is_us_index(symbol, self.symbols or self.indices):
            self.set_caption(f"{symbol}: solo índices USA")
            self.publish("enigma369.updated", {**base, "available": False, "reason": "Enigma369 solo funciona con índices USA"})
            return
        if minutes(tf) > MAX_TF_MINUTES or p.get("df") is None or not len(p["df"]):
            self.set_caption(f"no en {display_label(tf)}")
            self.publish("enigma369.updated", {**base, "available": False, "reason": f"Enigma369 se lee con velas de M1 a H{MAX_TF_MINUTES // 60}"})
            return
        ahead, estimated = server_minus_ny(self.offset)
        ts = p["df"]["ts"].to_numpy()
        result = cuartos.compute(ts, ahead, self.mode, self.anchor, self.colors)
        now = cuartos.last_zones(ts, ahead, self.mode, self.anchor)
        runs = cuartos.alignments(now)
        head = " ".join(z["text"] for z in now)
        self.set_caption(f"{runs[-1]['label']}" if runs else head)
        self.publish("enigma369.updated", {**base, "available": True, "estimated": estimated, "now": now, "alignments_now": runs,
                                               "ref_alignments_now": [] if any(z["number"] for z in now) else cuartos.alignments(now, "ref_number"), **result})
