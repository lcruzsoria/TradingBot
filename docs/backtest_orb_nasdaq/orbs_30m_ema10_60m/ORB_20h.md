# ORB de 30 min de las 20:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 20:00–20:30 | 1375 | 51.1 | -0.008 | -0.36 | +0.042 | 0.050 | no |
| 20:15–20:45 | 1380 | 49.4 | -0.048 | -2.02 | +0.008 | 0.056 | no |
| 20:30–21:00 | 1365 | 50.1 | -0.022 | -0.90 | +0.039 | 0.060 | no |
| 20:45–21:15 | 1377 | 50.4 | -0.034 | -1.34 | +0.030 | 0.063 | no |

## Detalle

### ORB 20:00–20:30

Rotura con cuerpo desde las 20:30 hasta las 02:30 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2081.

**No pasa los criterios**. Coste medio 0.050 R; ancho medio del ORB 0.21 %; cómo terminan: objetivo 485, stop 412, por tiempo 478.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1375 | 51.1 % | -0.008 | -11.1 | 0.98 | -41.9 | -0.36 |
| Sin costes | 1375 | 51.9 % | +0.042 | +58.2 | 1.12 | -17.1 | +1.86 |
| Long | 781 | 52.5 % | -0.003 | -2.1 | 0.99 | -22.3 | -0.09 |
| Short | 594 | 49.2 % | -0.015 | -9.1 | 0.96 | -35.1 | -0.43 |
| 1.ª mitad | 688 | 49.3 % | -0.020 | -14.0 | 0.95 | -34.1 | -0.63 |
| 2.ª mitad | 687 | 52.8 % | +0.004 | +2.9 | 1.01 | -26.8 | +0.13 |

Por año (R neto medio y operaciones): 2018 +0.149 (38), 2019 -0.084 (172), 2020 -0.003 (167), 2021 -0.061 (169), 2022 +0.008 (164), 2023 -0.041 (168), 2024 -0.010 (177), 2025 +0.055 (163), 2026 +0.042 (157).

Sensibilidad (R neto medio y t): colchón 0 % -0.019 (t -0.78), colchón 50 % -0.021 (t -1.00), objetivo 1,5:1 -0.000 (t -0.00), objetivo 2:1 +0.013 (t +0.47).

### ORB 20:15–20:45

Rotura con cuerpo desde las 20:45 hasta las 02:45 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2084.

**No pasa los criterios**. Coste medio 0.056 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 513, stop 492, por tiempo 375.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1380 | 49.4 % | -0.048 | -66.0 | 0.89 | -93.8 | -2.02 |
| Sin costes | 1380 | 50.1 % | +0.008 | +11.0 | 1.02 | -45.5 | +0.34 |
| Long | 802 | 51.5 % | -0.023 | -18.6 | 0.94 | -38.9 | -0.75 |
| Short | 578 | 46.5 % | -0.082 | -47.4 | 0.82 | -65.1 | -2.23 |
| 1.ª mitad | 690 | 46.7 % | -0.099 | -68.5 | 0.78 | -71.7 | -2.98 |
| 2.ª mitad | 690 | 52.2 % | +0.004 | +2.5 | 1.01 | -26.7 | +0.11 |

Por año (R neto medio y operaciones): 2018 -0.025 (45), 2019 -0.182 (168), 2020 -0.059 (168), 2021 -0.093 (176), 2022 -0.108 (165), 2023 -0.068 (174), 2024 +0.010 (168), 2025 +0.007 (165), 2026 +0.126 (151).

Sensibilidad (R neto medio y t): colchón 0 % -0.062 (t -2.54), colchón 50 % -0.043 (t -1.97), objetivo 1,5:1 -0.045 (t -1.66), objetivo 2:1 -0.038 (t -1.30).

### ORB 20:30–21:00

Rotura con cuerpo desde las 21:00 hasta las 03:00 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2085.

**No pasa los criterios**. Coste medio 0.060 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 551, stop 486, por tiempo 328.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1365 | 50.1 % | -0.022 | -29.8 | 0.95 | -56.6 | -0.90 |
| Sin costes | 1365 | 51.1 % | +0.039 | +52.7 | 1.10 | -20.5 | +1.59 |
| Long | 797 | 49.4 % | -0.043 | -34.4 | 0.90 | -58.1 | -1.36 |
| Short | 568 | 51.1 % | +0.008 | +4.6 | 1.02 | -29.7 | +0.22 |
| 1.ª mitad | 683 | 48.6 % | -0.052 | -35.6 | 0.88 | -38.6 | -1.53 |
| 2.ª mitad | 682 | 51.6 % | +0.008 | +5.8 | 1.02 | -22.1 | +0.25 |

Por año (R neto medio y operaciones): 2018 -0.034 (55), 2019 -0.130 (162), 2020 +0.009 (174), 2021 -0.005 (169), 2022 -0.112 (155), 2023 -0.035 (167), 2024 -0.005 (165), 2025 +0.004 (166), 2026 +0.104 (152).

Sensibilidad (R neto medio y t): colchón 0 % -0.051 (t -2.03), colchón 50 % -0.013 (t -0.57), objetivo 1,5:1 -0.027 (t -0.97), objetivo 2:1 -0.018 (t -0.60).

### ORB 20:45–21:15

Rotura con cuerpo desde las 21:15 hasta las 03:15 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2085.

**No pasa los criterios**. Coste medio 0.063 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 591, stop 550, por tiempo 236.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1377 | 50.4 % | -0.034 | -46.2 | 0.93 | -65.0 | -1.34 |
| Sin costes | 1377 | 51.1 % | +0.030 | +40.7 | 1.07 | -19.4 | +1.18 |
| Long | 797 | 51.1 % | -0.034 | -26.8 | 0.93 | -50.4 | -1.02 |
| Short | 580 | 49.5 % | -0.033 | -19.4 | 0.93 | -25.1 | -0.86 |
| 1.ª mitad | 689 | 50.2 % | -0.037 | -25.2 | 0.92 | -31.6 | -1.05 |
| 2.ª mitad | 688 | 50.6 % | -0.030 | -20.9 | 0.94 | -39.4 | -0.84 |

Por año (R neto medio y operaciones): 2018 +0.023 (48), 2019 -0.083 (165), 2020 -0.027 (171), 2021 -0.004 (160), 2022 -0.049 (162), 2023 -0.092 (165), 2024 +0.007 (178), 2025 -0.090 (169), 2026 +0.056 (159).

Sensibilidad (R neto medio y t): colchón 0 % -0.044 (t -1.73), colchón 50 % -0.015 (t -0.63), objetivo 1,5:1 -0.017 (t -0.58), objetivo 2:1 -0.017 (t -0.52).

