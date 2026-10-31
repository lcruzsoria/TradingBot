# ORB de 30 min de las 08:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 30 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 08:00–08:30 | 2093 | 49.3 | -0.052 | -2.43 | -0.012 | 0.040 | no |
| 08:15–08:45 | 2085 | 46.9 | -0.097 | -4.59 | -0.062 | 0.035 | no |
| 08:30–09:00 | 2088 | 47.3 | -0.084 | -4.03 | -0.051 | 0.034 | no |
| 08:45–09:15 | 2090 | 50.7 | -0.018 | -0.83 | +0.017 | 0.035 | no |

## Detalle

### ORB 08:00–08:30

Rotura con cuerpo desde las 08:30 hasta las 14:30; a esa hora se cierra. ORB completos: 2095; con rotura: 2093.

**No pasa los criterios**. Coste medio 0.040 R; ancho medio del ORB 0.23 %; cómo terminan: objetivo 998, stop 1018, por tiempo 77.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2093 | 49.3 % | -0.052 | -109.7 | 0.90 | -118.6 | -2.43 |
| Sin costes | 2093 | 49.3 % | -0.012 | -25.0 | 0.98 | -50.5 | -0.56 |
| Long | 1051 | 48.2 % | -0.080 | -84.6 | 0.85 | -90.2 | -2.65 |
| Short | 1042 | 50.4 % | -0.024 | -25.1 | 0.95 | -38.5 | -0.79 |
| 1.ª mitad | 1047 | 49.7 % | -0.049 | -50.9 | 0.91 | -66.8 | -1.59 |
| 2.ª mitad | 1046 | 48.9 % | -0.056 | -58.8 | 0.89 | -83.7 | -1.85 |

Por año (R neto medio y operaciones): 2018 -0.089 (75), 2019 -0.056 (257), 2020 -0.043 (254), 2021 -0.113 (259), 2022 +0.052 (258), 2023 -0.029 (258), 2024 -0.085 (259), 2025 -0.071 (257), 2026 -0.065 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.058 (t -2.66), colchón 50 % -0.040 (t -1.85), objetivo 1,5:1 -0.071 (t -2.75), objetivo 2:1 -0.075 (t -2.55).

### ORB 08:15–08:45

Rotura con cuerpo desde las 08:45 hasta las 14:45; a esa hora se cierra. ORB completos: 2095; con rotura: 2085.

**No pasa los criterios**. Coste medio 0.035 R; ancho medio del ORB 0.32 %; cómo terminan: objetivo 881, stop 1016, por tiempo 188.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2085 | 46.9 % | -0.097 | -201.5 | 0.81 | -203.6 | -4.59 |
| Sin costes | 2085 | 47.1 % | -0.062 | -128.6 | 0.88 | -131.6 | -2.93 |
| Long | 1045 | 46.9 % | -0.101 | -105.7 | 0.81 | -106.2 | -3.40 |
| Short | 1040 | 46.8 % | -0.092 | -95.8 | 0.82 | -103.4 | -3.09 |
| 1.ª mitad | 1043 | 47.4 % | -0.089 | -93.0 | 0.83 | -100.7 | -2.97 |
| 2.ª mitad | 1042 | 46.4 % | -0.104 | -108.5 | 0.80 | -118.7 | -3.52 |

Por año (R neto medio y operaciones): 2018 -0.133 (75), 2019 -0.117 (258), 2020 -0.115 (254), 2021 -0.091 (257), 2022 +0.021 (255), 2023 -0.078 (257), 2024 -0.138 (258), 2025 -0.105 (256), 2026 -0.148 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.098 (t -4.60), colchón 50 % -0.075 (t -3.66), objetivo 1,5:1 -0.114 (t -4.57), objetivo 2:1 -0.093 (t -3.33).

### ORB 08:30–09:00

Rotura con cuerpo desde las 09:00 hasta las 15:00; a esa hora se cierra. ORB completos: 2095; con rotura: 2088.

**No pasa los criterios**. Coste medio 0.034 R; ancho medio del ORB 0.32 %; cómo terminan: objetivo 885, stop 995, por tiempo 208.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2088 | 47.3 % | -0.084 | -176.3 | 0.84 | -183.0 | -4.03 |
| Sin costes | 2088 | 47.4 % | -0.051 | -105.8 | 0.90 | -115.4 | -2.42 |
| Long | 1071 | 47.6 % | -0.085 | -90.9 | 0.83 | -94.9 | -2.90 |
| Short | 1017 | 47.0 % | -0.084 | -85.4 | 0.84 | -92.6 | -2.79 |
| 1.ª mitad | 1044 | 48.6 % | -0.065 | -68.1 | 0.87 | -75.5 | -2.18 |
| 2.ª mitad | 1044 | 46.1 % | -0.104 | -108.3 | 0.80 | -119.7 | -3.53 |

Por año (R neto medio y operaciones): 2018 -0.136 (76), 2019 -0.080 (258), 2020 -0.080 (254), 2021 -0.027 (256), 2022 -0.021 (256), 2023 -0.122 (257), 2024 -0.086 (258), 2025 -0.123 (258), 2026 -0.128 (215).

Sensibilidad (R neto medio y t): colchón 0 % -0.085 (t -3.98), colchón 50 % -0.064 (t -3.10), objetivo 1,5:1 -0.076 (t -3.05), objetivo 2:1 -0.046 (t -1.65).

### ORB 08:45–09:15

Rotura con cuerpo desde las 09:15 hasta las 15:15; a esa hora se cierra. ORB completos: 2095; con rotura: 2090.

**No pasa los criterios**. Coste medio 0.035 R; ancho medio del ORB 0.25 %; cómo terminan: objetivo 1005, stop 978, por tiempo 107.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2090 | 50.7 % | -0.018 | -37.0 | 0.96 | -70.5 | -0.83 |
| Sin costes | 2090 | 50.8 % | +0.017 | +36.5 | 1.04 | -39.0 | +0.82 |
| Long | 1075 | 50.9 % | -0.015 | -15.8 | 0.97 | -39.6 | -0.49 |
| Short | 1015 | 50.5 % | -0.021 | -21.1 | 0.96 | -48.2 | -0.68 |
| 1.ª mitad | 1045 | 50.6 % | -0.025 | -26.5 | 0.95 | -53.1 | -0.84 |
| 2.ª mitad | 1045 | 50.8 % | -0.010 | -10.4 | 0.98 | -32.2 | -0.33 |

Por año (R neto medio y operaciones): 2018 -0.308 (76), 2019 +0.083 (258), 2020 +0.051 (254), 2021 -0.119 (257), 2022 -0.002 (258), 2023 -0.035 (257), 2024 -0.024 (259), 2025 +0.032 (257), 2026 -0.046 (214).

Sensibilidad (R neto medio y t): colchón 0 % -0.034 (t -1.56), colchón 50 % -0.017 (t -0.79), objetivo 1,5:1 -0.024 (t -0.94), objetivo 2:1 -0.025 (t -0.84).

