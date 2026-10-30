# ORB de 60 min de las 22:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 22:00–23:00 | 2082 | 50.7 | -0.031 | -1.51 | +0.026 | 0.057 | no |
| 22:15–23:15 | 2085 | 50.6 | -0.038 | -1.84 | +0.023 | 0.060 | no |
| 22:30–23:30 | 2091 | 49.1 | -0.063 | -3.05 | -0.001 | 0.063 | no |
| 22:45–23:45 | 2095 | 49.4 | -0.064 | -3.08 | +0.001 | 0.065 | no |

## Detalle

### ORB 22:00–23:00

Rotura con cuerpo desde las 23:00 hasta las 05:00 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2082.

**No pasa los criterios**. Coste medio 0.057 R; ancho medio del ORB 0.21 %; cómo terminan: objetivo 887, stop 840, por tiempo 355.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2082 | 50.7 % | -0.031 | -63.7 | 0.93 | -92.1 | -1.51 |
| Sin costes | 2082 | 51.3 % | +0.026 | +54.9 | 1.06 | -30.7 | +1.30 |
| Long | 1105 | 52.0 % | -0.010 | -11.0 | 0.98 | -35.4 | -0.36 |
| Short | 977 | 49.1 % | -0.054 | -52.7 | 0.88 | -69.7 | -1.82 |
| 1.ª mitad | 1041 | 50.9 % | -0.023 | -23.7 | 0.95 | -61.9 | -0.81 |
| 2.ª mitad | 1041 | 50.4 % | -0.038 | -40.0 | 0.92 | -64.6 | -1.31 |

Por año (R neto medio y operaciones): 2018 +0.113 (76), 2019 -0.074 (252), 2020 -0.080 (254), 2021 -0.027 (255), 2022 +0.042 (258), 2023 -0.050 (257), 2024 -0.096 (259), 2025 -0.023 (256), 2026 +0.028 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.028 (t -1.33), colchón 50 % -0.023 (t -1.21), objetivo 1,5:1 -0.019 (t -0.79), objetivo 2:1 -0.018 (t -0.70).

### ORB 22:15–23:15

Rotura con cuerpo desde las 23:15 hasta las 05:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2085.

**No pasa los criterios**. Coste medio 0.060 R; ancho medio del ORB 0.20 %; cómo terminan: objetivo 912, stop 863, por tiempo 310.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2085 | 50.6 % | -0.038 | -78.7 | 0.92 | -105.0 | -1.84 |
| Sin costes | 2085 | 51.2 % | +0.023 | +47.1 | 1.05 | -30.9 | +1.10 |
| Long | 1127 | 51.5 % | -0.032 | -36.6 | 0.93 | -57.4 | -1.17 |
| Short | 958 | 49.7 % | -0.044 | -42.1 | 0.91 | -61.2 | -1.45 |
| 1.ª mitad | 1043 | 50.3 % | -0.037 | -39.0 | 0.92 | -55.4 | -1.31 |
| 2.ª mitad | 1042 | 51.0 % | -0.038 | -39.7 | 0.92 | -73.7 | -1.30 |

Por año (R neto medio y operaciones): 2018 -0.000 (76), 2019 -0.052 (255), 2020 -0.065 (254), 2021 -0.020 (255), 2022 -0.000 (257), 2023 -0.075 (257), 2024 -0.123 (259), 2025 -0.049 (256), 2026 +0.092 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.037 (t -1.79), colchón 50 % -0.036 (t -1.82), objetivo 1,5:1 -0.023 (t -0.96), objetivo 2:1 -0.028 (t -1.06).

### ORB 22:30–23:30

Rotura con cuerpo desde las 23:30 hasta las 05:30 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.063 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 916, stop 912, por tiempo 263.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2091 | 49.1 % | -0.063 | -132.1 | 0.87 | -162.2 | -3.05 |
| Sin costes | 2091 | 49.5 % | -0.001 | -1.4 | 1.00 | -50.8 | -0.03 |
| Long | 1117 | 50.9 % | -0.033 | -37.2 | 0.93 | -57.2 | -1.18 |
| Short | 974 | 47.1 % | -0.097 | -94.9 | 0.81 | -112.3 | -3.20 |
| 1.ª mitad | 1046 | 48.2 % | -0.075 | -78.1 | 0.85 | -80.3 | -2.58 |
| 2.ª mitad | 1045 | 50.0 % | -0.052 | -54.0 | 0.90 | -95.1 | -1.74 |

Por año (R neto medio y operaciones): 2018 -0.112 (76), 2019 -0.083 (256), 2020 -0.121 (255), 2021 -0.034 (258), 2022 -0.030 (257), 2023 -0.081 (258), 2024 -0.180 (259), 2025 -0.064 (256), 2026 +0.135 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.070 (t -3.30), colchón 50 % -0.042 (t -2.12), objetivo 1,5:1 -0.053 (t -2.19), objetivo 2:1 -0.054 (t -2.01).

### ORB 22:45–23:45

Rotura con cuerpo desde las 23:45 hasta las 05:45 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.065 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 938, stop 932, por tiempo 225.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 49.4 % | -0.064 | -135.1 | 0.87 | -164.1 | -3.08 |
| Sin costes | 2095 | 49.9 % | +0.001 | +1.7 | 1.00 | -47.8 | +0.04 |
| Long | 1095 | 51.1 % | -0.035 | -38.6 | 0.93 | -66.1 | -1.22 |
| Short | 1000 | 47.5 % | -0.096 | -96.5 | 0.81 | -109.4 | -3.18 |
| 1.ª mitad | 1048 | 48.2 % | -0.082 | -86.0 | 0.84 | -86.7 | -2.80 |
| 2.ª mitad | 1047 | 50.5 % | -0.047 | -49.1 | 0.91 | -83.6 | -1.57 |

Por año (R neto medio y operaciones): 2018 -0.206 (76), 2019 -0.104 (258), 2020 -0.098 (255), 2021 -0.009 (259), 2022 -0.086 (257), 2023 -0.114 (258), 2024 -0.061 (259), 2025 -0.092 (257), 2026 +0.118 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.076 (t -3.58), colchón 50 % -0.070 (t -3.48), objetivo 1,5:1 -0.067 (t -2.71), objetivo 2:1 -0.046 (t -1.68).

