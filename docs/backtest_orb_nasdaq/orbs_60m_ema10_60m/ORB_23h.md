# ORB de 60 min de las 23:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 23:00–00:00 | 1446 | 51.0 | -0.039 | -1.56 | +0.024 | 0.064 | no |
| 23:15–00:15 | 1478 | 50.1 | -0.061 | -2.43 | +0.005 | 0.066 | no |
| 23:30–00:30 | 1475 | 51.0 | -0.041 | -1.62 | +0.026 | 0.067 | no |
| 23:45–00:45 | 1494 | 50.2 | -0.052 | -2.09 | +0.014 | 0.066 | no |

## Detalle

### ORB 23:00–00:00

Rotura con cuerpo desde las 00:00 hasta las 06:00 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.064 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 657, stop 625, por tiempo 164.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1446 | 51.0 % | -0.039 | -56.7 | 0.92 | -81.5 | -1.56 |
| Sin costes | 1446 | 51.4 % | +0.024 | +35.3 | 1.05 | -33.4 | +0.98 |
| Long | 799 | 54.6 % | +0.014 | +11.0 | 1.03 | -21.5 | +0.41 |
| Short | 647 | 46.7 % | -0.105 | -67.7 | 0.80 | -80.1 | -2.78 |
| 1.ª mitad | 723 | 48.5 % | -0.090 | -65.0 | 0.82 | -69.1 | -2.56 |
| 2.ª mitad | 723 | 53.5 % | +0.011 | +8.3 | 1.02 | -27.2 | +0.32 |

Por año (R neto medio y operaciones): 2018 -0.121 (52), 2019 -0.074 (163), 2020 -0.045 (186), 2021 -0.052 (177), 2022 -0.190 (188), 2023 +0.026 (166), 2024 -0.004 (171), 2025 -0.025 (181), 2026 +0.098 (162).

Sensibilidad (R neto medio y t): colchón 0 % -0.052 (t -2.02), colchón 50 % -0.021 (t -0.85), objetivo 1,5:1 -0.024 (t -0.80), objetivo 2:1 -0.002 (t -0.05).

### ORB 23:15–00:15

Rotura con cuerpo desde las 00:15 hasta las 06:15 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.066 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 674, stop 670, por tiempo 134.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1478 | 50.1 % | -0.061 | -89.7 | 0.88 | -116.0 | -2.43 |
| Sin costes | 1478 | 50.2 % | +0.005 | +7.2 | 1.01 | -56.7 | +0.19 |
| Long | 826 | 53.1 % | -0.008 | -6.9 | 0.98 | -34.9 | -0.25 |
| Short | 652 | 46.2 % | -0.127 | -82.8 | 0.76 | -94.7 | -3.36 |
| 1.ª mitad | 739 | 47.5 % | -0.112 | -82.9 | 0.79 | -92.3 | -3.18 |
| 2.ª mitad | 739 | 52.6 % | -0.009 | -6.8 | 0.98 | -29.0 | -0.26 |

Por año (R neto medio y operaciones): 2018 +0.022 (50), 2019 -0.091 (166), 2020 -0.050 (184), 2021 -0.188 (191), 2022 -0.172 (189), 2023 -0.024 (175), 2024 -0.014 (175), 2025 -0.004 (192), 2026 +0.060 (156).

Sensibilidad (R neto medio y t): colchón 0 % -0.049 (t -1.94), colchón 50 % -0.038 (t -1.57), objetivo 1,5:1 -0.046 (t -1.56), objetivo 2:1 -0.039 (t -1.18).

### ORB 23:30–00:30

Rotura con cuerpo desde las 00:30 hasta las 06:30 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.067 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 695, stop 654, por tiempo 126.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1475 | 51.0 % | -0.041 | -60.1 | 0.92 | -85.4 | -1.62 |
| Sin costes | 1475 | 51.1 % | +0.026 | +38.2 | 1.06 | -29.1 | +1.03 |
| Long | 830 | 53.4 % | -0.005 | -4.3 | 0.99 | -27.8 | -0.15 |
| Short | 645 | 47.9 % | -0.087 | -55.8 | 0.83 | -64.7 | -2.27 |
| 1.ª mitad | 738 | 50.0 % | -0.062 | -45.7 | 0.88 | -68.2 | -1.74 |
| 2.ª mitad | 737 | 52.0 % | -0.020 | -14.4 | 0.96 | -28.2 | -0.55 |

Por año (R neto medio y operaciones): 2018 -0.007 (53), 2019 -0.128 (162), 2020 +0.046 (177), 2021 -0.142 (184), 2022 -0.062 (181), 2023 -0.096 (173), 2024 +0.016 (184), 2025 +0.001 (202), 2026 +0.022 (159).

Sensibilidad (R neto medio y t): colchón 0 % -0.040 (t -1.59), colchón 50 % -0.025 (t -1.04), objetivo 1,5:1 -0.030 (t -0.99), objetivo 2:1 -0.014 (t -0.42).

### ORB 23:45–00:45

Rotura con cuerpo desde las 00:45 hasta las 06:45 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.066 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 693, stop 671, por tiempo 130.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1494 | 50.2 % | -0.052 | -77.9 | 0.89 | -97.3 | -2.09 |
| Sin costes | 1494 | 50.4 % | +0.014 | +20.4 | 1.03 | -50.4 | +0.55 |
| Long | 848 | 52.7 % | -0.018 | -15.7 | 0.96 | -42.7 | -0.56 |
| Short | 646 | 46.9 % | -0.096 | -62.2 | 0.81 | -65.5 | -2.54 |
| 1.ª mitad | 747 | 46.5 % | -0.108 | -80.6 | 0.79 | -85.6 | -3.07 |
| 2.ª mitad | 747 | 53.9 % | +0.004 | +2.7 | 1.01 | -29.9 | +0.10 |

Por año (R neto medio y operaciones): 2018 -0.044 (55), 2019 -0.147 (181), 2020 +0.028 (183), 2021 -0.180 (181), 2022 -0.098 (180), 2023 -0.021 (175), 2024 -0.091 (187), 2025 +0.126 (189), 2026 -0.042 (163).

Sensibilidad (R neto medio y t): colchón 0 % -0.067 (t -2.63), colchón 50 % -0.039 (t -1.60), objetivo 1,5:1 -0.030 (t -1.00), objetivo 2:1 -0.016 (t -0.49).

