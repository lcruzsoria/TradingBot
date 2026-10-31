# ORB de 60 min de las 01:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 01:00–02:00 | 1579 | 50.7 | -0.034 | -1.47 | +0.015 | 0.049 | no |
| 01:15–02:15 | 1665 | 49.1 | -0.050 | -2.23 | -0.005 | 0.045 | no |
| 01:30–02:30 | 1673 | 49.6 | -0.040 | -1.83 | +0.002 | 0.042 | no |
| 01:45–02:45 | 1669 | 48.9 | -0.041 | -1.84 | -0.000 | 0.041 | no |

## Detalle

### ORB 01:00–02:00

Rotura con cuerpo desde las 02:00 hasta las 08:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2088.

**No pasa los criterios**. Coste medio 0.049 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 664, stop 645, por tiempo 270.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1579 | 50.7 % | -0.034 | -54.3 | 0.93 | -71.3 | -1.47 |
| Sin costes | 1579 | 51.1 % | +0.015 | +23.0 | 1.03 | -31.1 | +0.62 |
| Long | 894 | 53.6 % | +0.003 | +2.7 | 1.01 | -25.0 | +0.10 |
| Short | 685 | 47.0 % | -0.083 | -57.0 | 0.83 | -63.5 | -2.32 |
| 1.ª mitad | 790 | 50.8 % | -0.038 | -30.0 | 0.92 | -44.1 | -1.15 |
| 2.ª mitad | 789 | 50.7 % | -0.031 | -24.3 | 0.93 | -49.8 | -0.93 |

Por año (R neto medio y operaciones): 2018 +0.005 (57), 2019 -0.105 (179), 2020 +0.083 (184), 2021 -0.097 (190), 2022 -0.044 (196), 2023 +0.016 (205), 2024 -0.036 (199), 2025 -0.122 (202), 2026 +0.027 (167).

Sensibilidad (R neto medio y t): colchón 0 % -0.029 (t -1.19), colchón 50 % -0.014 (t -0.63), objetivo 1,5:1 -0.024 (t -0.90), objetivo 2:1 -0.030 (t -1.02).

### ORB 01:15–02:15

Rotura con cuerpo desde las 02:15 hasta las 08:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2087.

**No pasa los criterios**. Coste medio 0.045 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 654, stop 659, por tiempo 352.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1665 | 49.1 % | -0.050 | -82.6 | 0.89 | -107.5 | -2.23 |
| Sin costes | 1665 | 49.6 % | -0.005 | -7.7 | 0.99 | -45.2 | -0.21 |
| Long | 957 | 50.5 % | -0.031 | -29.3 | 0.93 | -47.5 | -1.05 |
| Short | 708 | 47.3 % | -0.075 | -53.4 | 0.84 | -64.1 | -2.18 |
| 1.ª mitad | 833 | 47.2 % | -0.078 | -64.9 | 0.83 | -75.0 | -2.51 |
| 2.ª mitad | 832 | 51.1 % | -0.021 | -17.7 | 0.95 | -51.7 | -0.67 |

Por año (R neto medio y operaciones): 2018 +0.112 (62), 2019 -0.131 (197), 2020 -0.002 (189), 2021 -0.106 (210), 2022 -0.128 (210), 2023 +0.039 (212), 2024 -0.035 (210), 2025 -0.089 (213), 2026 +0.023 (162).

Sensibilidad (R neto medio y t): colchón 0 % -0.046 (t -2.01), colchón 50 % -0.036 (t -1.73), objetivo 1,5:1 -0.046 (t -1.79), objetivo 2:1 -0.052 (t -1.87).

### ORB 01:30–02:30

Rotura con cuerpo desde las 02:30 hasta las 08:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2080.

**No pasa los criterios**. Coste medio 0.042 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 655, stop 646, por tiempo 372.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1673 | 49.6 % | -0.040 | -67.6 | 0.91 | -95.0 | -1.83 |
| Sin costes | 1673 | 50.1 % | +0.002 | +3.2 | 1.00 | -43.0 | +0.09 |
| Long | 950 | 51.2 % | -0.024 | -22.4 | 0.94 | -41.0 | -0.82 |
| Short | 723 | 47.4 % | -0.062 | -45.2 | 0.87 | -58.1 | -1.83 |
| 1.ª mitad | 837 | 48.0 % | -0.063 | -53.1 | 0.86 | -66.8 | -2.07 |
| 2.ª mitad | 836 | 51.1 % | -0.017 | -14.5 | 0.96 | -32.3 | -0.55 |

Por año (R neto medio y operaciones): 2018 +0.157 (61), 2019 -0.133 (198), 2020 -0.017 (191), 2021 -0.098 (219), 2022 -0.091 (217), 2023 +0.010 (211), 2024 -0.023 (209), 2025 -0.081 (201), 2026 +0.076 (166).

Sensibilidad (R neto medio y t): colchón 0 % -0.054 (t -2.35), colchón 50 % -0.030 (t -1.46), objetivo 1,5:1 -0.046 (t -1.85), objetivo 2:1 -0.043 (t -1.61).

### ORB 01:45–02:45

Rotura con cuerpo desde las 02:45 hasta las 08:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2087.

**No pasa los criterios**. Coste medio 0.041 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 661, stop 658, por tiempo 350.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1669 | 48.9 % | -0.041 | -68.4 | 0.91 | -84.7 | -1.84 |
| Sin costes | 1669 | 49.3 % | -0.000 | -0.3 | 1.00 | -41.1 | -0.01 |
| Long | 929 | 50.8 % | -0.011 | -10.1 | 0.97 | -26.9 | -0.37 |
| Short | 740 | 46.5 % | -0.079 | -58.3 | 0.83 | -72.3 | -2.33 |
| 1.ª mitad | 835 | 48.4 % | -0.037 | -31.0 | 0.91 | -37.4 | -1.20 |
| 2.ª mitad | 834 | 49.4 % | -0.045 | -37.4 | 0.90 | -56.0 | -1.40 |

Por año (R neto medio y operaciones): 2018 -0.055 (62), 2019 -0.073 (209), 2020 +0.017 (202), 2021 -0.072 (212), 2022 -0.050 (204), 2023 +0.022 (210), 2024 -0.041 (205), 2025 -0.186 (195), 2026 +0.073 (170).

Sensibilidad (R neto medio y t): colchón 0 % -0.061 (t -2.65), colchón 50 % -0.034 (t -1.61), objetivo 1,5:1 -0.045 (t -1.77), objetivo 2:1 -0.039 (t -1.43).

