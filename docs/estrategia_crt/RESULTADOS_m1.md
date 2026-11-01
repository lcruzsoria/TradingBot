# Backtest: CRT (variante B) en NAS100, H3 → M15/M30/H1 → M1

Script: `scripts/backtest_crt.py`. Solo lee velas M1, M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están en la cabecera del script y en `GUIA.md`; se fijaron antes de ver los resultados.

- **Se da por buena (cada combinación LTF × entrada) si:** (1) NAS100 de PUPrime, todo el histórico: ≥ 100 operaciones y R neto > +0.05 con t > 2.0; (2) R neto positivo en los dos periodos (1.ª mitad (hasta 2025-06); 2.ª mitad (desde 2025-06)); (3) R neto > 0 en el control (NAS100 (USTEC) de MetaQuotes).
- Son 3 combinaciones, así que algún t alto por azar es esperable: se mira la consistencia, no un solo número.

## Veredicto

| Combinación | NAS100 de PUPrime | (1) | 1.ª mitad (hasta 2025-06) / 2.ª mitad (desde 2025-06) | (2) | Control: NAS100 (USTEC) de MetaQuotes | (3) | Resultado |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 790 ops, -0.162 R, t -3.94 | **no** | -0.150 R, t -2.47 / -0.172 R, t -3.10 | **no** | -0.073 R, t -1.68 | **no** | No pasa |
| M1 · 2. retesteo del iFVG | 457 ops, -0.166 R, t -2.99 | **no** | -0.210 R, t -2.62 / -0.126 R, t -1.63 | **no** | -0.061 R, t -1.05 | **no** | No pasa |
| M1 · 3. primera vela sin mecha | 588 ops, -0.137 R, t -2.85 | **no** | -0.069 R, t -0.96 / -0.199 R, t -3.07 | **no** | -0.113 R, t -2.23 | **no** | No pasa |

**0 de 3 combinaciones pasan.**

## Datos

- NAS100.s (puprime) M1: 999999 velas, 2024-01-04 → 2026-10-30 (NY).
- NAS100.s (puprime) M5: 573135 velas, 2018-09-10 → 2026-10-30 (NY).
- USTEC (metaquotes) M1: 999999 velas, 2023-10-30 → 2026-10-30 (NY).
- USTEC (metaquotes) M5: 292870 velas, 2022-07-06 → 2026-10-30 (NY).

## Embudo (cuántos pasos pasan)

| Mercado | velas HTF con sweep | con FVG de MTF sin mitigar al alcance | con el extremo tocando el FVG | con iFVG | con CISD | setups finales |
|---|---:|---:|---:|---:|---:|---:|
| NAS100.s (puprime) M1 | 5472 | 1680 | 1404 | 908 | 799 | 799 |
| USTEC (metaquotes) M1 | 5277 | 1578 | 1314 | 841 | 723 | 723 |

## Resultados en NAS100 de PUPrime (R neto, con spread)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 790 | 23.4 % | -0.162 | -127.9 | 0.72 | -131.1 | -3.94 |
|   1.ª mitad (hasta 2025-06) | 370 | 24.1 % | -0.150 | -55.6 | 0.74 | -63.7 | -2.47 |
|   2.ª mitad (desde 2025-06) | 420 | 22.9 % | -0.172 | -72.3 | 0.69 | -78.6 | -3.10 |
|   sin costes (R bruto) | 790 | 23.7 % | -0.066 | -52.4 | 0.87 | -66.3 | -1.62 |
|   largos | 383 | 24.5 % | -0.117 | -44.9 | 0.78 | -54.2 | -1.99 |
|   cortos | 407 | 22.4 % | -0.204 | -83.0 | 0.66 | -84.6 | -3.57 |
| M1 · 2. retesteo del iFVG | 457 | 24.9 % | -0.166 | -76.0 | 0.72 | -80.9 | -2.99 |
|   1.ª mitad (hasta 2025-06) | 219 | 23.7 % | -0.210 | -45.9 | 0.66 | -58.3 | -2.62 |
|   2.ª mitad (desde 2025-06) | 238 | 26.1 % | -0.126 | -30.1 | 0.78 | -43.4 | -1.63 |
|   sin costes (R bruto) | 457 | 25.2 % | -0.026 | -11.9 | 0.95 | -36.4 | -0.47 |
|   largos | 224 | 29.5 % | -0.066 | -14.7 | 0.89 | -31.8 | -0.77 |
|   cortos | 233 | 20.6 % | -0.263 | -61.3 | 0.56 | -62.7 | -3.66 |
| M1 · 3. primera vela sin mecha | 588 | 26.9 % | -0.137 | -80.6 | 0.76 | -82.9 | -2.85 |
|   1.ª mitad (hasta 2025-06) | 279 | 30.1 % | -0.069 | -19.2 | 0.87 | -35.3 | -0.96 |
|   2.ª mitad (desde 2025-06) | 309 | 23.9 % | -0.199 | -61.4 | 0.66 | -74.5 | -3.07 |
|   sin costes (R bruto) | 588 | 26.9 % | -0.051 | -30.2 | 0.90 | -54.7 | -1.07 |
|   largos | 287 | 30.0 % | -0.086 | -24.7 | 0.84 | -27.5 | -1.23 |
|   cortos | 301 | 23.9 % | -0.186 | -55.9 | 0.68 | -62.0 | -2.79 |

## Control: NAS100 (USTEC) de MetaQuotes

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 715 | 25.0 % | -0.073 | -52.5 | 0.86 | -71.7 | -1.68 |
|   1.ª mitad (hasta 2025-06) | 355 | 28.2 % | -0.013 | -4.5 | 0.97 | -26.6 | -0.20 |
|   2.ª mitad (desde 2025-06) | 360 | 21.9 % | -0.133 | -48.0 | 0.75 | -56.6 | -2.24 |
| M1 · 2. retesteo del iFVG | 420 | 26.2 % | -0.061 | -25.7 | 0.88 | -35.5 | -1.05 |
|   1.ª mitad (hasta 2025-06) | 214 | 29.0 % | +0.010 | +2.1 | 1.02 | -19.8 | +0.12 |
|   2.ª mitad (desde 2025-06) | 206 | 23.3 % | -0.135 | -27.9 | 0.75 | -31.4 | -1.68 |
| M1 · 3. primera vela sin mecha | 500 | 25.2 % | -0.113 | -56.7 | 0.78 | -70.1 | -2.23 |
|   1.ª mitad (hasta 2025-06) | 257 | 28.0 % | -0.049 | -12.7 | 0.90 | -24.5 | -0.67 |
|   2.ª mitad (desde 2025-06) | 243 | 22.2 % | -0.181 | -44.0 | 0.66 | -49.8 | -2.60 |

## Cómo terminan y riesgo (NAS100 de PUPrime)

| Combinación | Cierres | Riesgo mediano (pts) | p10 | p90 | Coste medio (R) | Coste > 0,2 R |
|---|---:|---:|---:|---:|---:|---:|
| M1 · 1 | stop 384, BE 196, objetivo 162, sesión 48 | 25.2 | 9.2 | 73.2 | 0.096 | 9 % |
| M1 · 2 | stop 223, BE 112, objetivo 104, sesión 18 | 17.5 | 6.5 | 54.2 | 0.140 | 21 % |
| M1 · 3 | stop 286, objetivo 121, BE 120, sesión 61 | 30.0 | 9.5 | 97.7 | 0.086 | 8 % |

## Por año (NAS100 de PUPrime)

**M1 · 1. vela siguiente al CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 262 | 22.9 % | -0.187 | -49.0 | 0.69 | -49.5 | -2.60 |
| 2025 | 283 | 23.7 % | -0.125 | -35.5 | 0.76 | -37.1 | -1.85 |
| 2026 | 245 | 23.7 % | -0.177 | -43.4 | 0.69 | -46.6 | -2.40 |

**M1 · 2. retesteo del iFVG**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 150 | 20.0 % | -0.323 | -48.4 | 0.51 | -51.2 | -3.55 |
| 2025 | 166 | 30.7 % | +0.010 | +1.7 | 1.02 | -13.8 | +0.10 |
| 2026 | 141 | 23.4 % | -0.207 | -29.3 | 0.65 | -31.4 | -2.15 |

**M1 · 3. primera vela sin mecha**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 194 | 26.8 % | -0.156 | -30.2 | 0.73 | -35.3 | -1.87 |
| 2025 | 218 | 32.1 % | +0.001 | +0.2 | 1.00 | -24.6 | +0.01 |
| 2026 | 176 | 20.5 % | -0.287 | -50.6 | 0.53 | -50.6 | -3.54 |

## Sensibilidad (no cuenta para el veredicto)

Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M1 · 1 | 804 | 23.4 % | -0.165 | -132.3 | 0.71 | -135.4 | -4.04 |
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M1 · 2 | 468 | 24.4 % | -0.184 | -86.3 | 0.70 | -91.2 | -3.36 |
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M1 · 3 | 598 | 26.6 % | -0.146 | -87.6 | 0.74 | -89.9 | -3.08 |
| antigüedad del FVG 3 días: M1 · 1 | 661 | 23.1 % | -0.157 | -103.6 | 0.72 | -107.4 | -3.48 |
| antigüedad del FVG 3 días: M1 · 2 | 388 | 25.8 % | -0.139 | -54.1 | 0.76 | -56.8 | -2.28 |
| antigüedad del FVG 3 días: M1 · 3 | 500 | 26.6 % | -0.136 | -67.8 | 0.76 | -67.8 | -2.57 |
| antigüedad del FVG 30 días: M1 · 1 | 848 | 23.1 % | -0.167 | -141.5 | 0.71 | -144.7 | -4.23 |
| antigüedad del FVG 30 días: M1 · 2 | 493 | 24.9 % | -0.165 | -81.4 | 0.72 | -87.2 | -3.08 |
| antigüedad del FVG 30 días: M1 · 3 | 622 | 27.0 % | -0.130 | -80.8 | 0.77 | -83.1 | -2.77 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 1 | 1479 | 26.4 % | -0.116 | -170.9 | 0.80 | -190.7 | -3.68 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 2 | 876 | 24.7 % | -0.182 | -159.6 | 0.70 | -167.1 | -4.48 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 3 | 1077 | 26.9 % | -0.111 | -119.2 | 0.80 | -136.4 | -3.10 |
| CISD con cierre dentro de C1 (la versión anterior): M1 · 1 | 447 | 25.1 % | -0.106 | -47.3 | 0.80 | -47.8 | -1.92 |
| CISD con cierre dentro de C1 (la versión anterior): M1 · 2 | 176 | 21.6 % | -0.219 | -38.5 | 0.64 | -39.6 | -2.48 |
| CISD con cierre dentro de C1 (la versión anterior): M1 · 3 | 375 | 28.3 % | -0.113 | -42.2 | 0.79 | -49.0 | -1.89 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 1 | 223 | 40.4 % | +0.369 | +82.2 | 2.01 | -9.6 | +4.31 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 2 | 113 | 37.2 % | +0.249 | +28.1 | 1.56 | -7.0 | +2.00 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 3 | 183 | 43.7 % | +0.327 | +59.9 | 1.86 | -6.8 | +3.51 |
| sin BE: M1 · 1 | 789 | 32.7 % | -0.150 | -118.2 | 0.79 | -121.0 | -3.13 |
| sin BE: M1 · 2 | 457 | 32.6 % | -0.186 | -85.1 | 0.75 | -90.0 | -2.91 |
| sin BE: M1 · 3 | 587 | 34.1 % | -0.142 | -83.3 | 0.79 | -85.6 | -2.61 |
| objetivo 3R: M1 · 1 | 783 | 16.9 % | -0.170 | -133.4 | 0.70 | -133.4 | -3.65 |
| objetivo 3R: M1 · 2 | 518 | 14.7 % | -0.264 | -136.9 | 0.57 | -145.9 | -4.78 |
| objetivo 3R: M1 · 3 | 583 | 19.4 % | -0.188 | -109.5 | 0.67 | -110.8 | -3.60 |
