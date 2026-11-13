"""Skill Barrido: los setups de barrido del modelo Greenbird del perfil Barrido_NYAM (índices USA), en un solo hexágono grande.

- `rth`:  el barrido del RTH (09:00-10:00 NY) en NY Open, con su breakeven y su segundo objetivo (`rth.py`).
- `asia`: el barrido de Asia (20:00-00:00 NY) entre las 00:00 y las 01:00 (`asia.py`).
- `pdh`:  el barrido del PDH/PDL entre las 20:00 y las 21:00, con objetivo en el otro lado de Asia (`pdh.py`).
- `continuacion`: la rotura del RTH tras tocar su 50 % entre las 10:00 y las 11:00, a favor de la rotura, stop 40 puntos y objetivo 2R (`continuacion.py`).
- `londres`: lo mismo con el rango de Londres: barrido entre las 02:00 y las 03:00, objetivo en el otro lado de Londres y salida al cierre (05:00) (`londres.py`).

Cada setup tiene su propio módulo de reglas y su propio bloque de ajustes (BARRIDO_RTH_*, BARRIDO_ASIA_*, BARRIDO_PDH_*, BARRIDO_LONDRES_*); esta skill solo los orquesta:
con las TBR de la skill TBR y las velas del gráfico evalúa cada día (o noche) con el rango ya cerrado y publica lo mismo que publica Pattern
(`pattern.updated`, `pattern.detected`, `pattern.discarded`, `pattern.swept`) para que Cortex, Setup, Stats y la ventana la traten igual.
Los tipos de esos mensajes viven en `skills/_comun/contratos.py`. Es independiente de la skill Pattern. La señal llega en cuanto cierra la
vela de entrada. `BARRIDO_SETUPS` (rth, asia, pdh, londres, continuacion) elige qué setups busca.
"""
from __future__ import annotations

from datetime import date

from ...clock import server_minus_ny
from ...core import Event, Skill, background_of, register_skill
from ...timeframes import display_label, minutes
from .._comun.contratos import DETECTED
from ..feed.datasource import aggregate_candles
from . import asia, continuacion, londres, pdh, rth
from .rth import cierre_del_dia

SETUPS = {"rth": rth, "asia": asia, "pdh": pdh, "londres": londres, "continuacion": continuacion}          # clave del setup -> su módulo (KEY, Ajustes, contextos, analizar)
DEFAULT_HISTORY_DAYS = 30        # días pasados de los que se dibujan las entradas
RECENT_SECONDS = 24 * 3600       # un rango cerrado en el último día siempre se evalúa y se avisa
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


@register_skill("barrido")
class BarridoSkill(Skill):
    title = "Barrido"
    description = ("Setups de barrido del perfil Barrido_NYAM. RTH: tras el rango 09:00-10:00, la primera rotura (vela que cierra fuera) entre las "
                   "10:00 y las 11:00 y la primera vela M5 posterior que cierra dentro (antes de las 12:00) da la entrada; stop fijo de 30 puntos "
                   "(o el swing + 5), objetivo 1 en el lado contrario del RTH y breakeven al tomar el Low/High de NY Open. Asia: lo mismo con el "
                   "rango de Asia entre las 00:00 y la 01:00 (la vela de entrada cierra dentro de Asia a la 01:00 como tarde) y objetivo en el lado contrario de Asia. PDH/PDL: "
                   "nivel del día anterior sin tocar que se barre entre las 20:00 y las 21:00; entrada en el primer cierre de vuelta dentro y objetivo en el otro lado de Asia. Londres: lo mismo entre las 02:00 y las 03:00 con salida al cierre de Londres (05:00). Continuación: tras tocar el 50 % del RTH, la primera vela M5 que cierra fuera del rango (antes de las 11:00) da la entrada a favor; stop 40 puntos y objetivo 2R (Nasdaq). Cortex los "
                   "valida; solo informa, no envía órdenes.")
    subscribes = ("candles.loaded", "tbr.updated", "clock.offset")
    publishes = ("pattern.updated", "pattern.detected", "pattern.discarded", "pattern.swept")
    slot = 4                      # hexágono grande 4 del anillo, el que ocupa Pattern en los demás perfiles

    def on_start(self) -> None:
        self.error = "Configuración BARRIDO no válida"
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
        # tradingbot.env, bloque BARRIDO: BARRIDO_SETUPS, BARRIDO_HISTORY_DAYS y, por setup, BARRIDO_RTH_*, BARRIDO_ASIA_*, BARRIDO_PDH_*, BARRIDO_LONDRES_* y BARRIDO_CONTINUACION_*
        names = [n.lower() for n in self.settings.get_list("SETUPS", list(SETUPS))]
        unknown = [n for n in names if n not in SETUPS]
        if unknown or not names:
            raise ValueError(f"BARRIDO_SETUPS={', '.join(names)}: setup desconocido {', '.join(unknown)}. Disponibles: {', '.join(SETUPS)}.")
        self.setups = {n: (SETUPS[n], SETUPS[n].Ajustes.desde(self.settings.section(n))) for n in names}
        self.history_days = self.settings.get_int("HISTORY_DAYS", DEFAULT_HISTORY_DAYS)
        if self.history_days < 1:
            raise ValueError(f"BARRIDO_HISTORY_DAYS={self.history_days} debe ser 1 o más.")
        env = self.services.env
        self.since = _forward_start(env)
        levels = env.section("LEVELS") if env is not None else None          # el día de trading de los índices USA acaba cuando empieza el siguiente
        self.day_end = _hhmm(levels.get("INDEX_DAY_START", DEFAULT_INDEX_DAY_START) if levels else DEFAULT_INDEX_DAY_START, "LEVELS_INDEX_DAY_START")
        setup = env.section("SETUP") if env is not None else None            # el breakeven del dibujo es el mismo que aplica Setup
        risk_pct, be_pct = (setup.get_float("RISK_PCT", 1.0), setup.get_float("BE_TRIGGER_PCT", 1.0)) if setup else (1.0, 1.0)
        strategy = (self.services.app_cfg["app"].get("strategy") or "") if self.services.app_cfg else ""
        if env is not None and strategy:                                     # <ESTRATEGIA>_SETUP_BE_TRIGGER_PCT: 0 = sin breakeven por % de ganancia
            be_pct = env.section(f"{strategy}_SETUP").get_float("BE_TRIGGER_PCT", be_pct)
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
        tfs = {mod.KEY: aj.tf for mod, aj in self.setups.values()}

        def publish_updated(tbr, hits, errors, unavailable, figures) -> None:
            self.publish("pattern.updated", {"symbol": symbol, "timeframe": tf, "tbr": tbr, "hits": hits, "errors": errors,
                                             "unavailable": unavailable, "tfs": tfs, "figures": figures, **mark})

        if not t["available"]:
            caption("sin TBR")
            publish_updated(None, [], [], [], [])
            return
        ahead, _ = server_minus_ny(self._offset)
        results, figures, errors, unavailable = [], [], [], []
        last_tbr, last_ts = None, 0
        for mod, aj in self.setups.values():
            df = _velas(c, aj.tf)
            if df is None:
                unavailable.append(f"{mod.TITLE} necesita velas {display_label(aj.tf)} y el gráfico está en {display_label(tf)} "
                                   f"(cámbialo a {display_label(aj.tf)} o a uno menor que lo divida)")
                continue
            df = df.iloc[:-1]                           # la última vela sigue formándose: solo se usan las cerradas
            if len(df) < 2:
                continue
            ts = df["ts"].to_numpy()
            arrays = tuple(df[k].to_numpy() for k in ("open", "high", "low", "close"))
            contexts = mod.contextos(symbol, minutes(aj.tf), ts, *arrays, t["sessions"], ahead, self.day_end, self.be_r)
            if not contexts:
                continue
            first_drawn = contexts[-1].tbr.day.toordinal() - self.history_days + 1
            for ctx in contexts:
                day = ctx.tbr.day
                recent = int(ts[-1]) - ctx.cierre_rango <= RECENT_SECONDS
                live = self.since is not None and day >= self.since       # desde el inicio del forwardtest se avisa de todo
                drawn = not background and self.history_days > 1 and day.toordinal() >= first_drawn
                if ctx.cierre_rango > last_ts:
                    last_tbr, last_ts = ctx.tbr, ctx.cierre_rango
                if not (recent or live or drawn):
                    continue
                try:
                    hits, figs = mod.analizar(ctx, aj)
                except Exception as exc:                # un día con error no debe tumbar a los demás
                    errors.append(f"{mod.TITLE}: {exc}")
                    continue
                if recent or live:
                    results += [(ctx.tbr, h) for h in hits]
                if recent or drawn:
                    figures += figs
        if last_tbr is None:
            caption("necesita velas más finas" if unavailable and not errors else "sin rango cerrado")
            publish_updated(None, [], errors, unavailable, [])
            return
        results.sort(key=lambda r: r[1].ts or 0)           # en orden de hora: así los decide Cortex
        hits = [h for _t, h in results]
        publish_updated(last_tbr, hits, errors, unavailable, figures)
        found = [h for h in hits if h.status == DETECTED]
        if errors:
            caption("error en un setup")
        elif found:
            caption(f"{len(found)} setup(s) detectado(s)")
        elif figures:
            caption(f"{len(figures)} entrada(s) dibujada(s)")
        else:
            caption("buscando barridos")
        for tbr, hit in results:
            key = (symbol, hit.key, hit.status, hit.direction, tbr.key, tbr.day, hit.ts or hit.x)
            if key in self._seen:
                continue
            self._seen.add(key)
            payload = {"symbol": symbol, "timeframe": tf, "tbr": tbr, "hit": hit,
                       "session_close": int(hit.levels["cierre"]) if hit.levels.get("cierre") else (cierre_del_dia(hit.ts, ahead, self.day_end) if hit.ts else None), **mark}
            self.publish("pattern.detected" if hit.status == DETECTED else "pattern.discarded", payload)
