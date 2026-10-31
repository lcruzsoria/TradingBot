# ORB de 15 min de las 18:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 18:00–18:15 | 1256 | 50.4 | -0.034 | -1.35 | +0.026 | 0.060 | no |
| 18:15–18:30 | 1108 | 53.2 | -0.040 | -1.37 | +0.056 | 0.096 | no |
| 18:30–18:45 | 1202 | 51.3 | -0.061 | -2.15 | +0.040 | 0.101 | no |
| 18:45–19:00 | 1237 | 53.8 | -0.041 | -1.45 | +0.071 | 0.111 | no |

## Detalle

### ORB 18:00–18:15

Rotura con cuerpo desde las 18:15 hasta las 00:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2079.

**No pasa los criterios**. Coste medio 0.060 R; ancho medio del ORB 0.20 %; cómo terminan: objetivo 500, stop 476, por tiempo 280.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1256 | 50.4 % | -0.034 | -43.0 | 0.92 | -52.7 | -1.35 |
| Sin costes | 1256 | 51.4 % | +0.026 | +32.5 | 1.06 | -18.4 | +1.02 |
| Long | 739 | 51.2 % | -0.032 | -23.7 | 0.93 | -27.7 | -0.97 |
| Short | 517 | 49.3 % | -0.037 | -19.3 | 0.92 | -30.9 | -0.93 |
| 1.ª mitad | 628 | 47.8 % | -0.065 | -41.1 | 0.86 | -44.1 | -1.79 |
| 2.ª mitad | 628 | 53.0 % | -0.003 | -1.9 | 0.99 | -23.8 | -0.09 |

Por año (R neto medio y operaciones): 2018 -0.268 (43), 2019 -0.023 (150), 2020 -0.084 (159), 2021 -0.032 (139), 2022 -0.039 (142), 2023 +0.002 (134), 2024 +0.028 (168), 2025 -0.065 (177), 2026 +0.013 (144).

Sensibilidad (R neto medio y t): colchón 0 % -0.054 (t -2.07), colchón 50 % -0.019 (t -0.80), objetivo 1,5:1 -0.018 (t -0.62), objetivo 2:1 -0.024 (t -0.75).

### ORB 18:15–18:30

Rotura con cuerpo desde las 18:30 hasta las 00:30 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2089.

**No pasa los criterios**. Coste medio 0.096 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 544, stop 476, por tiempo 88.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1108 | 53.2 % | -0.040 | -44.3 | 0.92 | -69.6 | -1.37 |
| Sin costes | 1108 | 53.2 % | +0.056 | +62.2 | 1.13 | -16.2 | +1.93 |
| Long | 643 | 53.8 % | -0.041 | -26.5 | 0.92 | -45.9 | -1.07 |
| Short | 465 | 52.3 % | -0.038 | -17.7 | 0.92 | -30.3 | -0.85 |
| 1.ª mitad | 554 | 50.7 % | -0.093 | -51.5 | 0.82 | -52.4 | -2.24 |
| 2.ª mitad | 554 | 55.6 % | +0.013 | +7.2 | 1.03 | -24.6 | +0.32 |

Por año (R neto medio y operaciones): 2018 -0.346 (29), 2019 -0.040 (123), 2020 -0.059 (134), 2021 -0.087 (126), 2022 -0.119 (128), 2023 -0.095 (134), 2024 +0.003 (156), 2025 +0.037 (142), 2026 +0.086 (136).

Sensibilidad (R neto medio y t): colchón 0 % -0.058 (t -1.96), colchón 50 % -0.025 (t -0.87), objetivo 1,5:1 -0.040 (t -1.15), objetivo 2:1 -0.025 (t -0.64).

### ORB 18:30–18:45

Rotura con cuerpo desde las 18:45 hasta las 00:45 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.101 R; ancho medio del ORB 0.11 %; cómo terminan: objetivo 593, stop 542, por tiempo 67.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1202 | 51.3 % | -0.061 | -73.1 | 0.88 | -82.3 | -2.15 |
| Sin costes | 1202 | 51.6 % | +0.040 | +48.2 | 1.09 | -33.8 | +1.42 |
| Long | 693 | 50.1 % | -0.097 | -67.1 | 0.82 | -70.9 | -2.59 |
| Short | 509 | 53.0 % | -0.012 | -6.0 | 0.98 | -19.5 | -0.27 |
| 1.ª mitad | 601 | 50.6 % | -0.087 | -52.4 | 0.84 | -62.9 | -2.16 |
| 2.ª mitad | 601 | 52.1 % | -0.034 | -20.6 | 0.93 | -27.4 | -0.87 |

Por año (R neto medio y operaciones): 2018 -0.063 (39), 2019 -0.008 (140), 2020 -0.073 (150), 2021 -0.044 (148), 2022 -0.239 (138), 2023 -0.082 (131), 2024 +0.023 (152), 2025 +0.008 (165), 2026 -0.093 (139).

Sensibilidad (R neto medio y t): colchón 0 % -0.059 (t -2.06), colchón 50 % -0.023 (t -0.82), objetivo 1,5:1 -0.025 (t -0.72), objetivo 2:1 -0.026 (t -0.67).

### ORB 18:45–19:00

Rotura con cuerpo desde las 19:00 hasta las 01:00 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.111 R; ancho medio del ORB 0.10 %; cómo terminan: objetivo 634, stop 550, por tiempo 53.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1237 | 53.8 % | -0.041 | -50.3 | 0.92 | -70.1 | -1.45 |
| Sin costes | 1237 | 53.9 % | +0.071 | +87.3 | 1.16 | -17.4 | +2.53 |
| Long | 705 | 54.2 % | -0.040 | -28.5 | 0.92 | -58.7 | -1.08 |
| Short | 532 | 53.2 % | -0.041 | -21.9 | 0.92 | -28.8 | -0.96 |
| 1.ª mitad | 619 | 53.8 % | -0.043 | -26.4 | 0.92 | -36.8 | -1.07 |
| 2.ª mitad | 618 | 53.7 % | -0.039 | -24.0 | 0.92 | -41.0 | -0.98 |

Por año (R neto medio y operaciones): 2018 -0.097 (49), 2019 -0.043 (157), 2020 +0.069 (151), 2021 -0.098 (144), 2022 -0.096 (150), 2023 -0.108 (141), 2024 -0.042 (151), 2025 +0.012 (159), 2026 -0.008 (135).

Sensibilidad (R neto medio y t): colchón 0 % -0.055 (t -1.92), colchón 50 % -0.036 (t -1.30), objetivo 1,5:1 -0.027 (t -0.79), objetivo 2:1 -0.037 (t -0.97).

