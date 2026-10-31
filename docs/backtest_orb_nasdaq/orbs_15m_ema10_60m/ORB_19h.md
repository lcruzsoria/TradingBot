# ORB de 15 min de las 19:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 19:00–19:15 | 1248 | 49.8 | -0.093 | -3.39 | +0.002 | 0.095 | no |
| 19:15–19:30 | 1227 | 49.6 | -0.102 | -3.66 | +0.001 | 0.102 | no |
| 19:30–19:45 | 1222 | 49.8 | -0.093 | -3.35 | +0.002 | 0.096 | no |
| 19:45–20:00 | 1195 | 49.3 | -0.078 | -2.78 | +0.009 | 0.087 | no |

## Detalle

### ORB 19:00–19:15

Rotura con cuerpo desde las 19:15 hasta las 01:15 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.095 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 572, stop 570, por tiempo 106.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1248 | 49.8 % | -0.093 | -116.1 | 0.82 | -130.3 | -3.39 |
| Sin costes | 1248 | 50.2 % | +0.002 | +2.6 | 1.00 | -46.5 | +0.08 |
| Long | 683 | 53.4 % | -0.040 | -27.2 | 0.92 | -39.6 | -1.07 |
| Short | 565 | 45.5 % | -0.157 | -88.9 | 0.72 | -95.7 | -3.86 |
| 1.ª mitad | 624 | 51.3 % | -0.064 | -40.1 | 0.87 | -43.8 | -1.64 |
| 2.ª mitad | 624 | 48.4 % | -0.122 | -76.0 | 0.77 | -88.5 | -3.16 |

Por año (R neto medio y operaciones): 2018 -0.189 (46), 2019 -0.086 (164), 2020 -0.015 (150), 2021 -0.058 (160), 2022 -0.130 (146), 2023 -0.232 (134), 2024 -0.080 (151), 2025 -0.084 (155), 2026 -0.048 (142).

Sensibilidad (R neto medio y t): colchón 0 % -0.100 (t -3.59), colchón 50 % -0.082 (t -3.04), objetivo 1,5:1 -0.077 (t -2.34), objetivo 2:1 -0.078 (t -2.14).

### ORB 19:15–19:30

Rotura con cuerpo desde las 19:30 hasta las 01:30 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.102 R; ancho medio del ORB 0.10 %; cómo terminan: objetivo 571, stop 570, por tiempo 86.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1227 | 49.6 % | -0.102 | -124.7 | 0.81 | -128.7 | -3.66 |
| Sin costes | 1227 | 49.8 % | +0.001 | +0.7 | 1.00 | -34.2 | +0.02 |
| Long | 693 | 50.5 % | -0.100 | -69.2 | 0.81 | -72.0 | -2.69 |
| Short | 534 | 48.3 % | -0.104 | -55.5 | 0.80 | -62.1 | -2.48 |
| 1.ª mitad | 614 | 50.7 % | -0.091 | -55.9 | 0.83 | -64.0 | -2.29 |
| 2.ª mitad | 613 | 48.5 % | -0.112 | -68.8 | 0.79 | -69.6 | -2.89 |

Por año (R neto medio y operaciones): 2018 -0.248 (38), 2019 -0.111 (165), 2020 -0.083 (156), 2021 +0.014 (165), 2022 -0.228 (139), 2023 -0.180 (125), 2024 -0.061 (132), 2025 -0.090 (162), 2026 -0.066 (145).

Sensibilidad (R neto medio y t): colchón 0 % -0.107 (t -3.82), colchón 50 % -0.089 (t -3.25), objetivo 1,5:1 -0.072 (t -2.16), objetivo 2:1 -0.058 (t -1.55).

### ORB 19:30–19:45

Rotura con cuerpo desde las 19:45 hasta las 01:45 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.096 R; ancho medio del ORB 0.11 %; cómo terminan: objetivo 568, stop 566, por tiempo 88.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1222 | 49.8 % | -0.093 | -114.1 | 0.82 | -117.8 | -3.35 |
| Sin costes | 1222 | 49.8 % | +0.002 | +2.7 | 1.00 | -42.0 | +0.08 |
| Long | 700 | 51.9 % | -0.059 | -41.6 | 0.88 | -53.3 | -1.62 |
| Short | 522 | 46.9 % | -0.139 | -72.5 | 0.75 | -76.3 | -3.24 |
| 1.ª mitad | 611 | 51.2 % | -0.056 | -34.4 | 0.89 | -36.2 | -1.43 |
| 2.ª mitad | 611 | 48.3 % | -0.130 | -79.6 | 0.76 | -83.6 | -3.31 |

Por año (R neto medio y operaciones): 2018 -0.027 (45), 2019 -0.100 (155), 2020 +0.020 (149), 2021 -0.012 (146), 2022 -0.170 (136), 2023 -0.177 (138), 2024 -0.133 (139), 2025 -0.096 (165), 2026 -0.112 (149).

Sensibilidad (R neto medio y t): colchón 0 % -0.114 (t -4.05), colchón 50 % -0.069 (t -2.54), objetivo 1,5:1 -0.044 (t -1.33), objetivo 2:1 -0.032 (t -0.86).

### ORB 19:45–20:00

Rotura con cuerpo desde las 20:00 hasta las 02:00 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.087 R; ancho medio del ORB 0.11 %; cómo terminan: objetivo 556, stop 542, por tiempo 97.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1195 | 49.3 % | -0.078 | -93.1 | 0.85 | -114.2 | -2.78 |
| Sin costes | 1195 | 49.5 % | +0.009 | +11.1 | 1.02 | -35.1 | +0.33 |
| Long | 691 | 49.9 % | -0.069 | -47.6 | 0.86 | -59.2 | -1.89 |
| Short | 504 | 48.4 % | -0.090 | -45.6 | 0.83 | -60.3 | -2.07 |
| 1.ª mitad | 598 | 49.0 % | -0.085 | -50.8 | 0.83 | -63.4 | -2.15 |
| 2.ª mitad | 597 | 49.6 % | -0.071 | -42.4 | 0.86 | -55.6 | -1.79 |

Por año (R neto medio y operaciones): 2018 +0.128 (45), 2019 -0.197 (151), 2020 -0.133 (143), 2021 -0.029 (145), 2022 -0.060 (138), 2023 -0.209 (136), 2024 -0.029 (149), 2025 -0.068 (155), 2026 +0.041 (133).

Sensibilidad (R neto medio y t): colchón 0 % -0.080 (t -2.84), colchón 50 % -0.067 (t -2.47), objetivo 1,5:1 -0.066 (t -1.97), objetivo 2:1 -0.044 (t -1.17).

