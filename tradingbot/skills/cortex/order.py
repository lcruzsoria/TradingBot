"""Orden que Cortex le pasa a Setup: todo lo que hace falta para operar, ya decidido."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..levels.daylevels import DEFAULT_DAY_START, DEFAULT_INDEX_DAY_START, DEFAULT_US_INDICES, is_us_index, parse_time

DAY = 86_400
MAX_HOLD_SECONDS = DAY                # tope: ningún trade de patrón dura más de 24 h
DEFAULT_AHEAD = 7 * 3600              # servidor = NY + 7 h (brokers con cierre en Nueva York)
SESSION_END = "antes del cierre de la sesión (17:00 NY; 18:00 en índices americanos)"


def session_close_ts(symbol: str, entry_ts: int, ahead: int = DEFAULT_AHEAD, day_start: str = DEFAULT_DAY_START,
                     index_day_start: str = DEFAULT_INDEX_DAY_START, indices=DEFAULT_US_INDICES) -> int:
    """Hora (servidor) a la que todo trade abierto en `entry_ts` debe estar cerrado: el final de la sesión del mercado, que es
    el inicio del siguiente día de trading (17:00 NY en el resto, 18:00 NY en los índices americanos), con tope de 24 h.
    La posición se cierra al cierre de la última vela anterior a esa hora."""
    start = parse_time(index_day_start if is_us_index(symbol, indices) else day_start, "inicio del día") * 60
    ny = int(entry_ts) - int(ahead)                                 # hora de NY como si fuera UTC
    end = ny - ny % DAY + start
    if end <= ny:
        end += DAY
    return min(end + int(ahead), int(entry_ts) + MAX_HOLD_SECONDS)


@dataclass(frozen=True)
class Order:
    symbol: str              # activo a operar
    timeframe: str           # temporalidad con la que se identificó el patrón
    direction: str           # "long" o "short"
    pattern: str             # patrón de entrada identificado (título)
    pattern_key: str
    tbr_zone: str            # TBR usada: nombre, día y niveles
    tbr_day: date
    tbr_high: float
    tbr_low: float
    tbr_mid: float
    price: float             # precio de referencia del patrón (entrada)
    stop: float | None       # los que defina el patrón (hit.levels["stop"], ["target"])
    target: float | None
    bias: str                # sesgo vigente (Bullish / Bearish / No Bias) y su puntuación
    score: float
    reason: str              # por qué Cortex da GO
    close_at: str | None = None    # cierre por tiempo, si la estrategia lo tiene (Calendario), para mostrarlo
    entry_ts: int | None = None    # hora de servidor de la vela de entrada y del cierre por tiempo: Setup sigue la posición
    close_ts: int | None = None

    @property
    def label(self) -> str:
        where = f" en {self.tbr_zone}" if self.tbr_zone else ""
        return f"{self.direction.capitalize()} {self.symbol} {self.timeframe} ({self.pattern}{where})"


def build_order(payload: dict, decision, bias_result, close_ts_for=session_close_ts) -> Order:
    """Orden a partir de un `pattern.detected`, la decisión de Cortex y el sesgo vigente."""
    hit, tbr = payload["hit"], payload["tbr"]
    close_ts = close_ts_for(payload["symbol"], hit.ts) if hit.ts else None
    return Order(payload["symbol"], payload["timeframe"], hit.direction, hit.title, hit.key, tbr.zone, tbr.day,
                 tbr.high, tbr.low, tbr.mid, hit.price, hit.levels.get("stop"), hit.levels.get("target"),
                 bias_result.bias.value, float(bias_result.score), decision.reason, SESSION_END,
                 hit.ts or None, close_ts)


def build_calendar_order(payload: dict, bias_result, reason: str) -> Order:
    """Orden a partir de un `calendar.signal`: sin TBR ni patrón, con cierre por tiempo."""
    price = payload["price"]
    bias = bias_result.bias.value if bias_result is not None else "sin consultar"
    score = float(bias_result.score) if bias_result is not None else 0.0
    return Order(payload["symbol"], payload["timeframe"], payload["direction"], "Calendario (largo a hora fija)", "calendario",
                 "", payload["day"], price, price, price, price, payload["stop"], payload["target"], bias, score, reason,
                 payload["close_at"], payload["entry_ts"], payload["close_ts"])
