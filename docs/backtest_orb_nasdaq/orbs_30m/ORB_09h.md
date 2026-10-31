# ORB de 30 min de las 09:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 09:00–09:30 | 2090 | 50.7 | -0.014 | -0.66 | +0.014 | 0.028 | no |
| 09:15–09:45 | 2079 | 53.0 | +0.035 | +1.89 | +0.051 | 0.016 | no |
| 09:30–10:00 | 2053 | 50.9 | -0.003 | -0.15 | +0.011 | 0.014 | no |
| 09:45–10:15 | 2060 | 52.0 | +0.011 | +0.61 | +0.027 | 0.016 | no |

## Detalle

### ORB 09:00–09:30

Rotura con cuerpo desde las 09:30 hasta las 15:30; a esa hora se cierra. ORB completos: 2092; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.028 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 999, stop 969, por tiempo 122.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2090 | 50.7 % | -0.014 | -29.4 | 0.97 | -58.2 | -0.66 |
| Sin costes | 2090 | 50.9 % | +0.014 | +29.6 | 1.03 | -37.1 | +0.66 |
| Long | 1056 | 51.0 % | -0.012 | -12.2 | 0.98 | -26.5 | -0.38 |
| Short | 1034 | 50.4 % | -0.017 | -17.2 | 0.97 | -48.0 | -0.55 |
| 1.ª mitad | 1045 | 48.9 % | -0.050 | -52.7 | 0.90 | -58.2 | -1.67 |
| 2.ª mitad | 1045 | 52.5 % | +0.022 | +23.3 | 1.05 | -31.1 | +0.74 |

Por año (R neto medio y operaciones): 2018 -0.227 (75), 2019 +0.042 (258), 2020 -0.044 (254), 2021 -0.071 (257), 2022 -0.024 (258), 2023 +0.056 (257), 2024 +0.066 (259), 2025 -0.003 (257), 2026 -0.084 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.001 (t -0.06), colchón 50 % +0.010 (t +0.50), objetivo 1,5:1 +0.020 (t +0.76), objetivo 2:1 +0.041 (t +1.42).

### ORB 09:15–09:45

Rotura con cuerpo desde las 09:45 hasta las 15:45; a esa hora se cierra. ORB completos: 2091; con rotura: 2079.

**No pasa los criterios**. Coste medio 0.016 R; ancho medio del ORB 0.56 %; cómo terminan: objetivo 701, stop 631, por tiempo 747.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2079 | 53.0 % | +0.035 | +72.4 | 1.09 | -15.4 | +1.89 |
| Sin costes | 2079 | 53.4 % | +0.051 | +105.4 | 1.14 | -13.1 | +2.75 |
| Long | 1078 | 56.6 % | +0.060 | +64.2 | 1.17 | -13.4 | +2.37 |
| Short | 1001 | 49.2 % | +0.008 | +8.1 | 1.02 | -17.5 | +0.30 |
| 1.ª mitad | 1040 | 52.5 % | +0.023 | +23.7 | 1.06 | -15.4 | +0.88 |
| 2.ª mitad | 1039 | 53.5 % | +0.047 | +48.7 | 1.13 | -14.5 | +1.80 |

Por año (R neto medio y operaciones): 2018 -0.052 (75), 2019 +0.062 (254), 2020 -0.030 (254), 2021 +0.079 (258), 2022 +0.049 (257), 2023 +0.028 (256), 2024 +0.045 (259), 2025 +0.067 (253), 2026 -0.004 (213).

Sensibilidad (R neto medio y t): colchón 0 % +0.034 (t +1.73), colchón 50 % +0.029 (t +1.75), objetivo 1,5:1 +0.041 (t +1.96), objetivo 2:1 +0.043 (t +1.99).

### ORB 09:30–10:00

Rotura con cuerpo desde las 10:00 hasta las 16:00; a esa hora se cierra. ORB completos: 2093; con rotura: 2053.

**No pasa los criterios**. Coste medio 0.014 R; ancho medio del ORB 0.68 %; cómo terminan: objetivo 495, stop 512, por tiempo 1046.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2053 | 50.9 % | -0.003 | -5.3 | 0.99 | -39.9 | -0.15 |
| Sin costes | 2053 | 51.4 % | +0.011 | +22.6 | 1.03 | -31.9 | +0.65 |
| Long | 1087 | 55.6 % | +0.028 | +29.9 | 1.09 | -16.9 | +1.22 |
| Short | 966 | 45.8 % | -0.036 | -35.2 | 0.90 | -40.0 | -1.43 |
| 1.ª mitad | 1027 | 49.6 % | -0.023 | -23.8 | 0.93 | -39.9 | -0.96 |
| 2.ª mitad | 1026 | 52.3 % | +0.018 | +18.5 | 1.06 | -16.0 | +0.76 |

Por año (R neto medio y operaciones): 2018 -0.122 (75), 2019 -0.009 (249), 2020 -0.073 (255), 2021 +0.021 (249), 2022 +0.043 (253), 2023 +0.001 (253), 2024 +0.041 (257), 2025 +0.013 (254), 2026 -0.026 (208).

Sensibilidad (R neto medio y t): colchón 0 % +0.017 (t +0.95), colchón 50 % -0.006 (t -0.37), objetivo 1,5:1 +0.004 (t +0.21), objetivo 2:1 +0.006 (t +0.31).

### ORB 09:45–10:15

Rotura con cuerpo desde las 10:15 hasta las 16:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2060.

**No pasa los criterios**. Coste medio 0.016 R; ancho medio del ORB 0.60 %; cómo terminan: objetivo 600, stop 571, por tiempo 889.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2060 | 52.0 % | +0.011 | +22.3 | 1.03 | -29.8 | +0.61 |
| Sin costes | 2060 | 52.3 % | +0.027 | +55.1 | 1.08 | -22.8 | +1.51 |
| Long | 1120 | 54.2 % | +0.016 | +17.7 | 1.05 | -17.0 | +0.67 |
| Short | 940 | 49.4 % | +0.005 | +4.7 | 1.01 | -23.4 | +0.18 |
| 1.ª mitad | 1030 | 53.7 % | +0.033 | +33.9 | 1.09 | -24.6 | +1.29 |
| 2.ª mitad | 1030 | 50.3 % | -0.011 | -11.5 | 0.97 | -24.7 | -0.46 |

Por año (R neto medio y operaciones): 2018 -0.069 (75), 2019 +0.051 (249), 2020 +0.029 (256), 2021 +0.064 (252), 2022 +0.026 (254), 2023 -0.037 (252), 2024 +0.013 (256), 2025 -0.000 (251), 2026 -0.044 (215).

Sensibilidad (R neto medio y t): colchón 0 % +0.022 (t +1.17), colchón 50 % -0.005 (t -0.34), objetivo 1,5:1 +0.001 (t +0.06), objetivo 2:1 +0.008 (t +0.41).

