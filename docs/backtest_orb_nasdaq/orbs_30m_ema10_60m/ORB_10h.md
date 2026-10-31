# ORB de 30 min de las 10:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 10:00–10:30 | 1678 | 52.3 | +0.022 | +1.10 | +0.039 | 0.017 | no |
| 10:15–10:45 | 1622 | 51.3 | +0.009 | +0.46 | +0.028 | 0.019 | no |
| 10:30–11:00 | 1615 | 51.2 | +0.007 | +0.32 | +0.026 | 0.020 | no |
| 10:45–11:15 | 1590 | 51.5 | +0.020 | +0.92 | +0.040 | 0.021 | no |

## Detalle

### ORB 10:00–10:30

Rotura con cuerpo desde las 10:30 hasta las 16:30; a esa hora se cierra. ORB completos: 2096; con rotura: 2065.

**No pasa los criterios**. Coste medio 0.017 R; ancho medio del ORB 0.56 %; cómo terminan: objetivo 503, stop 464, por tiempo 711.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1678 | 52.3 % | +0.022 | +36.5 | 1.06 | -21.4 | +1.10 |
| Sin costes | 1678 | 53.0 % | +0.039 | +65.0 | 1.11 | -15.8 | +1.96 |
| Long | 916 | 55.5 % | +0.050 | +45.9 | 1.15 | -13.4 | +1.90 |
| Short | 762 | 48.4 % | -0.012 | -9.4 | 0.97 | -27.6 | -0.41 |
| 1.ª mitad | 839 | 54.6 % | +0.047 | +39.7 | 1.14 | -11.1 | +1.67 |
| 2.ª mitad | 839 | 49.9 % | -0.004 | -3.2 | 0.99 | -17.4 | -0.14 |

Por año (R neto medio y operaciones): 2018 -0.051 (59), 2019 +0.041 (197), 2020 +0.059 (204), 2021 +0.057 (207), 2022 +0.035 (213), 2023 -0.038 (210), 2024 +0.081 (214), 2025 -0.042 (203), 2026 -0.002 (171).

Sensibilidad (R neto medio y t): colchón 0 % +0.030 (t +1.42), colchón 50 % +0.026 (t +1.47), objetivo 1,5:1 +0.026 (t +1.19), objetivo 2:1 +0.030 (t +1.29).

### ORB 10:15–10:45

Rotura con cuerpo desde las 10:45 hasta las 16:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2076.

**No pasa los criterios**. Coste medio 0.019 R; ancho medio del ORB 0.51 %; cómo terminan: objetivo 499, stop 481, por tiempo 642.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1622 | 51.3 % | +0.009 | +15.4 | 1.03 | -38.2 | +0.46 |
| Sin costes | 1622 | 52.0 % | +0.028 | +45.8 | 1.08 | -27.4 | +1.38 |
| Long | 893 | 55.2 % | +0.049 | +43.3 | 1.14 | -10.7 | +1.78 |
| Short | 729 | 46.5 % | -0.038 | -27.9 | 0.90 | -44.8 | -1.24 |
| 1.ª mitad | 811 | 54.3 % | +0.050 | +40.9 | 1.14 | -11.3 | +1.74 |
| 2.ª mitad | 811 | 48.3 % | -0.031 | -25.5 | 0.92 | -38.2 | -1.09 |

Por año (R neto medio y operaciones): 2018 +0.076 (59), 2019 +0.002 (201), 2020 +0.047 (200), 2021 +0.013 (197), 2022 +0.116 (198), 2023 -0.003 (205), 2024 -0.046 (209), 2025 -0.028 (197), 2026 -0.057 (156).

Sensibilidad (R neto medio y t): colchón 0 % +0.024 (t +1.11), colchón 50 % +0.024 (t +1.28), objetivo 1,5:1 +0.027 (t +1.17), objetivo 2:1 +0.044 (t +1.80).

### ORB 10:30–11:00

Rotura con cuerpo desde las 11:00 hasta las 17:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2080.

**No pasa los criterios**. Coste medio 0.020 R; ancho medio del ORB 0.49 %; cómo terminan: objetivo 533, stop 497, por tiempo 585.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1615 | 51.2 % | +0.007 | +10.8 | 1.02 | -30.9 | +0.32 |
| Sin costes | 1615 | 51.8 % | +0.026 | +42.6 | 1.07 | -16.8 | +1.27 |
| Long | 901 | 53.4 % | +0.035 | +31.6 | 1.10 | -13.4 | +1.27 |
| Short | 714 | 48.5 % | -0.029 | -20.9 | 0.93 | -39.7 | -0.92 |
| 1.ª mitad | 808 | 53.1 % | +0.033 | +26.7 | 1.09 | -13.3 | +1.12 |
| 2.ª mitad | 807 | 49.3 % | -0.020 | -15.9 | 0.95 | -29.3 | -0.67 |

Por año (R neto medio y operaciones): 2018 +0.170 (57), 2019 -0.005 (195), 2020 +0.039 (195), 2021 +0.011 (193), 2022 +0.030 (198), 2023 -0.010 (202), 2024 -0.009 (200), 2025 -0.064 (203), 2026 +0.020 (172).

Sensibilidad (R neto medio y t): colchón 0 % -0.003 (t -0.16), colchón 50 % +0.017 (t +0.90), objetivo 1,5:1 +0.009 (t +0.37), objetivo 2:1 +0.022 (t +0.90).

### ORB 10:45–11:15

Rotura con cuerpo desde las 11:15 hasta las 17:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2085.

**No pasa los criterios**. Coste medio 0.021 R; ancho medio del ORB 0.47 %; cómo terminan: objetivo 553, stop 491, por tiempo 546.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1590 | 51.5 % | +0.020 | +31.0 | 1.05 | -29.2 | +0.92 |
| Sin costes | 1590 | 51.9 % | +0.040 | +64.4 | 1.11 | -22.0 | +1.91 |
| Long | 892 | 53.6 % | +0.047 | +41.7 | 1.13 | -10.5 | +1.65 |
| Short | 698 | 48.9 % | -0.015 | -10.6 | 0.96 | -39.1 | -0.48 |
| 1.ª mitad | 795 | 53.6 % | +0.069 | +54.9 | 1.19 | -13.6 | +2.29 |
| 2.ª mitad | 795 | 49.4 % | -0.030 | -23.9 | 0.92 | -29.2 | -1.01 |

Por año (R neto medio y operaciones): 2018 +0.133 (61), 2019 +0.009 (188), 2020 +0.157 (207), 2021 +0.018 (187), 2022 +0.039 (199), 2023 -0.083 (200), 2024 +0.020 (203), 2025 -0.013 (183), 2026 -0.044 (162).

Sensibilidad (R neto medio y t): colchón 0 % +0.010 (t +0.43), colchón 50 % +0.029 (t +1.49), objetivo 1,5:1 +0.033 (t +1.36), objetivo 2:1 +0.042 (t +1.62).

