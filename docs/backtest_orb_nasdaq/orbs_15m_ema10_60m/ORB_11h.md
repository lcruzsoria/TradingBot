# ORB de 15 min de las 11:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 11:00–11:15 | 1444 | 50.8 | -0.002 | -0.08 | +0.027 | 0.029 | no |
| 11:15–11:30 | 1421 | 49.2 | -0.045 | -1.79 | -0.012 | 0.033 | no |
| 11:30–11:45 | 1389 | 49.4 | -0.033 | -1.29 | +0.002 | 0.034 | no |
| 11:45–12:00 | 1364 | 50.4 | -0.032 | -1.24 | +0.004 | 0.036 | no |

## Detalle

### ORB 11:00–11:15

Rotura con cuerpo desde las 11:15 hasta las 17:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.029 R; ancho medio del ORB 0.33 %; cómo terminan: objetivo 629, stop 592, por tiempo 223.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1444 | 50.8 % | -0.002 | -2.8 | 1.00 | -60.3 | -0.08 |
| Sin costes | 1444 | 51.1 % | +0.027 | +39.7 | 1.06 | -42.9 | +1.12 |
| Long | 808 | 52.4 % | +0.019 | +15.1 | 1.04 | -25.3 | +0.57 |
| Short | 636 | 48.9 % | -0.028 | -17.9 | 0.94 | -47.1 | -0.76 |
| 1.ª mitad | 722 | 53.6 % | +0.055 | +39.8 | 1.13 | -17.5 | +1.59 |
| 2.ª mitad | 722 | 48.1 % | -0.059 | -42.6 | 0.88 | -53.6 | -1.69 |

Por año (R neto medio y operaciones): 2018 +0.110 (61), 2019 +0.020 (175), 2020 +0.130 (195), 2021 +0.010 (174), 2022 -0.000 (169), 2023 -0.196 (180), 2024 -0.034 (178), 2025 +0.019 (164), 2026 -0.012 (148).

Sensibilidad (R neto medio y t): colchón 0 % -0.010 (t -0.41), colchón 50 % +0.021 (t +0.88), objetivo 1,5:1 -0.001 (t -0.03), objetivo 2:1 +0.029 (t +0.92).

### ORB 11:15–11:30

Rotura con cuerpo desde las 11:30 hasta las 17:30; a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.033 R; ancho medio del ORB 0.29 %; cómo terminan: objetivo 600, stop 626, por tiempo 195.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1421 | 49.2 % | -0.045 | -63.6 | 0.91 | -77.2 | -1.79 |
| Sin costes | 1421 | 49.8 % | -0.012 | -16.9 | 0.97 | -41.2 | -0.47 |
| Long | 790 | 50.5 % | -0.024 | -18.8 | 0.95 | -26.0 | -0.71 |
| Short | 631 | 47.5 % | -0.071 | -44.9 | 0.86 | -57.0 | -1.87 |
| 1.ª mitad | 711 | 51.3 % | -0.007 | -5.3 | 0.98 | -43.8 | -0.21 |
| 2.ª mitad | 710 | 47.0 % | -0.082 | -58.4 | 0.83 | -63.6 | -2.33 |

Por año (R neto medio y operaciones): 2018 +0.245 (49), 2019 -0.160 (185), 2020 +0.008 (181), 2021 +0.023 (183), 2022 -0.023 (172), 2023 -0.097 (171), 2024 +0.006 (170), 2025 -0.070 (176), 2026 -0.149 (134).

Sensibilidad (R neto medio y t): colchón 0 % -0.043 (t -1.69), colchón 50 % -0.022 (t -0.91), objetivo 1,5:1 -0.024 (t -0.83), objetivo 2:1 -0.034 (t -1.06).

### ORB 11:30–11:45

Rotura con cuerpo desde las 11:45 hasta las 17:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.034 R; ancho medio del ORB 0.28 %; cómo terminan: objetivo 601, stop 596, por tiempo 192.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1389 | 49.4 % | -0.033 | -45.2 | 0.93 | -63.6 | -1.29 |
| Sin costes | 1389 | 49.8 % | +0.002 | +2.1 | 1.00 | -36.5 | +0.06 |
| Long | 773 | 50.7 % | -0.015 | -11.8 | 0.97 | -19.8 | -0.45 |
| Short | 616 | 47.7 % | -0.054 | -33.5 | 0.89 | -58.9 | -1.43 |
| 1.ª mitad | 695 | 50.6 % | -0.010 | -7.0 | 0.98 | -27.9 | -0.28 |
| 2.ª mitad | 694 | 48.1 % | -0.055 | -38.2 | 0.89 | -43.4 | -1.54 |

Por año (R neto medio y operaciones): 2018 +0.008 (51), 2019 -0.048 (167), 2020 +0.076 (162), 2021 -0.053 (179), 2022 -0.063 (172), 2023 -0.109 (163), 2024 +0.011 (176), 2025 +0.001 (183), 2026 -0.101 (136).

Sensibilidad (R neto medio y t): colchón 0 % -0.059 (t -2.26), colchón 50 % -0.014 (t -0.56), objetivo 1,5:1 -0.014 (t -0.46), objetivo 2:1 -0.004 (t -0.12).

### ORB 11:45–12:00

Rotura con cuerpo desde las 12:00 hasta las 18:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.036 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 589, stop 587, por tiempo 188.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1364 | 50.4 % | -0.032 | -43.2 | 0.93 | -63.4 | -1.24 |
| Sin costes | 1364 | 50.4 % | +0.004 | +5.9 | 1.01 | -40.7 | +0.17 |
| Long | 747 | 53.3 % | +0.012 | +9.0 | 1.03 | -23.4 | +0.35 |
| Short | 617 | 46.8 % | -0.085 | -52.1 | 0.83 | -67.7 | -2.23 |
| 1.ª mitad | 682 | 47.8 % | -0.074 | -50.4 | 0.85 | -63.4 | -2.02 |
| 2.ª mitad | 682 | 52.9 % | +0.011 | +7.2 | 1.02 | -20.3 | +0.30 |

Por año (R neto medio y operaciones): 2018 +0.045 (50), 2019 -0.216 (161), 2020 -0.016 (169), 2021 -0.087 (167), 2022 -0.008 (169), 2023 +0.014 (156), 2024 +0.076 (178), 2025 +0.039 (180), 2026 -0.111 (134).

Sensibilidad (R neto medio y t): colchón 0 % -0.007 (t -0.27), colchón 50 % -0.030 (t -1.22), objetivo 1,5:1 -0.007 (t -0.23), objetivo 2:1 +0.016 (t +0.49).

