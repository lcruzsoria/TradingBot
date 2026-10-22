"""Skill Pattern: identifica los patrones de entrada dentro de la TBR activa (Cortex los valida después con el sesgo)."""
from __future__ import annotations

from datetime import date

import numpy as np

from ...clock import server_minus_ny
from ...core import Event, Skill, background_of, register_skill
from ...envconfig import EnvConfig
from ...timeframes import display_label, minutes
from ..feed.datasource import aggregate_candles
from ..levels.daylevels import DEFAULT_DAY_START, DEFAULT_INDEX_DAY_START, DEFAULT_US_INDICES, is_us_index, parse_time
from ..tbr.zones import zones_from_settings
from .patterns import DETECTED, PATTERN_REGISTRY, PatternContext, PeerTbr, history_tbrs, recent_tbrs, window_for
from .trade import day_close

DEFAULT_ZONE_ORDER = ("ASIA", "LONDON", "NY_AM", "NY_PM")
DEFAULT_UNTIL = ("ASIA:LONDON:FIN", "LONDON:NY_AM:FIN", "NY_AM@18:00")   # Asia hasta el final de London, London hasta el final de NY Open, NY Open hasta las 18:00
DEFAULT_EXTEND = ()                     # TBR cuyo plazo llega hasta el final de la última zona del ciclo
DEFAULT_HISTORY_DAYS = 30                      # días de TBR pasadas de las que se dibujan fibos y entradas
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
    publishes = ("pattern.updated", "pattern.detected", "pattern.discarded", "pattern.session", "pattern.swept")
    slot = 4

    def on_start(self) -> None:
        self.error = "Configuración PATTERN no válida"
        self._candles: dict | None = None
        self._tbr: dict | None = None
        self._offset: int | None = None
        self._seen: set = set()                        # resultados ya avisados: no se repiten
        self._bg: dict[str, dict] = {}                 # barrido de la watchlist: velas y TBR de cada mercado, hasta juntarse
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
        self.history_days = self.settings.get_int("HISTORY_DAYS", DEFAULT_HISTORY_DAYS)
        if self.history_days < 1:
            raise ValueError(f"PATTERN_HISTORY_DAYS={self.history_days} debe ser 1 o más.")
        self.since = forward_start(self.services.env)       # STATS_FORWARD_START: desde ahí se avisa de todas las TBR
        order = [z.upper() for z in self.settings.get_list("ZONE_ORDER", list(DEFAULT_ZONE_ORDER))]
        self.extend = [z.upper() for z in self.settings.get_list("EXTEND", list(DEFAULT_EXTEND))]
        unknown_zone = [z for z in self.extend if z not in order]
        if self.settings.get("EXTEND") is None:
            self.extend = [z for z in self.extend if z in order]                # el valor por defecto no da error
            unknown_zone = []
        if unknown_zone:
            raise ValueError(f"PATTERN_EXTEND={', '.join(self.extend)}: {', '.join(unknown_zone)} no está en PATTERN_ZONE_ORDER.")
        self.until = self._load_until(order)
        env = self.services.env if self.services.env is not None else EnvConfig()
        self.order = zones_from_settings(env.section("TBR"), order) if order else []        # ciclo de TBR: define el plazo
        levels = env.section("LEVELS")                  # el día de trading acaba cuando empieza el siguiente: ahí cierran los trades
        self.day_end = parse_time(levels.get("DAY_START", DEFAULT_DAY_START), "LEVELS_DAY_START")
        self.index_day_end = parse_time(levels.get("INDEX_DAY_START", DEFAULT_INDEX_DAY_START), "LEVELS_INDEX_DAY_START")
        self.us_indices = levels.get_list("US_INDICES", list(DEFAULT_US_INDICES))
        setup = env.section("SETUP")                    # el breakeven del dibujo es el mismo que aplica Setup a la posición simulada
        risk_pct, be_pct = setup.get_float("RISK_PCT", 1.0), setup.get_float("BE_TRIGGER_PCT", 1.0)
        self.be_r = be_pct / risk_pct if risk_pct > 0 and be_pct > 0 else None
        wanted = [t.lower() for t in self.settings.get_list("TYPES", [])]
        unknown = [t for t in wanted if t not in PATTERN_REGISTRY]
        if unknown:
            raise ValueError(f"PATTERN_TYPES={', '.join(wanted)}: patrón desconocido {', '.join(unknown)}. "
                             f"Disponibles: {', '.join(PATTERN_REGISTRY) or 'ninguno todavía'}.")
        self.types = wanted or list(PATTERN_REGISTRY)                                     # vacío: todos los definidos
        self.patterns = {key: PATTERN_REGISTRY[key](self.settings) for key in self.types}   # valida sus ajustes propios

    def _load_until(self, order: list[str]) -> dict[str, str]:
        """PATTERN_UNTIL=ASIA:NY_AM, LONDON:NY_AM:FIN: el plazo de cada zona llega hasta el inicio (o el final, con :FIN) de la zona indicada."""
        raw = self.settings.get("UNTIL")
        items = self.settings.get_list("UNTIL", list(DEFAULT_UNTIL))
        until = {}
        for item in items:
            if "@" in item:                                     # ZONA@HH:MM: hasta una hora fija de NY
                zone, _at, hour = (x.strip().upper() for x in item.partition("@"))
                try:
                    h, m = (int(x) for x in hour.split(":"))
                    assert 0 <= h < 24 and 0 <= m < 60
                except (ValueError, AssertionError):
                    raise ValueError(f"PATTERN_UNTIL={', '.join(items)}: la hora de {item} debe ser HH:MM.") from None
                if zone not in order:
                    if raw is None:
                        continue
                    raise ValueError(f"PATTERN_UNTIL={', '.join(items)}: {zone} no está en PATTERN_ZONE_ORDER.")
                until[zone] = f"@{h:02d}:{m:02d}"
                continue
            parts = [x.strip().upper() for x in item.split(":")]
            zone, target = parts[0], (parts[1] if len(parts) > 1 else "")
            if len(parts) not in (2, 3) or not zone or not target or (len(parts) == 3 and parts[2] != "FIN"):
                raise ValueError(f"PATTERN_UNTIL={', '.join(items)}: usa ZONA:ZONA o ZONA:ZONA:FIN (por ejemplo ASIA:NY_AM).")
            if zone not in order or target not in order:
                if raw is None:
                    continue                                    # el valor por defecto no da error
                raise ValueError(f"PATTERN_UNTIL={', '.join(items)}: {zone if zone not in order else target} no está en "
                                 f"PATTERN_ZONE_ORDER.")
            until[zone] = ":".join(parts[1:])
        return until

    # -- mensajes -----------------------------------------------------------------------------------
    def handle(self, event: Event) -> None:
        if self.error:
            raise ValueError(self.error)
        if event.payload.get("background") and event.topic != "clock.offset":
            self._background(event)
            return
        if event.topic == "candles.loaded":
            self._candles = event.payload
        elif event.topic == "tbr.updated":
            self._tbr = event.payload
        else:
            if event.payload.get("server_offset") == self._offset:
                return
            self._offset = event.payload.get("server_offset")
        self.update()

    def _background(self, event: Event) -> None:
        """Un mercado del barrido de la watchlist: cuando están sus velas y sus TBR de la misma vuelta, se evalúa como el del
        gráfico (sus avisos llegan a Cortex) y se avisa con `pattern.swept` de que ese mercado ya está repasado."""
        p = event.payload
        slot = self._bg.setdefault(p["symbol"], {})
        slot["candles" if event.topic == "candles.loaded" else "tbr"] = p
        c, t = slot.get("candles"), slot.get("tbr")
        if c is None or t is None or c.get("sweep") != t.get("sweep") or c["timeframe"] != t["timeframe"]:
            return
        del self._bg[p["symbol"]]
        try:
            self.update(c, t)
        finally:
            self.publish("pattern.swept", {"symbol": c["symbol"], "timeframe": c["timeframe"], **background_of(c)})

    def update(self, c: dict | None = None, t: dict | None = None) -> None:
        background = c is not None
        if not background:
            c, t = self._candles, self._tbr
        if c is None or t is None or (c["symbol"], c["timeframe"]) != (t["symbol"], t["timeframe"]):
            return                                      # aún no han llegado las zonas de estas velas
        symbol, tf = c["symbol"], c["timeframe"]
        mark = background_of(c)
        caption = self.set_caption if not background else (lambda _text: None)   # el hexágono habla del gráfico
        recents = recent_tbrs(t["sessions"], self.zones) if t["available"] else []
        if not recents:
            caption("sin TBR" if not t["available"] else "sin TBR cerrada")
            self.publish("pattern.updated", {"symbol": symbol, "timeframe": tf, "tbr": None, "hits": [], **mark})
            return
        ahead, _ = server_minus_ny(self._offset)
        chart_ts = c["df"]["ts"].to_numpy()
        tbr = recents[-1]                               # la TBR activa: la última que ha cerrado
        results, figures, errors, unavailable, tfs = [], [], [], [], {}
        windows = {}
        peers = self._peers(t["sessions"], ahead)
        for item in recents:
            window = window_for(item, self.order, ahead, self.extend, self.until)
            windows[item.key] = window
            if window is not None and int(chart_ts[-1]) - window.close_ts > RECENT_SECONDS:
                continue                                # una TBR de hace más de un día no se evalúa: ya es pasado
            self._evaluate_tbr(c, item, window, ahead, results, figures, errors, unavailable, tfs, peers)
        # TBR pasadas. Las de los últimos PATTERN_HISTORY_DAYS días se dibujan (fibos y entradas, solo en el gráfico); las
        # del inicio del forwardtest (STATS_FORWARD_START) en adelante además se avisan, para que Cortex las decida y el
        # forwardtest recoja todas las operaciones de todos los mercados, también lo que pasó con el bot cerrado.
        skip = {(r.key, r.day) for r in recents}
        past = history_tbrs(t["sessions"], self.zones, skip, 100_000)
        drawn_from = max((r.day for r in recents), default=None)
        drawn_from = drawn_from.toordinal() - self.history_days + 1 if drawn_from else 0
        for item in past:
            live = self.since is not None and item.day >= self.since
            drawn = not background and self.history_days > 1 and item.day.toordinal() >= drawn_from
            if not (live or drawn):
                continue
            window = window_for(item, self.order, ahead, self.extend, self.until)
            if window is None or window.end_ts is None:
                continue
            if live:
                self._evaluate_tbr(c, item, window, ahead, results, figures if drawn else [], errors, unavailable, tfs, peers)
            else:
                self._evaluate_tbr(c, item, window, ahead, [], figures, [], [], {}, peers)
        results.sort(key=lambda r: r[1].ts or 0)           # en orden de hora: así los decide Cortex
        hits = [h for _t, h in results]
        window = windows[tbr.key]
        self.publish("pattern.updated", {"symbol": symbol, "timeframe": tf, "tbr": tbr, "hits": hits, "errors": errors,
                                         "unavailable": sorted(set(unavailable)), "tfs": tfs, "figures": figures, **mark})
        found = [h for h in hits if h.status == DETECTED]
        ended = window is not None and window.session_end_ts is not None and int(chart_ts[-1]) >= window.session_end_ts
        if errors:
            caption("error en un patrón")
        elif unavailable and not hits and not figures:
            caption(f"necesita {display_label(next(iter(tfs.values())))}")
        elif not self.types:
            caption("sin patrones definidos")
        elif ended:
            caption("fin de jornada")
        elif found:
            caption(f"{len(found)} patrón(es) en {next(i.zone for i, h in results if h is found[-1])}")
        elif figures:
            caption(f"{len(figures)} fibo(s) en curso")
        else:
            caption(f"TBR {tbr.zone}: buscando")
        for item, hit in results:
            key = (symbol, hit.key, hit.status, hit.direction, item.key, item.day, hit.ts or hit.x)
            if key in self._seen:
                continue
            self._seen.add(key)
            payload = {"symbol": symbol, "timeframe": tfs.get(hit.key, tf), "tbr": item, "hit": hit,
                       "session_close": self._session_close(symbol, hit.ts, ahead), **mark}
            self.publish("pattern.detected" if hit.status == DETECTED else "pattern.discarded", payload)
        if ended:
            key = (symbol, "session", tbr.key, tbr.day)
            if key not in self._seen:
                self._seen.add(key)
                self.publish("pattern.session", {"symbol": symbol, "timeframe": tf, "tbr": tbr,
                                                 "session_end": window.session_end_hours, **mark})

    def _peers(self, sessions, ahead: int) -> tuple[PeerTbr, ...]:
        """Todas las TBR cerradas (de cualquier zona, aunque PATTERN_ZONES no las busque) con sus horas, para los patrones que cruzan varias."""
        peers = []
        for item in history_tbrs(sessions, None, set(), 100_000):
            window = window_for(item, self.order, ahead, self.extend, self.until)
            if window is not None:
                peers.append(PeerTbr(item.key, item.zone, item.day, item.high, item.low, window.start_ts, window.close_ts))
        return tuple(peers)

    def _day_end(self, symbol: str) -> int:
        """Fin del día de trading (minutos de NY): 17:00 en forex y metales, 18:00 en los índices USA."""
        return self.index_day_end if is_us_index(symbol, self.us_indices) else self.day_end

    def _session_close(self, symbol: str, ts: int | None, ahead: int) -> int | None:
        """Fin del día de trading siguiente a la hora `ts` (servidor): ahí se cierra el trade."""
        return day_close(ts, ahead, self._day_end(symbol)) if ts else None

    def _evaluate_tbr(self, c, tbr, window, ahead, results, figures, errors, unavailable, tfs, peers=()) -> None:
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
                                 window.next_zone if window else "", window.next_hours if window else "", ahead, start,
                                 window.limit_verb if window else "empezara", self._day_end(c["symbol"]), self.be_r, peers)
            try:
                results += [(tbr, h) for h in pattern.detect(ctx)]
                figures += pattern.figures(ctx)
            except Exception as exc:                    # un patrón con error no debe tumbar a los demás
                errors.append(f"{pattern.title or key}: {exc}")


def forward_start(env) -> date | None:
    """Día (de NY) de STATS_FORWARD_START, o None si no hay o no es una fecha (la skill Stats ya avisa de ese error)."""
    raw = env.section("STATS").get("FORWARD_START", "") if env is not None else ""
    try:
        return date.fromisoformat(raw) if raw else None
    except ValueError:
        return None
