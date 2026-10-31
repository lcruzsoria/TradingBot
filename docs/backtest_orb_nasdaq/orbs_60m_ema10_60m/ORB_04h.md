# ORB de 60 min de las 04:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 04:00–05:00 | 1721 | 50.0 | -0.029 | -1.26 | +0.004 | 0.033 | no |
| 04:15–05:15 | 1640 | 50.1 | -0.035 | -1.46 | +0.001 | 0.036 | no |
| 04:30–05:30 | 1597 | 50.0 | -0.035 | -1.42 | +0.004 | 0.038 | no |
| 04:45–05:45 | 1596 | 48.7 | -0.059 | -2.39 | -0.019 | 0.040 | no |

## Detalle

### ORB 04:00–05:00

Rotura con cuerpo desde las 05:00 hasta las 11:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.033 R; ancho medio del ORB 0.32 %; cómo terminan: objetivo 790, stop 780, por tiempo 151.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1721 | 50.0 % | -0.029 | -50.3 | 0.94 | -95.2 | -1.26 |
| Sin costes | 1721 | 50.1 % | +0.004 | +7.0 | 1.01 | -66.0 | +0.18 |
| Long | 946 | 49.6 % | -0.045 | -42.2 | 0.91 | -68.9 | -1.42 |
| Short | 775 | 50.6 % | -0.010 | -8.1 | 0.98 | -38.8 | -0.30 |
| 1.ª mitad | 861 | 48.1 % | -0.070 | -60.0 | 0.86 | -74.7 | -2.13 |
| 2.ª mitad | 860 | 52.0 % | +0.011 | +9.7 | 1.02 | -23.6 | +0.34 |

Por año (R neto medio y operaciones): 2018 +0.162 (56), 2019 -0.085 (216), 2020 -0.167 (206), 2021 -0.033 (215), 2022 -0.061 (216), 2023 -0.032 (208), 2024 +0.041 (229), 2025 +0.040 (212), 2026 +0.014 (163).

Sensibilidad (R neto medio y t): colchón 0 % -0.038 (t -1.63), colchón 50 % -0.024 (t -1.06), objetivo 1,5:1 -0.032 (t -1.16), objetivo 2:1 -0.033 (t -1.09).

### ORB 04:15–05:15

Rotura con cuerpo desde las 05:15 hasta las 11:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.036 R; ancho medio del ORB 0.30 %; cómo terminan: objetivo 766, stop 763, por tiempo 111.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1640 | 50.1 % | -0.035 | -57.5 | 0.93 | -97.1 | -1.46 |
| Sin costes | 1640 | 50.4 % | +0.001 | +1.8 | 1.00 | -63.4 | +0.05 |
| Long | 953 | 48.7 % | -0.073 | -69.2 | 0.86 | -90.4 | -2.30 |
| Short | 687 | 52.0 % | +0.017 | +11.7 | 1.04 | -30.7 | +0.46 |
| 1.ª mitad | 820 | 48.3 % | -0.070 | -57.0 | 0.86 | -78.1 | -2.05 |
| 2.ª mitad | 820 | 51.8 % | -0.001 | -0.5 | 1.00 | -21.8 | -0.02 |

Por año (R neto medio y operaciones): 2018 +0.232 (53), 2019 -0.097 (200), 2020 -0.108 (203), 2021 -0.112 (202), 2022 -0.055 (201), 2023 -0.013 (200), 2024 +0.013 (218), 2025 +0.012 (200), 2026 +0.017 (163).

Sensibilidad (R neto medio y t): colchón 0 % -0.056 (t -2.31), colchón 50 % -0.032 (t -1.35), objetivo 1,5:1 -0.064 (t -2.28), objetivo 2:1 -0.062 (t -1.96).

### ORB 04:30–05:30

Rotura con cuerpo desde las 05:30 hasta las 11:30; a esa hora se cierra. ORB completos: 2097; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.038 R; ancho medio del ORB 0.28 %; cómo terminan: objetivo 752, stop 747, por tiempo 98.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1597 | 50.0 % | -0.035 | -55.3 | 0.93 | -88.7 | -1.42 |
| Sin costes | 1597 | 50.2 % | +0.004 | +5.8 | 1.01 | -48.3 | +0.15 |
| Long | 927 | 49.3 % | -0.062 | -57.4 | 0.88 | -78.1 | -1.93 |
| Short | 670 | 51.0 % | +0.003 | +2.1 | 1.01 | -22.4 | +0.09 |
| 1.ª mitad | 799 | 49.2 % | -0.053 | -42.0 | 0.90 | -65.4 | -1.53 |
| 2.ª mitad | 798 | 50.9 % | -0.017 | -13.4 | 0.97 | -27.1 | -0.48 |

Por año (R neto medio y operaciones): 2018 +0.267 (55), 2019 -0.116 (203), 2020 -0.101 (192), 2021 -0.021 (198), 2022 -0.078 (191), 2023 -0.055 (196), 2024 +0.012 (204), 2025 +0.018 (193), 2026 -0.019 (165).

Sensibilidad (R neto medio y t): colchón 0 % -0.048 (t -1.95), colchón 50 % -0.036 (t -1.49), objetivo 1,5:1 -0.057 (t -1.96), objetivo 2:1 -0.062 (t -1.91).

### ORB 04:45–05:45

Rotura con cuerpo desde las 05:45 hasta las 11:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.040 R; ancho medio del ORB 0.27 %; cómo terminan: objetivo 740, stop 767, por tiempo 89.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1596 | 48.7 % | -0.059 | -93.4 | 0.89 | -113.8 | -2.39 |
| Sin costes | 1596 | 48.9 % | -0.019 | -30.2 | 0.96 | -62.4 | -0.77 |
| Long | 927 | 46.8 % | -0.101 | -94.0 | 0.81 | -111.3 | -3.15 |
| Short | 669 | 51.3 % | +0.001 | +0.6 | 1.00 | -29.1 | +0.02 |
| 1.ª mitad | 798 | 48.7 % | -0.055 | -43.8 | 0.89 | -61.4 | -1.60 |
| 2.ª mitad | 798 | 48.6 % | -0.062 | -49.6 | 0.88 | -64.5 | -1.79 |

Por año (R neto medio y operaciones): 2018 -0.030 (54), 2019 -0.057 (205), 2020 -0.110 (179), 2021 -0.013 (202), 2022 -0.064 (191), 2023 -0.120 (202), 2024 -0.040 (200), 2025 -0.047 (198), 2026 -0.024 (165).

Sensibilidad (R neto medio y t): colchón 0 % -0.064 (t -2.57), colchón 50 % -0.038 (t -1.58), objetivo 1,5:1 -0.061 (t -2.08), objetivo 2:1 -0.072 (t -2.20).

