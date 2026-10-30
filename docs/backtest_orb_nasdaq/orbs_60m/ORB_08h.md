# ORB de 60 min de las 08:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 08:00–09:00 | 2080 | 47.9 | -0.062 | -3.01 | -0.037 | 0.025 | no |
| 08:15–09:15 | 2078 | 48.5 | -0.050 | -2.45 | -0.026 | 0.024 | no |
| 08:30–09:30 | 2078 | 50.0 | -0.012 | -0.61 | +0.008 | 0.021 | no |
| 08:45–09:45 | 2066 | 53.1 | +0.039 | +2.20 | +0.054 | 0.015 | no |

## Detalle

### ORB 08:00–09:00

Rotura con cuerpo desde las 09:00 hasta las 15:00; a esa hora se cierra. ORB completos: 2094; con rotura: 2080.

**No pasa los criterios**. Coste medio 0.025 R; ancho medio del ORB 0.41 %; cómo terminan: objetivo 839, stop 916, por tiempo 325.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2080 | 47.9 % | -0.062 | -128.2 | 0.87 | -135.4 | -3.01 |
| Sin costes | 2080 | 48.0 % | -0.037 | -76.8 | 0.92 | -86.4 | -1.80 |
| Long | 1056 | 48.4 % | -0.069 | -72.7 | 0.86 | -76.0 | -2.40 |
| Short | 1024 | 47.5 % | -0.054 | -55.5 | 0.89 | -68.3 | -1.86 |
| 1.ª mitad | 1040 | 48.7 % | -0.050 | -52.0 | 0.90 | -60.3 | -1.71 |
| 2.ª mitad | 1040 | 47.2 % | -0.073 | -76.3 | 0.85 | -91.9 | -2.56 |

Por año (R neto medio y operaciones): 2018 -0.125 (75), 2019 +0.001 (257), 2020 -0.067 (253), 2021 -0.049 (256), 2022 -0.021 (255), 2023 -0.140 (257), 2024 -0.079 (258), 2025 -0.064 (256), 2026 -0.055 (213).

Sensibilidad (R neto medio y t): colchón 0 % -0.064 (t -3.06), colchón 50 % -0.054 (t -2.77), objetivo 1,5:1 -0.058 (t -2.43), objetivo 2:1 -0.043 (t -1.62).

### ORB 08:15–09:15

Rotura con cuerpo desde las 09:15 hasta las 15:15; a esa hora se cierra. ORB completos: 2094; con rotura: 2078.

**No pasa los criterios**. Coste medio 0.024 R; ancho medio del ORB 0.41 %; cómo terminan: objetivo 833, stop 903, por tiempo 342.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2078 | 48.5 % | -0.050 | -104.0 | 0.89 | -111.5 | -2.45 |
| Sin costes | 2078 | 48.7 % | -0.026 | -55.0 | 0.94 | -69.0 | -1.30 |
| Long | 1069 | 48.4 % | -0.058 | -62.3 | 0.88 | -67.5 | -2.05 |
| Short | 1009 | 48.7 % | -0.041 | -41.7 | 0.91 | -53.6 | -1.41 |
| 1.ª mitad | 1039 | 49.3 % | -0.039 | -40.5 | 0.92 | -50.6 | -1.33 |
| 2.ª mitad | 1039 | 47.7 % | -0.061 | -63.5 | 0.87 | -80.3 | -2.14 |

Por año (R neto medio y operaciones): 2018 -0.237 (75), 2019 +0.013 (257), 2020 -0.009 (254), 2021 -0.086 (256), 2022 +0.019 (254), 2023 -0.086 (256), 2024 -0.066 (258), 2025 -0.048 (255), 2026 -0.088 (213).

Sensibilidad (R neto medio y t): colchón 0 % -0.061 (t -2.91), colchón 50 % -0.033 (t -1.68), objetivo 1,5:1 -0.041 (t -1.73), objetivo 2:1 -0.029 (t -1.10).

### ORB 08:30–09:30

Rotura con cuerpo desde las 09:30 hasta las 15:30; a esa hora se cierra. ORB completos: 2092; con rotura: 2078.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.41 %; cómo terminan: objetivo 850, stop 853, por tiempo 375.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2078 | 50.0 % | -0.012 | -25.6 | 0.97 | -47.1 | -0.61 |
| Sin costes | 2078 | 50.4 % | +0.008 | +17.6 | 1.02 | -26.8 | +0.42 |
| Long | 1058 | 50.3 % | -0.015 | -15.9 | 0.97 | -22.9 | -0.53 |
| Short | 1020 | 49.7 % | -0.009 | -9.7 | 0.98 | -35.2 | -0.33 |
| 1.ª mitad | 1039 | 50.0 % | -0.009 | -8.9 | 0.98 | -34.7 | -0.29 |
| 2.ª mitad | 1039 | 50.0 % | -0.016 | -16.7 | 0.96 | -34.0 | -0.57 |

Por año (R neto medio y operaciones): 2018 -0.043 (75), 2019 +0.023 (256), 2020 +0.013 (254), 2021 -0.039 (254), 2022 +0.011 (256), 2023 -0.041 (256), 2024 -0.010 (258), 2025 +0.027 (256), 2026 -0.085 (213).

Sensibilidad (R neto medio y t): colchón 0 % -0.015 (t -0.74), colchón 50 % +0.020 (t +1.03), objetivo 1,5:1 +0.024 (t +0.99), objetivo 2:1 +0.033 (t +1.26).

### ORB 08:45–09:45

Rotura con cuerpo desde las 09:45 hasta las 15:45; a esa hora se cierra. ORB completos: 2090; con rotura: 2066.

**No pasa los criterios**. Coste medio 0.015 R; ancho medio del ORB 0.61 %; cómo terminan: objetivo 630, stop 568, por tiempo 868.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2066 | 53.1 % | +0.039 | +81.0 | 1.11 | -14.6 | +2.20 |
| Sin costes | 2066 | 53.6 % | +0.054 | +111.5 | 1.16 | -13.9 | +3.03 |
| Long | 1076 | 56.4 % | +0.055 | +59.0 | 1.17 | -15.0 | +2.27 |
| Short | 990 | 49.5 % | +0.022 | +22.0 | 1.06 | -14.5 | +0.85 |
| 1.ª mitad | 1033 | 52.6 % | +0.029 | +30.2 | 1.08 | -14.6 | +1.16 |
| 2.ª mitad | 1033 | 53.6 % | +0.049 | +50.8 | 1.14 | -13.5 | +1.95 |

Por año (R neto medio y operaciones): 2018 -0.056 (75), 2019 +0.051 (253), 2020 +0.017 (253), 2021 +0.084 (255), 2022 +0.041 (255), 2023 +0.012 (256), 2024 +0.061 (256), 2025 +0.073 (252), 2026 -0.003 (211).

Sensibilidad (R neto medio y t): colchón 0 % +0.046 (t +2.45), colchón 50 % +0.039 (t +2.42), objetivo 1,5:1 +0.044 (t +2.24), objetivo 2:1 +0.045 (t +2.16).

