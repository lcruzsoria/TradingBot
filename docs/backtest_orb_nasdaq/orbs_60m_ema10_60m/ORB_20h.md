# ORB de 60 min de las 20:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 20:00–21:00 | 1525 | 48.7 | -0.009 | -0.47 | +0.031 | 0.040 | no |
| 20:15–21:15 | 1507 | 48.8 | -0.014 | -0.67 | +0.030 | 0.044 | no |
| 20:30–21:30 | 1492 | 50.2 | -0.003 | -0.14 | +0.041 | 0.044 | no |
| 20:45–21:45 | 1494 | 51.5 | +0.006 | +0.27 | +0.050 | 0.044 | no |

## Detalle

### ORB 20:00–21:00

Rotura con cuerpo desde las 21:00 hasta las 03:00 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2034.

**No pasa los criterios**. Coste medio 0.040 R; ancho medio del ORB 0.28 %; cómo terminan: objetivo 392, stop 330, por tiempo 803.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1525 | 48.7 % | -0.009 | -13.8 | 0.97 | -47.8 | -0.47 |
| Sin costes | 1525 | 50.6 % | +0.031 | +46.8 | 1.10 | -22.0 | +1.61 |
| Long | 874 | 49.5 % | -0.008 | -7.1 | 0.98 | -28.9 | -0.32 |
| Short | 651 | 47.6 % | -0.010 | -6.6 | 0.97 | -34.2 | -0.35 |
| 1.ª mitad | 763 | 48.0 % | -0.035 | -26.9 | 0.89 | -35.3 | -1.32 |
| 2.ª mitad | 762 | 49.5 % | +0.017 | +13.1 | 1.05 | -19.2 | +0.63 |

Por año (R neto medio y operaciones): 2018 +0.024 (56), 2019 -0.062 (183), 2020 -0.002 (192), 2021 -0.039 (192), 2022 -0.074 (170), 2023 -0.033 (190), 2024 -0.021 (192), 2025 +0.044 (182), 2026 +0.114 (168).

Sensibilidad (R neto medio y t): colchón 0 % -0.024 (t -1.17), colchón 50 % -0.019 (t -1.12), objetivo 1,5:1 +0.004 (t +0.20), objetivo 2:1 +0.010 (t +0.44).

### ORB 20:15–21:15

Rotura con cuerpo desde las 21:15 hasta las 03:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2046.

**No pasa los criterios**. Coste medio 0.044 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 462, stop 408, por tiempo 637.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1507 | 48.8 % | -0.014 | -20.9 | 0.96 | -49.3 | -0.67 |
| Sin costes | 1507 | 50.4 % | +0.030 | +44.7 | 1.09 | -16.8 | +1.43 |
| Long | 878 | 49.4 % | -0.017 | -14.6 | 0.95 | -36.0 | -0.61 |
| Short | 629 | 48.0 % | -0.010 | -6.4 | 0.97 | -26.7 | -0.31 |
| 1.ª mitad | 754 | 47.3 % | -0.026 | -19.3 | 0.93 | -29.0 | -0.89 |
| 2.ª mitad | 753 | 50.3 % | -0.002 | -1.7 | 0.99 | -27.0 | -0.07 |

Por año (R neto medio y operaciones): 2018 +0.103 (54), 2019 -0.075 (175), 2020 +0.004 (185), 2021 -0.010 (188), 2022 -0.041 (170), 2023 -0.074 (189), 2024 -0.040 (193), 2025 +0.000 (187), 2026 +0.099 (166).

Sensibilidad (R neto medio y t): colchón 0 % -0.027 (t -1.24), colchón 50 % -0.015 (t -0.79), objetivo 1,5:1 -0.017 (t -0.71), objetivo 2:1 -0.011 (t -0.46).

### ORB 20:30–21:30

Rotura con cuerpo desde las 21:30 hasta las 03:30 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2059.

**No pasa los criterios**. Coste medio 0.044 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 505, stop 437, por tiempo 550.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1492 | 50.2 % | -0.003 | -4.5 | 0.99 | -35.9 | -0.14 |
| Sin costes | 1492 | 51.5 % | +0.041 | +61.3 | 1.12 | -13.1 | +1.91 |
| Long | 852 | 52.5 % | +0.015 | +12.8 | 1.04 | -24.8 | +0.53 |
| Short | 640 | 47.2 % | -0.027 | -17.3 | 0.93 | -33.0 | -0.83 |
| 1.ª mitad | 746 | 49.2 % | -0.030 | -22.6 | 0.92 | -27.4 | -1.01 |
| 2.ª mitad | 746 | 51.2 % | +0.024 | +18.0 | 1.06 | -21.0 | +0.78 |

Por año (R neto medio y operaciones): 2018 -0.047 (57), 2019 -0.076 (182), 2020 +0.030 (185), 2021 -0.029 (181), 2022 -0.000 (172), 2023 -0.006 (184), 2024 -0.057 (187), 2025 +0.017 (182), 2026 +0.127 (162).

Sensibilidad (R neto medio y t): colchón 0 % -0.009 (t -0.40), colchón 50 % -0.007 (t -0.37), objetivo 1,5:1 -0.010 (t -0.41), objetivo 2:1 -0.003 (t -0.10).

### ORB 20:45–21:45

Rotura con cuerpo desde las 21:45 hasta las 03:45 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2065.

**No pasa los criterios**. Coste medio 0.044 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 525, stop 445, por tiempo 524.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1494 | 51.5 % | +0.006 | +8.9 | 1.02 | -25.7 | +0.27 |
| Sin costes | 1494 | 52.3 % | +0.050 | +75.2 | 1.14 | -14.5 | +2.31 |
| Long | 860 | 53.5 % | +0.030 | +25.6 | 1.08 | -27.6 | +1.05 |
| Short | 634 | 48.7 % | -0.026 | -16.7 | 0.93 | -36.7 | -0.78 |
| 1.ª mitad | 747 | 51.3 % | +0.003 | +2.1 | 1.01 | -18.1 | +0.09 |
| 2.ª mitad | 747 | 51.7 % | +0.009 | +6.8 | 1.02 | -23.8 | +0.29 |

Por año (R neto medio y operaciones): 2018 +0.055 (62), 2019 -0.043 (184), 2020 +0.049 (188), 2021 +0.053 (179), 2022 -0.083 (173), 2023 +0.057 (184), 2024 -0.074 (181), 2025 +0.008 (178), 2026 +0.066 (165).

Sensibilidad (R neto medio y t): colchón 0 % -0.003 (t -0.11), colchón 50 % +0.006 (t +0.29), objetivo 1,5:1 +0.016 (t +0.66), objetivo 2:1 +0.024 (t +0.93).

