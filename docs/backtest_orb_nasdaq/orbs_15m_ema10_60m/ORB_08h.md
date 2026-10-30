# ORB de 15 min de las 08:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 08:00–08:15 | 1456 | 50.3 | -0.052 | -1.98 | +0.004 | 0.056 | no |
| 08:15–08:30 | 1473 | 48.9 | -0.075 | -2.90 | -0.021 | 0.053 | no |
| 08:30–08:45 | 1521 | 46.7 | -0.110 | -4.44 | -0.068 | 0.042 | no |
| 08:45–09:00 | 1447 | 47.8 | -0.096 | -3.67 | -0.044 | 0.051 | no |

## Detalle

### ORB 08:00–08:15

Rotura con cuerpo desde las 08:15 hasta las 14:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2095.

**No pasa los criterios**. Coste medio 0.056 R; ancho medio del ORB 0.17 %; cómo terminan: objetivo 721, stop 717, por tiempo 18.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1456 | 50.3 % | -0.052 | -75.3 | 0.90 | -101.0 | -1.98 |
| Sin costes | 1456 | 50.3 % | +0.004 | +6.0 | 1.01 | -55.6 | +0.16 |
| Long | 795 | 50.1 % | -0.062 | -49.3 | 0.88 | -57.5 | -1.75 |
| Short | 661 | 50.5 % | -0.039 | -26.0 | 0.92 | -49.3 | -1.02 |
| 1.ª mitad | 728 | 51.4 % | -0.035 | -25.1 | 0.93 | -37.0 | -0.94 |
| 2.ª mitad | 728 | 49.2 % | -0.069 | -50.1 | 0.87 | -79.5 | -1.86 |

Por año (R neto medio y operaciones): 2018 -0.111 (55), 2019 -0.033 (176), 2020 -0.060 (173), 2021 -0.058 (175), 2022 +0.071 (168), 2023 -0.109 (178), 2024 -0.178 (195), 2025 -0.106 (188), 2026 +0.129 (148).

Sensibilidad (R neto medio y t): colchón 0 % -0.067 (t -2.58), colchón 50 % -0.039 (t -1.49), objetivo 1,5:1 -0.053 (t -1.67), objetivo 2:1 -0.071 (t -1.97).

### ORB 08:15–08:30

Rotura con cuerpo desde las 08:30 hasta las 14:30; a esa hora se cierra. ORB completos: 2095; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.053 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 700, stop 731, por tiempo 42.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1473 | 48.9 % | -0.075 | -110.4 | 0.86 | -119.3 | -2.90 |
| Sin costes | 1473 | 48.9 % | -0.021 | -31.7 | 0.96 | -58.7 | -0.83 |
| Long | 782 | 49.1 % | -0.083 | -64.6 | 0.85 | -71.4 | -2.33 |
| Short | 691 | 48.8 % | -0.066 | -45.8 | 0.87 | -57.4 | -1.76 |
| 1.ª mitad | 737 | 47.8 % | -0.107 | -78.6 | 0.81 | -95.4 | -2.92 |
| 2.ª mitad | 736 | 50.1 % | -0.043 | -31.8 | 0.92 | -46.2 | -1.19 |

Por año (R neto medio y operaciones): 2018 +0.047 (43), 2019 -0.183 (188), 2020 -0.098 (177), 2021 -0.180 (184), 2022 +0.009 (181), 2023 +0.036 (185), 2024 -0.007 (196), 2025 -0.123 (169), 2026 -0.092 (150).

Sensibilidad (R neto medio y t): colchón 0 % -0.054 (t -2.08), colchón 50 % -0.049 (t -1.90), objetivo 1,5:1 -0.082 (t -2.63), objetivo 2:1 -0.069 (t -1.94).

### ORB 08:30–08:45

Rotura con cuerpo desde las 08:45 hasta las 14:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2089.

**No pasa los criterios**. Coste medio 0.042 R; ancho medio del ORB 0.29 %; cómo terminan: objetivo 641, stop 752, por tiempo 128.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1521 | 46.7 % | -0.110 | -166.6 | 0.79 | -170.4 | -4.44 |
| Sin costes | 1521 | 46.9 % | -0.068 | -103.3 | 0.87 | -108.9 | -2.75 |
| Long | 810 | 45.3 % | -0.143 | -115.5 | 0.74 | -115.5 | -4.22 |
| Short | 711 | 48.2 % | -0.072 | -51.1 | 0.86 | -59.3 | -1.99 |
| 1.ª mitad | 761 | 46.1 % | -0.123 | -93.5 | 0.77 | -97.3 | -3.49 |
| 2.ª mitad | 760 | 47.2 % | -0.096 | -73.2 | 0.81 | -75.2 | -2.78 |

Por año (R neto medio y operaciones): 2018 -0.077 (48), 2019 -0.161 (181), 2020 -0.176 (182), 2021 -0.064 (174), 2022 -0.082 (197), 2023 -0.096 (201), 2024 -0.061 (196), 2025 -0.077 (192), 2026 -0.189 (150).

Sensibilidad (R neto medio y t): colchón 0 % -0.109 (t -4.36), colchón 50 % -0.071 (t -2.90), objetivo 1,5:1 -0.130 (t -4.46), objetivo 2:1 -0.109 (t -3.30).

### ORB 08:45–09:00

Rotura con cuerpo desde las 09:00 hasta las 15:00; a esa hora se cierra. ORB completos: 2095; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.051 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 674, stop 740, por tiempo 33.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1447 | 47.8 % | -0.096 | -138.4 | 0.82 | -155.6 | -3.67 |
| Sin costes | 1447 | 47.8 % | -0.044 | -64.0 | 0.91 | -84.6 | -1.70 |
| Long | 775 | 48.4 % | -0.088 | -68.5 | 0.84 | -75.9 | -2.48 |
| Short | 672 | 47.0 % | -0.104 | -69.8 | 0.81 | -86.5 | -2.71 |
| 1.ª mitad | 724 | 48.9 % | -0.077 | -55.5 | 0.86 | -74.2 | -2.08 |
| 2.ª mitad | 723 | 46.6 % | -0.115 | -82.8 | 0.79 | -95.5 | -3.11 |

Por año (R neto medio y operaciones): 2018 -0.158 (52), 2019 -0.056 (178), 2020 -0.116 (173), 2021 -0.065 (177), 2022 -0.043 (169), 2023 -0.167 (178), 2024 -0.140 (181), 2025 -0.139 (193), 2026 +0.003 (146).

Sensibilidad (R neto medio y t): colchón 0 % -0.124 (t -4.76), colchón 50 % -0.043 (t -1.67), objetivo 1,5:1 -0.106 (t -3.39), objetivo 2:1 -0.095 (t -2.67).

