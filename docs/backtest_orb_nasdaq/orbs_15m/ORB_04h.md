# ORB de 15 min de las 04:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 04:00–04:15 | 2096 | 51.3 | -0.032 | -1.47 | +0.024 | 0.056 | no |
| 04:15–04:30 | 2096 | 50.5 | -0.058 | -2.66 | +0.010 | 0.068 | no |
| 04:30–04:45 | 2097 | 50.3 | -0.064 | -2.94 | +0.008 | 0.072 | no |
| 04:45–05:00 | 2097 | 47.6 | -0.126 | -5.79 | -0.049 | 0.077 | no |

## Detalle

### ORB 04:00–04:15

Rotura con cuerpo desde las 04:15 hasta las 10:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.056 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 1046, stop 998, por tiempo 52.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 51.3 % | -0.032 | -66.8 | 0.94 | -111.7 | -1.47 |
| Sin costes | 2096 | 51.3 % | +0.024 | +51.1 | 1.05 | -40.9 | +1.13 |
| Long | 1079 | 52.1 % | -0.018 | -19.2 | 0.96 | -46.3 | -0.59 |
| Short | 1017 | 50.4 % | -0.047 | -47.6 | 0.91 | -89.1 | -1.50 |
| 1.ª mitad | 1048 | 49.7 % | -0.071 | -74.3 | 0.86 | -78.7 | -2.33 |
| 2.ª mitad | 1048 | 52.9 % | +0.007 | +7.6 | 1.01 | -38.1 | +0.24 |

Por año (R neto medio y operaciones): 2018 -0.045 (76), 2019 -0.122 (258), 2020 +0.021 (255), 2021 -0.159 (259), 2022 -0.032 (258), 2023 -0.104 (258), 2024 +0.054 (259), 2025 +0.078 (257), 2026 +0.024 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.032 (t -1.47), colchón 50 % -0.032 (t -1.47), objetivo 1,5:1 -0.036 (t -1.38), objetivo 2:1 -0.031 (t -1.05).

### ORB 04:15–04:30

Rotura con cuerpo desde las 04:30 hasta las 10:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.068 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 1054, stop 1030, por tiempo 12.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 50.5 % | -0.058 | -121.7 | 0.89 | -145.5 | -2.66 |
| Sin costes | 2096 | 50.5 % | +0.010 | +21.3 | 1.02 | -43.2 | +0.47 |
| Long | 1095 | 51.4 % | -0.040 | -44.3 | 0.92 | -54.3 | -1.34 |
| Short | 1001 | 49.6 % | -0.077 | -77.4 | 0.86 | -104.0 | -2.44 |
| 1.ª mitad | 1048 | 49.1 % | -0.093 | -97.7 | 0.83 | -97.7 | -3.02 |
| 2.ª mitad | 1048 | 51.9 % | -0.023 | -24.0 | 0.95 | -54.4 | -0.74 |

Por año (R neto medio y operaciones): 2018 -0.174 (76), 2019 -0.135 (258), 2020 -0.016 (255), 2021 -0.078 (259), 2022 -0.120 (258), 2023 -0.107 (258), 2024 +0.022 (259), 2025 -0.030 (257), 2026 +0.051 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.053 (t -2.43), colchón 50 % -0.045 (t -2.09), objetivo 1,5:1 -0.047 (t -1.75), objetivo 2:1 -0.031 (t -1.00).

### ORB 04:30–04:45

Rotura con cuerpo desde las 04:45 hasta las 10:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.072 R; ancho medio del ORB 0.14 %; cómo terminan: objetivo 1049, stop 1033, por tiempo 15.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 50.3 % | -0.064 | -134.2 | 0.88 | -154.9 | -2.94 |
| Sin costes | 2097 | 50.4 % | +0.008 | +16.8 | 1.02 | -43.9 | +0.37 |
| Long | 1108 | 51.6 % | -0.040 | -44.1 | 0.92 | -71.2 | -1.33 |
| Short | 989 | 48.8 % | -0.091 | -90.1 | 0.83 | -104.7 | -2.87 |
| 1.ª mitad | 1049 | 49.5 % | -0.086 | -90.0 | 0.84 | -106.6 | -2.79 |
| 2.ª mitad | 1048 | 51.1 % | -0.042 | -44.2 | 0.92 | -58.4 | -1.37 |

Por año (R neto medio y operaciones): 2018 +0.180 (76), 2019 -0.123 (258), 2020 -0.097 (256), 2021 -0.058 (259), 2022 -0.137 (258), 2023 +0.024 (258), 2024 -0.097 (259), 2025 -0.077 (257), 2026 -0.010 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.067 (t -3.08), colchón 50 % -0.037 (t -1.72), objetivo 1,5:1 -0.057 (t -2.14), objetivo 2:1 -0.041 (t -1.34).

### ORB 04:45–05:00

Rotura con cuerpo desde las 05:00 hasta las 11:00; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.077 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 992, stop 1095, por tiempo 10.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 47.6 % | -0.126 | -264.5 | 0.78 | -283.0 | -5.79 |
| Sin costes | 2097 | 47.6 % | -0.049 | -102.7 | 0.91 | -135.5 | -2.25 |
| Long | 1105 | 47.9 % | -0.126 | -139.4 | 0.78 | -149.4 | -4.20 |
| Short | 992 | 47.3 % | -0.126 | -125.0 | 0.78 | -139.3 | -3.98 |
| 1.ª mitad | 1049 | 48.6 % | -0.111 | -116.6 | 0.80 | -130.6 | -3.61 |
| 2.ª mitad | 1048 | 46.6 % | -0.141 | -147.8 | 0.75 | -156.3 | -4.57 |

Por año (R neto medio y operaciones): 2018 +0.157 (76), 2019 -0.153 (258), 2020 -0.188 (256), 2021 -0.094 (259), 2022 -0.100 (258), 2023 -0.146 (258), 2024 -0.143 (259), 2025 -0.166 (257), 2026 -0.097 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.152 (t -6.99), colchón 50 % -0.113 (t -5.19), objetivo 1,5:1 -0.110 (t -4.14), objetivo 2:1 -0.108 (t -3.54).

