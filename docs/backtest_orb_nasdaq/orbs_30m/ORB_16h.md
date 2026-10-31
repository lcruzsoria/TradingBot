# ORB de 30 min de las 16:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 16:00–16:30 | 1028 | 45.9 | -0.098 | -4.11 | -0.054 | 0.044 | no |
| 16:15–16:45 | 1077 | 42.2 | -0.160 | -6.09 | -0.089 | 0.071 | no |
| 16:30–17:00 | 1603 | 45.9 | -0.137 | -5.95 | -0.067 | 0.070 | no |
| 16:45–17:15 | 0 | - | - | - | - | - | no |

## Detalle

### ORB 16:00–16:30

Rotura con cuerpo desde las 16:30 hasta las 22:30; a esa hora se cierra. ORB completos: 1237; con rotura: 1028.

**No pasa los criterios**. Coste medio 0.044 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 224, stop 295, por tiempo 509.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1028 | 45.9 % | -0.098 | -100.5 | 0.74 | -106.8 | -4.11 |
| Sin costes | 1028 | 48.4 % | -0.054 | -55.4 | 0.85 | -66.0 | -2.27 |
| Long | 571 | 49.0 % | -0.070 | -39.9 | 0.81 | -46.1 | -2.19 |
| Short | 457 | 42.0 % | -0.133 | -60.6 | 0.67 | -63.7 | -3.73 |
| 1.ª mitad | 514 | 47.3 % | -0.064 | -32.6 | 0.82 | -45.2 | -1.94 |
| 2.ª mitad | 514 | 44.6 % | -0.132 | -67.9 | 0.68 | -82.8 | -3.83 |

Por año (R neto medio y operaciones): 2021 -0.007 (29), 2022 -0.143 (208), 2023 -0.052 (206), 2024 -0.042 (198), 2025 -0.155 (203), 2026 -0.109 (184).

Sensibilidad (R neto medio y t): colchón 0 % -0.092 (t -3.60), colchón 50 % -0.084 (t -3.88), objetivo 1,5:1 -0.096 (t -3.69), objetivo 2:1 -0.090 (t -3.28).

### ORB 16:15–16:45

Rotura con cuerpo desde las 16:45 hasta las 22:45; a esa hora se cierra. ORB completos: 1238; con rotura: 1077.

**No pasa los criterios**. Coste medio 0.071 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 338, stop 431, por tiempo 308.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1077 | 42.2 % | -0.160 | -172.4 | 0.67 | -178.7 | -6.09 |
| Sin costes | 1077 | 43.4 % | -0.089 | -95.6 | 0.80 | -104.7 | -3.38 |
| Long | 580 | 45.7 % | -0.111 | -64.6 | 0.76 | -69.6 | -3.09 |
| Short | 497 | 38.0 % | -0.217 | -107.8 | 0.57 | -114.0 | -5.67 |
| 1.ª mitad | 539 | 42.1 % | -0.135 | -72.8 | 0.71 | -86.4 | -3.63 |
| 2.ª mitad | 538 | 42.2 % | -0.185 | -99.6 | 0.63 | -103.5 | -4.98 |

Por año (R neto medio y operaciones): 2021 +0.009 (30), 2022 -0.188 (222), 2023 -0.177 (217), 2024 -0.142 (213), 2025 -0.213 (211), 2026 -0.093 (184).

Sensibilidad (R neto medio y t): colchón 0 % -0.162 (t -6.00), colchón 50 % -0.116 (t -4.59), objetivo 1,5:1 -0.148 (t -4.86), objetivo 2:1 -0.156 (t -4.78).

### ORB 16:30–17:00

Rotura con cuerpo desde las 17:00 hasta las 23:00; a esa hora se cierra. ORB completos: 2026; con rotura: 1603.

**No pasa los criterios**. Coste medio 0.070 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 605, stop 714, por tiempo 284.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1603 | 45.9 % | -0.137 | -219.9 | 0.73 | -228.4 | -5.95 |
| Sin costes | 1603 | 46.1 % | -0.067 | -106.9 | 0.86 | -117.5 | -2.90 |
| Long | 860 | 48.8 % | -0.077 | -66.1 | 0.84 | -71.4 | -2.45 |
| Short | 743 | 42.4 % | -0.207 | -153.8 | 0.63 | -161.9 | -6.12 |
| 1.ª mitad | 802 | 46.1 % | -0.133 | -106.3 | 0.74 | -111.7 | -4.03 |
| 2.ª mitad | 801 | 45.6 % | -0.142 | -113.6 | 0.72 | -116.7 | -4.38 |

Por año (R neto medio y operaciones): 2018 +0.030 (56), 2019 -0.155 (193), 2020 -0.105 (201), 2021 -0.144 (200), 2022 -0.186 (197), 2023 -0.192 (196), 2024 -0.079 (196), 2025 -0.166 (196), 2026 -0.115 (168).

Sensibilidad (R neto medio y t): colchón 0 % -0.136 (t -5.77), colchón 50 % -0.117 (t -5.28), objetivo 1,5:1 -0.137 (t -5.17), objetivo 2:1 -0.144 (t -5.06).

### ORB 16:45–17:15

Rotura con cuerpo desde las 17:15 hasta las 23:15; a esa hora se cierra. ORB completos: 0; con rotura: 0.

Sin operaciones.

