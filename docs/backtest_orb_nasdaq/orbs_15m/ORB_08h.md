# ORB de 15 min de las 08:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 08:00–08:15 | 2095 | 49.6 | -0.066 | -3.03 | -0.008 | 0.058 | no |
| 08:15–08:30 | 2094 | 48.4 | -0.088 | -4.06 | -0.032 | 0.056 | no |
| 08:30–08:45 | 2089 | 46.4 | -0.119 | -5.61 | -0.073 | 0.046 | no |
| 08:45–09:00 | 2094 | 48.4 | -0.088 | -4.07 | -0.034 | 0.055 | no |

## Detalle

### ORB 08:00–08:15

Rotura con cuerpo desde las 08:15 hasta las 14:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.058 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 1029, stop 1047, por tiempo 19.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 49.6 % | -0.066 | -138.5 | 0.88 | -146.8 | -3.03 |
| Sin costes | 2095 | 49.6 % | -0.008 | -16.6 | 0.98 | -71.2 | -0.36 |
| Long | 1065 | 49.1 % | -0.079 | -83.6 | 0.85 | -85.6 | -2.57 |
| Short | 1030 | 50.2 % | -0.053 | -54.9 | 0.90 | -71.2 | -1.72 |
| 1.ª mitad | 1048 | 51.2 % | -0.039 | -40.7 | 0.92 | -62.6 | -1.26 |
| 2.ª mitad | 1047 | 48.0 % | -0.093 | -97.9 | 0.83 | -114.1 | -3.03 |

Por año (R neto medio y operaciones): 2018 -0.110 (76), 2019 -0.113 (258), 2020 -0.002 (254), 2021 -0.052 (259), 2022 +0.076 (258), 2023 -0.084 (258), 2024 -0.205 (259), 2025 -0.125 (257), 2026 -0.001 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.080 (t -3.68), colchón 50 % -0.051 (t -2.33), objetivo 1,5:1 -0.067 (t -2.53), objetivo 2:1 -0.076 (t -2.53).

### ORB 08:15–08:30

Rotura con cuerpo desde las 08:30 hasta las 14:30; a esa hora se cierra. ORB completos: 2095; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.056 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 992, stop 1059, por tiempo 43.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 48.4 % | -0.088 | -184.5 | 0.84 | -193.3 | -4.06 |
| Sin costes | 2094 | 48.4 % | -0.032 | -67.5 | 0.94 | -83.7 | -1.49 |
| Long | 1054 | 47.0 % | -0.122 | -128.3 | 0.78 | -132.1 | -3.99 |
| Short | 1040 | 49.9 % | -0.054 | -56.2 | 0.90 | -66.5 | -1.75 |
| 1.ª mitad | 1047 | 49.2 % | -0.081 | -84.8 | 0.85 | -103.1 | -2.63 |
| 2.ª mitad | 1047 | 47.7 % | -0.095 | -99.7 | 0.82 | -107.9 | -3.11 |

Por año (R neto medio y operaciones): 2018 +0.027 (75), 2019 -0.162 (258), 2020 -0.048 (254), 2021 -0.129 (259), 2022 -0.011 (258), 2023 -0.037 (258), 2024 -0.072 (259), 2025 -0.144 (257), 2026 -0.143 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.072 (t -3.31), colchón 50 % -0.069 (t -3.20), objetivo 1,5:1 -0.098 (t -3.76), objetivo 2:1 -0.098 (t -3.27).

### ORB 08:30–08:45

Rotura con cuerpo desde las 08:45 hasta las 14:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2089.

**No pasa los criterios**. Coste medio 0.046 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 897, stop 1057, por tiempo 135.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2089 | 46.4 % | -0.119 | -248.9 | 0.78 | -255.2 | -5.61 |
| Sin costes | 2089 | 46.6 % | -0.073 | -153.1 | 0.86 | -163.0 | -3.45 |
| Long | 1067 | 46.2 % | -0.125 | -132.9 | 0.77 | -134.9 | -4.19 |
| Short | 1022 | 46.7 % | -0.114 | -116.1 | 0.79 | -128.9 | -3.73 |
| 1.ª mitad | 1045 | 46.4 % | -0.123 | -128.8 | 0.78 | -135.8 | -4.07 |
| 2.ª mitad | 1044 | 46.5 % | -0.115 | -120.1 | 0.78 | -121.1 | -3.86 |

Por año (R neto medio y operaciones): 2018 -0.030 (76), 2019 -0.209 (258), 2020 -0.129 (254), 2021 -0.077 (257), 2022 -0.096 (256), 2023 -0.108 (257), 2024 -0.073 (258), 2025 -0.103 (257), 2026 -0.197 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.115 (t -5.36), colchón 50 % -0.083 (t -3.95), objetivo 1,5:1 -0.141 (t -5.61), objetivo 2:1 -0.107 (t -3.70).

### ORB 08:45–09:00

Rotura con cuerpo desde las 09:00 hasta las 15:00; a esa hora se cierra. ORB completos: 2095; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.055 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 990, stop 1064, por tiempo 40.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 48.4 % | -0.088 | -185.0 | 0.84 | -200.9 | -4.07 |
| Sin costes | 2094 | 48.4 % | -0.034 | -70.3 | 0.93 | -91.5 | -1.55 |
| Long | 1070 | 48.7 % | -0.083 | -88.7 | 0.85 | -94.7 | -2.73 |
| Short | 1024 | 48.0 % | -0.094 | -96.3 | 0.83 | -113.3 | -3.02 |
| 1.ª mitad | 1047 | 48.5 % | -0.092 | -96.0 | 0.83 | -103.8 | -2.99 |
| 2.ª mitad | 1047 | 48.2 % | -0.085 | -89.0 | 0.84 | -111.3 | -2.77 |

Por año (R neto medio y operaciones): 2018 -0.302 (76), 2019 -0.064 (258), 2020 -0.124 (254), 2021 -0.046 (258), 2022 -0.066 (258), 2023 -0.114 (258), 2024 -0.090 (259), 2025 -0.128 (258), 2026 +0.003 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.113 (t -5.19), colchón 50 % -0.049 (t -2.29), objetivo 1,5:1 -0.089 (t -3.40), objetivo 2:1 -0.068 (t -2.24).

