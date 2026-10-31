# ORB de 60 min de las 01:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 01:00–02:00 | 2088 | 50.3 | -0.044 | -2.17 | +0.007 | 0.051 | no |
| 01:15–02:15 | 2087 | 49.4 | -0.044 | -2.20 | +0.003 | 0.047 | no |
| 01:30–02:30 | 2080 | 49.9 | -0.037 | -1.87 | +0.007 | 0.044 | no |
| 01:45–02:45 | 2087 | 49.3 | -0.038 | -1.88 | +0.005 | 0.043 | no |

## Detalle

### ORB 01:00–02:00

Rotura con cuerpo desde las 02:00 hasta las 08:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2088.

**No pasa los criterios**. Coste medio 0.051 R; ancho medio del ORB 0.21 %; cómo terminan: objetivo 886, stop 878, por tiempo 324.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2088 | 50.3 % | -0.044 | -92.8 | 0.91 | -112.6 | -2.17 |
| Sin costes | 2088 | 50.7 % | +0.007 | +14.0 | 1.02 | -41.4 | +0.33 |
| Long | 1100 | 53.3 % | -0.001 | -1.4 | 1.00 | -31.0 | -0.04 |
| Short | 988 | 47.1 % | -0.093 | -91.4 | 0.82 | -100.1 | -3.07 |
| 1.ª mitad | 1044 | 50.7 % | -0.043 | -44.9 | 0.91 | -56.0 | -1.49 |
| 2.ª mitad | 1044 | 50.0 % | -0.046 | -47.9 | 0.90 | -65.4 | -1.58 |

Por año (R neto medio y operaciones): 2018 +0.047 (76), 2019 -0.098 (257), 2020 +0.048 (254), 2021 -0.100 (258), 2022 -0.046 (258), 2023 -0.017 (258), 2024 -0.043 (258), 2025 -0.120 (254), 2026 +0.001 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.041 (t -1.93), colchón 50 % -0.032 (t -1.63), objetivo 1,5:1 -0.040 (t -1.71), objetivo 2:1 -0.049 (t -1.91).

### ORB 01:15–02:15

Rotura con cuerpo desde las 02:15 hasta las 08:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2087.

**No pasa los criterios**. Coste medio 0.047 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 839, stop 832, por tiempo 416.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2087 | 49.4 % | -0.044 | -91.9 | 0.90 | -124.5 | -2.20 |
| Sin costes | 2087 | 50.0 % | +0.003 | +6.0 | 1.01 | -38.6 | +0.14 |
| Long | 1134 | 51.8 % | -0.005 | -5.5 | 0.99 | -32.9 | -0.18 |
| Short | 953 | 46.7 % | -0.091 | -86.4 | 0.81 | -102.3 | -3.02 |
| 1.ª mitad | 1044 | 48.6 % | -0.054 | -56.2 | 0.88 | -72.9 | -1.93 |
| 2.ª mitad | 1043 | 50.3 % | -0.034 | -35.7 | 0.93 | -59.5 | -1.19 |

Por año (R neto medio y operaciones): 2018 +0.140 (76), 2019 -0.106 (257), 2020 -0.026 (252), 2021 -0.078 (259), 2022 -0.081 (258), 2023 -0.001 (258), 2024 -0.078 (257), 2025 -0.047 (254), 2026 +0.023 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.041 (t -2.00), colchón 50 % -0.037 (t -1.97), objetivo 1,5:1 -0.042 (t -1.80), objetivo 2:1 -0.053 (t -2.13).

### ORB 01:30–02:30

Rotura con cuerpo desde las 02:30 hasta las 08:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2080.

**No pasa los criterios**. Coste medio 0.044 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 833, stop 808, por tiempo 439.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2080 | 49.9 % | -0.037 | -77.5 | 0.92 | -115.6 | -1.87 |
| Sin costes | 2080 | 50.4 % | +0.007 | +14.4 | 1.02 | -39.8 | +0.35 |
| Long | 1120 | 52.1 % | -0.008 | -9.2 | 0.98 | -32.8 | -0.31 |
| Short | 960 | 47.4 % | -0.071 | -68.2 | 0.85 | -86.3 | -2.38 |
| 1.ª mitad | 1040 | 49.0 % | -0.052 | -53.8 | 0.88 | -72.9 | -1.87 |
| 2.ª mitad | 1040 | 50.8 % | -0.023 | -23.6 | 0.95 | -47.8 | -0.80 |

Por año (R neto medio y operaciones): 2018 +0.153 (76), 2019 -0.133 (258), 2020 -0.043 (248), 2021 -0.071 (258), 2022 -0.044 (257), 2023 -0.025 (257), 2024 -0.060 (258), 2025 -0.052 (253), 2026 +0.095 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.049 (t -2.36), colchón 50 % -0.034 (t -1.83), objetivo 1,5:1 -0.043 (t -1.91), objetivo 2:1 -0.046 (t -1.86).

### ORB 01:45–02:45

Rotura con cuerpo desde las 02:45 hasta las 08:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2087.

**No pasa los criterios**. Coste medio 0.043 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 840, stop 828, por tiempo 419.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2087 | 49.3 % | -0.038 | -78.6 | 0.92 | -93.9 | -1.88 |
| Sin costes | 2087 | 49.7 % | +0.005 | +10.5 | 1.01 | -42.0 | +0.25 |
| Long | 1102 | 51.4 % | -0.002 | -2.6 | 0.99 | -28.0 | -0.09 |
| Short | 985 | 46.9 % | -0.077 | -76.0 | 0.84 | -92.6 | -2.62 |
| 1.ª mitad | 1044 | 49.5 % | -0.025 | -26.3 | 0.94 | -41.6 | -0.91 |
| 2.ª mitad | 1043 | 49.0 % | -0.050 | -52.3 | 0.89 | -66.9 | -1.74 |

Por año (R neto medio y operaciones): 2018 +0.000 (76), 2019 -0.066 (257), 2020 -0.014 (251), 2021 -0.035 (259), 2022 -0.035 (256), 2023 -0.003 (258), 2024 -0.053 (258), 2025 -0.134 (256), 2026 +0.039 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.053 (t -2.59), colchón 50 % -0.037 (t -1.98), objetivo 1,5:1 -0.045 (t -1.99), objetivo 2:1 -0.042 (t -1.68).

