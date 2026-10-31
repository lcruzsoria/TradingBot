# ORB de 15 min de las 01:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 01:00–01:15 | 2095 | 50.9 | -0.078 | -3.58 | +0.020 | 0.098 | no |
| 01:15–01:30 | 2096 | 52.0 | -0.066 | -3.02 | +0.041 | 0.107 | no |
| 01:30–01:45 | 2096 | 51.8 | -0.063 | -2.93 | +0.037 | 0.100 | no |
| 01:45–02:00 | 2095 | 49.2 | -0.108 | -4.96 | -0.012 | 0.096 | no |

## Detalle

### ORB 01:00–01:15

Rotura con cuerpo desde las 01:15 hasta las 07:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.098 R; ancho medio del ORB 0.11 %; cómo terminan: objetivo 1050, stop 1009, por tiempo 36.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 50.9 % | -0.078 | -163.0 | 0.85 | -188.2 | -3.58 |
| Sin costes | 2095 | 50.9 % | +0.020 | +41.5 | 1.04 | -49.5 | +0.91 |
| Long | 1079 | 52.6 % | -0.039 | -42.0 | 0.92 | -71.7 | -1.29 |
| Short | 1016 | 49.0 % | -0.119 | -120.9 | 0.79 | -127.5 | -3.81 |
| 1.ª mitad | 1048 | 48.6 % | -0.124 | -130.3 | 0.78 | -132.6 | -4.04 |
| 2.ª mitad | 1047 | 53.2 % | -0.031 | -32.7 | 0.94 | -57.6 | -1.02 |

Por año (R neto medio y operaciones): 2018 -0.043 (76), 2019 -0.182 (257), 2020 -0.075 (256), 2021 -0.102 (259), 2022 -0.149 (258), 2023 -0.060 (258), 2024 -0.053 (259), 2025 -0.044 (256), 2026 +0.052 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.085 (t -3.90), colchón 50 % -0.064 (t -2.98), objetivo 1,5:1 -0.053 (t -1.98), objetivo 2:1 -0.044 (t -1.45).

### ORB 01:15–01:30

Rotura con cuerpo desde las 01:30 hasta las 07:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.107 R; ancho medio del ORB 0.10 %; cómo terminan: objetivo 1079, stop 990, por tiempo 27.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 52.0 % | -0.066 | -138.5 | 0.88 | -184.6 | -3.02 |
| Sin costes | 2096 | 52.1 % | +0.041 | +86.4 | 1.09 | -57.2 | +1.90 |
| Long | 1085 | 53.5 % | -0.036 | -39.0 | 0.93 | -72.1 | -1.18 |
| Short | 1011 | 50.3 % | -0.098 | -99.5 | 0.82 | -120.5 | -3.12 |
| 1.ª mitad | 1048 | 49.5 % | -0.118 | -123.2 | 0.79 | -145.4 | -3.79 |
| 2.ª mitad | 1048 | 54.4 % | -0.015 | -15.2 | 0.97 | -53.7 | -0.47 |

Por año (R neto medio y operaciones): 2018 +0.132 (76), 2019 -0.200 (258), 2020 -0.069 (255), 2021 -0.211 (259), 2022 -0.028 (258), 2023 -0.037 (258), 2024 -0.075 (259), 2025 -0.058 (257), 2026 +0.123 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.093 (t -4.22), colchón 50 % -0.070 (t -3.22), objetivo 1,5:1 -0.067 (t -2.52), objetivo 2:1 -0.079 (t -2.59).

### ORB 01:30–01:45

Rotura con cuerpo desde las 01:45 hasta las 07:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.100 R; ancho medio del ORB 0.11 %; cómo terminan: objetivo 1067, stop 988, por tiempo 41.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 51.8 % | -0.063 | -132.9 | 0.88 | -173.3 | -2.93 |
| Sin costes | 2096 | 51.9 % | +0.037 | +76.7 | 1.08 | -43.3 | +1.69 |
| Long | 1108 | 53.2 % | -0.034 | -37.7 | 0.93 | -70.4 | -1.14 |
| Short | 988 | 50.1 % | -0.096 | -95.2 | 0.82 | -110.0 | -3.06 |
| 1.ª mitad | 1048 | 50.5 % | -0.091 | -95.3 | 0.83 | -114.7 | -2.97 |
| 2.ª mitad | 1048 | 53.1 % | -0.036 | -37.6 | 0.93 | -66.3 | -1.17 |

Por año (R neto medio y operaciones): 2018 +0.101 (76), 2019 -0.098 (258), 2020 -0.063 (255), 2021 -0.143 (259), 2022 -0.109 (258), 2023 -0.039 (258), 2024 -0.068 (259), 2025 -0.087 (257), 2026 +0.074 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.060 (t -2.76), colchón 50 % -0.065 (t -3.02), objetivo 1,5:1 -0.069 (t -2.62), objetivo 2:1 -0.079 (t -2.65).

### ORB 01:45–02:00

Rotura con cuerpo desde las 02:00 hasta las 08:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.096 R; ancho medio del ORB 0.10 %; cómo terminan: objetivo 1020, stop 1044, por tiempo 31.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 49.2 % | -0.108 | -225.8 | 0.80 | -233.6 | -4.96 |
| Sin costes | 2095 | 49.3 % | -0.012 | -24.3 | 0.98 | -63.0 | -0.53 |
| Long | 1047 | 51.3 % | -0.062 | -64.8 | 0.88 | -74.7 | -2.02 |
| Short | 1048 | 47.1 % | -0.154 | -161.0 | 0.73 | -168.5 | -4.99 |
| 1.ª mitad | 1048 | 49.4 % | -0.107 | -112.1 | 0.80 | -113.8 | -3.49 |
| 2.ª mitad | 1047 | 49.0 % | -0.109 | -113.7 | 0.80 | -128.1 | -3.52 |

Por año (R neto medio y operaciones): 2018 -0.172 (76), 2019 -0.128 (258), 2020 -0.043 (254), 2021 -0.075 (259), 2022 -0.162 (258), 2023 -0.090 (258), 2024 -0.174 (259), 2025 -0.082 (257), 2026 -0.083 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.119 (t -5.45), colchón 50 % -0.091 (t -4.20), objetivo 1,5:1 -0.094 (t -3.57), objetivo 2:1 -0.084 (t -2.81).

