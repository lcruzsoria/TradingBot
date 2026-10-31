# ORB de 45 min de las 09:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 09:00–09:45 | 1852 | 53.5 | +0.041 | +2.14 | +0.056 | 0.015 | no |
| 09:15–10:00 | 1890 | 51.3 | +0.004 | +0.21 | +0.017 | 0.013 | no |
| 09:30–10:15 | 1885 | 52.3 | +0.009 | +0.59 | +0.021 | 0.012 | no |
| 09:45–10:30 | 1790 | 52.0 | +0.010 | +0.58 | +0.023 | 0.013 | no |

## Detalle

### ORB 09:00–09:45

Rotura con cuerpo desde las 09:45 hasta las 15:45; a esa hora se cierra. ORB completos: 2090; con rotura: 2074.

**No pasa los criterios**. Coste medio 0.015 R; ancho medio del ORB 0.59 %; cómo terminan: objetivo 583, stop 525, por tiempo 744.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1852 | 53.5 % | +0.041 | +75.3 | 1.12 | -13.0 | +2.14 |
| Sin costes | 1852 | 53.9 % | +0.056 | +103.3 | 1.16 | -12.3 | +2.93 |
| Long | 975 | 57.0 % | +0.064 | +62.2 | 1.19 | -14.1 | +2.47 |
| Short | 877 | 49.5 % | +0.015 | +13.1 | 1.04 | -10.0 | +0.53 |
| 1.ª mitad | 926 | 52.9 % | +0.029 | +27.3 | 1.08 | -13.0 | +1.09 |
| 2.ª mitad | 926 | 54.0 % | +0.052 | +48.0 | 1.15 | -11.9 | +1.93 |

Por año (R neto medio y operaciones): 2018 -0.057 (71), 2019 +0.052 (229), 2020 +0.025 (226), 2021 +0.073 (234), 2022 +0.040 (232), 2023 +0.033 (233), 2024 +0.053 (221), 2025 +0.057 (221), 2026 +0.019 (185).

Sensibilidad (R neto medio y t): colchón 0 % +0.043 (t +2.14), colchón 50 % +0.035 (t +1.99), objetivo 1,5:1 +0.049 (t +2.30), objetivo 2:1 +0.050 (t +2.24).

### ORB 09:15–10:00

Rotura con cuerpo desde las 10:00 hasta las 16:00; a esa hora se cierra. ORB completos: 2091; con rotura: 2039.

**No pasa los criterios**. Coste medio 0.013 R; ancho medio del ORB 0.71 %; cómo terminan: objetivo 434, stop 440, por tiempo 1016.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1890 | 51.3 % | +0.004 | +6.9 | 1.01 | -21.2 | +0.21 |
| Sin costes | 1890 | 51.8 % | +0.017 | +31.3 | 1.05 | -18.1 | +0.96 |
| Long | 997 | 55.9 % | +0.032 | +32.3 | 1.11 | -9.9 | +1.40 |
| Short | 893 | 46.1 % | -0.028 | -25.4 | 0.92 | -33.9 | -1.10 |
| 1.ª mitad | 945 | 50.7 % | -0.001 | -1.0 | 1.00 | -21.2 | -0.04 |
| 2.ª mitad | 945 | 51.9 % | +0.008 | +7.8 | 1.03 | -17.9 | +0.34 |

Por año (R neto medio y operaciones): 2018 -0.095 (69), 2019 +0.038 (227), 2020 -0.040 (231), 2021 +0.009 (238), 2022 +0.036 (236), 2023 -0.009 (237), 2024 +0.053 (233), 2025 +0.002 (228), 2026 -0.039 (191).

Sensibilidad (R neto medio y t): colchón 0 % +0.015 (t +0.78), colchón 50 % -0.008 (t -0.51), objetivo 1,5:1 +0.004 (t +0.24), objetivo 2:1 +0.008 (t +0.41).

### ORB 09:30–10:15

Rotura con cuerpo desde las 10:15 hasta las 16:15; a esa hora se cierra. ORB completos: 2093; con rotura: 2004.

**No pasa los criterios**. Coste medio 0.012 R; ancho medio del ORB 0.81 %; cómo terminan: objetivo 329, stop 331, por tiempo 1225.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1885 | 52.3 % | +0.009 | +17.4 | 1.03 | -16.8 | +0.59 |
| Sin costes | 1885 | 52.7 % | +0.021 | +39.3 | 1.08 | -15.4 | +1.33 |
| Long | 1025 | 55.8 % | +0.026 | +26.9 | 1.10 | -8.8 | +1.29 |
| Short | 860 | 48.1 % | -0.011 | -9.5 | 0.96 | -22.1 | -0.45 |
| 1.ª mitad | 943 | 53.9 % | +0.014 | +13.6 | 1.05 | -16.8 | +0.64 |
| 2.ª mitad | 942 | 50.7 % | +0.004 | +3.9 | 1.01 | -14.5 | +0.19 |

Por año (R neto medio y operaciones): 2018 -0.060 (72), 2019 +0.023 (224), 2020 -0.034 (234), 2021 +0.044 (237), 2022 +0.037 (238), 2023 +0.010 (230), 2024 +0.051 (230), 2025 -0.008 (227), 2026 -0.035 (193).

Sensibilidad (R neto medio y t): colchón 0 % +0.021 (t +1.22), colchón 50 % +0.000 (t +0.02), objetivo 1,5:1 +0.011 (t +0.66), objetivo 2:1 +0.011 (t +0.64).

### ORB 09:45–10:30

Rotura con cuerpo desde las 10:30 hasta las 16:30; a esa hora se cierra. ORB completos: 2095; con rotura: 2026.

**No pasa los criterios**. Coste medio 0.013 R; ancho medio del ORB 0.72 %; cómo terminan: objetivo 358, stop 354, por tiempo 1078.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1790 | 52.0 % | +0.010 | +17.3 | 1.03 | -22.9 | +0.58 |
| Sin costes | 1790 | 52.8 % | +0.023 | +41.1 | 1.08 | -18.2 | +1.37 |
| Long | 983 | 56.0 % | +0.032 | +31.0 | 1.11 | -19.2 | +1.43 |
| Short | 807 | 47.2 % | -0.017 | -13.7 | 0.95 | -29.9 | -0.66 |
| 1.ª mitad | 895 | 55.2 % | +0.033 | +29.2 | 1.11 | -14.7 | +1.35 |
| 2.ª mitad | 895 | 48.8 % | -0.013 | -11.9 | 0.96 | -22.9 | -0.57 |

Por año (R neto medio y operaciones): 2018 -0.011 (64), 2019 +0.038 (206), 2020 +0.010 (222), 2021 +0.048 (223), 2022 +0.027 (223), 2023 -0.008 (220), 2024 +0.022 (224), 2025 -0.024 (221), 2026 -0.035 (187).

Sensibilidad (R neto medio y t): colchón 0 % +0.014 (t +0.76), colchón 50 % +0.007 (t +0.47), objetivo 1,5:1 +0.018 (t +0.98), objetivo 2:1 +0.021 (t +1.14).

