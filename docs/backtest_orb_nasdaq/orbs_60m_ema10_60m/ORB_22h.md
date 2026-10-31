# ORB de 60 min de las 22:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 22:00–23:00 | 1484 | 51.0 | -0.022 | -0.90 | +0.032 | 0.053 | no |
| 22:15–23:15 | 1461 | 51.8 | -0.008 | -0.31 | +0.049 | 0.056 | no |
| 22:30–23:30 | 1457 | 49.7 | -0.045 | -1.81 | +0.014 | 0.059 | no |
| 22:45–23:45 | 1451 | 49.9 | -0.046 | -1.84 | +0.015 | 0.061 | no |

## Detalle

### ORB 22:00–23:00

Rotura con cuerpo desde las 23:00 hasta las 05:00 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2082.

**No pasa los criterios**. Coste medio 0.053 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 622, stop 582, por tiempo 280.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1484 | 51.0 % | -0.022 | -31.9 | 0.95 | -54.8 | -0.90 |
| Sin costes | 1484 | 51.5 % | +0.032 | +46.9 | 1.07 | -36.8 | +1.33 |
| Long | 845 | 53.3 % | +0.009 | +8.0 | 1.02 | -22.7 | +0.30 |
| Short | 639 | 48.0 % | -0.062 | -39.9 | 0.87 | -52.0 | -1.73 |
| 1.ª mitad | 742 | 50.5 % | -0.031 | -22.8 | 0.93 | -54.8 | -0.94 |
| 2.ª mitad | 742 | 51.5 % | -0.012 | -9.1 | 0.97 | -33.8 | -0.36 |

Por año (R neto medio y operaciones): 2018 +0.074 (57), 2019 -0.074 (172), 2020 -0.067 (182), 2021 -0.073 (182), 2022 +0.057 (181), 2023 +0.004 (172), 2024 -0.073 (177), 2025 +0.005 (189), 2026 +0.018 (172).

Sensibilidad (R neto medio y t): colchón 0 % -0.021 (t -0.85), colchón 50 % -0.005 (t -0.21), objetivo 1,5:1 +0.008 (t +0.28), objetivo 2:1 +0.001 (t +0.04).

### ORB 22:15–23:15

Rotura con cuerpo desde las 23:15 hasta las 05:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2085.

**No pasa los criterios**. Coste medio 0.056 R; ancho medio del ORB 0.21 %; cómo terminan: objetivo 649, stop 574, por tiempo 238.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1461 | 51.8 % | -0.008 | -11.0 | 0.98 | -46.7 | -0.31 |
| Sin costes | 1461 | 52.4 % | +0.049 | +71.4 | 1.12 | -21.1 | +2.01 |
| Long | 855 | 53.8 % | +0.016 | +13.4 | 1.04 | -27.4 | +0.50 |
| Short | 606 | 49.0 % | -0.040 | -24.4 | 0.91 | -46.3 | -1.07 |
| 1.ª mitad | 731 | 51.4 % | -0.011 | -8.0 | 0.97 | -40.0 | -0.33 |
| 2.ª mitad | 730 | 52.2 % | -0.004 | -3.0 | 0.99 | -44.4 | -0.12 |

Por año (R neto medio y operaciones): 2018 -0.007 (56), 2019 -0.031 (162), 2020 -0.056 (189), 2021 +0.027 (166), 2022 +0.046 (179), 2023 -0.063 (178), 2024 -0.119 (186), 2025 +0.016 (178), 2026 +0.137 (167).

Sensibilidad (R neto medio y t): colchón 0 % -0.005 (t -0.22), colchón 50 % -0.009 (t -0.40), objetivo 1,5:1 +0.005 (t +0.19), objetivo 2:1 +0.003 (t +0.10).

### ORB 22:30–23:30

Rotura con cuerpo desde las 23:30 hasta las 05:30 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.059 R; ancho medio del ORB 0.20 %; cómo terminan: objetivo 642, stop 616, por tiempo 199.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1457 | 49.7 % | -0.045 | -65.1 | 0.91 | -101.2 | -1.81 |
| Sin costes | 1457 | 50.2 % | +0.014 | +20.4 | 1.03 | -30.2 | +0.57 |
| Long | 838 | 52.3 % | -0.003 | -2.6 | 0.99 | -24.9 | -0.10 |
| Short | 619 | 46.2 % | -0.101 | -62.5 | 0.80 | -80.9 | -2.66 |
| 1.ª mitad | 729 | 47.5 % | -0.078 | -57.0 | 0.84 | -59.0 | -2.28 |
| 2.ª mitad | 728 | 51.9 % | -0.011 | -8.1 | 0.98 | -49.2 | -0.31 |

Por año (R neto medio y operaciones): 2018 -0.192 (58), 2019 -0.109 (167), 2020 -0.073 (183), 2021 +0.009 (174), 2022 -0.097 (185), 2023 -0.051 (174), 2024 -0.173 (175), 2025 +0.025 (178), 2026 +0.176 (163).

Sensibilidad (R neto medio y t): colchón 0 % -0.048 (t -1.91), colchón 50 % -0.018 (t -0.76), objetivo 1,5:1 -0.029 (t -1.00), objetivo 2:1 -0.020 (t -0.62).

### ORB 22:45–23:45

Rotura con cuerpo desde las 23:45 hasta las 05:45 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.061 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 652, stop 622, por tiempo 177.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1451 | 49.9 % | -0.046 | -66.8 | 0.90 | -96.0 | -1.84 |
| Sin costes | 1451 | 50.4 % | +0.015 | +22.0 | 1.03 | -35.6 | +0.61 |
| Long | 816 | 52.1 % | -0.012 | -9.7 | 0.97 | -30.1 | -0.36 |
| Short | 635 | 47.1 % | -0.090 | -57.1 | 0.82 | -72.8 | -2.39 |
| 1.ª mitad | 726 | 47.2 % | -0.088 | -64.2 | 0.82 | -66.6 | -2.54 |
| 2.ª mitad | 725 | 52.6 % | -0.004 | -2.6 | 0.99 | -35.1 | -0.10 |

Por año (R neto medio y operaciones): 2018 -0.181 (56), 2019 -0.115 (169), 2020 -0.071 (181), 2021 -0.020 (175), 2022 -0.109 (178), 2023 -0.051 (173), 2024 -0.064 (176), 2025 -0.002 (183), 2026 +0.118 (160).

Sensibilidad (R neto medio y t): colchón 0 % -0.062 (t -2.43), colchón 50 % -0.053 (t -2.21), objetivo 1,5:1 -0.048 (t -1.62), objetivo 2:1 -0.016 (t -0.50).

