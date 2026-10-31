# ORB de 15 min de las 12:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 12:00–12:15 | 2090 | 48.9 | -0.066 | -3.14 | -0.028 | 0.038 | no |
| 12:15–12:30 | 2093 | 50.4 | -0.036 | -1.71 | +0.005 | 0.041 | no |
| 12:30–12:45 | 2089 | 49.0 | -0.058 | -2.77 | -0.016 | 0.042 | no |
| 12:45–13:00 | 2082 | 48.7 | -0.053 | -2.56 | -0.011 | 0.042 | no |

## Detalle

### ORB 12:00–12:15

Rotura con cuerpo desde las 12:15 hasta las 18:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.038 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 905, stop 975, por tiempo 210.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2090 | 48.9 % | -0.066 | -137.8 | 0.87 | -145.8 | -3.14 |
| Sin costes | 2090 | 48.9 % | -0.028 | -58.3 | 0.94 | -79.8 | -1.33 |
| Long | 1110 | 49.1 % | -0.066 | -73.4 | 0.87 | -73.6 | -2.31 |
| Short | 980 | 48.6 % | -0.066 | -64.4 | 0.87 | -81.9 | -2.14 |
| 1.ª mitad | 1045 | 48.3 % | -0.075 | -78.8 | 0.85 | -85.1 | -2.53 |
| 2.ª mitad | 1045 | 49.4 % | -0.057 | -59.1 | 0.89 | -65.2 | -1.92 |

Por año (R neto medio y operaciones): 2018 -0.007 (76), 2019 -0.097 (257), 2020 +0.061 (259), 2021 -0.127 (258), 2022 -0.162 (258), 2023 -0.048 (256), 2024 -0.004 (257), 2025 -0.105 (256), 2026 -0.063 (213).

Sensibilidad (R neto medio y t): colchón 0 % -0.058 (t -2.70), colchón 50 % -0.062 (t -3.07), objetivo 1,5:1 -0.055 (t -2.22), objetivo 2:1 -0.051 (t -1.87).

### ORB 12:15–12:30

Rotura con cuerpo desde las 12:30 hasta las 18:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.041 R; ancho medio del ORB 0.24 %; cómo terminan: objetivo 938, stop 935, por tiempo 220.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2093 | 50.4 % | -0.036 | -74.9 | 0.93 | -83.4 | -1.71 |
| Sin costes | 2093 | 50.8 % | +0.005 | +11.0 | 1.01 | -24.8 | +0.25 |
| Long | 1143 | 51.2 % | -0.028 | -32.3 | 0.94 | -35.4 | -1.00 |
| Short | 950 | 49.5 % | -0.045 | -42.6 | 0.91 | -54.4 | -1.44 |
| 1.ª mitad | 1047 | 50.7 % | -0.039 | -40.3 | 0.92 | -52.6 | -1.29 |
| 2.ª mitad | 1046 | 50.1 % | -0.033 | -34.5 | 0.93 | -53.1 | -1.12 |

Por año (R neto medio y operaciones): 2018 -0.061 (76), 2019 -0.037 (258), 2020 -0.057 (259), 2021 -0.047 (258), 2022 -0.030 (258), 2023 -0.010 (257), 2024 -0.019 (259), 2025 -0.014 (256), 2026 -0.070 (212).

Sensibilidad (R neto medio y t): colchón 0 % -0.035 (t -1.64), colchón 50 % -0.035 (t -1.71), objetivo 1,5:1 -0.031 (t -1.27), objetivo 2:1 -0.019 (t -0.68).

### ORB 12:30–12:45

Rotura con cuerpo desde las 12:45 hasta las 18:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2089.

**No pasa los criterios**. Coste medio 0.042 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 920, stop 951, por tiempo 218.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2089 | 49.0 % | -0.058 | -121.5 | 0.88 | -132.0 | -2.77 |
| Sin costes | 2089 | 49.3 % | -0.016 | -33.2 | 0.97 | -48.9 | -0.76 |
| Long | 1121 | 50.8 % | -0.033 | -36.9 | 0.93 | -43.3 | -1.16 |
| Short | 968 | 46.9 % | -0.087 | -84.5 | 0.83 | -100.3 | -2.82 |
| 1.ª mitad | 1045 | 48.2 % | -0.076 | -79.7 | 0.85 | -90.1 | -2.55 |
| 2.ª mitad | 1044 | 49.7 % | -0.040 | -41.8 | 0.92 | -55.3 | -1.36 |

Por año (R neto medio y operaciones): 2018 -0.061 (76), 2019 -0.163 (257), 2020 -0.059 (259), 2021 -0.074 (257), 2022 -0.007 (258), 2023 -0.016 (256), 2024 -0.025 (258), 2025 -0.062 (256), 2026 -0.057 (212).

Sensibilidad (R neto medio y t): colchón 0 % -0.065 (t -3.03), colchón 50 % -0.041 (t -2.02), objetivo 1,5:1 -0.047 (t -1.92), objetivo 2:1 -0.034 (t -1.26).

### ORB 12:45–13:00

Rotura con cuerpo desde las 13:00 hasta las 19:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2082.

**No pasa los criterios**. Coste medio 0.042 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 913, stop 938, por tiempo 231.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2082 | 48.7 % | -0.053 | -111.1 | 0.89 | -114.0 | -2.56 |
| Sin costes | 2082 | 48.9 % | -0.011 | -22.8 | 0.98 | -47.4 | -0.52 |
| Long | 1114 | 50.9 % | -0.023 | -26.1 | 0.95 | -31.7 | -0.82 |
| Short | 968 | 46.2 % | -0.088 | -85.0 | 0.83 | -88.8 | -2.86 |
| 1.ª mitad | 1041 | 48.8 % | -0.072 | -74.6 | 0.86 | -89.0 | -2.40 |
| 2.ª mitad | 1041 | 48.6 % | -0.035 | -36.5 | 0.93 | -48.4 | -1.20 |

Por año (R neto medio y operaciones): 2018 -0.238 (76), 2019 -0.103 (257), 2020 -0.027 (257), 2021 -0.107 (257), 2022 +0.016 (258), 2023 +0.011 (254), 2024 -0.067 (258), 2025 -0.046 (253), 2026 -0.048 (212).

Sensibilidad (R neto medio y t): colchón 0 % -0.050 (t -2.35), colchón 50 % -0.029 (t -1.44), objetivo 1,5:1 -0.037 (t -1.51), objetivo 2:1 -0.035 (t -1.27).

