"""Skill Pattern: identifica los patrones de entrada dentro de la TBR activa (Cortex los valida después con el sesgo)."""
from __future__ import annotations

import numpy as np

from ...clock import server_minus_ny
from ...core import Event, Skill, register_skill
from ...envconfig import EnvConfig
from ...timeframes import display_label, minutes
from ..feed.datasource import aggregate_candles
from ..tbr.zones import zones_from_settings
from .patterns import DETECTED, PATTERN_REGISTRY, PatternContext, recent_tbrs, window_for

DEFAULT_ZONE_ORDER = ("ASIA", "LONDON", "NY_AM", "NY_PM")
RECENT_SECONDS = 24 * 3600                      # solo se evalúan las TBR que cerraron en el último día


def candles_for(chart: dict, tf: str):
    """Velas con las que trabaja un patrón en el timeframe `tf`: las del gráfico si coincide, o agrupadas de otras más finas."""
    df, have = chart["df"], chart["timeframe"]
    if have == tf:
        return df
    if minutes(have) < minutes(tf) and minutes(tf) % minutes(have) == 0:
        return aggregate_candles(df, minutes(tf) * 60)
    return None


@register_skill("pattern")
class PatternSkill(Skill):
    title = "Pattern"
    description = ("Se conecta a la skill TBR: la TBR activa es la última que ha cerrado, con su High, Low y 50 %. Busca en "
                   "ella los patrones de entrada definidos, hasta que empieza la TBR siguiente, y avisa de cada uno que "
                   "identifica (y de los que se invalidan, anulan o vencen). Cortex valida cada patrón con el sesgo "
                   "(GO / NO GO). Solo informa: no envía órdenes.")
    subscribes = ("candles.loaded", "tbr.updated", "clock.offset")
    publishes = ("pattern.updated", "pattern.detected", "pattern.discarded", "pattern.session")
    slot = 4

    def on_start(self) -> None:
        self.error = "Configuración PATTERN no válida"
        self._candles: dict | None = None
        self._tbr: dict | None = None
        self._offset: int | None = None
        self._seen: set = set()                        # resultados ya avisados: no se repiten
        try:
            self._load_settings()
        except ValueError as exc:
            self.error = str(exc)
            raise
        self.error = ""
        self.set_caption("esperando TBR")

    def _load_settings(self) -> None:
        # tradingbot.env, bloque PATTERN
        self.zones = [z.upper() for z in self.settings.get_list("ZONES", [])] or None      # vacío: todas las TBR
        order = [z.upper() for z in self.settings.get_list("ZONE_ORDER", list(DEFAULT_ZONE_ORDER))]
        env = self.services.env if self.services.env is not None else EnvConfig()
        self.order = zones_from_settings(env.section("TBR"), order) if order else []        # ciclo de TBR: define el plazo
        wanted = [t.lower() for t in self.settings.get_list("TYPES", [])]
        unknown = [t for t in wanted if t not in PATTERN_REGISTRY]
        if unknown:
            raise ValueError(f"PATTERN_TYPES={', '.join(wanted)}: patrón desconocido {', '.join(unknown)}. "
                             f"Disponibles: {', '.join(PATTERN_REGISTRY) or 'ninguno todavía'}.")
        self.types = wanted or list(PATTERN_REGISTRY)                                     # vacío: todos los definidos
        self.patterns = {key: PATTERN_REGISTRY[key](self.settings) for key in self.types}   # valida sus ajustes propios

    # -- mensajes -----------------------------------------------------------------------------------
    def handle(self, event: Event) -> None:
        if self.error:
            raise ValueError(self.error)
        if event.topic == "candles.loaded":
            self._candles = event.payload
        elif event.topic == "tbr.updated":
            self._tbr = event.payload
        else:
            if event.payload.get("server_offset") == self._offset:
                return
            self._offset = event.payload.get("server_offset")
        self.update()

    def update(self) -> None:
        c, t = self._candles, self._tbr
        if c is None or t is None or (c["symbol"], c["timeframe"]) != (t["symbol"], t["timeframe"]):
            return                                      # aún no han llegado las zonas de estas velas
        symbol, tf = c["symbol"], c["timeframe"]
        recents = recent_tbrs(t["sessions"], self.zones) if t["available"] else []
        if not recents:
            self.set_caption("sin TBR" if not t["available"] else "sin TBR cerrada")
            self.publish("pattern.updated", {"symbol": symbol, "timeframe": tf, "tbr": None, "hits": []})
            return
        ahead, _ = server_minus_ny(self._offset)
        chart_ts = c["df"]["ts"].to_numpy()
        tbr = recents[-1]                               # la TBR activa: la última que ha cerrado
        results, figures, errors, unavailable, tfs = [], [], [], [], {}
        windows = {}
        for item in recents:
            window = window_for(item, self.order, ahead)
            windows[item.key] = window
            if window is not None and int(chart_ts[-1]) - window.close_ts > RECENT_SECONDS:
                continue                                # una TBR de hace más de un día no se evalúa: ya es pasado
            self._evaluate_tbr(c, item, window, ahead, results, figures, errors, unavailable, tfs)
        hits = [h for _t, h in results]
        window = windows[tbr.key]
        self.publish("pattern.updated", {"symbol": symbol, "timeframe": tf, "tbr": tbr, "hits": hits, "errors": errors,
                                         "unavailable": sorted(set(unavailable)), "tfs": tfs, "figures": figures})
        found = [h for h in hits if h.status == DETECTED]
        ended = window is not None and window.session_end_ts is not None and int(chart_ts[-1]) >= window.session_end_ts
        if errors:
            self.set_caption("error en un patrón")
        elif unavailable and not hits and not figures:
            self.set_caption(f"necesita {display_label(next(iter(tfs.values())))}")
        elif not self.types:
            self.set_caption("sin patrones definidos")
        elif ended:
            self.set_caption("fin de jornada")
        elif found:
            self.set_caption(f"{len(found)} patrón(es) en {next(i.zone for i, h in results if h is found[-1])}")
        elif figures:
            self.set_caption(f"{len(figures)} fibo(s) en curso")
        else:
            self.set_caption(f"TBR {tbr.zone}: buscando")
        for item, hit in results:
            key = (symbol, hit.key, hit.status, hit.direction, item.key, item.day, hit.ts or hit.x)
            if key in self._seen:
                continue
            self._seen.add(key)
            payload = {"symbol": symbol, "timeframe": tfs.get(hit.key, tf), "tbr": item, "hit": hit}
            self.publish("pattern.detected" if hit.status == DETECTED else "pattern.discarded", payload)
        if ended:
            key = (symbol, "session", tbr.key, tbr.day)
            if key not in self._seen:
                self._seen.add(key)
                self.publish("pattern.session", {"symbol": symbol, "timeframe": tf, "tbr": tbr,
                                                 "session_end": window.session_end_hours})

    def _evaluate_tbr(self, c, tbr, window, ahead, results, figures, errors, unavailable, tfs) -> None:
        """Ejecuta los patrones sobre una TBR y recoge sus resultados y dibujos."""
        tf = c["timeframe"]
        chart_ts = c["df"]["ts"].to_numpy()
        if window is not None:
            close_ts = window.close_ts
        else:                                           # zona fuera del ciclo: el cierre sale de las velas del gráfico
            i = tbr.first_bar
            close_ts = int(chart_ts[i]) if i < len(chart_ts) else int(chart_ts[-1]) + minutes(tf) * 60
        for key, pattern in self.patterns.items():
            ptf = pattern.timeframe() or tf
            tfs[key] = ptf
            df = candles_for(c, ptf)
            if df is None:
                unavailable.append(f"{pattern.title} necesita velas {display_label(ptf)} y el gráfico está en "
                                   f"{display_label(tf)} (cámbialo a {display_label(ptf)} o a uno menor que lo divida)")
                continue
            df = df.iloc[:-1]                           # la última vela sigue formándose: solo se usan las cerradas
            if len(df) < 2:
                continue
            ts = df["ts"].to_numpy()
            tf_sec = minutes(ptf) * 60
            first = int(np.searchsorted(ts, close_ts, "left"))
            start = int(np.searchsorted(ts, window.start_ts, "left")) if window is not None else max(0, first - 8)
            end = len(ts) - 1
            if window is not None and window.end_ts is not None:
                end = min(end, int(np.searchsorted(ts, window.end_ts, "left")) - 1)
            closed = window is not None and window.end_ts is not None and int(ts[-1]) + tf_sec >= window.end_ts
            ctx = PatternContext(c["symbol"], ptf, minutes(ptf), ts, df["open"].to_numpy(), df["high"].to_numpy(),
                                 df["low"].to_numpy(), df["close"].to_numpy(), tbr, first, end, closed,
                                 window.next_zone if window else "", window.next_hours if window else "", ahead, start)
            try:
                results += [(tbr, h) for h in pattern.detect(ctx)]
                figures += pattern.figures(ctx)
            except Exception as exc:                    # un patrón con error no debe tumbar a los demás
                errors.append(f"{pattern.title or key}: {exc}")
