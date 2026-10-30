# ORB de 30 min de las 21:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 21:00–21:30 | 2092 | 50.8 | -0.027 | -1.33 | +0.036 | 0.064 | no |
| 21:15–21:45 | 2087 | 51.1 | -0.024 | -1.16 | +0.039 | 0.063 | no |
| 21:30–22:00 | 2088 | 51.9 | -0.017 | -0.84 | +0.048 | 0.065 | no |
| 21:45–22:15 | 2093 | 49.9 | -0.062 | -2.95 | +0.009 | 0.070 | no |

## Detalle

### ORB 21:00–21:30

Rotura con cuerpo desde las 21:30 hasta las 03:30 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.064 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 921, stop 845, por tiempo 326.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2092 | 50.8 % | -0.027 | -56.7 | 0.94 | -92.5 | -1.33 |
| Sin costes | 2092 | 51.5 % | +0.036 | +76.1 | 1.08 | -19.3 | +1.78 |
| Long | 1123 | 52.3 % | -0.003 | -3.5 | 0.99 | -46.5 | -0.11 |
| Short | 969 | 49.1 % | -0.055 | -53.2 | 0.89 | -67.8 | -1.82 |
| 1.ª mitad | 1046 | 51.6 % | -0.011 | -11.8 | 0.97 | -24.8 | -0.40 |
| 2.ª mitad | 1046 | 50.0 % | -0.043 | -44.9 | 0.91 | -75.0 | -1.47 |

Por año (R neto medio y operaciones): 2018 -0.208 (76), 2019 -0.015 (254), 2020 +0.057 (257), 2021 -0.010 (259), 2022 -0.008 (258), 2023 -0.076 (258), 2024 -0.093 (258), 2025 -0.074 (256), 2026 +0.072 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.041 (t -1.95), colchón 50 % -0.013 (t -0.67), objetivo 1,5:1 -0.012 (t -0.52), objetivo 2:1 -0.005 (t -0.18).

### ORB 21:15–21:45

Rotura con cuerpo desde las 21:45 hasta las 03:45 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2087.

**No pasa los criterios**. Coste medio 0.063 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 931, stop 841, por tiempo 315.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2087 | 51.1 % | -0.024 | -49.5 | 0.95 | -90.8 | -1.16 |
| Sin costes | 2087 | 51.6 % | +0.039 | +81.6 | 1.09 | -23.8 | +1.91 |
| Long | 1116 | 52.1 % | -0.005 | -5.8 | 0.99 | -39.5 | -0.19 |
| Short | 971 | 50.1 % | -0.045 | -43.6 | 0.91 | -74.1 | -1.49 |
| 1.ª mitad | 1044 | 50.2 % | -0.033 | -34.5 | 0.93 | -43.9 | -1.16 |
| 2.ª mitad | 1043 | 52.1 % | -0.014 | -14.9 | 0.97 | -63.9 | -0.48 |

Por año (R neto medio y operaciones): 2018 +0.036 (76), 2019 -0.107 (252), 2020 +0.053 (257), 2021 -0.005 (258), 2022 -0.067 (258), 2023 -0.047 (255), 2024 -0.045 (259), 2025 -0.096 (257), 2026 +0.130 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.030 (t -1.44), colchón 50 % -0.005 (t -0.26), objetivo 1,5:1 -0.007 (t -0.31), objetivo 2:1 -0.003 (t -0.10).

### ORB 21:30–22:00

Rotura con cuerpo desde las 22:00 hasta las 04:00 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2088.

**No pasa los criterios**. Coste medio 0.065 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 953, stop 844, por tiempo 291.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2088 | 51.9 % | -0.017 | -36.1 | 0.96 | -76.5 | -0.84 |
| Sin costes | 2088 | 52.6 % | +0.048 | +100.0 | 1.11 | -34.5 | +2.33 |
| Long | 1113 | 53.1 % | -0.001 | -0.7 | 1.00 | -25.7 | -0.02 |
| Short | 975 | 50.6 % | -0.036 | -35.4 | 0.92 | -73.9 | -1.20 |
| 1.ª mitad | 1044 | 49.5 % | -0.052 | -53.8 | 0.89 | -67.9 | -1.81 |
| 2.ª mitad | 1044 | 54.3 % | +0.017 | +17.7 | 1.04 | -24.5 | +0.57 |

Por año (R neto medio y operaciones): 2018 -0.067 (76), 2019 -0.034 (252), 2020 -0.069 (257), 2021 -0.007 (259), 2022 -0.064 (258), 2023 -0.044 (256), 2024 +0.026 (259), 2025 +0.022 (256), 2026 +0.058 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.036 (t -1.69), colchón 50 % +0.000 (t +0.00), objetivo 1,5:1 -0.008 (t -0.34), objetivo 2:1 -0.015 (t -0.58).

### ORB 21:45–22:15

Rotura con cuerpo desde las 22:15 hasta las 04:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.070 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 949, stop 927, por tiempo 217.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2093 | 49.9 % | -0.062 | -129.3 | 0.88 | -135.5 | -2.95 |
| Sin costes | 2093 | 50.2 % | +0.009 | +18.0 | 1.02 | -43.0 | +0.41 |
| Long | 1121 | 52.4 % | -0.027 | -30.0 | 0.94 | -37.0 | -0.94 |
| Short | 972 | 47.1 % | -0.102 | -99.3 | 0.80 | -103.4 | -3.31 |
| 1.ª mitad | 1047 | 49.5 % | -0.062 | -65.1 | 0.87 | -72.1 | -2.14 |
| 2.ª mitad | 1046 | 50.4 % | -0.061 | -64.2 | 0.88 | -74.1 | -2.03 |

Por año (R neto medio y operaciones): 2018 -0.044 (76), 2019 -0.085 (255), 2020 -0.120 (256), 2021 -0.022 (259), 2022 -0.020 (258), 2023 -0.099 (258), 2024 -0.093 (259), 2025 +0.001 (256), 2026 -0.061 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.065 (t -3.04), colchón 50 % -0.047 (t -2.31), objetivo 1,5:1 -0.048 (t -1.93), objetivo 2:1 -0.044 (t -1.61).

