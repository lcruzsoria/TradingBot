# ORB de 30 min de las 22:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 22:00–22:30 | 2095 | 50.4 | -0.060 | -2.85 | +0.015 | 0.075 | no |
| 22:15–22:45 | 2089 | 51.1 | -0.060 | -2.83 | +0.019 | 0.079 | no |
| 22:30–23:00 | 2092 | 50.8 | -0.062 | -2.90 | +0.022 | 0.084 | no |
| 22:45–23:15 | 2096 | 50.3 | -0.074 | -3.43 | +0.014 | 0.088 | no |

## Detalle

### ORB 22:00–22:30

Rotura con cuerpo desde las 22:30 hasta las 04:30 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.075 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 974, stop 946, por tiempo 175.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 50.4 % | -0.060 | -126.2 | 0.88 | -144.1 | -2.85 |
| Sin costes | 2095 | 50.6 % | +0.015 | +30.9 | 1.03 | -38.1 | +0.70 |
| Long | 1105 | 52.9 % | -0.017 | -18.4 | 0.97 | -43.6 | -0.57 |
| Short | 990 | 47.6 % | -0.109 | -107.9 | 0.79 | -118.9 | -3.54 |
| 1.ª mitad | 1048 | 50.7 % | -0.047 | -49.7 | 0.90 | -75.8 | -1.61 |
| 2.ª mitad | 1047 | 50.0 % | -0.073 | -76.6 | 0.86 | -89.2 | -2.41 |

Por año (R neto medio y operaciones): 2018 +0.076 (76), 2019 -0.129 (257), 2020 -0.090 (256), 2021 -0.039 (258), 2022 +0.009 (258), 2023 -0.057 (258), 2024 -0.121 (259), 2025 -0.033 (257), 2026 -0.063 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.080 (t -3.72), colchón 50 % -0.048 (t -2.33), objetivo 1,5:1 -0.045 (t -1.78), objetivo 2:1 -0.034 (t -1.23).

### ORB 22:15–22:45

Rotura con cuerpo desde las 22:45 hasta las 04:45 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2089.

**No pasa los criterios**. Coste medio 0.079 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 998, stop 961, por tiempo 130.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2089 | 51.1 % | -0.060 | -125.9 | 0.88 | -141.7 | -2.83 |
| Sin costes | 2089 | 51.3 % | +0.019 | +39.4 | 1.04 | -39.3 | +0.89 |
| Long | 1109 | 52.3 % | -0.041 | -45.7 | 0.92 | -79.2 | -1.41 |
| Short | 980 | 49.7 % | -0.082 | -80.2 | 0.84 | -91.1 | -2.64 |
| 1.ª mitad | 1045 | 51.8 % | -0.040 | -42.1 | 0.92 | -76.3 | -1.35 |
| 2.ª mitad | 1044 | 50.4 % | -0.080 | -83.8 | 0.85 | -100.0 | -2.65 |

Por año (R neto medio y operaciones): 2018 -0.019 (76), 2019 -0.061 (255), 2020 -0.077 (255), 2021 -0.077 (256), 2022 +0.040 (258), 2023 -0.106 (257), 2024 -0.103 (259), 2025 -0.121 (257), 2026 +0.024 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.083 (t -3.85), colchón 50 % -0.049 (t -2.34), objetivo 1,5:1 -0.063 (t -2.46), objetivo 2:1 -0.034 (t -1.18).

### ORB 22:30–23:00

Rotura con cuerpo desde las 23:00 hasta las 05:00 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.084 R; ancho medio del ORB 0.14 %; cómo terminan: objetivo 1022, stop 970, por tiempo 100.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2092 | 50.8 % | -0.062 | -130.0 | 0.88 | -147.7 | -2.90 |
| Sin costes | 2092 | 51.0 % | +0.022 | +46.2 | 1.05 | -36.1 | +1.03 |
| Long | 1115 | 51.7 % | -0.051 | -57.0 | 0.90 | -73.8 | -1.74 |
| Short | 977 | 49.8 % | -0.075 | -73.0 | 0.86 | -85.5 | -2.39 |
| 1.ª mitad | 1046 | 51.1 % | -0.054 | -56.5 | 0.89 | -79.4 | -1.80 |
| 2.ª mitad | 1046 | 50.6 % | -0.070 | -73.5 | 0.87 | -104.3 | -2.30 |

Por año (R neto medio y operaciones): 2018 -0.029 (76), 2019 -0.070 (256), 2020 -0.094 (255), 2021 -0.100 (258), 2022 +0.075 (258), 2023 -0.146 (258), 2024 -0.147 (259), 2025 -0.064 (256), 2026 +0.059 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.076 (t -3.54), colchón 50 % -0.045 (t -2.15), objetivo 1,5:1 -0.056 (t -2.16), objetivo 2:1 -0.036 (t -1.25).

### ORB 22:45–23:15

Rotura con cuerpo desde las 23:15 hasta las 05:15 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.088 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 1021, stop 992, por tiempo 83.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 50.3 % | -0.074 | -154.5 | 0.86 | -183.4 | -3.43 |
| Sin costes | 2096 | 50.4 % | +0.014 | +29.2 | 1.03 | -54.3 | +0.65 |
| Long | 1112 | 51.3 % | -0.056 | -61.9 | 0.89 | -86.3 | -1.88 |
| Short | 984 | 49.2 % | -0.094 | -92.6 | 0.82 | -110.7 | -3.00 |
| 1.ª mitad | 1048 | 50.6 % | -0.063 | -66.1 | 0.88 | -66.1 | -2.08 |
| 2.ª mitad | 1048 | 50.0 % | -0.084 | -88.4 | 0.84 | -130.6 | -2.76 |

Por año (R neto medio y operaciones): 2018 -0.143 (76), 2019 -0.095 (258), 2020 -0.058 (256), 2021 -0.009 (259), 2022 -0.036 (257), 2023 -0.204 (258), 2024 -0.135 (259), 2025 -0.113 (257), 2026 +0.111 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.098 (t -4.53), colchón 50 % -0.073 (t -3.47), objetivo 1,5:1 -0.071 (t -2.72), objetivo 2:1 -0.055 (t -1.89).

