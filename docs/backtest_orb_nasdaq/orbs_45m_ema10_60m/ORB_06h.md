# ORB de 45 min de las 06:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 06:00–06:45 | 1526 | 51.0 | -0.026 | -1.03 | +0.019 | 0.045 | no |
| 06:15–07:00 | 1564 | 51.5 | -0.014 | -0.57 | +0.031 | 0.045 | no |
| 06:30–07:15 | 1635 | 51.4 | -0.009 | -0.36 | +0.032 | 0.041 | no |
| 06:45–07:30 | 1642 | 50.7 | -0.018 | -0.74 | +0.021 | 0.039 | no |

## Detalle

### ORB 06:00–06:45

Rotura con cuerpo desde las 06:45 hasta las 12:45; a esa hora se cierra. ORB completos: 2095; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.045 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 752, stop 727, por tiempo 47.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1526 | 51.0 % | -0.026 | -39.7 | 0.95 | -52.5 | -1.03 |
| Sin costes | 1526 | 51.0 % | +0.019 | +28.6 | 1.04 | -27.2 | +0.74 |
| Long | 880 | 51.0 % | -0.024 | -21.2 | 0.95 | -35.7 | -0.72 |
| Short | 646 | 50.9 % | -0.029 | -18.5 | 0.94 | -28.3 | -0.74 |
| 1.ª mitad | 763 | 51.0 % | -0.025 | -19.3 | 0.95 | -35.4 | -0.71 |
| 2.ª mitad | 763 | 51.0 % | -0.027 | -20.4 | 0.95 | -32.6 | -0.75 |

Por año (R neto medio y operaciones): 2018 -0.127 (53), 2019 -0.046 (183), 2020 -0.049 (176), 2021 -0.029 (192), 2022 +0.062 (188), 2023 -0.104 (192), 2024 +0.037 (187), 2025 -0.045 (192), 2026 -0.000 (163).

Sensibilidad (R neto medio y t): colchón 0 % -0.034 (t -1.35), colchón 50 % -0.034 (t -1.36), objetivo 1,5:1 -0.013 (t -0.42), objetivo 2:1 -0.022 (t -0.64).

### ORB 06:15–07:00

Rotura con cuerpo desde las 07:00 hasta las 13:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.045 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 784, stop 737, por tiempo 43.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1564 | 51.5 % | -0.014 | -22.2 | 0.97 | -49.9 | -0.57 |
| Sin costes | 1564 | 51.5 % | +0.031 | +48.4 | 1.07 | -24.8 | +1.24 |
| Long | 911 | 51.4 % | -0.026 | -23.6 | 0.95 | -41.1 | -0.79 |
| Short | 653 | 51.8 % | +0.002 | +1.4 | 1.00 | -27.5 | +0.06 |
| 1.ª mitad | 782 | 51.4 % | -0.014 | -11.2 | 0.97 | -25.9 | -0.40 |
| 2.ª mitad | 782 | 51.7 % | -0.014 | -11.0 | 0.97 | -37.7 | -0.40 |

Por año (R neto medio y operaciones): 2018 -0.047 (58), 2019 -0.032 (176), 2020 -0.019 (182), 2021 -0.020 (197), 2022 +0.025 (188), 2023 -0.107 (201), 2024 -0.029 (197), 2025 +0.044 (195), 2026 +0.045 (170).

Sensibilidad (R neto medio y t): colchón 0 % -0.007 (t -0.27), colchón 50 % -0.010 (t -0.41), objetivo 1,5:1 -0.004 (t -0.12), objetivo 2:1 -0.057 (t -1.65).

### ORB 06:30–07:15

Rotura con cuerpo desde las 07:15 hasta las 13:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.041 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 818, stop 766, por tiempo 51.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1635 | 51.4 % | -0.009 | -14.5 | 0.98 | -41.0 | -0.36 |
| Sin costes | 1635 | 51.6 % | +0.032 | +51.8 | 1.07 | -18.8 | +1.30 |
| Long | 940 | 51.0 % | -0.028 | -25.9 | 0.95 | -47.8 | -0.85 |
| Short | 695 | 52.1 % | +0.016 | +11.4 | 1.03 | -24.3 | +0.44 |
| 1.ª mitad | 818 | 51.0 % | -0.015 | -11.9 | 0.97 | -30.8 | -0.42 |
| 2.ª mitad | 817 | 51.9 % | -0.003 | -2.6 | 0.99 | -32.2 | -0.09 |

Por año (R neto medio y operaciones): 2018 -0.013 (55), 2019 -0.042 (187), 2020 -0.063 (197), 2021 +0.006 (204), 2022 +0.082 (196), 2023 -0.082 (206), 2024 -0.021 (209), 2025 +0.020 (207), 2026 +0.036 (174).

Sensibilidad (R neto medio y t): colchón 0 % -0.022 (t -0.91), colchón 50 % -0.007 (t -0.31), objetivo 1,5:1 -0.008 (t -0.28), objetivo 2:1 -0.009 (t -0.27).

### ORB 06:45–07:30

Rotura con cuerpo desde las 07:30 hasta las 13:30; a esa hora se cierra. ORB completos: 2095; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.039 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 809, stop 775, por tiempo 58.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1642 | 50.7 % | -0.018 | -29.5 | 0.96 | -69.3 | -0.74 |
| Sin costes | 1642 | 50.9 % | +0.021 | +34.9 | 1.04 | -34.7 | +0.88 |
| Long | 909 | 50.5 % | -0.029 | -26.6 | 0.94 | -45.5 | -0.89 |
| Short | 733 | 50.9 % | -0.004 | -2.9 | 0.99 | -32.8 | -0.11 |
| 1.ª mitad | 821 | 49.1 % | -0.045 | -36.6 | 0.91 | -52.9 | -1.29 |
| 2.ª mitad | 821 | 52.3 % | +0.009 | +7.1 | 1.02 | -31.3 | +0.25 |

Por año (R neto medio y operaciones): 2018 +0.027 (53), 2019 -0.031 (193), 2020 -0.095 (207), 2021 -0.056 (206), 2022 +0.019 (194), 2023 -0.097 (206), 2024 +0.122 (199), 2025 +0.009 (207), 2026 -0.021 (177).

Sensibilidad (R neto medio y t): colchón 0 % -0.045 (t -1.83), colchón 50 % -0.027 (t -1.14), objetivo 1,5:1 -0.017 (t -0.57), objetivo 2:1 -0.033 (t -0.99).

