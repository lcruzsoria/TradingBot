# ORB de 30 min de las 16:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 16:00–16:30 | 668 | 46.4 | -0.088 | -3.08 | -0.046 | 0.042 | no |
| 16:15–16:45 | 642 | 42.8 | -0.141 | -4.24 | -0.076 | 0.066 | no |
| 16:30–17:00 | 933 | 50.9 | -0.037 | -1.23 | +0.029 | 0.066 | no |
| 16:45–17:15 | 0 | - | - | - | - | - | no |

## Detalle

### ORB 16:00–16:30

Rotura con cuerpo desde las 16:30 hasta las 22:30; a esa hora se cierra. ORB completos: 1237; con rotura: 1028.

**No pasa los criterios**. Coste medio 0.042 R; ancho medio del ORB 0.28 %; cómo terminan: objetivo 135, stop 175, por tiempo 358.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 668 | 46.4 % | -0.088 | -58.6 | 0.75 | -63.3 | -3.08 |
| Sin costes | 668 | 48.7 % | -0.046 | -30.8 | 0.86 | -42.4 | -1.62 |
| Long | 391 | 48.8 % | -0.069 | -26.9 | 0.80 | -29.5 | -1.85 |
| Short | 277 | 43.0 % | -0.115 | -31.8 | 0.69 | -34.9 | -2.58 |
| 1.ª mitad | 334 | 49.7 % | -0.031 | -10.4 | 0.90 | -26.3 | -0.79 |
| 2.ª mitad | 334 | 43.1 % | -0.144 | -48.2 | 0.64 | -53.3 | -3.50 |

Por año (R neto medio y operaciones): 2021 -0.050 (21), 2022 -0.101 (118), 2023 -0.069 (130), 2024 -0.005 (129), 2025 -0.153 (152), 2026 -0.108 (118).

Sensibilidad (R neto medio y t): colchón 0 % -0.084 (t -2.74), colchón 50 % -0.068 (t -2.62), objetivo 1,5:1 -0.071 (t -2.24), objetivo 2:1 -0.071 (t -2.11).

### ORB 16:15–16:45

Rotura con cuerpo desde las 16:45 hasta las 22:45; a esa hora se cierra. ORB completos: 1238; con rotura: 1077.

**No pasa los criterios**. Coste medio 0.066 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 194, stop 240, por tiempo 208.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 642 | 42.8 % | -0.141 | -90.7 | 0.69 | -97.2 | -4.24 |
| Sin costes | 642 | 43.8 % | -0.076 | -48.5 | 0.82 | -56.9 | -2.27 |
| Long | 372 | 44.6 % | -0.129 | -48.0 | 0.71 | -51.0 | -2.95 |
| Short | 270 | 40.4 % | -0.158 | -42.7 | 0.66 | -48.8 | -3.07 |
| 1.ª mitad | 321 | 43.6 % | -0.100 | -31.9 | 0.76 | -45.1 | -2.14 |
| 2.ª mitad | 321 | 42.1 % | -0.183 | -58.8 | 0.62 | -62.2 | -3.86 |

Por año (R neto medio y operaciones): 2021 +0.077 (15), 2022 -0.165 (118), 2023 -0.187 (118), 2024 -0.103 (127), 2025 -0.181 (145), 2026 -0.092 (119).

Sensibilidad (R neto medio y t): colchón 0 % -0.129 (t -3.76), colchón 50 % -0.096 (t -3.02), objetivo 1,5:1 -0.129 (t -3.35), objetivo 2:1 -0.133 (t -3.20).

### ORB 16:30–17:00

Rotura con cuerpo desde las 17:00 hasta las 23:00; a esa hora se cierra. ORB completos: 2026; con rotura: 1603.

**No pasa los criterios**. Coste medio 0.066 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 378, stop 358, por tiempo 197.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 933 | 50.9 % | -0.037 | -34.1 | 0.92 | -44.9 | -1.23 |
| Sin costes | 933 | 51.3 % | +0.029 | +27.5 | 1.07 | -19.0 | +0.99 |
| Long | 546 | 54.0 % | +0.027 | +14.8 | 1.07 | -11.0 | +0.70 |
| Short | 387 | 46.5 % | -0.126 | -48.9 | 0.75 | -55.6 | -2.72 |
| 1.ª mitad | 467 | 50.1 % | -0.047 | -22.1 | 0.90 | -30.0 | -1.12 |
| 2.ª mitad | 466 | 51.7 % | -0.026 | -12.0 | 0.94 | -19.6 | -0.61 |

Por año (R neto medio y operaciones): 2018 -0.013 (31), 2019 -0.108 (111), 2020 -0.009 (114), 2021 +0.052 (97), 2022 -0.110 (115), 2023 -0.138 (107), 2024 +0.024 (124), 2025 +0.021 (124), 2026 -0.034 (110).

Sensibilidad (R neto medio y t): colchón 0 % -0.029 (t -0.95), colchón 50 % -0.033 (t -1.13), objetivo 1,5:1 -0.026 (t -0.75), objetivo 2:1 -0.054 (t -1.44).

### ORB 16:45–17:15

Rotura con cuerpo desde las 17:15 hasta las 23:15; a esa hora se cierra. ORB completos: 0; con rotura: 0.

Sin operaciones.

