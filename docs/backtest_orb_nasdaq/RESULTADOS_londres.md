# Backtest ORB apertura de Londres en NAS100.s (M5, PUPrime)

Script: `scripts/backtest_orb_nasdaq.py --sesion londres` → operaciones en `analisis/backtest_orb_nasdaq_londres.csv` (no se sube a git). Solo lee velas de MT5.

## Reglas (hora de Nueva York)

- **ORB:** máximo y mínimo de las velas M5 de las 03:00, 03:05, 03:10.
- **Rotura con cuerpo:** la primera vela M5 desde las 03:15 que cierra fuera del ORB, como tarde a las 09:30. Una operación por día.
- **Entrada** al cierre de esa vela. **Stop** en el extremo opuesto del ORB ± 20% de su ancho. **Objetivo** 1:1 (a la misma distancia que el stop).
- Sin stop ni objetivo a las 09:30: se cierra al cierre de la vela de las 09:25. Si caben stop y objetivo en una vela, cuenta el stop.
- **Costes:** spread real de MT5 en la vela de la entrada (R neto = R bruto − spread / riesgo). Sin comisiones ni deslizamiento.

## Datos

- 573.084 velas M5 de NAS100.s del 10/09/2018 al 30/10/2026 (hora de NY. servidor = NY + 7 h).
- Días con mercado: 2537; con todas las velas del ORB: 2096; con rotura antes de las 09:30: 2095 (100 %).
- Comprobación del horario: velas con hora NY 17 (la pausa diaria de los índices): 0 de 573.084.

## Veredicto (criterios fijados antes de ver los resultados)

| Criterio | Valor | Cumple |
|---|---:|---:|
| al menos 300 operaciones | 2095 | sí |
| R neto medio > +0.05 y t > 2.0 | -0.074 R, t -3.53 | **no** |
| R neto medio positivo en las dos mitades | -0.034 / -0.115 R | **no** |

**No pasa.**

## Resultado de la variante principal

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas | 2095 | 48.5 % | -0.074 | -155.5 | 0.85 | -167.5 | -3.53 |
| Sin costes (R bruto) | 2095 | 48.7 % | -0.022 | -46.1 | 0.95 | -82.5 | -1.05 |
| Long | 1115 | 49.0 % | -0.065 | -72.8 | 0.87 | -84.6 | -2.28 |
| Short | 980 | 48.0 % | -0.084 | -82.6 | 0.84 | -97.1 | -2.73 |
| 1.ª mitad | 1048 | 50.5 % | -0.034 | -35.6 | 0.93 | -49.5 | -1.16 |
| 2.ª mitad | 1047 | 46.5 % | -0.115 | -119.9 | 0.79 | -121.8 | -3.80 |

Cómo terminan: objetivo 933, stop 973, a las 09:30 189. Coste medio 0.052 R (mediano 0.044 R); riesgo medio 0.27 % del precio; ancho medio del ORB 0.19 %.

## Por año

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 76 | 56.6 % | +0.096 | +7.3 | 1.22 | -9.3 | +0.85 |
| 2019 | 258 | 47.7 % | -0.125 | -32.2 | 0.77 | -37.8 | -2.07 |
| 2020 | 255 | 50.6 % | -0.003 | -0.8 | 0.99 | -18.1 | -0.05 |
| 2021 | 259 | 54.1 % | +0.010 | +2.6 | 1.02 | -14.8 | +0.18 |
| 2022 | 257 | 43.6 % | -0.135 | -34.7 | 0.74 | -40.8 | -2.30 |
| 2023 | 258 | 50.0 % | -0.052 | -13.5 | 0.89 | -24.2 | -0.87 |
| 2024 | 259 | 42.5 % | -0.205 | -53.2 | 0.65 | -61.1 | -3.39 |
| 2025 | 257 | 49.4 % | -0.048 | -12.4 | 0.90 | -23.8 | -0.80 |
| 2026 | 216 | 47.7 % | -0.086 | -18.6 | 0.84 | -20.4 | -1.29 |

## Por día de la semana

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| lunes | 417 | 43.9 % | -0.151 | -63.1 | 0.72 | -68.7 | -3.27 |
| martes | 421 | 47.0 % | -0.103 | -43.5 | 0.80 | -55.9 | -2.21 |
| miércoles | 419 | 50.8 % | -0.032 | -13.6 | 0.93 | -29.9 | -0.68 |
| jueves | 422 | 51.2 % | -0.040 | -16.8 | 0.92 | -31.4 | -0.85 |
| viernes | 416 | 49.5 % | -0.044 | -18.5 | 0.91 | -31.8 | -0.94 |

## Por hora de la rotura

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 03:00 | 1766 | 48.6 % | -0.072 | -126.8 | 0.86 | -142.4 | -3.11 |
| 04:00 | 259 | 46.7 % | -0.103 | -26.8 | 0.80 | -32.5 | -1.77 |
| 05:00 | 48 | 56.2 % | +0.013 | +0.6 | 1.03 | -6.0 | +0.10 |
| 06:00 | 14 | 28.6 % | -0.201 | -2.8 | 0.54 | -3.2 | -1.00 |
| 07:00 | 6 | 50.0 % | -0.137 | -0.8 | 0.61 | -1.1 | -0.45 |
| 08:00 | 2 | 100.0 % | +0.576 | +1.2 | - | -0.0 | +0.00 |

## Por ancho del ORB

Ancho frente a la mediana de los 20 días anteriores con operación.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| estrecho (< 0,7) | 465 | 48.8 % | -0.101 | -47.2 | 0.81 | -57.6 | -2.21 |
| normal (0,7 - 1,3) | 1000 | 50.1 % | -0.042 | -42.2 | 0.92 | -55.2 | -1.37 |
| ancho (> 1,3) | 620 | 45.6 % | -0.107 | -66.0 | 0.79 | -76.9 | -2.88 |

## Sensibilidad

Cambiando una cosa cada vez sobre la variante principal.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| colchón 0% | 2095 | 48.7 % | -0.081 | -169.7 | 0.84 | -180.5 | -3.81 |
| colchón 10% | 2095 | 48.6 % | -0.076 | -159.0 | 0.85 | -168.5 | -3.59 |
| colchón 20% (principal) | 2095 | 48.5 % | -0.074 | -155.5 | 0.85 | -167.5 | -3.53 |
| colchón 30% | 2095 | 48.2 % | -0.072 | -150.7 | 0.86 | -160.5 | -3.46 |
| colchón 50% | 2095 | 48.0 % | -0.069 | -144.7 | 0.86 | -158.0 | -3.40 |
| objetivo 1.5:1 | 2095 | 41.5 % | -0.062 | -129.2 | 0.89 | -140.6 | -2.49 |
| objetivo 2:1 | 2095 | 37.3 % | -0.071 | -147.9 | 0.88 | -159.8 | -2.59 |
| salida a las 12:00 | 2095 | 48.9 % | -0.073 | -153.1 | 0.86 | -165.5 | -3.35 |
| salida a las 14:00 | 2095 | 49.0 % | -0.072 | -150.4 | 0.87 | -162.8 | -3.29 |
| salida a las 16:00 | 2095 | 49.1 % | -0.070 | -147.2 | 0.87 | -159.7 | -3.22 |

## Colchón elegido con la 1.ª mitad

Con la 1.ª mitad el mejor colchón es el 20% (-0.034 R). En la 2.ª mitad, sin haberla visto:

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| colchón 20%, 2.ª mitad | 1047 | 46.5 % | -0.115 | -119.9 | 0.79 | -121.8 | -3.80 |

