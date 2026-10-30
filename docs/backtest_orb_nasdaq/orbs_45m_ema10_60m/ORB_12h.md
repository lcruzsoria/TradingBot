# ORB de 45 min de las 12:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 12:00–12:45 | 1539 | 49.8 | -0.016 | -0.78 | +0.008 | 0.024 | no |
| 12:15–13:00 | 1541 | 50.4 | +0.002 | +0.08 | +0.026 | 0.025 | no |
| 12:30–13:15 | 1515 | 50.5 | +0.007 | +0.35 | +0.031 | 0.024 | no |
| 12:45–13:30 | 1487 | 51.5 | +0.024 | +1.16 | +0.048 | 0.024 | no |

## Detalle

### ORB 12:00–12:45

Rotura con cuerpo desde las 12:45 hasta las 18:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2058.

**No pasa los criterios**. Coste medio 0.024 R; ancho medio del ORB 0.44 %; cómo terminan: objetivo 456, stop 449, por tiempo 634.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1539 | 49.8 % | -0.016 | -24.9 | 0.96 | -35.2 | -0.78 |
| Sin costes | 1539 | 50.7 % | +0.008 | +12.1 | 1.02 | -27.0 | +0.38 |
| Long | 885 | 52.8 % | +0.013 | +11.2 | 1.04 | -28.6 | +0.46 |
| Short | 654 | 45.7 % | -0.055 | -36.1 | 0.86 | -47.6 | -1.75 |
| 1.ª mitad | 770 | 50.1 % | -0.019 | -14.3 | 0.95 | -34.3 | -0.63 |
| 2.ª mitad | 769 | 49.4 % | -0.014 | -10.6 | 0.96 | -31.2 | -0.47 |

Por año (R neto medio y operaciones): 2018 -0.159 (63), 2019 -0.062 (190), 2020 -0.002 (194), 2021 -0.031 (177), 2022 +0.058 (187), 2023 -0.058 (187), 2024 +0.095 (197), 2025 -0.067 (195), 2026 -0.022 (149).

Sensibilidad (R neto medio y t): colchón 0 % -0.011 (t -0.52), colchón 50 % -0.005 (t -0.27), objetivo 1,5:1 -0.003 (t -0.11), objetivo 2:1 +0.007 (t +0.29).

### ORB 12:15–13:00

Rotura con cuerpo desde las 13:00 hasta las 19:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2041.

**No pasa los criterios**. Coste medio 0.025 R; ancho medio del ORB 0.42 %; cómo terminan: objetivo 478, stop 444, por tiempo 619.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1541 | 50.4 % | +0.002 | +2.5 | 1.00 | -28.6 | +0.08 |
| Sin costes | 1541 | 51.1 % | +0.026 | +40.6 | 1.07 | -19.2 | +1.27 |
| Long | 871 | 53.0 % | +0.039 | +33.6 | 1.11 | -20.9 | +1.39 |
| Short | 670 | 47.0 % | -0.046 | -31.1 | 0.88 | -41.1 | -1.48 |
| 1.ª mitad | 771 | 51.0 % | +0.007 | +5.7 | 1.02 | -25.5 | +0.25 |
| 2.ª mitad | 770 | 49.9 % | -0.004 | -3.3 | 0.99 | -28.6 | -0.15 |

Por año (R neto medio y operaciones): 2018 -0.166 (57), 2019 +0.005 (189), 2020 -0.054 (193), 2021 +0.005 (184), 2022 +0.153 (191), 2023 -0.033 (189), 2024 +0.025 (193), 2025 -0.050 (185), 2026 +0.012 (160).

Sensibilidad (R neto medio y t): colchón 0 % +0.007 (t +0.31), colchón 50 % -0.004 (t -0.22), objetivo 1,5:1 +0.014 (t +0.58), objetivo 2:1 +0.019 (t +0.78).

### ORB 12:30–13:15

Rotura con cuerpo desde las 13:15 hasta las 19:15; a esa hora se cierra. ORB completos: 2042; con rotura: 1991.

**No pasa los criterios**. Coste medio 0.024 R; ancho medio del ORB 0.42 %; cómo terminan: objetivo 458, stop 409, por tiempo 648.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1515 | 50.5 % | +0.007 | +11.0 | 1.02 | -28.0 | +0.35 |
| Sin costes | 1515 | 51.2 % | +0.031 | +47.6 | 1.09 | -24.2 | +1.52 |
| Long | 856 | 53.4 % | +0.042 | +35.7 | 1.12 | -17.9 | +1.52 |
| Short | 659 | 46.7 % | -0.038 | -24.7 | 0.90 | -32.6 | -1.19 |
| 1.ª mitad | 758 | 52.0 % | +0.029 | +21.7 | 1.08 | -23.1 | +0.95 |
| 2.ª mitad | 757 | 49.0 % | -0.014 | -10.7 | 0.96 | -28.0 | -0.49 |

Por año (R neto medio y operaciones): 2018 +0.147 (52), 2019 -0.040 (183), 2020 -0.028 (197), 2021 -0.010 (184), 2022 +0.188 (188), 2023 +0.026 (182), 2024 -0.016 (185), 2025 -0.083 (186), 2026 -0.023 (158).

Sensibilidad (R neto medio y t): colchón 0 % +0.010 (t +0.46), colchón 50 % +0.012 (t +0.61), objetivo 1,5:1 +0.020 (t +0.84), objetivo 2:1 +0.031 (t +1.22).

### ORB 12:45–13:30

Rotura con cuerpo desde las 13:30 hasta las 19:30; a esa hora se cierra. ORB completos: 2025; con rotura: 1985.

**No pasa los criterios**. Coste medio 0.024 R; ancho medio del ORB 0.42 %; cómo terminan: objetivo 451, stop 387, por tiempo 649.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1487 | 51.5 % | +0.024 | +36.0 | 1.07 | -21.8 | +1.16 |
| Sin costes | 1487 | 52.5 % | +0.048 | +71.9 | 1.14 | -16.3 | +2.32 |
| Long | 855 | 53.0 % | +0.037 | +32.0 | 1.11 | -18.9 | +1.35 |
| Short | 632 | 49.5 % | +0.006 | +3.9 | 1.02 | -21.5 | +0.20 |
| 1.ª mitad | 744 | 52.4 % | +0.046 | +34.1 | 1.13 | -17.8 | +1.52 |
| 2.ª mitad | 743 | 50.6 % | +0.003 | +1.9 | 1.01 | -21.8 | +0.09 |

Por año (R neto medio y operaciones): 2018 +0.155 (49), 2019 -0.055 (175), 2020 -0.004 (197), 2021 +0.054 (174), 2022 +0.164 (198), 2023 +0.015 (186), 2024 +0.004 (179), 2025 +0.010 (184), 2026 -0.059 (145).

Sensibilidad (R neto medio y t): colchón 0 % +0.025 (t +1.14), colchón 50 % +0.028 (t +1.50), objetivo 1,5:1 +0.031 (t +1.33), objetivo 2:1 +0.039 (t +1.59).

