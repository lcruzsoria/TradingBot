# Backtest del sesgo en M5: reglas, pesos, umbral y filtro de lateralidad

Script: `scripts/analisis_sesgo.py` (datos: `scripts/descargar_m5.py`). Solo lee velas; el bot no envía órdenes.

## Cómo se midió

- **Datos:** 100.000 velas M5 por mercado (NAS100.r, SP500.r, DJ30.r, EURUSD, GBPUSD, XAUUSD), de mayo/junio de 2025 a octubre de
  2026. 15.012 bloques HTF (3 h en índices, 4 h en el resto).
- **Qué se evalúa:** el sesgo se calcula al abrirse cada bloque (con el precio de apertura, sin mirar al futuro) y se mantiene
  hasta el siguiente, como el bot en vivo. La **ventaja** es lo que hizo el precio en el bloque (cierre menos apertura) en la
  dirección del sesgo, en rangos medios de bloque (los 30 anteriores). Con No Bias no se cuenta.
- **Dos problemas medidos aparte:**
  - *Contradicción:* % de bloques con sesgo contrario a lo que hizo el precio en las 6 h anteriores (un alcista que prohíbe
    cortos con el precio bajista).
  - *Lateral:* % de bloques con sesgo cuando el precio venía lateral (eficiencia de las últimas 6 h < 0,15).
- **Búsqueda:** 1,9 millones de combinaciones: pesos 0/1/2 de nueve reglas candidatas (ruptura del día anterior, TDO, Midnight,
  barrido, continuación, SMA 30, SMA 200, momentum 6 h, momentum 24 h) x umbral 1-6 x filtro de lateralidad (ventanas 3/6/12 h,
  eficiencia mínima 0,10-0,30). Se **optimizó con el primer 60 %** del histórico y se **validó con el 40 % final**.

## Lo que dicen los datos

1. **Ninguna combinación tiene ventaja estadísticamente significativa** para predecir la dirección de un bloque. De las 1,9
   millones, la mejor en entrenamiento llega a t = 0,66 (lo esperable por azar con tantas pruebas es mucho mayor). En validación,
   las que parecían buenas bajan a t ≈ 0. El sesgo, tal como lo definimos, **no es un predictor**: sirve para ordenar y filtrar, no
   para ganar dinero por sí solo.
2. **Las reglas por separado** (peso 1, umbral 1; ventaja en entrenamiento / validación):

| Regla | Ventaja entren. | Ventaja valid. | Contradice al precio | Lectura |
|---|---:|---:|---:|---|
| `prev_day_break` | -0,047 (t -2,8) | -0,018 | 11 % | rompe y vuelve: a la contra en M5 |
| `tdo` | -0,015 | +0,024 (t +2,3) | 22 % | inestable entre mitades, algo a favor |
| `midnight` | -0,009 | +0,023 | 15 % | idem |
| `htf_sweep` | +0,004 | -0,041 (t -2,5) | **76 %** | es de reversión: **contradice al precio 3 de cada 4 veces** |
| `htf_break` | -0,010 | +0,036 (t +2,4) | **1 %** | continuación: nunca contradice al precio |
| `sma30` / `mom24h` | -0,020 | -0,014 / -0,016 | 33 % | pierde en las dos mitades |
| `sma200` | -0,020 | +0,007 | 19 % | sin ventaja |
| `mom6h` | -0,013 | -0,003 | 1 % | sin ventaja (es la tendencia pura) |

3. **El filtro de lateralidad es lo que más mejora el comportamiento visible.** Con las reglas anteriores (TDO, Midnight, ruptura)
   el 57-60 % de los bloques tenía sesgo y el **58 % de esos arrancaba con el mercado lateral**. Con el filtro (eficiencia de 6 h
   ≥ 0,15) quedan sesgos solo en el 26 % de los bloques y ninguno en lateral.
4. **El sesgo que contradecía al precio venía sobre todo de `htf_sweep`** (reversión) y, en menor medida, de `tdo`/`sma30`.

## Combinaciones comparadas (todas con los mismos datos)

| Config. | Reglas / pesos | Umbral | Filtro | Cobertura | Ventaja entren. | Ventaja valid. | Ventaja total (t) | Contradice | Lateral |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| A (antes, por defecto) | ruptura 2, TDO 1, Midnight 1 | 2 | no | 57 % | -0,021 | +0,025 | -0,003 (t -0,3) | 11,5 % | 58 % |
| B (antes, local) | ruptura 2, TDO 2, Midnight 1, barrido 2, continuación 2 | 3 | no | 60 % | -0,018 | +0,015 | -0,005 (t -0,6) | 14,1 % | 57 % |
| D (propuesta sin filtro) | ruptura 2, TDO 2, Midnight 1, continuación 2 | 3 | no | 62 % | -0,019 | +0,028 | +0,000 (t 0,0) | 9,5 % | 57 % |
| **C (propuesta, aplicada)** | **ruptura 2, TDO 2, Midnight 1, continuación 2** | **3** | **eficiencia 6 h ≥ 0,15** | **26 %** | **+0,003** | **+0,033** | **+0,015 (t +1,2)** | **0,7 %** | **0 %** |

Por mercado (estadístico t de la ventaja total de C): DJ30 +0,82, XAUUSD +1,21, NAS100 +0,37, SP500 +0,24, GBPUSD +0,22,
EURUSD +0,05: positivo o nulo en los seis, pero ninguno es significativo por separado.

## Decisión aplicada

- **Reglas:** `prev_day_break` (2), `tdo` (2), `midnight` (1), `htf_break` (2). Se **quita `htf_sweep`** (76 % de contradicciones
  con el precio) y `above_below_open` (duplica al TDO). `sma` queda disponible pero **apagada**: la SMA 30 pierde en las dos
  mitades.
- **Umbral 3:** una regla de peso 2 ya no basta sola; hacen falta dos que coincidan.
- **Filtro de lateralidad** (`BIAS_LATERAL_HOURS=6`, `BIAS_LATERAL_MIN_EFFICIENCY=0.15`): sin sesgo si el precio avanzó menos del
  15 % de su recorrido en las últimas 6 h. Ajustable en la ventana de reglas.

## Limitaciones (importante)

- Con tantas combinaciones probadas, que C sea la «mejor» sale en parte del azar: su ventaja total (+0,015 rangos de bloque, t 1,2)
  **no es significativa**. Lo que sí se mantiene de forma robusta es el efecto del filtro: menos sesgos, ninguno en lateral y casi
  ninguno contra el precio.
- Las dos mitades del histórico se comportan distinto (casi todo lo que pierde en la primera gana en la segunda): el mercado cambió
  de régimen, y 16 meses es poco para fiarse de pesos finos. Conviene repetir el backtest cada pocos meses.
- Se mide la dirección del bloque completo desde su apertura, no la utilidad del sesgo como filtro de los setups de las TBR; para eso
  ver `docs/analisis_setups/CAMBIOS.md` (donde el filtro de sesgo tampoco convirtió en rentable la continuación).
