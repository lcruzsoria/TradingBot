# ORB de 45 min de las 19:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 19:00–19:45 | 1322 | 49.2 | -0.063 | -2.59 | -0.007 | 0.056 | no |
| 19:15–20:00 | 1301 | 48.7 | -0.043 | -1.78 | +0.012 | 0.055 | no |
| 19:30–20:15 | 1378 | 50.4 | -0.014 | -0.63 | +0.035 | 0.049 | no |
| 19:45–20:30 | 1403 | 50.5 | -0.011 | -0.53 | +0.034 | 0.046 | no |

## Detalle

### ORB 19:00–19:45

Rotura con cuerpo desde las 19:45 hasta las 01:45 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2075.

**No pasa los criterios**. Coste medio 0.056 R; ancho medio del ORB 0.20 %; cómo terminan: objetivo 479, stop 489, por tiempo 354.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1322 | 49.2 % | -0.063 | -83.1 | 0.86 | -95.7 | -2.59 |
| Sin costes | 1322 | 49.6 % | -0.007 | -8.7 | 0.98 | -36.7 | -0.27 |
| Long | 761 | 51.2 % | -0.034 | -25.9 | 0.92 | -41.9 | -1.07 |
| Short | 561 | 46.5 % | -0.102 | -57.2 | 0.78 | -62.5 | -2.70 |
| 1.ª mitad | 661 | 49.2 % | -0.052 | -34.2 | 0.88 | -40.4 | -1.48 |
| 2.ª mitad | 661 | 49.3 % | -0.074 | -48.9 | 0.83 | -55.6 | -2.19 |

Por año (R neto medio y operaciones): 2018 +0.067 (42), 2019 -0.083 (169), 2020 -0.027 (158), 2021 -0.009 (159), 2022 -0.154 (150), 2023 -0.161 (150), 2024 -0.017 (152), 2025 -0.021 (183), 2026 -0.078 (159).

Sensibilidad (R neto medio y t): colchón 0 % -0.066 (t -2.64), colchón 50 % -0.067 (t -2.94), objetivo 1,5:1 -0.061 (t -2.21), objetivo 2:1 -0.061 (t -2.06).

### ORB 19:15–20:00

Rotura con cuerpo desde las 20:00 hasta las 02:00 (día siguiente); a esa hora se cierra. ORB completos: 2095; con rotura: 2073.

**No pasa los criterios**. Coste medio 0.055 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 478, stop 458, por tiempo 365.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1301 | 48.7 % | -0.043 | -56.1 | 0.90 | -66.8 | -1.78 |
| Sin costes | 1301 | 49.3 % | +0.012 | +15.7 | 1.03 | -26.9 | +0.50 |
| Long | 756 | 51.1 % | -0.016 | -11.8 | 0.96 | -35.4 | -0.50 |
| Short | 545 | 45.5 % | -0.081 | -44.2 | 0.83 | -46.9 | -2.11 |
| 1.ª mitad | 651 | 50.2 % | -0.021 | -13.8 | 0.95 | -26.5 | -0.61 |
| 2.ª mitad | 650 | 47.2 % | -0.065 | -42.3 | 0.85 | -46.5 | -1.91 |

Por año (R neto medio y operaciones): 2018 +0.082 (46), 2019 -0.086 (171), 2020 +0.004 (155), 2021 -0.034 (158), 2022 -0.063 (142), 2023 -0.102 (146), 2024 +0.013 (158), 2025 -0.078 (177), 2026 -0.034 (148).

Sensibilidad (R neto medio y t): colchón 0 % -0.044 (t -1.75), colchón 50 % -0.045 (t -1.98), objetivo 1,5:1 -0.034 (t -1.23), objetivo 2:1 -0.025 (t -0.85).

### ORB 19:30–20:15

Rotura con cuerpo desde las 20:15 hasta las 02:15 (día siguiente); a esa hora se cierra. ORB completos: 2095; con rotura: 2067.

**No pasa los criterios**. Coste medio 0.049 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 459, stop 399, por tiempo 520.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1378 | 50.4 % | -0.014 | -19.5 | 0.96 | -53.1 | -0.63 |
| Sin costes | 1378 | 51.0 % | +0.035 | +47.8 | 1.10 | -25.9 | +1.55 |
| Long | 790 | 51.6 % | +0.019 | +14.7 | 1.05 | -24.0 | +0.65 |
| Short | 588 | 48.6 % | -0.058 | -34.2 | 0.86 | -48.9 | -1.65 |
| 1.ª mitad | 689 | 50.9 % | -0.005 | -3.2 | 0.99 | -18.6 | -0.15 |
| 2.ª mitad | 689 | 49.8 % | -0.024 | -16.2 | 0.94 | -39.3 | -0.74 |

Por año (R neto medio y operaciones): 2018 +0.149 (48), 2019 -0.067 (179), 2020 +0.064 (149), 2021 -0.041 (173), 2022 -0.077 (164), 2023 -0.079 (165), 2024 -0.016 (169), 2025 +0.026 (176), 2026 +0.044 (155).

Sensibilidad (R neto medio y t): colchón 0 % -0.008 (t -0.34), colchón 50 % -0.028 (t -1.35), objetivo 1,5:1 -0.020 (t -0.80), objetivo 2:1 -0.014 (t -0.52).

### ORB 19:45–20:30

Rotura con cuerpo desde las 20:30 hasta las 02:30 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2062.

**No pasa los criterios**. Coste medio 0.046 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 435, stop 378, por tiempo 590.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1403 | 50.5 % | -0.011 | -16.0 | 0.97 | -49.3 | -0.53 |
| Sin costes | 1403 | 51.7 % | +0.034 | +47.9 | 1.10 | -14.8 | +1.59 |
| Long | 806 | 52.0 % | -0.003 | -2.3 | 0.99 | -23.2 | -0.10 |
| Short | 597 | 48.6 % | -0.023 | -13.7 | 0.94 | -39.0 | -0.68 |
| 1.ª mitad | 702 | 48.9 % | -0.027 | -18.8 | 0.93 | -34.1 | -0.88 |
| 2.ª mitad | 701 | 52.2 % | +0.004 | +2.8 | 1.01 | -26.0 | +0.13 |

Por año (R neto medio y operaciones): 2018 +0.187 (42), 2019 -0.082 (174), 2020 -0.008 (168), 2021 -0.048 (174), 2022 -0.039 (169), 2023 -0.052 (167), 2024 -0.011 (182), 2025 +0.057 (172), 2026 +0.050 (155).

Sensibilidad (R neto medio y t): colchón 0 % -0.011 (t -0.47), colchón 50 % -0.028 (t -1.41), objetivo 1,5:1 -0.009 (t -0.39), objetivo 2:1 +0.007 (t +0.29).

