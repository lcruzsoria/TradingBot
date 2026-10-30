# ORB de 60 min de las 15:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 15:00–16:00 | 1219 | 48.6 | -0.014 | -0.99 | +0.005 | 0.019 | no |
| 15:15–16:15 | 1146 | 47.6 | -0.015 | -1.03 | +0.005 | 0.020 | no |
| 15:30–16:30 | 660 | 46.5 | -0.033 | -1.72 | -0.013 | 0.020 | no |
| 15:45–16:45 | 656 | 46.5 | -0.028 | -1.32 | -0.006 | 0.022 | no |

## Detalle

### ORB 15:00–16:00

Rotura con cuerpo desde las 16:00 hasta las 22:00; a esa hora se cierra. ORB completos: 2024; con rotura: 1504.

**No pasa los criterios**. Coste medio 0.019 R; ancho medio del ORB 0.56 %; cómo terminan: objetivo 103, stop 99, por tiempo 1017.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1219 | 48.6 % | -0.014 | -17.6 | 0.93 | -28.4 | -0.99 |
| Sin costes | 1219 | 51.0 % | +0.005 | +5.8 | 1.03 | -17.6 | +0.33 |
| Long | 702 | 53.7 % | +0.014 | +9.8 | 1.08 | -10.9 | +0.72 |
| Short | 517 | 41.6 % | -0.053 | -27.3 | 0.76 | -34.8 | -2.39 |
| 1.ª mitad | 610 | 50.5 % | -0.003 | -1.6 | 0.99 | -11.3 | -0.13 |
| 2.ª mitad | 609 | 46.6 % | -0.026 | -16.0 | 0.87 | -23.5 | -1.26 |

Por año (R neto medio y operaciones): 2018 -0.061 (45), 2019 +0.028 (179), 2020 -0.006 (169), 2021 +0.017 (145), 2022 -0.043 (139), 2023 -0.049 (111), 2024 +0.019 (140), 2025 -0.004 (149), 2026 -0.082 (142).

Sensibilidad (R neto medio y t): colchón 0 % -0.017 (t -1.09), colchón 50 % -0.014 (t -1.14), objetivo 1,5:1 -0.009 (t -0.59), objetivo 2:1 -0.008 (t -0.52).

### ORB 15:15–16:15

Rotura con cuerpo desde las 16:15 hasta las 22:15; a esa hora se cierra. ORB completos: 2023; con rotura: 1406.

**No pasa los criterios**. Coste medio 0.020 R; ancho medio del ORB 0.57 %; cómo terminan: objetivo 84, stop 74, por tiempo 988.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1146 | 47.6 % | -0.015 | -16.7 | 0.92 | -33.1 | -1.03 |
| Sin costes | 1146 | 48.8 % | +0.005 | +5.7 | 1.03 | -20.2 | +0.35 |
| Long | 655 | 51.1 % | +0.004 | +2.7 | 1.02 | -9.9 | +0.22 |
| Short | 491 | 42.8 % | -0.039 | -19.4 | 0.80 | -29.7 | -1.83 |
| 1.ª mitad | 573 | 49.2 % | +0.010 | +5.4 | 1.06 | -9.2 | +0.49 |
| 2.ª mitad | 573 | 45.9 % | -0.039 | -22.1 | 0.81 | -30.4 | -1.91 |

Por año (R neto medio y operaciones): 2018 +0.046 (31), 2019 +0.014 (167), 2020 +0.021 (167), 2021 +0.007 (132), 2022 -0.037 (132), 2023 -0.079 (113), 2024 -0.013 (129), 2025 -0.033 (148), 2026 -0.035 (127).

Sensibilidad (R neto medio y t): colchón 0 % -0.018 (t -1.14), colchón 50 % -0.015 (t -1.24), objetivo 1,5:1 -0.015 (t -1.00), objetivo 2:1 -0.010 (t -0.65).

### ORB 15:30–16:30

Rotura con cuerpo desde las 16:30 hasta las 22:30; a esa hora se cierra. ORB completos: 1236; con rotura: 839.

**No pasa los criterios**. Coste medio 0.020 R; ancho medio del ORB 0.51 %; cómo terminan: objetivo 50, stop 50, por tiempo 560.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 660 | 46.5 % | -0.033 | -21.8 | 0.84 | -31.5 | -1.72 |
| Sin costes | 660 | 48.5 % | -0.013 | -8.3 | 0.93 | -25.8 | -0.66 |
| Long | 378 | 51.1 % | -0.013 | -5.0 | 0.93 | -15.2 | -0.53 |
| Short | 282 | 40.4 % | -0.060 | -16.8 | 0.73 | -22.1 | -1.96 |
| 1.ª mitad | 330 | 48.8 % | +0.012 | +4.0 | 1.09 | -9.6 | +0.57 |
| 2.ª mitad | 330 | 44.2 % | -0.078 | -25.8 | 0.70 | -31.5 | -2.48 |

Por año (R neto medio y operaciones): 2021 +0.066 (21), 2022 -0.015 (125), 2023 -0.041 (114), 2024 -0.017 (129), 2025 -0.041 (145), 2026 -0.068 (126).

Sensibilidad (R neto medio y t): colchón 0 % -0.040 (t -1.84), colchón 50 % -0.020 (t -1.21), objetivo 1,5:1 -0.025 (t -1.24), objetivo 2:1 -0.024 (t -1.14).

### ORB 15:45–16:45

Rotura con cuerpo desde las 16:45 hasta las 22:45; a esa hora se cierra. ORB completos: 1236; con rotura: 862.

**No pasa los criterios**. Coste medio 0.022 R; ancho medio del ORB 0.47 %; cómo terminan: objetivo 68, stop 67, por tiempo 521.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 656 | 46.5 % | -0.028 | -18.4 | 0.87 | -30.4 | -1.32 |
| Sin costes | 656 | 48.2 % | -0.006 | -3.7 | 0.97 | -24.2 | -0.27 |
| Long | 369 | 50.4 % | -0.017 | -6.1 | 0.92 | -16.3 | -0.63 |
| Short | 287 | 41.5 % | -0.043 | -12.3 | 0.83 | -20.0 | -1.24 |
| 1.ª mitad | 328 | 47.6 % | +0.023 | +7.5 | 1.15 | -8.2 | +0.93 |
| 2.ª mitad | 328 | 45.4 % | -0.079 | -25.9 | 0.73 | -30.4 | -2.30 |

Por año (R neto medio y operaciones): 2021 +0.097 (21), 2022 +0.001 (120), 2023 -0.010 (117), 2024 -0.014 (127), 2025 -0.046 (149), 2026 -0.088 (122).

Sensibilidad (R neto medio y t): colchón 0 % -0.045 (t -1.92), colchón 50 % -0.022 (t -1.21), objetivo 1,5:1 -0.024 (t -1.07), objetivo 2:1 -0.024 (t -1.07).

