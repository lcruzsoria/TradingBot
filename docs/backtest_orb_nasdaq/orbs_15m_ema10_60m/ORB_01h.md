# ORB de 15 min de las 01:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 01:00–01:15 | 1357 | 50.9 | -0.077 | -2.84 | +0.020 | 0.096 | no |
| 01:15–01:30 | 1360 | 51.8 | -0.064 | -2.34 | +0.041 | 0.105 | no |
| 01:30–01:45 | 1373 | 51.6 | -0.062 | -2.31 | +0.035 | 0.097 | no |
| 01:45–02:00 | 1350 | 49.0 | -0.108 | -3.99 | -0.017 | 0.091 | no |

## Detalle

### ORB 01:00–01:15

Rotura con cuerpo desde las 01:15 hasta las 07:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.096 R; ancho medio del ORB 0.11 %; cómo terminan: objetivo 678, stop 652, por tiempo 27.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1357 | 50.9 % | -0.077 | -104.0 | 0.86 | -133.9 | -2.84 |
| Sin costes | 1357 | 50.9 % | +0.020 | +26.8 | 1.04 | -38.9 | +0.73 |
| Long | 772 | 52.8 % | -0.040 | -31.1 | 0.92 | -56.8 | -1.13 |
| Short | 585 | 48.4 % | -0.125 | -72.9 | 0.78 | -83.6 | -3.03 |
| 1.ª mitad | 679 | 47.7 % | -0.141 | -95.9 | 0.75 | -98.7 | -3.69 |
| 2.ª mitad | 678 | 54.1 % | -0.012 | -8.1 | 0.98 | -37.7 | -0.32 |

Por año (R neto medio y operaciones): 2018 -0.097 (54), 2019 -0.233 (154), 2020 -0.101 (158), 2021 -0.064 (168), 2022 -0.189 (159), 2023 -0.093 (173), 2024 -0.042 (175), 2025 +0.063 (164), 2026 +0.045 (152).

Sensibilidad (R neto medio y t): colchón 0 % -0.068 (t -2.50), colchón 50 % -0.059 (t -2.22), objetivo 1,5:1 -0.042 (t -1.28), objetivo 2:1 -0.027 (t -0.72).

### ORB 01:15–01:30

Rotura con cuerpo desde las 01:30 hasta las 07:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.105 R; ancho medio del ORB 0.10 %; cómo terminan: objetivo 699, stop 640, por tiempo 21.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1360 | 51.8 % | -0.064 | -86.6 | 0.88 | -129.3 | -2.34 |
| Sin costes | 1360 | 51.9 % | +0.041 | +55.6 | 1.09 | -63.0 | +1.52 |
| Long | 778 | 52.6 % | -0.054 | -42.1 | 0.90 | -66.8 | -1.51 |
| Short | 582 | 50.7 % | -0.076 | -44.5 | 0.86 | -69.5 | -1.84 |
| 1.ª mitad | 680 | 47.4 % | -0.154 | -105.0 | 0.73 | -126.0 | -4.01 |
| 2.ª mitad | 680 | 56.2 % | +0.027 | +18.4 | 1.06 | -16.7 | +0.71 |

Por año (R neto medio y operaciones): 2018 +0.111 (54), 2019 -0.330 (145), 2020 -0.107 (175), 2021 -0.165 (170), 2022 -0.126 (165), 2023 -0.016 (163), 2024 -0.003 (172), 2025 +0.021 (179), 2026 +0.160 (137).

Sensibilidad (R neto medio y t): colchón 0 % -0.082 (t -3.01), colchón 50 % -0.050 (t -1.87), objetivo 1,5:1 -0.064 (t -1.93), objetivo 2:1 -0.068 (t -1.81).

### ORB 01:30–01:45

Rotura con cuerpo desde las 01:45 hasta las 07:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.097 R; ancho medio del ORB 0.11 %; cómo terminan: objetivo 696, stop 645, por tiempo 32.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1373 | 51.6 % | -0.062 | -85.1 | 0.88 | -120.1 | -2.31 |
| Sin costes | 1373 | 51.7 % | +0.035 | +48.3 | 1.07 | -37.7 | +1.32 |
| Long | 797 | 53.3 % | -0.036 | -28.9 | 0.93 | -51.8 | -1.03 |
| Short | 576 | 49.3 % | -0.098 | -56.2 | 0.82 | -73.9 | -2.37 |
| 1.ª mitad | 687 | 49.2 % | -0.112 | -77.2 | 0.79 | -102.0 | -2.97 |
| 2.ª mitad | 686 | 54.1 % | -0.012 | -7.9 | 0.98 | -31.9 | -0.30 |

Por año (R neto medio y operaciones): 2018 +0.102 (51), 2019 -0.205 (171), 2020 -0.112 (172), 2021 -0.064 (165), 2022 -0.126 (164), 2023 -0.006 (165), 2024 -0.066 (168), 2025 -0.027 (172), 2026 +0.083 (145).

Sensibilidad (R neto medio y t): colchón 0 % -0.055 (t -2.04), colchón 50 % -0.050 (t -1.90), objetivo 1,5:1 -0.054 (t -1.64), objetivo 2:1 -0.074 (t -2.01).

### ORB 01:45–02:00

Rotura con cuerpo desde las 02:00 hasta las 08:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.091 R; ancho medio del ORB 0.10 %; cómo terminan: objetivo 651, stop 675, por tiempo 24.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1350 | 49.0 % | -0.108 | -145.8 | 0.80 | -154.7 | -3.99 |
| Sin costes | 1350 | 49.0 % | -0.017 | -23.1 | 0.97 | -45.8 | -0.63 |
| Long | 746 | 51.6 % | -0.060 | -44.7 | 0.89 | -55.4 | -1.65 |
| Short | 604 | 45.9 % | -0.168 | -101.2 | 0.71 | -106.2 | -4.15 |
| 1.ª mitad | 675 | 47.7 % | -0.134 | -90.7 | 0.76 | -101.5 | -3.52 |
| 2.ª mitad | 675 | 50.4 % | -0.082 | -55.1 | 0.85 | -62.4 | -2.13 |

Por año (R neto medio y operaciones): 2018 -0.244 (52), 2019 -0.134 (149), 2020 -0.102 (171), 2021 -0.107 (160), 2022 -0.177 (162), 2023 -0.059 (179), 2024 -0.072 (156), 2025 -0.059 (174), 2026 -0.121 (147).

Sensibilidad (R neto medio y t): colchón 0 % -0.107 (t -3.96), colchón 50 % -0.087 (t -3.25), objetivo 1,5:1 -0.097 (t -2.95), objetivo 2:1 -0.073 (t -1.95).

