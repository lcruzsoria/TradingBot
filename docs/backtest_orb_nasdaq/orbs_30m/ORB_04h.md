# ORB de 30 min de las 04:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 04:00–04:30 | 2096 | 51.6 | -0.015 | -0.68 | +0.030 | 0.045 | no |
| 04:15–04:45 | 2095 | 50.5 | -0.036 | -1.68 | +0.014 | 0.051 | no |
| 04:30–05:00 | 2097 | 49.3 | -0.069 | -3.18 | -0.015 | 0.054 | no |
| 04:45–05:15 | 2095 | 49.6 | -0.063 | -2.90 | -0.007 | 0.056 | no |

## Detalle

### ORB 04:00–04:30

Rotura con cuerpo desde las 04:30 hasta las 10:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.045 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 1027, stop 967, por tiempo 102.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 51.6 % | -0.015 | -30.5 | 0.97 | -89.1 | -0.68 |
| Sin costes | 2096 | 51.7 % | +0.030 | +62.8 | 1.06 | -36.0 | +1.40 |
| Long | 1093 | 52.5 % | -0.003 | -3.4 | 0.99 | -35.3 | -0.11 |
| Short | 1003 | 50.6 % | -0.027 | -27.1 | 0.95 | -73.0 | -0.87 |
| 1.ª mitad | 1048 | 49.7 % | -0.061 | -63.5 | 0.88 | -64.8 | -2.00 |
| 2.ª mitad | 1048 | 53.5 % | +0.031 | +33.0 | 1.07 | -30.7 | +1.04 |

Por año (R neto medio y operaciones): 2018 +0.005 (76), 2019 -0.100 (258), 2020 -0.033 (255), 2021 -0.089 (259), 2022 -0.012 (258), 2023 -0.103 (258), 2024 +0.100 (259), 2025 +0.100 (257), 2026 +0.021 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.014 (t -0.65), colchón 50 % -0.008 (t -0.38), objetivo 1,5:1 -0.011 (t -0.44), objetivo 2:1 -0.018 (t -0.63).

### ORB 04:15–04:45

Rotura con cuerpo desde las 04:45 hasta las 10:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.051 R; ancho medio del ORB 0.21 %; cómo terminan: objetivo 1039, stop 1007, por tiempo 49.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 50.5 % | -0.036 | -76.4 | 0.93 | -93.9 | -1.68 |
| Sin costes | 2095 | 50.6 % | +0.014 | +30.3 | 1.03 | -40.3 | +0.67 |
| Long | 1125 | 50.1 % | -0.047 | -52.7 | 0.91 | -67.5 | -1.59 |
| Short | 970 | 50.9 % | -0.024 | -23.7 | 0.95 | -51.0 | -0.77 |
| 1.ª mitad | 1048 | 49.6 % | -0.058 | -61.1 | 0.89 | -70.1 | -1.90 |
| 2.ª mitad | 1047 | 51.4 % | -0.015 | -15.3 | 0.97 | -40.6 | -0.48 |

Por año (R neto medio y operaciones): 2018 +0.094 (76), 2019 -0.078 (258), 2020 -0.069 (255), 2021 -0.072 (259), 2022 -0.078 (258), 2023 -0.026 (258), 2024 +0.076 (259), 2025 -0.089 (256), 2026 +0.014 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.042 (t -1.95), colchón 50 % -0.036 (t -1.69), objetivo 1,5:1 -0.017 (t -0.66), objetivo 2:1 -0.004 (t -0.14).

### ORB 04:30–05:00

Rotura con cuerpo desde las 05:00 hasta las 11:00; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.054 R; ancho medio del ORB 0.20 %; cómo terminan: objetivo 1013, stop 1043, por tiempo 41.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 49.3 % | -0.069 | -144.8 | 0.87 | -177.8 | -3.18 |
| Sin costes | 2097 | 49.4 % | -0.015 | -31.1 | 0.97 | -79.1 | -0.68 |
| Long | 1130 | 49.6 % | -0.069 | -78.1 | 0.87 | -101.7 | -2.34 |
| Short | 967 | 48.9 % | -0.069 | -66.7 | 0.87 | -87.8 | -2.16 |
| 1.ª mitad | 1049 | 49.7 % | -0.063 | -66.6 | 0.88 | -95.0 | -2.07 |
| 2.ª mitad | 1048 | 48.9 % | -0.075 | -78.2 | 0.86 | -88.1 | -2.43 |

Por año (R neto medio y operaciones): 2018 +0.281 (76), 2019 -0.131 (258), 2020 -0.180 (256), 2021 -0.019 (259), 2022 -0.045 (258), 2023 -0.060 (258), 2024 -0.032 (259), 2025 -0.126 (257), 2026 -0.061 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.071 (t -3.26), colchón 50 % -0.064 (t -2.97), objetivo 1,5:1 -0.063 (t -2.41), objetivo 2:1 -0.038 (t -1.27).

### ORB 04:45–05:15

Rotura con cuerpo desde las 05:15 hasta las 11:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.056 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 1024, stop 1042, por tiempo 29.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 49.6 % | -0.063 | -132.3 | 0.88 | -167.3 | -2.90 |
| Sin costes | 2095 | 49.7 % | -0.007 | -15.7 | 0.98 | -60.3 | -0.35 |
| Long | 1130 | 49.3 % | -0.075 | -84.6 | 0.86 | -102.6 | -2.53 |
| Short | 965 | 50.1 % | -0.049 | -47.7 | 0.91 | -69.1 | -1.54 |
| 1.ª mitad | 1048 | 50.9 % | -0.043 | -45.2 | 0.92 | -83.7 | -1.41 |
| 2.ª mitad | 1047 | 48.4 % | -0.083 | -87.0 | 0.85 | -100.3 | -2.70 |

Por año (R neto medio y operaciones): 2018 +0.241 (76), 2019 -0.074 (257), 2020 -0.122 (255), 2021 -0.065 (259), 2022 +0.008 (258), 2023 -0.182 (258), 2024 -0.060 (259), 2025 -0.056 (257), 2026 -0.041 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.081 (t -3.70), colchón 50 % -0.047 (t -2.17), objetivo 1,5:1 -0.063 (t -2.39), objetivo 2:1 -0.077 (t -2.60).

