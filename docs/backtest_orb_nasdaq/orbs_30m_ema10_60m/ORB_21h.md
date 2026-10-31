# ORB de 30 min de las 21:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 21:00–21:30 | 1377 | 51.3 | -0.014 | -0.56 | +0.047 | 0.061 | no |
| 21:15–21:45 | 1386 | 53.5 | +0.022 | +0.89 | +0.082 | 0.060 | no |
| 21:30–22:00 | 1376 | 53.0 | +0.008 | +0.33 | +0.071 | 0.062 | no |
| 21:45–22:15 | 1371 | 50.2 | -0.055 | -2.12 | +0.014 | 0.069 | no |

## Detalle

### ORB 21:00–21:30

Rotura con cuerpo desde las 21:30 hasta las 03:30 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.061 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 608, stop 544, por tiempo 225.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1377 | 51.3 % | -0.014 | -19.4 | 0.97 | -50.2 | -0.56 |
| Sin costes | 1377 | 52.0 % | +0.047 | +64.5 | 1.11 | -11.5 | +1.87 |
| Long | 795 | 52.6 % | -0.004 | -3.0 | 0.99 | -38.4 | -0.11 |
| Short | 582 | 49.5 % | -0.028 | -16.4 | 0.94 | -33.0 | -0.73 |
| 1.ª mitad | 689 | 51.1 % | -0.022 | -15.1 | 0.95 | -23.3 | -0.63 |
| 2.ª mitad | 688 | 51.5 % | -0.006 | -4.3 | 0.99 | -33.7 | -0.17 |

Por año (R neto medio y operaciones): 2018 -0.164 (52), 2019 -0.029 (167), 2020 +0.015 (181), 2021 +0.030 (163), 2022 -0.048 (160), 2023 -0.019 (164), 2024 -0.049 (170), 2025 -0.058 (170), 2026 +0.103 (150).

Sensibilidad (R neto medio y t): colchón 0 % -0.031 (t -1.20), colchón 50 % -0.006 (t -0.27), objetivo 1,5:1 -0.007 (t -0.23), objetivo 2:1 +0.009 (t +0.27).

### ORB 21:15–21:45

Rotura con cuerpo desde las 21:45 hasta las 03:45 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2087.

**No pasa los criterios**. Coste medio 0.060 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 632, stop 516, por tiempo 238.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1386 | 53.5 % | +0.022 | +30.7 | 1.05 | -28.2 | +0.89 |
| Sin costes | 1386 | 53.9 % | +0.082 | +114.3 | 1.20 | -16.8 | +3.33 |
| Long | 812 | 53.9 % | +0.029 | +23.4 | 1.07 | -27.5 | +0.90 |
| Short | 574 | 52.8 % | +0.013 | +7.2 | 1.03 | -37.0 | +0.32 |
| 1.ª mitad | 693 | 52.7 % | +0.012 | +8.6 | 1.03 | -23.2 | +0.36 |
| 2.ª mitad | 693 | 54.3 % | +0.032 | +22.0 | 1.07 | -18.3 | +0.89 |

Por año (R neto medio y operaciones): 2018 +0.127 (59), 2019 -0.086 (175), 2020 +0.075 (177), 2021 +0.075 (173), 2022 -0.087 (153), 2023 -0.004 (173), 2024 +0.022 (160), 2025 -0.033 (170), 2026 +0.191 (146).

Sensibilidad (R neto medio y t): colchón 0 % +0.000 (t +0.02), colchón 50 % +0.031 (t +1.32), objetivo 1,5:1 +0.038 (t +1.31), objetivo 2:1 +0.048 (t +1.51).

### ORB 21:30–22:00

Rotura con cuerpo desde las 22:00 hasta las 04:00 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2088.

**No pasa los criterios**. Coste medio 0.062 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 628, stop 526, por tiempo 222.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1376 | 53.0 % | +0.008 | +11.4 | 1.02 | -55.5 | +0.33 |
| Sin costes | 1376 | 53.7 % | +0.071 | +97.4 | 1.17 | -26.2 | +2.83 |
| Long | 787 | 54.4 % | +0.023 | +18.5 | 1.05 | -24.7 | +0.72 |
| Short | 589 | 51.1 % | -0.012 | -7.1 | 0.97 | -49.3 | -0.31 |
| 1.ª mitad | 688 | 50.9 % | -0.027 | -18.6 | 0.94 | -38.3 | -0.78 |
| 2.ª mitad | 688 | 55.1 % | +0.044 | +30.0 | 1.10 | -21.7 | +1.21 |

Por año (R neto medio y operaciones): 2018 +0.081 (55), 2019 -0.015 (179), 2020 -0.084 (174), 2021 +0.058 (168), 2022 -0.135 (150), 2023 -0.073 (172), 2024 +0.105 (164), 2025 +0.046 (162), 2026 +0.150 (152).

Sensibilidad (R neto medio y t): colchón 0 % -0.018 (t -0.70), colchón 50 % +0.025 (t +1.06), objetivo 1,5:1 +0.018 (t +0.63), objetivo 2:1 +0.022 (t +0.69).

### ORB 21:45–22:15

Rotura con cuerpo desde las 22:15 hasta las 04:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.069 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 617, stop 594, por tiempo 160.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1371 | 50.2 % | -0.055 | -74.7 | 0.89 | -89.7 | -2.12 |
| Sin costes | 1371 | 50.3 % | +0.014 | +19.5 | 1.03 | -40.3 | +0.55 |
| Long | 800 | 52.8 % | -0.021 | -16.5 | 0.96 | -29.8 | -0.62 |
| Short | 571 | 46.6 % | -0.102 | -58.2 | 0.80 | -69.7 | -2.54 |
| 1.ª mitad | 686 | 49.0 % | -0.075 | -51.4 | 0.85 | -62.3 | -2.10 |
| 2.ª mitad | 685 | 51.4 % | -0.034 | -23.3 | 0.93 | -30.0 | -0.92 |

Por año (R neto medio y operaciones): 2018 +0.049 (58), 2019 -0.142 (177), 2020 -0.106 (166), 2021 -0.011 (163), 2022 -0.114 (158), 2023 -0.040 (170), 2024 -0.025 (168), 2025 -0.040 (167), 2026 +0.019 (144).

Sensibilidad (R neto medio y t): colchón 0 % -0.063 (t -2.39), colchón 50 % -0.044 (t -1.79), objetivo 1,5:1 -0.046 (t -1.50), objetivo 2:1 -0.032 (t -0.96).

