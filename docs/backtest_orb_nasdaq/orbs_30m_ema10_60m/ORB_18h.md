# ORB de 30 min de las 18:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 18:00–18:30 | 1259 | 50.7 | -0.018 | -0.75 | +0.033 | 0.051 | no |
| 18:15–18:45 | 1239 | 51.9 | -0.021 | -0.78 | +0.051 | 0.071 | no |
| 18:30–19:00 | 1283 | 52.5 | -0.019 | -0.70 | +0.059 | 0.078 | no |
| 18:45–19:15 | 1306 | 50.1 | -0.070 | -2.72 | +0.003 | 0.073 | no |

## Detalle

### ORB 18:00–18:30

Rotura con cuerpo desde las 18:30 hasta las 00:30 (día siguiente); a esa hora se cierra. ORB completos: 2093; con rotura: 2046.

**No pasa los criterios**. Coste medio 0.051 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 448, stop 416, por tiempo 395.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1259 | 50.7 % | -0.018 | -22.9 | 0.95 | -26.9 | -0.75 |
| Sin costes | 1259 | 51.5 % | +0.033 | +41.3 | 1.09 | -15.6 | +1.36 |
| Long | 741 | 52.5 % | -0.018 | -13.5 | 0.95 | -31.3 | -0.58 |
| Short | 518 | 48.1 % | -0.018 | -9.4 | 0.96 | -23.4 | -0.47 |
| 1.ª mitad | 630 | 49.0 % | -0.041 | -26.1 | 0.90 | -26.1 | -1.19 |
| 2.ª mitad | 629 | 52.3 % | +0.005 | +3.2 | 1.01 | -19.0 | +0.15 |

Por año (R neto medio y operaciones): 2018 -0.346 (41), 2019 +0.042 (144), 2020 -0.007 (153), 2021 -0.024 (143), 2022 -0.079 (141), 2023 +0.026 (136), 2024 +0.030 (171), 2025 -0.024 (177), 2026 -0.024 (153).

Sensibilidad (R neto medio y t): colchón 0 % -0.037 (t -1.44), colchón 50 % -0.012 (t -0.54), objetivo 1,5:1 -0.004 (t -0.16), objetivo 2:1 -0.018 (t -0.60).

### ORB 18:15–18:45

Rotura con cuerpo desde las 18:45 hasta las 00:45 (día siguiente); a esa hora se cierra. ORB completos: 2095; con rotura: 2077.

**No pasa los criterios**. Coste medio 0.071 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 542, stop 483, por tiempo 214.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1239 | 51.9 % | -0.021 | -25.4 | 0.95 | -43.0 | -0.78 |
| Sin costes | 1239 | 52.5 % | +0.051 | +62.9 | 1.12 | -19.1 | +1.93 |
| Long | 705 | 53.2 % | -0.009 | -6.4 | 0.98 | -31.5 | -0.26 |
| Short | 534 | 50.2 % | -0.036 | -19.0 | 0.92 | -28.7 | -0.89 |
| 1.ª mitad | 620 | 50.5 % | -0.054 | -33.4 | 0.89 | -34.6 | -1.43 |
| 2.ª mitad | 619 | 53.3 % | +0.013 | +7.9 | 1.03 | -26.9 | +0.35 |

Por año (R neto medio y operaciones): 2018 -0.279 (39), 2019 -0.012 (145), 2020 -0.022 (155), 2021 +0.024 (147), 2022 -0.146 (140), 2023 +0.027 (134), 2024 +0.102 (158), 2025 +0.010 (167), 2026 -0.091 (154).

Sensibilidad (R neto medio y t): colchón 0 % -0.024 (t -0.89), colchón 50 % -0.010 (t -0.41), objetivo 1,5:1 +0.007 (t +0.22), objetivo 2:1 +0.012 (t +0.36).

### ORB 18:30–19:00

Rotura con cuerpo desde las 19:00 hasta las 01:00 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.078 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 595, stop 516, por tiempo 172.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1283 | 52.5 % | -0.019 | -23.8 | 0.96 | -52.0 | -0.70 |
| Sin costes | 1283 | 52.8 % | +0.059 | +75.7 | 1.14 | -29.4 | +2.24 |
| Long | 730 | 52.2 % | -0.034 | -25.2 | 0.93 | -49.2 | -0.98 |
| Short | 553 | 52.8 % | +0.002 | +1.3 | 1.01 | -19.1 | +0.06 |
| 1.ª mitad | 642 | 53.1 % | -0.022 | -13.9 | 0.95 | -27.3 | -0.57 |
| 2.ª mitad | 641 | 51.8 % | -0.016 | -10.0 | 0.97 | -27.4 | -0.42 |

Por año (R neto medio y operaciones): 2018 -0.088 (45), 2019 +0.015 (158), 2020 +0.026 (159), 2021 -0.025 (156), 2022 -0.110 (151), 2023 -0.098 (138), 2024 +0.030 (157), 2025 +0.061 (168), 2026 -0.048 (151).

Sensibilidad (R neto medio y t): colchón 0 % -0.022 (t -0.83), colchón 50 % -0.022 (t -0.88), objetivo 1,5:1 -0.011 (t -0.36), objetivo 2:1 -0.029 (t -0.83).

### ORB 18:45–19:15

Rotura con cuerpo desde las 19:15 hasta las 01:15 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.073 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 542, stop 547, por tiempo 217.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1306 | 50.1 % | -0.070 | -91.4 | 0.85 | -104.7 | -2.72 |
| Sin costes | 1306 | 50.8 % | +0.003 | +3.5 | 1.01 | -43.9 | +0.10 |
| Long | 730 | 52.9 % | -0.032 | -23.3 | 0.93 | -43.4 | -0.93 |
| Short | 576 | 46.5 % | -0.118 | -68.1 | 0.77 | -76.8 | -3.02 |
| 1.ª mitad | 653 | 50.1 % | -0.065 | -42.5 | 0.87 | -47.3 | -1.77 |
| 2.ª mitad | 653 | 50.1 % | -0.075 | -49.0 | 0.84 | -61.6 | -2.07 |

Por año (R neto medio y operaciones): 2018 -0.087 (46), 2019 -0.065 (176), 2020 +0.033 (159), 2021 -0.104 (167), 2022 -0.168 (147), 2023 -0.150 (138), 2024 -0.041 (156), 2025 -0.019 (167), 2026 -0.060 (150).

Sensibilidad (R neto medio y t): colchón 0 % -0.091 (t -3.45), colchón 50 % -0.054 (t -2.18), objetivo 1,5:1 -0.056 (t -1.84), objetivo 2:1 -0.060 (t -1.81).

