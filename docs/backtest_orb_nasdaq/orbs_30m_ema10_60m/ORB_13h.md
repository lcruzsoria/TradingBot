# ORB de 30 min de las 13:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 13:00–13:30 | 1418 | 51.3 | +0.016 | +0.68 | +0.045 | 0.029 | no |
| 13:15–13:45 | 1424 | 49.4 | -0.011 | -0.46 | +0.019 | 0.030 | no |
| 13:30–14:00 | 1420 | 50.4 | -0.005 | -0.22 | +0.025 | 0.030 | no |
| 13:45–14:15 | 1440 | 49.6 | -0.029 | -1.32 | -0.000 | 0.029 | no |

## Detalle

### ORB 13:00–13:30

Rotura con cuerpo desde las 13:30 hasta las 19:30; a esa hora se cierra. ORB completos: 2025; con rotura: 2003.

**No pasa los criterios**. Coste medio 0.029 R; ancho medio del ORB 0.35 %; cómo terminan: objetivo 520, stop 462, por tiempo 436.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1418 | 51.3 % | +0.016 | +22.4 | 1.04 | -32.6 | +0.68 |
| Sin costes | 1418 | 52.0 % | +0.045 | +63.7 | 1.12 | -21.1 | +1.95 |
| Long | 815 | 52.4 % | +0.018 | +14.8 | 1.05 | -24.1 | +0.60 |
| Short | 603 | 49.9 % | +0.012 | +7.5 | 1.03 | -20.3 | +0.36 |
| 1.ª mitad | 709 | 52.3 % | +0.051 | +36.0 | 1.13 | -21.1 | +1.53 |
| 2.ª mitad | 709 | 50.4 % | -0.019 | -13.6 | 0.95 | -32.6 | -0.60 |

Por año (R neto medio y operaciones): 2018 +0.100 (47), 2019 +0.012 (166), 2020 -0.041 (189), 2021 +0.051 (164), 2022 +0.184 (192), 2023 -0.033 (180), 2024 -0.042 (178), 2025 +0.027 (167), 2026 -0.084 (135).

Sensibilidad (R neto medio y t): colchón 0 % +0.009 (t +0.39), colchón 50 % +0.032 (t +1.49), objetivo 1,5:1 +0.023 (t +0.86), objetivo 2:1 +0.025 (t +0.90).

### ORB 13:15–13:45

Rotura con cuerpo desde las 13:45 hasta las 19:45; a esa hora se cierra. ORB completos: 2026; con rotura: 2003.

**No pasa los criterios**. Coste medio 0.030 R; ancho medio del ORB 0.34 %; cómo terminan: objetivo 514, stop 471, por tiempo 439.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1424 | 49.4 % | -0.011 | -15.0 | 0.97 | -31.3 | -0.46 |
| Sin costes | 1424 | 49.8 % | +0.019 | +27.3 | 1.05 | -25.5 | +0.84 |
| Long | 800 | 51.5 % | +0.012 | +10.0 | 1.03 | -29.1 | +0.41 |
| Short | 624 | 46.6 % | -0.040 | -25.0 | 0.90 | -38.5 | -1.16 |
| 1.ª mitad | 712 | 51.7 % | +0.015 | +11.0 | 1.04 | -20.4 | +0.47 |
| 2.ª mitad | 712 | 47.1 % | -0.037 | -26.1 | 0.91 | -30.8 | -1.16 |

Por año (R neto medio y operaciones): 2018 +0.105 (49), 2019 -0.061 (181), 2020 +0.048 (176), 2021 -0.021 (173), 2022 +0.068 (186), 2023 -0.010 (177), 2024 -0.012 (185), 2025 -0.083 (176), 2026 -0.066 (121).

Sensibilidad (R neto medio y t): colchón 0 % -0.018 (t -0.77), colchón 50 % -0.001 (t -0.06), objetivo 1,5:1 -0.012 (t -0.47), objetivo 2:1 +0.003 (t +0.09).

### ORB 13:30–14:00

Rotura con cuerpo desde las 14:00 hasta las 20:00; a esa hora se cierra. ORB completos: 2025; con rotura: 2000.

**No pasa los criterios**. Coste medio 0.030 R; ancho medio del ORB 0.33 %; cómo terminan: objetivo 518, stop 467, por tiempo 435.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1420 | 50.4 % | -0.005 | -7.0 | 0.99 | -24.6 | -0.22 |
| Sin costes | 1420 | 50.8 % | +0.025 | +36.0 | 1.07 | -13.7 | +1.11 |
| Long | 787 | 53.2 % | +0.045 | +35.3 | 1.12 | -17.8 | +1.46 |
| Short | 633 | 46.8 % | -0.067 | -42.3 | 0.84 | -47.9 | -1.96 |
| 1.ª mitad | 710 | 50.8 % | -0.003 | -2.2 | 0.99 | -18.7 | -0.09 |
| 2.ª mitad | 710 | 49.9 % | -0.007 | -4.8 | 0.98 | -18.9 | -0.21 |

Por año (R neto medio y operaciones): 2018 +0.119 (57), 2019 -0.050 (176), 2020 +0.007 (184), 2021 +0.010 (168), 2022 -0.013 (185), 2023 -0.033 (174), 2024 +0.077 (174), 2025 -0.007 (175), 2026 -0.095 (127).

Sensibilidad (R neto medio y t): colchón 0 % -0.014 (t -0.60), colchón 50 % -0.001 (t -0.05), objetivo 1,5:1 -0.007 (t -0.28), objetivo 2:1 +0.017 (t +0.61).

### ORB 13:45–14:15

Rotura con cuerpo desde las 14:15 hasta las 20:15; a esa hora se cierra. ORB completos: 2025; con rotura: 1995.

**No pasa los criterios**. Coste medio 0.029 R; ancho medio del ORB 0.36 %; cómo terminan: objetivo 462, stop 470, por tiempo 508.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1440 | 49.6 % | -0.029 | -42.2 | 0.93 | -49.4 | -1.32 |
| Sin costes | 1440 | 49.8 % | -0.000 | -0.6 | 1.00 | -23.0 | -0.02 |
| Long | 803 | 51.9 % | -0.007 | -5.8 | 0.98 | -26.5 | -0.25 |
| Short | 637 | 46.6 % | -0.057 | -36.4 | 0.86 | -45.0 | -1.70 |
| 1.ª mitad | 720 | 49.6 % | -0.033 | -24.0 | 0.92 | -33.1 | -1.04 |
| 2.ª mitad | 720 | 49.6 % | -0.025 | -18.1 | 0.93 | -32.8 | -0.82 |

Por año (R neto medio y operaciones): 2018 +0.008 (51), 2019 -0.118 (176), 2020 +0.000 (198), 2021 -0.020 (157), 2022 -0.000 (194), 2023 -0.004 (188), 2024 -0.061 (179), 2025 -0.009 (171), 2026 -0.044 (126).

Sensibilidad (R neto medio y t): colchón 0 % -0.031 (t -1.33), colchón 50 % -0.023 (t -1.11), objetivo 1,5:1 -0.024 (t -0.97), objetivo 2:1 -0.010 (t -0.37).

