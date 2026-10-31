# ORB de 45 min de las 07:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 07:00–07:45 | 1681 | 49.5 | -0.048 | -2.01 | -0.010 | 0.038 | no |
| 07:15–08:00 | 1657 | 50.9 | -0.027 | -1.10 | +0.013 | 0.039 | no |
| 07:30–08:15 | 1673 | 49.6 | -0.046 | -1.93 | -0.010 | 0.036 | no |
| 07:45–08:30 | 1662 | 50.1 | -0.035 | -1.45 | -0.001 | 0.033 | no |

## Detalle

### ORB 07:00–07:45

Rotura con cuerpo desde las 07:45 hasta las 13:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.038 R; ancho medio del ORB 0.27 %; cómo terminan: objetivo 791, stop 808, por tiempo 82.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1681 | 49.5 % | -0.048 | -80.7 | 0.91 | -88.6 | -2.01 |
| Sin costes | 1681 | 49.6 % | -0.010 | -16.5 | 0.98 | -55.4 | -0.41 |
| Long | 906 | 49.7 % | -0.056 | -50.4 | 0.89 | -58.8 | -1.71 |
| Short | 775 | 49.3 % | -0.039 | -30.3 | 0.92 | -50.0 | -1.11 |
| 1.ª mitad | 841 | 50.2 % | -0.033 | -28.0 | 0.93 | -36.8 | -0.99 |
| 2.ª mitad | 840 | 48.8 % | -0.063 | -52.7 | 0.88 | -58.5 | -1.85 |

Por año (R neto medio y operaciones): 2018 +0.010 (57), 2019 -0.000 (199), 2020 -0.068 (208), 2021 -0.058 (209), 2022 +0.004 (201), 2023 -0.226 (217), 2024 +0.017 (207), 2025 +0.021 (209), 2026 -0.085 (174).

Sensibilidad (R neto medio y t): colchón 0 % -0.084 (t -3.48), colchón 50 % -0.057 (t -2.40), objetivo 1,5:1 -0.057 (t -1.99), objetivo 2:1 -0.044 (t -1.36).

### ORB 07:15–08:00

Rotura con cuerpo desde las 08:00 hasta las 14:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.039 R; ancho medio del ORB 0.26 %; cómo terminan: objetivo 804, stop 789, por tiempo 64.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1657 | 50.9 % | -0.027 | -44.0 | 0.95 | -89.0 | -1.10 |
| Sin costes | 1657 | 50.9 % | +0.013 | +21.2 | 1.03 | -51.3 | +0.53 |
| Long | 896 | 51.8 % | -0.015 | -13.2 | 0.97 | -41.2 | -0.45 |
| Short | 761 | 49.8 % | -0.040 | -30.8 | 0.92 | -63.0 | -1.14 |
| 1.ª mitad | 829 | 52.1 % | -0.006 | -4.8 | 0.99 | -43.3 | -0.17 |
| 2.ª mitad | 828 | 49.6 % | -0.047 | -39.2 | 0.91 | -51.6 | -1.38 |

Por año (R neto medio y operaciones): 2018 +0.271 (55), 2019 +0.048 (201), 2020 -0.042 (201), 2021 -0.073 (202), 2022 -0.018 (203), 2023 -0.150 (215), 2024 -0.055 (203), 2025 +0.026 (209), 2026 -0.023 (168).

Sensibilidad (R neto medio y t): colchón 0 % -0.035 (t -1.43), colchón 50 % -0.014 (t -0.58), objetivo 1,5:1 -0.035 (t -1.20), objetivo 2:1 -0.036 (t -1.10).

### ORB 07:30–08:15

Rotura con cuerpo desde las 08:15 hasta las 14:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2094.

**No pasa los criterios**. Coste medio 0.036 R; ancho medio del ORB 0.27 %; cómo terminan: objetivo 782, stop 804, por tiempo 87.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1673 | 49.6 % | -0.046 | -77.3 | 0.91 | -96.8 | -1.93 |
| Sin costes | 1673 | 49.7 % | -0.010 | -17.5 | 0.98 | -60.0 | -0.44 |
| Long | 909 | 50.7 % | -0.034 | -30.9 | 0.93 | -51.8 | -1.05 |
| Short | 764 | 48.3 % | -0.061 | -46.4 | 0.88 | -60.0 | -1.72 |
| 1.ª mitad | 837 | 50.4 % | -0.031 | -25.7 | 0.94 | -44.1 | -0.91 |
| 2.ª mitad | 836 | 48.8 % | -0.062 | -51.7 | 0.88 | -67.0 | -1.82 |

Por año (R neto medio y operaciones): 2018 +0.026 (59), 2019 +0.003 (206), 2020 -0.041 (208), 2021 -0.100 (200), 2022 +0.022 (198), 2023 -0.009 (209), 2024 -0.225 (213), 2025 -0.024 (212), 2026 -0.001 (168).

Sensibilidad (R neto medio y t): colchón 0 % -0.055 (t -2.27), colchón 50 % -0.047 (t -1.97), objetivo 1,5:1 -0.036 (t -1.26), objetivo 2:1 -0.056 (t -1.74).

### ORB 07:45–08:30

Rotura con cuerpo desde las 08:30 hasta las 14:30; a esa hora se cierra. ORB completos: 2095; con rotura: 2092.

**No pasa los criterios**. Coste medio 0.033 R; ancho medio del ORB 0.27 %; cómo terminan: objetivo 776, stop 780, por tiempo 106.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1662 | 50.1 % | -0.035 | -57.7 | 0.93 | -77.6 | -1.45 |
| Sin costes | 1662 | 50.1 % | -0.001 | -2.3 | 1.00 | -43.1 | -0.06 |
| Long | 879 | 50.1 % | -0.048 | -42.5 | 0.90 | -60.0 | -1.47 |
| Short | 783 | 50.2 % | -0.019 | -15.2 | 0.96 | -44.8 | -0.56 |
| 1.ª mitad | 831 | 49.5 % | -0.055 | -45.9 | 0.89 | -65.8 | -1.63 |
| 2.ª mitad | 831 | 50.8 % | -0.014 | -11.8 | 0.97 | -37.7 | -0.42 |

Por año (R neto medio y operaciones): 2018 -0.037 (51), 2019 -0.056 (210), 2020 -0.084 (204), 2021 -0.134 (198), 2022 +0.037 (202), 2023 +0.003 (200), 2024 -0.038 (219), 2025 +0.019 (207), 2026 -0.023 (171).

Sensibilidad (R neto medio y t): colchón 0 % -0.040 (t -1.64), colchón 50 % -0.023 (t -0.98), objetivo 1,5:1 -0.041 (t -1.42), objetivo 2:1 -0.042 (t -1.30).

