# ORB de 45 min de las 01:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 01:00–01:45 | 1546 | 50.8 | -0.041 | -1.68 | +0.016 | 0.057 | no |
| 01:15–02:00 | 1522 | 50.7 | -0.043 | -1.76 | +0.014 | 0.057 | no |
| 01:30–02:15 | 1607 | 49.2 | -0.050 | -2.15 | -0.001 | 0.049 | no |
| 01:45–02:30 | 1605 | 48.8 | -0.061 | -2.64 | -0.014 | 0.047 | no |

## Detalle

### ORB 01:00–01:45

Rotura con cuerpo desde las 01:45 hasta las 07:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.057 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 692, stop 671, por tiempo 183.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1546 | 50.8 % | -0.041 | -62.8 | 0.92 | -84.3 | -1.68 |
| Sin costes | 1546 | 51.1 % | +0.016 | +25.0 | 1.04 | -34.6 | +0.67 |
| Long | 886 | 53.6 % | -0.002 | -2.1 | 0.99 | -29.7 | -0.08 |
| Short | 660 | 47.0 % | -0.092 | -60.6 | 0.82 | -71.9 | -2.47 |
| 1.ª mitad | 773 | 49.9 % | -0.052 | -40.5 | 0.89 | -60.7 | -1.53 |
| 2.ª mitad | 773 | 51.6 % | -0.029 | -22.2 | 0.94 | -49.7 | -0.84 |

Por año (R neto medio y operaciones): 2018 -0.039 (55), 2019 -0.095 (179), 2020 +0.029 (185), 2021 -0.118 (187), 2022 -0.054 (185), 2023 +0.020 (198), 2024 -0.073 (196), 2025 -0.083 (195), 2026 +0.058 (166).

Sensibilidad (R neto medio y t): colchón 0 % -0.020 (t -0.82), colchón 50 % -0.040 (t -1.73), objetivo 1,5:1 -0.038 (t -1.35), objetivo 2:1 -0.037 (t -1.19).

### ORB 01:15–02:00

Rotura con cuerpo desde las 02:00 hasta las 08:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.057 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 692, stop 665, por tiempo 165.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1522 | 50.7 % | -0.043 | -65.5 | 0.91 | -81.0 | -1.76 |
| Sin costes | 1522 | 50.9 % | +0.014 | +21.1 | 1.03 | -35.8 | +0.57 |
| Long | 860 | 53.7 % | -0.001 | -0.5 | 1.00 | -23.8 | -0.02 |
| Short | 662 | 46.8 % | -0.098 | -65.0 | 0.81 | -67.9 | -2.61 |
| 1.ª mitad | 761 | 49.3 % | -0.072 | -55.1 | 0.86 | -72.4 | -2.09 |
| 2.ª mitad | 761 | 52.2 % | -0.014 | -10.4 | 0.97 | -22.8 | -0.39 |

Por año (R neto medio y operaciones): 2018 +0.080 (58), 2019 -0.136 (168), 2020 -0.010 (180), 2021 -0.075 (185), 2022 -0.125 (186), 2023 -0.007 (197), 2024 +0.025 (189), 2025 -0.044 (197), 2026 -0.019 (162).

Sensibilidad (R neto medio y t): colchón 0 % -0.060 (t -2.40), colchón 50 % -0.029 (t -1.21), objetivo 1,5:1 -0.030 (t -1.03), objetivo 2:1 -0.043 (t -1.37).

### ORB 01:30–02:15

Rotura con cuerpo desde las 02:15 hasta las 08:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.049 R; ancho medio del ORB 0.21 %; cómo terminan: objetivo 671, stop 668, por tiempo 268.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1607 | 49.2 % | -0.050 | -80.3 | 0.89 | -108.3 | -2.15 |
| Sin costes | 1607 | 49.6 % | -0.001 | -1.1 | 1.00 | -50.1 | -0.03 |
| Long | 926 | 50.3 % | -0.036 | -33.5 | 0.92 | -47.7 | -1.19 |
| Short | 681 | 47.7 % | -0.069 | -46.9 | 0.86 | -64.2 | -1.91 |
| 1.ª mitad | 804 | 47.0 % | -0.085 | -68.1 | 0.82 | -81.0 | -2.61 |
| 2.ª mitad | 803 | 51.4 % | -0.015 | -12.2 | 0.97 | -44.2 | -0.46 |

Por año (R neto medio y operaciones): 2018 +0.172 (59), 2019 -0.171 (194), 2020 -0.036 (184), 2021 -0.068 (202), 2022 -0.142 (207), 2023 +0.063 (205), 2024 -0.055 (202), 2025 -0.059 (201), 2026 +0.018 (153).

Sensibilidad (R neto medio y t): colchón 0 % -0.052 (t -2.18), colchón 50 % -0.037 (t -1.69), objetivo 1,5:1 -0.044 (t -1.62), objetivo 2:1 -0.059 (t -2.03).

### ORB 01:45–02:30

Rotura con cuerpo desde las 02:30 hasta las 08:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.047 R; ancho medio del ORB 0.22 %; cómo terminan: objetivo 657, stop 679, por tiempo 269.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1605 | 48.8 % | -0.061 | -98.3 | 0.87 | -124.4 | -2.64 |
| Sin costes | 1605 | 49.2 % | -0.014 | -22.5 | 0.97 | -56.4 | -0.61 |
| Long | 909 | 51.0 % | -0.031 | -27.8 | 0.93 | -52.0 | -1.00 |
| Short | 696 | 46.0 % | -0.101 | -70.5 | 0.80 | -82.1 | -2.86 |
| 1.ª mitad | 803 | 48.1 % | -0.072 | -58.0 | 0.85 | -72.3 | -2.24 |
| 2.ª mitad | 802 | 49.6 % | -0.050 | -40.2 | 0.90 | -55.8 | -1.51 |

Por año (R neto medio y operaciones): 2018 +0.111 (60), 2019 -0.171 (194), 2020 -0.006 (187), 2021 -0.111 (212), 2022 -0.109 (202), 2023 -0.072 (202), 2024 -0.037 (198), 2025 -0.088 (189), 2026 +0.082 (161).

Sensibilidad (R neto medio y t): colchón 0 % -0.077 (t -3.24), colchón 50 % -0.032 (t -1.44), objetivo 1,5:1 -0.049 (t -1.83), objetivo 2:1 -0.048 (t -1.64).

