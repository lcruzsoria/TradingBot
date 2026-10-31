# ORB de 45 min de las 01:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 01:00–01:45 | 2090 | 50.6 | -0.046 | -2.22 | +0.012 | 0.059 | no |
| 01:15–02:00 | 2093 | 50.5 | -0.049 | -2.34 | +0.010 | 0.060 | no |
| 01:30–02:15 | 2090 | 49.6 | -0.047 | -2.28 | +0.005 | 0.051 | no |
| 01:45–02:30 | 2090 | 49.2 | -0.059 | -2.89 | -0.010 | 0.049 | no |

## Detalle

### ORB 01:00–01:45

Rotura con cuerpo desde las 01:45 hasta las 07:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.059 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 943, stop 923, por tiempo 224.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2090 | 50.6 % | -0.046 | -97.2 | 0.90 | -129.9 | -2.22 |
| Sin costes | 2090 | 51.0 % | +0.012 | +25.9 | 1.03 | -36.6 | +0.59 |
| Long | 1107 | 53.3 % | -0.004 | -4.8 | 0.99 | -38.4 | -0.15 |
| Short | 983 | 47.6 % | -0.094 | -92.4 | 0.82 | -106.1 | -3.06 |
| 1.ª mitad | 1045 | 50.0 % | -0.056 | -58.7 | 0.89 | -72.7 | -1.90 |
| 2.ª mitad | 1045 | 51.2 % | -0.037 | -38.4 | 0.92 | -71.4 | -1.24 |

Por año (R neto medio y operaciones): 2018 +0.038 (76), 2019 -0.083 (257), 2020 +0.012 (254), 2021 -0.139 (259), 2022 -0.036 (258), 2023 +0.002 (258), 2024 -0.075 (259), 2025 -0.132 (254), 2026 +0.073 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.031 (t -1.48), colchón 50 % -0.053 (t -2.62), objetivo 1,5:1 -0.053 (t -2.13), objetivo 2:1 -0.056 (t -2.06).

### ORB 01:15–02:00

Rotura con cuerpo desde las 02:00 hasta las 08:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.060 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 961, stop 931, por tiempo 201.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2093 | 50.5 % | -0.049 | -102.9 | 0.90 | -121.1 | -2.34 |
| Sin costes | 2093 | 50.7 % | +0.010 | +21.8 | 1.02 | -33.0 | +0.50 |
| Long | 1098 | 53.7 % | +0.002 | +2.2 | 1.00 | -27.2 | +0.07 |
| Short | 995 | 46.9 % | -0.106 | -105.1 | 0.80 | -109.4 | -3.44 |
| 1.ª mitad | 1047 | 50.1 % | -0.059 | -61.8 | 0.88 | -80.7 | -1.99 |
| 2.ª mitad | 1046 | 50.9 % | -0.039 | -41.1 | 0.92 | -48.7 | -1.32 |

Por año (R neto medio y operaciones): 2018 +0.115 (76), 2019 -0.120 (258), 2020 -0.005 (254), 2021 -0.067 (259), 2022 -0.090 (258), 2023 -0.039 (258), 2024 -0.018 (258), 2025 -0.058 (256), 2026 -0.043 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.063 (t -2.94), colchón 50 % -0.042 (t -2.06), objetivo 1,5:1 -0.044 (t -1.78), objetivo 2:1 -0.063 (t -2.35).

### ORB 01:30–02:15

Rotura con cuerpo desde las 02:15 hasta las 08:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.051 R; ancho medio del ORB 0.21 %; cómo terminan: objetivo 892, stop 880, por tiempo 318.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2090 | 49.6 % | -0.047 | -97.7 | 0.90 | -132.7 | -2.28 |
| Sin costes | 2090 | 50.0 % | +0.005 | +9.9 | 1.01 | -43.4 | +0.23 |
| Long | 1135 | 51.5 % | -0.015 | -17.3 | 0.97 | -43.5 | -0.55 |
| Short | 955 | 47.2 % | -0.084 | -80.4 | 0.83 | -99.6 | -2.74 |
| 1.ª mitad | 1045 | 48.3 % | -0.067 | -69.9 | 0.86 | -85.5 | -2.33 |
| 2.ª mitad | 1045 | 50.8 % | -0.027 | -27.8 | 0.94 | -55.6 | -0.91 |

Por año (R neto medio y operaciones): 2018 +0.122 (76), 2019 -0.134 (258), 2020 -0.043 (252), 2021 -0.051 (259), 2022 -0.112 (258), 2023 +0.018 (258), 2024 -0.085 (258), 2025 -0.032 (255), 2026 +0.028 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.051 (t -2.43), colchón 50 % -0.039 (t -1.98), objetivo 1,5:1 -0.037 (t -1.55), objetivo 2:1 -0.053 (t -2.05).

### ORB 01:45–02:30

Rotura con cuerpo desde las 02:30 hasta las 08:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.049 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 869, stop 887, por tiempo 334.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2090 | 49.2 % | -0.059 | -123.0 | 0.88 | -154.3 | -2.89 |
| Sin costes | 2090 | 49.5 % | -0.010 | -20.2 | 0.98 | -62.7 | -0.47 |
| Long | 1113 | 52.1 % | -0.013 | -14.1 | 0.97 | -41.9 | -0.46 |
| Short | 977 | 45.9 % | -0.112 | -108.9 | 0.78 | -121.1 | -3.71 |
| 1.ª mitad | 1045 | 49.1 % | -0.060 | -62.7 | 0.87 | -80.2 | -2.11 |
| 2.ª mitad | 1045 | 49.3 % | -0.058 | -60.3 | 0.88 | -81.1 | -1.98 |

Por año (R neto medio y operaciones): 2018 +0.124 (76), 2019 -0.176 (258), 2020 -0.040 (252), 2021 -0.074 (259), 2022 -0.054 (257), 2023 -0.086 (258), 2024 -0.093 (258), 2025 -0.063 (256), 2026 +0.085 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.070 (t -3.37), colchón 50 % -0.037 (t -1.93), objetivo 1,5:1 -0.044 (t -1.86), objetivo 2:1 -0.050 (t -1.98).

