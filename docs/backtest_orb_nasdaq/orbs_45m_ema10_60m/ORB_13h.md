# ORB de 45 min de las 13:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 13:00–13:45 | 1480 | 50.1 | -0.007 | -0.34 | +0.017 | 0.024 | no |
| 13:15–14:00 | 1469 | 50.1 | -0.003 | -0.15 | +0.022 | 0.025 | no |
| 13:30–14:15 | 1496 | 49.9 | -0.011 | -0.55 | +0.013 | 0.024 | no |
| 13:45–14:30 | 1476 | 50.8 | -0.006 | -0.29 | +0.019 | 0.024 | no |

## Detalle

### ORB 13:00–13:45

Rotura con cuerpo desde las 13:45 hasta las 19:45; a esa hora se cierra. ORB completos: 2025; con rotura: 1975.

**No pasa los criterios**. Coste medio 0.024 R; ancho medio del ORB 0.43 %; cómo terminan: objetivo 415, stop 387, por tiempo 678.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1480 | 50.1 % | -0.007 | -10.2 | 0.98 | -40.6 | -0.34 |
| Sin costes | 1480 | 50.7 % | +0.017 | +25.7 | 1.05 | -28.5 | +0.84 |
| Long | 842 | 51.9 % | +0.008 | +6.8 | 1.02 | -28.8 | +0.29 |
| Short | 638 | 47.6 % | -0.027 | -17.0 | 0.93 | -29.2 | -0.85 |
| 1.ª mitad | 740 | 51.2 % | +0.016 | +11.9 | 1.05 | -19.6 | +0.54 |
| 2.ª mitad | 740 | 48.9 % | -0.030 | -22.2 | 0.92 | -40.6 | -1.05 |

Por año (R neto medio y operaciones): 2018 +0.088 (52), 2019 -0.064 (185), 2020 +0.042 (190), 2021 +0.020 (177), 2022 +0.091 (196), 2023 -0.042 (185), 2024 -0.035 (187), 2025 -0.082 (175), 2026 -0.025 (133).

Sensibilidad (R neto medio y t): colchón 0 % -0.010 (t -0.47), colchón 50 % +0.006 (t +0.30), objetivo 1,5:1 -0.002 (t -0.07), objetivo 2:1 +0.002 (t +0.08).

### ORB 13:15–14:00

Rotura con cuerpo desde las 14:00 hasta las 20:00; a esa hora se cierra. ORB completos: 2025; con rotura: 1969.

**No pasa los criterios**. Coste medio 0.025 R; ancho medio del ORB 0.41 %; cómo terminan: objetivo 435, stop 394, por tiempo 640.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1469 | 50.1 % | -0.003 | -4.5 | 0.99 | -30.0 | -0.15 |
| Sin costes | 1469 | 50.7 % | +0.022 | +32.0 | 1.06 | -24.6 | +1.04 |
| Long | 823 | 52.5 % | +0.033 | +27.6 | 1.10 | -14.2 | +1.20 |
| Short | 646 | 47.1 % | -0.050 | -32.1 | 0.87 | -38.0 | -1.58 |
| 1.ª mitad | 735 | 50.6 % | -0.003 | -2.2 | 0.99 | -30.0 | -0.10 |
| 2.ª mitad | 734 | 49.6 % | -0.003 | -2.3 | 0.99 | -19.9 | -0.11 |

Por año (R neto medio y operaciones): 2018 +0.089 (58), 2019 -0.121 (185), 2020 +0.036 (188), 2021 +0.039 (176), 2022 +0.019 (198), 2023 -0.030 (176), 2024 +0.064 (183), 2025 -0.030 (175), 2026 -0.045 (130).

Sensibilidad (R neto medio y t): colchón 0 % -0.005 (t -0.24), colchón 50 % -0.001 (t -0.04), objetivo 1,5:1 +0.003 (t +0.15), objetivo 2:1 +0.019 (t +0.75).

### ORB 13:30–14:15

Rotura con cuerpo desde las 14:15 hasta las 20:15; a esa hora se cierra. ORB completos: 2025; con rotura: 1964.

**No pasa los criterios**. Coste medio 0.024 R; ancho medio del ORB 0.44 %; cómo terminan: objetivo 384, stop 364, por tiempo 748.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1496 | 49.9 % | -0.011 | -16.3 | 0.97 | -29.9 | -0.55 |
| Sin costes | 1496 | 50.5 % | +0.013 | +19.6 | 1.04 | -17.3 | +0.66 |
| Long | 843 | 52.7 % | +0.015 | +12.9 | 1.05 | -20.9 | +0.59 |
| Short | 653 | 46.2 % | -0.045 | -29.2 | 0.88 | -38.4 | -1.48 |
| 1.ª mitad | 748 | 51.1 % | -0.006 | -4.6 | 0.98 | -22.2 | -0.21 |
| 2.ª mitad | 748 | 48.7 % | -0.016 | -11.7 | 0.95 | -27.4 | -0.58 |

Por año (R neto medio y operaciones): 2018 -0.021 (55), 2019 -0.083 (184), 2020 +0.051 (205), 2021 +0.009 (169), 2022 -0.008 (199), 2023 -0.032 (186), 2024 -0.022 (183), 2025 +0.004 (183), 2026 -0.010 (132).

Sensibilidad (R neto medio y t): colchón 0 % -0.010 (t -0.49), colchón 50 % +0.001 (t +0.07), objetivo 1,5:1 -0.004 (t -0.18), objetivo 2:1 +0.015 (t +0.66).

### ORB 13:45–14:30

Rotura con cuerpo desde las 14:30 hasta las 20:30; a esa hora se cierra. ORB completos: 2025; con rotura: 1957.

**No pasa los criterios**. Coste medio 0.024 R; ancho medio del ORB 0.43 %; cómo terminan: objetivo 366, stop 354, por tiempo 756.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1476 | 50.8 % | -0.006 | -8.4 | 0.98 | -23.1 | -0.29 |
| Sin costes | 1476 | 51.8 % | +0.019 | +27.4 | 1.06 | -17.4 | +0.94 |
| Long | 847 | 53.2 % | +0.021 | +17.4 | 1.06 | -14.0 | +0.79 |
| Short | 629 | 47.5 % | -0.041 | -25.9 | 0.88 | -35.2 | -1.36 |
| 1.ª mitad | 738 | 52.4 % | +0.002 | +1.7 | 1.01 | -23.1 | +0.08 |
| 2.ª mitad | 738 | 49.2 % | -0.014 | -10.1 | 0.96 | -19.3 | -0.51 |

Por año (R neto medio y operaciones): 2018 +0.204 (53), 2019 -0.095 (176), 2020 +0.016 (196), 2021 -0.014 (173), 2022 +0.041 (198), 2023 +0.008 (185), 2024 -0.038 (180), 2025 +0.020 (175), 2026 -0.068 (140).

Sensibilidad (R neto medio y t): colchón 0 % -0.004 (t -0.19), colchón 50 % -0.004 (t -0.25), objetivo 1,5:1 +0.003 (t +0.12), objetivo 2:1 +0.012 (t +0.51).

