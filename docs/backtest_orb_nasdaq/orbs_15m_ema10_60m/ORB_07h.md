# ORB de 15 min de las 07:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 07:00–07:15 | 1497 | 49.4 | -0.071 | -2.75 | -0.010 | 0.061 | no |
| 07:15–07:30 | 1398 | 50.8 | -0.054 | -2.04 | +0.015 | 0.070 | no |
| 07:30–07:45 | 1429 | 47.4 | -0.118 | -4.48 | -0.051 | 0.067 | no |
| 07:45–08:00 | 1439 | 49.7 | -0.079 | -3.01 | -0.011 | 0.069 | no |

## Detalle

### ORB 07:00–07:15

Rotura con cuerpo desde las 07:15 hasta las 13:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.061 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 735, stop 751, por tiempo 11.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1497 | 49.4 % | -0.071 | -106.3 | 0.87 | -117.4 | -2.75 |
| Sin costes | 1497 | 49.4 % | -0.010 | -14.9 | 0.98 | -55.5 | -0.39 |
| Long | 869 | 48.0 % | -0.107 | -92.6 | 0.81 | -99.7 | -3.15 |
| Short | 628 | 51.4 % | -0.022 | -13.6 | 0.96 | -33.3 | -0.54 |
| 1.ª mitad | 749 | 49.4 % | -0.076 | -56.7 | 0.86 | -63.1 | -2.07 |
| 2.ª mitad | 748 | 49.5 % | -0.066 | -49.6 | 0.88 | -58.3 | -1.81 |

Por año (R neto medio y operaciones): 2018 -0.068 (54), 2019 -0.074 (175), 2020 -0.077 (178), 2021 -0.010 (190), 2022 -0.124 (178), 2023 -0.151 (191), 2024 -0.074 (190), 2025 -0.028 (188), 2026 -0.026 (153).

Sensibilidad (R neto medio y t): colchón 0 % -0.090 (t -3.47), colchón 50 % -0.080 (t -3.12), objetivo 1,5:1 -0.053 (t -1.70), objetivo 2:1 -0.064 (t -1.77).

### ORB 07:15–07:30

Rotura con cuerpo desde las 07:30 hasta las 13:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.070 R; ancho medio del ORB 0.14 %; cómo terminan: objetivo 705, stop 685, por tiempo 8.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1398 | 50.8 % | -0.054 | -76.2 | 0.90 | -99.5 | -2.04 |
| Sin costes | 1398 | 50.8 % | +0.015 | +21.2 | 1.03 | -31.0 | +0.57 |
| Long | 755 | 51.1 % | -0.056 | -42.1 | 0.89 | -64.2 | -1.54 |
| Short | 643 | 50.4 % | -0.053 | -34.0 | 0.90 | -49.7 | -1.34 |
| 1.ª mitad | 699 | 50.6 % | -0.060 | -41.7 | 0.89 | -62.1 | -1.58 |
| 2.ª mitad | 699 | 50.9 % | -0.049 | -34.5 | 0.91 | -42.6 | -1.31 |

Por año (R neto medio y operaciones): 2018 +0.049 (45), 2019 +0.047 (161), 2020 -0.052 (181), 2021 -0.183 (172), 2022 -0.057 (159), 2023 -0.032 (168), 2024 -0.007 (178), 2025 -0.125 (183), 2026 -0.043 (151).

Sensibilidad (R neto medio y t): colchón 0 % -0.081 (t -3.02), colchón 50 % -0.028 (t -1.04), objetivo 1,5:1 -0.040 (t -1.22), objetivo 2:1 -0.031 (t -0.81).

### ORB 07:30–07:45

Rotura con cuerpo desde las 07:45 hasta las 13:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.067 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 671, stop 746, por tiempo 12.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1429 | 47.4 % | -0.118 | -168.9 | 0.79 | -172.7 | -4.48 |
| Sin costes | 1429 | 47.4 % | -0.051 | -73.4 | 0.90 | -88.9 | -1.95 |
| Long | 772 | 47.9 % | -0.117 | -90.3 | 0.79 | -93.2 | -3.25 |
| Short | 657 | 46.9 % | -0.120 | -78.6 | 0.79 | -83.9 | -3.07 |
| 1.ª mitad | 715 | 48.3 % | -0.108 | -77.1 | 0.80 | -79.9 | -2.89 |
| 2.ª mitad | 714 | 46.6 % | -0.129 | -91.8 | 0.77 | -96.6 | -3.44 |

Por año (R neto medio y operaciones): 2018 -0.225 (52), 2019 -0.130 (185), 2020 -0.004 (170), 2021 -0.172 (166), 2022 -0.087 (173), 2023 -0.290 (186), 2024 -0.078 (174), 2025 -0.053 (175), 2026 -0.081 (148).

Sensibilidad (R neto medio y t): colchón 0 % -0.121 (t -4.58), colchón 50 % -0.070 (t -2.67), objetivo 1,5:1 -0.089 (t -2.76), objetivo 2:1 -0.079 (t -2.13).

### ORB 07:45–08:00

Rotura con cuerpo desde las 08:00 hasta las 14:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.069 R; ancho medio del ORB 0.14 %; cómo terminan: objetivo 706, stop 724, por tiempo 9.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1439 | 49.7 % | -0.079 | -114.0 | 0.85 | -132.6 | -3.01 |
| Sin costes | 1439 | 49.7 % | -0.011 | -15.1 | 0.98 | -50.2 | -0.40 |
| Long | 812 | 48.2 % | -0.117 | -95.2 | 0.79 | -100.2 | -3.35 |
| Short | 627 | 51.7 % | -0.030 | -18.7 | 0.94 | -44.6 | -0.75 |
| 1.ª mitad | 720 | 48.5 % | -0.108 | -77.6 | 0.80 | -79.1 | -2.90 |
| 2.ª mitad | 719 | 50.9 % | -0.051 | -36.4 | 0.90 | -60.0 | -1.35 |

Por año (R neto medio y operaciones): 2018 -0.156 (50), 2019 -0.086 (175), 2020 -0.127 (173), 2021 -0.145 (181), 2022 -0.055 (166), 2023 -0.119 (188), 2024 -0.067 (177), 2025 -0.013 (180), 2026 +0.018 (149).

Sensibilidad (R neto medio y t): colchón 0 % -0.108 (t -4.11), colchón 50 % -0.069 (t -2.63), objetivo 1,5:1 -0.056 (t -1.74), objetivo 2:1 -0.045 (t -1.22).

