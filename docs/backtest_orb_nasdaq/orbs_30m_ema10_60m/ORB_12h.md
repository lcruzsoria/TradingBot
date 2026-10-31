# ORB de 30 min de las 12:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 12:00–12:30 | 1457 | 50.2 | -0.019 | -0.83 | +0.009 | 0.028 | no |
| 12:15–12:45 | 1478 | 50.7 | -0.013 | -0.55 | +0.017 | 0.030 | no |
| 12:30–13:00 | 1485 | 50.6 | -0.002 | -0.08 | +0.028 | 0.030 | no |
| 12:45–13:15 | 1429 | 52.0 | +0.016 | +0.70 | +0.045 | 0.029 | no |

## Detalle

### ORB 12:00–12:30

Rotura con cuerpo desde las 12:30 hasta las 18:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2079.

**No pasa los criterios**. Coste medio 0.028 R; ancho medio del ORB 0.37 %; cómo terminan: objetivo 519, stop 519, por tiempo 419.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1457 | 50.2 % | -0.019 | -27.6 | 0.95 | -37.5 | -0.83 |
| Sin costes | 1457 | 50.9 % | +0.009 | +13.2 | 1.02 | -29.5 | +0.40 |
| Long | 824 | 53.3 % | +0.026 | +21.4 | 1.07 | -26.9 | +0.85 |
| Short | 633 | 46.1 % | -0.077 | -49.0 | 0.83 | -53.9 | -2.23 |
| 1.ª mitad | 729 | 51.3 % | -0.004 | -2.7 | 0.99 | -26.2 | -0.11 |
| 2.ª mitad | 728 | 49.0 % | -0.034 | -24.9 | 0.92 | -37.5 | -1.06 |

Por año (R neto medio y operaciones): 2018 -0.093 (57), 2019 -0.070 (172), 2020 +0.045 (189), 2021 -0.002 (165), 2022 +0.034 (181), 2023 -0.057 (175), 2024 +0.056 (189), 2025 -0.096 (175), 2026 -0.054 (154).

Sensibilidad (R neto medio y t): colchón 0 % -0.014 (t -0.57), colchón 50 % -0.019 (t -0.89), objetivo 1,5:1 -0.017 (t -0.67), objetivo 2:1 -0.001 (t -0.03).

### ORB 12:15–12:45

Rotura con cuerpo desde las 12:45 hasta las 18:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2074.

**No pasa los criterios**. Coste medio 0.030 R; ancho medio del ORB 0.35 %; cómo terminan: objetivo 547, stop 521, por tiempo 410.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1478 | 50.7 % | -0.013 | -18.6 | 0.97 | -36.4 | -0.55 |
| Sin costes | 1478 | 51.3 % | +0.017 | +25.1 | 1.04 | -31.3 | +0.74 |
| Long | 847 | 52.5 % | +0.010 | +8.8 | 1.03 | -28.9 | +0.34 |
| Short | 631 | 48.3 % | -0.043 | -27.4 | 0.90 | -37.0 | -1.24 |
| 1.ª mitad | 739 | 51.6 % | -0.005 | -3.8 | 0.99 | -30.9 | -0.16 |
| 2.ª mitad | 739 | 49.9 % | -0.020 | -14.8 | 0.95 | -36.4 | -0.62 |

Por año (R neto medio y operaciones): 2018 -0.145 (60), 2019 -0.035 (183), 2020 -0.026 (184), 2021 -0.001 (172), 2022 +0.119 (175), 2023 -0.046 (182), 2024 +0.046 (184), 2025 -0.068 (189), 2026 -0.045 (149).

Sensibilidad (R neto medio y t): colchón 0 % -0.013 (t -0.54), colchón 50 % -0.010 (t -0.46), objetivo 1,5:1 +0.011 (t +0.42), objetivo 2:1 +0.026 (t +0.91).

### ORB 12:30–13:00

Rotura con cuerpo desde las 13:00 hasta las 19:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2067.

**No pasa los criterios**. Coste medio 0.030 R; ancho medio del ORB 0.34 %; cómo terminan: objetivo 560, stop 517, por tiempo 408.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1485 | 50.6 % | -0.002 | -2.8 | 1.00 | -37.1 | -0.08 |
| Sin costes | 1485 | 51.0 % | +0.028 | +42.1 | 1.07 | -21.2 | +1.25 |
| Long | 833 | 53.8 % | +0.038 | +32.0 | 1.10 | -16.1 | +1.27 |
| Short | 652 | 46.5 % | -0.053 | -34.8 | 0.88 | -44.7 | -1.55 |
| 1.ª mitad | 743 | 51.5 % | +0.013 | +10.0 | 1.03 | -31.5 | +0.41 |
| 2.ª mitad | 742 | 49.6 % | -0.017 | -12.8 | 0.96 | -37.1 | -0.55 |

Por año (R neto medio y operaciones): 2018 -0.076 (54), 2019 -0.041 (177), 2020 -0.003 (186), 2021 -0.072 (179), 2022 +0.219 (179), 2023 -0.031 (178), 2024 -0.039 (191), 2025 -0.008 (180), 2026 -0.017 (161).

Sensibilidad (R neto medio y t): colchón 0 % -0.012 (t -0.52), colchón 50 % +0.008 (t +0.36), objetivo 1,5:1 +0.007 (t +0.28), objetivo 2:1 +0.027 (t +0.96).

### ORB 12:45–13:15

Rotura con cuerpo desde las 13:15 hasta las 19:15; a esa hora se cierra. ORB completos: 2042; con rotura: 2014.

**No pasa los criterios**. Coste medio 0.029 R; ancho medio del ORB 0.34 %; cómo terminan: objetivo 538, stop 477, por tiempo 414.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1429 | 52.0 % | +0.016 | +23.2 | 1.04 | -28.8 | +0.70 |
| Sin costes | 1429 | 52.2 % | +0.045 | +64.4 | 1.12 | -19.7 | +1.95 |
| Long | 818 | 53.9 % | +0.038 | +30.7 | 1.10 | -19.8 | +1.22 |
| Short | 611 | 49.4 % | -0.012 | -7.5 | 0.97 | -24.2 | -0.35 |
| 1.ª mitad | 715 | 53.7 % | +0.038 | +26.9 | 1.10 | -19.4 | +1.14 |
| 2.ª mitad | 714 | 50.3 % | -0.005 | -3.7 | 0.99 | -28.8 | -0.16 |

Por año (R neto medio y operaciones): 2018 +0.084 (48), 2019 -0.072 (174), 2020 +0.000 (188), 2021 +0.024 (175), 2022 +0.223 (176), 2023 +0.056 (170), 2024 -0.018 (177), 2025 -0.072 (176), 2026 -0.037 (145).

Sensibilidad (R neto medio y t): colchón 0 % +0.020 (t +0.81), colchón 50 % +0.024 (t +1.11), objetivo 1,5:1 +0.034 (t +1.28), objetivo 2:1 +0.036 (t +1.27).

