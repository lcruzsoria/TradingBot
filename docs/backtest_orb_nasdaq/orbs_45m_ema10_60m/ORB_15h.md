# ORB de 45 min de las 15:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 15:00–15:45 | 1343 | 48.7 | -0.003 | -0.16 | +0.020 | 0.023 | no |
| 15:15–16:00 | 1235 | 48.8 | -0.013 | -0.84 | +0.008 | 0.021 | no |
| 15:30–16:15 | 1173 | 47.7 | -0.006 | -0.38 | +0.016 | 0.022 | no |
| 15:45–16:30 | 673 | 47.5 | -0.025 | -1.17 | -0.001 | 0.023 | no |

## Detalle

### ORB 15:00–15:45

Rotura con cuerpo desde las 15:45 hasta las 21:45; a esa hora se cierra. ORB completos: 2025; con rotura: 1804.

**No pasa los criterios**. Coste medio 0.023 R; ancho medio del ORB 0.46 %; cómo terminan: objetivo 210, stop 177, por tiempo 956.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1343 | 48.7 % | -0.003 | -3.7 | 0.99 | -18.9 | -0.16 |
| Sin costes | 1343 | 50.6 % | +0.020 | +27.0 | 1.08 | -14.2 | +1.18 |
| Long | 753 | 52.1 % | +0.027 | +20.4 | 1.11 | -13.2 | +1.19 |
| Short | 590 | 44.4 % | -0.041 | -24.1 | 0.85 | -28.5 | -1.60 |
| 1.ª mitad | 672 | 48.5 % | +0.013 | +8.7 | 1.05 | -10.5 | +0.54 |
| 2.ª mitad | 671 | 48.9 % | -0.018 | -12.4 | 0.93 | -18.9 | -0.76 |

Por año (R neto medio y operaciones): 2018 -0.093 (51), 2019 +0.016 (180), 2020 +0.064 (182), 2021 +0.001 (178), 2022 +0.005 (161), 2023 -0.083 (151), 2024 +0.016 (163), 2025 +0.070 (143), 2026 -0.107 (134).

Sensibilidad (R neto medio y t): colchón 0 % +0.004 (t +0.24), colchón 50 % -0.010 (t -0.70), objetivo 1,5:1 -0.008 (t -0.43), objetivo 2:1 -0.010 (t -0.55).

### ORB 15:15–16:00

Rotura con cuerpo desde las 16:00 hasta las 22:00; a esa hora se cierra. ORB completos: 2024; con rotura: 1585.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.50 %; cómo terminan: objetivo 128, stop 117, por tiempo 990.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1235 | 48.8 % | -0.013 | -15.9 | 0.94 | -33.2 | -0.84 |
| Sin costes | 1235 | 51.0 % | +0.008 | +10.4 | 1.04 | -19.5 | +0.55 |
| Long | 712 | 53.2 % | +0.017 | +12.1 | 1.09 | -13.1 | +0.83 |
| Short | 523 | 42.8 % | -0.054 | -28.0 | 0.77 | -36.9 | -2.28 |
| 1.ª mitad | 618 | 52.6 % | +0.010 | +6.5 | 1.05 | -9.3 | +0.48 |
| 2.ª mitad | 617 | 45.1 % | -0.036 | -22.4 | 0.84 | -28.4 | -1.66 |

Por año (R neto medio y operaciones): 2018 -0.030 (45), 2019 +0.039 (179), 2020 +0.023 (166), 2021 -0.005 (146), 2022 -0.045 (145), 2023 -0.061 (118), 2024 +0.017 (147), 2025 -0.010 (150), 2026 -0.085 (139).

Sensibilidad (R neto medio y t): colchón 0 % -0.017 (t -0.99), colchón 50 % -0.015 (t -1.10), objetivo 1,5:1 -0.004 (t -0.25), objetivo 2:1 -0.005 (t -0.27).

### ORB 15:30–16:15

Rotura con cuerpo desde las 16:15 hasta las 22:15; a esa hora se cierra. ORB completos: 2023; con rotura: 1481.

**No pasa los criterios**. Coste medio 0.022 R; ancho medio del ORB 0.51 %; cómo terminan: objetivo 110, stop 91, por tiempo 972.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1173 | 47.7 % | -0.006 | -6.6 | 0.97 | -26.9 | -0.38 |
| Sin costes | 1173 | 49.4 % | +0.016 | +19.0 | 1.09 | -18.6 | +1.08 |
| Long | 677 | 50.1 % | +0.003 | +2.0 | 1.02 | -11.8 | +0.15 |
| Short | 496 | 44.4 % | -0.017 | -8.6 | 0.92 | -21.8 | -0.73 |
| 1.ª mitad | 587 | 49.2 % | +0.019 | +11.4 | 1.11 | -8.3 | +0.93 |
| 2.ª mitad | 586 | 46.1 % | -0.031 | -18.0 | 0.86 | -26.9 | -1.43 |

Por año (R neto medio y operaciones): 2018 -0.002 (32), 2019 +0.017 (171), 2020 +0.057 (168), 2021 -0.001 (143), 2022 -0.009 (131), 2023 -0.062 (116), 2024 -0.006 (134), 2025 -0.023 (152), 2026 -0.049 (126).

Sensibilidad (R neto medio y t): colchón 0 % -0.007 (t -0.43), colchón 50 % -0.006 (t -0.46), objetivo 1,5:1 -0.006 (t -0.40), objetivo 2:1 -0.003 (t -0.19).

### ORB 15:45–16:30

Rotura con cuerpo desde las 16:30 hasta las 22:30; a esa hora se cierra. ORB completos: 1236; con rotura: 893.

**No pasa los criterios**. Coste medio 0.023 R; ancho medio del ORB 0.45 %; cómo terminan: objetivo 72, stop 67, por tiempo 534.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 673 | 47.5 % | -0.025 | -16.6 | 0.89 | -30.8 | -1.17 |
| Sin costes | 673 | 49.2 % | -0.001 | -0.9 | 0.99 | -24.4 | -0.07 |
| Long | 382 | 51.3 % | -0.012 | -4.7 | 0.94 | -14.8 | -0.45 |
| Short | 291 | 42.6 % | -0.041 | -11.9 | 0.83 | -20.7 | -1.23 |
| 1.ª mitad | 337 | 49.9 % | +0.020 | +6.8 | 1.12 | -10.2 | +0.81 |
| 2.ª mitad | 336 | 45.2 % | -0.070 | -23.5 | 0.75 | -30.8 | -2.07 |

Por año (R neto medio y operaciones): 2021 +0.026 (22), 2022 +0.014 (123), 2023 -0.033 (124), 2024 -0.006 (132), 2025 -0.022 (150), 2026 -0.088 (122).

Sensibilidad (R neto medio y t): colchón 0 % -0.041 (t -1.77), colchón 50 % -0.019 (t -1.06), objetivo 1,5:1 -0.020 (t -0.92), objetivo 2:1 -0.022 (t -0.95).

