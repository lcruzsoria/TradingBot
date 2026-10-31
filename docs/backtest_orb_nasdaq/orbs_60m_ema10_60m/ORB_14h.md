# ORB de 60 min de las 14:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 14:00–15:00 | 1465 | 48.9 | -0.005 | -0.31 | +0.015 | 0.021 | no |
| 14:15–15:15 | 1419 | 49.7 | -0.009 | -0.51 | +0.013 | 0.021 | no |
| 14:30–15:30 | 1382 | 48.9 | -0.011 | -0.66 | +0.010 | 0.021 | no |
| 14:45–15:45 | 1354 | 48.5 | -0.007 | -0.44 | +0.014 | 0.021 | no |

## Detalle

### ORB 14:00–15:00

Rotura con cuerpo desde las 15:00 hasta las 21:00; a esa hora se cierra. ORB completos: 2025; con rotura: 1871.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.51 %; cómo terminan: objetivo 277, stop 246, por tiempo 942.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1465 | 48.9 % | -0.005 | -8.0 | 0.98 | -40.7 | -0.31 |
| Sin costes | 1465 | 50.4 % | +0.015 | +22.6 | 1.06 | -24.7 | +0.88 |
| Long | 840 | 52.4 % | +0.027 | +23.0 | 1.11 | -15.3 | +1.20 |
| Short | 625 | 44.2 % | -0.050 | -31.0 | 0.84 | -38.8 | -1.82 |
| 1.ª mitad | 733 | 49.8 % | +0.010 | +7.2 | 1.04 | -19.0 | +0.39 |
| 2.ª mitad | 732 | 48.0 % | -0.021 | -15.2 | 0.93 | -26.0 | -0.86 |

Por año (R neto medio y operaciones): 2018 +0.136 (54), 2019 +0.021 (173), 2020 +0.042 (199), 2021 -0.035 (179), 2022 -0.052 (192), 2023 -0.039 (180), 2024 -0.027 (168), 2025 +0.015 (170), 2026 -0.013 (150).

Sensibilidad (R neto medio y t): colchón 0 % -0.010 (t -0.52), colchón 50 % -0.004 (t -0.24), objetivo 1,5:1 -0.007 (t -0.40), objetivo 2:1 -0.001 (t -0.07).

### ORB 14:15–15:15

Rotura con cuerpo desde las 15:15 hasta las 21:15; a esa hora se cierra. ORB completos: 2025; con rotura: 1832.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.51 %; cómo terminan: objetivo 234, stop 206, por tiempo 979.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1419 | 49.7 % | -0.009 | -12.2 | 0.97 | -35.4 | -0.51 |
| Sin costes | 1419 | 51.2 % | +0.013 | +17.8 | 1.05 | -19.8 | +0.74 |
| Long | 818 | 52.0 % | +0.005 | +4.4 | 1.02 | -15.6 | +0.24 |
| Short | 601 | 46.6 % | -0.028 | -16.5 | 0.90 | -22.7 | -1.09 |
| 1.ª mitad | 710 | 51.0 % | +0.023 | +16.6 | 1.09 | -11.5 | +0.97 |
| 2.ª mitad | 709 | 48.4 % | -0.041 | -28.8 | 0.85 | -30.5 | -1.73 |

Por año (R neto medio y operaciones): 2018 +0.116 (50), 2019 +0.018 (169), 2020 +0.006 (200), 2021 +0.044 (174), 2022 -0.020 (184), 2023 -0.071 (167), 2024 -0.020 (171), 2025 +0.040 (153), 2026 -0.111 (151).

Sensibilidad (R neto medio y t): colchón 0 % -0.000 (t -0.01), colchón 50 % -0.011 (t -0.76), objetivo 1,5:1 +0.001 (t +0.03), objetivo 2:1 +0.001 (t +0.07).

### ORB 14:30–15:30

Rotura con cuerpo desde las 15:30 hasta las 21:30; a esa hora se cierra. ORB completos: 2026; con rotura: 1795.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.52 %; cómo terminan: objetivo 202, stop 172, por tiempo 1008.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1382 | 48.9 % | -0.011 | -15.1 | 0.96 | -28.6 | -0.66 |
| Sin costes | 1382 | 50.6 % | +0.010 | +13.9 | 1.04 | -17.4 | +0.61 |
| Long | 773 | 53.0 % | +0.018 | +13.6 | 1.07 | -14.0 | +0.80 |
| Short | 609 | 43.7 % | -0.047 | -28.7 | 0.82 | -29.8 | -1.92 |
| 1.ª mitad | 691 | 50.1 % | +0.014 | +9.5 | 1.06 | -11.9 | +0.59 |
| 2.ª mitad | 691 | 47.8 % | -0.035 | -24.5 | 0.86 | -28.2 | -1.54 |

Por año (R neto medio y operaciones): 2018 -0.064 (55), 2019 +0.028 (175), 2020 +0.036 (194), 2021 -0.014 (171), 2022 +0.016 (178), 2023 -0.095 (157), 2024 +0.038 (159), 2025 +0.028 (146), 2026 -0.130 (147).

Sensibilidad (R neto medio y t): colchón 0 % -0.021 (t -1.19), colchón 50 % -0.006 (t -0.43), objetivo 1,5:1 -0.002 (t -0.14), objetivo 2:1 -0.000 (t -0.03).

### ORB 14:45–15:45

Rotura con cuerpo desde las 15:45 hasta las 21:45; a esa hora se cierra. ORB completos: 2025; con rotura: 1736.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.52 %; cómo terminan: objetivo 167, stop 146, por tiempo 1041.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1354 | 48.5 % | -0.007 | -9.4 | 0.97 | -21.2 | -0.44 |
| Sin costes | 1354 | 50.4 % | +0.014 | +18.6 | 1.06 | -15.4 | +0.87 |
| Long | 761 | 51.9 % | +0.024 | +18.2 | 1.11 | -13.0 | +1.15 |
| Short | 593 | 44.2 % | -0.047 | -27.7 | 0.81 | -31.6 | -1.96 |
| 1.ª mitad | 677 | 48.2 % | +0.004 | +2.9 | 1.02 | -9.3 | +0.19 |
| 2.ª mitad | 677 | 48.9 % | -0.018 | -12.3 | 0.92 | -21.2 | -0.81 |

Por año (R neto medio y operaciones): 2018 -0.108 (50), 2019 +0.021 (176), 2020 +0.037 (187), 2021 -0.009 (176), 2022 +0.012 (164), 2023 -0.065 (149), 2024 +0.018 (162), 2025 +0.044 (152), 2026 -0.109 (138).

Sensibilidad (R neto medio y t): colchón 0 % -0.002 (t -0.12), colchón 50 % -0.006 (t -0.47), objetivo 1,5:1 -0.012 (t -0.73), objetivo 2:1 -0.010 (t -0.60).

