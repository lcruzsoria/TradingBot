# ORB de 45 min de las 23:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 23:00–23:45 | 1399 | 50.0 | -0.059 | -2.28 | +0.012 | 0.071 | no |
| 23:15–00:00 | 1391 | 50.1 | -0.072 | -2.75 | +0.005 | 0.077 | no |
| 23:30–00:15 | 1452 | 50.8 | -0.059 | -2.30 | +0.017 | 0.076 | no |
| 23:45–00:30 | 1408 | 51.3 | -0.049 | -1.88 | +0.029 | 0.078 | no |

## Detalle

### ORB 23:00–23:45

Rotura con cuerpo desde las 23:45 hasta las 05:45 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.071 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 652, stop 635, por tiempo 112.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1399 | 50.0 % | -0.059 | -82.3 | 0.88 | -111.8 | -2.28 |
| Sin costes | 1399 | 50.3 % | +0.012 | +17.2 | 1.03 | -46.1 | +0.47 |
| Long | 791 | 51.6 % | -0.033 | -25.8 | 0.93 | -43.1 | -0.95 |
| Short | 608 | 47.9 % | -0.093 | -56.5 | 0.82 | -74.3 | -2.37 |
| 1.ª mitad | 700 | 46.1 % | -0.127 | -89.1 | 0.76 | -91.6 | -3.51 |
| 2.ª mitad | 699 | 53.8 % | +0.010 | +6.8 | 1.02 | -28.8 | +0.27 |

Por año (R neto medio y operaciones): 2018 -0.242 (56), 2019 -0.126 (158), 2020 -0.087 (174), 2021 -0.063 (170), 2022 -0.185 (176), 2023 -0.019 (170), 2024 -0.013 (162), 2025 +0.014 (176), 2026 +0.079 (157).

Sensibilidad (R neto medio y t): colchón 0 % -0.062 (t -2.38), colchón 50 % -0.045 (t -1.81), objetivo 1,5:1 -0.039 (t -1.26), objetivo 2:1 -0.022 (t -0.63).

### ORB 23:15–00:00

Rotura con cuerpo desde las 00:00 hasta las 06:00 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.077 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 653, stop 653, por tiempo 85.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1391 | 50.1 % | -0.072 | -100.0 | 0.86 | -115.6 | -2.75 |
| Sin costes | 1391 | 50.3 % | +0.005 | +6.5 | 1.01 | -38.7 | +0.18 |
| Long | 784 | 53.6 % | -0.023 | -18.2 | 0.95 | -39.4 | -0.67 |
| Short | 607 | 45.6 % | -0.135 | -81.8 | 0.75 | -87.6 | -3.41 |
| 1.ª mitad | 696 | 48.4 % | -0.107 | -74.8 | 0.80 | -82.4 | -2.91 |
| 2.ª mitad | 695 | 51.8 % | -0.036 | -25.2 | 0.93 | -42.9 | -0.98 |

Por año (R neto medio y operaciones): 2018 -0.065 (47), 2019 -0.146 (163), 2020 -0.046 (183), 2021 -0.147 (172), 2022 -0.109 (180), 2023 -0.078 (164), 2024 -0.033 (163), 2025 -0.041 (168), 2026 +0.036 (151).

Sensibilidad (R neto medio y t): colchón 0 % -0.068 (t -2.56), colchón 50 % -0.045 (t -1.75), objetivo 1,5:1 -0.054 (t -1.73), objetivo 2:1 -0.024 (t -0.69).

### ORB 23:30–00:15

Rotura con cuerpo desde las 00:15 hasta las 06:15 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.076 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 697, stop 669, por tiempo 86.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1452 | 50.8 % | -0.059 | -85.6 | 0.88 | -109.5 | -2.30 |
| Sin costes | 1452 | 50.8 % | +0.017 | +25.1 | 1.04 | -41.1 | +0.68 |
| Long | 820 | 52.2 % | -0.038 | -31.3 | 0.92 | -47.3 | -1.12 |
| Short | 632 | 48.9 % | -0.086 | -54.4 | 0.84 | -73.9 | -2.22 |
| 1.ª mitad | 726 | 48.5 % | -0.105 | -76.0 | 0.80 | -84.4 | -2.88 |
| 2.ª mitad | 726 | 53.0 % | -0.013 | -9.6 | 0.97 | -33.2 | -0.37 |

Por año (R neto medio y operaciones): 2018 +0.002 (50), 2019 -0.118 (162), 2020 -0.032 (178), 2021 -0.186 (189), 2022 -0.120 (183), 2023 -0.105 (168), 2024 +0.063 (172), 2025 -0.013 (195), 2026 +0.034 (155).

Sensibilidad (R neto medio y t): colchón 0 % -0.060 (t -2.34), colchón 50 % -0.045 (t -1.80), objetivo 1,5:1 -0.057 (t -1.84), objetivo 2:1 -0.057 (t -1.65).

### ORB 23:45–00:30

Rotura con cuerpo desde las 00:30 hasta las 06:30 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.078 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 687, stop 648, por tiempo 73.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1408 | 51.3 % | -0.049 | -69.1 | 0.90 | -85.2 | -1.88 |
| Sin costes | 1408 | 51.3 % | +0.029 | +40.1 | 1.06 | -41.1 | +1.09 |
| Long | 789 | 53.4 % | -0.021 | -16.7 | 0.96 | -33.2 | -0.61 |
| Short | 619 | 48.6 % | -0.085 | -52.5 | 0.84 | -60.7 | -2.16 |
| 1.ª mitad | 704 | 49.7 % | -0.080 | -56.5 | 0.85 | -70.9 | -2.18 |
| 2.ª mitad | 704 | 52.8 % | -0.018 | -12.6 | 0.96 | -26.4 | -0.48 |

Por año (R neto medio y operaciones): 2018 -0.083 (49), 2019 -0.096 (155), 2020 +0.057 (168), 2021 -0.202 (173), 2022 -0.083 (180), 2023 -0.094 (164), 2024 +0.051 (172), 2025 +0.010 (190), 2026 -0.032 (157).

Sensibilidad (R neto medio y t): colchón 0 % -0.049 (t -1.88), colchón 50 % -0.048 (t -1.87), objetivo 1,5:1 -0.038 (t -1.21), objetivo 2:1 -0.026 (t -0.73).

