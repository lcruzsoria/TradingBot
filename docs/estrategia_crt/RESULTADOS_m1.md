# Backtest: CRT (variante B) en NAS100, H3 → M15/M30/H1 → M1

Script: `scripts/backtest_crt.py`. Solo lee velas M1, M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están en la cabecera del script y en `GUIA.md`; se fijaron antes de ver los resultados.

- **Se da por buena (cada combinación LTF × entrada) si:** (1) NAS100 de PUPrime, todo el histórico: ≥ 100 operaciones y R neto > +0.05 con t > 2.0; (2) R neto positivo en los dos periodos (1.ª mitad (hasta 2025-06); 2.ª mitad (desde 2025-06)); (3) R neto > 0 en el control (NAS100 (USTEC) de MetaQuotes).
- Son 3 combinaciones, así que algún t alto por azar es esperable: se mira la consistencia, no un solo número.

## Veredicto

| Combinación | NAS100 de PUPrime | (1) | 1.ª mitad (hasta 2025-06) / 2.ª mitad (desde 2025-06) | (2) | Control: NAS100 (USTEC) de MetaQuotes | (3) | Resultado |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 804 ops, -0.030 R, t -0.72 | **no** | -0.007 R, t -0.11 / -0.051 R, t -0.90 | **no** | -0.018 R, t -0.42 | **no** | No pasa |
| M1 · 2. retesteo del iFVG | 611 ops, -0.031 R, t -0.66 | **no** | +0.041 R, t +0.57 / -0.096 R, t -1.49 | **no** | -0.082 R, t -1.73 | **no** | No pasa |
| M1 · 3. primera vela sin mecha | 644 ops, -0.081 R, t -1.79 | **no** | -0.093 R, t -1.47 / -0.070 R, t -1.08 | **no** | -0.114 R, t -2.44 | **no** | No pasa |
| M1 · 4. cierre del CISD | 805 ops, -0.021 R, t -0.52 | **no** | -0.006 R, t -0.11 / -0.035 R, t -0.62 | **no** | -0.025 R, t -0.59 | **no** | No pasa |

**0 de 3 combinaciones pasan.**

## Datos

- NAS100.s (puprime) M1: 999999 velas, 2024-01-04 → 2026-10-30 (NY).
- NAS100.s (puprime) M5: 573135 velas, 2018-09-10 → 2026-10-30 (NY).
- USTEC (metaquotes) M1: 999999 velas, 2023-10-30 → 2026-10-30 (NY).
- USTEC (metaquotes) M5: 292870 velas, 2022-07-06 → 2026-10-30 (NY).

## Embudo (cuántos pasos pasan)

| Mercado | velas HTF con sweep | con FVG de MTF formado tras el extremo | con vuelta al FVG | con iFVG | con CISD | invalidados | setups finales |
|---|---:|---:|---:|---:|---:|---:|---:|
| NAS100.s (puprime) M1 | 4688 | 1448 | 1070 | 988 | 855 | 707 | 855 |
| USTEC (metaquotes) M1 | 4546 | 1428 | 1052 | 938 | 805 | 656 | 805 |

## Invalidados

Un setup queda **invalidado** si el precio llega al extremo opuesto de C1 (el objetivo) antes de encontrar el FVG de MTF, la vuelta a él o el iFVG invertido. No se opera; se anota por qué. Detalle en `analisis/backtest_crt_*_invalidados.csv`.

| Mercado | Invalidados | sin FVG de MTF | sin vuelta al FVG de MTF | sin iFVG invertido |
|---|---:|---:|---:|---:|
| NAS100.s (puprime) M1 | 707 | 561 | 128 | 18 |
| USTEC (metaquotes) M1 | 656 | 495 | 136 | 25 |

## Resultados en NAS100 de PUPrime (R neto, con spread)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 804 | 30.8 % | -0.030 | -23.8 | 0.94 | -49.4 | -0.72 |
|   1.ª mitad (hasta 2025-06) | 389 | 31.6 % | -0.007 | -2.6 | 0.99 | -28.0 | -0.11 |
|   2.ª mitad (desde 2025-06) | 415 | 30.1 % | -0.051 | -21.2 | 0.90 | -30.2 | -0.90 |
|   sin costes (R bruto) | 804 | 30.8 % | +0.023 | +18.2 | 1.05 | -37.8 | +0.55 |
|   largos | 397 | 33.8 % | -0.024 | -9.4 | 0.95 | -26.8 | -0.40 |
|   cortos | 407 | 28.0 % | -0.035 | -14.4 | 0.93 | -32.8 | -0.62 |
| M1 · 2. retesteo del iFVG | 611 | 31.3 % | -0.031 | -19.2 | 0.94 | -52.5 | -0.66 |
|   1.ª mitad (hasta 2025-06) | 289 | 31.8 % | +0.041 | +11.7 | 1.09 | -21.7 | +0.57 |
|   2.ª mitad (desde 2025-06) | 322 | 30.7 % | -0.096 | -30.9 | 0.82 | -36.3 | -1.49 |
|   sin costes (R bruto) | 611 | 32.1 % | +0.025 | +15.3 | 1.05 | -36.1 | +0.52 |
|   largos | 303 | 32.3 % | -0.020 | -6.0 | 0.96 | -23.4 | -0.29 |
|   cortos | 308 | 30.2 % | -0.043 | -13.2 | 0.92 | -38.9 | -0.63 |
| M1 · 3. primera vela sin mecha | 644 | 29.0 % | -0.081 | -52.3 | 0.84 | -56.0 | -1.79 |
|   1.ª mitad (hasta 2025-06) | 316 | 27.5 % | -0.093 | -29.3 | 0.81 | -30.0 | -1.47 |
|   2.ª mitad (desde 2025-06) | 328 | 30.5 % | -0.070 | -22.9 | 0.87 | -30.3 | -1.08 |
|   sin costes (R bruto) | 644 | 29.0 % | -0.026 | -16.4 | 0.95 | -27.9 | -0.56 |
|   largos | 319 | 31.3 % | -0.059 | -18.7 | 0.89 | -25.1 | -0.89 |
|   cortos | 325 | 26.8 % | -0.103 | -33.6 | 0.80 | -37.4 | -1.66 |
| M1 · 4. cierre del CISD | 805 | 31.3 % | -0.021 | -17.2 | 0.96 | -46.9 | -0.52 |
|   1.ª mitad (hasta 2025-06) | 389 | 31.6 % | -0.006 | -2.5 | 0.99 | -27.9 | -0.11 |
|   2.ª mitad (desde 2025-06) | 416 | 31.0 % | -0.035 | -14.7 | 0.93 | -27.8 | -0.62 |
|   sin costes (R bruto) | 805 | 31.4 % | +0.031 | +24.7 | 1.07 | -35.3 | +0.75 |
|   largos | 398 | 33.9 % | -0.025 | -10.0 | 0.95 | -26.3 | -0.42 |
|   cortos | 407 | 28.7 % | -0.018 | -7.2 | 0.96 | -28.8 | -0.31 |

## Control: NAS100 (USTEC) de MetaQuotes

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 754 | 29.7 % | -0.018 | -13.4 | 0.96 | -37.3 | -0.42 |
|   1.ª mitad (hasta 2025-06) | 383 | 30.3 % | +0.009 | +3.6 | 1.02 | -24.0 | +0.16 |
|   2.ª mitad (desde 2025-06) | 371 | 29.1 % | -0.046 | -17.0 | 0.91 | -24.2 | -0.76 |
| M1 · 2. retesteo del iFVG | 577 | 26.5 % | -0.082 | -47.6 | 0.84 | -51.4 | -1.73 |
|   1.ª mitad (hasta 2025-06) | 286 | 25.9 % | -0.065 | -18.6 | 0.87 | -29.1 | -0.95 |
|   2.ª mitad (desde 2025-06) | 291 | 27.1 % | -0.100 | -29.0 | 0.81 | -34.8 | -1.49 |
| M1 · 3. primera vela sin mecha | 586 | 27.0 % | -0.114 | -66.7 | 0.78 | -68.7 | -2.44 |
|   1.ª mitad (hasta 2025-06) | 310 | 27.1 % | -0.081 | -25.1 | 0.83 | -27.2 | -1.27 |
|   2.ª mitad (desde 2025-06) | 276 | 26.8 % | -0.150 | -41.5 | 0.73 | -43.5 | -2.20 |
| M1 · 4. cierre del CISD | 756 | 29.4 % | -0.025 | -19.0 | 0.95 | -43.4 | -0.59 |
|   1.ª mitad (hasta 2025-06) | 383 | 30.3 % | +0.011 | +4.3 | 1.02 | -23.0 | +0.19 |
|   2.ª mitad (desde 2025-06) | 373 | 28.4 % | -0.063 | -23.3 | 0.88 | -30.3 | -1.04 |

## Cómo terminan y riesgo (NAS100 de PUPrime)

| Combinación | Cierres | Riesgo mediano (pts) | p10 | p90 | Coste medio (R) | Coste > 0,2 R |
|---|---:|---:|---:|---:|---:|---:|
| M1 · 1 | stop 354, objetivo 175, BE 149, sesión 126 | 47.2 | 17.5 | 127.7 | 0.052 | 2 % |
| M1 · 2 | stop 278, objetivo 136, BE 108, sesión 89 | 44.5 | 15.6 | 121.6 | 0.056 | 2 % |
| M1 · 3 | stop 298, objetivo 131, BE 115, sesión 100 | 47.5 | 16.1 | 133.1 | 0.056 | 2 % |
| M1 · 4 | stop 354, objetivo 178, BE 145, sesión 128 | 47.5 | 17.2 | 128.1 | 0.052 | 2 % |

## Por año (NAS100 de PUPrime)

**M1 · 1. vela siguiente al CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 257 | 33.9 % | +0.033 | +8.5 | 1.07 | -18.1 | +0.45 |
| 2025 | 290 | 26.9 % | -0.110 | -31.8 | 0.79 | -49.4 | -1.64 |
| 2026 | 257 | 32.3 % | -0.002 | -0.5 | 1.00 | -11.4 | -0.02 |

**M1 · 2. retesteo del iFVG**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 185 | 35.7 % | +0.112 | +20.7 | 1.24 | -15.8 | +1.23 |
| 2025 | 228 | 26.3 % | -0.138 | -31.4 | 0.74 | -45.1 | -1.84 |
| 2026 | 198 | 32.8 % | -0.043 | -8.5 | 0.92 | -12.6 | -0.51 |

**M1 · 3. primera vela sin mecha**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 207 | 27.5 % | -0.106 | -21.9 | 0.79 | -26.5 | -1.36 |
| 2025 | 239 | 29.7 % | -0.060 | -14.3 | 0.88 | -33.9 | -0.79 |
| 2026 | 198 | 29.8 % | -0.081 | -16.0 | 0.85 | -27.0 | -0.98 |

**M1 · 4. cierre del CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 257 | 33.9 % | +0.033 | +8.5 | 1.07 | -18.2 | +0.45 |
| 2025 | 291 | 27.5 % | -0.101 | -29.3 | 0.81 | -46.9 | -1.50 |
| 2026 | 257 | 33.1 % | +0.014 | +3.6 | 1.03 | -11.4 | +0.19 |

## Sensibilidad (no cuenta para el veredicto)

Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 1 | 513 | 35.7 % | +0.121 | +62.0 | 1.30 | -11.5 | +2.34 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 2 | 382 | 36.9 % | +0.131 | +49.9 | 1.31 | -12.7 | +2.14 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 3 | 427 | 30.9 % | -0.003 | -1.5 | 0.99 | -20.0 | -0.06 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 4 | 514 | 36.4 % | +0.133 | +68.5 | 1.33 | -11.5 | +2.57 |
| sin BE: M1 · 1 | 789 | 37.4 % | -0.037 | -28.8 | 0.94 | -51.2 | -0.79 |
| sin BE: M1 · 2 | 604 | 35.8 % | -0.082 | -49.7 | 0.87 | -73.7 | -1.57 |
| sin BE: M1 · 3 | 637 | 35.2 % | -0.080 | -50.7 | 0.87 | -52.7 | -1.56 |
| sin BE: M1 · 4 | 790 | 37.2 % | -0.035 | -27.3 | 0.94 | -50.3 | -0.75 |
| objetivo 3R: M1 · 1 | 789 | 25.0 % | -0.015 | -11.6 | 0.97 | -53.7 | -0.31 |
| objetivo 3R: M1 · 2 | 612 | 25.8 % | +0.007 | +4.2 | 1.01 | -44.2 | +0.12 |
| objetivo 3R: M1 · 3 | 636 | 22.2 % | -0.105 | -66.7 | 0.80 | -77.5 | -2.07 |
| objetivo 3R: M1 · 4 | 790 | 25.1 % | -0.016 | -12.3 | 0.97 | -53.6 | -0.33 |
