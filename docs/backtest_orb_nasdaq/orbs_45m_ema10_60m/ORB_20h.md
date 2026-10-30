# ORB de 45 min de las 20:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 20:00–20:45 | 1473 | 48.5 | -0.029 | -1.40 | +0.015 | 0.044 | no |
| 20:15–21:00 | 1445 | 49.3 | -0.022 | -1.00 | +0.027 | 0.049 | no |
| 20:30–21:15 | 1439 | 49.5 | -0.010 | -0.43 | +0.041 | 0.051 | no |
| 20:45–21:30 | 1442 | 50.8 | -0.015 | -0.66 | +0.036 | 0.052 | no |

## Detalle

### ORB 20:00–20:45

Rotura con cuerpo desde las 20:45 hasta las 02:45 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2061.

**No pasa los criterios**. Coste medio 0.044 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 415, stop 375, por tiempo 683.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1473 | 48.5 % | -0.029 | -42.1 | 0.92 | -79.1 | -1.40 |
| Sin costes | 1473 | 50.2 % | +0.015 | +22.0 | 1.04 | -36.6 | +0.73 |
| Long | 851 | 50.6 % | -0.017 | -14.7 | 0.95 | -35.6 | -0.64 |
| Short | 622 | 45.5 % | -0.044 | -27.4 | 0.88 | -52.7 | -1.40 |
| 1.ª mitad | 737 | 46.8 % | -0.064 | -47.2 | 0.83 | -59.7 | -2.24 |
| 2.ª mitad | 736 | 50.1 % | +0.007 | +5.1 | 1.02 | -29.7 | +0.24 |

Por año (R neto medio y operaciones): 2018 -0.012 (47), 2019 -0.102 (185), 2020 -0.021 (180), 2021 -0.100 (186), 2022 -0.084 (170), 2023 -0.071 (188), 2024 -0.011 (181), 2025 +0.054 (174), 2026 +0.122 (162).

Sensibilidad (R neto medio y t): colchón 0 % -0.043 (t -1.98), colchón 50 % -0.031 (t -1.70), objetivo 1,5:1 -0.002 (t -0.11), objetivo 2:1 -0.002 (t -0.09).

### ORB 20:15–21:00

Rotura con cuerpo desde las 21:00 hasta las 03:00 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2068.

**No pasa los criterios**. Coste medio 0.049 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 476, stop 426, por tiempo 543.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1445 | 49.3 % | -0.022 | -31.5 | 0.94 | -57.4 | -1.00 |
| Sin costes | 1445 | 50.7 % | +0.027 | +39.0 | 1.07 | -19.9 | +1.24 |
| Long | 840 | 49.5 % | -0.021 | -17.8 | 0.95 | -36.9 | -0.74 |
| Short | 605 | 49.1 % | -0.023 | -13.7 | 0.94 | -35.3 | -0.67 |
| 1.ª mitad | 723 | 48.0 % | -0.048 | -34.7 | 0.88 | -46.2 | -1.56 |
| 2.ª mitad | 722 | 50.7 % | +0.004 | +3.2 | 1.01 | -16.8 | +0.14 |

Por año (R neto medio y operaciones): 2018 +0.066 (54), 2019 -0.135 (170), 2020 +0.004 (181), 2021 -0.035 (183), 2022 -0.097 (164), 2023 -0.046 (179), 2024 +0.007 (179), 2025 +0.003 (176), 2026 +0.100 (159).

Sensibilidad (R neto medio y t): colchón 0 % -0.046 (t -1.98), colchón 50 % -0.030 (t -1.52), objetivo 1,5:1 -0.024 (t -0.97), objetivo 2:1 -0.015 (t -0.56).

### ORB 20:30–21:15

Rotura con cuerpo desde las 21:15 hasta las 03:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2066.

**No pasa los criterios**. Coste medio 0.051 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 529, stop 457, por tiempo 453.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1439 | 49.5 % | -0.010 | -14.0 | 0.98 | -42.2 | -0.43 |
| Sin costes | 1439 | 50.8 % | +0.041 | +59.1 | 1.11 | -14.1 | +1.82 |
| Long | 824 | 50.5 % | -0.016 | -13.3 | 0.96 | -42.5 | -0.54 |
| Short | 615 | 48.3 % | -0.001 | -0.7 | 1.00 | -23.2 | -0.03 |
| 1.ª mitad | 720 | 48.3 % | -0.026 | -19.0 | 0.93 | -27.6 | -0.83 |
| 2.ª mitad | 719 | 50.8 % | +0.007 | +5.0 | 1.02 | -25.3 | +0.21 |

Por año (R neto medio y operaciones): 2018 +0.035 (54), 2019 -0.088 (171), 2020 +0.042 (171), 2021 -0.018 (177), 2022 -0.038 (164), 2023 -0.055 (177), 2024 -0.011 (184), 2025 -0.023 (180), 2026 +0.108 (161).

Sensibilidad (R neto medio y t): colchón 0 % -0.021 (t -0.89), colchón 50 % -0.005 (t -0.26), objetivo 1,5:1 -0.010 (t -0.40), objetivo 2:1 -0.001 (t -0.02).

### ORB 20:45–21:30

Rotura con cuerpo desde las 21:30 hasta las 03:30 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2081.

**No pasa los criterios**. Coste medio 0.052 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 561, stop 510, por tiempo 371.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1442 | 50.8 % | -0.015 | -22.3 | 0.96 | -40.9 | -0.66 |
| Sin costes | 1442 | 51.9 % | +0.036 | +52.4 | 1.09 | -12.5 | +1.55 |
| Long | 835 | 52.8 % | +0.001 | +1.1 | 1.00 | -28.1 | +0.04 |
| Short | 607 | 48.1 % | -0.038 | -23.4 | 0.91 | -34.2 | -1.06 |
| 1.ª mitad | 721 | 50.3 % | -0.036 | -25.6 | 0.92 | -27.3 | -1.09 |
| 2.ª mitad | 721 | 51.3 % | +0.005 | +3.3 | 1.01 | -26.5 | +0.14 |

Por año (R neto medio y operaciones): 2018 -0.113 (53), 2019 -0.062 (177), 2020 +0.014 (187), 2021 -0.018 (170), 2022 -0.040 (169), 2023 +0.028 (170), 2024 -0.084 (178), 2025 -0.007 (177), 2026 +0.082 (161).

Sensibilidad (R neto medio y t): colchón 0 % -0.026 (t -1.08), colchón 50 % -0.008 (t -0.39), objetivo 1,5:1 -0.007 (t -0.25), objetivo 2:1 +0.000 (t +0.01).

