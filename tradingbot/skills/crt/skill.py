"""Skill CRT: Candle Range Theory por zona común (FVG ∩ iFVG, pullback y cierre sobre el CISD). Solo trabaja en el perfil de estrategia «crt»."""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np

from ...clock import server_minus_ny
from ...core import Event, Skill, register_skill
from ...timeframes import minutes
from ..calendario.skill import matches
from ..levels.daylevels import DEFAULT_US_INDICES, is_us_index
from ..bias.models import Bias, BiasResult
from . import bias as crt_bias, engine
from .chart import complete_series as engine_complete, sl_text

STRATEGY = "crt"
LTF_MINUTES = (3, 5)                           # el iFVG, el CISD y la entrada se buscan en las velas del gráfico
MAX_LATE_BARS = 2                                 # una señal se da si la vela de entrada es una de las últimas 2
MIN_BARS = 200
ENTRY_NAMES = {1: "vela siguiente al CISD", 4: "cierre del CISD"}
DEFAULT_SYMBOLS = ["NAS100.s", "SP500.s", "DJ30.s", "EURUSD", "GBPUSD"]     # los del backtest (PUPrime): con su nombre exacto


def build_signal(symbol: str, tf: str, st: dict, ep: dict, ts, ahead: int, rule: engine.Rule, entry_model: int, points) -> dict:
    """El `crt.signal` de un setup con su entrada (`engine.find_zone_setups` + `engine.entry_point`). La usa la skill y el script que rehace el forwardtest."""
    sgn, entry, risk = st["sign"], ep["entry"], ep["risk"]
    ny = datetime.fromtimestamp(int(ts[ep["start"]]) - ahead, timezone.utc)
    close_ny = datetime.fromtimestamp(ep["end"] - ahead, timezone.utc)
    return {"symbol": symbol, "timeframe": tf, "direction": st["dirección"], "price": sgn * entry,
            "stop": sgn * st["stop"], "target": sgn * (entry - rule.rr * risk), "day": ny.date(),
            "entry_ts": int(ts[ep["start"]]), "close_ts": ep["end"],
            "close_at": f"{close_ny:%H:%M} NY ({close_ny:%d/%m/%Y})", "strategy": STRATEGY,
            "pattern": f"CRT ({ENTRY_NAMES[entry_model]})", "pattern_key": STRATEGY,
            "bias_points": points, "bias_result": points.result(), "bias_enabled": points.enabled,
            "reason": f"CRT: sweep {st['dirección']} en C2 ({st.get('sweep', 'vela C1')}); el iFVG de M{st.get('ltf', tf)} y el FVG de {st['mtf']} (de sentido contrario) forman un BPR; con el iFVG invertido el "
                      f"precio vuelve a él y cierra con cuerpo más allá del CISD; entrada «{ENTRY_NAMES[entry_model]}». {points.summary()}"}


@register_skill("crt")
class CrtSkill(Skill):
    title = "CRT"
    description = ("Estrategia CRT (Candle Range Theory) por zona común, dentro de C2: una vela H3 (índices) o H4 (forex) barre con una mecha el "
                   "máximo o mínimo de la anterior; dentro de C2 un iFVG y un FVG de sentido contrario forman un BPR (zona común): los dos de 15 min, si no los dos de 5 y solo "
                   "después FVG de 15 con iFVG de 5; el retest, el CISD y la entrada son del TF menor (el del iFVG). Con el iFVG ya invertido, el precio vuelve a esa zona (pullback) y la primera "
                   "vela que cierra con el cuerpo más allá del CISD (el extremo de la vela que creó el iFVG) da la entrada, a la apertura de la vela "
                   "siguiente. Stop en el extremo del sweep y objetivo 2R (el breakeven a +1R lo lleva Setup). Si la zona existe pero el precio sigue "
                   "sin volver a ella, el gráfico lo marca «Setup OK sin Entrada». Avisa a Cortex, que le da la orden a Setup; solo simulación. "
                   "Solo actúa en el perfil CRT. Ojo: en el backtest (docs/estrategia_crt/RESULTADOS_zona.md) no hay ventaja.")
    subscribes = ("candles.loaded", "clock.offset")
    publishes = ("crt.signal", "crt.pending", "crt.blocked", "bias.updated", "bias.history")
    slot = "aux2"

    def on_start(self) -> None:
        self.error = "Configuración CRT no válida"
        self._offset: int | None = None
        self._seen: set = set()
        self._pending_seen: set = set()                  # (símbolo, C2, lado, CISD) de los avisos «setup completo, falta cerrar más allá del CISD» ya dados
        self._blocked_seen: set = set()                  # setups sin entrada por el stop máximo que ya se avisaron
        self._extra: dict[tuple, tuple] = {}             # (símbolo, TF) -> (última vela del perfil, velas que se pidieron a MT5)
        self._latest: dict[str, tuple] = {}              # símbolo -> (velas, cfg, último setup reciente o None): para la tarjeta del sesgo
        self._hist_key: dict[str, tuple] = {}            # símbolo -> clave del último histograma publicado
        self._card: dict[str, tuple] = {}                # símbolo -> lo último que se publicó a la tarjeta (solo se publica si cambia)
        self.marks: dict[str, dict] = {}                 # símbolo -> {ts, marks, key}: los setups de los últimos días, con las velas de la skill (M5 o M3)
        app = (self.services.app_cfg or {}).get("app", {})
        self.active = str(app.get("strategy") or "") == STRATEGY
        try:
            self._load_settings()
        except ValueError as exc:
            self.error = str(exc)
            raise
        self.error = ""
        self.set_caption("esperando velas" if self.active else f"solo en el perfil {STRATEGY.upper()}")

    def _load_settings(self) -> None:
        s = self.settings                                                              # tradingbot.env, bloque CRT
        self.symbols = s.get_list("SYMBOLS", DEFAULT_SYMBOLS)
        self.entry = s.get_int("ENTRY", 1)
        if self.entry not in ENTRY_NAMES:
            raise ValueError(f"CRT_ENTRY={self.entry}: usa 1 (apertura de la vela siguiente a la que cierra sobre el CISD) o 4 (cierre de esa vela)")
        rr = s.get_float("RR", 2.0)
        if rr <= 0:
            raise ValueError("CRT_RR debe ser mayor que 0")
        engine.MAX_SL_FOREX = s.get_float("MAX_SL_FOREX_PIPS", 25.0) * 1e-4        # stop máximo: más allá no se opera (0 = sin límite)
        engine.MAX_SL_INDICES = s.get_float("MAX_SL_INDICES_POINTS", 125.0)
        if engine.MAX_SL_FOREX < 0 or engine.MAX_SL_INDICES < 0:
            raise ValueError("CRT_MAX_SL_FOREX_PIPS y CRT_MAX_SL_INDICES_POINTS no pueden ser negativos")
        # El breakeven (a 1R) no lo hace esta skill: lo lleva Setup (SETUP_BE_TRIGGER_PCT / SETUP_RISK_PCT)
        self.rule = engine.Rule(rr=rr, be_at=0.0)
        env = self.services.env
        self.indices = env.get_list("LEVELS_US_INDICES", list(DEFAULT_US_INDICES)) if env is not None else DEFAULT_US_INDICES
        self.bias_cfg = crt_bias.load_cfg(s)                                           # sesgo propio del perfil CRT (CRT_BIAS_*)

    def handle(self, event: Event) -> None:
        if self.error:
            raise ValueError(self.error)
        if event.topic == "clock.offset":
            self._offset = event.payload.get("server_offset")
            return
        if not self.active:
            return
        symbol, tf, df = event.payload["symbol"], event.payload["timeframe"], event.payload["df"]
        background = bool(event.payload.get("background"))      # barrido de la watchlist: el hexágono habla del gráfico
        caption = self.set_caption if not background else (lambda _text: None)
        if not matches(symbol, self.symbols):
            caption(f"{symbol} no está en CRT_SYMBOLS")
            return
        if df is None or minutes(tf) not in LTF_MINUTES:
            caption("necesita velas de M3 o M5")
            return
        if len(df) < MIN_BARS:
            caption(f"{symbol}: faltan velas ({len(df)})")
            return
        self._remember_marks(symbol, tf, df)
        signal = self.scan(symbol, tf, df)
        if not background:
            self._publish_bias(symbol, tf)
            self._publish_history(symbol, tf, df)
        if signal is not None:
            self.publish("crt.signal", signal)
            caption(f"señal {symbol}")
        else:
            caption(f"{symbol}: buscando sweep + zona común FVG/iFVG + CISD")

    def _points(self, full, cfg: engine.Cfg, st: dict, ahead: int) -> "crt_bias.SetupBias":
        """Los puntos del sesgo CRT de un setup (la zona común del CRT contra las zonas de reversión HTF a favor, de los 10 días anteriores a su C2)."""
        sgn = st["sign"]
        common = (sgn * st["z_bottom"], sgn * st["z_top"])
        return crt_bias.evaluate(full, st["dirección"], int(st["C2"]), common, cfg, self.bias_cfg, ahead)

    HISTORY_HOURS = 36                                                  # un setup da sesgo a las velas siguientes durante 36 h (como la tarjeta)

    def _publish_history(self, symbol: str, tf: str, df) -> None:
        """El histograma del sesgo CRT: en cada vela, los puntos (± según el lado) del último setup con entrada de las 36 h anteriores, con los votos
        de cada regla HTF (FVG, rejection block, order block). Solo se recalcula con velas nuevas."""
        step = minutes(tf)
        key = (symbol, step, len(df), int(df["ts"].iloc[-1]), self._offset, self.bias_cfg)
        if self._hist_key.get(symbol) == key:
            return
        self._hist_key[symbol] = key
        ahead, _ = server_minus_ny(self._offset)
        base_cfg = engine.INDICES if is_us_index(symbol, self.indices) else engine.FOREX
        cfg = engine.Cfg(base_cfg.htf_min, base_cfg.origin, base_cfg.session_end, ahead)
        n, ts = len(df), df["ts"].to_numpy().astype(np.int64)
        scores, votes = np.zeros(n), np.zeros((n, len(crt_bias.RULES)))
        try:
            series = self._series(symbol, tf, df, cfg)
            setups, _ = engine.find_multi_setups({m: d.iloc[:len(d) - 1] for m, d in series.items()}, cfg, df)
            cache = crt_bias.zone_cache(df, cfg, self.bias_cfg) if self.bias_cfg.enabled else None
            known = []                                                    # (hora en que se conoce el setup, puntos con signo, votos con signo)
            for st in setups:
                sgn = st["sign"]
                points = crt_bias.evaluate(df, st["dirección"], int(st["C2"]), (sgn * st["z_bottom"], sgn * st["z_top"]), cfg, self.bias_cfg, ahead, cache)
                side = 1 if st["dirección"] == "long" else -1
                counts = points.counts()
                known.append((int(series[st["ltf"]]["ts"].iloc[st["jc"]]) + st["ltf"] * 60, side * points.score,
                              [side if counts[k] else 0 for k, _t in crt_bias.RULES]))
            known.sort(key=lambda x: x[0])
            starts = np.array([k[0] for k in known], dtype=np.int64)
            for i in range(n):
                j = int(np.searchsorted(starts, ts[i], "right")) - 1
                if j >= 0 and ts[i] - starts[j] <= self.HISTORY_HOURS * 3600:
                    scores[i], votes[i] = known[j][1], known[j][2]
        except Exception as exc:                                          # un fallo del histograma no puede parar la señal
            self.set_caption(f"histograma del sesgo: {exc}")
            return
        self.publish("bias.history", {"symbol": symbol, "timeframe": tf, "scores": scores, "min_score": max(self.bias_cfg.min_score, 1e-9), "lateral": None,
                                      "rules": [(title, 1.0) for _k, title in crt_bias.RULES], "votes": votes, "ts": ts})

    def _publish_bias(self, symbol: str, tf: str) -> None:
        """La tarjeta del sesgo enseña el del último setup reciente del mercado del gráfico (o «sin setup»); solo se publica si cambia."""
        latest = self._latest.get(symbol)
        if latest is None:
            return
        full, cfg, st, ahead = latest
        if st is None:
            key = (None, self.bias_cfg.enabled)
            result = BiasResult(Bias.NO_BIAS, None, (), {}, "Sin setup CRT en las últimas 36 h" + ("" if self.bias_cfg.enabled else " · sesgo CRT deshabilitado (sesgo 0, todo GO)"),
                                0.0, max(self.bias_cfg.min_score, 1e-9))
        else:
            points = self._points(full, cfg, st, ahead)
            key = (int(st["C2"]), st["dirección"], self.bias_cfg.enabled, points.score)
            result = points.result()
        if self._card.get(symbol) == key:
            return
        self._card[symbol] = key
        self.set_caption(f"{symbol}: {result.bias.value} ({result.score:+g})")
        self.publish("bias.updated", {"result": result, "symbol": symbol, "timeframe": tf, "reason": "setup CRT"})

    def _remember_marks(self, symbol: str, tf: str, df) -> None:
        """Calcula UNA vez los setups de zona común de los últimos días (los que dieron entrada, con su resultado simulado, y los «sin entrada») para que
        el gráfico los dibuje igual en cualquier timeframe; solo se recalculan si hay velas nuevas."""
        from .chart import NO_ENTRY_DAYS, zone_marks
        step = minutes(tf)
        key = (step, len(df), int(df["ts"].iloc[-1]), self._offset)
        if self.marks.get(symbol, {}).get("key") == key:
            return
        ahead, _ = server_minus_ny(self._offset)
        base_cfg = engine.INDICES if is_us_index(symbol, self.indices) else engine.FOREX
        cfg = engine.Cfg(base_cfg.htf_min, base_cfg.origin, base_cfg.session_end, ahead)
        tail = df.tail(NO_ENTRY_DAYS * 1440 // step + 60).reset_index(drop=True)
        try:
            series = {m: d.tail(NO_ENTRY_DAYS * 1440 // m + 60).reset_index(drop=True) for m, d in self._series(symbol, tf, df, cfg).items()}
            series[step] = tail
            marks = zone_marks(series, symbol, ahead, step, self.entry, self.rule.rr, 1.0, self.indices, tail["ts"].to_numpy(), df)
        except Exception as exc:                                         # un fallo del dibujo no puede parar la señal
            self.set_caption(f"marcas del gráfico: {exc}")
            return
        self.marks[symbol] = {"key": key, "ts": tail["ts"].to_numpy().copy(), "marks": marks, "ltf": step}

    def _series(self, symbol: str, tf: str, df, cfg: engine.Cfg) -> dict:
        """Las velas de los TF de la zona común (15 y 5 min) de un mercado: las del perfil (`df`), las que se agrupan desde ellas (la de 15 min) y las que hay
        que pedirle a MT5 (la de 3 con el perfil en 5, la de 5 con el perfil en 3). Si MT5 no las da, esa combinación no se mira."""
        step = minutes(tf)
        series = {step: df}
        last = int(df["ts"].iloc[-1])
        source = getattr(self.services, "source", None)
        for m in engine.ZONE_TFS:
            if m == step or (m % step == 0 and m > step):
                continue                                                          # las de múltiplo del TF del perfil salen de sus velas
            cached = self._extra.get((symbol, m))
            if cached is not None and cached[0] == last:
                series[m] = cached[1]
                continue
            if source is None or not hasattr(source, "load_recent"):
                continue
            try:
                extra = source.load_recent(symbol, f"{m}m", 2 * 1440 // m + 60)
            except Exception as exc:                                              # sin esas velas solo se pierden las combinaciones con ese TF
                self.set_caption(f"{symbol}: sin velas de {m}m ({type(exc).__name__})")
                continue
            self._extra[(symbol, m)] = (last, extra)
            series[m] = extra
        return engine_complete(series, cfg)

    def _announce_pending(self, symbol: str, tf: str, waiting: list, ahead: int, htf_min: int) -> None:
        """Avisa (una vez por setup) de que el BPR, el iFVG invertido y el retest ya están y solo falta que una vela del TF menor cierre con cuerpo más allá del CISD."""
        for w in waiting:
            sign = w["sign"]
            key = (symbol, int(w["C2"]), sign, round(float(w["level"]), 6))
            if key in self._pending_seen:
                continue
            self._pending_seen.add(key)
            c2 = datetime.fromtimestamp(int(w["C2"]) - ahead, timezone.utc)
            self.publish("crt.pending", {"symbol": symbol, "timeframe": tf, "direction": w["dirección"], "level": sign * float(w["level"]),
                                         "zone": tuple(sorted((sign * float(w["z_bottom"]), sign * float(w["z_top"])))), "stop": sign * float(w["stop"]),
                                         "ltf": w["ltf"], "mtf": w["mtf"], "sweep": w["sweep"], "c2": f"{c2:%d/%m %H:%M}",
                                         "htf": f"H{htf_min // 60}"})

    def scan(self, symbol: str, tf: str, df) -> dict | None:
        """La señal de entrada de las últimas velas (o None), con todas las combinaciones de TF del FVG y del iFVG (15 y 5 min, TF del FVG >= TF del iFVG). Cada
        combinación se mira con las velas del TF de su iFVG (el CISD y la entrada son de ese TF). La última vela puede estar formándose: los setups se buscan solo
        con las cerradas y la entrada, que es a su apertura, sí puede ser la de la vela en curso."""
        step = minutes(tf)
        full = df                                                          # todo el histórico: el sesgo mira hasta 10 días atrás
        ahead, _ = server_minus_ny(self._offset)
        base_cfg = engine.INDICES if is_us_index(symbol, self.indices) else engine.FOREX
        cfg = engine.Cfg(base_cfg.htf_min, base_cfg.origin, base_cfg.session_end, ahead)
        series = {m: d.tail(2 * 1440 // m).reset_index(drop=True) for m, d in self._series(symbol, tf, df, cfg).items()}    # lo que cubre C1, C2 y los FVG de C2
        closed = {m: len(d) - 1 for m, d in series.items()}
        setups, _ = engine.find_multi_setups({m: d.iloc[:closed[m]] for m, d in series.items()}, cfg, full)
        ts = {m: d["ts"].to_numpy().astype(np.int64) for m, d in series.items()}
        views = {m: {1: engine.view(d, 1), -1: engine.view(d, -1)} for m, d in series.items()}
        for st in setups:                                                  # un setup con entrada que el stop máximo cancela: se avisa (no hay señal)
            m = st["ltf"]
            key = (symbol, st["C2"], st["sign"])
            if key in self._blocked_seen or st["jc"] + 1 < len(series[m]) - MAX_LATE_BARS:
                continue
            if engine.entry_point(views[m][st["sign"]], st, self.entry, m, self.rule, cfg, closed[m]) is not None:
                continue
            risk = engine.sl_blocked(views[m][st["sign"]], st, self.entry, m, self.rule, cfg, closed[m])
            if risk is None:
                continue
            self._blocked_seen.add(key)
            self.publish("crt.blocked", {"symbol": symbol, "timeframe": tf, "direction": st["dirección"], "stop": st["sign"] * st["stop"],
                                         "entry_ts": int(ts[m][st["jc"]]) + m * 60, "text": sl_text(risk, cfg, long=True), "strategy": STRATEGY})
        recent = [x for x in setups if x["jc"] >= len(series[x["ltf"]]) - 1 - 36 * 60 // x["ltf"]]
        self._announce_pending(symbol, tf, getattr(setups, "waiting", []), ahead, cfg.htf_min)
        self._latest[symbol] = (full, cfg, recent[-1] if recent else None, ahead)
        for st in reversed(setups):
            m = st["ltf"]
            n = len(series[m])
            if st["jc"] < n - 1 - 36 * 60 // m:                            # nada que mirar: hace más de 36 h (y de una sesión)
                continue
            key = (symbol, st["C2"], st["sign"])
            if key in self._seen:
                continue
            ep = engine.entry_point(views[m][st["sign"]], st, self.entry, m, self.rule, cfg, closed[m])
            if ep is None or ep["start"] < n - MAX_LATE_BARS:
                continue
            self._seen.add(key)
            points = self._points(full, cfg, st, ahead)
            return build_signal(symbol, tf, st, ep, ts[m], ahead, self.rule, self.entry, points)
        return None
