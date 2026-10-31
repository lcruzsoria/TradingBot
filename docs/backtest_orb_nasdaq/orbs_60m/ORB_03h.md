# ORB de 60 min de las 03:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 03:00–04:00 | 2087 | 50.6 | -0.016 | -0.78 | +0.015 | 0.031 | no |
| 03:15–04:15 | 2090 | 50.0 | -0.026 | -1.29 | +0.005 | 0.032 | no |
| 03:30–04:30 | 2091 | 50.1 | -0.031 | -1.48 | +0.002 | 0.033 | no |
| 03:45–04:45 | 2092 | 49.9 | -0.026 | -1.24 | +0.008 | 0.034 | no |

## Detalle

### ORB 03:00–04:00

Rotura con cuerpo desde las 04:00 hasta las 10:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2087.

**No pasa los criterios**. Coste medio 0.031 R; ancho medio del ORB 0.35 %; cómo terminan: objetivo 855, stop 833, por tiempo 399.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2087 | 50.6 % | -0.016 | -32.7 | 0.96 | -52.4 | -0.78 |
| Sin costes | 2087 | 50.8 % | +0.015 | +32.2 | 1.04 | -37.5 | +0.77 |
| Long | 1128 | 51.2 % | -0.008 | -8.6 | 0.98 | -32.0 | -0.28 |
| Short | 959 | 49.8 % | -0.025 | -24.1 | 0.94 | -41.6 | -0.84 |
| 1.ª mitad | 1044 | 50.4 % | -0.025 | -26.2 | 0.94 | -52.4 | -0.91 |
| 2.ª mitad | 1043 | 50.8 % | -0.006 | -6.5 | 0.99 | -33.7 | -0.22 |

Por año (R neto medio y operaciones): 2018 +0.109 (76), 2019 -0.072 (257), 2020 -0.077 (254), 2021 +0.023 (256), 2022 -0.006 (257), 2023 +0.024 (257), 2024 +0.030 (259), 2025 +0.003 (255), 2026 -0.101 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.031 (t -1.49), colchón 50 % -0.010 (t -0.51), objetivo 1,5:1 +0.004 (t +0.17), objetivo 2:1 -0.005 (t -0.18).

### ORB 03:15–04:15

Rotura con cuerpo desde las 04:15 hasta las 10:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.032 R; ancho medio del ORB 0.34 %; cómo terminan: objetivo 891, stop 879, por tiempo 320.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2090 | 50.0 % | -0.026 | -55.3 | 0.94 | -79.4 | -1.29 |
| Sin costes | 2090 | 50.2 % | +0.005 | +10.6 | 1.01 | -40.0 | +0.25 |
| Long | 1119 | 50.1 % | -0.017 | -19.5 | 0.96 | -32.3 | -0.63 |
| Short | 971 | 49.7 % | -0.037 | -35.9 | 0.92 | -60.7 | -1.22 |
| 1.ª mitad | 1045 | 49.3 % | -0.044 | -46.4 | 0.90 | -54.9 | -1.56 |
| 2.ª mitad | 1045 | 50.6 % | -0.009 | -9.0 | 0.98 | -28.4 | -0.29 |

Por año (R neto medio y operaciones): 2018 +0.074 (76), 2019 -0.117 (256), 2020 -0.052 (254), 2021 +0.011 (259), 2022 -0.052 (258), 2023 -0.076 (258), 2024 +0.093 (258), 2025 +0.015 (255), 2026 -0.072 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.021 (t -1.02), colchón 50 % -0.022 (t -1.16), objetivo 1,5:1 -0.031 (t -1.31), objetivo 2:1 -0.022 (t -0.83).

### ORB 03:30–04:30

Rotura con cuerpo desde las 04:30 hasta las 10:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.033 R; ancho medio del ORB 0.33 %; cómo terminan: objetivo 909, stop 918, por tiempo 264.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2091 | 50.1 % | -0.031 | -64.2 | 0.94 | -92.9 | -1.48 |
| Sin costes | 2091 | 50.2 % | +0.002 | +4.0 | 1.00 | -51.1 | +0.09 |
| Long | 1122 | 50.6 % | -0.024 | -26.7 | 0.95 | -42.7 | -0.85 |
| Short | 969 | 49.5 % | -0.039 | -37.5 | 0.92 | -62.5 | -1.26 |
| 1.ª mitad | 1046 | 49.8 % | -0.049 | -51.2 | 0.90 | -62.8 | -1.68 |
| 2.ª mitad | 1045 | 50.4 % | -0.012 | -13.0 | 0.97 | -30.1 | -0.42 |

Por año (R neto medio y operaciones): 2018 +0.047 (76), 2019 -0.089 (257), 2020 -0.104 (253), 2021 +0.017 (259), 2022 -0.062 (258), 2023 -0.090 (258), 2024 +0.102 (259), 2025 -0.002 (256), 2026 -0.045 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.013 (t -0.60), colchón 50 % -0.029 (t -1.47), objetivo 1,5:1 -0.036 (t -1.49), objetivo 2:1 -0.023 (t -0.85).

### ORB 03:45–04:45

Rotura con cuerpo desde las 04:45 hasta las 10:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.034 R; ancho medio del ORB 0.32 %; cómo terminan: objetivo 951, stop 930, por tiempo 211.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2092 | 49.9 % | -0.026 | -54.6 | 0.95 | -100.7 | -1.24 |
| Sin costes | 2092 | 50.1 % | +0.008 | +16.1 | 1.02 | -63.2 | +0.37 |
| Long | 1119 | 50.5 % | -0.015 | -16.4 | 0.97 | -49.7 | -0.51 |
| Short | 973 | 49.1 % | -0.039 | -38.2 | 0.92 | -69.6 | -1.27 |
| 1.ª mitad | 1046 | 48.2 % | -0.062 | -64.4 | 0.88 | -76.0 | -2.08 |
| 2.ª mitad | 1046 | 51.5 % | +0.009 | +9.8 | 1.02 | -26.0 | +0.32 |

Por año (R neto medio y operaciones): 2018 +0.135 (76), 2019 -0.097 (257), 2020 -0.134 (254), 2021 -0.021 (259), 2022 -0.049 (258), 2023 -0.084 (258), 2024 +0.115 (259), 2025 +0.059 (255), 2026 -0.052 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.026 (t -1.21), colchón 50 % -0.022 (t -1.10), objetivo 1,5:1 -0.010 (t -0.41), objetivo 2:1 -0.004 (t -0.16).

