# ORB de 15 min de las 03:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 03:00–03:15 | 1566 | 47.4 | -0.091 | -3.76 | -0.040 | 0.051 | no |
| 03:15–03:30 | 1455 | 49.7 | -0.057 | -2.26 | +0.000 | 0.057 | no |
| 03:30–03:45 | 1400 | 48.9 | -0.086 | -3.26 | -0.025 | 0.061 | no |
| 03:45–04:00 | 1402 | 50.6 | -0.050 | -1.90 | +0.012 | 0.063 | no |

## Detalle

### ORB 03:00–03:15

Rotura con cuerpo desde las 03:15 hasta las 09:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.051 R; ancho medio del ORB 0.20 %; cómo terminan: objetivo 671, stop 726, por tiempo 169.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1566 | 47.4 % | -0.091 | -141.9 | 0.82 | -151.6 | -3.76 |
| Sin costes | 1566 | 47.7 % | -0.040 | -62.0 | 0.92 | -83.1 | -1.64 |
| Long | 888 | 48.3 % | -0.080 | -70.9 | 0.84 | -74.2 | -2.50 |
| Short | 678 | 46.2 % | -0.105 | -71.0 | 0.80 | -82.0 | -2.85 |
| 1.ª mitad | 783 | 49.6 % | -0.051 | -40.0 | 0.89 | -44.4 | -1.52 |
| 2.ª mitad | 783 | 45.2 % | -0.130 | -101.9 | 0.76 | -107.2 | -3.77 |

Por año (R neto medio y operaciones): 2018 -0.001 (53), 2019 -0.145 (198), 2020 +0.021 (189), 2021 -0.015 (201), 2022 -0.177 (205), 2023 -0.068 (196), 2024 -0.206 (191), 2025 -0.109 (176), 2026 -0.039 (157).

Sensibilidad (R neto medio y t): colchón 0 % -0.089 (t -3.65), colchón 50 % -0.081 (t -3.49), objetivo 1,5:1 -0.084 (t -2.97), objetivo 2:1 -0.092 (t -2.99).

### ORB 03:15–03:30

Rotura con cuerpo desde las 03:30 hasta las 09:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.057 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 669, stop 664, por tiempo 122.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1455 | 49.7 % | -0.057 | -83.1 | 0.89 | -102.7 | -2.26 |
| Sin costes | 1455 | 49.9 % | +0.000 | +0.0 | 1.00 | -61.8 | +0.00 |
| Long | 808 | 49.6 % | -0.058 | -46.6 | 0.88 | -56.9 | -1.70 |
| Short | 647 | 49.8 % | -0.057 | -36.6 | 0.89 | -54.5 | -1.49 |
| 1.ª mitad | 728 | 51.1 % | -0.032 | -23.2 | 0.93 | -30.5 | -0.90 |
| 2.ª mitad | 727 | 48.3 % | -0.082 | -59.9 | 0.84 | -76.9 | -2.27 |

Por año (R neto medio y operaciones): 2018 -0.083 (46), 2019 -0.080 (178), 2020 +0.034 (173), 2021 +0.039 (177), 2022 -0.135 (196), 2023 -0.146 (186), 2024 -0.093 (169), 2025 -0.102 (185), 2026 +0.071 (145).

Sensibilidad (R neto medio y t): colchón 0 % -0.054 (t -2.12), colchón 50 % -0.053 (t -2.16), objetivo 1,5:1 -0.052 (t -1.74), objetivo 2:1 -0.068 (t -2.05).

### ORB 03:30–03:45

Rotura con cuerpo desde las 03:45 hasta las 09:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.061 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 658, stop 698, por tiempo 44.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1400 | 48.9 % | -0.086 | -120.4 | 0.84 | -137.5 | -3.26 |
| Sin costes | 1400 | 49.0 % | -0.025 | -35.1 | 0.95 | -66.5 | -0.95 |
| Long | 824 | 49.0 % | -0.086 | -70.6 | 0.84 | -79.6 | -2.49 |
| Short | 576 | 48.8 % | -0.086 | -49.8 | 0.84 | -68.0 | -2.10 |
| 1.ª mitad | 700 | 49.3 % | -0.079 | -55.3 | 0.85 | -78.6 | -2.12 |
| 2.ª mitad | 700 | 48.6 % | -0.093 | -65.1 | 0.83 | -76.1 | -2.48 |

Por año (R neto medio y operaciones): 2018 +0.000 (42), 2019 -0.229 (182), 2020 -0.098 (181), 2021 -0.009 (155), 2022 -0.017 (176), 2023 -0.124 (171), 2024 -0.122 (170), 2025 -0.104 (176), 2026 +0.026 (147).

Sensibilidad (R neto medio y t): colchón 0 % -0.094 (t -3.54), colchón 50 % -0.072 (t -2.78), objetivo 1,5:1 -0.087 (t -2.75), objetivo 2:1 -0.096 (t -2.68).

### ORB 03:45–04:00

Rotura con cuerpo desde las 04:00 hasta las 10:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.063 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 697, stop 680, por tiempo 25.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1402 | 50.6 % | -0.050 | -70.7 | 0.90 | -77.0 | -1.90 |
| Sin costes | 1402 | 50.6 % | +0.012 | +17.3 | 1.03 | -44.7 | +0.47 |
| Long | 810 | 51.7 % | -0.034 | -27.8 | 0.93 | -56.0 | -0.99 |
| Short | 592 | 49.0 % | -0.072 | -42.9 | 0.86 | -45.2 | -1.76 |
| 1.ª mitad | 701 | 52.1 % | -0.025 | -17.8 | 0.95 | -40.5 | -0.68 |
| 2.ª mitad | 701 | 49.1 % | -0.075 | -52.9 | 0.86 | -77.0 | -2.00 |

Por año (R neto medio y operaciones): 2018 -0.214 (47), 2019 -0.105 (178), 2020 -0.029 (158), 2021 +0.091 (163), 2022 +0.056 (181), 2023 -0.041 (165), 2024 -0.043 (164), 2025 -0.146 (176), 2026 -0.133 (170).

Sensibilidad (R neto medio y t): colchón 0 % -0.049 (t -1.84), colchón 50 % -0.060 (t -2.27), objetivo 1,5:1 -0.057 (t -1.77), objetivo 2:1 -0.069 (t -1.90).

