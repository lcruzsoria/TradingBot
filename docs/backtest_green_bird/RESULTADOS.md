# Backtest: modelo Green Bird (barrido + reclaim con desplazamiento, parciales y trailing) sobre NQ

Script: `scripts/backtest_green_bird.py`. Lógica: `tradingbot/skills/pattern/green_bird.py`. Generado el 30/10/2026. Spread supuesto: 1.5 puntos por operación.

## Qué muestran sus gráficos

Observado en 7 capturas de @greenbirdtrader (13, 15, 19, 20, 23 y 27 de octubre de 2026; MNQ en 1-15 min, con su indicador «Green Bird NY»):

- Cajas de Asia (20:00-00:00) y London (02:00-05:00) con sus mínimos y máximos marcados, y la caja verde de 09:00-10:00 NY.
- El barrido de Asia / London / PDL / PWL lo hace el precio dentro de la hora de 09:00-10:00 (sobre todo a la apertura de las 09:30), a veces tomando varios niveles a la vez y aunque el precio ya los hubiera cruzado antes.
- Entra tras el reclaim, con una vela de desplazamiento, no en el primer cierre dentro; también opera antes de las 10:00 (27 oct, 9:42).
- Stop pequeño en el extremo del barrido (24-31 puntos), objetivo lejano (R:R dibujado 8 y 11, el extremo contrario de la caja o Asia / London) y escalera de parciales.

Solo se ve lo que publica (días ganadores) y su entrada con velas de 1-3 minutos; aquí solo hay M5.

## Datos

| mercado | velas M5 | desde (NY) | hasta (NY) | desfase servidor |
|---|---:|---:|---:|---:|
| USTEC | 199999 | 2023-10-19 | 2026-10-20 | NY + 7 h |
| NAS100.r | 99999 | 2025-05-21 | 2026-10-16 | NY + 7 h |

## Veredicto (criterios fijados antes de ver los resultados)

**La hipótesis NO cumple los criterios: no hay ventaja demostrada.**

- CUMPLE - Al menos 150 operaciones: 778 operaciones
- NO CUMPLE - R neto medio > +0.05 con t > 2 y positivo en cada mitad: completo -0.118 R (t -3.0); 1.ª mitad -0.055, 2.ª mitad -0.181
- NO CUMPLE - Mejora al control aleatorio: modelo -0.118 R frente a control -0.064 R

## Variantes

La primera es la hipótesis; las demás son sensibilidad, no se eligen por sus resultados. Los dos mercados cubren casi las mismas fechas: no son muestras independientes y las cifras agrupadas cuentan dos veces los mismos días.

| variante | operaciones | win rate % | R bruto medio | coste medio (R) | R neto medio | t | profit factor | mejor (R) | máx. drawdown (R) | R neto 1.ª mitad | R neto 2.ª mitad |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| principal (desplazamiento, parciales 1 R / 2 R y trailing) | 778 | 45.630 | -0.082 | 0.036 | -0.118 | -3.035 | 0.789 | 2.866 | -95.616 | -0.055 | -0.181 |
| sin desplazamiento (entrada al cierre del reclaim) | 912 | 43.969 | -0.106 | 0.057 | -0.164 | -4.328 | 0.723 | 4.751 | -156.498 | -0.144 | -0.183 |
| desplazamiento exigente (cuerpo >= 1,5 veces) | 659 | 47.496 | -0.017 | 0.033 | -0.050 | -1.150 | 0.908 | 2.866 | -46.883 | 0.010 | -0.109 |
| al menos 2 niveles barridos a la vez | 692 | 44.942 | -0.096 | 0.036 | -0.133 | -3.218 | 0.766 | 2.866 | -97.862 | -0.123 | -0.142 |
| sin parciales: stop a la entrada tras 1 R y trailing | 778 | 33.805 | -0.085 | 0.036 | -0.121 | -2.680 | 0.786 | 5.711 | -104.045 | -0.065 | -0.178 |
| solo parciales (1 R, 2 R) sin trailing ni breakeven | 778 | 32.134 | -0.113 | 0.036 | -0.149 | -3.400 | 0.755 | 4.515 | -116.874 | -0.117 | -0.181 |
| objetivo fijo 2 R | 778 | 30.977 | -0.069 | 0.036 | -0.105 | -2.107 | 0.853 | 1.987 | -93.223 | -0.040 | -0.170 |
| objetivo fijo 1 R | 778 | 45.887 | -0.082 | 0.036 | -0.119 | -3.316 | 0.789 | 0.987 | -98.977 | -0.037 | -0.200 |
| la operación puede pasar del cierre (24 h) | 778 | 45.887 | -0.077 | 0.036 | -0.113 | -2.891 | 0.799 | 2.866 | -93.235 | -0.047 | -0.179 |
| ventana de barrido hasta las 10:00 | 472 | 46.610 | -0.064 | 0.036 | -0.099 | -1.982 | 0.819 | 2.866 | -56.567 | 0.020 | -0.218 |
| nivel intacto (como en la primera versión) | 594 | 44.276 | -0.132 | 0.036 | -0.168 | -3.942 | 0.707 | 2.816 | -107.747 | -0.145 | -0.192 |
| solo Asia / London / PDH-PDL (sin la hora previa a NY) | 617 | 47.164 | -0.050 | 0.036 | -0.086 | -1.955 | 0.842 | 2.866 | -62.301 | 0.005 | -0.175 |
| primera versión (reclaim M5, objetivo 2 R) | 794 | 31.108 | -0.066 | 0.063 | -0.129 | -2.613 | 0.824 | 1.986 | -120.495 | -0.120 | -0.137 |
| control aleatorio (misma ventana, riesgo y gestión) | 7780 | 49.254 | -0.027 | 0.036 | -0.064 | -5.262 | 0.877 | 5.665 | -512.279 | -0.065 | -0.063 |

## Variante principal: por mercado

| mercado | operaciones | win rate % | R bruto medio | coste medio (R) | R neto medio | t | profit factor | mejor (R) | máx. drawdown (R) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| NAS100.r | 279 | 44.444 | -0.085 | 0.032 | -0.116 | -1.746 | 0.797 | 2.600 | -44.998 |
| USTEC | 499 | 46.293 | -0.080 | 0.039 | -0.119 | -2.485 | 0.785 | 2.866 | -62.691 |

## Variante principal: por nivel

| nivel | operaciones | win rate % | R bruto medio | coste medio (R) | R neto medio | t | profit factor | mejor (R) | máx. drawdown (R) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ASIA | 219 | 47.032 | -0.094 | 0.035 | -0.129 | -1.863 | 0.761 | 2.299 | -43.459 |
| LONDON | 219 | 44.749 | -0.042 | 0.038 | -0.080 | -1.026 | 0.860 | 2.866 | -25.165 |
| PDHL | 163 | 49.080 | -0.029 | 0.035 | -0.065 | -0.757 | 0.877 | 2.369 | -13.269 |
| PRE_NY | 177 | 41.808 | -0.164 | 0.037 | -0.201 | -2.498 | 0.667 | 2.494 | -39.941 |

## Variante principal: por dirección

| dirección | operaciones | win rate % | R bruto medio | coste medio (R) | R neto medio | t | profit factor | mejor (R) | máx. drawdown (R) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| long | 334 | 44.910 | -0.119 | 0.035 | -0.154 | -2.672 | 0.728 | 2.866 | -60.615 |
| short | 444 | 46.171 | -0.054 | 0.037 | -0.091 | -1.730 | 0.836 | 2.600 | -43.157 |

## Variante principal: por niveles barridos a la vez

| niveles barridos | operaciones | win rate % | R bruto medio | coste medio (R) | R neto medio | t | profit factor | mejor (R) | máx. drawdown (R) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 217 | 47.926 | -0.032 | 0.038 | -0.070 | -0.940 | 0.871 | 2.363 | -24.771 |
| 2 | 258 | 41.473 | -0.199 | 0.037 | -0.235 | -3.701 | 0.610 | 2.866 | -67.816 |
| 3 | 208 | 50.481 | 0.021 | 0.035 | -0.014 | -0.177 | 0.973 | 2.369 | -22.687 |
| 4 | 95 | 41.053 | -0.104 | 0.036 | -0.139 | -1.162 | 0.771 | 2.494 | -21.824 |

## Variante principal: por resultado

| resultado | operaciones | win rate % | R bruto medio | coste medio (R) | R neto medio | t | profit factor | mejor (R) | máx. drawdown (R) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| breakeven / trailing | 353 | 100.000 | 1.011 | 0.037 | 0.974 | 29.070 |  | 2.866 | -0.000 |
| stop | 418 | 0.000 | -1.000 | 0.036 | -1.036 | -1014.438 | 0.000 | -1.013 | -433.086 |
| tiempo | 7 | 28.571 | -0.336 | 0.020 | -0.355 | -1.782 | 0.234 | 0.408 | -3.247 |

## Variante principal: por año

| año | operaciones | win rate % | R bruto medio | coste medio (R) | R neto medio | t | profit factor | mejor (R) | máx. drawdown (R) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 38 | 34.211 | -0.352 | 0.054 | -0.406 | -2.618 | 0.416 | 1.517 | -15.495 |
| 2024 | 157 | 52.229 | 0.021 | 0.050 | -0.029 | -0.345 | 0.941 | 2.866 | -23.350 |
| 2025 | 284 | 45.775 | -0.092 | 0.038 | -0.130 | -2.045 | 0.769 | 2.600 | -46.808 |
| 2026 | 299 | 43.478 | -0.091 | 0.025 | -0.117 | -1.794 | 0.798 | 2.494 | -38.575 |

## Cómo leerlo

- `R bruto medio` cerca de 0 con `R neto medio` negativo significa que el movimiento no tiene memoria y el spread se come lo que quede.
- Un `t` por debajo de 2 no se distingue de cero. Con 13 variantes mirando los mismos datos, alguna sale bien por azar.
- Lo que NO mide: sus entradas con velas de 1-3 minutos, el tamaño variable, decidir no operar un día ni la selección de los días que publica en X (solo ganadores). Es la versión mecánica de lo que se ve en sus gráficos, con velas M5.
- CFD de un solo broker, spread fijo, sin ver el recorrido interno de cada vela M5.
