# ORB de 45 min de las 11:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 11:00–11:45 | 1579 | 51.6 | +0.019 | +0.98 | +0.038 | 0.019 | no |
| 11:15–12:00 | 1552 | 51.0 | +0.001 | +0.06 | +0.022 | 0.021 | no |
| 11:30–12:15 | 1535 | 50.0 | -0.006 | -0.29 | +0.015 | 0.021 | no |
| 11:45–12:30 | 1533 | 51.0 | +0.001 | +0.06 | +0.024 | 0.023 | no |

## Detalle

### ORB 11:00–11:45

Rotura con cuerpo desde las 11:45 hasta las 17:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2047.

**No pasa los criterios**. Coste medio 0.019 R; ancho medio del ORB 0.53 %; cómo terminan: objetivo 431, stop 374, por tiempo 774.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1579 | 51.6 % | +0.019 | +30.0 | 1.06 | -19.4 | +0.98 |
| Sin costes | 1579 | 52.4 % | +0.038 | +60.4 | 1.12 | -15.9 | +1.97 |
| Long | 892 | 54.5 % | +0.052 | +46.1 | 1.17 | -16.3 | +2.03 |
| Short | 687 | 47.7 % | -0.023 | -16.0 | 0.94 | -28.7 | -0.78 |
| 1.ª mitad | 790 | 51.3 % | +0.018 | +14.3 | 1.06 | -19.4 | +0.67 |
| 2.ª mitad | 789 | 51.8 % | +0.020 | +15.7 | 1.06 | -13.4 | +0.72 |

Por año (R neto medio y operaciones): 2018 -0.060 (62), 2019 -0.034 (197), 2020 +0.092 (201), 2021 -0.030 (203), 2022 +0.090 (190), 2023 -0.003 (192), 2024 +0.042 (194), 2025 +0.081 (190), 2026 -0.080 (150).

Sensibilidad (R neto medio y t): colchón 0 % +0.012 (t +0.57), colchón 50 % +0.032 (t +1.80), objetivo 1,5:1 +0.044 (t +2.05), objetivo 2:1 +0.041 (t +1.79).

### ORB 11:15–12:00

Rotura con cuerpo desde las 12:00 hasta las 18:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2046.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.49 %; cómo terminan: objetivo 433, stop 405, por tiempo 714.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1552 | 51.0 % | +0.001 | +1.8 | 1.00 | -26.8 | +0.06 |
| Sin costes | 1552 | 51.5 % | +0.022 | +33.8 | 1.06 | -22.6 | +1.09 |
| Long | 864 | 54.4 % | +0.036 | +30.9 | 1.11 | -17.9 | +1.36 |
| Short | 688 | 46.8 % | -0.042 | -29.2 | 0.89 | -40.0 | -1.38 |
| 1.ª mitad | 776 | 52.6 % | +0.020 | +15.2 | 1.06 | -26.8 | +0.69 |
| 2.ª mitad | 776 | 49.5 % | -0.017 | -13.4 | 0.95 | -20.4 | -0.61 |

Por año (R neto medio y operaciones): 2018 -0.067 (61), 2019 -0.085 (188), 2020 +0.139 (201), 2021 +0.026 (189), 2022 +0.012 (191), 2023 -0.063 (177), 2024 +0.063 (196), 2025 -0.028 (198), 2026 -0.060 (151).

Sensibilidad (R neto medio y t): colchón 0 % -0.003 (t -0.16), colchón 50 % +0.002 (t +0.14), objetivo 1,5:1 +0.013 (t +0.58), objetivo 2:1 +0.028 (t +1.17).

### ORB 11:30–12:15

Rotura con cuerpo desde las 12:15 hasta las 18:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2050.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.47 %; cómo terminan: objetivo 444, stop 425, por tiempo 666.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1535 | 50.0 % | -0.006 | -9.1 | 0.98 | -32.8 | -0.29 |
| Sin costes | 1535 | 50.7 % | +0.015 | +23.7 | 1.04 | -20.4 | +0.76 |
| Long | 846 | 53.0 % | +0.038 | +32.0 | 1.11 | -14.2 | +1.40 |
| Short | 689 | 46.4 % | -0.060 | -41.1 | 0.85 | -47.2 | -1.93 |
| 1.ª mitad | 768 | 51.7 % | +0.019 | +14.4 | 1.05 | -18.9 | +0.64 |
| 2.ª mitad | 767 | 48.4 % | -0.031 | -23.4 | 0.92 | -32.8 | -1.07 |

Por año (R neto medio y operaciones): 2018 -0.097 (59), 2019 -0.059 (185), 2020 +0.119 (199), 2021 +0.010 (177), 2022 +0.013 (191), 2023 -0.095 (181), 2024 +0.042 (202), 2025 -0.039 (194), 2026 -0.028 (147).

Sensibilidad (R neto medio y t): colchón 0 % -0.008 (t -0.38), colchón 50 % +0.004 (t +0.19), objetivo 1,5:1 +0.002 (t +0.10), objetivo 2:1 +0.013 (t +0.56).

### ORB 11:45–12:30

Rotura con cuerpo desde las 12:30 hasta las 18:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2055.

**No pasa los criterios**. Coste medio 0.023 R; ancho medio del ORB 0.45 %; cómo terminan: objetivo 453, stop 430, por tiempo 650.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1533 | 51.0 % | +0.001 | +1.9 | 1.00 | -25.3 | +0.06 |
| Sin costes | 1533 | 51.9 % | +0.024 | +36.9 | 1.07 | -19.7 | +1.17 |
| Long | 866 | 54.0 % | +0.032 | +28.0 | 1.09 | -21.0 | +1.19 |
| Short | 667 | 47.1 % | -0.039 | -26.1 | 0.90 | -32.8 | -1.24 |
| 1.ª mitad | 767 | 51.2 % | +0.010 | +8.0 | 1.03 | -21.4 | +0.35 |
| 2.ª mitad | 766 | 50.8 % | -0.008 | -6.2 | 0.98 | -25.3 | -0.28 |

Por año (R neto medio y operaciones): 2018 -0.049 (62), 2019 -0.041 (184), 2020 +0.007 (198), 2021 +0.008 (176), 2022 +0.080 (193), 2023 -0.026 (181), 2024 +0.052 (198), 2025 -0.013 (188), 2026 -0.058 (153).

Sensibilidad (R neto medio y t): colchón 0 % +0.000 (t +0.02), colchón 50 % +0.003 (t +0.18), objetivo 1,5:1 -0.004 (t -0.18), objetivo 2:1 +0.012 (t +0.52).

