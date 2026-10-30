# ORB de 30 min de las 14:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 14:00–14:30 | 1450 | 51.3 | -0.002 | -0.07 | +0.027 | 0.028 | no |
| 14:15–14:45 | 1398 | 49.6 | -0.013 | -0.60 | +0.016 | 0.029 | no |
| 14:30–15:00 | 1410 | 48.5 | -0.032 | -1.48 | -0.002 | 0.029 | no |
| 14:45–15:15 | 1374 | 49.6 | -0.019 | -0.94 | +0.009 | 0.029 | no |

## Detalle

### ORB 14:00–14:30

Rotura con cuerpo desde las 14:30 hasta las 20:30; a esa hora se cierra. ORB completos: 2025; con rotura: 1985.

**No pasa los criterios**. Coste medio 0.028 R; ancho medio del ORB 0.37 %; cómo terminan: objetivo 447, stop 421, por tiempo 582.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1450 | 51.3 % | -0.002 | -2.2 | 1.00 | -28.5 | -0.07 |
| Sin costes | 1450 | 52.3 % | +0.027 | +38.8 | 1.08 | -20.9 | +1.24 |
| Long | 833 | 52.7 % | +0.010 | +8.1 | 1.03 | -19.4 | +0.34 |
| Short | 617 | 49.4 % | -0.017 | -10.3 | 0.96 | -25.4 | -0.51 |
| 1.ª mitad | 725 | 53.1 % | +0.015 | +11.1 | 1.04 | -27.8 | +0.49 |
| 2.ª mitad | 725 | 49.5 % | -0.018 | -13.3 | 0.95 | -28.5 | -0.62 |

Por año (R neto medio y operaciones): 2018 +0.295 (49), 2019 -0.071 (173), 2020 -0.004 (193), 2021 -0.032 (176), 2022 +0.059 (191), 2023 +0.039 (177), 2024 -0.061 (182), 2025 -0.053 (167), 2026 +0.026 (142).

Sensibilidad (R neto medio y t): colchón 0 % +0.013 (t +0.57), colchón 50 % +0.002 (t +0.12), objetivo 1,5:1 +0.006 (t +0.26), objetivo 2:1 +0.008 (t +0.32).

### ORB 14:15–14:45

Rotura con cuerpo desde las 14:45 hasta las 20:45; a esa hora se cierra. ORB completos: 2025; con rotura: 1989.

**No pasa los criterios**. Coste medio 0.029 R; ancho medio del ORB 0.36 %; cómo terminan: objetivo 421, stop 400, por tiempo 577.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1398 | 49.6 % | -0.013 | -18.3 | 0.96 | -36.6 | -0.60 |
| Sin costes | 1398 | 50.6 % | +0.016 | +22.4 | 1.05 | -22.0 | +0.74 |
| Long | 800 | 51.9 % | +0.005 | +4.1 | 1.01 | -26.5 | +0.18 |
| Short | 598 | 46.5 % | -0.037 | -22.4 | 0.90 | -28.3 | -1.14 |
| 1.ª mitad | 699 | 51.5 % | +0.016 | +11.5 | 1.04 | -21.8 | +0.52 |
| 2.ª mitad | 699 | 47.6 % | -0.043 | -29.8 | 0.88 | -34.1 | -1.43 |

Por año (R neto medio y operaciones): 2018 +0.160 (49), 2019 -0.047 (164), 2020 +0.035 (182), 2021 -0.012 (169), 2022 +0.021 (193), 2023 -0.016 (185), 2024 -0.049 (168), 2025 -0.051 (153), 2026 -0.059 (135).

Sensibilidad (R neto medio y t): colchón 0 % -0.029 (t -1.28), colchón 50 % -0.017 (t -0.84), objetivo 1,5:1 -0.012 (t -0.49), objetivo 2:1 -0.003 (t -0.10).

### ORB 14:30–15:00

Rotura con cuerpo desde las 15:00 hasta las 21:00; a esa hora se cierra. ORB completos: 2026; con rotura: 1980.

**No pasa los criterios**. Coste medio 0.029 R; ancho medio del ORB 0.37 %; cómo terminan: objetivo 404, stop 401, por tiempo 605.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1410 | 48.5 % | -0.032 | -44.5 | 0.92 | -63.3 | -1.48 |
| Sin costes | 1410 | 49.6 % | -0.002 | -3.2 | 0.99 | -35.3 | -0.11 |
| Long | 784 | 50.5 % | -0.014 | -11.2 | 0.96 | -26.3 | -0.50 |
| Short | 626 | 46.0 % | -0.053 | -33.3 | 0.86 | -43.2 | -1.67 |
| 1.ª mitad | 705 | 50.1 % | -0.013 | -9.5 | 0.96 | -30.5 | -0.44 |
| 2.ª mitad | 705 | 47.0 % | -0.050 | -35.0 | 0.87 | -49.2 | -1.68 |

Por año (R neto medio y operaciones): 2018 +0.121 (48), 2019 -0.045 (164), 2020 -0.079 (189), 2021 +0.014 (176), 2022 -0.001 (185), 2023 -0.061 (184), 2024 -0.102 (160), 2025 -0.035 (160), 2026 +0.019 (144).

Sensibilidad (R neto medio y t): colchón 0 % -0.045 (t -1.99), colchón 50 % -0.018 (t -0.92), objetivo 1,5:1 -0.018 (t -0.76), objetivo 2:1 -0.011 (t -0.44).

### ORB 14:45–15:15

Rotura con cuerpo desde las 15:15 hasta las 21:15; a esa hora se cierra. ORB completos: 2026; con rotura: 1945.

**No pasa los criterios**. Coste medio 0.029 R; ancho medio del ORB 0.37 %; cómo terminan: objetivo 356, stop 327, por tiempo 691.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1374 | 49.6 % | -0.019 | -26.4 | 0.94 | -39.0 | -0.94 |
| Sin costes | 1374 | 50.7 % | +0.009 | +12.8 | 1.03 | -27.8 | +0.45 |
| Long | 771 | 50.5 % | -0.014 | -10.6 | 0.96 | -27.5 | -0.49 |
| Short | 603 | 48.4 % | -0.026 | -15.8 | 0.92 | -25.3 | -0.86 |
| 1.ª mitad | 687 | 51.4 % | +0.010 | +7.0 | 1.03 | -15.4 | +0.35 |
| 2.ª mitad | 687 | 47.7 % | -0.049 | -33.4 | 0.86 | -36.0 | -1.68 |

Por año (R neto medio y operaciones): 2018 +0.043 (50), 2019 -0.012 (154), 2020 -0.027 (190), 2021 +0.031 (169), 2022 +0.005 (183), 2023 -0.079 (174), 2024 -0.054 (171), 2025 +0.052 (144), 2026 -0.087 (139).

Sensibilidad (R neto medio y t): colchón 0 % -0.026 (t -1.17), colchón 50 % -0.015 (t -0.80), objetivo 1,5:1 -0.013 (t -0.57), objetivo 2:1 -0.005 (t -0.23).

