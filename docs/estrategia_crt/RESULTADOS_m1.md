# Backtest: CRT (variante B) en NAS100, H3 → M15/M30/H1 → M1

Script: `scripts/backtest_crt.py`. Solo lee velas M1, M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están en la cabecera del script y en `GUIA.md`; se fijaron antes de ver los resultados.

- **Se da por buena (cada combinación LTF × entrada) si:** (1) NAS100 de PUPrime, todo el histórico: ≥ 100 operaciones y R neto > +0.05 con t > 2.0; (2) R neto positivo en los dos periodos (1.ª mitad (hasta 2025-06); 2.ª mitad (desde 2025-06)); (3) R neto > 0 en el control (NAS100 (USTEC) de MetaQuotes).
- Son 3 combinaciones, así que algún t alto por azar es esperable: se mira la consistencia, no un solo número.

## Veredicto

| Combinación | NAS100 de PUPrime | (1) | 1.ª mitad (hasta 2025-06) / 2.ª mitad (desde 2025-06) | (2) | Control: NAS100 (USTEC) de MetaQuotes | (3) | Resultado |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 447 ops, -0.106 R, t -1.92 | **no** | -0.085 R, t -1.02 / -0.123 R, t -1.68 | **no** | -0.104 R, t -1.82 | **no** | No pasa |
| M1 · 2. retesteo del iFVG | 176 ops, -0.219 R, t -2.48 | **no** | -0.352 R, t -2.76 / -0.118 R, t -0.98 | **no** | -0.143 R, t -1.53 | **no** | No pasa |
| M1 · 3. primera vela sin mecha | 375 ops, -0.113 R, t -1.89 | **no** | -0.002 R, t -0.02 / -0.204 R, t -2.61 | **no** | -0.166 R, t -2.76 | **no** | No pasa |

**0 de 3 combinaciones pasan.**

## Datos

- NAS100.s (puprime) M1: 999999 velas, 2024-01-04 → 2026-10-30 (NY).
- NAS100.s (puprime) M5: 573135 velas, 2018-09-10 → 2026-10-30 (NY).
- USTEC (metaquotes) M1: 999999 velas, 2023-10-30 → 2026-10-30 (NY).
- USTEC (metaquotes) M5: 292870 velas, 2022-07-06 → 2026-10-30 (NY).

## Embudo (cuántos pasos pasan)

| Mercado | velas HTF con sweep | con FVG de MTF sin mitigar al alcance | con el extremo tocando el FVG | con iFVG | con CISD | setups finales |
|---|---:|---:|---:|---:|---:|---:|
| NAS100.s (puprime) M1 | 5472 | 1680 | 1404 | 908 | 457 | 457 |
| USTEC (metaquotes) M1 | 5277 | 1578 | 1314 | 841 | 428 | 428 |

## Resultados en NAS100 de PUPrime (R neto, con spread)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 447 | 25.1 % | -0.106 | -47.3 | 0.80 | -47.8 | -1.92 |
|   1.ª mitad (hasta 2025-06) | 205 | 26.8 % | -0.085 | -17.4 | 0.84 | -29.8 | -1.02 |
|   2.ª mitad (desde 2025-06) | 242 | 23.6 % | -0.123 | -29.9 | 0.77 | -31.8 | -1.68 |
|   sin costes (R bruto) | 447 | 25.1 % | -0.043 | -19.2 | 0.91 | -22.8 | -0.78 |
|   largos | 240 | 25.4 % | -0.126 | -30.3 | 0.77 | -36.6 | -1.72 |
|   cortos | 207 | 24.6 % | -0.082 | -17.0 | 0.85 | -23.8 | -0.99 |
| M1 · 2. retesteo del iFVG | 176 | 21.6 % | -0.219 | -38.5 | 0.64 | -39.6 | -2.48 |
|   1.ª mitad (hasta 2025-06) | 76 | 17.1 % | -0.352 | -26.7 | 0.48 | -33.6 | -2.76 |
|   2.ª mitad (desde 2025-06) | 100 | 25.0 % | -0.118 | -11.8 | 0.79 | -16.4 | -0.98 |
|   sin costes (R bruto) | 176 | 21.6 % | -0.110 | -19.4 | 0.79 | -25.0 | -1.26 |
|   largos | 97 | 23.7 % | -0.164 | -16.0 | 0.73 | -24.4 | -1.33 |
|   cortos | 79 | 19.0 % | -0.286 | -22.6 | 0.54 | -22.6 | -2.29 |
| M1 · 3. primera vela sin mecha | 375 | 28.3 % | -0.113 | -42.2 | 0.79 | -49.0 | -1.89 |
|   1.ª mitad (hasta 2025-06) | 170 | 32.4 % | -0.002 | -0.3 | 1.00 | -19.7 | -0.02 |
|   2.ª mitad (desde 2025-06) | 205 | 24.9 % | -0.204 | -41.9 | 0.65 | -49.0 | -2.61 |
|   sin costes (R bruto) | 375 | 28.3 % | -0.049 | -18.5 | 0.90 | -42.0 | -0.83 |
|   largos | 199 | 27.6 % | -0.147 | -29.3 | 0.72 | -30.6 | -1.90 |
|   cortos | 176 | 29.0 % | -0.073 | -12.9 | 0.87 | -34.8 | -0.80 |

## Control: NAS100 (USTEC) de MetaQuotes

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 414 | 25.1 % | -0.104 | -42.9 | 0.81 | -52.4 | -1.82 |
|   1.ª mitad (hasta 2025-06) | 206 | 28.2 % | -0.050 | -10.4 | 0.90 | -23.7 | -0.61 |
|   2.ª mitad (desde 2025-06) | 208 | 22.1 % | -0.156 | -32.5 | 0.71 | -36.2 | -1.99 |
| M1 · 2. retesteo del iFVG | 165 | 22.4 % | -0.143 | -23.6 | 0.75 | -26.4 | -1.53 |
|   1.ª mitad (hasta 2025-06) | 83 | 22.9 % | -0.153 | -12.7 | 0.74 | -23.2 | -1.14 |
|   2.ª mitad (desde 2025-06) | 82 | 22.0 % | -0.133 | -10.9 | 0.76 | -15.6 | -1.02 |
| M1 · 3. primera vela sin mecha | 330 | 24.2 % | -0.166 | -54.7 | 0.69 | -56.8 | -2.76 |
|   1.ª mitad (hasta 2025-06) | 169 | 25.4 % | -0.163 | -27.5 | 0.70 | -30.8 | -1.93 |
|   2.ª mitad (desde 2025-06) | 161 | 23.0 % | -0.169 | -27.2 | 0.68 | -30.1 | -1.98 |

## Cómo terminan y riesgo (NAS100 de PUPrime)

| Combinación | Cierres | Riesgo mediano (pts) | p10 | p90 | Coste medio (R) | Coste > 0,2 R |
|---|---:|---:|---:|---:|---:|---:|
| M1 · 1 | stop 210, BE 102, objetivo 93, sesión 42 | 37.5 | 13.9 | 106.5 | 0.063 | 2 % |
| M1 · 2 | stop 91, BE 41, objetivo 36, sesión 8 | 21.9 | 8.4 | 72.5 | 0.109 | 13 % |
| M1 · 3 | stop 177, objetivo 74, BE 71, sesión 53 | 42.0 | 15.3 | 141.4 | 0.063 | 3 % |

## Por año (NAS100 de PUPrime)

**M1 · 1. vela siguiente al CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 140 | 26.4 % | -0.141 | -19.8 | 0.76 | -26.0 | -1.39 |
| 2025 | 164 | 25.6 % | -0.075 | -12.3 | 0.85 | -18.0 | -0.83 |
| 2026 | 143 | 23.1 % | -0.106 | -15.2 | 0.80 | -18.1 | -1.11 |

**M1 · 2. retesteo del iFVG**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 52 | 11.5 % | -0.519 | -27.0 | 0.29 | -29.0 | -3.82 |
| 2025 | 58 | 29.3 % | +0.016 | +0.9 | 1.03 | -6.6 | +0.09 |
| 2026 | 66 | 22.7 % | -0.189 | -12.5 | 0.68 | -13.5 | -1.32 |

**M1 · 3. primera vela sin mecha**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 115 | 28.7 % | -0.138 | -15.9 | 0.76 | -19.7 | -1.27 |
| 2025 | 139 | 36.0 % | +0.115 | +16.0 | 1.27 | -9.9 | +1.13 |
| 2026 | 121 | 19.0 % | -0.350 | -42.4 | 0.46 | -42.9 | -3.69 |

## Sensibilidad (no cuenta para el veredicto)

Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M1 · 1 | 460 | 25.0 % | -0.113 | -52.0 | 0.79 | -52.5 | -2.09 |
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M1 · 2 | 187 | 20.9 % | -0.251 | -47.0 | 0.61 | -47.0 | -2.95 |
| regla anterior: el FVG solo tiene que llegar más allá del extremo de C1: M1 · 3 | 385 | 27.8 % | -0.126 | -48.6 | 0.77 | -50.1 | -2.16 |
| antigüedad del FVG 3 días: M1 · 1 | 396 | 25.5 % | -0.084 | -33.3 | 0.84 | -37.4 | -1.41 |
| antigüedad del FVG 3 días: M1 · 2 | 161 | 23.0 % | -0.189 | -30.5 | 0.69 | -33.7 | -2.01 |
| antigüedad del FVG 3 días: M1 · 3 | 336 | 26.8 % | -0.123 | -41.3 | 0.77 | -43.9 | -1.96 |
| antigüedad del FVG 30 días: M1 · 1 | 467 | 25.5 % | -0.088 | -41.1 | 0.83 | -41.5 | -1.63 |
| antigüedad del FVG 30 días: M1 · 2 | 179 | 21.8 % | -0.205 | -36.7 | 0.66 | -39.6 | -2.34 |
| antigüedad del FVG 30 días: M1 · 3 | 392 | 28.6 % | -0.109 | -42.6 | 0.80 | -48.7 | -1.87 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 1 | 1006 | 25.0 % | -0.130 | -131.1 | 0.77 | -139.0 | -3.51 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 2 | 467 | 22.9 % | -0.221 | -103.4 | 0.65 | -104.8 | -4.05 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 3 | 810 | 26.5 % | -0.117 | -95.1 | 0.78 | -101.7 | -2.92 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 1 | 207 | 33.8 % | +0.232 | +48.0 | 1.66 | -10.4 | +2.82 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 2 | 69 | 24.6 % | -0.014 | -1.0 | 0.97 | -6.5 | -0.10 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 3 | 183 | 36.6 % | +0.132 | +24.2 | 1.32 | -8.7 | +1.51 |
| sin BE: M1 · 1 | 446 | 31.8 % | -0.153 | -68.1 | 0.78 | -68.1 | -2.45 |
| sin BE: M1 · 2 | 176 | 31.8 % | -0.140 | -24.7 | 0.81 | -28.2 | -1.34 |
| sin BE: M1 · 3 | 374 | 34.2 % | -0.129 | -48.2 | 0.81 | -56.0 | -1.93 |
| objetivo 3R: M1 · 1 | 444 | 19.4 % | -0.090 | -39.8 | 0.83 | -42.8 | -1.42 |
| objetivo 3R: M1 · 2 | 214 | 11.7 % | -0.330 | -70.7 | 0.48 | -70.7 | -4.08 |
| objetivo 3R: M1 · 3 | 374 | 21.9 % | -0.141 | -52.7 | 0.74 | -54.5 | -2.16 |
