# ORB de 60 min de las 21:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 60 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 21:00–22:00 | 1493 | 52.2 | +0.021 | +0.98 | +0.066 | 0.045 | no |
| 21:15–22:15 | 1524 | 51.0 | -0.002 | -0.10 | +0.044 | 0.046 | no |
| 21:30–22:30 | 1512 | 50.5 | -0.016 | -0.69 | +0.031 | 0.047 | no |
| 21:45–22:45 | 1475 | 51.6 | -0.008 | -0.35 | +0.042 | 0.050 | no |

## Detalle

### ORB 21:00–22:00

Rotura con cuerpo desde las 22:00 hasta las 04:00 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2069.

**No pasa los criterios**. Coste medio 0.045 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 537, stop 437, por tiempo 519.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1493 | 52.2 % | +0.021 | +31.9 | 1.06 | -27.6 | +0.98 |
| Sin costes | 1493 | 53.3 % | +0.066 | +98.4 | 1.19 | -20.5 | +3.04 |
| Long | 849 | 53.1 % | +0.021 | +17.7 | 1.06 | -32.8 | +0.73 |
| Short | 644 | 50.9 % | +0.022 | +14.2 | 1.06 | -25.3 | +0.65 |
| 1.ª mitad | 747 | 51.8 % | +0.014 | +10.5 | 1.04 | -14.1 | +0.47 |
| 2.ª mitad | 746 | 52.5 % | +0.029 | +21.4 | 1.07 | -27.6 | +0.91 |

Por año (R neto medio y operaciones): 2018 +0.041 (64), 2019 -0.010 (187), 2020 +0.010 (189), 2021 +0.062 (180), 2022 -0.064 (167), 2023 +0.046 (189), 2024 -0.051 (180), 2025 +0.071 (174), 2026 +0.103 (163).

Sensibilidad (R neto medio y t): colchón 0 % +0.018 (t +0.79), colchón 50 % +0.018 (t +0.91), objetivo 1,5:1 +0.018 (t +0.76), objetivo 2:1 +0.032 (t +1.22).

### ORB 21:15–22:15

Rotura con cuerpo desde las 22:15 hasta las 04:15 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2071.

**No pasa los criterios**. Coste medio 0.046 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 558, stop 487, por tiempo 479.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1524 | 51.0 % | -0.002 | -3.4 | 0.99 | -41.4 | -0.10 |
| Sin costes | 1524 | 51.5 % | +0.044 | +66.5 | 1.12 | -30.7 | +1.98 |
| Long | 866 | 53.7 % | +0.016 | +13.6 | 1.04 | -24.1 | +0.54 |
| Short | 658 | 47.4 % | -0.026 | -17.0 | 0.94 | -38.9 | -0.76 |
| 1.ª mitad | 762 | 50.0 % | -0.014 | -10.5 | 0.96 | -39.7 | -0.46 |
| 2.ª mitad | 762 | 52.0 % | +0.009 | +7.1 | 1.02 | -29.4 | +0.29 |

Por año (R neto medio y operaciones): 2018 +0.148 (64), 2019 -0.090 (190), 2020 -0.067 (185), 2021 +0.022 (193), 2022 +0.009 (175), 2023 +0.011 (191), 2024 -0.072 (180), 2025 +0.074 (180), 2026 +0.050 (166).

Sensibilidad (R neto medio y t): colchón 0 % +0.004 (t +0.18), colchón 50 % +0.005 (t +0.23), objetivo 1,5:1 +0.002 (t +0.08), objetivo 2:1 +0.012 (t +0.45).

### ORB 21:30–22:30

Rotura con cuerpo desde las 22:30 hasta las 04:30 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2080.

**No pasa los criterios**. Coste medio 0.047 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 567, stop 523, por tiempo 422.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1512 | 50.5 % | -0.016 | -23.6 | 0.96 | -52.1 | -0.69 |
| Sin costes | 1512 | 51.4 % | +0.031 | +47.4 | 1.08 | -23.4 | +1.39 |
| Long | 873 | 53.6 % | +0.018 | +15.6 | 1.05 | -24.5 | +0.61 |
| Short | 639 | 46.2 % | -0.061 | -39.3 | 0.86 | -53.1 | -1.76 |
| 1.ª mitad | 756 | 48.9 % | -0.031 | -23.3 | 0.92 | -41.2 | -1.00 |
| 2.ª mitad | 756 | 52.0 % | -0.000 | -0.3 | 1.00 | -21.7 | -0.01 |

Por año (R neto medio y operaciones): 2018 +0.172 (60), 2019 -0.090 (187), 2020 -0.071 (192), 2021 -0.021 (190), 2022 -0.023 (169), 2023 -0.029 (186), 2024 -0.021 (183), 2025 +0.078 (177), 2026 -0.000 (168).

Sensibilidad (R neto medio y t): colchón 0 % -0.018 (t -0.79), colchón 50 % -0.015 (t -0.73), objetivo 1,5:1 -0.022 (t -0.86), objetivo 2:1 -0.007 (t -0.26).

### ORB 21:45–22:45

Rotura con cuerpo desde las 22:45 hasta las 04:45 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2079.

**No pasa los criterios**. Coste medio 0.050 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 603, stop 539, por tiempo 333.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1475 | 51.6 % | -0.008 | -12.2 | 0.98 | -43.8 | -0.35 |
| Sin costes | 1475 | 52.1 % | +0.042 | +62.3 | 1.10 | -22.4 | +1.80 |
| Long | 861 | 54.5 % | +0.032 | +27.4 | 1.08 | -17.0 | +1.05 |
| Short | 614 | 47.6 % | -0.065 | -39.6 | 0.86 | -52.7 | -1.77 |
| 1.ª mitad | 738 | 51.2 % | -0.013 | -9.8 | 0.97 | -38.7 | -0.41 |
| 2.ª mitad | 737 | 52.0 % | -0.003 | -2.4 | 0.99 | -27.9 | -0.10 |

Por año (R neto medio y operaciones): 2018 +0.192 (56), 2019 -0.056 (175), 2020 -0.048 (191), 2021 -0.026 (179), 2022 +0.008 (172), 2023 -0.034 (177), 2024 -0.028 (178), 2025 +0.015 (181), 2026 +0.045 (166).

Sensibilidad (R neto medio y t): colchón 0 % -0.026 (t -1.06), colchón 50 % -0.000 (t -0.00), objetivo 1,5:1 +0.005 (t +0.20), objetivo 2:1 +0.019 (t +0.63).

