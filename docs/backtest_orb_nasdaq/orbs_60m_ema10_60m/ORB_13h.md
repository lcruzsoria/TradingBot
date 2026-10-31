# ORB de 60 min de las 13:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 13:00–14:00 | 1501 | 49.9 | -0.007 | -0.37 | +0.014 | 0.021 | no |
| 13:15–14:15 | 1518 | 49.8 | +0.004 | +0.24 | +0.025 | 0.021 | no |
| 13:30–14:30 | 1511 | 50.9 | +0.005 | +0.30 | +0.027 | 0.021 | no |
| 13:45–14:45 | 1483 | 49.6 | -0.002 | -0.13 | +0.019 | 0.021 | no |

## Detalle

### ORB 13:00–14:00

Rotura con cuerpo desde las 14:00 hasta las 20:00; a esa hora se cierra. ORB completos: 2024; con rotura: 1934.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.48 %; cómo terminan: objetivo 351, stop 329, por tiempo 821.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1501 | 49.9 % | -0.007 | -10.6 | 0.98 | -29.8 | -0.37 |
| Sin costes | 1501 | 50.8 % | +0.014 | +21.4 | 1.05 | -22.6 | +0.75 |
| Long | 852 | 51.5 % | +0.017 | +14.1 | 1.05 | -17.0 | +0.65 |
| Short | 649 | 47.8 % | -0.038 | -24.7 | 0.89 | -33.6 | -1.30 |
| 1.ª mitad | 751 | 49.5 % | -0.015 | -11.5 | 0.96 | -29.8 | -0.55 |
| 2.ª mitad | 750 | 50.3 % | +0.001 | +1.0 | 1.00 | -17.4 | +0.05 |

Por año (R neto medio y operaciones): 2018 +0.083 (56), 2019 -0.121 (187), 2020 +0.017 (197), 2021 +0.048 (173), 2022 +0.013 (208), 2023 -0.041 (182), 2024 +0.033 (185), 2025 -0.022 (174), 2026 -0.013 (139).

Sensibilidad (R neto medio y t): colchón 0 % -0.003 (t -0.17), colchón 50 % +0.005 (t +0.29), objetivo 1,5:1 -0.003 (t -0.13), objetivo 2:1 +0.004 (t +0.20).

### ORB 13:15–14:15

Rotura con cuerpo desde las 14:15 hasta las 20:15; a esa hora se cierra. ORB completos: 2025; con rotura: 1920.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.51 %; cómo terminan: objetivo 329, stop 292, por tiempo 897.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1518 | 49.8 % | +0.004 | +6.7 | 1.01 | -24.1 | +0.24 |
| Sin costes | 1518 | 50.7 % | +0.025 | +38.5 | 1.09 | -18.3 | +1.39 |
| Long | 865 | 52.5 % | +0.023 | +19.5 | 1.08 | -19.1 | +0.95 |
| Short | 653 | 46.2 % | -0.020 | -12.8 | 0.94 | -22.6 | -0.69 |
| 1.ª mitad | 759 | 51.4 % | +0.009 | +6.7 | 1.03 | -24.1 | +0.33 |
| 2.ª mitad | 759 | 48.2 % | +0.000 | +0.0 | 1.00 | -18.4 | +0.00 |

Por año (R neto medio y operaciones): 2018 -0.000 (58), 2019 -0.076 (186), 2020 +0.071 (205), 2021 +0.023 (173), 2022 +0.022 (209), 2023 +0.006 (186), 2024 -0.021 (184), 2025 -0.014 (182), 2026 +0.023 (135).

Sensibilidad (R neto medio y t): colchón 0 % +0.001 (t +0.05), colchón 50 % +0.013 (t +0.83), objetivo 1,5:1 +0.016 (t +0.80), objetivo 2:1 +0.029 (t +1.37).

### ORB 13:30–14:30

Rotura con cuerpo desde las 14:30 hasta las 20:30; a esa hora se cierra. ORB completos: 2025; con rotura: 1916.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.49 %; cómo terminan: objetivo 314, stop 279, por tiempo 918.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1511 | 50.9 % | +0.005 | +8.1 | 1.02 | -21.3 | +0.30 |
| Sin costes | 1511 | 52.2 % | +0.027 | +40.2 | 1.09 | -16.5 | +1.48 |
| Long | 876 | 53.0 % | +0.031 | +27.4 | 1.11 | -11.5 | +1.33 |
| Short | 635 | 48.0 % | -0.030 | -19.3 | 0.90 | -25.0 | -1.09 |
| 1.ª mitad | 756 | 53.4 % | +0.019 | +14.2 | 1.06 | -21.3 | +0.71 |
| 2.ª mitad | 755 | 48.3 % | -0.008 | -6.1 | 0.97 | -16.2 | -0.33 |

Por año (R neto medio y operaciones): 2018 +0.132 (53), 2019 -0.071 (181), 2020 +0.071 (202), 2021 +0.005 (181), 2022 +0.021 (201), 2023 -0.012 (185), 2024 +0.017 (177), 2025 +0.014 (186), 2026 -0.063 (145).

Sensibilidad (R neto medio y t): colchón 0 % +0.006 (t +0.29), colchón 50 % +0.008 (t +0.52), objetivo 1,5:1 +0.010 (t +0.50), objetivo 2:1 +0.020 (t +0.95).

### ORB 13:45–14:45

Rotura con cuerpo desde las 14:45 hasta las 20:45; a esa hora se cierra. ORB completos: 2025; con rotura: 1898.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.50 %; cómo terminan: objetivo 293, stop 264, por tiempo 926.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1483 | 49.6 % | -0.002 | -3.5 | 0.99 | -23.3 | -0.13 |
| Sin costes | 1483 | 51.2 % | +0.019 | +28.3 | 1.07 | -17.1 | +1.07 |
| Long | 849 | 53.8 % | +0.037 | +31.7 | 1.14 | -11.0 | +1.60 |
| Short | 634 | 44.0 % | -0.055 | -35.2 | 0.83 | -40.4 | -2.02 |
| 1.ª mitad | 742 | 50.4 % | +0.010 | +7.4 | 1.03 | -17.4 | +0.38 |
| 2.ª mitad | 741 | 48.9 % | -0.015 | -10.9 | 0.95 | -18.8 | -0.61 |

Por año (R neto medio y operaciones): 2018 +0.124 (53), 2019 -0.030 (181), 2020 +0.061 (196), 2021 -0.018 (176), 2022 -0.007 (200), 2023 -0.015 (185), 2024 -0.025 (173), 2025 +0.021 (175), 2026 -0.060 (144).

Sensibilidad (R neto medio y t): colchón 0 % -0.005 (t -0.28), colchón 50 % -0.003 (t -0.19), objetivo 1,5:1 -0.003 (t -0.17), objetivo 2:1 +0.010 (t +0.50).

