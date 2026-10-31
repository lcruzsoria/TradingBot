# ORB de 15 min de las 12:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 12:00–12:15 | 1328 | 50.3 | -0.034 | -1.32 | +0.002 | 0.037 | no |
| 12:15–12:30 | 1370 | 51.3 | -0.012 | -0.46 | +0.028 | 0.040 | no |
| 12:30–12:45 | 1379 | 50.5 | -0.027 | -1.04 | +0.014 | 0.041 | no |
| 12:45–13:00 | 1363 | 49.4 | -0.038 | -1.47 | +0.004 | 0.041 | no |

## Detalle

### ORB 12:00–12:15

Rotura con cuerpo desde las 12:15 hasta las 18:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.037 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 584, stop 587, por tiempo 157.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1328 | 50.3 % | -0.034 | -45.8 | 0.93 | -54.9 | -1.32 |
| Sin costes | 1328 | 50.4 % | +0.002 | +3.0 | 1.00 | -28.3 | +0.09 |
| Long | 747 | 51.8 % | -0.014 | -10.7 | 0.97 | -26.3 | -0.41 |
| Short | 581 | 48.4 % | -0.060 | -35.0 | 0.88 | -53.6 | -1.53 |
| 1.ª mitad | 664 | 51.1 % | -0.024 | -15.7 | 0.95 | -26.9 | -0.64 |
| 2.ª mitad | 664 | 49.5 % | -0.045 | -30.1 | 0.91 | -37.1 | -1.23 |

Por año (R neto medio y operaciones): 2018 +0.043 (51), 2019 -0.110 (152), 2020 +0.042 (176), 2021 +0.006 (144), 2022 -0.079 (158), 2023 -0.035 (163), 2024 -0.026 (186), 2025 -0.073 (166), 2026 -0.033 (132).

Sensibilidad (R neto medio y t): colchón 0 % -0.045 (t -1.67), colchón 50 % -0.025 (t -1.01), objetivo 1,5:1 -0.023 (t -0.75), objetivo 2:1 -0.011 (t -0.32).

### ORB 12:15–12:30

Rotura con cuerpo desde las 12:30 hasta las 18:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.040 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 623, stop 588, por tiempo 159.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1370 | 51.3 % | -0.012 | -16.1 | 0.97 | -29.7 | -0.46 |
| Sin costes | 1370 | 51.8 % | +0.028 | +38.5 | 1.06 | -17.6 | +1.09 |
| Long | 776 | 53.7 % | +0.025 | +19.6 | 1.06 | -23.1 | +0.74 |
| Short | 594 | 48.1 % | -0.060 | -35.8 | 0.88 | -41.7 | -1.55 |
| 1.ª mitad | 685 | 51.7 % | -0.016 | -11.0 | 0.97 | -29.7 | -0.44 |
| 2.ª mitad | 685 | 50.9 % | -0.007 | -5.1 | 0.98 | -23.1 | -0.21 |

Por año (R neto medio y operaciones): 2018 +0.009 (54), 2019 -0.084 (167), 2020 -0.017 (178), 2021 -0.002 (160), 2022 +0.046 (169), 2023 +0.035 (165), 2024 -0.040 (170), 2025 +0.014 (166), 2026 -0.058 (141).

Sensibilidad (R neto medio y t): colchón 0 % -0.013 (t -0.49), colchón 50 % -0.002 (t -0.06), objetivo 1,5:1 +0.013 (t +0.43), objetivo 2:1 +0.027 (t +0.81).

### ORB 12:30–12:45

Rotura con cuerpo desde las 12:45 hasta las 18:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2089.

**No pasa los criterios**. Coste medio 0.041 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 623, stop 597, por tiempo 159.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1379 | 50.5 % | -0.027 | -37.0 | 0.94 | -49.8 | -1.04 |
| Sin costes | 1379 | 50.8 % | +0.014 | +19.2 | 1.03 | -24.5 | +0.54 |
| Long | 778 | 52.4 % | -0.005 | -3.6 | 0.99 | -28.7 | -0.14 |
| Short | 601 | 48.1 % | -0.055 | -33.3 | 0.89 | -46.4 | -1.42 |
| 1.ª mitad | 690 | 50.0 % | -0.039 | -26.8 | 0.92 | -44.7 | -1.06 |
| 2.ª mitad | 689 | 51.1 % | -0.015 | -10.2 | 0.97 | -29.6 | -0.41 |

Por año (R neto medio y operaciones): 2018 -0.006 (57), 2019 -0.174 (168), 2020 +0.048 (170), 2021 -0.088 (163), 2022 +0.071 (159), 2023 +0.006 (170), 2024 -0.012 (173), 2025 -0.044 (175), 2026 -0.026 (144).

Sensibilidad (R neto medio y t): colchón 0 % -0.045 (t -1.73), colchón 50 % -0.014 (t -0.56), objetivo 1,5:1 -0.020 (t -0.67), objetivo 2:1 +0.015 (t +0.45).

### ORB 12:45–13:00

Rotura con cuerpo desde las 13:00 hasta las 19:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2082.

**No pasa los criterios**. Coste medio 0.041 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 606, stop 601, por tiempo 156.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1363 | 49.4 % | -0.038 | -51.6 | 0.92 | -53.2 | -1.47 |
| Sin costes | 1363 | 49.7 % | +0.004 | +4.9 | 1.01 | -25.9 | +0.14 |
| Long | 758 | 51.6 % | -0.016 | -11.8 | 0.97 | -28.5 | -0.45 |
| Short | 605 | 46.8 % | -0.066 | -39.9 | 0.87 | -43.5 | -1.71 |
| 1.ª mitad | 682 | 51.2 % | -0.029 | -19.8 | 0.94 | -48.9 | -0.79 |
| 2.ª mitad | 681 | 47.7 % | -0.047 | -31.8 | 0.90 | -44.0 | -1.30 |

Por año (R neto medio y operaciones): 2018 -0.256 (48), 2019 -0.082 (165), 2020 -0.028 (173), 2021 -0.078 (159), 2022 +0.162 (166), 2023 +0.027 (164), 2024 -0.092 (175), 2025 -0.044 (165), 2026 -0.112 (148).

Sensibilidad (R neto medio y t): colchón 0 % -0.043 (t -1.65), colchón 50 % -0.009 (t -0.37), objetivo 1,5:1 -0.018 (t -0.61), objetivo 2:1 -0.010 (t -0.31).

