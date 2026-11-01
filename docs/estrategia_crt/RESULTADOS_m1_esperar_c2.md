# Backtest: CRT (variante B) en NAS100, H3 → M15/M30/H1 → M1 · esperando al cierre de C2

**Variante sin look-ahead:** C2 tiene que haber cerrado dentro del rango de C1 (cierre real del HTF) y el CISD y la entrada se buscan desde el cierre de C2 hasta el final de C3. Si el precio supera el extremo del sweep en C3, el setup se anula.

Script: `scripts/backtest_crt.py`. Solo lee velas M1, M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están en la cabecera del script y en `GUIA.md`; se fijaron antes de ver los resultados.

- **Se da por buena (cada combinación LTF × entrada) si:** (1) NAS100 de PUPrime, todo el histórico: ≥ 100 operaciones y R neto > +0.05 con t > 2.0; (2) R neto positivo en los dos periodos (1.ª mitad (hasta 2025-06); 2.ª mitad (desde 2025-06)); (3) R neto > 0 en el control (NAS100 (USTEC) de MetaQuotes).
- Son 3 combinaciones, así que algún t alto por azar es esperable: se mira la consistencia, no un solo número.

## Veredicto

| Combinación | NAS100 de PUPrime | (1) | 1.ª mitad (hasta 2025-06) / 2.ª mitad (desde 2025-06) | (2) | Control: NAS100 (USTEC) de MetaQuotes | (3) | Resultado |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 138 ops, -0.249 R, t -2.78 | **no** | -0.262 R, t -1.89 / -0.237 R, t -2.03 | **no** | -0.234 R, t -2.71 | **no** | No pasa |
| M1 · 2. retesteo del iFVG | 19 ops, +0.167 R, t +0.57 | **no** | -0.112 R, t -0.30 / +0.477 R, t +1.02 | **no** | -0.346 R, t -1.54 | **no** | No pasa |
| M1 · 3. primera vela sin mecha | 130 ops, -0.067 R, t -0.67 | **no** | -0.060 R, t -0.38 / -0.073 R, t -0.57 | **no** | -0.133 R, t -1.44 | **no** | No pasa |

**0 de 3 combinaciones pasan.**

## Datos

- NAS100.s (puprime) M1: 999999 velas, 2024-01-04 → 2026-10-30 (NY).
- NAS100.s (puprime) M5: 573135 velas, 2018-09-10 → 2026-10-30 (NY).
- USTEC (metaquotes) M1: 999999 velas, 2023-10-30 → 2026-10-30 (NY).
- USTEC (metaquotes) M5: 292870 velas, 2022-07-06 → 2026-10-30 (NY).

## Embudo (cuántos pasos pasan)

| Mercado | velas HTF con sweep | con FVG de MTF sin mitigar al alcance | con el extremo tocando el FVG | con iFVG | con CISD | setups finales |
|---|---:|---:|---:|---:|---:|---:|
| NAS100.s (puprime) M1 | 2184 | 400 | 327 | 240 | 139 | 139 |
| USTEC (metaquotes) M1 | 2048 | 388 | 316 | 223 | 143 | 143 |

## Resultados en NAS100 de PUPrime (R neto, con spread)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 138 | 18.8 % | -0.249 | -34.4 | 0.56 | -34.4 | -2.78 |
|   1.ª mitad (hasta 2025-06) | 66 | 19.7 % | -0.262 | -17.3 | 0.58 | -21.3 | -1.89 |
|   2.ª mitad (desde 2025-06) | 72 | 18.1 % | -0.237 | -17.1 | 0.54 | -22.1 | -2.03 |
|   sin costes (R bruto) | 138 | 18.8 % | -0.211 | -29.2 | 0.61 | -29.2 | -2.37 |
|   largos | 75 | 16.0 % | -0.308 | -23.1 | 0.45 | -23.1 | -2.76 |
|   cortos | 63 | 22.2 % | -0.179 | -11.3 | 0.69 | -11.3 | -1.23 |
| M1 · 2. retesteo del iFVG | 19 | 31.6 % | +0.167 | +3.2 | 1.39 | -4.8 | +0.57 |
|   1.ª mitad (hasta 2025-06) | 10 | 20.0 % | -0.112 | -1.1 | 0.77 | -4.8 | -0.30 |
|   2.ª mitad (desde 2025-06) | 9 | 44.4 % | +0.477 | +4.3 | 2.31 | -3.2 | +1.02 |
|   sin costes (R bruto) | 19 | 31.6 % | +0.263 | +5.0 | 1.71 | -4.0 | +0.89 |
|   largos | 12 | 33.3 % | +0.316 | +3.8 | 2.01 | -2.7 | +0.89 |
|   cortos | 7 | 28.6 % | -0.090 | -0.6 | 0.86 | -2.2 | -0.17 |
| M1 · 3. primera vela sin mecha | 130 | 30.0 % | -0.067 | -8.7 | 0.87 | -15.3 | -0.67 |
|   1.ª mitad (hasta 2025-06) | 61 | 31.1 % | -0.060 | -3.7 | 0.89 | -14.0 | -0.38 |
|   2.ª mitad (desde 2025-06) | 69 | 29.0 % | -0.073 | -5.0 | 0.84 | -15.3 | -0.57 |
|   sin costes (R bruto) | 130 | 30.0 % | -0.024 | -3.1 | 0.95 | -13.9 | -0.24 |
|   largos | 71 | 28.2 % | -0.112 | -8.0 | 0.77 | -10.7 | -0.90 |
|   cortos | 59 | 32.2 % | -0.012 | -0.7 | 0.98 | -7.5 | -0.08 |

## Control: NAS100 (USTEC) de MetaQuotes

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 143 | 20.3 % | -0.234 | -33.5 | 0.57 | -36.5 | -2.71 |
|   1.ª mitad (hasta 2025-06) | 71 | 23.9 % | -0.225 | -16.0 | 0.61 | -17.0 | -1.76 |
|   2.ª mitad (desde 2025-06) | 72 | 16.7 % | -0.243 | -17.5 | 0.53 | -22.4 | -2.08 |
| M1 · 2. retesteo del iFVG | 18 | 11.1 % | -0.346 | -6.2 | 0.39 | -6.2 | -1.54 |
|   1.ª mitad (hasta 2025-06) | 10 | 10.0 % | -0.286 | -2.9 | 0.41 | -3.7 | -0.98 |
|   2.ª mitad (desde 2025-06) | 8 | 12.5 % | -0.420 | -3.4 | 0.37 | -4.1 | -1.14 |
| M1 · 3. primera vela sin mecha | 137 | 25.5 % | -0.133 | -18.2 | 0.74 | -21.0 | -1.44 |
|   1.ª mitad (hasta 2025-06) | 66 | 30.3 % | -0.082 | -5.4 | 0.84 | -9.1 | -0.59 |
|   2.ª mitad (desde 2025-06) | 71 | 21.1 % | -0.180 | -12.8 | 0.64 | -17.5 | -1.48 |

## Cómo terminan y riesgo (NAS100 de PUPrime)

| Combinación | Cierres | Riesgo mediano (pts) | p10 | p90 | Coste medio (R) | Coste > 0,2 R |
|---|---:|---:|---:|---:|---:|---:|
| M1 · 1 | stop 69, BE 29, sesión 20, objetivo 20 | 63.5 | 24.4 | 165.9 | 0.038 | 0 % |
| M1 · 2 | stop 7, BE 6, objetivo 6 | 19.0 | 11.1 | 61.3 | 0.096 | 5 % |
| M1 · 3 | stop 57, sesión 28, objetivo 24, BE 21 | 60.1 | 19.4 | 185.7 | 0.043 | 2 % |

## Por año (NAS100 de PUPrime)

**M1 · 1. vela siguiente al CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 41 | 17.1 % | -0.411 | -16.9 | 0.43 | -21.3 | -2.42 |
| 2025 | 59 | 27.1 % | +0.040 | +2.4 | 1.10 | -5.8 | +0.28 |
| 2026 | 38 | 7.9 % | -0.524 | -19.9 | 0.23 | -19.9 | -3.79 |

**M1 · 2. retesteo del iFVG**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 9 | 22.2 % | -0.113 | -1.0 | 0.79 | -4.8 | -0.27 |
| 2025 | 6 | 66.7 % | +1.234 | +7.4 | 47.31 | -0.2 | +2.97 |
| 2026 | 4 | 0.0 % | -0.804 | -3.2 | 0.00 | -3.2 | -3.21 |

**M1 · 3. primera vela sin mecha**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 37 | 24.3 % | -0.253 | -9.4 | 0.61 | -14.0 | -1.34 |
| 2025 | 58 | 43.1 % | +0.228 | +13.2 | 1.63 | -3.2 | +1.47 |
| 2026 | 35 | 14.3 % | -0.358 | -12.5 | 0.41 | -12.5 | -2.18 |

## Sensibilidad (no cuenta para el veredicto)

Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M1 · 1 | 143 | 18.9 % | -0.250 | -35.8 | 0.56 | -35.8 | -2.83 |
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M1 · 2 | 21 | 28.6 % | +0.044 | +0.9 | 1.09 | -5.9 | +0.16 |
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M1 · 3 | 135 | 29.6 % | -0.083 | -11.2 | 0.84 | -16.4 | -0.84 |
| antigüedad del FVG 3 días: M1 · 1 | 119 | 16.0 % | -0.320 | -38.1 | 0.46 | -38.4 | -3.48 |
| antigüedad del FVG 3 días: M1 · 2 | 16 | 31.2 % | +0.154 | +2.5 | 1.35 | -3.7 | +0.48 |
| antigüedad del FVG 3 días: M1 · 3 | 111 | 27.9 % | -0.112 | -12.5 | 0.79 | -15.5 | -1.05 |
| antigüedad del FVG 30 días: M1 · 1 | 151 | 20.5 % | -0.224 | -33.8 | 0.59 | -35.8 | -2.62 |
| antigüedad del FVG 30 días: M1 · 2 | 21 | 33.3 % | +0.164 | +3.4 | 1.42 | -4.8 | +0.62 |
| antigüedad del FVG 30 días: M1 · 3 | 143 | 30.1 % | -0.068 | -9.7 | 0.86 | -16.3 | -0.72 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 1 | 359 | 23.7 % | -0.174 | -62.6 | 0.69 | -67.3 | -2.97 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 2 | 67 | 23.9 % | -0.250 | -16.8 | 0.63 | -18.4 | -1.70 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 3 | 335 | 28.4 % | -0.120 | -40.3 | 0.77 | -40.3 | -1.97 |
| CISD con cierre dentro de C1 (la versión anterior): M1 · 1 | 134 | 20.1 % | -0.210 | -28.2 | 0.62 | -28.2 | -2.26 |
| CISD con cierre dentro de C1 (la versión anterior): M1 · 2 | 19 | 31.6 % | +0.114 | +2.2 | 1.24 | -4.8 | +0.38 |
| CISD con cierre dentro de C1 (la versión anterior): M1 · 3 | 127 | 30.7 % | -0.026 | -3.4 | 0.95 | -14.2 | -0.26 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 1 | 138 | 18.8 % | -0.249 | -34.4 | 0.56 | -34.4 | -2.78 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 2 | 19 | 31.6 % | +0.167 | +3.2 | 1.39 | -4.8 | +0.57 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 3 | 130 | 30.0 % | -0.067 | -8.7 | 0.87 | -15.3 | -0.67 |
| sin BE: M1 · 1 | 138 | 29.7 % | -0.163 | -22.5 | 0.76 | -22.6 | -1.51 |
| sin BE: M1 · 2 | 19 | 36.8 % | +0.054 | +1.0 | 1.08 | -6.8 | +0.16 |
| sin BE: M1 · 3 | 130 | 35.4 % | -0.067 | -8.7 | 0.89 | -16.0 | -0.60 |
| objetivo 3R: M1 · 1 | 138 | 17.4 % | -0.187 | -25.8 | 0.67 | -25.8 | -1.76 |
| objetivo 3R: M1 · 2 | 30 | 13.3 % | -0.136 | -4.1 | 0.74 | -7.2 | -0.57 |
| objetivo 3R: M1 · 3 | 129 | 24.0 % | -0.082 | -10.6 | 0.84 | -18.8 | -0.74 |
