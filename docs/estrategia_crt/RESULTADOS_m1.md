# Backtest: CRT (variante B) en NAS100, H3 → M15/M30/H1 → M1

Script: `scripts/backtest_crt.py`. Solo lee velas M1, M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están en la cabecera del script y en `GUIA.md`; se fijaron antes de ver los resultados.

- **Se da por buena (cada combinación LTF × entrada) si:** (1) NAS100 de PUPrime, todo el histórico: ≥ 100 operaciones y R neto > +0.05 con t > 2.0; (2) R neto positivo en los dos periodos (1.ª mitad (hasta 2025-06); 2.ª mitad (desde 2025-06)); (3) R neto > 0 en el control (NAS100 (USTEC) de MetaQuotes).
- Son 3 combinaciones, así que algún t alto por azar es esperable: se mira la consistencia, no un solo número.

## Veredicto

| Combinación | NAS100 de PUPrime | (1) | 1.ª mitad (hasta 2025-06) / 2.ª mitad (desde 2025-06) | (2) | Control: NAS100 (USTEC) de MetaQuotes | (3) | Resultado |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 892 ops, -0.015 R, t -0.38 | **no** | -0.021 R, t -0.38 / -0.009 R, t -0.17 | **no** | -0.018 R, t -0.44 | **no** | No pasa |
| M1 · 2. retesteo del iFVG | 693 ops, -0.028 R, t -0.63 | **no** | +0.009 R, t +0.14 / -0.062 R, t -1.03 | **no** | -0.064 R, t -1.41 | **no** | No pasa |
| M1 · 3. primera vela sin mecha | 723 ops, -0.077 R, t -1.79 | **no** | -0.076 R, t -1.26 / -0.077 R, t -1.27 | **no** | -0.098 R, t -2.22 | **no** | No pasa |
| M1 · 4. cierre del CISD | 894 ops, -0.008 R, t -0.21 | **no** | -0.016 R, t -0.29 / -0.000 R, t -0.01 | **no** | -0.023 R, t -0.57 | **no** | No pasa |

**0 de 3 combinaciones pasan.**

## Datos

- NAS100.s (puprime) M1: 999999 velas, 2024-01-04 → 2026-10-30 (NY).
- NAS100.s (puprime) M5: 573135 velas, 2018-09-10 → 2026-10-30 (NY).
- USTEC (metaquotes) M1: 999999 velas, 2023-10-30 → 2026-10-30 (NY).
- USTEC (metaquotes) M5: 292870 velas, 2022-07-06 → 2026-10-30 (NY).

## Embudo (cuántos pasos pasan)

| Mercado | velas HTF con sweep | con FVG de MTF formado tras el extremo | con vuelta al FVG | con iFVG | con CISD | setups finales |
|---|---:|---:|---:|---:|---:|---:|
| NAS100.s (puprime) M1 | 5472 | 2086 | 1115 | 1104 | 959 | 959 |
| USTEC (metaquotes) M1 | 5277 | 1995 | 1097 | 1055 | 906 | 906 |

## Resultados en NAS100 de PUPrime (R neto, con spread)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 892 | 31.4 % | -0.015 | -13.2 | 0.97 | -39.0 | -0.38 |
|   1.ª mitad (hasta 2025-06) | 432 | 31.0 % | -0.021 | -9.1 | 0.96 | -26.8 | -0.38 |
|   2.ª mitad (desde 2025-06) | 460 | 31.7 % | -0.009 | -4.1 | 0.98 | -29.2 | -0.17 |
|   sin costes (R bruto) | 892 | 31.5 % | +0.035 | +31.6 | 1.08 | -25.6 | +0.91 |
|   largos | 459 | 33.8 % | -0.019 | -8.8 | 0.96 | -24.5 | -0.35 |
|   cortos | 433 | 28.9 % | -0.010 | -4.4 | 0.98 | -20.1 | -0.18 |
| M1 · 2. retesteo del iFVG | 693 | 30.9 % | -0.028 | -19.4 | 0.94 | -39.6 | -0.63 |
|   1.ª mitad (hasta 2025-06) | 330 | 30.9 % | +0.009 | +3.1 | 1.02 | -24.6 | +0.14 |
|   2.ª mitad (desde 2025-06) | 363 | 30.9 % | -0.062 | -22.4 | 0.88 | -31.0 | -1.03 |
|   sin costes (R bruto) | 693 | 31.7 % | +0.026 | +18.0 | 1.06 | -27.5 | +0.59 |
|   largos | 353 | 32.3 % | -0.030 | -10.6 | 0.94 | -21.1 | -0.49 |
|   cortos | 340 | 29.4 % | -0.026 | -8.7 | 0.95 | -33.4 | -0.40 |
| M1 · 3. primera vela sin mecha | 723 | 28.9 % | -0.077 | -55.3 | 0.85 | -59.2 | -1.79 |
|   1.ª mitad (hasta 2025-06) | 359 | 28.1 % | -0.076 | -27.2 | 0.85 | -32.0 | -1.26 |
|   2.ª mitad (desde 2025-06) | 364 | 29.7 % | -0.077 | -28.2 | 0.85 | -37.7 | -1.27 |
|   sin costes (R bruto) | 723 | 28.9 % | -0.023 | -16.5 | 0.95 | -29.2 | -0.53 |
|   largos | 369 | 31.4 % | -0.048 | -17.6 | 0.91 | -23.8 | -0.78 |
|   cortos | 354 | 26.3 % | -0.107 | -37.8 | 0.79 | -39.6 | -1.78 |
| M1 · 4. cierre del CISD | 894 | 31.7 % | -0.008 | -7.2 | 0.98 | -35.0 | -0.21 |
|   1.ª mitad (hasta 2025-06) | 433 | 31.2 % | -0.016 | -7.0 | 0.97 | -25.9 | -0.29 |
|   2.ª mitad (desde 2025-06) | 461 | 32.1 % | -0.000 | -0.2 | 1.00 | -27.2 | -0.01 |
|   sin costes (R bruto) | 894 | 31.9 % | +0.042 | +37.6 | 1.09 | -22.5 | +1.08 |
|   largos | 460 | 33.7 % | -0.021 | -9.9 | 0.96 | -25.5 | -0.39 |
|   cortos | 434 | 29.5 % | +0.006 | +2.7 | 1.01 | -17.2 | +0.11 |

## Control: NAS100 (USTEC) de MetaQuotes

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 837 | 30.1 % | -0.018 | -14.8 | 0.96 | -37.8 | -0.44 |
|   1.ª mitad (hasta 2025-06) | 424 | 30.2 % | -0.010 | -4.1 | 0.98 | -26.6 | -0.17 |
|   2.ª mitad (desde 2025-06) | 413 | 30.0 % | -0.026 | -10.6 | 0.95 | -30.2 | -0.45 |
| M1 · 2. retesteo del iFVG | 641 | 27.0 % | -0.064 | -41.3 | 0.87 | -45.1 | -1.41 |
|   1.ª mitad (hasta 2025-06) | 324 | 28.4 % | -0.025 | -8.0 | 0.95 | -31.0 | -0.38 |
|   2.ª mitad (desde 2025-06) | 317 | 25.6 % | -0.105 | -33.3 | 0.79 | -41.1 | -1.67 |
| M1 · 3. primera vela sin mecha | 654 | 27.5 % | -0.098 | -64.1 | 0.81 | -71.6 | -2.22 |
|   1.ª mitad (hasta 2025-06) | 352 | 28.1 % | -0.060 | -21.0 | 0.88 | -30.1 | -0.99 |
|   2.ª mitad (desde 2025-06) | 302 | 26.8 % | -0.143 | -43.1 | 0.74 | -47.1 | -2.20 |
| M1 · 4. cierre del CISD | 840 | 29.9 % | -0.023 | -19.3 | 0.95 | -42.2 | -0.57 |
|   1.ª mitad (hasta 2025-06) | 425 | 30.4 % | -0.005 | -2.3 | 0.99 | -27.2 | -0.10 |
|   2.ª mitad (desde 2025-06) | 415 | 29.4 % | -0.041 | -17.0 | 0.92 | -36.6 | -0.72 |

## Cómo terminan y riesgo (NAS100 de PUPrime)

| Combinación | Cierres | Riesgo mediano (pts) | p10 | p90 | Coste medio (R) | Coste > 0,2 R |
|---|---:|---:|---:|---:|---:|---:|
| M1 · 1 | stop 384, objetivo 193, BE 169, sesión 146 | 50.1 | 17.9 | 130.7 | 0.050 | 2 % |
| M1 · 2 | stop 309, objetivo 151, BE 135, sesión 98 | 46.2 | 16.8 | 125.0 | 0.054 | 2 % |
| M1 · 3 | stop 335, objetivo 146, BE 127, sesión 115 | 48.2 | 16.3 | 139.9 | 0.054 | 1 % |
| M1 · 4 | stop 384, objetivo 196, BE 166, sesión 148 | 50.3 | 17.9 | 130.5 | 0.050 | 2 % |

## Por año (NAS100 de PUPrime)

**M1 · 1. vela siguiente al CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 289 | 32.2 % | -0.004 | -1.2 | 0.99 | -25.9 | -0.06 |
| 2025 | 318 | 28.3 % | -0.072 | -23.1 | 0.86 | -39.0 | -1.13 |
| 2026 | 285 | 34.0 % | +0.039 | +11.0 | 1.08 | -13.8 | +0.55 |

**M1 · 2. retesteo del iFVG**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 213 | 32.9 % | +0.040 | +8.6 | 1.08 | -21.2 | +0.49 |
| 2025 | 252 | 27.0 % | -0.096 | -24.2 | 0.81 | -38.1 | -1.35 |
| 2026 | 228 | 33.3 % | -0.017 | -3.8 | 0.97 | -15.0 | -0.22 |

**M1 · 3. primera vela sin mecha**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 240 | 29.2 % | -0.061 | -14.6 | 0.88 | -24.8 | -0.82 |
| 2025 | 263 | 28.5 % | -0.084 | -22.1 | 0.84 | -35.0 | -1.18 |
| 2026 | 220 | 29.1 % | -0.085 | -18.6 | 0.84 | -33.8 | -1.09 |

**M1 · 4. cierre del CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 290 | 32.1 % | -0.004 | -1.2 | 0.99 | -25.9 | -0.06 |
| 2025 | 319 | 28.8 % | -0.060 | -19.0 | 0.88 | -35.0 | -0.93 |
| 2026 | 285 | 34.4 % | +0.046 | +13.0 | 1.10 | -11.8 | +0.65 |

## Sensibilidad (no cuenta para el veredicto)

Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 1 | 571 | 36.3 % | +0.129 | +73.8 | 1.32 | -15.3 | +2.65 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 2 | 427 | 36.1 % | +0.129 | +55.1 | 1.32 | -11.4 | +2.29 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 3 | 474 | 31.4 % | +0.005 | +2.6 | 1.01 | -18.1 | +0.10 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 4 | 573 | 36.6 % | +0.139 | +79.7 | 1.35 | -15.3 | +2.85 |
| sin BE: M1 · 1 | 871 | 39.0 % | +0.001 | +1.0 | 1.00 | -38.4 | +0.03 |
| sin BE: M1 · 2 | 683 | 36.9 % | -0.058 | -39.7 | 0.91 | -62.2 | -1.17 |
| sin BE: M1 · 3 | 714 | 35.3 % | -0.069 | -49.1 | 0.89 | -54.0 | -1.42 |
| sin BE: M1 · 4 | 873 | 38.9 % | +0.006 | +5.5 | 1.01 | -35.4 | +0.14 |
| objetivo 3R: M1 · 1 | 873 | 25.7 % | +0.007 | +6.0 | 1.01 | -41.6 | +0.15 |
| objetivo 3R: M1 · 2 | 692 | 25.4 % | +0.013 | +8.8 | 1.03 | -32.8 | +0.25 |
| objetivo 3R: M1 · 3 | 712 | 22.8 % | -0.074 | -52.9 | 0.86 | -70.5 | -1.53 |
| objetivo 3R: M1 · 4 | 875 | 25.4 % | +0.000 | +0.0 | 1.00 | -41.6 | +0.00 |
