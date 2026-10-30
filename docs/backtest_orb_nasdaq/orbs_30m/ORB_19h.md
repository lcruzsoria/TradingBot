# ORB de 30 min de las 19:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 19:00–19:30 | 2083 | 48.3 | -0.094 | -4.61 | -0.021 | 0.073 | no |
| 19:15–19:45 | 2086 | 50.0 | -0.065 | -3.20 | +0.009 | 0.074 | no |
| 19:30–20:00 | 2088 | 49.2 | -0.061 | -2.99 | +0.008 | 0.069 | no |
| 19:45–20:15 | 2081 | 50.3 | -0.034 | -1.78 | +0.023 | 0.057 | no |

## Detalle

### ORB 19:00–19:30

Rotura con cuerpo desde las 19:30 hasta las 01:30 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2083.

**No pasa los criterios**. Coste medio 0.073 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 844, stop 888, por tiempo 351.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2083 | 48.3 % | -0.094 | -196.0 | 0.81 | -201.7 | -4.61 |
| Sin costes | 2083 | 49.0 % | -0.021 | -43.4 | 0.95 | -80.0 | -1.02 |
| Long | 1073 | 51.3 % | -0.051 | -55.1 | 0.89 | -70.9 | -1.81 |
| Short | 1010 | 45.2 % | -0.140 | -141.0 | 0.73 | -142.1 | -4.76 |
| 1.ª mitad | 1042 | 48.4 % | -0.100 | -104.5 | 0.80 | -110.6 | -3.41 |
| 2.ª mitad | 1041 | 48.3 % | -0.088 | -91.5 | 0.82 | -97.4 | -3.11 |

Por año (R neto medio y operaciones): 2018 -0.168 (75), 2019 -0.079 (253), 2020 -0.010 (255), 2021 -0.131 (257), 2022 -0.169 (257), 2023 -0.205 (257), 2024 -0.061 (257), 2025 -0.041 (256), 2026 -0.024 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.091 (t -4.33), colchón 50 % -0.090 (t -4.61), objetivo 1,5:1 -0.082 (t -3.44), objetivo 2:1 -0.089 (t -3.44).

### ORB 19:15–19:45

Rotura con cuerpo desde las 19:45 hasta las 01:45 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2086.

**No pasa los criterios**. Coste medio 0.074 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 889, stop 869, por tiempo 328.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2086 | 50.0 % | -0.065 | -136.5 | 0.86 | -146.3 | -3.20 |
| Sin costes | 2086 | 50.3 % | +0.009 | +18.6 | 1.02 | -50.2 | +0.44 |
| Long | 1102 | 50.9 % | -0.054 | -59.3 | 0.88 | -82.9 | -1.93 |
| Short | 984 | 48.9 % | -0.078 | -77.2 | 0.84 | -80.2 | -2.60 |
| 1.ª mitad | 1043 | 50.0 % | -0.060 | -62.1 | 0.88 | -70.2 | -2.04 |
| 2.ª mitad | 1043 | 50.0 % | -0.071 | -74.4 | 0.85 | -81.5 | -2.48 |

Por año (R neto medio y operaciones): 2018 -0.035 (76), 2019 -0.067 (255), 2020 -0.026 (254), 2021 -0.035 (256), 2022 -0.158 (258), 2023 -0.152 (256), 2024 -0.027 (258), 2025 -0.066 (257), 2026 +0.011 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.070 (t -3.35), colchón 50 % -0.066 (t -3.35), objetivo 1,5:1 -0.073 (t -3.07), objetivo 2:1 -0.077 (t -2.96).

### ORB 19:30–20:00

Rotura con cuerpo desde las 20:00 hasta las 02:00 (día siguiente); a esa hora se cierra. ORB completos: 2095; con rotura: 2088.

**No pasa los criterios**. Coste medio 0.069 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 873, stop 859, por tiempo 356.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2088 | 49.2 % | -0.061 | -126.7 | 0.87 | -137.1 | -2.99 |
| Sin costes | 2088 | 49.9 % | +0.008 | +17.4 | 1.02 | -44.9 | +0.41 |
| Long | 1079 | 51.0 % | -0.025 | -26.9 | 0.94 | -50.7 | -0.90 |
| Short | 1009 | 47.4 % | -0.099 | -99.8 | 0.81 | -107.7 | -3.31 |
| 1.ª mitad | 1044 | 50.1 % | -0.041 | -42.7 | 0.91 | -55.7 | -1.43 |
| 2.ª mitad | 1044 | 48.4 % | -0.080 | -84.0 | 0.84 | -86.4 | -2.78 |

Por año (R neto medio y operaciones): 2018 +0.017 (76), 2019 -0.124 (253), 2020 +0.021 (254), 2021 -0.064 (259), 2022 -0.056 (258), 2023 -0.140 (258), 2024 -0.046 (257), 2025 -0.067 (257), 2026 -0.027 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.059 (t -2.83), colchón 50 % -0.070 (t -3.61), objetivo 1,5:1 -0.056 (t -2.37), objetivo 2:1 -0.057 (t -2.21).

### ORB 19:45–20:15

Rotura con cuerpo desde las 20:15 hasta las 02:15 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2081.

**No pasa los criterios**. Coste medio 0.057 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 785, stop 735, por tiempo 561.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2081 | 50.3 % | -0.034 | -71.4 | 0.92 | -99.4 | -1.78 |
| Sin costes | 2081 | 50.8 % | +0.023 | +47.2 | 1.06 | -52.5 | +1.18 |
| Long | 1119 | 50.9 % | -0.011 | -12.6 | 0.97 | -52.9 | -0.43 |
| Short | 962 | 49.6 % | -0.061 | -58.8 | 0.87 | -69.3 | -2.11 |
| 1.ª mitad | 1041 | 52.4 % | -0.000 | -0.4 | 1.00 | -28.9 | -0.02 |
| 2.ª mitad | 1040 | 48.3 % | -0.068 | -70.9 | 0.85 | -88.2 | -2.48 |

Por año (R neto medio y operaciones): 2018 +0.075 (76), 2019 -0.037 (251), 2020 +0.019 (256), 2021 -0.015 (257), 2022 -0.022 (258), 2023 -0.203 (256), 2024 -0.028 (257), 2025 +0.018 (256), 2026 -0.040 (214).

Sensibilidad (R neto medio y t): colchón 0 % -0.028 (t -1.37), colchón 50 % -0.047 (t -2.60), objetivo 1,5:1 -0.050 (t -2.28), objetivo 2:1 -0.038 (t -1.60).

