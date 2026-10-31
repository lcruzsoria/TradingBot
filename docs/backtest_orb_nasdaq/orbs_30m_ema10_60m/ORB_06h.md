# ORB de 30 min de las 06:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 06:00–06:30 | 1448 | 49.4 | -0.068 | -2.59 | -0.013 | 0.055 | no |
| 06:15–06:45 | 1432 | 51.3 | -0.033 | -1.24 | +0.023 | 0.055 | no |
| 06:30–07:00 | 1465 | 52.5 | -0.005 | -0.20 | +0.048 | 0.053 | no |
| 06:45–07:15 | 1564 | 50.3 | -0.039 | -1.56 | +0.009 | 0.048 | no |

## Detalle

### ORB 06:00–06:30

Rotura con cuerpo desde las 06:30 hasta las 12:30; a esa hora se cierra. ORB completos: 2095; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.055 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 703, stop 725, por tiempo 20.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1448 | 49.4 % | -0.068 | -98.2 | 0.87 | -104.1 | -2.59 |
| Sin costes | 1448 | 49.5 % | -0.013 | -18.1 | 0.98 | -41.4 | -0.48 |
| Long | 825 | 50.7 % | -0.047 | -38.9 | 0.91 | -44.6 | -1.36 |
| Short | 623 | 47.8 % | -0.095 | -59.3 | 0.83 | -64.3 | -2.39 |
| 1.ª mitad | 724 | 50.6 % | -0.049 | -35.2 | 0.91 | -50.4 | -1.31 |
| 2.ª mitad | 724 | 48.3 % | -0.087 | -63.0 | 0.84 | -67.6 | -2.35 |

Por año (R neto medio y operaciones): 2018 -0.153 (51), 2019 -0.135 (169), 2020 +0.032 (161), 2021 -0.098 (183), 2022 +0.052 (185), 2023 -0.180 (193), 2024 -0.040 (181), 2025 -0.082 (181), 2026 -0.054 (144).

Sensibilidad (R neto medio y t): colchón 0 % -0.092 (t -3.49), colchón 50 % -0.054 (t -2.08), objetivo 1,5:1 -0.028 (t -0.87), objetivo 2:1 -0.026 (t -0.72).

### ORB 06:15–06:45

Rotura con cuerpo desde las 06:45 hasta las 12:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.055 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 720, stop 693, por tiempo 19.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1432 | 51.3 % | -0.033 | -46.7 | 0.94 | -69.2 | -1.24 |
| Sin costes | 1432 | 51.3 % | +0.023 | +32.6 | 1.05 | -29.8 | +0.87 |
| Long | 831 | 52.3 % | -0.017 | -13.8 | 0.97 | -33.3 | -0.48 |
| Short | 601 | 49.9 % | -0.055 | -32.9 | 0.90 | -45.0 | -1.35 |
| 1.ª mitad | 716 | 51.0 % | -0.041 | -29.5 | 0.92 | -40.8 | -1.10 |
| 2.ª mitad | 716 | 51.7 % | -0.024 | -17.2 | 0.95 | -35.9 | -0.65 |

Por año (R neto medio y operaciones): 2018 +0.045 (51), 2019 -0.097 (167), 2020 -0.092 (163), 2021 -0.020 (189), 2022 +0.028 (175), 2023 -0.076 (178), 2024 -0.012 (181), 2025 -0.061 (172), 2026 +0.048 (156).

Sensibilidad (R neto medio y t): colchón 0 % -0.060 (t -2.28), colchón 50 % -0.027 (t -1.03), objetivo 1,5:1 -0.002 (t -0.05), objetivo 2:1 -0.031 (t -0.84).

### ORB 06:30–07:00

Rotura con cuerpo desde las 07:00 hasta las 13:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.053 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 755, stop 686, por tiempo 24.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1465 | 52.5 % | -0.005 | -7.4 | 0.99 | -32.1 | -0.20 |
| Sin costes | 1465 | 52.5 % | +0.048 | +69.9 | 1.10 | -14.9 | +1.84 |
| Long | 875 | 51.5 % | -0.031 | -26.7 | 0.94 | -35.9 | -0.91 |
| Short | 590 | 53.9 % | +0.033 | +19.3 | 1.07 | -17.2 | +0.80 |
| 1.ª mitad | 733 | 52.5 % | -0.004 | -2.8 | 0.99 | -21.1 | -0.10 |
| 2.ª mitad | 732 | 52.5 % | -0.006 | -4.7 | 0.99 | -27.9 | -0.17 |

Por año (R neto medio y operaciones): 2018 -0.019 (54), 2019 -0.021 (160), 2020 -0.012 (168), 2021 -0.001 (185), 2022 +0.021 (170), 2023 -0.046 (183), 2024 -0.022 (186), 2025 +0.012 (194), 2026 +0.034 (165).

Sensibilidad (R neto medio y t): colchón 0 % -0.027 (t -1.05), colchón 50 % +0.007 (t +0.27), objetivo 1,5:1 +0.041 (t +1.29), objetivo 2:1 +0.017 (t +0.47).

### ORB 06:45–07:15

Rotura con cuerpo desde las 07:15 hasta las 13:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.048 R; ancho medio del ORB 0.21 %; cómo terminan: objetivo 775, stop 763, por tiempo 26.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1564 | 50.3 % | -0.039 | -61.4 | 0.92 | -86.7 | -1.56 |
| Sin costes | 1564 | 50.3 % | +0.009 | +13.5 | 1.02 | -30.2 | +0.34 |
| Long | 896 | 49.4 % | -0.065 | -57.8 | 0.88 | -69.4 | -1.94 |
| Short | 668 | 51.5 % | -0.005 | -3.6 | 0.99 | -32.8 | -0.14 |
| 1.ª mitad | 782 | 48.8 % | -0.069 | -53.6 | 0.87 | -65.3 | -1.93 |
| 2.ª mitad | 782 | 51.8 % | -0.010 | -7.8 | 0.98 | -37.0 | -0.28 |

Por año (R neto medio y operaciones): 2018 -0.070 (53), 2019 -0.083 (183), 2020 -0.113 (191), 2021 -0.020 (193), 2022 -0.013 (182), 2023 -0.090 (199), 2024 -0.036 (199), 2025 +0.028 (197), 2026 +0.027 (167).

Sensibilidad (R neto medio y t): colchón 0 % -0.065 (t -2.58), colchón 50 % -0.035 (t -1.40), objetivo 1,5:1 -0.019 (t -0.63), objetivo 2:1 -0.018 (t -0.52).

