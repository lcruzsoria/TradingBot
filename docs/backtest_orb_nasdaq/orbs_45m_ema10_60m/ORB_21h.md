# ORB de 45 min de las 21:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 21:00–21:45 | 1439 | 52.3 | +0.013 | +0.56 | +0.063 | 0.050 | no |
| 21:15–22:00 | 1450 | 53.6 | +0.036 | +1.57 | +0.088 | 0.051 | no |
| 21:30–22:15 | 1464 | 51.0 | -0.023 | -0.98 | +0.030 | 0.053 | no |
| 21:45–22:30 | 1422 | 50.5 | -0.038 | -1.54 | +0.019 | 0.057 | no |

## Detalle

### ORB 21:00–21:45

Rotura con cuerpo desde las 21:45 hasta las 03:45 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2079.

**No pasa los criterios**. Coste medio 0.050 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 567, stop 469, por tiempo 403.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1439 | 52.3 % | +0.013 | +18.6 | 1.03 | -27.8 | +0.56 |
| Sin costes | 1439 | 53.1 % | +0.063 | +90.2 | 1.17 | -16.5 | +2.71 |
| Long | 834 | 53.4 % | +0.022 | +18.7 | 1.06 | -29.8 | +0.75 |
| Short | 605 | 50.9 % | -0.000 | -0.1 | 1.00 | -33.7 | -0.01 |
| 1.ª mitad | 720 | 53.2 % | +0.026 | +18.9 | 1.07 | -17.7 | +0.82 |
| 2.ª mitad | 719 | 51.5 % | -0.000 | -0.3 | 1.00 | -25.0 | -0.01 |

Por año (R neto medio y operaciones): 2018 +0.137 (61), 2019 -0.051 (180), 2020 +0.067 (187), 2021 +0.079 (174), 2022 -0.102 (162), 2023 +0.056 (178), 2024 -0.040 (172), 2025 -0.033 (173), 2026 +0.080 (152).

Sensibilidad (R neto medio y t): colchón 0 % -0.005 (t -0.21), colchón 50 % +0.014 (t +0.63), objetivo 1,5:1 +0.026 (t +0.98), objetivo 2:1 +0.035 (t +1.21).

### ORB 21:15–22:00

Rotura con cuerpo desde las 22:00 hasta las 04:00 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2080.

**No pasa los criterios**. Coste medio 0.051 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 599, stop 472, por tiempo 379.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1450 | 53.6 % | +0.036 | +52.8 | 1.09 | -27.4 | +1.57 |
| Sin costes | 1450 | 54.3 % | +0.088 | +127.2 | 1.24 | -19.7 | +3.79 |
| Long | 826 | 54.8 % | +0.044 | +36.3 | 1.12 | -19.5 | +1.45 |
| Short | 624 | 51.9 % | +0.026 | +16.5 | 1.06 | -35.3 | +0.74 |
| 1.ª mitad | 725 | 51.9 % | +0.010 | +7.0 | 1.02 | -27.4 | +0.30 |
| 2.ª mitad | 725 | 55.3 % | +0.063 | +45.8 | 1.16 | -15.7 | +1.87 |

Por año (R neto medio y operaciones): 2018 +0.090 (61), 2019 -0.012 (183), 2020 -0.031 (183), 2021 +0.069 (180), 2022 -0.041 (162), 2023 -0.004 (182), 2024 +0.022 (169), 2025 +0.108 (172), 2026 +0.175 (158).

Sensibilidad (R neto medio y t): colchón 0 % +0.027 (t +1.12), colchón 50 % +0.034 (t +1.56), objetivo 1,5:1 +0.027 (t +1.03), objetivo 2:1 +0.042 (t +1.45).

### ORB 21:30–22:15

Rotura con cuerpo desde las 22:15 hasta las 04:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2083.

**No pasa los criterios**. Coste medio 0.053 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 590, stop 540, por tiempo 334.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1464 | 51.0 % | -0.023 | -33.8 | 0.95 | -58.2 | -0.98 |
| Sin costes | 1464 | 51.3 % | +0.030 | +44.2 | 1.07 | -32.7 | +1.28 |
| Long | 838 | 54.1 % | +0.007 | +5.5 | 1.02 | -23.7 | +0.21 |
| Short | 626 | 46.8 % | -0.063 | -39.3 | 0.86 | -52.7 | -1.73 |
| 1.ª mitad | 732 | 49.9 % | -0.041 | -30.1 | 0.90 | -44.6 | -1.27 |
| 2.ª mitad | 732 | 52.0 % | -0.005 | -3.7 | 0.99 | -18.1 | -0.15 |

Por año (R neto medio y operaciones): 2018 +0.137 (60), 2019 -0.131 (187), 2020 -0.082 (178), 2021 +0.025 (187), 2022 -0.063 (164), 2023 -0.036 (181), 2024 -0.014 (177), 2025 +0.031 (170), 2026 +0.039 (160).

Sensibilidad (R neto medio y t): colchón 0 % -0.031 (t -1.27), colchón 50 % -0.011 (t -0.50), objetivo 1,5:1 -0.023 (t -0.84), objetivo 2:1 -0.004 (t -0.15).

### ORB 21:45–22:30

Rotura con cuerpo desde las 22:30 hasta las 04:30 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.057 R; ancho medio del ORB 0.21 %; cómo terminan: objetivo 597, stop 573, por tiempo 252.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1422 | 50.5 % | -0.038 | -53.9 | 0.92 | -73.6 | -1.54 |
| Sin costes | 1422 | 51.0 % | +0.019 | +27.4 | 1.04 | -30.8 | +0.78 |
| Long | 828 | 53.9 % | +0.014 | +11.3 | 1.03 | -21.7 | +0.43 |
| Short | 594 | 45.8 % | -0.110 | -65.2 | 0.78 | -77.0 | -2.89 |
| 1.ª mitad | 711 | 49.4 % | -0.050 | -35.7 | 0.89 | -51.5 | -1.48 |
| 2.ª mitad | 711 | 51.6 % | -0.026 | -18.2 | 0.95 | -30.9 | -0.72 |

Por año (R neto medio y operaciones): 2018 +0.092 (54), 2019 -0.102 (180), 2020 -0.099 (184), 2021 -0.020 (165), 2022 -0.058 (164), 2023 -0.038 (176), 2024 -0.054 (172), 2025 +0.035 (170), 2026 +0.004 (157).

Sensibilidad (R neto medio y t): colchón 0 % -0.056 (t -2.23), colchón 50 % -0.030 (t -1.31), objetivo 1,5:1 -0.028 (t -0.97), objetivo 2:1 -0.023 (t -0.75).

