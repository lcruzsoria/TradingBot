# ORB de 30 min de las 07:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 07:00–07:30 | 1579 | 49.8 | -0.042 | -1.67 | +0.005 | 0.046 | no |
| 07:15–07:45 | 1553 | 49.0 | -0.069 | -2.74 | -0.020 | 0.049 | no |
| 07:30–08:00 | 1568 | 49.4 | -0.066 | -2.65 | -0.018 | 0.048 | no |
| 07:45–08:15 | 1582 | 49.5 | -0.057 | -2.27 | -0.013 | 0.043 | no |

## Detalle

### ORB 07:00–07:30

Rotura con cuerpo desde las 07:30 hasta las 13:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.046 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 775, stop 768, por tiempo 36.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1579 | 49.8 % | -0.042 | -65.9 | 0.92 | -79.9 | -1.67 |
| Sin costes | 1579 | 50.0 % | +0.005 | +7.1 | 1.01 | -45.6 | +0.18 |
| Long | 870 | 49.5 % | -0.055 | -47.6 | 0.90 | -63.0 | -1.62 |
| Short | 709 | 50.2 % | -0.026 | -18.3 | 0.95 | -35.6 | -0.70 |
| 1.ª mitad | 790 | 49.7 % | -0.042 | -33.5 | 0.92 | -49.6 | -1.20 |
| 2.ª mitad | 789 | 49.9 % | -0.041 | -32.4 | 0.92 | -39.2 | -1.16 |

Por año (R neto medio y operaciones): 2018 -0.016 (51), 2019 -0.009 (187), 2020 -0.043 (197), 2021 -0.090 (200), 2022 -0.038 (184), 2023 -0.123 (197), 2024 +0.057 (195), 2025 -0.061 (205), 2026 -0.026 (163).

Sensibilidad (R neto medio y t): colchón 0 % -0.080 (t -3.20), colchón 50 % -0.048 (t -1.94), objetivo 1,5:1 -0.044 (t -1.44), objetivo 2:1 -0.015 (t -0.44).

### ORB 07:15–07:45

Rotura con cuerpo desde las 07:45 hasta las 13:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.049 R; ancho medio del ORB 0.21 %; cómo terminan: objetivo 745, stop 777, por tiempo 31.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1553 | 49.0 % | -0.069 | -107.2 | 0.87 | -120.9 | -2.74 |
| Sin costes | 1553 | 49.0 % | -0.020 | -31.7 | 0.96 | -68.5 | -0.81 |
| Long | 834 | 50.4 % | -0.050 | -41.8 | 0.90 | -56.7 | -1.46 |
| Short | 719 | 47.4 % | -0.091 | -65.4 | 0.83 | -78.1 | -2.46 |
| 1.ª mitad | 777 | 49.7 % | -0.059 | -45.8 | 0.89 | -54.2 | -1.66 |
| 2.ª mitad | 776 | 48.3 % | -0.079 | -61.4 | 0.85 | -71.0 | -2.21 |

Por año (R neto medio y operaciones): 2018 +0.009 (56), 2019 +0.000 (190), 2020 -0.067 (192), 2021 -0.123 (183), 2022 -0.045 (190), 2023 -0.248 (199), 2024 -0.036 (193), 2025 -0.006 (189), 2026 -0.040 (161).

Sensibilidad (R neto medio y t): colchón 0 % -0.079 (t -3.14), colchón 50 % -0.029 (t -1.18), objetivo 1,5:1 -0.054 (t -1.78), objetivo 2:1 -0.048 (t -1.36).

### ORB 07:30–08:00

Rotura con cuerpo desde las 08:00 hasta las 14:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.048 R; ancho medio del ORB 0.21 %; cómo terminan: objetivo 745, stop 781, por tiempo 42.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1568 | 49.4 % | -0.066 | -103.8 | 0.87 | -128.4 | -2.65 |
| Sin costes | 1568 | 49.4 % | -0.018 | -28.7 | 0.96 | -75.9 | -0.73 |
| Long | 868 | 50.5 % | -0.052 | -45.1 | 0.90 | -65.9 | -1.54 |
| Short | 700 | 48.1 % | -0.084 | -58.7 | 0.84 | -72.5 | -2.25 |
| 1.ª mitad | 784 | 50.4 % | -0.052 | -41.0 | 0.90 | -61.7 | -1.48 |
| 2.ª mitad | 784 | 48.5 % | -0.080 | -62.8 | 0.85 | -73.1 | -2.26 |

Por año (R neto medio y operaciones): 2018 +0.007 (52), 2019 +0.021 (193), 2020 -0.061 (187), 2021 -0.146 (191), 2022 -0.037 (189), 2023 -0.187 (207), 2024 -0.067 (195), 2025 -0.010 (196), 2026 -0.052 (158).

Sensibilidad (R neto medio y t): colchón 0 % -0.090 (t -3.57), colchón 50 % -0.045 (t -1.80), objetivo 1,5:1 -0.053 (t -1.75), objetivo 2:1 -0.055 (t -1.60).

### ORB 07:45–08:15

Rotura con cuerpo desde las 08:15 hasta las 14:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.043 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 758, stop 779, por tiempo 45.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1582 | 49.5 % | -0.057 | -89.4 | 0.89 | -116.3 | -2.27 |
| Sin costes | 1582 | 49.5 % | -0.013 | -20.7 | 0.97 | -66.0 | -0.53 |
| Long | 861 | 49.5 % | -0.064 | -55.1 | 0.88 | -73.9 | -1.90 |
| Short | 721 | 49.5 % | -0.048 | -34.3 | 0.91 | -59.2 | -1.29 |
| 1.ª mitad | 791 | 49.8 % | -0.053 | -41.9 | 0.90 | -56.0 | -1.51 |
| 2.ª mitad | 791 | 49.2 % | -0.060 | -47.5 | 0.89 | -76.4 | -1.70 |

Por año (R neto medio y operaciones): 2018 -0.003 (54), 2019 -0.041 (192), 2020 -0.087 (196), 2021 -0.093 (194), 2022 +0.026 (185), 2023 -0.037 (190), 2024 -0.243 (205), 2025 -0.031 (207), 2026 +0.077 (159).

Sensibilidad (R neto medio y t): colchón 0 % -0.076 (t -3.02), colchón 50 % -0.038 (t -1.55), objetivo 1,5:1 -0.039 (t -1.30), objetivo 2:1 -0.059 (t -1.74).

