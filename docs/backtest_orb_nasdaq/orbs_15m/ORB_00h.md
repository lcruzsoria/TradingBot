# ORB de 15 min de las 00:00 en NAS100.s (M5, PUPrime)

Reglas: ORB de 15 min; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después de su final; stop en el extremo opuesto ± 20% del ancho; objetivo 1:1; a las 6 h se cierra. Una operación por ORB y día. Con el spread real de MT5 (R neto). NAS100.s de PUPrime, del 10/09/2018 al 30/10/2026, hora de Nueva York.

Criterios (fijados antes de ver resultados): al menos 300 operaciones, R neto medio > +0.05 con t > 2.0, y R neto medio positivo en las dos mitades del histórico.

## Los 4 ORB de esta hora

| ORB | Ops | Acierto % | R neto | t | Sin costes | Coste (R) | Pasa |
|---|---:|---:|---:|---:|---:|---:|---:|
| 00:00–00:15 | 2096 | 49.6 | -0.135 | -6.16 | -0.005 | 0.130 | no |
| 00:15–00:30 | 2097 | 50.9 | -0.113 | -5.16 | +0.021 | 0.134 | no |
| 00:30–00:45 | 2097 | 49.6 | -0.131 | -5.99 | -0.006 | 0.126 | no |
| 00:45–01:00 | 2097 | 49.3 | -0.141 | -6.44 | -0.014 | 0.127 | no |

## Detalle

### ORB 00:00–00:15

Rotura con cuerpo desde las 00:15 hasta las 06:15; a esa hora se cierra. ORB completos: 2097; con rotura: 2096.

**No pasa los criterios**. Coste medio 0.130 R; ancho medio del ORB 0.09 %; cómo terminan: objetivo 1032, stop 1043, por tiempo 21.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2096 | 49.6 % | -0.135 | -282.7 | 0.76 | -299.6 | -6.16 |
| Sin costes | 2096 | 49.7 % | -0.005 | -11.0 | 0.99 | -68.9 | -0.24 |
| Long | 1086 | 49.6 % | -0.138 | -149.5 | 0.76 | -158.8 | -4.51 |
| Short | 1010 | 49.6 % | -0.132 | -133.2 | 0.77 | -152.3 | -4.20 |
| 1.ª mitad | 1048 | 49.0 % | -0.150 | -157.4 | 0.74 | -159.2 | -4.86 |
| 2.ª mitad | 1048 | 50.2 % | -0.120 | -125.3 | 0.79 | -145.0 | -3.85 |

Por año (R neto medio y operaciones): 2018 -0.133 (76), 2019 -0.185 (258), 2020 -0.057 (256), 2021 -0.136 (259), 2022 -0.250 (258), 2023 -0.195 (258), 2024 -0.110 (259), 2025 -0.187 (256), 2026 +0.075 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.142 (t -6.48), colchón 50 % -0.109 (t -5.01), objetivo 1,5:1 -0.125 (t -4.69), objetivo 2:1 -0.104 (t -3.39).

### ORB 00:15–00:30

Rotura con cuerpo desde las 00:30 hasta las 06:30; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.134 R; ancho medio del ORB 0.08 %; cómo terminan: objetivo 1064, stop 1019, por tiempo 14.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 50.9 % | -0.113 | -237.2 | 0.80 | -239.8 | -5.16 |
| Sin costes | 2097 | 51.0 % | +0.021 | +43.7 | 1.04 | -28.0 | +0.96 |
| Long | 1076 | 50.5 % | -0.121 | -130.5 | 0.78 | -134.3 | -3.95 |
| Short | 1021 | 51.3 % | -0.105 | -106.8 | 0.81 | -109.8 | -3.33 |
| 1.ª mitad | 1049 | 50.5 % | -0.123 | -129.2 | 0.78 | -132.8 | -3.96 |
| 2.ª mitad | 1048 | 51.2 % | -0.103 | -108.0 | 0.81 | -112.1 | -3.33 |

Por año (R neto medio y operaciones): 2018 -0.161 (76), 2019 -0.239 (258), 2020 -0.076 (256), 2021 -0.030 (259), 2022 -0.130 (258), 2023 -0.204 (258), 2024 -0.069 (259), 2025 -0.074 (257), 2026 -0.062 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.147 (t -6.68), colchón 50 % -0.098 (t -4.51), objetivo 1,5:1 -0.097 (t -3.60), objetivo 2:1 -0.098 (t -3.19).

### ORB 00:30–00:45

Rotura con cuerpo desde las 00:45 hasta las 06:45; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.126 R; ancho medio del ORB 0.09 %; cómo terminan: objetivo 1036, stop 1045, por tiempo 16.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 49.6 % | -0.131 | -274.9 | 0.77 | -278.6 | -5.99 |
| Sin costes | 2097 | 49.6 % | -0.006 | -11.6 | 0.99 | -61.1 | -0.25 |
| Long | 1074 | 50.5 % | -0.116 | -124.2 | 0.79 | -127.0 | -3.77 |
| Short | 1023 | 48.7 % | -0.147 | -150.7 | 0.74 | -156.7 | -4.71 |
| 1.ª mitad | 1049 | 47.5 % | -0.177 | -186.1 | 0.70 | -188.5 | -5.72 |
| 2.ª mitad | 1048 | 51.7 % | -0.085 | -88.8 | 0.84 | -98.3 | -2.74 |

Por año (R neto medio y operaciones): 2018 -0.185 (76), 2019 -0.194 (258), 2020 -0.121 (256), 2021 -0.251 (259), 2022 -0.093 (258), 2023 -0.097 (258), 2024 -0.145 (259), 2025 -0.071 (257), 2026 -0.045 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.151 (t -6.88), colchón 50 % -0.098 (t -4.51), objetivo 1,5:1 -0.095 (t -3.57), objetivo 2:1 -0.087 (t -2.83).

### ORB 00:45–01:00

Rotura con cuerpo desde las 01:00 hasta las 07:00; a esa hora se cierra. ORB completos: 2097; con rotura: 2097.

**No pasa los criterios**. Coste medio 0.127 R; ancho medio del ORB 0.08 %; cómo terminan: objetivo 1024, stop 1054, por tiempo 19.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas (con spread) | 2097 | 49.3 % | -0.141 | -296.3 | 0.75 | -321.8 | -6.44 |
| Sin costes | 2097 | 49.3 % | -0.014 | -29.8 | 0.97 | -70.9 | -0.65 |
| Long | 1079 | 51.2 % | -0.104 | -111.9 | 0.81 | -135.6 | -3.39 |
| Short | 1018 | 47.2 % | -0.181 | -184.4 | 0.69 | -194.4 | -5.77 |
| 1.ª mitad | 1049 | 47.4 % | -0.182 | -190.8 | 0.69 | -195.1 | -5.87 |
| 2.ª mitad | 1048 | 51.1 % | -0.101 | -105.5 | 0.82 | -134.5 | -3.25 |

Por año (R neto medio y operaciones): 2018 +0.010 (76), 2019 -0.235 (258), 2020 -0.169 (256), 2021 -0.201 (259), 2022 -0.117 (258), 2023 -0.192 (258), 2024 -0.182 (259), 2025 -0.075 (257), 2026 +0.022 (216).

Sensibilidad (R neto medio y t): colchón 0 % -0.168 (t -7.65), colchón 50 % -0.117 (t -5.38), objetivo 1,5:1 -0.106 (t -3.96), objetivo 2:1 -0.106 (t -3.46).

