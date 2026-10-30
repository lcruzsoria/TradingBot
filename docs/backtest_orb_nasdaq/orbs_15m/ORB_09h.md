# ORB de 15 min de las 09:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 09:00–09:15 | 2091 | 48.5 | -0.078 | -3.58 | -0.028 | 0.049 | no |
| 09:15–09:30 | 2091 | 51.1 | -0.014 | -0.67 | +0.020 | 0.034 | no |
| 09:30–09:45 | 2086 | 52.5 | +0.021 | +1.14 | +0.038 | 0.017 | no |
| 09:45–10:00 | 2089 | 52.3 | +0.022 | +1.09 | +0.043 | 0.021 | no |

## Detalle

### ORB 09:00–09:15

Rotura con cuerpo desde las 09:15 hasta las 15:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.049 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 997, stop 1058, por tiempo 36.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2091 | 48.5 % | -0.078 | -162.9 | 0.85 | -164.1 | -3.58 |
| Sin costes | 2091 | 48.5 % | -0.028 | -59.4 | 0.94 | -72.3 | -1.31 |
| Long | 1053 | 49.0 % | -0.070 | -73.7 | 0.87 | -75.6 | -2.28 |
| Short | 1038 | 48.1 % | -0.086 | -89.1 | 0.84 | -93.2 | -2.79 |
| 1.ª mitad | 1046 | 46.9 % | -0.113 | -117.8 | 0.80 | -120.7 | -3.67 |
| 2.ª mitad | 1045 | 50.1 % | -0.043 | -45.0 | 0.92 | -58.9 | -1.40 |

Por año (R neto medio y operaciones): 2018 -0.358 (76), 2019 -0.054 (258), 2020 -0.049 (254), 2021 -0.168 (257), 2022 -0.061 (258), 2023 -0.108 (257), 2024 +0.071 (259), 2025 -0.068 (257), 2026 -0.109 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.091 (t -4.18), colchón 50 % -0.069 (t -3.17), objetivo 1,5:1 -0.069 (t -2.62), objetivo 2:1 -0.059 (t -1.96).

### ORB 09:15–09:30

Rotura con cuerpo desde las 09:30 hasta las 15:30; a esa hora se cierra. ORB completos: 2093; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.034 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 1039, stop 995, por tiempo 57.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2091 | 51.1 % | -0.014 | -30.1 | 0.97 | -51.3 | -0.67 |
| Sin costes | 2091 | 51.1 % | +0.020 | +41.5 | 1.04 | -31.4 | +0.92 |
| Long | 1057 | 51.4 % | -0.013 | -13.9 | 0.97 | -36.3 | -0.43 |
| Short | 1034 | 50.9 % | -0.016 | -16.1 | 0.97 | -46.3 | -0.51 |
| 1.ª mitad | 1046 | 49.9 % | -0.038 | -40.2 | 0.92 | -51.3 | -1.26 |
| 2.ª mitad | 1045 | 52.3 % | +0.010 | +10.1 | 1.02 | -28.3 | +0.32 |

Por año (R neto medio y operaciones): 2018 -0.124 (75), 2019 +0.047 (258), 2020 -0.053 (254), 2021 -0.063 (258), 2022 -0.008 (258), 2023 +0.086 (257), 2024 -0.005 (259), 2025 -0.039 (257), 2026 -0.055 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.016 (t -0.74), colchón 50 % -0.015 (t -0.68), objetivo 1,5:1 +0.025 (t +0.95), objetivo 2:1 +0.055 (t +1.82).

### ORB 09:30–09:45

Rotura con cuerpo desde las 09:45 hasta las 15:45; a esa hora se cierra. ORB completos: 2093; con rotura: 2086.

**No pasa los criterios**. Coste medio 0.017 R; ancho medio del ORB 0.53 %; cómo terminan: objetivo 730, stop 687, por tiempo 669.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2086 | 52.5 % | +0.021 | +44.6 | 1.06 | -28.3 | +1.14 |
| Sin costes | 2086 | 52.9 % | +0.038 | +79.9 | 1.10 | -25.7 | +2.04 |
| Long | 1073 | 56.2 % | +0.054 | +58.2 | 1.15 | -12.4 | +2.10 |
| Short | 1013 | 48.7 % | -0.013 | -13.6 | 0.97 | -24.9 | -0.49 |
| 1.ª mitad | 1043 | 51.9 % | -0.000 | -0.5 | 1.00 | -28.3 | -0.02 |
| 2.ª mitad | 1043 | 53.2 % | +0.043 | +45.1 | 1.11 | -15.7 | +1.62 |

Por año (R neto medio y operaciones): 2018 -0.099 (75), 2019 +0.030 (254), 2020 -0.077 (256), 2021 +0.089 (258), 2022 +0.025 (257), 2023 +0.026 (256), 2024 +0.028 (259), 2025 +0.079 (256), 2026 +0.004 (215).

Sensibilidad (R neto medio y t): colchón 0 % +0.024 (t +1.24), colchón 50 % +0.027 (t +1.53), objetivo 1,5:1 +0.030 (t +1.41), objetivo 2:1 +0.042 (t +1.87).

### ORB 09:45–10:00

Rotura con cuerpo desde las 10:00 hasta las 16:00; a esa hora se cierra. ORB completos: 2095; con rotura: 2089.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.43 %; cómo terminan: objetivo 863, stop 795, por tiempo 431.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2089 | 52.3 % | +0.022 | +45.5 | 1.05 | -26.7 | +1.09 |
| Sin costes | 2089 | 52.6 % | +0.043 | +90.0 | 1.10 | -24.8 | +2.15 |
| Long | 1114 | 54.5 % | +0.044 | +49.2 | 1.11 | -21.7 | +1.64 |
| Short | 975 | 49.8 % | -0.004 | -3.8 | 0.99 | -33.7 | -0.13 |
| 1.ª mitad | 1045 | 51.9 % | +0.015 | +15.3 | 1.03 | -26.7 | +0.52 |
| 2.ª mitad | 1044 | 52.8 % | +0.029 | +30.2 | 1.07 | -22.4 | +1.02 |

Por año (R neto medio y operaciones): 2018 -0.125 (75), 2019 +0.111 (257), 2020 -0.008 (258), 2021 +0.006 (256), 2022 +0.044 (258), 2023 -0.060 (255), 2024 +0.111 (259), 2025 +0.027 (256), 2026 -0.024 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.000 (t -0.01), colchón 50 % -0.000 (t -0.00), objetivo 1,5:1 +0.011 (t +0.46), objetivo 2:1 +0.026 (t +1.04).

