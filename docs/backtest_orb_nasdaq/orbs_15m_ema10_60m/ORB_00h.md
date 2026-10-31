# ORB de 15 min de las 00:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 00:00–00:15 | 1349 | 49.2 | -0.139 | -5.10 | -0.014 | 0.125 | no |
| 00:15–00:30 | 1266 | 49.2 | -0.141 | -4.99 | -0.012 | 0.129 | no |
| 00:30–00:45 | 1320 | 48.1 | -0.156 | -5.65 | -0.034 | 0.123 | no |
| 00:45–01:00 | 1277 | 50.0 | -0.123 | -4.39 | -0.000 | 0.123 | no |

## Detalle

### ORB 00:00–00:15

Rotura con cuerpo desde las 00:15 hasta las 06:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.125 R; ancho medio del ORB 0.09 %; cómo terminan: objetivo 657, stop 676, por tiempo 16.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1349 | 49.2 % | -0.139 | -187.7 | 0.75 | -197.8 | -5.10 |
| Sin costes | 1349 | 49.3 % | -0.014 | -19.2 | 0.97 | -58.8 | -0.53 |
| Long | 767 | 47.8 % | -0.178 | -136.9 | 0.70 | -138.8 | -4.93 |
| Short | 582 | 51.0 % | -0.087 | -50.8 | 0.84 | -71.4 | -2.11 |
| 1.ª mitad | 675 | 47.9 % | -0.167 | -112.9 | 0.71 | -112.9 | -4.37 |
| 2.ª mitad | 674 | 50.6 % | -0.111 | -74.7 | 0.80 | -91.3 | -2.86 |

Por año (R neto medio y operaciones): 2018 -0.142 (44), 2019 -0.144 (149), 2020 -0.101 (167), 2021 -0.182 (176), 2022 -0.264 (173), 2023 -0.194 (167), 2024 -0.075 (156), 2025 -0.171 (178), 2026 +0.066 (139).

Sensibilidad (R neto medio y t): colchón 0 % -0.155 (t -5.68), colchón 50 % -0.117 (t -4.33), objetivo 1,5:1 -0.141 (t -4.27), objetivo 2:1 -0.117 (t -3.09).

### ORB 00:15–00:30

Rotura con cuerpo desde las 00:30 hasta las 06:30; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.129 R; ancho medio del ORB 0.08 %; cómo terminan: objetivo 622, stop 636, por tiempo 8.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1266 | 49.2 % | -0.141 | -178.1 | 0.75 | -181.0 | -4.99 |
| Sin costes | 1266 | 49.3 % | -0.012 | -15.4 | 0.98 | -46.9 | -0.43 |
| Long | 721 | 49.2 % | -0.151 | -108.9 | 0.74 | -109.9 | -4.03 |
| Short | 545 | 49.2 % | -0.127 | -69.2 | 0.77 | -76.7 | -2.96 |
| 1.ª mitad | 633 | 46.6 % | -0.198 | -125.5 | 0.67 | -130.7 | -4.98 |
| 2.ª mitad | 633 | 51.8 % | -0.083 | -52.7 | 0.85 | -58.7 | -2.09 |

Por año (R neto medio y operaciones): 2018 -0.327 (46), 2019 -0.246 (140), 2020 -0.115 (147), 2021 -0.175 (163), 2022 -0.195 (166), 2023 -0.182 (139), 2024 -0.020 (161), 2025 -0.089 (165), 2026 -0.055 (139).

Sensibilidad (R neto medio y t): colchón 0 % -0.150 (t -5.30), colchón 50 % -0.118 (t -4.21), objetivo 1,5:1 -0.115 (t -3.34), objetivo 2:1 -0.118 (t -2.98).

### ORB 00:30–00:45

Rotura con cuerpo desde las 00:45 hasta las 06:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.123 R; ancho medio del ORB 0.09 %; cómo terminan: objetivo 633, stop 675, por tiempo 12.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1320 | 48.1 % | -0.156 | -206.1 | 0.73 | -209.9 | -5.65 |
| Sin costes | 1320 | 48.2 % | -0.034 | -44.3 | 0.93 | -88.1 | -1.22 |
| Long | 743 | 49.5 % | -0.139 | -103.3 | 0.76 | -111.5 | -3.75 |
| Short | 577 | 46.3 % | -0.178 | -102.8 | 0.70 | -105.1 | -4.30 |
| 1.ª mitad | 660 | 43.3 % | -0.255 | -168.6 | 0.60 | -171.4 | -6.56 |
| 2.ª mitad | 660 | 52.9 % | -0.057 | -37.5 | 0.89 | -42.8 | -1.46 |

Por año (R neto medio y operaciones): 2018 -0.222 (52), 2019 -0.287 (165), 2020 -0.194 (165), 2021 -0.315 (172), 2022 -0.156 (156), 2023 -0.105 (149), 2024 -0.105 (169), 2025 -0.008 (152), 2026 -0.014 (140).

Sensibilidad (R neto medio y t): colchón 0 % -0.172 (t -6.19), colchón 50 % -0.126 (t -4.60), objetivo 1,5:1 -0.122 (t -3.64), objetivo 2:1 -0.110 (t -2.88).

### ORB 00:45–01:00

Rotura con cuerpo desde las 01:00 hasta las 07:00; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.123 R; ancho medio del ORB 0.09 %; cómo terminan: objetivo 629, stop 630, por tiempo 18.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1277 | 50.0 % | -0.123 | -157.0 | 0.78 | -188.0 | -4.39 |
| Sin costes | 1277 | 50.0 % | -0.000 | -0.2 | 1.00 | -71.0 | -0.00 |
| Long | 733 | 51.3 % | -0.106 | -77.6 | 0.81 | -105.1 | -2.86 |
| Short | 544 | 48.2 % | -0.146 | -79.4 | 0.74 | -87.7 | -3.41 |
| 1.ª mitad | 639 | 45.1 % | -0.223 | -142.2 | 0.64 | -146.4 | -5.62 |
| 2.ª mitad | 638 | 54.9 % | -0.023 | -14.8 | 0.95 | -46.9 | -0.59 |

Por año (R neto medio y operaciones): 2018 -0.070 (53), 2019 -0.290 (162), 2020 -0.110 (147), 2021 -0.285 (161), 2022 -0.189 (140), 2023 -0.080 (135), 2024 -0.107 (169), 2025 -0.010 (163), 2026 +0.087 (147).

Sensibilidad (R neto medio y t): colchón 0 % -0.147 (t -5.23), colchón 50 % -0.099 (t -3.54), objetivo 1,5:1 -0.081 (t -2.35), objetivo 2:1 -0.077 (t -1.95).

