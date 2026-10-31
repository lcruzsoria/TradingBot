# ORB de 15 min de las 11:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 11:00–11:15 | 2096 | 49.6 | -0.028 | -1.38 | +0.002 | 0.031 | no |
| 11:15–11:30 | 2095 | 48.1 | -0.062 | -3.01 | -0.029 | 0.034 | no |
| 11:30–11:45 | 2092 | 48.4 | -0.053 | -2.57 | -0.019 | 0.034 | no |
| 11:45–12:00 | 2091 | 50.0 | -0.038 | -1.80 | -0.000 | 0.037 | no |

## Detalle

### ORB 11:00–11:15

Rotura con cuerpo desde las 11:15 hasta las 17:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.031 R; ancho medio del ORB 0.31 %; cómo terminan: objetivo 897, stop 892, por tiempo 307.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 49.6 % | -0.028 | -59.2 | 0.94 | -112.4 | -1.38 |
| Sin costes | 2096 | 49.9 % | +0.002 | +5.1 | 1.01 | -79.7 | +0.12 |
| Long | 1150 | 51.1 % | -0.004 | -4.9 | 0.99 | -48.3 | -0.15 |
| Short | 946 | 47.8 % | -0.057 | -54.3 | 0.88 | -84.1 | -1.87 |
| 1.ª mitad | 1048 | 51.6 % | +0.012 | +12.5 | 1.03 | -38.6 | +0.41 |
| 2.ª mitad | 1048 | 47.6 % | -0.068 | -71.6 | 0.86 | -78.4 | -2.36 |

Por año (R neto medio y operaciones): 2018 +0.135 (76), 2019 +0.015 (258), 2020 +0.118 (259), 2021 -0.096 (258), 2022 -0.063 (258), 2023 -0.166 (257), 2024 -0.063 (259), 2025 +0.018 (256), 2026 -0.040 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.045 (t -2.12), colchón 50 % -0.006 (t -0.32), objetivo 1,5:1 -0.022 (t -0.94), objetivo 2:1 +0.001 (t +0.04).

### ORB 11:15–11:30

Rotura con cuerpo desde las 11:30 hasta las 17:30; a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.034 R; ancho medio del ORB 0.28 %; cómo terminan: objetivo 879, stop 945, por tiempo 271.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 48.1 % | -0.062 | -130.5 | 0.87 | -140.0 | -3.01 |
| Sin costes | 2095 | 48.6 % | -0.029 | -59.8 | 0.94 | -72.3 | -1.38 |
| Long | 1142 | 49.6 % | -0.037 | -42.5 | 0.92 | -43.4 | -1.34 |
| Short | 953 | 46.4 % | -0.092 | -88.0 | 0.82 | -99.2 | -2.98 |
| 1.ª mitad | 1048 | 50.3 % | -0.029 | -30.1 | 0.94 | -53.6 | -0.98 |
| 2.ª mitad | 1047 | 45.9 % | -0.096 | -100.3 | 0.81 | -106.5 | -3.30 |

Por año (R neto medio y operaciones): 2018 +0.102 (76), 2019 -0.149 (258), 2020 -0.011 (259), 2021 -0.011 (258), 2022 -0.019 (258), 2023 -0.083 (257), 2024 -0.044 (258), 2025 -0.082 (256), 2026 -0.166 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.065 (t -3.06), colchón 50 % -0.046 (t -2.32), objetivo 1,5:1 -0.054 (t -2.25), objetivo 2:1 -0.067 (t -2.57).

### ORB 11:30–11:45

Rotura con cuerpo desde las 11:45 hasta las 17:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.034 R; ancho medio del ORB 0.28 %; cómo terminan: objetivo 894, stop 932, por tiempo 266.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2092 | 48.4 % | -0.053 | -111.4 | 0.89 | -120.5 | -2.57 |
| Sin costes | 2092 | 48.8 % | -0.019 | -39.3 | 0.96 | -73.0 | -0.91 |
| Long | 1129 | 49.1 % | -0.045 | -51.1 | 0.91 | -57.7 | -1.61 |
| Short | 963 | 47.7 % | -0.063 | -60.3 | 0.87 | -80.2 | -2.04 |
| 1.ª mitad | 1046 | 49.4 % | -0.041 | -42.4 | 0.92 | -48.6 | -1.37 |
| 2.ª mitad | 1046 | 47.4 % | -0.066 | -69.0 | 0.86 | -82.6 | -2.27 |

Por año (R neto medio y operaciones): 2018 -0.086 (76), 2019 -0.048 (256), 2020 +0.022 (259), 2021 -0.066 (258), 2022 -0.078 (258), 2023 -0.092 (257), 2024 -0.031 (259), 2025 -0.043 (256), 2026 -0.085 (213).

Sensibilidad (R neto medio y t): colchón 0 % -0.058 (t -2.76), colchón 50 % -0.033 (t -1.66), objetivo 1,5:1 -0.033 (t -1.36), objetivo 2:1 -0.019 (t -0.70).

### ORB 11:45–12:00

Rotura con cuerpo desde las 12:00 hasta las 18:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.037 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 918, stop 927, por tiempo 246.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2091 | 50.0 % | -0.038 | -78.4 | 0.92 | -94.7 | -1.80 |
| Sin costes | 2091 | 50.1 % | -0.000 | -0.3 | 1.00 | -49.7 | -0.01 |
| Long | 1086 | 52.5 % | +0.002 | +2.2 | 1.00 | -26.1 | +0.07 |
| Short | 1005 | 47.3 % | -0.080 | -80.6 | 0.84 | -102.6 | -2.66 |
| 1.ª mitad | 1046 | 48.1 % | -0.074 | -77.1 | 0.85 | -86.4 | -2.48 |
| 2.ª mitad | 1045 | 51.9 % | -0.001 | -1.3 | 1.00 | -21.7 | -0.04 |

Por año (R neto medio y operaciones): 2018 -0.007 (76), 2019 -0.175 (257), 2020 +0.027 (259), 2021 -0.137 (258), 2022 -0.032 (258), 2023 -0.040 (257), 2024 +0.088 (257), 2025 +0.007 (255), 2026 -0.047 (214).

Sensibilidad (R neto medio y t): colchón 0 % -0.014 (t -0.68), colchón 50 % -0.043 (t -2.14), objetivo 1,5:1 -0.039 (t -1.61), objetivo 2:1 -0.018 (t -0.67).

