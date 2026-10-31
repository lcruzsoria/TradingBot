# ORB de 45 min de las 04:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 04:00–04:45 | 1655 | 49.7 | -0.028 | -1.18 | +0.009 | 0.037 | no |
| 04:15–05:00 | 1559 | 48.9 | -0.062 | -2.50 | -0.021 | 0.041 | no |
| 04:30–05:15 | 1548 | 49.6 | -0.049 | -1.97 | -0.006 | 0.043 | no |
| 04:45–05:30 | 1509 | 48.6 | -0.070 | -2.76 | -0.025 | 0.045 | no |

## Detalle

### ORB 04:00–04:45

Rotura con cuerpo desde las 04:45 hasta las 10:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.037 R; ancho medio del ORB 0.29 %; cómo terminan: objetivo 775, stop 753, por tiempo 127.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1655 | 49.7 % | -0.028 | -46.6 | 0.94 | -95.7 | -1.18 |
| Sin costes | 1655 | 50.0 % | +0.009 | +14.5 | 1.02 | -61.3 | +0.37 |
| Long | 915 | 50.2 % | -0.025 | -22.7 | 0.95 | -60.0 | -0.77 |
| Short | 740 | 49.2 % | -0.032 | -23.9 | 0.93 | -50.9 | -0.91 |
| 1.ª mitad | 828 | 47.5 % | -0.074 | -61.0 | 0.86 | -71.4 | -2.19 |
| 2.ª mitad | 827 | 52.0 % | +0.017 | +14.4 | 1.04 | -28.6 | +0.51 |

Por año (R neto medio y operaciones): 2018 +0.123 (57), 2019 -0.115 (206), 2020 -0.188 (199), 2021 -0.007 (209), 2022 -0.053 (213), 2023 -0.080 (200), 2024 +0.075 (217), 2025 +0.053 (204), 2026 +0.061 (150).

Sensibilidad (R neto medio y t): colchón 0 % -0.042 (t -1.75), colchón 50 % -0.012 (t -0.52), objetivo 1,5:1 -0.024 (t -0.83), objetivo 2:1 -0.015 (t -0.46).

### ORB 04:15–05:00

Rotura con cuerpo desde las 05:00 hasta las 11:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.041 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 731, stop 762, por tiempo 66.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1559 | 48.9 % | -0.062 | -96.9 | 0.88 | -118.8 | -2.50 |
| Sin costes | 1559 | 49.0 % | -0.021 | -32.4 | 0.96 | -83.9 | -0.84 |
| Long | 883 | 48.6 % | -0.075 | -66.4 | 0.86 | -84.4 | -2.27 |
| Short | 676 | 49.3 % | -0.045 | -30.5 | 0.91 | -48.4 | -1.20 |
| 1.ª mitad | 780 | 47.1 % | -0.102 | -79.4 | 0.81 | -94.3 | -2.90 |
| 2.ª mitad | 779 | 50.7 % | -0.022 | -17.5 | 0.95 | -33.3 | -0.64 |

Por año (R neto medio y operaciones): 2018 +0.146 (49), 2019 -0.107 (192), 2020 -0.184 (195), 2021 -0.103 (193), 2022 -0.113 (197), 2023 -0.005 (185), 2024 +0.086 (207), 2025 -0.122 (192), 2026 +0.005 (149).

Sensibilidad (R neto medio y t): colchón 0 % -0.069 (t -2.76), colchón 50 % -0.062 (t -2.52), objetivo 1,5:1 -0.075 (t -2.54), objetivo 2:1 -0.073 (t -2.20).

### ORB 04:30–05:15

Rotura con cuerpo desde las 05:15 hasta las 11:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.043 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 741, stop 751, por tiempo 56.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1548 | 49.6 % | -0.049 | -76.3 | 0.90 | -109.1 | -1.97 |
| Sin costes | 1548 | 49.8 % | -0.006 | -9.6 | 0.99 | -56.1 | -0.25 |
| Long | 899 | 48.3 % | -0.085 | -76.1 | 0.84 | -96.3 | -2.57 |
| Short | 649 | 51.5 % | -0.000 | -0.2 | 1.00 | -21.8 | -0.01 |
| 1.ª mitad | 774 | 49.1 % | -0.061 | -47.5 | 0.88 | -66.2 | -1.74 |
| 2.ª mitad | 774 | 50.1 % | -0.037 | -28.8 | 0.93 | -46.7 | -1.05 |

Por año (R neto medio y operaciones): 2018 +0.219 (50), 2019 -0.044 (196), 2020 -0.127 (192), 2021 -0.073 (193), 2022 -0.074 (184), 2023 -0.071 (192), 2024 -0.027 (200), 2025 -0.048 (186), 2026 +0.009 (155).

Sensibilidad (R neto medio y t): colchón 0 % -0.060 (t -2.37), colchón 50 % -0.041 (t -1.64), objetivo 1,5:1 -0.070 (t -2.34), objetivo 2:1 -0.085 (t -2.54).

### ORB 04:45–05:30

Rotura con cuerpo desde las 05:30 hasta las 11:30; a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.045 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 708, stop 747, por tiempo 54.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1509 | 48.6 % | -0.070 | -105.8 | 0.87 | -133.7 | -2.76 |
| Sin costes | 1509 | 48.7 % | -0.025 | -37.8 | 0.95 | -77.4 | -0.99 |
| Long | 882 | 47.6 % | -0.097 | -85.7 | 0.82 | -103.5 | -2.92 |
| Short | 627 | 49.9 % | -0.032 | -20.1 | 0.94 | -38.3 | -0.82 |
| 1.ª mitad | 755 | 48.2 % | -0.078 | -58.7 | 0.85 | -79.1 | -2.18 |
| 2.ª mitad | 754 | 48.9 % | -0.062 | -47.0 | 0.88 | -65.8 | -1.73 |

Por año (R neto medio y operaciones): 2018 +0.136 (52), 2019 -0.118 (196), 2020 -0.172 (180), 2021 -0.027 (188), 2022 -0.047 (180), 2023 -0.155 (188), 2024 -0.011 (188), 2025 -0.072 (181), 2026 -0.007 (156).

Sensibilidad (R neto medio y t): colchón 0 % -0.079 (t -3.11), colchón 50 % -0.045 (t -1.81), objetivo 1,5:1 -0.070 (t -2.29), objetivo 2:1 -0.086 (t -2.51).

