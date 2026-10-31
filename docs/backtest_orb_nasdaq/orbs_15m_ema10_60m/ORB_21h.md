# ORB de 15 min de las 21:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 21:00–21:15 | 1303 | 51.0 | -0.050 | -1.87 | +0.033 | 0.083 | no |
| 21:15–21:30 | 1273 | 51.3 | -0.046 | -1.67 | +0.040 | 0.085 | no |
| 21:30–21:45 | 1293 | 52.5 | -0.024 | -0.89 | +0.057 | 0.081 | no |
| 21:45–22:00 | 1278 | 50.7 | -0.071 | -2.57 | +0.021 | 0.092 | no |

## Detalle

### ORB 21:00–21:15

Rotura con cuerpo desde las 21:15 hasta las 03:15 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.083 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 627, stop 580, por tiempo 96.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1303 | 51.0 % | -0.050 | -65.5 | 0.90 | -81.8 | -1.87 |
| Sin costes | 1303 | 51.3 % | +0.033 | +42.9 | 1.07 | -15.8 | +1.23 |
| Long | 743 | 50.3 % | -0.071 | -52.6 | 0.86 | -66.8 | -1.98 |
| Short | 560 | 52.0 % | -0.023 | -13.0 | 0.95 | -24.3 | -0.57 |
| 1.ª mitad | 652 | 50.5 % | -0.057 | -36.9 | 0.89 | -38.3 | -1.49 |
| 2.ª mitad | 651 | 51.6 % | -0.044 | -28.7 | 0.91 | -48.0 | -1.15 |

Por año (R neto medio y operaciones): 2018 -0.087 (50), 2019 -0.047 (154), 2020 +0.003 (162), 2021 -0.062 (153), 2022 -0.114 (144), 2023 -0.130 (158), 2024 -0.010 (170), 2025 -0.079 (160), 2026 +0.041 (152).

Sensibilidad (R neto medio y t): colchón 0 % -0.071 (t -2.61), colchón 50 % -0.030 (t -1.14), objetivo 1,5:1 -0.012 (t -0.37), objetivo 2:1 -0.009 (t -0.24).

### ORB 21:15–21:30

Rotura con cuerpo desde las 21:30 hasta las 03:30 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.085 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 627, stop 572, por tiempo 74.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1273 | 51.3 % | -0.046 | -58.2 | 0.91 | -75.1 | -1.67 |
| Sin costes | 1273 | 51.5 % | +0.040 | +50.6 | 1.09 | -26.0 | +1.45 |
| Long | 745 | 51.8 % | -0.044 | -32.6 | 0.91 | -44.5 | -1.22 |
| Short | 528 | 50.6 % | -0.048 | -25.6 | 0.90 | -56.1 | -1.14 |
| 1.ª mitad | 637 | 49.6 % | -0.076 | -48.7 | 0.85 | -51.1 | -1.99 |
| 2.ª mitad | 636 | 53.0 % | -0.015 | -9.5 | 0.97 | -31.8 | -0.38 |

Por año (R neto medio y operaciones): 2018 -0.229 (45), 2019 -0.066 (155), 2020 -0.026 (161), 2021 -0.065 (157), 2022 -0.097 (151), 2023 -0.108 (156), 2024 +0.032 (153), 2025 -0.031 (156), 2026 +0.058 (139).

Sensibilidad (R neto medio y t): colchón 0 % -0.083 (t -3.01), colchón 50 % -0.026 (t -0.98), objetivo 1,5:1 +0.005 (t +0.16), objetivo 2:1 +0.039 (t +1.04).

### ORB 21:30–21:45

Rotura con cuerpo desde las 21:45 hasta las 03:45 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.081 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 637, stop 559, por tiempo 97.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1293 | 52.5 % | -0.024 | -30.9 | 0.95 | -51.7 | -0.89 |
| Sin costes | 1293 | 52.7 % | +0.057 | +73.5 | 1.13 | -17.8 | +2.12 |
| Long | 746 | 54.4 % | +0.009 | +6.3 | 1.02 | -36.3 | +0.24 |
| Short | 547 | 49.9 % | -0.068 | -37.2 | 0.87 | -62.5 | -1.62 |
| 1.ª mitad | 647 | 52.4 % | -0.019 | -12.1 | 0.96 | -24.8 | -0.50 |
| 2.ª mitad | 646 | 52.6 % | -0.029 | -18.7 | 0.94 | -44.5 | -0.75 |

Por año (R neto medio y operaciones): 2018 +0.007 (54), 2019 -0.087 (170), 2020 +0.053 (165), 2021 +0.005 (156), 2022 -0.044 (138), 2023 -0.089 (162), 2024 -0.009 (150), 2025 -0.118 (160), 2026 +0.105 (138).

Sensibilidad (R neto medio y t): colchón 0 % -0.063 (t -2.30), colchón 50 % -0.023 (t -0.88), objetivo 1,5:1 -0.009 (t -0.27), objetivo 2:1 +0.012 (t +0.35).

### ORB 21:45–22:00

Rotura con cuerpo desde las 22:00 hasta las 04:00 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.092 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 629, stop 598, por tiempo 51.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1278 | 50.7 % | -0.071 | -90.5 | 0.86 | -123.7 | -2.57 |
| Sin costes | 1278 | 50.9 % | +0.021 | +26.5 | 1.04 | -68.2 | +0.75 |
| Long | 739 | 52.1 % | -0.048 | -35.6 | 0.90 | -48.9 | -1.33 |
| Short | 539 | 48.8 % | -0.102 | -54.9 | 0.81 | -84.3 | -2.39 |
| 1.ª mitad | 639 | 47.9 % | -0.114 | -72.8 | 0.79 | -85.9 | -2.95 |
| 2.ª mitad | 639 | 53.5 % | -0.028 | -17.7 | 0.95 | -39.5 | -0.70 |

Por año (R neto medio y operaciones): 2018 +0.006 (57), 2019 -0.040 (163), 2020 -0.126 (163), 2021 -0.176 (147), 2022 -0.236 (149), 2023 -0.125 (152), 2024 +0.027 (156), 2025 -0.037 (152), 2026 +0.127 (139).

Sensibilidad (R neto medio y t): colchón 0 % -0.108 (t -3.88), colchón 50 % -0.036 (t -1.34), objetivo 1,5:1 -0.029 (t -0.87), objetivo 2:1 +0.003 (t +0.08).

