# ORB de 60 min de las 05:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 05:00–06:00 | 1576 | 50.0 | -0.039 | -1.57 | +0.001 | 0.040 | no |
| 05:15–06:15 | 1591 | 50.3 | -0.028 | -1.13 | +0.012 | 0.040 | no |
| 05:30–06:30 | 1606 | 50.0 | -0.034 | -1.39 | +0.006 | 0.040 | no |
| 05:45–06:45 | 1601 | 51.2 | -0.014 | -0.59 | +0.026 | 0.040 | no |

## Detalle

### ORB 05:00–06:00

Rotura con cuerpo desde las 06:00 hasta las 12:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.040 R; ancho medio del ORB 0.27 %; cómo terminan: objetivo 747, stop 749, por tiempo 80.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1576 | 50.0 % | -0.039 | -61.2 | 0.92 | -84.6 | -1.57 |
| Sin costes | 1576 | 50.1 % | +0.001 | +1.6 | 1.00 | -47.0 | +0.04 |
| Long | 893 | 49.0 % | -0.064 | -57.5 | 0.88 | -75.6 | -1.96 |
| Short | 683 | 51.2 % | -0.005 | -3.7 | 0.99 | -20.9 | -0.15 |
| 1.ª mitad | 788 | 49.1 % | -0.054 | -42.5 | 0.89 | -59.9 | -1.56 |
| 2.ª mitad | 788 | 50.9 % | -0.024 | -18.7 | 0.95 | -32.5 | -0.67 |

Por año (R neto medio y operaciones): 2018 +0.068 (54), 2019 -0.060 (205), 2020 -0.090 (174), 2021 +0.002 (196), 2022 -0.155 (193), 2023 -0.069 (202), 2024 +0.042 (202), 2025 -0.005 (193), 2026 -0.007 (157).

Sensibilidad (R neto medio y t): colchón 0 % -0.067 (t -2.69), colchón 50 % -0.038 (t -1.58), objetivo 1,5:1 -0.042 (t -1.42), objetivo 2:1 -0.057 (t -1.70).

### ORB 05:15–06:15

Rotura con cuerpo desde las 06:15 hasta las 12:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.040 R; ancho medio del ORB 0.27 %; cómo terminan: objetivo 773, stop 751, por tiempo 67.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1591 | 50.3 % | -0.028 | -44.4 | 0.94 | -63.9 | -1.13 |
| Sin costes | 1591 | 50.5 % | +0.012 | +18.9 | 1.02 | -28.6 | +0.48 |
| Long | 913 | 50.2 % | -0.039 | -35.2 | 0.92 | -56.0 | -1.18 |
| Short | 678 | 50.4 % | -0.014 | -9.2 | 0.97 | -24.3 | -0.36 |
| 1.ª mitad | 796 | 49.7 % | -0.042 | -33.3 | 0.92 | -53.2 | -1.20 |
| 2.ª mitad | 795 | 50.8 % | -0.014 | -11.2 | 0.97 | -29.5 | -0.40 |

Por año (R neto medio y operaciones): 2018 +0.022 (56), 2019 -0.092 (200), 2020 -0.074 (177), 2021 -0.051 (202), 2022 +0.027 (196), 2023 -0.054 (204), 2024 +0.096 (194), 2025 -0.029 (199), 2026 -0.066 (163).

Sensibilidad (R neto medio y t): colchón 0 % -0.040 (t -1.62), colchón 50 % -0.034 (t -1.38), objetivo 1,5:1 -0.040 (t -1.36), objetivo 2:1 -0.043 (t -1.27).

### ORB 05:30–06:30

Rotura con cuerpo desde las 06:30 hasta las 12:30; a esa hora se cierra. ORB completos: 2095; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.040 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 775, stop 768, por tiempo 63.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1606 | 50.0 % | -0.034 | -54.7 | 0.93 | -65.8 | -1.39 |
| Sin costes | 1606 | 50.2 % | +0.006 | +10.3 | 1.01 | -35.4 | +0.26 |
| Long | 909 | 50.8 % | -0.027 | -24.2 | 0.95 | -43.4 | -0.81 |
| Short | 697 | 48.9 % | -0.044 | -30.5 | 0.91 | -38.3 | -1.18 |
| 1.ª mitad | 803 | 49.9 % | -0.039 | -31.7 | 0.92 | -42.3 | -1.13 |
| 2.ª mitad | 803 | 50.1 % | -0.029 | -23.1 | 0.94 | -36.2 | -0.83 |

Por año (R neto medio y operaciones): 2018 -0.035 (54), 2019 -0.064 (197), 2020 -0.005 (182), 2021 -0.079 (197), 2022 +0.020 (203), 2023 -0.129 (214), 2024 +0.058 (198), 2025 -0.018 (200), 2026 -0.050 (161).

Sensibilidad (R neto medio y t): colchón 0 % -0.039 (t -1.56), colchón 50 % -0.030 (t -1.26), objetivo 1,5:1 -0.043 (t -1.45), objetivo 2:1 -0.061 (t -1.83).

### ORB 05:45–06:45

Rotura con cuerpo desde las 06:45 hasta las 12:45; a esa hora se cierra. ORB completos: 2095; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.040 R; ancho medio del ORB 0.27 %; cómo terminan: objetivo 789, stop 748, por tiempo 64.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1601 | 51.2 % | -0.014 | -23.1 | 0.97 | -61.8 | -0.59 |
| Sin costes | 1601 | 51.2 % | +0.026 | +41.0 | 1.05 | -31.6 | +1.04 |
| Long | 920 | 51.3 % | -0.014 | -12.5 | 0.97 | -46.4 | -0.42 |
| Short | 681 | 51.1 % | -0.016 | -10.6 | 0.97 | -24.1 | -0.42 |
| 1.ª mitad | 801 | 50.8 % | -0.022 | -17.9 | 0.95 | -33.1 | -0.64 |
| 2.ª mitad | 800 | 51.6 % | -0.007 | -5.2 | 0.99 | -40.5 | -0.19 |

Por año (R neto medio y operaciones): 2018 -0.043 (57), 2019 -0.019 (195), 2020 -0.062 (190), 2021 -0.046 (201), 2022 +0.048 (195), 2023 -0.145 (203), 2024 +0.081 (193), 2025 +0.029 (198), 2026 +0.017 (169).

Sensibilidad (R neto medio y t): colchón 0 % -0.039 (t -1.58), colchón 50 % -0.026 (t -1.06), objetivo 1,5:1 -0.030 (t -1.00), objetivo 2:1 -0.048 (t -1.43).

