# ORB de 15 min de las 23:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 23:00–23:15 | 1278 | 51.0 | -0.092 | -3.31 | +0.024 | 0.116 | no |
| 23:15–23:30 | 1245 | 50.6 | -0.110 | -3.86 | +0.012 | 0.122 | no |
| 23:30–23:45 | 1278 | 49.7 | -0.129 | -4.59 | -0.001 | 0.127 | no |
| 23:45–00:00 | 1280 | 50.6 | -0.121 | -4.31 | +0.015 | 0.136 | no |

## Detalle

### ORB 23:00–23:15

Rotura con cuerpo desde las 23:15 hasta las 05:15 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.116 R; ancho medio del ORB 0.09 %; cómo terminan: objetivo 643, stop 613, por tiempo 22.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1278 | 51.0 % | -0.092 | -118.0 | 0.83 | -142.9 | -3.31 |
| Sin costes | 1278 | 51.1 % | +0.024 | +30.6 | 1.05 | -27.0 | +0.86 |
| Long | 747 | 50.6 % | -0.109 | -81.4 | 0.80 | -104.0 | -2.97 |
| Short | 531 | 51.6 % | -0.069 | -36.5 | 0.87 | -44.7 | -1.60 |
| 1.ª mitad | 639 | 49.1 % | -0.126 | -80.3 | 0.77 | -81.3 | -3.18 |
| 2.ª mitad | 639 | 52.9 % | -0.059 | -37.6 | 0.89 | -73.3 | -1.50 |

Por año (R neto medio y operaciones): 2018 -0.160 (56), 2019 -0.326 (148), 2020 -0.018 (164), 2021 -0.068 (143), 2022 -0.037 (158), 2023 -0.166 (149), 2024 -0.150 (157), 2025 -0.110 (161), 2026 +0.167 (142).

Sensibilidad (R neto medio y t): colchón 0 % -0.118 (t -4.22), colchón 50 % -0.076 (t -2.74), objetivo 1,5:1 -0.075 (t -2.20), objetivo 2:1 -0.054 (t -1.39).

### ORB 23:15–23:30

Rotura con cuerpo desde las 23:30 hasta las 05:30 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2098.

**No pasa los criterios**. Coste medio 0.122 R; ancho medio del ORB 0.09 %; cómo terminan: objetivo 623, stop 608, por tiempo 14.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1245 | 50.6 % | -0.110 | -136.4 | 0.80 | -152.6 | -3.86 |
| Sin costes | 1245 | 50.6 % | +0.012 | +15.4 | 1.03 | -43.1 | +0.44 |
| Long | 716 | 51.7 % | -0.097 | -69.8 | 0.82 | -71.7 | -2.60 |
| Short | 529 | 49.1 % | -0.126 | -66.7 | 0.77 | -85.9 | -2.91 |
| 1.ª mitad | 623 | 47.0 % | -0.176 | -109.8 | 0.70 | -113.4 | -4.39 |
| 2.ª mitad | 622 | 54.2 % | -0.043 | -26.6 | 0.92 | -47.4 | -1.07 |

Por año (R neto medio y operaciones): 2018 -0.149 (43), 2019 -0.362 (148), 2020 -0.078 (160), 2021 -0.135 (154), 2022 -0.116 (155), 2023 -0.099 (148), 2024 -0.139 (147), 2025 +0.038 (150), 2026 +0.029 (140).

Sensibilidad (R neto medio y t): colchón 0 % -0.129 (t -4.52), colchón 50 % -0.117 (t -4.16), objetivo 1,5:1 -0.114 (t -3.31), objetivo 2:1 -0.077 (t -1.94).

### ORB 23:30–23:45

Rotura con cuerpo desde las 23:45 hasta las 05:45 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2098.

**No pasa los criterios**. Coste medio 0.127 R; ancho medio del ORB 0.09 %; cómo terminan: objetivo 631, stop 633, por tiempo 14.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1278 | 49.7 % | -0.129 | -164.3 | 0.77 | -183.7 | -4.59 |
| Sin costes | 1278 | 49.8 % | -0.001 | -1.6 | 1.00 | -50.9 | -0.05 |
| Long | 727 | 49.9 % | -0.134 | -97.4 | 0.76 | -104.3 | -3.60 |
| Short | 551 | 49.4 % | -0.122 | -67.0 | 0.78 | -86.3 | -2.86 |
| 1.ª mitad | 639 | 47.9 % | -0.165 | -105.6 | 0.72 | -108.6 | -4.18 |
| 2.ª mitad | 639 | 51.5 % | -0.092 | -58.7 | 0.83 | -76.0 | -2.32 |

Por año (R neto medio y operaciones): 2018 -0.172 (50), 2019 -0.207 (146), 2020 -0.062 (155), 2021 -0.213 (161), 2022 -0.208 (156), 2023 -0.180 (162), 2024 -0.121 (151), 2025 -0.079 (157), 2026 +0.076 (140).

Sensibilidad (R neto medio y t): colchón 0 % -0.171 (t -6.12), colchón 50 % -0.083 (t -2.97), objetivo 1,5:1 -0.130 (t -3.82), objetivo 2:1 -0.122 (t -3.11).

### ORB 23:45–00:00

Rotura con cuerpo desde las 00:00 hasta las 06:00 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2098.

**No pasa los criterios**. Coste medio 0.136 R; ancho medio del ORB 0.08 %; cómo terminan: objetivo 643, stop 624, por tiempo 13.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1280 | 50.6 % | -0.121 | -154.4 | 0.78 | -162.9 | -4.31 |
| Sin costes | 1280 | 50.8 % | +0.015 | +19.8 | 1.03 | -33.0 | +0.55 |
| Long | 727 | 50.3 % | -0.139 | -100.7 | 0.76 | -102.1 | -3.72 |
| Short | 553 | 51.0 % | -0.097 | -53.7 | 0.82 | -66.6 | -2.28 |
| 1.ª mitad | 640 | 51.1 % | -0.107 | -68.5 | 0.80 | -71.6 | -2.72 |
| 2.ª mitad | 640 | 50.2 % | -0.134 | -85.9 | 0.76 | -96.2 | -3.36 |

Por año (R neto medio y operaciones): 2018 -0.461 (44), 2019 -0.145 (149), 2020 -0.030 (163), 2021 -0.106 (152), 2022 -0.098 (160), 2023 -0.233 (156), 2024 -0.133 (151), 2025 -0.101 (159), 2026 -0.022 (146).

Sensibilidad (R neto medio y t): colchón 0 % -0.126 (t -4.49), colchón 50 % -0.099 (t -3.56), objetivo 1,5:1 -0.116 (t -3.41), objetivo 2:1 -0.098 (t -2.50).

