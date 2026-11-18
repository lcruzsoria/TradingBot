# Backtest Barrido RTH (desde 2026-11-01)

Velas M5 de PUPrime-Demo: NAS100.s 2024-01-10..2026-11-05, SP500.s 2024-01-10..2026-11-05, DJ30.s 2024-01-10..2026-11-05.
Reglas: rotura 10:00-11:00 NY, entrada hasta 12:00, stop fijo 30 puntos (swing + 5 si queda más lejos), TP1 en el lado contrario del RTH, breakeven al tomar el Low/High de NY Open.
Cuenta simulada: 10,000 USD, riesgo 1 % por operación (sobre el saldo en que se consolida).

| Mercado | Operaciones | TP1 | SL | BE | Tiempo | Acierto | R medio | R total |
|---|---|---|---|---|---|---|---|---|
| NAS100.s | 3 | 1 | 0 | 2 | 0 | 33 % | +0.40 | +1.19 |
| SP500.s | 3 | 0 | 0 | 2 | 1 | 0 % | -0.11 | -0.34 |
| DJ30.s | 3 | 1 | 1 | 0 | 1 | 67 % | +1.45 | +4.35 |
| **Total** | 9 | 2 | 1 | 4 | 2 | 33 % | +0.58 | +5.20 |

**Saldo final 10,524.82 USD** (+524.82 USD, +5.25 %), drawdown máximo 1.00 %.

## Por mes

| Mes | Operaciones | R total | PnL (USD) |
|---|---|---|---|
| 2026-11 | 9 | +5.20 | +524.82 |

## Operaciones

| Día NY | Mercado | Lado | Entrada | Stop | TP1 | BE | Resultado | R | PnL (USD) | Saldo |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-02 | DJ30.s | corto | 52391.20 | 52483.20 | 52119.20 | 52271.20 | objetivo | +2.96 | +299.18 | 10,418.54 |
| 2026-11-02 | NAS100.s | corto | 28664.30 | 28780.55 | 28525.55 | 28549.05 | objetivo | +1.19 | +119.35 | 10,119.35 |
| 2026-11-02 | SP500.s | corto | 7636.00 | 7675.00 | 7618.25 | 7630.25 | breakeven | -0.00 | -0.00 | 10,000.00 |
| 2026-11-03 | DJ30.s | corto | 51876.20 | 51942.20 | 51621.20 | 51655.55 | tiempo | +2.39 | +248.09 | 10,631.14 |
| 2026-11-03 | NAS100.s | corto | 28259.40 | 28335.02 | 28103.65 | 28135.40 | breakeven | -0.00 | -0.00 | 10,418.54 |
| 2026-11-03 | SP500.s | corto | 7574.26 | 7604.26 | 7546.26 | 7559.01 | tiempo | -0.34 | -35.49 | 10,383.04 |
| 2026-11-04 | SP500.s | corto | 7708.21 | 7738.21 | 7654.46 | 7699.46 | breakeven | -0.00 | -0.00 | 10,524.82 |
| 2026-11-04 | NAS100.s | corto | 28689.05 | 28862.05 | 28248.80 | 28674.05 | breakeven | -0.00 | -0.00 | 10,631.14 |
| 2026-11-04 | DJ30.s | corto | 53080.23 | 53227.23 | 52817.58 | 52836.23 | stop | -1.00 | -106.31 | 10,524.82 |
