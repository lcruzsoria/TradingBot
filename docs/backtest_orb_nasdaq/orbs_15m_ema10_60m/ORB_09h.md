# ORB de 15 min de las 09:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 09:00–09:15 | 1444 | 49.4 | -0.060 | -2.28 | -0.012 | 0.048 | no |
| 09:15–09:30 | 1575 | 51.2 | -0.012 | -0.48 | +0.022 | 0.034 | no |
| 09:30–09:45 | 1793 | 53.0 | +0.028 | +1.39 | +0.044 | 0.016 | no |
| 09:45–10:00 | 1663 | 52.1 | +0.017 | +0.75 | +0.037 | 0.020 | no |

## Detalle

### ORB 09:00–09:15

Rotura con cuerpo desde las 09:15 hasta las 15:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.048 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 699, stop 717, por tiempo 28.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1444 | 49.4 % | -0.060 | -86.1 | 0.89 | -92.5 | -2.28 |
| Sin costes | 1444 | 49.4 % | -0.012 | -17.1 | 0.98 | -44.6 | -0.45 |
| Long | 770 | 50.1 % | -0.049 | -37.8 | 0.91 | -47.3 | -1.37 |
| Short | 674 | 48.5 % | -0.072 | -48.2 | 0.86 | -50.8 | -1.87 |
| 1.ª mitad | 722 | 48.2 % | -0.086 | -61.8 | 0.84 | -71.0 | -2.31 |
| 2.ª mitad | 722 | 50.6 % | -0.034 | -24.3 | 0.93 | -33.3 | -0.91 |

Por año (R neto medio y operaciones): 2018 -0.294 (48), 2019 -0.056 (188), 2020 -0.058 (173), 2021 -0.121 (179), 2022 -0.020 (173), 2023 -0.111 (182), 2024 +0.082 (189), 2025 -0.048 (173), 2026 -0.096 (139).

Sensibilidad (R neto medio y t): colchón 0 % -0.087 (t -3.31), colchón 50 % -0.052 (t -2.01), objetivo 1,5:1 -0.057 (t -1.80), objetivo 2:1 -0.060 (t -1.68).

### ORB 09:15–09:30

Rotura con cuerpo desde las 09:30 hasta las 15:30; a esa hora se cierra. ORB completos: 2093; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.034 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 785, stop 748, por tiempo 42.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1575 | 51.2 % | -0.012 | -18.7 | 0.98 | -46.2 | -0.48 |
| Sin costes | 1575 | 51.2 % | +0.022 | +34.1 | 1.05 | -32.4 | +0.87 |
| Long | 824 | 50.5 % | -0.030 | -25.0 | 0.94 | -39.8 | -0.88 |
| Short | 751 | 52.1 % | +0.008 | +6.3 | 1.02 | -47.7 | +0.23 |
| 1.ª mitad | 788 | 49.9 % | -0.041 | -32.0 | 0.92 | -46.2 | -1.15 |
| 2.ª mitad | 787 | 52.6 % | +0.017 | +13.3 | 1.04 | -25.6 | +0.48 |

Por año (R neto medio y operaciones): 2018 -0.129 (55), 2019 +0.090 (197), 2020 -0.081 (191), 2021 -0.087 (204), 2022 +0.016 (193), 2023 +0.071 (196), 2024 -0.027 (181), 2025 -0.051 (199), 2026 +0.011 (159).

Sensibilidad (R neto medio y t): colchón 0 % -0.011 (t -0.43), colchón 50 % -0.014 (t -0.56), objetivo 1,5:1 +0.021 (t +0.68), objetivo 2:1 +0.042 (t +1.21).

### ORB 09:30–09:45

Rotura con cuerpo desde las 09:45 hasta las 15:45; a esa hora se cierra. ORB completos: 2093; con rotura: 2086.

**No pasa los criterios**. Coste medio 0.016 R; ancho medio del ORB 0.54 %; cómo terminan: objetivo 620, stop 577, por tiempo 596.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1793 | 53.0 % | +0.028 | +50.1 | 1.07 | -16.8 | +1.39 |
| Sin costes | 1793 | 53.3 % | +0.044 | +79.4 | 1.12 | -16.1 | +2.20 |
| Long | 935 | 56.5 % | +0.058 | +54.2 | 1.16 | -13.5 | +2.10 |
| Short | 858 | 49.2 % | -0.005 | -4.1 | 0.99 | -18.2 | -0.16 |
| 1.ª mitad | 897 | 52.5 % | +0.010 | +8.6 | 1.02 | -16.8 | +0.34 |
| 2.ª mitad | 896 | 53.5 % | +0.046 | +41.5 | 1.12 | -14.6 | +1.62 |

Por año (R neto medio y operaciones): 2018 -0.133 (71), 2019 +0.041 (218), 2020 -0.041 (220), 2021 +0.106 (226), 2022 +0.015 (225), 2023 +0.016 (224), 2024 +0.035 (211), 2025 +0.069 (216), 2026 +0.035 (182).

Sensibilidad (R neto medio y t): colchón 0 % +0.028 (t +1.34), colchón 50 % +0.036 (t +1.94), objetivo 1,5:1 +0.046 (t +2.01), objetivo 2:1 +0.054 (t +2.22).

### ORB 09:45–10:00

Rotura con cuerpo desde las 10:00 hasta las 16:00; a esa hora se cierra. ORB completos: 2095; con rotura: 2089.

**No pasa los criterios**. Coste medio 0.020 R; ancho medio del ORB 0.44 %; cómo terminan: objetivo 671, stop 631, por tiempo 361.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1663 | 52.1 % | +0.017 | +27.7 | 1.04 | -25.3 | +0.75 |
| Sin costes | 1663 | 52.4 % | +0.037 | +61.1 | 1.09 | -22.8 | +1.65 |
| Long | 888 | 54.3 % | +0.038 | +33.7 | 1.09 | -15.1 | +1.26 |
| Short | 775 | 49.5 % | -0.008 | -6.0 | 0.98 | -32.0 | -0.23 |
| 1.ª mitad | 832 | 51.4 % | +0.009 | +7.4 | 1.02 | -25.3 | +0.28 |
| 2.ª mitad | 831 | 52.7 % | +0.025 | +20.4 | 1.06 | -23.5 | +0.78 |

Por año (R neto medio y operaciones): 2018 -0.244 (66), 2019 +0.134 (193), 2020 -0.020 (196), 2021 +0.014 (219), 2022 +0.031 (205), 2023 -0.098 (206), 2024 +0.145 (204), 2025 +0.035 (209), 2026 -0.026 (165).

Sensibilidad (R neto medio y t): colchón 0 % -0.004 (t -0.17), colchón 50 % +0.003 (t +0.15), objetivo 1,5:1 +0.020 (t +0.79), objetivo 2:1 +0.045 (t +1.64).

