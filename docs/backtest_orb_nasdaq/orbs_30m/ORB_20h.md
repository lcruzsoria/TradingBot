# ORB de 30 min de las 20:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 20:00–20:30 | 2081 | 50.0 | -0.032 | -1.70 | +0.021 | 0.053 | no |
| 20:15–20:45 | 2084 | 48.8 | -0.064 | -3.29 | -0.006 | 0.058 | no |
| 20:30–21:00 | 2085 | 50.0 | -0.036 | -1.82 | +0.027 | 0.063 | no |
| 20:45–21:15 | 2085 | 49.8 | -0.047 | -2.29 | +0.018 | 0.065 | no |

## Detalle

### ORB 20:00–20:30

Rotura con cuerpo desde las 20:30 hasta las 02:30 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2081.

**No pasa los criterios**. Coste medio 0.053 R; ancho medio del ORB 0.21 %; cómo terminan: objetivo 735, stop 684, por tiempo 662.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2081 | 50.0 % | -0.032 | -66.5 | 0.92 | -90.2 | -1.70 |
| Sin costes | 2081 | 50.8 % | +0.021 | +43.3 | 1.05 | -25.5 | +1.11 |
| Long | 1094 | 52.6 % | -0.001 | -0.7 | 1.00 | -26.8 | -0.02 |
| Short | 987 | 47.1 % | -0.067 | -65.8 | 0.85 | -80.3 | -2.40 |
| 1.ª mitad | 1041 | 49.9 % | -0.022 | -22.8 | 0.95 | -43.6 | -0.83 |
| 2.ª mitad | 1040 | 50.1 % | -0.042 | -43.6 | 0.90 | -63.3 | -1.56 |

Por año (R neto medio y operaciones): 2018 +0.021 (75), 2019 -0.067 (255), 2020 +0.003 (258), 2021 -0.033 (254), 2022 -0.004 (256), 2023 -0.123 (256), 2024 -0.058 (259), 2025 +0.025 (255), 2026 -0.009 (213).

Sensibilidad (R neto medio y t): colchón 0 % -0.033 (t -1.65), colchón 50 % -0.043 (t -2.48), objetivo 1,5:1 -0.032 (t -1.53), objetivo 2:1 -0.019 (t -0.85).

### ORB 20:15–20:45

Rotura con cuerpo desde las 20:45 hasta las 02:45 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2084.

**No pasa los criterios**. Coste medio 0.058 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 777, stop 782, por tiempo 525.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2084 | 48.8 % | -0.064 | -133.8 | 0.86 | -176.8 | -3.29 |
| Sin costes | 2084 | 49.6 % | -0.006 | -12.0 | 0.99 | -66.8 | -0.29 |
| Long | 1128 | 51.3 % | -0.033 | -36.8 | 0.92 | -59.3 | -1.24 |
| Short | 956 | 45.9 % | -0.102 | -97.0 | 0.79 | -122.9 | -3.50 |
| 1.ª mitad | 1042 | 47.0 % | -0.094 | -98.1 | 0.80 | -101.7 | -3.43 |
| 2.ª mitad | 1042 | 50.7 % | -0.034 | -35.7 | 0.92 | -81.0 | -1.24 |

Por año (R neto medio y operaciones): 2018 -0.101 (75), 2019 -0.163 (256), 2020 -0.049 (257), 2021 -0.075 (256), 2022 -0.107 (254), 2023 -0.102 (258), 2024 -0.100 (258), 2025 -0.011 (255), 2026 +0.137 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.080 (t -3.95), colchón 50 % -0.052 (t -2.85), objetivo 1,5:1 -0.051 (t -2.27), objetivo 2:1 -0.045 (t -1.88).

### ORB 20:30–21:00

Rotura con cuerpo desde las 21:00 hasta las 03:00 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2085.

**No pasa los criterios**. Coste medio 0.063 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 841, stop 781, por tiempo 463.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2085 | 50.0 % | -0.036 | -75.4 | 0.92 | -110.6 | -1.82 |
| Sin costes | 2085 | 50.9 % | +0.027 | +55.8 | 1.06 | -36.7 | +1.35 |
| Long | 1129 | 50.8 % | -0.029 | -33.3 | 0.93 | -64.0 | -1.09 |
| Short | 956 | 49.1 % | -0.044 | -42.2 | 0.90 | -58.6 | -1.50 |
| 1.ª mitad | 1043 | 50.4 % | -0.027 | -27.9 | 0.94 | -36.5 | -0.96 |
| 2.ª mitad | 1042 | 49.5 % | -0.046 | -47.5 | 0.90 | -83.5 | -1.62 |

Por año (R neto medio y operaciones): 2018 -0.015 (76), 2019 -0.083 (255), 2020 +0.029 (256), 2021 -0.005 (258), 2022 -0.057 (255), 2023 -0.103 (256), 2024 -0.123 (258), 2025 -0.044 (256), 2026 +0.115 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.062 (t -3.04), colchón 50 % -0.025 (t -1.33), objetivo 1,5:1 -0.024 (t -1.03), objetivo 2:1 -0.009 (t -0.36).

### ORB 20:45–21:15

Rotura con cuerpo desde las 21:15 hasta las 03:15 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2085.

**No pasa los criterios**. Coste medio 0.065 R; ancho medio del ORB 0.18 %; cómo terminan: objetivo 897, stop 857, por tiempo 331.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2085 | 49.8 % | -0.047 | -97.8 | 0.90 | -113.0 | -2.29 |
| Sin costes | 2085 | 50.4 % | +0.018 | +36.9 | 1.04 | -37.8 | +0.87 |
| Long | 1126 | 51.7 % | -0.017 | -18.6 | 0.96 | -48.5 | -0.60 |
| Short | 959 | 47.7 % | -0.083 | -79.1 | 0.83 | -83.7 | -2.71 |
| 1.ª mitad | 1043 | 51.1 % | -0.026 | -27.4 | 0.94 | -41.2 | -0.92 |
| 2.ª mitad | 1042 | 48.6 % | -0.068 | -70.3 | 0.86 | -88.3 | -2.31 |

Por año (R neto medio y operaciones): 2018 -0.112 (75), 2019 -0.067 (254), 2020 -0.045 (257), 2021 +0.002 (257), 2022 +0.018 (258), 2023 -0.112 (257), 2024 -0.066 (256), 2025 -0.130 (256), 2026 +0.062 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.065 (t -3.10), colchón 50 % -0.029 (t -1.49), objetivo 1,5:1 -0.033 (t -1.39), objetivo 2:1 -0.026 (t -1.01).

