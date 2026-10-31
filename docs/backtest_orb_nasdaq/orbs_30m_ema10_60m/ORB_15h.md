# ORB de 30 min de las 15:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 15:00–15:30 | 1335 | 49.5 | -0.010 | -0.53 | +0.017 | 0.027 | no |
| 15:15–15:45 | 1330 | 50.9 | +0.013 | +0.71 | +0.041 | 0.028 | no |
| 15:30–16:00 | 1255 | 49.0 | -0.005 | -0.31 | +0.019 | 0.024 | no |
| 15:45–16:15 | 1189 | 47.9 | -0.005 | -0.29 | +0.020 | 0.025 | no |

## Detalle

### ORB 15:00–15:30

Rotura con cuerpo desde las 15:30 hasta las 21:30; a esa hora se cierra. ORB completos: 2026; con rotura: 1940.

**No pasa los criterios**. Coste medio 0.027 R; ancho medio del ORB 0.38 %; cómo terminan: objetivo 313, stop 266, por tiempo 756.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1335 | 49.5 % | -0.010 | -13.9 | 0.97 | -29.8 | -0.53 |
| Sin costes | 1335 | 51.1 % | +0.017 | +22.6 | 1.06 | -18.3 | +0.85 |
| Long | 729 | 52.9 % | +0.016 | +12.0 | 1.05 | -19.6 | +0.61 |
| Short | 606 | 45.4 % | -0.043 | -25.8 | 0.87 | -30.8 | -1.45 |
| 1.ª mitad | 668 | 51.5 % | +0.020 | +13.7 | 1.07 | -11.2 | +0.74 |
| 2.ª mitad | 667 | 47.5 % | -0.041 | -27.6 | 0.87 | -29.0 | -1.47 |

Por año (R neto medio y operaciones): 2018 -0.060 (55), 2019 +0.030 (167), 2020 +0.062 (180), 2021 -0.019 (169), 2022 +0.007 (175), 2023 -0.107 (165), 2024 -0.001 (162), 2025 +0.051 (129), 2026 -0.102 (133).

Sensibilidad (R neto medio y t): colchón 0 % -0.012 (t -0.58), colchón 50 % -0.017 (t -0.96), objetivo 1,5:1 -0.019 (t -0.91), objetivo 2:1 -0.011 (t -0.50).

### ORB 15:15–15:45

Rotura con cuerpo desde las 15:45 hasta las 21:45; a esa hora se cierra. ORB completos: 2025; con rotura: 1890.

**No pasa los criterios**. Coste medio 0.028 R; ancho medio del ORB 0.37 %; cómo terminan: objetivo 297, stop 233, por tiempo 800.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1330 | 50.9 % | +0.013 | +17.9 | 1.05 | -23.0 | +0.71 |
| Sin costes | 1330 | 52.3 % | +0.041 | +54.8 | 1.15 | -13.7 | +2.16 |
| Long | 747 | 53.9 % | +0.052 | +38.5 | 1.19 | -12.4 | +2.02 |
| Short | 583 | 47.0 % | -0.035 | -20.6 | 0.88 | -28.5 | -1.24 |
| 1.ª mitad | 665 | 51.3 % | +0.023 | +15.6 | 1.08 | -14.8 | +0.87 |
| 2.ª mitad | 665 | 50.5 % | +0.004 | +2.3 | 1.01 | -18.8 | +0.13 |

Por año (R neto medio y operaciones): 2018 -0.010 (48), 2019 +0.043 (177), 2020 +0.078 (180), 2021 -0.015 (178), 2022 +0.002 (164), 2023 -0.097 (149), 2024 +0.011 (162), 2025 +0.134 (140), 2026 -0.052 (132).

Sensibilidad (R neto medio y t): colchón 0 % +0.003 (t +0.13), colchón 50 % +0.017 (t +1.01), objetivo 1,5:1 +0.018 (t +0.85), objetivo 2:1 +0.006 (t +0.25).

### ORB 15:30–16:00

Rotura con cuerpo desde las 16:00 hasta las 22:00; a esa hora se cierra. ORB completos: 2024; con rotura: 1674.

**No pasa los criterios**. Coste medio 0.024 R; ancho medio del ORB 0.43 %; cómo terminan: objetivo 168, stop 146, por tiempo 941.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1255 | 49.0 % | -0.005 | -6.5 | 0.98 | -24.7 | -0.31 |
| Sin costes | 1255 | 51.6 % | +0.019 | +24.0 | 1.09 | -16.1 | +1.15 |
| Long | 731 | 51.8 % | +0.010 | +7.4 | 1.05 | -15.7 | +0.47 |
| Short | 524 | 45.0 % | -0.027 | -13.9 | 0.89 | -22.0 | -1.04 |
| 1.ª mitad | 628 | 53.3 % | +0.021 | +13.0 | 1.09 | -9.0 | +0.88 |
| 2.ª mitad | 627 | 44.7 % | -0.031 | -19.5 | 0.87 | -24.7 | -1.34 |

Por año (R neto medio y operaciones): 2018 -0.051 (47), 2019 +0.020 (184), 2020 +0.061 (164), 2021 -0.012 (153), 2022 +0.005 (144), 2023 -0.043 (122), 2024 +0.011 (150), 2025 +0.002 (152), 2026 -0.098 (139).

Sensibilidad (R neto medio y t): colchón 0 % -0.011 (t -0.62), colchón 50 % -0.004 (t -0.25), objetivo 1,5:1 -0.001 (t -0.07), objetivo 2:1 -0.002 (t -0.11).

### ORB 15:45–16:15

Rotura con cuerpo desde las 16:15 hasta las 22:15; a esa hora se cierra. ORB completos: 2023; con rotura: 1572.

**No pasa los criterios**. Coste medio 0.025 R; ancho medio del ORB 0.44 %; cómo terminan: objetivo 152, stop 132, por tiempo 905.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1189 | 47.9 % | -0.005 | -5.8 | 0.98 | -27.0 | -0.29 |
| Sin costes | 1189 | 49.3 % | +0.020 | +24.2 | 1.10 | -19.6 | +1.22 |
| Long | 693 | 49.9 % | -0.003 | -1.8 | 0.99 | -11.5 | -0.12 |
| Short | 496 | 45.2 % | -0.008 | -4.0 | 0.97 | -22.1 | -0.31 |
| 1.ª mitad | 595 | 49.6 % | +0.019 | +11.4 | 1.09 | -9.1 | +0.82 |
| 2.ª mitad | 594 | 46.3 % | -0.029 | -17.3 | 0.88 | -27.0 | -1.24 |

Por año (R neto medio y operaciones): 2018 -0.069 (37), 2019 +0.018 (172), 2020 +0.037 (168), 2021 +0.004 (143), 2022 +0.034 (128), 2023 -0.048 (126), 2024 +0.003 (135), 2025 -0.013 (157), 2026 -0.081 (123).

Sensibilidad (R neto medio y t): colchón 0 % -0.015 (t -0.83), colchón 50 % -0.010 (t -0.71), objetivo 1,5:1 -0.008 (t -0.44), objetivo 2:1 -0.011 (t -0.64).

