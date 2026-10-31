# ORB de 45 min de las 16:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 16:00–16:45 | 657 | 45.8 | -0.084 | -2.96 | -0.045 | 0.038 | no |
| 16:15–17:00 | 610 | 46.9 | -0.091 | -2.63 | -0.038 | 0.053 | no |
| 16:30–17:15 | 0 | - | - | - | - | - | no |
| 16:45–17:30 | 0 | - | - | - | - | - | no |

## Detalle

### ORB 16:00–16:45

Rotura con cuerpo desde las 16:45 hasta las 22:45; a esa hora se cierra. ORB completos: 1237; con rotura: 987.

**No pasa los criterios**. Coste medio 0.038 R; ancho medio del ORB 0.30 %; cómo terminan: objetivo 130, stop 164, por tiempo 363.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 657 | 45.8 % | -0.084 | -55.1 | 0.76 | -58.9 | -2.96 |
| Sin costes | 657 | 47.2 % | -0.045 | -29.9 | 0.86 | -38.8 | -1.60 |
| Long | 384 | 48.2 % | -0.075 | -28.6 | 0.78 | -32.2 | -2.01 |
| Short | 273 | 42.5 % | -0.097 | -26.5 | 0.73 | -29.3 | -2.19 |
| 1.ª mitad | 329 | 47.7 % | -0.023 | -7.5 | 0.92 | -26.7 | -0.58 |
| 2.ª mitad | 328 | 43.9 % | -0.145 | -47.6 | 0.64 | -48.9 | -3.53 |

Por año (R neto medio y operaciones): 2021 +0.064 (19), 2022 -0.124 (112), 2023 -0.075 (126), 2024 +0.016 (126), 2025 -0.132 (153), 2026 -0.121 (121).

Sensibilidad (R neto medio y t): colchón 0 % -0.099 (t -3.22), colchón 50 % -0.066 (t -2.57), objetivo 1,5:1 -0.074 (t -2.36), objetivo 2:1 -0.082 (t -2.52).

### ORB 16:15–17:00

Rotura con cuerpo desde las 17:00 hasta las 23:00; a esa hora se cierra. ORB completos: 1238; con rotura: 963.

**No pasa los criterios**. Coste medio 0.053 R; ancho medio del ORB 0.21 %; cómo terminan: objetivo 200, stop 217, por tiempo 193.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 610 | 46.9 % | -0.091 | -55.5 | 0.79 | -64.9 | -2.63 |
| Sin costes | 610 | 47.2 % | -0.038 | -23.3 | 0.91 | -39.5 | -1.11 |
| Long | 369 | 47.7 % | -0.087 | -31.9 | 0.80 | -34.1 | -1.96 |
| Short | 241 | 45.6 % | -0.098 | -23.6 | 0.78 | -36.4 | -1.75 |
| 1.ª mitad | 305 | 49.5 % | -0.025 | -7.7 | 0.94 | -26.2 | -0.52 |
| 2.ª mitad | 305 | 44.3 % | -0.157 | -47.9 | 0.67 | -50.5 | -3.19 |

Por año (R neto medio y operaciones): 2021 -0.102 (16), 2022 -0.065 (115), 2023 -0.058 (106), 2024 -0.082 (127), 2025 -0.137 (134), 2026 -0.103 (112).

Sensibilidad (R neto medio y t): colchón 0 % -0.103 (t -2.85), colchón 50 % -0.076 (t -2.31), objetivo 1,5:1 -0.083 (t -2.10), objetivo 2:1 -0.080 (t -1.91).

### ORB 16:30–17:15

Rotura con cuerpo desde las 17:15 hasta las 23:15; a esa hora se cierra. ORB completos: 0; con rotura: 0.

Sin operaciones.

### ORB 16:45–17:30

Rotura con cuerpo desde las 17:30 hasta las 23:30; a esa hora se cierra. ORB completos: 0; con rotura: 0.

Sin operaciones.

