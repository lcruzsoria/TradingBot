# ORB de 60 min de las 02:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 02:00–03:00 | 1701 | 49.0 | -0.049 | -2.24 | -0.009 | 0.040 | no |
| 02:15–03:15 | 1735 | 48.1 | -0.045 | -2.14 | -0.008 | 0.036 | no |
| 02:30–03:30 | 1736 | 48.7 | -0.026 | -1.30 | +0.007 | 0.034 | no |
| 02:45–03:45 | 1785 | 50.0 | -0.021 | -0.98 | +0.011 | 0.031 | no |

## Detalle

### ORB 02:00–03:00

Rotura con cuerpo desde las 03:00 hasta las 09:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2086.

**No pasa los criterios**. Coste medio 0.040 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 656, stop 665, por tiempo 380.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1701 | 49.0 % | -0.049 | -83.4 | 0.89 | -99.1 | -2.24 |
| Sin costes | 1701 | 49.2 % | -0.009 | -15.4 | 0.98 | -51.9 | -0.41 |
| Long | 944 | 50.1 % | -0.035 | -33.1 | 0.92 | -44.6 | -1.20 |
| Short | 757 | 47.6 % | -0.066 | -50.3 | 0.86 | -64.4 | -2.01 |
| 1.ª mitad | 851 | 48.2 % | -0.049 | -41.3 | 0.89 | -41.9 | -1.61 |
| 2.ª mitad | 850 | 49.8 % | -0.049 | -42.0 | 0.89 | -67.3 | -1.56 |

Por año (R neto medio y operaciones): 2018 -0.028 (59), 2019 -0.098 (210), 2020 -0.043 (204), 2021 -0.034 (219), 2022 -0.047 (213), 2023 +0.062 (217), 2024 -0.155 (205), 2025 -0.158 (196), 2026 +0.081 (178).

Sensibilidad (R neto medio y t): colchón 0 % -0.053 (t -2.34), colchón 50 % -0.051 (t -2.49), objetivo 1,5:1 -0.066 (t -2.65), objetivo 2:1 -0.068 (t -2.53).

### ORB 02:15–03:15

Rotura con cuerpo desde las 03:15 hasta las 09:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2085.

**No pasa los criterios**. Coste medio 0.036 R; ancho medio del ORB 0.30 %; cómo terminan: objetivo 618, stop 622, por tiempo 495.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1735 | 48.1 % | -0.045 | -77.8 | 0.90 | -100.5 | -2.14 |
| Sin costes | 1735 | 48.9 % | -0.008 | -14.5 | 0.98 | -58.5 | -0.40 |
| Long | 982 | 48.9 % | -0.026 | -25.2 | 0.94 | -53.2 | -0.92 |
| Short | 753 | 47.1 % | -0.070 | -52.5 | 0.84 | -63.8 | -2.20 |
| 1.ª mitad | 868 | 49.3 % | -0.017 | -15.1 | 0.96 | -30.7 | -0.61 |
| 2.ª mitad | 867 | 46.9 % | -0.072 | -62.7 | 0.84 | -81.4 | -2.37 |

Por año (R neto medio y operaciones): 2018 -0.002 (60), 2019 -0.055 (219), 2020 +0.003 (209), 2021 -0.042 (223), 2022 -0.036 (224), 2023 -0.023 (216), 2024 -0.182 (208), 2025 -0.102 (205), 2026 +0.088 (171).

Sensibilidad (R neto medio y t): colchón 0 % -0.037 (t -1.68), colchón 50 % -0.043 (t -2.21), objetivo 1,5:1 -0.056 (t -2.38), objetivo 2:1 -0.047 (t -1.84).

### ORB 02:30–03:30

Rotura con cuerpo desde las 03:30 hasta las 09:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2072.

**No pasa los criterios**. Coste medio 0.034 R; ancho medio del ORB 0.33 %; cómo terminan: objetivo 594, stop 557, por tiempo 585.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1736 | 48.7 % | -0.026 | -45.7 | 0.93 | -64.7 | -1.30 |
| Sin costes | 1736 | 49.5 % | +0.007 | +12.8 | 1.02 | -27.4 | +0.36 |
| Long | 970 | 49.3 % | -0.009 | -8.9 | 0.98 | -38.0 | -0.34 |
| Short | 766 | 47.9 % | -0.048 | -36.8 | 0.88 | -46.7 | -1.57 |
| 1.ª mitad | 868 | 48.2 % | -0.018 | -16.0 | 0.95 | -25.7 | -0.67 |
| 2.ª mitad | 868 | 49.2 % | -0.034 | -29.7 | 0.92 | -45.4 | -1.15 |

Por año (R neto medio y operaciones): 2018 +0.003 (62), 2019 -0.058 (211), 2020 +0.024 (214), 2021 -0.010 (223), 2022 -0.062 (231), 2023 -0.016 (212), 2024 -0.041 (205), 2025 -0.085 (208), 2026 +0.044 (170).

Sensibilidad (R neto medio y t): colchón 0 % -0.037 (t -1.72), colchón 50 % -0.033 (t -1.76), objetivo 1,5:1 -0.025 (t -1.08), objetivo 2:1 -0.018 (t -0.71).

### ORB 02:45–03:45

Rotura con cuerpo desde las 03:45 hasta las 09:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2084.

**No pasa los criterios**. Coste medio 0.031 R; ancho medio del ORB 0.35 %; cómo terminan: objetivo 677, stop 661, por tiempo 447.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1785 | 50.0 % | -0.021 | -36.8 | 0.95 | -55.3 | -0.98 |
| Sin costes | 1785 | 50.2 % | +0.011 | +19.3 | 1.03 | -36.8 | +0.51 |
| Long | 1012 | 51.5 % | -0.000 | -0.4 | 1.00 | -28.1 | -0.01 |
| Short | 773 | 48.1 % | -0.047 | -36.5 | 0.89 | -50.2 | -1.47 |
| 1.ª mitad | 893 | 49.9 % | -0.024 | -21.1 | 0.94 | -50.6 | -0.82 |
| 2.ª mitad | 892 | 50.1 % | -0.018 | -15.8 | 0.96 | -29.4 | -0.58 |

Por año (R neto medio y operaciones): 2018 +0.102 (63), 2019 -0.121 (215), 2020 -0.046 (220), 2021 -0.004 (222), 2022 +0.006 (234), 2023 -0.002 (219), 2024 +0.024 (216), 2025 -0.029 (216), 2026 -0.034 (180).

Sensibilidad (R neto medio y t): colchón 0 % -0.048 (t -2.17), colchón 50 % -0.015 (t -0.75), objetivo 1,5:1 +0.000 (t +0.00), objetivo 2:1 -0.007 (t -0.26).

