# ORB de 30 min de las 11:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 11:00–11:30 | 2075 | 49.6 | -0.021 | -1.09 | +0.003 | 0.023 | no |
| 11:15–11:45 | 2079 | 49.2 | -0.024 | -1.28 | +0.001 | 0.025 | no |
| 11:30–12:00 | 2072 | 49.6 | -0.030 | -1.55 | -0.004 | 0.026 | no |
| 11:45–12:15 | 2077 | 48.7 | -0.037 | -1.87 | -0.009 | 0.027 | no |

## Detalle

### ORB 11:00–11:30

Rotura con cuerpo desde las 11:30 hasta las 17:30; a esa hora se cierra. ORB completos: 2097; con rotura: 2075.

**No pasa los criterios**. Coste medio 0.023 R; ancho medio del ORB 0.42 %; cómo terminan: objetivo 705, stop 706, por tiempo 664.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2075 | 49.6 % | -0.021 | -42.8 | 0.95 | -71.9 | -1.09 |
| Sin costes | 2075 | 50.3 % | +0.003 | +5.7 | 1.01 | -37.1 | +0.15 |
| Long | 1144 | 51.7 % | +0.006 | +6.5 | 1.01 | -25.7 | +0.23 |
| Short | 931 | 47.2 % | -0.053 | -49.2 | 0.88 | -61.8 | -1.84 |
| 1.ª mitad | 1038 | 51.7 % | +0.011 | +11.4 | 1.03 | -21.3 | +0.41 |
| 2.ª mitad | 1037 | 47.5 % | -0.052 | -54.1 | 0.88 | -59.4 | -1.95 |

Por año (R neto medio y operaciones): 2018 +0.019 (76), 2019 -0.042 (257), 2020 +0.125 (258), 2021 -0.049 (257), 2022 -0.022 (255), 2023 -0.039 (257), 2024 -0.046 (257), 2025 -0.010 (249), 2026 -0.111 (209).

Sensibilidad (R neto medio y t): colchón 0 % -0.017 (t -0.85), colchón 50 % -0.010 (t -0.54), objetivo 1,5:1 -0.009 (t -0.41), objetivo 2:1 -0.001 (t -0.02).

### ORB 11:15–11:45

Rotura con cuerpo desde las 11:45 hasta las 17:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2079.

**No pasa los criterios**. Coste medio 0.025 R; ancho medio del ORB 0.40 %; cómo terminan: objetivo 730, stop 730, por tiempo 619.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2079 | 49.2 % | -0.024 | -50.8 | 0.94 | -61.3 | -1.28 |
| Sin costes | 2079 | 49.7 % | +0.001 | +1.3 | 1.00 | -28.5 | +0.03 |
| Long | 1148 | 50.3 % | -0.009 | -9.9 | 0.98 | -34.4 | -0.34 |
| Short | 931 | 47.7 % | -0.044 | -40.9 | 0.90 | -54.9 | -1.52 |
| 1.ª mitad | 1040 | 49.7 % | -0.024 | -24.6 | 0.94 | -37.6 | -0.87 |
| 2.ª mitad | 1039 | 48.6 % | -0.025 | -26.2 | 0.94 | -38.0 | -0.94 |

Por año (R neto medio y operaciones): 2018 -0.023 (76), 2019 -0.082 (256), 2020 +0.071 (257), 2021 -0.035 (257), 2022 -0.041 (257), 2023 -0.015 (255), 2024 -0.013 (256), 2025 +0.007 (253), 2026 -0.101 (212).

Sensibilidad (R neto medio y t): colchón 0 % -0.031 (t -1.57), colchón 50 % -0.001 (t -0.08), objetivo 1,5:1 -0.006 (t -0.29), objetivo 2:1 -0.006 (t -0.27).

### ORB 11:30–12:00

Rotura con cuerpo desde las 12:00 hasta las 18:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2072.

**No pasa los criterios**. Coste medio 0.026 R; ancho medio del ORB 0.38 %; cómo terminan: objetivo 729, stop 743, por tiempo 600.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2072 | 49.6 % | -0.030 | -61.7 | 0.93 | -74.2 | -1.55 |
| Sin costes | 2072 | 50.0 % | -0.004 | -7.6 | 0.99 | -38.8 | -0.19 |
| Long | 1092 | 52.4 % | +0.005 | +5.6 | 1.01 | -22.3 | +0.20 |
| Short | 980 | 46.5 % | -0.069 | -67.3 | 0.85 | -77.2 | -2.43 |
| 1.ª mitad | 1036 | 50.5 % | -0.028 | -28.5 | 0.94 | -38.4 | -1.00 |
| 2.ª mitad | 1036 | 48.7 % | -0.032 | -33.2 | 0.92 | -49.7 | -1.20 |

Por año (R neto medio y operaciones): 2018 -0.048 (75), 2019 -0.082 (254), 2020 +0.100 (258), 2021 -0.078 (255), 2022 -0.045 (257), 2023 -0.067 (255), 2024 +0.013 (253), 2025 -0.039 (253), 2026 -0.037 (212).

Sensibilidad (R neto medio y t): colchón 0 % -0.029 (t -1.43), colchón 50 % -0.015 (t -0.81), objetivo 1,5:1 -0.018 (t -0.83), objetivo 2:1 -0.007 (t -0.30).

### ORB 11:45–12:15

Rotura con cuerpo desde las 12:15 hasta las 18:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2077.

**No pasa los criterios**. Coste medio 0.027 R; ancho medio del ORB 0.36 %; cómo terminan: objetivo 761, stop 792, por tiempo 524.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2077 | 48.7 % | -0.037 | -75.9 | 0.92 | -92.1 | -1.87 |
| Sin costes | 2077 | 49.3 % | -0.009 | -18.8 | 0.98 | -50.1 | -0.46 |
| Long | 1118 | 50.4 % | -0.016 | -17.8 | 0.96 | -37.1 | -0.61 |
| Short | 959 | 46.7 % | -0.061 | -58.0 | 0.87 | -77.3 | -2.08 |
| 1.ª mitad | 1039 | 47.8 % | -0.056 | -58.4 | 0.88 | -63.1 | -2.00 |
| 2.ª mitad | 1038 | 49.5 % | -0.017 | -17.5 | 0.96 | -39.4 | -0.62 |

Por año (R neto medio y operaciones): 2018 -0.029 (76), 2019 -0.054 (256), 2020 +0.040 (259), 2021 -0.100 (257), 2022 -0.098 (257), 2023 -0.030 (254), 2024 -0.021 (256), 2025 -0.007 (251), 2026 -0.021 (211).

Sensibilidad (R neto medio y t): colchón 0 % -0.028 (t -1.40), colchón 50 % -0.025 (t -1.35), objetivo 1,5:1 -0.039 (t -1.78), objetivo 2:1 -0.025 (t -1.03).

