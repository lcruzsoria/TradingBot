# ORB de 45 min de las 10:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 45 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 10:00–10:45 | 2029 | 50.7 | +0.007 | +0.45 | +0.023 | 0.015 | no |
| 10:15–11:00 | 2044 | 51.1 | +0.008 | +0.45 | +0.024 | 0.017 | no |
| 10:30–11:15 | 2046 | 50.9 | +0.014 | +0.79 | +0.031 | 0.018 | no |
| 10:45–11:30 | 2044 | 50.5 | +0.004 | +0.23 | +0.023 | 0.019 | no |

## Detalle

### ORB 10:00–10:45

Rotura con cuerpo desde las 10:45 hasta las 16:45; a esa hora se cierra. ORB completos: 2096; con rotura: 2029.

**No pasa los criterios**. Coste medio 0.015 R; ancho medio del ORB 0.65 %; cómo terminan: objetivo 477, stop 447, por tiempo 1105.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2029 | 50.7 % | +0.007 | +15.0 | 1.02 | -59.1 | +0.45 |
| Sin costes | 2029 | 51.7 % | +0.023 | +46.0 | 1.07 | -43.6 | +1.37 |
| Long | 1114 | 53.6 % | +0.033 | +36.7 | 1.11 | -14.5 | +1.51 |
| Short | 915 | 47.2 % | -0.024 | -21.7 | 0.93 | -57.3 | -0.94 |
| 1.ª mitad | 1015 | 54.6 % | +0.063 | +64.2 | 1.21 | -11.8 | +2.68 |
| 2.ª mitad | 1014 | 46.8 % | -0.049 | -49.2 | 0.86 | -53.3 | -2.11 |

Por año (R neto medio y operaciones): 2018 +0.076 (75), 2019 +0.026 (247), 2020 +0.058 (253), 2021 +0.066 (247), 2022 +0.055 (254), 2023 -0.016 (251), 2024 -0.051 (253), 2025 -0.019 (247), 2026 -0.101 (202).

Sensibilidad (R neto medio y t): colchón 0 % +0.012 (t +0.66), colchón 50 % +0.017 (t +1.12), objetivo 1,5:1 +0.015 (t +0.85), objetivo 2:1 +0.024 (t +1.24).

### ORB 10:15–11:00

Rotura con cuerpo desde las 11:00 hasta las 17:00; a esa hora se cierra. ORB completos: 2096; con rotura: 2044.

**No pasa los criterios**. Coste medio 0.017 R; ancho medio del ORB 0.59 %; cómo terminan: objetivo 536, stop 500, por tiempo 1008.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2044 | 51.1 % | +0.008 | +15.6 | 1.02 | -43.1 | +0.45 |
| Sin costes | 2044 | 51.8 % | +0.024 | +49.6 | 1.07 | -27.0 | +1.43 |
| Long | 1126 | 53.8 % | +0.032 | +36.0 | 1.10 | -18.5 | +1.42 |
| Short | 918 | 47.7 % | -0.022 | -20.4 | 0.94 | -44.2 | -0.85 |
| 1.ª mitad | 1022 | 54.5 % | +0.052 | +53.0 | 1.16 | -11.3 | +2.12 |
| 2.ª mitad | 1022 | 47.7 % | -0.037 | -37.4 | 0.89 | -40.6 | -1.55 |

Por año (R neto medio y operaciones): 2018 +0.105 (74), 2019 -0.005 (252), 2020 +0.065 (254), 2021 +0.047 (253), 2022 +0.054 (254), 2023 +0.000 (252), 2024 -0.056 (251), 2025 -0.022 (251), 2026 -0.066 (203).

Sensibilidad (R neto medio y t): colchón 0 % +0.010 (t +0.54), colchón 50 % +0.012 (t +0.78), objetivo 1,5:1 +0.021 (t +1.13), objetivo 2:1 +0.029 (t +1.45).

### ORB 10:30–11:15

Rotura con cuerpo desde las 11:15 hasta las 17:15; a esa hora se cierra. ORB completos: 2096; con rotura: 2046.

**No pasa los criterios**. Coste medio 0.018 R; ancho medio del ORB 0.56 %; cómo terminan: objetivo 560, stop 503, por tiempo 983.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2046 | 50.9 % | +0.014 | +27.7 | 1.04 | -28.5 | +0.79 |
| Sin costes | 2046 | 51.5 % | +0.031 | +64.0 | 1.10 | -17.7 | +1.83 |
| Long | 1151 | 52.0 % | +0.018 | +21.1 | 1.06 | -14.3 | +0.82 |
| Short | 895 | 49.5 % | +0.007 | +6.5 | 1.02 | -31.4 | +0.28 |
| 1.ª mitad | 1023 | 51.5 % | +0.026 | +26.4 | 1.08 | -14.6 | +1.04 |
| 2.ª mitad | 1023 | 50.2 % | +0.001 | +1.3 | 1.00 | -22.2 | +0.05 |

Por año (R neto medio y operaciones): 2018 +0.075 (72), 2019 -0.003 (252), 2020 +0.100 (256), 2021 -0.021 (252), 2022 -0.006 (250), 2023 -0.047 (253), 2024 +0.024 (251), 2025 +0.029 (252), 2026 +0.012 (208).

Sensibilidad (R neto medio y t): colchón 0 % +0.019 (t +1.06), colchón 50 % +0.014 (t +0.92), objetivo 1,5:1 +0.019 (t +0.99), objetivo 2:1 +0.031 (t +1.57).

### ORB 10:45–11:30

Rotura con cuerpo desde las 11:30 hasta las 17:30; a esa hora se cierra. ORB completos: 2097; con rotura: 2044.

**No pasa los criterios**. Coste medio 0.019 R; ancho medio del ORB 0.53 %; cómo terminan: objetivo 565, stop 537, por tiempo 942.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2044 | 50.5 % | +0.004 | +8.0 | 1.01 | -26.0 | +0.23 |
| Sin costes | 2044 | 51.4 % | +0.023 | +46.6 | 1.07 | -15.5 | +1.31 |
| Long | 1139 | 51.8 % | +0.017 | +18.9 | 1.05 | -17.8 | +0.73 |
| Short | 905 | 49.0 % | -0.012 | -10.9 | 0.97 | -32.1 | -0.45 |
| 1.ª mitad | 1022 | 51.6 % | +0.021 | +21.3 | 1.06 | -18.5 | +0.84 |
| 2.ª mitad | 1022 | 49.5 % | -0.013 | -13.2 | 0.96 | -20.1 | -0.53 |

Por año (R neto medio y operaciones): 2018 -0.011 (76), 2019 -0.055 (254), 2020 +0.143 (258), 2021 -0.016 (250), 2022 +0.004 (252), 2023 -0.003 (253), 2024 -0.006 (255), 2025 -0.001 (245), 2026 -0.043 (201).

Sensibilidad (R neto medio y t): colchón 0 % +0.003 (t +0.18), colchón 50 % +0.013 (t +0.83), objetivo 1,5:1 +0.012 (t +0.63), objetivo 2:1 +0.029 (t +1.39).

