# ORB de 30 min de las 05:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 05:00–05:30 | 1423 | 50.3 | -0.045 | -1.72 | +0.008 | 0.054 | no |
| 05:15–05:45 | 1429 | 48.5 | -0.086 | -3.29 | -0.031 | 0.056 | no |
| 05:30–06:00 | 1414 | 48.2 | -0.094 | -3.55 | -0.037 | 0.057 | no |
| 05:45–06:15 | 1459 | 50.0 | -0.054 | -2.08 | +0.001 | 0.056 | no |

## Detalle

### ORB 05:00–05:30

Rotura con cuerpo desde las 05:30 hasta las 11:30; a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.054 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 705, stop 694, por tiempo 24.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1423 | 50.3 % | -0.045 | -64.5 | 0.91 | -97.2 | -1.72 |
| Sin costes | 1423 | 50.4 % | +0.008 | +11.9 | 1.02 | -40.0 | +0.32 |
| Long | 821 | 49.0 % | -0.077 | -62.9 | 0.86 | -85.0 | -2.21 |
| Short | 602 | 52.2 % | -0.003 | -1.6 | 0.99 | -22.8 | -0.06 |
| 1.ª mitad | 712 | 50.0 % | -0.053 | -37.9 | 0.90 | -59.3 | -1.43 |
| 2.ª mitad | 711 | 50.6 % | -0.037 | -26.6 | 0.93 | -47.9 | -1.00 |

Por año (R neto medio y operaciones): 2018 +0.155 (47), 2019 -0.040 (192), 2020 -0.174 (178), 2021 -0.039 (176), 2022 -0.042 (165), 2023 -0.120 (174), 2024 +0.030 (182), 2025 -0.062 (168), 2026 +0.046 (141).

Sensibilidad (R neto medio y t): colchón 0 % -0.074 (t -2.80), colchón 50 % -0.047 (t -1.78), objetivo 1,5:1 -0.057 (t -1.78), objetivo 2:1 -0.088 (t -2.43).

### ORB 05:15–05:45

Rotura con cuerpo desde las 05:45 hasta las 11:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.056 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 680, stop 725, por tiempo 24.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1429 | 48.5 % | -0.086 | -123.6 | 0.84 | -153.7 | -3.29 |
| Sin costes | 1429 | 48.6 % | -0.031 | -44.2 | 0.94 | -83.4 | -1.18 |
| Long | 816 | 47.7 % | -0.109 | -88.8 | 0.80 | -107.8 | -3.13 |
| Short | 613 | 49.6 % | -0.057 | -34.7 | 0.89 | -55.9 | -1.41 |
| 1.ª mitad | 715 | 47.7 % | -0.105 | -75.3 | 0.81 | -90.3 | -2.84 |
| 2.ª mitad | 714 | 49.3 % | -0.068 | -48.3 | 0.87 | -71.9 | -1.81 |

Por año (R neto medio y operaciones): 2018 +0.024 (51), 2019 -0.118 (182), 2020 -0.246 (165), 2021 -0.007 (180), 2022 -0.129 (170), 2023 -0.143 (180), 2024 -0.082 (178), 2025 -0.069 (182), 2026 +0.094 (141).

Sensibilidad (R neto medio y t): colchón 0 % -0.118 (t -4.48), colchón 50 % -0.064 (t -2.44), objetivo 1,5:1 -0.107 (t -3.38), objetivo 2:1 -0.114 (t -3.16).

### ORB 05:30–06:00

Rotura con cuerpo desde las 06:00 hasta las 12:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.057 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 672, stop 724, por tiempo 18.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1414 | 48.2 % | -0.094 | -132.7 | 0.83 | -143.4 | -3.55 |
| Sin costes | 1414 | 48.2 % | -0.037 | -52.3 | 0.93 | -80.3 | -1.40 |
| Long | 789 | 47.8 % | -0.110 | -86.6 | 0.80 | -90.1 | -3.10 |
| Short | 625 | 48.6 % | -0.074 | -46.1 | 0.86 | -59.0 | -1.86 |
| 1.ª mitad | 707 | 46.7 % | -0.125 | -88.4 | 0.78 | -96.4 | -3.35 |
| 2.ª mitad | 707 | 49.6 % | -0.063 | -44.4 | 0.88 | -50.3 | -1.67 |

Por año (R neto medio y operaciones): 2018 -0.009 (50), 2019 -0.143 (191), 2020 -0.098 (156), 2021 -0.133 (168), 2022 -0.152 (176), 2023 -0.160 (180), 2024 +0.061 (181), 2025 -0.111 (175), 2026 -0.026 (137).

Sensibilidad (R neto medio y t): colchón 0 % -0.117 (t -4.43), colchón 50 % -0.086 (t -3.26), objetivo 1,5:1 -0.069 (t -2.14), objetivo 2:1 -0.090 (t -2.46).

### ORB 05:45–06:15

Rotura con cuerpo desde las 06:15 hasta las 12:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.056 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 724, stop 720, por tiempo 15.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1459 | 50.0 % | -0.054 | -79.1 | 0.90 | -90.4 | -2.08 |
| Sin costes | 1459 | 50.0 % | +0.001 | +1.9 | 1.00 | -34.9 | +0.05 |
| Long | 833 | 50.1 % | -0.061 | -50.6 | 0.89 | -56.0 | -1.75 |
| Short | 626 | 50.0 % | -0.046 | -28.5 | 0.91 | -40.6 | -1.15 |
| 1.ª mitad | 730 | 49.5 % | -0.066 | -47.8 | 0.88 | -59.9 | -1.78 |
| 2.ª mitad | 729 | 50.6 % | -0.043 | -31.3 | 0.92 | -40.8 | -1.16 |

Por año (R neto medio y operaciones): 2018 -0.051 (54), 2019 -0.229 (180), 2020 -0.008 (160), 2021 -0.027 (179), 2022 +0.018 (179), 2023 -0.097 (188), 2024 -0.015 (178), 2025 -0.081 (187), 2026 +0.025 (154).

Sensibilidad (R neto medio y t): colchón 0 % -0.080 (t -3.04), colchón 50 % -0.053 (t -2.03), objetivo 1,5:1 -0.068 (t -2.15), objetivo 2:1 -0.065 (t -1.79).

