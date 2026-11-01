# Backtest: CRT (variante B) en NAS100, H3 → M5/M15 → M1

Script: `scripts/backtest_crt.py`. Solo lee velas M1, M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están en la cabecera del script y en `GUIA.md`; se fijaron antes de ver los resultados.

- **Se da por buena (cada combinación LTF × entrada) si:** (1) NAS100 de PUPrime, todo el histórico: ≥ 100 operaciones y R neto > +0.05 con t > 2.0; (2) R neto positivo en los dos periodos (1.ª mitad (hasta 2025-06); 2.ª mitad (desde 2025-06)); (3) R neto > 0 en el control (NAS100 (USTEC) de MetaQuotes).
- Son 3 combinaciones, así que algún t alto por azar es esperable: se mira la consistencia, no un solo número.

## Veredicto

| Combinación | NAS100 de PUPrime | (1) | 1.ª mitad (hasta 2025-06) / 2.ª mitad (desde 2025-06) | (2) | Control: NAS100 (USTEC) de MetaQuotes | (3) | Resultado |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 2412 ops, -0.068 R, t -2.86 | **no** | -0.037 R, t -1.07 / -0.097 R, t -2.96 | **no** | -0.082 R, t -3.39 | **no** | No pasa |
| M1 · 2. retesteo del iFVG | 1915 ops, -0.089 R, t -3.31 | **no** | -0.069 R, t -1.76 / -0.106 R, t -2.91 | **no** | -0.128 R, t -4.79 | **no** | No pasa |
| M1 · 3. primera vela sin mecha | 1939 ops, -0.078 R, t -2.94 | **no** | -0.019 R, t -0.50 / -0.134 R, t -3.68 | **no** | -0.096 R, t -3.51 | **no** | No pasa |
| M1 · 4. cierre del CISD | 2420 ops, -0.066 R, t -2.78 | **no** | -0.037 R, t -1.06 / -0.094 R, t -2.87 | **no** | -0.085 R, t -3.50 | **no** | No pasa |

**0 de 3 combinaciones pasan.**

## Datos

- NAS100.s (puprime) M1: 999999 velas, 2024-01-04 → 2026-10-30 (NY).
- NAS100.s (puprime) M5: 573135 velas, 2018-09-10 → 2026-10-30 (NY).
- USTEC (metaquotes) M1: 999999 velas, 2023-10-30 → 2026-10-30 (NY).
- USTEC (metaquotes) M5: 292870 velas, 2022-07-06 → 2026-10-30 (NY).

## Embudo (cuántos pasos pasan)

| Mercado | velas HTF con sweep | con FVG de MTF formado tras el extremo | con vuelta al FVG | con iFVG | con CISD | invalidados | setups finales |
|---|---:|---:|---:|---:|---:|---:|---:|
| NAS100.s (puprime) M1 | 4688 | 3671 | 3344 | 3098 | 2714 | 486 | 2714 |
| USTEC (metaquotes) M1 | 4546 | 3490 | 3195 | 2914 | 2570 | 446 | 2570 |

## Invalidados

Un setup queda **invalidado** si el precio llega al extremo opuesto de C1 (el objetivo) antes de encontrar el FVG de MTF, la vuelta a él o el iFVG invertido. No se opera; se anota por qué. Detalle en `analisis/backtest_crt_*_invalidados.csv`.

| Mercado | Invalidados | sin FVG de MTF | sin vuelta al FVG de MTF | sin iFVG invertido |
|---|---:|---:|---:|---:|
| NAS100.s (puprime) M1 | 486 | 223 | 160 | 103 |
| USTEC (metaquotes) M1 | 446 | 215 | 139 | 92 |

## Resultados en NAS100 de PUPrime (R neto, con spread)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 2412 | 29.0 % | -0.068 | -164.6 | 0.87 | -170.1 | -2.86 |
|   1.ª mitad (hasta 2025-06) | 1163 | 30.3 % | -0.037 | -43.3 | 0.93 | -81.7 | -1.07 |
|   2.ª mitad (desde 2025-06) | 1249 | 27.8 % | -0.097 | -121.3 | 0.82 | -126.8 | -2.96 |
|   sin costes (R bruto) | 2412 | 29.4 % | -0.000 | -0.2 | 1.00 | -64.4 | -0.00 |
|   largos | 1165 | 30.9 % | -0.041 | -47.9 | 0.92 | -67.9 | -1.19 |
|   cortos | 1247 | 27.2 % | -0.094 | -116.8 | 0.82 | -124.6 | -2.83 |
| M1 · 2. retesteo del iFVG | 1915 | 28.4 % | -0.089 | -169.7 | 0.83 | -172.6 | -3.31 |
|   1.ª mitad (hasta 2025-06) | 909 | 29.2 % | -0.069 | -62.8 | 0.87 | -69.1 | -1.76 |
|   2.ª mitad (desde 2025-06) | 1006 | 27.6 % | -0.106 | -106.9 | 0.80 | -109.8 | -2.91 |
|   sin costes (R bruto) | 1915 | 29.2 % | -0.013 | -24.9 | 0.97 | -64.7 | -0.49 |
|   largos | 930 | 30.0 % | -0.058 | -54.1 | 0.89 | -67.7 | -1.51 |
|   cortos | 985 | 26.8 % | -0.117 | -115.6 | 0.79 | -124.9 | -3.16 |
| M1 · 3. primera vela sin mecha | 1939 | 29.4 % | -0.078 | -150.4 | 0.85 | -150.4 | -2.94 |
|   1.ª mitad (hasta 2025-06) | 953 | 31.5 % | -0.019 | -18.3 | 0.96 | -53.5 | -0.50 |
|   2.ª mitad (desde 2025-06) | 986 | 27.5 % | -0.134 | -132.1 | 0.75 | -132.1 | -3.68 |
|   sin costes (R bruto) | 1939 | 30.0 % | -0.009 | -18.3 | 0.98 | -80.7 | -0.36 |
|   largos | 926 | 31.9 % | -0.045 | -41.6 | 0.91 | -53.5 | -1.16 |
|   cortos | 1013 | 27.2 % | -0.107 | -108.8 | 0.80 | -113.0 | -2.98 |
| M1 · 4. cierre del CISD | 2420 | 29.0 % | -0.066 | -160.2 | 0.87 | -163.5 | -2.78 |
|   1.ª mitad (hasta 2025-06) | 1165 | 30.3 % | -0.037 | -42.6 | 0.93 | -84.7 | -1.06 |
|   2.ª mitad (desde 2025-06) | 1255 | 27.7 % | -0.094 | -117.5 | 0.82 | -120.9 | -2.87 |
|   sin costes (R bruto) | 2420 | 29.3 % | +0.002 | +4.7 | 1.00 | -65.6 | +0.08 |
|   largos | 1168 | 30.9 % | -0.039 | -46.1 | 0.92 | -65.1 | -1.15 |
|   cortos | 1252 | 27.2 % | -0.091 | -114.1 | 0.83 | -121.9 | -2.76 |

## Control: NAS100 (USTEC) de MetaQuotes

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 2279 | 28.0 % | -0.082 | -187.1 | 0.84 | -188.4 | -3.39 |
|   1.ª mitad (hasta 2025-06) | 1161 | 28.4 % | -0.077 | -89.6 | 0.85 | -102.0 | -2.25 |
|   2.ª mitad (desde 2025-06) | 1118 | 27.5 % | -0.087 | -97.5 | 0.83 | -98.8 | -2.55 |
| M1 · 2. retesteo del iFVG | 1818 | 26.5 % | -0.128 | -233.5 | 0.76 | -241.8 | -4.79 |
|   1.ª mitad (hasta 2025-06) | 924 | 26.1 % | -0.148 | -136.7 | 0.74 | -138.7 | -3.90 |
|   2.ª mitad (desde 2025-06) | 894 | 27.0 % | -0.108 | -96.7 | 0.79 | -110.3 | -2.85 |
| M1 · 3. primera vela sin mecha | 1766 | 28.4 % | -0.096 | -169.0 | 0.82 | -170.1 | -3.51 |
|   1.ª mitad (hasta 2025-06) | 934 | 30.0 % | -0.066 | -61.7 | 0.87 | -77.3 | -1.72 |
|   2.ª mitad (desde 2025-06) | 832 | 26.7 % | -0.129 | -107.3 | 0.75 | -108.0 | -3.34 |
| M1 · 4. cierre del CISD | 2278 | 28.1 % | -0.085 | -192.7 | 0.84 | -194.0 | -3.50 |
|   1.ª mitad (hasta 2025-06) | 1159 | 28.6 % | -0.075 | -86.9 | 0.86 | -103.3 | -2.19 |
|   2.ª mitad (desde 2025-06) | 1119 | 27.4 % | -0.095 | -105.9 | 0.82 | -107.2 | -2.77 |

## Cómo terminan y riesgo (NAS100 de PUPrime)

| Combinación | Cierres | Riesgo mediano (pts) | p10 | p90 | Coste medio (R) | Coste > 0,2 R |
|---|---:|---:|---:|---:|---:|---:|
| M1 · 1 | stop 1106, objetivo 524, BE 462, sesión 320 | 36.8 | 12.5 | 106.2 | 0.068 | 4 % |
| M1 · 2 | stop 896, objetivo 411, BE 378, sesión 230 | 33.8 | 11.2 | 99.9 | 0.076 | 5 % |
| M1 · 3 | stop 883, objetivo 411, BE 346, sesión 299 | 38.5 | 12.5 | 115.5 | 0.068 | 4 % |
| M1 · 4 | stop 1105, objetivo 526, BE 465, sesión 324 | 36.6 | 12.5 | 105.9 | 0.068 | 5 % |

## Por año (NAS100 de PUPrime)

**M1 · 1. vela siguiente al CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 791 | 29.2 % | -0.070 | -55.6 | 0.86 | -81.7 | -1.70 |
| 2025 | 879 | 28.1 % | -0.074 | -65.5 | 0.86 | -99.6 | -1.89 |
| 2026 | 742 | 29.8 % | -0.059 | -43.6 | 0.89 | -57.1 | -1.35 |

**M1 · 2. retesteo del iFVG**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 614 | 29.5 % | -0.063 | -38.5 | 0.88 | -69.1 | -1.30 |
| 2025 | 701 | 26.7 % | -0.123 | -86.4 | 0.77 | -97.5 | -2.82 |
| 2026 | 600 | 29.2 % | -0.075 | -44.8 | 0.86 | -53.2 | -1.57 |

**M1 · 3. primera vela sin mecha**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 644 | 29.5 % | -0.056 | -36.0 | 0.89 | -53.5 | -1.23 |
| 2025 | 727 | 30.1 % | -0.070 | -50.5 | 0.87 | -90.6 | -1.60 |
| 2026 | 568 | 28.5 % | -0.113 | -63.9 | 0.79 | -71.8 | -2.33 |

**M1 · 4. cierre del CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 793 | 29.1 % | -0.072 | -56.9 | 0.86 | -84.7 | -1.74 |
| 2025 | 882 | 28.0 % | -0.074 | -65.6 | 0.86 | -103.6 | -1.89 |
| 2026 | 745 | 29.9 % | -0.051 | -37.7 | 0.90 | -49.1 | -1.17 |

## Sensibilidad (no cuenta para el veredicto)

Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 1 | 1220 | 36.8 % | +0.180 | +220.0 | 1.47 | -15.6 | +5.35 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 2 | 946 | 36.9 % | +0.183 | +173.0 | 1.47 | -17.0 | +4.73 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 3 | 1043 | 35.7 % | +0.118 | +123.1 | 1.29 | -18.0 | +3.28 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 4 | 1223 | 36.9 % | +0.186 | +226.9 | 1.49 | -17.6 | +5.51 |
| sin BE: M1 · 1 | 2344 | 36.4 % | -0.046 | -108.8 | 0.93 | -121.0 | -1.70 |
| sin BE: M1 · 2 | 1871 | 35.5 % | -0.088 | -163.8 | 0.87 | -173.9 | -2.86 |
| sin BE: M1 · 3 | 1892 | 36.2 % | -0.065 | -123.3 | 0.90 | -129.2 | -2.18 |
| sin BE: M1 · 4 | 2351 | 36.5 % | -0.043 | -101.8 | 0.93 | -113.1 | -1.59 |
| objetivo 3R: M1 · 1 | 2310 | 23.2 % | -0.047 | -109.3 | 0.91 | -126.6 | -1.68 |
| objetivo 3R: M1 · 2 | 1891 | 21.5 % | -0.090 | -170.0 | 0.83 | -170.0 | -2.94 |
| objetivo 3R: M1 · 3 | 1881 | 23.7 % | -0.055 | -102.9 | 0.90 | -128.9 | -1.77 |
| objetivo 3R: M1 · 4 | 2318 | 23.2 % | -0.047 | -108.5 | 0.91 | -127.5 | -1.67 |
