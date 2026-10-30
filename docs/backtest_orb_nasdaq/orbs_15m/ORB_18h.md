# ORB de 15 min de las 18:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 18:00–18:15 | 2079 | 48.8 | -0.069 | -3.45 | -0.004 | 0.064 | no |
| 18:15–18:30 | 2089 | 49.6 | -0.111 | -5.23 | -0.011 | 0.101 | no |
| 18:30–18:45 | 2094 | 49.2 | -0.107 | -5.01 | -0.003 | 0.105 | no |
| 18:45–19:00 | 2096 | 51.2 | -0.092 | -4.23 | +0.023 | 0.114 | no |

## Detalle

### ORB 18:00–18:15

Rotura con cuerpo desde las 18:15 hasta las 00:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2079.

**No pasa los criterios**. Coste medio 0.064 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 806, stop 828, por tiempo 445.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2079 | 48.8 % | -0.069 | -142.9 | 0.85 | -151.7 | -3.45 |
| Sin costes | 2079 | 49.7 % | -0.004 | -8.9 | 0.99 | -44.1 | -0.22 |
| Long | 1125 | 50.4 % | -0.051 | -56.9 | 0.89 | -61.7 | -1.89 |
| Short | 954 | 47.0 % | -0.090 | -86.0 | 0.81 | -95.4 | -3.03 |
| 1.ª mitad | 1040 | 47.2 % | -0.098 | -101.8 | 0.80 | -109.4 | -3.41 |
| 2.ª mitad | 1039 | 50.4 % | -0.040 | -41.1 | 0.91 | -50.6 | -1.44 |

Por año (R neto medio y operaciones): 2018 -0.159 (74), 2019 -0.078 (255), 2020 -0.077 (256), 2021 -0.136 (259), 2022 -0.077 (254), 2023 -0.027 (254), 2024 -0.020 (256), 2025 -0.076 (256), 2026 -0.024 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.094 (t -4.58), colchón 50 % -0.067 (t -3.54), objetivo 1,5:1 -0.065 (t -2.84), objetivo 2:1 -0.069 (t -2.77).

### ORB 18:15–18:30

Rotura con cuerpo desde las 18:30 hasta las 00:30 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2089.

**No pasa los criterios**. Coste medio 0.101 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 962, stop 975, por tiempo 152.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2089 | 49.6 % | -0.111 | -232.8 | 0.79 | -243.3 | -5.23 |
| Sin costes | 2089 | 49.7 % | -0.011 | -22.0 | 0.98 | -68.8 | -0.49 |
| Long | 1084 | 51.9 % | -0.071 | -76.9 | 0.86 | -95.4 | -2.40 |
| Short | 1005 | 47.1 % | -0.155 | -155.8 | 0.72 | -164.2 | -5.07 |
| 1.ª mitad | 1045 | 48.2 % | -0.147 | -153.9 | 0.73 | -160.6 | -4.89 |
| 2.ª mitad | 1044 | 51.0 % | -0.076 | -78.9 | 0.85 | -92.8 | -2.51 |

Por año (R neto medio y operaciones): 2018 -0.175 (74), 2019 -0.137 (255), 2020 -0.143 (255), 2021 -0.194 (259), 2022 -0.136 (257), 2023 -0.108 (257), 2024 -0.070 (259), 2025 -0.064 (257), 2026 -0.007 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.140 (t -6.49), colchón 50 % -0.096 (t -4.60), objetivo 1,5:1 -0.116 (t -4.55), objetivo 2:1 -0.106 (t -3.71).

### ORB 18:30–18:45

Rotura con cuerpo desde las 18:45 hasta las 00:45 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.105 R; ancho medio del ORB 0.11 %; cómo terminan: objetivo 986, stop 988, por tiempo 120.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 49.2 % | -0.107 | -224.9 | 0.80 | -229.5 | -5.01 |
| Sin costes | 2094 | 49.5 % | -0.003 | -6.0 | 0.99 | -68.1 | -0.13 |
| Long | 1095 | 50.0 % | -0.095 | -104.2 | 0.82 | -109.9 | -3.22 |
| Short | 999 | 48.3 % | -0.121 | -120.7 | 0.78 | -124.6 | -3.89 |
| 1.ª mitad | 1047 | 48.8 % | -0.126 | -132.1 | 0.77 | -140.9 | -4.13 |
| 2.ª mitad | 1047 | 49.7 % | -0.089 | -92.8 | 0.83 | -94.9 | -2.95 |

Por año (R neto medio y operaciones): 2018 -0.046 (74), 2019 -0.109 (256), 2020 -0.084 (257), 2021 -0.071 (259), 2022 -0.277 (257), 2023 -0.109 (258), 2024 -0.068 (259), 2025 -0.053 (258), 2026 -0.107 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.111 (t -5.14), colchón 50 % -0.070 (t -3.35), objetivo 1,5:1 -0.074 (t -2.86), objetivo 2:1 -0.066 (t -2.28).

### ORB 18:45–19:00

Rotura con cuerpo desde las 19:00 hasta las 01:00 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.114 R; ancho medio del ORB 0.10 %; cómo terminan: objetivo 1027, stop 983, por tiempo 86.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 51.2 % | -0.092 | -192.0 | 0.83 | -209.6 | -4.23 |
| Sin costes | 2096 | 51.3 % | +0.023 | +47.4 | 1.05 | -39.5 | +1.05 |
| Long | 1083 | 52.5 % | -0.067 | -72.2 | 0.87 | -95.7 | -2.21 |
| Short | 1013 | 49.8 % | -0.118 | -119.8 | 0.78 | -128.3 | -3.80 |
| 1.ª mitad | 1048 | 51.2 % | -0.094 | -98.7 | 0.82 | -111.6 | -3.06 |
| 2.ª mitad | 1048 | 51.1 % | -0.089 | -93.3 | 0.83 | -105.1 | -2.91 |

Por año (R neto medio y operaciones): 2018 -0.078 (75), 2019 -0.087 (257), 2020 +0.016 (256), 2021 -0.191 (259), 2022 -0.155 (258), 2023 -0.132 (258), 2024 -0.090 (259), 2025 -0.050 (258), 2026 -0.037 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.096 (t -4.42), colchón 50 % -0.079 (t -3.73), objetivo 1,5:1 -0.079 (t -3.01), objetivo 2:1 -0.078 (t -2.66).

