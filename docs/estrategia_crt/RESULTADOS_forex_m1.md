# Backtest: CRT (variante B) en EURUSD y GBPUSD, H4 → M15/M30/H1 → M1

**Forex:** velas H4 alineadas a las 17:00 NY, sin entradas a las 17:00 NY y lo abierto se cierra (el corte del día FX; las 18:00 eran el cierre de los índices). Mismas reglas que en NAS100 para FVG, iFVG, CISD, entradas y gestión.

Script: `scripts/backtest_crt.py`. Solo lee velas M1, M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están en la cabecera del script y en `GUIA.md`; se fijaron antes de ver los resultados.

- **Se da por buena (cada combinación LTF × entrada) si:** (1) EURUSD de PUPrime, todo el histórico: ≥ 100 operaciones y R neto > +0.05 con t > 2.0; (2) R neto positivo en los dos periodos (1.ª mitad (hasta 2025-06); 2.ª mitad (desde 2025-06)); (3) R neto > 0 en el control (GBPUSD de PUPrime).
- Son 3 combinaciones, así que algún t alto por azar es esperable: se mira la consistencia, no un solo número.

## Veredicto

| Combinación | EURUSD de PUPrime | (1) | 1.ª mitad (hasta 2025-06) / 2.ª mitad (desde 2025-06) | (2) | Control: GBPUSD de PUPrime | (3) | Resultado |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 1070 ops, -0.064 R, t -1.93 | **no** | -0.110 R, t -2.43 / -0.018 R, t -0.36 | **no** | -0.087 R, t -2.72 | **no** | No pasa |
| M1 · 2. retesteo del iFVG | 878 ops, -0.057 R, t -1.52 | **no** | -0.125 R, t -2.43 / +0.010 R, t +0.19 | **no** | -0.069 R, t -1.95 | **no** | No pasa |
| M1 · 3. primera vela sin mecha | 972 ops, -0.086 R, t -2.57 | **no** | -0.128 R, t -2.79 / -0.042 R, t -0.87 | **no** | -0.065 R, t -1.98 | **no** | No pasa |
| M1 · 4. cierre del CISD | 1068 ops, -0.064 R, t -1.93 | **no** | -0.102 R, t -2.25 / -0.025 R, t -0.53 | **no** | -0.088 R, t -2.78 | **no** | No pasa |

**0 de 3 combinaciones pasan.**

## Datos

- EURUSD (puprime) M1: 999999 velas, 2024-02-25 → 2026-10-30 (NY).
- EURUSD (puprime) M5: 999999 velas, 2013-05-30 → 2026-10-30 (NY).
- GBPUSD (puprime) M1: 999999 velas, 2024-02-23 → 2026-10-30 (NY).
- GBPUSD (puprime) M5: 999999 velas, 2013-05-30 → 2026-10-30 (NY).

## Embudo (cuántos pasos pasan)

| Mercado | velas HTF con sweep | con FVG de MTF formado tras el extremo | con vuelta al FVG | con iFVG | con CISD | setups finales |
|---|---:|---:|---:|---:|---:|---:|
| EURUSD (puprime) M1 | 3937 | 2012 | 1376 | 1310 | 1185 | 1185 |
| GBPUSD (puprime) M1 | 3959 | 2082 | 1427 | 1361 | 1257 | 1257 |

## Resultados en EURUSD de PUPrime (R neto, con spread)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 1070 | 30.4 % | -0.064 | -68.3 | 0.86 | -95.8 | -1.93 |
|   1.ª mitad (hasta 2025-06) | 537 | 29.2 % | -0.110 | -58.9 | 0.77 | -70.6 | -2.43 |
|   2.ª mitad (desde 2025-06) | 533 | 31.5 % | -0.018 | -9.4 | 0.96 | -34.1 | -0.36 |
|   sin costes (R bruto) | 1070 | 31.1 % | -0.003 | -2.8 | 0.99 | -45.6 | -0.08 |
|   largos | 528 | 30.3 % | -0.089 | -46.9 | 0.81 | -59.4 | -1.94 |
|   cortos | 542 | 30.4 % | -0.040 | -21.4 | 0.92 | -45.5 | -0.83 |
| M1 · 2. retesteo del iFVG | 878 | 30.8 % | -0.057 | -49.9 | 0.88 | -74.3 | -1.52 |
|   1.ª mitad (hasta 2025-06) | 435 | 29.0 % | -0.125 | -54.4 | 0.75 | -63.8 | -2.43 |
|   2.ª mitad (desde 2025-06) | 443 | 32.5 % | +0.010 | +4.5 | 1.02 | -21.7 | +0.19 |
|   sin costes (R bruto) | 878 | 31.3 % | +0.012 | +10.1 | 1.03 | -26.6 | +0.31 |
|   largos | 440 | 28.9 % | -0.114 | -50.1 | 0.77 | -54.5 | -2.25 |
|   cortos | 438 | 32.6 % | +0.000 | +0.2 | 1.00 | -30.7 | +0.01 |
| M1 · 3. primera vela sin mecha | 972 | 29.4 % | -0.086 | -83.6 | 0.81 | -92.1 | -2.57 |
|   1.ª mitad (hasta 2025-06) | 494 | 28.5 % | -0.128 | -63.4 | 0.73 | -71.7 | -2.79 |
|   2.ª mitad (desde 2025-06) | 478 | 30.3 % | -0.042 | -20.2 | 0.90 | -33.5 | -0.87 |
|   sin costes (R bruto) | 972 | 30.0 % | -0.023 | -22.5 | 0.94 | -40.9 | -0.69 |
|   largos | 486 | 28.6 % | -0.133 | -64.8 | 0.72 | -70.8 | -2.93 |
|   cortos | 486 | 30.2 % | -0.039 | -18.7 | 0.91 | -46.7 | -0.79 |
| M1 · 4. cierre del CISD | 1068 | 30.3 % | -0.064 | -68.1 | 0.86 | -91.3 | -1.93 |
|   1.ª mitad (hasta 2025-06) | 537 | 29.6 % | -0.102 | -54.5 | 0.78 | -66.1 | -2.25 |
|   2.ª mitad (desde 2025-06) | 531 | 31.1 % | -0.025 | -13.5 | 0.95 | -34.0 | -0.53 |
|   sin costes (R bruto) | 1068 | 31.3 % | -0.002 | -2.4 | 0.99 | -41.0 | -0.07 |
|   largos | 526 | 30.2 % | -0.090 | -47.4 | 0.81 | -59.8 | -1.96 |
|   cortos | 542 | 30.4 % | -0.038 | -20.7 | 0.92 | -43.4 | -0.80 |

## Control: GBPUSD de PUPrime

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 1143 | 31.3 % | -0.087 | -99.1 | 0.82 | -99.7 | -2.72 |
|   1.ª mitad (hasta 2025-06) | 556 | 33.8 % | -0.057 | -31.9 | 0.88 | -37.5 | -1.25 |
|   2.ª mitad (desde 2025-06) | 587 | 29.0 % | -0.114 | -67.2 | 0.77 | -70.5 | -2.60 |
| M1 · 2. retesteo del iFVG | 938 | 31.0 % | -0.069 | -64.4 | 0.85 | -75.3 | -1.95 |
|   1.ª mitad (hasta 2025-06) | 451 | 35.5 % | -0.003 | -1.5 | 0.99 | -24.7 | -0.06 |
|   2.ª mitad (desde 2025-06) | 487 | 26.9 % | -0.129 | -62.9 | 0.74 | -68.9 | -2.71 |
| M1 · 3. primera vela sin mecha | 1051 | 32.4 % | -0.065 | -68.8 | 0.86 | -72.7 | -1.98 |
|   1.ª mitad (hasta 2025-06) | 506 | 37.0 % | -0.023 | -11.7 | 0.95 | -32.5 | -0.48 |
|   2.ª mitad (desde 2025-06) | 545 | 28.1 % | -0.105 | -57.1 | 0.78 | -66.3 | -2.34 |
| M1 · 4. cierre del CISD | 1144 | 31.2 % | -0.088 | -100.9 | 0.82 | -101.4 | -2.78 |
|   1.ª mitad (hasta 2025-06) | 556 | 34.0 % | -0.054 | -30.0 | 0.88 | -37.5 | -1.17 |
|   2.ª mitad (desde 2025-06) | 588 | 28.6 % | -0.121 | -70.9 | 0.75 | -74.5 | -2.76 |

## Cómo terminan y riesgo (EURUSD de PUPrime)

| Combinación | Cierres | Riesgo mediano (pips) | p10 | p90 | Coste medio (R) | Coste > 0,2 R |
|---|---:|---:|---:|---:|---:|---:|
| M1 · 1 | stop 419, sesión 258, BE 210, objetivo 183 | 10.1 | 4.2 | 23.8 | 0.061 | 5 % |
| M1 · 2 | stop 351, sesión 196, BE 170, objetivo 161 | 9.5 | 3.9 | 22.7 | 0.068 | 6 % |
| M1 · 3 | stop 371, sesión 250, BE 204, objetivo 146, fin de datos 1 | 10.5 | 4.2 | 24.6 | 0.063 | 6 % |
| M1 · 4 | stop 419, sesión 258, BE 210, objetivo 181 | 10.1 | 4.2 | 23.8 | 0.061 | 5 % |

## Por año (EURUSD de PUPrime)

**M1 · 1. vela siguiente al CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 338 | 30.8 % | -0.135 | -45.6 | 0.73 | -56.5 | -2.38 |
| 2025 | 401 | 27.4 % | -0.110 | -44.2 | 0.77 | -45.2 | -2.09 |
| 2026 | 331 | 33.5 % | +0.065 | +21.5 | 1.15 | -20.8 | +1.04 |

**M1 · 2. retesteo del iFVG**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 268 | 30.2 % | -0.153 | -41.0 | 0.70 | -50.1 | -2.36 |
| 2025 | 343 | 28.9 % | -0.083 | -28.5 | 0.83 | -30.1 | -1.39 |
| 2026 | 267 | 33.7 % | +0.073 | +19.6 | 1.17 | -12.8 | +1.05 |

**M1 · 3. primera vela sin mecha**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 312 | 28.8 % | -0.160 | -50.1 | 0.67 | -52.8 | -2.85 |
| 2025 | 372 | 29.0 % | -0.097 | -36.2 | 0.80 | -39.6 | -1.77 |
| 2026 | 288 | 30.6 % | +0.010 | +2.7 | 1.02 | -17.1 | +0.15 |

**M1 · 4. cierre del CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 338 | 31.4 % | -0.125 | -42.2 | 0.75 | -53.1 | -2.20 |
| 2025 | 401 | 27.2 % | -0.108 | -43.2 | 0.78 | -44.2 | -2.04 |
| 2026 | 329 | 33.1 % | +0.053 | +17.4 | 1.12 | -20.8 | +0.84 |

## Sensibilidad (no cuenta para el veredicto)

Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 1 | 642 | 36.4 % | +0.095 | +60.7 | 1.25 | -16.6 | +2.19 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 2 | 518 | 36.5 % | +0.104 | +54.1 | 1.27 | -15.4 | +2.14 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 3 | 594 | 34.7 % | +0.059 | +34.9 | 1.16 | -14.4 | +1.36 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 4 | 641 | 36.2 % | +0.090 | +57.5 | 1.24 | -15.0 | +2.08 |
| sin BE: M1 · 1 | 1042 | 36.9 % | -0.077 | -79.8 | 0.87 | -123.5 | -2.02 |
| sin BE: M1 · 2 | 861 | 37.4 % | -0.075 | -64.3 | 0.87 | -93.1 | -1.77 |
| sin BE: M1 · 3 | 952 | 37.1 % | -0.080 | -76.2 | 0.86 | -110.8 | -2.05 |
| sin BE: M1 · 4 | 1041 | 36.6 % | -0.082 | -85.5 | 0.86 | -125.2 | -2.18 |
| objetivo 3R: M1 · 1 | 1042 | 25.8 % | -0.059 | -61.5 | 0.87 | -93.5 | -1.57 |
| objetivo 3R: M1 · 2 | 869 | 24.5 % | -0.091 | -79.3 | 0.81 | -111.3 | -2.24 |
| objetivo 3R: M1 · 3 | 957 | 26.2 % | -0.061 | -58.1 | 0.87 | -75.6 | -1.57 |
| objetivo 3R: M1 · 4 | 1041 | 25.9 % | -0.054 | -55.9 | 0.89 | -86.0 | -1.43 |
