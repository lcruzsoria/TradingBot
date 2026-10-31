# ORB de 45 min de las 18:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 18:00–18:45 | 1329 | 50.0 | -0.022 | -0.98 | +0.025 | 0.047 | no |
| 18:15–19:00 | 1320 | 50.7 | -0.020 | -0.83 | +0.041 | 0.061 | no |
| 18:30–19:15 | 1335 | 49.5 | -0.056 | -2.28 | +0.004 | 0.060 | no |
| 18:45–19:30 | 1330 | 49.3 | -0.061 | -2.50 | -0.002 | 0.059 | no |

## Detalle

### ORB 18:00–18:45

Rotura con cuerpo desde las 18:45 hasta las 00:45 (día siguiente); a esa hora se cierra. ORB completos: 2092; con rotura: 2025.

**No pasa los criterios**. Coste medio 0.047 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 422, stop 397, por tiempo 510.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1329 | 50.0 % | -0.022 | -29.4 | 0.94 | -33.4 | -0.98 |
| Sin costes | 1329 | 51.5 % | +0.025 | +32.8 | 1.07 | -19.7 | +1.10 |
| Long | 765 | 52.4 % | -0.003 | -2.6 | 0.99 | -25.9 | -0.12 |
| Short | 564 | 46.8 % | -0.047 | -26.8 | 0.88 | -30.4 | -1.35 |
| 1.ª mitad | 665 | 49.5 % | -0.035 | -23.3 | 0.91 | -23.3 | -1.08 |
| 2.ª mitad | 664 | 50.6 % | -0.009 | -6.1 | 0.97 | -25.4 | -0.29 |

Por año (R neto medio y operaciones): 2018 -0.334 (44), 2019 -0.013 (162), 2020 +0.031 (164), 2021 +0.018 (159), 2022 -0.116 (149), 2023 -0.002 (144), 2024 +0.080 (164), 2025 -0.012 (181), 2026 -0.085 (162).

Sensibilidad (R neto medio y t): colchón 0 % -0.032 (t -1.34), colchón 50 % -0.019 (t -0.91), objetivo 1,5:1 -0.006 (t -0.25), objetivo 2:1 -0.016 (t -0.61).

### ORB 18:15–19:00

Rotura con cuerpo desde las 19:00 hasta las 01:00 (día siguiente); a esa hora se cierra. ORB completos: 2095; con rotura: 2073.

**No pasa los criterios**. Coste medio 0.061 R; ancho medio del ORB 0.20 %; cómo terminan: objetivo 524, stop 465, por tiempo 331.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1320 | 50.7 % | -0.020 | -27.0 | 0.95 | -34.8 | -0.83 |
| Sin costes | 1320 | 51.7 % | +0.041 | +53.5 | 1.10 | -27.9 | +1.65 |
| Long | 748 | 51.3 % | -0.020 | -15.2 | 0.95 | -29.8 | -0.62 |
| Short | 572 | 49.8 % | -0.021 | -11.8 | 0.95 | -25.0 | -0.55 |
| 1.ª mitad | 660 | 51.4 % | -0.026 | -17.4 | 0.94 | -20.2 | -0.75 |
| 2.ª mitad | 660 | 50.0 % | -0.014 | -9.6 | 0.97 | -34.8 | -0.42 |

Por año (R neto medio y operaciones): 2018 -0.221 (44), 2019 +0.001 (166), 2020 -0.003 (168), 2021 -0.020 (160), 2022 -0.053 (150), 2023 +0.012 (141), 2024 +0.109 (160), 2025 -0.035 (168), 2026 -0.116 (163).

Sensibilidad (R neto medio y t): colchón 0 % -0.021 (t -0.82), colchón 50 % -0.020 (t -0.87), objetivo 1,5:1 -0.021 (t -0.75), objetivo 2:1 -0.017 (t -0.57).

### ORB 18:30–19:15

Rotura con cuerpo desde las 19:15 hasta las 01:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2081.

**No pasa los criterios**. Coste medio 0.060 R; ancho medio del ORB 0.20 %; cómo terminan: objetivo 495, stop 497, por tiempo 343.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1335 | 49.5 % | -0.056 | -74.2 | 0.87 | -78.0 | -2.28 |
| Sin costes | 1335 | 50.6 % | +0.004 | +5.3 | 1.01 | -35.3 | +0.16 |
| Long | 753 | 51.0 % | -0.048 | -35.8 | 0.89 | -50.0 | -1.48 |
| Short | 582 | 47.6 % | -0.066 | -38.4 | 0.85 | -44.4 | -1.78 |
| 1.ª mitad | 668 | 49.6 % | -0.057 | -37.8 | 0.87 | -40.6 | -1.62 |
| 2.ª mitad | 667 | 49.5 % | -0.055 | -36.4 | 0.87 | -39.2 | -1.61 |

Por año (R neto medio y operaciones): 2018 -0.088 (41), 2019 -0.096 (173), 2020 +0.039 (167), 2021 -0.080 (168), 2022 -0.121 (150), 2023 -0.122 (138), 2024 +0.033 (157), 2025 -0.018 (181), 2026 -0.088 (160).

Sensibilidad (R neto medio y t): colchón 0 % -0.061 (t -2.41), colchón 50 % -0.041 (t -1.79), objetivo 1,5:1 -0.046 (t -1.63), objetivo 2:1 -0.052 (t -1.74).

### ORB 18:45–19:30

Rotura con cuerpo desde las 19:30 hasta las 01:30 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2076.

**No pasa los criterios**. Coste medio 0.059 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 493, stop 500, por tiempo 337.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1330 | 49.3 % | -0.061 | -81.0 | 0.86 | -86.3 | -2.50 |
| Sin costes | 1330 | 50.2 % | -0.002 | -2.0 | 1.00 | -35.7 | -0.06 |
| Long | 745 | 52.6 % | -0.009 | -6.5 | 0.98 | -23.2 | -0.27 |
| Short | 585 | 45.1 % | -0.127 | -74.5 | 0.74 | -79.8 | -3.43 |
| 1.ª mitad | 665 | 49.0 % | -0.061 | -40.7 | 0.87 | -50.8 | -1.73 |
| 2.ª mitad | 665 | 49.6 % | -0.061 | -40.3 | 0.86 | -41.2 | -1.80 |

Por año (R neto medio y operaciones): 2018 +0.031 (44), 2019 -0.094 (172), 2020 +0.005 (161), 2021 -0.070 (168), 2022 -0.165 (152), 2023 -0.139 (144), 2024 -0.029 (150), 2025 +0.018 (177), 2026 -0.055 (162).

Sensibilidad (R neto medio y t): colchón 0 % -0.069 (t -2.73), colchón 50 % -0.048 (t -2.06), objetivo 1,5:1 -0.046 (t -1.64), objetivo 2:1 -0.051 (t -1.68).

