# ORB de 15 min de las 06:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 06:00–06:15 | 1362 | 49.2 | -0.091 | -3.35 | -0.018 | 0.073 | no |
| 06:15–06:30 | 1341 | 47.2 | -0.134 | -4.92 | -0.056 | 0.078 | no |
| 06:30–06:45 | 1301 | 51.4 | -0.048 | -1.74 | +0.026 | 0.074 | no |
| 06:45–07:00 | 1352 | 52.3 | -0.026 | -0.97 | +0.046 | 0.072 | no |

## Detalle

### ORB 06:00–06:15

Rotura con cuerpo desde las 06:15 hasta las 12:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.073 R; ancho medio del ORB 0.14 %; cómo terminan: objetivo 666, stop 690, por tiempo 6.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1362 | 49.2 % | -0.091 | -123.5 | 0.83 | -137.4 | -3.35 |
| Sin costes | 1362 | 49.2 % | -0.018 | -24.2 | 0.97 | -44.2 | -0.66 |
| Long | 784 | 49.9 % | -0.083 | -65.2 | 0.85 | -72.8 | -2.33 |
| Short | 578 | 48.3 % | -0.101 | -58.4 | 0.82 | -68.4 | -2.43 |
| 1.ª mitad | 681 | 49.2 % | -0.093 | -63.4 | 0.83 | -67.2 | -2.43 |
| 2.ª mitad | 681 | 49.2 % | -0.088 | -60.2 | 0.84 | -76.6 | -2.30 |

Por año (R neto medio y operaciones): 2018 -0.115 (48), 2019 -0.272 (168), 2020 -0.017 (142), 2021 -0.034 (168), 2022 -0.019 (173), 2023 -0.168 (175), 2024 -0.096 (167), 2025 -0.110 (179), 2026 +0.029 (142).

Sensibilidad (R neto medio y t): colchón 0 % -0.104 (t -3.85), colchón 50 % -0.091 (t -3.38), objetivo 1,5:1 -0.089 (t -2.70), objetivo 2:1 -0.094 (t -2.49).

### ORB 06:15–06:30

Rotura con cuerpo desde las 06:30 hasta las 12:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.078 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 630, stop 706, por tiempo 5.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1341 | 47.2 % | -0.134 | -180.3 | 0.76 | -187.3 | -4.92 |
| Sin costes | 1341 | 47.2 % | -0.056 | -75.4 | 0.89 | -86.7 | -2.06 |
| Long | 776 | 48.2 % | -0.122 | -94.8 | 0.78 | -101.4 | -3.40 |
| Short | 565 | 45.8 % | -0.151 | -85.5 | 0.74 | -93.2 | -3.61 |
| 1.ª mitad | 671 | 46.3 % | -0.155 | -103.8 | 0.73 | -109.5 | -4.00 |
| 2.ª mitad | 670 | 48.1 % | -0.114 | -76.5 | 0.79 | -78.9 | -2.96 |

Por año (R neto medio y operaciones): 2018 -0.099 (45), 2019 -0.231 (153), 2020 -0.142 (150), 2021 -0.156 (167), 2022 -0.109 (177), 2023 -0.141 (183), 2024 -0.074 (171), 2025 -0.133 (163), 2026 -0.103 (132).

Sensibilidad (R neto medio y t): colchón 0 % -0.157 (t -5.74), colchón 50 % -0.114 (t -4.19), objetivo 1,5:1 -0.130 (t -3.93), objetivo 2:1 -0.126 (t -3.32).

### ORB 06:30–06:45

Rotura con cuerpo desde las 06:45 hasta las 12:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.074 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 664, stop 631, por tiempo 6.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1301 | 51.4 % | -0.048 | -62.8 | 0.91 | -82.9 | -1.74 |
| Sin costes | 1301 | 51.4 % | +0.026 | +34.0 | 1.05 | -22.6 | +0.95 |
| Long | 763 | 52.0 % | -0.042 | -31.7 | 0.92 | -42.4 | -1.15 |
| Short | 538 | 50.6 % | -0.058 | -31.1 | 0.89 | -42.4 | -1.34 |
| 1.ª mitad | 651 | 50.5 % | -0.070 | -45.5 | 0.87 | -50.6 | -1.78 |
| 2.ª mitad | 650 | 52.3 % | -0.027 | -17.3 | 0.95 | -37.9 | -0.68 |

Por año (R neto medio y operaciones): 2018 -0.001 (45), 2019 -0.167 (151), 2020 -0.013 (146), 2021 -0.044 (175), 2022 -0.052 (156), 2023 -0.088 (162), 2024 +0.014 (163), 2025 -0.108 (160), 2026 +0.066 (143).

Sensibilidad (R neto medio y t): colchón 0 % -0.071 (t -2.54), colchón 50 % -0.031 (t -1.13), objetivo 1,5:1 -0.009 (t -0.25), objetivo 2:1 +0.009 (t +0.22).

### ORB 06:45–07:00

Rotura con cuerpo desde las 07:00 hasta las 13:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.072 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 703, stop 640, por tiempo 9.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1352 | 52.3 % | -0.026 | -35.6 | 0.95 | -54.5 | -0.97 |
| Sin costes | 1352 | 52.3 % | +0.046 | +62.2 | 1.10 | -18.1 | +1.70 |
| Long | 799 | 51.3 % | -0.053 | -42.4 | 0.90 | -46.2 | -1.50 |
| Short | 553 | 53.7 % | +0.012 | +6.8 | 1.03 | -22.0 | +0.29 |
| 1.ª mitad | 676 | 51.9 % | -0.033 | -22.5 | 0.94 | -36.3 | -0.87 |
| 2.ª mitad | 676 | 52.7 % | -0.019 | -13.0 | 0.96 | -34.2 | -0.50 |

Por año (R neto medio y operaciones): 2018 -0.133 (51), 2019 -0.070 (149), 2020 -0.055 (155), 2021 +0.055 (164), 2022 -0.054 (152), 2023 -0.047 (175), 2024 -0.037 (170), 2025 +0.036 (181), 2026 -0.016 (155).

Sensibilidad (R neto medio y t): colchón 0 % -0.026 (t -0.94), colchón 50 % -0.005 (t -0.18), objetivo 1,5:1 +0.043 (t +1.26), objetivo 2:1 +0.041 (t +1.03).

