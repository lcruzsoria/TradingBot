# ORB de 30 min de las 02:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 02:00–02:30 | 2093 | 49.3 | -0.069 | -3.31 | -0.013 | 0.056 | no |
| 02:15–02:45 | 2093 | 49.0 | -0.073 | -3.43 | -0.013 | 0.060 | no |
| 02:30–03:00 | 2095 | 48.9 | -0.082 | -3.86 | -0.023 | 0.059 | no |
| 02:45–03:15 | 2092 | 49.0 | -0.054 | -2.62 | -0.008 | 0.046 | no |

## Detalle

### ORB 02:00–02:30

Rotura con cuerpo desde las 02:30 hasta las 08:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.056 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 915, stop 945, por tiempo 233.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2093 | 49.3 % | -0.069 | -144.4 | 0.86 | -177.6 | -3.31 |
| Sin costes | 2093 | 49.6 % | -0.013 | -27.7 | 0.97 | -73.0 | -0.64 |
| Long | 1123 | 51.3 % | -0.035 | -39.1 | 0.93 | -65.0 | -1.23 |
| Short | 970 | 47.0 % | -0.109 | -105.3 | 0.79 | -115.9 | -3.53 |
| 1.ª mitad | 1047 | 48.4 % | -0.085 | -89.0 | 0.83 | -106.1 | -2.91 |
| 2.ª mitad | 1046 | 50.2 % | -0.053 | -55.4 | 0.89 | -79.9 | -1.78 |

Por año (R neto medio y operaciones): 2018 +0.101 (76), 2019 -0.206 (258), 2020 -0.075 (253), 2021 -0.076 (259), 2022 -0.107 (257), 2023 -0.071 (258), 2024 -0.095 (259), 2025 -0.038 (257), 2026 +0.094 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.082 (t -3.88), colchón 50 % -0.043 (t -2.14), objetivo 1,5:1 -0.051 (t -2.08), objetivo 2:1 -0.063 (t -2.34).

### ORB 02:15–02:45

Rotura con cuerpo desde las 02:45 hasta las 08:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.060 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 954, stop 982, por tiempo 157.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2093 | 49.0 % | -0.073 | -152.1 | 0.86 | -155.0 | -3.43 |
| Sin costes | 2093 | 49.1 % | -0.013 | -26.5 | 0.97 | -53.1 | -0.60 |
| Long | 1093 | 50.8 % | -0.040 | -44.2 | 0.92 | -55.2 | -1.39 |
| Short | 1000 | 47.1 % | -0.108 | -107.9 | 0.80 | -116.5 | -3.49 |
| 1.ª mitad | 1047 | 49.3 % | -0.061 | -63.4 | 0.88 | -82.0 | -2.04 |
| 2.ª mitad | 1046 | 48.8 % | -0.085 | -88.7 | 0.84 | -90.5 | -2.80 |

Por año (R neto medio y operaciones): 2018 -0.106 (76), 2019 -0.149 (257), 2020 -0.056 (254), 2021 -0.061 (259), 2022 -0.021 (257), 2023 +0.019 (258), 2024 -0.110 (259), 2025 -0.127 (257), 2026 -0.065 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.086 (t -4.03), colchón 50 % -0.046 (t -2.20), objetivo 1,5:1 -0.056 (t -2.23), objetivo 2:1 -0.060 (t -2.15).

### ORB 02:30–03:00

Rotura con cuerpo desde las 03:00 hasta las 09:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.059 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 951, stop 1000, por tiempo 144.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 48.9 % | -0.082 | -171.6 | 0.84 | -172.6 | -3.86 |
| Sin costes | 2095 | 49.0 % | -0.023 | -48.2 | 0.95 | -68.8 | -1.08 |
| Long | 1061 | 49.4 % | -0.074 | -78.3 | 0.86 | -78.3 | -2.48 |
| Short | 1034 | 48.5 % | -0.090 | -93.3 | 0.83 | -99.6 | -2.98 |
| 1.ª mitad | 1048 | 49.8 % | -0.066 | -69.7 | 0.87 | -98.8 | -2.23 |
| 2.ª mitad | 1047 | 48.0 % | -0.097 | -101.9 | 0.82 | -106.0 | -3.23 |

Por año (R neto medio y operaciones): 2018 -0.145 (76), 2019 -0.154 (258), 2020 -0.106 (255), 2021 -0.029 (259), 2022 +0.028 (258), 2023 +0.017 (258), 2024 -0.189 (259), 2025 -0.133 (256), 2026 -0.070 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.084 (t -3.90), colchón 50 % -0.072 (t -3.49), objetivo 1,5:1 -0.085 (t -3.38), objetivo 2:1 -0.079 (t -2.84).

### ORB 02:45–03:15

Rotura con cuerpo desde las 03:15 hasta las 09:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.046 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 887, stop 894, por tiempo 311.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2092 | 49.0 % | -0.054 | -112.1 | 0.89 | -129.1 | -2.62 |
| Sin costes | 2092 | 49.3 % | -0.008 | -16.7 | 0.98 | -81.0 | -0.39 |
| Long | 1106 | 50.1 % | -0.038 | -42.5 | 0.92 | -67.8 | -1.37 |
| Short | 986 | 47.9 % | -0.071 | -69.6 | 0.86 | -87.5 | -2.36 |
| 1.ª mitad | 1046 | 51.3 % | -0.010 | -10.8 | 0.98 | -35.0 | -0.36 |
| 2.ª mitad | 1046 | 46.7 % | -0.097 | -101.3 | 0.81 | -117.6 | -3.31 |

Por año (R neto medio y operaciones): 2018 +0.002 (76), 2019 -0.087 (258), 2020 +0.037 (253), 2021 +0.023 (259), 2022 -0.091 (257), 2023 -0.044 (258), 2024 -0.208 (259), 2025 -0.043 (256), 2026 -0.025 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.057 (t -2.72), colchón 50 % -0.055 (t -2.80), objetivo 1,5:1 -0.057 (t -2.42), objetivo 2:1 -0.062 (t -2.40).

