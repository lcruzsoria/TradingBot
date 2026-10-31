# ORB de 30 min de las 18:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 18:00–18:30 | 2046 | 49.3 | -0.057 | -2.99 | -0.003 | 0.055 | no |
| 18:15–18:45 | 2077 | 49.6 | -0.066 | -3.22 | +0.008 | 0.074 | no |
| 18:30–19:00 | 2091 | 50.2 | -0.060 | -2.89 | +0.020 | 0.080 | no |
| 18:45–19:15 | 2090 | 48.7 | -0.097 | -4.73 | -0.022 | 0.075 | no |

## Detalle

### ORB 18:00–18:30

Rotura con cuerpo desde las 18:30 hasta las 00:30 (día siguiente); a esa hora se cierra. ORB completos: 2093; con rotura: 2046.

**No pasa los criterios**. Coste medio 0.055 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 702, stop 723, por tiempo 621.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2046 | 49.3 % | -0.057 | -117.5 | 0.87 | -119.6 | -2.99 |
| Sin costes | 2046 | 50.1 % | -0.003 | -5.5 | 0.99 | -49.3 | -0.14 |
| Long | 1109 | 51.9 % | -0.038 | -42.5 | 0.91 | -51.6 | -1.49 |
| Short | 937 | 46.1 % | -0.080 | -75.0 | 0.82 | -81.3 | -2.79 |
| 1.ª mitad | 1023 | 47.7 % | -0.087 | -88.7 | 0.81 | -90.6 | -3.12 |
| 2.ª mitad | 1023 | 50.8 % | -0.028 | -28.8 | 0.93 | -31.5 | -1.06 |

Por año (R neto medio y operaciones): 2018 -0.226 (71), 2019 -0.039 (250), 2020 -0.048 (246), 2021 -0.137 (259), 2022 -0.109 (253), 2023 -0.015 (250), 2024 +0.004 (250), 2025 -0.030 (254), 2026 -0.031 (213).

Sensibilidad (R neto medio y t): colchón 0 % -0.076 (t -3.80), colchón 50 % -0.054 (t -3.04), objetivo 1,5:1 -0.053 (t -2.46), objetivo 2:1 -0.062 (t -2.69).

### ORB 18:15–18:45

Rotura con cuerpo desde las 18:45 hasta las 00:45 (día siguiente); a esa hora se cierra. ORB completos: 2095; con rotura: 2077.

**No pasa los criterios**. Coste medio 0.074 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 880, stop 864, por tiempo 333.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2077 | 49.6 % | -0.066 | -137.0 | 0.86 | -139.5 | -3.22 |
| Sin costes | 2077 | 50.1 % | +0.008 | +16.7 | 1.02 | -58.6 | +0.39 |
| Long | 1091 | 51.9 % | -0.029 | -31.4 | 0.94 | -57.3 | -1.02 |
| Short | 986 | 47.1 % | -0.107 | -105.6 | 0.79 | -112.6 | -3.60 |
| 1.ª mitad | 1039 | 48.7 % | -0.090 | -94.0 | 0.82 | -94.6 | -3.09 |
| 2.ª mitad | 1038 | 50.5 % | -0.041 | -43.0 | 0.91 | -46.6 | -1.45 |

Por año (R neto medio y operaciones): 2018 -0.155 (73), 2019 -0.061 (253), 2020 -0.014 (255), 2021 -0.115 (259), 2022 -0.187 (256), 2023 -0.045 (256), 2024 +0.028 (255), 2025 -0.002 (254), 2026 -0.111 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.067 (t -3.18), colchón 50 % -0.054 (t -2.73), objetivo 1,5:1 -0.049 (t -2.04), objetivo 2:1 -0.053 (t -2.00).

### ORB 18:30–19:00

Rotura con cuerpo desde las 19:00 hasta las 01:00 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.080 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 931, stop 887, por tiempo 273.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2091 | 50.2 % | -0.060 | -125.5 | 0.88 | -130.1 | -2.89 |
| Sin costes | 2091 | 50.6 % | +0.020 | +41.5 | 1.04 | -62.1 | +0.96 |
| Long | 1090 | 51.2 % | -0.043 | -47.2 | 0.91 | -75.3 | -1.51 |
| Short | 1001 | 49.1 % | -0.078 | -78.3 | 0.84 | -84.1 | -2.61 |
| 1.ª mitad | 1046 | 50.2 % | -0.069 | -72.1 | 0.86 | -77.7 | -2.34 |
| 2.ª mitad | 1045 | 50.1 % | -0.051 | -53.4 | 0.89 | -58.6 | -1.75 |

Por año (R neto medio y operaciones): 2018 -0.086 (73), 2019 -0.012 (256), 2020 +0.006 (256), 2021 -0.123 (259), 2022 -0.155 (257), 2023 -0.122 (258), 2024 -0.020 (259), 2025 +0.004 (257), 2026 -0.048 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.071 (t -3.34), colchón 50 % -0.057 (t -2.88), objetivo 1,5:1 -0.046 (t -1.89), objetivo 2:1 -0.062 (t -2.31).

### ORB 18:45–19:15

Rotura con cuerpo desde las 19:15 hasta las 01:15 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.075 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 851, stop 906, por tiempo 333.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2090 | 48.7 % | -0.097 | -202.1 | 0.81 | -207.3 | -4.73 |
| Sin costes | 2090 | 49.2 % | -0.022 | -45.6 | 0.95 | -97.7 | -1.07 |
| Long | 1071 | 51.3 % | -0.058 | -62.2 | 0.88 | -78.7 | -2.04 |
| Short | 1019 | 45.9 % | -0.137 | -140.0 | 0.74 | -142.6 | -4.70 |
| 1.ª mitad | 1045 | 49.5 % | -0.081 | -84.5 | 0.84 | -95.6 | -2.78 |
| 2.ª mitad | 1045 | 47.8 % | -0.113 | -117.6 | 0.78 | -119.2 | -3.93 |

Por año (R neto medio y operaciones): 2018 -0.097 (75), 2019 -0.012 (256), 2020 +0.002 (255), 2021 -0.164 (259), 2022 -0.162 (256), 2023 -0.216 (258), 2024 -0.028 (258), 2025 -0.104 (257), 2026 -0.086 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.108 (t -5.18), colchón 50 % -0.080 (t -4.06), objetivo 1,5:1 -0.091 (t -3.80), objetivo 2:1 -0.095 (t -3.68).

