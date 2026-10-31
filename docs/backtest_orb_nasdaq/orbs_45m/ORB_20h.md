# ORB de 45 min de las 20:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 20:00–20:45 | 2061 | 48.6 | -0.035 | -1.98 | +0.010 | 0.045 | no |
| 20:15–21:00 | 2068 | 49.1 | -0.033 | -1.80 | +0.017 | 0.051 | no |
| 20:30–21:15 | 2066 | 49.2 | -0.026 | -1.33 | +0.027 | 0.052 | no |
| 20:45–21:30 | 2081 | 50.2 | -0.025 | -1.26 | +0.029 | 0.054 | no |

## Detalle

### ORB 20:00–20:45

Rotura con cuerpo desde las 20:45 hasta las 02:45 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2061.

**No pasa los criterios**. Coste medio 0.045 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 601, stop 561, por tiempo 899.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2061 | 48.6 % | -0.035 | -71.8 | 0.91 | -115.1 | -1.98 |
| Sin costes | 2061 | 50.4 % | +0.010 | +20.7 | 1.03 | -41.7 | +0.57 |
| Long | 1128 | 51.2 % | -0.013 | -14.5 | 0.96 | -37.8 | -0.54 |
| Short | 933 | 45.6 % | -0.061 | -57.3 | 0.84 | -85.3 | -2.34 |
| 1.ª mitad | 1031 | 47.5 % | -0.047 | -48.9 | 0.87 | -60.4 | -1.93 |
| 2.ª mitad | 1030 | 49.7 % | -0.022 | -23.0 | 0.94 | -64.5 | -0.88 |

Por año (R neto medio y operaciones): 2018 -0.015 (75), 2019 -0.086 (254), 2020 -0.009 (253), 2021 -0.070 (252), 2022 -0.067 (251), 2023 -0.074 (254), 2024 -0.071 (256), 2025 +0.019 (254), 2026 +0.096 (212).

Sensibilidad (R neto medio y t): colchón 0 % -0.050 (t -2.67), colchón 50 % -0.032 (t -2.02), objetivo 1,5:1 -0.015 (t -0.76), objetivo 2:1 -0.016 (t -0.78).

### ORB 20:15–21:00

Rotura con cuerpo desde las 21:00 hasta las 03:00 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2068.

**No pasa los criterios**. Coste medio 0.051 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 688, stop 655, por tiempo 725.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2068 | 49.1 % | -0.033 | -69.2 | 0.92 | -96.3 | -1.80 |
| Sin costes | 2068 | 50.6 % | +0.017 | +35.4 | 1.05 | -21.8 | +0.92 |
| Long | 1126 | 50.4 % | -0.015 | -16.9 | 0.96 | -40.5 | -0.60 |
| Short | 942 | 47.6 % | -0.055 | -52.2 | 0.87 | -67.1 | -2.01 |
| 1.ª mitad | 1034 | 48.7 % | -0.036 | -37.5 | 0.91 | -45.4 | -1.39 |
| 2.ª mitad | 1034 | 49.5 % | -0.031 | -31.7 | 0.92 | -57.3 | -1.16 |

Por año (R neto medio y operaciones): 2018 +0.019 (75), 2019 -0.096 (254), 2020 -0.011 (254), 2021 -0.014 (255), 2022 -0.057 (250), 2023 -0.069 (256), 2024 -0.081 (257), 2025 -0.015 (253), 2026 +0.077 (214).

Sensibilidad (R neto medio y t): colchón 0 % -0.056 (t -2.89), colchón 50 % -0.032 (t -1.90), objetivo 1,5:1 -0.021 (t -0.99), objetivo 2:1 -0.012 (t -0.54).

### ORB 20:30–21:15

Rotura con cuerpo desde las 21:15 hasta las 03:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2066.

**No pasa los criterios**. Coste medio 0.052 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 765, stop 698, por tiempo 603.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2066 | 49.2 % | -0.026 | -52.8 | 0.94 | -83.7 | -1.33 |
| Sin costes | 2066 | 50.5 % | +0.027 | +55.1 | 1.07 | -28.5 | +1.39 |
| Long | 1118 | 51.3 % | -0.005 | -5.5 | 0.99 | -50.8 | -0.19 |
| Short | 948 | 46.7 % | -0.050 | -47.2 | 0.88 | -53.1 | -1.75 |
| 1.ª mitad | 1033 | 49.8 % | -0.013 | -13.2 | 0.97 | -28.6 | -0.47 |
| 2.ª mitad | 1033 | 48.6 % | -0.038 | -39.6 | 0.91 | -70.6 | -1.40 |

Por año (R neto medio y operaciones): 2018 -0.023 (75), 2019 -0.084 (253), 2020 +0.015 (253), 2021 +0.028 (255), 2022 -0.005 (253), 2023 -0.117 (256), 2024 -0.080 (255), 2025 -0.036 (254), 2026 +0.096 (212).

Sensibilidad (R neto medio y t): colchón 0 % -0.040 (t -1.99), colchón 50 % -0.015 (t -0.87), objetivo 1,5:1 -0.019 (t -0.86), objetivo 2:1 -0.010 (t -0.42).

### ORB 20:45–21:30

Rotura con cuerpo desde las 21:30 hasta las 03:30 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2081.

**No pasa los criterios**. Coste medio 0.054 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 818, stop 754, por tiempo 509.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2081 | 50.2 % | -0.025 | -51.5 | 0.94 | -78.8 | -1.26 |
| Sin costes | 2081 | 51.2 % | +0.029 | +59.9 | 1.07 | -25.9 | +1.47 |
| Long | 1128 | 51.9 % | -0.003 | -3.9 | 0.99 | -41.8 | -0.13 |
| Short | 953 | 48.3 % | -0.050 | -47.6 | 0.89 | -61.4 | -1.71 |
| 1.ª mitad | 1041 | 51.1 % | -0.018 | -18.3 | 0.96 | -26.6 | -0.64 |
| 2.ª mitad | 1040 | 49.3 % | -0.032 | -33.2 | 0.93 | -59.4 | -1.14 |

Por año (R neto medio y operaciones): 2018 -0.149 (76), 2019 -0.026 (252), 2020 +0.032 (256), 2021 +0.001 (256), 2022 -0.022 (258), 2023 -0.055 (257), 2024 -0.119 (257), 2025 -0.025 (254), 2026 +0.069 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.034 (t -1.66), colchón 50 % -0.010 (t -0.57), objetivo 1,5:1 -0.016 (t -0.71), objetivo 2:1 -0.008 (t -0.31).

