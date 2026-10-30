# ORB de 15 min de las 10:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 10:00–10:15 | 2090 | 51.5 | +0.009 | +0.43 | +0.031 | 0.022 | no |
| 10:15–10:30 | 2095 | 52.2 | +0.011 | +0.54 | +0.037 | 0.026 | no |
| 10:30–10:45 | 2094 | 50.1 | -0.015 | -0.76 | +0.012 | 0.027 | no |
| 10:45–11:00 | 2096 | 50.9 | -0.009 | -0.46 | +0.020 | 0.029 | no |

## Detalle

### ORB 10:00–10:15

Rotura con cuerpo desde las 10:15 hasta las 16:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.022 R; ancho medio del ORB 0.41 %; cómo terminan: objetivo 865, stop 802, por tiempo 423.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2090 | 51.5 % | +0.009 | +18.1 | 1.02 | -24.0 | +0.43 |
| Sin costes | 2090 | 51.7 % | +0.031 | +65.0 | 1.07 | -22.2 | +1.56 |
| Long | 1123 | 53.3 % | +0.028 | +31.6 | 1.07 | -14.4 | +1.04 |
| Short | 967 | 49.3 % | -0.014 | -13.5 | 0.97 | -30.0 | -0.47 |
| 1.ª mitad | 1045 | 52.2 % | +0.023 | +24.1 | 1.05 | -24.0 | +0.80 |
| 2.ª mitad | 1045 | 50.8 % | -0.006 | -6.0 | 0.99 | -22.1 | -0.21 |

Por año (R neto medio y operaciones): 2018 -0.099 (75), 2019 +0.045 (256), 2020 +0.007 (259), 2021 -0.005 (258), 2022 +0.041 (258), 2023 -0.007 (255), 2024 +0.079 (258), 2025 -0.041 (256), 2026 -0.025 (215).

Sensibilidad (R neto medio y t): colchón 0 % +0.017 (t +0.80), colchón 50 % +0.002 (t +0.11), objetivo 1,5:1 +0.013 (t +0.55), objetivo 2:1 +0.017 (t +0.67).

### ORB 10:15–10:30

Rotura con cuerpo desde las 10:30 hasta las 16:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.026 R; ancho medio del ORB 0.36 %; cómo terminan: objetivo 909, stop 846, por tiempo 340.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2095 | 52.2 % | +0.011 | +22.9 | 1.02 | -27.4 | +0.54 |
| Sin costes | 2095 | 52.5 % | +0.037 | +76.7 | 1.08 | -22.6 | +1.80 |
| Long | 1111 | 54.2 % | +0.027 | +29.7 | 1.06 | -19.2 | +0.97 |
| Short | 984 | 50.0 % | -0.007 | -6.8 | 0.98 | -34.1 | -0.23 |
| 1.ª mitad | 1048 | 53.4 % | +0.028 | +28.9 | 1.06 | -24.6 | +0.95 |
| 2.ª mitad | 1047 | 51.0 % | -0.006 | -6.0 | 0.99 | -25.8 | -0.20 |

Por año (R neto medio y operaciones): 2018 +0.010 (75), 2019 -0.001 (258), 2020 +0.059 (259), 2021 +0.040 (258), 2022 -0.014 (258), 2023 +0.007 (256), 2024 +0.020 (259), 2025 -0.055 (257), 2026 +0.035 (215).

Sensibilidad (R neto medio y t): colchón 0 % +0.013 (t +0.63), colchón 50 % +0.016 (t +0.83), objetivo 1,5:1 +0.018 (t +0.77), objetivo 2:1 +0.033 (t +1.27).

### ORB 10:30–10:45

Rotura con cuerpo desde las 10:45 hasta las 16:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.027 R; ancho medio del ORB 0.34 %; cómo terminan: objetivo 874, stop 862, por tiempo 358.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2094 | 50.1 % | -0.015 | -32.1 | 0.97 | -79.1 | -0.76 |
| Sin costes | 2094 | 50.5 % | +0.012 | +24.8 | 1.03 | -37.7 | +0.58 |
| Long | 1121 | 51.6 % | +0.007 | +7.5 | 1.02 | -23.3 | +0.24 |
| Short | 973 | 48.4 % | -0.041 | -39.6 | 0.91 | -68.4 | -1.35 |
| 1.ª mitad | 1047 | 51.5 % | +0.009 | +9.9 | 1.02 | -33.2 | +0.33 |
| 2.ª mitad | 1047 | 48.7 % | -0.040 | -42.0 | 0.91 | -55.7 | -1.41 |

Por año (R neto medio y operaciones): 2018 +0.132 (75), 2019 +0.035 (258), 2020 -0.012 (259), 2021 -0.020 (257), 2022 -0.026 (258), 2023 -0.023 (257), 2024 -0.016 (259), 2025 -0.074 (257), 2026 -0.033 (214).

Sensibilidad (R neto medio y t): colchón 0 % -0.044 (t -2.11), colchón 50 % -0.004 (t -0.18), objetivo 1,5:1 -0.008 (t -0.35), objetivo 2:1 +0.005 (t +0.19).

### ORB 10:45–11:00

Rotura con cuerpo desde las 11:00 hasta las 17:00; a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.029 R; ancho medio del ORB 0.32 %; cómo terminan: objetivo 928, stop 884, por tiempo 284.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 50.9 % | -0.009 | -19.6 | 0.98 | -57.2 | -0.46 |
| Sin costes | 2096 | 51.2 % | +0.020 | +41.1 | 1.04 | -40.1 | +0.95 |
| Long | 1134 | 51.9 % | +0.005 | +5.5 | 1.01 | -38.0 | +0.18 |
| Short | 962 | 49.6 % | -0.026 | -25.2 | 0.94 | -48.5 | -0.85 |
| 1.ª mitad | 1048 | 52.5 % | +0.016 | +16.5 | 1.03 | -25.3 | +0.54 |
| 2.ª mitad | 1048 | 49.2 % | -0.035 | -36.2 | 0.93 | -57.2 | -1.19 |

Por año (R neto medio y operaciones): 2018 +0.114 (76), 2019 -0.027 (258), 2020 +0.074 (259), 2021 -0.013 (258), 2022 -0.009 (258), 2023 +0.009 (257), 2024 +0.000 (259), 2025 -0.154 (257), 2026 +0.011 (214).

Sensibilidad (R neto medio y t): colchón 0 % -0.031 (t -1.45), colchón 50 % -0.008 (t -0.41), objetivo 1,5:1 -0.008 (t -0.35), objetivo 2:1 +0.004 (t +0.16).

