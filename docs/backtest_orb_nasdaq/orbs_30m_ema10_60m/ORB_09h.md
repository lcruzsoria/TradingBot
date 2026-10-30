# ORB de 30 min de las 09:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 09:00–09:30 | 1644 | 50.5 | -0.018 | -0.77 | +0.009 | 0.028 | no |
| 09:15–09:45 | 1822 | 53.3 | +0.037 | +1.88 | +0.052 | 0.016 | no |
| 09:30–10:00 | 1881 | 50.7 | -0.004 | -0.21 | +0.010 | 0.013 | no |
| 09:45–10:15 | 1752 | 52.3 | +0.015 | +0.81 | +0.031 | 0.015 | no |

## Detalle

### ORB 09:00–09:30

Rotura con cuerpo desde las 09:30 hasta las 15:30; a esa hora se cierra. ORB completos: 2092; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.028 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 780, stop 764, por tiempo 100.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1644 | 50.5 % | -0.018 | -30.3 | 0.96 | -57.9 | -0.77 |
| Sin costes | 1644 | 50.7 % | +0.009 | +15.6 | 1.02 | -37.7 | +0.39 |
| Long | 859 | 50.5 % | -0.023 | -19.9 | 0.95 | -23.4 | -0.69 |
| Short | 785 | 50.6 % | -0.013 | -10.5 | 0.97 | -46.7 | -0.38 |
| 1.ª mitad | 822 | 48.5 % | -0.060 | -49.7 | 0.88 | -57.9 | -1.77 |
| 2.ª mitad | 822 | 52.6 % | +0.024 | +19.4 | 1.05 | -22.3 | +0.69 |

Por año (R neto medio y operaciones): 2018 -0.197 (60), 2019 +0.044 (210), 2020 -0.074 (195), 2021 -0.089 (214), 2022 -0.018 (197), 2023 +0.056 (202), 2024 +0.035 (196), 2025 -0.019 (205), 2026 -0.030 (165).

Sensibilidad (R neto medio y t): colchón 0 % -0.007 (t -0.28), colchón 50 % +0.013 (t +0.53), objetivo 1,5:1 +0.011 (t +0.39), objetivo 2:1 +0.032 (t +0.97).

### ORB 09:15–09:45

Rotura con cuerpo desde las 09:45 hasta las 15:45; a esa hora se cierra. ORB completos: 2091; con rotura: 2079.

**No pasa los criterios**. Coste medio 0.016 R; ancho medio del ORB 0.56 %; cómo terminan: objetivo 604, stop 545, por tiempo 673.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1822 | 53.3 % | +0.037 | +67.0 | 1.10 | -14.7 | +1.88 |
| Sin costes | 1822 | 53.7 % | +0.052 | +95.6 | 1.15 | -13.3 | +2.68 |
| Long | 954 | 56.6 % | +0.057 | +54.3 | 1.16 | -14.6 | +2.13 |
| Short | 868 | 49.7 % | +0.015 | +12.8 | 1.04 | -12.9 | +0.51 |
| 1.ª mitad | 911 | 53.0 % | +0.028 | +25.1 | 1.08 | -14.7 | +1.00 |
| 2.ª mitad | 911 | 53.6 % | +0.046 | +41.9 | 1.13 | -14.6 | +1.66 |

Por año (R neto medio y operaciones): 2018 -0.083 (71), 2019 +0.068 (226), 2020 -0.004 (221), 2021 +0.094 (228), 2022 +0.032 (228), 2023 +0.021 (229), 2024 +0.041 (217), 2025 +0.060 (217), 2026 +0.016 (185).

Sensibilidad (R neto medio y t): colchón 0 % +0.033 (t +1.60), colchón 50 % +0.032 (t +1.79), objetivo 1,5:1 +0.050 (t +2.26), objetivo 2:1 +0.051 (t +2.20).

### ORB 09:30–10:00

Rotura con cuerpo desde las 10:00 hasta las 16:00; a esa hora se cierra. ORB completos: 2093; con rotura: 2053.

**No pasa los criterios**. Coste medio 0.013 R; ancho medio del ORB 0.69 %; cómo terminan: objetivo 448, stop 467, por tiempo 966.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1881 | 50.7 % | -0.004 | -6.9 | 0.99 | -37.4 | -0.21 |
| Sin costes | 1881 | 51.2 % | +0.010 | +18.1 | 1.03 | -30.2 | +0.55 |
| Long | 993 | 55.2 % | +0.027 | +27.2 | 1.09 | -14.1 | +1.16 |
| Short | 888 | 45.7 % | -0.038 | -34.1 | 0.90 | -41.6 | -1.46 |
| 1.ª mitad | 941 | 49.5 % | -0.024 | -22.2 | 0.93 | -37.4 | -0.94 |
| 2.ª mitad | 940 | 51.9 % | +0.016 | +15.3 | 1.05 | -15.8 | +0.66 |

Por año (R neto medio y operaciones): 2018 -0.129 (71), 2019 +0.010 (228), 2020 -0.081 (231), 2021 +0.008 (237), 2022 +0.037 (235), 2023 -0.014 (233), 2024 +0.065 (230), 2025 -0.003 (227), 2026 -0.018 (189).

Sensibilidad (R neto medio y t): colchón 0 % +0.010 (t +0.50), colchón 50 % -0.006 (t -0.37), objetivo 1,5:1 +0.002 (t +0.12), objetivo 2:1 +0.001 (t +0.07).

### ORB 09:45–10:15

Rotura con cuerpo desde las 10:15 hasta las 16:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2060.

**No pasa los criterios**. Coste medio 0.015 R; ancho medio del ORB 0.62 %; cómo terminan: objetivo 493, stop 470, por tiempo 789.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1752 | 52.3 % | +0.015 | +27.1 | 1.04 | -24.5 | +0.81 |
| Sin costes | 1752 | 52.7 % | +0.031 | +53.5 | 1.09 | -22.0 | +1.61 |
| Long | 955 | 54.7 % | +0.022 | +20.7 | 1.06 | -20.2 | +0.86 |
| Short | 797 | 49.6 % | +0.008 | +6.4 | 1.02 | -23.0 | +0.28 |
| 1.ª mitad | 876 | 54.5 % | +0.044 | +38.8 | 1.13 | -18.0 | +1.62 |
| 2.ª mitad | 876 | 50.2 % | -0.013 | -11.7 | 0.96 | -24.5 | -0.51 |

Por año (R neto medio y operaciones): 2018 -0.106 (65), 2019 +0.094 (201), 2020 +0.024 (213), 2021 +0.069 (221), 2022 +0.037 (220), 2023 -0.036 (215), 2024 +0.045 (214), 2025 -0.008 (217), 2026 -0.073 (186).

Sensibilidad (R neto medio y t): colchón 0 % +0.030 (t +1.48), colchón 50 % +0.008 (t +0.47), objetivo 1,5:1 +0.020 (t +0.97), objetivo 2:1 +0.026 (t +1.19).

