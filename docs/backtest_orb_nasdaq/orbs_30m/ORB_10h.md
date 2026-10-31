# ORB de 30 min de las 10:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 10:00–10:30 | 2065 | 51.6 | +0.012 | +0.67 | +0.030 | 0.018 | no |
| 10:15–10:45 | 2076 | 50.9 | +0.004 | +0.22 | +0.024 | 0.019 | no |
| 10:30–11:00 | 2080 | 51.0 | -0.001 | -0.04 | +0.020 | 0.021 | no |
| 10:45–11:15 | 2085 | 50.6 | +0.003 | +0.13 | +0.025 | 0.022 | no |

## Detalle

### ORB 10:00–10:30

Rotura con cuerpo desde las 10:30 hasta las 16:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2065.

**No pasa los criterios**. Coste medio 0.018 R; ancho medio del ORB 0.55 %; cómo terminan: objetivo 638, stop 598, por tiempo 829.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2065 | 51.6 % | +0.012 | +24.9 | 1.03 | -30.9 | +0.67 |
| Sin costes | 2065 | 52.3 % | +0.030 | +61.4 | 1.08 | -20.2 | +1.64 |
| Long | 1117 | 54.2 % | +0.029 | +31.9 | 1.08 | -17.7 | +1.18 |
| Short | 948 | 48.6 % | -0.007 | -7.1 | 0.98 | -35.8 | -0.27 |
| 1.ª mitad | 1033 | 54.1 % | +0.045 | +46.9 | 1.13 | -17.4 | +1.75 |
| 2.ª mitad | 1032 | 49.1 % | -0.021 | -22.1 | 0.94 | -28.5 | -0.85 |

Por año (R neto medio y operaciones): 2018 -0.062 (75), 2019 +0.006 (253), 2020 +0.051 (257), 2021 +0.061 (253), 2022 +0.058 (256), 2023 -0.029 (252), 2024 +0.024 (256), 2025 -0.060 (253), 2026 +0.004 (210).

Sensibilidad (R neto medio y t): colchón 0 % +0.016 (t +0.83), colchón 50 % +0.012 (t +0.74), objetivo 1,5:1 +0.009 (t +0.47), objetivo 2:1 +0.008 (t +0.37).

### ORB 10:15–10:45

Rotura con cuerpo desde las 10:45 hasta las 16:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2076.

**No pasa los criterios**. Coste medio 0.019 R; ancho medio del ORB 0.50 %; cómo terminan: objetivo 674, stop 644, por tiempo 758.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2076 | 50.9 % | +0.004 | +8.5 | 1.01 | -58.9 | +0.22 |
| Sin costes | 2076 | 51.4 % | +0.024 | +48.9 | 1.06 | -44.5 | +1.28 |
| Long | 1117 | 54.2 % | +0.034 | +38.1 | 1.10 | -13.9 | +1.39 |
| Short | 959 | 47.1 % | -0.031 | -29.6 | 0.92 | -61.2 | -1.12 |
| 1.ª mitad | 1038 | 54.1 % | +0.055 | +57.4 | 1.15 | -15.2 | +2.11 |
| 2.ª mitad | 1038 | 47.7 % | -0.047 | -48.9 | 0.88 | -58.5 | -1.83 |

Por año (R neto medio y operaciones): 2018 +0.114 (75), 2019 +0.006 (258), 2020 +0.058 (258), 2021 +0.037 (254), 2022 +0.089 (257), 2023 -0.015 (256), 2024 -0.058 (257), 2025 -0.026 (253), 2026 -0.112 (208).

Sensibilidad (R neto medio y t): colchón 0 % +0.015 (t +0.76), colchón 50 % +0.015 (t +0.88), objetivo 1,5:1 +0.016 (t +0.78), objetivo 2:1 +0.030 (t +1.36).

### ORB 10:30–11:00

Rotura con cuerpo desde las 11:00 hasta las 17:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2080.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.47 %; cómo terminan: objetivo 700, stop 669, por tiempo 711.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2080 | 51.0 % | -0.001 | -1.4 | 1.00 | -50.6 | -0.04 |
| Sin costes | 2080 | 51.5 % | +0.020 | +41.5 | 1.05 | -31.2 | +1.07 |
| Long | 1144 | 52.5 % | +0.018 | +20.6 | 1.05 | -21.5 | +0.73 |
| Short | 936 | 49.0 % | -0.024 | -22.1 | 0.94 | -40.7 | -0.83 |
| 1.ª mitad | 1040 | 53.2 % | +0.030 | +30.7 | 1.08 | -13.6 | +1.11 |
| 2.ª mitad | 1040 | 48.8 % | -0.031 | -32.1 | 0.92 | -45.9 | -1.19 |

Por año (R neto medio y operaciones): 2018 +0.117 (74), 2019 -0.001 (255), 2020 +0.043 (258), 2021 +0.029 (257), 2022 -0.006 (256), 2023 -0.033 (256), 2024 -0.035 (255), 2025 -0.047 (257), 2026 +0.012 (212).

Sensibilidad (R neto medio y t): colchón 0 % -0.007 (t -0.37), colchón 50 % +0.008 (t +0.45), objetivo 1,5:1 +0.008 (t +0.38), objetivo 2:1 +0.020 (t +0.91).

### ORB 10:45–11:15

Rotura con cuerpo desde las 11:15 hasta las 17:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2085.

**No pasa los criterios**. Coste medio 0.022 R; ancho medio del ORB 0.45 %; cómo terminan: objetivo 724, stop 678, por tiempo 683.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2085 | 50.6 % | +0.003 | +5.3 | 1.01 | -43.5 | +0.13 |
| Sin costes | 2085 | 51.1 % | +0.025 | +51.1 | 1.06 | -24.5 | +1.31 |
| Long | 1153 | 51.9 % | +0.018 | +21.1 | 1.05 | -23.3 | +0.73 |
| Short | 932 | 49.1 % | -0.017 | -15.8 | 0.96 | -45.4 | -0.60 |
| 1.ª mitad | 1043 | 52.0 % | +0.033 | +34.5 | 1.09 | -23.3 | +1.24 |
| 2.ª mitad | 1042 | 49.3 % | -0.028 | -29.2 | 0.93 | -35.9 | -1.08 |

Por año (R neto medio y operaciones): 2018 +0.094 (76), 2019 -0.001 (258), 2020 +0.138 (259), 2021 -0.065 (255), 2022 +0.016 (257), 2023 -0.064 (256), 2024 -0.006 (258), 2025 -0.014 (255), 2026 -0.017 (211).

Sensibilidad (R neto medio y t): colchón 0 % -0.011 (t -0.54), colchón 50 % +0.017 (t +1.00), objetivo 1,5:1 +0.016 (t +0.74), objetivo 2:1 +0.026 (t +1.13).

