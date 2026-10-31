# ORB de 30 min de las 01:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 01:00–01:30 | 1477 | 51.2 | -0.033 | -1.32 | +0.037 | 0.071 | no |
| 01:15–01:45 | 1462 | 50.6 | -0.056 | -2.20 | +0.016 | 0.072 | no |
| 01:30–02:00 | 1458 | 50.3 | -0.062 | -2.43 | +0.005 | 0.067 | no |
| 01:45–02:15 | 1531 | 48.7 | -0.078 | -3.18 | -0.021 | 0.057 | no |

## Detalle

### ORB 01:00–01:30

Rotura con cuerpo desde las 01:30 hasta las 07:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.071 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 717, stop 662, por tiempo 98.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1477 | 51.2 % | -0.033 | -49.5 | 0.93 | -85.8 | -1.32 |
| Sin costes | 1477 | 51.5 % | +0.037 | +55.4 | 1.08 | -30.6 | +1.48 |
| Long | 836 | 54.1 % | +0.014 | +12.0 | 1.03 | -32.8 | +0.43 |
| Short | 641 | 47.4 % | -0.096 | -61.5 | 0.82 | -77.2 | -2.48 |
| 1.ª mitad | 739 | 49.4 % | -0.065 | -47.9 | 0.87 | -60.4 | -1.81 |
| 2.ª mitad | 738 | 53.0 % | -0.002 | -1.6 | 1.00 | -41.2 | -0.06 |

Por año (R neto medio y operaciones): 2018 +0.052 (55), 2019 -0.107 (171), 2020 -0.020 (175), 2021 -0.049 (182), 2022 -0.107 (177), 2023 -0.037 (182), 2024 -0.087 (191), 2025 +0.020 (187), 2026 +0.109 (157).

Sensibilidad (R neto medio y t): colchón 0 % -0.026 (t -1.00), colchón 50 % -0.036 (t -1.46), objetivo 1,5:1 -0.028 (t -0.93), objetivo 2:1 -0.026 (t -0.75).

### ORB 01:15–01:45

Rotura con cuerpo desde las 01:45 hasta las 07:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.072 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 701, stop 672, por tiempo 89.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1462 | 50.6 % | -0.056 | -82.2 | 0.89 | -108.2 | -2.20 |
| Sin costes | 1462 | 50.8 % | +0.016 | +23.3 | 1.03 | -45.6 | +0.62 |
| Long | 837 | 53.3 % | -0.015 | -12.9 | 0.97 | -41.7 | -0.46 |
| Short | 625 | 47.0 % | -0.111 | -69.4 | 0.80 | -77.0 | -2.82 |
| 1.ª mitad | 731 | 48.4 % | -0.098 | -71.3 | 0.82 | -94.2 | -2.69 |
| 2.ª mitad | 731 | 52.8 % | -0.015 | -10.9 | 0.97 | -40.3 | -0.41 |

Por año (R neto medio y operaciones): 2018 +0.047 (54), 2019 -0.193 (170), 2020 -0.029 (183), 2021 -0.100 (177), 2022 -0.100 (170), 2023 +0.027 (182), 2024 -0.064 (183), 2025 -0.065 (186), 2026 +0.045 (157).

Sensibilidad (R neto medio y t): colchón 0 % -0.059 (t -2.28), colchón 50 % -0.048 (t -1.91), objetivo 1,5:1 -0.054 (t -1.76), objetivo 2:1 -0.051 (t -1.50).

### ORB 01:30–02:00

Rotura con cuerpo desde las 02:00 hasta las 08:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.067 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 684, stop 673, por tiempo 101.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1458 | 50.3 % | -0.062 | -90.3 | 0.88 | -108.0 | -2.43 |
| Sin costes | 1458 | 50.4 % | +0.005 | +7.9 | 1.01 | -34.7 | +0.21 |
| Long | 830 | 52.0 % | -0.038 | -31.7 | 0.92 | -40.6 | -1.14 |
| Short | 628 | 47.9 % | -0.093 | -58.6 | 0.82 | -68.8 | -2.39 |
| 1.ª mitad | 729 | 49.1 % | -0.085 | -62.1 | 0.84 | -78.8 | -2.38 |
| 2.ª mitad | 729 | 51.4 % | -0.039 | -28.2 | 0.92 | -37.3 | -1.07 |

Por año (R neto medio y operaciones): 2018 +0.075 (55), 2019 -0.143 (163), 2020 -0.108 (178), 2021 -0.040 (175), 2022 -0.107 (182), 2023 -0.005 (188), 2024 -0.072 (179), 2025 -0.036 (186), 2026 -0.032 (152).

Sensibilidad (R neto medio y t): colchón 0 % -0.065 (t -2.51), colchón 50 % -0.039 (t -1.57), objetivo 1,5:1 -0.035 (t -1.15), objetivo 2:1 -0.051 (t -1.51).

### ORB 01:45–02:15

Rotura con cuerpo desde las 02:15 hasta las 08:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.057 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 670, stop 703, por tiempo 158.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1531 | 48.7 % | -0.078 | -119.3 | 0.85 | -140.5 | -3.18 |
| Sin costes | 1531 | 49.0 % | -0.021 | -31.9 | 0.96 | -59.9 | -0.85 |
| Long | 885 | 49.4 % | -0.068 | -60.0 | 0.86 | -74.1 | -2.11 |
| Short | 646 | 47.8 % | -0.092 | -59.3 | 0.82 | -73.5 | -2.42 |
| 1.ª mitad | 766 | 47.5 % | -0.095 | -72.5 | 0.81 | -81.2 | -2.76 |
| 2.ª mitad | 765 | 49.9 % | -0.061 | -46.8 | 0.88 | -65.5 | -1.75 |

Por año (R neto medio y operaciones): 2018 +0.114 (58), 2019 -0.217 (187), 2020 -0.021 (177), 2021 -0.074 (193), 2022 -0.135 (191), 2023 -0.023 (195), 2024 -0.092 (193), 2025 -0.107 (192), 2026 +0.008 (145).

Sensibilidad (R neto medio y t): colchón 0 % -0.067 (t -2.68), colchón 50 % -0.049 (t -2.10), objetivo 1,5:1 -0.058 (t -2.02), objetivo 2:1 -0.069 (t -2.19).

