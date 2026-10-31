# Exploración: precio frente a la EMA 10 y el VWAP en M15 (NAS100.s, PUPrime, entrenamiento)

Periodo: 10/09/2018 – 30/12/2022 (100.640 velas M15). Los datos posteriores y los demás mercados se reservan para la prueba.

Movimientos en ATR 14 de M15. Coste medio de una operación (spread / ATR): 0.087 ATR (mediano 0.066). Para ganar algo, una señal tiene que mover el precio bastante más que eso.

Cada celda: movimiento medio del cierre k velas después (en ATR, positivo = sube), estadístico t y número de muestras (una cada k velas). Un largo gana ese número; un corto, el mismo con el signo cambiado.

## 1. Según el estado al cierre

| Estado | 1 velas (15 min) | 4 velas (60 min) | 8 velas (120 min) | 16 velas (240 min) |
|---|---:|---:|---:|---:|
| encima | +0.012 (t +3.2, 45017) | +0.007 (t +0.4, 10889) | +0.016 (t +0.4, 5194) | +0.026 (t +0.3, 2340) |
| mixto | -0.003 (t -0.5, 19083) | +0.048 (t +1.9, 4595) | +0.110 (t +1.9, 2138) | +0.057 (t +0.4, 957) |
| debajo | -0.001 (t -0.2, 35426) | +0.016 (t +0.9, 8562) | +0.005 (t +0.1, 4134) | +0.077 (t +0.9, 1879) |

## 2. Estado por sesión (a 4 velas, 1 h)

| Sesión | encima | mixto | debajo |
|---|---:|---:|---:|
| Asia 18-02 | +0.026 (t +1.2, 4062) | +0.065 (t +2.1, 1524) | +0.022 (t +1.0, 3284) |
| Londres 02-08 | +0.014 (t +0.5, 2993) | +0.018 (t +0.4, 1441) | +0.048 (t +1.3, 2214) |
| NY mañana 08-12 | -0.102 (t -1.7, 1982) | +0.080 (t +0.8, 792) | +0.002 (t +0.0, 1659) |
| NY tarde 12-17 | +0.069 (t +2.3, 1852) | +0.040 (t +0.9, 838) | -0.030 (t -0.8, 1405) |

## 3. Cambios de estado (la vela en que cambia)

| Estado | 1 velas (15 min) | 4 velas (60 min) | 8 velas (120 min) | 16 velas (240 min) |
|---|---:|---:|---:|---:|
| entra en «encima» (venía de mixto / debajo) | +0.015 (t +1.6, 7890) | +0.028 (t +1.4, 7696) | +0.061 (t +2.0, 7391) | +0.121 (t +2.6, 6807) |
| entra en «debajo» (venía de mixto / encima) | -0.005 (t -0.5, 7239) | +0.007 (t +0.3, 7079) | +0.001 (t +0.0, 6796) | +0.012 (t +0.2, 6270) |
| sale de «encima» a mixto | -0.013 (t -1.1, 5192) | +0.022 (t +0.9, 5045) | +0.056 (t +1.4, 4782) | +0.130 (t +2.0, 4311) |
| sale de «debajo» a mixto | -0.004 (t -0.4, 4488) | +0.035 (t +1.5, 4374) | -0.049 (t -1.2, 4155) | -0.080 (t -1.3, 3721) |

## 4. Retroceso a la media dentro de la tendencia

| Estado | 1 velas (15 min) | 4 velas (60 min) | 8 velas (120 min) | 16 velas (240 min) |
|---|---:|---:|---:|---:|
| tendencia arriba: la vela toca la EMA y cierra encima de los dos | +0.000 (t +0.0, 7341) | -0.020 (t -0.9, 7163) | -0.018 (t -0.6, 6748) | +0.072 (t +1.4, 6027) |
| tendencia abajo: la vela toca la EMA y cierra debajo de los dos | +0.011 (t +1.0, 5735) | +0.089 (t +3.9, 5621) | +0.072 (t +2.1, 5379) | +0.105 (t +1.9, 4860) |
| tendencia arriba: la vela toca el VWAP y cierra encima de los dos | -0.011 (t -0.7, 2258) | -0.054 (t -1.6, 2242) | -0.013 (t -0.3, 2194) | +0.006 (t +0.1, 2107) |
| tendencia abajo: la vela toca el VWAP y cierra debajo de los dos | +0.061 (t +3.0, 1954) | +0.119 (t +3.1, 1935) | +0.155 (t +2.8, 1909) | +0.314 (t +3.9, 1855) |

## 5. Distancia del cierre al VWAP (en ATR)

| Distancia | 1 velas (15 min) | 4 velas (60 min) | 8 velas (120 min) | 16 velas (240 min) |
|---|---:|---:|---:|---:|
| ≤ −4 ATR | -0.059 (t -1.9, 1554) | -0.124 (t -1.1, 320) | +0.041 (t +0.2, 149) | +0.048 (t +0.1, 74) |
| −4 a −2 | +0.001 (t +0.1, 9630) | +0.008 (t +0.2, 2314) | -0.023 (t -0.3, 1083) | -0.183 (t -1.0, 461) |
| −2 a −1 | -0.001 (t -0.1, 12123) | -0.012 (t -0.4, 2881) | -0.037 (t -0.5, 1374) | +0.132 (t +0.8, 634) |
| −1 a 0 | +0.001 (t +0.2, 20916) | +0.046 (t +2.1, 5148) | +0.056 (t +1.2, 2506) | +0.044 (t +0.4, 1126) |
| 0 a 1 | +0.005 (t +1.0, 22573) | +0.003 (t +0.1, 5634) | +0.029 (t +0.6, 2720) | +0.045 (t +0.5, 1284) |
| 1 a 2 | +0.010 (t +1.5, 13818) | +0.058 (t +1.9, 3360) | +0.182 (t +2.7, 1610) | +0.149 (t +0.9, 721) |
| 2 a 4 | +0.012 (t +1.7, 14399) | +0.003 (t +0.1, 3408) | -0.046 (t -0.6, 1612) | +0.120 (t +0.7, 718) |
| ≥ 4 ATR | +0.021 (t +1.7, 4513) | +0.034 (t +0.6, 981) | -0.073 (t -0.5, 412) | -0.279 (t -0.7, 158) |

## 6. Estado y pendiente de la EMA (4 velas)

| Estado | 1 velas (15 min) | 4 velas (60 min) | 8 velas (120 min) | 16 velas (240 min) |
|---|---:|---:|---:|---:|
| encima y EMA subiendo | +0.013 (t +3.3, 40498) | -0.003 (t -0.2, 9768) | -0.011 (t -0.3, 4654) | -0.006 (t -0.1, 2087) |
| encima y EMA bajando | +0.002 (t +0.2, 4516) | +0.096 (t +1.9, 1121) | +0.247 (t +2.1, 540) | +0.291 (t +1.2, 253) |
| debajo y EMA bajando | +0.000 (t +0.0, 31584) | +0.011 (t +0.6, 7633) | +0.000 (t +0.0, 3702) | +0.057 (t +0.6, 1666) |
| debajo y EMA subiendo | -0.008 (t -0.6, 3842) | +0.065 (t +1.2, 929) | +0.045 (t +0.4, 432) | +0.236 (t +1.0, 213) |

## 7. Referencia: deriva de fondo

Cualquier vela, sin condición: 1 velas +0.005 (t +1.8, 99526), 4 velas +0.018 (t +1.6, 24046), 8 velas +0.030 (t +1.2, 11466), 16 velas +0.050 (t +0.9, 5176).
Una condición solo aporta algo si se separa de esta deriva (el Nasdaq subió mucho en estos años).

