# ORB de 60 min de las 09:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 09:00–10:00 | 1900 | 51.4 | +0.006 | +0.35 | +0.019 | 0.013 | no |
| 09:15–10:15 | 1887 | 52.7 | +0.015 | +1.00 | +0.027 | 0.011 | no |
| 09:30–10:30 | 1884 | 52.3 | +0.009 | +0.64 | +0.020 | 0.011 | no |
| 09:45–10:45 | 1800 | 51.4 | +0.007 | +0.46 | +0.019 | 0.012 | no |

## Detalle

### ORB 09:00–10:00

Rotura con cuerpo desde las 10:00 hasta las 16:00; a esa hora se cierra. ORB completos: 2090; con rotura: 2031.

**No pasa los criterios**. Coste medio 0.013 R; ancho medio del ORB 0.73 %; cómo terminan: objetivo 413, stop 421, por tiempo 1066.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1900 | 51.4 % | +0.006 | +11.2 | 1.02 | -21.6 | +0.35 |
| Sin costes | 1900 | 51.8 % | +0.019 | +35.2 | 1.06 | -16.5 | +1.09 |
| Long | 999 | 55.8 % | +0.034 | +34.3 | 1.12 | -9.6 | +1.52 |
| Short | 901 | 46.5 % | -0.026 | -23.1 | 0.93 | -31.6 | -1.01 |
| 1.ª mitad | 950 | 51.1 % | +0.003 | +2.7 | 1.01 | -21.6 | +0.12 |
| 2.ª mitad | 950 | 51.7 % | +0.009 | +8.5 | 1.03 | -17.4 | +0.38 |

Por año (R neto medio y operaciones): 2018 -0.063 (69), 2019 +0.026 (228), 2020 -0.032 (235), 2021 +0.013 (238), 2022 +0.033 (236), 2023 -0.008 (238), 2024 +0.063 (234), 2025 +0.002 (231), 2026 -0.038 (191).

Sensibilidad (R neto medio y t): colchón 0 % +0.018 (t +1.00), colchón 50 % -0.003 (t -0.20), objetivo 1,5:1 +0.010 (t +0.55), objetivo 2:1 +0.013 (t +0.67).

### ORB 09:15–10:15

Rotura con cuerpo desde las 10:15 hasta las 16:15; a esa hora se cierra. ORB completos: 2091; con rotura: 1991.

**No pasa los criterios**. Coste medio 0.011 R; ancho medio del ORB 0.83 %; cómo terminan: objetivo 313, stop 309, por tiempo 1265.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1887 | 52.7 % | +0.015 | +28.9 | 1.06 | -17.0 | +1.00 |
| Sin costes | 1887 | 53.2 % | +0.027 | +50.4 | 1.10 | -15.8 | +1.74 |
| Long | 1021 | 56.3 % | +0.033 | +33.4 | 1.13 | -9.1 | +1.64 |
| Short | 866 | 48.5 % | -0.005 | -4.5 | 0.98 | -19.9 | -0.22 |
| 1.ª mitad | 944 | 54.9 % | +0.026 | +25.0 | 1.10 | -14.7 | +1.19 |
| 2.ª mitad | 943 | 50.6 % | +0.004 | +3.9 | 1.02 | -17.0 | +0.20 |

Por año (R neto medio y operaciones): 2018 -0.022 (70), 2019 +0.035 (223), 2020 -0.008 (233), 2021 +0.041 (238), 2022 +0.028 (239), 2023 +0.018 (232), 2024 +0.055 (232), 2025 -0.003 (226), 2026 -0.044 (194).

Sensibilidad (R neto medio y t): colchón 0 % +0.027 (t +1.59), colchón 50 % +0.003 (t +0.22), objetivo 1,5:1 +0.017 (t +1.05), objetivo 2:1 +0.018 (t +1.10).

### ORB 09:30–10:30

Rotura con cuerpo desde las 10:30 hasta las 16:30; a esa hora se cierra. ORB completos: 2093; con rotura: 1960.

**No pasa los criterios**. Coste medio 0.011 R; ancho medio del ORB 0.88 %; cómo terminan: objetivo 244, stop 252, por tiempo 1388.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1884 | 52.3 % | +0.009 | +17.1 | 1.04 | -16.0 | +0.64 |
| Sin costes | 1884 | 53.2 % | +0.020 | +37.4 | 1.08 | -12.2 | +1.39 |
| Long | 1041 | 56.6 % | +0.026 | +26.8 | 1.11 | -12.8 | +1.41 |
| Short | 843 | 47.1 % | -0.012 | -9.7 | 0.96 | -22.3 | -0.51 |
| 1.ª mitad | 942 | 55.1 % | +0.022 | +21.1 | 1.09 | -16.0 | +1.10 |
| 2.ª mitad | 942 | 49.6 % | -0.004 | -4.0 | 0.98 | -13.4 | -0.21 |

Por año (R neto medio y operaciones): 2018 -0.024 (70), 2019 +0.004 (223), 2020 -0.027 (236), 2021 +0.063 (233), 2022 +0.044 (238), 2023 +0.013 (230), 2024 +0.004 (236), 2025 -0.001 (230), 2026 -0.023 (188).

Sensibilidad (R neto medio y t): colchón 0 % +0.020 (t +1.27), colchón 50 % +0.006 (t +0.46), objetivo 1,5:1 +0.008 (t +0.51), objetivo 2:1 +0.011 (t +0.70).

### ORB 09:45–10:45

Rotura con cuerpo desde las 10:45 hasta las 16:45; a esa hora se cierra. ORB completos: 2095; con rotura: 1983.

**No pasa los criterios**. Coste medio 0.012 R; ancho medio del ORB 0.80 %; cómo terminan: objetivo 280, stop 279, por tiempo 1241.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1800 | 51.4 % | +0.007 | +12.7 | 1.03 | -36.4 | +0.46 |
| Sin costes | 1800 | 52.4 % | +0.019 | +34.5 | 1.07 | -28.4 | +1.24 |
| Long | 1003 | 55.6 % | +0.029 | +29.6 | 1.12 | -15.3 | +1.47 |
| Short | 797 | 46.2 % | -0.021 | -16.9 | 0.93 | -35.5 | -0.88 |
| 1.ª mitad | 900 | 55.3 % | +0.048 | +42.9 | 1.19 | -10.2 | +2.17 |
| 2.ª mitad | 900 | 47.6 % | -0.034 | -30.2 | 0.88 | -36.4 | -1.55 |

Por año (R neto medio y operaciones): 2018 +0.058 (66), 2019 +0.015 (207), 2020 +0.013 (223), 2021 +0.063 (225), 2022 +0.073 (222), 2023 -0.003 (225), 2024 -0.047 (231), 2025 -0.008 (220), 2026 -0.078 (181).

Sensibilidad (R neto medio y t): colchón 0 % +0.007 (t +0.42), colchón 50 % +0.006 (t +0.47), objetivo 1,5:1 +0.012 (t +0.73), objetivo 2:1 +0.017 (t +1.03).

