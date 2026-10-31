# ORB de 15 min de las 13:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 13:00–13:15 | 2025 | 51.1 | -0.012 | -0.55 | +0.029 | 0.040 | no |
| 13:15–13:30 | 2025 | 50.5 | -0.014 | -0.68 | +0.028 | 0.042 | no |
| 13:30–13:45 | 2023 | 49.4 | -0.047 | -2.24 | -0.005 | 0.042 | no |
| 13:45–14:00 | 2021 | 47.8 | -0.079 | -3.79 | -0.036 | 0.043 | no |

## Detalle

### ORB 13:00–13:15

Rotura con cuerpo desde las 13:15 hasta las 19:15; a esa hora se cierra. ORB completos: 2042; con rotura: 2025.

**No pasa los criterios**. Coste medio 0.040 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 910, stop 854, por tiempo 261.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2025 | 51.1 % | -0.012 | -23.5 | 0.98 | -60.9 | -0.55 |
| Sin costes | 2025 | 51.4 % | +0.029 | +57.9 | 1.06 | -35.1 | +1.36 |
| Long | 1101 | 52.0 % | +0.008 | +8.7 | 1.02 | -33.3 | +0.28 |
| Short | 924 | 50.0 % | -0.035 | -32.1 | 0.93 | -49.4 | -1.11 |
| 1.ª mitad | 1013 | 52.4 % | +0.015 | +15.5 | 1.03 | -45.3 | +0.51 |
| 2.ª mitad | 1012 | 49.8 % | -0.039 | -39.0 | 0.92 | -60.9 | -1.30 |

Por año (R neto medio y operaciones): 2018 +0.090 (73), 2019 +0.010 (250), 2020 -0.041 (250), 2021 -0.067 (251), 2022 +0.172 (249), 2023 +0.010 (248), 2024 -0.072 (250), 2025 -0.086 (246), 2026 -0.057 (208).

Sensibilidad (R neto medio y t): colchón 0 % -0.016 (t -0.76), colchón 50 % -0.013 (t -0.64), objetivo 1,5:1 -0.012 (t -0.48), objetivo 2:1 -0.008 (t -0.28).

### ORB 13:15–13:30

Rotura con cuerpo desde las 13:30 hasta las 19:30; a esa hora se cierra. ORB completos: 2026; con rotura: 2025.

**No pasa los criterios**. Coste medio 0.042 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 921, stop 853, por tiempo 251.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2025 | 50.5 % | -0.014 | -29.0 | 0.97 | -76.6 | -0.68 |
| Sin costes | 2025 | 50.8 % | +0.028 | +56.8 | 1.06 | -49.9 | +1.33 |
| Long | 1103 | 51.4 % | -0.007 | -7.8 | 0.98 | -33.9 | -0.25 |
| Short | 922 | 49.5 % | -0.023 | -21.2 | 0.95 | -48.8 | -0.73 |
| 1.ª mitad | 1013 | 49.5 % | -0.046 | -46.7 | 0.91 | -76.6 | -1.54 |
| 2.ª mitad | 1012 | 51.6 % | +0.018 | +17.7 | 1.04 | -16.8 | +0.59 |

Por año (R neto medio y operaciones): 2018 +0.009 (73), 2019 -0.101 (249), 2020 -0.056 (251), 2021 -0.144 (251), 2022 +0.120 (250), 2023 -0.008 (248), 2024 -0.005 (249), 2025 +0.083 (247), 2026 -0.007 (207).

Sensibilidad (R neto medio y t): colchón 0 % -0.015 (t -0.68), colchón 50 % -0.025 (t -1.24), objetivo 1,5:1 -0.022 (t -0.89), objetivo 2:1 -0.005 (t -0.19).

### ORB 13:30–13:45

Rotura con cuerpo desde las 13:45 hasta las 19:45; a esa hora se cierra. ORB completos: 2026; con rotura: 2023.

**No pasa los criterios**. Coste medio 0.042 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 872, stop 881, por tiempo 270.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2023 | 49.4 % | -0.047 | -95.0 | 0.90 | -126.0 | -2.24 |
| Sin costes | 2023 | 49.6 % | -0.005 | -9.4 | 0.99 | -72.4 | -0.22 |
| Long | 1070 | 50.6 % | -0.029 | -31.4 | 0.94 | -54.1 | -1.03 |
| Short | 953 | 48.1 % | -0.067 | -63.6 | 0.86 | -83.0 | -2.17 |
| 1.ª mitad | 1012 | 49.0 % | -0.068 | -68.7 | 0.86 | -100.8 | -2.27 |
| 2.ª mitad | 1011 | 49.8 % | -0.026 | -26.3 | 0.94 | -43.9 | -0.89 |

Por año (R neto medio y operaciones): 2018 +0.186 (73), 2019 -0.012 (249), 2020 -0.132 (251), 2021 -0.141 (251), 2022 -0.037 (250), 2023 +0.005 (247), 2024 -0.034 (249), 2025 -0.011 (245), 2026 -0.084 (208).

Sensibilidad (R neto medio y t): colchón 0 % -0.046 (t -2.14), colchón 50 % -0.054 (t -2.67), objetivo 1,5:1 -0.060 (t -2.47), objetivo 2:1 -0.059 (t -2.22).

### ORB 13:45–14:00

Rotura con cuerpo desde las 14:00 hasta las 20:00; a esa hora se cierra. ORB completos: 2025; con rotura: 2021.

**No pasa los criterios**. Coste medio 0.043 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 842, stop 910, por tiempo 269.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2021 | 47.8 % | -0.079 | -160.4 | 0.84 | -170.3 | -3.79 |
| Sin costes | 2021 | 48.0 % | -0.036 | -73.5 | 0.92 | -99.9 | -1.73 |
| Long | 1024 | 50.4 % | -0.029 | -29.4 | 0.94 | -44.2 | -0.99 |
| Short | 997 | 45.1 % | -0.131 | -131.0 | 0.75 | -139.3 | -4.37 |
| 1.ª mitad | 1011 | 45.7 % | -0.119 | -119.9 | 0.77 | -131.1 | -3.96 |
| 2.ª mitad | 1010 | 49.9 % | -0.040 | -40.6 | 0.91 | -50.3 | -1.37 |

Por año (R neto medio y operaciones): 2018 +0.066 (73), 2019 -0.169 (249), 2020 -0.061 (250), 2021 -0.134 (251), 2022 -0.156 (249), 2023 -0.054 (247), 2024 +0.042 (248), 2025 -0.039 (247), 2026 -0.110 (207).

Sensibilidad (R neto medio y t): colchón 0 % -0.072 (t -3.36), colchón 50 % -0.087 (t -4.30), objetivo 1,5:1 -0.063 (t -2.55), objetivo 2:1 -0.062 (t -2.31).

