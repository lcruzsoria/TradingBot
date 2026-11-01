# Backtest: CRT (variante B) en EURUSD y GBPUSD, H4 → M15/M30/H1 → M1

**Forex:** velas H4 alineadas a las 17:00 NY, sin entradas a las 17:00 NY y lo abierto se cierra (el corte del día FX; las 18:00 eran el cierre de los índices). Mismas reglas que en NAS100 para FVG, iFVG, CISD, entradas y gestión.

Script: `scripts/backtest_crt.py`. Solo lee velas M1, M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están en la cabecera del script y en `GUIA.md`; se fijaron antes de ver los resultados.

- **Se da por buena (cada combinación LTF × entrada) si:** (1) EURUSD de PUPrime, todo el histórico: ≥ 100 operaciones y R neto > +0.05 con t > 2.0; (2) R neto positivo en los dos periodos (1.ª mitad (hasta 2025-06); 2.ª mitad (desde 2025-06)); (3) R neto > 0 en el control (GBPUSD de PUPrime).
- Son 3 combinaciones, así que algún t alto por azar es esperable: se mira la consistencia, no un solo número.

## Veredicto

| Combinación | EURUSD de PUPrime | (1) | 1.ª mitad (hasta 2025-06) / 2.ª mitad (desde 2025-06) | (2) | Control: GBPUSD de PUPrime | (3) | Resultado |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 1031 ops, -0.060 R, t -1.77 | **no** | -0.113 R, t -2.44 / -0.007 R, t -0.14 | **no** | -0.085 R, t -2.63 | **no** | No pasa |
| M1 · 2. retesteo del iFVG | 846 ops, -0.054 R, t -1.42 | **no** | -0.126 R, t -2.39 / +0.017 R, t +0.30 | **no** | -0.065 R, t -1.81 | **no** | No pasa |
| M1 · 3. primera vela sin mecha | 939 ops, -0.084 R, t -2.47 | **no** | -0.129 R, t -2.76 / -0.038 R, t -0.77 | **no** | -0.055 R, t -1.63 | **no** | No pasa |
| M1 · 4. cierre del CISD | 1029 ops, -0.060 R, t -1.77 | **no** | -0.104 R, t -2.26 / -0.015 R, t -0.30 | **no** | -0.085 R, t -2.63 | **no** | No pasa |

**0 de 3 combinaciones pasan.**

## Datos

- EURUSD (puprime) M1: 999999 velas, 2024-02-25 → 2026-10-30 (NY).
- EURUSD (puprime) M5: 999999 velas, 2013-05-30 → 2026-10-30 (NY).
- GBPUSD (puprime) M1: 999999 velas, 2024-02-23 → 2026-10-30 (NY).
- GBPUSD (puprime) M5: 999999 velas, 2013-05-30 → 2026-10-30 (NY).

## Embudo (cuántos pasos pasan)

| Mercado | velas HTF con sweep | con FVG de MTF formado tras el extremo | con vuelta al FVG | con iFVG | con CISD | invalidados | setups finales |
|---|---:|---:|---:|---:|---:|---:|---:|
| EURUSD (puprime) M1 | 3343 | 1611 | 1309 | 1249 | 1135 | 450 | 1135 |
| GBPUSD (puprime) M1 | 3375 | 1671 | 1367 | 1307 | 1212 | 449 | 1212 |

## Invalidados

Un setup queda **invalidado** si el precio llega al extremo opuesto de C1 (el objetivo) antes de encontrar el FVG de MTF, la vuelta a él o el iFVG invertido. No se opera; se anota por qué. Detalle en `analisis/backtest_crt_*_invalidados.csv`.

| Mercado | Invalidados | sin FVG de MTF | sin vuelta al FVG de MTF | sin iFVG invertido |
|---|---:|---:|---:|---:|
| EURUSD (puprime) M1 | 450 | 288 | 140 | 22 |
| GBPUSD (puprime) M1 | 449 | 271 | 156 | 22 |

## Resultados en EURUSD de PUPrime (R neto, con spread)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 1031 | 30.4 % | -0.060 | -61.9 | 0.87 | -89.6 | -1.77 |
|   1.ª mitad (hasta 2025-06) | 518 | 29.0 % | -0.113 | -58.5 | 0.76 | -67.2 | -2.44 |
|   2.ª mitad (desde 2025-06) | 513 | 31.8 % | -0.007 | -3.4 | 0.99 | -29.2 | -0.14 |
|   sin costes (R bruto) | 1031 | 31.0 % | +0.001 | +1.2 | 1.00 | -43.2 | +0.03 |
|   largos | 518 | 30.5 % | -0.081 | -42.0 | 0.83 | -53.4 | -1.74 |
|   cortos | 513 | 30.2 % | -0.039 | -19.9 | 0.92 | -44.1 | -0.79 |
| M1 · 2. retesteo del iFVG | 846 | 30.5 % | -0.054 | -46.0 | 0.89 | -73.9 | -1.42 |
|   1.ª mitad (hasta 2025-06) | 422 | 28.4 % | -0.126 | -53.1 | 0.75 | -61.5 | -2.39 |
|   2.ª mitad (desde 2025-06) | 424 | 32.5 % | +0.017 | +7.1 | 1.04 | -22.1 | +0.30 |
|   sin costes (R bruto) | 846 | 31.1 % | +0.014 | +11.7 | 1.03 | -25.9 | +0.36 |
|   largos | 430 | 29.1 % | -0.102 | -43.8 | 0.79 | -49.2 | -1.98 |
|   cortos | 416 | 32.0 % | -0.005 | -2.2 | 0.99 | -29.7 | -0.09 |
| M1 · 3. primera vela sin mecha | 939 | 29.2 % | -0.084 | -79.1 | 0.82 | -88.3 | -2.47 |
|   1.ª mitad (hasta 2025-06) | 477 | 28.1 % | -0.129 | -61.4 | 0.73 | -69.1 | -2.76 |
|   2.ª mitad (desde 2025-06) | 462 | 30.3 % | -0.038 | -17.7 | 0.91 | -31.6 | -0.77 |
|   sin costes (R bruto) | 939 | 29.8 % | -0.021 | -20.1 | 0.95 | -39.6 | -0.63 |
|   largos | 480 | 28.7 % | -0.130 | -62.2 | 0.72 | -68.9 | -2.82 |
|   cortos | 459 | 29.6 % | -0.037 | -16.9 | 0.92 | -44.8 | -0.73 |
| M1 · 4. cierre del CISD | 1029 | 30.3 % | -0.060 | -61.7 | 0.87 | -85.1 | -1.77 |
|   1.ª mitad (hasta 2025-06) | 518 | 29.3 % | -0.104 | -54.1 | 0.78 | -62.8 | -2.26 |
|   2.ª mitad (desde 2025-06) | 511 | 31.3 % | -0.015 | -7.6 | 0.97 | -29.2 | -0.30 |
|   sin costes (R bruto) | 1029 | 31.2 % | +0.001 | +1.5 | 1.00 | -38.6 | +0.04 |
|   largos | 516 | 30.4 % | -0.082 | -42.5 | 0.82 | -53.8 | -1.76 |
|   cortos | 513 | 30.2 % | -0.037 | -19.2 | 0.92 | -41.9 | -0.76 |

## Control: GBPUSD de PUPrime

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 1101 | 31.5 % | -0.085 | -93.7 | 0.82 | -94.3 | -2.63 |
|   1.ª mitad (hasta 2025-06) | 538 | 34.4 % | -0.046 | -25.0 | 0.90 | -37.6 | -0.99 |
|   2.ª mitad (desde 2025-06) | 563 | 28.8 % | -0.122 | -68.8 | 0.75 | -72.1 | -2.74 |
| M1 · 2. retesteo del iFVG | 906 | 31.3 % | -0.065 | -58.7 | 0.86 | -70.3 | -1.81 |
|   1.ª mitad (hasta 2025-06) | 437 | 35.9 % | +0.002 | +1.0 | 1.01 | -27.5 | +0.04 |
|   2.ª mitad (desde 2025-06) | 469 | 27.1 % | -0.127 | -59.7 | 0.74 | -65.7 | -2.61 |
| M1 · 3. primera vela sin mecha | 1023 | 33.0 % | -0.055 | -56.2 | 0.88 | -64.6 | -1.63 |
|   1.ª mitad (hasta 2025-06) | 493 | 37.7 % | -0.010 | -5.1 | 0.98 | -33.3 | -0.21 |
|   2.ª mitad (desde 2025-06) | 530 | 28.7 % | -0.097 | -51.2 | 0.79 | -62.3 | -2.10 |
| M1 · 4. cierre del CISD | 1102 | 31.5 % | -0.085 | -93.5 | 0.82 | -94.1 | -2.63 |
|   1.ª mitad (hasta 2025-06) | 538 | 34.6 % | -0.043 | -23.0 | 0.91 | -37.6 | -0.91 |
|   2.ª mitad (desde 2025-06) | 564 | 28.5 % | -0.125 | -70.5 | 0.74 | -74.1 | -2.82 |

## Cómo terminan y riesgo (EURUSD de PUPrime)

| Combinación | Cierres | Riesgo mediano (pips) | p10 | p90 | Coste medio (R) | Coste > 0,2 R |
|---|---:|---:|---:|---:|---:|---:|
| M1 · 1 | stop 403, sesión 247, BE 201, objetivo 180 | 10.0 | 4.2 | 23.8 | 0.061 | 5 % |
| M1 · 2 | stop 336, sesión 187, BE 166, objetivo 157 | 9.4 | 3.9 | 22.7 | 0.068 | 6 % |
| M1 · 3 | stop 356, sesión 240, BE 200, objetivo 142, fin de datos 1 | 10.5 | 4.2 | 24.6 | 0.063 | 5 % |
| M1 · 4 | stop 403, sesión 247, BE 201, objetivo 178 | 10.0 | 4.2 | 23.8 | 0.061 | 5 % |

## Por año (EURUSD de PUPrime)

**M1 · 1. vela siguiente al CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 327 | 30.6 % | -0.137 | -44.8 | 0.73 | -55.1 | -2.36 |
| 2025 | 378 | 27.5 % | -0.104 | -39.5 | 0.78 | -40.0 | -1.90 |
| 2026 | 326 | 33.4 % | +0.068 | +22.3 | 1.16 | -19.8 | +1.09 |

**M1 · 2. retesteo del iFVG**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 259 | 29.7 % | -0.156 | -40.4 | 0.70 | -50.2 | -2.35 |
| 2025 | 325 | 28.6 % | -0.080 | -26.0 | 0.84 | -30.7 | -1.30 |
| 2026 | 262 | 33.6 % | +0.078 | +20.4 | 1.19 | -12.8 | +1.10 |

**M1 · 3. primera vela sin mecha**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 302 | 29.1 % | -0.148 | -44.8 | 0.69 | -47.1 | -2.57 |
| 2025 | 352 | 28.1 % | -0.108 | -38.1 | 0.78 | -41.2 | -1.92 |
| 2026 | 285 | 30.5 % | +0.013 | +3.7 | 1.03 | -15.1 | +0.21 |

**M1 · 4. cierre del CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 327 | 31.2 % | -0.127 | -41.4 | 0.74 | -51.7 | -2.18 |
| 2025 | 378 | 27.2 % | -0.102 | -38.4 | 0.79 | -38.9 | -1.85 |
| 2026 | 324 | 33.0 % | +0.056 | +18.2 | 1.13 | -19.8 | +0.89 |

## Sensibilidad (no cuenta para el veredicto)

Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 1 | 617 | 37.0 % | +0.105 | +64.6 | 1.28 | -15.9 | +2.37 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 2 | 499 | 37.1 % | +0.121 | +60.4 | 1.32 | -13.3 | +2.42 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 3 | 574 | 35.0 % | +0.071 | +41.0 | 1.19 | -13.6 | +1.63 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 4 | 616 | 36.7 % | +0.100 | +61.4 | 1.26 | -14.3 | +2.26 |
| sin BE: M1 · 1 | 1004 | 37.0 % | -0.066 | -66.7 | 0.89 | -109.2 | -1.71 |
| sin BE: M1 · 2 | 829 | 37.3 % | -0.072 | -59.3 | 0.88 | -89.6 | -1.65 |
| sin BE: M1 · 3 | 917 | 37.1 % | -0.077 | -70.2 | 0.87 | -103.0 | -1.92 |
| sin BE: M1 · 4 | 1003 | 36.7 % | -0.072 | -72.4 | 0.88 | -109.4 | -1.86 |
| objetivo 3R: M1 · 1 | 1003 | 25.7 % | -0.055 | -55.1 | 0.88 | -86.2 | -1.43 |
| objetivo 3R: M1 · 2 | 837 | 24.1 % | -0.091 | -76.4 | 0.81 | -106.7 | -2.20 |
| objetivo 3R: M1 · 3 | 925 | 25.8 % | -0.061 | -56.0 | 0.87 | -72.2 | -1.54 |
| objetivo 3R: M1 · 4 | 1002 | 25.8 % | -0.049 | -49.5 | 0.89 | -78.7 | -1.28 |
