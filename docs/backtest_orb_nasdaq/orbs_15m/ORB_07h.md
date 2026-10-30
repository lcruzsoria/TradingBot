# ORB de 15 min de las 07:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 07:00–07:15 | 2096 | 49.9 | -0.066 | -3.01 | -0.002 | 0.064 | no |
| 07:15–07:30 | 2096 | 50.0 | -0.071 | -3.28 | +0.000 | 0.072 | no |
| 07:30–07:45 | 2096 | 47.2 | -0.124 | -5.69 | -0.056 | 0.068 | no |
| 07:45–08:00 | 2096 | 49.6 | -0.081 | -3.71 | -0.011 | 0.070 | no |

## Detalle

### ORB 07:00–07:15

Rotura con cuerpo desde las 07:15 hasta las 13:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.064 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 1039, stop 1044, por tiempo 13.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 49.9 % | -0.066 | -137.8 | 0.88 | -151.9 | -3.01 |
| Sin costes | 2096 | 49.9 % | -0.002 | -3.8 | 1.00 | -60.4 | -0.08 |
| Long | 1116 | 47.9 % | -0.106 | -118.5 | 0.81 | -125.3 | -3.56 |
| Short | 980 | 52.0 % | -0.020 | -19.3 | 0.96 | -44.0 | -0.62 |
| 1.ª mitad | 1048 | 51.6 % | -0.035 | -37.0 | 0.93 | -56.8 | -1.14 |
| 2.ª mitad | 1048 | 48.1 % | -0.096 | -100.8 | 0.82 | -109.2 | -3.12 |

Por año (R neto medio y operaciones): 2018 +0.039 (76), 2019 -0.058 (258), 2020 -0.014 (256), 2021 -0.044 (259), 2022 -0.059 (258), 2023 -0.176 (258), 2024 -0.054 (259), 2025 -0.069 (257), 2026 -0.087 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.081 (t -3.69), colchón 50 % -0.063 (t -2.89), objetivo 1,5:1 -0.062 (t -2.31), objetivo 2:1 -0.058 (t -1.88).

### ORB 07:15–07:30

Rotura con cuerpo desde las 07:30 hasta las 13:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.072 R; ancho medio del ORB 0.14 %; cómo terminan: objetivo 1042, stop 1043, por tiempo 11.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 50.0 % | -0.071 | -149.8 | 0.87 | -176.9 | -3.28 |
| Sin costes | 2096 | 50.0 % | +0.000 | +0.5 | 1.00 | -56.2 | +0.01 |
| Long | 1037 | 50.0 % | -0.075 | -78.3 | 0.86 | -93.7 | -2.44 |
| Short | 1059 | 50.1 % | -0.068 | -71.6 | 0.87 | -94.3 | -2.20 |
| 1.ª mitad | 1048 | 52.1 % | -0.034 | -35.2 | 0.93 | -66.7 | -1.09 |
| 2.ª mitad | 1048 | 48.0 % | -0.109 | -114.6 | 0.80 | -119.3 | -3.55 |

Por año (R neto medio y operaciones): 2018 +0.143 (76), 2019 +0.008 (258), 2020 -0.039 (255), 2021 -0.170 (259), 2022 -0.014 (258), 2023 -0.111 (258), 2024 -0.055 (259), 2025 -0.161 (257), 2026 -0.096 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.089 (t -4.07), colchón 50 % -0.050 (t -2.29), objetivo 1,5:1 -0.074 (t -2.79), objetivo 2:1 -0.065 (t -2.11).

### ORB 07:30–07:45

Rotura con cuerpo desde las 07:45 hasta las 13:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.068 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 982, stop 1100, por tiempo 14.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 47.2 % | -0.124 | -259.9 | 0.78 | -268.5 | -5.69 |
| Sin costes | 2096 | 47.2 % | -0.056 | -116.5 | 0.89 | -144.6 | -2.56 |
| Long | 1031 | 46.6 % | -0.140 | -144.1 | 0.76 | -150.7 | -4.49 |
| Short | 1065 | 47.9 % | -0.109 | -115.8 | 0.80 | -124.2 | -3.56 |
| 1.ª mitad | 1048 | 49.6 % | -0.081 | -85.3 | 0.85 | -91.4 | -2.64 |
| 2.ª mitad | 1048 | 44.8 % | -0.167 | -174.6 | 0.72 | -180.2 | -5.42 |

Por año (R neto medio y operaciones): 2018 -0.098 (76), 2019 -0.124 (258), 2020 -0.027 (255), 2021 -0.130 (259), 2022 -0.057 (258), 2023 -0.287 (258), 2024 -0.159 (259), 2025 -0.124 (257), 2026 -0.084 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.125 (t -5.73), colchón 50 % -0.078 (t -3.58), objetivo 1,5:1 -0.110 (t -4.16), objetivo 2:1 -0.108 (t -3.58).

### ORB 07:45–08:00

Rotura con cuerpo desde las 08:00 hasta las 14:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.070 R; ancho medio del ORB 0.14 %; cómo terminan: objetivo 1030, stop 1056, por tiempo 10.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 49.6 % | -0.081 | -169.7 | 0.85 | -177.5 | -3.71 |
| Sin costes | 2096 | 49.6 % | -0.011 | -23.5 | 0.98 | -71.5 | -0.51 |
| Long | 1087 | 46.8 % | -0.138 | -150.3 | 0.76 | -152.2 | -4.57 |
| Short | 1009 | 52.5 % | -0.019 | -19.4 | 0.96 | -40.9 | -0.61 |
| 1.ª mitad | 1048 | 51.3 % | -0.050 | -52.1 | 0.90 | -69.9 | -1.61 |
| 2.ª mitad | 1048 | 47.8 % | -0.112 | -117.5 | 0.80 | -122.0 | -3.63 |

Por año (R neto medio y operaciones): 2018 +0.006 (76), 2019 -0.085 (258), 2020 -0.067 (255), 2021 -0.081 (259), 2022 -0.000 (258), 2023 -0.125 (258), 2024 -0.177 (259), 2025 -0.077 (257), 2026 -0.056 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.106 (t -4.84), colchón 50 % -0.069 (t -3.16), objetivo 1,5:1 -0.070 (t -2.63), objetivo 2:1 -0.049 (t -1.59).

