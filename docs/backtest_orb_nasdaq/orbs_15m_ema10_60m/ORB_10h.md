# ORB de 15 min de las 10:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 10:00–10:15 | 1568 | 52.6 | +0.030 | +1.32 | +0.052 | 0.021 | no |
| 10:15–10:30 | 1519 | 54.0 | +0.040 | +1.70 | +0.065 | 0.025 | no |
| 10:30–10:45 | 1455 | 49.6 | -0.021 | -0.85 | +0.006 | 0.026 | no |
| 10:45–11:00 | 1508 | 51.7 | +0.008 | +0.32 | +0.035 | 0.028 | no |

## Detalle

### ORB 10:00–10:15

Rotura con cuerpo desde las 10:15 hasta las 16:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.42 %; cómo terminan: objetivo 651, stop 577, por tiempo 340.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1568 | 52.6 % | +0.030 | +47.4 | 1.07 | -25.9 | +1.32 |
| Sin costes | 1568 | 52.9 % | +0.052 | +80.8 | 1.13 | -24.3 | +2.25 |
| Long | 851 | 55.0 % | +0.062 | +53.0 | 1.16 | -16.7 | +2.02 |
| Short | 717 | 49.7 % | -0.008 | -5.6 | 0.98 | -24.8 | -0.23 |
| 1.ª mitad | 784 | 54.0 % | +0.063 | +49.1 | 1.15 | -16.5 | +1.91 |
| 2.ª mitad | 784 | 51.1 % | -0.002 | -1.7 | 0.99 | -25.9 | -0.07 |

Por año (R neto medio y operaciones): 2018 -0.138 (54), 2019 +0.141 (181), 2020 +0.039 (187), 2021 +0.047 (200), 2022 +0.055 (202), 2023 -0.060 (198), 2024 +0.126 (200), 2025 +0.002 (182), 2026 -0.074 (164).

Sensibilidad (R neto medio y t): colchón 0 % +0.038 (t +1.59), colchón 50 % +0.028 (t +1.31), objetivo 1,5:1 +0.052 (t +1.98), objetivo 2:1 +0.062 (t +2.18).

### ORB 10:15–10:30

Rotura con cuerpo desde las 10:30 hasta las 16:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.025 R; ancho medio del ORB 0.37 %; cómo terminan: objetivo 665, stop 585, por tiempo 269.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1519 | 54.0 % | +0.040 | +61.2 | 1.10 | -21.2 | +1.70 |
| Sin costes | 1519 | 54.3 % | +0.065 | +99.0 | 1.16 | -16.8 | +2.75 |
| Long | 818 | 56.5 % | +0.062 | +50.5 | 1.15 | -16.9 | +1.92 |
| Short | 701 | 51.2 % | +0.015 | +10.7 | 1.03 | -24.6 | +0.43 |
| 1.ª mitad | 760 | 55.0 % | +0.051 | +38.6 | 1.12 | -18.1 | +1.50 |
| 2.ª mitad | 759 | 53.1 % | +0.030 | +22.6 | 1.07 | -16.7 | +0.90 |

Por año (R neto medio y operaciones): 2018 +0.024 (49), 2019 +0.037 (185), 2020 +0.093 (186), 2021 +0.045 (181), 2022 +0.005 (190), 2023 -0.000 (193), 2024 +0.073 (195), 2025 -0.021 (191), 2026 +0.111 (149).

Sensibilidad (R neto medio y t): colchón 0 % +0.040 (t +1.65), colchón 50 % +0.039 (t +1.71), objetivo 1,5:1 +0.063 (t +2.27), objetivo 2:1 +0.082 (t +2.71).

### ORB 10:30–10:45

Rotura con cuerpo desde las 10:45 hasta las 16:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.026 R; ancho medio del ORB 0.35 %; cómo terminan: objetivo 588, stop 587, por tiempo 280.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1455 | 49.6 % | -0.021 | -29.9 | 0.95 | -64.3 | -0.85 |
| Sin costes | 1455 | 50.1 % | +0.006 | +8.2 | 1.01 | -36.8 | +0.23 |
| Long | 798 | 51.8 % | +0.014 | +11.4 | 1.03 | -17.7 | +0.44 |
| Short | 657 | 46.9 % | -0.063 | -41.2 | 0.87 | -62.6 | -1.74 |
| 1.ª mitad | 728 | 50.0 % | -0.017 | -12.5 | 0.96 | -35.7 | -0.50 |
| 2.ª mitad | 727 | 49.1 % | -0.024 | -17.4 | 0.95 | -31.8 | -0.71 |

Por año (R neto medio y operaciones): 2018 +0.056 (50), 2019 +0.062 (174), 2020 -0.055 (175), 2021 -0.067 (186), 2022 -0.054 (179), 2023 -0.017 (180), 2024 +0.014 (184), 2025 -0.066 (178), 2026 +0.004 (149).

Sensibilidad (R neto medio y t): colchón 0 % -0.040 (t -1.60), colchón 50 % +0.013 (t +0.57), objetivo 1,5:1 -0.007 (t -0.23), objetivo 2:1 +0.004 (t +0.14).

### ORB 10:45–11:00

Rotura con cuerpo desde las 11:00 hasta las 17:00; a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.028 R; ancho medio del ORB 0.33 %; cómo terminan: objetivo 672, stop 615, por tiempo 221.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1508 | 51.7 % | +0.008 | +11.5 | 1.02 | -41.3 | +0.32 |
| Sin costes | 1508 | 52.1 % | +0.035 | +53.3 | 1.08 | -36.1 | +1.47 |
| Long | 830 | 53.7 % | +0.039 | +32.7 | 1.09 | -23.1 | +1.22 |
| Short | 678 | 49.1 % | -0.031 | -21.2 | 0.93 | -44.7 | -0.86 |
| 1.ª mitad | 754 | 54.2 % | +0.051 | +38.6 | 1.12 | -12.4 | +1.50 |
| 2.ª mitad | 754 | 49.1 % | -0.036 | -27.1 | 0.92 | -41.3 | -1.06 |

Por año (R neto medio y operaciones): 2018 +0.141 (52), 2019 +0.027 (179), 2020 +0.091 (183), 2021 +0.052 (173), 2022 -0.037 (194), 2023 +0.004 (190), 2024 +0.058 (186), 2025 -0.193 (188), 2026 +0.033 (163).

Sensibilidad (R neto medio y t): colchón 0 % -0.014 (t -0.57), colchón 50 % +0.014 (t +0.60), objetivo 1,5:1 +0.015 (t +0.53), objetivo 2:1 +0.029 (t +0.93).

