# ORB de 60 min de las 16:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 16:00–17:00 | 621 | 48.6 | -0.067 | -2.28 | -0.032 | 0.035 | no |
| 16:15–17:15 | 0 | - | - | - | - | - | no |
| 16:30–17:30 | 0 | - | - | - | - | - | no |
| 16:45–17:45 | 0 | - | - | - | - | - | no |

## Detalle

### ORB 16:00–17:00

Rotura con cuerpo desde las 17:00 hasta las 23:00; a esa hora se cierra. ORB completos: 1237; con rotura: 919.

**No pasa los criterios**. Coste medio 0.035 R; ancho medio del ORB 0.32 %; cómo terminan: objetivo 130, stop 153, por tiempo 338.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 621 | 48.6 % | -0.067 | -41.6 | 0.81 | -49.0 | -2.28 |
| Sin costes | 621 | 49.1 % | -0.032 | -19.8 | 0.90 | -39.9 | -1.08 |
| Long | 372 | 49.2 % | -0.079 | -29.3 | 0.77 | -36.8 | -2.10 |
| Short | 249 | 47.8 % | -0.049 | -12.3 | 0.86 | -16.0 | -1.04 |
| 1.ª mitad | 311 | 52.4 % | +0.011 | +3.3 | 1.04 | -16.5 | +0.27 |
| 2.ª mitad | 310 | 44.8 % | -0.145 | -44.9 | 0.65 | -48.3 | -3.37 |

Por año (R neto medio y operaciones): 2021 +0.031 (19), 2022 -0.067 (110), 2023 -0.012 (111), 2024 +0.012 (122), 2025 -0.125 (144), 2026 -0.148 (115).

Sensibilidad (R neto medio y t): colchón 0 % -0.086 (t -2.68), colchón 50 % -0.057 (t -2.16), objetivo 1,5:1 -0.082 (t -2.58), objetivo 2:1 -0.079 (t -2.41).

### ORB 16:15–17:15

Rotura con cuerpo desde las 17:15 hasta las 23:15; a esa hora se cierra. ORB completos: 0; con rotura: 0.

Sin operaciones.

### ORB 16:30–17:30

Rotura con cuerpo desde las 17:30 hasta las 23:30; a esa hora se cierra. ORB completos: 0; con rotura: 0.

Sin operaciones.

### ORB 16:45–17:45

Rotura con cuerpo desde las 17:45 hasta las 23:45; a esa hora se cierra. ORB completos: 0; con rotura: 0.

Sin operaciones.

