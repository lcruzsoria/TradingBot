# ORB de 30 min de las 03:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 03:00–03:30 | 1656 | 48.6 | -0.049 | -2.23 | -0.010 | 0.039 | no |
| 03:15–03:45 | 1585 | 49.3 | -0.063 | -2.62 | -0.020 | 0.043 | no |
| 03:30–04:00 | 1560 | 48.9 | -0.066 | -2.69 | -0.021 | 0.045 | no |
| 03:45–04:15 | 1593 | 48.3 | -0.075 | -3.05 | -0.032 | 0.043 | no |

## Detalle

### ORB 03:00–03:30

Rotura con cuerpo desde las 03:30 hasta las 09:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2087.

**No pasa los criterios**. Coste medio 0.039 R; ancho medio del ORB 0.28 %; cómo terminan: objetivo 631, stop 630, por tiempo 395.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1656 | 48.6 % | -0.049 | -81.3 | 0.89 | -98.5 | -2.23 |
| Sin costes | 1656 | 49.0 % | -0.010 | -16.3 | 0.98 | -51.9 | -0.45 |
| Long | 927 | 48.3 % | -0.048 | -44.5 | 0.89 | -60.9 | -1.64 |
| Short | 729 | 48.8 % | -0.050 | -36.8 | 0.89 | -50.1 | -1.51 |
| 1.ª mitad | 828 | 49.0 % | -0.030 | -25.1 | 0.93 | -34.4 | -1.00 |
| 2.ª mitad | 828 | 48.1 % | -0.068 | -56.2 | 0.86 | -68.2 | -2.12 |

Por año (R neto medio y operaciones): 2018 +0.002 (57), 2019 -0.077 (202), 2020 +0.018 (205), 2021 -0.007 (210), 2022 -0.094 (221), 2023 -0.052 (207), 2024 -0.059 (190), 2025 -0.151 (200), 2026 +0.029 (164).

Sensibilidad (R neto medio y t): colchón 0 % -0.055 (t -2.41), colchón 50 % -0.034 (t -1.67), objetivo 1,5:1 -0.033 (t -1.29), objetivo 2:1 -0.040 (t -1.45).

### ORB 03:15–03:45

Rotura con cuerpo desde las 03:45 hasta las 09:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.043 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 697, stop 730, por tiempo 158.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1585 | 49.3 % | -0.063 | -99.9 | 0.87 | -120.8 | -2.62 |
| Sin costes | 1585 | 49.4 % | -0.020 | -31.9 | 0.96 | -63.6 | -0.84 |
| Long | 905 | 49.3 % | -0.069 | -62.9 | 0.86 | -78.1 | -2.18 |
| Short | 680 | 49.4 % | -0.054 | -37.0 | 0.89 | -61.0 | -1.48 |
| 1.ª mitad | 793 | 48.4 % | -0.080 | -63.6 | 0.84 | -81.5 | -2.39 |
| 2.ª mitad | 792 | 50.3 % | -0.046 | -36.2 | 0.91 | -46.7 | -1.33 |

Por año (R neto medio y operaciones): 2018 +0.095 (53), 2019 -0.187 (197), 2020 -0.094 (205), 2021 -0.045 (191), 2022 -0.059 (205), 2023 -0.107 (195), 2024 +0.026 (184), 2025 -0.075 (196), 2026 +0.016 (159).

Sensibilidad (R neto medio y t): colchón 0 % -0.080 (t -3.26), colchón 50 % -0.056 (t -2.40), objetivo 1,5:1 -0.064 (t -2.27), objetivo 2:1 -0.053 (t -1.69).

### ORB 03:30–04:00

Rotura con cuerpo desde las 04:00 hasta las 10:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.045 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 713, stop 751, por tiempo 96.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1560 | 48.9 % | -0.066 | -103.5 | 0.87 | -104.0 | -2.69 |
| Sin costes | 1560 | 49.2 % | -0.021 | -32.6 | 0.96 | -45.7 | -0.85 |
| Long | 894 | 50.2 % | -0.048 | -43.2 | 0.90 | -48.1 | -1.49 |
| Short | 666 | 47.1 % | -0.091 | -60.4 | 0.83 | -67.0 | -2.38 |
| 1.ª mitad | 780 | 48.6 % | -0.078 | -61.0 | 0.85 | -63.5 | -2.26 |
| 2.ª mitad | 780 | 49.2 % | -0.055 | -42.6 | 0.89 | -60.0 | -1.55 |

Por año (R neto medio y operaciones): 2018 -0.064 (52), 2019 -0.139 (193), 2020 -0.156 (184), 2021 +0.037 (179), 2022 -0.006 (203), 2023 -0.030 (186), 2024 +0.017 (193), 2025 -0.142 (194), 2026 -0.115 (176).

Sensibilidad (R neto medio y t): colchón 0 % -0.066 (t -2.66), colchón 50 % -0.053 (t -2.22), objetivo 1,5:1 -0.063 (t -2.13), objetivo 2:1 -0.072 (t -2.22).

### ORB 03:45–04:15

Rotura con cuerpo desde las 04:15 hasta las 10:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.043 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 728, stop 776, por tiempo 89.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1593 | 48.3 % | -0.075 | -118.9 | 0.86 | -120.9 | -3.05 |
| Sin costes | 1593 | 48.4 % | -0.032 | -51.1 | 0.94 | -64.3 | -1.31 |
| Long | 888 | 50.7 % | -0.034 | -30.4 | 0.93 | -41.3 | -1.05 |
| Short | 705 | 45.4 % | -0.126 | -88.5 | 0.77 | -103.8 | -3.41 |
| 1.ª mitad | 797 | 48.1 % | -0.088 | -69.7 | 0.83 | -70.7 | -2.55 |
| 2.ª mitad | 796 | 48.6 % | -0.062 | -49.2 | 0.88 | -50.9 | -1.77 |

Por año (R neto medio y operaciones): 2018 -0.142 (56), 2019 -0.141 (203), 2020 -0.060 (186), 2021 -0.084 (192), 2022 -0.038 (205), 2023 -0.185 (201), 2024 +0.072 (201), 2025 -0.015 (195), 2026 -0.140 (154).

Sensibilidad (R neto medio y t): colchón 0 % -0.059 (t -2.39), colchón 50 % -0.071 (t -2.96), objetivo 1,5:1 -0.066 (t -2.24), objetivo 2:1 -0.069 (t -2.11).

