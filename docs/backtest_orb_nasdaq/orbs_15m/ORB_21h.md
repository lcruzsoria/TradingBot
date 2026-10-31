# ORB de 15 min de las 21:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 21:00–21:15 | 2096 | 50.4 | -0.065 | -3.03 | +0.021 | 0.086 | no |
| 21:15–21:30 | 2097 | 49.7 | -0.083 | -3.87 | +0.006 | 0.089 | no |
| 21:30–21:45 | 2092 | 51.3 | -0.052 | -2.43 | +0.032 | 0.084 | no |
| 21:45–22:00 | 2095 | 50.2 | -0.085 | -3.92 | +0.010 | 0.095 | no |

## Detalle

### ORB 21:00–21:15

Rotura con cuerpo desde las 21:15 hasta las 03:15 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.086 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 1004, stop 951, por tiempo 141.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 50.4 % | -0.065 | -135.5 | 0.87 | -148.2 | -3.03 |
| Sin costes | 2096 | 50.7 % | +0.021 | +44.4 | 1.05 | -36.2 | +1.00 |
| Long | 1102 | 51.6 % | -0.038 | -41.5 | 0.92 | -68.8 | -1.28 |
| Short | 994 | 49.1 % | -0.095 | -94.0 | 0.82 | -102.3 | -3.05 |
| 1.ª mitad | 1048 | 51.8 % | -0.036 | -38.2 | 0.93 | -45.1 | -1.21 |
| 2.ª mitad | 1048 | 49.0 % | -0.093 | -97.3 | 0.82 | -116.4 | -3.07 |

Por año (R neto medio y operaciones): 2018 -0.173 (76), 2019 -0.008 (256), 2020 -0.013 (257), 2021 -0.054 (259), 2022 -0.039 (258), 2023 -0.145 (258), 2024 -0.104 (259), 2025 -0.130 (257), 2026 +0.022 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.098 (t -4.53), colchón 50 % -0.042 (t -2.00), objetivo 1,5:1 -0.030 (t -1.17), objetivo 2:1 -0.022 (t -0.78).

### ORB 21:15–21:30

Rotura con cuerpo desde las 21:30 hasta las 03:30 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.089 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 1000, stop 986, por tiempo 111.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 49.7 % | -0.083 | -174.1 | 0.84 | -192.0 | -3.87 |
| Sin costes | 2097 | 50.0 % | +0.006 | +12.0 | 1.01 | -34.5 | +0.27 |
| Long | 1116 | 50.2 % | -0.076 | -85.2 | 0.85 | -88.6 | -2.61 |
| Short | 981 | 49.2 % | -0.091 | -88.8 | 0.83 | -113.7 | -2.88 |
| 1.ª mitad | 1049 | 49.0 % | -0.092 | -96.3 | 0.83 | -98.8 | -3.04 |
| 2.ª mitad | 1048 | 50.5 % | -0.074 | -77.8 | 0.86 | -101.9 | -2.44 |

Por año (R neto medio y operaciones): 2018 -0.327 (76), 2019 -0.126 (256), 2020 -0.016 (257), 2021 -0.069 (259), 2022 -0.076 (258), 2023 -0.140 (258), 2024 -0.105 (259), 2025 -0.048 (258), 2026 +0.000 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.106 (t -4.92), colchón 50 % -0.064 (t -3.06), objetivo 1,5:1 -0.050 (t -1.94), objetivo 2:1 -0.022 (t -0.75).

### ORB 21:30–21:45

Rotura con cuerpo desde las 21:45 hasta las 03:45 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.084 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 1020, stop 944, por tiempo 128.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2092 | 51.3 % | -0.052 | -108.4 | 0.90 | -120.5 | -2.43 |
| Sin costes | 2092 | 51.5 % | +0.032 | +67.4 | 1.07 | -27.0 | +1.51 |
| Long | 1097 | 53.6 % | -0.005 | -6.0 | 0.99 | -42.7 | -0.19 |
| Short | 995 | 48.7 % | -0.103 | -102.4 | 0.81 | -118.9 | -3.31 |
| 1.ª mitad | 1046 | 51.1 % | -0.046 | -47.9 | 0.91 | -53.9 | -1.53 |
| 2.ª mitad | 1046 | 51.4 % | -0.058 | -60.5 | 0.89 | -84.6 | -1.90 |

Por año (R neto medio y operaciones): 2018 -0.134 (76), 2019 -0.121 (255), 2020 +0.052 (257), 2021 -0.021 (259), 2022 -0.030 (258), 2023 -0.064 (255), 2024 -0.092 (259), 2025 -0.126 (257), 2026 +0.023 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.071 (t -3.29), colchón 50 % -0.050 (t -2.42), objetivo 1,5:1 -0.047 (t -1.83), objetivo 2:1 -0.032 (t -1.11).

### ORB 21:45–22:00

Rotura con cuerpo desde las 22:00 hasta las 04:00 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.095 R; ancho medio del ORB 0.11 %; cómo terminan: objetivo 1024, stop 997, por tiempo 74.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 50.2 % | -0.085 | -177.0 | 0.84 | -180.8 | -3.92 |
| Sin costes | 2095 | 50.4 % | +0.010 | +21.3 | 1.02 | -52.8 | +0.47 |
| Long | 1107 | 51.0 % | -0.068 | -75.2 | 0.87 | -83.5 | -2.29 |
| Short | 988 | 49.3 % | -0.103 | -101.8 | 0.81 | -113.7 | -3.27 |
| 1.ª mitad | 1048 | 49.2 % | -0.093 | -97.6 | 0.82 | -102.1 | -3.07 |
| 2.ª mitad | 1047 | 51.2 % | -0.076 | -79.5 | 0.86 | -80.7 | -2.47 |

Por año (R neto medio y operaciones): 2018 -0.140 (76), 2019 -0.054 (255), 2020 -0.103 (257), 2021 -0.161 (259), 2022 -0.088 (258), 2023 -0.156 (258), 2024 -0.035 (259), 2025 -0.027 (257), 2026 -0.025 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.116 (t -5.35), colchón 50 % -0.050 (t -2.37), objetivo 1,5:1 -0.049 (t -1.87), objetivo 2:1 -0.034 (t -1.14).

