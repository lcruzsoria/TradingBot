# ORB de 30 min de las 14:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 14:00–14:30 | 1985 | 50.5 | -0.019 | -1.02 | +0.011 | 0.030 | no |
| 14:15–14:45 | 1989 | 48.5 | -0.035 | -1.92 | -0.005 | 0.031 | no |
| 14:30–15:00 | 1980 | 48.1 | -0.049 | -2.68 | -0.018 | 0.031 | no |
| 14:45–15:15 | 1945 | 48.5 | -0.042 | -2.43 | -0.013 | 0.030 | no |

## Detalle

### ORB 14:00–14:30

Rotura con cuerpo desde las 14:30 hasta las 20:30; a esa hora se cierra. ORB completos: 2025; con rotura: 1985.

**No pasa los criterios**. Coste medio 0.030 R; ancho medio del ORB 0.35 %; cómo terminan: objetivo 612, stop 607, por tiempo 766.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1985 | 50.5 % | -0.019 | -37.7 | 0.95 | -63.2 | -1.02 |
| Sin costes | 1985 | 51.4 % | +0.011 | +21.5 | 1.03 | -30.8 | +0.58 |
| Long | 1111 | 51.9 % | -0.000 | -0.4 | 1.00 | -22.4 | -0.02 |
| Short | 874 | 48.6 % | -0.043 | -37.2 | 0.90 | -58.7 | -1.49 |
| 1.ª mitad | 993 | 50.4 % | -0.034 | -33.8 | 0.92 | -54.7 | -1.26 |
| 2.ª mitad | 992 | 50.6 % | -0.004 | -3.9 | 0.99 | -23.4 | -0.15 |

Por año (R neto medio y operaciones): 2018 +0.172 (72), 2019 -0.103 (245), 2020 +0.000 (247), 2021 -0.104 (244), 2022 -0.002 (246), 2023 +0.032 (241), 2024 -0.035 (241), 2025 -0.010 (243), 2026 +0.020 (206).

Sensibilidad (R neto medio y t): colchón 0 % -0.007 (t -0.36), colchón 50 % -0.016 (t -0.92), objetivo 1,5:1 -0.019 (t -0.90), objetivo 2:1 -0.011 (t -0.49).

### ORB 14:15–14:45

Rotura con cuerpo desde las 14:45 hasta las 20:45; a esa hora se cierra. ORB completos: 2025; con rotura: 1989.

**No pasa los criterios**. Coste medio 0.031 R; ancho medio del ORB 0.34 %; cómo terminan: objetivo 608, stop 608, por tiempo 773.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1989 | 48.5 % | -0.035 | -70.5 | 0.91 | -82.9 | -1.92 |
| Sin costes | 1989 | 49.4 % | -0.005 | -9.0 | 0.99 | -35.5 | -0.25 |
| Long | 1090 | 50.2 % | -0.019 | -21.1 | 0.95 | -44.6 | -0.79 |
| Short | 899 | 46.5 % | -0.055 | -49.4 | 0.87 | -67.9 | -1.97 |
| 1.ª mitad | 995 | 49.0 % | -0.035 | -34.5 | 0.91 | -53.8 | -1.30 |
| 2.ª mitad | 994 | 48.0 % | -0.036 | -36.0 | 0.90 | -39.0 | -1.42 |

Por año (R neto medio y operaciones): 2018 +0.077 (71), 2019 -0.080 (244), 2020 +0.010 (247), 2021 -0.119 (247), 2022 -0.001 (249), 2023 -0.038 (240), 2024 -0.037 (242), 2025 -0.017 (243), 2026 -0.034 (206).

Sensibilidad (R neto medio y t): colchón 0 % -0.051 (t -2.60), colchón 50 % -0.034 (t -2.01), objetivo 1,5:1 -0.038 (t -1.86), objetivo 2:1 -0.030 (t -1.37).

### ORB 14:30–15:00

Rotura con cuerpo desde las 15:00 hasta las 21:00; a esa hora se cierra. ORB completos: 2026; con rotura: 1980.

**No pasa los criterios**. Coste medio 0.031 R; ancho medio del ORB 0.34 %; cómo terminan: objetivo 567, stop 595, por tiempo 818.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1980 | 48.1 % | -0.049 | -96.6 | 0.87 | -118.5 | -2.68 |
| Sin costes | 1980 | 49.1 % | -0.018 | -35.4 | 0.95 | -67.8 | -0.98 |
| Long | 1039 | 50.3 % | -0.020 | -21.0 | 0.95 | -35.3 | -0.81 |
| Short | 941 | 45.6 % | -0.080 | -75.7 | 0.80 | -86.5 | -3.01 |
| 1.ª mitad | 990 | 48.5 % | -0.053 | -52.8 | 0.87 | -65.9 | -2.03 |
| 2.ª mitad | 990 | 47.7 % | -0.044 | -43.8 | 0.88 | -60.5 | -1.75 |

Por año (R neto medio y operaciones): 2018 +0.014 (72), 2019 -0.058 (244), 2020 -0.095 (249), 2021 -0.077 (246), 2022 -0.019 (244), 2023 -0.076 (235), 2024 -0.086 (239), 2025 -0.004 (245), 2026 +0.016 (206).

Sensibilidad (R neto medio y t): colchón 0 % -0.066 (t -3.41), colchón 50 % -0.040 (t -2.37), objetivo 1,5:1 -0.041 (t -2.00), objetivo 2:1 -0.035 (t -1.62).

### ORB 14:45–15:15

Rotura con cuerpo desde las 15:15 hasta las 21:15; a esa hora se cierra. ORB completos: 2026; con rotura: 1945.

**No pasa los criterios**. Coste medio 0.030 R; ancho medio del ORB 0.35 %; cómo terminan: objetivo 495, stop 499, por tiempo 951.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1945 | 48.5 % | -0.042 | -82.5 | 0.88 | -91.3 | -2.43 |
| Sin costes | 1945 | 49.7 % | -0.013 | -24.8 | 0.96 | -54.0 | -0.73 |
| Long | 1026 | 50.3 % | -0.019 | -19.4 | 0.94 | -26.8 | -0.79 |
| Short | 919 | 46.5 % | -0.069 | -63.1 | 0.82 | -69.7 | -2.69 |
| 1.ª mitad | 973 | 48.7 % | -0.039 | -38.1 | 0.89 | -52.4 | -1.58 |
| 2.ª mitad | 972 | 48.3 % | -0.046 | -44.4 | 0.87 | -48.2 | -1.87 |

Por año (R neto medio y operaciones): 2018 +0.030 (68), 2019 -0.065 (243), 2020 -0.043 (249), 2021 -0.072 (241), 2022 +0.000 (238), 2023 -0.086 (230), 2024 -0.054 (236), 2025 +0.028 (236), 2026 -0.073 (204).

Sensibilidad (R neto medio y t): colchón 0 % -0.058 (t -3.10), colchón 50 % -0.038 (t -2.37), objetivo 1,5:1 -0.034 (t -1.75), objetivo 2:1 -0.022 (t -1.06).

