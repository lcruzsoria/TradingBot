"""Motor de Bias: ejecuta las reglas activas y decide Bullish / Bearish / No Bias.

Cada regla vota +1, -1 o 0 y tiene un peso (BIAS_<REGLA>_WEIGHT, 1 por defecto). La puntuación del día es la suma de
voto x peso: Bullish si llega a +min_score, Bearish si llega a -min_score y No Bias en otro caso. Así una regla de
estructura (p. ej. la ruptura del día anterior) puede pesar más que una de contexto, y dos señales opuestas de igual
peso se anulan.
"""
from __future__ import annotations

from datetime import date

import pandas as pd

from .context import build_context
from .models import Bias, BiasResult, RuleVote
from .rules import RULE_REGISTRY, BiasRule


class BiasEngine:
    def __init__(self, rules: list[BiasRule], min_score: float = 1, require_all: bool = False):
        self.rules = rules
        self.min_score = max(float(min_score), 1e-9)
        self.require_all = require_all

    @classmethod
    def from_config(cls, cfg: dict) -> "BiasEngine":
        rules: list[BiasRule] = []
        for entry in cfg.get("rules", []):
            if not entry.get("enabled", True):
                continue
            key = entry.get("type")
            if key not in RULE_REGISTRY:
                raise ValueError(f"Regla de Bias desconocida: {key!r}. Disponibles: {', '.join(RULE_REGISTRY)}")
            params = {k: v for k, v in entry.items() if k not in ("type", "enabled")}
            rules.append(RULE_REGISTRY[key](**params))
        return cls(rules, cfg.get("min_score", 1), cfg.get("require_all", False))

    def evaluate(self, candles: pd.DataFrame, day: date | None = None) -> BiasResult:
        ctx = build_context(candles, day)
        if ctx is None or len(ctx.today) == 0:
            return BiasResult(Bias.NO_BIAS, day, summary="Sin velas para evaluar el día")

        votes: list[RuleVote] = []
        for rule in self.rules:
            try:
                votes.append(rule.evaluate(ctx))
            except Exception as exc:  # una regla con error no debe tumbar el resto
                votes.append(RuleVote(rule.title or rule.key, 0, f"Error en la regla: {exc}", rule.weight))

        bias, summary = self._aggregate(votes)
        score = sum(v.points for v in votes)
        levels = {}
        if ctx.prev_high is not None:
            levels["Máx. previo"] = ctx.prev_high
            levels["Mín. previo"] = ctx.prev_low
        if ctx.day_open is not None:
            levels["Apertura"] = ctx.day_open
        return BiasResult(bias, ctx.day, tuple(votes), levels, summary, score, self.min_score)

    def _aggregate(self, votes: list[RuleVote]) -> tuple[Bias, str]:
        if not votes:
            return Bias.NO_BIAS, "No hay reglas activas"
        bulls = sum(v.vote > 0 for v in votes)
        bears = sum(v.vote < 0 for v in votes)
        total = len(votes)
        if self.require_all:
            if bulls == total:
                return Bias.BULLISH, f"{bulls}/{total} reglas alcistas"
            if bears == total:
                return Bias.BEARISH, f"{bears}/{total} reglas bajistas"
            return Bias.NO_BIAS, "Las reglas no coinciden todas"
        score = sum(v.points for v in votes)
        tally = f"puntuación {score:+g} (mínimo {self.min_score:g}): {bulls} alcista(s), {bears} bajista(s)"
        if score >= self.min_score:
            return Bias.BULLISH, tally
        if score <= -self.min_score:
            return Bias.BEARISH, tally
        if bulls and bears:
            return Bias.NO_BIAS, f"Señales opuestas, {tally}"
        return Bias.NO_BIAS, f"Puntuación insuficiente, {tally}"
