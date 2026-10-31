# ORB de 15 min de las 16:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 16:00–16:15 | 1180 | 49.0 | -0.023 | -1.02 | +0.025 | 0.048 | no |
| 16:15–16:30 | 679 | 43.9 | -0.179 | -5.36 | -0.093 | 0.087 | no |
| 16:30–16:45 | 1038 | 44.8 | -0.130 | -4.66 | -0.030 | 0.100 | no |
| 16:45–17:00 | 899 | 52.4 | -0.035 | -1.10 | +0.049 | 0.085 | no |

## Detalle

### ORB 16:00–16:15

Rotura con cuerpo desde las 16:15 hasta las 22:15; a esa hora se cierra. ORB completos: 2025; con rotura: 1791.

**No pasa los criterios**. Coste medio 0.048 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 322, stop 316, por tiempo 542.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1180 | 49.0 % | -0.023 | -27.3 | 0.93 | -58.5 | -1.02 |
| Sin costes | 1180 | 51.1 % | +0.025 | +29.3 | 1.08 | -28.1 | +1.10 |
| Long | 690 | 50.9 % | -0.001 | -1.0 | 1.00 | -25.6 | -0.05 |
| Short | 490 | 46.3 % | -0.054 | -26.3 | 0.86 | -37.4 | -1.49 |
| 1.ª mitad | 590 | 52.9 % | +0.035 | +20.7 | 1.11 | -16.1 | +1.09 |
| 2.ª mitad | 590 | 45.1 % | -0.081 | -48.0 | 0.78 | -53.3 | -2.57 |

Por año (R neto medio y operaciones): 2018 +0.045 (40), 2019 +0.016 (173), 2020 +0.016 (148), 2021 +0.114 (139), 2022 -0.082 (130), 2023 -0.118 (140), 2024 -0.003 (130), 2025 -0.072 (157), 2026 -0.090 (123).

Sensibilidad (R neto medio y t): colchón 0 % -0.035 (t -1.49), colchón 50 % -0.029 (t -1.39), objetivo 1,5:1 -0.023 (t -0.89), objetivo 2:1 -0.020 (t -0.72).

### ORB 16:15–16:30

Rotura con cuerpo desde las 16:30 hasta las 22:30; a esa hora se cierra. ORB completos: 1238; con rotura: 1148.

**No pasa los criterios**. Coste medio 0.087 R; ancho medio del ORB 0.14 %; cómo terminan: objetivo 210, stop 283, por tiempo 186.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 679 | 43.9 % | -0.179 | -121.7 | 0.64 | -126.0 | -5.36 |
| Sin costes | 679 | 45.1 % | -0.093 | -62.9 | 0.79 | -68.3 | -2.78 |
| Long | 401 | 46.9 % | -0.143 | -57.5 | 0.70 | -61.2 | -3.26 |
| Short | 278 | 39.6 % | -0.231 | -64.3 | 0.55 | -67.1 | -4.49 |
| 1.ª mitad | 340 | 44.1 % | -0.168 | -57.1 | 0.65 | -60.8 | -3.60 |
| 2.ª mitad | 339 | 43.7 % | -0.191 | -64.6 | 0.63 | -69.9 | -3.97 |

Por año (R neto medio y operaciones): 2021 -0.168 (22), 2022 -0.203 (133), 2023 -0.194 (129), 2024 -0.215 (135), 2025 -0.172 (147), 2026 -0.104 (113).

Sensibilidad (R neto medio y t): colchón 0 % -0.185 (t -5.35), colchón 50 % -0.136 (t -4.21), objetivo 1,5:1 -0.144 (t -3.68), objetivo 2:1 -0.139 (t -3.22).

### ORB 16:30–16:45

Rotura con cuerpo desde las 16:45 hasta las 22:45; a esa hora se cierra. ORB completos: 2026; con rotura: 1851.

**No pasa los criterios**. Coste medio 0.100 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 384, stop 418, por tiempo 236.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1038 | 44.8 % | -0.130 | -135.2 | 0.73 | -143.1 | -4.66 |
| Sin costes | 1038 | 46.1 % | -0.030 | -31.0 | 0.93 | -45.4 | -1.08 |
| Long | 592 | 46.8 % | -0.100 | -59.3 | 0.79 | -68.6 | -2.71 |
| Short | 446 | 42.2 % | -0.170 | -75.9 | 0.67 | -80.7 | -3.99 |
| 1.ª mitad | 519 | 43.7 % | -0.128 | -66.6 | 0.73 | -72.7 | -3.29 |
| 2.ª mitad | 519 | 45.9 % | -0.132 | -68.6 | 0.73 | -73.9 | -3.30 |

Por año (R neto medio y operaciones): 2018 -0.052 (36), 2019 -0.248 (142), 2020 -0.071 (137), 2021 -0.113 (123), 2022 -0.145 (109), 2023 -0.234 (121), 2024 -0.068 (126), 2025 -0.153 (136), 2026 -0.011 (108).

Sensibilidad (R neto medio y t): colchón 0 % -0.151 (t -5.33), colchón 50 % -0.102 (t -3.75), objetivo 1,5:1 -0.116 (t -3.53), objetivo 2:1 -0.104 (t -2.82).

### ORB 16:45–17:00

Rotura con cuerpo desde las 17:00 hasta las 23:00; a esa hora se cierra. ORB completos: 2026; con rotura: 1614.

**No pasa los criterios**. Coste medio 0.085 R; ancho medio del ORB 0.10 %; cómo terminan: objetivo 417, stop 375, por tiempo 107.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 899 | 52.4 % | -0.035 | -31.5 | 0.93 | -61.6 | -1.10 |
| Sin costes | 899 | 52.4 % | +0.049 | +44.4 | 1.11 | -18.0 | +1.56 |
| Long | 521 | 55.1 % | +0.015 | +8.1 | 1.03 | -18.5 | +0.37 |
| Short | 378 | 48.7 % | -0.105 | -39.6 | 0.80 | -52.6 | -2.13 |
| 1.ª mitad | 450 | 49.6 % | -0.084 | -38.0 | 0.83 | -45.3 | -1.87 |
| 2.ª mitad | 449 | 55.2 % | +0.014 | +6.5 | 1.03 | -19.4 | +0.32 |

Por año (R neto medio y operaciones): 2018 -0.049 (31), 2019 -0.173 (104), 2020 +0.025 (103), 2021 -0.126 (91), 2022 -0.059 (117), 2023 -0.175 (105), 2024 +0.110 (114), 2025 +0.056 (122), 2026 +0.026 (112).

Sensibilidad (R neto medio y t): colchón 0 % -0.038 (t -1.17), colchón 50 % -0.046 (t -1.46), objetivo 1,5:1 -0.002 (t -0.06), objetivo 2:1 -0.032 (t -0.76).

