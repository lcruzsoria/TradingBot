# ORB de 30 min de las 12:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 12:00–12:30 | 2079 | 49.5 | -0.042 | -2.16 | -0.013 | 0.029 | no |
| 12:15–12:45 | 2074 | 50.3 | -0.023 | -1.16 | +0.008 | 0.030 | no |
| 12:30–13:00 | 2067 | 50.0 | -0.011 | -0.54 | +0.020 | 0.031 | no |
| 12:45–13:15 | 2014 | 50.9 | -0.002 | -0.09 | +0.028 | 0.029 | no |

## Detalle

### ORB 12:00–12:30

Rotura con cuerpo desde las 12:30 hasta las 18:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2079.

**No pasa los criterios**. Coste medio 0.029 R; ancho medio del ORB 0.35 %; cómo terminan: objetivo 745, stop 790, por tiempo 544.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2079 | 49.5 % | -0.042 | -87.2 | 0.90 | -96.4 | -2.16 |
| Sin costes | 2079 | 50.2 % | -0.013 | -27.0 | 0.97 | -42.4 | -0.67 |
| Long | 1134 | 51.7 % | -0.013 | -14.4 | 0.97 | -35.7 | -0.49 |
| Short | 945 | 46.9 % | -0.077 | -72.8 | 0.83 | -85.9 | -2.65 |
| 1.ª mitad | 1040 | 49.7 % | -0.046 | -48.2 | 0.90 | -56.4 | -1.66 |
| 2.ª mitad | 1039 | 49.3 % | -0.038 | -39.0 | 0.91 | -49.2 | -1.38 |

Por año (R neto medio y operaciones): 2018 -0.080 (75), 2019 -0.033 (255), 2020 +0.001 (258), 2021 -0.080 (256), 2022 -0.074 (258), 2023 -0.051 (256), 2024 +0.051 (258), 2025 -0.110 (253), 2026 -0.028 (210).

Sensibilidad (R neto medio y t): colchón 0 % -0.039 (t -1.90), colchón 50 % -0.037 (t -2.03), objetivo 1,5:1 -0.043 (t -1.95), objetivo 2:1 -0.029 (t -1.23).

### ORB 12:15–12:45

Rotura con cuerpo desde las 12:45 hasta las 18:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2074.

**No pasa los criterios**. Coste medio 0.030 R; ancho medio del ORB 0.34 %; cómo terminan: objetivo 773, stop 768, por tiempo 533.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2074 | 50.3 % | -0.023 | -47.0 | 0.95 | -57.1 | -1.16 |
| Sin costes | 2074 | 50.9 % | +0.008 | +16.0 | 1.02 | -33.7 | +0.40 |
| Long | 1142 | 51.8 % | -0.007 | -8.2 | 0.98 | -37.8 | -0.27 |
| Short | 932 | 48.5 % | -0.042 | -38.7 | 0.91 | -55.8 | -1.42 |
| 1.ª mitad | 1037 | 50.0 % | -0.034 | -35.2 | 0.92 | -43.0 | -1.22 |
| 2.ª mitad | 1037 | 50.6 % | -0.011 | -11.7 | 0.97 | -41.6 | -0.41 |

Por año (R neto medio y operaciones): 2018 -0.084 (76), 2019 -0.023 (255), 2020 -0.060 (258), 2021 -0.021 (254), 2022 -0.001 (258), 2023 -0.014 (253), 2024 +0.047 (257), 2025 -0.056 (254), 2026 -0.037 (209).

Sensibilidad (R neto medio y t): colchón 0 % -0.015 (t -0.72), colchón 50 % -0.024 (t -1.32), objetivo 1,5:1 -0.011 (t -0.47), objetivo 2:1 +0.003 (t +0.11).

### ORB 12:30–13:00

Rotura con cuerpo desde las 13:00 hasta las 19:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2067.

**No pasa los criterios**. Coste medio 0.031 R; ancho medio del ORB 0.33 %; cómo terminan: objetivo 790, stop 748, por tiempo 529.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2067 | 50.0 % | -0.011 | -21.8 | 0.97 | -49.9 | -0.54 |
| Sin costes | 2067 | 50.5 % | +0.020 | +41.9 | 1.05 | -21.8 | +1.04 |
| Long | 1129 | 53.4 % | +0.037 | +41.8 | 1.10 | -20.5 | +1.42 |
| Short | 938 | 45.9 % | -0.068 | -63.7 | 0.85 | -74.0 | -2.32 |
| 1.ª mitad | 1034 | 49.5 % | -0.027 | -27.5 | 0.94 | -49.9 | -0.95 |
| 2.ª mitad | 1033 | 50.5 % | +0.005 | +5.6 | 1.01 | -32.4 | +0.20 |

Por año (R neto medio y operaciones): 2018 -0.048 (75), 2019 -0.054 (255), 2020 -0.020 (257), 2021 -0.075 (256), 2022 +0.087 (257), 2023 -0.001 (250), 2024 -0.008 (254), 2025 -0.027 (252), 2026 +0.032 (211).

Sensibilidad (R neto medio y t): colchón 0 % -0.016 (t -0.76), colchón 50 % -0.007 (t -0.38), objetivo 1,5:1 -0.009 (t -0.40), objetivo 2:1 +0.008 (t +0.32).

### ORB 12:45–13:15

Rotura con cuerpo desde las 13:15 hasta las 19:15; a esa hora se cierra. ORB completos: 2042; con rotura: 2014.

**No pasa los criterios**. Coste medio 0.029 R; ancho medio del ORB 0.33 %; cómo terminan: objetivo 768, stop 710, por tiempo 536.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2014 | 50.9 % | -0.002 | -3.6 | 1.00 | -46.0 | -0.09 |
| Sin costes | 2014 | 51.3 % | +0.028 | +55.8 | 1.07 | -30.9 | +1.40 |
| Long | 1119 | 52.8 % | +0.020 | +22.9 | 1.05 | -26.1 | +0.78 |
| Short | 895 | 48.5 % | -0.030 | -26.5 | 0.93 | -38.8 | -1.00 |
| 1.ª mitad | 1007 | 52.5 % | +0.017 | +17.1 | 1.04 | -25.0 | +0.60 |
| 2.ª mitad | 1007 | 49.3 % | -0.021 | -20.7 | 0.95 | -46.0 | -0.75 |

Por año (R neto medio y operaciones): 2018 +0.020 (73), 2019 -0.045 (249), 2020 -0.025 (250), 2021 +0.005 (249), 2022 +0.159 (248), 2023 +0.013 (248), 2024 -0.056 (247), 2025 -0.084 (244), 2026 +0.015 (206).

Sensibilidad (R neto medio y t): colchón 0 % -0.002 (t -0.12), colchón 50 % -0.000 (t -0.01), objetivo 1,5:1 +0.008 (t +0.34), objetivo 2:1 +0.006 (t +0.27).

