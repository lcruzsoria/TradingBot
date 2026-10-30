# ORB de 60 min de las 03:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 03:00–04:00 | 1818 | 50.1 | -0.024 | -1.12 | +0.007 | 0.030 | no |
| 03:15–04:15 | 1787 | 49.1 | -0.045 | -2.04 | -0.014 | 0.031 | no |
| 03:30–04:30 | 1749 | 50.0 | -0.032 | -1.42 | -0.000 | 0.032 | no |
| 03:45–04:45 | 1723 | 49.7 | -0.026 | -1.12 | +0.007 | 0.033 | no |

## Detalle

### ORB 03:00–04:00

Rotura con cuerpo desde las 04:00 hasta las 10:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2087.

**No pasa los criterios**. Coste medio 0.030 R; ancho medio del ORB 0.36 %; cómo terminan: objetivo 721, stop 720, por tiempo 377.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1818 | 50.1 % | -0.024 | -43.5 | 0.95 | -56.4 | -1.12 |
| Sin costes | 1818 | 50.4 % | +0.007 | +11.9 | 1.02 | -40.5 | +0.31 |
| Long | 1024 | 51.2 % | -0.011 | -11.3 | 0.97 | -32.8 | -0.39 |
| Short | 794 | 48.7 % | -0.040 | -32.1 | 0.91 | -45.0 | -1.25 |
| 1.ª mitad | 909 | 50.1 % | -0.032 | -28.9 | 0.93 | -50.7 | -1.09 |
| 2.ª mitad | 909 | 50.2 % | -0.016 | -14.5 | 0.97 | -34.6 | -0.51 |

Por año (R neto medio y operaciones): 2018 +0.079 (63), 2019 -0.060 (219), 2020 -0.117 (220), 2021 +0.002 (224), 2022 +0.011 (236), 2023 +0.026 (220), 2024 +0.032 (225), 2025 -0.041 (223), 2026 -0.086 (188).

Sensibilidad (R neto medio y t): colchón 0 % -0.044 (t -2.01), colchón 50 % -0.014 (t -0.71), objetivo 1,5:1 -0.005 (t -0.22), objetivo 2:1 -0.013 (t -0.50).

### ORB 03:15–04:15

Rotura con cuerpo desde las 04:15 hasta las 10:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.031 R; ancho medio del ORB 0.35 %; cómo terminan: objetivo 732, stop 756, por tiempo 299.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1787 | 49.1 % | -0.045 | -80.2 | 0.90 | -97.9 | -2.04 |
| Sin costes | 1787 | 49.3 % | -0.014 | -25.3 | 0.97 | -52.1 | -0.64 |
| Long | 992 | 49.4 % | -0.034 | -33.7 | 0.93 | -51.6 | -1.15 |
| Short | 795 | 48.8 % | -0.059 | -46.5 | 0.88 | -62.7 | -1.76 |
| 1.ª mitad | 894 | 48.8 % | -0.057 | -51.1 | 0.88 | -61.9 | -1.87 |
| 2.ª mitad | 893 | 49.5 % | -0.033 | -29.1 | 0.93 | -37.2 | -1.03 |

Por año (R neto medio y operaciones): 2018 +0.053 (64), 2019 -0.092 (223), 2020 -0.104 (211), 2021 -0.027 (217), 2022 -0.042 (233), 2023 -0.077 (224), 2024 +0.059 (220), 2025 -0.027 (218), 2026 -0.088 (177).

Sensibilidad (R neto medio y t): colchón 0 % -0.044 (t -1.97), colchón 50 % -0.038 (t -1.84), objetivo 1,5:1 -0.055 (t -2.16), objetivo 2:1 -0.044 (t -1.58).

### ORB 03:30–04:30

Rotura con cuerpo desde las 04:30 hasta las 10:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2091.

**No pasa los criterios**. Coste medio 0.032 R; ancho medio del ORB 0.33 %; cómo terminan: objetivo 744, stop 757, por tiempo 248.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1749 | 50.0 % | -0.032 | -56.0 | 0.93 | -71.0 | -1.42 |
| Sin costes | 1749 | 50.1 % | -0.000 | -0.8 | 1.00 | -42.2 | -0.02 |
| Long | 981 | 50.8 % | -0.024 | -23.7 | 0.95 | -39.7 | -0.81 |
| Short | 768 | 49.1 % | -0.042 | -32.3 | 0.91 | -45.3 | -1.23 |
| 1.ª mitad | 875 | 49.9 % | -0.047 | -41.1 | 0.90 | -50.5 | -1.48 |
| 2.ª mitad | 874 | 50.1 % | -0.017 | -14.9 | 0.96 | -27.5 | -0.53 |

Por año (R neto medio y operaciones): 2018 -0.031 (62), 2019 -0.065 (220), 2020 -0.112 (205), 2021 +0.006 (211), 2022 -0.039 (226), 2023 -0.072 (217), 2024 +0.099 (220), 2025 -0.023 (214), 2026 -0.061 (174).

Sensibilidad (R neto medio y t): colchón 0 % -0.020 (t -0.85), colchón 50 % -0.026 (t -1.19), objetivo 1,5:1 -0.039 (t -1.48), objetivo 2:1 -0.030 (t -1.03).

### ORB 03:45–04:45

Rotura con cuerpo desde las 04:45 hasta las 10:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.033 R; ancho medio del ORB 0.33 %; cómo terminan: objetivo 772, stop 756, por tiempo 195.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1723 | 49.7 % | -0.026 | -44.5 | 0.95 | -92.9 | -1.12 |
| Sin costes | 1723 | 50.0 % | +0.007 | +11.7 | 1.01 | -61.6 | +0.30 |
| Long | 956 | 50.2 % | -0.017 | -16.6 | 0.96 | -46.2 | -0.56 |
| Short | 767 | 49.0 % | -0.036 | -27.8 | 0.92 | -56.4 | -1.05 |
| 1.ª mitad | 862 | 47.7 % | -0.069 | -59.2 | 0.86 | -69.7 | -2.12 |
| 2.ª mitad | 861 | 51.7 % | +0.017 | +14.8 | 1.04 | -24.6 | +0.53 |

Por año (R neto medio y operaciones): 2018 +0.100 (59), 2019 -0.091 (215), 2020 -0.192 (208), 2021 -0.020 (212), 2022 -0.026 (224), 2023 -0.076 (207), 2024 +0.141 (223), 2025 +0.054 (209), 2026 -0.048 (166).

Sensibilidad (R neto medio y t): colchón 0 % -0.034 (t -1.43), colchón 50 % -0.023 (t -1.04), objetivo 1,5:1 -0.019 (t -0.70), objetivo 2:1 -0.009 (t -0.28).

