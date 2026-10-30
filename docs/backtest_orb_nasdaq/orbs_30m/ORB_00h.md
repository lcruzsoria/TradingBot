# ORB de 30 min de las 00:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 00:00–00:30 | 2095 | 50.8 | -0.079 | -3.64 | +0.017 | 0.096 | no |
| 00:15–00:45 | 2097 | 49.7 | -0.093 | -4.30 | +0.001 | 0.094 | no |
| 00:30–01:00 | 2097 | 50.2 | -0.079 | -3.66 | +0.012 | 0.091 | no |
| 00:45–01:15 | 2095 | 50.3 | -0.067 | -3.10 | +0.013 | 0.079 | no |

## Detalle

### ORB 00:00–00:30

Rotura con cuerpo desde las 00:30 hasta las 06:30; a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.096 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 1043, stop 1006, por tiempo 46.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 50.8 % | -0.079 | -165.5 | 0.85 | -184.4 | -3.64 |
| Sin costes | 2095 | 50.8 % | +0.017 | +36.5 | 1.04 | -41.6 | +0.81 |
| Long | 1077 | 52.4 % | -0.052 | -56.4 | 0.90 | -79.8 | -1.73 |
| Short | 1018 | 49.1 % | -0.107 | -109.1 | 0.80 | -117.7 | -3.44 |
| 1.ª mitad | 1048 | 50.5 % | -0.086 | -89.9 | 0.84 | -97.5 | -2.80 |
| 2.ª mitad | 1047 | 51.1 % | -0.072 | -75.6 | 0.86 | -91.4 | -2.35 |

Por año (R neto medio y operaciones): 2018 +0.025 (76), 2019 -0.141 (258), 2020 -0.021 (256), 2021 -0.088 (259), 2022 -0.121 (258), 2023 -0.176 (258), 2024 -0.022 (259), 2025 -0.101 (255), 2026 +0.024 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.082 (t -3.77), colchón 50 % -0.070 (t -3.25), objetivo 1,5:1 -0.092 (t -3.51), objetivo 2:1 -0.057 (t -1.90).

### ORB 00:15–00:45

Rotura con cuerpo desde las 00:45 hasta las 06:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.094 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 1019, stop 1016, por tiempo 62.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 49.7 % | -0.093 | -195.3 | 0.83 | -211.7 | -4.30 |
| Sin costes | 2097 | 49.8 % | +0.001 | +1.6 | 1.00 | -67.0 | +0.04 |
| Long | 1070 | 50.9 % | -0.069 | -73.9 | 0.87 | -91.3 | -2.27 |
| Short | 1027 | 48.5 % | -0.118 | -121.4 | 0.78 | -127.8 | -3.83 |
| 1.ª mitad | 1049 | 46.6 % | -0.154 | -161.8 | 0.73 | -165.4 | -5.06 |
| 2.ª mitad | 1048 | 52.9 % | -0.032 | -33.5 | 0.94 | -63.7 | -1.04 |

Por año (R neto medio y operaciones): 2018 -0.145 (76), 2019 -0.202 (258), 2020 -0.042 (256), 2021 -0.181 (259), 2022 -0.149 (258), 2023 -0.038 (258), 2024 -0.105 (259), 2025 -0.041 (257), 2026 +0.054 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.109 (t -5.00), colchón 50 % -0.077 (t -3.57), objetivo 1,5:1 -0.093 (t -3.56), objetivo 2:1 -0.067 (t -2.25).

### ORB 00:30–01:00

Rotura con cuerpo desde las 01:00 hasta las 07:00; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.091 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 1038, stop 1007, por tiempo 52.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 50.2 % | -0.079 | -166.1 | 0.85 | -191.6 | -3.66 |
| Sin costes | 2097 | 50.4 % | +0.012 | +25.6 | 1.03 | -44.5 | +0.56 |
| Long | 1079 | 51.6 % | -0.051 | -55.1 | 0.90 | -79.1 | -1.69 |
| Short | 1018 | 48.7 % | -0.109 | -111.0 | 0.80 | -121.5 | -3.51 |
| 1.ª mitad | 1049 | 48.4 % | -0.118 | -124.3 | 0.78 | -127.3 | -3.88 |
| 2.ª mitad | 1048 | 52.0 % | -0.040 | -41.8 | 0.92 | -83.2 | -1.30 |

Por año (R neto medio y operaciones): 2018 +0.028 (76), 2019 -0.149 (258), 2020 -0.101 (256), 2021 -0.136 (259), 2022 -0.073 (258), 2023 -0.069 (258), 2024 -0.081 (259), 2025 -0.072 (257), 2026 +0.034 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.095 (t -4.38), colchón 50 % -0.062 (t -2.92), objetivo 1,5:1 -0.068 (t -2.59), objetivo 2:1 -0.062 (t -2.08).

### ORB 00:45–01:15

Rotura con cuerpo desde las 01:15 hasta las 07:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.079 R; ancho medio del ORB 0.14 %; cómo terminan: objetivo 1023, stop 994, por tiempo 78.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 50.3 % | -0.067 | -139.9 | 0.87 | -170.7 | -3.10 |
| Sin costes | 2095 | 50.5 % | +0.013 | +26.6 | 1.03 | -56.5 | +0.59 |
| Long | 1080 | 52.2 % | -0.024 | -26.3 | 0.95 | -55.9 | -0.82 |
| Short | 1015 | 48.2 % | -0.112 | -113.6 | 0.80 | -121.0 | -3.60 |
| 1.ª mitad | 1048 | 48.1 % | -0.108 | -113.6 | 0.80 | -115.6 | -3.56 |
| 2.ª mitad | 1047 | 52.4 % | -0.025 | -26.2 | 0.95 | -71.6 | -0.82 |

Por año (R neto medio y operaciones): 2018 -0.010 (76), 2019 -0.079 (257), 2020 -0.110 (256), 2021 -0.095 (259), 2022 -0.124 (258), 2023 -0.037 (258), 2024 -0.111 (259), 2025 -0.054 (256), 2026 +0.084 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.066 (t -3.03), colchón 50 % -0.055 (t -2.58), objetivo 1,5:1 -0.045 (t -1.73), objetivo 2:1 -0.062 (t -2.13).

