# ORB de 30 min de las 22:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 22:00–22:30 | 1353 | 50.8 | -0.053 | -2.03 | +0.018 | 0.072 | no |
| 22:15–22:45 | 1335 | 52.1 | -0.037 | -1.39 | +0.038 | 0.075 | no |
| 22:30–23:00 | 1333 | 50.1 | -0.069 | -2.58 | +0.011 | 0.079 | no |
| 22:45–23:15 | 1335 | 51.8 | -0.038 | -1.40 | +0.045 | 0.082 | no |

## Detalle

### ORB 22:00–22:30

Rotura con cuerpo desde las 22:30 hasta las 04:30 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.072 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 623, stop 605, por tiempo 125.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1353 | 50.8 % | -0.053 | -72.2 | 0.89 | -98.1 | -2.03 |
| Sin costes | 1353 | 51.1 % | +0.018 | +24.9 | 1.04 | -33.7 | +0.70 |
| Long | 779 | 53.4 % | -0.012 | -9.2 | 0.98 | -29.0 | -0.34 |
| Short | 574 | 47.2 % | -0.110 | -63.0 | 0.79 | -76.4 | -2.73 |
| 1.ª mitad | 677 | 50.1 % | -0.059 | -40.3 | 0.88 | -60.9 | -1.63 |
| 2.ª mitad | 676 | 51.5 % | -0.047 | -31.9 | 0.91 | -45.4 | -1.25 |

Por año (R neto medio y operaciones): 2018 +0.149 (49), 2019 -0.157 (166), 2020 -0.066 (165), 2021 -0.070 (167), 2022 -0.042 (156), 2023 -0.049 (171), 2024 -0.109 (163), 2025 +0.029 (163), 2026 -0.019 (153).

Sensibilidad (R neto medio y t): colchón 0 % -0.083 (t -3.12), colchón 50 % -0.051 (t -2.01), objetivo 1,5:1 -0.043 (t -1.38), objetivo 2:1 -0.040 (t -1.17).

### ORB 22:15–22:45

Rotura con cuerpo desde las 22:45 hasta las 04:45 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2089.

**No pasa los criterios**. Coste medio 0.075 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 647, stop 598, por tiempo 90.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1335 | 52.1 % | -0.037 | -49.3 | 0.93 | -73.7 | -1.39 |
| Sin costes | 1335 | 52.2 % | +0.038 | +50.8 | 1.08 | -47.6 | +1.43 |
| Long | 781 | 53.9 % | -0.013 | -9.8 | 0.97 | -33.4 | -0.36 |
| Short | 554 | 49.5 % | -0.071 | -39.5 | 0.86 | -52.1 | -1.73 |
| 1.ª mitad | 668 | 51.3 % | -0.046 | -30.7 | 0.91 | -72.4 | -1.23 |
| 2.ª mitad | 667 | 52.8 % | -0.028 | -18.6 | 0.94 | -37.3 | -0.74 |

Por año (R neto medio y operaciones): 2018 +0.110 (47), 2019 -0.115 (151), 2020 -0.110 (174), 2021 -0.122 (163), 2022 +0.120 (155), 2023 -0.098 (167), 2024 -0.040 (167), 2025 -0.038 (161), 2026 +0.084 (150).

Sensibilidad (R neto medio y t): colchón 0 % -0.053 (t -1.98), colchón 50 % -0.023 (t -0.88), objetivo 1,5:1 -0.032 (t -1.01), objetivo 2:1 -0.006 (t -0.18).

### ORB 22:30–23:00

Rotura con cuerpo desde las 23:00 hasta las 05:00 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.079 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 640, stop 620, por tiempo 73.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1333 | 50.1 % | -0.069 | -91.8 | 0.87 | -107.9 | -2.58 |
| Sin costes | 1333 | 50.3 % | +0.011 | +14.1 | 1.02 | -41.3 | +0.39 |
| Long | 785 | 51.7 % | -0.053 | -41.2 | 0.90 | -53.0 | -1.50 |
| Short | 548 | 47.8 % | -0.092 | -50.6 | 0.82 | -64.9 | -2.22 |
| 1.ª mitad | 667 | 49.9 % | -0.071 | -47.6 | 0.86 | -67.6 | -1.91 |
| 2.ª mitad | 666 | 50.3 % | -0.066 | -44.2 | 0.87 | -58.0 | -1.73 |

Por año (R neto medio y operaciones): 2018 -0.019 (49), 2019 -0.129 (145), 2020 -0.087 (169), 2021 -0.136 (160), 2022 +0.030 (162), 2023 -0.135 (154), 2024 -0.143 (166), 2025 -0.041 (172), 2026 +0.071 (156).

Sensibilidad (R neto medio y t): colchón 0 % -0.078 (t -2.90), colchón 50 % -0.024 (t -0.94), objetivo 1,5:1 -0.037 (t -1.14), objetivo 2:1 -0.012 (t -0.33).

### ORB 22:45–23:15

Rotura con cuerpo desde las 23:15 hasta las 05:15 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.082 R; ancho medio del ORB 0.14 %; cómo terminan: objetivo 667, stop 607, por tiempo 61.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1335 | 51.8 % | -0.038 | -50.3 | 0.92 | -79.5 | -1.40 |
| Sin costes | 1335 | 51.9 % | +0.045 | +59.5 | 1.10 | -20.0 | +1.66 |
| Long | 772 | 53.5 % | -0.015 | -11.3 | 0.97 | -44.4 | -0.42 |
| Short | 563 | 49.4 % | -0.069 | -38.9 | 0.87 | -58.6 | -1.67 |
| 1.ª mitad | 668 | 51.3 % | -0.043 | -28.6 | 0.91 | -35.1 | -1.13 |
| 2.ª mitad | 667 | 52.2 % | -0.032 | -21.7 | 0.94 | -61.0 | -0.85 |

Por año (R neto medio y operaciones): 2018 -0.160 (55), 2019 -0.132 (151), 2020 +0.012 (169), 2021 +0.010 (152), 2022 +0.006 (170), 2023 -0.127 (152), 2024 -0.128 (165), 2025 -0.077 (167), 2026 +0.176 (154).

Sensibilidad (R neto medio y t): colchón 0 % -0.063 (t -2.32), colchón 50 % -0.045 (t -1.70), objetivo 1,5:1 -0.029 (t -0.88), objetivo 2:1 -0.008 (t -0.21).

