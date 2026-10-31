# ORB de 45 min de las 11:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 11:00–11:45 | 2047 | 50.2 | -0.006 | -0.32 | +0.014 | 0.020 | no |
| 11:15–12:00 | 2046 | 49.8 | -0.018 | -1.02 | +0.003 | 0.021 | no |
| 11:30–12:15 | 2050 | 48.4 | -0.033 | -1.82 | -0.011 | 0.022 | no |
| 11:45–12:30 | 2055 | 50.2 | -0.016 | -0.86 | +0.008 | 0.024 | no |

## Detalle

### ORB 11:00–11:45

Rotura con cuerpo desde las 11:45 hasta las 17:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2047.

**No pasa los criterios**. Coste medio 0.020 R; ancho medio del ORB 0.51 %; cómo terminan: objetivo 570, stop 538, por tiempo 939.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2047 | 50.2 % | -0.006 | -11.4 | 0.98 | -34.6 | -0.32 |
| Sin costes | 2047 | 51.0 % | +0.014 | +29.3 | 1.04 | -23.4 | +0.82 |
| Long | 1140 | 52.2 % | +0.017 | +19.3 | 1.05 | -17.5 | +0.74 |
| Short | 907 | 47.6 % | -0.034 | -30.7 | 0.91 | -43.1 | -1.26 |
| 1.ª mitad | 1024 | 50.3 % | -0.008 | -8.3 | 0.98 | -31.5 | -0.33 |
| 2.ª mitad | 1023 | 50.0 % | -0.003 | -3.0 | 0.99 | -26.1 | -0.12 |

Por año (R neto medio y operaciones): 2018 -0.065 (76), 2019 -0.037 (251), 2020 +0.118 (254), 2021 -0.072 (255), 2022 +0.004 (254), 2023 -0.026 (255), 2024 +0.008 (253), 2025 +0.066 (243), 2026 -0.104 (206).

Sensibilidad (R neto medio y t): colchón 0 % -0.007 (t -0.39), colchón 50 % +0.010 (t +0.66), objetivo 1,5:1 +0.017 (t +0.88), objetivo 2:1 +0.014 (t +0.66).

### ORB 11:15–12:00

Rotura con cuerpo desde las 12:00 hasta las 18:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2046.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.47 %; cómo terminan: objetivo 590, stop 581, por tiempo 875.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2046 | 49.8 % | -0.018 | -37.2 | 0.95 | -55.0 | -1.02 |
| Sin costes | 2046 | 50.2 % | +0.003 | +6.5 | 1.01 | -29.9 | +0.18 |
| Long | 1107 | 52.5 % | +0.008 | +8.9 | 1.02 | -21.3 | +0.34 |
| Short | 939 | 46.5 % | -0.049 | -46.1 | 0.88 | -56.6 | -1.82 |
| 1.ª mitad | 1023 | 50.8 % | -0.015 | -15.8 | 0.96 | -29.4 | -0.61 |
| 2.ª mitad | 1023 | 48.7 % | -0.021 | -21.4 | 0.94 | -35.8 | -0.84 |

Por año (R neto medio y operaciones): 2018 -0.088 (75), 2019 -0.065 (251), 2020 +0.110 (256), 2021 -0.030 (252), 2022 -0.048 (255), 2023 -0.071 (249), 2024 +0.018 (250), 2025 -0.006 (250), 2026 -0.038 (208).

Sensibilidad (R neto medio y t): colchón 0 % -0.027 (t -1.45), colchón 50 % -0.012 (t -0.73), objetivo 1,5:1 +0.000 (t +0.01), objetivo 2:1 +0.013 (t +0.62).

### ORB 11:30–12:15

Rotura con cuerpo desde las 12:15 hasta las 18:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2050.

**No pasa los criterios**. Coste medio 0.022 R; ancho medio del ORB 0.46 %; cómo terminan: objetivo 599, stop 624, por tiempo 827.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2050 | 48.4 % | -0.033 | -67.3 | 0.91 | -85.5 | -1.82 |
| Sin costes | 2050 | 49.1 % | -0.011 | -22.3 | 0.97 | -57.3 | -0.60 |
| Long | 1095 | 51.0 % | +0.007 | +7.2 | 1.02 | -28.5 | +0.27 |
| Short | 955 | 45.5 % | -0.078 | -74.5 | 0.81 | -83.2 | -2.89 |
| 1.ª mitad | 1025 | 48.9 % | -0.030 | -31.1 | 0.92 | -41.1 | -1.18 |
| 2.ª mitad | 1025 | 48.0 % | -0.035 | -36.2 | 0.91 | -55.7 | -1.40 |

Por año (R neto medio y operaciones): 2018 -0.111 (76), 2019 -0.037 (254), 2020 +0.087 (256), 2021 -0.063 (252), 2022 -0.071 (255), 2023 -0.099 (250), 2024 -0.002 (250), 2025 -0.036 (250), 2026 -0.016 (207).

Sensibilidad (R neto medio y t): colchón 0 % -0.039 (t -2.04), colchón 50 % -0.017 (t -1.01), objetivo 1,5:1 -0.016 (t -0.82), objetivo 2:1 -0.017 (t -0.79).

### ORB 11:45–12:30

Rotura con cuerpo desde las 12:30 hasta las 18:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2055.

**No pasa los criterios**. Coste medio 0.024 R; ancho medio del ORB 0.44 %; cómo terminan: objetivo 627, stop 626, por tiempo 802.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2055 | 50.2 % | -0.016 | -32.2 | 0.96 | -40.8 | -0.86 |
| Sin costes | 2055 | 50.9 % | +0.008 | +16.3 | 1.02 | -21.4 | +0.44 |
| Long | 1127 | 53.0 % | +0.014 | +16.2 | 1.04 | -25.3 | +0.59 |
| Short | 928 | 46.8 % | -0.052 | -48.4 | 0.87 | -62.3 | -1.90 |
| 1.ª mitad | 1028 | 50.1 % | -0.021 | -21.5 | 0.95 | -30.8 | -0.80 |
| 2.ª mitad | 1027 | 50.2 % | -0.010 | -10.6 | 0.97 | -26.5 | -0.41 |

Por año (R neto medio y operaciones): 2018 -0.058 (74), 2019 -0.018 (254), 2020 +0.009 (257), 2021 -0.052 (253), 2022 -0.015 (256), 2023 -0.041 (253), 2024 +0.038 (256), 2025 -0.009 (246), 2026 -0.027 (206).

Sensibilidad (R neto medio y t): colchón 0 % -0.014 (t -0.75), colchón 50 % -0.014 (t -0.86), objetivo 1,5:1 -0.024 (t -1.19), objetivo 2:1 -0.012 (t -0.56).

