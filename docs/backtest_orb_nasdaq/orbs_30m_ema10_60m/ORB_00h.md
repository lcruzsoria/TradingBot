# ORB de 30 min de las 00:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 00:00–00:30 | 1365 | 50.4 | -0.082 | -3.08 | +0.009 | 0.091 | no |
| 00:15–00:45 | 1392 | 48.1 | -0.120 | -4.51 | -0.030 | 0.089 | no |
| 00:30–01:00 | 1370 | 49.5 | -0.090 | -3.38 | -0.002 | 0.088 | no |
| 00:45–01:15 | 1421 | 50.3 | -0.064 | -2.46 | +0.014 | 0.078 | no |

## Detalle

### ORB 00:00–00:30

Rotura con cuerpo desde las 00:30 hasta las 06:30; a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.091 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 672, stop 660, por tiempo 33.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1365 | 50.4 % | -0.082 | -112.6 | 0.84 | -131.7 | -3.08 |
| Sin costes | 1365 | 50.4 % | +0.009 | +11.8 | 1.02 | -48.5 | +0.32 |
| Long | 776 | 51.0 % | -0.083 | -64.1 | 0.84 | -72.7 | -2.32 |
| Short | 589 | 49.6 % | -0.082 | -48.5 | 0.84 | -61.0 | -2.02 |
| 1.ª mitad | 683 | 48.9 % | -0.115 | -78.3 | 0.79 | -92.0 | -3.04 |
| 2.ª mitad | 682 | 51.9 % | -0.050 | -34.3 | 0.90 | -49.2 | -1.32 |

Por año (R neto medio y operaciones): 2018 +0.029 (47), 2019 -0.117 (149), 2020 -0.032 (159), 2021 -0.168 (174), 2022 -0.162 (180), 2023 -0.143 (161), 2024 +0.064 (166), 2025 -0.091 (179), 2026 -0.029 (150).

Sensibilidad (R neto medio y t): colchón 0 % -0.093 (t -3.46), colchón 50 % -0.063 (t -2.39), objetivo 1,5:1 -0.089 (t -2.73), objetivo 2:1 -0.042 (t -1.13).

### ORB 00:15–00:45

Rotura con cuerpo desde las 00:45 hasta las 06:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.089 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 654, stop 693, por tiempo 45.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1392 | 48.1 % | -0.120 | -166.5 | 0.78 | -185.4 | -4.51 |
| Sin costes | 1392 | 48.1 % | -0.030 | -42.1 | 0.94 | -99.9 | -1.14 |
| Long | 780 | 49.5 % | -0.097 | -75.8 | 0.82 | -91.8 | -2.73 |
| Short | 612 | 46.2 % | -0.148 | -90.7 | 0.74 | -100.9 | -3.74 |
| 1.ª mitad | 696 | 42.2 % | -0.233 | -162.0 | 0.62 | -164.0 | -6.29 |
| 2.ª mitad | 696 | 53.9 % | -0.006 | -4.5 | 0.99 | -33.3 | -0.17 |

Por año (R neto medio y operaciones): 2018 -0.233 (56), 2019 -0.273 (173), 2020 -0.117 (173), 2021 -0.245 (172), 2022 -0.216 (164), 2023 -0.042 (161), 2024 -0.108 (181), 2025 +0.081 (161), 2026 +0.032 (151).

Sensibilidad (R neto medio y t): colchón 0 % -0.124 (t -4.65), colchón 50 % -0.095 (t -3.62), objetivo 1,5:1 -0.114 (t -3.59), objetivo 2:1 -0.066 (t -1.80).

### ORB 00:30–01:00

Rotura con cuerpo desde las 01:00 hasta las 07:00; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.088 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 664, stop 663, por tiempo 43.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1370 | 49.5 % | -0.090 | -123.9 | 0.83 | -150.2 | -3.38 |
| Sin costes | 1370 | 49.6 % | -0.002 | -3.0 | 1.00 | -66.8 | -0.08 |
| Long | 779 | 50.7 % | -0.075 | -58.2 | 0.86 | -84.7 | -2.10 |
| Short | 591 | 47.9 % | -0.111 | -65.8 | 0.80 | -70.8 | -2.74 |
| 1.ª mitad | 685 | 45.4 % | -0.178 | -121.9 | 0.69 | -125.5 | -4.72 |
| 2.ª mitad | 685 | 53.6 % | -0.003 | -2.0 | 0.99 | -43.4 | -0.08 |

Por año (R neto medio y operaciones): 2018 -0.019 (50), 2019 -0.213 (167), 2020 -0.165 (173), 2021 -0.181 (166), 2022 -0.153 (150), 2023 -0.023 (153), 2024 -0.081 (183), 2025 +0.018 (167), 2026 +0.058 (161).

Sensibilidad (R neto medio y t): colchón 0 % -0.097 (t -3.59), colchón 50 % -0.059 (t -2.25), objetivo 1,5:1 -0.081 (t -2.50), objetivo 2:1 -0.066 (t -1.80).

### ORB 00:45–01:15

Rotura con cuerpo desde las 01:15 hasta las 07:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.078 R; ancho medio del ORB 0.14 %; cómo terminan: objetivo 689, stop 667, por tiempo 65.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1421 | 50.3 % | -0.064 | -90.9 | 0.88 | -121.8 | -2.46 |
| Sin costes | 1421 | 50.6 % | +0.014 | +19.6 | 1.03 | -40.4 | +0.53 |
| Long | 807 | 51.8 % | -0.036 | -29.0 | 0.93 | -55.0 | -1.04 |
| Short | 614 | 48.4 % | -0.101 | -62.0 | 0.81 | -71.0 | -2.53 |
| 1.ª mitad | 711 | 47.8 % | -0.111 | -79.0 | 0.79 | -82.7 | -3.02 |
| 2.ª mitad | 710 | 52.8 % | -0.017 | -12.0 | 0.97 | -49.3 | -0.46 |

Por año (R neto medio y operaciones): 2018 -0.099 (56), 2019 -0.076 (156), 2020 -0.106 (167), 2021 -0.072 (184), 2022 -0.160 (164), 2023 -0.038 (173), 2024 -0.158 (188), 2025 +0.005 (175), 2026 +0.120 (158).

Sensibilidad (R neto medio y t): colchón 0 % -0.072 (t -2.73), colchón 50 % -0.046 (t -1.78), objetivo 1,5:1 -0.036 (t -1.14), objetivo 2:1 -0.036 (t -1.00).

