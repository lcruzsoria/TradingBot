# ORB de 60 min de las 08:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 08:00–09:00 | 1820 | 48.1 | -0.057 | -2.64 | -0.034 | 0.023 | no |
| 08:15–09:15 | 1799 | 48.8 | -0.042 | -1.93 | -0.020 | 0.022 | no |
| 08:30–09:30 | 1822 | 50.3 | -0.006 | -0.30 | +0.014 | 0.020 | no |
| 08:45–09:45 | 1867 | 53.3 | +0.040 | +2.17 | +0.055 | 0.015 | no |

## Detalle

### ORB 08:00–09:00

Rotura con cuerpo desde las 09:00 hasta las 15:00; a esa hora se cierra. ORB completos: 2094; con rotura: 2080.

**No pasa los criterios**. Coste medio 0.023 R; ancho medio del ORB 0.43 %; cómo terminan: objetivo 720, stop 783, por tiempo 317.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1820 | 48.1 % | -0.057 | -104.1 | 0.88 | -111.3 | -2.64 |
| Sin costes | 1820 | 48.2 % | -0.034 | -61.4 | 0.93 | -70.4 | -1.55 |
| Long | 942 | 48.7 % | -0.063 | -59.2 | 0.87 | -61.1 | -2.09 |
| Short | 878 | 47.4 % | -0.051 | -44.9 | 0.89 | -62.5 | -1.64 |
| 1.ª mitad | 910 | 48.8 % | -0.046 | -41.8 | 0.90 | -55.4 | -1.49 |
| 2.ª mitad | 910 | 47.4 % | -0.068 | -62.3 | 0.86 | -74.6 | -2.25 |

Por año (R neto medio y operaciones): 2018 -0.147 (61), 2019 -0.000 (225), 2020 -0.096 (222), 2021 -0.045 (215), 2022 +0.019 (226), 2023 -0.139 (228), 2024 -0.103 (231), 2025 -0.029 (229), 2026 -0.035 (183).

Sensibilidad (R neto medio y t): colchón 0 % -0.061 (t -2.73), colchón 50 % -0.048 (t -2.29), objetivo 1,5:1 -0.056 (t -2.19), objetivo 2:1 -0.039 (t -1.39).

### ORB 08:15–09:15

Rotura con cuerpo desde las 09:15 hasta las 15:15; a esa hora se cierra. ORB completos: 2094; con rotura: 2078.

**No pasa los criterios**. Coste medio 0.022 R; ancho medio del ORB 0.43 %; cómo terminan: objetivo 712, stop 761, por tiempo 326.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1799 | 48.8 % | -0.042 | -75.7 | 0.91 | -81.8 | -1.93 |
| Sin costes | 1799 | 49.0 % | -0.020 | -35.2 | 0.96 | -45.9 | -0.90 |
| Long | 947 | 49.1 % | -0.041 | -39.3 | 0.91 | -43.1 | -1.38 |
| Short | 852 | 48.5 % | -0.043 | -36.4 | 0.91 | -50.4 | -1.35 |
| 1.ª mitad | 900 | 49.2 % | -0.040 | -36.1 | 0.91 | -53.0 | -1.29 |
| 2.ª mitad | 899 | 48.4 % | -0.044 | -39.6 | 0.90 | -53.7 | -1.44 |

Por año (R neto medio y operaciones): 2018 -0.277 (63), 2019 -0.022 (229), 2020 -0.031 (213), 2021 -0.072 (216), 2022 +0.071 (222), 2023 -0.064 (225), 2024 -0.087 (231), 2025 +0.008 (224), 2026 -0.079 (176).

Sensibilidad (R neto medio y t): colchón 0 % -0.056 (t -2.52), colchón 50 % -0.019 (t -0.90), objetivo 1,5:1 -0.033 (t -1.28), objetivo 2:1 -0.015 (t -0.53).

### ORB 08:30–09:30

Rotura con cuerpo desde las 09:30 hasta las 15:30; a esa hora se cierra. ORB completos: 2092; con rotura: 2078.

**No pasa los criterios**. Coste medio 0.020 R; ancho medio del ORB 0.42 %; cómo terminan: objetivo 742, stop 735, por tiempo 345.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1822 | 50.3 % | -0.006 | -11.8 | 0.99 | -39.5 | -0.30 |
| Sin costes | 1822 | 50.8 % | +0.014 | +25.2 | 1.03 | -25.0 | +0.64 |
| Long | 944 | 50.3 % | -0.016 | -15.3 | 0.96 | -23.8 | -0.54 |
| Short | 878 | 50.3 % | +0.004 | +3.5 | 1.01 | -30.1 | +0.13 |
| 1.ª mitad | 911 | 50.2 % | -0.006 | -5.9 | 0.99 | -32.1 | -0.21 |
| 2.ª mitad | 911 | 50.5 % | -0.006 | -5.9 | 0.99 | -27.7 | -0.22 |

Por año (R neto medio y operaciones): 2018 -0.062 (66), 2019 +0.031 (223), 2020 -0.002 (212), 2021 -0.042 (225), 2022 +0.021 (228), 2023 -0.031 (227), 2024 -0.021 (230), 2025 +0.065 (226), 2026 -0.066 (185).

Sensibilidad (R neto medio y t): colchón 0 % -0.017 (t -0.79), colchón 50 % +0.032 (t +1.56), objetivo 1,5:1 +0.036 (t +1.42), objetivo 2:1 +0.043 (t +1.54).

### ORB 08:45–09:45

Rotura con cuerpo desde las 09:45 hasta las 15:45; a esa hora se cierra. ORB completos: 2090; con rotura: 2066.

**No pasa los criterios**. Coste medio 0.015 R; ancho medio del ORB 0.61 %; cómo terminan: objetivo 559, stop 507, por tiempo 801.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1867 | 53.3 % | +0.040 | +75.5 | 1.12 | -13.9 | +2.17 |
| Sin costes | 1867 | 53.8 % | +0.055 | +102.7 | 1.16 | -13.3 | +2.95 |
| Long | 983 | 56.8 % | +0.059 | +58.1 | 1.18 | -15.1 | +2.33 |
| Short | 884 | 49.5 % | +0.020 | +17.4 | 1.05 | -9.8 | +0.72 |
| 1.ª mitad | 934 | 53.1 % | +0.033 | +30.4 | 1.09 | -13.9 | +1.24 |
| 2.ª mitad | 933 | 53.6 % | +0.048 | +45.0 | 1.14 | -10.5 | +1.83 |

Por año (R neto medio y operaciones): 2018 -0.072 (72), 2019 +0.053 (231), 2020 +0.034 (228), 2021 +0.088 (235), 2022 +0.032 (233), 2023 +0.020 (234), 2024 +0.049 (226), 2025 +0.059 (224), 2026 +0.019 (184).

Sensibilidad (R neto medio y t): colchón 0 % +0.045 (t +2.26), colchón 50 % +0.043 (t +2.53), objetivo 1,5:1 +0.051 (t +2.43), objetivo 2:1 +0.050 (t +2.30).

