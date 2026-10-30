# ORB de 60 min de las 12:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 12:00–13:00 | 1587 | 48.6 | -0.023 | -1.24 | -0.002 | 0.021 | no |
| 12:15–13:15 | 1560 | 51.0 | +0.009 | +0.49 | +0.030 | 0.021 | no |
| 12:30–13:30 | 1540 | 51.0 | +0.017 | +0.86 | +0.038 | 0.021 | no |
| 12:45–13:45 | 1532 | 51.2 | +0.011 | +0.59 | +0.033 | 0.021 | no |

## Detalle

### ORB 12:00–13:00

Rotura con cuerpo desde las 13:00 hasta las 19:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2020.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.49 %; cómo terminan: objetivo 381, stop 390, por tiempo 816.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1587 | 48.6 % | -0.023 | -37.3 | 0.93 | -46.0 | -1.24 |
| Sin costes | 1587 | 49.5 % | -0.002 | -3.7 | 0.99 | -31.2 | -0.12 |
| Long | 896 | 52.2 % | +0.010 | +9.0 | 1.03 | -20.9 | +0.40 |
| Short | 691 | 43.8 % | -0.067 | -46.2 | 0.81 | -53.1 | -2.36 |
| 1.ª mitad | 794 | 48.2 % | -0.026 | -20.8 | 0.92 | -46.0 | -0.96 |
| 2.ª mitad | 793 | 48.9 % | -0.021 | -16.5 | 0.94 | -25.1 | -0.79 |

Por año (R neto medio y operaciones): 2018 -0.124 (59), 2019 -0.069 (196), 2020 -0.058 (203), 2021 -0.039 (185), 2022 +0.084 (200), 2023 -0.068 (189), 2024 +0.045 (200), 2025 -0.047 (197), 2026 -0.007 (158).

Sensibilidad (R neto medio y t): colchón 0 % -0.017 (t -0.82), colchón 50 % -0.010 (t -0.59), objetivo 1,5:1 -0.005 (t -0.24), objetivo 2:1 -0.003 (t -0.12).

### ORB 12:15–13:15

Rotura con cuerpo desde las 13:15 hasta las 19:15; a esa hora se cierra. ORB completos: 2042; con rotura: 1962.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.48 %; cómo terminan: objetivo 397, stop 355, por tiempo 808.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1560 | 51.0 % | +0.009 | +14.5 | 1.03 | -28.3 | +0.49 |
| Sin costes | 1560 | 51.8 % | +0.030 | +47.2 | 1.10 | -25.3 | +1.58 |
| Long | 880 | 53.2 % | +0.040 | +35.5 | 1.13 | -21.5 | +1.58 |
| Short | 680 | 48.1 % | -0.031 | -21.0 | 0.91 | -30.0 | -1.07 |
| 1.ª mitad | 780 | 51.7 % | +0.021 | +16.2 | 1.06 | -17.7 | +0.75 |
| 2.ª mitad | 780 | 50.3 % | -0.002 | -1.7 | 0.99 | -28.3 | -0.08 |

Por año (R neto medio y operaciones): 2018 +0.111 (54), 2019 -0.021 (195), 2020 -0.046 (202), 2021 +0.015 (189), 2022 +0.126 (197), 2023 +0.046 (190), 2024 +0.022 (187), 2025 -0.096 (188), 2026 -0.002 (158).

Sensibilidad (R neto medio y t): colchón 0 % +0.012 (t +0.57), colchón 50 % +0.007 (t +0.39), objetivo 1,5:1 +0.017 (t +0.78), objetivo 2:1 +0.017 (t +0.76).

### ORB 12:30–13:30

Rotura con cuerpo desde las 13:30 hasta las 19:30; a esa hora se cierra. ORB completos: 2025; con rotura: 1947.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.48 %; cómo terminan: objetivo 388, stop 341, por tiempo 811.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1540 | 51.0 % | +0.017 | +25.5 | 1.05 | -19.4 | +0.86 |
| Sin costes | 1540 | 51.9 % | +0.038 | +58.3 | 1.12 | -17.9 | +1.97 |
| Long | 878 | 53.4 % | +0.042 | +37.1 | 1.14 | -13.5 | +1.66 |
| Short | 662 | 47.7 % | -0.018 | -11.6 | 0.95 | -22.2 | -0.60 |
| 1.ª mitad | 770 | 51.6 % | +0.030 | +22.8 | 1.09 | -19.4 | +1.05 |
| 2.ª mitad | 770 | 50.4 % | +0.004 | +2.8 | 1.01 | -19.4 | +0.14 |

Por año (R neto medio y operaciones): 2018 +0.093 (52), 2019 -0.033 (179), 2020 -0.040 (206), 2021 +0.030 (181), 2022 +0.148 (202), 2023 +0.009 (193), 2024 +0.022 (185), 2025 -0.014 (187), 2026 -0.025 (155).

Sensibilidad (R neto medio y t): colchón 0 % +0.014 (t +0.66), colchón 50 % +0.016 (t +0.90), objetivo 1,5:1 +0.019 (t +0.88), objetivo 2:1 +0.035 (t +1.56).

### ORB 12:45–13:45

Rotura con cuerpo desde las 13:45 hasta las 19:45; a esa hora se cierra. ORB completos: 2025; con rotura: 1950.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.48 %; cómo terminan: objetivo 365, stop 320, por tiempo 847.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1532 | 51.2 % | +0.011 | +17.1 | 1.04 | -21.9 | +0.59 |
| Sin costes | 1532 | 51.8 % | +0.033 | +49.9 | 1.11 | -16.1 | +1.73 |
| Long | 878 | 53.3 % | +0.030 | +26.1 | 1.10 | -16.4 | +1.19 |
| Short | 654 | 48.3 % | -0.014 | -9.0 | 0.96 | -23.9 | -0.48 |
| 1.ª mitad | 766 | 52.6 % | +0.030 | +23.3 | 1.10 | -19.5 | +1.11 |
| 2.ª mitad | 766 | 49.7 % | -0.008 | -6.2 | 0.97 | -21.9 | -0.31 |

Por año (R neto medio y operaciones): 2018 +0.136 (53), 2019 -0.082 (188), 2020 +0.066 (199), 2021 +0.035 (186), 2022 +0.089 (201), 2023 -0.021 (188), 2024 +0.002 (187), 2025 -0.015 (188), 2026 -0.040 (142).

Sensibilidad (R neto medio y t): colchón 0 % +0.015 (t +0.73), colchón 50 % +0.016 (t +0.96), objetivo 1,5:1 +0.008 (t +0.40), objetivo 2:1 +0.021 (t +0.94).

