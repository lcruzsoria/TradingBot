# ORB de 60 min de las 00:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 00:00–01:00 | 1511 | 50.0 | -0.052 | -2.10 | +0.012 | 0.064 | no |
| 00:15–01:15 | 1545 | 50.2 | -0.045 | -1.87 | +0.014 | 0.060 | no |
| 00:30–01:30 | 1568 | 50.6 | -0.024 | -1.00 | +0.032 | 0.056 | no |
| 00:45–01:45 | 1585 | 49.8 | -0.053 | -2.27 | -0.001 | 0.052 | no |

## Detalle

### ORB 00:00–01:00

Rotura con cuerpo desde las 01:00 hasta las 07:00; a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.064 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 693, stop 675, por tiempo 143.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1511 | 50.0 % | -0.052 | -78.5 | 0.89 | -103.4 | -2.10 |
| Sin costes | 1511 | 50.2 % | +0.012 | +18.8 | 1.03 | -49.8 | +0.50 |
| Long | 870 | 52.0 % | -0.022 | -19.2 | 0.95 | -44.4 | -0.68 |
| Short | 641 | 47.3 % | -0.093 | -59.3 | 0.82 | -67.8 | -2.43 |
| 1.ª mitad | 756 | 46.2 % | -0.115 | -86.7 | 0.78 | -94.2 | -3.28 |
| 2.ª mitad | 755 | 53.8 % | +0.011 | +8.2 | 1.02 | -40.4 | +0.31 |

Por año (R neto medio y operaciones): 2018 -0.048 (56), 2019 -0.155 (181), 2020 -0.039 (182), 2021 -0.125 (180), 2022 -0.123 (173), 2023 -0.001 (179), 2024 -0.064 (198), 2025 +0.034 (191), 2026 +0.056 (171).

Sensibilidad (R neto medio y t): colchón 0 % -0.051 (t -2.04), colchón 50 % -0.029 (t -1.23), objetivo 1,5:1 -0.037 (t -1.28), objetivo 2:1 -0.011 (t -0.33).

### ORB 00:15–01:15

Rotura con cuerpo desde las 01:15 hasta las 07:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.060 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 700, stop 672, por tiempo 173.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1545 | 50.2 % | -0.045 | -70.2 | 0.91 | -88.9 | -1.87 |
| Sin costes | 1545 | 50.6 % | +0.014 | +22.0 | 1.03 | -41.4 | +0.59 |
| Long | 862 | 53.0 % | +0.005 | +4.3 | 1.01 | -36.6 | +0.15 |
| Short | 683 | 46.6 % | -0.109 | -74.4 | 0.79 | -78.3 | -2.96 |
| 1.ª mitad | 773 | 48.5 % | -0.075 | -57.8 | 0.85 | -66.8 | -2.19 |
| 2.ª mitad | 772 | 51.8 % | -0.016 | -12.4 | 0.97 | -48.4 | -0.46 |

Por año (R neto medio y operaciones): 2018 -0.092 (61), 2019 -0.076 (178), 2020 -0.017 (190), 2021 -0.057 (194), 2022 -0.117 (175), 2023 +0.016 (186), 2024 -0.134 (199), 2025 -0.024 (191), 2026 +0.071 (171).

Sensibilidad (R neto medio y t): colchón 0 % -0.046 (t -1.88), colchón 50 % -0.035 (t -1.48), objetivo 1,5:1 -0.049 (t -1.71), objetivo 2:1 -0.021 (t -0.64).

### ORB 00:30–01:30

Rotura con cuerpo desde las 01:30 hasta las 07:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.056 R; ancho medio del ORB 0.20 %; cómo terminan: objetivo 716, stop 655, por tiempo 197.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1568 | 50.6 % | -0.024 | -37.7 | 0.95 | -70.9 | -1.00 |
| Sin costes | 1568 | 51.0 % | +0.032 | +50.1 | 1.07 | -39.9 | +1.34 |
| Long | 889 | 52.1 % | -0.012 | -10.4 | 0.97 | -42.6 | -0.37 |
| Short | 679 | 48.6 % | -0.040 | -27.3 | 0.92 | -62.5 | -1.10 |
| 1.ª mitad | 784 | 48.3 % | -0.059 | -46.0 | 0.88 | -58.5 | -1.74 |
| 2.ª mitad | 784 | 52.8 % | +0.011 | +8.2 | 1.02 | -32.5 | +0.31 |

Por año (R neto medio y operaciones): 2018 +0.038 (54), 2019 -0.050 (185), 2020 -0.031 (190), 2021 -0.080 (198), 2022 -0.077 (182), 2023 +0.018 (191), 2024 -0.109 (200), 2025 +0.029 (198), 2026 +0.105 (170).

Sensibilidad (R neto medio y t): colchón 0 % -0.029 (t -1.19), colchón 50 % -0.031 (t -1.36), objetivo 1,5:1 -0.042 (t -1.51), objetivo 2:1 -0.025 (t -0.80).

### ORB 00:45–01:45

Rotura con cuerpo desde las 01:45 hasta las 07:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2089.

**No pasa los criterios**. Coste medio 0.052 R; ancho medio del ORB 0.21 %; cómo terminan: objetivo 669, stop 679, por tiempo 237.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1585 | 49.8 % | -0.053 | -84.6 | 0.89 | -100.7 | -2.27 |
| Sin costes | 1585 | 50.2 % | -0.001 | -2.4 | 1.00 | -45.5 | -0.06 |
| Long | 908 | 51.8 % | -0.039 | -35.6 | 0.92 | -54.7 | -1.27 |
| Short | 677 | 47.3 % | -0.072 | -49.0 | 0.85 | -64.2 | -1.99 |
| 1.ª mitad | 793 | 49.2 % | -0.061 | -48.2 | 0.87 | -64.2 | -1.82 |
| 2.ª mitad | 792 | 50.5 % | -0.046 | -36.4 | 0.90 | -61.4 | -1.38 |

Por año (R neto medio y operaciones): 2018 -0.029 (55), 2019 -0.049 (183), 2020 -0.000 (193), 2021 -0.144 (195), 2022 -0.062 (186), 2023 +0.026 (199), 2024 -0.112 (203), 2025 -0.115 (200), 2026 +0.037 (171).

Sensibilidad (R neto medio y t): colchón 0 % -0.039 (t -1.63), colchón 50 % -0.042 (t -1.89), objetivo 1,5:1 -0.058 (t -2.13), objetivo 2:1 -0.061 (t -2.03).

