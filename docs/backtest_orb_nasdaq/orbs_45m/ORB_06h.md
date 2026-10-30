# ORB de 45 min de las 06:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 06:00–06:45 | 2094 | 49.9 | -0.050 | -2.30 | -0.004 | 0.046 | no |
| 06:15–07:00 | 2095 | 50.3 | -0.040 | -1.85 | +0.006 | 0.046 | no |
| 06:30–07:15 | 2094 | 51.2 | -0.017 | -0.77 | +0.025 | 0.042 | no |
| 06:45–07:30 | 2094 | 50.4 | -0.027 | -1.27 | +0.013 | 0.041 | no |

## Detalle

### ORB 06:00–06:45

Rotura con cuerpo desde las 06:45 hasta las 12:45; a esa hora se cierra. ORB completos: 2095; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.046 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 1014, stop 1026, por tiempo 54.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 49.9 % | -0.050 | -104.6 | 0.90 | -115.0 | -2.30 |
| Sin costes | 2094 | 49.9 % | -0.004 | -7.6 | 0.99 | -33.9 | -0.17 |
| Long | 1130 | 50.4 % | -0.039 | -43.7 | 0.92 | -52.4 | -1.31 |
| Short | 964 | 49.4 % | -0.063 | -60.9 | 0.88 | -69.5 | -1.98 |
| 1.ª mitad | 1047 | 50.3 % | -0.040 | -41.9 | 0.92 | -47.6 | -1.31 |
| 2.ª mitad | 1047 | 49.5 % | -0.060 | -62.6 | 0.89 | -75.7 | -1.95 |

Por año (R neto medio y operaciones): 2018 -0.091 (76), 2019 -0.053 (258), 2020 -0.024 (254), 2021 -0.068 (258), 2022 +0.028 (258), 2023 -0.127 (258), 2024 -0.028 (259), 2025 -0.079 (257), 2026 -0.032 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.054 (t -2.48), colchón 50 % -0.054 (t -2.53), objetivo 1,5:1 -0.048 (t -1.83), objetivo 2:1 -0.048 (t -1.61).

### ORB 06:15–07:00

Rotura con cuerpo desde las 07:00 hasta las 13:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.046 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 1029, stop 1016, por tiempo 50.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 50.3 % | -0.040 | -84.1 | 0.92 | -105.7 | -1.85 |
| Sin costes | 2095 | 50.3 % | +0.006 | +12.8 | 1.01 | -40.7 | +0.28 |
| Long | 1142 | 50.0 % | -0.052 | -59.3 | 0.90 | -73.8 | -1.77 |
| Short | 953 | 50.6 % | -0.026 | -24.8 | 0.95 | -51.7 | -0.81 |
| 1.ª mitad | 1048 | 50.0 % | -0.045 | -47.0 | 0.91 | -55.9 | -1.46 |
| 2.ª mitad | 1047 | 50.5 % | -0.035 | -37.1 | 0.93 | -57.4 | -1.16 |

Por año (R neto medio y operaciones): 2018 -0.021 (76), 2019 -0.084 (258), 2020 +0.010 (255), 2021 -0.082 (259), 2022 -0.027 (258), 2023 -0.117 (258), 2024 -0.065 (259), 2025 +0.031 (256), 2026 +0.018 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.030 (t -1.39), colchón 50 % -0.030 (t -1.41), objetivo 1,5:1 -0.033 (t -1.27), objetivo 2:1 -0.068 (t -2.29).

### ORB 06:30–07:15

Rotura con cuerpo desde las 07:15 hasta las 13:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.042 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 1045, stop 994, por tiempo 55.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 51.2 % | -0.017 | -34.8 | 0.97 | -57.1 | -0.77 |
| Sin costes | 2094 | 51.3 % | +0.025 | +52.9 | 1.05 | -25.1 | +1.17 |
| Long | 1136 | 50.5 % | -0.036 | -40.3 | 0.93 | -56.1 | -1.21 |
| Short | 958 | 52.0 % | +0.006 | +5.6 | 1.01 | -24.7 | +0.18 |
| 1.ª mitad | 1047 | 51.6 % | -0.007 | -7.5 | 0.99 | -33.4 | -0.23 |
| 2.ª mitad | 1047 | 50.8 % | -0.026 | -27.2 | 0.95 | -43.0 | -0.85 |

Por año (R neto medio y operaciones): 2018 +0.098 (76), 2019 -0.072 (258), 2020 +0.006 (255), 2021 -0.012 (259), 2022 +0.036 (258), 2023 -0.116 (258), 2024 -0.003 (259), 2025 +0.013 (256), 2026 -0.019 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.027 (t -1.26), colchón 50 % -0.009 (t -0.44), objetivo 1,5:1 -0.019 (t -0.72), objetivo 2:1 -0.021 (t -0.71).

### ORB 06:45–07:30

Rotura con cuerpo desde las 07:30 hasta las 13:30; a esa hora se cierra. ORB completos: 2095; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.041 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 1028, stop 1002, por tiempo 64.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 50.4 % | -0.027 | -57.2 | 0.95 | -84.9 | -1.27 |
| Sin costes | 2094 | 50.5 % | +0.013 | +27.9 | 1.03 | -45.8 | +0.62 |
| Long | 1096 | 50.0 % | -0.039 | -42.5 | 0.92 | -52.2 | -1.30 |
| Short | 998 | 50.8 % | -0.015 | -14.7 | 0.97 | -39.5 | -0.47 |
| 1.ª mitad | 1047 | 50.9 % | -0.013 | -13.2 | 0.97 | -47.1 | -0.41 |
| 2.ª mitad | 1047 | 49.9 % | -0.042 | -44.0 | 0.92 | -48.9 | -1.38 |

Por año (R neto medio y operaciones): 2018 +0.152 (76), 2019 +0.004 (258), 2020 -0.063 (254), 2021 -0.060 (259), 2022 +0.015 (258), 2023 -0.129 (258), 2024 +0.067 (259), 2025 -0.060 (257), 2026 -0.051 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.044 (t -2.03), colchón 50 % -0.030 (t -1.41), objetivo 1,5:1 -0.034 (t -1.31), objetivo 2:1 -0.050 (t -1.69).

