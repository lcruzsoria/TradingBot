# ORB de 60 min de las 20:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 20:00–21:00 | 2034 | 48.8 | -0.014 | -0.84 | +0.027 | 0.041 | no |
| 20:15–21:15 | 2046 | 48.7 | -0.022 | -1.23 | +0.022 | 0.045 | no |
| 20:30–21:30 | 2059 | 50.0 | -0.013 | -0.69 | +0.033 | 0.046 | no |
| 20:45–21:45 | 2065 | 50.2 | -0.019 | -1.02 | +0.027 | 0.046 | no |

## Detalle

### ORB 20:00–21:00

Rotura con cuerpo desde las 21:00 hasta las 03:00 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2034.

**No pasa los criterios**. Coste medio 0.041 R; ancho medio del ORB 0.28 %; cómo terminan: objetivo 541, stop 473, por tiempo 1020.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2034 | 48.8 % | -0.014 | -28.8 | 0.96 | -62.5 | -0.84 |
| Sin costes | 2034 | 50.6 % | +0.027 | +54.6 | 1.08 | -20.7 | +1.59 |
| Long | 1113 | 50.5 % | +0.005 | +5.9 | 1.02 | -25.1 | +0.23 |
| Short | 921 | 46.7 % | -0.038 | -34.7 | 0.89 | -51.4 | -1.50 |
| 1.ª mitad | 1017 | 48.6 % | -0.016 | -16.8 | 0.95 | -26.8 | -0.70 |
| 2.ª mitad | 1017 | 49.0 % | -0.012 | -12.1 | 0.97 | -40.8 | -0.49 |

Por año (R neto medio y operaciones): 2018 +0.052 (75), 2019 -0.050 (250), 2020 +0.002 (249), 2021 -0.016 (249), 2022 -0.042 (245), 2023 -0.035 (250), 2024 -0.065 (254), 2025 +0.011 (252), 2026 +0.076 (210).

Sensibilidad (R neto medio y t): colchón 0 % -0.026 (t -1.44), colchón 50 % -0.018 (t -1.21), objetivo 1,5:1 +0.000 (t +0.01), objetivo 2:1 +0.006 (t +0.32).

### ORB 20:15–21:15

Rotura con cuerpo desde las 21:15 hasta las 03:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2046.

**No pasa los criterios**. Coste medio 0.045 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 645, stop 587, por tiempo 814.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2046 | 48.7 % | -0.022 | -45.7 | 0.94 | -75.2 | -1.23 |
| Sin costes | 2046 | 50.4 % | +0.022 | +45.8 | 1.06 | -24.0 | +1.24 |
| Long | 1127 | 50.2 % | -0.006 | -7.3 | 0.98 | -42.2 | -0.27 |
| Short | 919 | 46.8 % | -0.042 | -38.4 | 0.89 | -46.5 | -1.53 |
| 1.ª mitad | 1023 | 48.3 % | -0.019 | -19.9 | 0.95 | -31.1 | -0.77 |
| 2.ª mitad | 1023 | 49.1 % | -0.025 | -25.8 | 0.94 | -51.1 | -0.97 |

Por año (R neto medio y operaciones): 2018 +0.037 (73), 2019 -0.072 (249), 2020 -0.024 (252), 2021 +0.019 (253), 2022 -0.031 (250), 2023 -0.080 (255), 2024 -0.070 (254), 2025 +0.004 (249), 2026 +0.075 (211).

Sensibilidad (R neto medio y t): colchón 0 % -0.036 (t -1.87), colchón 50 % -0.011 (t -0.66), objetivo 1,5:1 -0.013 (t -0.63), objetivo 2:1 -0.009 (t -0.40).

### ORB 20:30–21:30

Rotura con cuerpo desde las 21:30 hasta las 03:30 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2059.

**No pasa los criterios**. Coste medio 0.046 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 706, stop 631, por tiempo 722.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2059 | 50.0 % | -0.013 | -26.3 | 0.97 | -65.9 | -0.69 |
| Sin costes | 2059 | 51.1 % | +0.033 | +67.6 | 1.09 | -21.5 | +1.77 |
| Long | 1115 | 52.0 % | +0.008 | +8.8 | 1.02 | -37.5 | +0.32 |
| Short | 944 | 47.6 % | -0.037 | -35.2 | 0.91 | -43.1 | -1.35 |
| 1.ª mitad | 1030 | 50.2 % | -0.013 | -13.2 | 0.97 | -27.4 | -0.50 |
| 2.ª mitad | 1029 | 49.8 % | -0.013 | -13.1 | 0.97 | -47.5 | -0.48 |

Por año (R neto medio y operaciones): 2018 -0.060 (75), 2019 -0.057 (250), 2020 +0.055 (253), 2021 +0.002 (254), 2022 -0.010 (254), 2023 -0.052 (254), 2024 -0.099 (256), 2025 +0.000 (253), 2026 +0.089 (210).

Sensibilidad (R neto medio y t): colchón 0 % -0.019 (t -0.97), colchón 50 % -0.007 (t -0.39), objetivo 1,5:1 -0.020 (t -0.98), objetivo 2:1 -0.010 (t -0.46).

### ORB 20:45–21:45

Rotura con cuerpo desde las 21:45 hasta las 03:45 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2065.

**No pasa los criterios**. Coste medio 0.046 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 725, stop 655, por tiempo 685.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2065 | 50.2 % | -0.019 | -39.5 | 0.95 | -70.2 | -1.02 |
| Sin costes | 2065 | 51.0 % | +0.027 | +55.3 | 1.07 | -29.5 | +1.43 |
| Long | 1116 | 52.5 % | +0.014 | +15.4 | 1.04 | -37.0 | +0.55 |
| Short | 949 | 47.5 % | -0.058 | -54.9 | 0.86 | -70.7 | -2.08 |
| 1.ª mitad | 1033 | 50.6 % | -0.010 | -10.6 | 0.97 | -31.0 | -0.40 |
| 2.ª mitad | 1032 | 49.8 % | -0.028 | -28.9 | 0.93 | -51.6 | -1.03 |

Por año (R neto medio y operaciones): 2018 +0.006 (76), 2019 -0.036 (246), 2020 +0.039 (252), 2021 +0.040 (255), 2022 -0.083 (257), 2023 -0.019 (254), 2024 -0.115 (257), 2025 -0.019 (254), 2026 +0.046 (214).

Sensibilidad (R neto medio y t): colchón 0 % -0.020 (t -1.02), colchón 50 % -0.011 (t -0.65), objetivo 1,5:1 -0.009 (t -0.40), objetivo 2:1 -0.005 (t -0.20).

