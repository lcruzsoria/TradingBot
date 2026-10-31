# ORB de 30 min de las 01:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 01:00–01:30 | 2094 | 51.1 | -0.041 | -1.92 | +0.031 | 0.072 | no |
| 01:15–01:45 | 2095 | 51.0 | -0.052 | -2.45 | +0.022 | 0.075 | no |
| 01:30–02:00 | 2095 | 50.2 | -0.066 | -3.11 | +0.004 | 0.070 | no |
| 01:45–02:15 | 2094 | 49.5 | -0.066 | -3.13 | -0.006 | 0.060 | no |

## Detalle

### ORB 01:00–01:30

Rotura con cuerpo desde las 01:30 hasta las 07:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.072 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 1015, stop 952, por tiempo 127.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 51.1 % | -0.041 | -85.7 | 0.92 | -134.1 | -1.92 |
| Sin costes | 2094 | 51.4 % | +0.031 | +65.4 | 1.07 | -32.4 | +1.47 |
| Long | 1097 | 54.5 % | +0.021 | +22.7 | 1.04 | -31.4 | +0.71 |
| Short | 997 | 47.4 % | -0.109 | -108.4 | 0.80 | -127.7 | -3.50 |
| 1.ª mitad | 1047 | 50.1 % | -0.057 | -59.8 | 0.89 | -72.1 | -1.90 |
| 2.ª mitad | 1047 | 52.1 % | -0.025 | -25.9 | 0.95 | -67.6 | -0.82 |

Por año (R neto medio y operaciones): 2018 +0.097 (76), 2019 -0.050 (257), 2020 -0.044 (255), 2021 -0.087 (259), 2022 -0.072 (258), 2023 -0.051 (258), 2024 -0.108 (259), 2025 -0.063 (256), 2026 +0.137 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.035 (t -1.63), colchón 50 % -0.045 (t -2.15), objetivo 1,5:1 -0.039 (t -1.54), objetivo 2:1 -0.045 (t -1.56).

### ORB 01:15–01:45

Rotura con cuerpo desde las 01:45 hasta las 07:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.075 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 1019, stop 966, por tiempo 110.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 51.0 % | -0.052 | -109.7 | 0.90 | -139.7 | -2.45 |
| Sin costes | 2095 | 51.2 % | +0.022 | +46.7 | 1.05 | -48.6 | +1.04 |
| Long | 1100 | 53.6 % | -0.007 | -8.0 | 0.98 | -43.5 | -0.25 |
| Short | 995 | 48.0 % | -0.102 | -101.7 | 0.81 | -106.2 | -3.28 |
| 1.ª mitad | 1048 | 49.8 % | -0.077 | -80.8 | 0.85 | -94.8 | -2.55 |
| 2.ª mitad | 1047 | 52.1 % | -0.028 | -28.9 | 0.94 | -60.3 | -0.91 |

Por año (R neto medio y operaciones): 2018 +0.038 (76), 2019 -0.100 (258), 2020 -0.008 (255), 2021 -0.143 (259), 2022 -0.058 (258), 2023 -0.001 (258), 2024 -0.067 (259), 2025 -0.103 (256), 2026 +0.053 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.059 (t -2.74), colchón 50 % -0.052 (t -2.50), objetivo 1,5:1 -0.069 (t -2.70), objetivo 2:1 -0.072 (t -2.53).

### ORB 01:30–02:00

Rotura con cuerpo desde las 02:00 hasta las 08:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.070 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 993, stop 979, por tiempo 123.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 50.2 % | -0.066 | -138.9 | 0.87 | -156.6 | -3.11 |
| Sin costes | 2095 | 50.3 % | +0.004 | +8.7 | 1.01 | -32.4 | +0.20 |
| Long | 1097 | 52.4 % | -0.026 | -28.9 | 0.95 | -38.9 | -0.90 |
| Short | 998 | 47.7 % | -0.110 | -110.0 | 0.80 | -122.7 | -3.55 |
| 1.ª mitad | 1048 | 50.0 % | -0.074 | -77.0 | 0.86 | -91.7 | -2.44 |
| 2.ª mitad | 1047 | 50.3 % | -0.059 | -61.8 | 0.88 | -70.1 | -1.95 |

Por año (R neto medio y operaciones): 2018 +0.047 (76), 2019 -0.122 (258), 2020 -0.037 (254), 2021 -0.055 (259), 2022 -0.105 (258), 2023 -0.031 (258), 2024 -0.092 (259), 2025 -0.059 (257), 2026 -0.061 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.071 (t -3.30), colchón 50 % -0.058 (t -2.77), objetivo 1,5:1 -0.051 (t -1.99), objetivo 2:1 -0.063 (t -2.22).

### ORB 01:45–02:15

Rotura con cuerpo desde las 02:15 hasta las 08:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.060 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 943, stop 958, por tiempo 193.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 49.5 % | -0.066 | -137.9 | 0.87 | -168.1 | -3.13 |
| Sin costes | 2094 | 49.9 % | -0.006 | -12.8 | 0.99 | -53.6 | -0.29 |
| Long | 1125 | 50.8 % | -0.040 | -44.6 | 0.92 | -63.8 | -1.39 |
| Short | 969 | 47.9 % | -0.096 | -93.3 | 0.82 | -111.0 | -3.10 |
| 1.ª mitad | 1047 | 49.1 % | -0.070 | -72.9 | 0.86 | -88.4 | -2.36 |
| 2.ª mitad | 1047 | 49.9 % | -0.062 | -65.1 | 0.88 | -88.1 | -2.07 |

Por año (R neto medio y operaciones): 2018 +0.071 (76), 2019 -0.169 (258), 2020 -0.031 (254), 2021 -0.042 (259), 2022 -0.120 (258), 2023 -0.052 (258), 2024 -0.107 (258), 2025 -0.058 (257), 2026 +0.027 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.060 (t -2.80), colchón 50 % -0.045 (t -2.22), objetivo 1,5:1 -0.047 (t -1.87), objetivo 2:1 -0.057 (t -2.08).

