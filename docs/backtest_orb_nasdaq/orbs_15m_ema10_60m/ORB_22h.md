# ORB de 15 min de las 22:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 22:00–22:15 | 1290 | 50.5 | -0.079 | -2.87 | +0.017 | 0.096 | no |
| 22:15–22:30 | 1232 | 50.3 | -0.098 | -3.46 | +0.005 | 0.102 | no |
| 22:30–22:45 | 1249 | 51.5 | -0.075 | -2.69 | +0.029 | 0.105 | no |
| 22:45–23:00 | 1259 | 51.9 | -0.071 | -2.52 | +0.043 | 0.113 | no |

## Detalle

### ORB 22:00–22:15

Rotura con cuerpo desde las 22:15 hasta las 04:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.096 R; ancho medio del ORB 0.11 %; cómo terminan: objetivo 632, stop 609, por tiempo 49.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1290 | 50.5 % | -0.079 | -101.9 | 0.85 | -117.4 | -2.87 |
| Sin costes | 1290 | 50.7 % | +0.017 | +22.4 | 1.04 | -47.0 | +0.63 |
| Long | 749 | 51.3 % | -0.075 | -56.2 | 0.86 | -66.6 | -2.08 |
| Short | 541 | 49.5 % | -0.084 | -45.6 | 0.84 | -60.1 | -1.98 |
| 1.ª mitad | 645 | 49.0 % | -0.100 | -64.8 | 0.81 | -75.8 | -2.60 |
| 2.ª mitad | 645 | 52.1 % | -0.057 | -37.1 | 0.89 | -43.6 | -1.46 |

Por año (R neto medio y operaciones): 2018 +0.054 (54), 2019 -0.143 (159), 2020 -0.118 (149), 2021 -0.114 (157), 2022 -0.091 (148), 2023 -0.073 (165), 2024 -0.046 (156), 2025 -0.052 (165), 2026 -0.039 (137).

Sensibilidad (R neto medio y t): colchón 0 % -0.079 (t -2.86), colchón 50 % -0.077 (t -2.84), objetivo 1,5:1 -0.079 (t -2.40), objetivo 2:1 -0.060 (t -1.59).

### ORB 22:15–22:30

Rotura con cuerpo desde las 22:30 hasta las 04:30 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.102 R; ancho medio del ORB 0.11 %; cómo terminan: objetivo 603, stop 600, por tiempo 29.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1232 | 50.3 % | -0.098 | -120.4 | 0.82 | -128.9 | -3.46 |
| Sin costes | 1232 | 50.3 % | +0.005 | +5.7 | 1.01 | -27.7 | +0.16 |
| Long | 696 | 52.9 % | -0.063 | -44.1 | 0.88 | -51.5 | -1.68 |
| Short | 536 | 47.0 % | -0.142 | -76.3 | 0.75 | -82.5 | -3.33 |
| 1.ª mitad | 616 | 50.0 % | -0.096 | -59.1 | 0.82 | -68.5 | -2.41 |
| 2.ª mitad | 616 | 50.6 % | -0.099 | -61.3 | 0.82 | -68.3 | -2.48 |

Por año (R neto medio y operaciones): 2018 -0.049 (46), 2019 -0.173 (149), 2020 -0.054 (153), 2021 -0.154 (152), 2022 -0.090 (140), 2023 -0.117 (164), 2024 -0.098 (151), 2025 -0.084 (143), 2026 -0.015 (134).

Sensibilidad (R neto medio y t): colchón 0 % -0.122 (t -4.29), colchón 50 % -0.071 (t -2.52), objetivo 1,5:1 -0.076 (t -2.23), objetivo 2:1 -0.083 (t -2.13).

### ORB 22:30–22:45

Rotura con cuerpo desde las 22:45 hasta las 04:45 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.105 R; ancho medio del ORB 0.11 %; cómo terminan: objetivo 628, stop 593, por tiempo 28.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1249 | 51.5 % | -0.075 | -94.2 | 0.86 | -122.8 | -2.69 |
| Sin costes | 1249 | 51.6 % | +0.029 | +36.4 | 1.06 | -33.1 | +1.04 |
| Long | 746 | 52.8 % | -0.056 | -41.9 | 0.89 | -70.5 | -1.55 |
| Short | 503 | 49.5 % | -0.104 | -52.3 | 0.81 | -63.0 | -2.35 |
| 1.ª mitad | 625 | 51.2 % | -0.070 | -43.7 | 0.87 | -65.8 | -1.77 |
| 2.ª mitad | 624 | 51.8 % | -0.081 | -50.5 | 0.85 | -71.1 | -2.03 |

Por año (R neto medio y operaciones): 2018 +0.084 (43), 2019 -0.113 (142), 2020 -0.116 (163), 2021 -0.147 (159), 2022 +0.035 (141), 2023 -0.236 (152), 2024 -0.145 (162), 2025 -0.004 (149), 2026 +0.112 (138).

Sensibilidad (R neto medio y t): colchón 0 % -0.087 (t -3.08), colchón 50 % -0.052 (t -1.87), objetivo 1,5:1 -0.055 (t -1.62), objetivo 2:1 -0.036 (t -0.91).

### ORB 22:45–23:00

Rotura con cuerpo desde las 23:00 hasta las 05:00 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.113 R; ancho medio del ORB 0.10 %; cómo terminan: objetivo 647, stop 591, por tiempo 21.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1259 | 51.9 % | -0.071 | -88.8 | 0.87 | -108.6 | -2.52 |
| Sin costes | 1259 | 51.9 % | +0.043 | +53.6 | 1.09 | -25.0 | +1.52 |
| Long | 732 | 52.2 % | -0.079 | -58.1 | 0.85 | -68.1 | -2.15 |
| Short | 527 | 51.4 % | -0.058 | -30.7 | 0.89 | -53.4 | -1.35 |
| 1.ª mitad | 630 | 52.1 % | -0.061 | -38.2 | 0.88 | -50.1 | -1.53 |
| 2.ª mitad | 629 | 51.7 % | -0.080 | -50.6 | 0.85 | -70.7 | -2.02 |

Por año (R neto medio y operaciones): 2018 -0.038 (47), 2019 -0.075 (135), 2020 -0.012 (148), 2021 -0.181 (154), 2022 +0.014 (156), 2023 -0.288 (145), 2024 -0.069 (153), 2025 -0.071 (170), 2026 +0.099 (151).

Sensibilidad (R neto medio y t): colchón 0 % -0.113 (t -4.02), colchón 50 % -0.071 (t -2.53), objetivo 1,5:1 -0.066 (t -1.93), objetivo 2:1 -0.049 (t -1.24).

