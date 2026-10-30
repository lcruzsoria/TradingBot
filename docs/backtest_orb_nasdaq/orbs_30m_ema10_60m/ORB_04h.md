# ORB de 30 min de las 04:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 04:00–04:30 | 1586 | 51.3 | -0.018 | -0.75 | +0.024 | 0.042 | no |
| 04:15–04:45 | 1482 | 49.3 | -0.058 | -2.26 | -0.010 | 0.048 | no |
| 04:30–05:00 | 1470 | 48.8 | -0.077 | -2.97 | -0.023 | 0.053 | no |
| 04:45–05:15 | 1429 | 48.8 | -0.076 | -2.91 | -0.023 | 0.053 | no |

## Detalle

### ORB 04:00–04:30

Rotura con cuerpo desde las 04:30 hasta las 10:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.042 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 768, stop 732, por tiempo 86.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1586 | 51.3 % | -0.018 | -29.1 | 0.96 | -76.0 | -0.75 |
| Sin costes | 1586 | 51.3 % | +0.024 | +38.3 | 1.05 | -39.9 | +0.98 |
| Long | 884 | 52.1 % | -0.009 | -7.5 | 0.98 | -39.5 | -0.26 |
| Short | 702 | 50.1 % | -0.031 | -21.6 | 0.94 | -57.4 | -0.83 |
| 1.ª mitad | 793 | 49.3 % | -0.066 | -52.5 | 0.87 | -57.4 | -1.90 |
| 2.ª mitad | 793 | 53.2 % | +0.029 | +23.4 | 1.06 | -26.1 | +0.85 |

Por año (R neto medio y operaciones): 2018 -0.009 (54), 2019 -0.109 (203), 2020 -0.028 (186), 2021 -0.114 (194), 2022 -0.003 (206), 2023 -0.125 (197), 2024 +0.121 (203), 2025 +0.086 (195), 2026 +0.032 (148).

Sensibilidad (R neto medio y t): colchón 0 % -0.028 (t -1.13), colchón 50 % -0.010 (t -0.40), objetivo 1,5:1 -0.023 (t -0.77), objetivo 2:1 -0.024 (t -0.73).

### ORB 04:15–04:45

Rotura con cuerpo desde las 04:45 hasta las 10:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.048 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 714, stop 726, por tiempo 42.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1482 | 49.3 % | -0.058 | -85.9 | 0.89 | -103.2 | -2.26 |
| Sin costes | 1482 | 49.4 % | -0.010 | -14.2 | 0.98 | -53.7 | -0.37 |
| Long | 857 | 48.5 % | -0.080 | -68.8 | 0.85 | -80.2 | -2.38 |
| Short | 625 | 50.2 % | -0.027 | -17.1 | 0.95 | -42.6 | -0.69 |
| 1.ª mitad | 741 | 47.8 % | -0.091 | -67.8 | 0.83 | -74.4 | -2.52 |
| 2.ª mitad | 741 | 50.7 % | -0.024 | -18.1 | 0.95 | -34.8 | -0.67 |

Por año (R neto medio y operaciones): 2018 +0.044 (54), 2019 -0.095 (179), 2020 -0.112 (183), 2021 -0.088 (184), 2022 -0.160 (189), 2023 -0.006 (177), 2024 +0.075 (194), 2025 -0.127 (184), 2026 +0.041 (138).

Sensibilidad (R neto medio y t): colchón 0 % -0.063 (t -2.46), colchón 50 % -0.052 (t -2.04), objetivo 1,5:1 -0.057 (t -1.85), objetivo 2:1 -0.048 (t -1.38).

### ORB 04:30–05:00

Rotura con cuerpo desde las 05:00 hasta las 11:00; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.053 R; ancho medio del ORB 0.20 %; cómo terminan: objetivo 701, stop 734, por tiempo 35.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1470 | 48.8 % | -0.077 | -112.8 | 0.86 | -132.1 | -2.97 |
| Sin costes | 1470 | 48.9 % | -0.023 | -34.4 | 0.95 | -66.1 | -0.91 |
| Long | 846 | 48.1 % | -0.099 | -83.7 | 0.82 | -100.5 | -2.90 |
| Short | 624 | 49.7 % | -0.047 | -29.2 | 0.91 | -38.4 | -1.18 |
| 1.ª mitad | 735 | 48.6 % | -0.083 | -60.7 | 0.84 | -75.1 | -2.27 |
| 2.ª mitad | 735 | 49.0 % | -0.071 | -52.2 | 0.87 | -58.0 | -1.93 |

Por año (R neto medio y operaciones): 2018 +0.101 (48), 2019 -0.105 (187), 2020 -0.228 (188), 2021 +0.008 (180), 2022 -0.085 (181), 2023 -0.006 (179), 2024 -0.032 (193), 2025 -0.188 (178), 2026 -0.003 (136).

Sensibilidad (R neto medio y t): colchón 0 % -0.082 (t -3.15), colchón 50 % -0.085 (t -3.29), objetivo 1,5:1 -0.096 (t -3.10), objetivo 2:1 -0.077 (t -2.18).

### ORB 04:45–05:15

Rotura con cuerpo desde las 05:15 hasta las 11:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.053 R; ancho medio del ORB 0.20 %; cómo terminan: objetivo 684, stop 719, por tiempo 26.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1429 | 48.8 % | -0.076 | -109.1 | 0.86 | -129.1 | -2.91 |
| Sin costes | 1429 | 49.0 % | -0.023 | -32.8 | 0.95 | -66.8 | -0.87 |
| Long | 838 | 47.7 % | -0.108 | -90.7 | 0.80 | -102.8 | -3.16 |
| Short | 591 | 50.4 % | -0.031 | -18.4 | 0.94 | -36.4 | -0.76 |
| 1.ª mitad | 715 | 49.8 % | -0.062 | -44.5 | 0.88 | -58.4 | -1.68 |
| 2.ª mitad | 714 | 47.9 % | -0.091 | -64.6 | 0.83 | -78.2 | -2.43 |

Por año (R neto medio y operaciones): 2018 +0.054 (46), 2019 -0.023 (183), 2020 -0.141 (179), 2021 -0.062 (177), 2022 -0.025 (168), 2023 -0.185 (180), 2024 -0.043 (181), 2025 -0.117 (171), 2026 -0.042 (144).

Sensibilidad (R neto medio y t): colchón 0 % -0.105 (t -3.98), colchón 50 % -0.056 (t -2.15), objetivo 1,5:1 -0.080 (t -2.51), objetivo 2:1 -0.099 (t -2.76).

