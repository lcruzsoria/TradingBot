# ORB de 15 min de las 15:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 15:00–15:15 | 1335 | 49.0 | -0.051 | -2.20 | -0.014 | 0.037 | no |
| 15:15–15:30 | 1263 | 50.4 | -0.015 | -0.66 | +0.023 | 0.039 | no |
| 15:30–15:45 | 1285 | 52.1 | +0.023 | +1.03 | +0.057 | 0.035 | no |
| 15:45–16:00 | 1256 | 49.7 | +0.001 | +0.04 | +0.030 | 0.029 | no |

## Detalle

### ORB 15:00–15:15

Rotura con cuerpo desde las 15:15 hasta las 21:15; a esa hora se cierra. ORB completos: 2026; con rotura: 2000.

**No pasa los criterios**. Coste medio 0.037 R; ancho medio del ORB 0.27 %; cómo terminan: objetivo 440, stop 456, por tiempo 439.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1335 | 49.0 % | -0.051 | -68.7 | 0.88 | -85.1 | -2.20 |
| Sin costes | 1335 | 50.0 % | -0.014 | -19.3 | 0.96 | -45.7 | -0.62 |
| Long | 736 | 49.5 % | -0.057 | -42.2 | 0.87 | -52.3 | -1.80 |
| Short | 599 | 48.4 % | -0.044 | -26.6 | 0.89 | -42.9 | -1.29 |
| 1.ª mitad | 668 | 50.0 % | -0.030 | -20.0 | 0.93 | -40.7 | -0.90 |
| 2.ª mitad | 667 | 48.0 % | -0.073 | -48.7 | 0.83 | -58.2 | -2.21 |

Por año (R neto medio y operaciones): 2018 +0.129 (50), 2019 -0.077 (162), 2020 -0.099 (180), 2021 -0.038 (167), 2022 +0.026 (172), 2023 -0.135 (170), 2024 -0.091 (168), 2025 -0.036 (131), 2026 -0.000 (135).

Sensibilidad (R neto medio y t): colchón 0 % -0.057 (t -2.33), colchón 50 % -0.056 (t -2.55), objetivo 1,5:1 -0.051 (t -1.96), objetivo 2:1 -0.039 (t -1.37).

### ORB 15:15–15:30

Rotura con cuerpo desde las 15:30 hasta las 21:30; a esa hora se cierra. ORB completos: 2026; con rotura: 2005.

**No pasa los criterios**. Coste medio 0.039 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 425, stop 380, por tiempo 458.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1263 | 50.4 % | -0.015 | -19.5 | 0.96 | -52.4 | -0.66 |
| Sin costes | 1263 | 51.1 % | +0.023 | +29.1 | 1.06 | -28.3 | +0.98 |
| Long | 686 | 53.1 % | +0.005 | +3.5 | 1.01 | -32.9 | +0.16 |
| Short | 577 | 47.1 % | -0.040 | -23.1 | 0.90 | -30.6 | -1.15 |
| 1.ª mitad | 632 | 53.3 % | +0.019 | +12.3 | 1.05 | -22.7 | +0.59 |
| 2.ª mitad | 631 | 47.4 % | -0.050 | -31.8 | 0.88 | -34.5 | -1.50 |

Por año (R neto medio y operaciones): 2018 -0.031 (55), 2019 +0.071 (159), 2020 +0.054 (176), 2021 -0.040 (154), 2022 -0.052 (167), 2023 -0.116 (154), 2024 -0.027 (155), 2025 +0.043 (121), 2026 -0.058 (122).

Sensibilidad (R neto medio y t): colchón 0 % -0.033 (t -1.32), colchón 50 % -0.013 (t -0.58), objetivo 1,5:1 -0.008 (t -0.31), objetivo 2:1 -0.007 (t -0.24).

### ORB 15:30–15:45

Rotura con cuerpo desde las 15:45 hasta las 21:45; a esa hora se cierra. ORB completos: 2025; con rotura: 1972.

**No pasa los criterios**. Coste medio 0.035 R; ancho medio del ORB 0.27 %; cómo terminan: objetivo 397, stop 320, por tiempo 568.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1285 | 52.1 % | +0.023 | +29.1 | 1.07 | -21.2 | +1.03 |
| Sin costes | 1285 | 53.0 % | +0.057 | +73.7 | 1.18 | -12.9 | +2.60 |
| Long | 716 | 54.2 % | +0.049 | +34.9 | 1.15 | -12.4 | +1.65 |
| Short | 569 | 49.4 % | -0.010 | -5.8 | 0.97 | -18.2 | -0.31 |
| 1.ª mitad | 643 | 54.0 % | +0.057 | +36.9 | 1.18 | -14.0 | +1.86 |
| 2.ª mitad | 642 | 50.2 % | -0.012 | -7.9 | 0.97 | -21.2 | -0.39 |

Por año (R neto medio y operaciones): 2018 -0.035 (45), 2019 +0.094 (162), 2020 +0.129 (174), 2021 -0.006 (174), 2022 +0.060 (156), 2023 -0.075 (142), 2024 -0.042 (155), 2025 +0.095 (144), 2026 -0.090 (133).

Sensibilidad (R neto medio y t): colchón 0 % +0.006 (t +0.28), colchón 50 % +0.021 (t +1.06), objetivo 1,5:1 +0.025 (t +1.01), objetivo 2:1 +0.032 (t +1.19).

### ORB 15:45–16:00

Rotura con cuerpo desde las 16:00 hasta las 22:00; a esa hora se cierra. ORB completos: 2024; con rotura: 1776.

**No pasa los criterios**. Coste medio 0.029 R; ancho medio del ORB 0.34 %; cómo terminan: objetivo 234, stop 204, por tiempo 818.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1256 | 49.7 % | +0.001 | +0.9 | 1.00 | -20.0 | +0.04 |
| Sin costes | 1256 | 51.7 % | +0.030 | +37.8 | 1.12 | -18.1 | +1.62 |
| Long | 735 | 52.1 % | +0.011 | +7.8 | 1.04 | -15.4 | +0.44 |
| Short | 521 | 46.3 % | -0.013 | -6.9 | 0.95 | -15.3 | -0.45 |
| 1.ª mitad | 628 | 52.9 % | +0.017 | +10.5 | 1.06 | -12.3 | +0.63 |
| 2.ª mitad | 628 | 46.5 % | -0.015 | -9.6 | 0.94 | -20.0 | -0.59 |

Por año (R neto medio y operaciones): 2018 -0.094 (50), 2019 +0.016 (185), 2020 +0.026 (160), 2021 +0.022 (153), 2022 +0.024 (142), 2023 -0.009 (131), 2024 +0.022 (151), 2025 +0.029 (151), 2026 -0.112 (133).

Sensibilidad (R neto medio y t): colchón 0 % -0.016 (t -0.81), colchón 50 % -0.005 (t -0.33), objetivo 1,5:1 -0.003 (t -0.13), objetivo 2:1 -0.001 (t -0.06).

