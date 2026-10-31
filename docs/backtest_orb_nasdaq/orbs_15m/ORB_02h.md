# ORB de 15 min de las 02:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 02:00–02:15 | 2097 | 49.4 | -0.087 | -4.06 | -0.013 | 0.074 | no |
| 02:15–02:30 | 2095 | 49.7 | -0.087 | -4.03 | -0.002 | 0.085 | no |
| 02:30–02:45 | 2097 | 49.2 | -0.100 | -4.63 | -0.016 | 0.084 | no |
| 02:45–03:00 | 2095 | 50.5 | -0.069 | -3.20 | +0.010 | 0.079 | no |

## Detalle

### ORB 02:00–02:15

Rotura con cuerpo desde las 02:15 hasta las 08:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.074 R; ancho medio del ORB 0.14 %; cómo terminan: objetivo 982, stop 1017, por tiempo 98.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 49.4 % | -0.087 | -183.0 | 0.84 | -196.9 | -4.06 |
| Sin costes | 2097 | 49.5 % | -0.013 | -28.2 | 0.97 | -64.6 | -0.63 |
| Long | 1104 | 51.4 % | -0.044 | -48.5 | 0.91 | -69.7 | -1.49 |
| Short | 993 | 47.0 % | -0.135 | -134.5 | 0.76 | -139.1 | -4.32 |
| 1.ª mitad | 1049 | 48.2 % | -0.105 | -109.8 | 0.80 | -126.9 | -3.45 |
| 2.ª mitad | 1048 | 50.5 % | -0.070 | -73.3 | 0.87 | -79.5 | -2.30 |

Por año (R neto medio y operaciones): 2018 +0.088 (76), 2019 -0.234 (258), 2020 -0.050 (256), 2021 -0.063 (259), 2022 -0.168 (258), 2023 -0.024 (258), 2024 -0.134 (259), 2025 -0.039 (257), 2026 -0.027 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.077 (t -3.56), colchón 50 % -0.062 (t -2.96), objetivo 1,5:1 -0.059 (t -2.28), objetivo 2:1 -0.059 (t -2.03).

### ORB 02:15–02:30

Rotura con cuerpo desde las 02:30 hasta las 08:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.085 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 1013, stop 1020, por tiempo 62.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 49.7 % | -0.087 | -182.3 | 0.84 | -201.1 | -4.03 |
| Sin costes | 2095 | 50.0 % | -0.002 | -5.0 | 1.00 | -61.0 | -0.11 |
| Long | 1120 | 50.8 % | -0.065 | -72.9 | 0.87 | -108.4 | -2.21 |
| Short | 975 | 48.4 % | -0.112 | -109.3 | 0.80 | -118.0 | -3.54 |
| 1.ª mitad | 1048 | 49.3 % | -0.097 | -101.9 | 0.82 | -125.6 | -3.20 |
| 2.ª mitad | 1047 | 50.0 % | -0.077 | -80.3 | 0.86 | -89.9 | -2.50 |

Por año (R neto medio y operaciones): 2018 +0.122 (76), 2019 -0.232 (258), 2020 -0.087 (255), 2021 -0.145 (259), 2022 -0.057 (257), 2023 -0.120 (258), 2024 -0.139 (259), 2025 +0.016 (257), 2026 +0.025 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.113 (t -5.20), colchón 50 % -0.062 (t -2.89), objetivo 1,5:1 -0.060 (t -2.31), objetivo 2:1 -0.066 (t -2.23).

### ORB 02:30–02:45

Rotura con cuerpo desde las 02:45 hasta las 08:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.084 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 1003, stop 1038, por tiempo 56.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 49.2 % | -0.100 | -210.3 | 0.81 | -211.2 | -4.63 |
| Sin costes | 2097 | 49.2 % | -0.016 | -34.1 | 0.97 | -60.5 | -0.75 |
| Long | 1078 | 49.7 % | -0.091 | -98.2 | 0.83 | -102.5 | -3.02 |
| Short | 1019 | 48.6 % | -0.110 | -112.1 | 0.80 | -119.1 | -3.53 |
| 1.ª mitad | 1049 | 49.8 % | -0.086 | -90.1 | 0.84 | -109.4 | -2.82 |
| 2.ª mitad | 1048 | 48.6 % | -0.115 | -120.1 | 0.79 | -125.5 | -3.73 |

Por año (R neto medio y operaciones): 2018 -0.158 (76), 2019 -0.204 (258), 2020 -0.052 (256), 2021 -0.082 (259), 2022 +0.004 (258), 2023 -0.023 (258), 2024 -0.189 (259), 2025 -0.086 (257), 2026 -0.161 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.127 (t -5.86), colchón 50 % -0.074 (t -3.46), objetivo 1,5:1 -0.076 (t -2.89), objetivo 2:1 -0.074 (t -2.47).

### ORB 02:45–03:00

Rotura con cuerpo desde las 03:00 hasta las 09:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.079 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 1037, stop 1016, por tiempo 42.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 50.5 % | -0.069 | -145.6 | 0.87 | -149.4 | -3.20 |
| Sin costes | 2095 | 50.5 % | +0.010 | +20.7 | 1.02 | -45.4 | +0.46 |
| Long | 1045 | 51.2 % | -0.054 | -56.7 | 0.90 | -57.7 | -1.77 |
| Short | 1050 | 49.7 % | -0.085 | -88.9 | 0.84 | -109.2 | -2.75 |
| 1.ª mitad | 1048 | 51.0 % | -0.059 | -62.2 | 0.89 | -82.6 | -1.93 |
| 2.ª mitad | 1047 | 49.9 % | -0.080 | -83.4 | 0.85 | -90.5 | -2.59 |

Por año (R neto medio y operaciones): 2018 -0.047 (76), 2019 -0.191 (258), 2020 -0.037 (255), 2021 -0.028 (259), 2022 -0.018 (258), 2023 +0.013 (258), 2024 -0.135 (259), 2025 -0.102 (256), 2026 -0.062 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.096 (t -4.42), colchón 50 % -0.076 (t -3.55), objetivo 1,5:1 -0.102 (t -3.91), objetivo 2:1 -0.095 (t -3.23).

