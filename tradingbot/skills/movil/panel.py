"""Panel para el móvil: una página web de solo lectura que sirve el propio bot (sin librerías extra: http.server).

- `/`                    la página (panel.html), instalable en la pantalla de inicio del móvil
- `/api/estado`          el estado en JSON: cuenta, abiertas, cierres, sesgo y decisiones de Cortex
- `/manifest.webmanifest`, `/icon.svg`   para instalarla como app

Lo que se ve sale del disco (abiertas y cuenta virtual de Setup, diario del forwardtest) y de los mensajes del bot que la
skill va guardando (cotizaciones, sesgo, decisiones). No se puede operar ni cambiar nada desde el panel.

Con PANEL_TOKEN puesto (en el fichero de cuentas, fuera del repo), `/api/estado` pide esa clave en la cabecera
`X-Panel-Token`; la página la pregunta una vez y la recuerda en el móvil.
"""
from __future__ import annotations

import hmac
import json
import threading
from collections import deque
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zoneinfo import ZoneInfo

from ...config import profile_dir
from ...clock import trading_day
from ..setup import account, store
from ..stats import journal

NY = ZoneInfo("America/New_York")
PAGE = Path(__file__).with_name("panel.html")
MAX_DECISIONS = 30
MAX_CLOSED = 30
SIDE = {"long": "Largo", "short": "Corto"}
RESULT = {"objetivo": "TP", "stop": "SL", "breakeven": "BE", "tiempo": "T"}
ICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#0b0e14"/>'
        '<path d="M32 9l20 11.5v23L32 55 12 43.5v-23z" fill="none" stroke="#378ADD" stroke-width="4"/>'
        '<path d="M22 38l7-8 6 5 8-11" fill="none" stroke="#26A69A" stroke-width="4" stroke-linecap="round" '
        'stroke-linejoin="round"/></svg>')
MANIFEST = {"name": "TradingBot", "short_name": "TradingBot", "start_url": "/", "display": "standalone",
            "background_color": "#0b0e14", "theme_color": "#0b0e14",
            "icons": [{"src": "/icon.svg", "sizes": "any", "type": "image/svg+xml"}]}


def _day(value) -> str:
    return value.isoformat() if isinstance(value, date) else str(value or "")


def _closed_day(at, fallback: str) -> str:
    """Día de trading (desde el inicio de la TBR de Asia, 20:00 NY) en que se cerró la operación: el diario anota `at`
    con la hora local de este equipo (sin zona). Es el día que cuenta para «hoy»."""
    try:
        return trading_day(datetime.fromisoformat(str(at)).astimezone(NY)).isoformat()
    except (TypeError, ValueError):
        return fallback


def _r_now(order, price: float | None) -> float | None:
    if price is None or order.stop is None:
        return None
    risk = abs(order.price - order.stop)
    if risk <= 0:
        return None
    sign = 1.0 if order.direction == "long" else -1.0
    return round(sign * (price - order.price) / risk, 2)


class PanelState:
    """Lo que el panel enseña y no está en disco: cotizaciones, cuenta del broker, sesgo y decisiones de Cortex."""

    def __init__(self, app_cfg: dict, stats_dir: str | None = None, now=None) -> None:
        self.app_cfg = app_cfg
        self.stats_dir = stats_dir
        self._now = now or (lambda: datetime.now(NY))
        self._lock = threading.Lock()
        self.prices: dict[str, float] = {}
        self.account: dict | None = None
        self.bias: dict[str, dict] = {}
        self.decisions: deque = deque(maxlen=MAX_DECISIONS)

    # -- lo que llega por el bus -------------------------------------------------------------------
    def quotes(self, payload: dict) -> None:
        with self._lock:
            for symbol, q in (payload.get("quotes") or {}).items():
                if q is not None:
                    self.prices[symbol] = float(q.bid)
            acc = payload.get("account")
            if acc is not None:
                self.account = {"balance": acc.balance, "equity": acc.equity, "profit": acc.profit, "currency": acc.currency}

    def bias_updated(self, payload: dict) -> None:
        result = payload.get("result")
        if result is None or not payload.get("symbol"):
            return
        with self._lock:
            self.bias[payload["symbol"]] = {"symbol": payload["symbol"], "timeframe": payload.get("timeframe", ""),
                                            "bias": getattr(result.bias, "value", str(result.bias)),
                                            "score": float(getattr(result, "score", 0.0)),
                                            "lateral": bool(getattr(result, "lateral", False))}

    def decision(self, payload: dict) -> None:
        hit, tbr, dec = payload["hit"], payload.get("tbr"), payload["decision"]
        with self._lock:
            self.decisions.appendleft({"at": self._now().strftime("%H:%M"), "symbol": payload["symbol"],
                                       "timeframe": payload.get("timeframe", ""), "side": SIDE.get(hit.direction, hit.direction),
                                       "pattern": getattr(hit, "title", ""), "zone": getattr(tbr, "zone", "") or "",
                                       "go": bool(dec.allowed), "reason": dec.reason})

    # -- la foto para el móvil ---------------------------------------------------------------------
    def snapshot(self, profile: str | None = None) -> dict:
        """La foto del panel. Con `profile` (otra cuenta, p. ej. «metaquotes») lee de su carpeta las abiertas, la cuenta
        virtual y el diario del forwardtest; el sesgo, las decisiones y la cuenta del broker son solo los de esta ejecución."""
        app = self.app_cfg.get("app") or {}
        cfg = self.app_cfg
        other = bool(profile) and profile.lower() != (app.get("profile_name") or "").lower()
        if other:
            cfg = {**self.app_cfg, "app": {**app, "data_dir": str(profile_dir(profile)), "profile_name": profile.lower()}}
        with self._lock:
            prices = dict(self.prices)
            out = {"profile": (cfg.get("app") or {}).get("profile_name") or "", "updated": self._now().strftime("%d/%m %H:%M:%S"),
                   "broker": None if other else self.account,
                   "bias": [] if other else sorted(self.bias.values(), key=lambda b: b["symbol"]),
                   "decisions": [] if other else list(self.decisions)}
        out["open"] = [self._open(o, prices.get(o.symbol)) for o in store.load(store.file_for(cfg))]
        virtual = account.VirtualAccount(account.file_for(cfg))
        out["virtual"] = ({"balance": round(virtual.balance, 2), "currency": virtual.currency, "since": virtual.since}
                          if virtual.started else None)
        closed = self._closed(cfg)
        today = trading_day(self._now()).isoformat()
        day = [c for c in closed if c["closed_day"] == today]
        out["today"] = {"day": today, "count": len(day), "r": round(sum(c["r"] for c in day), 2),
                        **{k: sum(1 for c in day if c["result"] == k) for k in ("TP", "SL", "BE", "T")}}
        out["closed"] = closed[:MAX_CLOSED]
        return out

    @staticmethod
    def _open(order, price: float | None) -> dict:
        return {"symbol": order.symbol, "timeframe": order.timeframe, "side": SIDE.get(order.direction, order.direction),
                "pattern": order.pattern, "zone": order.tbr_zone, "day": _day(order.tbr_day), "entry": order.price,
                "stop": order.stop, "target": order.target, "price": price, "r_now": _r_now(order, price),
                "bias": order.bias, "score": order.score}

    def _closed(self, cfg: dict | None = None) -> list[dict]:
        """Los cierres del diario del forwardtest de este mes y el anterior, del más reciente al más antiguo."""
        folder = journal.folder_for(cfg or self.app_cfg, self.stats_dir)
        month = journal.month_of(self._now())
        rows = []
        for m in (journal.previous_month(month), month):
            path = folder / f"{m}.jsonl"
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            for line in lines:
                try:
                    rec = json.loads(line)
                    if rec.get("t") != "close":
                        continue
                    o, c = rec["order"], rec["closed"]
                    rows.append({"symbol": o["symbol"], "timeframe": o.get("timeframe", ""),
                                 "side": SIDE.get(o["direction"], o["direction"]), "pattern": o.get("pattern", ""),
                                 "zone": o.get("tbr_zone", ""), "day": _day(o.get("tbr_day")),
                                 "closed_day": _closed_day(rec.get("at"), _day(o.get("tbr_day"))),
                                 "result": RESULT.get(c["result"], c["result"]), "r": round(float(c["r"]), 2),
                                 "max_r": None if c.get("max_r") is None else round(float(c["max_r"]), 2),
                                 "exit_ts": int(c.get("exit_ts") or 0)})
                except (ValueError, KeyError, TypeError):
                    continue
        rows.sort(key=lambda r: (r["closed_day"], r["exit_ts"]), reverse=True)
        return rows


class PanelServer:
    """El servidor web del panel, en un hilo aparte (se para con la skill)."""

    def __init__(self, state: PanelState, host: str, port: int, token: str | None = None) -> None:
        self.state, self.token = state, token
        panel = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                path = self.path.split("?", 1)[0]
                if path in ("/", "/index.html"):
                    self._reply(200, PAGE.read_bytes(), "text/html; charset=utf-8")
                elif path == "/manifest.webmanifest":
                    self._reply(200, json.dumps(MANIFEST).encode(), "application/manifest+json")
                elif path == "/icon.svg":
                    self._reply(200, ICON.encode(), "image/svg+xml")
                elif path == "/api/estado":
                    if not panel.allowed(self.headers.get("X-Panel-Token")):
                        self._reply(401, b'{"error": "clave"}', "application/json")
                        return
                    body = json.dumps(panel.state.snapshot(), ensure_ascii=False, default=str).encode("utf-8")
                    self._reply(200, body, "application/json; charset=utf-8")
                else:
                    self._reply(404, b"no existe", "text/plain; charset=utf-8")

            def _reply(self, code: int, body: bytes, kind: str) -> None:
                self.send_response(code)
                self.send_header("Content-Type", kind)
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args) -> None:       # sin ruido en la consola
                pass

        self.httpd = ThreadingHTTPServer((host, port), Handler)
        self.httpd.daemon_threads = True
        self.thread = threading.Thread(target=self.httpd.serve_forever, name="panel-movil", daemon=True)

    @property
    def port(self) -> int:
        return self.httpd.server_address[1]

    def allowed(self, given: str | None) -> bool:
        return not self.token or (given is not None and hmac.compare_digest(given, self.token))

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
