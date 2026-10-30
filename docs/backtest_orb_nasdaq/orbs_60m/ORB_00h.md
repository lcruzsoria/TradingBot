# ORB de 60 min de las 00:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 00:00–01:00 | 2095 | 50.6 | -0.047 | -2.21 | +0.021 | 0.067 | no |
| 00:15–01:15 | 2090 | 50.4 | -0.046 | -2.19 | +0.015 | 0.061 | no |
| 00:30–01:30 | 2092 | 50.7 | -0.029 | -1.40 | +0.028 | 0.057 | no |
| 00:45–01:45 | 2089 | 49.7 | -0.058 | -2.81 | -0.004 | 0.054 | no |

## Detalle

### ORB 00:00–01:00

Rotura con cuerpo desde las 01:00 hasta las 07:00; a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.067 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 976, stop 935, por tiempo 184.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 50.6 % | -0.047 | -97.7 | 0.91 | -136.7 | -2.21 |
| Sin costes | 2095 | 50.9 % | +0.021 | +43.2 | 1.04 | -52.1 | +0.98 |
| Long | 1098 | 52.6 % | -0.011 | -12.0 | 0.98 | -49.3 | -0.38 |
| Short | 997 | 48.3 % | -0.086 | -85.7 | 0.83 | -99.4 | -2.80 |
| 1.ª mitad | 1048 | 47.1 % | -0.103 | -107.5 | 0.80 | -113.7 | -3.44 |
| 2.ª mitad | 1047 | 54.1 % | +0.009 | +9.8 | 1.02 | -58.9 | +0.31 |

Por año (R neto medio y operaciones): 2018 -0.003 (76), 2019 -0.119 (258), 2020 -0.031 (256), 2021 -0.116 (259), 2022 -0.126 (258), 2023 -0.011 (258), 2024 -0.037 (259), 2025 -0.032 (255), 2026 +0.114 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.041 (t -1.90), colchón 50 % -0.036 (t -1.75), objetivo 1,5:1 -0.043 (t -1.74), objetivo 2:1 -0.021 (t -0.73).

### ORB 00:15–01:15

Rotura con cuerpo desde las 01:15 hasta las 07:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.061 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 960, stop 925, por tiempo 205.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2090 | 50.4 % | -0.046 | -96.0 | 0.91 | -120.6 | -2.19 |
| Sin costes | 2090 | 50.8 % | +0.015 | +32.1 | 1.03 | -44.2 | +0.73 |
| Long | 1078 | 53.7 % | +0.017 | +18.0 | 1.04 | -33.4 | +0.58 |
| Short | 1012 | 46.8 % | -0.113 | -114.1 | 0.79 | -121.2 | -3.71 |
| 1.ª mitad | 1045 | 48.8 % | -0.079 | -82.5 | 0.84 | -84.6 | -2.67 |
| 2.ª mitad | 1045 | 52.0 % | -0.013 | -13.6 | 0.97 | -64.5 | -0.44 |

Por año (R neto medio y operaciones): 2018 -0.028 (76), 2019 -0.066 (256), 2020 -0.006 (255), 2021 -0.105 (256), 2022 -0.108 (258), 2023 +0.052 (258), 2024 -0.139 (259), 2025 -0.050 (256), 2026 +0.067 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.037 (t -1.75), colchón 50 % -0.042 (t -2.07), objetivo 1,5:1 -0.057 (t -2.31), objetivo 2:1 -0.044 (t -1.60).

### ORB 00:30–01:30

Rotura con cuerpo desde las 01:30 hasta las 07:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.057 R; ancho medio del ORB 0.20 %; cómo terminan: objetivo 961, stop 893, por tiempo 238.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2092 | 50.7 % | -0.029 | -60.8 | 0.94 | -100.6 | -1.40 |
| Sin costes | 2092 | 51.0 % | +0.028 | +59.1 | 1.06 | -39.6 | +1.36 |
| Long | 1106 | 53.3 % | +0.011 | +12.0 | 1.02 | -33.0 | +0.38 |
| Short | 986 | 47.8 % | -0.074 | -72.8 | 0.85 | -93.5 | -2.41 |
| 1.ª mitad | 1046 | 48.9 % | -0.054 | -56.3 | 0.89 | -69.6 | -1.84 |
| 2.ª mitad | 1046 | 52.4 % | -0.004 | -4.5 | 0.99 | -50.2 | -0.15 |

Por año (R neto medio y operaciones): 2018 +0.052 (76), 2019 -0.041 (257), 2020 -0.017 (255), 2021 -0.097 (258), 2022 -0.048 (257), 2023 +0.011 (258), 2024 -0.126 (259), 2025 -0.007 (256), 2026 +0.088 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.025 (t -1.19), colchón 50 % -0.036 (t -1.77), objetivo 1,5:1 -0.049 (t -2.02), objetivo 2:1 -0.047 (t -1.74).

### ORB 00:45–01:45

Rotura con cuerpo desde las 01:45 hasta las 07:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2089.

**No pasa los criterios**. Coste medio 0.054 R; ancho medio del ORB 0.20 %; cómo terminan: objetivo 896, stop 912, por tiempo 281.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2089 | 49.7 % | -0.058 | -121.4 | 0.88 | -149.6 | -2.81 |
| Sin costes | 2089 | 50.1 % | -0.004 | -8.6 | 0.99 | -61.7 | -0.20 |
| Long | 1110 | 52.1 % | -0.026 | -28.6 | 0.94 | -56.0 | -0.92 |
| Short | 979 | 47.0 % | -0.095 | -92.8 | 0.81 | -109.8 | -3.11 |
| 1.ª mitad | 1045 | 49.0 % | -0.069 | -71.9 | 0.86 | -85.6 | -2.35 |
| 2.ª mitad | 1044 | 50.4 % | -0.047 | -49.5 | 0.90 | -76.2 | -1.62 |

Por año (R neto medio y operaciones): 2018 +0.046 (76), 2019 -0.074 (257), 2020 -0.009 (254), 2021 -0.157 (259), 2022 -0.058 (258), 2023 -0.003 (258), 2024 -0.090 (259), 2025 -0.139 (254), 2026 +0.054 (214).

Sensibilidad (R neto medio y t): colchón 0 % -0.039 (t -1.84), colchón 50 % -0.048 (t -2.41), objetivo 1,5:1 -0.063 (t -2.64), objetivo 2:1 -0.066 (t -2.52).

