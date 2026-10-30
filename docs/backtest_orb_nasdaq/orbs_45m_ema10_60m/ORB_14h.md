# ORB de 45 min de las 14:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 14:00–14:45 | 1469 | 49.7 | -0.006 | -0.30 | +0.018 | 0.024 | no |
| 14:15–15:00 | 1447 | 48.4 | -0.011 | -0.59 | +0.013 | 0.024 | no |
| 14:30–15:15 | 1404 | 49.8 | -0.013 | -0.71 | +0.011 | 0.024 | no |
| 14:45–15:30 | 1371 | 49.2 | -0.011 | -0.63 | +0.013 | 0.024 | no |

## Detalle

### ORB 14:00–14:45

Rotura con cuerpo desde las 14:45 hasta las 20:45; a esa hora se cierra. ORB completos: 2025; con rotura: 1936.

**No pasa los criterios**. Coste medio 0.024 R; ancho medio del ORB 0.44 %; cómo terminan: objetivo 340, stop 308, por tiempo 821.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1469 | 49.7 % | -0.006 | -8.3 | 0.98 | -32.7 | -0.30 |
| Sin costes | 1469 | 50.9 % | +0.018 | +26.5 | 1.06 | -16.6 | +0.95 |
| Long | 843 | 52.8 % | +0.021 | +17.5 | 1.07 | -14.1 | +0.83 |
| Short | 626 | 45.5 % | -0.041 | -25.8 | 0.88 | -32.6 | -1.41 |
| 1.ª mitad | 735 | 50.9 % | +0.011 | +8.1 | 1.03 | -17.8 | +0.40 |
| 2.ª mitad | 734 | 48.5 % | -0.022 | -16.5 | 0.93 | -26.8 | -0.87 |

Por año (R neto medio y operaciones): 2018 +0.167 (50), 2019 -0.030 (178), 2020 +0.053 (196), 2021 -0.030 (178), 2022 -0.009 (199), 2023 -0.017 (182), 2024 -0.041 (177), 2025 -0.006 (167), 2026 -0.023 (142).

Sensibilidad (R neto medio y t): colchón 0 % -0.003 (t -0.14), colchón 50 % -0.004 (t -0.24), objetivo 1,5:1 -0.007 (t -0.37), objetivo 2:1 +0.002 (t +0.09).

### ORB 14:15–15:00

Rotura con cuerpo desde las 15:00 hasta las 21:00; a esa hora se cierra. ORB completos: 2025; con rotura: 1936.

**No pasa los criterios**. Coste medio 0.024 R; ancho medio del ORB 0.44 %; cómo terminan: objetivo 344, stop 316, por tiempo 787.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1447 | 48.4 % | -0.011 | -16.4 | 0.96 | -49.6 | -0.59 |
| Sin costes | 1447 | 49.8 % | +0.013 | +18.8 | 1.04 | -29.1 | +0.68 |
| Long | 818 | 51.2 % | +0.014 | +11.7 | 1.05 | -22.6 | +0.56 |
| Short | 629 | 44.7 % | -0.045 | -28.0 | 0.87 | -43.8 | -1.52 |
| 1.ª mitad | 724 | 49.6 % | +0.008 | +6.0 | 1.03 | -17.5 | +0.30 |
| 2.ª mitad | 723 | 47.2 % | -0.031 | -22.3 | 0.90 | -39.9 | -1.16 |

Por año (R neto medio y operaciones): 2018 +0.175 (53), 2019 -0.001 (169), 2020 -0.010 (193), 2021 -0.014 (177), 2022 -0.015 (189), 2023 -0.050 (185), 2024 -0.061 (169), 2025 -0.044 (163), 2026 +0.056 (149).

Sensibilidad (R neto medio y t): colchón 0 % -0.025 (t -1.23), colchón 50 % -0.012 (t -0.69), objetivo 1,5:1 -0.005 (t -0.22), objetivo 2:1 -0.001 (t -0.05).

### ORB 14:30–15:15

Rotura con cuerpo desde las 15:15 hasta las 21:15; a esa hora se cierra. ORB completos: 2026; con rotura: 1881.

**No pasa los criterios**. Coste medio 0.024 R; ancho medio del ORB 0.45 %; cómo terminan: objetivo 285, stop 255, por tiempo 864.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1404 | 49.8 % | -0.013 | -18.5 | 0.96 | -35.8 | -0.71 |
| Sin costes | 1404 | 51.1 % | +0.011 | +15.1 | 1.04 | -22.1 | +0.58 |
| Long | 797 | 51.3 % | -0.003 | -2.2 | 0.99 | -19.4 | -0.11 |
| Short | 607 | 47.8 % | -0.027 | -16.3 | 0.91 | -21.4 | -0.99 |
| 1.ª mitad | 702 | 52.0 % | +0.019 | +13.4 | 1.07 | -11.9 | +0.72 |
| 2.ª mitad | 702 | 47.6 % | -0.045 | -31.9 | 0.85 | -32.5 | -1.76 |

Por año (R neto medio y operaciones): 2018 +0.072 (50), 2019 +0.002 (162), 2020 -0.021 (197), 2021 +0.058 (170), 2022 -0.000 (184), 2023 -0.099 (171), 2024 -0.009 (169), 2025 +0.050 (151), 2026 -0.115 (150).

Sensibilidad (R neto medio y t): colchón 0 % -0.013 (t -0.66), colchón 50 % -0.012 (t -0.71), objetivo 1,5:1 -0.004 (t -0.19), objetivo 2:1 -0.003 (t -0.12).

### ORB 14:45–15:30

Rotura con cuerpo desde las 15:30 hasta las 21:30; a esa hora se cierra. ORB completos: 2026; con rotura: 1867.

**No pasa los criterios**. Coste medio 0.024 R; ancho medio del ORB 0.45 %; cómo terminan: objetivo 251, stop 211, por tiempo 909.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1371 | 49.2 % | -0.011 | -15.3 | 0.96 | -28.1 | -0.63 |
| Sin costes | 1371 | 50.9 % | +0.013 | +17.3 | 1.05 | -16.2 | +0.71 |
| Long | 753 | 53.0 % | +0.017 | +12.5 | 1.06 | -16.5 | +0.70 |
| Short | 618 | 44.5 % | -0.045 | -27.8 | 0.85 | -29.9 | -1.68 |
| 1.ª mitad | 686 | 51.0 % | +0.013 | +9.1 | 1.05 | -13.1 | +0.52 |
| 2.ª mitad | 685 | 47.3 % | -0.036 | -24.4 | 0.88 | -28.1 | -1.42 |

Por año (R neto medio y operaciones): 2018 -0.078 (54), 2019 +0.012 (168), 2020 +0.053 (189), 2021 -0.028 (173), 2022 +0.015 (180), 2023 -0.072 (162), 2024 -0.002 (164), 2025 +0.059 (144), 2026 -0.127 (137).

Sensibilidad (R neto medio y t): colchón 0 % -0.017 (t -0.88), colchón 50 % -0.010 (t -0.63), objetivo 1,5:1 -0.009 (t -0.47), objetivo 2:1 -0.006 (t -0.30).

