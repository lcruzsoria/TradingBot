# Backtest: CRT (variante B) en NAS100, H3 → M15/M30/H1 → M1

Script: `scripts/backtest_crt.py`. Solo lee velas M1, M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están en la cabecera del script y en `GUIA.md`; se fijaron antes de ver los resultados.

- **Se da por buena (cada combinación LTF × entrada) si:** (1) NAS100 de PUPrime, todo el histórico: ≥ 100 operaciones y R neto > +0.05 con t > 2.0; (2) R neto positivo en los dos periodos (1.ª mitad (hasta 2025-06); 2.ª mitad (desde 2025-06)); (3) R neto > 0 en el control (NAS100 (USTEC) de MetaQuotes).
- Son 3 combinaciones, así que algún t alto por azar es esperable: se mira la consistencia, no un solo número.

## Veredicto

| Combinación | NAS100 de PUPrime | (1) | 1.ª mitad (hasta 2025-06) / 2.ª mitad (desde 2025-06) | (2) | Control: NAS100 (USTEC) de MetaQuotes | (3) | Resultado |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 460 ops, -0.113 R, t -2.09 | **no** | -0.075 R, t -0.91 / -0.145 R, t -2.03 | **no** | -0.109 R, t -1.94 | **no** | No pasa |
| M1 · 2. retesteo del iFVG | 187 ops, -0.251 R, t -2.95 | **no** | -0.357 R, t -2.90 / -0.169 R, t -1.44 | **no** | -0.140 R, t -1.52 | **no** | No pasa |
| M1 · 3. primera vela sin mecha | 385 ops, -0.126 R, t -2.16 | **no** | -0.023 R, t -0.26 / -0.213 R, t -2.77 | **no** | -0.178 R, t -3.01 | **no** | No pasa |

**0 de 3 combinaciones pasan.**

## Datos

- NAS100.s (puprime) M1: 999999 velas, 2024-01-04 → 2026-10-30 (NY).
- NAS100.s (puprime) M5: 573135 velas, 2018-09-10 → 2026-10-30 (NY).
- USTEC (metaquotes) M1: 999999 velas, 2023-10-30 → 2026-10-30 (NY).
- USTEC (metaquotes) M5: 292870 velas, 2022-07-06 → 2026-10-30 (NY).

## Embudo (cuántos pasos pasan)

| Mercado | velas HTF con sweep | con FVG de MTF sin mitigar al alcance | con el extremo tocando el FVG | con iFVG | con CISD | setups finales |
|---|---:|---:|---:|---:|---:|---:|
| NAS100.s (puprime) M1 | 5472 | 1716 | 1432 | 930 | 472 | 472 |
| USTEC (metaquotes) M1 | 5277 | 1606 | 1332 | 853 | 437 | 437 |

## Resultados en NAS100 de PUPrime (R neto, con spread)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 460 | 25.0 % | -0.113 | -52.0 | 0.79 | -52.5 | -2.09 |
|   1.ª mitad (hasta 2025-06) | 212 | 27.4 % | -0.075 | -16.0 | 0.86 | -27.4 | -0.91 |
|   2.ª mitad (desde 2025-06) | 248 | 23.0 % | -0.145 | -36.0 | 0.73 | -37.8 | -2.03 |
|   sin costes (R bruto) | 460 | 25.0 % | -0.049 | -22.6 | 0.90 | -25.9 | -0.91 |
|   largos | 249 | 24.9 % | -0.142 | -35.3 | 0.74 | -38.6 | -1.97 |
|   cortos | 211 | 25.1 % | -0.079 | -16.7 | 0.85 | -25.4 | -0.96 |
| M1 · 2. retesteo del iFVG | 187 | 20.9 % | -0.251 | -47.0 | 0.61 | -47.0 | -2.95 |
|   1.ª mitad (hasta 2025-06) | 82 | 17.1 % | -0.357 | -29.3 | 0.48 | -35.0 | -2.90 |
|   2.ª mitad (desde 2025-06) | 105 | 23.8 % | -0.169 | -17.7 | 0.72 | -19.9 | -1.44 |
|   sin costes (R bruto) | 187 | 20.9 % | -0.141 | -26.4 | 0.74 | -29.5 | -1.67 |
|   largos | 105 | 22.9 % | -0.210 | -22.1 | 0.67 | -26.3 | -1.76 |
|   cortos | 82 | 18.3 % | -0.304 | -24.9 | 0.52 | -24.9 | -2.51 |
| M1 · 3. primera vela sin mecha | 385 | 27.8 % | -0.126 | -48.6 | 0.77 | -50.1 | -2.16 |
|   1.ª mitad (hasta 2025-06) | 176 | 31.8 % | -0.023 | -4.0 | 0.95 | -23.9 | -0.26 |
|   2.ª mitad (desde 2025-06) | 209 | 24.4 % | -0.213 | -44.6 | 0.63 | -50.1 | -2.77 |
|   sin costes (R bruto) | 385 | 27.8 % | -0.062 | -23.9 | 0.87 | -43.0 | -1.07 |
|   largos | 206 | 27.2 % | -0.166 | -34.2 | 0.69 | -35.4 | -2.19 |
|   cortos | 179 | 28.5 % | -0.081 | -14.4 | 0.85 | -36.1 | -0.89 |

## Control: NAS100 (USTEC) de MetaQuotes

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 422 | 24.9 % | -0.109 | -46.2 | 0.80 | -55.7 | -1.94 |
|   1.ª mitad (hasta 2025-06) | 208 | 28.4 % | -0.046 | -9.5 | 0.91 | -21.8 | -0.55 |
|   2.ª mitad (desde 2025-06) | 214 | 21.5 % | -0.171 | -36.7 | 0.69 | -40.4 | -2.24 |
| M1 · 2. retesteo del iFVG | 171 | 22.8 % | -0.140 | -24.0 | 0.76 | -25.6 | -1.52 |
|   1.ª mitad (hasta 2025-06) | 84 | 23.8 % | -0.128 | -10.8 | 0.78 | -21.3 | -0.95 |
|   2.ª mitad (desde 2025-06) | 87 | 21.8 % | -0.151 | -13.2 | 0.74 | -15.7 | -1.19 |
| M1 · 3. primera vela sin mecha | 337 | 23.7 % | -0.178 | -59.9 | 0.67 | -62.0 | -3.01 |
|   1.ª mitad (hasta 2025-06) | 171 | 25.1 % | -0.167 | -28.6 | 0.69 | -30.9 | -2.00 |
|   2.ª mitad (desde 2025-06) | 166 | 22.3 % | -0.189 | -31.3 | 0.65 | -34.3 | -2.26 |

## Cómo terminan y riesgo (NAS100 de PUPrime)

| Combinación | Cierres | Riesgo mediano (pts) | p10 | p90 | Coste medio (R) | Coste > 0,2 R |
|---|---:|---:|---:|---:|---:|---:|
| M1 · 1 | stop 218, BE 104, objetivo 95, sesión 43 | 37.0 | 13.8 | 105.6 | 0.064 | 2 % |
| M1 · 2 | stop 100, BE 42, objetivo 37, sesión 8 | 21.8 | 8.4 | 71.6 | 0.110 | 13 % |
| M1 · 3 | stop 183, objetivo 74, BE 73, sesión 55 | 40.5 | 15.0 | 141.4 | 0.064 | 4 % |

## Por año (NAS100 de PUPrime)

**M1 · 1. vela siguiente al CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 144 | 26.4 % | -0.147 | -21.1 | 0.75 | -27.4 | -1.46 |
| 2025 | 170 | 26.5 % | -0.061 | -10.3 | 0.88 | -18.9 | -0.68 |
| 2026 | 146 | 21.9 % | -0.141 | -20.6 | 0.74 | -21.1 | -1.50 |

**M1 · 2. retesteo del iFVG**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 55 | 10.9 % | -0.549 | -30.2 | 0.27 | -30.2 | -4.18 |
| 2025 | 63 | 28.6 % | -0.012 | -0.8 | 0.98 | -6.2 | -0.08 |
| 2026 | 69 | 21.7 % | -0.232 | -16.0 | 0.63 | -16.0 | -1.66 |

**M1 · 3. primera vela sin mecha**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 119 | 27.7 % | -0.169 | -20.1 | 0.71 | -23.9 | -1.59 |
| 2025 | 144 | 35.4 % | +0.104 | +14.9 | 1.24 | -9.9 | +1.05 |
| 2026 | 122 | 18.9 % | -0.356 | -43.5 | 0.45 | -44.0 | -3.78 |

## Sensibilidad (no cuenta para el veredicto)

Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| antigüedad del FVG 3 días: M1 · 1 | 409 | 25.4 % | -0.093 | -38.0 | 0.83 | -41.0 | -1.59 |
| antigüedad del FVG 3 días: M1 · 2 | 172 | 22.1 % | -0.226 | -38.9 | 0.64 | -41.0 | -2.49 |
| antigüedad del FVG 3 días: M1 · 3 | 346 | 26.3 % | -0.138 | -47.7 | 0.75 | -49.2 | -2.24 |
| antigüedad del FVG 30 días: M1 · 1 | 480 | 25.4 % | -0.095 | -45.8 | 0.82 | -46.3 | -1.80 |
| antigüedad del FVG 30 días: M1 · 2 | 190 | 21.1 % | -0.237 | -45.1 | 0.62 | -47.0 | -2.80 |
| antigüedad del FVG 30 días: M1 · 3 | 402 | 28.1 % | -0.122 | -49.0 | 0.78 | -50.9 | -2.14 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 1 | 1021 | 25.2 % | -0.129 | -132.0 | 0.77 | -139.8 | -3.51 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 2 | 477 | 22.6 % | -0.233 | -111.0 | 0.63 | -112.4 | -4.33 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 3 | 822 | 26.6 % | -0.115 | -94.7 | 0.78 | -101.3 | -2.89 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 1 | 218 | 33.0 % | +0.192 | +41.8 | 1.51 | -10.6 | +2.38 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 2 | 77 | 20.8 % | -0.140 | -10.8 | 0.74 | -11.8 | -1.07 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 3 | 191 | 34.6 % | +0.083 | +15.8 | 1.19 | -10.9 | +0.98 |
| sin BE: M1 · 1 | 458 | 31.4 % | -0.168 | -76.8 | 0.76 | -76.8 | -2.74 |
| sin BE: M1 · 2 | 187 | 31.0 % | -0.166 | -31.1 | 0.78 | -31.1 | -1.65 |
| sin BE: M1 · 3 | 383 | 33.4 % | -0.150 | -57.3 | 0.78 | -60.0 | -2.27 |
| objetivo 3R: M1 · 1 | 457 | 19.5 % | -0.093 | -42.6 | 0.83 | -45.6 | -1.49 |
| objetivo 3R: M1 · 2 | 226 | 11.5 % | -0.346 | -78.2 | 0.46 | -78.2 | -4.38 |
| objetivo 3R: M1 · 3 | 383 | 21.7 % | -0.154 | -59.0 | 0.72 | -60.4 | -2.40 |
