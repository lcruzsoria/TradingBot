# ORB de 45 min de las 00:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 00:00–00:45 | 2095 | 50.3 | -0.065 | -3.03 | +0.013 | 0.077 | no |
| 00:15–01:00 | 2097 | 49.8 | -0.071 | -3.33 | +0.006 | 0.077 | no |
| 00:30–01:15 | 2094 | 50.1 | -0.057 | -2.67 | +0.011 | 0.068 | no |
| 00:45–01:30 | 2094 | 50.7 | -0.040 | -1.87 | +0.024 | 0.064 | no |

## Detalle

### ORB 00:00–00:45

Rotura con cuerpo desde las 00:45 hasta las 06:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.077 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 1007, stop 979, por tiempo 109.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 50.3 % | -0.065 | -135.9 | 0.87 | -157.1 | -3.03 |
| Sin costes | 2095 | 50.4 % | +0.013 | +26.4 | 1.03 | -54.1 | +0.59 |
| Long | 1087 | 52.3 % | -0.032 | -35.1 | 0.93 | -65.5 | -1.09 |
| Short | 1008 | 48.0 % | -0.100 | -100.8 | 0.81 | -112.2 | -3.24 |
| 1.ª mitad | 1048 | 47.4 % | -0.113 | -118.1 | 0.79 | -122.5 | -3.74 |
| 2.ª mitad | 1047 | 53.1 % | -0.017 | -17.8 | 0.97 | -51.6 | -0.56 |

Por año (R neto medio y operaciones): 2018 -0.001 (76), 2019 -0.170 (258), 2020 -0.016 (256), 2021 -0.142 (259), 2022 -0.128 (258), 2023 -0.032 (258), 2024 -0.062 (259), 2025 -0.026 (255), 2026 +0.058 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.074 (t -3.43), colchón 50 % -0.053 (t -2.51), objetivo 1,5:1 -0.064 (t -2.49), objetivo 2:1 -0.033 (t -1.15).

### ORB 00:15–01:00

Rotura con cuerpo desde las 01:00 hasta las 07:00; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.077 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 998, stop 983, por tiempo 116.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 49.8 % | -0.071 | -149.1 | 0.86 | -174.8 | -3.33 |
| Sin costes | 2097 | 50.1 % | +0.006 | +12.3 | 1.01 | -48.4 | +0.27 |
| Long | 1083 | 51.6 % | -0.036 | -39.1 | 0.93 | -69.8 | -1.22 |
| Short | 1014 | 47.9 % | -0.108 | -110.0 | 0.80 | -114.0 | -3.52 |
| 1.ª mitad | 1049 | 48.1 % | -0.104 | -108.7 | 0.81 | -113.0 | -3.43 |
| 2.ª mitad | 1048 | 51.5 % | -0.039 | -40.4 | 0.92 | -89.9 | -1.27 |

Por año (R neto medio y operaciones): 2018 +0.029 (76), 2019 -0.160 (258), 2020 -0.027 (256), 2021 -0.110 (259), 2022 -0.125 (258), 2023 -0.033 (258), 2024 -0.100 (259), 2025 -0.055 (257), 2026 +0.030 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.069 (t -3.19), colchón 50 % -0.054 (t -2.56), objetivo 1,5:1 -0.068 (t -2.68), objetivo 2:1 -0.050 (t -1.74).

### ORB 00:30–01:15

Rotura con cuerpo desde las 01:15 hasta las 07:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.068 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 993, stop 961, por tiempo 140.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 50.1 % | -0.057 | -118.8 | 0.89 | -139.7 | -2.67 |
| Sin costes | 2094 | 50.4 % | +0.011 | +23.3 | 1.02 | -54.7 | +0.52 |
| Long | 1084 | 52.3 % | -0.014 | -15.0 | 0.97 | -43.2 | -0.47 |
| Short | 1010 | 47.7 % | -0.103 | -103.8 | 0.81 | -111.4 | -3.34 |
| 1.ª mitad | 1047 | 48.1 % | -0.093 | -96.8 | 0.82 | -99.5 | -3.09 |
| 2.ª mitad | 1047 | 52.1 % | -0.021 | -22.0 | 0.96 | -61.1 | -0.70 |

Por año (R neto medio y operaciones): 2018 -0.015 (76), 2019 -0.058 (257), 2020 -0.063 (256), 2021 -0.124 (258), 2022 -0.104 (258), 2023 +0.043 (258), 2024 -0.138 (259), 2025 -0.063 (256), 2026 +0.060 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.053 (t -2.46), colchón 50 % -0.047 (t -2.27), objetivo 1,5:1 -0.054 (t -2.12), objetivo 2:1 -0.047 (t -1.66).

### ORB 00:45–01:30

Rotura con cuerpo desde las 01:30 hasta las 07:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.064 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 984, stop 933, por tiempo 177.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 50.7 % | -0.040 | -82.9 | 0.92 | -134.4 | -1.87 |
| Sin costes | 2094 | 51.0 % | +0.024 | +50.7 | 1.05 | -35.4 | +1.15 |
| Long | 1104 | 53.6 % | +0.013 | +14.4 | 1.03 | -39.9 | +0.45 |
| Short | 990 | 47.4 % | -0.098 | -97.3 | 0.81 | -120.8 | -3.18 |
| 1.ª mitad | 1047 | 49.8 % | -0.054 | -56.2 | 0.89 | -71.1 | -1.80 |
| 2.ª mitad | 1047 | 51.6 % | -0.026 | -26.7 | 0.95 | -75.7 | -0.85 |

Por año (R neto medio y operaciones): 2018 +0.066 (76), 2019 -0.031 (257), 2020 -0.033 (255), 2021 -0.075 (259), 2022 -0.075 (258), 2023 -0.025 (258), 2024 -0.136 (259), 2025 -0.063 (256), 2026 +0.116 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.033 (t -1.54), colchón 50 % -0.039 (t -1.91), objetivo 1,5:1 -0.051 (t -2.03), objetivo 2:1 -0.052 (t -1.86).

