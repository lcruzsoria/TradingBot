# ORB de 45 min de las 05:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 05:00–05:45 | 1530 | 50.2 | -0.040 | -1.57 | +0.006 | 0.045 | no |
| 05:15–06:00 | 1487 | 48.9 | -0.070 | -2.74 | -0.024 | 0.046 | no |
| 05:30–06:15 | 1541 | 49.8 | -0.044 | -1.75 | +0.001 | 0.046 | no |
| 05:45–06:30 | 1523 | 50.0 | -0.043 | -1.68 | +0.004 | 0.047 | no |

## Detalle

### ORB 05:00–05:45

Rotura con cuerpo desde las 05:45 hasta las 11:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.045 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 744, stop 736, por tiempo 50.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1530 | 50.2 % | -0.040 | -60.7 | 0.92 | -84.5 | -1.57 |
| Sin costes | 1530 | 50.3 % | +0.006 | +8.7 | 1.01 | -30.9 | +0.23 |
| Long | 870 | 48.5 % | -0.076 | -65.8 | 0.86 | -82.2 | -2.26 |
| Short | 660 | 52.4 % | +0.008 | +5.1 | 1.02 | -24.1 | +0.20 |
| 1.ª mitad | 765 | 49.3 % | -0.056 | -43.1 | 0.89 | -53.4 | -1.59 |
| 2.ª mitad | 765 | 51.1 % | -0.023 | -17.7 | 0.95 | -40.5 | -0.64 |

Por año (R neto medio y operaciones): 2018 -0.075 (52), 2019 -0.064 (200), 2020 -0.120 (178), 2021 +0.052 (192), 2022 -0.102 (181), 2023 -0.086 (190), 2024 +0.019 (193), 2025 -0.041 (189), 2026 +0.041 (155).

Sensibilidad (R neto medio y t): colchón 0 % -0.059 (t -2.31), colchón 50 % -0.053 (t -2.14), objetivo 1,5:1 -0.088 (t -2.90), objetivo 2:1 -0.092 (t -2.69).

### ORB 05:15–06:00

Rotura con cuerpo desde las 06:00 hasta las 12:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.046 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 702, stop 738, por tiempo 47.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1487 | 48.9 % | -0.070 | -104.2 | 0.87 | -115.9 | -2.74 |
| Sin costes | 1487 | 48.9 % | -0.024 | -35.0 | 0.95 | -59.5 | -0.92 |
| Long | 845 | 48.4 % | -0.083 | -70.3 | 0.84 | -80.4 | -2.45 |
| Short | 642 | 49.5 % | -0.053 | -33.8 | 0.90 | -43.1 | -1.36 |
| 1.ª mitad | 744 | 48.4 % | -0.080 | -59.2 | 0.85 | -74.9 | -2.21 |
| 2.ª mitad | 743 | 49.4 % | -0.061 | -45.0 | 0.88 | -47.3 | -1.67 |

Por año (R neto medio y operaciones): 2018 +0.074 (53), 2019 -0.118 (197), 2020 -0.115 (161), 2021 -0.036 (183), 2022 -0.138 (183), 2023 -0.094 (189), 2024 +0.037 (187), 2025 -0.081 (186), 2026 -0.058 (148).

Sensibilidad (R neto medio y t): colchón 0 % -0.093 (t -3.60), colchón 50 % -0.053 (t -2.10), objetivo 1,5:1 -0.058 (t -1.88), objetivo 2:1 -0.065 (t -1.85).

### ORB 05:30–06:15

Rotura con cuerpo desde las 06:15 hasta las 12:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.046 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 754, stop 749, por tiempo 38.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1541 | 49.8 % | -0.044 | -68.3 | 0.91 | -80.1 | -1.75 |
| Sin costes | 1541 | 50.0 % | +0.001 | +2.3 | 1.00 | -33.1 | +0.06 |
| Long | 882 | 49.9 % | -0.053 | -46.4 | 0.90 | -57.5 | -1.57 |
| Short | 659 | 49.8 % | -0.033 | -21.9 | 0.93 | -36.2 | -0.86 |
| 1.ª mitad | 771 | 49.7 % | -0.050 | -38.4 | 0.90 | -52.6 | -1.39 |
| 2.ª mitad | 770 | 50.0 % | -0.039 | -29.9 | 0.92 | -36.5 | -1.09 |

Por año (R neto medio y operaciones): 2018 +0.053 (53), 2019 -0.095 (193), 2020 -0.042 (170), 2021 -0.088 (190), 2022 +0.009 (195), 2023 -0.107 (197), 2024 +0.048 (194), 2025 -0.039 (192), 2026 -0.073 (157).

Sensibilidad (R neto medio y t): colchón 0 % -0.058 (t -2.27), colchón 50 % -0.050 (t -2.01), objetivo 1,5:1 -0.054 (t -1.75), objetivo 2:1 -0.061 (t -1.76).

### ORB 05:45–06:30

Rotura con cuerpo desde las 06:30 hasta las 12:30; a esa hora se cierra. ORB completos: 2095; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.047 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 747, stop 742, por tiempo 34.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1523 | 50.0 % | -0.043 | -64.9 | 0.92 | -80.9 | -1.68 |
| Sin costes | 1523 | 50.2 % | +0.004 | +5.9 | 1.01 | -43.1 | +0.15 |
| Long | 855 | 51.3 % | -0.023 | -19.7 | 0.95 | -39.6 | -0.68 |
| Short | 668 | 48.4 % | -0.068 | -45.2 | 0.87 | -51.2 | -1.77 |
| 1.ª mitad | 762 | 50.7 % | -0.031 | -23.8 | 0.94 | -36.3 | -0.87 |
| 2.ª mitad | 761 | 49.4 % | -0.054 | -41.1 | 0.90 | -54.8 | -1.50 |

Por año (R neto medio y operaciones): 2018 -0.042 (54), 2019 -0.115 (186), 2020 +0.019 (173), 2021 -0.041 (187), 2022 +0.025 (190), 2023 -0.205 (204), 2024 +0.047 (186), 2025 -0.042 (189), 2026 -0.005 (154).

Sensibilidad (R neto medio y t): colchón 0 % -0.062 (t -2.43), colchón 50 % -0.033 (t -1.32), objetivo 1,5:1 -0.037 (t -1.21), objetivo 2:1 -0.053 (t -1.51).

