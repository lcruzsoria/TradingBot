# ORB de 60 min de las 19:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 19:00–20:00 | 1351 | 47.5 | -0.054 | -2.38 | -0.006 | 0.048 | no |
| 19:15–20:15 | 1411 | 49.3 | -0.026 | -1.22 | +0.018 | 0.044 | no |
| 19:30–20:30 | 1443 | 49.6 | -0.030 | -1.49 | +0.011 | 0.041 | no |
| 19:45–20:45 | 1495 | 48.2 | -0.028 | -1.45 | +0.012 | 0.040 | no |

## Detalle

### ORB 19:00–20:00

Rotura con cuerpo desde las 20:00 hasta las 02:00 (día siguiente); a esa hora se cierra. ORB completos: 2095; con rotura: 2059.

**No pasa los criterios**. Coste medio 0.048 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 428, stop 428, por tiempo 495.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1351 | 47.5 % | -0.054 | -72.9 | 0.87 | -86.2 | -2.38 |
| Sin costes | 1351 | 48.2 % | -0.006 | -8.6 | 0.98 | -43.4 | -0.28 |
| Long | 777 | 49.9 % | -0.026 | -20.3 | 0.93 | -37.3 | -0.89 |
| Short | 574 | 44.3 % | -0.092 | -52.5 | 0.79 | -59.6 | -2.56 |
| 1.ª mitad | 676 | 49.4 % | -0.024 | -16.2 | 0.94 | -25.9 | -0.74 |
| 2.ª mitad | 675 | 45.6 % | -0.084 | -56.7 | 0.80 | -60.4 | -2.64 |

Por año (R neto medio y operaciones): 2018 +0.156 (44), 2019 -0.080 (174), 2020 +0.009 (161), 2021 -0.034 (161), 2022 -0.059 (150), 2023 -0.171 (151), 2024 -0.033 (163), 2025 -0.083 (186), 2026 -0.039 (161).

Sensibilidad (R neto medio y t): colchón 0 % -0.045 (t -1.91), colchón 50 % -0.056 (t -2.67), objetivo 1,5:1 -0.054 (t -2.13), objetivo 2:1 -0.046 (t -1.74).

### ORB 19:15–20:15

Rotura con cuerpo desde las 20:15 hasta las 02:15 (día siguiente); a esa hora se cierra. ORB completos: 2095; con rotura: 2044.

**No pasa los criterios**. Coste medio 0.044 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 404, stop 369, por tiempo 638.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1411 | 49.3 % | -0.026 | -36.1 | 0.93 | -59.7 | -1.22 |
| Sin costes | 1411 | 50.3 % | +0.018 | +25.8 | 1.05 | -30.2 | +0.87 |
| Long | 804 | 51.0 % | -0.002 | -1.8 | 0.99 | -33.3 | -0.08 |
| Short | 607 | 47.1 % | -0.057 | -34.3 | 0.86 | -42.9 | -1.72 |
| 1.ª mitad | 706 | 50.0 % | -0.014 | -9.7 | 0.96 | -22.2 | -0.46 |
| 2.ª mitad | 705 | 48.7 % | -0.038 | -26.5 | 0.90 | -41.0 | -1.27 |

Por año (R neto medio y operaciones): 2018 +0.088 (48), 2019 -0.050 (184), 2020 +0.030 (157), 2021 -0.041 (178), 2022 -0.067 (160), 2023 -0.104 (164), 2024 -0.023 (173), 2025 -0.017 (183), 2026 +0.038 (164).

Sensibilidad (R neto medio y t): colchón 0 % -0.008 (t -0.35), colchón 50 % -0.027 (t -1.42), objetivo 1,5:1 -0.033 (t -1.44), objetivo 2:1 -0.026 (t -1.07).

### ORB 19:30–20:30

Rotura con cuerpo desde las 20:30 hasta las 02:30 (día siguiente); a esa hora se cierra. ORB completos: 2095; con rotura: 2043.

**No pasa los criterios**. Coste medio 0.041 R; ancho medio del ORB 0.27 %; cómo terminan: objetivo 382, stop 367, por tiempo 694.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1443 | 49.6 % | -0.030 | -43.8 | 0.91 | -72.7 | -1.49 |
| Sin costes | 1443 | 50.6 % | +0.011 | +16.0 | 1.03 | -23.8 | +0.54 |
| Long | 823 | 52.2 % | -0.011 | -9.0 | 0.97 | -25.3 | -0.41 |
| Short | 620 | 46.1 % | -0.056 | -34.8 | 0.85 | -52.2 | -1.76 |
| 1.ª mitad | 722 | 48.8 % | -0.036 | -26.3 | 0.90 | -41.3 | -1.27 |
| 2.ª mitad | 721 | 50.5 % | -0.024 | -17.4 | 0.93 | -39.8 | -0.84 |

Por año (R neto medio y operaciones): 2018 +0.167 (44), 2019 -0.097 (180), 2020 -0.024 (170), 2021 -0.045 (184), 2022 -0.046 (173), 2023 -0.085 (173), 2024 -0.061 (184), 2025 +0.039 (177), 2026 +0.037 (158).

Sensibilidad (R neto medio y t): colchón 0 % -0.022 (t -1.03), colchón 50 % -0.038 (t -2.08), objetivo 1,5:1 -0.024 (t -1.08), objetivo 2:1 -0.013 (t -0.54).

### ORB 19:45–20:45

Rotura con cuerpo desde las 20:45 hasta las 02:45 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2039.

**No pasa los criterios**. Coste medio 0.040 R; ancho medio del ORB 0.27 %; cómo terminan: objetivo 371, stop 339, por tiempo 785.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1495 | 48.2 % | -0.028 | -42.0 | 0.92 | -81.8 | -1.45 |
| Sin costes | 1495 | 50.1 % | +0.012 | +18.2 | 1.04 | -39.6 | +0.63 |
| Long | 869 | 50.2 % | -0.012 | -10.8 | 0.96 | -31.7 | -0.49 |
| Short | 626 | 45.4 % | -0.050 | -31.2 | 0.86 | -55.2 | -1.66 |
| 1.ª mitad | 748 | 45.9 % | -0.065 | -48.3 | 0.82 | -60.8 | -2.37 |
| 2.ª mitad | 747 | 50.5 % | +0.008 | +6.2 | 1.03 | -26.7 | +0.30 |

Por año (R neto medio y operaciones): 2018 +0.092 (49), 2019 -0.126 (188), 2020 -0.019 (182), 2021 -0.074 (187), 2022 -0.098 (173), 2023 -0.082 (188), 2024 -0.013 (187), 2025 +0.061 (180), 2026 +0.114 (161).

Sensibilidad (R neto medio y t): colchón 0 % -0.044 (t -2.08), colchón 50 % -0.037 (t -2.12), objetivo 1,5:1 -0.014 (t -0.67), objetivo 2:1 -0.003 (t -0.14).

