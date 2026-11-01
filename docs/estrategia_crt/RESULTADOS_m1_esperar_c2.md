# Backtest: CRT (variante B) en NAS100, H3 → M15/M30/H1 → M1 · esperando al cierre de C2

**Variante sin look-ahead:** C2 tiene que haber cerrado dentro del rango de C1 (cierre real del HTF) y el CISD y la entrada se buscan desde el cierre de C2 hasta el final de C3. Si el precio supera el extremo del sweep en C3, el setup se anula.

Script: `scripts/backtest_crt.py`. Solo lee velas M1, M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están en la cabecera del script y en `GUIA.md`; se fijaron antes de ver los resultados.

- **Se da por buena (cada combinación LTF × entrada) si:** (1) NAS100 de PUPrime, todo el histórico: ≥ 100 operaciones y R neto > +0.05 con t > 2.0; (2) R neto positivo en los dos periodos (1.ª mitad (hasta 2025-06); 2.ª mitad (desde 2025-06)); (3) R neto > 0 en el control (NAS100 (USTEC) de MetaQuotes).
- Son 3 combinaciones, así que algún t alto por azar es esperable: se mira la consistencia, no un solo número.

## Veredicto

| Combinación | NAS100 de PUPrime | (1) | 1.ª mitad (hasta 2025-06) / 2.ª mitad (desde 2025-06) | (2) | Control: NAS100 (USTEC) de MetaQuotes | (3) | Resultado |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 134 ops, -0.210 R, t -2.26 | **no** | -0.206 R, t -1.41 / -0.214 R, t -1.80 | **no** | -0.204 R, t -2.29 | **no** | No pasa |
| M1 · 2. retesteo del iFVG | 19 ops, +0.114 R, t +0.38 | **no** | -0.212 R, t -0.56 / +0.477 R, t +1.02 | **no** | -0.346 R, t -1.54 | **no** | No pasa |
| M1 · 3. primera vela sin mecha | 127 ops, -0.026 R, t -0.26 | **no** | -0.010 R, t -0.06 / -0.041 R, t -0.31 | **no** | -0.127 R, t -1.36 | **no** | No pasa |

**0 de 3 combinaciones pasan.**

## Datos

- NAS100.s (puprime) M1: 999999 velas, 2024-01-04 → 2026-10-30 (NY).
- NAS100.s (puprime) M5: 573135 velas, 2018-09-10 → 2026-10-30 (NY).
- USTEC (metaquotes) M1: 999999 velas, 2023-10-30 → 2026-10-30 (NY).
- USTEC (metaquotes) M5: 292870 velas, 2022-07-06 → 2026-10-30 (NY).

## Embudo (cuántos pasos pasan)

| Mercado | velas HTF con sweep | con FVG de MTF sin mitigar al alcance | con el extremo tocando el FVG | con iFVG | con CISD | setups finales |
|---|---:|---:|---:|---:|---:|---:|
| NAS100.s (puprime) M1 | 2184 | 400 | 327 | 240 | 135 | 135 |
| USTEC (metaquotes) M1 | 2048 | 388 | 316 | 223 | 140 | 140 |

## Resultados en NAS100 de PUPrime (R neto, con spread)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 134 | 20.1 % | -0.210 | -28.2 | 0.62 | -28.2 | -2.26 |
|   1.ª mitad (hasta 2025-06) | 64 | 21.9 % | -0.206 | -13.2 | 0.66 | -20.3 | -1.41 |
|   2.ª mitad (desde 2025-06) | 70 | 18.6 % | -0.214 | -15.0 | 0.58 | -21.1 | -1.80 |
|   sin costes (R bruto) | 134 | 20.1 % | -0.174 | -23.3 | 0.67 | -23.3 | -1.88 |
|   largos | 72 | 16.7 % | -0.279 | -20.1 | 0.49 | -20.1 | -2.43 |
|   cortos | 62 | 24.2 % | -0.130 | -8.1 | 0.77 | -11.2 | -0.86 |
| M1 · 2. retesteo del iFVG | 19 | 31.6 % | +0.114 | +2.2 | 1.24 | -4.8 | +0.38 |
|   1.ª mitad (hasta 2025-06) | 10 | 20.0 % | -0.212 | -2.1 | 0.64 | -4.8 | -0.56 |
|   2.ª mitad (desde 2025-06) | 9 | 44.4 % | +0.477 | +4.3 | 2.31 | -3.2 | +1.02 |
|   sin costes (R bruto) | 19 | 31.6 % | +0.211 | +4.0 | 1.50 | -4.0 | +0.70 |
|   largos | 12 | 33.3 % | +0.233 | +2.8 | 1.59 | -3.7 | +0.62 |
|   cortos | 7 | 28.6 % | -0.090 | -0.6 | 0.86 | -2.2 | -0.17 |
| M1 · 3. primera vela sin mecha | 127 | 30.7 % | -0.026 | -3.4 | 0.95 | -14.2 | -0.26 |
|   1.ª mitad (hasta 2025-06) | 60 | 33.3 % | -0.010 | -0.6 | 0.98 | -14.0 | -0.06 |
|   2.ª mitad (desde 2025-06) | 67 | 28.4 % | -0.041 | -2.7 | 0.91 | -14.2 | -0.31 |
|   sin costes (R bruto) | 127 | 30.7 % | +0.014 | +1.8 | 1.03 | -12.9 | +0.14 |
|   largos | 69 | 27.5 % | -0.086 | -6.0 | 0.82 | -9.6 | -0.68 |
|   cortos | 58 | 34.5 % | +0.045 | +2.6 | 1.09 | -7.5 | +0.27 |

## Control: NAS100 (USTEC) de MetaQuotes

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 140 | 21.4 % | -0.204 | -28.5 | 0.62 | -31.5 | -2.29 |
|   1.ª mitad (hasta 2025-06) | 68 | 26.5 % | -0.161 | -10.9 | 0.71 | -14.1 | -1.18 |
|   2.ª mitad (desde 2025-06) | 72 | 16.7 % | -0.244 | -17.6 | 0.53 | -22.5 | -2.09 |
| M1 · 2. retesteo del iFVG | 18 | 11.1 % | -0.346 | -6.2 | 0.39 | -6.2 | -1.54 |
|   1.ª mitad (hasta 2025-06) | 10 | 10.0 % | -0.286 | -2.9 | 0.41 | -3.7 | -0.98 |
|   2.ª mitad (desde 2025-06) | 8 | 12.5 % | -0.420 | -3.4 | 0.37 | -4.1 | -1.14 |
| M1 · 3. primera vela sin mecha | 135 | 25.9 % | -0.127 | -17.1 | 0.75 | -19.9 | -1.36 |
|   1.ª mitad (hasta 2025-06) | 64 | 31.2 % | -0.068 | -4.3 | 0.87 | -9.0 | -0.47 |
|   2.ª mitad (desde 2025-06) | 71 | 21.1 % | -0.180 | -12.8 | 0.64 | -17.5 | -1.48 |

## Cómo terminan y riesgo (NAS100 de PUPrime)

| Combinación | Cierres | Riesgo mediano (pts) | p10 | p90 | Coste medio (R) | Coste > 0,2 R |
|---|---:|---:|---:|---:|---:|---:|
| M1 · 1 | stop 65, BE 28, objetivo 21, sesión 20 | 64.2 | 24.8 | 172.9 | 0.036 | 0 % |
| M1 · 2 | stop 8, objetivo 6, BE 5 | 19.0 | 11.1 | 61.3 | 0.096 | 5 % |
| M1 · 3 | stop 54, sesión 28, objetivo 25, BE 20 | 61.5 | 20.2 | 186.5 | 0.040 | 1 % |

## Por año (NAS100 de PUPrime)

**M1 · 1. vela siguiente al CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 40 | 17.5 % | -0.395 | -15.8 | 0.45 | -20.3 | -2.27 |
| 2025 | 57 | 29.8 % | +0.115 | +6.6 | 1.31 | -4.2 | +0.78 |
| 2026 | 37 | 8.1 % | -0.511 | -18.9 | 0.24 | -18.9 | -3.62 |

**M1 · 2. retesteo del iFVG**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 9 | 22.2 % | -0.224 | -2.0 | 0.65 | -4.8 | -0.53 |
| 2025 | 6 | 66.7 % | +1.234 | +7.4 | 47.31 | -0.2 | +2.97 |
| 2026 | 4 | 0.0 % | -0.804 | -3.2 | 0.00 | -3.2 | -3.21 |

**M1 · 3. primera vela sin mecha**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 37 | 24.3 % | -0.253 | -9.4 | 0.61 | -14.0 | -1.34 |
| 2025 | 56 | 44.6 % | +0.312 | +17.5 | 1.94 | -3.2 | +1.96 |
| 2026 | 34 | 14.7 % | -0.337 | -11.5 | 0.43 | -11.5 | -2.01 |

## Sensibilidad (no cuenta para el veredicto)

Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M1 · 1 | 139 | 20.1 % | -0.212 | -29.5 | 0.62 | -29.5 | -2.32 |
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M1 · 2 | 21 | 28.6 % | -0.004 | -0.1 | 0.99 | -5.9 | -0.01 |
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M1 · 3 | 132 | 30.3 % | -0.044 | -5.9 | 0.91 | -15.3 | -0.44 |
| antigüedad del FVG 3 días: M1 · 1 | 115 | 17.4 % | -0.277 | -31.9 | 0.52 | -32.1 | -2.88 |
| antigüedad del FVG 3 días: M1 · 2 | 16 | 31.2 % | +0.092 | +1.5 | 1.18 | -4.7 | +0.28 |
| antigüedad del FVG 3 días: M1 · 3 | 108 | 28.7 % | -0.066 | -7.1 | 0.87 | -15.5 | -0.60 |
| antigüedad del FVG 30 días: M1 · 1 | 147 | 21.8 % | -0.187 | -27.6 | 0.65 | -29.5 | -2.12 |
| antigüedad del FVG 30 días: M1 · 2 | 21 | 33.3 % | +0.116 | +2.4 | 1.26 | -4.8 | +0.43 |
| antigüedad del FVG 30 días: M1 · 3 | 140 | 30.7 % | -0.031 | -4.3 | 0.94 | -15.3 | -0.32 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 1 | 353 | 24.1 % | -0.166 | -58.8 | 0.70 | -61.4 | -2.82 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 2 | 67 | 23.9 % | -0.265 | -17.8 | 0.61 | -19.4 | -1.79 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 3 | 330 | 28.8 % | -0.103 | -34.0 | 0.80 | -34.5 | -1.66 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 1 | 134 | 20.1 % | -0.210 | -28.2 | 0.62 | -28.2 | -2.26 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 2 | 19 | 31.6 % | +0.114 | +2.2 | 1.24 | -4.8 | +0.38 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 3 | 127 | 30.7 % | -0.026 | -3.4 | 0.95 | -14.2 | -0.26 |
| sin BE: M1 · 1 | 134 | 29.9 % | -0.138 | -18.5 | 0.79 | -18.5 | -1.25 |
| sin BE: M1 · 2 | 19 | 36.8 % | +0.054 | +1.0 | 1.08 | -6.8 | +0.16 |
| sin BE: M1 · 3 | 127 | 35.4 % | -0.042 | -5.4 | 0.93 | -16.0 | -0.37 |
| objetivo 3R: M1 · 1 | 134 | 18.7 % | -0.138 | -18.5 | 0.75 | -23.1 | -1.24 |
| objetivo 3R: M1 · 2 | 30 | 13.3 % | -0.169 | -5.1 | 0.70 | -7.2 | -0.71 |
| objetivo 3R: M1 · 3 | 126 | 23.8 % | -0.058 | -7.3 | 0.88 | -17.7 | -0.51 |
