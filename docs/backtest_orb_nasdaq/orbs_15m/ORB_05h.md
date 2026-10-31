# ORB de 15 min de las 05:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 05:00–05:15 | 2096 | 50.4 | -0.065 | -3.00 | +0.009 | 0.074 | no |
| 05:15–05:30 | 2097 | 48.6 | -0.105 | -4.79 | -0.027 | 0.078 | no |
| 05:30–05:45 | 2098 | 46.8 | -0.143 | -6.56 | -0.065 | 0.078 | no |
| 05:45–06:00 | 2096 | 47.5 | -0.128 | -5.88 | -0.048 | 0.081 | no |

## Detalle

### ORB 05:00–05:15

Rotura con cuerpo desde las 05:15 hasta las 11:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.074 R; ancho medio del ORB 0.14 %; cómo terminan: objetivo 1054, stop 1036, por tiempo 6.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 50.4 % | -0.065 | -137.0 | 0.88 | -158.6 | -3.00 |
| Sin costes | 2096 | 50.5 % | +0.009 | +17.8 | 1.02 | -49.2 | +0.39 |
| Long | 1115 | 50.2 % | -0.069 | -77.1 | 0.87 | -103.6 | -2.32 |
| Short | 981 | 50.7 % | -0.061 | -59.9 | 0.88 | -76.2 | -1.91 |
| 1.ª mitad | 1048 | 52.2 % | -0.036 | -37.4 | 0.93 | -66.3 | -1.16 |
| 2.ª mitad | 1048 | 48.7 % | -0.095 | -99.6 | 0.83 | -106.2 | -3.07 |

Por año (R neto medio y operaciones): 2018 +0.066 (76), 2019 -0.013 (257), 2020 -0.083 (256), 2021 -0.060 (259), 2022 -0.045 (258), 2023 -0.148 (258), 2024 -0.033 (259), 2025 -0.095 (257), 2026 -0.088 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.089 (t -4.08), colchón 50 % -0.063 (t -2.89), objetivo 1,5:1 -0.087 (t -3.28), objetivo 2:1 -0.091 (t -3.00).

### ORB 05:15–05:30

Rotura con cuerpo desde las 05:30 hasta las 11:30; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.078 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 1019, stop 1075, por tiempo 3.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 48.6 % | -0.105 | -219.4 | 0.81 | -249.5 | -4.79 |
| Sin costes | 2097 | 48.6 % | -0.027 | -56.2 | 0.95 | -102.2 | -1.23 |
| Long | 1093 | 48.9 % | -0.102 | -112.0 | 0.81 | -136.3 | -3.39 |
| Short | 1004 | 48.4 % | -0.107 | -107.4 | 0.81 | -121.8 | -3.39 |
| 1.ª mitad | 1049 | 49.6 % | -0.091 | -95.4 | 0.83 | -118.3 | -2.95 |
| 2.ª mitad | 1048 | 47.7 % | -0.118 | -123.9 | 0.79 | -142.2 | -3.83 |

Por año (R neto medio y operaciones): 2018 +0.164 (76), 2019 -0.149 (258), 2020 -0.139 (256), 2021 -0.073 (259), 2022 -0.064 (258), 2023 -0.145 (258), 2024 -0.104 (259), 2025 -0.162 (257), 2026 -0.075 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.144 (t -6.59), colchón 50 % -0.080 (t -3.68), objetivo 1,5:1 -0.094 (t -3.54), objetivo 2:1 -0.074 (t -2.40).

### ORB 05:30–05:45

Rotura con cuerpo desde las 05:45 hasta las 11:45; a esa hora se cierra. ORB completos: 2098; con rotura: 2098.

**No pasa los criterios**. Coste medio 0.078 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 976, stop 1114, por tiempo 8.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2098 | 46.8 % | -0.143 | -300.3 | 0.75 | -308.5 | -6.56 |
| Sin costes | 2098 | 46.8 % | -0.065 | -137.2 | 0.88 | -147.2 | -3.01 |
| Long | 1101 | 46.3 % | -0.153 | -168.7 | 0.74 | -169.8 | -5.09 |
| Short | 997 | 47.2 % | -0.132 | -131.6 | 0.77 | -145.0 | -4.17 |
| 1.ª mitad | 1049 | 46.3 % | -0.156 | -163.2 | 0.73 | -172.0 | -5.05 |
| 2.ª mitad | 1049 | 47.2 % | -0.131 | -137.1 | 0.77 | -140.8 | -4.23 |

Por año (R neto medio y operaciones): 2018 -0.126 (76), 2019 -0.223 (258), 2020 -0.110 (257), 2021 -0.109 (259), 2022 -0.211 (258), 2023 -0.204 (258), 2024 -0.084 (259), 2025 -0.073 (257), 2026 -0.135 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.127 (t -5.81), colchón 50 % -0.118 (t -5.41), objetivo 1,5:1 -0.137 (t -5.20), objetivo 2:1 -0.145 (t -4.79).

### ORB 05:45–06:00

Rotura con cuerpo desde las 06:00 hasta las 12:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.081 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 995, stop 1094, por tiempo 7.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 47.5 % | -0.128 | -268.9 | 0.77 | -272.3 | -5.88 |
| Sin costes | 2096 | 47.6 % | -0.048 | -99.6 | 0.91 | -105.6 | -2.18 |
| Long | 1088 | 47.4 % | -0.134 | -145.8 | 0.76 | -149.7 | -4.42 |
| Short | 1008 | 47.6 % | -0.122 | -123.1 | 0.78 | -127.1 | -3.89 |
| 1.ª mitad | 1048 | 47.3 % | -0.133 | -139.9 | 0.76 | -146.7 | -4.33 |
| 2.ª mitad | 1048 | 47.7 % | -0.123 | -129.0 | 0.78 | -131.9 | -3.99 |

Por año (R neto medio y operaciones): 2018 -0.097 (76), 2019 -0.215 (258), 2020 -0.038 (255), 2021 -0.133 (259), 2022 -0.165 (258), 2023 -0.149 (258), 2024 -0.043 (259), 2025 -0.136 (257), 2026 -0.161 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.135 (t -6.18), colchón 50 % -0.122 (t -5.62), objetivo 1,5:1 -0.122 (t -4.62), objetivo 2:1 -0.097 (t -3.17).

