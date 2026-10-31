# ORB de 60 min de las 21:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 21:00–22:00 | 2069 | 50.9 | -0.006 | -0.31 | +0.040 | 0.046 | no |
| 21:15–22:15 | 2071 | 50.5 | -0.015 | -0.79 | +0.033 | 0.048 | no |
| 21:30–22:30 | 2080 | 50.6 | -0.019 | -0.96 | +0.031 | 0.050 | no |
| 21:45–22:45 | 2079 | 51.3 | -0.015 | -0.75 | +0.039 | 0.054 | no |

## Detalle

### ORB 21:00–22:00

Rotura con cuerpo desde las 22:00 hasta las 04:00 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2069.

**No pasa los criterios**. Coste medio 0.046 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 750, stop 657, por tiempo 662.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2069 | 50.9 % | -0.006 | -12.2 | 0.99 | -41.0 | -0.31 |
| Sin costes | 2069 | 52.1 % | +0.040 | +83.8 | 1.11 | -24.3 | +2.16 |
| Long | 1106 | 52.5 % | +0.009 | +9.7 | 1.02 | -35.9 | +0.35 |
| Short | 963 | 49.1 % | -0.023 | -21.9 | 0.94 | -45.9 | -0.81 |
| 1.ª mitad | 1035 | 50.0 % | -0.014 | -14.9 | 0.96 | -26.0 | -0.56 |
| 2.ª mitad | 1034 | 51.9 % | +0.003 | +2.7 | 1.01 | -39.4 | +0.10 |

Por año (R neto medio y operaciones): 2018 -0.009 (76), 2019 -0.016 (245), 2020 -0.002 (254), 2021 +0.020 (255), 2022 -0.062 (258), 2023 +0.028 (255), 2024 -0.068 (258), 2025 +0.017 (254), 2026 +0.048 (214).

Sensibilidad (R neto medio y t): colchón 0 % -0.002 (t -0.10), colchón 50 % -0.003 (t -0.19), objetivo 1,5:1 -0.012 (t -0.56), objetivo 2:1 -0.001 (t -0.05).

### ORB 21:15–22:15

Rotura con cuerpo desde las 22:15 hasta las 04:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2071.

**No pasa los criterios**. Coste medio 0.048 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 776, stop 706, por tiempo 589.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2071 | 50.5 % | -0.015 | -31.6 | 0.96 | -59.6 | -0.79 |
| Sin costes | 2071 | 51.1 % | +0.033 | +67.7 | 1.08 | -30.3 | +1.70 |
| Long | 1104 | 52.8 % | +0.002 | +2.1 | 1.00 | -35.0 | +0.07 |
| Short | 967 | 47.9 % | -0.035 | -33.6 | 0.92 | -52.2 | -1.22 |
| 1.ª mitad | 1036 | 49.6 % | -0.014 | -14.7 | 0.96 | -42.0 | -0.54 |
| 2.ª mitad | 1035 | 51.4 % | -0.016 | -16.9 | 0.96 | -52.6 | -0.58 |

Por año (R neto medio y operaciones): 2018 +0.092 (76), 2019 -0.058 (250), 2020 -0.055 (251), 2021 +0.039 (255), 2022 +0.020 (258), 2023 +0.013 (255), 2024 -0.126 (257), 2025 +0.006 (254), 2026 +0.011 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.009 (t -0.44), colchón 50 % -0.011 (t -0.62), objetivo 1,5:1 -0.016 (t -0.71), objetivo 2:1 -0.009 (t -0.37).

### ORB 21:30–22:30

Rotura con cuerpo desde las 22:30 hasta las 04:30 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2080.

**No pasa los criterios**. Coste medio 0.050 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 815, stop 750, por tiempo 515.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2080 | 50.6 % | -0.019 | -38.8 | 0.96 | -62.4 | -0.96 |
| Sin costes | 2080 | 51.2 % | +0.031 | +65.4 | 1.08 | -25.9 | +1.61 |
| Long | 1118 | 53.4 % | +0.013 | +15.0 | 1.03 | -30.0 | +0.51 |
| Short | 962 | 47.3 % | -0.056 | -53.8 | 0.88 | -74.2 | -1.93 |
| 1.ª mitad | 1040 | 49.5 % | -0.021 | -22.0 | 0.95 | -42.9 | -0.79 |
| 2.ª mitad | 1040 | 51.6 % | -0.016 | -16.8 | 0.96 | -44.1 | -0.57 |

Por año (R neto medio y operaciones): 2018 +0.107 (75), 2019 -0.055 (252), 2020 -0.050 (255), 2021 -0.027 (255), 2022 +0.038 (258), 2023 -0.009 (256), 2024 -0.080 (259), 2025 +0.022 (254), 2026 -0.027 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.023 (t -1.12), colchón 50 % -0.016 (t -0.90), objetivo 1,5:1 -0.020 (t -0.91), objetivo 2:1 -0.019 (t -0.80).

### ORB 21:45–22:45

Rotura con cuerpo desde las 22:45 hasta las 04:45 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2079.

**No pasa los criterios**. Coste medio 0.054 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 870, stop 789, por tiempo 420.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2079 | 51.3 % | -0.015 | -31.2 | 0.97 | -67.1 | -0.75 |
| Sin costes | 2079 | 51.9 % | +0.039 | +81.0 | 1.09 | -23.5 | +1.95 |
| Long | 1125 | 53.2 % | +0.011 | +12.0 | 1.03 | -31.7 | +0.40 |
| Short | 954 | 49.1 % | -0.045 | -43.3 | 0.90 | -63.0 | -1.53 |
| 1.ª mitad | 1040 | 51.9 % | +0.001 | +1.5 | 1.00 | -37.0 | +0.05 |
| 2.ª mitad | 1039 | 50.7 % | -0.032 | -32.8 | 0.93 | -61.6 | -1.09 |

Por año (R neto medio y operaciones): 2018 +0.118 (75), 2019 +0.001 (250), 2020 -0.041 (255), 2021 -0.028 (255), 2022 +0.043 (258), 2023 -0.056 (257), 2024 -0.084 (258), 2025 -0.013 (256), 2026 +0.026 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.036 (t -1.77), colchón 50 % -0.004 (t -0.21), objetivo 1,5:1 -0.007 (t -0.31), objetivo 2:1 +0.001 (t +0.02).

