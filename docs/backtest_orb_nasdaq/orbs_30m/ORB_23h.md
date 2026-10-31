# ORB de 30 min de las 23:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 23:00–23:30 | 2097 | 49.4 | -0.097 | -4.49 | -0.006 | 0.090 | no |
| 23:15–23:45 | 2098 | 49.4 | -0.103 | -4.75 | -0.008 | 0.095 | no |
| 23:30–00:00 | 2098 | 50.0 | -0.097 | -4.46 | +0.002 | 0.098 | no |
| 23:45–00:15 | 2095 | 50.7 | -0.083 | -3.80 | +0.016 | 0.098 | no |

## Detalle

### ORB 23:00–23:30

Rotura con cuerpo desde las 23:30 hasta las 05:30 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.090 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 1002, stop 1014, por tiempo 81.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 49.4 % | -0.097 | -202.7 | 0.82 | -231.3 | -4.49 |
| Sin costes | 2097 | 49.5 % | -0.006 | -13.2 | 0.99 | -61.3 | -0.29 |
| Long | 1088 | 49.6 % | -0.087 | -94.4 | 0.84 | -110.0 | -2.91 |
| Short | 1009 | 49.1 % | -0.107 | -108.4 | 0.80 | -126.1 | -3.45 |
| 1.ª mitad | 1049 | 47.9 % | -0.123 | -129.5 | 0.77 | -132.2 | -4.08 |
| 2.ª mitad | 1048 | 50.9 % | -0.070 | -73.2 | 0.87 | -109.0 | -2.28 |

Por año (R neto medio y operaciones): 2018 -0.164 (76), 2019 -0.155 (258), 2020 -0.102 (256), 2021 -0.059 (259), 2022 -0.166 (258), 2023 -0.135 (258), 2024 -0.162 (259), 2025 -0.056 (257), 2026 +0.116 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.105 (t -4.85), colchón 50 % -0.074 (t -3.52), objetivo 1,5:1 -0.083 (t -3.20), objetivo 2:1 -0.067 (t -2.29).

### ORB 23:15–23:45

Rotura con cuerpo desde las 23:45 hasta las 05:45 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2098.

**No pasa los criterios**. Coste medio 0.095 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 1006, stop 1027, por tiempo 65.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2098 | 49.4 % | -0.103 | -215.4 | 0.81 | -229.5 | -4.75 |
| Sin costes | 2098 | 49.5 % | -0.008 | -16.9 | 0.98 | -60.2 | -0.37 |
| Long | 1093 | 50.8 % | -0.079 | -86.2 | 0.85 | -99.7 | -2.64 |
| Short | 1005 | 48.0 % | -0.128 | -129.1 | 0.77 | -141.3 | -4.11 |
| 1.ª mitad | 1049 | 48.5 % | -0.123 | -129.0 | 0.78 | -131.2 | -4.02 |
| 2.ª mitad | 1049 | 50.3 % | -0.082 | -86.3 | 0.85 | -99.2 | -2.69 |

Por año (R neto medio y operaciones): 2018 -0.149 (76), 2019 -0.177 (258), 2020 -0.049 (257), 2021 -0.141 (259), 2022 -0.134 (258), 2023 -0.164 (258), 2024 -0.066 (259), 2025 -0.080 (257), 2026 +0.026 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.111 (t -5.11), colchón 50 % -0.100 (t -4.68), objetivo 1,5:1 -0.101 (t -3.87), objetivo 2:1 -0.072 (t -2.44).

### ORB 23:30–00:00

Rotura con cuerpo desde las 00:00 hasta las 06:00 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2098.

**No pasa los criterios**. Coste medio 0.098 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 1017, stop 1020, por tiempo 61.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2098 | 50.0 % | -0.097 | -202.6 | 0.82 | -217.1 | -4.46 |
| Sin costes | 2098 | 50.1 % | +0.002 | +3.8 | 1.00 | -64.4 | +0.08 |
| Long | 1078 | 51.4 % | -0.072 | -77.5 | 0.86 | -89.0 | -2.38 |
| Short | 1020 | 48.6 % | -0.123 | -125.1 | 0.78 | -135.5 | -3.94 |
| 1.ª mitad | 1049 | 50.1 % | -0.099 | -104.1 | 0.82 | -108.8 | -3.23 |
| 2.ª mitad | 1049 | 50.0 % | -0.094 | -98.5 | 0.83 | -109.3 | -3.07 |

Por año (R neto medio y operaciones): 2018 -0.013 (76), 2019 -0.159 (258), 2020 -0.011 (257), 2021 -0.124 (259), 2022 -0.167 (258), 2023 -0.191 (258), 2024 -0.036 (259), 2025 -0.122 (257), 2026 +0.035 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.125 (t -5.77), colchón 50 % -0.073 (t -3.42), objetivo 1,5:1 -0.087 (t -3.32), objetivo 2:1 -0.074 (t -2.48).

### ORB 23:45–00:15

Rotura con cuerpo desde las 00:15 hasta las 06:15 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.098 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 1037, stop 1003, por tiempo 55.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 50.7 % | -0.083 | -172.9 | 0.85 | -197.8 | -3.80 |
| Sin costes | 2095 | 50.7 % | +0.016 | +32.5 | 1.03 | -60.8 | +0.72 |
| Long | 1087 | 51.9 % | -0.062 | -67.8 | 0.88 | -87.2 | -2.07 |
| Short | 1008 | 49.5 % | -0.104 | -105.1 | 0.81 | -121.6 | -3.34 |
| 1.ª mitad | 1048 | 50.1 % | -0.094 | -98.8 | 0.82 | -101.5 | -3.08 |
| 2.ª mitad | 1047 | 51.4 % | -0.071 | -74.1 | 0.87 | -102.0 | -2.30 |

Por año (R neto medio y operaciones): 2018 -0.108 (76), 2019 -0.089 (257), 2020 +0.013 (256), 2021 -0.199 (259), 2022 -0.121 (258), 2023 -0.208 (258), 2024 -0.028 (259), 2025 -0.077 (256), 2026 +0.083 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.078 (t -3.57), colchón 50 % -0.073 (t -3.43), objetivo 1,5:1 -0.074 (t -2.82), objetivo 2:1 -0.064 (t -2.14).

