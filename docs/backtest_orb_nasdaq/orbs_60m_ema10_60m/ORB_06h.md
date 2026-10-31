# ORB de 60 min de las 06:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 06:00–07:00 | 1640 | 51.2 | -0.011 | -0.47 | +0.028 | 0.039 | no |
| 06:15–07:15 | 1693 | 51.4 | -0.006 | -0.27 | +0.030 | 0.036 | no |
| 06:30–07:30 | 1702 | 51.8 | +0.008 | +0.32 | +0.043 | 0.035 | no |
| 06:45–07:45 | 1728 | 49.7 | -0.038 | -1.63 | -0.004 | 0.034 | no |

## Detalle

### ORB 06:00–07:00

Rotura con cuerpo desde las 07:00 hasta las 13:00; a esa hora se cierra. ORB completos: 2095; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.039 R; ancho medio del ORB 0.27 %; cómo terminan: objetivo 797, stop 755, por tiempo 88.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1640 | 51.2 % | -0.011 | -18.6 | 0.98 | -49.9 | -0.47 |
| Sin costes | 1640 | 51.2 % | +0.028 | +45.3 | 1.06 | -29.5 | +1.14 |
| Long | 951 | 50.9 % | -0.028 | -26.2 | 0.94 | -54.2 | -0.86 |
| Short | 689 | 51.5 % | +0.011 | +7.5 | 1.02 | -24.0 | +0.29 |
| 1.ª mitad | 820 | 51.6 % | -0.000 | -0.2 | 1.00 | -23.2 | -0.01 |
| 2.ª mitad | 820 | 50.7 % | -0.023 | -18.5 | 0.95 | -38.4 | -0.66 |

Por año (R neto medio y operaciones): 2018 -0.080 (59), 2019 -0.027 (191), 2020 +0.037 (192), 2021 -0.029 (202), 2022 +0.018 (200), 2023 -0.100 (211), 2024 -0.020 (206), 2025 +0.015 (204), 2026 +0.049 (175).

Sensibilidad (R neto medio y t): colchón 0 % +0.001 (t +0.04), colchón 50 % -0.008 (t -0.33), objetivo 1,5:1 -0.008 (t -0.29), objetivo 2:1 -0.047 (t -1.44).

### ORB 06:15–07:15

Rotura con cuerpo desde las 07:15 hasta las 13:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.036 R; ancho medio del ORB 0.28 %; cómo terminan: objetivo 832, stop 784, por tiempo 77.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1693 | 51.4 % | -0.006 | -10.7 | 0.99 | -60.6 | -0.27 |
| Sin costes | 1693 | 51.6 % | +0.030 | +50.9 | 1.06 | -26.7 | +1.26 |
| Long | 960 | 51.6 % | -0.014 | -13.4 | 0.97 | -42.5 | -0.44 |
| Short | 733 | 51.2 % | +0.004 | +2.7 | 1.01 | -34.7 | +0.10 |
| 1.ª mitad | 847 | 50.3 % | -0.024 | -20.4 | 0.95 | -43.4 | -0.71 |
| 2.ª mitad | 846 | 52.5 % | +0.011 | +9.7 | 1.02 | -41.9 | +0.34 |

Por año (R neto medio y operaciones): 2018 -0.026 (60), 2019 -0.035 (196), 2020 -0.097 (206), 2021 -0.024 (210), 2022 +0.099 (203), 2023 -0.123 (217), 2024 -0.031 (216), 2025 +0.095 (209), 2026 +0.092 (176).

Sensibilidad (R neto medio y t): colchón 0 % -0.017 (t -0.72), colchón 50 % -0.034 (t -1.44), objetivo 1,5:1 -0.016 (t -0.55), objetivo 2:1 -0.034 (t -1.07).

### ORB 06:30–07:30

Rotura con cuerpo desde las 07:30 hasta las 13:30; a esa hora se cierra. ORB completos: 2095; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.035 R; ancho medio del ORB 0.29 %; cómo terminan: objetivo 842, stop 767, por tiempo 93.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1702 | 51.8 % | +0.008 | +13.0 | 1.02 | -30.6 | +0.32 |
| Sin costes | 1702 | 52.0 % | +0.043 | +72.4 | 1.09 | -17.3 | +1.80 |
| Long | 937 | 51.9 % | +0.002 | +1.8 | 1.00 | -24.5 | +0.06 |
| Short | 765 | 51.8 % | +0.015 | +11.2 | 1.03 | -27.5 | +0.42 |
| 1.ª mitad | 851 | 50.8 % | -0.006 | -5.0 | 0.99 | -30.6 | -0.17 |
| 2.ª mitad | 851 | 52.9 % | +0.021 | +18.0 | 1.04 | -24.6 | +0.63 |

Por año (R neto medio y operaciones): 2018 +0.049 (54), 2019 -0.004 (199), 2020 -0.032 (212), 2021 -0.048 (212), 2022 +0.099 (205), 2023 -0.069 (215), 2024 +0.055 (209), 2025 +0.034 (213), 2026 +0.022 (183).

Sensibilidad (R neto medio y t): colchón 0 % -0.010 (t -0.43), colchón 50 % -0.008 (t -0.35), objetivo 1,5:1 -0.013 (t -0.46), objetivo 2:1 -0.014 (t -0.45).

### ORB 06:45–07:45

Rotura con cuerpo desde las 07:45 hasta las 13:45; a esa hora se cierra. ORB completos: 2095; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.034 R; ancho medio del ORB 0.30 %; cómo terminan: objetivo 805, stop 813, por tiempo 110.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1728 | 49.7 % | -0.038 | -66.0 | 0.92 | -77.7 | -1.63 |
| Sin costes | 1728 | 49.8 % | -0.004 | -7.6 | 0.99 | -43.1 | -0.19 |
| Long | 936 | 50.0 % | -0.042 | -39.2 | 0.92 | -47.4 | -1.31 |
| Short | 792 | 49.2 % | -0.034 | -26.8 | 0.93 | -43.0 | -0.98 |
| 1.ª mitad | 864 | 49.3 % | -0.039 | -33.5 | 0.92 | -44.5 | -1.17 |
| 2.ª mitad | 864 | 50.0 % | -0.038 | -32.5 | 0.92 | -47.3 | -1.13 |

Por año (R neto medio y operaciones): 2018 -0.006 (58), 2019 -0.015 (203), 2020 -0.084 (213), 2021 -0.064 (215), 2022 +0.051 (208), 2023 -0.168 (223), 2024 +0.026 (210), 2025 +0.034 (212), 2026 -0.090 (186).

Sensibilidad (R neto medio y t): colchón 0 % -0.051 (t -2.17), colchón 50 % -0.045 (t -1.94), objetivo 1,5:1 -0.046 (t -1.64), objetivo 2:1 -0.064 (t -2.06).

