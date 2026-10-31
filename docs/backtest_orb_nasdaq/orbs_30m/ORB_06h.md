# ORB de 30 min de las 06:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 06:00–06:30 | 2094 | 49.3 | -0.070 | -3.22 | -0.014 | 0.056 | no |
| 06:15–06:45 | 2096 | 49.7 | -0.065 | -3.00 | -0.008 | 0.057 | no |
| 06:30–07:00 | 2095 | 51.2 | -0.034 | -1.55 | +0.021 | 0.055 | no |
| 06:45–07:15 | 2095 | 50.2 | -0.044 | -2.03 | +0.005 | 0.050 | no |

## Detalle

### ORB 06:00–06:30

Rotura con cuerpo desde las 06:30 hasta las 12:30; a esa hora se cierra. ORB completos: 2095; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.056 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 1019, stop 1052, por tiempo 23.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 49.3 % | -0.070 | -147.0 | 0.87 | -153.4 | -3.22 |
| Sin costes | 2094 | 49.4 % | -0.014 | -30.0 | 0.97 | -67.4 | -0.66 |
| Long | 1115 | 50.7 % | -0.044 | -49.4 | 0.91 | -58.0 | -1.48 |
| Short | 979 | 47.8 % | -0.100 | -97.6 | 0.82 | -103.6 | -3.12 |
| 1.ª mitad | 1047 | 51.1 % | -0.038 | -39.4 | 0.93 | -55.1 | -1.22 |
| 2.ª mitad | 1047 | 47.6 % | -0.103 | -107.6 | 0.81 | -118.7 | -3.33 |

Por año (R neto medio y operaciones): 2018 -0.108 (76), 2019 -0.077 (258), 2020 +0.028 (254), 2021 -0.099 (258), 2022 +0.060 (258), 2023 -0.195 (258), 2024 -0.061 (259), 2025 -0.096 (257), 2026 -0.115 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.086 (t -3.93), colchón 50 % -0.059 (t -2.74), objetivo 1,5:1 -0.051 (t -1.92), objetivo 2:1 -0.046 (t -1.51).

### ORB 06:15–06:45

Rotura con cuerpo desde las 06:45 hasta las 12:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.057 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 1024, stop 1045, por tiempo 27.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 49.7 % | -0.065 | -136.9 | 0.88 | -153.4 | -3.00 |
| Sin costes | 2096 | 49.7 % | -0.008 | -16.4 | 0.98 | -52.9 | -0.36 |
| Long | 1136 | 51.1 % | -0.037 | -42.4 | 0.93 | -58.8 | -1.26 |
| Short | 960 | 48.0 % | -0.098 | -94.5 | 0.82 | -109.0 | -3.06 |
| 1.ª mitad | 1048 | 49.6 % | -0.068 | -70.9 | 0.87 | -81.2 | -2.19 |
| 2.ª mitad | 1048 | 49.8 % | -0.063 | -66.0 | 0.88 | -83.5 | -2.05 |

Por año (R neto medio y operaciones): 2018 +0.023 (76), 2019 -0.107 (258), 2020 -0.068 (255), 2021 -0.070 (259), 2022 -0.011 (258), 2023 -0.126 (258), 2024 -0.067 (259), 2025 -0.100 (257), 2026 +0.014 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.082 (t -3.74), colchón 50 % -0.053 (t -2.43), objetivo 1,5:1 -0.050 (t -1.89), objetivo 2:1 -0.065 (t -2.13).

### ORB 06:30–07:00

Rotura con cuerpo desde las 07:00 hasta las 13:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.055 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 1056, stop 1013, por tiempo 26.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 51.2 % | -0.034 | -70.8 | 0.93 | -89.1 | -1.55 |
| Sin costes | 2095 | 51.2 % | +0.021 | +44.5 | 1.04 | -24.6 | +0.98 |
| Long | 1157 | 50.7 % | -0.045 | -52.2 | 0.91 | -59.5 | -1.54 |
| Short | 938 | 51.7 % | -0.020 | -18.6 | 0.96 | -39.6 | -0.61 |
| 1.ª mitad | 1048 | 51.6 % | -0.026 | -27.8 | 0.95 | -38.3 | -0.86 |
| 2.ª mitad | 1047 | 50.7 % | -0.041 | -43.0 | 0.92 | -55.9 | -1.33 |

Por año (R neto medio y operaciones): 2018 +0.022 (76), 2019 -0.074 (258), 2020 +0.019 (255), 2021 -0.051 (259), 2022 -0.041 (258), 2023 -0.088 (258), 2024 -0.037 (259), 2025 +0.006 (256), 2026 -0.016 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.058 (t -2.68), colchón 50 % -0.024 (t -1.13), objetivo 1,5:1 -0.006 (t -0.24), objetivo 2:1 -0.026 (t -0.85).

### ORB 06:45–07:15

Rotura con cuerpo desde las 07:15 hasta las 13:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.050 R; ancho medio del ORB 0.21 %; cómo terminan: objetivo 1036, stop 1028, por tiempo 31.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 50.2 % | -0.044 | -92.7 | 0.91 | -109.5 | -2.03 |
| Sin costes | 2095 | 50.2 % | +0.005 | +11.2 | 1.01 | -40.0 | +0.25 |
| Long | 1119 | 49.2 % | -0.069 | -77.2 | 0.87 | -85.4 | -2.32 |
| Short | 976 | 51.4 % | -0.016 | -15.5 | 0.97 | -44.3 | -0.50 |
| 1.ª mitad | 1048 | 50.9 % | -0.033 | -34.2 | 0.94 | -55.6 | -1.06 |
| 2.ª mitad | 1047 | 49.6 % | -0.056 | -58.5 | 0.89 | -68.9 | -1.82 |

Por año (R neto medio y operaciones): 2018 +0.057 (76), 2019 -0.066 (258), 2020 -0.054 (255), 2021 -0.025 (259), 2022 -0.017 (258), 2023 -0.152 (258), 2024 -0.041 (259), 2025 -0.009 (257), 2026 -0.014 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.062 (t -2.86), colchón 50 % -0.038 (t -1.76), objetivo 1,5:1 -0.030 (t -1.13), objetivo 2:1 -0.033 (t -1.08).

