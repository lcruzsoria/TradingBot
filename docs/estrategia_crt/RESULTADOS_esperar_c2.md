# Backtest: CRT (variante B) en NAS100, H3 → M15/M30/H1 → M5/M3 · esperando al cierre de C2

**Variante sin look-ahead:** C2 tiene que haber cerrado dentro del rango de C1 (cierre real del HTF) y el CISD y la entrada se buscan desde el cierre de C2 hasta el final de C3. Si el precio supera el extremo del sweep en C3, el setup se anula.

Script: `scripts/backtest_crt.py`. Solo lee velas M1, M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están en la cabecera del script y en `GUIA.md`; se fijaron antes de ver los resultados.

- **Se da por buena (cada combinación LTF × entrada) si:** (1) NAS100 de PUPrime, todo el histórico: ≥ 100 operaciones y R neto > +0.05 con t > 2.0; (2) R neto positivo en los dos periodos (hasta 2022; 2023 en adelante); (3) R neto > 0 en el control (NAS100 (USTEC) de MetaQuotes).
- Son 6 combinaciones, así que algún t alto por azar es esperable: se mira la consistencia, no un solo número.

## Veredicto

| Combinación | NAS100 de PUPrime | (1) | hasta 2022 / 2023 en adelante | (2) | Control: NAS100 (USTEC) de MetaQuotes | (3) | Resultado |
|---|---:|---:|---:|---:|---:|---:|---:|
| M5 · 1. vela siguiente al CISD | 477 ops, -0.103 R, t -1.99 | **no** | -0.100 R, t -1.50 / -0.107 R, t -1.31 | **no** | -0.083 R, t -1.12 | **no** | No pasa |
| M5 · 2. retesteo del iFVG | 201 ops, -0.160 R, t -2.06 | **no** | -0.198 R, t -2.06 / -0.097 R, t -0.73 | **no** | -0.083 R, t -0.66 | **no** | No pasa |
| M5 · 3. primera vela sin mecha | 312 ops, -0.063 R, t -1.03 | **no** | -0.060 R, t -0.76 / -0.066 R, t -0.68 | **no** | +0.037 R, t +0.41 | sí | No pasa |
| M3 · 1. vela siguiente al CISD | 475 ops, -0.114 R, t -2.22 | **no** | -0.124 R, t -1.91 / -0.099 R, t -1.18 | **no** | -0.157 R, t -2.17 | **no** | No pasa |
| M3 · 2. retesteo del iFVG | 165 ops, -0.018 R, t -0.20 | **no** | +0.004 R, t +0.03 / -0.054 R, t -0.38 | **no** | +0.005 R, t +0.03 | sí | No pasa |
| M3 · 3. primera vela sin mecha | 370 ops, -0.049 R, t -0.87 | **no** | -0.073 R, t -1.03 / -0.010 R, t -0.11 | **no** | -0.032 R, t -0.39 | **no** | No pasa |

**0 de 6 combinaciones pasan.**

## Datos

- NAS100.s (puprime) M3: 955133 velas, 2018-09-10 → 2026-10-30 (NY).
- NAS100.s (puprime) M5: 573135 velas, 2018-09-10 → 2026-10-30 (NY).
- USTEC (metaquotes) M3: 488017 velas, 2022-07-06 → 2026-10-30 (NY).
- USTEC (metaquotes) M5: 292870 velas, 2022-07-06 → 2026-10-30 (NY).

## Embudo (cuántos pasos pasan)

| Mercado | velas HTF con sweep | con FVG de MTF sin mitigar al alcance | con el extremo tocando el FVG | con iFVG | con CISD | setups finales |
|---|---:|---:|---:|---:|---:|---:|
| NAS100.s (puprime) M5 | 6136 | 1487 | 1100 | 734 | 497 | 497 |
| NAS100.s (puprime) M3 | 6137 | 1287 | 989 | 694 | 486 | 486 |
| USTEC (metaquotes) M5 | 3063 | 759 | 550 | 366 | 241 | 241 |
| USTEC (metaquotes) M3 | 3064 | 648 | 495 | 336 | 229 | 229 |

## Resultados en NAS100 de PUPrime (R neto, con spread)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M5 · 1. vela siguiente al CISD | 477 | 27.5 % | -0.103 | -49.2 | 0.80 | -56.9 | -1.99 |
|   hasta 2022 | 285 | 27.4 % | -0.100 | -28.6 | 0.81 | -34.1 | -1.50 |
|   2023 en adelante | 192 | 27.6 % | -0.107 | -20.6 | 0.80 | -26.3 | -1.31 |
|   sin costes (R bruto) | 477 | 27.5 % | -0.065 | -31.2 | 0.87 | -43.6 | -1.27 |
|   largos | 264 | 29.5 % | -0.069 | -18.3 | 0.86 | -25.1 | -1.00 |
|   cortos | 213 | 24.9 % | -0.145 | -30.8 | 0.74 | -37.7 | -1.85 |
| M5 · 2. retesteo del iFVG | 201 | 26.4 % | -0.160 | -32.2 | 0.70 | -32.2 | -2.06 |
|   hasta 2022 | 126 | 23.8 % | -0.198 | -24.9 | 0.64 | -29.6 | -2.06 |
|   2023 en adelante | 75 | 30.7 % | -0.097 | -7.2 | 0.82 | -13.7 | -0.73 |
|   sin costes (R bruto) | 201 | 26.4 % | -0.101 | -20.3 | 0.80 | -23.3 | -1.30 |
|   largos | 114 | 28.1 % | -0.164 | -18.7 | 0.70 | -18.7 | -1.60 |
|   cortos | 87 | 24.1 % | -0.155 | -13.5 | 0.71 | -19.1 | -1.29 |
| M5 · 3. primera vela sin mecha | 312 | 30.1 % | -0.063 | -19.5 | 0.87 | -31.2 | -1.03 |
|   hasta 2022 | 187 | 31.6 % | -0.060 | -11.3 | 0.87 | -21.1 | -0.76 |
|   2023 en adelante | 125 | 28.0 % | -0.066 | -8.2 | 0.86 | -20.0 | -0.68 |
|   sin costes (R bruto) | 312 | 30.1 % | -0.028 | -8.9 | 0.94 | -22.7 | -0.47 |
|   largos | 181 | 34.3 % | -0.068 | -12.2 | 0.85 | -19.4 | -0.87 |
|   cortos | 131 | 24.4 % | -0.056 | -7.3 | 0.88 | -12.9 | -0.57 |

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M3 · 1. vela siguiente al CISD | 475 | 27.4 % | -0.114 | -54.1 | 0.78 | -63.8 | -2.22 |
|   hasta 2022 | 287 | 27.2 % | -0.124 | -35.5 | 0.76 | -39.1 | -1.91 |
|   2023 en adelante | 188 | 27.7 % | -0.099 | -18.7 | 0.81 | -26.0 | -1.18 |
|   sin costes (R bruto) | 475 | 27.6 % | -0.075 | -35.5 | 0.85 | -49.9 | -1.46 |
|   largos | 263 | 31.6 % | -0.065 | -17.2 | 0.87 | -28.0 | -0.95 |
|   cortos | 212 | 22.2 % | -0.174 | -36.9 | 0.69 | -41.3 | -2.25 |
| M3 · 2. retesteo del iFVG | 165 | 29.7 % | -0.018 | -3.0 | 0.96 | -15.0 | -0.20 |
|   hasta 2022 | 102 | 28.4 % | +0.004 | +0.4 | 1.01 | -15.0 | +0.03 |
|   2023 en adelante | 63 | 31.7 % | -0.054 | -3.4 | 0.89 | -8.1 | -0.38 |
|   sin costes (R bruto) | 165 | 29.7 % | +0.042 | +7.0 | 1.09 | -10.6 | +0.46 |
|   largos | 85 | 34.1 % | +0.032 | +2.7 | 1.06 | -7.5 | +0.24 |
|   cortos | 80 | 25.0 % | -0.072 | -5.7 | 0.86 | -12.8 | -0.54 |
| M3 · 3. primera vela sin mecha | 370 | 31.6 % | -0.049 | -18.1 | 0.89 | -30.1 | -0.87 |
|   hasta 2022 | 228 | 30.7 % | -0.073 | -16.7 | 0.84 | -29.0 | -1.03 |
|   2023 en adelante | 142 | 33.1 % | -0.010 | -1.5 | 0.98 | -13.9 | -0.11 |
|   sin costes (R bruto) | 370 | 31.9 % | -0.011 | -4.1 | 0.97 | -24.2 | -0.20 |
|   largos | 217 | 35.5 % | -0.008 | -1.8 | 0.98 | -12.9 | -0.11 |
|   cortos | 153 | 26.1 % | -0.107 | -16.3 | 0.79 | -26.3 | -1.16 |

## Control: NAS100 (USTEC) de MetaQuotes

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M5 · 1. vela siguiente al CISD | 238 | 28.2 % | -0.083 | -19.7 | 0.84 | -35.5 | -1.12 |
|   hasta 2022 | 38 | 42.1 % | +0.198 | +7.5 | 1.47 | -7.1 | +0.98 |
|   2023 en adelante | 200 | 25.5 % | -0.136 | -27.2 | 0.74 | -32.4 | -1.72 |
| M5 · 2. retesteo del iFVG | 92 | 31.5 % | -0.083 | -7.6 | 0.85 | -21.9 | -0.66 |
|   hasta 2022 | 9 | 88.9 % | +1.413 | +12.7 | 12.26 | -1.1 | +3.99 |
|   2023 en adelante | 83 | 25.3 % | -0.245 | -20.3 | 0.60 | -21.9 | -2.01 |
| M5 · 3. primera vela sin mecha | 145 | 29.7 % | +0.037 | +5.3 | 1.09 | -12.0 | +0.41 |
|   hasta 2022 | 27 | 33.3 % | +0.071 | +1.9 | 1.19 | -4.9 | +0.34 |
|   2023 en adelante | 118 | 28.8 % | +0.029 | +3.4 | 1.07 | -9.1 | +0.29 |
| M3 · 1. vela siguiente al CISD | 227 | 26.0 % | -0.157 | -35.6 | 0.70 | -45.1 | -2.17 |
|   hasta 2022 | 39 | 33.3 % | -0.078 | -3.1 | 0.85 | -8.8 | -0.42 |
|   2023 en adelante | 188 | 24.5 % | -0.173 | -32.6 | 0.67 | -37.7 | -2.21 |
| M3 · 2. retesteo del iFVG | 76 | 31.6 % | +0.005 | +0.4 | 1.01 | -11.7 | +0.03 |
|   hasta 2022 | 10 | 40.0 % | +0.116 | +1.2 | 1.26 | -2.2 | +0.28 |
|   2023 en adelante | 66 | 30.3 % | -0.012 | -0.8 | 0.98 | -10.4 | -0.08 |
| M3 · 3. primera vela sin mecha | 178 | 33.7 % | -0.032 | -5.6 | 0.93 | -22.8 | -0.39 |
|   hasta 2022 | 32 | 40.6 % | +0.145 | +4.6 | 1.33 | -6.9 | +0.66 |
|   2023 en adelante | 146 | 32.2 % | -0.070 | -10.3 | 0.85 | -16.3 | -0.80 |

## Cómo terminan y riesgo (NAS100 de PUPrime)

| Combinación | Cierres | Riesgo mediano (pts) | p10 | p90 | Coste medio (R) | Coste > 0,2 R |
|---|---:|---:|---:|---:|---:|---:|
| M5 · 1 | stop 225, objetivo 86, sesión 84, BE 82 | 45.0 | 17.5 | 131.0 | 0.038 | 0 % |
| M5 · 2 | stop 97, BE 44, objetivo 34, sesión 26 | 26.5 | 10.2 | 77.5 | 0.059 | 2 % |
| M5 · 3 | stop 129, sesión 78, BE 54, objetivo 51 | 51.0 | 20.0 | 185.7 | 0.034 | 0 % |
| M3 · 1 | stop 223, BE 88, objetivo 84, sesión 80 | 41.0 | 16.2 | 129.9 | 0.039 | 0 % |
| M3 · 2 | stop 74, BE 36, objetivo 36, sesión 19 | 28.8 | 10.5 | 75.9 | 0.061 | 1 % |
| M3 · 3 | stop 150, sesión 94, BE 65, objetivo 61 | 48.0 | 16.4 | 152.8 | 0.038 | 1 % |

## Por año (NAS100 de PUPrime)

**M5 · 1. vela siguiente al CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 17 | 35.3 % | -0.199 | -3.4 | 0.69 | -5.8 | -0.69 |
| 2019 | 71 | 28.2 % | -0.104 | -7.4 | 0.79 | -17.9 | -0.79 |
| 2020 | 62 | 25.8 % | -0.151 | -9.4 | 0.74 | -12.0 | -1.03 |
| 2021 | 60 | 21.7 % | -0.116 | -6.9 | 0.76 | -13.5 | -0.84 |
| 2022 | 75 | 30.7 % | -0.020 | -1.5 | 0.96 | -10.6 | -0.15 |
| 2023 | 63 | 23.8 % | -0.213 | -13.4 | 0.61 | -15.4 | -1.61 |
| 2024 | 33 | 24.2 % | -0.213 | -7.0 | 0.66 | -11.8 | -1.01 |
| 2025 | 60 | 40.0 % | +0.206 | +12.3 | 1.53 | -6.0 | +1.33 |
| 2026 | 36 | 16.7 % | -0.346 | -12.5 | 0.45 | -12.5 | -2.01 |

**M5 · 2. retesteo del iFVG**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 4 | 0.0 % | -0.811 | -3.2 | 0.00 | -3.2 | -3.10 |
| 2019 | 40 | 27.5 % | -0.142 | -5.7 | 0.74 | -11.6 | -0.78 |
| 2020 | 31 | 19.4 % | -0.248 | -7.7 | 0.56 | -8.7 | -1.27 |
| 2021 | 23 | 17.4 % | -0.460 | -10.6 | 0.28 | -12.4 | -2.48 |
| 2022 | 28 | 32.1 % | +0.081 | +2.3 | 1.21 | -4.3 | +0.38 |
| 2023 | 23 | 39.1 % | +0.169 | +3.9 | 1.46 | -2.6 | +0.71 |
| 2024 | 16 | 31.2 % | -0.257 | -4.1 | 0.61 | -7.1 | -0.86 |
| 2025 | 23 | 30.4 % | -0.050 | -1.2 | 0.90 | -5.8 | -0.21 |
| 2026 | 13 | 15.4 % | -0.451 | -5.9 | 0.40 | -6.7 | -1.45 |

**M5 · 3. primera vela sin mecha**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 11 | 18.2 % | -0.630 | -6.9 | 0.11 | -7.6 | -3.37 |
| 2019 | 48 | 27.1 % | -0.233 | -11.2 | 0.56 | -14.9 | -1.64 |
| 2020 | 39 | 30.8 % | +0.017 | +0.7 | 1.04 | -7.0 | +0.09 |
| 2021 | 43 | 34.9 % | -0.017 | -0.7 | 0.96 | -8.5 | -0.09 |
| 2022 | 46 | 37.0 % | +0.150 | +6.9 | 1.41 | -7.7 | +0.90 |
| 2023 | 42 | 19.0 % | -0.319 | -13.4 | 0.44 | -13.5 | -2.10 |
| 2024 | 20 | 35.0 % | +0.058 | +1.2 | 1.11 | -6.5 | +0.19 |
| 2025 | 43 | 39.5 % | +0.205 | +8.8 | 1.61 | -3.7 | +1.20 |
| 2026 | 20 | 15.0 % | -0.240 | -4.8 | 0.43 | -4.8 | -1.34 |

**M3 · 1. vela siguiente al CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 18 | 33.3 % | -0.101 | -1.8 | 0.83 | -5.7 | -0.34 |
| 2019 | 73 | 27.4 % | -0.143 | -10.4 | 0.71 | -18.5 | -1.18 |
| 2020 | 65 | 21.5 % | -0.271 | -17.6 | 0.54 | -17.6 | -2.05 |
| 2021 | 59 | 27.1 % | -0.073 | -4.3 | 0.84 | -15.3 | -0.52 |
| 2022 | 72 | 30.6 % | -0.018 | -1.3 | 0.96 | -11.9 | -0.13 |
| 2023 | 61 | 24.6 % | -0.214 | -13.1 | 0.62 | -14.1 | -1.56 |
| 2024 | 37 | 24.3 % | -0.182 | -6.7 | 0.71 | -12.9 | -0.92 |
| 2025 | 56 | 41.1 % | +0.232 | +13.0 | 1.59 | -4.1 | +1.42 |
| 2026 | 34 | 14.7 % | -0.349 | -11.9 | 0.46 | -12.1 | -1.93 |

**M3 · 2. retesteo del iFVG**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 4 | 50.0 % | +0.961 | +3.8 | 58.39 | -0.1 | +1.67 |
| 2019 | 32 | 28.1 % | +0.009 | +0.3 | 1.02 | -10.0 | +0.04 |
| 2020 | 26 | 19.2 % | -0.226 | -5.9 | 0.62 | -7.6 | -1.00 |
| 2021 | 16 | 37.5 % | +0.073 | +1.2 | 1.15 | -7.3 | +0.23 |
| 2022 | 24 | 29.2 % | +0.040 | +1.0 | 1.08 | -4.6 | +0.16 |
| 2023 | 19 | 36.8 % | +0.171 | +3.2 | 1.53 | -3.7 | +0.68 |
| 2024 | 15 | 33.3 % | -0.037 | -0.6 | 0.93 | -4.2 | -0.12 |
| 2025 | 19 | 31.6 % | -0.127 | -2.4 | 0.79 | -6.1 | -0.46 |
| 2026 | 10 | 20.0 % | -0.369 | -3.7 | 0.39 | -5.4 | -1.21 |

**M3 · 3. primera vela sin mecha**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 14 | 14.3 % | -0.452 | -6.3 | 0.11 | -6.9 | -2.97 |
| 2019 | 60 | 30.0 % | -0.164 | -9.8 | 0.67 | -16.5 | -1.24 |
| 2020 | 50 | 22.0 % | -0.219 | -11.0 | 0.57 | -14.0 | -1.55 |
| 2021 | 47 | 36.2 % | +0.116 | +5.4 | 1.28 | -6.2 | +0.67 |
| 2022 | 57 | 38.6 % | +0.088 | +5.0 | 1.21 | -9.5 | +0.57 |
| 2023 | 44 | 27.3 % | -0.125 | -5.5 | 0.75 | -6.0 | -0.77 |
| 2024 | 30 | 33.3 % | -0.030 | -0.9 | 0.95 | -8.3 | -0.13 |
| 2025 | 48 | 41.7 % | +0.083 | +4.0 | 1.21 | -5.6 | +0.52 |
| 2026 | 20 | 25.0 % | +0.048 | +1.0 | 1.13 | -3.7 | +0.21 |

## Sensibilidad (no cuenta para el veredicto)

Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M5 · 1 | 526 | 26.8 % | -0.118 | -62.0 | 0.78 | -77.2 | -2.39 |
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M5 · 2 | 224 | 25.4 % | -0.176 | -39.4 | 0.68 | -39.4 | -2.39 |
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M5 · 3 | 340 | 30.0 % | -0.062 | -20.9 | 0.87 | -38.4 | -1.05 |
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M3 · 1 | 496 | 27.0 % | -0.123 | -61.1 | 0.77 | -74.4 | -2.45 |
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M3 · 2 | 175 | 30.3 % | -0.004 | -0.8 | 0.99 | -17.4 | -0.05 |
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M3 · 3 | 389 | 31.4 % | -0.061 | -23.7 | 0.87 | -36.7 | -1.10 |
| antigüedad del FVG 3 días: M5 · 1 | 423 | 27.0 % | -0.129 | -54.6 | 0.76 | -58.8 | -2.35 |
| antigüedad del FVG 3 días: M5 · 2 | 184 | 26.1 % | -0.175 | -32.3 | 0.68 | -32.3 | -2.17 |
| antigüedad del FVG 3 días: M5 · 3 | 276 | 29.7 % | -0.092 | -25.4 | 0.81 | -28.6 | -1.43 |
| antigüedad del FVG 3 días: M3 · 1 | 418 | 27.0 % | -0.131 | -54.7 | 0.76 | -59.9 | -2.38 |
| antigüedad del FVG 3 días: M3 · 2 | 149 | 28.2 % | -0.045 | -6.8 | 0.91 | -13.7 | -0.47 |
| antigüedad del FVG 3 días: M3 · 3 | 326 | 32.5 % | -0.045 | -14.5 | 0.90 | -21.1 | -0.74 |
| antigüedad del FVG 30 días: M5 · 1 | 510 | 27.3 % | -0.116 | -59.0 | 0.78 | -62.3 | -2.34 |
| antigüedad del FVG 30 días: M5 · 2 | 216 | 27.3 % | -0.150 | -32.5 | 0.72 | -32.5 | -1.99 |
| antigüedad del FVG 30 días: M5 · 3 | 335 | 30.1 % | -0.068 | -22.7 | 0.85 | -35.3 | -1.16 |
| antigüedad del FVG 30 días: M3 · 1 | 510 | 27.3 % | -0.130 | -66.1 | 0.75 | -72.3 | -2.65 |
| antigüedad del FVG 30 días: M3 · 2 | 177 | 31.1 % | +0.004 | +0.7 | 1.01 | -17.1 | +0.05 |
| antigüedad del FVG 30 días: M3 · 3 | 396 | 31.8 % | -0.052 | -20.4 | 0.89 | -34.6 | -0.95 |
| tolerancia al tocar el FVG 0,05 % del precio: M5 · 1 | 938 | 27.6 % | -0.113 | -105.7 | 0.78 | -105.7 | -3.10 |
| tolerancia al tocar el FVG 0,05 % del precio: M5 · 2 | 402 | 26.4 % | -0.144 | -57.9 | 0.73 | -64.8 | -2.57 |
| tolerancia al tocar el FVG 0,05 % del precio: M5 · 3 | 619 | 31.2 % | -0.062 | -38.6 | 0.86 | -47.7 | -1.45 |
| tolerancia al tocar el FVG 0,05 % del precio: M3 · 1 | 983 | 27.3 % | -0.122 | -119.8 | 0.77 | -119.8 | -3.44 |
| tolerancia al tocar el FVG 0,05 % del precio: M3 · 2 | 367 | 26.7 % | -0.125 | -45.8 | 0.78 | -54.7 | -2.05 |
| tolerancia al tocar el FVG 0,05 % del precio: M3 · 3 | 765 | 30.5 % | -0.079 | -60.3 | 0.83 | -62.9 | -2.04 |
| CISD con cierre dentro de C1 (la versión anterior): M5 · 1 | 474 | 27.6 % | -0.098 | -46.7 | 0.81 | -55.7 | -1.89 |
| CISD con cierre dentro de C1 (la versión anterior): M5 · 2 | 199 | 26.6 % | -0.151 | -30.1 | 0.72 | -30.1 | -1.93 |
| CISD con cierre dentro de C1 (la versión anterior): M5 · 3 | 312 | 30.1 % | -0.063 | -19.5 | 0.87 | -31.2 | -1.02 |
| CISD con cierre dentro de C1 (la versión anterior): M3 · 1 | 471 | 27.6 % | -0.106 | -49.9 | 0.80 | -60.9 | -2.05 |
| CISD con cierre dentro de C1 (la versión anterior): M3 · 2 | 165 | 29.7 % | -0.018 | -3.0 | 0.96 | -15.0 | -0.20 |
| CISD con cierre dentro de C1 (la versión anterior): M3 · 3 | 368 | 31.5 % | -0.055 | -20.4 | 0.88 | -33.4 | -0.98 |
| exigir que C2 cierre dentro de C1 (look-ahead): M5 · 1 | 477 | 27.5 % | -0.103 | -49.2 | 0.80 | -56.9 | -1.99 |
| exigir que C2 cierre dentro de C1 (look-ahead): M5 · 2 | 201 | 26.4 % | -0.160 | -32.2 | 0.70 | -32.2 | -2.06 |
| exigir que C2 cierre dentro de C1 (look-ahead): M5 · 3 | 312 | 30.1 % | -0.063 | -19.5 | 0.87 | -31.2 | -1.03 |
| exigir que C2 cierre dentro de C1 (look-ahead): M3 · 1 | 475 | 27.4 % | -0.114 | -54.1 | 0.78 | -63.8 | -2.22 |
| exigir que C2 cierre dentro de C1 (look-ahead): M3 · 2 | 165 | 29.7 % | -0.018 | -3.0 | 0.96 | -15.0 | -0.20 |
| exigir que C2 cierre dentro de C1 (look-ahead): M3 · 3 | 370 | 31.6 % | -0.049 | -18.1 | 0.89 | -30.1 | -0.87 |
| sin BE: M5 · 1 | 470 | 32.8 % | -0.117 | -55.1 | 0.81 | -64.2 | -2.02 |
| sin BE: M5 · 2 | 200 | 34.5 % | -0.122 | -24.5 | 0.81 | -25.4 | -1.34 |
| sin BE: M5 · 3 | 310 | 36.8 % | -0.045 | -14.0 | 0.92 | -24.7 | -0.66 |
| sin BE: M3 · 1 | 472 | 33.7 % | -0.110 | -51.8 | 0.83 | -60.0 | -1.89 |
| sin BE: M3 · 2 | 165 | 37.6 % | -0.001 | -0.1 | 1.00 | -14.5 | -0.01 |
| sin BE: M3 · 3 | 369 | 36.6 % | -0.085 | -31.2 | 0.85 | -40.2 | -1.34 |
| objetivo 3R: M5 · 1 | 475 | 23.2 % | -0.078 | -36.9 | 0.85 | -53.4 | -1.31 |
| objetivo 3R: M5 · 2 | 250 | 22.0 % | -0.110 | -27.5 | 0.80 | -34.8 | -1.30 |
| objetivo 3R: M5 · 3 | 311 | 26.7 % | -0.043 | -13.3 | 0.91 | -29.3 | -0.62 |
| objetivo 3R: M3 · 1 | 474 | 22.8 % | -0.117 | -55.5 | 0.78 | -65.9 | -2.05 |
| objetivo 3R: M3 · 2 | 217 | 21.2 % | -0.056 | -12.0 | 0.90 | -35.8 | -0.60 |
| objetivo 3R: M3 · 3 | 369 | 26.3 % | -0.071 | -26.2 | 0.85 | -38.7 | -1.16 |
