# ORB de 15 min de las 13:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 13:00–13:15 | 1330 | 53.0 | +0.026 | +1.01 | +0.065 | 0.039 | no |
| 13:15–13:30 | 1352 | 51.8 | +0.012 | +0.46 | +0.053 | 0.041 | no |
| 13:30–13:45 | 1317 | 51.6 | +0.002 | +0.08 | +0.044 | 0.041 | no |
| 13:45–14:00 | 1310 | 50.1 | -0.035 | -1.36 | +0.007 | 0.042 | no |

## Detalle

### ORB 13:00–13:15

Rotura con cuerpo desde las 13:15 hasta las 19:15; a esa hora se cierra. ORB completos: 2042; con rotura: 2025.

**No pasa los criterios**. Coste medio 0.039 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 611, stop 527, por tiempo 192.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1330 | 53.0 % | +0.026 | +34.6 | 1.06 | -29.0 | +1.01 |
| Sin costes | 1330 | 53.2 % | +0.065 | +86.7 | 1.15 | -20.4 | +2.53 |
| Long | 756 | 53.2 % | +0.027 | +20.5 | 1.06 | -13.9 | +0.79 |
| Short | 574 | 52.8 % | +0.025 | +14.2 | 1.06 | -25.4 | +0.63 |
| 1.ª mitad | 665 | 52.8 % | +0.034 | +22.3 | 1.08 | -29.0 | +0.91 |
| 2.ª mitad | 665 | 53.2 % | +0.019 | +12.3 | 1.04 | -24.5 | +0.51 |

Por año (R neto medio y operaciones): 2018 +0.145 (45), 2019 -0.013 (159), 2020 -0.049 (183), 2021 -0.027 (160), 2022 +0.276 (168), 2023 +0.041 (158), 2024 -0.063 (171), 2025 +0.027 (157), 2026 -0.022 (129).

Sensibilidad (R neto medio y t): colchón 0 % +0.018 (t +0.69), colchón 50 % +0.016 (t +0.65), objetivo 1,5:1 +0.022 (t +0.71), objetivo 2:1 +0.016 (t +0.49).

### ORB 13:15–13:30

Rotura con cuerpo desde las 13:30 hasta las 19:30; a esa hora se cierra. ORB completos: 2026; con rotura: 2025.

**No pasa los criterios**. Coste medio 0.041 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 627, stop 548, por tiempo 177.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1352 | 51.8 % | +0.012 | +16.0 | 1.03 | -32.8 | +0.46 |
| Sin costes | 1352 | 52.1 % | +0.053 | +71.8 | 1.12 | -23.2 | +2.07 |
| Long | 768 | 51.7 % | -0.003 | -2.3 | 0.99 | -20.9 | -0.09 |
| Short | 584 | 52.1 % | +0.031 | +18.4 | 1.07 | -23.1 | +0.81 |
| 1.ª mitad | 676 | 51.9 % | +0.003 | +2.3 | 1.01 | -32.8 | +0.09 |
| 2.ª mitad | 676 | 51.8 % | +0.020 | +13.7 | 1.05 | -23.0 | +0.56 |

Por año (R neto medio y operaciones): 2018 +0.121 (42), 2019 -0.065 (158), 2020 +0.030 (176), 2021 -0.120 (172), 2022 +0.156 (183), 2023 -0.005 (173), 2024 -0.044 (169), 2025 +0.092 (159), 2026 +0.014 (120).

Sensibilidad (R neto medio y t): colchón 0 % +0.005 (t +0.20), colchón 50 % -0.010 (t -0.41), objetivo 1,5:1 +0.004 (t +0.13), objetivo 2:1 +0.031 (t +0.92).

### ORB 13:30–13:45

Rotura con cuerpo desde las 13:45 hasta las 19:45; a esa hora se cierra. ORB completos: 2026; con rotura: 2023.

**No pasa los criterios**. Coste medio 0.041 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 589, stop 528, por tiempo 200.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1317 | 51.6 % | +0.002 | +2.9 | 1.00 | -42.5 | +0.08 |
| Sin costes | 1317 | 51.8 % | +0.044 | +57.3 | 1.10 | -26.3 | +1.69 |
| Long | 731 | 53.2 % | +0.024 | +17.5 | 1.05 | -15.9 | +0.69 |
| Short | 586 | 49.5 % | -0.025 | -14.7 | 0.95 | -42.8 | -0.65 |
| 1.ª mitad | 659 | 52.7 % | +0.005 | +3.3 | 1.01 | -42.5 | +0.14 |
| 2.ª mitad | 658 | 50.5 % | -0.001 | -0.5 | 1.00 | -19.7 | -0.02 |

Por año (R neto medio y operaciones): 2018 +0.200 (47), 2019 +0.020 (178), 2020 -0.070 (157), 2021 -0.098 (159), 2022 +0.136 (168), 2023 +0.029 (165), 2024 -0.024 (169), 2025 -0.033 (166), 2026 -0.015 (108).

Sensibilidad (R neto medio y t): colchón 0 % -0.001 (t -0.03), colchón 50 % -0.020 (t -0.79), objetivo 1,5:1 -0.005 (t -0.17), objetivo 2:1 +0.006 (t +0.17).

### ORB 13:45–14:00

Rotura con cuerpo desde las 14:00 hasta las 20:00; a esa hora se cierra. ORB completos: 2025; con rotura: 2021.

**No pasa los criterios**. Coste medio 0.042 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 570, stop 561, por tiempo 179.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1310 | 50.1 % | -0.035 | -46.3 | 0.92 | -52.6 | -1.36 |
| Sin costes | 1310 | 50.4 % | +0.007 | +8.7 | 1.01 | -26.5 | +0.26 |
| Long | 705 | 53.0 % | +0.023 | +16.3 | 1.05 | -23.5 | +0.66 |
| Short | 605 | 46.6 % | -0.103 | -62.6 | 0.80 | -68.3 | -2.70 |
| 1.ª mitad | 655 | 50.8 % | -0.021 | -13.8 | 0.96 | -27.2 | -0.57 |
| 2.ª mitad | 655 | 49.3 % | -0.050 | -32.5 | 0.89 | -38.7 | -1.37 |

Por año (R neto medio y operaciones): 2018 +0.051 (51), 2019 -0.078 (160), 2020 +0.014 (165), 2021 -0.013 (148), 2022 -0.045 (167), 2023 -0.054 (169), 2024 +0.052 (169), 2025 -0.038 (165), 2026 -0.196 (116).

Sensibilidad (R neto medio y t): colchón 0 % -0.044 (t -1.66), colchón 50 % -0.033 (t -1.34), objetivo 1,5:1 -0.011 (t -0.37), objetivo 2:1 +0.006 (t +0.18).

