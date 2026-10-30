# ORB de 15 min de las 22:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 22:00–22:15 | 2096 | 49.6 | -0.102 | -4.71 | -0.004 | 0.097 | no |
| 22:15–22:30 | 2095 | 49.3 | -0.120 | -5.55 | -0.014 | 0.106 | no |
| 22:30–22:45 | 2095 | 51.0 | -0.092 | -4.22 | +0.018 | 0.110 | no |
| 22:45–23:00 | 2097 | 51.3 | -0.092 | -4.22 | +0.028 | 0.120 | no |

## Detalle

### ORB 22:00–22:15

Rotura con cuerpo desde las 22:15 hasta las 04:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.097 R; ancho medio del ORB 0.11 %; cómo terminan: objetivo 1004, stop 1015, por tiempo 77.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 49.6 % | -0.102 | -213.1 | 0.81 | -225.7 | -4.71 |
| Sin costes | 2096 | 49.8 % | -0.004 | -8.8 | 0.99 | -69.5 | -0.19 |
| Long | 1110 | 50.8 % | -0.080 | -88.8 | 0.85 | -98.6 | -2.70 |
| Short | 986 | 48.2 % | -0.126 | -124.3 | 0.77 | -135.9 | -4.01 |
| 1.ª mitad | 1048 | 48.6 % | -0.113 | -118.7 | 0.79 | -124.7 | -3.73 |
| 2.ª mitad | 1048 | 50.6 % | -0.090 | -94.4 | 0.83 | -105.5 | -2.93 |

Por año (R neto medio y operaciones): 2018 +0.013 (76), 2019 -0.122 (257), 2020 -0.163 (256), 2021 -0.121 (259), 2022 -0.071 (258), 2023 -0.134 (258), 2024 -0.090 (259), 2025 -0.024 (257), 2026 -0.126 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.103 (t -4.75), colchón 50 % -0.080 (t -3.75), objetivo 1,5:1 -0.090 (t -3.45), objetivo 2:1 -0.065 (t -2.21).

### ORB 22:15–22:30

Rotura con cuerpo desde las 22:30 hasta las 04:30 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.106 R; ancho medio del ORB 0.10 %; cómo terminan: objetivo 1011, stop 1040, por tiempo 44.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 49.3 % | -0.120 | -252.0 | 0.78 | -254.7 | -5.55 |
| Sin costes | 2095 | 49.3 % | -0.014 | -29.2 | 0.97 | -75.9 | -0.64 |
| Long | 1070 | 52.0 % | -0.075 | -79.9 | 0.86 | -97.3 | -2.46 |
| Short | 1025 | 46.4 % | -0.168 | -172.1 | 0.71 | -172.1 | -5.45 |
| 1.ª mitad | 1048 | 51.4 % | -0.071 | -74.8 | 0.86 | -87.7 | -2.34 |
| 2.ª mitad | 1047 | 47.1 % | -0.169 | -177.3 | 0.71 | -180.9 | -5.51 |

Por año (R neto medio y operaciones): 2018 -0.109 (76), 2019 -0.128 (257), 2020 -0.055 (256), 2021 -0.075 (258), 2022 -0.085 (258), 2023 -0.130 (258), 2024 -0.208 (259), 2025 -0.159 (257), 2026 -0.125 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.135 (t -6.22), colchón 50 % -0.085 (t -3.96), objetivo 1,5:1 -0.109 (t -4.13), objetivo 2:1 -0.090 (t -3.00).

### ORB 22:30–22:45

Rotura con cuerpo desde las 22:45 hasta las 04:45 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.110 R; ancho medio del ORB 0.10 %; cómo terminan: objetivo 1044, stop 1010, por tiempo 41.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 51.0 % | -0.092 | -191.9 | 0.83 | -210.2 | -4.22 |
| Sin costes | 2095 | 51.1 % | +0.018 | +38.2 | 1.04 | -49.3 | +0.84 |
| Long | 1123 | 52.3 % | -0.066 | -74.5 | 0.87 | -101.0 | -2.24 |
| Short | 972 | 49.6 % | -0.121 | -117.4 | 0.78 | -122.8 | -3.78 |
| 1.ª mitad | 1048 | 52.0 % | -0.068 | -70.9 | 0.87 | -80.5 | -2.21 |
| 2.ª mitad | 1047 | 50.0 % | -0.116 | -121.1 | 0.79 | -140.9 | -3.75 |

Por año (R neto medio y operaciones): 2018 -0.088 (76), 2019 -0.117 (256), 2020 -0.057 (256), 2021 -0.096 (259), 2022 +0.013 (258), 2023 -0.238 (258), 2024 -0.201 (259), 2025 -0.076 (257), 2026 +0.063 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.115 (t -5.26), colchón 50 % -0.075 (t -3.49), objetivo 1,5:1 -0.097 (t -3.70), objetivo 2:1 -0.082 (t -2.74).

### ORB 22:45–23:00

Rotura con cuerpo desde las 23:00 hasta las 05:00 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.120 R; ancho medio del ORB 0.09 %; cómo terminan: objetivo 1067, stop 1005, por tiempo 25.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 51.3 % | -0.092 | -192.8 | 0.83 | -208.0 | -4.22 |
| Sin costes | 2097 | 51.3 % | +0.028 | +59.6 | 1.06 | -44.4 | +1.31 |
| Long | 1099 | 52.0 % | -0.081 | -89.3 | 0.85 | -101.9 | -2.69 |
| Short | 998 | 50.5 % | -0.104 | -103.6 | 0.81 | -115.2 | -3.28 |
| 1.ª mitad | 1049 | 52.0 % | -0.073 | -76.5 | 0.86 | -87.6 | -2.37 |
| 2.ª mitad | 1048 | 50.5 % | -0.111 | -116.3 | 0.80 | -135.7 | -3.59 |

Por año (R neto medio y operaciones): 2018 -0.083 (76), 2019 -0.139 (258), 2020 -0.046 (256), 2021 -0.115 (259), 2022 +0.031 (258), 2023 -0.264 (258), 2024 -0.125 (259), 2025 -0.101 (257), 2026 +0.042 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.132 (t -6.03), colchón 50 % -0.074 (t -3.42), objetivo 1,5:1 -0.090 (t -3.37), objetivo 2:1 -0.063 (t -2.05).

