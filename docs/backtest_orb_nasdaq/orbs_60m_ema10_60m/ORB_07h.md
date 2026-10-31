# ORB de 60 min de las 07:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 07:00–08:00 | 1772 | 50.8 | -0.022 | -0.97 | +0.011 | 0.033 | no |
| 07:15–08:15 | 1746 | 50.2 | -0.029 | -1.24 | +0.003 | 0.032 | no |
| 07:30–08:30 | 1748 | 50.3 | -0.027 | -1.18 | +0.002 | 0.029 | no |
| 07:45–08:45 | 1778 | 48.3 | -0.057 | -2.56 | -0.031 | 0.026 | no |

## Detalle

### ORB 07:00–08:00

Rotura con cuerpo desde las 08:00 hasta las 14:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.033 R; ancho medio del ORB 0.31 %; cómo terminan: objetivo 828, stop 815, por tiempo 129.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1772 | 50.8 % | -0.022 | -39.5 | 0.95 | -73.7 | -0.97 |
| Sin costes | 1772 | 50.8 % | +0.011 | +19.1 | 1.02 | -38.0 | +0.47 |
| Long | 953 | 51.2 % | -0.022 | -20.6 | 0.96 | -40.1 | -0.68 |
| Short | 819 | 50.3 % | -0.023 | -18.9 | 0.95 | -54.1 | -0.68 |
| 1.ª mitad | 886 | 52.4 % | +0.007 | +6.4 | 1.02 | -30.5 | +0.22 |
| 2.ª mitad | 886 | 49.2 % | -0.052 | -45.9 | 0.90 | -51.9 | -1.59 |

Por año (R neto medio y operaciones): 2018 +0.218 (62), 2019 -0.003 (209), 2020 +0.001 (217), 2021 -0.051 (219), 2022 +0.028 (216), 2023 -0.157 (229), 2024 -0.003 (217), 2025 +0.025 (220), 2026 -0.091 (183).

Sensibilidad (R neto medio y t): colchón 0 % -0.040 (t -1.72), colchón 50 % -0.036 (t -1.61), objetivo 1,5:1 -0.048 (t -1.75), objetivo 2:1 -0.021 (t -0.68).

### ORB 07:15–08:15

Rotura con cuerpo desde las 08:15 hasta las 14:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.032 R; ancho medio del ORB 0.31 %; cómo terminan: objetivo 809, stop 812, por tiempo 125.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1746 | 50.2 % | -0.029 | -50.3 | 0.94 | -78.2 | -1.24 |
| Sin costes | 1746 | 50.3 % | +0.003 | +4.8 | 1.01 | -45.2 | +0.12 |
| Long | 930 | 51.7 % | -0.013 | -12.1 | 0.97 | -41.7 | -0.41 |
| Short | 816 | 48.5 % | -0.047 | -38.2 | 0.91 | -61.8 | -1.38 |
| 1.ª mitad | 873 | 50.9 % | -0.017 | -14.9 | 0.96 | -47.1 | -0.52 |
| 2.ª mitad | 873 | 49.6 % | -0.041 | -35.4 | 0.92 | -53.3 | -1.23 |

Por año (R neto medio y operaciones): 2018 +0.244 (61), 2019 +0.013 (213), 2020 -0.077 (217), 2021 -0.068 (209), 2022 +0.034 (213), 2023 -0.005 (220), 2024 -0.186 (217), 2025 +0.016 (218), 2026 -0.036 (178).

Sensibilidad (R neto medio y t): colchón 0 % -0.026 (t -1.12), colchón 50 % -0.025 (t -1.10), objetivo 1,5:1 -0.020 (t -0.72), objetivo 2:1 -0.032 (t -1.05).

### ORB 07:30–08:30

Rotura con cuerpo desde las 08:30 hasta las 14:30; a esa hora se cierra. ORB completos: 2095; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.029 R; ancho medio del ORB 0.31 %; cómo terminan: objetivo 797, stop 799, por tiempo 152.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1748 | 50.3 % | -0.027 | -47.5 | 0.94 | -72.4 | -1.18 |
| Sin costes | 1748 | 50.3 % | +0.002 | +3.6 | 1.00 | -45.5 | +0.09 |
| Long | 919 | 50.7 % | -0.034 | -31.2 | 0.93 | -49.8 | -1.07 |
| Short | 829 | 49.8 % | -0.020 | -16.4 | 0.96 | -40.7 | -0.59 |
| 1.ª mitad | 874 | 49.7 % | -0.042 | -37.1 | 0.91 | -63.0 | -1.30 |
| 2.ª mitad | 874 | 50.9 % | -0.012 | -10.4 | 0.98 | -37.3 | -0.37 |

Por año (R neto medio y operaciones): 2018 +0.022 (58), 2019 -0.054 (218), 2020 -0.014 (217), 2021 -0.168 (206), 2022 +0.031 (213), 2023 +0.038 (215), 2024 -0.066 (225), 2025 +0.043 (216), 2026 -0.048 (180).

Sensibilidad (R neto medio y t): colchón 0 % -0.018 (t -0.75), colchón 50 % -0.025 (t -1.10), objetivo 1,5:1 -0.038 (t -1.37), objetivo 2:1 -0.030 (t -0.97).

### ORB 07:45–08:45

Rotura con cuerpo desde las 08:45 hasta las 14:45; a esa hora se cierra. ORB completos: 2095; con rotura: 2083.

**No pasa los criterios**. Coste medio 0.026 R; ancho medio del ORB 0.41 %; cómo terminan: objetivo 726, stop 785, por tiempo 267.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1778 | 48.3 % | -0.057 | -101.1 | 0.88 | -107.3 | -2.56 |
| Sin costes | 1778 | 48.5 % | -0.031 | -55.7 | 0.93 | -62.9 | -1.41 |
| Long | 915 | 49.3 % | -0.053 | -48.5 | 0.89 | -51.7 | -1.71 |
| Short | 863 | 47.3 % | -0.061 | -52.6 | 0.87 | -60.7 | -1.91 |
| 1.ª mitad | 889 | 48.1 % | -0.058 | -51.5 | 0.88 | -62.3 | -1.83 |
| 2.ª mitad | 889 | 48.5 % | -0.056 | -49.6 | 0.88 | -57.4 | -1.79 |

Por año (R neto medio y operaciones): 2018 +0.056 (53), 2019 -0.058 (227), 2020 -0.075 (213), 2021 -0.108 (212), 2022 +0.007 (224), 2023 -0.071 (220), 2024 -0.096 (229), 2025 +0.015 (220), 2026 -0.107 (180).

Sensibilidad (R neto medio y t): colchón 0 % -0.054 (t -2.36), colchón 50 % -0.047 (t -2.18), objetivo 1,5:1 -0.068 (t -2.63), objetivo 2:1 -0.053 (t -1.84).

