# ORB de 45 min de las 02:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 02:00–02:45 | 1630 | 48.3 | -0.056 | -2.44 | -0.011 | 0.045 | no |
| 02:15–03:00 | 1583 | 48.1 | -0.076 | -3.22 | -0.028 | 0.048 | no |
| 02:30–03:15 | 1673 | 48.4 | -0.050 | -2.29 | -0.010 | 0.040 | no |
| 02:45–03:30 | 1700 | 48.7 | -0.038 | -1.79 | -0.002 | 0.036 | no |

## Detalle

### ORB 02:00–02:45

Rotura con cuerpo desde las 02:45 hasta las 08:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.045 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 677, stop 689, por tiempo 264.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1630 | 48.3 % | -0.056 | -91.7 | 0.88 | -103.7 | -2.44 |
| Sin costes | 1630 | 48.6 % | -0.011 | -18.4 | 0.97 | -43.2 | -0.49 |
| Long | 915 | 49.5 % | -0.036 | -33.3 | 0.92 | -39.1 | -1.19 |
| Short | 715 | 46.9 % | -0.082 | -58.3 | 0.83 | -72.1 | -2.32 |
| 1.ª mitad | 815 | 47.0 % | -0.067 | -54.6 | 0.86 | -56.7 | -2.09 |
| 2.ª mitad | 815 | 49.7 % | -0.046 | -37.1 | 0.91 | -58.4 | -1.37 |

Por año (R neto medio y operaciones): 2018 -0.059 (59), 2019 -0.109 (203), 2020 -0.035 (201), 2021 -0.077 (209), 2022 -0.084 (200), 2023 +0.071 (203), 2024 -0.071 (198), 2025 -0.165 (191), 2026 +0.031 (166).

Sensibilidad (R neto medio y t): colchón 0 % -0.082 (t -3.46), colchón 50 % -0.047 (t -2.14), objetivo 1,5:1 -0.066 (t -2.49), objetivo 2:1 -0.064 (t -2.20).

### ORB 02:15–03:00

Rotura con cuerpo desde las 03:00 hasta las 09:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.048 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 667, stop 708, por tiempo 208.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1583 | 48.1 % | -0.076 | -120.8 | 0.85 | -128.2 | -3.22 |
| Sin costes | 1583 | 48.4 % | -0.028 | -44.9 | 0.94 | -57.1 | -1.20 |
| Long | 887 | 49.7 % | -0.051 | -44.9 | 0.89 | -58.7 | -1.61 |
| Short | 696 | 46.1 % | -0.109 | -76.0 | 0.79 | -84.2 | -3.04 |
| 1.ª mitad | 792 | 48.2 % | -0.070 | -55.1 | 0.85 | -60.7 | -2.11 |
| 2.ª mitad | 791 | 48.0 % | -0.083 | -65.8 | 0.84 | -76.1 | -2.44 |

Por año (R neto medio y operaciones): 2018 -0.118 (58), 2019 -0.122 (193), 2020 -0.071 (192), 2021 -0.068 (204), 2022 -0.018 (193), 2023 +0.009 (201), 2024 -0.153 (195), 2025 -0.179 (186), 2026 +0.011 (161).

Sensibilidad (R neto medio y t): colchón 0 % -0.083 (t -3.44), colchón 50 % -0.059 (t -2.59), objetivo 1,5:1 -0.083 (t -3.03), objetivo 2:1 -0.081 (t -2.72).

### ORB 02:30–03:15

Rotura con cuerpo desde las 03:15 hasta las 09:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.040 R; ancho medio del ORB 0.27 %; cómo terminan: objetivo 642, stop 653, por tiempo 378.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1673 | 48.4 % | -0.050 | -84.3 | 0.89 | -105.6 | -2.29 |
| Sin costes | 1673 | 49.1 % | -0.010 | -17.3 | 0.98 | -65.2 | -0.47 |
| Long | 939 | 49.5 % | -0.027 | -25.8 | 0.94 | -53.7 | -0.94 |
| Short | 734 | 47.0 % | -0.080 | -58.5 | 0.83 | -69.1 | -2.39 |
| 1.ª mitad | 837 | 49.8 % | -0.017 | -14.4 | 0.96 | -27.2 | -0.57 |
| 2.ª mitad | 836 | 47.0 % | -0.084 | -69.9 | 0.83 | -87.5 | -2.63 |

Por año (R neto medio y operaciones): 2018 -0.037 (59), 2019 -0.054 (208), 2020 +0.021 (204), 2021 -0.022 (217), 2022 -0.087 (217), 2023 -0.027 (209), 2024 -0.195 (198), 2025 -0.105 (197), 2026 +0.080 (164).

Sensibilidad (R neto medio y t): colchón 0 % -0.049 (t -2.14), colchón 50 % -0.051 (t -2.45), objetivo 1,5:1 -0.052 (t -2.06), objetivo 2:1 -0.050 (t -1.85).

### ORB 02:45–03:30

Rotura con cuerpo desde las 03:30 hasta las 09:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2078.

**No pasa los criterios**. Coste medio 0.036 R; ancho medio del ORB 0.30 %; cómo terminan: objetivo 608, stop 591, por tiempo 501.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1700 | 48.7 % | -0.038 | -64.2 | 0.91 | -84.5 | -1.79 |
| Sin costes | 1700 | 49.3 % | -0.002 | -2.7 | 1.00 | -41.2 | -0.07 |
| Long | 949 | 49.2 % | -0.025 | -23.6 | 0.94 | -46.8 | -0.88 |
| Short | 751 | 48.1 % | -0.054 | -40.6 | 0.87 | -54.4 | -1.70 |
| 1.ª mitad | 850 | 48.8 % | -0.025 | -21.5 | 0.94 | -32.3 | -0.88 |
| 2.ª mitad | 850 | 48.6 % | -0.050 | -42.7 | 0.89 | -58.0 | -1.63 |

Por año (R neto medio y operaciones): 2018 -0.002 (59), 2019 -0.088 (208), 2020 +0.039 (209), 2021 -0.020 (215), 2022 -0.068 (225), 2023 -0.034 (211), 2024 -0.042 (199), 2025 -0.135 (206), 2026 +0.052 (168).

Sensibilidad (R neto medio y t): colchón 0 % -0.051 (t -2.32), colchón 50 % -0.028 (t -1.41), objetivo 1,5:1 -0.031 (t -1.29), objetivo 2:1 -0.032 (t -1.25).

