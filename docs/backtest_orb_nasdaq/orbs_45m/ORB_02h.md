# ORB de 45 min de las 02:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 02:00–02:45 | 2090 | 49.0 | -0.048 | -2.33 | -0.001 | 0.047 | no |
| 02:15–03:00 | 2090 | 48.6 | -0.070 | -3.37 | -0.020 | 0.049 | no |
| 02:30–03:15 | 2091 | 48.7 | -0.048 | -2.44 | -0.008 | 0.041 | no |
| 02:45–03:30 | 2078 | 49.4 | -0.034 | -1.78 | +0.003 | 0.037 | no |

## Detalle

### ORB 02:00–02:45

Rotura con cuerpo desde las 02:45 hasta las 08:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.047 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 887, stop 884, por tiempo 319.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2090 | 49.0 % | -0.048 | -99.7 | 0.90 | -113.3 | -2.33 |
| Sin costes | 2090 | 49.3 % | -0.001 | -1.8 | 1.00 | -43.9 | -0.04 |
| Long | 1113 | 50.3 % | -0.023 | -25.5 | 0.95 | -32.3 | -0.82 |
| Short | 977 | 47.6 % | -0.076 | -74.2 | 0.85 | -91.1 | -2.51 |
| 1.ª mitad | 1045 | 48.8 % | -0.041 | -43.3 | 0.91 | -56.9 | -1.46 |
| 2.ª mitad | 1045 | 49.3 % | -0.054 | -56.4 | 0.89 | -65.2 | -1.83 |

Por año (R neto medio y operaciones): 2018 +0.014 (76), 2019 -0.102 (257), 2020 -0.040 (252), 2021 -0.044 (259), 2022 -0.055 (257), 2023 +0.024 (258), 2024 -0.072 (258), 2025 -0.114 (257), 2026 +0.011 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.072 (t -3.45), colchón 50 % -0.044 (t -2.25), objetivo 1,5:1 -0.055 (t -2.32), objetivo 2:1 -0.057 (t -2.20).

### ORB 02:15–03:00

Rotura con cuerpo desde las 03:00 hasta las 09:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.049 R; ancho medio del ORB 0.21 %; cómo terminan: objetivo 896, stop 936, por tiempo 258.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2090 | 48.6 % | -0.070 | -145.9 | 0.86 | -146.9 | -3.37 |
| Sin costes | 2090 | 48.8 % | -0.020 | -42.7 | 0.96 | -74.8 | -0.99 |
| Long | 1081 | 50.1 % | -0.041 | -44.4 | 0.91 | -54.8 | -1.43 |
| Short | 1009 | 47.0 % | -0.101 | -101.5 | 0.80 | -108.3 | -3.36 |
| 1.ª mitad | 1045 | 49.6 % | -0.048 | -50.6 | 0.90 | -70.6 | -1.67 |
| 2.ª mitad | 1045 | 47.7 % | -0.091 | -95.3 | 0.82 | -97.9 | -3.08 |

Por año (R neto medio y operaciones): 2018 -0.120 (76), 2019 -0.114 (257), 2020 -0.065 (254), 2021 -0.044 (259), 2022 +0.005 (257), 2023 +0.030 (258), 2024 -0.156 (258), 2025 -0.156 (256), 2026 -0.038 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.071 (t -3.38), colchón 50 % -0.059 (t -2.96), objetivo 1,5:1 -0.088 (t -3.65), objetivo 2:1 -0.086 (t -3.30).

### ORB 02:30–03:15

Rotura con cuerpo desde las 03:15 hasta las 09:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.041 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 821, stop 830, por tiempo 440.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2091 | 48.7 % | -0.048 | -101.1 | 0.89 | -114.6 | -2.44 |
| Sin costes | 2091 | 49.3 % | -0.008 | -15.8 | 0.98 | -71.2 | -0.38 |
| Long | 1113 | 49.7 % | -0.029 | -32.2 | 0.93 | -57.6 | -1.07 |
| Short | 978 | 47.6 % | -0.070 | -68.9 | 0.85 | -80.9 | -2.42 |
| 1.ª mitad | 1046 | 50.8 % | -0.006 | -6.4 | 0.99 | -30.0 | -0.22 |
| 2.ª mitad | 1045 | 46.7 % | -0.091 | -94.7 | 0.82 | -105.2 | -3.16 |

Por año (R neto medio y operaciones): 2018 -0.008 (76), 2019 -0.045 (258), 2020 -0.001 (252), 2021 +0.018 (259), 2022 -0.071 (257), 2023 -0.023 (258), 2024 -0.196 (259), 2025 -0.056 (256), 2026 -0.018 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.048 (t -2.33), colchón 50 % -0.047 (t -2.52), objetivo 1,5:1 -0.051 (t -2.24), objetivo 2:1 -0.048 (t -1.96).

### ORB 02:45–03:30

Rotura con cuerpo desde las 03:30 hasta las 09:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2078.

**No pasa los criterios**. Coste medio 0.037 R; ancho medio del ORB 0.29 %; cómo terminan: objetivo 768, stop 745, por tiempo 565.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2078 | 49.4 % | -0.034 | -71.3 | 0.92 | -91.9 | -1.78 |
| Sin costes | 2078 | 49.9 % | +0.003 | +6.1 | 1.01 | -52.7 | +0.15 |
| Long | 1098 | 50.2 % | -0.017 | -18.2 | 0.96 | -50.7 | -0.63 |
| Short | 980 | 48.5 % | -0.054 | -53.1 | 0.88 | -64.0 | -1.92 |
| 1.ª mitad | 1039 | 50.8 % | +0.000 | +0.3 | 1.00 | -23.3 | +0.01 |
| 2.ª mitad | 1039 | 47.9 % | -0.069 | -71.6 | 0.85 | -75.9 | -2.44 |

Por año (R neto medio y operaciones): 2018 +0.030 (76), 2019 -0.053 (258), 2020 +0.053 (250), 2021 +0.030 (257), 2022 -0.080 (254), 2023 -0.039 (256), 2024 -0.075 (257), 2025 -0.097 (255), 2026 -0.031 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.042 (t -2.12), colchón 50 % -0.019 (t -1.05), objetivo 1,5:1 -0.022 (t -1.01), objetivo 2:1 -0.020 (t -0.84).

