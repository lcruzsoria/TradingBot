# ORB de 60 min de las 15:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 15:00–16:00 | 1504 | 48.2 | -0.022 | -1.67 | -0.002 | 0.020 | no |
| 15:15–16:15 | 1406 | 47.3 | -0.024 | -1.87 | -0.004 | 0.020 | no |
| 15:30–16:30 | 839 | 46.1 | -0.045 | -2.60 | -0.024 | 0.021 | no |
| 15:45–16:45 | 862 | 46.2 | -0.045 | -2.40 | -0.021 | 0.023 | no |

## Detalle

### ORB 15:00–16:00

Rotura con cuerpo desde las 16:00 hasta las 22:00; a esa hora se cierra. ORB completos: 2024; con rotura: 1504.

**No pasa los criterios**. Coste medio 0.020 R; ancho medio del ORB 0.54 %; cómo terminan: objetivo 126, stop 133, por tiempo 1245.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1504 | 48.2 % | -0.022 | -33.1 | 0.89 | -42.4 | -1.67 |
| Sin costes | 1504 | 50.8 % | -0.002 | -3.1 | 0.99 | -21.7 | -0.16 |
| Long | 829 | 52.4 % | -0.001 | -0.6 | 1.00 | -13.6 | -0.04 |
| Short | 675 | 43.1 % | -0.048 | -32.5 | 0.78 | -37.5 | -2.43 |
| 1.ª mitad | 752 | 51.1 % | -0.001 | -1.0 | 0.99 | -13.7 | -0.07 |
| 2.ª mitad | 752 | 45.3 % | -0.043 | -32.1 | 0.80 | -33.7 | -2.24 |

Por año (R neto medio y operaciones): 2018 -0.049 (52), 2019 +0.026 (209), 2020 -0.026 (193), 2021 +0.030 (173), 2022 -0.058 (175), 2023 -0.059 (152), 2024 +0.011 (174), 2025 -0.033 (195), 2026 -0.068 (181).

Sensibilidad (R neto medio y t): colchón 0 % -0.025 (t -1.75), colchón 50 % -0.020 (t -1.76), objetivo 1,5:1 -0.020 (t -1.43), objetivo 2:1 -0.018 (t -1.28).

### ORB 15:15–16:15

Rotura con cuerpo desde las 16:15 hasta las 22:15; a esa hora se cierra. ORB completos: 2023; con rotura: 1406.

**No pasa los criterios**. Coste medio 0.020 R; ancho medio del ORB 0.55 %; cómo terminan: objetivo 102, stop 104, por tiempo 1200.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1406 | 47.3 % | -0.024 | -33.9 | 0.87 | -48.9 | -1.87 |
| Sin costes | 1406 | 48.9 % | -0.004 | -5.3 | 0.98 | -32.6 | -0.29 |
| Long | 778 | 50.8 % | -0.008 | -6.4 | 0.95 | -17.7 | -0.49 |
| Short | 628 | 43.0 % | -0.044 | -27.5 | 0.79 | -34.5 | -2.20 |
| 1.ª mitad | 703 | 48.6 % | +0.002 | +1.5 | 1.01 | -10.5 | +0.12 |
| 2.ª mitad | 703 | 45.9 % | -0.050 | -35.5 | 0.77 | -42.4 | -2.66 |

Por año (R neto medio y operaciones): 2018 +0.042 (38), 2019 -0.009 (193), 2020 +0.024 (187), 2021 +0.023 (162), 2022 -0.063 (165), 2023 -0.079 (152), 2024 -0.022 (157), 2025 -0.056 (184), 2026 -0.036 (168).

Sensibilidad (R neto medio y t): colchón 0 % -0.029 (t -1.98), colchón 50 % -0.023 (t -2.12), objetivo 1,5:1 -0.025 (t -1.86), objetivo 2:1 -0.022 (t -1.56).

### ORB 15:30–16:30

Rotura con cuerpo desde las 16:30 hasta las 22:30; a esa hora se cierra. ORB completos: 1236; con rotura: 839.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.49 %; cómo terminan: objetivo 61, stop 75, por tiempo 703.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 839 | 46.1 % | -0.045 | -37.8 | 0.79 | -45.1 | -2.60 |
| Sin costes | 839 | 48.3 % | -0.024 | -20.1 | 0.88 | -31.3 | -1.38 |
| Long | 461 | 51.2 % | -0.019 | -8.6 | 0.90 | -15.5 | -0.82 |
| Short | 378 | 39.9 % | -0.077 | -29.2 | 0.67 | -32.1 | -2.93 |
| 1.ª mitad | 420 | 46.9 % | -0.009 | -4.0 | 0.94 | -17.3 | -0.48 |
| 2.ª mitad | 419 | 45.3 % | -0.081 | -33.9 | 0.70 | -39.2 | -2.83 |

Por año (R neto medio y operaciones): 2021 +0.105 (24), 2022 -0.058 (165), 2023 -0.032 (156), 2024 -0.043 (156), 2025 -0.051 (175), 2026 -0.063 (163).

Sensibilidad (R neto medio y t): colchón 0 % -0.052 (t -2.66), colchón 50 % -0.034 (t -2.27), objetivo 1,5:1 -0.040 (t -2.21), objetivo 2:1 -0.039 (t -2.09).

### ORB 15:45–16:45

Rotura con cuerpo desde las 16:45 hasta las 22:45; a esa hora se cierra. ORB completos: 1236; con rotura: 862.

**No pasa los criterios**. Coste medio 0.023 R; ancho medio del ORB 0.45 %; cómo terminan: objetivo 82, stop 100, por tiempo 680.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 862 | 46.2 % | -0.045 | -38.6 | 0.81 | -48.0 | -2.40 |
| Sin costes | 862 | 47.9 % | -0.021 | -18.4 | 0.90 | -34.7 | -1.14 |
| Long | 470 | 50.4 % | -0.029 | -13.6 | 0.86 | -19.7 | -1.20 |
| Short | 392 | 41.1 % | -0.064 | -25.0 | 0.75 | -31.5 | -2.19 |
| 1.ª mitad | 431 | 45.9 % | -0.004 | -1.6 | 0.98 | -15.2 | -0.17 |
| 2.ª mitad | 431 | 46.4 % | -0.086 | -37.0 | 0.71 | -43.3 | -2.86 |

Por año (R neto medio y operaciones): 2021 +0.126 (25), 2022 -0.055 (170), 2023 +0.005 (162), 2024 -0.050 (161), 2025 -0.071 (179), 2026 -0.076 (165).

Sensibilidad (R neto medio y t): colchón 0 % -0.058 (t -2.83), colchón 50 % -0.037 (t -2.34), objetivo 1,5:1 -0.043 (t -2.18), objetivo 2:1 -0.044 (t -2.23).

