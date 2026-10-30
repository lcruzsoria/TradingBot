# ORB de 15 min de las 23:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 23:00–23:15 | 2097 | 49.3 | -0.130 | -5.97 | -0.010 | 0.120 | no |
| 23:15–23:30 | 2098 | 49.1 | -0.144 | -6.59 | -0.017 | 0.127 | no |
| 23:30–23:45 | 2098 | 49.2 | -0.143 | -6.53 | -0.012 | 0.131 | no |
| 23:45–00:00 | 2098 | 49.8 | -0.143 | -6.55 | -0.004 | 0.140 | no |

## Detalle

### ORB 23:00–23:15

Rotura con cuerpo desde las 23:15 hasta las 05:15 (día siguiente); a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.120 R; ancho medio del ORB 0.09 %; cómo terminan: objetivo 1022, stop 1042, por tiempo 33.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 49.3 % | -0.130 | -272.8 | 0.77 | -288.1 | -5.97 |
| Sin costes | 2097 | 49.3 % | -0.010 | -21.1 | 0.98 | -59.7 | -0.46 |
| Long | 1116 | 49.2 % | -0.129 | -143.5 | 0.77 | -159.9 | -4.30 |
| Short | 981 | 49.3 % | -0.132 | -129.3 | 0.77 | -133.1 | -4.13 |
| 1.ª mitad | 1049 | 47.9 % | -0.154 | -161.6 | 0.73 | -161.6 | -5.01 |
| 2.ª mitad | 1048 | 50.7 % | -0.106 | -111.2 | 0.81 | -133.7 | -3.43 |

Por año (R neto medio y operaciones): 2018 -0.191 (76), 2019 -0.285 (258), 2020 -0.069 (256), 2021 -0.074 (259), 2022 -0.145 (258), 2023 -0.222 (258), 2024 -0.138 (259), 2025 -0.113 (257), 2026 +0.056 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.152 (t -6.93), colchón 50 % -0.104 (t -4.81), objetivo 1,5:1 -0.130 (t -4.94), objetivo 2:1 -0.116 (t -3.83).

### ORB 23:15–23:30

Rotura con cuerpo desde las 23:30 hasta las 05:30 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2098.

**No pasa los criterios**. Coste medio 0.127 R; ancho medio del ORB 0.09 %; cómo terminan: objetivo 1020, stop 1056, por tiempo 22.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2098 | 49.1 % | -0.144 | -302.0 | 0.75 | -303.8 | -6.59 |
| Sin costes | 2098 | 49.1 % | -0.017 | -35.9 | 0.97 | -70.5 | -0.79 |
| Long | 1085 | 49.8 % | -0.128 | -138.6 | 0.77 | -139.1 | -4.21 |
| Short | 1013 | 48.4 % | -0.161 | -163.4 | 0.72 | -174.7 | -5.13 |
| 1.ª mitad | 1049 | 47.5 % | -0.173 | -181.7 | 0.70 | -187.0 | -5.60 |
| 2.ª mitad | 1049 | 50.7 % | -0.115 | -120.3 | 0.79 | -120.8 | -3.72 |

Por año (R neto medio y operaciones): 2018 -0.232 (76), 2019 -0.278 (258), 2020 -0.077 (257), 2021 -0.140 (259), 2022 -0.175 (258), 2023 -0.174 (258), 2024 -0.189 (259), 2025 -0.033 (257), 2026 -0.043 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.161 (t -7.32), colchón 50 % -0.141 (t -6.51), objetivo 1,5:1 -0.154 (t -5.83), objetivo 2:1 -0.123 (t -4.02).

### ORB 23:30–23:45

Rotura con cuerpo desde las 23:45 hasta las 05:45 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2098.

**No pasa los criterios**. Coste medio 0.131 R; ancho medio del ORB 0.09 %; cómo terminan: objetivo 1028, stop 1054, por tiempo 16.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2098 | 49.2 % | -0.143 | -299.6 | 0.75 | -316.6 | -6.53 |
| Sin costes | 2098 | 49.3 % | -0.012 | -25.7 | 0.98 | -87.6 | -0.56 |
| Long | 1073 | 50.1 % | -0.125 | -133.9 | 0.78 | -145.4 | -4.08 |
| Short | 1025 | 48.2 % | -0.162 | -165.7 | 0.72 | -176.3 | -5.17 |
| 1.ª mitad | 1049 | 48.4 % | -0.162 | -169.7 | 0.72 | -173.5 | -5.24 |
| 2.ª mitad | 1049 | 50.0 % | -0.124 | -129.9 | 0.78 | -144.9 | -4.00 |

Por año (R neto medio y operaciones): 2018 -0.097 (76), 2019 -0.197 (258), 2020 -0.070 (257), 2021 -0.197 (259), 2022 -0.227 (258), 2023 -0.225 (258), 2024 -0.111 (259), 2025 -0.142 (257), 2026 +0.042 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.185 (t -8.46), colchón 50 % -0.113 (t -5.18), objetivo 1,5:1 -0.145 (t -5.46), objetivo 2:1 -0.163 (t -5.40).

### ORB 23:45–00:00

Rotura con cuerpo desde las 00:00 hasta las 06:00 (día siguiente); a esa hora se cierra. ORB completos: 2098; con rotura: 2098.

**No pasa los criterios**. Coste medio 0.140 R; ancho medio del ORB 0.08 %; cómo terminan: objetivo 1035, stop 1045, por tiempo 18.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2098 | 49.8 % | -0.143 | -301.0 | 0.75 | -303.6 | -6.55 |
| Sin costes | 2098 | 49.9 % | -0.004 | -8.1 | 0.99 | -56.1 | -0.18 |
| Long | 1074 | 49.7 % | -0.146 | -156.3 | 0.74 | -158.6 | -4.76 |
| Short | 1024 | 49.8 % | -0.141 | -144.7 | 0.75 | -153.8 | -4.50 |
| 1.ª mitad | 1049 | 50.2 % | -0.134 | -140.5 | 0.76 | -140.5 | -4.32 |
| 2.ª mitad | 1049 | 49.3 % | -0.153 | -160.6 | 0.73 | -164.0 | -4.94 |

Por año (R neto medio y operaciones): 2018 -0.219 (76), 2019 -0.184 (258), 2020 -0.061 (257), 2021 -0.184 (259), 2022 -0.124 (258), 2023 -0.230 (258), 2024 -0.135 (259), 2025 -0.143 (257), 2026 -0.050 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.156 (t -7.12), colchón 50 % -0.116 (t -5.34), objetivo 1,5:1 -0.138 (t -5.18), objetivo 2:1 -0.114 (t -3.71).

