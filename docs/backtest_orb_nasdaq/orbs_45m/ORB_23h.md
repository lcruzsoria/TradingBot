# ORB de 45 min de las 23:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 23:00–23:45 | 2097 | 49.5 | -0.075 | -3.51 | +0.001 | 0.076 | no |
| 23:15–00:00 | 2097 | 50.2 | -0.074 | -3.44 | +0.006 | 0.080 | no |
| 23:30–00:15 | 2095 | 51.3 | -0.053 | -2.48 | +0.026 | 0.079 | no |
| 23:45–00:30 | 2093 | 51.3 | -0.052 | -2.44 | +0.029 | 0.081 | no |

## Detalle

### ORB 23:00–23:45

Rotura con cuerpo desde las 23:45 hasta las 05:45 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.076 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 976, stop 976, por tiempo 145.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 49.5 % | -0.075 | -156.2 | 0.86 | -183.1 | -3.51 |
| Sin costes | 2097 | 49.8 % | +0.001 | +3.0 | 1.00 | -46.8 | +0.07 |
| Long | 1085 | 51.0 % | -0.047 | -51.1 | 0.91 | -71.4 | -1.60 |
| Short | 1012 | 48.0 % | -0.104 | -105.2 | 0.81 | -120.1 | -3.39 |
| 1.ª mitad | 1049 | 47.7 % | -0.110 | -115.5 | 0.79 | -116.3 | -3.68 |
| 2.ª mitad | 1048 | 51.4 % | -0.039 | -40.8 | 0.92 | -67.9 | -1.29 |

Por año (R neto medio y operaciones): 2018 -0.265 (76), 2019 -0.119 (258), 2020 -0.071 (256), 2021 -0.035 (259), 2022 -0.190 (258), 2023 -0.080 (258), 2024 -0.038 (259), 2025 -0.080 (257), 2026 +0.101 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.082 (t -3.81), colchón 50 % -0.060 (t -2.90), objetivo 1,5:1 -0.060 (t -2.36), objetivo 2:1 -0.054 (t -1.91).

### ORB 23:15–00:00

Rotura con cuerpo desde las 00:00 hasta las 06:00 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.080 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 995, stop 989, por tiempo 113.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 50.2 % | -0.074 | -154.5 | 0.86 | -181.1 | -3.44 |
| Sin costes | 2097 | 50.4 % | +0.006 | +13.0 | 1.01 | -50.2 | +0.29 |
| Long | 1077 | 52.7 % | -0.034 | -36.4 | 0.93 | -60.5 | -1.14 |
| Short | 1020 | 47.5 % | -0.116 | -118.1 | 0.79 | -131.9 | -3.76 |
| 1.ª mitad | 1049 | 49.4 % | -0.090 | -94.1 | 0.83 | -102.6 | -2.96 |
| 2.ª mitad | 1048 | 51.0 % | -0.058 | -60.4 | 0.89 | -83.4 | -1.90 |

Por año (R neto medio y operaciones): 2018 -0.057 (75), 2019 -0.146 (258), 2020 -0.010 (257), 2021 -0.110 (259), 2022 -0.104 (258), 2023 -0.136 (258), 2024 -0.043 (259), 2025 -0.102 (257), 2026 +0.083 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.086 (t -4.00), colchón 50 % -0.053 (t -2.55), objetivo 1,5:1 -0.059 (t -2.28), objetivo 2:1 -0.039 (t -1.35).

### ORB 23:30–00:15

Rotura con cuerpo desde las 00:15 hasta las 06:15 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.079 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 1018, stop 963, por tiempo 114.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 51.3 % | -0.053 | -111.2 | 0.90 | -150.8 | -2.48 |
| Sin costes | 2095 | 51.4 % | +0.026 | +54.8 | 1.06 | -45.3 | +1.22 |
| Long | 1088 | 52.8 % | -0.025 | -27.3 | 0.95 | -55.2 | -0.85 |
| Short | 1007 | 49.6 % | -0.083 | -84.0 | 0.84 | -111.6 | -2.70 |
| 1.ª mitad | 1048 | 50.5 % | -0.070 | -73.6 | 0.86 | -87.3 | -2.32 |
| 2.ª mitad | 1047 | 52.1 % | -0.036 | -37.6 | 0.93 | -65.6 | -1.19 |

Por año (R neto medio y operaciones): 2018 +0.036 (76), 2019 -0.139 (257), 2020 +0.004 (256), 2021 -0.074 (259), 2022 -0.127 (258), 2023 -0.153 (258), 2024 +0.023 (259), 2025 -0.040 (256), 2026 +0.076 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.058 (t -2.67), colchón 50 % -0.041 (t -1.96), objetivo 1,5:1 -0.059 (t -2.31), objetivo 2:1 -0.062 (t -2.14).

### ORB 23:45–00:30

Rotura con cuerpo desde las 00:30 hasta las 06:30 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.081 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 1027, stop 965, por tiempo 101.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2093 | 51.3 % | -0.052 | -109.4 | 0.90 | -135.6 | -2.44 |
| Sin costes | 2093 | 51.3 % | +0.029 | +61.1 | 1.06 | -45.3 | +1.36 |
| Long | 1075 | 53.9 % | -0.009 | -9.4 | 0.98 | -49.6 | -0.29 |
| Short | 1018 | 48.6 % | -0.098 | -99.9 | 0.82 | -109.3 | -3.19 |
| 1.ª mitad | 1047 | 50.1 % | -0.074 | -77.8 | 0.86 | -83.5 | -2.45 |
| 2.ª mitad | 1046 | 52.5 % | -0.030 | -31.6 | 0.94 | -54.4 | -1.00 |

Por año (R neto medio y operaciones): 2018 -0.040 (76), 2019 -0.093 (257), 2020 +0.019 (256), 2021 -0.152 (259), 2022 -0.094 (258), 2023 -0.139 (257), 2024 +0.019 (259), 2025 -0.006 (255), 2026 +0.038 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.046 (t -2.12), colchón 50 % -0.061 (t -2.92), objetivo 1,5:1 -0.054 (t -2.10), objetivo 2:1 -0.042 (t -1.42).

