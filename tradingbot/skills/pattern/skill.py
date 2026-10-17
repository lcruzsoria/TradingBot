"""Skill Pattern: identifica los patrones de entrada dentro de la TBR activa (los valida después la skill Setup)."""
from __future__ import annotations

from ...core import Event, Skill, register_skill
from ...timeframes import minutes
from . import patterns as _patterns   # noqa: F401  (registra los patrones definidos)
from .patterns import PATTERN_REGISTRY, PatternContext, active_tbr

DEFAULT_WINDOW_HOURS = 24.0


@register_skill("pattern")
class PatternSkill(Skill):
    title = "Pattern"
    description = ("Se conecta a la skill TBR: la TBR activa es la última que ha cerrado, con su High, Low y 50 %. Busca en "
                   "ella los patrones de entrada definidos y avisa de cada uno que identifica. La validación con el sesgo "
                   "(GO / NO GO) la hace la skill Setup. Solo informa: no envía órdenes.")
    subscribes = ("candles.loaded", "tbr.updated")
    publishes = ("pattern.updated", "pattern.detected")
    slot = "aux1"

    def on_start(self) -> None:
        self.error = "Configuración PATTERN no válida"
        self._candles: dict | None = None
        self._tbr: dict | None = None
        self._seen: set = set()                        # patrones ya avisados: no se repiten
        self._active_key: tuple | None = None
        try:
            self._load_settings()
        except ValueError as exc:
            self.error = str(exc)
            raise
        self.error = ""
        self.set_caption("esperando TBR")

    def _load_settings(self) -> None:
        # tradingbot.env, bloque PATTERN
        self.window_hours = self.settings.get_float("WINDOW_HOURS", DEFAULT_WINDOW_HOURS)
        if self.window_hours <= 0:
            raise ValueError(f"PATTERN_WINDOW_HOURS={self.window_hours:g} debe ser mayor que 0.")
        self.zones = [z.upper() for z in self.settings.get_list("ZONES", [])] or None      # vacío: todas las TBR
        wanted = [t.lower() for t in self.settings.get_list("TYPES", [])]
        unknown = [t for t in wanted if t not in PATTERN_REGISTRY]
        if unknown:
            raise ValueError(f"PATTERN_TYPES={', '.join(wanted)}: patrón desconocido {', '.join(unknown)}. "
                             f"Disponibles: {', '.join(PATTERN_REGISTRY) or 'ninguno todavía'}.")
        self.types = wanted or list(PATTERN_REGISTRY)                                     # vacío: todos los definidos

    # -- mensajes -----------------------------------------------------------------------------------
    def handle(self, event: Event) -> None:
        if self.error:
            raise ValueError(self.error)
        if event.topic == "candles.loaded":
            self._candles = event.payload
        else:
            self._tbr = event.payload
        self.update()

    def update(self) -> None:
        c, t = self._candles, self._tbr
        if c is None or t is None or (c["symbol"], c["timeframe"]) != (t["symbol"], t["timeframe"]):
            return                                      # aún no han llegado las zonas de estas velas
        symbol, tf = c["symbol"], c["timeframe"]
        tbr = active_tbr(t["sessions"], self.zones) if t["available"] else None
        if tbr is None:
            self.set_caption("sin TBR" if not t["available"] else "sin TBR cerrada")
            self.publish("pattern.updated", {"symbol": symbol, "timeframe": tf, "tbr": None, "hits": []})
            return
        df = c["df"]
        ctx = PatternContext(symbol, tf, minutes(tf), df["ts"].to_numpy(), df["open"].to_numpy(), df["high"].to_numpy(),
                             df["low"].to_numpy(), df["close"].to_numpy(), tbr,
                             max(1, int(self.window_hours * 60 / minutes(tf))))
        hits, errors = [], []
        for key in self.types:
            pattern = PATTERN_REGISTRY[key]()
            try:
                hits += pattern.detect(ctx)
            except Exception as exc:                    # un patrón con error no debe tumbar a los demás
                errors.append(f"{pattern.title or key}: {exc}")
        self.publish("pattern.updated", {"symbol": symbol, "timeframe": tf, "tbr": tbr, "hits": hits, "errors": errors})
        if errors:
            self.set_caption("error en un patrón")
        elif not self.types:
            self.set_caption("sin patrones definidos")
        elif hits:
            self.set_caption(f"{len(hits)} patrón(es) en {tbr.zone}")
        else:
            self.set_caption(f"TBR {tbr.zone}: sin patrones")
        for hit in hits:
            key = (symbol, tf, hit.key, hit.direction, tbr.key, tbr.day, hit.x)
            if key in self._seen:
                continue
            self._seen.add(key)
            self.publish("pattern.detected", {"symbol": symbol, "timeframe": tf, "tbr": tbr, "hit": hit})
