"""Skill Barrido RTH: busca el setup del barrido del RTH en NY Open (solo perfil Barrido_NYAM, índices USA).

Skill independiente: no hereda ni importa código de Pattern. Con las TBR de la skill TBR (RTH, Asia y London) y las velas del gráfico
busca, en cada día con el RTH ya cerrado, la rotura y la entrada de `deteccion.py`, y publica lo mismo que publica Pattern
(`pattern.updated`, `pattern.detected`, `pattern.discarded`, `pattern.swept`) para que Cortex, Setup, Stats y la ventana la traten igual.
Los tipos de esos mensajes viven en `skills/_comun/contratos.py`. No espera a que NY Open termine: el RTH cerrado basta, así que
la señal llega en cuanto cierra la vela de entrada.
"""
from __future__ import annotations

from datetime import date

import numpy as np

from ...clock import server_minus_ny
from ...core import Event, Skill, background_of, register_skill
from ...timeframes import display_label, minutes
from .._comun.contratos import DETECTED, ActiveTbr
from ..feed.datasource import aggregate_candles
from .deteccion import KEY, Ajustes, Contexto, Zona, analizar, cierre_del_dia

DEFAULT_HISTORY_DAYS = 30        # días pasados de los que se dibujan las entradas
RECENT_SECONDS = 24 * 3600       # un RTH cerrado en el último día siempre se evalúa y se avisa
MAX_GAP = 36 * 3600              # una Asia o London más antigua que esto no es la del día
ZONAS = ("PRE_NY", "ASIA", "LONDON")
DEFAULT_INDEX_DAY_START = "18:00"


def _hhmm(text: str, key: str) -> int:
    try:
        h, m = (int(x) for x in str(text).strip().split(":"))
        assert 0 <= h < 24 and 0 <= m < 60
    except (ValueError, AssertionError):
        raise ValueError(f"{key}={text!r}: usa el formato HH:MM (por ejemplo 18:00).") from None
    return h * 60 + m


def _velas(chart: dict, tf: str):
    """Velas del timeframe `tf`: las del gráfico si coincide, o agrupadas de otras más finas; None si no se puede."""
    df, have = chart["df"], chart["timeframe"]
    if have == tf:
        return df
    if minutes(have) < minutes(tf) and minutes(tf) % minutes(have) == 0:
        return aggregate_candles(df, minutes(tf) * 60)
    return None


def _forward_start(env) -> date | None:
    """Día (de NY) de STATS_FORWARD_START, o None si no hay o no es una fecha: desde ahí se avisa de todos los días."""
    raw = env.section("STATS").get("FORWARD_START", "") if env is not None else ""
    try:
        return date.fromisoformat(raw) if raw else None
    except ValueError:
        return None


@register_skill("barrido_rth")
class BarridoRthSkill(Skill):
    title = "Barrido RTH"
    description = ("Setup del perfil Barrido_NYAM: tras el RTH (09:00-10:00), la primera rotura de su High o su Low (una vela que cierra fuera) "
                   "entre las 10:00 y las 11:00 y la primera vela M5 posterior que cierra de nuevo dentro del rango (antes de las 12:00) da la "
                   "entrada. Stop en el swing, objetivo 1 en el lado contrario del RTH y objetivo 2 en lo más cercano entre Asia/London y el "
                   "50 % del NDOG/NWOG. Cortex lo valida; solo informa, no envía órdenes.")
    subscribes = ("candles.loaded", "tbr.updated", "clock.offset")
    publishes = ("pattern.updated", "pattern.detected", "pattern.discarded", "pattern.swept")
    slot = 4                      # hexágono grande 4 del anillo, el que ocupa Pattern en los demás perfiles

    def on_start(self) -> None:
        self.error = "Configuración BARRIDO_RTH no válida"
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
        # tradingbot.env, bloque BARRIDO_RTH
        self.ajustes = Ajustes.desde(self.settings)
        self.history_days = self.settings.get_int("HISTORY_DAYS", DEFAULT_HISTORY_DAYS)
        if self.history_days < 1:
            raise ValueError(f"BARRIDO_RTH_HISTORY_DAYS={self.history_days} debe ser 1 o más.")
        env = self.services.env
        self.since = _forward_start(env)
        levels = env.section("LEVELS") if env is not None else None          # el día de trading de los índices USA acaba cuando empieza el siguiente
        self.day_end = _hhmm(levels.get("INDEX_DAY_START", DEFAULT_INDEX_DAY_START) if levels else DEFAULT_INDEX_DAY_START, "LEVELS_INDEX_DAY_START")
        setup = env.section("SETUP") if env is not None else None            # el breakeven del dibujo es el mismo que aplica Setup
        risk_pct, be_pct = (setup.get_float("RISK_PCT", 1.0), setup.get_float("BE_TRIGGER_PCT", 1.0)) if setup else (1.0, 1.0)
        self.be_r = be_pct / risk_pct if risk_pct > 0 and be_pct > 0 else None

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
        """Un mercado del barrido de la watchlist: con sus velas y sus TBR de la misma vuelta se evalúa como el del gráfico (sus avisos
        llegan a Cortex) y se avisa con `pattern.swept` de que ese mercado ya está repasado."""
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

    # -- evaluación ---------------------------------------------------------------------------------
    def update(self, c: dict | None = None, t: dict | None = None) -> None:
        background = c is not None
        if not background:
            c, t = self._candles, self._tbr
        if c is None or t is None or (c["symbol"], c["timeframe"]) != (t["symbol"], t["timeframe"]):
            return                                      # aún no han llegado las zonas de estas velas
        symbol, tf = c["symbol"], c["timeframe"]
        mark = background_of(c)
        caption = self.set_caption if not background else (lambda _text: None)   # el hexágono habla del gráfico
        ptf = self.ajustes.tf

        def publish_updated(tbr, hits, errors, unavailable, figures) -> None:
            self.publish("pattern.updated", {"symbol": symbol, "timeframe": tf, "tbr": tbr, "hits": hits, "errors": errors,
                                             "unavailable": unavailable, "tfs": {KEY: ptf}, "figures": figures, **mark})

        if not t["available"]:
            caption("sin TBR")
            publish_updated(None, [], [], [], [])
            return
        df = _velas(c, ptf)
        if df is None:
            caption(f"necesita {display_label(ptf)}")
            publish_updated(None, [], [], [f"Barrido RTH necesita velas {display_label(ptf)} y el gráfico está en {display_label(tf)} "
                                              f"(cámbialo a {display_label(ptf)} o a uno menor que lo divida)"], [])
            return
        df = df.iloc[:-1]                               # la última vela sigue formándose: solo se usan las cerradas
        if len(df) < 2:
            return
        ahead, _ = server_minus_ny(self._offset)
        ts = df["ts"].to_numpy()
        arrays = tuple(df[k].to_numpy() for k in ("open", "high", "low", "close"))
        zonas = {}                                      # (zona, día) -> (sesión de la skill TBR, Zona con su cierre en hora del servidor)
        for s in t["sessions"]:
            if s.complete and s.high > s.low and s.zone.key in ZONAS:
                day0 = (s.day.toordinal() - date(1970, 1, 1).toordinal()) * 86400
                close_ts = day0 + s.zone.start * 60 + s.zone.minutes * 60 + ahead
                zonas[(s.zone.key, s.day)] = (s, Zona(s.zone.key, s.zone.name, s.day, s.high, s.low, close_ts))
        days = sorted(day for key, day in zonas if key == "PRE_NY")
        if not days:
            caption("sin RTH cerrado")
            publish_updated(None, [], [], [], [])
            return
        results, figures, errors = [], [], []
        first_drawn = days[-1].toordinal() - self.history_days + 1
        last_tbr = None
        for day in days:
            session, rth = zonas[("PRE_NY", day)]
            tbr = ActiveTbr("PRE_NY", session.zone.name, day, session.high, session.low, session.x0, session.x1)
            last_tbr = tbr
            recent = int(ts[-1]) - rth.close_ts <= RECENT_SECONDS
            live = self.since is not None and day >= self.since       # desde el inicio del forwardtest se avisa de todo
            drawn = not background and self.history_days > 1 and day.toordinal() >= first_drawn
            if not (recent or live or drawn):
                continue
            previas = []
            for key in ("ASIA", "LONDON"):                            # las últimas cerradas antes de que empezara NY Open
                options = [z for (k, _d), (_s, z) in zonas.items() if k == key and z.close_ts <= rth.close_ts
                           and rth.close_ts - z.close_ts <= MAX_GAP]
                if options:
                    previas.append(max(options, key=lambda z: z.close_ts))
            ctx = Contexto(symbol, minutes(ptf), ts, *arrays, ahead, tbr, rth, tuple(previas), len(ts) - 1, self.day_end, self.be_r)
            try:
                hits, figs = analizar(ctx, self.ajustes)
            except Exception as exc:                    # un día con error no debe tumbar a los demás
                errors.append(f"Barrido RTH: {exc}")
                continue
            if recent or live:
                results += [(tbr, h) for h in hits]
            if recent or drawn:
                figures += figs
        results.sort(key=lambda r: r[1].ts or 0)           # en orden de hora: así los decide Cortex
        hits = [h for _t, h in results]
        publish_updated(last_tbr, hits, errors, [], figures)
        found = [h for h in hits if h.status == DETECTED]
        if errors:
            caption("error en el setup")
        elif found:
            caption(f"{len(found)} setup(s) detectado(s)")
        elif figures:
            caption(f"{len(figures)} entrada(s) dibujada(s)")
        else:
            caption("buscando rotura del RTH")
        for tbr, hit in results:
            key = (symbol, hit.key, hit.status, hit.direction, tbr.key, tbr.day, hit.ts or hit.x)
            if key in self._seen:
                continue
            self._seen.add(key)
            payload = {"symbol": symbol, "timeframe": tf, "tbr": tbr, "hit": hit,
                       "session_close": cierre_del_dia(hit.ts, ahead, self.day_end) if hit.ts else None, **mark}
            self.publish("pattern.detected" if hit.status == DETECTED else "pattern.discarded", payload)
