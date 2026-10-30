# ORB de 30 min de las 13:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 13:00–13:30 | 2003 | 49.7 | -0.015 | -0.77 | +0.015 | 0.030 | no |
| 13:15–13:45 | 2003 | 47.8 | -0.043 | -2.20 | -0.012 | 0.031 | no |
| 13:30–14:00 | 2000 | 48.8 | -0.041 | -2.13 | -0.010 | 0.031 | no |
| 13:45–14:15 | 1995 | 49.1 | -0.038 | -1.98 | -0.008 | 0.030 | no |

## Detalle

### ORB 13:00–13:30

Rotura con cuerpo desde las 13:30 hasta las 19:30; a esa hora se cierra. ORB completos: 2025; con rotura: 2003.

**No pasa los criterios**. Coste medio 0.030 R; ancho medio del ORB 0.34 %; cómo terminan: objetivo 727, stop 699, por tiempo 577.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2003 | 49.7 % | -0.015 | -30.3 | 0.96 | -55.5 | -0.77 |
| Sin costes | 2003 | 50.3 % | +0.015 | +29.9 | 1.04 | -38.5 | +0.76 |
| Long | 1117 | 51.0 % | -0.003 | -2.9 | 0.99 | -25.0 | -0.10 |
| Short | 886 | 48.1 % | -0.031 | -27.4 | 0.93 | -41.0 | -1.04 |
| 1.ª mitad | 1002 | 49.1 % | -0.023 | -22.7 | 0.95 | -55.5 | -0.80 |
| 2.ª mitad | 1001 | 50.3 % | -0.008 | -7.6 | 0.98 | -32.5 | -0.28 |

Por año (R neto medio y operaciones): 2018 +0.037 (72), 2019 -0.055 (248), 2020 -0.097 (250), 2021 -0.045 (247), 2022 +0.139 (249), 2023 -0.001 (246), 2024 -0.050 (246), 2025 +0.026 (242), 2026 -0.061 (203).

Sensibilidad (R neto medio y t): colchón 0 % -0.016 (t -0.79), colchón 50 % +0.004 (t +0.23), objetivo 1,5:1 -0.003 (t -0.13), objetivo 2:1 -0.010 (t -0.42).

### ORB 13:15–13:45

Rotura con cuerpo desde las 13:45 hasta las 19:45; a esa hora se cierra. ORB completos: 2026; con rotura: 2003.

**No pasa los criterios**. Coste medio 0.031 R; ancho medio del ORB 0.33 %; cómo terminan: objetivo 707, stop 713, por tiempo 583.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2003 | 47.8 % | -0.043 | -85.9 | 0.90 | -98.9 | -2.20 |
| Sin costes | 2003 | 48.2 % | -0.012 | -24.6 | 0.97 | -44.8 | -0.63 |
| Long | 1084 | 50.0 % | -0.018 | -19.3 | 0.96 | -34.9 | -0.68 |
| Short | 919 | 45.3 % | -0.073 | -66.6 | 0.84 | -76.0 | -2.49 |
| 1.ª mitad | 1002 | 48.2 % | -0.053 | -53.4 | 0.88 | -69.5 | -1.89 |
| 2.ª mitad | 1001 | 47.5 % | -0.033 | -32.5 | 0.92 | -49.2 | -1.21 |

Por año (R neto medio y operaciones): 2018 +0.116 (72), 2019 -0.103 (249), 2020 -0.027 (250), 2021 -0.096 (247), 2022 -0.004 (247), 2023 +0.025 (244), 2024 -0.036 (248), 2025 -0.058 (242), 2026 -0.100 (204).

Sensibilidad (R neto medio y t): colchón 0 % -0.050 (t -2.45), colchón 50 % -0.030 (t -1.64), objetivo 1,5:1 -0.043 (t -1.94), objetivo 2:1 -0.038 (t -1.61).

### ORB 13:30–14:00

Rotura con cuerpo desde las 14:00 hasta las 20:00; a esa hora se cierra. ORB completos: 2025; con rotura: 2000.

**No pasa los criterios**. Coste medio 0.031 R; ancho medio del ORB 0.32 %; cómo terminan: objetivo 704, stop 705, por tiempo 591.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2000 | 48.8 % | -0.041 | -82.7 | 0.90 | -102.8 | -2.13 |
| Sin costes | 2000 | 49.2 % | -0.010 | -20.2 | 0.98 | -66.9 | -0.52 |
| Long | 1058 | 50.7 % | -0.009 | -9.0 | 0.98 | -33.4 | -0.32 |
| Short | 942 | 46.6 % | -0.078 | -73.7 | 0.83 | -86.1 | -2.73 |
| 1.ª mitad | 1000 | 46.8 % | -0.074 | -74.4 | 0.84 | -90.4 | -2.66 |
| 2.ª mitad | 1000 | 50.7 % | -0.008 | -8.3 | 0.98 | -23.7 | -0.31 |

Por año (R neto medio y operaciones): 2018 +0.143 (73), 2019 -0.099 (248), 2020 -0.058 (249), 2021 -0.103 (249), 2022 -0.101 (248), 2023 -0.000 (245), 2024 +0.041 (243), 2025 -0.015 (241), 2026 -0.047 (204).

Sensibilidad (R neto medio y t): colchón 0 % -0.040 (t -1.99), colchón 50 % -0.034 (t -1.88), objetivo 1,5:1 -0.035 (t -1.59), objetivo 2:1 -0.027 (t -1.14).

### ORB 13:45–14:15

Rotura con cuerpo desde las 14:15 hasta las 20:15; a esa hora se cierra. ORB completos: 2025; con rotura: 1995.

**No pasa los criterios**. Coste medio 0.030 R; ancho medio del ORB 0.34 %; cómo terminan: objetivo 651, stop 670, por tiempo 674.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1995 | 49.1 % | -0.038 | -75.1 | 0.91 | -95.9 | -1.98 |
| Sin costes | 1995 | 49.4 % | -0.008 | -15.0 | 0.98 | -51.7 | -0.40 |
| Long | 1082 | 50.9 % | -0.016 | -17.1 | 0.96 | -30.0 | -0.63 |
| Short | 913 | 47.0 % | -0.064 | -58.0 | 0.85 | -71.0 | -2.21 |
| 1.ª mitad | 998 | 47.2 % | -0.073 | -73.1 | 0.83 | -81.4 | -2.67 |
| 2.ª mitad | 997 | 51.1 % | -0.002 | -2.0 | 0.99 | -33.0 | -0.08 |

Por año (R neto medio y operaciones): 2018 -0.000 (72), 2019 -0.124 (247), 2020 +0.010 (249), 2021 -0.137 (246), 2022 -0.050 (245), 2023 +0.034 (247), 2024 -0.052 (239), 2025 -0.009 (245), 2026 +0.027 (205).

Sensibilidad (R neto medio y t): colchón 0 % -0.043 (t -2.16), colchón 50 % -0.038 (t -2.14), objetivo 1,5:1 -0.033 (t -1.57), objetivo 2:1 -0.023 (t -1.02).

