# ORB de 60 min de las 11:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 11:00–12:00 | 1609 | 51.1 | +0.011 | +0.61 | +0.028 | 0.017 | no |
| 11:15–12:15 | 1591 | 50.3 | +0.004 | +0.19 | +0.022 | 0.018 | no |
| 11:30–12:30 | 1584 | 51.1 | +0.008 | +0.42 | +0.027 | 0.019 | no |
| 11:45–12:45 | 1585 | 50.3 | -0.003 | -0.14 | +0.018 | 0.021 | no |

## Detalle

### ORB 11:00–12:00

Rotura con cuerpo desde las 12:00 hasta las 18:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2005.

**No pasa los criterios**. Coste medio 0.017 R; ancho medio del ORB 0.59 %; cómo terminan: objetivo 358, stop 313, por tiempo 938.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1609 | 51.1 % | +0.011 | +17.6 | 1.04 | -23.0 | +0.61 |
| Sin costes | 1609 | 51.8 % | +0.028 | +45.4 | 1.10 | -19.9 | +1.58 |
| Long | 904 | 55.5 % | +0.055 | +50.1 | 1.20 | -14.8 | +2.36 |
| Short | 705 | 45.5 % | -0.046 | -32.5 | 0.86 | -37.2 | -1.67 |
| 1.ª mitad | 805 | 51.4 % | +0.013 | +10.4 | 1.04 | -23.0 | +0.52 |
| 2.ª mitad | 804 | 50.9 % | +0.009 | +7.2 | 1.03 | -15.2 | +0.35 |

Por año (R neto medio y operaciones): 2018 -0.104 (65), 2019 -0.038 (201), 2020 +0.113 (209), 2021 -0.029 (198), 2022 +0.039 (199), 2023 -0.043 (192), 2024 +0.090 (198), 2025 +0.013 (196), 2026 -0.037 (151).

Sensibilidad (R neto medio y t): colchón 0 % +0.013 (t +0.68), colchón 50 % +0.014 (t +0.85), objetivo 1,5:1 +0.029 (t +1.46), objetivo 2:1 +0.025 (t +1.23).

### ORB 11:15–12:15

Rotura con cuerpo desde las 12:15 hasta las 18:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2018.

**No pasa los criterios**. Coste medio 0.018 R; ancho medio del ORB 0.56 %; cómo terminan: objetivo 380, stop 347, por tiempo 864.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1591 | 50.3 % | +0.004 | +5.6 | 1.01 | -24.2 | +0.19 |
| Sin costes | 1591 | 51.2 % | +0.022 | +34.6 | 1.07 | -17.5 | +1.17 |
| Long | 884 | 53.4 % | +0.044 | +39.2 | 1.16 | -13.6 | +1.83 |
| Short | 707 | 46.4 % | -0.048 | -33.6 | 0.87 | -44.2 | -1.66 |
| 1.ª mitad | 796 | 51.3 % | +0.015 | +11.6 | 1.05 | -24.2 | +0.56 |
| 2.ª mitad | 795 | 49.3 % | -0.008 | -6.0 | 0.98 | -19.9 | -0.29 |

Por año (R neto medio y operaciones): 2018 -0.106 (62), 2019 -0.080 (195), 2020 +0.135 (209), 2021 +0.019 (193), 2022 +0.017 (197), 2023 -0.074 (182), 2024 +0.057 (206), 2025 -0.030 (199), 2026 +0.002 (148).

Sensibilidad (R neto medio y t): colchón 0 % -0.002 (t -0.11), colchón 50 % +0.008 (t +0.46), objetivo 1,5:1 +0.014 (t +0.68), objetivo 2:1 +0.017 (t +0.82).

### ORB 11:30–12:30

Rotura con cuerpo desde las 12:30 hasta las 18:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2017.

**No pasa los criterios**. Coste medio 0.019 R; ancho medio del ORB 0.54 %; cómo terminan: objetivo 379, stop 356, por tiempo 849.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1584 | 51.1 % | +0.008 | +12.3 | 1.02 | -27.9 | +0.42 |
| Sin costes | 1584 | 52.0 % | +0.027 | +42.6 | 1.09 | -24.0 | +1.44 |
| Long | 885 | 55.3 % | +0.050 | +43.9 | 1.17 | -18.4 | +2.01 |
| Short | 699 | 45.9 % | -0.045 | -31.6 | 0.87 | -36.7 | -1.59 |
| 1.ª mitad | 792 | 52.9 % | +0.028 | +22.3 | 1.09 | -18.0 | +1.06 |
| 2.ª mitad | 792 | 49.4 % | -0.013 | -10.0 | 0.96 | -27.9 | -0.48 |

Por año (R neto medio y operaciones): 2018 -0.071 (62), 2019 -0.042 (190), 2020 +0.068 (212), 2021 +0.037 (185), 2022 +0.075 (202), 2023 -0.064 (185), 2024 +0.084 (200), 2025 -0.047 (195), 2026 -0.048 (153).

Sensibilidad (R neto medio y t): colchón 0 % +0.004 (t +0.22), colchón 50 % +0.010 (t +0.59), objetivo 1,5:1 +0.012 (t +0.57), objetivo 2:1 +0.023 (t +1.08).

### ORB 11:45–12:45

Rotura con cuerpo desde las 12:45 hasta las 18:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2029.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.51 %; cómo terminan: objetivo 387, stop 370, por tiempo 828.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1585 | 50.3 % | -0.003 | -4.1 | 0.99 | -23.6 | -0.14 |
| Sin costes | 1585 | 51.4 % | +0.018 | +28.4 | 1.06 | -19.8 | +0.95 |
| Long | 903 | 53.2 % | +0.019 | +17.0 | 1.06 | -24.3 | +0.76 |
| Short | 682 | 46.5 % | -0.031 | -21.1 | 0.91 | -33.1 | -1.07 |
| 1.ª mitad | 793 | 50.2 % | +0.008 | +6.5 | 1.03 | -23.4 | +0.30 |
| 2.ª mitad | 792 | 50.4 % | -0.013 | -10.6 | 0.96 | -23.6 | -0.51 |

Por año (R neto medio y operaciones): 2018 -0.109 (67), 2019 -0.036 (198), 2020 +0.015 (205), 2021 +0.004 (183), 2022 +0.087 (190), 2023 -0.052 (189), 2024 +0.051 (204), 2025 -0.035 (201), 2026 -0.023 (148).

Sensibilidad (R neto medio y t): colchón 0 % -0.008 (t -0.42), colchón 50 % +0.006 (t +0.38), objetivo 1,5:1 +0.002 (t +0.12), objetivo 2:1 +0.005 (t +0.25).

