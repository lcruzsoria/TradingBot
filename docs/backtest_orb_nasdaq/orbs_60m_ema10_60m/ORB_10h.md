# ORB de 60 min de las 10:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 10:00–11:00 | 1784 | 51.0 | +0.011 | +0.69 | +0.024 | 0.013 | no |
| 10:15–11:15 | 1734 | 51.1 | +0.018 | +1.07 | +0.033 | 0.015 | no |
| 10:30–11:30 | 1688 | 51.2 | +0.025 | +1.47 | +0.041 | 0.015 | no |
| 10:45–11:45 | 1652 | 51.6 | +0.025 | +1.43 | +0.041 | 0.016 | no |

## Detalle

### ORB 10:00–11:00

Rotura con cuerpo desde las 11:00 hasta las 17:00; a esa hora se cierra. ORB completos: 2096; con rotura: 1992.

**No pasa los criterios**. Coste medio 0.013 R; ancho medio del ORB 0.73 %; cómo terminan: objetivo 321, stop 294, por tiempo 1169.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1784 | 51.0 % | +0.011 | +19.6 | 1.04 | -30.3 | +0.69 |
| Sin costes | 1784 | 51.7 % | +0.024 | +43.6 | 1.09 | -20.0 | +1.53 |
| Long | 1002 | 54.0 % | +0.031 | +31.3 | 1.12 | -11.4 | +1.49 |
| Short | 782 | 47.1 % | -0.015 | -11.7 | 0.95 | -33.6 | -0.61 |
| 1.ª mitad | 892 | 54.5 % | +0.050 | +44.4 | 1.19 | -11.5 | +2.18 |
| 2.ª mitad | 892 | 47.4 % | -0.028 | -24.8 | 0.90 | -28.6 | -1.25 |

Por año (R neto medio y operaciones): 2018 +0.137 (65), 2019 -0.002 (210), 2020 +0.045 (221), 2021 +0.058 (220), 2022 +0.048 (222), 2023 +0.005 (225), 2024 -0.043 (227), 2025 -0.017 (217), 2026 -0.055 (177).

Sensibilidad (R neto medio y t): colchón 0 % +0.014 (t +0.80), colchón 50 % +0.006 (t +0.40), objetivo 1,5:1 +0.016 (t +0.92), objetivo 2:1 +0.021 (t +1.16).

### ORB 10:15–11:15

Rotura con cuerpo desde las 11:15 hasta las 17:15; a esa hora se cierra. ORB completos: 2096; con rotura: 1996.

**No pasa los criterios**. Coste medio 0.015 R; ancho medio del ORB 0.69 %; cómo terminan: objetivo 346, stop 321, por tiempo 1067.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1734 | 51.1 % | +0.018 | +31.2 | 1.06 | -14.4 | +1.07 |
| Sin costes | 1734 | 51.8 % | +0.033 | +56.4 | 1.12 | -10.4 | +1.94 |
| Long | 974 | 54.2 % | +0.051 | +49.6 | 1.19 | -9.2 | +2.31 |
| Short | 760 | 47.1 % | -0.024 | -18.4 | 0.92 | -28.3 | -0.94 |
| 1.ª mitad | 867 | 52.7 % | +0.047 | +40.6 | 1.17 | -13.1 | +1.95 |
| 2.ª mitad | 867 | 49.5 % | -0.011 | -9.5 | 0.96 | -14.4 | -0.47 |

Por año (R neto medio y operaciones): 2018 +0.036 (62), 2019 -0.036 (212), 2020 +0.100 (226), 2021 +0.024 (213), 2022 +0.095 (213), 2023 -0.014 (213), 2024 -0.003 (219), 2025 -0.028 (206), 2026 -0.012 (170).

Sensibilidad (R neto medio y t): colchón 0 % +0.019 (t +1.06), colchón 50 % +0.014 (t +0.92), objetivo 1,5:1 +0.026 (t +1.45), objetivo 2:1 +0.030 (t +1.57).

### ORB 10:30–11:30

Rotura con cuerpo desde las 11:30 hasta las 17:30; a esa hora se cierra. ORB completos: 2096; con rotura: 1996.

**No pasa los criterios**. Coste medio 0.015 R; ancho medio del ORB 0.65 %; cómo terminan: objetivo 362, stop 313, por tiempo 1013.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1688 | 51.2 % | +0.025 | +42.6 | 1.09 | -17.9 | +1.47 |
| Sin costes | 1688 | 52.3 % | +0.041 | +68.7 | 1.15 | -14.7 | +2.37 |
| Long | 957 | 53.3 % | +0.040 | +38.3 | 1.15 | -10.6 | +1.80 |
| Short | 731 | 48.6 % | +0.006 | +4.3 | 1.02 | -17.3 | +0.22 |
| 1.ª mitad | 844 | 51.7 % | +0.037 | +31.6 | 1.13 | -17.9 | +1.54 |
| 2.ª mitad | 844 | 50.8 % | +0.013 | +11.0 | 1.05 | -12.3 | +0.54 |

Por año (R neto medio y operaciones): 2018 +0.029 (64), 2019 -0.056 (208), 2020 +0.094 (218), 2021 +0.036 (208), 2022 +0.064 (209), 2023 +0.008 (210), 2024 +0.007 (210), 2025 +0.047 (197), 2026 -0.008 (164).

Sensibilidad (R neto medio y t): colchón 0 % +0.032 (t +1.69), colchón 50 % +0.023 (t +1.48), objetivo 1,5:1 +0.034 (t +1.84), objetivo 2:1 +0.039 (t +2.02).

### ORB 10:45–11:45

Rotura con cuerpo desde las 11:45 hasta las 17:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2005.

**No pasa los criterios**. Coste medio 0.016 R; ancho medio del ORB 0.63 %; cómo terminan: objetivo 358, stop 309, por tiempo 985.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1652 | 51.6 % | +0.025 | +40.8 | 1.09 | -23.1 | +1.43 |
| Sin costes | 1652 | 52.7 % | +0.041 | +67.7 | 1.15 | -19.5 | +2.37 |
| Long | 927 | 55.2 % | +0.066 | +60.8 | 1.25 | -13.9 | +2.90 |
| Short | 725 | 46.9 % | -0.028 | -20.0 | 0.91 | -30.7 | -1.03 |
| 1.ª mitad | 826 | 51.7 % | +0.021 | +17.7 | 1.07 | -23.1 | +0.87 |
| 2.ª mitad | 826 | 51.5 % | +0.028 | +23.1 | 1.10 | -11.8 | +1.14 |

Por año (R neto medio y operaciones): 2018 -0.051 (65), 2019 -0.069 (203), 2020 +0.096 (211), 2021 +0.023 (207), 2022 +0.052 (206), 2023 +0.028 (206), 2024 +0.053 (205), 2025 +0.058 (193), 2026 -0.034 (156).

Sensibilidad (R neto medio y t): colchón 0 % +0.026 (t +1.39), colchón 50 % +0.030 (t +1.93), objetivo 1,5:1 +0.041 (t +2.16), objetivo 2:1 +0.042 (t +2.13).

