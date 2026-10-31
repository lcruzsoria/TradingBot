# ORB de 60 min de las 18:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 18:00–19:00 | 1378 | 48.6 | -0.034 | -1.59 | +0.010 | 0.044 | no |
| 18:15–19:15 | 1362 | 49.9 | -0.031 | -1.35 | +0.020 | 0.051 | no |
| 18:30–19:30 | 1360 | 49.2 | -0.046 | -2.00 | +0.005 | 0.051 | no |
| 18:45–19:45 | 1352 | 49.3 | -0.055 | -2.39 | -0.004 | 0.051 | no |

## Detalle

### ORB 18:00–19:00

Rotura con cuerpo desde las 19:00 hasta las 01:00 (día siguiente); a esa hora se cierra. ORB completos: 2092; con rotura: 2016.

**No pasa los criterios**. Coste medio 0.044 R; ancho medio del ORB 0.27 %; cómo terminan: objetivo 382, stop 377, por tiempo 619.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1378 | 48.6 % | -0.034 | -46.5 | 0.91 | -47.9 | -1.59 |
| Sin costes | 1378 | 50.6 % | +0.010 | +13.8 | 1.03 | -27.3 | +0.47 |
| Long | 788 | 51.3 % | -0.014 | -10.8 | 0.96 | -29.0 | -0.50 |
| Short | 590 | 45.1 % | -0.060 | -35.7 | 0.85 | -38.2 | -1.82 |
| 1.ª mitad | 689 | 49.2 % | -0.036 | -24.8 | 0.90 | -26.2 | -1.17 |
| 2.ª mitad | 689 | 48.0 % | -0.032 | -21.7 | 0.91 | -32.6 | -1.07 |

Por año (R neto medio y operaciones): 2018 -0.306 (44), 2019 -0.031 (176), 2020 +0.023 (172), 2021 -0.010 (170), 2022 -0.098 (154), 2023 -0.022 (151), 2024 +0.099 (165), 2025 -0.025 (180), 2026 -0.139 (166).

Sensibilidad (R neto medio y t): colchón 0 % -0.036 (t -1.58), colchón 50 % -0.037 (t -1.89), objetivo 1,5:1 -0.026 (t -1.08), objetivo 2:1 -0.028 (t -1.10).

### ORB 18:15–19:15

Rotura con cuerpo desde las 19:15 hasta las 01:15 (día siguiente); a esa hora se cierra. ORB completos: 2095; con rotura: 2058.

**No pasa los criterios**. Coste medio 0.051 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 453, stop 436, por tiempo 473.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1362 | 49.9 % | -0.031 | -42.1 | 0.92 | -46.1 | -1.35 |
| Sin costes | 1362 | 51.1 % | +0.020 | +27.1 | 1.05 | -23.2 | +0.87 |
| Long | 777 | 51.6 % | -0.023 | -18.2 | 0.94 | -31.4 | -0.78 |
| Short | 585 | 47.7 % | -0.041 | -23.9 | 0.90 | -29.8 | -1.16 |
| 1.ª mitad | 681 | 50.4 % | -0.021 | -14.1 | 0.95 | -22.8 | -0.63 |
| 2.ª mitad | 681 | 49.5 % | -0.041 | -28.0 | 0.90 | -31.8 | -1.29 |

Por año (R neto medio y operaciones): 2018 -0.143 (42), 2019 -0.065 (180), 2020 +0.036 (172), 2021 -0.020 (171), 2022 -0.066 (149), 2023 -0.073 (140), 2024 +0.076 (160), 2025 +0.011 (182), 2026 -0.127 (166).

Sensibilidad (R neto medio y t): colchón 0 % -0.034 (t -1.42), colchón 50 % -0.020 (t -0.93), objetivo 1,5:1 -0.022 (t -0.86), objetivo 2:1 -0.020 (t -0.73).

### ORB 18:30–19:30

Rotura con cuerpo desde las 19:30 hasta las 01:30 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2067.

**No pasa los criterios**. Coste medio 0.051 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 454, stop 447, por tiempo 459.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1360 | 49.2 % | -0.046 | -62.6 | 0.89 | -68.7 | -2.00 |
| Sin costes | 1360 | 50.3 % | +0.005 | +7.1 | 1.01 | -28.7 | +0.23 |
| Long | 767 | 51.2 % | -0.019 | -14.6 | 0.95 | -24.8 | -0.63 |
| Short | 593 | 46.5 % | -0.081 | -47.9 | 0.81 | -57.6 | -2.30 |
| 1.ª mitad | 680 | 49.1 % | -0.043 | -29.6 | 0.90 | -39.8 | -1.30 |
| 2.ª mitad | 680 | 49.3 % | -0.049 | -33.0 | 0.88 | -33.0 | -1.53 |

Por año (R neto medio y operaciones): 2018 +0.037 (40), 2019 -0.075 (169), 2020 +0.026 (170), 2021 -0.056 (171), 2022 -0.151 (157), 2023 -0.108 (146), 2024 +0.045 (153), 2025 -0.027 (188), 2026 -0.051 (166).

Sensibilidad (R neto medio y t): colchón 0 % -0.054 (t -2.23), colchón 50 % -0.030 (t -1.38), objetivo 1,5:1 -0.026 (t -0.99), objetivo 2:1 -0.041 (t -1.50).

### ORB 18:45–19:45

Rotura con cuerpo desde las 19:45 hasta las 01:45 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2067.

**No pasa los criterios**. Coste medio 0.051 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 448, stop 452, por tiempo 452.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1352 | 49.3 % | -0.055 | -74.4 | 0.87 | -87.2 | -2.39 |
| Sin costes | 1352 | 49.9 % | -0.004 | -5.4 | 0.99 | -35.9 | -0.17 |
| Long | 775 | 51.7 % | -0.018 | -14.1 | 0.95 | -36.3 | -0.60 |
| Short | 577 | 46.1 % | -0.105 | -60.3 | 0.77 | -67.4 | -2.93 |
| 1.ª mitad | 676 | 49.4 % | -0.037 | -24.9 | 0.91 | -33.0 | -1.11 |
| 2.ª mitad | 676 | 49.3 % | -0.073 | -49.5 | 0.82 | -55.2 | -2.29 |

Por año (R neto medio y operaciones): 2018 +0.075 (44), 2019 -0.064 (175), 2020 +0.013 (161), 2021 -0.018 (159), 2022 -0.130 (152), 2023 -0.165 (155), 2024 -0.009 (158), 2025 -0.007 (188), 2026 -0.110 (160).

Sensibilidad (R neto medio y t): colchón 0 % -0.061 (t -2.52), colchón 50 % -0.041 (t -1.92), objetivo 1,5:1 -0.043 (t -1.63), objetivo 2:1 -0.049 (t -1.79).

