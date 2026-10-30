# ORB de 45 min de las 18:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 18:00–18:45 | 2025 | 48.9 | -0.048 | -2.60 | +0.001 | 0.049 | no |
| 18:15–19:00 | 2073 | 48.8 | -0.057 | -2.87 | +0.007 | 0.063 | no |
| 18:30–19:15 | 2081 | 48.2 | -0.083 | -4.22 | -0.020 | 0.062 | no |
| 18:45–19:30 | 2076 | 48.6 | -0.077 | -3.93 | -0.015 | 0.062 | no |

## Detalle

### ORB 18:00–18:45

Rotura con cuerpo desde las 18:45 hasta las 00:45 (día siguiente); a esa hora se cierra. ORB completos: 2092; con rotura: 2025.

**No pasa los criterios**. Coste medio 0.049 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 628, stop 641, por tiempo 756.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2025 | 48.9 % | -0.048 | -97.0 | 0.88 | -106.0 | -2.60 |
| Sin costes | 2025 | 50.2 % | +0.001 | +1.8 | 1.00 | -50.9 | +0.05 |
| Long | 1092 | 51.6 % | -0.022 | -24.1 | 0.94 | -47.2 | -0.89 |
| Short | 933 | 45.8 % | -0.078 | -72.9 | 0.82 | -73.9 | -2.82 |
| 1.ª mitad | 1013 | 48.0 % | -0.071 | -72.0 | 0.83 | -74.9 | -2.66 |
| 2.ª mitad | 1012 | 49.8 % | -0.025 | -25.0 | 0.93 | -34.1 | -0.97 |

Por año (R neto medio y operaciones): 2018 -0.258 (70), 2019 -0.026 (247), 2020 -0.005 (245), 2021 -0.104 (259), 2022 -0.125 (249), 2023 -0.054 (250), 2024 +0.058 (242), 2025 +0.004 (250), 2026 -0.070 (213).

Sensibilidad (R neto medio y t): colchón 0 % -0.059 (t -3.01), colchón 50 % -0.043 (t -2.55), objetivo 1,5:1 -0.041 (t -1.96), objetivo 2:1 -0.048 (t -2.24).

### ORB 18:15–19:00

Rotura con cuerpo desde las 19:00 hasta las 01:00 (día siguiente); a esa hora se cierra. ORB completos: 2095; con rotura: 2073.

**No pasa los criterios**. Coste medio 0.063 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 798, stop 776, por tiempo 499.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2073 | 48.8 % | -0.057 | -117.6 | 0.87 | -118.6 | -2.87 |
| Sin costes | 2073 | 49.8 % | +0.007 | +13.5 | 1.02 | -56.7 | +0.33 |
| Long | 1092 | 50.0 % | -0.039 | -42.5 | 0.91 | -60.6 | -1.43 |
| Short | 981 | 47.4 % | -0.077 | -75.1 | 0.84 | -77.7 | -2.66 |
| 1.ª mitad | 1037 | 48.9 % | -0.067 | -69.0 | 0.86 | -70.7 | -2.36 |
| 2.ª mitad | 1036 | 48.6 % | -0.047 | -48.6 | 0.89 | -51.7 | -1.69 |

Por año (R neto medio y operaciones): 2018 -0.154 (72), 2019 -0.013 (253), 2020 +0.014 (254), 2021 -0.149 (259), 2022 -0.118 (255), 2023 -0.061 (256), 2024 +0.046 (255), 2025 -0.027 (253), 2026 -0.127 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.052 (t -2.51), colchón 50 % -0.053 (t -2.83), objetivo 1,5:1 -0.054 (t -2.39), objetivo 2:1 -0.054 (t -2.20).

### ORB 18:30–19:15

Rotura con cuerpo desde las 19:15 hasta las 01:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2081.

**No pasa los criterios**. Coste medio 0.062 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 756, stop 808, por tiempo 517.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2081 | 48.2 % | -0.083 | -171.9 | 0.82 | -172.9 | -4.22 |
| Sin costes | 2081 | 49.1 % | -0.020 | -42.6 | 0.95 | -79.6 | -1.05 |
| Long | 1081 | 50.8 % | -0.050 | -53.7 | 0.89 | -68.9 | -1.84 |
| Short | 1000 | 45.4 % | -0.118 | -118.2 | 0.76 | -118.8 | -4.17 |
| 1.ª mitad | 1041 | 48.6 % | -0.083 | -86.7 | 0.82 | -91.4 | -2.98 |
| 2.ª mitad | 1040 | 47.8 % | -0.082 | -85.2 | 0.82 | -86.0 | -2.99 |

Por año (R neto medio y operaciones): 2018 -0.110 (72), 2019 -0.066 (255), 2020 -0.003 (254), 2021 -0.138 (258), 2022 -0.135 (254), 2023 -0.188 (258), 2024 +0.001 (258), 2025 -0.035 (256), 2026 -0.089 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.090 (t -4.44), colchón 50 % -0.069 (t -3.72), objetivo 1,5:1 -0.076 (t -3.41), objetivo 2:1 -0.081 (t -3.36).

### ORB 18:45–19:30

Rotura con cuerpo desde las 19:30 hasta las 01:30 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2076.

**No pasa los criterios**. Coste medio 0.062 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 770, stop 803, por tiempo 503.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2076 | 48.6 % | -0.077 | -160.2 | 0.83 | -165.4 | -3.93 |
| Sin costes | 2076 | 49.3 % | -0.015 | -30.7 | 0.97 | -88.2 | -0.75 |
| Long | 1077 | 51.3 % | -0.036 | -39.2 | 0.92 | -62.2 | -1.34 |
| Short | 999 | 45.6 % | -0.121 | -120.9 | 0.75 | -122.5 | -4.26 |
| 1.ª mitad | 1038 | 48.6 % | -0.081 | -84.2 | 0.83 | -93.1 | -2.86 |
| 2.ª mitad | 1038 | 48.6 % | -0.073 | -76.0 | 0.83 | -77.4 | -2.69 |

Por año (R neto medio y operaciones): 2018 -0.037 (75), 2019 -0.025 (251), 2020 -0.002 (255), 2021 -0.134 (256), 2022 -0.192 (255), 2023 -0.190 (257), 2024 -0.029 (257), 2025 -0.007 (255), 2026 -0.043 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.088 (t -4.34), colchón 50 % -0.073 (t -3.94), objetivo 1,5:1 -0.074 (t -3.29), objetivo 2:1 -0.074 (t -3.05).

