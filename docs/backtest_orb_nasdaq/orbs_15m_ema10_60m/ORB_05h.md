# ORB de 15 min de las 05:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 05:00–05:15 | 1324 | 49.7 | -0.077 | -2.82 | -0.006 | 0.071 | no |
| 05:15–05:30 | 1307 | 46.8 | -0.140 | -5.05 | -0.063 | 0.077 | no |
| 05:30–05:45 | 1354 | 47.2 | -0.133 | -4.89 | -0.057 | 0.076 | no |
| 05:45–06:00 | 1297 | 47.1 | -0.137 | -4.94 | -0.057 | 0.080 | no |

## Detalle

### ORB 05:00–05:15

Rotura con cuerpo desde las 05:15 hasta las 11:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.071 R; ancho medio del ORB 0.14 %; cómo terminan: objetivo 655, stop 663, por tiempo 6.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1324 | 49.7 % | -0.077 | -102.4 | 0.86 | -116.0 | -2.82 |
| Sin costes | 1324 | 49.8 % | -0.006 | -8.2 | 0.99 | -48.2 | -0.23 |
| Long | 773 | 48.6 % | -0.103 | -79.8 | 0.81 | -96.3 | -2.89 |
| Short | 551 | 51.2 % | -0.041 | -22.6 | 0.92 | -31.9 | -0.96 |
| 1.ª mitad | 662 | 51.8 % | -0.040 | -26.7 | 0.92 | -37.9 | -1.05 |
| 2.ª mitad | 662 | 47.6 % | -0.114 | -75.7 | 0.80 | -83.2 | -2.94 |

Por año (R neto medio y operaciones): 2018 -0.016 (40), 2019 +0.023 (172), 2020 -0.089 (174), 2021 +0.001 (159), 2022 -0.108 (159), 2023 -0.137 (167), 2024 -0.026 (172), 2025 -0.185 (149), 2026 -0.140 (132).

Sensibilidad (R neto medio y t): colchón 0 % -0.100 (t -3.64), colchón 50 % -0.083 (t -3.02), objetivo 1,5:1 -0.107 (t -3.20), objetivo 2:1 -0.100 (t -2.64).

### ORB 05:15–05:30

Rotura con cuerpo desde las 05:30 hasta las 11:30; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.077 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 611, stop 693, por tiempo 3.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1307 | 46.8 % | -0.140 | -182.4 | 0.76 | -201.0 | -5.05 |
| Sin costes | 1307 | 46.8 % | -0.063 | -82.2 | 0.88 | -111.9 | -2.28 |
| Long | 745 | 46.7 % | -0.150 | -111.8 | 0.74 | -126.4 | -4.10 |
| Short | 562 | 47.0 % | -0.126 | -70.6 | 0.78 | -80.9 | -2.99 |
| 1.ª mitad | 654 | 46.5 % | -0.151 | -98.9 | 0.74 | -111.8 | -3.88 |
| 2.ª mitad | 653 | 47.2 % | -0.128 | -83.5 | 0.77 | -94.3 | -3.27 |

Por año (R neto medio y operaciones): 2018 +0.159 (47), 2019 -0.218 (177), 2020 -0.267 (160), 2021 -0.046 (154), 2022 -0.157 (160), 2023 -0.176 (160), 2024 -0.067 (164), 2025 -0.210 (160), 2026 -0.029 (125).

Sensibilidad (R neto medio y t): colchón 0 % -0.180 (t -6.51), colchón 50 % -0.097 (t -3.53), objetivo 1,5:1 -0.122 (t -3.65), objetivo 2:1 -0.121 (t -3.16).

### ORB 05:30–05:45

Rotura con cuerpo desde las 05:45 hasta las 11:45; a esa hora se cierra. ORB completos: 2098; con rotura: 2098.

**No pasa los criterios**. Coste medio 0.076 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 635, stop 712, por tiempo 7.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1354 | 47.2 % | -0.133 | -179.7 | 0.77 | -186.1 | -4.89 |
| Sin costes | 1354 | 47.2 % | -0.057 | -76.5 | 0.89 | -92.5 | -2.09 |
| Long | 775 | 45.2 % | -0.180 | -139.9 | 0.70 | -140.2 | -5.04 |
| Short | 579 | 49.9 % | -0.069 | -39.9 | 0.87 | -56.8 | -1.66 |
| 1.ª mitad | 677 | 45.8 % | -0.165 | -111.4 | 0.72 | -117.9 | -4.30 |
| 2.ª mitad | 677 | 48.6 % | -0.101 | -68.4 | 0.82 | -74.4 | -2.63 |

Por año (R neto medio y operaciones): 2018 -0.037 (50), 2019 -0.215 (166), 2020 -0.219 (168), 2021 -0.071 (174), 2022 -0.200 (155), 2023 -0.182 (171), 2024 -0.053 (175), 2025 -0.097 (165), 2026 -0.045 (130).

Sensibilidad (R neto medio y t): colchón 0 % -0.126 (t -4.62), colchón 50 % -0.118 (t -4.36), objetivo 1,5:1 -0.142 (t -4.32), objetivo 2:1 -0.178 (t -4.77).

### ORB 05:45–06:00

Rotura con cuerpo desde las 06:00 hasta las 12:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.080 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 609, stop 683, por tiempo 5.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1297 | 47.1 % | -0.137 | -177.5 | 0.76 | -183.9 | -4.94 |
| Sin costes | 1297 | 47.2 % | -0.057 | -73.8 | 0.89 | -85.8 | -2.05 |
| Long | 742 | 45.7 % | -0.175 | -130.0 | 0.70 | -134.4 | -4.79 |
| Short | 555 | 49.0 % | -0.086 | -47.5 | 0.84 | -52.9 | -2.02 |
| 1.ª mitad | 649 | 47.1 % | -0.140 | -90.6 | 0.75 | -95.7 | -3.57 |
| 2.ª mitad | 648 | 47.1 % | -0.134 | -86.9 | 0.76 | -90.1 | -3.42 |

Por año (R neto medio y operaciones): 2018 -0.026 (50), 2019 -0.256 (179), 2020 -0.050 (140), 2021 -0.116 (150), 2022 -0.170 (158), 2023 -0.177 (162), 2024 -0.033 (166), 2025 -0.198 (163), 2026 -0.097 (129).

Sensibilidad (R neto medio y t): colchón 0 % -0.153 (t -5.53), colchón 50 % -0.135 (t -4.87), objetivo 1,5:1 -0.130 (t -3.87), objetivo 2:1 -0.110 (t -2.85).

