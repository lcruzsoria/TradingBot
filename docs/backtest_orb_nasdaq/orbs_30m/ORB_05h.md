# ORB de 30 min de las 05:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 05:00–05:30 | 2096 | 50.3 | -0.046 | -2.12 | +0.009 | 0.055 | no |
| 05:15–05:45 | 2097 | 49.2 | -0.075 | -3.45 | -0.018 | 0.057 | no |
| 05:30–06:00 | 2095 | 48.0 | -0.099 | -4.55 | -0.041 | 0.058 | no |
| 05:45–06:15 | 2093 | 49.8 | -0.058 | -2.67 | -0.002 | 0.056 | no |

## Detalle

### ORB 05:00–05:30

Rotura con cuerpo desde las 05:30 hasta las 11:30; a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.055 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 1043, stop 1025, por tiempo 28.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 50.3 % | -0.046 | -96.8 | 0.91 | -133.5 | -2.12 |
| Sin costes | 2096 | 50.4 % | +0.009 | +19.2 | 1.02 | -36.3 | +0.42 |
| Long | 1114 | 50.2 % | -0.050 | -55.9 | 0.90 | -80.5 | -1.68 |
| Short | 982 | 50.5 % | -0.042 | -40.9 | 0.92 | -62.7 | -1.31 |
| 1.ª mitad | 1048 | 51.0 % | -0.034 | -35.8 | 0.93 | -64.0 | -1.11 |
| 2.ª mitad | 1048 | 49.6 % | -0.058 | -61.0 | 0.89 | -87.0 | -1.89 |

Por año (R neto medio y operaciones): 2018 +0.088 (76), 2019 -0.030 (257), 2020 -0.098 (256), 2021 -0.046 (259), 2022 -0.022 (258), 2023 -0.140 (258), 2024 -0.005 (259), 2025 -0.061 (257), 2026 +0.001 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.061 (t -2.80), colchón 50 % -0.038 (t -1.75), objetivo 1,5:1 -0.054 (t -2.03), objetivo 2:1 -0.081 (t -2.72).

### ORB 05:15–05:45

Rotura con cuerpo desde las 05:45 hasta las 11:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.057 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 1016, stop 1055, por tiempo 26.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 49.2 % | -0.075 | -157.2 | 0.86 | -182.2 | -3.45 |
| Sin costes | 2097 | 49.2 % | -0.018 | -37.4 | 0.96 | -77.8 | -0.82 |
| Long | 1105 | 49.4 % | -0.071 | -78.9 | 0.87 | -107.1 | -2.39 |
| Short | 992 | 48.9 % | -0.079 | -78.3 | 0.85 | -93.2 | -2.49 |
| 1.ª mitad | 1049 | 48.4 % | -0.093 | -97.5 | 0.83 | -115.0 | -3.03 |
| 2.ª mitad | 1048 | 49.9 % | -0.057 | -59.7 | 0.89 | -77.7 | -1.85 |

Por año (R neto medio y operaciones): 2018 +0.012 (76), 2019 -0.116 (258), 2020 -0.137 (256), 2021 -0.056 (259), 2022 -0.107 (258), 2023 -0.145 (258), 2024 -0.042 (259), 2025 -0.029 (257), 2026 +0.022 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.099 (t -4.53), colchón 50 % -0.052 (t -2.39), objetivo 1,5:1 -0.072 (t -2.75), objetivo 2:1 -0.063 (t -2.09).

### ORB 05:30–06:00

Rotura con cuerpo desde las 06:00 hasta las 12:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.058 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 994, stop 1079, por tiempo 22.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 48.0 % | -0.099 | -207.5 | 0.82 | -221.3 | -4.55 |
| Sin costes | 2095 | 48.0 % | -0.041 | -85.6 | 0.92 | -118.9 | -1.88 |
| Long | 1076 | 48.4 % | -0.095 | -102.2 | 0.83 | -105.3 | -3.13 |
| Short | 1019 | 47.5 % | -0.103 | -105.3 | 0.81 | -120.2 | -3.32 |
| 1.ª mitad | 1048 | 46.7 % | -0.127 | -133.2 | 0.77 | -144.2 | -4.15 |
| 2.ª mitad | 1047 | 49.3 % | -0.071 | -74.2 | 0.87 | -87.5 | -2.30 |

Por año (R neto medio y operaciones): 2018 -0.051 (76), 2019 -0.127 (258), 2020 -0.058 (255), 2021 -0.168 (258), 2022 -0.170 (258), 2023 -0.173 (258), 2024 +0.046 (259), 2025 -0.103 (257), 2026 -0.047 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.114 (t -5.22), colchón 50 % -0.079 (t -3.65), objetivo 1,5:1 -0.071 (t -2.70), objetivo 2:1 -0.073 (t -2.43).

### ORB 05:45–06:15

Rotura con cuerpo desde las 06:15 hasta las 12:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.056 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 1036, stop 1037, por tiempo 20.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2093 | 49.8 % | -0.058 | -121.8 | 0.89 | -129.6 | -2.67 |
| Sin costes | 2093 | 49.8 % | -0.002 | -4.1 | 1.00 | -38.0 | -0.09 |
| Long | 1119 | 50.2 % | -0.053 | -59.5 | 0.90 | -64.3 | -1.78 |
| Short | 974 | 49.4 % | -0.064 | -62.3 | 0.88 | -76.0 | -2.00 |
| 1.ª mitad | 1047 | 50.0 % | -0.054 | -56.9 | 0.90 | -70.7 | -1.77 |
| 2.ª mitad | 1046 | 49.6 % | -0.062 | -64.9 | 0.88 | -76.5 | -2.01 |

Por año (R neto medio y operaciones): 2018 -0.079 (76), 2019 -0.098 (257), 2020 -0.025 (254), 2021 -0.042 (258), 2022 -0.017 (258), 2023 -0.152 (258), 2024 -0.017 (259), 2025 -0.081 (257), 2026 -0.023 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.069 (t -3.18), colchón 50 % -0.055 (t -2.52), objetivo 1,5:1 -0.061 (t -2.28), objetivo 2:1 -0.057 (t -1.88).

