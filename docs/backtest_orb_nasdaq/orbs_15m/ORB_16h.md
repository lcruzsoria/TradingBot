# ORB de 15 min de las 16:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 16:00–16:15 | 1791 | 47.7 | -0.048 | -2.57 | +0.001 | 0.049 | no |
| 16:15–16:30 | 1148 | 44.1 | -0.175 | -6.71 | -0.083 | 0.092 | no |
| 16:30–16:45 | 1851 | 42.6 | -0.178 | -8.40 | -0.074 | 0.105 | no |
| 16:45–17:00 | 1614 | 48.2 | -0.125 | -5.20 | -0.033 | 0.092 | no |

## Detalle

### ORB 16:00–16:15

Rotura con cuerpo desde las 16:15 hasta las 22:15; a esa hora se cierra. ORB completos: 2025; con rotura: 1791.

**No pasa los criterios**. Coste medio 0.049 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 494, stop 530, por tiempo 767.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1791 | 47.7 % | -0.048 | -86.8 | 0.87 | -102.2 | -2.57 |
| Sin costes | 1791 | 49.4 % | +0.001 | +1.5 | 1.00 | -58.0 | +0.05 |
| Long | 994 | 49.9 % | -0.015 | -15.4 | 0.96 | -43.2 | -0.62 |
| Short | 797 | 44.9 % | -0.090 | -71.5 | 0.78 | -81.5 | -3.12 |
| 1.ª mitad | 896 | 49.4 % | -0.027 | -24.4 | 0.93 | -33.9 | -1.01 |
| 2.ª mitad | 895 | 45.9 % | -0.070 | -62.5 | 0.82 | -77.0 | -2.65 |

Por año (R neto medio y operaciones): 2018 +0.041 (62), 2019 -0.020 (226), 2020 -0.011 (218), 2021 +0.033 (218), 2022 -0.129 (220), 2023 -0.047 (217), 2024 -0.015 (212), 2025 -0.139 (223), 2026 -0.086 (195).

Sensibilidad (R neto medio y t): colchón 0 % -0.049 (t -2.46), colchón 50 % -0.057 (t -3.30), objetivo 1,5:1 -0.058 (t -2.82), objetivo 2:1 -0.057 (t -2.60).

### ORB 16:15–16:30

Rotura con cuerpo desde las 16:30 hasta las 22:30; a esa hora se cierra. ORB completos: 1238; con rotura: 1148.

**No pasa los criterios**. Coste medio 0.092 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 383, stop 486, por tiempo 279.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1148 | 44.1 % | -0.175 | -200.8 | 0.65 | -206.5 | -6.71 |
| Sin costes | 1148 | 45.5 % | -0.083 | -95.1 | 0.82 | -102.5 | -3.18 |
| Long | 639 | 46.9 % | -0.135 | -86.1 | 0.73 | -93.6 | -3.79 |
| Short | 509 | 40.5 % | -0.225 | -114.7 | 0.57 | -117.5 | -5.89 |
| 1.ª mitad | 574 | 44.9 % | -0.156 | -89.8 | 0.68 | -96.1 | -4.26 |
| 2.ª mitad | 574 | 43.2 % | -0.193 | -111.1 | 0.63 | -116.3 | -5.21 |

Por año (R neto medio y operaciones): 2021 -0.117 (30), 2022 -0.152 (233), 2023 -0.213 (232), 2024 -0.199 (231), 2025 -0.197 (226), 2026 -0.112 (196).

Sensibilidad (R neto medio y t): colchón 0 % -0.186 (t -6.93), colchón 50 % -0.142 (t -5.59), objetivo 1,5:1 -0.148 (t -4.81), objetivo 2:1 -0.147 (t -4.33).

### ORB 16:30–16:45

Rotura con cuerpo desde las 16:45 hasta las 22:45; a esa hora se cierra. ORB completos: 2026; con rotura: 1851.

**No pasa los criterios**. Coste medio 0.105 R; ancho medio del ORB 0.11 %; cómo terminan: objetivo 681, stop 808, por tiempo 362.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1851 | 42.6 % | -0.178 | -329.9 | 0.66 | -343.0 | -8.40 |
| Sin costes | 1851 | 43.9 % | -0.074 | -136.2 | 0.84 | -154.4 | -3.50 |
| Long | 969 | 45.8 % | -0.115 | -111.9 | 0.76 | -120.4 | -3.93 |
| Short | 882 | 39.0 % | -0.247 | -218.1 | 0.56 | -226.5 | -8.10 |
| 1.ª mitad | 926 | 41.8 % | -0.183 | -169.5 | 0.65 | -176.3 | -6.13 |
| 2.ª mitad | 925 | 43.4 % | -0.173 | -160.4 | 0.67 | -167.7 | -5.75 |

Por año (R neto medio y operaciones): 2018 +0.054 (64), 2019 -0.261 (233), 2020 -0.106 (225), 2021 -0.194 (231), 2022 -0.244 (230), 2023 -0.257 (226), 2024 -0.121 (226), 2025 -0.204 (225), 2026 -0.086 (191).

Sensibilidad (R neto medio y t): colchón 0 % -0.200 (t -9.30), colchón 50 % -0.143 (t -6.89), objetivo 1,5:1 -0.175 (t -7.03), objetivo 2:1 -0.176 (t -6.37).

### ORB 16:45–17:00

Rotura con cuerpo desde las 17:00 hasta las 23:00; a esa hora se cierra. ORB completos: 2026; con rotura: 1614.

**No pasa los criterios**. Coste medio 0.092 R; ancho medio del ORB 0.09 %; cómo terminan: objetivo 703, stop 760, por tiempo 151.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1614 | 48.2 % | -0.125 | -201.5 | 0.77 | -209.5 | -5.20 |
| Sin costes | 1614 | 48.2 % | -0.033 | -53.5 | 0.93 | -69.0 | -1.39 |
| Long | 854 | 50.6 % | -0.073 | -62.3 | 0.86 | -71.8 | -2.22 |
| Short | 760 | 45.5 % | -0.183 | -139.2 | 0.68 | -146.0 | -5.24 |
| 1.ª mitad | 807 | 48.0 % | -0.132 | -106.5 | 0.76 | -114.7 | -3.88 |
| 2.ª mitad | 807 | 48.5 % | -0.118 | -95.0 | 0.78 | -97.9 | -3.48 |

Por año (R neto medio y operaciones): 2018 +0.038 (57), 2019 -0.228 (197), 2020 -0.058 (201), 2021 -0.206 (201), 2022 -0.085 (199), 2023 -0.202 (198), 2024 -0.071 (197), 2025 -0.140 (196), 2026 -0.043 (168).

Sensibilidad (R neto medio y t): colchón 0 % -0.120 (t -4.93), colchón 50 % -0.136 (t -5.78), objetivo 1,5:1 -0.128 (t -4.51), objetivo 2:1 -0.140 (t -4.51).

