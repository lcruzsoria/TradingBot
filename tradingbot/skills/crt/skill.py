"""Skill CRT: Candle Range Theory por zona común (FVG ∩ iFVG, pullback y cierre sobre el CISD). Solo trabaja en el perfil de estrategia «crt»."""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np

from ...clock import server_minus_ny
from ...core import Event, Skill, register_skill
from ...timeframes import minutes
from ..calendario.skill import matches
from ..levels.daylevels import DEFAULT_US_INDICES, is_us_index
from . import engine

STRATEGY = "crt"
LTF_MINUTES = (3, 5)                           # el iFVG, el CISD y la entrada se buscan en las velas del gráfico
MAX_LATE_BARS = 2                                 # una señal se da si la vela de entrada es una de las últimas 2
MIN_BARS = 200
ENTRY_NAMES = {1: "vela siguiente al CISD", 4: "cierre del CISD"}
DEFAULT_SYMBOLS = ["NAS100.s", "SP500.s", "DJ30.s", "EURUSD", "GBPUSD"]     # los del backtest (PUPrime): con su nombre exacto


@register_skill("crt")
class CrtSkill(Skill):
    title = "CRT"
    description = ("Estrategia CRT (Candle Range Theory) por zona común, dentro de C2: una vela H3 (índices) o H4 (forex) barre con una mecha el "
                   "máximo o mínimo de la anterior; dentro de C2 un FVG (M15 o M5) y un iFVG de las velas del gráfico (M3 o M5, de TF igual o menor que el "
                   "del FVG; se busca el de mayor TF) comparten una zona. Con el iFVG ya invertido, el precio vuelve a esa zona (pullback) y la primera "
                   "vela que cierra con el cuerpo más allá del CISD (el extremo de la vela que creó el iFVG) da la entrada, a la apertura de la vela "
                   "siguiente. Stop en el extremo del sweep y objetivo 2R (el breakeven a +1R lo lleva Setup). Si la zona existe pero el precio sigue "
                   "sin volver a ella, el gráfico lo marca «Setup OK sin Entrada». Avisa a Cortex, que le da la orden a Setup; solo simulación. "
                   "Solo actúa en el perfil CRT. Ojo: en el backtest (docs/estrategia_crt/RESULTADOS_zona.md) no hay ventaja.")
    subscribes = ("candles.loaded", "clock.offset")
    publishes = ("crt.signal",)
    slot = "aux2"

    def on_start(self) -> None:
        self.error = "Configuración CRT no válida"
        self._offset: int | None = None
        self._seen: set = set()
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
        # El breakeven (a 1R) no lo hace esta skill: lo lleva Setup (SETUP_BE_TRIGGER_PCT / SETUP_RISK_PCT)
        self.rule = engine.Rule(rr=rr, be_at=0.0)
        env = self.services.env
        self.indices = env.get_list("LEVELS_US_INDICES", list(DEFAULT_US_INDICES)) if env is not None else DEFAULT_US_INDICES

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
        if signal is not None:
            self.publish("crt.signal", signal)
            caption(f"señal {symbol}")
        else:
            caption(f"{symbol}: buscando sweep + zona común FVG/iFVG + CISD")

    def _remember_marks(self, symbol: str, tf: str, df) -> None:
        """Calcula UNA vez los setups de zona común de los últimos días (los que dieron entrada, con su resultado simulado, y los «sin entrada») para que
        el gráfico los dibuje igual en cualquier timeframe; solo se recalculan si hay velas nuevas."""
        from .chart import NO_ENTRY_DAYS, zone_marks
        step = minutes(tf)
        key = (step, len(df), int(df["ts"].iloc[-1]), self._offset)
        if self.marks.get(symbol, {}).get("key") == key:
            return
        ahead, _ = server_minus_ny(self._offset)
        tail = df.tail(NO_ENTRY_DAYS * 1440 // step + 60).reset_index(drop=True)
        try:
            marks = zone_marks(tail, symbol, ahead, step, self.entry, self.rule.rr, 1.0, self.indices)
        except Exception as exc:                                         # un fallo del dibujo no puede parar la señal
            self.set_caption(f"marcas del gráfico: {exc}")
            return
        self.marks[symbol] = {"key": key, "ts": tail["ts"].to_numpy().copy(), "marks": marks, "ltf": step}

    def scan(self, symbol: str, tf: str, df) -> dict | None:
        """La señal de entrada de las últimas velas de `df` (o None). La última vela puede estar formándose: los setups se
        buscan solo con las cerradas y la entrada, que es a su apertura, sí puede ser la de la vela en curso."""
        step = minutes(tf)
        ahead, _ = server_minus_ny(self._offset)
        base_cfg = engine.INDICES if is_us_index(symbol, self.indices) else engine.FOREX
        cfg = engine.Cfg(base_cfg.htf_min, base_cfg.origin, base_cfg.session_end, ahead)
        keep = 2 * 1440 // step                                            # lo que cubre C1, C2 y el FVG de MTF que nace en C2
        df = df.tail(keep).reset_index(drop=True)
        closed = len(df) - 1
        setups, _ = engine.find_zone_setups(df.iloc[:closed], df.iloc[:closed], step, cfg)
        ts = df["ts"].to_numpy().astype(np.int64)
        views = {1: engine.view(df, 1), -1: engine.view(df, -1)}
        n = len(df)
        for st in reversed(setups):
            if st["jc"] < n - 1 - 36 * 60 // step:                         # nada que mirar: hace más de 36 h (y de una sesión)
                break
            key = (symbol, st["C2"], st["sign"])
            if key in self._seen:
                continue
            L = views[st["sign"]]
            ep = engine.entry_point(L, st, self.entry, step, self.rule, cfg, closed)
            if ep is None or ep["start"] < n - MAX_LATE_BARS:
                continue
            self._seen.add(key)
            sgn, entry, risk = st["sign"], ep["entry"], ep["risk"]
            ny = datetime.fromtimestamp(int(ts[ep["start"]]) - ahead, timezone.utc)
            close_ny = datetime.fromtimestamp(ep["end"] - ahead, timezone.utc)
            return {"symbol": symbol, "timeframe": tf, "direction": st["dirección"], "price": sgn * entry,
                    "stop": sgn * st["stop"], "target": sgn * (entry - self.rule.rr * risk), "day": ny.date(),
                    "entry_ts": int(ts[ep["start"]]), "close_ts": ep["end"],
                    "close_at": f"{close_ny:%H:%M} NY ({close_ny:%d/%m/%Y})", "strategy": STRATEGY,
                    "pattern": f"CRT ({ENTRY_NAMES[self.entry]})", "pattern_key": STRATEGY,
                    "reason": f"CRT: sweep {st['dirección']} en C2; el FVG de {st['mtf']} y el iFVG de {tf} comparten una zona; con el iFVG invertido el "
                              f"precio vuelve a ella y cierra con cuerpo más allá del CISD; entrada «{ENTRY_NAMES[self.entry]}». No depende del sesgo"}
        return None
