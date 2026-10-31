# ORB de 15 min de las 02:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 02:00–02:15 | 1460 | 48.8 | -0.094 | -3.69 | -0.024 | 0.070 | no |
| 02:15–02:30 | 1385 | 47.9 | -0.119 | -4.49 | -0.036 | 0.083 | no |
| 02:30–02:45 | 1345 | 48.3 | -0.115 | -4.28 | -0.035 | 0.080 | no |
| 02:45–03:00 | 1407 | 49.1 | -0.093 | -3.52 | -0.015 | 0.078 | no |

## Detalle

### ORB 02:00–02:15

Rotura con cuerpo desde las 02:15 hasta las 08:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.070 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 668, stop 709, por tiempo 83.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1460 | 48.8 % | -0.094 | -137.8 | 0.82 | -150.8 | -3.69 |
| Sin costes | 1460 | 49.0 % | -0.024 | -35.1 | 0.95 | -70.6 | -0.94 |
| Long | 836 | 49.8 % | -0.078 | -65.1 | 0.85 | -75.9 | -2.31 |
| Short | 624 | 47.6 % | -0.116 | -72.7 | 0.79 | -84.3 | -2.96 |
| 1.ª mitad | 730 | 46.2 % | -0.138 | -100.9 | 0.75 | -116.4 | -3.84 |
| 2.ª mitad | 730 | 51.5 % | -0.050 | -36.8 | 0.90 | -49.3 | -1.39 |

Por año (R neto medio y operaciones): 2018 +0.121 (54), 2019 -0.276 (173), 2020 -0.084 (171), 2021 -0.122 (192), 2022 -0.169 (181), 2023 +0.035 (185), 2024 -0.147 (190), 2025 -0.039 (182), 2026 +0.001 (132).

Sensibilidad (R neto medio y t): colchón 0 % -0.089 (t -3.45), colchón 50 % -0.070 (t -2.80), objetivo 1,5:1 -0.066 (t -2.16), objetivo 2:1 -0.070 (t -2.05).

### ORB 02:15–02:30

Rotura con cuerpo desde las 02:30 hasta las 08:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.083 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 640, stop 690, por tiempo 55.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1385 | 47.9 % | -0.119 | -164.2 | 0.78 | -173.8 | -4.49 |
| Sin costes | 1385 | 48.3 % | -0.036 | -49.8 | 0.93 | -78.3 | -1.36 |
| Long | 803 | 50.1 % | -0.080 | -64.5 | 0.85 | -86.3 | -2.32 |
| Short | 582 | 45.0 % | -0.171 | -99.7 | 0.70 | -104.4 | -4.22 |
| 1.ª mitad | 693 | 46.2 % | -0.158 | -109.4 | 0.72 | -113.5 | -4.25 |
| 2.ª mitad | 692 | 49.7 % | -0.079 | -54.8 | 0.85 | -62.2 | -2.11 |

Por año (R neto medio y operaciones): 2018 +0.049 (51), 2019 -0.260 (169), 2020 -0.076 (159), 2021 -0.179 (199), 2022 -0.212 (166), 2023 -0.081 (171), 2024 -0.169 (172), 2025 +0.017 (166), 2026 +0.000 (132).

Sensibilidad (R neto medio y t): colchón 0 % -0.137 (t -5.16), colchón 50 % -0.098 (t -3.75), objetivo 1,5:1 -0.088 (t -2.78), objetivo 2:1 -0.084 (t -2.33).

### ORB 02:30–02:45

Rotura con cuerpo desde las 02:45 hasta las 08:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.080 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 628, stop 675, por tiempo 42.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1345 | 48.3 % | -0.115 | -154.7 | 0.79 | -155.7 | -4.28 |
| Sin costes | 1345 | 48.3 % | -0.035 | -47.0 | 0.93 | -52.3 | -1.30 |
| Long | 765 | 48.1 % | -0.123 | -94.1 | 0.78 | -100.3 | -3.46 |
| Short | 580 | 48.4 % | -0.105 | -60.7 | 0.81 | -65.6 | -2.54 |
| 1.ª mitad | 673 | 48.3 % | -0.109 | -73.3 | 0.80 | -82.4 | -2.89 |
| 2.ª mitad | 672 | 48.2 % | -0.121 | -81.4 | 0.78 | -83.4 | -3.16 |

Por año (R neto medio y operaciones): 2018 -0.154 (53), 2019 -0.211 (167), 2020 -0.081 (167), 2021 -0.095 (171), 2022 -0.059 (157), 2023 -0.001 (167), 2024 -0.197 (172), 2025 -0.118 (158), 2026 -0.149 (133).

Sensibilidad (R neto medio y t): colchón 0 % -0.140 (t -5.18), colchón 50 % -0.087 (t -3.28), objetivo 1,5:1 -0.092 (t -2.83), objetivo 2:1 -0.081 (t -2.20).

### ORB 02:45–03:00

Rotura con cuerpo desde las 03:00 hasta las 09:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.078 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 677, stop 698, por tiempo 32.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1407 | 49.1 % | -0.093 | -131.2 | 0.83 | -142.9 | -3.52 |
| Sin costes | 1407 | 49.3 % | -0.015 | -21.5 | 0.97 | -39.6 | -0.58 |
| Long | 776 | 49.0 % | -0.100 | -77.3 | 0.82 | -84.3 | -2.81 |
| Short | 631 | 49.3 % | -0.085 | -53.9 | 0.84 | -70.8 | -2.14 |
| 1.ª mitad | 704 | 48.3 % | -0.113 | -79.3 | 0.79 | -84.5 | -3.01 |
| 2.ª mitad | 703 | 49.9 % | -0.074 | -51.9 | 0.86 | -66.1 | -1.97 |

Por año (R neto medio y operaciones): 2018 -0.092 (55), 2019 -0.238 (177), 2020 -0.105 (165), 2021 -0.062 (182), 2022 -0.073 (163), 2023 -0.020 (178), 2024 -0.124 (176), 2025 -0.107 (166), 2026 -0.002 (145).

Sensibilidad (R neto medio y t): colchón 0 % -0.123 (t -4.64), colchón 50 % -0.088 (t -3.36), objetivo 1,5:1 -0.110 (t -3.46), objetivo 2:1 -0.102 (t -2.84).

