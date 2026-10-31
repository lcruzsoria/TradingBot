# ORB de 45 min de las 00:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 00:00–00:45 | 1458 | 49.5 | -0.076 | -2.98 | -0.003 | 0.074 | no |
| 00:15–01:00 | 1444 | 49.2 | -0.079 | -3.06 | -0.005 | 0.074 | no |
| 00:30–01:15 | 1495 | 49.7 | -0.062 | -2.47 | +0.004 | 0.066 | no |
| 00:45–01:30 | 1521 | 50.6 | -0.034 | -1.39 | +0.028 | 0.062 | no |

## Detalle

### ORB 00:00–00:45

Rotura con cuerpo desde las 00:45 hasta las 06:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.074 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 686, stop 688, por tiempo 84.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1458 | 49.5 % | -0.076 | -111.2 | 0.85 | -124.3 | -2.98 |
| Sin costes | 1458 | 49.7 % | -0.003 | -3.7 | 0.99 | -67.5 | -0.10 |
| Long | 830 | 51.4 % | -0.054 | -44.8 | 0.89 | -64.5 | -1.58 |
| Short | 628 | 47.0 % | -0.106 | -66.4 | 0.80 | -70.9 | -2.72 |
| 1.ª mitad | 729 | 45.1 % | -0.150 | -109.1 | 0.73 | -112.7 | -4.16 |
| 2.ª mitad | 729 | 53.9 % | -0.003 | -2.1 | 0.99 | -27.9 | -0.08 |

Por año (R neto medio y operaciones): 2018 -0.040 (56), 2019 -0.221 (178), 2020 -0.025 (174), 2021 -0.175 (179), 2022 -0.145 (176), 2023 -0.034 (175), 2024 -0.073 (182), 2025 +0.079 (177), 2026 -0.019 (161).

Sensibilidad (R neto medio y t): colchón 0 % -0.086 (t -3.35), colchón 50 % -0.053 (t -2.13), objetivo 1,5:1 -0.068 (t -2.24), objetivo 2:1 -0.024 (t -0.70).

### ORB 00:15–01:00

Rotura con cuerpo desde las 01:00 hasta las 07:00; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.074 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 676, stop 679, por tiempo 89.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1444 | 49.2 % | -0.079 | -113.6 | 0.85 | -136.1 | -3.06 |
| Sin costes | 1444 | 49.4 % | -0.005 | -6.7 | 0.99 | -57.7 | -0.18 |
| Long | 818 | 51.2 % | -0.043 | -35.5 | 0.91 | -63.6 | -1.27 |
| Short | 626 | 46.6 % | -0.125 | -78.0 | 0.77 | -79.9 | -3.20 |
| 1.ª mitad | 722 | 46.1 % | -0.139 | -100.6 | 0.75 | -104.8 | -3.85 |
| 2.ª mitad | 722 | 52.4 % | -0.018 | -12.9 | 0.96 | -62.1 | -0.49 |

Por año (R neto medio y operaciones): 2018 +0.008 (55), 2019 -0.208 (177), 2020 -0.047 (175), 2021 -0.143 (172), 2022 -0.166 (161), 2023 +0.001 (165), 2024 -0.118 (195), 2025 +0.010 (177), 2026 +0.022 (167).

Sensibilidad (R neto medio y t): colchón 0 % -0.072 (t -2.76), colchón 50 % -0.047 (t -1.87), objetivo 1,5:1 -0.069 (t -2.25), objetivo 2:1 -0.027 (t -0.77).

### ORB 00:30–01:15

Rotura con cuerpo desde las 01:15 hasta las 07:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.066 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 695, stop 680, por tiempo 120.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1495 | 49.7 % | -0.062 | -92.2 | 0.88 | -110.0 | -2.47 |
| Sin costes | 1495 | 50.0 % | +0.004 | +6.2 | 1.01 | -49.3 | +0.17 |
| Long | 845 | 51.6 % | -0.028 | -23.3 | 0.94 | -44.2 | -0.83 |
| Short | 650 | 47.2 % | -0.106 | -69.0 | 0.80 | -73.1 | -2.79 |
| 1.ª mitad | 748 | 47.2 % | -0.108 | -80.9 | 0.79 | -84.7 | -3.08 |
| 2.ª mitad | 747 | 52.2 % | -0.015 | -11.4 | 0.97 | -40.0 | -0.43 |

Por año (R neto medio y operaciones): 2018 -0.130 (57), 2019 -0.067 (169), 2020 -0.077 (183), 2021 -0.092 (193), 2022 -0.170 (171), 2023 +0.015 (182), 2024 -0.127 (189), 2025 -0.027 (182), 2026 +0.079 (169).

Sensibilidad (R neto medio y t): colchón 0 % -0.066 (t -2.59), colchón 50 % -0.043 (t -1.78), objetivo 1,5:1 -0.062 (t -2.07), objetivo 2:1 -0.036 (t -1.06).

### ORB 00:45–01:30

Rotura con cuerpo desde las 01:30 hasta las 07:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.062 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 711, stop 667, por tiempo 143.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1521 | 50.6 % | -0.034 | -52.2 | 0.93 | -86.5 | -1.39 |
| Sin costes | 1521 | 51.0 % | +0.028 | +42.5 | 1.06 | -29.2 | +1.13 |
| Long | 865 | 52.5 % | -0.008 | -7.0 | 0.98 | -47.3 | -0.25 |
| Short | 656 | 48.0 % | -0.069 | -45.2 | 0.86 | -63.6 | -1.82 |
| 1.ª mitad | 761 | 49.5 % | -0.048 | -36.6 | 0.90 | -49.9 | -1.38 |
| 2.ª mitad | 760 | 51.6 % | -0.021 | -15.7 | 0.96 | -51.7 | -0.59 |

Por año (R neto medio y operaciones): 2018 +0.024 (54), 2019 -0.038 (175), 2020 -0.029 (181), 2021 -0.056 (192), 2022 -0.084 (177), 2023 -0.019 (184), 2024 -0.153 (200), 2025 -0.008 (193), 2026 +0.118 (165).

Sensibilidad (R neto medio y t): colchón 0 % -0.034 (t -1.36), colchón 50 % -0.036 (t -1.52), objetivo 1,5:1 -0.043 (t -1.48), objetivo 2:1 -0.034 (t -1.03).

