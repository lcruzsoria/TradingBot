# ORB de 15 min de las 15:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 15:00–15:15 | 2000 | 49.1 | -0.054 | -2.80 | -0.016 | 0.038 | no |
| 15:15–15:30 | 2005 | 49.2 | -0.045 | -2.34 | -0.004 | 0.041 | no |
| 15:30–15:45 | 1972 | 51.0 | -0.002 | -0.11 | +0.035 | 0.037 | no |
| 15:45–16:00 | 1776 | 48.8 | -0.018 | -1.14 | +0.012 | 0.030 | no |

## Detalle

### ORB 15:00–15:15

Rotura con cuerpo desde las 15:15 hasta las 21:15; a esa hora se cierra. ORB completos: 2026; con rotura: 2000.

**No pasa los criterios**. Coste medio 0.038 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 670, stop 706, por tiempo 624.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2000 | 49.1 % | -0.054 | -107.9 | 0.87 | -125.2 | -2.80 |
| Sin costes | 2000 | 49.9 % | -0.016 | -31.0 | 0.96 | -72.7 | -0.81 |
| Long | 1042 | 50.8 % | -0.037 | -38.5 | 0.91 | -48.7 | -1.39 |
| Short | 958 | 47.3 % | -0.072 | -69.4 | 0.83 | -89.1 | -2.60 |
| 1.ª mitad | 1000 | 48.7 % | -0.061 | -61.2 | 0.86 | -82.8 | -2.24 |
| 2.ª mitad | 1000 | 49.5 % | -0.047 | -46.6 | 0.89 | -63.0 | -1.71 |

Por año (R neto medio y operaciones): 2018 +0.045 (71), 2019 -0.098 (248), 2020 -0.110 (251), 2021 -0.109 (248), 2022 +0.053 (246), 2023 -0.115 (242), 2024 -0.069 (243), 2025 +0.024 (246), 2026 -0.032 (205).

Sensibilidad (R neto medio y t): colchón 0 % -0.074 (t -3.69), colchón 50 % -0.050 (t -2.81), objetivo 1,5:1 -0.059 (t -2.71), objetivo 2:1 -0.049 (t -2.08).

### ORB 15:15–15:30

Rotura con cuerpo desde las 15:30 hasta las 21:30; a esa hora se cierra. ORB completos: 2026; con rotura: 2005.

**No pasa los criterios**. Coste medio 0.041 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 685, stop 678, por tiempo 642.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2005 | 49.2 % | -0.045 | -89.8 | 0.89 | -117.6 | -2.34 |
| Sin costes | 2005 | 50.0 % | -0.004 | -8.3 | 0.99 | -77.9 | -0.22 |
| Long | 1015 | 51.6 % | -0.020 | -20.6 | 0.95 | -49.8 | -0.76 |
| Short | 990 | 46.7 % | -0.070 | -69.2 | 0.84 | -83.6 | -2.54 |
| 1.ª mitad | 1003 | 49.9 % | -0.050 | -50.0 | 0.88 | -65.2 | -1.85 |
| 2.ª mitad | 1002 | 48.5 % | -0.040 | -39.8 | 0.91 | -52.4 | -1.45 |

Por año (R neto medio y operaciones): 2018 +0.024 (72), 2019 +0.003 (249), 2020 -0.017 (249), 2021 -0.146 (251), 2022 -0.057 (247), 2023 -0.121 (241), 2024 -0.056 (245), 2025 +0.043 (243), 2026 -0.023 (208).

Sensibilidad (R neto medio y t): colchón 0 % -0.058 (t -2.89), colchón 50 % -0.052 (t -2.91), objetivo 1,5:1 -0.045 (t -2.05), objetivo 2:1 -0.038 (t -1.61).

### ORB 15:30–15:45

Rotura con cuerpo desde las 15:45 hasta las 21:45; a esa hora se cierra. ORB completos: 2025; con rotura: 1972.

**No pasa los criterios**. Coste medio 0.037 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 600, stop 535, por tiempo 837.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1972 | 51.0 % | -0.002 | -3.9 | 0.99 | -52.2 | -0.11 |
| Sin costes | 1972 | 52.1 % | +0.035 | +68.2 | 1.10 | -21.7 | +1.92 |
| Long | 1026 | 53.2 % | +0.034 | +35.2 | 1.10 | -21.2 | +1.40 |
| Short | 946 | 48.5 % | -0.041 | -39.1 | 0.89 | -51.6 | -1.56 |
| 1.ª mitad | 986 | 52.2 % | +0.021 | +20.9 | 1.06 | -20.8 | +0.83 |
| 2.ª mitad | 986 | 49.7 % | -0.025 | -24.7 | 0.93 | -38.6 | -0.98 |

Por año (R neto medio y operaciones): 2018 -0.047 (72), 2019 +0.069 (243), 2020 +0.073 (243), 2021 -0.041 (248), 2022 -0.012 (238), 2023 -0.036 (239), 2024 -0.085 (241), 2025 +0.078 (243), 2026 -0.058 (205).

Sensibilidad (R neto medio y t): colchón 0 % -0.015 (t -0.80), colchón 50 % -0.004 (t -0.25), objetivo 1,5:1 +0.002 (t +0.10), objetivo 2:1 +0.005 (t +0.21).

### ORB 15:45–16:00

Rotura con cuerpo desde las 16:00 hasta las 22:00; a esa hora se cierra. ORB completos: 2024; con rotura: 1776.

**No pasa los criterios**. Coste medio 0.030 R; ancho medio del ORB 0.34 %; cómo terminan: objetivo 312, stop 310, por tiempo 1154.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1776 | 48.8 % | -0.018 | -31.9 | 0.94 | -43.3 | -1.14 |
| Sin costes | 1776 | 50.7 % | +0.012 | +21.4 | 1.05 | -33.3 | +0.77 |
| Long | 983 | 51.4 % | +0.005 | +4.5 | 1.02 | -19.6 | +0.22 |
| Short | 793 | 45.6 % | -0.046 | -36.3 | 0.85 | -40.7 | -1.92 |
| 1.ª mitad | 888 | 51.4 % | -0.000 | -0.3 | 1.00 | -18.2 | -0.01 |
| 2.ª mitad | 888 | 46.3 % | -0.036 | -31.6 | 0.88 | -43.3 | -1.60 |

Por año (R neto medio y operaciones): 2018 -0.079 (64), 2019 -0.020 (230), 2020 +0.033 (218), 2021 +0.024 (213), 2022 -0.023 (211), 2023 +0.014 (204), 2024 +0.001 (214), 2025 -0.054 (225), 2026 -0.104 (197).

Sensibilidad (R neto medio y t): colchón 0 % -0.031 (t -1.81), colchón 50 % -0.021 (t -1.47), objetivo 1,5:1 -0.018 (t -1.04), objetivo 2:1 -0.019 (t -1.07).

