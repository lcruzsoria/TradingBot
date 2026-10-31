# ORB de 15 min de las 20:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 20:00–20:15 | 1304 | 51.8 | -0.009 | -0.37 | +0.057 | 0.066 | no |
| 20:15–20:30 | 1268 | 51.3 | -0.048 | -1.81 | +0.028 | 0.076 | no |
| 20:30–20:45 | 1276 | 51.7 | -0.027 | -1.02 | +0.052 | 0.079 | no |
| 20:45–21:00 | 1250 | 50.9 | -0.061 | -2.24 | +0.025 | 0.086 | no |

## Detalle

### ORB 20:00–20:15

Rotura con cuerpo desde las 20:15 hasta las 02:15 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.066 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 575, stop 488, por tiempo 241.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1304 | 51.8 % | -0.009 | -12.2 | 0.98 | -47.6 | -0.37 |
| Sin costes | 1304 | 52.1 % | +0.057 | +74.5 | 1.14 | -20.6 | +2.24 |
| Long | 745 | 52.8 % | +0.007 | +5.3 | 1.02 | -32.0 | +0.21 |
| Short | 559 | 50.4 % | -0.031 | -17.4 | 0.93 | -35.7 | -0.79 |
| 1.ª mitad | 652 | 52.6 % | +0.013 | +8.7 | 1.03 | -16.7 | +0.37 |
| 2.ª mitad | 652 | 50.9 % | -0.032 | -20.8 | 0.93 | -40.9 | -0.88 |

Por año (R neto medio y operaciones): 2018 +0.219 (41), 2019 -0.031 (169), 2020 -0.007 (146), 2021 +0.015 (159), 2022 -0.029 (159), 2023 -0.117 (163), 2024 -0.002 (157), 2025 +0.028 (162), 2026 +0.016 (148).

Sensibilidad (R neto medio y t): colchón 0 % -0.008 (t -0.30), colchón 50 % -0.014 (t -0.59), objetivo 1,5:1 -0.011 (t -0.37), objetivo 2:1 +0.000 (t +0.01).

### ORB 20:15–20:30

Rotura con cuerpo desde las 20:30 hasta las 02:30 (día siguiente); a esa hora se cierra. ORB completos: 2099; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.076 R; ancho medio del ORB 0.14 %; cómo terminan: objetivo 572, stop 537, por tiempo 159.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1268 | 51.3 % | -0.048 | -61.3 | 0.90 | -67.8 | -1.81 |
| Sin costes | 1268 | 51.5 % | +0.028 | +35.1 | 1.06 | -25.6 | +1.04 |
| Long | 711 | 52.6 % | -0.040 | -28.4 | 0.92 | -38.8 | -1.13 |
| Short | 557 | 49.6 % | -0.059 | -32.9 | 0.88 | -42.6 | -1.45 |
| 1.ª mitad | 634 | 49.4 % | -0.080 | -50.5 | 0.84 | -58.0 | -2.11 |
| 2.ª mitad | 634 | 53.2 % | -0.017 | -10.8 | 0.96 | -21.8 | -0.45 |

Por año (R neto medio y operaciones): 2018 -0.180 (31), 2019 -0.198 (161), 2020 -0.004 (154), 2021 -0.061 (161), 2022 -0.020 (155), 2023 -0.048 (156), 2024 +0.010 (160), 2025 -0.015 (144), 2026 -0.014 (146).

Sensibilidad (R neto medio y t): colchón 0 % -0.068 (t -2.51), colchón 50 % -0.019 (t -0.76), objetivo 1,5:1 -0.032 (t -1.02), objetivo 2:1 -0.042 (t -1.21).

### ORB 20:30–20:45

Rotura con cuerpo desde las 20:45 hasta las 02:45 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.079 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 588, stop 514, por tiempo 174.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1276 | 51.7 % | -0.027 | -34.4 | 0.94 | -72.8 | -1.02 |
| Sin costes | 1276 | 52.0 % | +0.052 | +66.0 | 1.12 | -24.0 | +1.97 |
| Long | 742 | 53.8 % | +0.005 | +3.7 | 1.01 | -45.4 | +0.15 |
| Short | 534 | 48.9 % | -0.071 | -38.2 | 0.85 | -53.3 | -1.76 |
| 1.ª mitad | 638 | 49.1 % | -0.076 | -48.5 | 0.84 | -50.9 | -2.05 |
| 2.ª mitad | 638 | 54.4 % | +0.022 | +14.1 | 1.05 | -29.7 | +0.59 |

Por año (R neto medio y operaciones): 2018 -0.240 (46), 2019 -0.141 (159), 2020 +0.016 (150), 2021 -0.027 (160), 2022 -0.161 (159), 2023 -0.024 (158), 2024 +0.071 (153), 2025 -0.035 (154), 2026 +0.183 (137).

Sensibilidad (R neto medio y t): colchón 0 % -0.057 (t -2.10), colchón 50 % -0.034 (t -1.34), objetivo 1,5:1 -0.041 (t -1.32), objetivo 2:1 -0.045 (t -1.30).

### ORB 20:45–21:00

Rotura con cuerpo desde las 21:00 hasta las 03:00 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.086 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 590, stop 557, por tiempo 103.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1250 | 50.9 % | -0.061 | -76.7 | 0.88 | -88.8 | -2.24 |
| Sin costes | 1250 | 51.0 % | +0.025 | +30.8 | 1.05 | -24.8 | +0.90 |
| Long | 737 | 50.6 % | -0.084 | -61.7 | 0.84 | -73.1 | -2.35 |
| Short | 513 | 51.3 % | -0.029 | -15.0 | 0.94 | -26.8 | -0.68 |
| 1.ª mitad | 625 | 51.5 % | -0.046 | -28.6 | 0.91 | -39.8 | -1.19 |
| 2.ª mitad | 625 | 50.2 % | -0.077 | -48.1 | 0.85 | -57.2 | -1.98 |

Por año (R neto medio y operaciones): 2018 -0.007 (51), 2019 -0.102 (155), 2020 -0.044 (162), 2021 -0.013 (151), 2022 -0.146 (147), 2023 -0.101 (148), 2024 -0.041 (149), 2025 -0.090 (148), 2026 +0.032 (139).

Sensibilidad (R neto medio y t): colchón 0 % -0.072 (t -2.60), colchón 50 % -0.054 (t -2.01), objetivo 1,5:1 -0.035 (t -1.06), objetivo 2:1 -0.026 (t -0.71).

