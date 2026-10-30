# ORB de 30 min de las 19:00 en NAS100.s (M5, PUPrime), filtro EMA 10 (60 min)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). Filtro EMA 10 en velas de 60 min: largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura va contra la EMA, ese día no se opera. NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 19:00–19:30 | 1281 | 49.3 | -0.070 | -2.69 | -0.001 | 0.069 | no |
| 19:15–19:45 | 1269 | 50.8 | -0.045 | -1.71 | +0.025 | 0.070 | no |
| 19:30–20:00 | 1257 | 49.6 | -0.048 | -1.85 | +0.018 | 0.066 | no |
| 19:45–20:15 | 1337 | 50.9 | -0.007 | -0.29 | +0.049 | 0.056 | no |

## Detalle

### ORB 19:00–19:30

Rotura con cuerpo desde las 19:30 hasta las 01:30 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2083.

**No pasa los criterios**. Coste medio 0.069 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 528, stop 530, por tiempo 223.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1281 | 49.3 % | -0.070 | -89.3 | 0.85 | -94.0 | -2.69 |
| Sin costes | 1281 | 49.9 % | -0.001 | -1.4 | 1.00 | -33.1 | -0.04 |
| Long | 713 | 53.0 % | -0.013 | -9.4 | 0.97 | -24.5 | -0.38 |
| Short | 568 | 44.5 % | -0.141 | -79.9 | 0.73 | -81.2 | -3.62 |
| 1.ª mitad | 641 | 49.5 % | -0.065 | -41.9 | 0.87 | -49.0 | -1.75 |
| 2.ª mitad | 640 | 49.1 % | -0.074 | -47.4 | 0.84 | -49.9 | -2.06 |

Por año (R neto medio y operaciones): 2018 -0.053 (43), 2019 -0.054 (164), 2020 -0.045 (155), 2021 -0.064 (165), 2022 -0.158 (147), 2023 -0.135 (137), 2024 -0.048 (141), 2025 -0.022 (170), 2026 -0.053 (159).

Sensibilidad (R neto medio y t): colchón 0 % -0.073 (t -2.75), colchón 50 % -0.071 (t -2.87), objetivo 1,5:1 -0.048 (t -1.59), objetivo 2:1 -0.054 (t -1.63).

### ORB 19:15–19:45

Rotura con cuerpo desde las 19:45 hasta las 01:45 (día siguiente); a esa hora se cierra. ORB completos: 2096; con rotura: 2086.

**No pasa los criterios**. Coste medio 0.070 R; ancho medio del ORB 0.15 %; cómo terminan: objetivo 545, stop 514, por tiempo 210.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1269 | 50.8 % | -0.045 | -56.6 | 0.90 | -68.0 | -1.71 |
| Sin costes | 1269 | 51.1 % | +0.025 | +31.8 | 1.06 | -25.8 | +0.96 |
| Long | 733 | 52.5 % | -0.025 | -18.7 | 0.94 | -43.3 | -0.75 |
| Short | 536 | 48.5 % | -0.071 | -37.9 | 0.86 | -39.9 | -1.74 |
| 1.ª mitad | 635 | 51.5 % | -0.018 | -11.6 | 0.96 | -20.2 | -0.49 |
| 2.ª mitad | 634 | 50.2 % | -0.071 | -45.0 | 0.85 | -49.3 | -1.95 |

Por año (R neto medio y operaciones): 2018 +0.044 (43), 2019 -0.048 (168), 2020 -0.001 (153), 2021 +0.076 (153), 2022 -0.205 (145), 2023 -0.083 (140), 2024 +0.012 (143), 2025 -0.066 (176), 2026 -0.071 (148).

Sensibilidad (R neto medio y t): colchón 0 % -0.058 (t -2.17), colchón 50 % -0.040 (t -1.59), objetivo 1,5:1 -0.044 (t -1.44), objetivo 2:1 -0.047 (t -1.42).

### ORB 19:30–20:00

Rotura con cuerpo desde las 20:00 hasta las 02:00 (día siguiente); a esa hora se cierra. ORB completos: 2095; con rotura: 2088.

**No pasa los criterios**. Coste medio 0.066 R; ancho medio del ORB 0.16 %; cómo terminan: objetivo 521, stop 501, por tiempo 235.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1257 | 49.6 % | -0.048 | -60.3 | 0.90 | -67.9 | -1.85 |
| Sin costes | 1257 | 50.0 % | +0.018 | +22.4 | 1.04 | -28.6 | +0.69 |
| Long | 721 | 52.1 % | -0.004 | -2.9 | 0.99 | -27.1 | -0.12 |
| Short | 536 | 46.1 % | -0.107 | -57.4 | 0.79 | -63.4 | -2.63 |
| 1.ª mitad | 629 | 50.1 % | -0.039 | -24.2 | 0.92 | -29.5 | -1.05 |
| 2.ª mitad | 628 | 49.0 % | -0.057 | -36.1 | 0.88 | -39.3 | -1.56 |

Por año (R neto medio y operaciones): 2018 +0.016 (48), 2019 -0.114 (162), 2020 +0.040 (145), 2021 -0.036 (151), 2022 -0.117 (143), 2023 -0.070 (146), 2024 -0.028 (155), 2025 -0.064 (164), 2026 -0.009 (143).

Sensibilidad (R neto medio y t): colchón 0 % -0.046 (t -1.73), colchón 50 % -0.058 (t -2.33), objetivo 1,5:1 -0.026 (t -0.87), objetivo 2:1 -0.028 (t -0.86).

### ORB 19:45–20:15

Rotura con cuerpo desde las 20:15 hasta las 02:15 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2081.

**No pasa los criterios**. Coste medio 0.056 R; ancho medio del ORB 0.19 %; cómo terminan: objetivo 510, stop 434, por tiempo 393.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 1337 | 50.9 % | -0.007 | -9.3 | 0.98 | -48.2 | -0.29 |
| Sin costes | 1337 | 51.3 % | +0.049 | +65.6 | 1.13 | -26.3 | +2.07 |
| Long | 777 | 51.6 % | +0.020 | +15.8 | 1.05 | -29.4 | +0.67 |
| Short | 560 | 49.8 % | -0.045 | -25.1 | 0.90 | -41.4 | -1.19 |
| 1.ª mitad | 669 | 52.2 % | +0.012 | +8.3 | 1.03 | -15.6 | +0.37 |
| 2.ª mitad | 668 | 49.6 % | -0.026 | -17.6 | 0.94 | -40.7 | -0.78 |

Por año (R neto medio y operaciones): 2018 +0.203 (46), 2019 -0.071 (168), 2020 +0.061 (149), 2021 -0.007 (166), 2022 -0.050 (162), 2023 -0.125 (163), 2024 +0.023 (165), 2025 +0.031 (168), 2026 +0.032 (150).

Sensibilidad (R neto medio y t): colchón 0 % -0.002 (t -0.10), colchón 50 % -0.018 (t -0.79), objetivo 1,5:1 -0.020 (t -0.76), objetivo 2:1 -0.011 (t -0.39).

