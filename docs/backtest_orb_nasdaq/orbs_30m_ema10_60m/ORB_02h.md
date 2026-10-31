# ORB de 30 min de las 02:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 02:00–02:30 | 1553 | 48.8 | -0.074 | -3.09 | -0.021 | 0.053 | no |
| 02:15–02:45 | 1491 | 48.1 | -0.088 | -3.54 | -0.031 | 0.058 | no |
| 02:30–03:00 | 1495 | 48.7 | -0.084 | -3.37 | -0.027 | 0.058 | no |
| 02:45–03:15 | 1622 | 47.9 | -0.073 | -3.18 | -0.028 | 0.045 | no |

## Detalle

### ORB 02:00–02:30

Rotura con cuerpo desde las 02:30 hasta las 08:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.053 R; ancho medio del ORB 0.20 %; cómo terminan: objetivo 667, stop 701, por tiempo 185.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1553 | 48.8 % | -0.074 | -115.6 | 0.85 | -139.3 | -3.09 |
| Sin costes | 1553 | 49.2 % | -0.021 | -32.5 | 0.96 | -72.6 | -0.87 |
| Long | 888 | 50.2 % | -0.054 | -47.5 | 0.89 | -67.0 | -1.69 |
| Short | 665 | 46.9 % | -0.102 | -68.1 | 0.80 | -78.6 | -2.77 |
| 1.ª mitad | 777 | 46.7 % | -0.110 | -85.3 | 0.78 | -95.5 | -3.26 |
| 2.ª mitad | 776 | 50.9 % | -0.039 | -30.3 | 0.92 | -50.3 | -1.13 |

Por año (R neto medio y operaciones): 2018 +0.049 (58), 2019 -0.221 (184), 2020 -0.063 (183), 2021 -0.115 (211), 2022 -0.158 (196), 2023 -0.030 (192), 2024 -0.065 (191), 2025 -0.037 (185), 2026 +0.093 (153).

Sensibilidad (R neto medio y t): colchón 0 % -0.086 (t -3.51), colchón 50 % -0.043 (t -1.85), objetivo 1,5:1 -0.059 (t -2.09), objetivo 2:1 -0.064 (t -2.06).

### ORB 02:15–02:45

Rotura con cuerpo desde las 02:45 hasta las 08:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.058 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 660, stop 706, por tiempo 125.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1491 | 48.1 % | -0.088 | -131.9 | 0.83 | -135.4 | -3.54 |
| Sin costes | 1491 | 48.2 % | -0.031 | -45.9 | 0.94 | -54.1 | -1.23 |
| Long | 841 | 49.9 % | -0.057 | -47.7 | 0.89 | -56.3 | -1.72 |
| Short | 650 | 45.7 % | -0.130 | -84.2 | 0.76 | -89.7 | -3.39 |
| 1.ª mitad | 746 | 46.9 % | -0.102 | -76.2 | 0.80 | -79.2 | -2.93 |
| 2.ª mitad | 745 | 49.3 % | -0.075 | -55.7 | 0.86 | -64.6 | -2.09 |

Por año (R neto medio y operaciones): 2018 -0.152 (57), 2019 -0.165 (185), 2020 -0.061 (186), 2021 -0.118 (195), 2022 -0.058 (176), 2023 +0.029 (185), 2024 -0.101 (185), 2025 -0.147 (177), 2026 -0.060 (145).

Sensibilidad (R neto medio y t): colchón 0 % -0.103 (t -4.07), colchón 50 % -0.063 (t -2.58), objetivo 1,5:1 -0.064 (t -2.17), objetivo 2:1 -0.064 (t -1.97).

### ORB 02:30–03:00

Rotura con cuerpo desde las 03:00 hasta las 09:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.058 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 674, stop 713, por tiempo 108.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1495 | 48.7 % | -0.084 | -126.2 | 0.84 | -132.0 | -3.37 |
| Sin costes | 1495 | 48.8 % | -0.027 | -40.1 | 0.95 | -48.8 | -1.07 |
| Long | 834 | 49.4 % | -0.080 | -66.8 | 0.84 | -73.6 | -2.40 |
| Short | 661 | 47.8 % | -0.090 | -59.4 | 0.83 | -65.1 | -2.37 |
| 1.ª mitad | 748 | 48.7 % | -0.083 | -62.3 | 0.84 | -78.1 | -2.37 |
| 2.ª mitad | 747 | 48.7 % | -0.086 | -64.0 | 0.84 | -71.7 | -2.40 |

Por año (R neto medio y operaciones): 2018 -0.168 (57), 2019 -0.203 (182), 2020 -0.095 (181), 2021 -0.027 (193), 2022 +0.010 (178), 2023 -0.009 (190), 2024 -0.157 (186), 2025 -0.152 (177), 2026 -0.009 (151).

Sensibilidad (R neto medio y t): colchón 0 % -0.088 (t -3.47), colchón 50 % -0.061 (t -2.49), objetivo 1,5:1 -0.068 (t -2.29), objetivo 2:1 -0.066 (t -2.00).

### ORB 02:45–03:15

Rotura con cuerpo desde las 03:15 hasta las 09:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.045 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 659, stop 697, por tiempo 266.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1622 | 47.9 % | -0.073 | -118.8 | 0.85 | -141.0 | -3.18 |
| Sin costes | 1622 | 48.3 % | -0.028 | -46.0 | 0.94 | -81.7 | -1.23 |
| Long | 911 | 49.2 % | -0.052 | -47.2 | 0.89 | -67.2 | -1.69 |
| Short | 711 | 46.3 % | -0.101 | -71.5 | 0.80 | -86.5 | -2.89 |
| 1.ª mitad | 811 | 49.4 % | -0.044 | -35.4 | 0.90 | -39.5 | -1.36 |
| 2.ª mitad | 811 | 46.4 % | -0.103 | -83.4 | 0.80 | -103.3 | -3.11 |

Por año (R neto medio y operaciones): 2018 -0.050 (58), 2019 -0.106 (204), 2020 +0.035 (194), 2021 -0.043 (208), 2022 -0.126 (206), 2023 -0.063 (205), 2024 -0.217 (195), 2025 -0.110 (190), 2026 +0.059 (162).

Sensibilidad (R neto medio y t): colchón 0 % -0.066 (t -2.81), colchón 50 % -0.072 (t -3.30), objetivo 1,5:1 -0.081 (t -3.05), objetivo 2:1 -0.086 (t -3.00).

