# ORB de 45 min de las 22:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 22:00–22:45 | 1424 | 51.2 | -0.032 | -1.27 | +0.028 | 0.060 | no |
| 22:15–23:00 | 1402 | 51.1 | -0.034 | -1.34 | +0.030 | 0.064 | no |
| 22:30–23:15 | 1413 | 50.6 | -0.043 | -1.68 | +0.024 | 0.067 | no |
| 22:45–23:30 | 1388 | 50.6 | -0.044 | -1.70 | +0.025 | 0.069 | no |

## Detalle

### ORB 22:00–22:45

Rotura con cuerpo desde las 22:45 hasta las 04:45 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2086.

**No pasa los criterios**. Coste medio 0.060 R; ancho medio del ORB 0.20 %; cómo terminan: objetivo 626, stop 591, por tiempo 207.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1424 | 51.2 % | -0.032 | -44.9 | 0.93 | -75.5 | -1.27 |
| Sin costes | 1424 | 51.5 % | +0.028 | +40.2 | 1.06 | -43.7 | +1.14 |
| Long | 835 | 53.2 % | -0.007 | -6.1 | 0.98 | -33.8 | -0.22 |
| Short | 589 | 48.4 % | -0.066 | -38.9 | 0.86 | -52.5 | -1.71 |
| 1.ª mitad | 712 | 50.8 % | -0.038 | -27.3 | 0.92 | -63.9 | -1.11 |
| 2.ª mitad | 712 | 51.5 % | -0.025 | -17.7 | 0.95 | -39.0 | -0.70 |

Por año (R neto medio y operaciones): 2018 +0.207 (51), 2019 -0.126 (164), 2020 -0.073 (178), 2021 -0.069 (180), 2022 +0.036 (166), 2023 -0.046 (173), 2024 -0.064 (172), 2025 +0.003 (175), 2026 +0.017 (165).

Sensibilidad (R neto medio y t): colchón 0 % -0.044 (t -1.72), colchón 50 % -0.016 (t -0.67), objetivo 1,5:1 -0.010 (t -0.33), objetivo 2:1 +0.003 (t +0.11).

### ORB 22:15–23:00

Rotura con cuerpo desde las 23:00 hasta las 05:00 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2086.

**No pasa los criterios**. Coste medio 0.064 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 640, stop 604, por tiempo 158.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1402 | 51.1 % | -0.034 | -47.7 | 0.93 | -65.4 | -1.34 |
| Sin costes | 1402 | 51.4 % | +0.030 | +41.4 | 1.07 | -44.1 | +1.16 |
| Long | 807 | 53.2 % | -0.005 | -4.1 | 0.99 | -29.1 | -0.15 |
| Short | 595 | 48.4 % | -0.073 | -43.7 | 0.85 | -57.1 | -1.88 |
| 1.ª mitad | 701 | 50.6 % | -0.037 | -26.1 | 0.92 | -64.4 | -1.05 |
| 2.ª mitad | 701 | 51.6 % | -0.031 | -21.7 | 0.94 | -39.4 | -0.85 |

Por año (R neto medio y operaciones): 2018 +0.016 (53), 2019 -0.070 (157), 2020 -0.090 (180), 2021 -0.118 (166), 2022 +0.116 (169), 2023 -0.061 (164), 2024 -0.090 (176), 2025 -0.038 (176), 2026 +0.071 (161).

Sensibilidad (R neto medio y t): colchón 0 % -0.031 (t -1.22), colchón 50 % +0.001 (t +0.04), objetivo 1,5:1 -0.015 (t -0.51), objetivo 2:1 -0.001 (t -0.03).

### ORB 22:30–23:15

Rotura con cuerpo desde las 23:15 hasta las 05:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.067 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 652, stop 615, por tiempo 146.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1413 | 50.6 % | -0.043 | -60.2 | 0.91 | -82.4 | -1.68 |
| Sin costes | 1413 | 50.9 % | +0.024 | +33.7 | 1.05 | -23.7 | +0.94 |
| Long | 834 | 52.3 % | -0.018 | -15.4 | 0.96 | -36.7 | -0.56 |
| Short | 579 | 48.2 % | -0.078 | -44.9 | 0.85 | -58.2 | -1.95 |
| 1.ª mitad | 707 | 50.1 % | -0.053 | -37.8 | 0.89 | -46.5 | -1.51 |
| 2.ª mitad | 706 | 51.1 % | -0.032 | -22.5 | 0.94 | -56.4 | -0.87 |

Por año (R neto medio y operaciones): 2018 -0.178 (57), 2019 -0.122 (157), 2020 -0.039 (179), 2021 +0.044 (162), 2022 -0.020 (177), 2023 -0.110 (171), 2024 -0.151 (177), 2025 -0.024 (172), 2026 +0.137 (161).

Sensibilidad (R neto medio y t): colchón 0 % -0.056 (t -2.16), colchón 50 % -0.029 (t -1.18), objetivo 1,5:1 -0.021 (t -0.70), objetivo 2:1 -0.013 (t -0.38).

### ORB 22:45–23:30

Rotura con cuerpo desde las 23:30 hasta las 05:30 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.069 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 661, stop 622, por tiempo 105.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1388 | 50.6 % | -0.044 | -61.5 | 0.91 | -108.4 | -1.70 |
| Sin costes | 1388 | 50.9 % | +0.025 | +34.2 | 1.05 | -35.1 | +0.95 |
| Long | 788 | 52.2 % | -0.021 | -16.2 | 0.96 | -49.2 | -0.59 |
| Short | 600 | 48.5 % | -0.076 | -45.4 | 0.85 | -64.7 | -1.91 |
| 1.ª mitad | 694 | 49.0 % | -0.070 | -48.9 | 0.86 | -52.1 | -1.93 |
| 2.ª mitad | 694 | 52.2 % | -0.018 | -12.6 | 0.96 | -63.0 | -0.49 |

Por año (R neto medio y operaciones): 2018 -0.178 (55), 2019 -0.123 (160), 2020 -0.031 (173), 2021 -0.027 (171), 2022 -0.069 (177), 2023 -0.087 (156), 2024 -0.207 (169), 2025 +0.050 (172), 2026 +0.194 (155).

Sensibilidad (R neto medio y t): colchón 0 % -0.041 (t -1.54), colchón 50 % -0.033 (t -1.32), objetivo 1,5:1 -0.043 (t -1.38), objetivo 2:1 -0.020 (t -0.57).

