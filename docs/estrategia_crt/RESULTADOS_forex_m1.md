# Backtest: CRT (variante B) en EURUSD y GBPUSD, H4 → M15/M30/H1 → M1

**Forex:** velas H4 alineadas a las 17:00 NY, sin entradas a las 17:00 NY y lo abierto se cierra (el corte del día FX; las 18:00 eran el cierre de los índices). Mismas reglas que en NAS100 para FVG, iFVG, CISD, entradas y gestión.

Script: `scripts/backtest_crt.py`. Solo lee velas M1, M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están en la cabecera del script y en `GUIA.md`; se fijaron antes de ver los resultados.

- **Se da por buena (cada combinación LTF × entrada) si:** (1) EURUSD de PUPrime, todo el histórico: ≥ 100 operaciones y R neto > +0.05 con t > 2.0; (2) R neto positivo en los dos periodos (1.ª mitad (hasta 2025-06); 2.ª mitad (desde 2025-06)); (3) R neto > 0 en el control (GBPUSD de PUPrime).
- Son 3 combinaciones, así que algún t alto por azar es esperable: se mira la consistencia, no un solo número.

## Veredicto

| Combinación | EURUSD de PUPrime | (1) | 1.ª mitad (hasta 2025-06) / 2.ª mitad (desde 2025-06) | (2) | Control: GBPUSD de PUPrime | (3) | Resultado |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 1112 ops, -0.072 R, t -2.23 | **no** | -0.111 R, t -2.53 / -0.032 R, t -0.68 | **no** | -0.069 R, t -2.19 | **no** | No pasa |
| M1 · 2. retesteo del iFVG | 933 ops, -0.062 R, t -1.73 | **no** | -0.112 R, t -2.26 / -0.013 R, t -0.24 | **no** | -0.064 R, t -1.86 | **no** | No pasa |
| M1 · 3. primera vela sin mecha | 1029 ops, -0.080 R, t -2.46 | **no** | -0.127 R, t -2.83 / -0.032 R, t -0.67 | **no** | -0.057 R, t -1.78 | **no** | No pasa |
| M1 · 4. cierre del CISD | 1112 ops, -0.066 R, t -2.06 | **no** | -0.107 R, t -2.43 / -0.025 R, t -0.54 | **no** | -0.071 R, t -2.26 | **no** | No pasa |

**0 de 3 combinaciones pasan.**

## Datos

- EURUSD (puprime) M1: 999999 velas, 2024-02-25 → 2026-10-30 (NY).
- EURUSD (puprime) M5: 999999 velas, 2013-05-30 → 2026-10-30 (NY).
- GBPUSD (puprime) M1: 999999 velas, 2024-02-23 → 2026-10-30 (NY).
- GBPUSD (puprime) M5: 999999 velas, 2013-05-30 → 2026-10-30 (NY).

## Embudo (cuántos pasos pasan)

| Mercado | velas HTF con sweep | con FVG de MTF formado tras el extremo | con vuelta al FVG | con iFVG | con CISD | setups finales |
|---|---:|---:|---:|---:|---:|---:|
| EURUSD (puprime) M1 | 3937 | 2012 | 1376 | 1374 | 1241 | 1241 |
| GBPUSD (puprime) M1 | 3959 | 2082 | 1427 | 1422 | 1313 | 1313 |

## Resultados en EURUSD de PUPrime (R neto, con spread)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 1112 | 29.8 % | -0.072 | -79.8 | 0.85 | -100.8 | -2.23 |
|   1.ª mitad (hasta 2025-06) | 560 | 29.1 % | -0.111 | -62.2 | 0.76 | -71.7 | -2.53 |
|   2.ª mitad (desde 2025-06) | 552 | 30.4 % | -0.032 | -17.6 | 0.93 | -36.0 | -0.68 |
|   sin costes (R bruto) | 1112 | 30.5 % | -0.012 | -13.6 | 0.97 | -49.2 | -0.38 |
|   largos | 545 | 29.7 % | -0.097 | -52.7 | 0.79 | -65.6 | -2.15 |
|   cortos | 567 | 29.8 % | -0.048 | -27.1 | 0.90 | -46.8 | -1.04 |
| M1 · 2. retesteo del iFVG | 933 | 29.7 % | -0.062 | -58.2 | 0.87 | -76.3 | -1.73 |
|   1.ª mitad (hasta 2025-06) | 465 | 28.2 % | -0.112 | -52.2 | 0.77 | -58.9 | -2.26 |
|   2.ª mitad (desde 2025-06) | 468 | 31.2 % | -0.013 | -5.9 | 0.97 | -23.8 | -0.24 |
|   sin costes (R bruto) | 933 | 30.2 % | +0.004 | +4.1 | 1.01 | -22.4 | +0.12 |
|   largos | 466 | 28.1 % | -0.114 | -53.2 | 0.77 | -58.9 | -2.32 |
|   cortos | 467 | 31.3 % | -0.011 | -5.0 | 0.98 | -28.1 | -0.20 |
| M1 · 3. primera vela sin mecha | 1029 | 29.7 % | -0.080 | -82.8 | 0.83 | -94.0 | -2.46 |
|   1.ª mitad (hasta 2025-06) | 527 | 29.2 % | -0.127 | -66.7 | 0.74 | -72.2 | -2.83 |
|   2.ª mitad (desde 2025-06) | 502 | 30.3 % | -0.032 | -16.1 | 0.93 | -34.5 | -0.67 |
|   sin costes (R bruto) | 1029 | 30.4 % | -0.019 | -19.1 | 0.96 | -44.0 | -0.57 |
|   largos | 514 | 28.4 % | -0.138 | -71.0 | 0.71 | -80.3 | -3.14 |
|   cortos | 515 | 31.1 % | -0.023 | -11.8 | 0.95 | -40.9 | -0.47 |
| M1 · 4. cierre del CISD | 1112 | 30.1 % | -0.066 | -73.7 | 0.86 | -96.2 | -2.06 |
|   1.ª mitad (hasta 2025-06) | 560 | 29.5 % | -0.107 | -59.8 | 0.77 | -69.2 | -2.43 |
|   2.ª mitad (desde 2025-06) | 552 | 30.8 % | -0.025 | -13.9 | 0.94 | -33.9 | -0.54 |
|   sin costes (R bruto) | 1112 | 30.8 % | -0.007 | -7.5 | 0.98 | -43.6 | -0.21 |
|   largos | 545 | 30.1 % | -0.091 | -49.5 | 0.81 | -62.3 | -2.01 |
|   cortos | 567 | 30.2 % | -0.043 | -24.2 | 0.91 | -46.0 | -0.93 |

## Control: GBPUSD de PUPrime

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 1192 | 31.7 % | -0.069 | -81.9 | 0.85 | -84.3 | -2.19 |
|   1.ª mitad (hasta 2025-06) | 577 | 33.8 % | -0.046 | -26.7 | 0.90 | -36.5 | -1.02 |
|   2.ª mitad (desde 2025-06) | 615 | 29.8 % | -0.090 | -55.2 | 0.81 | -60.1 | -2.05 |
| M1 · 2. retesteo del iFVG | 979 | 31.4 % | -0.064 | -62.9 | 0.86 | -72.0 | -1.86 |
|   1.ª mitad (hasta 2025-06) | 471 | 35.2 % | -0.003 | -1.3 | 0.99 | -26.4 | -0.05 |
|   2.ª mitad (desde 2025-06) | 508 | 27.8 % | -0.121 | -61.6 | 0.75 | -65.0 | -2.58 |
| M1 · 3. primera vela sin mecha | 1089 | 32.6 % | -0.057 | -62.6 | 0.87 | -65.5 | -1.78 |
|   1.ª mitad (hasta 2025-06) | 523 | 36.1 % | -0.029 | -15.0 | 0.94 | -36.2 | -0.61 |
|   2.ª mitad (desde 2025-06) | 566 | 29.3 % | -0.084 | -47.5 | 0.82 | -54.6 | -1.89 |
| M1 · 4. cierre del CISD | 1193 | 31.5 % | -0.071 | -84.7 | 0.85 | -87.1 | -2.26 |
|   1.ª mitad (hasta 2025-06) | 577 | 33.8 % | -0.043 | -24.9 | 0.91 | -36.5 | -0.95 |
|   2.ª mitad (desde 2025-06) | 616 | 29.4 % | -0.097 | -59.8 | 0.80 | -65.0 | -2.24 |

## Cómo terminan y riesgo (EURUSD de PUPrime)

| Combinación | Cierres | Riesgo mediano (pips) | p10 | p90 | Coste medio (R) | Coste > 0,2 R |
|---|---:|---:|---:|---:|---:|---:|
| M1 · 1 | stop 435, sesión 267, BE 225, objetivo 185 | 10.2 | 4.4 | 24.0 | 0.059 | 5 % |
| M1 · 2 | stop 371, sesión 206, BE 188, objetivo 168 | 9.5 | 4.0 | 23.1 | 0.067 | 6 % |
| M1 · 3 | stop 394, sesión 264, BE 211, objetivo 159, fin de datos 1 | 10.7 | 4.3 | 24.7 | 0.062 | 5 % |
| M1 · 4 | stop 434, sesión 269, BE 224, objetivo 185 | 10.2 | 4.4 | 24.0 | 0.059 | 5 % |

## Por año (EURUSD de PUPrime)

**M1 · 1. vela siguiente al CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 353 | 30.6 % | -0.131 | -46.4 | 0.73 | -56.0 | -2.37 |
| 2025 | 417 | 27.1 % | -0.118 | -49.3 | 0.76 | -53.2 | -2.30 |
| 2026 | 342 | 32.2 % | +0.046 | +15.9 | 1.11 | -27.4 | +0.76 |

**M1 · 2. retesteo del iFVG**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 289 | 29.8 % | -0.133 | -38.3 | 0.73 | -45.7 | -2.13 |
| 2025 | 361 | 27.4 % | -0.096 | -34.7 | 0.81 | -36.4 | -1.67 |
| 2026 | 283 | 32.5 % | +0.053 | +14.9 | 1.12 | -13.4 | +0.78 |

**M1 · 3. primera vela sin mecha**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 333 | 30.3 % | -0.147 | -49.1 | 0.70 | -52.8 | -2.65 |
| 2025 | 393 | 28.2 % | -0.105 | -41.3 | 0.78 | -44.8 | -1.99 |
| 2026 | 303 | 31.0 % | +0.025 | +7.6 | 1.06 | -16.6 | +0.40 |

**M1 · 4. cierre del CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 353 | 31.2 % | -0.124 | -43.9 | 0.75 | -53.6 | -2.24 |
| 2025 | 417 | 27.1 % | -0.113 | -47.3 | 0.76 | -51.2 | -2.21 |
| 2026 | 342 | 32.7 % | +0.051 | +17.5 | 1.12 | -27.4 | +0.84 |

## Sensibilidad (no cuenta para el veredicto)

Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 1 | 663 | 35.9 % | +0.090 | +59.7 | 1.24 | -14.6 | +2.14 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 2 | 541 | 35.9 % | +0.123 | +66.5 | 1.33 | -11.7 | +2.59 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 3 | 629 | 34.7 % | +0.054 | +33.9 | 1.14 | -20.4 | +1.29 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 4 | 663 | 36.0 % | +0.092 | +61.2 | 1.25 | -13.8 | +2.19 |
| sin BE: M1 · 1 | 1078 | 36.6 % | -0.078 | -83.8 | 0.87 | -118.9 | -2.09 |
| sin BE: M1 · 2 | 907 | 36.8 % | -0.075 | -67.6 | 0.87 | -84.1 | -1.81 |
| sin BE: M1 · 3 | 1003 | 36.5 % | -0.094 | -94.6 | 0.84 | -118.0 | -2.50 |
| sin BE: M1 · 4 | 1078 | 36.6 % | -0.078 | -84.5 | 0.87 | -119.0 | -2.11 |
| objetivo 3R: M1 · 1 | 1081 | 25.5 % | -0.061 | -66.5 | 0.87 | -97.5 | -1.68 |
| objetivo 3R: M1 · 2 | 920 | 23.3 % | -0.109 | -100.1 | 0.77 | -118.7 | -2.82 |
| objetivo 3R: M1 · 3 | 1013 | 26.6 % | -0.051 | -51.6 | 0.89 | -89.1 | -1.34 |
| objetivo 3R: M1 · 4 | 1081 | 25.9 % | -0.055 | -59.1 | 0.88 | -89.9 | -1.48 |
