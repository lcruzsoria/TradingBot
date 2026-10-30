# ORB de 30 min de las 11:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 11:00–11:30 | 1540 | 51.2 | +0.008 | +0.37 | +0.031 | 0.023 | no |
| 11:15–11:45 | 1497 | 50.3 | -0.006 | -0.29 | +0.018 | 0.024 | no |
| 11:30–12:00 | 1473 | 51.2 | -0.005 | -0.21 | +0.021 | 0.025 | no |
| 11:45–12:15 | 1455 | 50.3 | -0.008 | -0.35 | +0.019 | 0.027 | no |

## Detalle

### ORB 11:00–11:30

Rotura con cuerpo desde las 11:30 hasta las 17:30; a esa hora se cierra. ORB completos: 2097; con rotura: 2075.

**No pasa los criterios**. Coste medio 0.023 R; ancho medio del ORB 0.44 %; cómo terminan: objetivo 527, stop 494, por tiempo 519.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1540 | 51.2 % | +0.008 | +12.4 | 1.02 | -25.6 | +0.37 |
| Sin costes | 1540 | 51.9 % | +0.031 | +47.1 | 1.08 | -13.4 | +1.41 |
| Long | 859 | 54.4 % | +0.056 | +48.4 | 1.16 | -11.6 | +1.97 |
| Short | 681 | 47.1 % | -0.053 | -36.0 | 0.88 | -47.9 | -1.60 |
| 1.ª mitad | 770 | 53.2 % | +0.047 | +35.8 | 1.13 | -11.0 | +1.53 |
| 2.ª mitad | 770 | 49.1 % | -0.030 | -23.4 | 0.93 | -25.6 | -0.98 |

Por año (R neto medio y operaciones): 2018 +0.027 (62), 2019 -0.009 (196), 2020 +0.099 (199), 2021 +0.001 (198), 2022 +0.047 (184), 2023 -0.029 (190), 2024 -0.014 (189), 2025 +0.031 (180), 2026 -0.095 (142).

Sensibilidad (R neto medio y t): colchón 0 % +0.012 (t +0.51), colchón 50 % +0.019 (t +0.94), objetivo 1,5:1 +0.023 (t +0.93), objetivo 2:1 +0.030 (t +1.15).

### ORB 11:15–11:45

Rotura con cuerpo desde las 11:45 hasta las 17:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2079.

**No pasa los criterios**. Coste medio 0.024 R; ancho medio del ORB 0.41 %; cómo terminan: objetivo 516, stop 496, por tiempo 485.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1497 | 50.3 % | -0.006 | -9.7 | 0.98 | -24.4 | -0.29 |
| Sin costes | 1497 | 51.0 % | +0.018 | +26.9 | 1.05 | -20.9 | +0.81 |
| Long | 844 | 52.0 % | +0.016 | +13.8 | 1.04 | -19.3 | +0.56 |
| Short | 653 | 48.1 % | -0.036 | -23.5 | 0.91 | -37.7 | -1.06 |
| 1.ª mitad | 749 | 50.7 % | -0.003 | -2.4 | 0.99 | -24.4 | -0.10 |
| 2.ª mitad | 748 | 49.9 % | -0.010 | -7.3 | 0.98 | -20.2 | -0.31 |

Por año (R neto medio y operaciones): 2018 +0.022 (56), 2019 -0.092 (183), 2020 +0.064 (187), 2021 +0.014 (192), 2022 +0.013 (181), 2023 -0.002 (174), 2024 -0.000 (188), 2025 +0.018 (188), 2026 -0.094 (148).

Sensibilidad (R neto medio y t): colchón 0 % -0.015 (t -0.64), colchón 50 % +0.021 (t +1.03), objetivo 1,5:1 +0.018 (t +0.71), objetivo 2:1 +0.015 (t +0.57).

### ORB 11:30–12:00

Rotura con cuerpo desde las 12:00 hasta las 18:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2072.

**No pasa los criterios**. Coste medio 0.025 R; ancho medio del ORB 0.39 %; cómo terminan: objetivo 519, stop 495, por tiempo 459.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1473 | 51.2 % | -0.005 | -7.0 | 0.99 | -28.1 | -0.21 |
| Sin costes | 1473 | 51.5 % | +0.021 | +30.5 | 1.05 | -19.1 | +0.92 |
| Long | 808 | 54.7 % | +0.041 | +33.1 | 1.11 | -17.7 | +1.36 |
| Short | 665 | 46.9 % | -0.060 | -40.1 | 0.86 | -50.5 | -1.79 |
| 1.ª mitad | 737 | 53.1 % | +0.026 | +19.1 | 1.07 | -22.2 | +0.81 |
| 2.ª mitad | 736 | 49.3 % | -0.035 | -26.1 | 0.91 | -28.1 | -1.13 |

Por año (R neto medio y operaciones): 2018 +0.051 (55), 2019 -0.095 (172), 2020 +0.121 (186), 2021 +0.012 (173), 2022 +0.014 (187), 2023 -0.049 (171), 2024 +0.048 (188), 2025 -0.038 (194), 2026 -0.095 (147).

Sensibilidad (R neto medio y t): colchón 0 % -0.005 (t -0.23), colchón 50 % +0.007 (t +0.32), objetivo 1,5:1 -0.000 (t -0.00), objetivo 2:1 +0.019 (t +0.68).

### ORB 11:45–12:15

Rotura con cuerpo desde las 12:15 hasta las 18:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2077.

**No pasa los criterios**. Coste medio 0.027 R; ancho medio del ORB 0.37 %; cómo terminan: objetivo 532, stop 514, por tiempo 409.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1455 | 50.3 % | -0.008 | -11.6 | 0.98 | -27.3 | -0.35 |
| Sin costes | 1455 | 51.0 % | +0.019 | +27.3 | 1.05 | -18.7 | +0.82 |
| Long | 816 | 52.3 % | +0.018 | +14.5 | 1.04 | -16.3 | +0.58 |
| Short | 639 | 47.7 % | -0.041 | -26.1 | 0.90 | -38.6 | -1.17 |
| 1.ª mitad | 728 | 49.6 % | -0.021 | -14.9 | 0.95 | -27.3 | -0.62 |
| 2.ª mitad | 727 | 51.0 % | +0.005 | +3.3 | 1.01 | -14.6 | +0.14 |

Por año (R neto medio y operaciones): 2018 +0.017 (56), 2019 -0.110 (175), 2020 +0.055 (185), 2021 -0.036 (165), 2022 +0.008 (181), 2023 -0.016 (178), 2024 -0.012 (198), 2025 +0.045 (177), 2026 -0.012 (140).

Sensibilidad (R neto medio y t): colchón 0 % +0.002 (t +0.09), colchón 50 % +0.001 (t +0.03), objetivo 1,5:1 -0.008 (t -0.32), objetivo 2:1 +0.007 (t +0.25).

