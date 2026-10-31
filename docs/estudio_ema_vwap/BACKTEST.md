# Backtest: «Rechazo fallido del VWAP» (largos, M15)

Script: `scripts/backtest_ema_vwap.py`. Exploración previa: [EXPLORACION.md](EXPLORACION.md).

## Estrategia y criterios (fijados antes de ver los datos de prueba)

- **Señal:** las dos velas M15 anteriores cerraron por debajo de la EMA 10 y del VWAP del día; la vela actual toca el VWAP con su máximo y vuelve a cerrar por debajo de los dos.
- **Largo** al cierre de esa vela; **salida** a las 16 velas (4 h) o al final del día de trading. Sin stop. Una posición a la vez. Resultado en ATR 14 de M15, con el spread descontado.
- **Línea base:** largo en cualquier vela (una cada 16) con la misma salida: la subida de fondo.
- **Se da por buena si:** (1) NAS100 de PUPrime de 2023 en adelante: R neto > 0 con t > 2.0; (2) ahí supera a la línea base; (3) R neto > 0 con t > 1.65 en al menos 2 de 3: SP500 y DJ30 de PUPrime, NAS100 de MetaQuotes.

## Veredicto

| Criterio | Valor | Cumple |
|---|---:|---:|
| NAS100 PUPrime 2023-2026: R neto > 0 y t > 2.0 | -0.122 ATR, t -1.05 | **no** |
| Supera a la línea base | -0.122 frente a -0.033 | **no** |
| Otros mercados con R neto > 0 y t > 1.65 | 0 de 3 | **no** |

**No pasa.**

## Resultados

|  | Ops | Acierto | R neto medio (ATR) | t | R total (ATR) |
|---|---:|---:|---:|---:|---:|
| NAS100.s (puprime) 2018-2022 (exploración) | 1061 | 54.1 % | +0.132 | +1.18 | +140.2 |
| NAS100.s (puprime) 2023-2026 (prueba) | 897 | 52.0 % | -0.122 | -1.05 | -109.5 |
|   línea base 2023-2026 | 2958 | 52.6 % | -0.033 | -0.62 | -97.6 |
| SP500.s (puprime) | 1954 | 51.6 % | -0.112 | -1.45 | -218.4 |
|   línea base | 6279 | 51.6 % | -0.092 | -2.45 | -575.7 |
| DJ30.s (puprime) | 2119 | 51.2 % | +0.010 | +0.14 | +21.4 |
|   línea base | 6276 | 51.0 % | -0.049 | -1.31 | -309.7 |
| USTEC (metaquotes) | 977 | 50.5 % | +0.301 | +0.28 | +293.7 |
|   línea base | 3214 | 50.3 % | +1.382 | +1.60 | +4440.8 |

Sin costes (R bruto, en ATR):

|  | Ops | Acierto | R neto medio (ATR) | t | R total (ATR) |
|---|---:|---:|---:|---:|---:|
| NAS100.s (puprime) 2023-2026 | 897 | 53.8 % | -0.035 | -0.30 | -31.3 |
| SP500.s (puprime) | 1954 | 54.0 % | +0.018 | +0.23 | +35.0 |
| DJ30.s (puprime) | 2119 | 53.0 % | +0.117 | +1.60 | +247.1 |
| USTEC (metaquotes) | 977 | 54.7 % | +0.669 | +0.63 | +653.5 |

## Por año (todos los conjuntos de prueba)

|  | Ops | Acierto | R neto medio (ATR) | t | R total (ATR) |
|---|---:|---:|---:|---:|---:|
| NAS100.s (puprime) prueba 2023 | 251 | 47.8 % | -0.153 | -0.72 | -38.3 |
| NAS100.s (puprime) prueba 2024 | 251 | 54.6 % | +0.213 | +0.91 | +53.5 |
| NAS100.s (puprime) prueba 2025 | 207 | 57.5 % | -0.033 | -0.16 | -6.9 |
| NAS100.s (puprime) prueba 2026 | 188 | 47.9 % | -0.626 | -2.26 | -117.7 |
| SP500.s (puprime) 2018 | 75 | 52.0 % | +0.173 | +0.50 | +13.0 |
| SP500.s (puprime) 2019 | 228 | 48.7 % | -0.075 | -0.28 | -17.2 |
| SP500.s (puprime) 2020 | 205 | 51.7 % | -0.311 | -1.48 | -63.7 |
| SP500.s (puprime) 2021 | 227 | 51.1 % | -0.110 | -0.49 | -25.1 |
| SP500.s (puprime) 2022 | 257 | 54.5 % | -0.225 | -1.25 | -57.7 |
| SP500.s (puprime) 2023 | 277 | 50.9 % | +0.106 | +0.51 | +29.4 |
| SP500.s (puprime) 2024 | 259 | 47.5 % | -0.013 | -0.06 | -3.3 |
| SP500.s (puprime) 2025 | 221 | 56.6 % | -0.125 | -0.58 | -27.6 |
| SP500.s (puprime) 2026 | 205 | 52.7 % | -0.324 | -1.13 | -66.3 |
| DJ30.s (puprime) 2018 | 81 | 50.6 % | +0.215 | +0.59 | +17.4 |
| DJ30.s (puprime) 2019 | 232 | 52.2 % | +0.211 | +0.91 | +49.0 |
| DJ30.s (puprime) 2020 | 244 | 48.0 % | -0.230 | -1.10 | -56.2 |
| DJ30.s (puprime) 2021 | 248 | 50.4 % | -0.018 | -0.10 | -4.4 |
| DJ30.s (puprime) 2022 | 291 | 57.4 % | +0.119 | +0.79 | +34.5 |
| DJ30.s (puprime) 2023 | 308 | 49.0 % | -0.106 | -0.54 | -32.6 |
| DJ30.s (puprime) 2024 | 266 | 50.8 % | -0.010 | -0.05 | -2.7 |
| DJ30.s (puprime) 2025 | 238 | 49.2 % | -0.179 | -0.85 | -42.6 |
| DJ30.s (puprime) 2026 | 211 | 52.6 % | +0.279 | +0.93 | +58.9 |
| USTEC (metaquotes) 2022 | 124 | 53.2 % | +0.240 | +0.81 | +29.8 |
| USTEC (metaquotes) 2023 | 253 | 48.2 % | -0.222 | -1.09 | -56.1 |
| USTEC (metaquotes) 2024 | 228 | 47.8 % | +1.932 | +0.43 | +440.4 |
| USTEC (metaquotes) 2025 | 186 | 59.1 % | -0.131 | -0.55 | -24.3 |
| USTEC (metaquotes) 2026 | 186 | 46.2 % | -0.517 | -1.89 | -96.1 |

## Por sesión de la señal

|  | Ops | Acierto | R neto medio (ATR) | t | R total (ATR) |
|---|---:|---:|---:|---:|---:|
| NAS100.s (puprime) prueba, Asia 18-02 | 492 | 49.6 % | -0.161 | -1.39 | -79.1 |
| NAS100.s (puprime) prueba, Londres 02-08 | 176 | 56.2 % | -0.059 | -0.15 | -10.3 |
| NAS100.s (puprime) prueba, NY mañana 08-12 | 165 | 50.9 % | -0.103 | -0.33 | -17.0 |
| NAS100.s (puprime) prueba, NY tarde 12-17 | 64 | 60.9 % | -0.049 | -0.13 | -3.1 |
| SP500.s (puprime), Asia 18-02 | 1060 | 50.9 % | -0.161 | -2.02 | -170.8 |
| SP500.s (puprime), Londres 02-08 | 371 | 53.1 % | +0.083 | +0.35 | +31.0 |
| SP500.s (puprime), NY mañana 08-12 | 359 | 52.4 % | -0.177 | -0.76 | -63.4 |
| SP500.s (puprime), NY tarde 12-17 | 164 | 51.2 % | -0.092 | -0.49 | -15.1 |
| DJ30.s (puprime), Asia 18-02 | 1165 | 50.9 % | -0.049 | -0.64 | -57.4 |
| DJ30.s (puprime), Londres 02-08 | 445 | 53.0 % | +0.193 | +0.88 | +85.7 |
| DJ30.s (puprime), NY mañana 08-12 | 344 | 47.4 % | -0.112 | -0.51 | -38.4 |
| DJ30.s (puprime), NY tarde 12-17 | 165 | 56.4 % | +0.191 | +1.17 | +31.4 |
| USTEC (metaquotes),  | 6 | 33.3 % | -1.133 | -0.65 | -6.8 |
| USTEC (metaquotes), Asia 18-02 | 561 | 48.8 % | -0.173 | -0.20 | -96.8 |
| USTEC (metaquotes), Londres 02-08 | 179 | 48.6 % | +2.099 | +0.41 | +375.7 |
| USTEC (metaquotes), NY mañana 08-12 | 149 | 55.0 % | +0.185 | +0.50 | +27.6 |
| USTEC (metaquotes), NY tarde 12-17 | 82 | 58.5 % | -0.073 | -0.26 | -6.0 |

## Sensibilidad (no cuenta para el veredicto)

|  | Ops | Acierto | R neto medio (ATR) | t | R total (ATR) |
|---|---:|---:|---:|---:|---:|
| tocar la EMA en lugar del VWAP: NAS100.s (puprime) 2023-2026 | 1854 | 52.2 % | -0.032 | -0.38 | -60.1 |
| tocar la EMA en lugar del VWAP: SP500.s (puprime) | 3837 | 51.8 % | -0.116 | -2.02 | -444.0 |
| tocar la EMA en lugar del VWAP: DJ30.s (puprime) | 4102 | 50.8 % | -0.082 | -1.43 | -334.9 |
| tocar la EMA en lugar del VWAP: USTEC (metaquotes) | 2006 | 50.0 % | +0.321 | +0.42 | +644.8 |
| salida a las 8 velas: NAS100.s (puprime) 2023-2026 | 998 | 50.6 % | -0.074 | -1.06 | -73.6 |
| salida a las 8 velas: SP500.s (puprime) | 2141 | 50.8 % | -0.059 | -1.13 | -125.7 |
| salida a las 8 velas: DJ30.s (puprime) | 2338 | 50.6 % | -0.088 | -1.79 | -206.2 |
| salida a las 8 velas: USTEC (metaquotes) | 1097 | 47.4 % | -4.437 | -1.01 | -4867.2 |
| stop a 1,5 ATR: NAS100.s (puprime) 2023-2026 | 960 | 37.0 % | -0.173 | -2.64 | -166.2 |
| stop a 1,5 ATR: SP500.s (puprime) | 2069 | 39.9 % | -0.062 | -1.31 | -127.3 |
| stop a 1,5 ATR: DJ30.s (puprime) | 2273 | 39.4 % | -0.035 | -0.74 | -80.6 |
| stop a 1,5 ATR: USTEC (metaquotes) | 1026 | 35.1 % | +0.872 | +1.03 | +894.2 |
