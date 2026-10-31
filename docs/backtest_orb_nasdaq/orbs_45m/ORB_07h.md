# ORB de 45 min de las 07:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 07:00–07:45 | 2094 | 49.8 | -0.043 | -2.01 | -0.003 | 0.040 | no |
| 07:15–08:00 | 2096 | 51.4 | -0.016 | -0.73 | +0.025 | 0.041 | no |
| 07:30–08:15 | 2094 | 49.4 | -0.050 | -2.34 | -0.013 | 0.037 | no |
| 07:45–08:30 | 2092 | 49.2 | -0.053 | -2.47 | -0.018 | 0.035 | no |

## Detalle

### ORB 07:00–07:45

Rotura con cuerpo desde las 07:45 hasta las 13:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.040 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 999, stop 1007, por tiempo 88.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 49.8 % | -0.043 | -90.3 | 0.92 | -116.5 | -2.01 |
| Sin costes | 2094 | 49.9 % | -0.003 | -7.1 | 0.99 | -59.7 | -0.16 |
| Long | 1060 | 49.8 % | -0.052 | -55.5 | 0.90 | -68.5 | -1.73 |
| Short | 1034 | 49.8 % | -0.034 | -34.8 | 0.93 | -51.2 | -1.10 |
| 1.ª mitad | 1047 | 51.5 % | -0.008 | -8.6 | 0.98 | -42.1 | -0.27 |
| 2.ª mitad | 1047 | 48.1 % | -0.078 | -81.7 | 0.85 | -85.0 | -2.57 |

Por año (R neto medio y operaciones): 2018 +0.117 (76), 2019 +0.015 (258), 2020 -0.022 (254), 2021 -0.081 (259), 2022 +0.023 (258), 2023 -0.203 (258), 2024 -0.012 (259), 2025 -0.036 (257), 2026 -0.083 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.088 (t -4.05), colchón 50 % -0.044 (t -2.06), objetivo 1,5:1 -0.059 (t -2.28), objetivo 2:1 -0.040 (t -1.36).

### ORB 07:15–08:00

Rotura con cuerpo desde las 08:00 hasta las 14:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.041 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 1037, stop 990, por tiempo 69.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 51.4 % | -0.016 | -33.1 | 0.97 | -90.3 | -0.73 |
| Sin costes | 2096 | 51.4 % | +0.025 | +52.6 | 1.05 | -49.5 | +1.17 |
| Long | 1054 | 52.2 % | -0.005 | -5.3 | 0.99 | -39.4 | -0.16 |
| Short | 1042 | 50.7 % | -0.027 | -27.8 | 0.95 | -64.3 | -0.88 |
| 1.ª mitad | 1048 | 54.0 % | +0.033 | +34.3 | 1.07 | -22.1 | +1.08 |
| 2.ª mitad | 1048 | 48.9 % | -0.064 | -67.4 | 0.88 | -84.3 | -2.11 |

Por año (R neto medio y operaciones): 2018 +0.199 (76), 2019 +0.051 (258), 2020 -0.002 (255), 2021 +0.005 (259), 2022 -0.003 (258), 2023 -0.106 (258), 2024 -0.062 (259), 2025 -0.048 (257), 2026 -0.026 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.027 (t -1.24), colchón 50 % -0.015 (t -0.69), objetivo 1,5:1 -0.041 (t -1.58), objetivo 2:1 -0.046 (t -1.56).

### ORB 07:30–08:15

Rotura con cuerpo desde las 08:15 hasta las 14:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.037 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 985, stop 1014, por tiempo 95.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 49.4 % | -0.050 | -105.0 | 0.90 | -124.8 | -2.34 |
| Sin costes | 2094 | 49.5 % | -0.013 | -27.0 | 0.97 | -64.4 | -0.60 |
| Long | 1075 | 50.0 % | -0.044 | -47.3 | 0.91 | -65.3 | -1.47 |
| Short | 1019 | 48.8 % | -0.057 | -57.7 | 0.89 | -71.4 | -1.84 |
| 1.ª mitad | 1047 | 50.6 % | -0.029 | -30.9 | 0.94 | -51.2 | -0.97 |
| 2.ª mitad | 1047 | 48.2 % | -0.071 | -74.2 | 0.86 | -88.7 | -2.33 |

Por año (R neto medio y operaciones): 2018 +0.024 (76), 2019 -0.061 (258), 2020 -0.022 (254), 2021 -0.063 (259), 2022 +0.025 (258), 2023 -0.028 (258), 2024 -0.194 (259), 2025 -0.064 (256), 2026 -0.009 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.054 (t -2.49), colchón 50 % -0.047 (t -2.21), objetivo 1,5:1 -0.045 (t -1.76), objetivo 2:1 -0.059 (t -2.05).

### ORB 07:45–08:30

Rotura con cuerpo desde las 08:30 hasta las 14:30; a esa hora se cierra. ORB completos: 2095; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.035 R; ancho medio del ORB 0.27 %; cómo terminan: objetivo 970, stop 1007, por tiempo 115.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2092 | 49.2 % | -0.053 | -110.4 | 0.90 | -113.2 | -2.47 |
| Sin costes | 2092 | 49.2 % | -0.018 | -37.5 | 0.96 | -53.3 | -0.84 |
| Long | 1058 | 48.9 % | -0.068 | -71.7 | 0.87 | -79.8 | -2.26 |
| Short | 1034 | 49.5 % | -0.037 | -38.7 | 0.93 | -49.3 | -1.22 |
| 1.ª mitad | 1046 | 48.9 % | -0.063 | -65.5 | 0.88 | -78.9 | -2.07 |
| 2.ª mitad | 1046 | 49.4 % | -0.043 | -44.9 | 0.91 | -56.0 | -1.42 |

Por año (R neto medio y operaciones): 2018 -0.037 (75), 2019 -0.065 (257), 2020 -0.095 (253), 2021 -0.103 (259), 2022 +0.015 (258), 2023 -0.025 (258), 2024 -0.054 (259), 2025 -0.024 (257), 2026 -0.081 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.062 (t -2.87), colchón 50 % -0.045 (t -2.13), objetivo 1,5:1 -0.060 (t -2.33), objetivo 2:1 -0.061 (t -2.12).

