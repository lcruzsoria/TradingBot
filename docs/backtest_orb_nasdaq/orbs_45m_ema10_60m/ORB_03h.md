# ORB de 45 min de las 03:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 03:00–03:45 | 1747 | 49.6 | -0.035 | -1.63 | -0.002 | 0.034 | no |
| 03:15–04:00 | 1695 | 49.1 | -0.045 | -1.98 | -0.009 | 0.037 | no |
| 03:30–04:15 | 1690 | 48.7 | -0.062 | -2.68 | -0.027 | 0.036 | no |
| 03:45–04:30 | 1658 | 50.5 | -0.026 | -1.10 | +0.010 | 0.036 | no |

## Detalle

### ORB 03:00–03:45

Rotura con cuerpo desde las 03:45 hasta las 09:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.034 R; ancho medio del ORB 0.32 %; cómo terminan: objetivo 687, stop 688, por tiempo 372.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1747 | 49.6 % | -0.035 | -61.8 | 0.92 | -80.8 | -1.63 |
| Sin costes | 1747 | 49.7 % | -0.002 | -3.2 | 1.00 | -46.4 | -0.08 |
| Long | 994 | 50.5 % | -0.024 | -23.5 | 0.95 | -43.9 | -0.82 |
| Short | 753 | 48.3 % | -0.051 | -38.3 | 0.89 | -53.5 | -1.53 |
| 1.ª mitad | 874 | 49.5 % | -0.038 | -32.8 | 0.91 | -61.1 | -1.26 |
| 2.ª mitad | 873 | 49.6 % | -0.033 | -28.9 | 0.93 | -38.1 | -1.05 |

Por año (R neto medio y operaciones): 2018 +0.079 (61), 2019 -0.129 (210), 2020 -0.082 (218), 2021 -0.003 (217), 2022 -0.007 (230), 2023 -0.030 (213), 2024 +0.017 (209), 2025 -0.069 (213), 2026 -0.009 (176).

Sensibilidad (R neto medio y t): colchón 0 % -0.066 (t -2.96), colchón 50 % -0.025 (t -1.24), objetivo 1,5:1 -0.004 (t -0.15), objetivo 2:1 -0.013 (t -0.47).

### ORB 03:15–04:00

Rotura con cuerpo desde las 04:00 hasta las 10:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.037 R; ancho medio del ORB 0.29 %; cómo terminan: objetivo 731, stop 750, por tiempo 214.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1695 | 49.1 % | -0.045 | -77.1 | 0.91 | -87.5 | -1.98 |
| Sin costes | 1695 | 49.4 % | -0.009 | -15.1 | 0.98 | -54.6 | -0.39 |
| Long | 954 | 49.4 % | -0.042 | -40.4 | 0.91 | -51.6 | -1.39 |
| Short | 741 | 48.7 % | -0.050 | -36.7 | 0.90 | -55.8 | -1.41 |
| 1.ª mitad | 848 | 47.9 % | -0.076 | -64.6 | 0.84 | -72.7 | -2.39 |
| 2.ª mitad | 847 | 50.3 % | -0.015 | -12.5 | 0.97 | -33.9 | -0.44 |

Por año (R neto medio y operaciones): 2018 +0.069 (59), 2019 -0.134 (205), 2020 -0.154 (206), 2021 -0.024 (209), 2022 -0.008 (219), 2023 -0.016 (205), 2024 +0.071 (205), 2025 -0.053 (208), 2026 -0.086 (179).

Sensibilidad (R neto medio y t): colchón 0 % -0.065 (t -2.76), colchón 50 % -0.036 (t -1.61), objetivo 1,5:1 -0.036 (t -1.35), objetivo 2:1 -0.033 (t -1.10).

### ORB 03:30–04:15

Rotura con cuerpo desde las 04:15 hasta las 10:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.036 R; ancho medio del ORB 0.29 %; cómo terminan: objetivo 736, stop 779, por tiempo 175.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1690 | 48.7 % | -0.062 | -105.4 | 0.87 | -115.5 | -2.68 |
| Sin costes | 1690 | 48.7 % | -0.027 | -45.1 | 0.94 | -62.2 | -1.15 |
| Long | 947 | 50.5 % | -0.030 | -28.5 | 0.94 | -39.2 | -0.97 |
| Short | 743 | 46.4 % | -0.103 | -76.9 | 0.80 | -84.2 | -2.94 |
| 1.ª mitad | 845 | 49.0 % | -0.066 | -55.5 | 0.87 | -63.3 | -2.02 |
| 2.ª mitad | 845 | 48.4 % | -0.059 | -49.9 | 0.88 | -55.2 | -1.77 |

Por año (R neto medio y operaciones): 2018 +0.006 (60), 2019 -0.079 (212), 2020 -0.115 (199), 2021 -0.022 (201), 2022 -0.083 (218), 2023 -0.123 (213), 2024 +0.043 (210), 2025 -0.021 (209), 2026 -0.131 (168).

Sensibilidad (R neto medio y t): colchón 0 % -0.045 (t -1.89), colchón 50 % -0.055 (t -2.44), objetivo 1,5:1 -0.076 (t -2.81), objetivo 2:1 -0.072 (t -2.39).

### ORB 03:45–04:30

Rotura con cuerpo desde las 04:30 hasta las 10:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.036 R; ancho medio del ORB 0.29 %; cómo terminan: objetivo 757, stop 749, por tiempo 152.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1658 | 50.5 % | -0.026 | -43.2 | 0.95 | -83.4 | -1.10 |
| Sin costes | 1658 | 50.6 % | +0.010 | +16.5 | 1.02 | -45.7 | +0.42 |
| Long | 925 | 51.8 % | -0.011 | -10.2 | 0.98 | -28.2 | -0.35 |
| Short | 733 | 49.0 % | -0.045 | -33.0 | 0.91 | -70.7 | -1.26 |
| 1.ª mitad | 829 | 49.1 % | -0.065 | -54.0 | 0.87 | -62.9 | -1.94 |
| 2.ª mitad | 829 | 52.0 % | +0.013 | +10.8 | 1.03 | -28.5 | +0.39 |

Por año (R neto medio y operaciones): 2018 -0.062 (58), 2019 -0.112 (213), 2020 -0.118 (196), 2021 -0.044 (201), 2022 +0.005 (217), 2023 -0.115 (203), 2024 +0.167 (209), 2025 +0.072 (200), 2026 -0.067 (161).

Sensibilidad (R neto medio y t): colchón 0 % -0.027 (t -1.14), colchón 50 % -0.035 (t -1.52), objetivo 1,5:1 -0.023 (t -0.82), objetivo 2:1 -0.030 (t -0.97).

