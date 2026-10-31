# ORB de 15 min de las 14:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 14:00–14:15 | 1369 | 50.9 | -0.019 | -0.79 | +0.018 | 0.037 | no |
| 14:15–14:30 | 1303 | 51.8 | +0.003 | +0.13 | +0.044 | 0.041 | no |
| 14:30–14:45 | 1311 | 49.1 | -0.050 | -2.02 | -0.011 | 0.040 | no |
| 14:45–15:00 | 1335 | 49.4 | -0.032 | -1.30 | +0.008 | 0.040 | no |

## Detalle

### ORB 14:00–14:15

Rotura con cuerpo desde las 14:15 hasta las 20:15; a esa hora se cierra. ORB completos: 2025; con rotura: 2014.

**No pasa los criterios**. Coste medio 0.037 R; ancho medio del ORB 0.28 %; cómo terminan: objetivo 546, stop 528, por tiempo 295.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1369 | 50.9 % | -0.019 | -26.3 | 0.96 | -44.4 | -0.79 |
| Sin costes | 1369 | 51.3 % | +0.018 | +24.7 | 1.04 | -20.9 | +0.74 |
| Long | 772 | 51.7 % | -0.021 | -16.4 | 0.95 | -28.0 | -0.66 |
| Short | 597 | 49.9 % | -0.017 | -9.9 | 0.96 | -26.1 | -0.44 |
| 1.ª mitad | 685 | 50.1 % | -0.043 | -29.2 | 0.91 | -33.6 | -1.22 |
| 2.ª mitad | 684 | 51.8 % | +0.004 | +2.9 | 1.01 | -31.6 | +0.13 |

Por año (R neto medio y operaciones): 2018 +0.000 (39), 2019 -0.070 (171), 2020 -0.052 (187), 2021 -0.030 (157), 2022 -0.021 (178), 2023 +0.109 (172), 2024 -0.083 (182), 2025 -0.076 (163), 2026 +0.104 (120).

Sensibilidad (R neto medio y t): colchón 0 % -0.026 (t -1.02), colchón 50 % -0.013 (t -0.54), objetivo 1,5:1 -0.006 (t -0.23), objetivo 2:1 -0.008 (t -0.26).

### ORB 14:15–14:30

Rotura con cuerpo desde las 14:30 hasta las 20:30; a esa hora se cierra. ORB completos: 2025; con rotura: 2018.

**No pasa los criterios**. Coste medio 0.041 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 563, stop 510, por tiempo 230.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1303 | 51.8 % | +0.003 | +4.3 | 1.01 | -27.4 | +0.13 |
| Sin costes | 1303 | 52.4 % | +0.044 | +58.0 | 1.11 | -18.2 | +1.74 |
| Long | 748 | 52.3 % | +0.005 | +3.8 | 1.01 | -28.5 | +0.15 |
| Short | 555 | 51.2 % | +0.001 | +0.5 | 1.00 | -22.2 | +0.02 |
| 1.ª mitad | 652 | 53.4 % | +0.022 | +14.1 | 1.05 | -27.4 | +0.59 |
| 2.ª mitad | 651 | 50.2 % | -0.015 | -9.8 | 0.97 | -27.4 | -0.42 |

Por año (R neto medio y operaciones): 2018 +0.315 (44), 2019 -0.017 (160), 2020 -0.038 (170), 2021 -0.039 (161), 2022 +0.066 (175), 2023 +0.087 (158), 2024 -0.065 (163), 2025 -0.066 (147), 2026 +0.008 (125).

Sensibilidad (R neto medio y t): colchón 0 % -0.022 (t -0.85), colchón 50 % +0.013 (t +0.53), objetivo 1,5:1 -0.003 (t -0.12), objetivo 2:1 +0.004 (t +0.14).

### ORB 14:30–14:45

Rotura con cuerpo desde las 14:45 hasta las 20:45; a esa hora se cierra. ORB completos: 2026; con rotura: 2018.

**No pasa los criterios**. Coste medio 0.040 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 500, stop 513, por tiempo 298.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1311 | 49.1 % | -0.050 | -65.9 | 0.89 | -73.7 | -2.02 |
| Sin costes | 1311 | 49.5 % | -0.011 | -13.9 | 0.98 | -42.9 | -0.43 |
| Long | 750 | 49.9 % | -0.058 | -43.5 | 0.87 | -52.1 | -1.75 |
| Short | 561 | 48.1 % | -0.040 | -22.4 | 0.91 | -29.1 | -1.05 |
| 1.ª mitad | 656 | 50.6 % | -0.021 | -13.8 | 0.95 | -45.7 | -0.59 |
| 2.ª mitad | 655 | 47.6 % | -0.080 | -52.1 | 0.83 | -58.0 | -2.30 |

Por año (R neto medio y operaciones): 2018 +0.013 (42), 2019 -0.154 (155), 2020 -0.019 (168), 2021 +0.025 (161), 2022 +0.019 (181), 2023 -0.009 (176), 2024 -0.066 (148), 2025 -0.103 (151), 2026 -0.155 (129).

Sensibilidad (R neto medio y t): colchón 0 % -0.070 (t -2.71), colchón 50 % -0.038 (t -1.63), objetivo 1,5:1 -0.037 (t -1.28), objetivo 2:1 -0.029 (t -0.92).

### ORB 14:45–15:00

Rotura con cuerpo desde las 15:00 hasta las 21:00; a esa hora se cierra. ORB completos: 2026; con rotura: 2017.

**No pasa los criterios**. Coste medio 0.040 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 522, stop 506, por tiempo 307.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1335 | 49.4 % | -0.032 | -42.6 | 0.93 | -69.3 | -1.30 |
| Sin costes | 1335 | 50.2 % | +0.008 | +10.8 | 1.02 | -43.9 | +0.33 |
| Long | 732 | 50.7 % | -0.011 | -8.0 | 0.97 | -28.8 | -0.33 |
| Short | 603 | 47.9 % | -0.057 | -34.6 | 0.87 | -46.5 | -1.57 |
| 1.ª mitad | 668 | 51.3 % | -0.001 | -1.0 | 1.00 | -35.5 | -0.04 |
| 2.ª mitad | 667 | 47.5 % | -0.062 | -41.6 | 0.86 | -62.2 | -1.80 |

Por año (R neto medio y operaciones): 2018 +0.042 (46), 2019 -0.049 (144), 2020 -0.084 (180), 2021 +0.029 (167), 2022 +0.052 (174), 2023 -0.047 (185), 2024 -0.181 (158), 2025 -0.076 (150), 2026 +0.094 (131).

Sensibilidad (R neto medio y t): colchón 0 % -0.054 (t -2.11), colchón 50 % -0.031 (t -1.32), objetivo 1,5:1 -0.031 (t -1.09), objetivo 2:1 -0.015 (t -0.49).

