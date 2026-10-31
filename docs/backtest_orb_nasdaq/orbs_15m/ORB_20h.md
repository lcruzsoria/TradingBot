# ORB de 15 min de las 20:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 20:00–20:15 | 2092 | 51.2 | -0.031 | -1.55 | +0.036 | 0.068 | no |
| 20:15–20:30 | 2095 | 50.0 | -0.071 | -3.41 | +0.008 | 0.080 | no |
| 20:30–20:45 | 2096 | 50.8 | -0.054 | -2.60 | +0.029 | 0.083 | no |
| 20:45–21:00 | 2094 | 49.3 | -0.099 | -4.68 | -0.010 | 0.090 | no |

## Detalle

### ORB 20:00–20:15

Rotura con cuerpo desde las 20:15 hasta las 02:15 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.068 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 906, stop 825, por tiempo 361.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2092 | 51.2 % | -0.031 | -65.8 | 0.93 | -89.6 | -1.55 |
| Sin costes | 2092 | 51.5 % | +0.036 | +76.3 | 1.09 | -39.5 | +1.80 |
| Long | 1091 | 52.2 % | -0.011 | -11.5 | 0.98 | -48.2 | -0.38 |
| Short | 1001 | 50.2 % | -0.054 | -54.3 | 0.89 | -63.5 | -1.84 |
| 1.ª mitad | 1046 | 53.2 % | +0.003 | +3.0 | 1.01 | -32.7 | +0.10 |
| 2.ª mitad | 1046 | 49.3 % | -0.066 | -68.8 | 0.86 | -80.4 | -2.28 |

Por año (R neto medio y operaciones): 2018 +0.025 (76), 2019 -0.004 (255), 2020 -0.020 (258), 2021 -0.000 (257), 2022 +0.003 (258), 2023 -0.192 (257), 2024 -0.053 (259), 2025 +0.040 (257), 2026 -0.045 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.036 (t -1.72), colchón 50 % -0.046 (t -2.36), objetivo 1,5:1 -0.037 (t -1.57), objetivo 2:1 -0.025 (t -0.97).

### ORB 20:15–20:30

Rotura con cuerpo desde las 20:30 hasta las 02:30 (día siguiente); a esa hora se cierra. ORB completos: 2099; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.080 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 942, stop 926, por tiempo 227.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 50.0 % | -0.071 | -149.4 | 0.86 | -156.6 | -3.41 |
| Sin costes | 2095 | 50.4 % | +0.008 | +17.3 | 1.02 | -25.1 | +0.40 |
| Long | 1072 | 52.4 % | -0.037 | -40.2 | 0.92 | -48.5 | -1.30 |
| Short | 1023 | 47.5 % | -0.107 | -109.3 | 0.80 | -115.6 | -3.52 |
| 1.ª mitad | 1048 | 49.4 % | -0.083 | -86.9 | 0.84 | -87.5 | -2.80 |
| 2.ª mitad | 1047 | 50.6 % | -0.060 | -62.6 | 0.88 | -83.3 | -2.02 |

Por año (R neto medio y operaciones): 2018 -0.206 (75), 2019 -0.162 (257), 2020 +0.012 (258), 2021 -0.066 (257), 2022 -0.025 (258), 2023 -0.141 (258), 2024 -0.084 (259), 2025 -0.037 (257), 2026 -0.021 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.079 (t -3.69), colchón 50 % -0.051 (t -2.55), objetivo 1,5:1 -0.060 (t -2.46), objetivo 2:1 -0.066 (t -2.44).

### ORB 20:30–20:45

Rotura con cuerpo desde las 20:45 hasta las 02:45 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.083 R; ancho medio del ORB 0.13 %; cómo terminan: objetivo 960, stop 890, por tiempo 246.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 50.8 % | -0.054 | -113.4 | 0.89 | -166.9 | -2.60 |
| Sin costes | 2096 | 51.1 % | +0.029 | +59.8 | 1.06 | -46.7 | +1.38 |
| Long | 1113 | 52.3 % | -0.025 | -28.0 | 0.95 | -67.4 | -0.88 |
| Short | 983 | 49.1 % | -0.087 | -85.4 | 0.83 | -109.7 | -2.86 |
| 1.ª mitad | 1048 | 49.3 % | -0.076 | -80.0 | 0.85 | -82.6 | -2.61 |
| 2.ª mitad | 1048 | 52.3 % | -0.032 | -33.4 | 0.93 | -87.8 | -1.08 |

Por año (R neto medio y operaciones): 2018 -0.190 (76), 2019 -0.117 (256), 2020 +0.009 (257), 2021 -0.041 (259), 2022 -0.154 (258), 2023 -0.108 (258), 2024 -0.082 (259), 2025 -0.037 (257), 2026 +0.175 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.077 (t -3.64), colchón 50 % -0.058 (t -2.88), objetivo 1,5:1 -0.055 (t -2.23), objetivo 2:1 -0.052 (t -1.92).

### ORB 20:45–21:00

Rotura con cuerpo desde las 21:00 hasta las 03:00 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.090 R; ancho medio del ORB 0.12 %; cómo terminan: objetivo 961, stop 974, por tiempo 159.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 49.3 % | -0.099 | -208.3 | 0.81 | -210.9 | -4.68 |
| Sin costes | 2094 | 49.4 % | -0.010 | -19.9 | 0.98 | -50.5 | -0.45 |
| Long | 1113 | 50.9 % | -0.075 | -83.0 | 0.85 | -87.1 | -2.57 |
| Short | 981 | 47.4 % | -0.128 | -125.3 | 0.77 | -127.9 | -4.09 |
| 1.ª mitad | 1047 | 50.2 % | -0.079 | -83.1 | 0.85 | -85.9 | -2.64 |
| 2.ª mitad | 1047 | 48.3 % | -0.120 | -125.1 | 0.78 | -128.6 | -3.97 |

Por año (R neto medio y operaciones): 2018 -0.095 (76), 2019 -0.149 (255), 2020 -0.053 (258), 2021 -0.065 (258), 2022 -0.065 (257), 2023 -0.106 (258), 2024 -0.167 (259), 2025 -0.161 (257), 2026 -0.018 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.106 (t -4.90), colchón 50 % -0.082 (t -3.94), objetivo 1,5:1 -0.080 (t -3.18), objetivo 2:1 -0.059 (t -2.06).

