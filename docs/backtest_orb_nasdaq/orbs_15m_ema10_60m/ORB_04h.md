# ORB de 15 min de las 04:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 04:00–04:15 | 1519 | 48.8 | -0.077 | -3.04 | -0.023 | 0.054 | no |
| 04:15–04:30 | 1373 | 49.9 | -0.067 | -2.47 | -0.003 | 0.064 | no |
| 04:30–04:45 | 1354 | 49.8 | -0.072 | -2.66 | -0.001 | 0.070 | no |
| 04:45–05:00 | 1356 | 46.1 | -0.155 | -5.73 | -0.079 | 0.075 | no |

## Detalle

### ORB 04:00–04:15

Rotura con cuerpo desde las 04:15 hasta las 10:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.054 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 721, stop 757, por tiempo 41.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1519 | 48.8 % | -0.077 | -117.2 | 0.85 | -134.9 | -3.04 |
| Sin costes | 1519 | 48.9 % | -0.023 | -35.4 | 0.95 | -64.5 | -0.92 |
| Long | 849 | 50.1 % | -0.054 | -46.2 | 0.90 | -56.4 | -1.60 |
| Short | 670 | 47.3 % | -0.106 | -71.0 | 0.81 | -91.6 | -2.77 |
| 1.ª mitad | 760 | 47.2 % | -0.116 | -88.0 | 0.79 | -88.0 | -3.24 |
| 2.ª mitad | 759 | 50.5 % | -0.038 | -29.1 | 0.93 | -48.2 | -1.06 |

Por año (R neto medio y operaciones): 2018 -0.180 (52), 2019 -0.121 (190), 2020 +0.003 (177), 2021 -0.226 (189), 2022 -0.086 (191), 2023 -0.125 (196), 2024 -0.012 (193), 2025 -0.019 (189), 2026 +0.029 (142).

Sensibilidad (R neto medio y t): colchón 0 % -0.063 (t -2.45), colchón 50 % -0.056 (t -2.25), objetivo 1,5:1 -0.075 (t -2.45), objetivo 2:1 -0.074 (t -2.13).

### ORB 04:15–04:30

Rotura con cuerpo desde las 04:30 hasta las 10:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.064 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 680, stop 681, por tiempo 12.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1373 | 49.9 % | -0.067 | -91.5 | 0.87 | -98.3 | -2.47 |
| Sin costes | 1373 | 49.9 % | -0.003 | -3.7 | 0.99 | -37.4 | -0.10 |
| Long | 792 | 51.3 % | -0.044 | -35.2 | 0.91 | -43.4 | -1.25 |
| Short | 581 | 48.0 % | -0.097 | -56.3 | 0.82 | -69.9 | -2.34 |
| 1.ª mitad | 687 | 49.1 % | -0.089 | -61.0 | 0.84 | -61.0 | -2.32 |
| 2.ª mitad | 686 | 50.7 % | -0.044 | -30.5 | 0.91 | -37.3 | -1.17 |

Por año (R neto medio y operaciones): 2018 -0.146 (48), 2019 -0.152 (175), 2020 +0.002 (165), 2021 -0.077 (164), 2022 -0.126 (176), 2023 -0.133 (179), 2024 +0.116 (166), 2025 -0.101 (169), 2026 -0.013 (131).

Sensibilidad (R neto medio y t): colchón 0 % -0.054 (t -1.99), colchón 50 % -0.045 (t -1.68), objetivo 1,5:1 -0.050 (t -1.53), objetivo 2:1 -0.050 (t -1.33).

### ORB 04:30–04:45

Rotura con cuerpo desde las 04:45 hasta las 10:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.070 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 669, stop 671, por tiempo 14.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1354 | 49.8 % | -0.072 | -97.3 | 0.86 | -112.7 | -2.66 |
| Sin costes | 1354 | 49.9 % | -0.001 | -1.8 | 1.00 | -38.4 | -0.05 |
| Long | 780 | 50.8 % | -0.060 | -46.6 | 0.89 | -68.6 | -1.68 |
| Short | 574 | 48.4 % | -0.088 | -50.6 | 0.84 | -60.5 | -2.12 |
| 1.ª mitad | 677 | 48.9 % | -0.095 | -64.0 | 0.83 | -74.0 | -2.48 |
| 2.ª mitad | 677 | 50.7 % | -0.049 | -33.3 | 0.91 | -46.8 | -1.28 |

Por año (R neto medio y operaciones): 2018 +0.135 (54), 2019 -0.119 (168), 2020 -0.136 (164), 2021 -0.037 (170), 2022 -0.172 (162), 2023 +0.062 (166), 2024 -0.077 (176), 2025 -0.149 (170), 2026 +0.006 (124).

Sensibilidad (R neto medio y t): colchón 0 % -0.075 (t -2.75), colchón 50 % -0.057 (t -2.12), objetivo 1,5:1 -0.089 (t -2.71), objetivo 2:1 -0.074 (t -1.95).

### ORB 04:45–05:00

Rotura con cuerpo desde las 05:00 hasta las 11:00; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.075 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 619, stop 727, por tiempo 10.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1356 | 46.1 % | -0.155 | -209.8 | 0.73 | -216.6 | -5.73 |
| Sin costes | 1356 | 46.1 % | -0.079 | -107.7 | 0.85 | -115.3 | -2.94 |
| Long | 786 | 46.7 % | -0.154 | -121.3 | 0.73 | -125.6 | -4.33 |
| Short | 570 | 45.3 % | -0.155 | -88.5 | 0.73 | -96.1 | -3.74 |
| 1.ª mitad | 678 | 45.9 % | -0.164 | -111.5 | 0.72 | -114.3 | -4.31 |
| 2.ª mitad | 678 | 46.3 % | -0.145 | -98.3 | 0.75 | -105.1 | -3.78 |

Por año (R neto medio y operaciones): 2018 -0.213 (48), 2019 -0.147 (170), 2020 -0.249 (178), 2021 -0.087 (166), 2022 -0.126 (162), 2023 -0.112 (158), 2024 -0.168 (178), 2025 -0.257 (162), 2026 -0.048 (134).

Sensibilidad (R neto medio y t): colchón 0 % -0.170 (t -6.29), colchón 50 % -0.133 (t -4.92), objetivo 1,5:1 -0.145 (t -4.43), objetivo 2:1 -0.154 (t -4.13).

