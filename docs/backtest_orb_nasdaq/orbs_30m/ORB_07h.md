# ORB de 30 min de las 07:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 07:00–07:30 | 2095 | 49.8 | -0.046 | -2.13 | +0.002 | 0.048 | no |
| 07:15–07:45 | 2096 | 49.6 | -0.059 | -2.71 | -0.008 | 0.051 | no |
| 07:30–08:00 | 2096 | 49.7 | -0.060 | -2.75 | -0.010 | 0.049 | no |
| 07:45–08:15 | 2095 | 48.9 | -0.068 | -3.16 | -0.023 | 0.045 | no |

## Detalle

### ORB 07:00–07:30

Rotura con cuerpo desde las 07:30 hasta las 13:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.048 R; ancho medio del ORB 0.21 %; cómo terminan: objetivo 1028, stop 1025, por tiempo 42.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 49.8 % | -0.046 | -96.8 | 0.91 | -127.1 | -2.13 |
| Sin costes | 2095 | 50.0 % | +0.002 | +3.9 | 1.00 | -57.6 | +0.09 |
| Long | 1076 | 49.2 % | -0.063 | -68.0 | 0.88 | -73.3 | -2.09 |
| Short | 1019 | 50.5 % | -0.028 | -28.8 | 0.94 | -64.0 | -0.91 |
| 1.ª mitad | 1048 | 51.4 % | -0.013 | -13.5 | 0.97 | -52.8 | -0.42 |
| 2.ª mitad | 1047 | 48.2 % | -0.080 | -83.3 | 0.85 | -89.6 | -2.60 |

Por año (R neto medio y operaciones): 2018 +0.093 (76), 2019 +0.018 (258), 2020 -0.002 (255), 2021 -0.098 (259), 2022 -0.014 (258), 2023 -0.160 (258), 2024 +0.028 (259), 2025 -0.111 (257), 2026 -0.079 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.078 (t -3.59), colchón 50 % -0.041 (t -1.91), objetivo 1,5:1 -0.057 (t -2.18), objetivo 2:1 -0.028 (t -0.93).

### ORB 07:15–07:45

Rotura con cuerpo desde las 07:45 hasta las 13:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.051 R; ancho medio del ORB 0.20 %; cómo terminan: objetivo 1022, stop 1039, por tiempo 35.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 49.6 % | -0.059 | -123.1 | 0.89 | -154.4 | -2.71 |
| Sin costes | 2096 | 49.6 % | -0.008 | -17.0 | 0.98 | -84.1 | -0.37 |
| Long | 1038 | 50.8 % | -0.039 | -40.5 | 0.92 | -63.5 | -1.26 |
| Short | 1058 | 48.4 % | -0.078 | -82.7 | 0.85 | -102.2 | -2.56 |
| 1.ª mitad | 1048 | 52.2 % | -0.009 | -9.4 | 0.98 | -41.3 | -0.29 |
| 2.ª mitad | 1048 | 46.9 % | -0.109 | -113.8 | 0.80 | -123.5 | -3.53 |

Por año (R neto medio y operaciones): 2018 +0.152 (76), 2019 +0.030 (258), 2020 -0.026 (255), 2021 -0.092 (259), 2022 -0.013 (258), 2023 -0.194 (258), 2024 -0.065 (259), 2025 -0.102 (257), 2026 -0.072 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.082 (t -3.77), colchón 50 % -0.028 (t -1.31), objetivo 1,5:1 -0.054 (t -2.05), objetivo 2:1 -0.057 (t -1.90).

### ORB 07:30–08:00

Rotura con cuerpo desde las 08:00 hasta las 14:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.049 R; ancho medio del ORB 0.20 %; cómo terminan: objetivo 1012, stop 1040, por tiempo 44.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 49.7 % | -0.060 | -125.0 | 0.89 | -149.2 | -2.75 |
| Sin costes | 2096 | 49.7 % | -0.010 | -21.5 | 0.98 | -79.1 | -0.47 |
| Long | 1068 | 50.2 % | -0.054 | -57.2 | 0.90 | -77.4 | -1.76 |
| Short | 1028 | 49.2 % | -0.066 | -67.7 | 0.87 | -83.7 | -2.13 |
| 1.ª mitad | 1048 | 51.8 % | -0.022 | -22.8 | 0.96 | -47.0 | -0.71 |
| 2.ª mitad | 1048 | 47.6 % | -0.097 | -102.2 | 0.82 | -114.4 | -3.18 |

Por año (R neto medio y operaciones): 2018 +0.017 (76), 2019 -0.018 (258), 2020 -0.013 (255), 2021 -0.085 (259), 2022 +0.004 (258), 2023 -0.151 (258), 2024 -0.104 (259), 2025 -0.077 (257), 2026 -0.055 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.082 (t -3.75), colchón 50 % -0.047 (t -2.19), objetivo 1,5:1 -0.060 (t -2.27), objetivo 2:1 -0.066 (t -2.20).

### ORB 07:45–08:15

Rotura con cuerpo desde las 08:15 hasta las 14:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.045 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 998, stop 1046, por tiempo 51.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 48.9 % | -0.068 | -143.3 | 0.87 | -159.8 | -3.16 |
| Sin costes | 2095 | 48.9 % | -0.023 | -48.8 | 0.95 | -75.0 | -1.08 |
| Long | 1067 | 48.3 % | -0.084 | -89.5 | 0.84 | -93.6 | -2.77 |
| Short | 1028 | 49.6 % | -0.052 | -53.7 | 0.90 | -73.9 | -1.69 |
| 1.ª mitad | 1048 | 49.8 % | -0.054 | -56.1 | 0.90 | -70.2 | -1.75 |
| 2.ª mitad | 1047 | 48.0 % | -0.083 | -87.2 | 0.84 | -108.7 | -2.71 |

Por año (R neto medio y operaciones): 2018 +0.011 (76), 2019 -0.107 (258), 2020 -0.076 (254), 2021 -0.060 (259), 2022 +0.059 (258), 2023 -0.074 (258), 2024 -0.227 (259), 2025 -0.082 (257), 2026 +0.010 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.077 (t -3.55), colchón 50 % -0.050 (t -2.35), objetivo 1,5:1 -0.048 (t -1.84), objetivo 2:1 -0.068 (t -2.30).

