# ORB de 45 min de las 08:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 08:00–08:45 | 1723 | 47.7 | -0.068 | -2.97 | -0.040 | 0.028 | no |
| 08:15–09:00 | 1746 | 48.1 | -0.062 | -2.74 | -0.035 | 0.026 | no |
| 08:30–09:15 | 1750 | 48.2 | -0.057 | -2.53 | -0.032 | 0.025 | no |
| 08:45–09:30 | 1712 | 51.2 | -0.000 | -0.01 | +0.024 | 0.024 | no |

## Detalle

### ORB 08:00–08:45

Rotura con cuerpo desde las 08:45 hasta las 14:45; a esa hora se cierra. ORB completos: 2095; con rotura: 2084.

**No pasa los criterios**. Coste medio 0.028 R; ancho medio del ORB 0.39 %; cómo terminan: objetivo 712, stop 781, por tiempo 230.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1723 | 47.7 % | -0.068 | -116.5 | 0.86 | -123.7 | -2.97 |
| Sin costes | 1723 | 47.9 % | -0.040 | -68.7 | 0.92 | -76.7 | -1.75 |
| Long | 880 | 48.2 % | -0.069 | -60.4 | 0.86 | -63.9 | -2.15 |
| Short | 843 | 47.2 % | -0.067 | -56.1 | 0.86 | -67.3 | -2.05 |
| 1.ª mitad | 862 | 48.0 % | -0.057 | -48.7 | 0.89 | -67.3 | -1.74 |
| 2.ª mitad | 861 | 47.4 % | -0.079 | -67.7 | 0.84 | -74.5 | -2.47 |

Por año (R neto medio y operaciones): 2018 -0.010 (51), 2019 -0.092 (215), 2020 -0.114 (210), 2021 -0.044 (205), 2022 +0.035 (216), 2023 -0.093 (218), 2024 -0.113 (222), 2025 -0.026 (213), 2026 -0.115 (173).

Sensibilidad (R neto medio y t): colchón 0 % -0.065 (t -2.82), colchón 50 % -0.062 (t -2.82), objetivo 1,5:1 -0.083 (t -3.12), objetivo 2:1 -0.070 (t -2.36).

### ORB 08:15–09:00

Rotura con cuerpo desde las 09:00 hasta las 15:00; a esa hora se cierra. ORB completos: 2094; con rotura: 2083.

**No pasa los criterios**. Coste medio 0.026 R; ancho medio del ORB 0.39 %; cómo terminan: objetivo 711, stop 780, por tiempo 255.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1746 | 48.1 % | -0.062 | -107.5 | 0.87 | -122.4 | -2.74 |
| Sin costes | 1746 | 48.2 % | -0.035 | -61.5 | 0.93 | -78.1 | -1.57 |
| Long | 911 | 48.2 % | -0.071 | -64.9 | 0.85 | -69.7 | -2.29 |
| Short | 835 | 48.0 % | -0.051 | -42.7 | 0.89 | -60.7 | -1.57 |
| 1.ª mitad | 873 | 49.4 % | -0.038 | -32.9 | 0.92 | -49.9 | -1.18 |
| 2.ª mitad | 873 | 46.8 % | -0.086 | -74.7 | 0.83 | -90.2 | -2.72 |

Por año (R neto medio y operaciones): 2018 -0.192 (60), 2019 -0.016 (214), 2020 -0.069 (208), 2021 -0.037 (208), 2022 +0.040 (219), 2023 -0.108 (220), 2024 -0.130 (224), 2025 -0.075 (221), 2026 -0.056 (172).

Sensibilidad (R neto medio y t): colchón 0 % -0.078 (t -3.41), colchón 50 % -0.040 (t -1.82), objetivo 1,5:1 -0.071 (t -2.69), objetivo 2:1 -0.046 (t -1.55).

### ORB 08:30–09:15

Rotura con cuerpo desde las 09:15 hasta las 15:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2084.

**No pasa los criterios**. Coste medio 0.025 R; ancho medio del ORB 0.39 %; cómo terminan: objetivo 709, stop 779, por tiempo 262.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1750 | 48.2 % | -0.057 | -99.5 | 0.88 | -103.5 | -2.53 |
| Sin costes | 1750 | 48.2 % | -0.032 | -55.8 | 0.93 | -61.0 | -1.42 |
| Long | 920 | 47.9 % | -0.062 | -57.0 | 0.87 | -60.2 | -2.00 |
| Short | 830 | 48.4 % | -0.051 | -42.4 | 0.89 | -49.2 | -1.57 |
| 1.ª mitad | 875 | 49.4 % | -0.039 | -34.1 | 0.92 | -46.5 | -1.21 |
| 2.ª mitad | 875 | 47.0 % | -0.075 | -65.4 | 0.85 | -73.2 | -2.38 |

Por año (R neto medio y operaciones): 2018 -0.217 (61), 2019 +0.001 (221), 2020 -0.037 (208), 2021 -0.074 (207), 2022 +0.024 (217), 2023 -0.079 (220), 2024 -0.135 (224), 2025 +0.011 (222), 2026 -0.140 (170).

Sensibilidad (R neto medio y t): colchón 0 % -0.063 (t -2.75), colchón 50 % -0.029 (t -1.32), objetivo 1,5:1 -0.039 (t -1.49), objetivo 2:1 -0.024 (t -0.80).

### ORB 08:45–09:30

Rotura con cuerpo desde las 09:30 hasta las 15:30; a esa hora se cierra. ORB completos: 2092; con rotura: 2088.

**No pasa los criterios**. Coste medio 0.024 R; ancho medio del ORB 0.30 %; cómo terminan: objetivo 781, stop 750, por tiempo 181.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1712 | 51.2 % | -0.000 | -0.5 | 1.00 | -34.3 | -0.01 |
| Sin costes | 1712 | 51.5 % | +0.024 | +41.1 | 1.05 | -24.7 | +1.04 |
| Long | 897 | 50.9 % | -0.011 | -9.6 | 0.98 | -27.1 | -0.33 |
| Short | 815 | 51.5 % | +0.011 | +9.0 | 1.02 | -37.8 | +0.33 |
| 1.ª mitad | 856 | 50.1 % | -0.025 | -21.2 | 0.95 | -34.3 | -0.75 |
| 2.ª mitad | 856 | 52.3 % | +0.024 | +20.7 | 1.05 | -26.2 | +0.74 |

Por año (R neto medio y operaciones): 2018 -0.206 (65), 2019 +0.052 (217), 2020 +0.028 (201), 2021 -0.045 (219), 2022 -0.031 (209), 2023 +0.081 (209), 2024 +0.002 (207), 2025 +0.020 (214), 2026 -0.055 (171).

Sensibilidad (R neto medio y t): colchón 0 % -0.006 (t -0.26), colchón 50 % +0.030 (t +1.33), objetivo 1,5:1 +0.031 (t +1.14), objetivo 2:1 +0.048 (t +1.56).

