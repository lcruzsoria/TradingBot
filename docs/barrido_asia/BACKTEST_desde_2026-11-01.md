# Backtest Barrido de Asia (desde 2026-11-01)

Velas M5 de PUPrime-Demo: NAS100.s 2024-01-10..2026-11-05, SP500.s 2024-01-10..2026-11-05, DJ30.s 2024-01-10..2026-11-05.
Reglas: rotura 00:00-01:00 NY, entrada hasta 01:00, stop fijo 30 puntos (swing + 5 si queda más lejos), objetivo en el lado contrario de Asia, sin breakeven.
Cuenta simulada: 10,000 USD, riesgo 1 % por operación (sobre el saldo en que se consolida).

| Mercado | Operaciones | Objetivo | SL | BE | Tiempo | Acierto | R medio | R total |
|---|---|---|---|---|---|---|---|---|
| NAS100.s | 3 | 1 | 2 | 0 | 0 | 33 % | +0.66 | +1.98 |
| SP500.s | 2 | 2 | 0 | 0 | 0 | 100 % | +0.81 | +1.61 |
| DJ30.s | 1 | 0 | 1 | 0 | 0 | 0 % | -1.00 | -1.00 |
| **Total** | 6 | 3 | 3 | 0 | 0 | 50 % | +0.43 | +2.59 |

**Saldo final 10,252.03 USD** (+252.03 USD, +2.52 %), drawdown máximo 2.25 %.

## Por mes

| Mes | Operaciones | R total | PnL (USD) |
|---|---|---|---|
| 2026-11 | 6 | +2.59 | +252.03 |

## Operaciones

| Día NY | Mercado | Lado | Entrada | Stop | Objetivo | Resultado | R | PnL (USD) | Saldo |
|---|---|---|---|---|---|---|---|---|---|
| 2026-11-01 | NAS100.s | corto | 28695.00 | 28725.00 | 28575.75 | objetivo | +3.98 | +397.50 | 10,397.50 |
| 2026-11-02 | NAS100.s | largo | 28005.40 | 27975.40 | 28155.40 | stop | -1.00 | -103.98 | 10,293.52 |
| 2026-11-02 | DJ30.s | largo | 51846.20 | 51816.20 | 52039.20 | stop | -1.00 | -102.94 | 10,190.59 |
| 2026-11-02 | SP500.s | largo | 7538.94 | 7508.94 | 7561.19 | objetivo | +0.74 | +75.58 | 10,266.17 |
| 2026-11-03 | NAS100.s | corto | 28049.16 | 28089.80 | 27512.30 | stop | -1.00 | -102.66 | 10,163.51 |
| 2026-11-04 | SP500.s | largo | 7674.43 | 7644.43 | 7700.56 | objetivo | +0.87 | +88.52 | 10,252.03 |
