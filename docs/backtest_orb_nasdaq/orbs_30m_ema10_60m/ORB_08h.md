# ORB de 30 min de las 08:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 08:00–08:30 | 1585 | 49.9 | -0.039 | -1.60 | -0.001 | 0.039 | no |
| 08:15–08:45 | 1630 | 47.5 | -0.080 | -3.38 | -0.047 | 0.033 | no |
| 08:30–09:00 | 1674 | 47.1 | -0.084 | -3.61 | -0.053 | 0.031 | no |
| 08:45–09:15 | 1587 | 50.6 | -0.019 | -0.79 | +0.014 | 0.034 | no |

## Detalle

### ORB 08:00–08:30

Rotura con cuerpo desde las 08:30 hasta las 14:30; a esa hora se cierra. ORB completos: 2095; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.039 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 757, stop 755, por tiempo 73.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1585 | 49.9 % | -0.039 | -62.5 | 0.92 | -76.2 | -1.60 |
| Sin costes | 1585 | 49.9 % | -0.001 | -1.4 | 1.00 | -31.2 | -0.03 |
| Long | 840 | 49.0 % | -0.068 | -57.1 | 0.87 | -61.3 | -2.01 |
| Short | 745 | 50.9 % | -0.007 | -5.4 | 0.99 | -35.6 | -0.20 |
| 1.ª mitad | 793 | 49.9 % | -0.044 | -34.7 | 0.91 | -57.0 | -1.25 |
| 2.ª mitad | 792 | 49.9 % | -0.035 | -27.8 | 0.93 | -47.9 | -1.01 |

Por año (R neto medio y operaciones): 2018 -0.092 (50), 2019 -0.061 (196), 2020 -0.075 (194), 2021 -0.111 (191), 2022 +0.083 (190), 2023 -0.010 (196), 2024 -0.061 (208), 2025 -0.057 (196), 2026 -0.001 (164).

Sensibilidad (R neto medio y t): colchón 0 % -0.040 (t -1.63), colchón 50 % -0.017 (t -0.69), objetivo 1,5:1 -0.052 (t -1.77), objetivo 2:1 -0.063 (t -1.87).

### ORB 08:15–08:45

Rotura con cuerpo desde las 08:45 hasta las 14:45; a esa hora se cierra. ORB completos: 2095; con rotura: 2085.

**No pasa los criterios**. Coste medio 0.033 R; ancho medio del ORB 0.34 %; cómo terminan: objetivo 683, stop 767, por tiempo 180.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1630 | 47.5 % | -0.080 | -130.0 | 0.84 | -134.2 | -3.38 |
| Sin costes | 1630 | 47.8 % | -0.047 | -76.8 | 0.90 | -82.7 | -2.00 |
| Long | 841 | 47.6 % | -0.088 | -74.1 | 0.83 | -79.2 | -2.68 |
| Short | 789 | 47.5 % | -0.071 | -55.9 | 0.86 | -66.5 | -2.09 |
| 1.ª mitad | 815 | 48.1 % | -0.068 | -55.4 | 0.87 | -60.8 | -2.02 |
| 2.ª mitad | 815 | 47.0 % | -0.092 | -74.7 | 0.82 | -83.4 | -2.77 |

Por año (R neto medio y operaciones): 2018 -0.101 (49), 2019 -0.092 (201), 2020 -0.126 (194), 2021 -0.036 (194), 2022 +0.019 (208), 2023 -0.057 (212), 2024 -0.157 (212), 2025 -0.089 (199), 2026 -0.100 (161).

Sensibilidad (R neto medio y t): colchón 0 % -0.090 (t -3.75), colchón 50 % -0.053 (t -2.31), objetivo 1,5:1 -0.112 (t -4.04), objetivo 2:1 -0.096 (t -3.09).

### ORB 08:30–09:00

Rotura con cuerpo desde las 09:00 hasta las 15:00; a esa hora se cierra. ORB completos: 2095; con rotura: 2088.

**No pasa los criterios**. Coste medio 0.031 R; ancho medio del ORB 0.35 %; cómo terminan: objetivo 693, stop 785, por tiempo 196.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1674 | 47.1 % | -0.084 | -140.6 | 0.83 | -147.9 | -3.61 |
| Sin costes | 1674 | 47.3 % | -0.053 | -88.7 | 0.89 | -96.7 | -2.28 |
| Long | 881 | 46.8 % | -0.101 | -89.4 | 0.80 | -92.7 | -3.17 |
| Short | 793 | 47.5 % | -0.065 | -51.1 | 0.87 | -59.4 | -1.91 |
| 1.ª mitad | 837 | 48.7 % | -0.055 | -45.6 | 0.89 | -63.2 | -1.65 |
| 2.ª mitad | 837 | 45.5 % | -0.113 | -94.9 | 0.78 | -97.1 | -3.48 |

Por año (R neto medio y operaciones): 2018 -0.132 (57), 2019 -0.075 (203), 2020 -0.099 (199), 2021 -0.027 (196), 2022 +0.004 (210), 2023 -0.118 (212), 2024 -0.112 (213), 2025 -0.089 (219), 2026 -0.153 (165).

Sensibilidad (R neto medio y t): colchón 0 % -0.092 (t -3.92), colchón 50 % -0.065 (t -2.87), objetivo 1,5:1 -0.073 (t -2.64), objetivo 2:1 -0.050 (t -1.61).

### ORB 08:45–09:15

Rotura con cuerpo desde las 09:15 hasta las 15:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.034 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 756, stop 741, por tiempo 90.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1587 | 50.6 % | -0.019 | -30.7 | 0.96 | -49.3 | -0.79 |
| Sin costes | 1587 | 50.7 % | +0.014 | +22.9 | 1.03 | -27.8 | +0.59 |
| Long | 847 | 51.4 % | -0.006 | -4.8 | 0.99 | -25.6 | -0.17 |
| Short | 740 | 49.7 % | -0.035 | -25.9 | 0.93 | -36.4 | -0.97 |
| 1.ª mitad | 794 | 50.6 % | -0.025 | -19.6 | 0.95 | -36.9 | -0.71 |
| 2.ª mitad | 793 | 50.6 % | -0.014 | -11.1 | 0.97 | -27.1 | -0.40 |

Por año (R neto medio y operaciones): 2018 -0.301 (58), 2019 +0.046 (209), 2020 +0.038 (190), 2021 -0.096 (196), 2022 +0.034 (186), 2023 -0.031 (197), 2024 -0.067 (200), 2025 +0.055 (196), 2026 -0.058 (155).

Sensibilidad (R neto medio y t): colchón 0 % -0.035 (t -1.42), colchón 50 % -0.007 (t -0.27), objetivo 1,5:1 -0.022 (t -0.75), objetivo 2:1 -0.032 (t -0.95).

