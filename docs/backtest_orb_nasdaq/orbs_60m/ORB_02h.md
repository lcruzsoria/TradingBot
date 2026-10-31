# ORB de 60 min de las 02:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 02:00–03:00 | 2086 | 49.2 | -0.047 | -2.36 | -0.006 | 0.041 | no |
| 02:15–03:15 | 2085 | 48.8 | -0.035 | -1.84 | +0.002 | 0.037 | no |
| 02:30–03:30 | 2072 | 48.8 | -0.032 | -1.69 | +0.003 | 0.034 | no |
| 02:45–03:45 | 2084 | 50.2 | -0.018 | -0.89 | +0.015 | 0.032 | no |

## Detalle

### ORB 02:00–03:00

Rotura con cuerpo desde las 03:00 hasta las 09:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2086.

**No pasa los criterios**. Coste medio 0.041 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 817, stop 826, por tiempo 443.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2086 | 49.2 % | -0.047 | -98.0 | 0.90 | -115.1 | -2.36 |
| Sin costes | 2086 | 49.5 % | -0.006 | -12.1 | 0.99 | -61.6 | -0.29 |
| Long | 1096 | 50.3 % | -0.031 | -33.6 | 0.93 | -45.1 | -1.12 |
| Short | 990 | 48.1 % | -0.065 | -64.4 | 0.86 | -77.2 | -2.23 |
| 1.ª mitad | 1043 | 49.4 % | -0.035 | -36.8 | 0.92 | -54.3 | -1.28 |
| 2.ª mitad | 1043 | 49.1 % | -0.059 | -61.2 | 0.88 | -81.0 | -2.04 |

Por año (R neto medio y operaciones): 2018 -0.016 (76), 2019 -0.099 (257), 2020 -0.039 (250), 2021 -0.033 (259), 2022 -0.021 (257), 2023 +0.050 (258), 2024 -0.140 (258), 2025 -0.135 (256), 2026 +0.048 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.051 (t -2.49), colchón 50 % -0.057 (t -3.03), objetivo 1,5:1 -0.068 (t -3.01), objetivo 2:1 -0.066 (t -2.68).

### ORB 02:15–03:15

Rotura con cuerpo desde las 03:15 hasta las 09:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2085.

**No pasa los criterios**. Coste medio 0.037 R; ancho medio del ORB 0.29 %; cómo terminan: objetivo 770, stop 753, por tiempo 562.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2085 | 48.8 % | -0.035 | -73.8 | 0.92 | -92.7 | -1.84 |
| Sin costes | 2085 | 49.5 % | +0.002 | +3.4 | 1.00 | -53.6 | +0.08 |
| Long | 1123 | 49.7 % | -0.013 | -14.4 | 0.97 | -50.2 | -0.49 |
| Short | 962 | 47.7 % | -0.062 | -59.4 | 0.86 | -67.5 | -2.17 |
| 1.ª mitad | 1043 | 50.2 % | -0.004 | -4.5 | 0.99 | -29.0 | -0.16 |
| 2.ª mitad | 1042 | 47.3 % | -0.067 | -69.3 | 0.86 | -83.3 | -2.37 |

Por año (R neto medio y operaciones): 2018 -0.009 (76), 2019 -0.033 (257), 2020 -0.002 (251), 2021 -0.013 (258), 2022 -0.037 (256), 2023 -0.007 (258), 2024 -0.156 (258), 2025 -0.062 (256), 2026 +0.031 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.026 (t -1.32), colchón 50 % -0.036 (t -2.03), objetivo 1,5:1 -0.049 (t -2.24), objetivo 2:1 -0.040 (t -1.69).

### ORB 02:30–03:30

Rotura con cuerpo desde las 03:30 hasta las 09:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2072.

**No pasa los criterios**. Coste medio 0.034 R; ancho medio del ORB 0.32 %; cómo terminan: objetivo 722, stop 695, por tiempo 655.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2072 | 48.8 % | -0.032 | -65.9 | 0.92 | -83.8 | -1.69 |
| Sin costes | 2072 | 49.6 % | +0.003 | +5.5 | 1.01 | -45.2 | +0.14 |
| Long | 1107 | 49.6 % | -0.012 | -13.4 | 0.97 | -45.4 | -0.47 |
| Short | 965 | 48.0 % | -0.054 | -52.6 | 0.87 | -59.2 | -1.97 |
| 1.ª mitad | 1036 | 49.8 % | -0.000 | -0.1 | 1.00 | -19.7 | -0.00 |
| 2.ª mitad | 1036 | 47.9 % | -0.064 | -65.8 | 0.86 | -70.4 | -2.30 |

Por año (R neto medio y operaciones): 2018 +0.017 (76), 2019 -0.021 (257), 2020 +0.014 (249), 2021 +0.028 (256), 2022 -0.073 (254), 2023 -0.026 (254), 2024 -0.089 (257), 2025 -0.066 (254), 2026 -0.035 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.038 (t -1.95), colchón 50 % -0.029 (t -1.70), objetivo 1,5:1 -0.028 (t -1.32), objetivo 2:1 -0.019 (t -0.85).

### ORB 02:45–03:45

Rotura con cuerpo desde las 03:45 hasta las 09:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2084.

**No pasa los criterios**. Coste medio 0.032 R; ancho medio del ORB 0.34 %; cómo terminan: objetivo 813, stop 789, por tiempo 482.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2084 | 50.2 % | -0.018 | -36.7 | 0.96 | -54.0 | -0.89 |
| Sin costes | 2084 | 50.5 % | +0.015 | +30.9 | 1.04 | -36.5 | +0.75 |
| Long | 1138 | 51.6 % | +0.000 | +0.0 | 1.00 | -31.1 | +0.00 |
| Short | 946 | 48.5 % | -0.039 | -36.7 | 0.91 | -56.9 | -1.32 |
| 1.ª mitad | 1042 | 50.2 % | -0.020 | -20.5 | 0.95 | -53.4 | -0.73 |
| 2.ª mitad | 1042 | 50.2 % | -0.016 | -16.2 | 0.97 | -27.7 | -0.54 |

Por año (R neto medio y operaciones): 2018 +0.114 (76), 2019 -0.114 (257), 2020 -0.034 (251), 2021 +0.027 (258), 2022 -0.025 (257), 2023 +0.005 (256), 2024 +0.024 (257), 2025 -0.002 (257), 2026 -0.070 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.032 (t -1.54), colchón 50 % -0.009 (t -0.47), objetivo 1,5:1 +0.005 (t +0.24), objetivo 2:1 +0.005 (t +0.20).

