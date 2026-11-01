# Backtest: CRT (variante B) en NAS100, H3 → M15/M30/H1 → M1

Script: `scripts/backtest_crt.py`. Solo lee velas M1, M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están en la cabecera del script y en `GUIA.md`; se fijaron antes de ver los resultados.

- **Se da por buena (cada combinación LTF × entrada) si:** (1) NAS100 de PUPrime, todo el histórico: ≥ 100 operaciones y R neto > +0.05 con t > 2.0; (2) R neto positivo en los dos periodos (1.ª mitad (hasta 2025-06); 2.ª mitad (desde 2025-06)); (3) R neto > 0 en el control (NAS100 (USTEC) de MetaQuotes).
- Son 3 combinaciones, así que algún t alto por azar es esperable: se mira la consistencia, no un solo número.

## Veredicto

| Combinación | NAS100 de PUPrime | (1) | 1.ª mitad (hasta 2025-06) / 2.ª mitad (desde 2025-06) | (2) | Control: NAS100 (USTEC) de MetaQuotes | (3) | Resultado |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 837 ops, -0.024 R, t -0.60 | **no** | -0.007 R, t -0.13 / -0.040 R, t -0.71 | **no** | -0.019 R, t -0.45 | **no** | No pasa |
| M1 · 2. retesteo del iFVG | 635 ops, -0.022 R, t -0.47 | **no** | +0.037 R, t +0.54 / -0.077 R, t -1.20 | **no** | -0.080 R, t -1.70 | **no** | No pasa |
| M1 · 3. primera vela sin mecha | 668 ops, -0.071 R, t -1.58 | **no** | -0.092 R, t -1.49 / -0.050 R, t -0.77 | **no** | -0.101 R, t -2.17 | **no** | No pasa |
| M1 · 4. cierre del CISD | 838 ops, -0.016 R, t -0.40 | **no** | -0.007 R, t -0.13 / -0.025 R, t -0.44 | **no** | -0.026 R, t -0.62 | **no** | No pasa |

**0 de 3 combinaciones pasan.**

## Datos

- NAS100.s (puprime) M1: 999999 velas, 2024-01-04 → 2026-10-30 (NY).
- NAS100.s (puprime) M5: 573135 velas, 2018-09-10 → 2026-10-30 (NY).
- USTEC (metaquotes) M1: 999999 velas, 2023-10-30 → 2026-10-30 (NY).
- USTEC (metaquotes) M5: 292870 velas, 2022-07-06 → 2026-10-30 (NY).

## Embudo (cuántos pasos pasan)

| Mercado | velas HTF con sweep | con FVG de MTF formado tras el extremo | con vuelta al FVG | con iFVG | con CISD | setups finales |
|---|---:|---:|---:|---:|---:|---:|
| NAS100.s (puprime) M1 | 5472 | 2086 | 1115 | 1027 | 889 | 889 |
| USTEC (metaquotes) M1 | 5277 | 1995 | 1097 | 980 | 840 | 840 |

## Resultados en NAS100 de PUPrime (R neto, con spread)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 837 | 30.8 % | -0.024 | -20.1 | 0.95 | -44.4 | -0.60 |
|   1.ª mitad (hasta 2025-06) | 408 | 31.4 % | -0.007 | -3.0 | 0.98 | -29.5 | -0.13 |
|   2.ª mitad (desde 2025-06) | 429 | 30.3 % | -0.040 | -17.1 | 0.92 | -28.3 | -0.71 |
|   sin costes (R bruto) | 837 | 30.8 % | +0.028 | +23.4 | 1.06 | -32.4 | +0.70 |
|   largos | 418 | 33.7 % | -0.012 | -5.1 | 0.98 | -23.5 | -0.21 |
|   cortos | 419 | 27.9 % | -0.036 | -15.0 | 0.93 | -30.2 | -0.63 |
| M1 · 2. retesteo del iFVG | 635 | 31.5 % | -0.022 | -14.2 | 0.96 | -46.2 | -0.47 |
|   1.ª mitad (hasta 2025-06) | 302 | 31.8 % | +0.037 | +11.3 | 1.08 | -22.8 | +0.54 |
|   2.ª mitad (desde 2025-06) | 333 | 31.2 % | -0.077 | -25.5 | 0.85 | -32.8 | -1.20 |
|   sin costes (R bruto) | 635 | 32.3 % | +0.033 | +21.1 | 1.07 | -30.2 | +0.71 |
|   largos | 316 | 32.9 % | -0.001 | -0.5 | 1.00 | -19.7 | -0.02 |
|   cortos | 319 | 30.1 % | -0.043 | -13.7 | 0.92 | -36.3 | -0.65 |
| M1 · 3. primera vela sin mecha | 668 | 29.3 % | -0.071 | -47.3 | 0.86 | -51.0 | -1.58 |
|   1.ª mitad (hasta 2025-06) | 331 | 27.8 % | -0.092 | -30.6 | 0.82 | -33.3 | -1.49 |
|   2.ª mitad (desde 2025-06) | 337 | 30.9 % | -0.050 | -16.7 | 0.91 | -26.8 | -0.77 |
|   sin costes (R bruto) | 668 | 29.3 % | -0.016 | -10.5 | 0.97 | -24.3 | -0.35 |
|   largos | 333 | 31.5 % | -0.042 | -14.0 | 0.92 | -21.1 | -0.65 |
|   cortos | 335 | 27.2 % | -0.099 | -33.3 | 0.81 | -37.1 | -1.61 |
| M1 · 4. cierre del CISD | 838 | 31.3 % | -0.016 | -13.5 | 0.97 | -41.9 | -0.40 |
|   1.ª mitad (hasta 2025-06) | 408 | 31.4 % | -0.007 | -3.0 | 0.98 | -29.4 | -0.13 |
|   2.ª mitad (desde 2025-06) | 430 | 31.2 % | -0.025 | -10.6 | 0.95 | -25.9 | -0.44 |
|   sin costes (R bruto) | 838 | 31.4 % | +0.036 | +29.9 | 1.08 | -29.9 | +0.88 |
|   largos | 419 | 33.9 % | -0.014 | -5.7 | 0.97 | -23.0 | -0.24 |
|   cortos | 419 | 28.6 % | -0.019 | -7.8 | 0.96 | -26.0 | -0.33 |

## Control: NAS100 (USTEC) de MetaQuotes

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 787 | 29.6 % | -0.019 | -14.9 | 0.96 | -35.6 | -0.45 |
|   1.ª mitad (hasta 2025-06) | 402 | 29.9 % | -0.001 | -0.4 | 1.00 | -25.5 | -0.02 |
|   2.ª mitad (desde 2025-06) | 385 | 29.4 % | -0.038 | -14.5 | 0.92 | -24.2 | -0.63 |
| M1 · 2. retesteo del iFVG | 599 | 26.7 % | -0.080 | -48.2 | 0.84 | -51.0 | -1.70 |
|   1.ª mitad (hasta 2025-06) | 298 | 25.8 % | -0.070 | -21.0 | 0.86 | -31.3 | -1.05 |
|   2.ª mitad (desde 2025-06) | 301 | 27.6 % | -0.090 | -27.2 | 0.83 | -33.9 | -1.36 |
| M1 · 3. primera vela sin mecha | 605 | 27.3 % | -0.101 | -61.0 | 0.81 | -66.6 | -2.17 |
|   1.ª mitad (hasta 2025-06) | 322 | 27.6 % | -0.063 | -20.4 | 0.87 | -26.7 | -0.99 |
|   2.ª mitad (desde 2025-06) | 283 | 26.9 % | -0.144 | -40.6 | 0.74 | -44.6 | -2.12 |
| M1 · 4. cierre del CISD | 789 | 29.3 % | -0.026 | -20.4 | 0.95 | -42.0 | -0.62 |
|   1.ª mitad (hasta 2025-06) | 402 | 29.9 % | +0.001 | +0.4 | 1.00 | -24.6 | +0.02 |
|   2.ª mitad (desde 2025-06) | 387 | 28.7 % | -0.054 | -20.8 | 0.89 | -30.5 | -0.91 |

## Cómo terminan y riesgo (NAS100 de PUPrime)

| Combinación | Cierres | Riesgo mediano (pts) | p10 | p90 | Coste medio (R) | Coste > 0,2 R |
|---|---:|---:|---:|---:|---:|---:|
| M1 · 1 | stop 367, objetivo 183, BE 158, sesión 129 | 47.8 | 17.5 | 127.5 | 0.052 | 2 % |
| M1 · 2 | stop 289, objetivo 144, BE 112, sesión 90 | 45.5 | 16.1 | 121.6 | 0.056 | 2 % |
| M1 · 3 | stop 309, objetivo 139, BE 119, sesión 101 | 47.9 | 16.5 | 132.7 | 0.055 | 2 % |
| M1 · 4 | stop 367, objetivo 186, BE 154, sesión 131 | 47.7 | 17.2 | 127.8 | 0.052 | 2 % |

## Por año (NAS100 de PUPrime)

**M1 · 1. vela siguiente al CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 271 | 33.2 % | +0.028 | +7.6 | 1.06 | -21.4 | +0.39 |
| 2025 | 301 | 27.6 % | -0.089 | -26.9 | 0.83 | -44.4 | -1.35 |
| 2026 | 265 | 32.1 % | -0.003 | -0.8 | 0.99 | -12.7 | -0.04 |

**M1 · 2. retesteo del iFVG**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 193 | 35.2 % | +0.101 | +19.5 | 1.22 | -17.8 | +1.13 |
| 2025 | 238 | 27.3 % | -0.109 | -26.0 | 0.79 | -39.7 | -1.47 |
| 2026 | 204 | 32.8 % | -0.038 | -7.7 | 0.93 | -14.2 | -0.45 |

**M1 · 3. primera vela sin mecha**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 217 | 27.6 % | -0.104 | -22.5 | 0.80 | -27.3 | -1.36 |
| 2025 | 248 | 30.2 % | -0.047 | -11.6 | 0.91 | -30.7 | -0.63 |
| 2026 | 203 | 30.0 % | -0.065 | -13.2 | 0.87 | -26.8 | -0.79 |

**M1 · 4. cierre del CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 271 | 33.2 % | +0.028 | +7.6 | 1.06 | -21.4 | +0.39 |
| 2025 | 302 | 28.1 % | -0.081 | -24.4 | 0.84 | -41.9 | -1.22 |
| 2026 | 265 | 32.8 % | +0.012 | +3.2 | 1.03 | -12.4 | +0.17 |

## Sensibilidad (no cuenta para el veredicto)

Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 1 | 533 | 35.6 % | +0.127 | +67.8 | 1.32 | -12.7 | +2.51 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 2 | 396 | 37.1 % | +0.142 | +56.3 | 1.34 | -11.6 | +2.37 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 3 | 442 | 31.2 % | +0.010 | +4.5 | 1.02 | -17.5 | +0.18 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 4 | 534 | 36.3 % | +0.139 | +74.3 | 1.35 | -12.7 | +2.73 |
| sin BE: M1 · 1 | 821 | 37.5 % | -0.032 | -26.6 | 0.95 | -45.6 | -0.71 |
| sin BE: M1 · 2 | 627 | 36.2 % | -0.066 | -41.6 | 0.89 | -65.4 | -1.28 |
| sin BE: M1 · 3 | 661 | 35.6 % | -0.066 | -43.8 | 0.89 | -46.5 | -1.31 |
| sin BE: M1 · 4 | 822 | 37.3 % | -0.030 | -25.0 | 0.95 | -45.1 | -0.67 |
| objetivo 3R: M1 · 1 | 822 | 25.1 % | -0.004 | -2.9 | 0.99 | -48.7 | -0.08 |
| objetivo 3R: M1 · 2 | 636 | 26.1 % | +0.021 | +13.1 | 1.04 | -36.7 | +0.37 |
| objetivo 3R: M1 · 3 | 659 | 22.6 % | -0.083 | -54.8 | 0.84 | -65.4 | -1.64 |
| objetivo 3R: M1 · 4 | 823 | 25.2 % | -0.004 | -3.6 | 0.99 | -48.6 | -0.09 |
