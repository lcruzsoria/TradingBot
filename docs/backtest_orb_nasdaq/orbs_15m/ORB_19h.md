# ORB de 15 min de las 19:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 19:00–19:15 | 2092 | 48.8 | -0.116 | -5.44 | -0.018 | 0.097 | no |
| 19:15–19:30 | 2093 | 49.9 | -0.106 | -4.93 | +0.003 | 0.108 | no |
| 19:30–19:45 | 2094 | 51.0 | -0.075 | -3.52 | +0.026 | 0.101 | no |
| 19:45–20:00 | 2095 | 50.2 | -0.072 | -3.37 | +0.021 | 0.092 | no |

## Detalle

### ORB 19:00–19:15

Rotura con cuerpo desde las 19:15 hasta las 01:15 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.097 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 941, stop 983, por tiempo 168.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2092 | 48.8 % | -0.116 | -241.9 | 0.78 | -247.4 | -5.44 |
| Sin costes | 2092 | 49.1 % | -0.018 | -38.6 | 0.96 | -90.2 | -0.87 |
| Long | 1050 | 51.5 % | -0.075 | -78.8 | 0.85 | -85.3 | -2.50 |
| Short | 1042 | 46.1 % | -0.157 | -163.1 | 0.72 | -167.1 | -5.21 |
| 1.ª mitad | 1046 | 50.8 % | -0.077 | -80.5 | 0.85 | -87.6 | -2.54 |
| 2.ª mitad | 1046 | 46.8 % | -0.154 | -161.4 | 0.72 | -164.6 | -5.19 |

Por año (R neto medio y operaciones): 2018 -0.229 (76), 2019 -0.109 (257), 2020 +0.017 (255), 2021 -0.092 (259), 2022 -0.119 (256), 2023 -0.244 (258), 2024 -0.080 (258), 2025 -0.172 (257), 2026 -0.087 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.113 (t -5.22), colchón 50 % -0.103 (t -4.97), objetivo 1,5:1 -0.112 (t -4.42), objetivo 2:1 -0.118 (t -4.22).

### ORB 19:15–19:30

Rotura con cuerpo desde las 19:30 hasta las 01:30 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.108 R; ancho medio del ORB 0.10 %; cómo terminan: objetivo 986, stop 980, por tiempo 127.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2093 | 49.9 % | -0.106 | -220.9 | 0.80 | -223.0 | -4.93 |
| Sin costes | 2093 | 50.1 % | +0.003 | +5.5 | 1.01 | -43.3 | +0.12 |
| Long | 1080 | 49.7 % | -0.111 | -120.0 | 0.79 | -126.0 | -3.73 |
| Short | 1013 | 50.0 % | -0.100 | -100.9 | 0.81 | -104.8 | -3.24 |
| 1.ª mitad | 1047 | 50.5 % | -0.100 | -104.4 | 0.81 | -109.0 | -3.27 |
| 2.ª mitad | 1046 | 49.2 % | -0.111 | -116.5 | 0.79 | -117.2 | -3.71 |

Por año (R neto medio y operaciones): 2018 -0.243 (76), 2019 -0.138 (256), 2020 -0.024 (257), 2021 -0.014 (257), 2022 -0.206 (258), 2023 -0.170 (257), 2024 -0.105 (259), 2025 -0.092 (257), 2026 -0.044 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.117 (t -5.40), colchón 50 % -0.098 (t -4.64), objetivo 1,5:1 -0.086 (t -3.35), objetivo 2:1 -0.080 (t -2.78).

### ORB 19:30–19:45

Rotura con cuerpo desde las 19:45 hasta las 01:45 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.101 R; ancho medio del ORB 0.11 %; cómo terminan: objetivo 1006, stop 951, por tiempo 137.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 51.0 % | -0.075 | -157.5 | 0.85 | -166.1 | -3.52 |
| Sin costes | 2094 | 51.1 % | +0.026 | +54.9 | 1.06 | -27.7 | +1.23 |
| Long | 1088 | 51.2 % | -0.074 | -80.2 | 0.86 | -95.4 | -2.50 |
| Short | 1006 | 50.8 % | -0.077 | -77.3 | 0.85 | -82.1 | -2.48 |
| 1.ª mitad | 1047 | 51.5 % | -0.062 | -65.3 | 0.88 | -71.6 | -2.06 |
| 2.ª mitad | 1047 | 50.5 % | -0.088 | -92.2 | 0.83 | -102.1 | -2.92 |

Por año (R neto medio y operaciones): 2018 +0.001 (76), 2019 -0.124 (256), 2020 +0.020 (255), 2021 -0.082 (259), 2022 -0.106 (258), 2023 -0.132 (258), 2024 -0.074 (258), 2025 -0.102 (258), 2026 -0.012 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.103 (t -4.76), colchón 50 % -0.057 (t -2.71), objetivo 1,5:1 -0.047 (t -1.84), objetivo 2:1 -0.030 (t -1.04).

### ORB 19:45–20:00

Rotura con cuerpo desde las 20:00 hasta las 02:00 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.092 R; ancho medio del ORB 0.11 %; cómo terminan: objetivo 1001, stop 955, por tiempo 139.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 50.2 % | -0.072 | -150.0 | 0.86 | -166.2 | -3.37 |
| Sin costes | 2095 | 50.5 % | +0.021 | +43.6 | 1.04 | -38.0 | +0.98 |
| Long | 1081 | 50.9 % | -0.053 | -57.4 | 0.89 | -74.0 | -1.81 |
| Short | 1014 | 49.5 % | -0.091 | -92.7 | 0.83 | -102.8 | -2.96 |
| 1.ª mitad | 1048 | 51.2 % | -0.053 | -55.7 | 0.89 | -84.6 | -1.77 |
| 2.ª mitad | 1047 | 49.2 % | -0.090 | -94.3 | 0.83 | -104.3 | -2.99 |

Por año (R neto medio y operaciones): 2018 +0.057 (76), 2019 -0.127 (254), 2020 -0.084 (258), 2021 -0.058 (259), 2022 +0.027 (258), 2023 -0.222 (258), 2024 -0.038 (259), 2025 -0.100 (257), 2026 +0.002 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.091 (t -4.21), colchón 50 % -0.060 (t -2.86), objetivo 1,5:1 -0.062 (t -2.42), objetivo 2:1 -0.063 (t -2.22).

