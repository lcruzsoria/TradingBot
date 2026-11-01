# Backtest: CRT (variante B) en EURUSD y GBPUSD, H4 → M5/M15 → M1

**Forex:** velas H4 alineadas a las 17:00 NY, sin entradas a las 17:00 NY y lo abierto se cierra (el corte del día FX; las 18:00 eran el cierre de los índices). Mismas reglas que en NAS100 para FVG, iFVG, CISD, entradas y gestión.

Script: `scripts/backtest_crt.py`. Solo lee velas M1, M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están en la cabecera del script y en `GUIA.md`; se fijaron antes de ver los resultados.

- **Se da por buena (cada combinación LTF × entrada) si:** (1) EURUSD de PUPrime, todo el histórico: ≥ 100 operaciones y R neto > +0.05 con t > 2.0; (2) R neto positivo en los dos periodos (1.ª mitad (hasta 2025-06); 2.ª mitad (desde 2025-06)); (3) R neto > 0 en el control (GBPUSD de PUPrime).
- Son 3 combinaciones, así que algún t alto por azar es esperable: se mira la consistencia, no un solo número.

## Veredicto

| Combinación | EURUSD de PUPrime | (1) | 1.ª mitad (hasta 2025-06) / 2.ª mitad (desde 2025-06) | (2) | Control: GBPUSD de PUPrime | (3) | Resultado |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 2282 ops, -0.065 R, t -2.69 | **no** | -0.103 R, t -2.97 / -0.029 R, t -0.84 | **no** | -0.064 R, t -2.64 | **no** | No pasa |
| M1 · 2. retesteo del iFVG | 1906 ops, -0.097 R, t -3.64 | **no** | -0.116 R, t -3.03 / -0.078 R, t -2.12 | **no** | -0.069 R, t -2.59 | **no** | No pasa |
| M1 · 3. primera vela sin mecha | 2042 ops, -0.107 R, t -4.30 | **no** | -0.147 R, t -4.19 / -0.069 R, t -1.93 | **no** | -0.048 R, t -1.87 | **no** | No pasa |
| M1 · 4. cierre del CISD | 2282 ops, -0.066 R, t -2.68 | **no** | -0.105 R, t -3.01 / -0.027 R, t -0.78 | **no** | -0.061 R, t -2.52 | **no** | No pasa |

**0 de 3 combinaciones pasan.**

## Datos

- EURUSD (puprime) M1: 999999 velas, 2024-02-25 → 2026-10-30 (NY).
- EURUSD (puprime) M5: 999999 velas, 2013-05-30 → 2026-10-30 (NY).
- GBPUSD (puprime) M1: 999999 velas, 2024-02-23 → 2026-10-30 (NY).
- GBPUSD (puprime) M5: 999999 velas, 2013-05-30 → 2026-10-30 (NY).

## Embudo (cuántos pasos pasan)

| Mercado | velas HTF con sweep | con FVG de MTF formado tras el extremo | con vuelta al FVG | con iFVG | con CISD | invalidados | setups finales |
|---|---:|---:|---:|---:|---:|---:|---:|
| EURUSD (puprime) M1 | 3343 | 2979 | 2830 | 2736 | 2563 | 193 | 2563 |
| GBPUSD (puprime) M1 | 3375 | 3047 | 2918 | 2820 | 2643 | 191 | 2643 |

## Invalidados

Un setup queda **invalidado** si el precio llega al extremo opuesto de C1 (el objetivo) antes de encontrar el FVG de MTF, la vuelta a él o el iFVG invertido. No se opera; se anota por qué. Detalle en `analisis/backtest_crt_*_invalidados.csv`.

| Mercado | Invalidados | sin FVG de MTF | sin vuelta al FVG de MTF | sin iFVG invertido |
|---|---:|---:|---:|---:|
| EURUSD (puprime) M1 | 193 | 58 | 87 | 48 |
| GBPUSD (puprime) M1 | 191 | 58 | 80 | 53 |

## Resultados en EURUSD de PUPrime (R neto, con spread)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 2282 | 29.5 % | -0.065 | -149.4 | 0.87 | -171.8 | -2.69 |
|   1.ª mitad (hasta 2025-06) | 1135 | 29.3 % | -0.103 | -116.4 | 0.81 | -130.7 | -2.97 |
|   2.ª mitad (desde 2025-06) | 1147 | 29.7 % | -0.029 | -32.9 | 0.94 | -55.4 | -0.84 |
|   sin costes (R bruto) | 2282 | 30.0 % | +0.027 | +61.9 | 1.06 | -45.8 | +1.12 |
|   largos | 1171 | 30.1 % | -0.064 | -75.0 | 0.88 | -83.6 | -1.87 |
|   cortos | 1111 | 29.0 % | -0.067 | -74.4 | 0.87 | -99.6 | -1.93 |
| M1 · 2. retesteo del iFVG | 1906 | 28.4 % | -0.097 | -184.4 | 0.82 | -189.7 | -3.64 |
|   1.ª mitad (hasta 2025-06) | 935 | 29.3 % | -0.116 | -108.5 | 0.79 | -126.3 | -3.03 |
|   2.ª mitad (desde 2025-06) | 971 | 27.6 % | -0.078 | -75.9 | 0.85 | -81.2 | -2.12 |
|   sin costes (R bruto) | 1906 | 29.2 % | +0.003 | +6.4 | 1.01 | -64.2 | +0.13 |
|   largos | 991 | 28.7 % | -0.104 | -102.7 | 0.81 | -105.8 | -2.83 |
|   cortos | 915 | 28.2 % | -0.089 | -81.7 | 0.83 | -87.7 | -2.32 |
| M1 · 3. primera vela sin mecha | 2042 | 28.2 % | -0.107 | -219.4 | 0.79 | -225.9 | -4.30 |
|   1.ª mitad (hasta 2025-06) | 1018 | 27.9 % | -0.147 | -149.2 | 0.73 | -157.7 | -4.19 |
|   2.ª mitad (desde 2025-06) | 1024 | 28.5 % | -0.069 | -70.2 | 0.86 | -78.5 | -1.93 |
|   sin costes (R bruto) | 2042 | 28.8 % | -0.018 | -37.6 | 0.96 | -57.4 | -0.74 |
|   largos | 1043 | 27.3 % | -0.132 | -137.9 | 0.75 | -140.1 | -3.88 |
|   cortos | 999 | 29.1 % | -0.082 | -81.5 | 0.84 | -110.0 | -2.23 |
| M1 · 4. cierre del CISD | 2282 | 29.7 % | -0.066 | -149.7 | 0.87 | -172.2 | -2.68 |
|   1.ª mitad (hasta 2025-06) | 1137 | 29.5 % | -0.105 | -119.0 | 0.81 | -133.2 | -3.01 |
|   2.ª mitad (desde 2025-06) | 1145 | 29.9 % | -0.027 | -30.7 | 0.95 | -54.1 | -0.78 |
|   sin costes (R bruto) | 2282 | 30.1 % | +0.029 | +65.7 | 1.06 | -47.1 | +1.19 |
|   largos | 1170 | 30.1 % | -0.065 | -75.7 | 0.88 | -84.3 | -1.89 |
|   cortos | 1112 | 29.2 % | -0.067 | -74.0 | 0.87 | -100.1 | -1.90 |

## Control: GBPUSD de PUPrime

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 2329 | 29.8 % | -0.064 | -148.2 | 0.88 | -171.4 | -2.64 |
|   1.ª mitad (hasta 2025-06) | 1164 | 29.2 % | -0.110 | -127.8 | 0.79 | -142.7 | -3.29 |
|   2.ª mitad (desde 2025-06) | 1165 | 30.5 % | -0.018 | -20.4 | 0.96 | -47.5 | -0.51 |
| M1 · 2. retesteo del iFVG | 1921 | 29.3 % | -0.069 | -132.4 | 0.87 | -145.1 | -2.59 |
|   1.ª mitad (hasta 2025-06) | 948 | 29.1 % | -0.114 | -108.1 | 0.79 | -111.3 | -3.03 |
|   2.ª mitad (desde 2025-06) | 973 | 29.4 % | -0.025 | -24.3 | 0.95 | -45.5 | -0.66 |
| M1 · 3. primera vela sin mecha | 2085 | 31.3 % | -0.048 | -99.2 | 0.91 | -125.3 | -1.87 |
|   1.ª mitad (hasta 2025-06) | 1040 | 30.7 % | -0.094 | -97.8 | 0.82 | -112.0 | -2.67 |
|   2.ª mitad (desde 2025-06) | 1045 | 32.0 % | -0.001 | -1.4 | 1.00 | -41.5 | -0.04 |
| M1 · 4. cierre del CISD | 2331 | 29.9 % | -0.061 | -141.2 | 0.88 | -164.3 | -2.52 |
|   1.ª mitad (hasta 2025-06) | 1164 | 29.3 % | -0.107 | -124.0 | 0.80 | -141.0 | -3.19 |
|   2.ª mitad (desde 2025-06) | 1167 | 30.5 % | -0.015 | -17.2 | 0.97 | -44.2 | -0.43 |

## Cómo terminan y riesgo (EURUSD de PUPrime)

| Combinación | Cierres | Riesgo mediano (pips) | p10 | p90 | Coste medio (R) | Coste > 0,2 R |
|---|---:|---:|---:|---:|---:|---:|
| M1 · 1 | stop 993, BE 489, objetivo 480, sesión 320 | 7.5 | 3.0 | 18.3 | 0.093 | 12 % |
| M1 · 2 | stop 855, BE 404, objetivo 394, sesión 253 | 6.9 | 2.7 | 17.1 | 0.100 | 13 % |
| M1 · 3 | stop 891, BE 424, objetivo 384, sesión 342, fin de datos 1 | 8.1 | 3.2 | 20.5 | 0.089 | 10 % |
| M1 · 4 | stop 992, BE 487, objetivo 481, sesión 322 | 7.5 | 3.0 | 18.3 | 0.094 | 12 % |

## Por año (EURUSD de PUPrime)

**M1 · 1. vela siguiente al CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 722 | 29.9 % | -0.130 | -93.5 | 0.77 | -108.9 | -2.99 |
| 2025 | 853 | 28.8 % | -0.069 | -59.1 | 0.87 | -78.6 | -1.75 |
| 2026 | 707 | 30.0 % | +0.005 | +3.3 | 1.01 | -52.6 | +0.11 |

**M1 · 2. retesteo del iFVG**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 580 | 28.6 % | -0.183 | -106.2 | 0.69 | -126.3 | -3.86 |
| 2025 | 731 | 29.8 % | -0.058 | -42.6 | 0.89 | -70.3 | -1.32 |
| 2026 | 595 | 26.6 % | -0.060 | -35.7 | 0.88 | -70.0 | -1.30 |

**M1 · 3. primera vela sin mecha**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 648 | 27.6 % | -0.174 | -112.5 | 0.69 | -119.8 | -3.97 |
| 2025 | 766 | 28.1 % | -0.116 | -88.8 | 0.78 | -111.2 | -2.85 |
| 2026 | 628 | 29.0 % | -0.029 | -18.1 | 0.94 | -62.8 | -0.63 |

**M1 · 4. cierre del CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 723 | 29.9 % | -0.132 | -95.6 | 0.77 | -111.0 | -3.06 |
| 2025 | 854 | 29.2 % | -0.066 | -56.3 | 0.87 | -76.9 | -1.64 |
| 2026 | 705 | 30.1 % | +0.003 | +2.3 | 1.01 | -54.1 | +0.07 |

## Sensibilidad (no cuenta para el veredicto)

Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 1 | 1072 | 38.0 % | +0.186 | +199.0 | 1.50 | -16.2 | +5.25 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 2 | 869 | 37.2 % | +0.180 | +156.1 | 1.49 | -17.1 | +4.61 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 3 | 991 | 35.3 % | +0.116 | +114.8 | 1.30 | -17.9 | +3.28 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 4 | 1073 | 37.8 % | +0.180 | +193.4 | 1.48 | -18.2 | +5.08 |
| sin BE: M1 · 1 | 2227 | 35.7 % | -0.099 | -220.0 | 0.85 | -232.4 | -3.58 |
| sin BE: M1 · 2 | 1863 | 35.3 % | -0.113 | -210.1 | 0.83 | -216.9 | -3.74 |
| sin BE: M1 · 3 | 1986 | 35.6 % | -0.098 | -195.1 | 0.85 | -198.1 | -3.42 |
| sin BE: M1 · 4 | 2226 | 35.8 % | -0.099 | -221.1 | 0.85 | -233.5 | -3.60 |
| objetivo 3R: M1 · 1 | 2176 | 23.9 % | -0.048 | -105.1 | 0.91 | -163.8 | -1.68 |
| objetivo 3R: M1 · 2 | 1861 | 21.7 % | -0.117 | -218.0 | 0.79 | -221.0 | -3.91 |
| objetivo 3R: M1 · 3 | 1959 | 23.2 % | -0.093 | -182.5 | 0.82 | -202.2 | -3.22 |
| objetivo 3R: M1 · 4 | 2177 | 24.1 % | -0.048 | -104.6 | 0.91 | -164.9 | -1.67 |
