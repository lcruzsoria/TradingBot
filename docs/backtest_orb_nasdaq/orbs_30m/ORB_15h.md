# ORB de 30 min de las 15:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 15:00–15:30 | 1940 | 48.6 | -0.038 | -2.24 | -0.009 | 0.029 | no |
| 15:15–15:45 | 1890 | 50.4 | +0.003 | +0.18 | +0.032 | 0.029 | no |
| 15:30–16:00 | 1674 | 48.5 | -0.019 | -1.32 | +0.006 | 0.025 | no |
| 15:45–16:15 | 1572 | 47.6 | -0.020 | -1.39 | +0.006 | 0.026 | no |

## Detalle

### ORB 15:00–15:30

Rotura con cuerpo desde las 15:30 hasta las 21:30; a esa hora se cierra. ORB completos: 2026; con rotura: 1940.

**No pasa los criterios**. Coste medio 0.029 R; ancho medio del ORB 0.35 %; cómo terminan: objetivo 452, stop 449, por tiempo 1039.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1940 | 48.6 % | -0.038 | -73.1 | 0.89 | -77.9 | -2.24 |
| Sin costes | 1940 | 49.8 % | -0.009 | -16.9 | 0.97 | -37.3 | -0.52 |
| Long | 992 | 52.5 % | +0.003 | +2.6 | 1.01 | -23.1 | +0.12 |
| Short | 948 | 44.4 % | -0.080 | -75.8 | 0.78 | -79.2 | -3.25 |
| 1.ª mitad | 970 | 49.8 % | -0.020 | -18.9 | 0.94 | -31.4 | -0.82 |
| 2.ª mitad | 970 | 47.3 % | -0.056 | -54.2 | 0.84 | -54.7 | -2.34 |

Por año (R neto medio y operaciones): 2018 -0.026 (70), 2019 -0.008 (245), 2020 +0.004 (241), 2021 -0.085 (240), 2022 -0.007 (241), 2023 -0.120 (230), 2024 -0.025 (236), 2025 +0.048 (236), 2026 -0.130 (201).

Sensibilidad (R neto medio y t): colchón 0 % -0.047 (t -2.64), colchón 50 % -0.036 (t -2.38), objetivo 1,5:1 -0.047 (t -2.55), objetivo 2:1 -0.035 (t -1.79).

### ORB 15:15–15:45

Rotura con cuerpo desde las 15:45 hasta las 21:45; a esa hora se cierra. ORB completos: 2025; con rotura: 1890.

**No pasa los criterios**. Coste medio 0.029 R; ancho medio del ORB 0.35 %; cómo terminan: objetivo 423, stop 365, por tiempo 1102.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1890 | 50.4 % | +0.003 | +5.6 | 1.01 | -42.1 | +0.18 |
| Sin costes | 1890 | 51.9 % | +0.032 | +60.1 | 1.11 | -16.3 | +1.95 |
| Long | 1000 | 53.4 % | +0.043 | +42.8 | 1.16 | -20.5 | +1.95 |
| Short | 890 | 47.0 % | -0.042 | -37.2 | 0.87 | -49.6 | -1.73 |
| 1.ª mitad | 945 | 50.5 % | +0.008 | +7.3 | 1.03 | -22.2 | +0.34 |
| 2.ª mitad | 945 | 50.3 % | -0.002 | -1.8 | 0.99 | -23.0 | -0.08 |

Por año (R neto medio y operaciones): 2018 +0.045 (65), 2019 +0.054 (237), 2020 +0.023 (235), 2021 -0.031 (240), 2022 -0.030 (223), 2023 -0.067 (225), 2024 -0.016 (235), 2025 +0.098 (233), 2026 -0.028 (197).

Sensibilidad (R neto medio y t): colchón 0 % -0.009 (t -0.51), colchón 50 % +0.002 (t +0.15), objetivo 1,5:1 -0.001 (t -0.04), objetivo 2:1 -0.007 (t -0.39).

### ORB 15:30–16:00

Rotura con cuerpo desde las 16:00 hasta las 22:00; a esa hora se cierra. ORB completos: 2024; con rotura: 1674.

**No pasa los criterios**. Coste medio 0.025 R; ancho medio del ORB 0.42 %; cómo terminan: objetivo 211, stop 206, por tiempo 1257.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1674 | 48.5 % | -0.019 | -31.7 | 0.92 | -43.8 | -1.32 |
| Sin costes | 1674 | 50.9 % | +0.006 | +9.9 | 1.03 | -29.4 | +0.41 |
| Long | 923 | 51.1 % | -0.002 | -1.9 | 0.99 | -21.5 | -0.11 |
| Short | 751 | 45.3 % | -0.040 | -29.7 | 0.84 | -34.9 | -1.83 |
| 1.ª mitad | 837 | 52.1 % | +0.005 | +4.2 | 1.02 | -11.5 | +0.25 |
| 2.ª mitad | 837 | 44.9 % | -0.043 | -35.8 | 0.83 | -40.0 | -2.09 |

Por año (R neto medio y operaciones): 2018 -0.045 (61), 2019 -0.007 (224), 2020 +0.041 (203), 2021 +0.016 (198), 2022 -0.038 (200), 2023 -0.018 (186), 2024 -0.003 (199), 2025 -0.058 (213), 2026 -0.079 (190).

Sensibilidad (R neto medio y t): colchón 0 % -0.025 (t -1.60), colchón 50 % -0.017 (t -1.32), objetivo 1,5:1 -0.014 (t -0.90), objetivo 2:1 -0.015 (t -0.96).

### ORB 15:45–16:15

Rotura con cuerpo desde las 16:15 hasta las 22:15; a esa hora se cierra. ORB completos: 2023; con rotura: 1572.

**No pasa los criterios**. Coste medio 0.026 R; ancho medio del ORB 0.42 %; cómo terminan: objetivo 190, stop 193, por tiempo 1189.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1572 | 47.6 % | -0.020 | -32.0 | 0.91 | -44.0 | -1.39 |
| Sin costes | 1572 | 49.3 % | +0.006 | +9.1 | 1.03 | -30.1 | +0.40 |
| Long | 884 | 49.9 % | -0.010 | -8.9 | 0.95 | -15.2 | -0.53 |
| Short | 688 | 44.8 % | -0.033 | -23.0 | 0.87 | -34.8 | -1.48 |
| 1.ª mitad | 786 | 48.7 % | +0.002 | +1.2 | 1.01 | -13.1 | +0.07 |
| 2.ª mitad | 786 | 46.6 % | -0.042 | -33.1 | 0.83 | -40.4 | -2.02 |

Por año (R neto medio y operaciones): 2018 -0.054 (51), 2019 -0.022 (205), 2020 +0.046 (203), 2021 +0.014 (191), 2022 -0.036 (183), 2023 -0.028 (179), 2024 -0.019 (180), 2025 -0.048 (200), 2026 -0.067 (180).

Sensibilidad (R neto medio y t): colchón 0 % -0.025 (t -1.53), colchón 50 % -0.018 (t -1.39), objetivo 1,5:1 -0.019 (t -1.20), objetivo 2:1 -0.024 (t -1.54).

