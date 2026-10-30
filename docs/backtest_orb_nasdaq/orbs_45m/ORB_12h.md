# ORB de 45 min de las 12:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 12:00–12:45 | 2058 | 49.6 | -0.024 | -1.35 | +0.000 | 0.024 | no |
| 12:15–13:00 | 2041 | 50.2 | -0.005 | -0.29 | +0.020 | 0.025 | no |
| 12:30–13:15 | 1991 | 49.9 | -0.005 | -0.27 | +0.020 | 0.025 | no |
| 12:45–13:30 | 1985 | 49.9 | -0.004 | -0.21 | +0.021 | 0.025 | no |

## Detalle

### ORB 12:00–12:45

Rotura con cuerpo desde las 12:45 hasta las 18:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2058.

**No pasa los criterios**. Coste medio 0.024 R; ancho medio del ORB 0.42 %; cómo terminan: objetivo 623, stop 635, por tiempo 800.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2058 | 49.6 % | -0.024 | -50.2 | 0.94 | -63.3 | -1.35 |
| Sin costes | 2058 | 50.5 % | +0.000 | +0.2 | 1.00 | -29.6 | +0.01 |
| Long | 1147 | 52.1 % | -0.004 | -4.0 | 0.99 | -35.9 | -0.15 |
| Short | 911 | 46.4 % | -0.051 | -46.1 | 0.87 | -58.1 | -1.84 |
| 1.ª mitad | 1029 | 49.6 % | -0.033 | -34.3 | 0.92 | -41.0 | -1.28 |
| 2.ª mitad | 1029 | 49.7 % | -0.015 | -15.9 | 0.96 | -37.7 | -0.62 |

Por año (R neto medio y operaciones): 2018 -0.114 (75), 2019 -0.017 (253), 2020 -0.015 (257), 2021 -0.066 (250), 2022 -0.021 (256), 2023 -0.020 (252), 2024 +0.057 (257), 2025 -0.073 (251), 2026 -0.015 (207).

Sensibilidad (R neto medio y t): colchón 0 % -0.018 (t -0.92), colchón 50 % -0.018 (t -1.06), objetivo 1,5:1 -0.019 (t -0.95), objetivo 2:1 -0.009 (t -0.42).

### ORB 12:15–13:00

Rotura con cuerpo desde las 13:00 hasta las 19:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2041.

**No pasa los criterios**. Coste medio 0.025 R; ancho medio del ORB 0.41 %; cómo terminan: objetivo 643, stop 616, por tiempo 782.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2041 | 50.2 % | -0.005 | -10.8 | 0.99 | -30.5 | -0.29 |
| Sin costes | 2041 | 50.7 % | +0.020 | +40.3 | 1.05 | -23.1 | +1.08 |
| Long | 1131 | 53.1 % | +0.034 | +38.0 | 1.10 | -24.2 | +1.38 |
| Short | 910 | 46.5 % | -0.054 | -48.8 | 0.87 | -60.1 | -1.94 |
| 1.ª mitad | 1021 | 50.0 % | -0.016 | -16.0 | 0.96 | -30.5 | -0.60 |
| 2.ª mitad | 1020 | 50.4 % | +0.005 | +5.2 | 1.01 | -28.7 | +0.20 |

Por año (R neto medio y operaciones): 2018 -0.088 (75), 2019 +0.033 (251), 2020 -0.054 (255), 2021 -0.033 (251), 2022 +0.039 (256), 2023 -0.004 (245), 2024 +0.031 (253), 2025 -0.054 (248), 2026 +0.030 (207).

Sensibilidad (R neto medio y t): colchón 0 % +0.002 (t +0.11), colchón 50 % -0.011 (t -0.67), objetivo 1,5:1 +0.001 (t +0.05), objetivo 2:1 +0.008 (t +0.37).

### ORB 12:30–13:15

Rotura con cuerpo desde las 13:15 hasta las 19:15; a esa hora se cierra. ORB completos: 2042; con rotura: 1991.

**No pasa los criterios**. Coste medio 0.025 R; ancho medio del ORB 0.41 %; cómo terminan: objetivo 616, stop 576, por tiempo 799.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1991 | 49.9 % | -0.005 | -9.9 | 0.99 | -41.1 | -0.27 |
| Sin costes | 1991 | 50.7 % | +0.020 | +39.2 | 1.05 | -28.4 | +1.07 |
| Long | 1108 | 52.9 % | +0.031 | +34.1 | 1.09 | -20.5 | +1.27 |
| Short | 883 | 46.2 % | -0.050 | -44.0 | 0.88 | -54.6 | -1.78 |
| 1.ª mitad | 996 | 50.6 % | +0.000 | +0.2 | 1.00 | -39.2 | +0.01 |
| 2.ª mitad | 995 | 49.2 % | -0.010 | -10.1 | 0.97 | -41.1 | -0.40 |

Por año (R neto medio y operaciones): 2018 +0.117 (71), 2019 -0.035 (246), 2020 -0.055 (249), 2021 -0.042 (246), 2022 +0.148 (246), 2023 +0.011 (245), 2024 -0.047 (241), 2025 -0.074 (243), 2026 +0.022 (204).

Sensibilidad (R neto medio y t): colchón 0 % +0.003 (t +0.15), colchón 50 % -0.001 (t -0.08), objetivo 1,5:1 +0.003 (t +0.14), objetivo 2:1 +0.013 (t +0.57).

### ORB 12:45–13:30

Rotura con cuerpo desde las 13:30 hasta las 19:30; a esa hora se cierra. ORB completos: 2025; con rotura: 1985.

**No pasa los criterios**. Coste medio 0.025 R; ancho medio del ORB 0.41 %; cómo terminan: objetivo 604, stop 565, por tiempo 816.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1985 | 49.9 % | -0.004 | -7.5 | 0.99 | -54.3 | -0.21 |
| Sin costes | 1985 | 50.7 % | +0.021 | +41.7 | 1.06 | -34.8 | +1.15 |
| Long | 1121 | 51.4 % | +0.012 | +13.1 | 1.03 | -22.6 | +0.48 |
| Short | 864 | 47.9 % | -0.024 | -20.5 | 0.94 | -45.8 | -0.85 |
| 1.ª mitad | 993 | 49.3 % | -0.020 | -20.3 | 0.95 | -54.3 | -0.77 |
| 2.ª mitad | 992 | 50.4 % | +0.013 | +12.8 | 1.04 | -16.2 | +0.51 |

Por año (R neto medio y operaciones): 2018 +0.082 (72), 2019 -0.123 (246), 2020 -0.064 (249), 2021 -0.007 (243), 2022 +0.132 (247), 2023 +0.025 (245), 2024 -0.022 (244), 2025 +0.015 (241), 2026 -0.012 (198).

Sensibilidad (R neto medio y t): colchón 0 % -0.003 (t -0.15), colchón 50 % +0.007 (t +0.40), objetivo 1,5:1 +0.003 (t +0.13), objetivo 2:1 +0.000 (t +0.01).

