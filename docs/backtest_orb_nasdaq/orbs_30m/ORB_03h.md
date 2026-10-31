# ORB de 30 min de las 03:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 03:00–03:30 | 2087 | 49.2 | -0.045 | -2.26 | -0.004 | 0.041 | no |
| 03:15–03:45 | 2095 | 50.5 | -0.038 | -1.80 | +0.006 | 0.044 | no |
| 03:30–04:00 | 2096 | 50.0 | -0.045 | -2.13 | +0.001 | 0.047 | no |
| 03:45–04:15 | 2094 | 49.9 | -0.046 | -2.15 | -0.002 | 0.044 | no |

## Detalle

### ORB 03:00–03:30

Rotura con cuerpo desde las 03:30 hasta las 09:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2087.

**No pasa los criterios**. Coste medio 0.041 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 820, stop 811, por tiempo 456.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2087 | 49.2 % | -0.045 | -93.5 | 0.90 | -105.3 | -2.26 |
| Sin costes | 2087 | 49.5 % | -0.004 | -9.0 | 0.99 | -60.5 | -0.22 |
| Long | 1098 | 49.4 % | -0.035 | -38.2 | 0.92 | -64.4 | -1.29 |
| Short | 989 | 48.9 % | -0.056 | -55.3 | 0.88 | -64.1 | -1.93 |
| 1.ª mitad | 1044 | 50.8 % | -0.008 | -8.4 | 0.98 | -25.2 | -0.30 |
| 2.ª mitad | 1043 | 47.6 % | -0.082 | -85.1 | 0.83 | -87.0 | -2.84 |

Por año (R neto medio y operaciones): 2018 +0.030 (76), 2019 -0.049 (258), 2020 +0.016 (253), 2021 +0.041 (257), 2022 -0.088 (254), 2023 -0.061 (258), 2024 -0.098 (259), 2025 -0.099 (256), 2026 -0.042 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.053 (t -2.62), colchón 50 % -0.025 (t -1.34), objetivo 1,5:1 -0.023 (t -1.01), objetivo 2:1 -0.031 (t -1.24).

### ORB 03:15–03:45

Rotura con cuerpo desde las 03:45 hasta las 09:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.044 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 957, stop 947, por tiempo 191.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 50.5 % | -0.038 | -79.4 | 0.92 | -103.6 | -1.80 |
| Sin costes | 2095 | 50.7 % | +0.006 | +13.6 | 1.01 | -45.2 | +0.31 |
| Long | 1132 | 50.4 % | -0.046 | -52.2 | 0.91 | -65.5 | -1.62 |
| Short | 963 | 50.7 % | -0.028 | -27.2 | 0.94 | -59.0 | -0.91 |
| 1.ª mitad | 1048 | 50.1 % | -0.045 | -47.0 | 0.91 | -68.0 | -1.53 |
| 2.ª mitad | 1047 | 51.0 % | -0.031 | -32.4 | 0.94 | -44.4 | -1.03 |

Por año (R neto medio y operaciones): 2018 +0.139 (76), 2019 -0.143 (258), 2020 -0.029 (255), 2021 +0.015 (259), 2022 -0.080 (258), 2023 -0.106 (258), 2024 +0.040 (259), 2025 -0.039 (257), 2026 -0.009 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.051 (t -2.41), colchón 50 % -0.032 (t -1.56), objetivo 1,5:1 -0.031 (t -1.27), objetivo 2:1 -0.023 (t -0.82).

### ORB 03:30–04:00

Rotura con cuerpo desde las 04:00 hasta las 10:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.047 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 991, stop 995, por tiempo 110.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 50.0 % | -0.045 | -95.2 | 0.91 | -111.2 | -2.13 |
| Sin costes | 2096 | 50.2 % | +0.001 | +2.9 | 1.00 | -50.5 | +0.06 |
| Long | 1122 | 50.4 % | -0.042 | -47.6 | 0.91 | -57.7 | -1.46 |
| Short | 974 | 49.6 % | -0.049 | -47.7 | 0.90 | -65.0 | -1.55 |
| 1.ª mitad | 1048 | 50.0 % | -0.054 | -56.1 | 0.89 | -73.6 | -1.79 |
| 2.ª mitad | 1048 | 50.0 % | -0.037 | -39.1 | 0.93 | -51.8 | -1.23 |

Por año (R neto medio y operaciones): 2018 +0.036 (76), 2019 -0.075 (258), 2020 -0.136 (255), 2021 +0.058 (259), 2022 -0.062 (258), 2023 -0.068 (258), 2024 +0.049 (259), 2025 -0.048 (257), 2026 -0.119 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.043 (t -1.97), colchón 50 % -0.040 (t -1.89), objetivo 1,5:1 -0.040 (t -1.56), objetivo 2:1 -0.042 (t -1.47).

### ORB 03:45–04:15

Rotura con cuerpo desde las 04:15 hasta las 10:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.044 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 995, stop 999, por tiempo 100.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 49.9 % | -0.046 | -96.3 | 0.91 | -105.8 | -2.15 |
| Sin costes | 2094 | 50.0 % | -0.002 | -4.1 | 1.00 | -45.8 | -0.09 |
| Long | 1089 | 51.6 % | -0.018 | -19.9 | 0.96 | -38.1 | -0.62 |
| Short | 1005 | 48.1 % | -0.076 | -76.5 | 0.86 | -102.2 | -2.45 |
| 1.ª mitad | 1047 | 49.7 % | -0.057 | -60.2 | 0.89 | -61.2 | -1.91 |
| 2.ª mitad | 1047 | 50.1 % | -0.035 | -36.2 | 0.93 | -48.1 | -1.13 |

Por año (R neto medio y operaciones): 2018 -0.046 (76), 2019 -0.117 (257), 2020 -0.026 (255), 2021 -0.050 (259), 2022 -0.033 (258), 2023 -0.164 (258), 2024 +0.100 (258), 2025 +0.028 (257), 2026 -0.118 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.028 (t -1.30), colchón 50 % -0.053 (t -2.50), objetivo 1,5:1 -0.030 (t -1.17), objetivo 2:1 -0.032 (t -1.11).

