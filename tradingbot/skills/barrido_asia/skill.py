"""Skill Barrido de Asia: busca el setup del barrido del rango de Asia entre las 00:00 y las 01:00 NY (solo perfil Barrido_ASIA, índices USA).

Skill independiente: no hereda ni importa código de Pattern. Con las TBR de la skill TBR (Asia) y las velas del gráfico
busca, en cada noche con Asia ya cerrada, la rotura y la entrada de `deteccion.py`, y publica lo mismo que publica Pattern
(`pattern.updated`, `pattern.detected`, `pattern.discarded`, `pattern.swept`) para que Cortex, Setup, Stats y la ventana la traten igual.
Los tipos de esos mensajes viven en `skills/_comun/contratos.py`. Es independiente de la skill Barrido RTH (aunque se parezcan, cada
una tiene su propio código). La señal llega en cuanto cierra la vela de entrada.
"""
from __future__ import annotations

from datetime import date

from ...clock import server_minus_ny
from ...core import Event, Skill, background_of, register_skill
from ...timeframes import display_label, minutes
from .._comun.contratos import DETECTED
from ..feed.datasource import aggregate_candles
from .deteccion import KEY, Ajustes, analizar, cierre_del_dia, contextos

DEFAULT_HISTORY_DAYS = 30        # días pasados de los que se dibujan las entradas
RECENT_SECONDS = 24 * 3600       # una noche de Asia cerrada en el último día siempre se evalúa y se avisa
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


@register_skill("barrido_asia")
class BarridoAsiaSkill(Skill):
    title = "Barrido Asia"
    description = ("Setup del perfil Barrido_ASIA: tras el rango de Asia (20:00-00:00), la primera rotura de su High o su Low (una vela que cierra fuera) "
                   "entre las 00:00 y la 01:00 y la primera vela M5 posterior que cierra de nuevo dentro del rango (antes de las 02:00) da la "
                   "entrada. Stop fijo de 30 puntos (o el swing + 5 si queda más lejos) y objetivo en el lado contrario de Asia. Cortex lo "
                   "valida; solo informa, no envía órdenes.")
    subscribes = ("candles.loaded", "tbr.updated", "clock.offset")
    publishes = ("pattern.updated", "pattern.detected", "pattern.discarded", "pattern.swept")
    slot = 4                      # hexágono grande 4 del anillo, el que ocupa Pattern en los demás perfiles

    def on_start(self) -> None:
        self.error = "Configuración BARRIDO_ASIA no válida"
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
        # tradingbot.env, bloque BARRIDO_ASIA
        self.ajustes = Ajustes.desde(self.settings)
        self.history_days = self.settings.get_int("HISTORY_DAYS", DEFAULT_HISTORY_DAYS)
        if self.history_days < 1:
            raise ValueError(f"BARRIDO_ASIA_HISTORY_DAYS={self.history_days} debe ser 1 o más.")
        env = self.services.env
        self.since = _forward_start(env)
        levels = env.section("LEVELS") if env is not None else None          # el día de trading de los índices USA acaba cuando empieza el siguiente
        self.day_end = _hhmm(levels.get("INDEX_DAY_START", DEFAULT_INDEX_DAY_START) if levels else DEFAULT_INDEX_DAY_START, "LEVELS_INDEX_DAY_START")

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
            publish_updated(None, [], [], [f"Barrido Asia necesita velas {display_label(ptf)} y el gráfico está en {display_label(tf)} "
                                              f"(cámbialo a {display_label(ptf)} o a uno menor que lo divida)"], [])
            return
        df = df.iloc[:-1]                               # la última vela sigue formándose: solo se usan las cerradas
        if len(df) < 2:
            return
        ahead, _ = server_minus_ny(self._offset)
        ts = df["ts"].to_numpy()
        arrays = tuple(df[k].to_numpy() for k in ("open", "high", "low", "close"))
        contexts = contextos(symbol, minutes(ptf), ts, *arrays, t["sessions"], ahead, self.day_end)
        if not contexts:
            caption("sin Asia cerrada")
            publish_updated(None, [], [], [], [])
            return
        results, figures, errors = [], [], []
        first_drawn = contexts[-1].tbr.day.toordinal() - self.history_days + 1
        for ctx in contexts:
            day = ctx.tbr.day
            recent = int(ts[-1]) - ctx.asia.close_ts <= RECENT_SECONDS
            live = self.since is not None and day >= self.since       # desde el inicio del forwardtest se avisa de todo
            drawn = not background and self.history_days > 1 and day.toordinal() >= first_drawn
            if not (recent or live or drawn):
                continue
            try:
                hits, figs = analizar(ctx, self.ajustes)
            except Exception as exc:                    # un día con error no debe tumbar a los demás
                errors.append(f"Barrido Asia: {exc}")
                continue
            if recent or live:
                results += [(ctx.tbr, h) for h in hits]
            if recent or drawn:
                figures += figs
        last_tbr = contexts[-1].tbr
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
            caption("buscando rotura de Asia")
        for tbr, hit in results:
            key = (symbol, hit.key, hit.status, hit.direction, tbr.key, tbr.day, hit.ts or hit.x)
            if key in self._seen:
                continue
            self._seen.add(key)
            payload = {"symbol": symbol, "timeframe": tf, "tbr": tbr, "hit": hit,
                       "session_close": cierre_del_dia(hit.ts, ahead, self.day_end) if hit.ts else None, **mark}
            self.publish("pattern.detected" if hit.status == DETECTED else "pattern.discarded", payload)
