# ORB de 45 min de las 10:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 10:00–10:45 | 1729 | 51.1 | +0.014 | +0.78 | +0.028 | 0.015 | no |
| 10:15–11:00 | 1710 | 51.3 | +0.011 | +0.60 | +0.027 | 0.016 | no |
| 10:30–11:15 | 1676 | 51.5 | +0.023 | +1.23 | +0.040 | 0.017 | no |
| 10:45–11:30 | 1638 | 51.3 | +0.019 | +0.97 | +0.037 | 0.018 | no |

## Detalle

### ORB 10:00–10:45

Rotura con cuerpo desde las 10:45 hasta las 16:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2029.

**No pasa los criterios**. Coste medio 0.015 R; ancho medio del ORB 0.66 %; cómo terminan: objetivo 386, stop 360, por tiempo 983.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1729 | 51.1 % | +0.014 | +23.8 | 1.04 | -41.2 | +0.78 |
| Sin costes | 1729 | 52.2 % | +0.028 | +49.3 | 1.10 | -28.4 | +1.62 |
| Long | 965 | 54.2 % | +0.042 | +40.4 | 1.15 | -9.8 | +1.82 |
| Short | 764 | 47.3 % | -0.022 | -16.6 | 0.94 | -45.6 | -0.81 |
| 1.ª mitad | 865 | 55.0 % | +0.069 | +59.7 | 1.24 | -9.1 | +2.76 |
| 2.ª mitad | 864 | 47.2 % | -0.042 | -35.9 | 0.87 | -38.1 | -1.70 |

Por año (R neto medio y operaciones): 2018 +0.087 (62), 2019 +0.035 (203), 2020 +0.055 (211), 2021 +0.075 (216), 2022 +0.061 (215), 2023 -0.020 (222), 2024 -0.043 (224), 2025 -0.014 (207), 2026 -0.075 (169).

Sensibilidad (R neto medio y t): colchón 0 % +0.017 (t +0.90), colchón 50 % +0.022 (t +1.44), objetivo 1,5:1 +0.022 (t +1.13), objetivo 2:1 +0.031 (t +1.55).

### ORB 10:15–11:00

Rotura con cuerpo desde las 11:00 hasta las 17:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2044.

**No pasa los criterios**. Coste medio 0.016 R; ancho medio del ORB 0.60 %; cómo terminan: objetivo 427, stop 405, por tiempo 878.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1710 | 51.3 % | +0.011 | +18.8 | 1.03 | -32.1 | +0.60 |
| Sin costes | 1710 | 51.9 % | +0.027 | +46.4 | 1.09 | -22.3 | +1.48 |
| Long | 950 | 54.4 % | +0.040 | +37.6 | 1.13 | -14.2 | +1.63 |
| Short | 760 | 47.5 % | -0.025 | -18.8 | 0.93 | -39.2 | -0.89 |
| 1.ª mitad | 855 | 54.6 % | +0.055 | +46.8 | 1.18 | -12.3 | +2.08 |
| 2.ª mitad | 855 | 48.1 % | -0.033 | -28.0 | 0.90 | -31.2 | -1.28 |

Por año (R neto medio y operaciones): 2018 +0.169 (61), 2019 -0.017 (209), 2020 +0.067 (214), 2021 +0.042 (205), 2022 +0.063 (208), 2023 +0.014 (212), 2024 -0.048 (217), 2025 -0.048 (215), 2026 -0.038 (169).

Sensibilidad (R neto medio y t): colchón 0 % +0.016 (t +0.82), colchón 50 % +0.011 (t +0.69), objetivo 1,5:1 +0.024 (t +1.20), objetivo 2:1 +0.033 (t +1.57).

### ORB 10:30–11:15

Rotura con cuerpo desde las 11:15 hasta las 17:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2046.

**No pasa los criterios**. Coste medio 0.017 R; ancho medio del ORB 0.58 %; cómo terminan: objetivo 448, stop 386, por tiempo 842.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1676 | 51.5 % | +0.023 | +38.5 | 1.07 | -20.2 | +1.23 |
| Sin costes | 1676 | 52.1 % | +0.040 | +67.0 | 1.13 | -14.5 | +2.15 |
| Long | 953 | 53.3 % | +0.040 | +38.2 | 1.13 | -9.5 | +1.64 |
| Short | 723 | 49.1 % | +0.000 | +0.3 | 1.00 | -23.0 | +0.01 |
| 1.ª mitad | 838 | 52.3 % | +0.044 | +37.0 | 1.14 | -11.6 | +1.65 |
| 2.ª mitad | 838 | 50.7 % | +0.002 | +1.5 | 1.01 | -19.8 | +0.07 |

Por año (R neto medio y operaciones): 2018 +0.084 (61), 2019 -0.035 (206), 2020 +0.116 (216), 2021 +0.008 (201), 2022 +0.070 (203), 2023 -0.065 (208), 2024 +0.030 (212), 2025 +0.033 (197), 2026 +0.002 (172).

Sensibilidad (R neto medio y t): colchón 0 % +0.027 (t +1.32), colchón 50 % +0.021 (t +1.24), objetivo 1,5:1 +0.025 (t +1.22), objetivo 2:1 +0.032 (t +1.50).

### ORB 10:45–11:30

Rotura con cuerpo desde las 11:30 hasta las 17:30; a esa hora se cierra. ORB completos: 2097; con rotura: 2044.

**No pasa los criterios**. Coste medio 0.018 R; ancho medio del ORB 0.55 %; cómo terminan: objetivo 446, stop 406, por tiempo 786.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1638 | 51.3 % | +0.019 | +30.4 | 1.06 | -15.5 | +0.97 |
| Sin costes | 1638 | 52.4 % | +0.037 | +60.1 | 1.11 | -12.4 | +1.92 |
| Long | 920 | 53.7 % | +0.049 | +45.5 | 1.16 | -9.3 | +1.96 |
| Short | 718 | 48.3 % | -0.021 | -15.1 | 0.94 | -30.2 | -0.72 |
| 1.ª mitad | 819 | 52.7 % | +0.048 | +39.6 | 1.15 | -15.2 | +1.79 |
| 2.ª mitad | 819 | 49.9 % | -0.011 | -9.2 | 0.97 | -15.0 | -0.41 |

Por año (R neto medio y operaciones): 2018 +0.031 (64), 2019 -0.038 (202), 2020 +0.120 (211), 2021 +0.028 (205), 2022 +0.034 (204), 2023 -0.009 (206), 2024 +0.033 (204), 2025 +0.016 (190), 2026 -0.067 (152).

Sensibilidad (R neto medio y t): colchón 0 % +0.020 (t +1.00), colchón 50 % +0.024 (t +1.39), objetivo 1,5:1 +0.027 (t +1.28), objetivo 2:1 +0.041 (t +1.82).

