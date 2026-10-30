# ORB de 30 min de las 23:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 23:00–23:30 | 1324 | 51.1 | -0.056 | -2.06 | +0.030 | 0.085 | no |
| 23:15–23:45 | 1342 | 49.9 | -0.088 | -3.26 | +0.002 | 0.090 | no |
| 23:30–00:00 | 1350 | 50.2 | -0.088 | -3.26 | +0.007 | 0.095 | no |
| 23:45–00:15 | 1382 | 50.4 | -0.086 | -3.23 | +0.008 | 0.095 | no |

## Detalle

### ORB 23:00–23:30

Rotura con cuerpo desde las 23:30 hasta las 05:30 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.085 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 654, stop 613, por tiempo 57.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1324 | 51.1 % | -0.056 | -73.7 | 0.89 | -126.2 | -2.06 |
| Sin costes | 1324 | 51.4 % | +0.030 | +39.3 | 1.06 | -35.9 | +1.10 |
| Long | 750 | 51.5 % | -0.053 | -39.6 | 0.90 | -69.0 | -1.47 |
| Short | 574 | 50.7 % | -0.059 | -34.1 | 0.88 | -63.3 | -1.45 |
| 1.ª mitad | 662 | 47.4 % | -0.125 | -82.6 | 0.77 | -86.6 | -3.28 |
| 2.ª mitad | 662 | 54.8 % | +0.013 | +8.9 | 1.03 | -52.8 | +0.35 |

Por año (R neto medio y operaciones): 2018 -0.174 (53), 2019 -0.209 (153), 2020 -0.072 (165), 2021 -0.039 (160), 2022 -0.147 (172), 2023 -0.061 (155), 2024 -0.157 (155), 2025 +0.085 (163), 2026 +0.209 (148).

Sensibilidad (R neto medio y t): colchón 0 % -0.053 (t -1.94), colchón 50 % -0.046 (t -1.72), objetivo 1,5:1 -0.038 (t -1.15), objetivo 2:1 -0.038 (t -1.02).

### ORB 23:15–23:45

Rotura con cuerpo desde las 23:45 hasta las 05:45 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2098.

**No pasa los criterios**. Coste medio 0.090 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 647, stop 648, por tiempo 47.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1342 | 49.9 % | -0.088 | -118.0 | 0.83 | -128.2 | -3.26 |
| Sin costes | 1342 | 50.0 % | +0.002 | +3.0 | 1.00 | -46.9 | +0.08 |
| Long | 771 | 51.6 % | -0.064 | -49.5 | 0.88 | -56.6 | -1.80 |
| Short | 571 | 47.5 % | -0.120 | -68.5 | 0.78 | -77.5 | -2.91 |
| 1.ª mitad | 671 | 47.4 % | -0.136 | -91.4 | 0.76 | -95.3 | -3.58 |
| 2.ª mitad | 671 | 52.3 % | -0.040 | -26.7 | 0.92 | -36.4 | -1.04 |

Por año (R neto medio y operaciones): 2018 -0.103 (51), 2019 -0.185 (152), 2020 -0.090 (169), 2021 -0.192 (166), 2022 -0.087 (165), 2023 -0.108 (168), 2024 -0.000 (158), 2025 -0.021 (165), 2026 -0.012 (148).

Sensibilidad (R neto medio y t): colchón 0 % -0.091 (t -3.35), colchón 50 % -0.084 (t -3.17), objetivo 1,5:1 -0.080 (t -2.48), objetivo 2:1 -0.041 (t -1.09).

### ORB 23:30–00:00

Rotura con cuerpo desde las 00:00 hasta las 06:00 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2098.

**No pasa los criterios**. Coste medio 0.095 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 655, stop 649, por tiempo 46.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1350 | 50.2 % | -0.088 | -118.5 | 0.84 | -128.0 | -3.26 |
| Sin costes | 1350 | 50.3 % | +0.007 | +10.0 | 1.02 | -36.4 | +0.28 |
| Long | 764 | 52.0 % | -0.064 | -48.7 | 0.88 | -61.5 | -1.78 |
| Short | 586 | 48.0 % | -0.119 | -69.8 | 0.78 | -75.0 | -2.92 |
| 1.ª mitad | 675 | 48.9 % | -0.120 | -80.7 | 0.78 | -83.3 | -3.13 |
| 2.ª mitad | 675 | 51.6 % | -0.056 | -37.8 | 0.89 | -47.4 | -1.47 |

Por año (R neto medio y operaciones): 2018 -0.145 (45), 2019 -0.180 (162), 2020 -0.051 (175), 2021 -0.146 (167), 2022 -0.133 (172), 2023 -0.148 (157), 2024 +0.017 (157), 2025 -0.046 (163), 2026 +0.011 (152).

Sensibilidad (R neto medio y t): colchón 0 % -0.109 (t -4.01), colchón 50 % -0.062 (t -2.31), objetivo 1,5:1 -0.066 (t -2.03), objetivo 2:1 -0.039 (t -1.05).

### ORB 23:45–00:15

Rotura con cuerpo desde las 00:15 hasta las 06:15 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.095 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 679, stop 665, por tiempo 38.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1382 | 50.4 % | -0.086 | -119.1 | 0.84 | -132.5 | -3.23 |
| Sin costes | 1382 | 50.4 % | +0.008 | +11.7 | 1.02 | -61.0 | +0.32 |
| Long | 779 | 51.1 % | -0.082 | -63.8 | 0.85 | -74.8 | -2.30 |
| Short | 603 | 49.4 % | -0.092 | -55.3 | 0.83 | -72.4 | -2.27 |
| 1.ª mitad | 691 | 48.2 % | -0.126 | -87.1 | 0.77 | -89.0 | -3.36 |
| 2.ª mitad | 691 | 52.5 % | -0.046 | -32.0 | 0.91 | -49.5 | -1.22 |

Por año (R neto medio y operaciones): 2018 -0.134 (45), 2019 -0.073 (153), 2020 -0.019 (168), 2021 -0.282 (179), 2022 -0.147 (178), 2023 -0.181 (165), 2024 +0.037 (162), 2025 -0.023 (181), 2026 +0.040 (151).

Sensibilidad (R neto medio y t): colchón 0 % -0.093 (t -3.46), colchón 50 % -0.071 (t -2.71), objetivo 1,5:1 -0.065 (t -2.01), objetivo 2:1 -0.068 (t -1.85).

