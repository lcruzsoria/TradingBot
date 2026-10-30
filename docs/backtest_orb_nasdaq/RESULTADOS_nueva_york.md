# Backtest ORB apertura de Nueva York en NAS100.s (M5, PUPrime)

Script: `scripts/backtest_orb_nasdaq.py --sesion nueva_york` → operaciones en `analisis/backtest_orb_nasdaq_nueva_york.csv` (no se sube a git). Solo lee velas de MT5.

## Reglas (hora de Nueva York)

- **ORB:** máximo y mínimo de las velas M5 de las 09:30, 09:35, 09:40.
- **Rotura con cuerpo:** la primera vela M5 desde las 09:45 que cierra fuera del ORB, como tarde a las 16:00. Una operación por día.
- **Entrada** al cierre de esa vela. **Stop** en el extremo opuesto del ORB ± 20% de su ancho. **Objetivo** 1:1 (a la misma distancia que el stop).
- Sin stop ni objetivo a las 16:00: se cierra al cierre de la vela de las 15:55. Si caben stop y objetivo en una vela, cuenta el stop.
- **Costes:** spread real de MT5 en la vela de la entrada (R neto = R bruto − spread / riesgo). Sin comisiones ni deslizamiento.

## Datos

- 573.084 velas M5 de NAS100.s del 10/09/2018 al 30/10/2026 (hora de NY. servidor = NY + 7 h).
- Días laborables: 2117; con las tres velas del ORB: 2093; con rotura antes de las 16:00: 2088 (100 %).
- Comprobación del horario: velas con hora NY 17 (la pausa diaria de los índices): 0 de 573.084.

## Veredicto (criterios fijados antes de ver los resultados)

| Criterio | Valor | Cumple |
|---|---:|---:|
| al menos 300 operaciones | 2088 | sí |
| R neto medio > +0.05 y t > 2.0 | +0.015 R, t +0.77 | **no** |
| R neto medio positivo en las dos mitades | -0.005 / +0.034 R | **no** |

**No pasa.**

## Resultado de la variante principal

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todas | 2088 | 52.0 % | +0.015 | +30.6 | 1.04 | -33.8 | +0.77 |
| Sin costes (R bruto) | 2088 | 52.3 % | +0.032 | +66.0 | 1.08 | -30.1 | +1.65 |
| Long | 1074 | 55.2 % | +0.049 | +52.7 | 1.13 | -15.2 | +1.87 |
| Short | 1014 | 48.5 % | -0.022 | -22.1 | 0.95 | -28.3 | -0.78 |
| 1.ª mitad | 1044 | 51.3 % | -0.005 | -5.2 | 0.99 | -33.8 | -0.18 |
| 2.ª mitad | 1044 | 52.6 % | +0.034 | +35.8 | 1.09 | -17.8 | +1.27 |

Cómo terminan: objetivo 759, stop 716, a las 16:00 613. Coste medio 0.017 R (mediano 0.014 R); riesgo medio 0.73 % del precio; ancho medio del ORB 0.53 %.

## Por año

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 75 | 45.3 % | -0.102 | -7.7 | 0.78 | -11.3 | -1.00 |
| 2019 | 255 | 51.0 % | +0.023 | +5.9 | 1.06 | -9.6 | +0.44 |
| 2020 | 256 | 47.7 % | -0.092 | -23.4 | 0.80 | -27.6 | -1.64 |
| 2021 | 258 | 56.6 % | +0.079 | +20.4 | 1.22 | -8.6 | +1.47 |
| 2022 | 257 | 54.5 % | +0.039 | +10.0 | 1.10 | -14.3 | +0.71 |
| 2023 | 257 | 51.4 % | +0.013 | +3.4 | 1.03 | -12.8 | +0.24 |
| 2024 | 259 | 52.5 % | +0.020 | +5.1 | 1.05 | -9.1 | +0.35 |
| 2025 | 256 | 54.7 % | +0.080 | +20.5 | 1.22 | -8.6 | +1.48 |
| 2026 | 215 | 48.8 % | -0.017 | -3.7 | 0.95 | -17.8 | -0.30 |

## Por día de la semana

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| lunes | 417 | 50.6 % | +0.001 | +0.6 | 1.00 | -18.7 | +0.04 |
| martes | 422 | 54.5 % | +0.031 | +13.1 | 1.08 | -14.7 | +0.73 |
| miércoles | 417 | 49.9 % | -0.018 | -7.5 | 0.96 | -28.4 | -0.41 |
| jueves | 419 | 48.7 % | -0.040 | -16.6 | 0.91 | -28.5 | -0.92 |
| viernes | 413 | 56.2 % | +0.099 | +41.0 | 1.28 | -11.6 | +2.33 |

## Por hora de la rotura

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 09:00 | 1048 | 54.0 % | +0.046 | +48.6 | 1.12 | -15.1 | +1.67 |
| 10:00 | 932 | 51.2 % | -0.002 | -1.4 | 1.00 | -25.3 | -0.05 |
| 11:00 | 77 | 37.7 % | -0.227 | -17.5 | 0.51 | -19.0 | -2.62 |
| 12:00 | 13 | 61.5 % | +0.274 | +3.6 | 2.94 | -0.9 | +1.66 |
| 13:00 | 9 | 33.3 % | -0.191 | -1.7 | 0.47 | -2.6 | -0.89 |
| 14:00 | 5 | 20.0 % | -0.136 | -0.7 | 0.59 | -1.7 | -0.42 |
| 15:00 | 4 | 25.0 % | -0.064 | -0.3 | 0.65 | -0.7 | -0.30 |

## Por ancho del ORB

Ancho frente a la mediana de los 20 días anteriores con operación.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| estrecho (< 0,7) | 401 | 51.1 % | -0.005 | -2.1 | 0.99 | -23.0 | -0.11 |
| normal (0,7 - 1,3) | 1110 | 53.2 % | +0.044 | +48.6 | 1.11 | -15.1 | +1.65 |
| ancho (> 1,3) | 567 | 49.9 % | -0.033 | -18.5 | 0.91 | -24.7 | -0.97 |

## Sensibilidad

Cambiando una cosa cada vez sobre la variante principal.

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| colchón 0% | 2088 | 52.0 % | +0.017 | +36.3 | 1.04 | -44.9 | +0.87 |
| colchón 10% | 2088 | 51.8 % | +0.011 | +22.4 | 1.03 | -43.3 | +0.55 |
| colchón 20% (principal) | 2088 | 52.0 % | +0.015 | +30.6 | 1.04 | -33.8 | +0.77 |
| colchón 30% | 2088 | 51.9 % | +0.016 | +32.6 | 1.04 | -27.6 | +0.84 |
| colchón 50% | 2088 | 52.3 % | +0.023 | +47.3 | 1.06 | -23.6 | +1.28 |
| objetivo 1.5:1 | 2088 | 47.8 % | +0.026 | +54.6 | 1.06 | -25.7 | +1.20 |
| objetivo 2:1 | 2088 | 46.8 % | +0.038 | +80.1 | 1.09 | -28.2 | +1.66 |
| rotura y salida hasta las 12:00 | 2058 | 51.3 % | +0.006 | +11.5 | 1.02 | -27.1 | +0.35 |

## Colchón elegido con la 1.ª mitad

Con la 1.ª mitad el mejor colchón es el 50% (+0.009 R). En la 2.ª mitad, sin haberla visto:

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| colchón 50%, 2.ª mitad | 1044 | 52.5 % | +0.036 | +38.0 | 1.10 | -17.5 | +1.45 |

