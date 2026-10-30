# Backtest ORB 01:00 en NAS100.s (M5, PUPrime)

Script: `scripts/backtest_orb_nasdaq.py` → operaciones en `analisis/backtest_orb_nasdaq.csv` (no se sube a git). Solo lee velas de MT5.

## Reglas (hora de Nueva York)

- **ORB:** máximo y mínimo de las velas M5 de las 01:00, 01:05 y 01:10.
- **Rotura con cuerpo:** la primera vela M5 desde las 01:15 que cierra fuera del ORB, como tarde a las 09:30. Una operación por día.
- **Entrada** al cierre de esa vela. **Stop** en el extremo opuesto del ORB ± 20% de su ancho. **Objetivo** 1:1 (a la misma distancia que el stop).
- Sin stop ni objetivo a las 09:30: se cierra al cierre de la vela de las 09:25. Si caben stop y objetivo en una vela, cuenta el stop.
- **Costes:** spread real de MT5 en la vela de la entrada (R neto = R bruto − spread / riesgo). Sin comisiones ni deslizamiento.

## Datos

- 573.084 velas M5 de NAS100.s del 10/09/2018 al 30/10/2026 (hora de NY. servidor = NY + 7 h).
- Días laborables: 2117; con las tres velas del ORB: 2097; con rotura antes de las 09:30: 2097 (100 %).
- Comprobación del horario: velas con hora NY 17 (la pausa diaria de los índices): 0 de 573.084.

## Veredicto (criterios fijados antes de ver los resultados)

| Criterio | Valor | Cumple |
|---|---:|---:|
| al menos 300 operaciones | 2097 | sí |
| R neto medio > +0.05 y t > 2.0 | -0.077 R, t -3.51 | **no** |
| R neto medio positivo en las dos mitades | -0.125 / -0.028 R | **no** |

**No pasa.**

## Resultado de la variante principal

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas | 2097 | 51.1 % | -0.077 | -160.7 | 0.86 | -186.3 | -3.51 |
| Sin costes (R bruto) | 2097 | 51.1 % | +0.021 | +43.7 | 1.04 | -48.5 | +0.96 |
| Long | 1081 | 52.9 % | -0.039 | -41.8 | 0.92 | -72.3 | -1.27 |
| Short | 1016 | 49.1 % | -0.117 | -118.9 | 0.79 | -129.1 | -3.73 |
| 1.ª mitad | 1049 | 48.6 % | -0.125 | -131.1 | 0.78 | -133.3 | -4.04 |
| 2.ª mitad | 1048 | 53.5 % | -0.028 | -29.7 | 0.94 | -54.9 | -0.92 |

Cómo terminan: objetivo 1063, stop 1022, a las 09:30 12. Coste medio 0.097 R (mediano 0.082 R); riesgo medio 0.16 % del precio; ancho medio del ORB 0.11 %.

## Por año

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 76 | 52.6 % | -0.043 | -3.3 | 0.92 | -9.0 | -0.37 |
| 2019 | 258 | 48.4 % | -0.189 | -48.7 | 0.68 | -48.9 | -3.00 |
| 2020 | 256 | 49.2 % | -0.076 | -19.4 | 0.86 | -32.7 | -1.22 |
| 2021 | 259 | 50.2 % | -0.096 | -25.0 | 0.82 | -40.3 | -1.54 |
| 2022 | 258 | 46.1 % | -0.149 | -38.3 | 0.74 | -43.3 | -2.39 |
| 2023 | 258 | 53.9 % | -0.060 | -15.5 | 0.88 | -16.3 | -0.97 |
| 2024 | 259 | 53.7 % | -0.044 | -11.3 | 0.92 | -26.9 | -0.70 |
| 2025 | 257 | 51.8 % | -0.042 | -10.9 | 0.92 | -24.5 | -0.68 |
| 2026 | 216 | 55.6 % | +0.054 | +11.6 | 1.11 | -9.8 | +0.79 |

## Por día de la semana

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| lunes | 418 | 51.7 % | -0.065 | -27.1 | 0.88 | -40.7 | -1.32 |
| martes | 421 | 50.6 % | -0.084 | -35.5 | 0.84 | -50.8 | -1.73 |
| miércoles | 420 | 50.5 % | -0.088 | -37.1 | 0.84 | -40.5 | -1.82 |
| jueves | 422 | 51.2 % | -0.072 | -30.5 | 0.87 | -48.2 | -1.47 |
| viernes | 416 | 51.4 % | -0.074 | -30.6 | 0.86 | -46.2 | -1.50 |

## Por hora de la rotura

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 01:00 | 1834 | 51.9 % | -0.064 | -117.6 | 0.88 | -143.3 | -2.74 |
| 02:00 | 245 | 44.9 % | -0.175 | -42.9 | 0.70 | -52.9 | -2.75 |
| 03:00 | 15 | 46.7 % | -0.085 | -1.3 | 0.84 | -3.9 | -0.32 |
| 04:00 | 1 | 100.0 % | +0.974 | +1.0 | - | -0.0 | +0.00 |
| 08:00 | 2 | 50.0 % | +0.023 | +0.0 | 1.28 | -0.2 | +0.00 |

## Por ancho del ORB

Ancho frente a la mediana de los 20 días anteriores con operación.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| estrecho (< 0,7) | 457 | 51.0 % | -0.130 | -59.4 | 0.77 | -60.7 | -2.78 |
| normal (0,7 - 1,3) | 1003 | 51.2 % | -0.076 | -76.6 | 0.86 | -101.9 | -2.41 |
| ancho (> 1,3) | 627 | 50.9 % | -0.039 | -24.6 | 0.92 | -53.1 | -0.99 |

## Sensibilidad

Cambiando una cosa cada vez sobre la variante principal.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| colchón 0% | 2097 | 51.5 % | -0.083 | -175.1 | 0.85 | -204.3 | -3.81 |
| colchón 10% | 2097 | 51.3 % | -0.080 | -167.3 | 0.85 | -193.5 | -3.65 |
| colchón 20% (principal) | 2097 | 51.1 % | -0.077 | -160.7 | 0.86 | -186.3 | -3.51 |
| colchón 30% | 2097 | 50.8 % | -0.076 | -159.9 | 0.86 | -188.8 | -3.49 |
| colchón 50% | 2097 | 50.8 % | -0.066 | -137.6 | 0.88 | -170.0 | -3.02 |
| objetivo 1.5:1 | 2097 | 42.0 % | -0.055 | -115.1 | 0.91 | -184.4 | -2.05 |
| objetivo 2:1 | 2097 | 36.0 % | -0.040 | -84.3 | 0.94 | -163.8 | -1.30 |
| salida a las 12:00 | 2097 | 51.1 % | -0.077 | -160.5 | 0.86 | -186.5 | -3.50 |
| salida a las 16:00 | 2097 | 51.1 % | -0.076 | -159.4 | 0.86 | -185.8 | -3.47 |

## Colchón elegido con la 1.ª mitad

Con la 1.ª mitad el mejor colchón es el 50% (-0.101 R). En la 2.ª mitad, sin haberla visto:

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| colchón 50%, 2.ª mitad | 1048 | 52.7 % | -0.030 | -31.9 | 0.94 | -69.8 | -0.99 |

