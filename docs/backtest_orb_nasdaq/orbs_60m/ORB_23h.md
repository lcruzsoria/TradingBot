# ORB de 60 min de las 23:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 23:00–00:00 | 2096 | 50.8 | -0.045 | -2.16 | +0.023 | 0.068 | no |
| 23:15–00:15 | 2094 | 50.8 | -0.049 | -2.32 | +0.020 | 0.068 | no |
| 23:30–00:30 | 2092 | 50.8 | -0.046 | -2.16 | +0.023 | 0.069 | no |
| 23:45–00:45 | 2094 | 50.8 | -0.044 | -2.08 | +0.025 | 0.069 | no |

## Detalle

### ORB 23:00–00:00

Rotura con cuerpo desde las 00:00 hasta las 06:00 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.068 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 966, stop 921, por tiempo 209.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 50.8 % | -0.045 | -94.6 | 0.91 | -124.8 | -2.16 |
| Sin costes | 2096 | 51.2 % | +0.023 | +47.3 | 1.05 | -33.4 | +1.08 |
| Long | 1059 | 53.6 % | -0.001 | -1.0 | 1.00 | -43.6 | -0.03 |
| Short | 1037 | 47.9 % | -0.090 | -93.6 | 0.83 | -112.0 | -3.01 |
| 1.ª mitad | 1048 | 49.1 % | -0.078 | -81.7 | 0.84 | -85.1 | -2.65 |
| 2.ª mitad | 1048 | 52.5 % | -0.012 | -12.9 | 0.97 | -51.8 | -0.41 |

Por año (R neto medio y operaciones): 2018 -0.096 (75), 2019 -0.080 (258), 2020 -0.054 (256), 2021 -0.022 (259), 2022 -0.159 (258), 2023 -0.047 (258), 2024 -0.000 (259), 2025 -0.080 (257), 2026 +0.123 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.070 (t -3.26), colchón 50 % -0.034 (t -1.68), objetivo 1,5:1 -0.034 (t -1.38), objetivo 2:1 -0.026 (t -0.94).

### ORB 23:15–00:15

Rotura con cuerpo desde las 00:15 hasta las 06:15 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.068 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 979, stop 943, por tiempo 172.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 50.8 % | -0.049 | -102.3 | 0.90 | -140.1 | -2.32 |
| Sin costes | 2094 | 51.0 % | +0.020 | +41.1 | 1.04 | -36.6 | +0.93 |
| Long | 1080 | 53.5 % | +0.000 | +0.5 | 1.00 | -36.3 | +0.02 |
| Short | 1014 | 47.9 % | -0.101 | -102.8 | 0.81 | -122.7 | -3.32 |
| 1.ª mitad | 1047 | 49.6 % | -0.074 | -77.0 | 0.86 | -87.3 | -2.47 |
| 2.ª mitad | 1047 | 52.1 % | -0.024 | -25.3 | 0.95 | -57.8 | -0.81 |

Por año (R neto medio y operaciones): 2018 +0.011 (75), 2019 -0.098 (257), 2020 -0.024 (256), 2021 -0.088 (259), 2022 -0.130 (258), 2023 -0.074 (258), 2024 -0.023 (259), 2025 -0.045 (256), 2026 +0.098 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.048 (t -2.24), colchón 50 % -0.036 (t -1.76), objetivo 1,5:1 -0.046 (t -1.85), objetivo 2:1 -0.045 (t -1.63).

### ORB 23:30–00:30

Rotura con cuerpo desde las 00:30 hasta las 06:30 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.069 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 990, stop 938, por tiempo 164.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2092 | 50.8 % | -0.046 | -95.8 | 0.91 | -141.0 | -2.16 |
| Sin costes | 2092 | 50.9 % | +0.023 | +49.0 | 1.05 | -45.7 | +1.11 |
| Long | 1076 | 53.3 % | -0.003 | -3.6 | 0.99 | -38.1 | -0.11 |
| Short | 1016 | 48.1 % | -0.091 | -92.2 | 0.83 | -113.6 | -2.98 |
| 1.ª mitad | 1046 | 49.9 % | -0.064 | -66.7 | 0.87 | -83.7 | -2.13 |
| 2.ª mitad | 1046 | 51.7 % | -0.028 | -29.2 | 0.94 | -60.8 | -0.93 |

Por año (R neto medio y operaciones): 2018 +0.044 (76), 2019 -0.130 (257), 2020 +0.006 (256), 2021 -0.092 (259), 2022 -0.080 (257), 2023 -0.143 (257), 2024 +0.006 (259), 2025 -0.018 (255), 2026 +0.077 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.044 (t -2.03), colchón 50 % -0.034 (t -1.67), objetivo 1,5:1 -0.046 (t -1.81), objetivo 2:1 -0.033 (t -1.16).

### ORB 23:45–00:45

Rotura con cuerpo desde las 00:45 hasta las 06:45 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.069 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 991, stop 937, por tiempo 166.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 50.8 % | -0.044 | -92.1 | 0.91 | -117.6 | -2.08 |
| Sin costes | 2094 | 50.9 % | +0.025 | +51.8 | 1.05 | -55.1 | +1.17 |
| Long | 1090 | 53.3 % | -0.006 | -6.1 | 0.99 | -45.6 | -0.19 |
| Short | 1004 | 48.0 % | -0.086 | -86.1 | 0.83 | -97.3 | -2.81 |
| 1.ª mitad | 1047 | 47.9 % | -0.089 | -93.0 | 0.83 | -97.2 | -2.98 |
| 2.ª mitad | 1047 | 53.7 % | +0.001 | +0.8 | 1.00 | -42.8 | +0.03 |

Por año (R neto medio y operaciones): 2018 -0.015 (76), 2019 -0.106 (258), 2020 +0.022 (256), 2021 -0.173 (259), 2022 -0.089 (258), 2023 -0.028 (257), 2024 -0.056 (259), 2025 +0.045 (255), 2026 +0.040 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.056 (t -2.63), colchón 50 % -0.047 (t -2.28), objetivo 1,5:1 -0.037 (t -1.46), objetivo 2:1 -0.027 (t -0.95).

