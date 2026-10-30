# ORB de 60 min de las 12:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 12:00–13:00 | 2020 | 48.8 | -0.025 | -1.46 | -0.003 | 0.021 | no |
| 12:15–13:15 | 1962 | 50.7 | +0.006 | +0.36 | +0.027 | 0.021 | no |
| 12:30–13:30 | 1947 | 49.5 | -0.010 | -0.59 | +0.012 | 0.022 | no |
| 12:45–13:45 | 1950 | 49.4 | -0.016 | -0.91 | +0.006 | 0.022 | no |

## Detalle

### ORB 12:00–13:00

Rotura con cuerpo desde las 13:00 hasta las 19:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2020.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.48 %; cómo terminan: objetivo 506, stop 521, por tiempo 993.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2020 | 48.8 % | -0.025 | -50.0 | 0.93 | -64.4 | -1.46 |
| Sin costes | 2020 | 49.6 % | -0.003 | -6.7 | 0.99 | -36.8 | -0.20 |
| Long | 1130 | 52.3 % | +0.005 | +5.6 | 1.02 | -20.8 | +0.22 |
| Short | 890 | 44.3 % | -0.062 | -55.6 | 0.83 | -65.0 | -2.41 |
| 1.ª mitad | 1010 | 47.9 % | -0.041 | -41.8 | 0.89 | -55.3 | -1.68 |
| 2.ª mitad | 1010 | 49.6 % | -0.008 | -8.2 | 0.98 | -25.9 | -0.35 |

Por año (R neto medio y operaciones): 2018 -0.087 (73), 2019 -0.036 (249), 2020 -0.054 (254), 2021 -0.074 (247), 2022 +0.020 (253), 2023 -0.028 (243), 2024 +0.033 (251), 2025 -0.056 (245), 2026 +0.021 (205).

Sensibilidad (R neto medio y t): colchón 0 % -0.016 (t -0.87), colchón 50 % -0.014 (t -0.92), objetivo 1,5:1 -0.012 (t -0.63), objetivo 2:1 -0.008 (t -0.40).

### ORB 12:15–13:15

Rotura con cuerpo desde las 13:15 hasta las 19:15; a esa hora se cierra. ORB completos: 2042; con rotura: 1962.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.47 %; cómo terminan: objetivo 516, stop 471, por tiempo 975.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1962 | 50.7 % | +0.006 | +12.2 | 1.02 | -31.6 | +0.36 |
| Sin costes | 1962 | 51.6 % | +0.027 | +53.8 | 1.08 | -24.8 | +1.58 |
| Long | 1092 | 53.1 % | +0.036 | +39.0 | 1.11 | -21.9 | +1.56 |
| Short | 870 | 47.6 % | -0.031 | -26.8 | 0.91 | -47.4 | -1.17 |
| 1.ª mitad | 981 | 51.5 % | +0.016 | +15.4 | 1.05 | -27.4 | +0.63 |
| 2.ª mitad | 981 | 49.8 % | -0.003 | -3.2 | 0.99 | -31.6 | -0.14 |

Por año (R neto medio y operaciones): 2018 +0.126 (70), 2019 +0.028 (243), 2020 -0.055 (246), 2021 -0.011 (241), 2022 +0.079 (245), 2023 +0.028 (240), 2024 +0.003 (239), 2025 -0.083 (238), 2026 +0.028 (200).

Sensibilidad (R neto medio y t): colchón 0 % +0.008 (t +0.44), colchón 50 % +0.004 (t +0.23), objetivo 1,5:1 +0.013 (t +0.66), objetivo 2:1 +0.013 (t +0.66).

### ORB 12:30–13:30

Rotura con cuerpo desde las 13:30 hasta las 19:30; a esa hora se cierra. ORB completos: 2025; con rotura: 1947.

**No pasa los criterios**. Coste medio 0.022 R; ancho medio del ORB 0.47 %; cómo terminan: objetivo 484, stop 472, por tiempo 991.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1947 | 49.5 % | -0.010 | -19.7 | 0.97 | -57.5 | -0.59 |
| Sin costes | 1947 | 50.4 % | +0.012 | +22.6 | 1.04 | -38.4 | +0.67 |
| Long | 1103 | 52.0 % | +0.019 | +20.9 | 1.06 | -16.1 | +0.83 |
| Short | 844 | 46.1 % | -0.048 | -40.5 | 0.87 | -53.8 | -1.81 |
| 1.ª mitad | 974 | 48.8 % | -0.028 | -27.2 | 0.92 | -57.5 | -1.11 |
| 2.ª mitad | 973 | 50.2 % | +0.008 | +7.5 | 1.02 | -18.2 | +0.33 |

Por año (R neto medio y operaciones): 2018 +0.094 (70), 2019 -0.099 (241), 2020 -0.090 (247), 2021 -0.020 (240), 2022 +0.117 (241), 2023 +0.009 (241), 2024 -0.030 (236), 2025 -0.006 (237), 2026 +0.014 (194).

Sensibilidad (R neto medio y t): colchón 0 % -0.006 (t -0.30), colchón 50 % -0.003 (t -0.21), objetivo 1,5:1 -0.006 (t -0.31), objetivo 2:1 +0.001 (t +0.07).

### ORB 12:45–13:45

Rotura con cuerpo desde las 13:45 hasta las 19:45; a esa hora se cierra. ORB completos: 2025; con rotura: 1950.

**No pasa los criterios**. Coste medio 0.022 R; ancho medio del ORB 0.47 %; cómo terminan: objetivo 464, stop 445, por tiempo 1041.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1950 | 49.4 % | -0.016 | -30.2 | 0.95 | -44.9 | -0.91 |
| Sin costes | 1950 | 49.9 % | +0.006 | +12.1 | 1.02 | -23.5 | +0.36 |
| Long | 1100 | 51.2 % | -0.001 | -1.3 | 1.00 | -23.4 | -0.05 |
| Short | 850 | 47.1 % | -0.034 | -28.9 | 0.90 | -43.4 | -1.30 |
| 1.ª mitad | 975 | 49.6 % | -0.017 | -16.1 | 0.95 | -38.8 | -0.67 |
| 2.ª mitad | 975 | 49.1 % | -0.014 | -14.1 | 0.95 | -34.0 | -0.62 |

Por año (R neto medio y operaciones): 2018 +0.127 (70), 2019 -0.118 (243), 2020 +0.006 (247), 2021 -0.011 (241), 2022 +0.044 (241), 2023 -0.013 (240), 2024 -0.037 (238), 2025 -0.021 (236), 2026 -0.017 (194).

Sensibilidad (R neto medio y t): colchón 0 % -0.013 (t -0.71), colchón 50 % -0.003 (t -0.21), objetivo 1,5:1 -0.013 (t -0.69), objetivo 2:1 -0.006 (t -0.30).

